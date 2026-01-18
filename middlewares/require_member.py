# Dependency to require member authentication
from fastapi import HTTPException, Request

from schema.user import UserRole


async def require_member(request: Request):
    """Ensures authenticated user is member"""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Authentication required")
    if request.state.user["role"] != UserRole.MEMBER.value:
        raise HTTPException(status_code=403, detail="Only Members allowed to access")
    return request.state.user
