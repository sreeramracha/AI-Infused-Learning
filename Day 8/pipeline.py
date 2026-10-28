import json
import re

from chains import (
    classify_chain,
    escalate_chain,
    draft_email_chain,
)
from tools import (
    calculate_delay_compensation,
    calculate_damage_compensation,
    calculate_lost_compensation,
)


ESCALATION_THRESHOLDS = {
    "standard": 250.00,
    "premium": 100.00,
}


def _parse_classification(raw_output):
    """Parse and validate the classifier's JSON response."""
    text = raw_output.strip()

    # Handle models that unexpectedly wrap JSON in a code fence.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        result = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {
            "category": "unknown",
            "delay_days": None,
            "damage_severity": None,
            "reason": "Could not parse the classification response.",
        }

    if not isinstance(result, dict):
        return {
            "category": "unknown",
            "delay_days": None,
            "damage_severity": None,
            "reason": "Classification response was not an object.",
        }

    category = str(result.get("category", "unknown")).lower().strip()

    if category not in {"delayed", "damaged", "lost", "unknown"}:
        category = "unknown"

    delay_days = result.get("delay_days")
    severity = result.get("damage_severity")

    # Validate values before passing them to business logic.
    if (
        isinstance(delay_days, bool)
        or not isinstance(delay_days, int)
        or delay_days < 0
    ):
        delay_days = None

    if severity is not None:
        severity = str(severity).lower().strip()

    if severity not in {"minor", "moderate", "severe"}:
        severity = None

    return {
        "category": category,
        "delay_days": delay_days,
        "damage_severity": severity,
        "reason": str(result.get("reason", "")),
    }


def _extract_delay_days(report):
    """Conservative fallback when the classifier omits delay_days."""
    match = re.search(
        r"\b(\d+)\s*(?:days?|d)\s*(?:late|delayed|delay)\b"
        r"|\b(?:late|delayed|delay)\s*(?:by\s*)?(\d+)\s*days?\b",
        report.lower(),
    )

    if match:
        return int(match.group(1) or match.group(2))

    # If no duration is supplied, do not invent one.
    return None


def _extract_damage_severity(report):
    """Use explicit damage descriptions when severity is missing."""
    text = report.lower()

    if any(word in text for word in ("severe", "destroyed", "shattered")):
        return "severe"

    if any(word in text for word in ("moderate", "significant damage")):
        return "moderate"

    if any(word in text for word in ("minor", "small scratch", "slight damage")):
        return "minor"

    return None


def process_exception(
    report,
    shipment_value,
    customer_tier="standard",
    session=None,
):
    """
    Process a shipment exception and return a structured result.

    Pass a TriageSession instance to record the result automatically.
    """
    if not isinstance(report, str) or not report.strip():
        raise ValueError("Please enter a shipment exception report.")

    shipment_value = float(shipment_value)

    if shipment_value < 0 or not __import__("math").isfinite(shipment_value):
        raise ValueError("Shipment value must be finite and non-negative.")

    customer_tier = str(customer_tier).strip().lower()

    if customer_tier not in ESCALATION_THRESHOLDS:
        raise ValueError("Customer tier must be standard or premium.")

    steps = []

    # 1. Classify the report.
    try:
        raw_classification = classify_chain.invoke({
            "report": report,
        })
        classification = _parse_classification(raw_classification)
    except Exception as exc:
        # Fail safely: never auto-resolve when classification fails.
        classification = {
            "category": "unknown",
            "delay_days": None,
            "damage_severity": None,
            "reason": f"Classification failed: {type(exc).__name__}",
        }

    category = classification["category"]
    steps.append(f"Classification: {category}")

    # 2. Calculate compensation with deterministic Python rules.
    try:
        if category == "delayed":
            delay_days = classification["delay_days"]

            if delay_days is None:
                delay_days = _extract_delay_days(report)

            if delay_days is None:
                category = "unknown"
                compensation = {
                    "category": "unknown",
                    "compensation": 0.0,
                    "reason": "Delay duration is unclear; manual review required.",
                }
            else:
                compensation = calculate_delay_compensation(
                    shipment_value,
                    delay_days,
                )

        elif category == "damaged":
            severity = classification["damage_severity"]

            if severity is None:
                severity = _extract_damage_severity(report)

            if severity is None:
                category = "unknown"
                compensation = {
                    "category": "unknown",
                    "compensation": 0.0,
                    "reason": "Damage severity is unclear; manual review required.",
                }
            else:
                compensation = calculate_damage_compensation(
                    shipment_value,
                    severity,
                )

        elif category == "lost":
            compensation = calculate_lost_compensation(shipment_value)

        else:
            category = "unknown"
            compensation = {
                "category": "unknown",
                "compensation": 0.0,
                "reason": "Unclassifiable report; manual review required.",
            }

    except (ValueError, TypeError, OverflowError):
        category = "unknown"
        compensation = {
            "category": "unknown",
            "compensation": 0.0,
            "reason": "Compensation calculation failed; manual review required.",
        }

    amount = float(compensation["compensation"])
    steps.append(f"Compensation calculated: {amount:.2f}")
    steps.append(f"Policy reason: {compensation['reason']}")

    # 3. Apply escalation policy.
    threshold = ESCALATION_THRESHOLDS[customer_tier]

    escalated = (
        category == "unknown"
        or amount > threshold
    )

    if category == "unknown":
        escalation_reason = "Unknown or unclear category requires manual review."
    elif amount > threshold:
        escalation_reason = (
            f"Compensation {amount:.2f} exceeds the "
            f"{customer_tier} threshold of {threshold:.2f}."
        )
    else:
        escalation_reason = (
            f"Compensation is within the {customer_tier} threshold "
            f"of {threshold:.2f}."
        )

    steps.append(f"Escalation decision: {escalated}")
    steps.append(escalation_reason)

    # 4. Draft a customer email or internal manager note.
    chain_inputs = {
        "report": report,
        "category": category,
        "shipment_value": f"{shipment_value:.2f}",
        "customer_tier": customer_tier,
        "compensation": f"{amount:.2f}",
        "reason": escalation_reason + " " + compensation["reason"],
    }

    try:
        if escalated:
            message = escalate_chain.invoke(chain_inputs)
            message_type = "manager_escalation"
            steps.append("Generated internal manager escalation note.")
        else:
            message = draft_email_chain.invoke(chain_inputs)
            message_type = "customer_email"
            steps.append("Generated customer-facing resolution email.")
    except Exception as exc:
        # Preserve the routing result if drafting fails.
        message = (
            f"Message drafting failed ({type(exc).__name__}). "
            "A human must prepare the message."
        )
        steps.append("Drafting failed; manual message preparation required.")

        # A failed manager-note draft remains escalated.
        # A failed customer-email draft must not be treated as a
        # completed automatic resolution.
        escalated = True
        message_type = "manager_escalation"
        escalation_reason += " Message drafting failed; manual follow-up required."

    result = {
        "category": category,
        "shipment_value": round(shipment_value, 2),
        "customer_tier": customer_tier,
        "compensation": round(amount, 2),
        "compensation_reason": compensation["reason"],
        "escalated": escalated,
        "escalation_reason": escalation_reason if escalated else None,
        "status": "escalated" if escalated else "auto_resolved",
        "message_type": message_type,
        "message": message,
        "steps": steps,
    }

    if session is not None:
        session.log_exception(result)

    return result
