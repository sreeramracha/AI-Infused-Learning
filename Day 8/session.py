from collections import defaultdict
from datetime import datetime


class TriageSession:
    def __init__(self):
        self.exceptions = []

    def log_exception(self, result):
        """Record one processed exception."""
        entry = {
            **result,
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
        }
        self.exceptions.append(entry)
        return entry

    def get_log(self):
        """Return all exceptions recorded in this session."""
        return list(self.exceptions)

    def generate_daily_summary(self):
        """
        Aggregate proposed compensation, escalation rate,
        and category totals for this session.
        """
        total = len(self.exceptions)
        escalated_count = sum(
            1 for item in self.exceptions if item["escalated"]
        )

        category_totals = defaultdict(float)
        category_counts = defaultdict(int)

        for item in self.exceptions:
            category = item["category"]
            category_totals[category] += item["compensation"]
            category_counts[category] += 1

        category_totals = {
            category: round(amount, 2)
            for category, amount in category_totals.items()
        }

        # Include only categories with at least one recorded claim.
        if category_totals:
            costliest_category = max(
                category_totals,
                key=category_totals.get,
            )
            costliest_amount = category_totals[costliest_category]
        else:
            costliest_category = "None"
            costliest_amount = 0.0

        total_compensation = round(
            sum(item["compensation"] for item in self.exceptions),
            2,
        )

        return {
            "total_exceptions": total,
            "total_proposed_compensation": total_compensation,
            "escalated_count": escalated_count,
            "auto_resolved_count": total - escalated_count,
            "escalation_rate": (
                round(escalated_count / total * 100, 2)
                if total else 0.0
            ),
            "category_totals": category_totals,
            "category_counts": dict(category_counts),
            "costliest_category": costliest_category,
            "costliest_category_total": costliest_amount,
        }


# Optional convenience function for code that wants a fresh summary.
def generate_daily_summary(session):
    return session.generate_daily_summary()
