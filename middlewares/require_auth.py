# Dependency to require authentication
from fastapi import HTTPException, Request


async def require_auth(request: Request):
    """Ensures user is authenticated"""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return request.state.user
