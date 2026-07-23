from __future__ import annotations

from pathlib import Path

from iloilo_jobs.providers.inspiro import parse_inspiro_careers_html, parse_inspiro_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_inspiro_html_fixture():
    html = (FIXTURES / "inspiro_careers.html").read_text(encoding="utf-8")
    jobs = parse_inspiro_careers_html(html)
    assert len(jobs) >= 5
    assert all(j.company_id == "inspiro" for j in jobs)
    assert all(j.source == "html" for j in jobs)
    assert all(j.city == "Iloilo" for j in jobs)
    assert all(j.source_url.startswith("https://inspiro.com/careers/") for j in jobs)


def test_inspiro_payload_envelope():
    html = (FIXTURES / "inspiro_careers.html").read_text(encoding="utf-8")
    jobs = parse_inspiro_payload({"html": html})
    titles = {j.title for j in jobs}
    assert any("Customer Service" in t for t in titles)
