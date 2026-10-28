from pipeline import process_exception
from session import TriageSession


SCENARIOS = [
    {
        "name": "Mild delay",
        "report": (
            "The shipment arrived 1 day late. "
            "The package is otherwise in good condition."
        ),
        "shipment_value": 100,
        "customer_tier": "standard",
        "expected_category": "delayed",
        "expected_escalated": False,
    },
    {
        "name": "High-value lost shipment",
        "report": (
            "The shipment has been confirmed lost in transit. "
            "The customer has not received the package."
        ),
        "shipment_value": 2000,
        "customer_tier": "standard",
        "expected_category": "lost",
        "expected_escalated": True,
    },
    {
        "name": "Minor damage",
        "report": (
            "The shipment arrived with a minor scratch on the "
            "outer packaging. The contents are otherwise intact."
        ),
        "shipment_value": 100,
        "customer_tier": "standard",
        "expected_category": "damaged",
        "expected_escalated": False,
    },
    {
        "name": "Unclassifiable report",
        "report": "xqz !!! ??? blargh 123 %% not-a-shipment",
        "shipment_value": 10,
        "customer_tier": "standard",
        "expected_category": "unknown",
        "expected_escalated": True,
    },
]


def main():
    session = TriageSession()
    failures = []

    for scenario in SCENARIOS:
        print(f"\nTesting: {scenario['name']}")

        result = process_exception(
            report=scenario["report"],
            shipment_value=scenario["shipment_value"],
            customer_tier=scenario["customer_tier"],
            session=session,
        )

        category_ok = (
            result["category"] == scenario["expected_category"]
        )
        routing_ok = (
            result["escalated"] == scenario["expected_escalated"]
        )

        print(f"Category: {result['category']}")
        print(f"Compensation: {result['compensation']:.2f}")
        print(f"Escalated: {result['escalated']}")
        print(f"Category check: {'PASS' if category_ok else 'FAIL'}")
        print(f"Routing check: {'PASS' if routing_ok else 'FAIL'}")

        if not category_ok or not routing_ok:
            failures.append({
                "scenario": scenario["name"],
                "expected_category": scenario["expected_category"],
                "actual_category": result["category"],
                "expected_escalated": scenario["expected_escalated"],
                "actual_escalated": result["escalated"],
            })

    print("\n--- Aggregated Summary ---")
    print(session.generate_daily_summary())

    if failures:
        print(f"\nFAILED: {len(failures)} scenario(s)")
        for failure in failures:
            print(failure)
        raise SystemExit(1)

    print("\nSUCCESS: All four scenarios passed.")


if __name__ == "__main__":
    main()
