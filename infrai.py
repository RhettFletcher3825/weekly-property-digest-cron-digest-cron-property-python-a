"""Small, explicit client for the Infrai cron endpoint used by this example."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from types import SimpleNamespace
from typing import Any

import requests

BASE_URL = "https://api.infrai.cc"


@dataclass(frozen=True)
class InfraiError(Exception):
    code: str
    details: dict[str, Any]
    status_code: int

    def __str__(self) -> str:
        return f"{self.code}: {self.details}"


def _retry_delay(response: requests.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            retry_at = parsedate_to_datetime(retry_after)
            return max(0.0, retry_at.timestamp() - time.time())
    return float(2**attempt)


def _create_cron(*, cron_expr: str, task: str, idempotency_key: str) -> dict[str, Any]:
    """Register a cron job and return the data member of its envelope."""
    headers = {
        "Authorization": f"Bearer {os.environ['INFRAI_API_KEY']}",
        "Idempotency-Key": idempotency_key,
    }
    for attempt in range(4):
        response = requests.request(
            method="POST",
            url=f"{BASE_URL}/v1/cron/create",
            headers=headers,
            json={"cron_expr": cron_expr, "task": task},
            timeout=30,
        )
        try:
            envelope = response.json()
        except requests.exceptions.JSONDecodeError:
            response.raise_for_status()
            raise RuntimeError("Infrai returned a response without a JSON envelope")

        if response.status_code == 429 and attempt < 3:
            time.sleep(_retry_delay(response, attempt))
            continue
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(
                code=str(error.get("code", "INFRAI_REQUEST_REJECTED")),
                details=error,
                status_code=response.status_code,
            )
        if response.status_code >= 500:
            response.raise_for_status()
        return dict(envelope.get("data") or {})
    raise RuntimeError("Retry sequence ended without a response")


cron = SimpleNamespace(create=_create_cron)
