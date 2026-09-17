"""Monthly equivalent energy + fixed charges. No invented levies or ToD enrollment."""

import copy
import json
import math
from decimal import ROUND_HALF_UP, Decimal

from energy.common import ROOT

TARIFF = json.loads((ROOT / "config/kseb_domestic_tariff_2025_04.json").read_text())


def money(value):
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def band_for(kwh, bands):
    return next(b for b in bands if b["up_to"] is None or kwh <= b["up_to"])


def validate_number(value, maximum=100000):
    if isinstance(value, bool):
        raise ValueError("A finite non-negative number is required.")
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= maximum:
        raise ValueError(f"Value must be between 0 and {maximum}.")
    return number


def estimate(kwh, tariff=None, phase="single"):
    tariff = tariff or TARIFF
    kwh = validate_number(kwh)
    energy = Decimal("0")
    breakdown = []
    if kwh <= tariff["telescopic_limit_kwh"]:
        previous = 0
        for b in tariff["slabs"]:
            units = max(0, min(kwh, b["up_to"]) - previous)
            charge = Decimal(str(units)) * Decimal(str(b["rate"]))
            if units:
                breakdown.append(
                    {"kwh": round(units, 4), "rate": b["rate"], "charge": money(charge)}
                )
            energy += charge
            previous = b["up_to"]
        mode = "telescopic"
        marginal = band_for(kwh, tariff["slabs"])["rate"]
    else:
        marginal = band_for(kwh, tariff["flat_bands"])["rate"]
        energy = Decimal(str(kwh)) * Decimal(str(marginal))
        breakdown = [{"kwh": kwh, "rate": marginal, "charge": money(energy)}]
        mode = "whole-month rate"
    fixed = band_for(kwh, tariff["fixed"])[phase]
    edges = [
        b["up_to"]
        for b in tariff["fixed"]
        if b["up_to"] is not None and b["up_to"] >= kwh
    ]
    next_edge = min(edges) if edges else None
    distance = round(next_edge - kwh, 2) if next_edge is not None else None
    return {
        "kwh": round(kwh, 2),
        "energy_charge": money(energy),
        "fixed_charge": fixed,
        "estimated_cost": money(energy + Decimal(str(fixed))),
        "mode": mode,
        "breakdown": breakdown,
        "marginal_rate": marginal,
        "next_band_kwh": next_edge,
        "distance_to_band_kwh": distance,
        "slab_warning": distance is not None and distance <= tariff["slab_warning_kwh"],
        "exclusions": tariff["exclusions"],
    }


def what_if(payload, projected_kwh):
    if set(payload) != {"usage_kwh", "slab_rates"}:
        raise ValueError("Only usage_kwh and slab_rates are accepted.")
    rates = payload["slab_rates"]
    if not isinstance(rates, list) or len(rates) != 10:
        raise ValueError("Supply five telescopic and five whole-month rates.")
    cfg = copy.deepcopy(TARIFF)
    for band, rate in zip(cfg["slabs"] + cfg["flat_bands"], rates):
        band["rate"] = validate_number(rate, 100)
    return {
        "scenario": estimate(payload["usage_kwh"], cfg),
        "baseline": estimate(projected_kwh),
        "difference_inr": money(
            estimate(payload["usage_kwh"], cfg)["estimated_cost"]
            - estimate(projected_kwh)["estimated_cost"]
        ),
        "note": "Estimator only. Does not change telemetry, forecasts, alerts or saved tariff.",
    }


def tariff_multiplier(hour, eligible, cfg=None):
    if not eligible:
        return 1
    return next(
        p["multiplier"]
        for p in (cfg or TARIFF)["tod"]["periods"]
        if p["start"] <= hour < p["end"]
    )


def schedule(events, future, projected_kwh, phase="single", enrolled=False):
    eligible = (
        phase == "three"
        and enrolled
        and projected_kwh > TARIFF["tod"]["monthly_threshold_kwh"]
    )
    rate = estimate(projected_kwh)["marginal_rate"]
    suggestions = []
    for event in [e for e in events if e["flexible"]][-5:]:
        duration = event["duration_minutes"] / 60
        width = math.ceil(duration)
        if width > len(future):
            continue
        energy = event["energy_kwh"]
        candidates = []
        for start in range(len(future) - width + 1):
            window = future[start : start + width]
            weights = [min(1, duration - i) for i in range(width)]
            avg = (
                sum(
                    tariff_multiplier(int(r["timestamp"][11:13]), eligible) * w
                    for r, w in zip(window, weights)
                )
                / duration
            )
            demand = sum(r["forecast_kwh"] * w for r, w in zip(window, weights))
            candidates.append((energy * rate * avg, demand, start))
        cost, demand, start = min(candidates)
        original_hour = int(event["timestamp"][11:13])
        original_avg = (
            sum(
                tariff_multiplier((original_hour + i) % 24, eligible)
                * min(1, duration - i)
                for i in range(width)
            )
            / duration
        )
        old_cost = energy * rate * original_avg
        from datetime import datetime, timedelta

        end = datetime.fromisoformat(future[start]["timestamp"]) + timedelta(
            minutes=event["duration_minutes"]
        )
        suggestions.append(
            {
                "likely_appliance_class": event["likely_appliance_class"],
                "start": future[start]["timestamp"],
                "end": end.isoformat(),
                "duration_minutes": event["duration_minutes"],
                "energy_kwh": energy,
                "estimated_saving": money(max(0, old_cost - cost)),
                "tod_eligible": eligible,
                "reason": "Cheapest contiguous window; forecast demand breaks ties. Confirm that delaying this use is convenient."
                if eligible
                else "No time-of-day price difference for this demo connection. Lower forecast demand breaks the price tie; shifting alone saves ₹0.",
            }
        )
    return suggestions
