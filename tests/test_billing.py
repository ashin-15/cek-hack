import copy

import pytest

from energy.billing import TARIFF, estimate, schedule, tariff_multiplier, what_if


@pytest.mark.parametrize(
    "kwh,energy,fixed,total",
    [
        (0, 0, 50, 50),
        (50, 167.5, 50, 217.5),
        (100, 380, 85, 465),
        (250, 1432.5, 160, 1592.5),
        (250.01, 1687.57, 220, 1907.57),
        (300, 2025, 220, 2245),
        (350, 2660, 240, 2900),
        (500, 4125, 285, 4410),
        (501, 4609.2, 310, 4919.2),
    ],
)
def test_golden_monthly_schedule(kwh, energy, fixed, total):
    result = estimate(kwh)
    assert (
        result["energy_charge"],
        result["fixed_charge"],
        result["estimated_cost"],
    ) == (energy, fixed, total)


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True, 100001])
def test_invalid_usage(value):
    with pytest.raises(ValueError):
        estimate(value)


def test_cliff_and_what_if_isolation():
    before = copy.deepcopy(TARIFF)
    rates = [b["rate"] for b in TARIFF["slabs"] + TARIFF["flat_bands"]]
    rates[0] = 1
    result = what_if({"usage_kwh": 50, "slab_rates": rates}, 240)
    assert result["scenario"]["estimated_cost"] == 100
    assert result["baseline"]["slab_warning"] is True
    assert result["baseline"]["distance_to_band_kwh"] == 10
    assert TARIFF == before
    with pytest.raises(ValueError):
        what_if({"usage_kwh": 50, "slab_rates": rates, "appliance_inventory": []}, 240)


def test_scheduler_eligibility_ties_and_duration():
    event = {
        "flexible": True,
        "duration_minutes": 90,
        "energy_kwh": 3,
        "timestamp": "2026-08-28T18:00:00+05:30",
        "likely_appliance_class": "Water heater / geyser",
    }
    future = [
        {
            "timestamp": f"2026-08-29T{h:02}:00:00+05:30",
            "forecast_kwh": 1 if h != 9 else 0,
        }
        for h in range(24)
    ]
    basic = schedule([event], future, 350)[0]
    assert basic["estimated_saving"] == 0 and not basic["tod_eligible"]
    assert basic["start"].endswith("09:00:00+05:30")
    assert basic["end"].endswith("10:30:00+05:30")
    eligible = schedule([event], future, 350, phase="three", enrolled=True)[0]
    assert eligible["estimated_saving"] == 7.98
    assert eligible["tod_eligible"]
    assert tariff_multiplier(18, True) == 1.25
    assert tariff_multiplier(22, True) == 1
