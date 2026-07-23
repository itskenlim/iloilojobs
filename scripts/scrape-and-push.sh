#!/usr/bin/env bash
# Scrape all providers and push jobs.json to GitHub (triggers Pages/Vercel).
# Intended for a home/always-on Linux box (systemd timer), not GitHub Actions.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="${ILOILO_JOBS_ROOT:-$ROOT}"
cd "$ROOT"

VENV_BIN="${ILOILO_JOBS_VENV:-$ROOT/scrapers/.venv}/bin"
if [[ ! -x "$VENV_BIN/iloilo-jobs" ]]; then
  echo "Missing $VENV_BIN/iloilo-jobs — create the venv first:" >&2
  echo "  cd $ROOT/scrapers && python3 -m venv .venv && .venv/bin/pip install -e ." >&2
  exit 1
fi

BRANCH="${ILOILO_JOBS_BRANCH:-main}"
REMOTE="${ILOILO_JOBS_REMOTE:-origin}"

echo "==> $(date -u +%Y-%m-%dT%H:%M:%SZ) pull $REMOTE/$BRANCH"
git fetch "$REMOTE" "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only "$REMOTE" "$BRANCH"

echo "==> scrape"
"$VENV_BIN/iloilo-jobs" scrape \
  --out "$ROOT/web/public/data/jobs.json" \
  --metadata "$ROOT/web/public/data/metadata.json" \
  --cache-dir "$ROOT/cache/raw" \
  --log-dir "$ROOT/logs"

git add web/public/data/jobs.json web/public/data/metadata.json

if git diff --staged --quiet; then
  echo "==> no job data changes"
  exit 0
fi

git -c user.name="${GIT_AUTHOR_NAME:-iloilo-jobs-laptop}" \
    -c user.email="${GIT_AUTHOR_EMAIL:-iloilo-jobs@localhost}" \
    commit -m "chore: refresh scraped job data"

echo "==> push"
git push "$REMOTE" "HEAD:$BRANCH"
echo "==> done"
