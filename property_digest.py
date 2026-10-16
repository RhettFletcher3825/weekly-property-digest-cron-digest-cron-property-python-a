"""Typed property records and the weekly digest decision."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MaintenanceRequest:
    property_name: str
    summary: str
    priority: str
    opened_on: date


@dataclass(frozen=True)
class TenantDocument:
    property_name: str
    tenant_name: str
    document_name: str
    due_on: date
    received: bool


@dataclass(frozen=True)
class InspectionReminder:
    property_name: str
    inspection_type: str
    scheduled_for: date


@dataclass(frozen=True)
class DigestRequest:
    audience_email: str
    week_ending: date
    maintenance_requests: tuple[MaintenanceRequest, ...]
    tenant_documents: tuple[TenantDocument, ...]
    inspection_reminders: tuple[InspectionReminder, ...]


@dataclass(frozen=True)
class DigestEmail:
    recipient: str
    subject: str
    body: str


def build_digest(request: DigestRequest) -> DigestEmail:
    """Put urgent work first and omit tenant documents already received."""
    priority_order = {"urgent": 0, "routine": 1}
    maintenance = sorted(
        request.maintenance_requests,
        key=lambda item: (priority_order.get(item.priority, 2), item.opened_on, item.property_name),
    )
    missing_documents = sorted(
        (item for item in request.tenant_documents if not item.received),
        key=lambda item: (item.due_on, item.property_name, item.tenant_name),
    )
    inspections = sorted(
        request.inspection_reminders,
        key=lambda item: (item.scheduled_for, item.property_name),
    )

    lines = [f"Property digest for week ending {request.week_ending.isoformat()}", ""]
    lines.extend(["Maintenance", *[
        f"- [{item.priority.upper()}] {item.property_name}: {item.summary} (opened {item.opened_on.isoformat()})"
        for item in maintenance
    ]])
    lines.extend(["", "Tenant documents still due", *[
        f"- {item.property_name}: {item.tenant_name} - {item.document_name} by {item.due_on.isoformat()}"
        for item in missing_documents
    ]])
    lines.extend(["", "Upcoming inspections", *[
        f"- {item.property_name}: {item.inspection_type} on {item.scheduled_for.isoformat()}"
        for item in inspections
    ]])
    return DigestEmail(
        recipient=request.audience_email,
        subject=f"Weekly property digest - {request.week_ending.isoformat()}",
        body="\n".join(lines),
    )

