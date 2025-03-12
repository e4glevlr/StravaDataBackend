# app/services/auth_service.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.security import verify_password, get_password_hash, decode_token
import random
import string

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def generate_verification_code(length=6):
    """Tạo mã xác nhận ngẫu nhiên"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_user(db: Session, user_data, verification_code):
    """Tạo người dùng mới với mã xác nhận"""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        verification_code=verification_code
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    """Xác thực người dùng bằng tên đăng nhập và mật khẩu"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Lấy người dùng hiện tại từ token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user
