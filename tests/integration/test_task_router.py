import pytest


class TestGetAllTasks:
    def test_returns_tasks(self, client, manager_headers):
        # Create a task first
        create_resp = client.post(
            "/manager/tasks/",
            json={"title": "Test Task"},
            headers=manager_headers,
        )
        assert create_resp.status_code == 200, f"Failed to create task: {create_resp.json()}"

        response = client.get("/tasks/", headers=manager_headers)

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_unauthorized_without_token(self, client):
        response = client.get("/tasks/")

        assert response.status_code == 401


class TestCreateTask:
    def test_create_task_success(self, client, manager_headers):
        response = client.post(
            "/manager/tasks/",
            json={
                "title": "New Task",
                "description": "Task description",
                "priority": "high",
            },
            headers=manager_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["priority"] == "high"
        assert data["status"] == "icebox"

    def test_create_task_with_defaults(self, client, manager_headers):
        response = client.post(
            "/manager/tasks/",
            json={"title": "Minimal Task"},
            headers=manager_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["status"] == "icebox"
        assert data["priority"] == "low"

    def test_create_task_forbidden_for_member(self, client, member_headers):
        response = client.post(
            "/manager/tasks/",
            json={"title": "Test Task"},
            headers=member_headers,
        )

        # Member role gets 403 Forbidden from require_manager
        assert response.status_code == 403


class TestUpdateTask:
    def test_manager_can_update_own_task(self, client, manager_headers):
        # Create task
        create_response = client.post(
            "/manager/tasks/",
            json={"title": "Original Title"},
            headers=manager_headers,
        )
        task_id = create_response.json()["id"]

        # Update task
        response = client.patch(
            f"/manager/tasks/{task_id}",
            json={"title": "Updated Title", "priority": "high"},
            headers=manager_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "high"


class TestDeleteTask:
    def test_manager_can_delete_own_task(self, client, manager_headers):
        # Create task
        create_response = client.post(
            "/manager/tasks/",
            json={"title": "Task to Delete"},
            headers=manager_headers,
        )
        task_id = create_response.json()["id"]

        # Delete task
        response = client.delete(
            f"/manager/tasks/{task_id}",
            headers=manager_headers,
        )

        assert response.status_code == 200

        # Verify task is deleted
        get_response = client.get(
            f"/tasks/{task_id}",
            headers=manager_headers,
        )
        assert get_response.status_code == 404


class TestTaskDependency:
    def test_add_dependency_success(self, client, manager_headers):
        # Create pre-task (completed)
        pre_task = client.post(
            "/manager/tasks/",
            json={"title": "Pre Task", "status": "completed"},
            headers=manager_headers,
        ).json()

        # Create post-task (icebox)
        post_task = client.post(
            "/manager/tasks/",
            json={"title": "Post Task", "status": "icebox"},
            headers=manager_headers,
        ).json()

        # Add dependency
        response = client.post(
            f"/manager/tasks/{post_task['id']}/blocked-by",
            json={"pre_task_id": pre_task["id"]},
            headers=manager_headers,
        )

        assert response.status_code == 200

    def test_add_dependency_fails_for_invalid_status(self, client, manager_headers):
        # Create pre-task (not completed)
        pre_task = client.post(
            "/manager/tasks/",
            json={"title": "Pre Task", "status": "in_progress"},
            headers=manager_headers,
        ).json()

        # Create post-task (not icebox)
        post_task = client.post(
            "/manager/tasks/",
            json={"title": "Post Task", "status": "in_progress"},
            headers=manager_headers,
        ).json()

        # Try to add dependency
        response = client.post(
            f"/manager/tasks/{post_task['id']}/blocked-by",
            json={"pre_task_id": pre_task["id"]},
            headers=manager_headers,
        )

        assert response.status_code == 400
        assert "icebox" in response.json()["detail"]
