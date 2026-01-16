import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or "30")

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@abc.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
