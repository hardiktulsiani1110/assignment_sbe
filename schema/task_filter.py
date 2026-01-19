from datetime import datetime
from typing import List, Literal, Union
from uuid import UUID

from pydantic import BaseModel

from schema.task import TaskPriority, TaskStatus


class PriorityTaskFilterPayload(BaseModel):
    type: Literal["priority"]
    priority: TaskPriority


class StatusTaskFilterPayload(BaseModel):
    type: Literal["status"]
    status: TaskStatus


class DuedateTaskFilterPayload(BaseModel):
    type: Literal["due_date"]
    greater_than: datetime | None = None
    lesser_than: datetime | None = None


class AssigneeTaskFilterPayload(BaseModel):
    type: Literal["assignee"]
    assignee: UUID


TaskFilterPayload = Union[
    PriorityTaskFilterPayload,
    StatusTaskFilterPayload,
    DuedateTaskFilterPayload,
    AssigneeTaskFilterPayload,
]


class FilterRequest(BaseModel):
    filters: List[TaskFilterPayload]
