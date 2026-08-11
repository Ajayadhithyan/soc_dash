"""
Agent authentication service.

Endpoint Detection Agents authenticate with a per-agent API token sent in the
`X-Agent-Token` header. The plaintext token is never persisted — only an
HMAC-SHA256 hash (with a random per-row salt) is stored in MongoDB.

Bootstrap flow:
    * If `AGENT_TOKEN` is set in the environment, the backend registers that
      token on startup (and logs it is active).
    * Otherwise, if no token exists for `AGENT_AGENT_ID`, the backend generates
      one, stores its hash, and logs the plaintext token once so you can paste
      it into the agent's configuration.
"""

import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timezone
from typing import Optional

from backend import config

logger = logging.getLogger("soc_backend")


def _hash_token(token: str, key: str) -> str:
    """Deterministic HMAC-SHA256 fingerprint of a token using a fixed key."""
    return hmac.new(key.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()


class AgentAuthService:
    def __init__(self, db=None):
        self.db = db

    async def _upsert_token(
        self,
        token: str,
        agent_id: str,
        hostname: str = "",
        is_bootstrap: bool = False,
    ) -> dict:
        """Register a token under an agent identity. Idempotent by token_id."""
        if self.db is None:
            raise RuntimeError("AgentAuthService has no database handle")

        token_id = _hash_token(token, "token-id")[:16]
        salt = secrets.token_hex(16)
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "token_id": token_id,
            "agent_id": agent_id,
            "hostname": hostname,
            "salt": salt,
            "token_hash": _hash_token(token, salt),
            "is_bootstrap": is_bootstrap,
            "created_at": now,
            "last_seen": now,
            "active": True,
        }
        await self.db["agent_tokens"].replace_one({"token_id": token_id}, doc, upsert=True)
        return doc

    async def verify(self, token: Optional[str]) -> Optional[dict]:
        """Validate an agent token; returns the verified identity if valid."""
        if not token or self.db is None:
            return None

        token_id = _hash_token(token, "token-id")[:16]
        row = await self.db["agent_tokens"].find_one({"token_id": token_id, "active": True})
        if not row:
            return None

        expected = _hash_token(token, row.get("salt", ""))
        if not hmac.compare_digest(str(row.get("token_hash", "")), expected):
            return None

        return {
            "agent_id": row.get("agent_id", ""),
            "hostname": row.get("hostname", ""),
            "is_bootstrap": row.get("is_bootstrap", False),
        }

    async def ensure_bootstrap_token(self) -> Optional[str]:
        """
        Guarantee a working agent token exists. Returns the plaintext token
        when one was just generated (so it can be logged for configuration),
        otherwise None.
        """
        if self.db is None:
            return None

        if config.AGENT_TOKEN:
            await self._upsert_token(
                config.AGENT_TOKEN,
                config.AGENT_AGENT_ID,
                hostname="bootstrap",
                is_bootstrap=True,
            )
            logger.info("[AgentAuth] Bootstrapped agent token for agent_id=%s", config.AGENT_AGENT_ID)
            return config.AGENT_TOKEN

        existing = await self.db["agent_tokens"].find_one({"agent_id": config.AGENT_AGENT_ID})
        if existing:
            return None

        token = secrets.token_urlsafe(32)
        await self._upsert_token(
            token,
            config.AGENT_AGENT_ID,
            hostname="bootstrap",
            is_bootstrap=True,
        )
        logger.warning(
            "[Agent] Generated new agent token for agent_id=%s: %s",
            config.AGENT_AGENT_ID,
            token,
        )
        return token