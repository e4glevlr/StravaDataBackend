# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import auth_service, email_service
from app.models.user import User
from app.utils.security import create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class VerifyEmail(BaseModel):
    email: str
    code: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Kiểm tra email đã tồn tại chưa
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Tạo mã xác nhận và lưu người dùng
        verification_code = auth_service.generate_verification_code()
        new_user = auth_service.create_user(db, user, verification_code)

        # Tạm thời bỏ qua phần gửi email
        # await email_service.send_verification_email(user.email, verification_code)

        # Tạm thời đánh dấu tài khoản đã xác nhận
        new_user.is_verified = True
        new_user.is_active = True
        db.commit()

        return {"message": "User created successfully", "verification_code": verification_code}
    except Exception as e:
        print(f"Error in register: {str(e)}")
        raise

@router.post("/verify-email")
async def verify_email(verify_data: VerifyEmail, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == verify_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.verification_code != verify_data.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # Xác nhận tài khoản
    user.is_verified = True
    user.is_active = True
    user.verification_code = None
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: User = Depends(auth_service.get_current_user)):
    return {"message": "Successfully logged out"}