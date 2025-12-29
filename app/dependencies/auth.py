# app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.auth.jwt_handler import decode_access_token
from app.database.database import get_session
from app.services.crud.user import get_user_by_id
from app.core.config import get_settings
from app.schemas.auth import TokenData

bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required (Bearer token)",
        )
    return credentials.credentials


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session)
) -> TokenData:
    
    settings = get_settings()

    # Если аутентификация отключена, возвращаем внутреннего пользователя
    if not settings.AUTH_ENABLED:
        return TokenData(
            user_id=0,
            email="internal@service",
            is_admin=True,
        )

    token = _extract_bearer_token(credentials)
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    is_admin = payload.get("is_admin", False)
    email = payload.get("email")

    if not isinstance(user_id, int):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenData(user_id=user_id, email=email, is_admin=is_admin)


def get_current_admin(user: TokenData = Depends(get_current_user)) -> TokenData:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session)
):
    """
    Возвращает TokenData если пользователь залогинен.
    Если не залогинен или токен невалиден — возвращает None.
    """

    # Токена нет → пользователь неавторизован
    if not credentials:
        return None

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("user_id")

        user = get_user_by_id(user_id, session)
        if not user:
            return None

        return TokenData(
            user_id=user.id,
            email=user.email,
            is_admin=bool(user.is_admin)
        )

    except Exception:
        # Любая ошибка → считаем пользователя неавторизованным
        return None