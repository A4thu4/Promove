from fastapi import HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator

from backend.app.models.user import User
from backend.app.core.security import get_password_hash


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="A senha deve ter no mínimo 8 caracteres")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="A senha deve conter ao menos uma letra maiúscula")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="A senha deve conter ao menos um número")
    return password


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("A senha deve conter ao menos uma letra maiúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("A senha deve conter ao menos um número")
        return v

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate):
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
