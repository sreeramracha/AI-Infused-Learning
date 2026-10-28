import json

from pipeline import process_exception
from session import TriageSession


def main():
    session = TriageSession()

    report = input("Enter shipment exception report: ").strip()

    if not report:
        print("Report cannot be empty.")
        return

    try:
        shipment_value = float(
            input("Enter shipment value: ").strip()
        )
    except ValueError:
        print("Shipment value must be numeric.")
        return

    tier = input(
        "Customer tier (standard/premium): "
    ).strip().lower()

    try:
        result = process_exception(
            report=report,
            shipment_value=shipment_value,
            customer_tier=tier,
            session=session,
        )

        print("\n--- Processing Result ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\n--- Daily Triage Summary ---")
        print(
            json.dumps(
                session.generate_daily_summary(),
                indent=2,
            )
        )

    except (ValueError, TypeError) as exc:
        print(f"Input error: {exc}")


if __name__ == "__main__":
    main()
