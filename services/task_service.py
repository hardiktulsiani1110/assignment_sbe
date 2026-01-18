from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import HTTPException

from db.models.task import Task
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schema.task import TaskPriority, TaskStatus
from schema.user import UserRole


class TaskService:
    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository):
        self.task_repo = task_repo
        self.user_repo = user_repo

    def _verify_owner_and_get_task(
        self, task_id: UUID, owner_id: UUID
    ) -> Task:  # returning Task to avoid duplicate task fetching
        task = self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException("Task not found")
        if task.owner_id != owner_id:
            raise HTTPException("You are not the real owner of the task")
        return task

    def _verify_user_in_collaborator_and_get_task(
        self, user_id: UUID, task_id: UUID
    ) -> Task:  # returning Task to avoid duplicate task fetching
        task = self.task_repo.get_by_id_with_collaborators(task_id)

        if task is None:
            raise HTTPException(404, "Task Doesn't exist")

        user_is_collaborator = False

        for collab in task.collaborators:
            if collab.id == user_id:
                user_is_collaborator = True
                break

        if not user_is_collaborator:
            raise HTTPException("User should be a collaborator to update task")

        return task

    def get_tasks_by_owner(
        self, owner_id: UUID, include_subtasks: bool = True
    ) -> List[Task]:
        if include_subtasks:
            return self.task_repo.get_tasks_by_owner(owner_id)
        return self.task_repo.get_parent_tasks_by_owner(owner_id)

    def get_all_tasks(self, include_subtasks: bool = True) -> List[Task]:
        if include_subtasks:
            return self.task_repo.get_tasks()
        return self.task_repo.get_parent_tasks()

    def get_task_by_id(self, task_id: UUID) -> Task:
        task = self.task_repo.get_by_id_with_collaborators(task_id)
        if not task:
            raise HTTPException(404, detail="Task not found")
        return task

    def create_task(
        self,
        title: str,
        description: str | None = None,
        status: TaskStatus = TaskStatus.ICEBOX,
        priority: TaskPriority = TaskPriority.LOW,
        due_date: datetime | None = None,
        owner_id: UUID | None = None,
        parent_task_id: UUID | None = None,
    ) -> Task:
        new_task = self.task_repo.create(
            title,
            description,
            status.value,
            priority.value,
            due_date,
            owner_id,
            parent_task_id,
        )
        return new_task

    def update_task(self, task_id: UUID, owner_id: UUID, update_data: dict) -> Task:
        task = self._verify_owner_and_get_task(task_id, owner_id)

        for key, value in update_data.items():
            if key in ["priority", "status"]:
                value = value.value
            setattr(task, key, value)

        return self.task_repo.update(task)

    def bulk_update_tasks(
        self, task_ids: List[UUID], owner_id: UUID, update_data: dict
    ) -> Task:
        for task_id in task_ids:
            self._verify_owner_and_get_task(task_id, owner_id)

        for key, value in update_data.items():
            if key in ["priority", "status"]:  # since it is enum we need to store value
                value = value.value
                update_data[key] = value

        return self.task_repo.bulk_update(task_ids, update_data)

    def add_collaborators(
        self, task_id: UUID, owner_id: UUID, user_ids: List[UUID]
    ) -> None:
        task = self._verify_owner_and_get_task(task_id, owner_id)

        users = []
        for user_id in user_ids:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(404, detail=f"user:{user_id} doesn't exist")
            if (
                user.role != UserRole.MANAGER.value
                and user.role != UserRole.MEMBER.value
            ):
                raise HTTPException(
                    403,
                    detail="Only managers and members can be added as collaborators",
                )
            users.append(user)

        self.task_repo.add_collaborators(task, users)

    def remove_collaborators(
        self, task_id: UUID, owner_id: UUID, user_ids: List[UUID]
    ) -> None:
        task = self._verify_owner_and_get_task(task_id, owner_id)

        users = []
        for user_id in user_ids:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(404, detail=f"user:{user_id} doesn't exist")
            users.append(user)

        self.task_repo.remove_collaborators(task, users)

    def delete_task(self, owner_id: UUID, task_id: UUID) -> None:
        task = self._verify_owner_and_get_task(task_id, owner_id)
        self.task_repo.delete(task)

    def user_update_task(self, user_id: UUID, task_id: UUID, update_data: dict) -> None:
        if update_data is None:
            raise HTTPException(500, "Nothing to update")

        task = self._verify_user_in_collaborator_and_get_task(user_id, task_id)

        for key, value in update_data.items():
            if key in ["status", "priority"]:
                value = value.value
            setattr(task, key, value)

        self.task_repo.update(task)
