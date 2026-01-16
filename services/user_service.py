from uuid import UUID

from fastapi import HTTPException

from db.models.user import User
from repositories.user_repository import UserRepository
from utils.auth import get_password_hash


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, email: str, password: str) -> User:
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=500, detail="User already exists")

        hashed_password = get_password_hash(password)
        new_user = self.user_repo.create(email, hashed_password)
        return new_user

    def get_user_by_mail(self, email: str) -> User | None:
        user = self.user_repo.get_by_email(email)
        return user

    def get_user_by_id(self, id: UUID) -> User | None:
        user = self.user_repo.get_by_id(id)
        return user
