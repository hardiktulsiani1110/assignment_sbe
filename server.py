from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from db.seed import seed_admin
from middlewares.jwt_auth_middleware import JWTAuthMiddleware
from routers.admin import router as admin_router
from routers.auth_router import auth_router
from routers.authenticated.task_router import task_router
from routers.authenticated.user_router import user_router
from routers.manager import router as manager_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_admin()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(JWTAuthMiddleware)


@app.get("/health", tags=["health"])
async def root():
    return {"message": "Ok!"}


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(manager_router)
app.include_router(user_router)
app.include_router(task_router)

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
