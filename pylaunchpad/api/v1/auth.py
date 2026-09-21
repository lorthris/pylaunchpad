"""Authentication and user session routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from pylaunchpad.database import get_db
from pylaunchpad.models.user import User
from pylaunchpad.schemas.user import (
    UserCreate,
    UserRead,
    LoginRequest,
    Token,
)
from pylaunchpad.auth.security import hash_password, verify_password, create_access_token
from pylaunchpad.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user account."""
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login_json(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate user with JSON credentials and return JWT bearer token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, token_type="bearer")


@router.post("/token", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """OAuth2 compatible token login for Swagger UI and CLI tools."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserRead)
def read_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Retrieve profile of currently authenticated user."""
    return current_user
