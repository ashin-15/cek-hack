from django.db import OperationalError
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.api.models import Snapshot
from energy.advisor import narrate
from energy.billing import what_if
from energy.provider import ReplayProvider

SECTIONS = {
    "consumption",
    "forecast",
    "insights",
    "appliances",
    "power-quality",
    "safety",
    "cost",
    "evidence",
    "facts",
}


@api_view(["GET", "POST"])
def section(request, name):
    if name not in SECTIONS and name != "chat":
        return Response({"detail": "Unknown endpoint."}, status=404)
    try:
        provider = ReplayProvider()
        if name == "chat":
            if request.method == "GET":
                return Response(provider.get("advisory"))
            data = request.data
            if not isinstance(data, dict) or set(data) - {"question", "live"}:
                raise ValueError("Only question and live are accepted.")
            question = data.get("question", "")
            if not isinstance(question, str) or not 1 <= len(question.strip()) <= 500:
                raise ValueError("Question must have 1–500 characters.")
            if "live" in data and not isinstance(data["live"], bool):
                raise ValueError("live must be a boolean.")
            return Response(
                narrate(provider.get("facts"), question, live=data.get("live", False))
            )
        if (
            name == "forecast"
            and request.method == "GET"
            and request.query_params.get("live") == "true"
        ):
            from energy.inference import forecast_from_artifact

            payload = provider.get("forecast")
            try:
                payload["future"] = forecast_from_artifact()
                payload["inference_mode"] = (
                    "Live inference from saved artifact; no retraining"
                )
            except (OSError, ValueError, KeyError):
                payload["inference_mode"] = (
                    "Artifact unavailable; showing cached forecast"
                )
            return Response(payload)
        if request.method == "POST":
            if name != "cost":
                return Response({"detail": "This endpoint is read-only."}, status=405)
            return Response(
                what_if(request.data, provider.get("cost")["projection"]["kwh"])
            )
        return Response(provider.get(name))
    except (Snapshot.DoesNotExist, OperationalError):
        return Response(
            {
                "detail": "Demo data is not prepared. Run .venv/bin/python scripts/train.py."
            },
            status=503,
        )
    except (ValueError, TypeError, KeyError) as exc:
        return Response({"detail": str(exc)}, status=400)
