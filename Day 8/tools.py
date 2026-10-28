from decimal import Decimal, ROUND_HALF_UP


def _money(value):
    """Convert a value to a rounded monetary amount."""
    amount = Decimal(str(value))
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _validate_shipment_value(shipment_value):
    value = Decimal(str(shipment_value))

    if not value.is_finite() or value < 0:
        raise ValueError(
            "Shipment value must be a finite, non-negative number.")

    return value


def calculate_delay_compensation(shipment_value, delay_days):
    """
    Example policy:
    2% of shipment value per day, capped at 20%.
    """
    value = _validate_shipment_value(shipment_value)
    days = int(delay_days)

    if days < 0:
        raise ValueError("Delay days cannot be negative.")

    rate = min(Decimal("0.02") * days, Decimal("0.20"))
    amount = min(value * rate, value)

    return {
        "category": "delayed",
        "compensation": float(_money(amount)),
        "reason": (
            f"{days}-day delay; compensation rate "
            f"{rate * 100}% of shipment value."
        ),
    }


def calculate_damage_compensation(
    shipment_value,
    damage_severity="minor",
):
    """
    Example policy:
    minor = 10%, moderate = 30%, severe = 60%.
    """
    value = _validate_shipment_value(shipment_value)
    severity = str(damage_severity).strip().lower()

    rates = {
        "minor": Decimal("0.10"),
        "moderate": Decimal("0.30"),
        "severe": Decimal("0.60"),
    }

    if severity not in rates:
        raise ValueError(
            "Damage severity must be minor, moderate, or severe."
        )

    amount = min(value * rates[severity], value)

    return {
        "category": "damaged",
        "compensation": float(_money(amount)),
        "reason": (
            f"{severity.capitalize()} damage; "
            f"{rates[severity] * 100}% of shipment value."
        ),
    }


def calculate_lost_compensation(shipment_value):
    """Example policy: reimburse 100% of shipment value."""
    value = _validate_shipment_value(shipment_value)

    return {
        "category": "lost",
        "compensation": float(_money(value)),
        "reason": "Lost shipment; full shipment value reimbursement.",
    }
