"""Dataset discovery, inventorying, hashing, and schema signature matching."""
import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import yaml

from backend.ml.contracts.schemas import SourceDescriptor


def compute_file_hash_and_rows(file_path: Path) -> Tuple[str, int, int, List[str]]:
    """Compute SHA-256 hash, size in bytes, row count, and header columns."""
    sha256 = hashlib.sha256()
    size_bytes = 0
    row_count = 0
    columns: List[str] = []

    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            size_bytes += len(chunk)

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            columns = [col.strip() for col in header]
        except StopIteration:
            columns = []
        for _ in reader:
            row_count += 1

    return sha256.hexdigest(), size_bytes, row_count, columns


def match_schema_signature(
    columns: List[str], contracts_config: dict
) -> Optional[str]:
    """Match a column list against the signatures defined in contracts."""
    col_set = set(columns)
    matched_sources = []

    for source_id, source_cfg in contracts_config.get("sources", {}).items():
        req_cols = set(source_cfg.get("required_columns", []))
        if req_cols and req_cols.issubset(col_set):
            matched_sources.append(source_id)

    if len(matched_sources) == 1:
        return matched_sources[0]
    elif len(matched_sources) > 1:
        raise ValueError(
            f"Ambiguous schema match: columns match multiple sources {matched_sources}"
        )
    return None


def inventory_datasets(
    data_dir: str, contracts_config_path: str
) -> Dict[str, SourceDescriptor]:
    """Inventory and fingerprint all supported datasets in data_dir."""
    p_data = Path(data_dir)
    if not p_data.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    with open(contracts_config_path, "r", encoding="utf-8") as f:
        contracts_cfg = yaml.safe_load(f)

    descriptors: Dict[str, SourceDescriptor] = {}
    csv_files = sorted(list(p_data.glob("*.csv")))

    for csv_file in csv_files:
        sha256, size_bytes, row_count, columns = compute_file_hash_and_rows(csv_file)
        source_id = match_schema_signature(columns, contracts_cfg)
        if source_id:
            src_cfg = contracts_cfg["sources"][source_id]
            descriptors[source_id] = SourceDescriptor(
                source_id=source_id,
                path=str(csv_file.resolve()),
                sha256=sha256,
                size_bytes=size_bytes,
                row_count=row_count,
                columns=columns,
                schema_version="v1.0",
                provenance_class=src_cfg.get("provenance_class", "unknown"),
                adapter_version="1.0",
            )

    return descriptors
