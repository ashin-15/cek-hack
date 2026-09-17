"""Tests for AC-001 and AC-002: Dataset inventory, fingerprinting, and signature matching."""
import pytest
from pathlib import Path
from backend.ml.inventory import inventory_datasets, compute_file_hash_and_rows


def test_inventory_all_three_sources():
    descriptors = inventory_datasets("data", "configs/ml/data_contracts.yaml")
    assert len(descriptors) == 3
    assert "smart_meter_15min_v1" in descriptors
    assert "labelled_home_15min_v1" in descriptors
    assert "daily_abnormal_v1" in descriptors

    sm = descriptors["smart_meter_15min_v1"]
    assert sm.row_count == 32256
    assert len(sm.columns) == 19
    assert sm.provenance_class == "synthetic"

    daily = descriptors["daily_abnormal_v1"]
    assert daily.row_count == 10800
    assert len(daily.columns) == 15
    assert daily.provenance_class == "community-undocumented"

    lh = descriptors["labelled_home_15min_v1"]
    assert lh.row_count == 5760
    assert len(lh.columns) == 30
    assert lh.provenance_class == "synthetic"


def test_inventory_nonexistent_directory():
    with pytest.raises(FileNotFoundError):
        inventory_datasets("nonexistent_dir", "configs/ml/data_contracts.yaml")


def test_deterministic_hash():
    p = Path("data/synthetic_smart_meter_15min.csv")
    if not p.exists():
        p = Path("data/raw/synthetic_smart_meter_15min.csv")
    h1, sz1, r1, _ = compute_file_hash_and_rows(p)
    h2, sz2, r2, _ = compute_file_hash_and_rows(p)
    assert h1 == h2
    assert sz1 == sz2
    assert r1 == r2 == 32256
