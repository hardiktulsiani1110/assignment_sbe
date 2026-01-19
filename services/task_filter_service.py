from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Query, Session

from db.models.task import Task
from db.models.user import User
from schema.task import TaskPriority, TaskStatus
from schema.task_filter import TaskFilterPayload


class TaskFilter(ABC):
    @abstractmethod
    def search(self, query: Query) -> Query:
        pass


class StatusTaskFilter(TaskFilter):
    def __init__(self, status: TaskStatus):
        self.status = status

    def search(self, query: Query) -> Query:
        return query.filter(Task.status == self.status.value)


class PriorityTaskFilter(TaskFilter):
    def __init__(self, priority: TaskPriority):
        self.priority = priority

    def search(self, query: Query) -> Query:
        return query.filter(Task.priority == self.priority.value)


class AssigneeTaskFilter(TaskFilter):
    def __init__(self, assignee: UUID):
        self.assignee = assignee

    def search(self, query: Query) -> Query:
        return query.filter(Task.collaborators.any(User.id == self.assignee))


class DueDateTaskFilter(TaskFilter):
    def __init__(self, lesser_than: datetime = None, greater_than: datetime = None):
        self.lesser_than = lesser_than
        self.greater_than = greater_than

    def search(self, query: Query) -> Query:
        if self.lesser_than and self.greater_than:
            return query.filter(
                and_(
                    Task.due_date > self.greater_than, Task.due_date < self.lesser_than
                )
            )

        if self.lesser_than:
            return query.filter(Task.due_date < self.lesser_than)

        return query.filter(Task.due_date > self.greater_than)


class TaskFilterService:
    def __init__(self, db: Session):
        self.query = db

    def _determine_filter(self, filter: TaskFilterPayload) -> TaskFilter:
        if filter.type == "status":
            return StatusTaskFilter(filter.status)

        elif filter.type == "priority":
            return PriorityTaskFilter(filter.priority)

        elif filter.type == "assignee":
            return AssigneeTaskFilter(filter.assignee)

        elif filter.type == "due_date":
            return DueDateTaskFilter(filter.lesser_than, filter.greater_than)

        else:
            raise ValueError(f"Unknown filter type {filter.type}")

    def search(self, filters: List[TaskFilterPayload]) -> List[Task]:
        query = self.db.query(Task)

        for filter in filters:
            task_filter = self._determine_filter(filter)
            query = task_filter.search(query)

        return query.all()
