from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from db.database import SessionLocal
from db.models.user import User
from utils.auth import decode_access_token


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Sets request.state.user for authenticated requests"""

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)

            if payload:
                user_id = payload.get("sub")
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        request.state.user = {
                            "id": str(user.id),
                            "email": user.email,
                            "role": user.role,
                        }
                finally:
                    db.close()

        response = await call_next(request)
        return response
