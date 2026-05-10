"""
Pytest configuration and shared fixtures for the pioneer-trader test suite.

This module is loaded by pytest BEFORE any test file is imported.  It sets
the environment variables that config.py requires at startup so that the
server-side startup validation guard does not abort the process during tests.
"""

import os

# Provide dummy secrets so config.py's startup validation guard does not raise.
# These are intentionally fixed, well-known test values — they are never used
# in production and carry no real credentials.  DO NOT copy them to .env.
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-suite-32chars!")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")

# Disable Redis by default in the test environment; no Redis server is running.
os.environ.setdefault("REDIS_ENABLED", "False")
