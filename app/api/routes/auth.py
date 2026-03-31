from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.db.models import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.token import Token
from app.schemas.user import UserRead
from app.services.auth_service import get_user_by_email, create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = create_user(db, data.email, data.password)
    return user


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)
        

@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user