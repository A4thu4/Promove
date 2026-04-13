from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

try:
    from app.models.user import User
    from app.core.security import get_password_hash
except ImportError:
    from backend.app.models.user import User
    from backend.app.core.security import get_password_hash

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

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
