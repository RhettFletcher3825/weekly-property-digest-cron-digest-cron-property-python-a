"""Runnable webhook that builds and sends the scheduled property digest."""

from __future__ import annotations

import json
import os
import smtplib
from datetime import date
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from property_digest import (
    DigestRequest,
    InspectionReminder,
    MaintenanceRequest,
    TenantDocument,
    build_digest,
)


def load_request(path: Path) -> DigestRequest:
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return DigestRequest(
        audience_email=str(raw["audience_email"]),
        week_ending=date.fromisoformat(raw["week_ending"]),
        maintenance_requests=tuple(
            MaintenanceRequest(
                property_name=item["property_name"],
                summary=item["summary"],
                priority=item["priority"],
                opened_on=date.fromisoformat(item["opened_on"]),
            )
            for item in raw["maintenance_requests"]
        ),
        tenant_documents=tuple(
            TenantDocument(
                property_name=item["property_name"],
                tenant_name=item["tenant_name"],
                document_name=item["document_name"],
                due_on=date.fromisoformat(item["due_on"]),
                received=bool(item["received"]),
            )
            for item in raw["tenant_documents"]
        ),
        inspection_reminders=tuple(
            InspectionReminder(
                property_name=item["property_name"],
                inspection_type=item["inspection_type"],
                scheduled_for=date.fromisoformat(item["scheduled_for"]),
            )
            for item in raw["inspection_reminders"]
        ),
    )


def send_digest() -> str:
    digest = build_digest(load_request(Path(os.environ["DIGEST_INPUT_FILE"])))
    message = EmailMessage()
    message["From"] = os.environ["DIGEST_FROM_EMAIL"]
    message["To"] = digest.recipient
    message["Subject"] = digest.subject
    message.set_content(digest.body)
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587"))) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(message)
    return digest.subject


class DigestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/weekly-digest":
            self.send_error(404)
            return
        subject = send_digest()
        body = json.dumps({"sent": True, "subject": subject}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), DigestHandler).serve_forever()

