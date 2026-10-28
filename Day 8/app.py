import json
import gradio as gr

from pipeline import process_exception
from session import TriageSession


def format_log(session):
    entries = session.get_log()

    if not entries:
        return "No exceptions processed yet."

    lines = []

    for index, entry in enumerate(entries, start=1):
        timestamp = entry.get("timestamp", "")
        lines.append(
            f"### {index}. {entry['category'].upper()} — {timestamp}\n"
            f"- **Status:** {entry['status']}\n"
            f"- **Tier:** {entry['customer_tier']}\n"
            f"- **Shipment value:** ${entry['shipment_value']:.2f}\n"
            f"- **Proposed compensation:** ${entry['compensation']:.2f}\n"
            f"- **Escalated:** {'Yes' if entry['escalated'] else 'No'}"
        )

    return "\n\n".join(lines)


def format_result(result):
    steps = "\n".join(
        f"{index}. {step}"
        for index, step in enumerate(result["steps"], start=1)
    )

    return f"""
## Processing Outcome

- **Category:** {result['category']}
- **Status:** {result['status'].replace('_', ' ').title()}
- **Shipment value:** ${result['shipment_value']:.2f}
- **Customer tier:** {result['customer_tier'].title()}
- **Proposed compensation:** ${result['compensation']:.2f}
- **Compensation reason:** {result['compensation_reason']}
- **Escalated:** {'Yes' if result['escalated'] else 'No'}

## Processing Steps

{steps}

## Generated Message

{result['message']}
"""


def submit_exception(report, shipment_value, customer_tier, session):
    if session is None:
        session = TriageSession()

    if not report or not report.strip():
        return (
            "Please enter a shipment exception report.",
            format_log(session),
            session,
        )

    if shipment_value is None:
        return (
            "Please enter a valid shipment value.",
            format_log(session),
            session,
        )

    try:
        result = process_exception(
            report=report,
            shipment_value=shipment_value,
            customer_tier=customer_tier,
            session=session,
        )

        return (
            format_result(result),
            format_log(session),
            session,
        )

    except (ValueError, TypeError) as exc:
        return (
            f"## Input Error\n\n{str(exc)}",
            format_log(session),
            session,
        )

    except Exception as exc:
        return (
            f"## Processing Error\n\n{type(exc).__name__}: {str(exc)}",
            format_log(session),
            session,
        )


def show_daily_summary(session):
    if session is None:
        session = TriageSession()

    summary = session.generate_daily_summary()

    return json.dumps(summary, indent=2, ensure_ascii=False)


with gr.Blocks(title="Shipment Exception Desk") as app:
    gr.Markdown(
        """
        # Shipment Exception Desk

        Automatically classify shipment exceptions, calculate proposed
        compensation, and route claims to customer resolution or a manager.
        """
    )

    session_state = gr.State(TriageSession())

    with gr.Row():
        with gr.Column(scale=2):
            report_input = gr.Textbox(
                label="Shipment Exception Report",
                placeholder=(
                    "Describe the delayed, damaged, or lost shipment..."
                ),
                lines=6,
            )

            shipment_value_input = gr.Number(
                label="Shipment Value ($)",
                value=100,
                minimum=0,
                precision=2,
            )

            customer_tier_input = gr.Dropdown(
                choices=["standard", "premium"],
                value="standard",
                label="Customer Tier",
            )

            submit_button = gr.Button(
                "Process Exception",
                variant="primary",
            )

        with gr.Column(scale=3):
            result_output = gr.Markdown(
                label="Processing Outcome",
                value="Submit a report to see its outcome.",
            )

    submit_button.click(
        fn=submit_exception,
        inputs=[
            report_input,
            shipment_value_input,
            customer_tier_input,
            session_state,
        ],
        outputs=[
            result_output,
            # Log output is defined below; see the component order.
        ],
    ) if False else None

    gr.Markdown("---")
    gr.Markdown("## Daily Triage Log")

    log_output = gr.Markdown(
        value="No exceptions processed yet."
    )

    gr.Markdown("## Daily Summary")

    summary_output = gr.Code(
        label="Aggregated Session Metrics",
        language="json",
        value="{}",
    )

    with gr.Row():
        summary_button = gr.Button("Generate Daily Summary")
        refresh_log_button = gr.Button("Refresh Triage Log")

    # Return all updated outputs after processing a report.
    submit_button.click(
        fn=submit_exception,
        inputs=[
            report_input,
            shipment_value_input,
            customer_tier_input,
            session_state,
        ],
        outputs=[
            result_output,
            log_output,
            session_state,
        ],
    )

    summary_button.click(
        fn=show_daily_summary,
        inputs=[session_state],
        outputs=[summary_output],
    )

    refresh_log_button.click(
        fn=format_log,
        inputs=[session_state],
        outputs=[log_output],
    )


if __name__ == "__main__":
    app.launch()
