import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

from backend.app.db.session import get_db
from backend.app.crud.user import get_user_by_email, create_user, UserCreate, validate_password_strength
from backend.app.models.audit_log import AuditLog
from backend.app.services.email import send_verification_email, send_password_reset_email
from backend.app.core.security import (
    verify_password,
    create_access_token,
    create_scoped_token,
    decode_scoped_token,
    get_password_hash,
    generate_verification_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    LOCKOUT_THRESHOLD,
    LOCKOUT_DURATION_MINUTES,
)

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("TESTING", "").lower() not in ("true", "1"),
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

_IS_PRODUCTION = os.getenv("ENVIRONMENT", "production").lower() == "production"


def _audit(db: Session, action: str, request: Request, user_id: int | None = None, detail: str | None = None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=request.client.host if request.client else None,
        detail=detail,
    )
    db.add(entry)
    db.commit()


class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    full_name: str = None

class EmailRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db=db, user_in=user_in)

    token = generate_verification_token()
    user.verification_token = token
    db.commit()

    send_verification_email(user.email, token)

    _audit(db, "register", request, user_id=user.id)
    return user


@router.post("/verify-email")
def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    from backend.app.models.user import User
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    _audit(db, "email_verified", request, user_id=user.id)
    return {"detail": "Email verified successfully"}


@router.post("/resend-verification")
@limiter.limit("3/minute")
def resend_verification(request: Request, body: EmailRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=body.email)
    if not user or user.is_verified:
        return {"detail": "If the email exists and is unverified, a new token was sent"}
    token = generate_verification_token()
    user.verification_token = token
    db.commit()
    send_verification_email(user.email, token)
    return {"detail": "If the email exists and is unverified, a new token was sent"}


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=form_data.username)

    now = datetime.now(timezone.utc)
    locked_until = None
    if user and user.locked_until:
        locked_until = user.locked_until.replace(tzinfo=timezone.utc) if user.locked_until.tzinfo is None else user.locked_until
    if locked_until and locked_until > now:
        remaining = int((locked_until - now).total_seconds() / 60) + 1
        _audit(db, "login_blocked_lockout", request, user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {remaining} minutes",
        )

    if user and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Check your inbox or request a new verification link.",
        )

    if not user or not verify_password(form_data.password, user.hashed_password):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                db.commit()
                _audit(db, "account_locked", request, user_id=user.id,
                       detail=f"Locked after {LOCKOUT_THRESHOLD} failed attempts")
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked for {LOCKOUT_DURATION_MINUTES} minutes due to too many failed attempts",
                )
            db.commit()
        _audit(db, "login_failed", request, user_id=user.id if user else None,
               detail=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    access_token = create_access_token(subject=user.email)
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=_IS_PRODUCTION,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    _audit(db, "login_success", request, user_id=user.id)
    return response


@router.post("/logout")
def logout(request: Request):
    response = JSONResponse(content={"detail": "Logged out"})
    response.delete_cookie(key="access_token", path="/")
    return response


@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, body: EmailRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=body.email)
    if user:
        token = create_scoped_token(user.email, scope="password_reset", expires_minutes=30)
        send_password_reset_email(user.email, token)
        _audit(db, "password_reset_requested", request, user_id=user.id)
    return {"detail": "If the email exists, a reset link was sent"}


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, body: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = decode_scoped_token(body.token, expected_scope="password_reset")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    validate_password_strength(body.new_password)
    user.hashed_password = get_password_hash(body.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    _audit(db, "password_reset_completed", request, user_id=user.id)
    return {"detail": "Password updated successfully"}


def _extract_token(
    bearer: str | None = Depends(oauth2_scheme),
    access_token: str | None = Cookie(default=None),
) -> str:
    token = bearer or access_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

def get_current_user(token: str = Depends(_extract_token), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
