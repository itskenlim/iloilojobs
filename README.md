# Iloilo Jobs

Centralized Iloilo BPO job board. Python providers scrape career sites into `jobs.json`; a Next.js static export renders the board.

## Layout

```
scrapers/     # Python package (providers, pipeline, CLI)
web/          # Next.js static export
cache/raw/    # latest raw provider payloads (gitignored)
logs/         # scraper.log (gitignored)
```

## Scrapers

```bash
cd scrapers
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m iloilo_jobs.cli scrape --providers carelon iqor
```

Pipeline: **collect → normalize → deduplicate → validate → writer**.

Providers register with `@provider`. Company branding lives in `src/iloilo_jobs/companies/*.json`.

Current providers: **Carelon**, **iQor**, **WNS**, **Concentrix**, **RELX**, **Nearsol**, **Inspiro**, **Transcom**, **TELUS Digital**.

## Web

```bash
cd web
npm install
npm run build   # output: web/out (static)
npm run dev
```

UI reads data through `JsonJobRepository` (`src/lib/job-repository.ts`).

## CI

`.github/workflows/scrape-and-deploy.yml` runs every 6 hours: scrape → build → commit data → deploy GitHub Pages.
# iloilojobs
