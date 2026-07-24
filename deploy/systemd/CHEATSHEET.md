# Iloilo Jobs scraper — systemd cheat sheet

Service: `iloilo-jobs-scrape.service`  
Timer: `iloilo-jobs-scrape.timer`  
Repo: `~/dev/personal/iloilojobs`

Scraping runs on the always-on home laptop (not GitHub Actions). The timer kicks off a scrape + git push of `web/public/data/*.json`.

---

## Status

```bash
systemctl status iloilo-jobs-scrape.timer
systemctl status iloilo-jobs-scrape.service
systemctl list-timers | grep iloilo
systemctl is-enabled iloilo-jobs-scrape.timer
```

## Run now (manual scrape + push)

```bash
sudo systemctl start iloilo-jobs-scrape.service
```

## Enable / disable schedule

```bash
# turn timer on (every ~6h)
sudo systemctl enable --now iloilo-jobs-scrape.timer

# stop future runs, keep unit installed
sudo systemctl disable --now iloilo-jobs-scrape.timer

# pause without disabling
sudo systemctl stop iloilo-jobs-scrape.timer

# resume
sudo systemctl start iloilo-jobs-scrape.timer
```

## Logs

```bash
# last run
sudo journalctl -u iloilo-jobs-scrape.service -n 80 --no-pager

# follow live
sudo journalctl -u iloilo-jobs-scrape.service -f

# today’s logs
sudo journalctl -u iloilo-jobs-scrape.service --since today

# errors only
sudo journalctl -u iloilo-jobs-scrape.service -p err -n 50
```

## After `git pull` (if unit files changed)

```bash
cd ~/dev/personal/iloilojobs
git pull
sudo cp deploy/systemd/iloilo-jobs-scrape.{service,timer} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart iloilo-jobs-scrape.timer
```

## Run script without systemd

```bash
cd ~/dev/personal/iloilojobs
./scripts/scrape-and-push.sh

# scrape only (no git push)
scrapers/.venv/bin/iloilo-jobs scrape
```

## Quick failure checks

```bash
# did last service fail?
systemctl show iloilo-jobs-scrape.service -p Result -p ExecMainStatus

# SSH to GitHub still works? (needed for push)
ssh -T git@github.com
```

## Useful paths

| What | Path |
| --- | --- |
| Unit files (installed) | `/etc/systemd/system/iloilo-jobs-scrape.*` |
| Unit templates (repo) | `deploy/systemd/` |
| Scrape log file | `~/dev/personal/iloilojobs/logs/` |
| Job data | `~/dev/personal/iloilojobs/web/public/data/` |

## Note on `git push` rejected

If your desktop `git push` is rejected, the laptop likely pushed a `chore: refresh scraped job data` commit. Reconcile with:

```bash
git pull --rebase origin main   # or: git pull origin main
git push
```
