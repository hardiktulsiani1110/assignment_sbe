from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.security import HTTPBearer

from dependencies import get_task_filter_service, get_task_service
from middlewares.require_member import require_member
from schema.task import UserUpdateTaskPayload
from schema.task_filter import FilterRequest
from services.task_filter_service import TaskFilterService
from services.task_service import TaskService

bearer_scheme = HTTPBearer()

task_router = APIRouter(prefix="/tasks", dependencies=[Depends(bearer_scheme)])


@task_router.get("/", tags=["authenticated/tasks"])
def get_all_tasks(
    include_subtasks: bool = Query(default=True),
    task_service: TaskService = Depends(get_task_service),
):
    tasks = task_service.get_all_tasks(include_subtasks)
    return tasks


@task_router.get("/{task_id}", tags=["authenticated/tasks"])
def get_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.get_task_by_id(task_id)


@task_router.patch(
    "/{task_id}", tags=["member"], dependencies=[Depends(require_member)]
)
def update_task(
    request: Request,
    task_id: UUID,
    payload: UserUpdateTaskPayload,
    task_service: TaskService = Depends(get_task_service),
):
    update_data = payload.model_dump(exclude_unset=True)
    return task_service.user_update_task(
     UUID(request.state.user["id"]), task_id, update_data
    )


@task_router.post("/filter", tags=["authenticated/tasks"])
def filter_tasks(
    payload: FilterRequest,
    task_filter_service: TaskFilterService = Depends(get_task_filter_service),
):
    filtered_tasks = task_filter_service.search(payload.filters)
    return filtered_tasks
