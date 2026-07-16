"""
Authentication and Authorization service.
Uses JWT tokens for API authentication and role-based access control.
"""

import os
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("soc_backend")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme-in-production-use-a-strong-random-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)


def _base64url_encode(data: bytes) -> str:
    return json.dumps(data, default=str)


def _base64url_decode(s: str):
    import base64
    return base64.urlsafe_b64decode(s)


def _create_jwt(payload: dict) -> str:
    import base64
    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).rstrip(b"=").decode()
    signature_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(SECRET_KEY.encode(), signature_input.encode(), hashlib.sha256).hexdigest()
    return f"{header_b64}.{payload_b64}.{signature}"


def _verify_jwt(token: str) -> Optional[dict]:
    import base64
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature = parts
        expected_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(SECRET_KEY.encode(), expected_input.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload_data = json.loads(base64.urlsafe_b64decode(payload_b64))
        exp = payload_data.get("exp")
        if exp:
            exp_dt = datetime.fromisoformat(exp) if isinstance(exp, str) else datetime.fromtimestamp(exp)
            if exp_dt < datetime.now():
                return None
        return payload_data
    except Exception:
        return None


def create_access_token(username: str, role: str = "analyst") -> str:
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.now().isoformat(),
        "exp": (datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).isoformat(),
    }
    return _create_jwt(payload)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = _verify_jwt(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if credentials is None:
        return None
    payload = _verify_jwt(credentials.credentials)
    return payload


USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "analyst": {"password": "analyst123", "role": "analyst"},
    "viewer": {"password": "viewer123", "role": "viewer"},
}


class AuthService:
    def __init__(self, db=None):
        self.db = db

    async def authenticate(self, username: str, password: str) -> Optional[dict]:
        user = USERS_DB.get(username)
        if user and user["password"] == password:
            return {"username": username, "role": user["role"]}
        return None

    async def get_user(self, username: str) -> Optional[dict]:
        user = USERS_DB.get(username)
        if user:
            return {"username": username, "role": user["role"]}
        return None
