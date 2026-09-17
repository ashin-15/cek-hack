import json

import pytest
from rest_framework.test import APIClient

from backend.api.models import Snapshot
from energy.common import ARTIFACTS


@pytest.fixture
def seeded(db):
    for key, payload in json.loads(
        (ARTIFACTS / "demo_snapshots.json").read_text()
    ).items():
        Snapshot.objects.create(name=key, payload=payload)
    return APIClient()


@pytest.mark.parametrize(
    "name",
    [
        "consumption",
        "forecast",
        "insights",
        "appliances",
        "power-quality",
        "safety",
        "cost",
        "chat",
        "facts",
        "evidence",
    ],
)
def test_seeded_readonly_endpoints(seeded, name):
    assert seeded.get("/" + name).status_code == 200
    if name not in ["cost", "chat"]:
        assert seeded.post("/" + name, {}, format="json").status_code == 405


def test_estimator_never_mutates_snapshots(seeded):
    before = list(Snapshot.objects.values_list("name", "payload"))
    response = seeded.post(
        "/cost",
        {
            "usage_kwh": 100,
            "slab_rates": [3.35, 4.25, 5.35, 7.2, 8.5, 6.75, 7.6, 7.95, 8.25, 9.2],
        },
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["scenario"]["estimated_cost"] == 465
    assert list(Snapshot.objects.values_list("name", "payload")) == before
    assert (
        seeded.post(
            "/cost", {"usage_kwh": -1, "slab_rates": []}, format="json"
        ).status_code
        == 400
    )


def test_input_limits_and_unknown_endpoints(seeded):
    assert (
        seeded.post("/chat", {"question": "a" * 501}, format="json").status_code == 400
    )
    assert (
        seeded.post(
            "/chat", {"question": "hello", "live": "false"}, format="json"
        ).status_code
        == 400
    )
    assert seeded.get("/inventory").status_code == 404
    assert (
        seeded.post(
            "/chat", {"question": "Why is my bill higher?"}, format="json"
        ).status_code
        == 200
    )


def test_unseeded_returns_actionable_error(db):
    response = APIClient().get("/consumption")
    assert (
        response.status_code == 503 and "scripts/train.py" in response.json()["detail"]
    )
