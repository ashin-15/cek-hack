"""Tests for AC-003: Immutability of raw CSV datasets."""
from pathlib import Path
from backend.ml.inventory import compute_file_hash_and_rows


EXPECTED_HASHES = {
    "data/synthetic_smart_meter_15min.csv": "1ad55014cd693c278a29639c9e33c6aee5d23c83f9781964bc187cf368b620ab",
    "data/Intelligent_abnormal_electricity_usage.csv": "fc18db41237265c3fc779303c3e0baa5741635a8efcc1349eaa3848af6c34eff",
}


def test_raw_csv_hashes_unchanged():
    for rel_path, expected_hash in EXPECTED_HASHES.items():
        p = Path(rel_path)
        assert p.exists()
        current_hash, _, _, _ = compute_file_hash_and_rows(p)
        assert current_hash == expected_hash, f"Raw data modified for {rel_path}! Expected {expected_hash}, got {current_hash}"
