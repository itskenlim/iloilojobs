from __future__ import annotations

import iloilo_jobs.providers  # noqa: F401
from iloilo_jobs.registry import get_providers, registered_ids


def test_providers_registered():
    ids = registered_ids()
    assert "carelon" in ids
    assert "iqor" in ids
    assert "wns" in ids
    assert "concentrix" in ids
    assert "relx" in ids
    assert "nearsol" in ids
    assert "inspiro" in ids
    assert "transcom" in ids
    assert "telus" in ids


def test_get_providers_enabled():
    providers = get_providers(enabled_only=True)
    ids = {p.company_id for p in providers}
    assert ids >= {
        "carelon",
        "iqor",
        "wns",
        "concentrix",
        "relx",
        "nearsol",
        "inspiro",
        "transcom",
        "telus",
    }
