from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from middlewares.require_admin import require_admin
from routers.admin.user_router import admin_user_router

# Create main admin router
router = APIRouter(prefix="/admin", tags=["admin"])

bearer_scheme = HTTPBearer()
# Add the dependency to all admin routes
router.dependencies = [Depends(bearer_scheme), Depends(require_admin)]

router.include_router(admin_user_router)
# router.include_router(other_router)
