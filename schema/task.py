from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(Enum):
    ICEBOX = "icebox"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    DELETED = "deleted"


class CreateTaskPayload(BaseModel):
    title: str
    description: str = Field(default="")
    status: TaskStatus = Field(default=TaskStatus.ICEBOX)
    priority: TaskPriority = Field(default=TaskPriority.LOW)
    due_date: datetime | None = Field(default=None)
    parent_task_id: UUID | None = None


class UpdateTaskPayload(BaseModel):
    title: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    description: str | None = None
    due_date: datetime | None = None
    parent_task_id: UUID | None = None


class BulkUpdateTaskPayload(BaseModel):
    task_ids: List[UUID]
    updates: UpdateTaskPayload


class AddCollaboratorsPayload(BaseModel):
    user_ids: List[UUID] = Field(..., min_length=1)


class RemoveCollaboratorsPayload(BaseModel):
    user_ids: List[UUID] = Field(..., min_length=1)


# User can only update status for now
class UserUpdateTaskPayload(BaseModel):
    status: TaskStatus = None


class AddDependencyPayload(BaseModel):
    pre_task_id: UUID
