from __future__ import annotations

from iloilo_jobs.filters.location import matches_location
from iloilo_jobs.models.job import Job


def _job(**kwargs) -> Job:
    defaults = dict(
        id="x:1",
        title="Agent",
        company_id="x",
        company_name="X",
        raw_id="1",
        source="test",
        scraped_at="2026-07-23T00:00:00Z",
    )
    defaults.update(kwargs)
    return Job(**defaults)


def test_matches_iloilo_location():
    assert matches_location(_job(location="PHL-ILO-One Fintech Place, Mandurriao"))


def test_matches_iloilo_city_field():
    assert matches_location(_job(city="Iloilo 04"))


def test_matches_workday_ilo_path():
    assert matches_location(
        _job(source_url="https://example.com/job/PHL-ILO-SM-Strata/Role_JR1")
    )


def test_rejects_manila():
    assert not matches_location(
        _job(location="Taguig - BGC", city="Taguig", title="CSR Manila")
    )


def test_custom_city_cebu():
    job = _job(location="Cebu City IT Park")
    assert not matches_location(job)  # default Iloilo keywords
    assert matches_location(job, cities=["Cebu"], keywords=[])
