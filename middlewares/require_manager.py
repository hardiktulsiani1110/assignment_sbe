# Dependency to require manager authentication
from fastapi import HTTPException, Request

from schema.user import UserRole


async def require_manager(request: Request):
    """Ensures authenticated user is manager"""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Authentication required")
    if request.state.user["role"] != UserRole.MANAGER.value:
        raise HTTPException(status_code=403, detail="Only MAnagers allowed to access")
    return request.state.user
