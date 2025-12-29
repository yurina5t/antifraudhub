# app/services/crud/user.py
from sqlmodel import Session, select
from app.models.user import User
from app.auth.hash_password import HashPassword

pwd = HashPassword()


def get_user_by_email(email: str, session: Session):
    return session.exec(select(User).where(User.email == email)).first()


def get_user_by_id(user_id: int, session: Session):
    return session.get(User, user_id)


def create_user(data, session: Session) -> User:
    hashed = pwd.create_hash(data.password)
    user = User(email=data.email, password=hashed, is_admin=False)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_all_users(session: Session):
    return session.exec(select(User)).all()


def delete_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True
