"""API Key management endpoints for developers."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pylaunchpad.database import get_db
from pylaunchpad.models.user import User
from pylaunchpad.models.apikey import APIKey
from pylaunchpad.schemas.apikey import (
    APIKeyCreate,
    APIKeyRead,
    APIKeyCreatedResponse,
)
from pylaunchpad.auth.security import generate_api_key
from pylaunchpad.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/apikeys", tags=["API Keys"])


@router.get("", response_model=List[APIKeyRead])
def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[APIKey]:
    """List all API keys belonging to the authenticated user."""
    return db.query(APIKey).filter(APIKey.user_id == current_user.id).order_by(APIKey.created_at.desc()).all()


@router.post("", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """Generate a new API key. The plaintext key is only returned once upon creation."""
    raw_key, prefix, key_hash = generate_api_key()

    api_key_obj = APIKey(
        user_id=current_user.id,
        name=payload.name,
        key_prefix=prefix,
        key_hash=key_hash,
        is_active=True,
        rate_limit=payload.rate_limit,
    )
    db.add(api_key_obj)
    db.commit()
    db.refresh(api_key_obj)

    return {
        "id": api_key_obj.id,
        "name": api_key_obj.name,
        "key_prefix": api_key_obj.key_prefix,
        "is_active": api_key_obj.is_active,
        "last_used_at": api_key_obj.last_used_at,
        "rate_limit": api_key_obj.rate_limit,
        "created_at": api_key_obj.created_at,
        "api_key": raw_key,
    }


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """Revoke and deactivate a developer API key."""
    api_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key.is_active = False
    db.commit()
    return None
