from pydantic import BaseModel


class CreateUserPayload(BaseModel):
    email: str
    password: str
