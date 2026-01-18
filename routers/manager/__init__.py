from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from middlewares.require_manager import require_manager
from routers.manager.task_router import manager_task_router

# Create main manager router
router = APIRouter(prefix="/manager", tags=["manager"])

bearer_scheme = HTTPBearer()
# Add the dependency to all manager routes
router.dependencies = [Depends(bearer_scheme), Depends(require_manager)]

router.include_router(manager_task_router)
