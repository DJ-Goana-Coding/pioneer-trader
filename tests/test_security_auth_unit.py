#!/usr/bin/env python3
"""Unit tests for backend/core/security.py authentication functions."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta


class TestVerifyAdminCredentials(unittest.TestCase):
    """Test verify_admin_credentials function."""

    @patch("backend.core.security.settings")
    def test_correct_credentials(self, mock_settings):
        mock_settings.ADMIN_USERNAME = "admin"
        mock_settings.ADMIN_PASSWORD = "secret123"
        from backend.core.security import verify_admin_credentials
        self.assertTrue(verify_admin_credentials("admin", "secret123"))

    @patch("backend.core.security.settings")
    def test_incorrect_username(self, mock_settings):
        mock_settings.ADMIN_USERNAME = "admin"
        mock_settings.ADMIN_PASSWORD = "secret123"
        from backend.core.security import verify_admin_credentials
        self.assertFalse(verify_admin_credentials("wrong_user", "secret123"))

    @patch("backend.core.security.settings")
    def test_incorrect_password(self, mock_settings):
        mock_settings.ADMIN_USERNAME = "admin"
        mock_settings.ADMIN_PASSWORD = "secret123"
        from backend.core.security import verify_admin_credentials
        self.assertFalse(verify_admin_credentials("admin", "wrong_password"))


class TestCreateAccessToken(unittest.TestCase):
    """Test create_access_token function."""

    @patch("backend.core.security.settings")
    def test_returns_string(self, mock_settings):
        mock_settings.SECRET_KEY = "test-secret-key"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        from backend.core.security import create_access_token
        token = create_access_token("testuser")
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    @patch("backend.core.security.settings")
    def test_custom_expires_minutes(self, mock_settings):
        mock_settings.SECRET_KEY = "test-secret-key"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        from backend.core.security import create_access_token
        token = create_access_token("testuser", expires_minutes=60)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)


class TestDecodeToken(unittest.TestCase):
    """Test decode_token function."""

    @patch("backend.core.security.settings")
    def test_decode_valid_token(self, mock_settings):
        mock_settings.SECRET_KEY = "test-secret-key"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        from backend.core.security import create_access_token, decode_token
        token = create_access_token("testuser")
        subject = decode_token(token)
        self.assertEqual(subject, "testuser")

    @patch("backend.core.security.settings")
    def test_decode_invalid_token(self, mock_settings):
        mock_settings.SECRET_KEY = "test-secret-key"
        from backend.core.security import decode_token
        result = decode_token("invalid.token.string")
        self.assertIsNone(result)

    @patch("backend.core.security.settings")
    def test_decode_expired_token(self, mock_settings):
        mock_settings.SECRET_KEY = "test-secret-key"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        from jose import jwt
        expired_payload = {
            "sub": "testuser",
            "exp": datetime.utcnow() - timedelta(minutes=10),
        }
        expired_token = jwt.encode(expired_payload, "test-secret-key", algorithm="HS256")
        from backend.core.security import decode_token
        result = decode_token(expired_token)
        self.assertIsNone(result)


class TestGetCurrentAdmin(unittest.TestCase):
    """Test get_current_admin async function."""

    @patch("backend.core.security.settings")
    def test_invalid_token_raises_401(self, mock_settings):
        mock_settings.SECRET_KEY = "test-secret-key"
        mock_settings.ADMIN_USERNAME = "admin"
        from backend.core.security import get_current_admin
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(get_current_admin(token="invalid.token.here"))
        self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
