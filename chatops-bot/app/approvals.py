"""Redis-backed, expiring and atomically single-use approval grants."""
from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import Any

from redis import Redis


CONSUME_EXACT = """
local value = redis.call('GET', KEYS[1])
if value and value == ARGV[1] then
  redis.call('DEL', KEYS[1])
  return 1
end
return 0
"""


@dataclass(frozen=True)
class ApprovalGrant:
    user: str
    action: str
    arguments: dict[str, Any]


def _payload(grant: ApprovalGrant) -> str:
    return json.dumps({"user": grant.user, "action": grant.action,
                       "arguments": grant.arguments}, sort_keys=True,
                      separators=(",", ":"))


class ApprovalStore:
    def __init__(self, client: Redis, prefix: str, ttl_seconds: int = 60) -> None:
        self.client = client
        self.prefix = prefix
        self.ttl_seconds = ttl_seconds

    def _key(self, token: str) -> str:
        return f"{self.prefix}:{hashlib.sha256(token.encode()).hexdigest()}"

    def issue(self, grant: ApprovalGrant) -> str:
        token = secrets.token_urlsafe(24)
        self.client.set(self._key(token), _payload(grant), ex=self.ttl_seconds, nx=True)
        return token

    def get(self, token: str) -> ApprovalGrant | None:
        raw = self.client.get(self._key(token))
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            if (not isinstance(data, dict) or not isinstance(data.get("user"), str)
                    or not isinstance(data.get("action"), str)
                    or not isinstance(data.get("arguments"), dict)):
                return None
            return ApprovalGrant(data["user"], data["action"], data["arguments"])
        except (TypeError, json.JSONDecodeError):
            return None

    def consume_exact(self, token: str, grant: ApprovalGrant) -> bool:
        return bool(self.client.eval(CONSUME_EXACT, 1, self._key(token), _payload(grant)))

    @staticmethod
    def reference(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()[:12]
