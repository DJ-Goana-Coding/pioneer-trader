import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.routers.auth import router


def _create_test_app():
    """Create a minimal FastAPI app with the auth router."""
    app = FastAPI()
    app.include_router(router)
    return app


app = _create_test_app()
client = TestClient(app)


class TestAuthLogin(unittest.TestCase):
    """Tests for POST /auth/login."""

    def setUp(self):
        self._orig_username = settings.ADMIN_USERNAME
        self._orig_password = settings.ADMIN_PASSWORD
        self._orig_secret = settings.SECRET_KEY
        self._orig_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        settings.ADMIN_USERNAME = "admin"
        settings.ADMIN_PASSWORD = "testpassword123"
        settings.SECRET_KEY = "testsecretkey"
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def tearDown(self):
        settings.ADMIN_USERNAME = self._orig_username
        settings.ADMIN_PASSWORD = self._orig_password
        settings.SECRET_KEY = self._orig_secret
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = self._orig_expire

    def test_login_correct_credentials_returns_200(self):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "testpassword123"},
        )
        self.assertEqual(response.status_code, 200)

    def test_login_correct_credentials_returns_access_token(self):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "testpassword123"},
        )
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertTrue(len(data["access_token"]) > 0)

    def test_login_wrong_password_returns_401(self):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 401)

    def test_login_wrong_username_returns_401(self):
        response = client.post(
            "/auth/login",
            json={"username": "baduser", "password": "testpassword123"},
        )
        self.assertEqual(response.status_code, 401)

    def test_login_empty_credentials_returns_401(self):
        response = client.post(
            "/auth/login",
            json={"username": "", "password": ""},
        )
        self.assertEqual(response.status_code, 401)


class TestAuthMe(unittest.TestCase):
    """Tests for GET /auth/me."""

    def setUp(self):
        self._orig_username = settings.ADMIN_USERNAME
        self._orig_password = settings.ADMIN_PASSWORD
        self._orig_secret = settings.SECRET_KEY
        self._orig_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        settings.ADMIN_USERNAME = "admin"
        settings.ADMIN_PASSWORD = "testpassword123"
        settings.SECRET_KEY = "testsecretkey"
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def tearDown(self):
        settings.ADMIN_USERNAME = self._orig_username
        settings.ADMIN_PASSWORD = self._orig_password
        settings.SECRET_KEY = self._orig_secret
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = self._orig_expire

    def test_me_without_token_returns_401(self):
        response = client.get("/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_me_with_invalid_token_returns_401(self):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        self.assertEqual(response.status_code, 401)

    def test_me_with_valid_token_returns_username(self):
        # First log in to get a valid token
        login_resp = client.post(
            "/auth/login",
            json={"username": "admin", "password": "testpassword123"},
        )
        token = login_resp.json()["access_token"]
        # Use the token
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "admin")
        self.assertEqual(data["role"], "admin")


if __name__ == "__main__":
    unittest.main()
