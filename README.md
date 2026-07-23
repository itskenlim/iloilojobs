# Iloilo Jobs

Centralized Iloilo BPO job board. Python providers scrape career sites into `jobs.json`; a Next.js static export renders the board.

**Live:** https://iloilojobs.vercel.app · Pages: https://itskenlim.github.io/iloilojobs/

## Layout

```
scrapers/          # Python package (providers, pipeline, CLI)
web/               # Next.js static export
scripts/           # local scrape-and-push helper
deploy/systemd/    # timer units for the always-on laptop
cache/raw/         # latest raw provider payloads (gitignored)
logs/              # scraper.log (gitignored)
```

## Scraping (home laptop)

iQor / TELUS block GitHub Actions IPs (`403`). Run **all** scrapes on a normal home IP instead.

### One-time setup

```bash
git clone git@github.com:itskenlim/iloilojobs.git
cd iloilojobs

cd scrapers
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cd ..

chmod +x scripts/scrape-and-push.sh
# dry run (no push if you only want scrape):
scrapers/.venv/bin/iloilo-jobs scrape
```

You only need **Python** on the laptop for scraping. `npm` is only required if you want `web/` locally (`npm install && npm run dev`).

Ensure `git push` works from that machine (SSH key or credential helper).

### systemd every 6 hours

```bash
# edit User + paths first
nano deploy/systemd/iloilo-jobs-scrape.service

sudo cp deploy/systemd/iloilo-jobs-scrape.service /etc/systemd/system/
sudo cp deploy/systemd/iloilo-jobs-scrape.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now iloilo-jobs-scrape.timer
systemctl list-timers | grep iloilo
journalctl -u iloilo-jobs-scrape.service -n 50
```

Manual run:

```bash
./scripts/scrape-and-push.sh
# or: sudo systemctl start iloilo-jobs-scrape.service
```

The script updates `web/public/data/jobs.json` + `metadata.json`, commits, and pushes. That push triggers Vercel and the Pages deploy workflow.

## Scrapers (dev)

```bash
cd scrapers
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m iloilo_jobs.cli scrape --providers carelon asurion
```

Pipeline: **collect → normalize → deduplicate → validate → writer**.

Providers register with `@provider`. Company branding lives in `src/iloilo_jobs/companies/*.json`.

Current providers: **Asurion**, **Carelon**, **Concentrix**, **Inspiro**, **iQor**, **Nearsol**, **RELX**, **TELUS Digital**, **Transcom**, **WNS**.

## Web

```bash
cd web
npm install
npm run build   # output: web/out (static)
npm run dev
```

UI reads data through `JsonJobRepository` (`src/lib/job-repository.ts`).

## CI

`.github/workflows/deploy-pages.yml` builds and deploys GitHub Pages when `web/**` changes on `main` (no cloud scrape).
