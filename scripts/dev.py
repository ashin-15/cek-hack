"""Start local servers. Explicitly never trains or seeds at application startup."""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "energy.sqlite3").exists():
    raise SystemExit("Prepare the demo first: .venv/bin/python scripts/train.py")
children = []
try:
    children.append(
        subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
            cwd=ROOT,
        )
    )
    children.append(
        subprocess.Popen(["npm", "run", "dev", "--prefix", "frontend"], cwd=ROOT)
    )
    print("Open http://127.0.0.1:5173 — press Ctrl+C to stop both servers.", flush=True)
    while all(p.poll() is None for p in children):
        time.sleep(0.5)
finally:
    for p in children:
        if p.poll() is None:
            p.terminate()
    for p in children:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
