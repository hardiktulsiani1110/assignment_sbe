from pydantic import BaseModel

from schema.user import CreateUserPayload


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginPayload(CreateUserPayload):
    pass
