"""FastAPI dependency injection utilities for user and API key authentication."""

from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from pylaunchpad.database import get_db
from pylaunchpad.models.base import utc_now
from pylaunchpad.models.user import User
from pylaunchpad.models.apikey import APIKey
from pylaunchpad.auth.security import decode_access_token, hash_api_key

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate bearer token and return corresponding user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure authenticated user account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    return current_user


def get_api_key_user(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate request using X-API-Key header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    key_hash = hash_api_key(x_api_key)
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash, APIKey.is_active.is_(True)).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    # Update last_used_at timestamp
    api_key.last_used_at = utc_now()
    db.commit()

    user = db.query(User).filter(User.id == api_key.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Associated user is inactive or deleted",
        )

    return user


def get_authenticated_client(
    token: Optional[str] = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate via either Bearer JWT token or X-API-Key header."""
    if token:
        try:
            return get_current_user(token=token, db=db)
        except HTTPException:
            pass

    if x_api_key:
        return get_api_key_user(x_api_key=x_api_key, db=db)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required via Bearer token or X-API-Key",
    )
