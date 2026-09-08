"""Ignition script for the Financial Scout pipeline.

Performs an authenticated POST to ``/v1/finance/analyze`` so the parser
-> yield engine linkage can be smoke-tested end-to-end.

Environment variables:
    PIONEER_API_URL       Base URL of the FastAPI service (default: http://localhost:8000)
    PIONEER_ADMIN_USER    Admin username (default: admin)
    PIONEER_ADMIN_PASS    Admin password (required)
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

import requests

DEFAULT_PAYLOAD: Dict[str, Any] = {
    "message_type": "pacs.008.001.08",
    "message_id": "IGNITE-0001",
    "creation_datetime": "2026-04-17T00:00:00Z",
    "body": {"note": "ignition smoke-test payload"},
}


def main() -> int:
    base_url = os.environ.get("PIONEER_API_URL", "http://localhost:8000").rstrip("/")
    username = os.environ.get("PIONEER_ADMIN_USER", "admin")
    password = os.environ.get("PIONEER_ADMIN_PASS")

    if not password:
        print("ERROR: PIONEER_ADMIN_PASS is not set.", file=sys.stderr)
        return 2

    try:
        login = requests.post(
            f"{base_url}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
    except requests.RequestException as exc:
        print(f"ERROR: login request failed: {exc}", file=sys.stderr)
        return 1

    if login.status_code != 200:
        print(
            f"ERROR: login failed ({login.status_code}): {login.text}",
            file=sys.stderr,
        )
        return 1

    token = login.json().get("access_token")
    if not token:
        print("ERROR: login response missing access_token.", file=sys.stderr)
        return 1

    try:
        resp = requests.post(
            f"{base_url}/v1/finance/analyze",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "payload": DEFAULT_PAYLOAD,
                "postcode": "4874",
                "latency_ms": 42.0,
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        print(f"ERROR: analyze request failed: {exc}", file=sys.stderr)
        return 1

    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except ValueError:
        print(resp.text)

    return 0 if resp.ok else 1


if __name__ == "__main__":
    sys.exit(main())
