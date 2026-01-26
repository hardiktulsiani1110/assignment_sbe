from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from services.task_dependency_service import TaskDependencyService


@pytest.fixture
def service():
    return TaskDependencyService()


def make_mock_task(
    task_id=None,
    title=None,
    status="icebox",
    parent_task=None,
    parent_task_id=None,
    depends_on_tasks=None,
):
    """Factory for creating mock tasks"""
    task = MagicMock()
    task.id = task_id or uuid4()
    task.title = title or f"Task {task.id}"
    task.status = status
    task.parent_task = parent_task
    task.parent_task_id = parent_task_id
    task.depends_on_tasks = depends_on_tasks or []
    return task


class TestIsAncestor:
    def test_returns_false_when_no_parent(self, service):
        task = make_mock_task(parent_task_id=None)
        assert service._is_ancestor(uuid4(), task) is False

    def test_returns_true_when_direct_parent(self, service):
        parent_id = uuid4()
        parent = make_mock_task(task_id=parent_id, parent_task_id=None)
        child = make_mock_task(parent_task_id=parent_id, parent_task=parent)

        assert service._is_ancestor(parent_id, child) is True

    def test_returns_false_when_not_ancestor(self, service):
        other_id = uuid4()
        parent = make_mock_task(parent_task_id=None)
        child = make_mock_task(parent_task_id=parent.id, parent_task=parent)

        assert service._is_ancestor(other_id, child) is False

    def test_returns_true_when_grandparent(self, service):
        grandparent_id = uuid4()
        grandparent = make_mock_task(task_id=grandparent_id, parent_task_id=None)
        parent = make_mock_task(parent_task_id=grandparent_id, parent_task=grandparent)
        child = make_mock_task(parent_task_id=parent.id, parent_task=parent)

        assert service._is_ancestor(grandparent_id, child) is True


class TestCheckCycle:
    def test_no_cycle_returns_false(self, service):
        task_a = make_mock_task(depends_on_tasks=[])
        task_b = make_mock_task(depends_on_tasks=[])

        assert service._check_cycle(task_a, task_b) is False

    def test_direct_cycle_returns_true(self, service):
        task_a = make_mock_task()
        task_b = make_mock_task()
        task_a.depends_on_tasks = [task_b]

        assert service._check_cycle(task_a, task_b) is True

    def test_indirect_cycle_returns_true(self, service):
        task_a = make_mock_task()
        task_b = make_mock_task()
        task_c = make_mock_task()

        task_b.depends_on_tasks = [task_c]
        task_a.depends_on_tasks = [task_b]

        assert service._check_cycle(task_a, task_c) is True


class TestValidateStatus:
    def test_allows_when_pre_task_completed(self, service):
        pre_task = make_mock_task(status="completed")
        post_task = make_mock_task(status="in_progress")

        result = service._validate_status(pre_task, post_task)
        assert result is True

    def test_allows_when_post_task_icebox(self, service):
        pre_task = make_mock_task(status="in_progress")
        post_task = make_mock_task(status="icebox")

        result = service._validate_status(pre_task, post_task)
        assert result is True

    def test_raises_when_pre_task_deleted(self, service):
        pre_task = make_mock_task(status="deleted")
        post_task = make_mock_task(status="icebox")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_status(pre_task, post_task)
        assert exc_info.value.status_code == 400

    def test_raises_when_invalid_status_combination(self, service):
        pre_task = make_mock_task(status="in_progress")
        post_task = make_mock_task(status="in_progress")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_status(pre_task, post_task)
        assert exc_info.value.status_code == 400
        assert "icebox" in str(exc_info.value.detail)


class TestCanCreateDependency:
    def test_raises_when_dependency_already_exists(self, service):
        pre_task = make_mock_task(status="completed")
        post_task = make_mock_task(status="icebox")
        post_task.depends_on_tasks = [pre_task]

        with pytest.raises(HTTPException) as exc_info:
            service.can_create_dependency(pre_task, post_task)
        assert "already depends on" in str(exc_info.value.detail)

    def test_raises_when_pre_task_is_ancestor(self, service):
        pre_task_id = uuid4()
        pre_task = make_mock_task(
            task_id=pre_task_id, status="completed", parent_task_id=None
        )
        post_task = make_mock_task(
            status="icebox", parent_task_id=pre_task_id, parent_task=pre_task
        )

        with pytest.raises(HTTPException) as exc_info:
            service.can_create_dependency(pre_task, post_task)
        assert "ancestor" in str(exc_info.value.detail)

    def test_raises_when_circular_dependency(self, service):
        task_a = make_mock_task(status="completed")
        task_b = make_mock_task(status="icebox")
        task_a.depends_on_tasks = [task_b]
        task_b.depends_on_tasks = []

        with pytest.raises(HTTPException) as exc_info:
            service.can_create_dependency(task_a, task_b)
        assert "Circular" in str(exc_info.value.detail)

    def test_success_when_valid_dependency(self, service):
        pre_task = make_mock_task(status="completed", depends_on_tasks=[])
        post_task = make_mock_task(status="icebox", depends_on_tasks=[])

        result = service.can_create_dependency(pre_task, post_task)
        assert result is True
