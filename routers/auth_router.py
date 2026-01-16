from fastapi import APIRouter, Depends

from dependencies import get_auth_service
from schema.auth import LoginPayload
from services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
def login(payload: LoginPayload, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(payload.email, payload.password)
