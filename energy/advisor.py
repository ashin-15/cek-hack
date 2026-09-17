"""Facts-only narration. Llama selects grounded sentences; arbitrary claims fail closed."""

import json
import os
import re
from functools import lru_cache

import httpx
from jsonschema import validate

MODEL = "openai/gpt-oss-120b"  # Groq catalogue model this project's API key can reach, verified 2026-09-17.
NUMBER = re.compile(r"(?<!\w)-?\d+(?:\.\d+)?")


def statements(facts):
    return {
        "usage": f"Observed consumption for the selected hour was {facts['actual_kwh']} kWh; its baseline was {facts['baseline_kwh']} kWh.",
        "forecast": f"The next-hour forecast is {facts['forecast_kwh']} kWh. Forecasts are model estimates from simulated history.",
        "bill": f"The projected monthly energy and fixed charge estimate is ₹{facts['estimated_cost']}. Taxes, duty, rent and fuel surcharges are excluded.",
        "anomaly": f"The selected hour has a z-score of {facts['z_score']} and a wastage score of {facts['wastage_score']}. Unusual usage is evidence to review, not proof of avoidable waste.",
        "appliance": f"The likely appliance class is {facts['likely_appliance_class']}. Aggregate step matching cannot establish appliance identity.",
        "quality": f"Voltage status: {facts['voltage_status']}. Power factor status: {facts['power_factor_status']}.",
        "safety": "Safety events come from a separate simulated sensor fixture. This system cannot confirm an electrical diagnosis; persistent events need a qualified electrician.",
        "bill_change": "There is no prior bill in the fact sheet, so a bill increase cannot be established. The estimate describes projected consumption in this replay.",
        "review": "Review persistent high-usage periods and check whether the associated use was needed.",
        "shift": "Consider the suggested lower-demand window if convenient. This demo connection has no time-of-day price difference, so shifting alone has no estimated monetary saving.",
        "scope": "I can explain the visible household facts, forecasts, costs, appliance estimates and safety replay. I cannot control devices or answer from unavailable records.",
    }


def fallback(facts, question=""):
    s = statements(facts)
    q = question.lower()
    if any(w in q for w in ["safety", "leak", "earth", "wiring", "fault"]):
        keys = ["safety", "quality"]
    elif any(w in q for w in ["bill", "cost", "higher", "save"]):
        keys = ["bill_change", "bill", "anomaly"]
    elif any(w in q for w in ["appliance", "fridge", "ac ", "efficient"]):
        keys = ["appliance"]
    elif "forecast" in q:
        keys = ["forecast"]
    elif (
        any(w in q for w in ["usage", "energy", "consumption", "today", "why"]) or not q
    ):
        keys = ["usage", "anomaly", "bill"]
    else:
        keys = ["scope"]
    return {
        "explanation": " ".join(s[k] for k in keys),
        "recommendations": [s["review"], s["shift"]],
        "source": "Deterministic facts template",
        "model": None,
    }


def map_to_approved(item: str, approved_list: list) -> str:
    if not isinstance(item, str):
        return ""
    item_clean = item.strip().lower()
    for app in approved_list:
        if (
            item_clean == app.lower()
            or item_clean in app.lower()
            or app.lower().startswith(item_clean)
        ):
            return app
    return item


def validate_response(response, facts, source="Groq facts narration", model=None):
    s = statements(facts)
    schema = {
        "type": "object",
        "properties": {
            "explanation": {
                "type": "array",
                "items": {"type": "string", "enum": list(s.values())},
                "minItems": 1,
                "maxItems": 4,
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string", "enum": [s["review"], s["shift"]]},
                "minItems": 1,
                "maxItems": 3,
            },
        },
        "required": ["explanation", "recommendations"],
        "additionalProperties": False,
    }
    validate(response, schema)
    numbers = set(NUMBER.findall(json.dumps(facts)))
    cited = set(
        NUMBER.findall(" ".join(response["explanation"] + response["recommendations"]))
    )
    if not cited <= numbers:
        raise ValueError("Narration contains numbers outside the fact sheet.")
    return {
        "explanation": " ".join(response["explanation"]),
        "recommendations": list(dict.fromkeys(response["recommendations"])),
        "source": source,
        "model": model or MODEL,
    }


@lru_cache(maxsize=64)
def _narrate(serialized, question):
    facts = json.loads(serialized)
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if nvidia_key:
        api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        api_key = nvidia_key
        model_name = os.getenv("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")
        source_name = "NVIDIA AI facts narration"
    elif groq_key:
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = groq_key
        model_name = os.getenv("GROQ_MODEL", MODEL)
        source_name = "Groq facts narration"
    else:
        return fallback(facts, question)

    s = statements(facts)
    obs_approved = list(s.values())
    rec_approved = [s["review"], s["shift"]]

    prompt = (
        "You are an AI household energy advisor. Analyze the user question and select the most relevant observations "
        "and suggestions to directly answer it. "
        "Return ONLY a JSON object with keys \"explanation\" (array of 1 to 4 sentences) and \"recommendations\" (array of 1 to 3 sentences). "
        "Each array item must be copied verbatim, whole and unmodified, from the supplied approved observations or "
        "suggestions values. Never split, truncate, or reword values. Use only supplied facts. "
        "- For questions about bills, costs, or increases, include the bill and bill_change observations. "
        "- For questions about appliances or specific devices, include the appliance observation. "
        "- For questions about safety, wiring, earthing, or faults, include the safety and quality observations. "
        "- For questions about forecast or future, include the forecast observation. "
        "- For questions about usage or energy, include the usage and anomaly observations. "
        "- For general or greeting questions, include usage, anomaly, and bill observations. "
        "Preserve every number exactly. Never calculate unsupplied figures or confirm physical diagnoses. "
        "Explanation uses observations; recommendations use suggestions."
    )
    try:
        req_json = {
            "model": model_name,
            "temperature": 0.1,
            "max_tokens": 600,
            "messages": [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "facts": facts,
                            "observations": {
                                k: v
                                for k, v in s.items()
                                if k not in ["review", "shift"]
                            },
                            "suggestions": [s["review"], s["shift"]],
                            "question": question,
                        }
                    ),
                },
            ],
        }
        if "groq.com" in api_url:
            req_json["response_format"] = {"type": "json_object"}
            req_json["max_completion_tokens"] = 800

        response = httpx.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=14,
            json=req_json,
        )
        response.raise_for_status()
        raw_content = response.json()["choices"][0]["message"]["content"].strip()
        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            raw_content = match.group(0)
        parsed = json.loads(raw_content)

        if "observations" in parsed and "explanation" not in parsed:
            parsed["explanation"] = parsed.pop("observations")
        if "suggestions" in parsed and "recommendations" not in parsed:
            parsed["recommendations"] = parsed.pop("suggestions")

        if isinstance(parsed.get("explanation"), list):
            parsed["explanation"] = [
                map_to_approved(x, obs_approved)
                for x in parsed["explanation"]
                if isinstance(x, str)
            ][:4]
        elif isinstance(parsed.get("explanation"), str):
            parsed["explanation"] = [map_to_approved(parsed["explanation"], obs_approved)]
        else:
            parsed["explanation"] = [s["usage"]]

        if isinstance(parsed.get("recommendations"), list):
            parsed["recommendations"] = [
                map_to_approved(x, rec_approved)
                for x in parsed["recommendations"]
                if isinstance(x, str)
            ][:3]
        elif isinstance(parsed.get("recommendations"), str):
            parsed["recommendations"] = [
                map_to_approved(parsed["recommendations"], rec_approved)
            ]
        else:
            parsed["recommendations"] = [s["review"]]

        return validate_response(parsed, facts, source=source_name, model=model_name)
    except Exception:
        result = fallback(facts, question)
        result["fallback_reason"] = (
            "Live narration unavailable or did not pass grounding validation."
        )
        return result


def narrate(facts, question="", live=False):
    return (
        _narrate(json.dumps(facts, sort_keys=True), question)
        if live
        else fallback(facts, question)
    )
