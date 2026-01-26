class TestLogin:
    def test_login_success(self, client, test_member):
        response = client.post(
            "/auth/login",
            json={"email": "member@test.com", "password": "testpass"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_member):
        response = client.post(
            "/auth/login",
            json={"email": "member@test.com", "password": "wrongpass"},
        )

        assert response.status_code == 401

    def test_login_user_not_found(self, client):
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@test.com", "password": "testpass"},
        )

        assert response.status_code == 404
