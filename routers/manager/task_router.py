from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from dependencies import get_task_service
from schema.task import (
    AddCollaboratorsPayload,
    BulkUpdateTaskPayload,
    CreateTaskPayload,
    UpdateTaskPayload,
)
from services.task_service import TaskService

manager_task_router = APIRouter(
    prefix="/tasks",
)


@manager_task_router.get("/my")
def get_manager_tasks(
    request: Request,
    include_subtasks: bool = Query(default=True),
    task_service: TaskService = Depends(get_task_service),
):
    tasks = task_service.get_tasks_by_owner(
        UUID(request.state.user["id"]), include_subtasks
    )
    return tasks


@manager_task_router.get("/all")
def get_all_tasks(
    request: Request,
    include_subtasks: bool = Query(default=True),
    task_service: TaskService = Depends(get_task_service),
):
    tasks = task_service.get_tasks_by_owner(
        UUID(request.state.user["id"]), include_subtasks
    )
    return tasks


@manager_task_router.get("/{task_id}")
def get_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.get_task_by_id(task_id)


@manager_task_router.post("/")
def create_task(
    request: Request,
    payload: CreateTaskPayload,
    task_service: TaskService = Depends(get_task_service),
):
    new_task = task_service.create_task(
        payload.title,
        payload.description,
        payload.status,
        payload.priority,
        payload.due_date,
        UUID(request.state.user["id"]),
        payload.parent_task_id,
    )
    return new_task


@manager_task_router.patch("/bulk")
def bulk_update_tasks(
    request: Request,
    payload: BulkUpdateTaskPayload,
    task_service: TaskService = Depends(get_task_service),
):
    update_data = payload.updates.model_dump(exclude_unset=True)
    return task_service.bulk_update_tasks(
        payload.task_ids, UUID(request.state.user["id"]), update_data
    )


@manager_task_router.patch("/{task_id}")
def update_task(
    request: Request,
    task_id: UUID,
    payload: UpdateTaskPayload,
    task_service: TaskService = Depends(get_task_service),
):
    update_data = payload.model_dump(exclude_unset=True)
    return task_service.update_task(
        task_id, UUID(request.state.user["id"]), update_data
    )


@manager_task_router.post("/{task_id}/collaborators/add")
def add_collaborators(
    request: Request,
    task_id: UUID,
    payload: AddCollaboratorsPayload,
    task_service: TaskService = Depends(get_task_service),
):
    task_service.add_collaborators(
        task_id, UUID(request.state.user["id"]), payload.user_ids
    )
    return JSONResponse(
        content={"message": "Added mentioned collaborators successfully"}
    )


@manager_task_router.post("/{task_id}/collaborators/remove")
def remove_collaborators(
    request: Request,
    task_id: UUID,
    payload: AddCollaboratorsPayload,
    task_service: TaskService = Depends(get_task_service),
):
    task_service.remove_collaborators(
        task_id, UUID(request.state.user["id"]), payload.user_ids
    )
    return JSONResponse(
        content={"message": "Removed mentioned collaborators successfully"}
    )


@manager_task_router.delete("/{task_id}")
def delete_task(
    request: Request,
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
):
    task_service.delete_task(UUID(request.state.user["id"]), task_id)
    return JSONResponse(content={"message": "Task deleted successfully"})
