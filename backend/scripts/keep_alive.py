"""
keep_alive.py — Render free-tier cold-start prevention.

Pings the /wake endpoint every PING_INTERVAL seconds so the service never
hits the 15-minute inactivity threshold and spins down.

Deploy this as a Render Cron Job:
  - Command : python backend/scripts/keep_alive.py
  - Schedule: */10 * * * *   (every 10 minutes)
  - Env var : RENDER_BACKEND_URL=https://senti-mind-majc.onrender.com

The script exits after ONE successful ping — the cron scheduler is
responsible for re-running it every 10 minutes.
"""

import os
import sys
import datetime
import urllib.request
import urllib.error

BACKEND_URL = os.getenv("RENDER_BACKEND_URL", "https://senti-mind-majc.onrender.com").rstrip("/")
WAKE_PATH = "/wake"
TIMEOUT_SECONDS = 20


def ping() -> bool:
    url = BACKEND_URL + WAKE_PATH
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read().decode()
            print(f"[{ts}] ✅ WAKE OK  {url}  →  {body.strip()}")
            return True
    except urllib.error.HTTPError as exc:
        print(f"[{ts}] ⚠️  HTTP {exc.code} from {url}: {exc.reason}", file=sys.stderr)
    except urllib.error.URLError as exc:
        print(f"[{ts}] ❌ UNREACHABLE {url}: {exc.reason}", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"[{ts}] ❌ ERROR pinging {url}: {exc}", file=sys.stderr)
    return False


if __name__ == "__main__":
    success = ping()
    sys.exit(0 if success else 1)
