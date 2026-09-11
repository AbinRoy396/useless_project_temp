"""Small dependency-free bearer-token implementation for a single admin account.

Use a real SSO/OIDC provider before multi-admin production deployment.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)
TOKEN_TTL_SECONDS = 60 * 60 * 8


def _secret() -> bytes:
    return os.getenv("ADMIN_TOKEN_SECRET", "local-demo-secret-change-before-production").encode()


def authenticate(username: str, password: str) -> bool:
    expected_user = os.getenv("ADMIN_USERNAME", "admin")
    expected_password = os.getenv("ADMIN_PASSWORD", "change-me-before-production")
    return secrets.compare_digest(username, expected_user) and secrets.compare_digest(password, expected_password)


def issue_token(username: str) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"sub": username, "exp": int(time.time()) + TOKEN_TTL_SECONDS}).encode()).decode().rstrip("=")
    signature = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def current_admin(credentials: HTTPAuthorizationCredentials | None = Security(security)) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Admin authentication required")
    try:
        payload, signature = credentials.credentials.rsplit(".", 1)
        expected = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
        decoded = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if not hmac.compare_digest(signature, expected) or decoded["exp"] < time.time():
            raise ValueError
        return decoded["sub"]
    except (ValueError, KeyError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired admin token")
