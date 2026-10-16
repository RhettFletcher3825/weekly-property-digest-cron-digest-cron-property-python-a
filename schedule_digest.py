"""Register the public digest webhook as a weekly Infrai cron job."""

from __future__ import annotations

import os

import infrai


def schedule_weekly_digest() -> str:
    data = infrai.cron.create(
        cron_expr="0 8 * * 1",
        task=os.environ["DIGEST_WEBHOOK_URL"],
        idempotency_key="property-management-weekly-digest-v1",
    )
    return str(data["job_id"])


if __name__ == "__main__":
    print(f"Scheduled weekly digest as job {schedule_weekly_digest()}")
