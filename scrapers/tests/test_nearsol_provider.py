from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.nearsol import map_nearsol_item, parse_nearsol_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_nearsol_fixture():
    raw = json.loads((FIXTURES / "nearsol_wp.json").read_text(encoding="utf-8"))
    jobs = parse_nearsol_payload(raw)
    assert len(jobs) == 9
    assert all(j.company_id == "nearsol" for j in jobs)
    assert all(j.source == "wordpress" for j in jobs)


def test_nearsol_iloilo_location_extracted():
    raw = json.loads((FIXTURES / "nearsol_wp.json").read_text(encoding="utf-8"))
    iloilo_jobs = [
        map_nearsol_item(item)
        for item in raw["items"]
        if "Iloilo" in (item.get("content") or {}).get("rendered", "")
    ]
    assert len(iloilo_jobs) >= 1
    assert all(j.city == "Iloilo" for j in iloilo_jobs)
    assert all(j.source_url.startswith("https://nearsol.com/") for j in iloilo_jobs)
