from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from db.models.task import Task
from db.models.user import User


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        title: str,
        description: str | None = None,
        status: str = "icebox",
        priority: str = "low",
        due_date: datetime | None = None,
        owner_id: UUID | None = None,
        parent_task_id: UUID | None = None,
    ):
        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            owner_id=owner_id,
            parent_task_id=parent_task_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: UUID) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_id_with_collaborators_and_dependencies(
        self, task_id: UUID
    ) -> Task | None:
        return (
            self.db.query(Task)
            .filter(Task.id == task_id)
            .options(joinedload(Task.collaborators))
            .options(joinedload(Task.depends_on_tasks))
            .options(joinedload(Task.dependent_tasks))
            .first()
        )

    def get_by_status(self, task_status: str) -> List[Task]:
        return self.db.query(Task).filter(Task.status == task_status).all()

    def get_by_priority(self, task_priority: str) -> List[Task]:
        return self.db.query(Task).filter(Task.priority == task_priority).all()

    def get_parent_tasks_by_owner(self, owner_id: UUID) -> List[Task]:
        return (
            self.db.query(Task)
            .filter(Task.owner_id == owner_id, Task.parent_task_id.is_(None))
            .all()
        )

    def get_tasks_by_owner(self, owner_id: UUID) -> List[Task]:
        return self.db.query(Task).filter(Task.owner_id == owner_id).all()

    def get_parent_tasks(self) -> List[Task]:
        return self.db.query(Task).filter(Task.parent_task_id.is_(None)).all()

    def get_tasks(self) -> List[Task]:
        return self.db.query(Task).all()

    def update(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def bulk_update(self, task_ids: List[UUID], update_data: dict) -> int:
        result = (
            self.db.query(Task)
            .filter(Task.id.in_(task_ids))
            .update(update_data, synchronize_session="fetch")
        )
        self.db.commit()
        return result

    def delete(self, task: Task) -> bool:
        self.db.delete(task)
        self.db.commit()
        return True

    def get_by_all_collaborators(self, user_ids: List[UUID]) -> List[Task]:
        task_query = self.db.query(Task)

        for user_id in user_ids:
            task_query = task_query.filter(Task.collaborators.any(User.id == user_id))

        return task_query.all()

    def get_by_collaborator(self, user_id: UUID) -> Task | None:
        return self.db.query(Task).filter(Task.collaborators.any(User.id == user_id)).all()

    def add_collaborators(self, task: Task, users: User) -> None:
        for user in users:
            if user not in task.collaborators:
                task.collaborators.append(user)
        self.db.commit()

    def remove_collaborators(self, task: Task, users: User) -> None:
        for user in users:
            if user in task.collaborators:
                task.collaborators.remove(user)
        self.db.commit()
