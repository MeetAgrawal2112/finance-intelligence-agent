# tests/test_auth.py
"""Auth endpoint tests — register, login, JWT, profile."""

import pytest

class TestRegister:
    """Registration tests."""

    def test_register_success(self, client):
        """Valid data se register ho jao."""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "securepass123",
            "currency": "INR"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["full_name"] == "New User"
        # Password kabhi response mein nahi aana chahiye
        assert "password" not in data["data"]
        assert "hashed_password" not in data["data"]

    def test_register_duplicate_email(self, client, test_user):
        """Duplicate email pe error aana chahiye."""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",  # Already exists
            "full_name": "Another User",
            "password": "securepass123",
        })
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()

    def test_register_invalid_email(self, client):
        """Invalid email pe validation error."""
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "full_name": "Test",
            "password": "securepass123",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Short password pe validation error."""
        response = client.post("/api/v1/auth/register", json={
            "email": "test2@example.com",
            "full_name": "Test User",
            "password": "short",  # Too short
        })
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        """Required fields missing pe error."""
        response = client.post("/api/v1/auth/register", json={
            "email": "test3@example.com",
            # Missing full_name and password
        })
        assert response.status_code == 422


class TestLogin:
    """Login tests."""

    def test_login_success(self, client, test_user):
        """Valid credentials se login."""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == "test@example.com"

    def test_login_wrong_password(self, client, test_user):
        """Wrong password pe 401."""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()

    def test_login_nonexistent_email(self, client):
        """Non-existent email pe 401."""
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "somepassword123"
        })
        assert response.status_code == 401

    def test_login_case_insensitive_email(self, client, test_user):
        """Email case insensitive hona chahiye."""
        response = client.post("/api/v1/auth/login", json={
            "email": "TEST@EXAMPLE.COM",
            "password": "testpassword123"
        })
        assert response.status_code == 200


class TestProtectedRoutes:
    """JWT protection tests."""

    def test_get_me_success(self, client, auth_headers):
        """Valid token se /me access."""
        response = client.get("/api/v1/auth/me",
                            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "test@example.com"

    def test_get_me_no_token(self, client):
        """Bina token ke 403."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_get_me_invalid_token(self, client):
        """Invalid token pe 403."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        assert response.status_code == 401 or response.status_code == 403

    def test_logout(self, client, auth_headers):
        """Logout endpoint kaam karta hai."""
        response = client.post("/api/v1/auth/logout",
                             headers=auth_headers)
        assert response.status_code == 200

    def test_token_refresh(self, client, test_user):
        """Refresh token se naya access token lo."""
        # Login karo
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        refresh_token = login_resp.json()["data"]["refresh_token"]

        # Refresh karo
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]

    def test_update_profile(self, client, auth_headers):
        """Profile update karo."""
        response = client.put(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["full_name"] == "Updated Name"

    def test_change_password(self, client, auth_headers):
        """Password change karo."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        """Wrong current password pe error."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == 400