import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
DERIVED = ROOT / "data/derived"
ARTIFACTS = ROOT / "artifacts"
PRIMARY = "synthetic_smart_meter_15min.csv"
LABELLED = "ai_energy_intelligence_dataset.csv"
DAILY = "Intelligent_abnormal_electricity_usage.csv"
METER = "SM-KL-001"
TZ = "Asia/Kolkata"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def records(frame):
    return json.loads(frame.to_json(orient="records", date_format="iso"))
