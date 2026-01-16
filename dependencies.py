from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.user_service import UserService


# managing all dependencies in this file
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)
