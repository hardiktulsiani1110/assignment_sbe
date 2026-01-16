from datetime import timedelta

from fastapi import HTTPException

from config import Config
from repositories.user_repository import UserRepository
from schema.auth import Token
from utils.auth import create_access_token, verify_password


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login(self, email: str, password: str) -> Token:
        user = self.user_repo.get_by_email(email)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
