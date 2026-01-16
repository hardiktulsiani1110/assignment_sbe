from fastapi import APIRouter, Depends

from dependencies import get_user_service
from schema.user import CreateUserPayload
from services.user_service import UserService

admin_user_router = APIRouter(
    prefix="/users",
)


@admin_user_router.post("/")
def create_user(
    payload: CreateUserPayload, user_service: UserService = Depends(get_user_service)
):
    new_user = user_service.create_user(payload.email, payload.password)
    return new_user
