# Dependency to require authentication
from fastapi import HTTPException, Request


async def require_admin(request: Request):
    """Ensures authenticated user is admin"""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Authentication required")
    if request.state.user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admins allowed to access")
    return request.state.user
