# app/dependencies/authz.py
from fastapi import Depends, HTTPException, status
from app.dependencies.auth import TokenData, get_current_user

def self_or_admin(
    user_id: int,
    token: TokenData = Depends(get_current_user),
) -> TokenData:
    if token.is_admin or token.user_id == user_id:
        return token

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )
