from enum import Enum

from pydantic import BaseModel, Field


class UserRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"
    MANAGER = "manager"


class CreateUserPayload(BaseModel):
    email: str
    password: str
    role: UserRole = Field(default=UserRole.MEMBER)
