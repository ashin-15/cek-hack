import json

import httpx
import pytest

from energy.advisor import _narrate, fallback, narrate, statements, validate_response
from energy.common import ARTIFACTS


@pytest.fixture
def facts():
    return json.loads((ARTIFACTS / "demo_snapshots.json").read_text())["facts"]


def test_unknown_numbers_and_diagnoses_rejected(facts):
    with pytest.raises(Exception):
        validate_response(
            {
                "explanation": ["Your bill is ₹999999."],
                "recommendations": ["Repair the confirmed wiring fault."],
            },
            facts,
        )
    s = statements(facts)
    result = validate_response(
        {"explanation": [s["bill"], s["anomaly"]], "recommendations": [s["review"]]},
        facts,
    )
    assert result["source"] == "Groq facts narration"


def test_outage_falls_back(monkeypatch, facts):
    monkeypatch.setenv("GROQ_API_KEY", "test-placeholder")

    def fail(*a, **kw):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "post", fail)
    _narrate.cache_clear()
    result = narrate(facts, "Why is my bill higher?", live=True)
    assert result["source"] == "Deterministic facts template"
    assert "no prior bill" in result["explanation"]
    assert result["fallback_reason"]


def test_malicious_vendor_output_falls_back(monkeypatch, facts):
    monkeypatch.setenv("GROQ_API_KEY", "test-placeholder")
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *a, **k: httpx.Response(
            200,
            request=httpx.Request("POST", "https://example.com"),
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"explanation":["Confirmed leakage."],"recommendations":["Save 500 rupees."]}'
                        }
                    }
                ]
            },
        ),
    )
    _narrate.cache_clear()
    assert (
        narrate(facts, "Tell me a diagnosis", live=True)["source"]
        == "Deterministic facts template"
    )


def test_safety_and_out_of_scope(facts):
    assert "cannot confirm" in fallback(facts, "Is there leakage?")["explanation"]
    assert "cannot control" in fallback(facts, "Switch my device off")["explanation"]
