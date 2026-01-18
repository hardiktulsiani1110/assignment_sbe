from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

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
    new_user = user_service.create_user(payload.email, payload.password, payload.role)
    return new_user


@admin_user_router.delete("/{user_id}")
def delete_user(user_id: UUID, user_service: UserService = Depends(get_user_service)):
    user_service.delete_user(user_id)
    return JSONResponse(content={"message": "User deleted successfully"})
