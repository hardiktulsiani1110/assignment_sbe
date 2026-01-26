from uuid import UUID

from fastapi import HTTPException

from db.models.task import Task
from schema.task import TaskStatus


class TaskDependencyService:
    def _is_ancestor(self, potential_ancestor_id: UUID, task: Task) -> bool:
        current = task
        while current.parent_task_id is not None:
            if current.parent_task_id == potential_ancestor_id:
                return True
            current = current.parent_task
            if current is None:
                break
        return False

    def _validate_parent_relationship(
        self, pre_task: Task | None, post_task: Task | None
    ):
        # if pre_task is an ancestor of post_task then we can't allow and vice-versa
        if self._is_ancestor(pre_task.id, post_task):
            raise HTTPException(
                400,
                f"Can't create dependency: '{pre_task.title}' is an ancestor of '{post_task.title}'",
            )

        if self._is_ancestor(post_task.id, pre_task):
            raise HTTPException(
                400,
                f"Can't create dependency: '{post_task.title}' is an ancestor of '{pre_task.title}'",
            )
        return True

    def _validate_status(self, pre_task: Task, post_task: Task):
        if pre_task.status == TaskStatus.DELETED.value:
            raise HTTPException(400, "Can't delete pre_task it has dependencies")

        if post_task.status == TaskStatus.DELETED.value:
            return True

        if (
            pre_task.status != TaskStatus.COMPLETED.value
            and post_task.status != TaskStatus.ICEBOX.value
        ):
            raise HTTPException(
                400,
                f"post_task: '{post_task.title}' status should be 'icebox' until pre_task: '{pre_task.title}' is 'completed'",
            )
        return True

    def _check_cycle(self, pre_task: Task, post_task: Task, visited=None):
        if visited is None:
            visited = set()

        if pre_task.id in visited:
            return True

        visited.add(pre_task.id)

        for dependency in pre_task.depends_on_tasks:
            if dependency.id == post_task.id:
                return True
            if self._check_cycle(dependency, post_task, visited):
                return True

        return False

    def can_create_dependency(self, pre_task: Task, post_task: Task) -> bool:
        if pre_task in post_task.depends_on_tasks:
            raise HTTPException(
                400, f"{post_task.title} already depends on {pre_task.title}"
            )

        self._validate_parent_relationship(pre_task, post_task)

        self._validate_status(pre_task, post_task)

        if self._check_cycle(pre_task, post_task):
            raise HTTPException(400, "Circular dependency detected")
    
        return True

    def validate_post_task_status(
        self, pre_task: Task, new_post_task_status: TaskStatus
    ):
        if pre_task.status == TaskStatus.DELETED.value:
            raise HTTPException(400, "Can't update task, it depends on a deleted task")

        if new_post_task_status == TaskStatus.DELETED:
            return True

        if (
            pre_task.status != TaskStatus.COMPLETED.value
            and new_post_task_status != TaskStatus.ICEBOX
        ):
            raise HTTPException(
                400,
                f"this task status should be 'icebox' until pre_task: '{pre_task.title}' is 'completed'",
            )
        return True
