# app/routes/user.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from typing import List

from app.database.database import get_session
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import Token
from app.services.crud import user as UserService
from app.auth.hash_password import HashPassword
from app.auth.jwt_handler import create_access_token
from app.dependencies.auth import get_current_admin, get_current_user

hash_password = HashPassword()
user_route = APIRouter(prefix="/users", tags=["Users"])


@user_route.post("/signup", response_model=UserResponse)
async def signup(data: UserCreate, session: Session = Depends(get_session)):
    existing = UserService.get_user_by_email(data.email, session)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = UserService.create_user(data, session)
    return new_user


@user_route.post("/signin", response_model=Token)
async def signin(data: UserLogin, session: Session = Depends(get_session)):

    user = UserService.get_user_by_email(data.email, session)
    if not user or not hash_password.verify_hash(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "is_admin": user.is_admin
    })

    return Token(access_token=token)


#@user_route.get("/me", response_model=UserResponse)
#async def me(user=Depends(get_current_user)):
#    return user


@user_route.get("/", response_model=List[UserResponse])
async def list_users(
        session: Session = Depends(get_session),
        admin=Depends(get_current_admin)
):
    return UserService.get_all_users(session)


@user_route.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
        user_id: int,
        session: Session = Depends(get_session),
        admin=Depends(get_current_admin)
):
    user = UserService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user


@user_route.delete("/{user_id}")
async def delete_user(
        user_id: int,
        session: Session = Depends(get_session),
        admin=Depends(get_current_admin)
):
    ok = UserService.delete_user(user_id, session)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "deleted", "user_id": user_id}
