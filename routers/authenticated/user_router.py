from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from dependencies import get_user_service
from services.user_service import UserService

bearer_scheme = HTTPBearer()

user_router = APIRouter(
    prefix="/users", tags=["authenticated/users"], dependencies=[Depends(bearer_scheme)]
)


@user_router.get("/")
def get_all_users(user_service: UserService = Depends(get_user_service)):
    users = user_service.get_all_users()
    return users
