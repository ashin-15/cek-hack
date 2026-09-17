"""Typed data contracts and schemas for the ML pipeline."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class SourceDescriptor:
    source_id: str
    path: str
    sha256: str
    size_bytes: int
    row_count: int
    columns: List[str]
    schema_version: str
    provenance_class: str
    adapter_version: str


@dataclass
class AuditFinding:
    rule_id: str
    severity: str  # "INFO", "WARNING", "BLOCKING"
    message: str
    count: int = 0
    sample: Optional[Any] = None


@dataclass
class AuditReport:
    source_id: str
    timestamp: str
    sha256: str
    row_count: int
    findings: List[AuditFinding] = field(default_factory=list)
    passed_gates: bool = True


@dataclass
class SplitManifest:
    source_id: str
    policy: str
    membership_hash: str
    train_count: int
    val_count: int
    test_count: int
    train_meters: List[str]
    test_meters: List[str]


@dataclass
class FeatureSchema:
    name: str
    features: List[str]
    dtypes: Dict[str, str]
    warmup_intervals: int
    version: str


@dataclass
class AnomalyFacts:
    household_id: str
    timestamp: str
    observed_kwh: float
    expected_kwh: float
    forecast_model: str
    residual: float
    residual_robust_z: float
    iforest_percentile: float
    rule_flags: List[str]
    fused_score: float
    event_state: str  # "normal", "open", "continuing", "closed"
    model_version: str
    source_provenance: str
    top_factors: List[str] = field(default_factory=list)


@dataclass
class RunManifest:
    run_id: str
    status: str  # "created", "completed", "failed"
    created_at: str
    completed_at: Optional[str]
    command: str
    git_sha: Optional[str]
    git_dirty: bool
    python_version: str
    sources: Dict[str, Dict[str, Any]]
    config_hash: str
    split_manifest: Dict[str, Any]
    artifacts: Dict[str, str]
    metrics: Dict[str, Any]
    limitations: List[str]
