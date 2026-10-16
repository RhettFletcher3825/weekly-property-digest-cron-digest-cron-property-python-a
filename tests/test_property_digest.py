from datetime import date

from property_digest import (
    DigestRequest,
    InspectionReminder,
    MaintenanceRequest,
    TenantDocument,
    build_digest,
)


def test_digest_prioritizes_urgent_work_and_only_lists_missing_documents() -> None:
    request = DigestRequest(
        audience_email="manager@example.com",
        week_ending=date(2026, 10, 4),
        maintenance_requests=(
            MaintenanceRequest("Maple House", "Replace hallway light", "routine", date(2026, 9, 27)),
            MaintenanceRequest("Cedar Court", "Restore boiler pressure", "urgent", date(2026, 9, 28)),
        ),
        tenant_documents=(
            TenantDocument("Maple House", "Sam Lee", "Renewal form", date(2026, 10, 3), True),
            TenantDocument("Cedar Court", "Alex Morgan", "Insurance certificate", date(2026, 10, 2), False),
        ),
        inspection_reminders=(
            InspectionReminder("Cedar Court", "Fire alarm", date(2026, 10, 6)),
        ),
    )

    digest = build_digest(request)

    assert digest.body.index("Restore boiler pressure") < digest.body.index("Replace hallway light")
    assert "Alex Morgan - Insurance certificate" in digest.body
    assert "Sam Lee" not in digest.body
    assert "Fire alarm on 2026-10-06" in digest.body

