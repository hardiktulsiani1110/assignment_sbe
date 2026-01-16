# Dependency to require authentication
from fastapi import HTTPException, Request


async def require_auth(request: Request):
    """Ensures user is authenticated"""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Authentication required")
    if request.state.user["role"] != "member" or request.state.user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Members allowed to access")
    return request.state.user
