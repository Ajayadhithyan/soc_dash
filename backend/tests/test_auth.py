"""
Tests for the authentication service.
"""

import pytest
from backend.services.auth import create_access_token, _verify_jwt


class TestAuth:
    def test_create_and_verify_token(self):
        token = create_access_token("testuser", "analyst")
        payload = _verify_jwt(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "analyst"

    def test_invalid_token(self):
        payload = _verify_jwt("invalid.token.here")
        assert payload is None

    def test_tampered_token(self):
        token = create_access_token("testuser", "analyst")
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".bad_signature"
        payload = _verify_jwt(tampered)
        assert payload is None

    def test_token_has_expiry(self):
        token = create_access_token("testuser", "admin")
        payload = _verify_jwt(token)
        assert payload is not None
        assert "exp" in payload
        assert "iat" in payload
