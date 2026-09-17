"""Report generators for data audit, model cards, and benchmark summaries."""
from typing import Dict, Any, List
from backend.ml.contracts.schemas import AuditReport, RunManifest


def format_audit_markdown(reports: List[AuditReport]) -> str:
    """Format multiple dataset audit reports into markdown."""
    lines = ["# Data Audit and Verification Report\n"]
    for rep in reports:
        status_str = "PASSED" if rep.passed_gates else "FAILED"
        lines.append(f"## Dataset: `{rep.source_id}` — {status_str}")
        lines.append(f"- **Timestamp**: `{rep.timestamp}`")
        lines.append(f"- **SHA-256**: `{rep.sha256}`")
        lines.append(f"- **Rows**: `{rep.row_count:,}`\n")
        lines.append("| Rule ID | Severity | Findings Count | Message |")
        lines.append("|---|---|---|---|")
        for f in rep.findings:
            lines.append(f"| `{f.rule_id}` | `{f.severity}` | {f.count} | {f.message} |")
        lines.append("\n---\n")
    return "\n".join(lines)


def format_summary_markdown(manifest: RunManifest) -> str:
    """Format run summary into markdown."""
    m = manifest.metrics
    lines = [
        f"# Run Summary — `{manifest.run_id}`",
        f"- **Status**: `{manifest.status}`",
        f"- **Completed**: `{manifest.completed_at}`",
        f"- **Python Version**: `{manifest.python_version}`",
        f"- **Forecast Winner**: `{m.get('forecast_winner', 'N/A')}`",
        f"- **Selection Reason**: {m.get('forecast_selection_reason', 'N/A')}",
        "",
        "## Performance Highlights",
        f"- **Test MAE**: `{m.get('test_metrics', {}).get('mae', 0.0):.4f} kWh`",
        f"- **Test RMSE**: `{m.get('test_metrics', {}).get('rmse', 0.0):.4f} kW`",
        f"- **Test sMAPE**: `{m.get('test_metrics', {}).get('smape', 0.0):.2f}%`",
        f"- **Clean Test False Alert Rate**: `{m.get('clean_test_false_alert_rate', 0.0)*100:.2f}%`",
        f"- **Injection PR-AUC**: `{m.get('injection_benchmark', {}).get('pr_auc', 0.0):.4f}`",
        "",
        "## Limitations",
    ]
    for lim in manifest.limitations:
        lines.append(f"- {lim}")
    return "\n".join(lines)
