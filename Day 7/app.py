import gradio as gr

from agent import InterviewAgent
from interview_bank import INTERVIEW_QUESTIONS


def create_session():
    return InterviewAgent()


def render_scorecard(agent):
    if not agent.history:
        return "No questions answered yet."

    lines = [
        "| # | Question | Relevance |",
        "|---:|---|---:|"
    ]

    for index, item in enumerate(agent.history, start=1):
        question = item["question"].replace("|", "\\|")
        lines.append(
            f"| {index} | {question} | "
            f"{item['relevance_score']}/100 |"
        )

    return "\n".join(lines)


def evaluate(agent, question_index, answer):
    if not answer.strip():
        return (
            "Please enter your answer.",
            render_scorecard(agent),
            agent,
        )

    item = INTERVIEW_QUESTIONS[int(question_index)]

    try:
        result = agent.evaluate_answer(
            question=item["question"],
            answer=answer,
            expected_keywords=item["expected_keywords"]
        )

        tool_results = "\n".join(
            f"- **{r['tool']}**: "
            f"{r.get('feedback', r.get('score', 'Completed'))}"
            for r in result["tool_results"]
        )

        feedback = (
            f"### Coach Feedback\n{result['feedback']}\n\n"
            f"**Relevance:** {result['relevance_score']}/100\n\n"
            f"{tool_results}"
        )

    except Exception as exc:
        feedback = (
            f"Evaluation failed: {exc}\n\n"
            "Check your API key, model name, and network connection."
        )

    return feedback, render_scorecard(agent), agent


def ask_coach(agent, question):
    if not question.strip():
        return "Enter a question for your coach."

    try:
        return agent.ask_agent(question)
    except Exception as exc:
        return f"Unable to contact the coach: {exc}"


def final_report(agent):
    return agent.generate_final_report()["summary"]


def next_question(index):
    return (int(index) + 1) % len(INTERVIEW_QUESTIONS)


with gr.Blocks(title="InterviewIQ — AI Interview Coach") as demo:
    gr.Markdown(
        "# InterviewIQ\n"
        "Practice interview answers and receive AI-powered feedback."
    )

    session = gr.State(create_session())

    question_index = gr.Dropdown(
        choices=[
            (f"{i + 1}. {item['question']}", str(i))
            for i, item in enumerate(INTERVIEW_QUESTIONS)
        ],
        value="0",
        label="Choose an interview question"
    )

    question_display = gr.Markdown(
        f"### {INTERVIEW_QUESTIONS[0]['question']}"
    )

    question_index.change(
        lambda i: f"### {INTERVIEW_QUESTIONS[int(i)]['question']}",
        inputs=question_index,
        outputs=question_display
    )

    answer = gr.Textbox(
        label="Your answer",
        placeholder="Type your answer here...",
        lines=7
    )

    evaluate_button = gr.Button(
        "Evaluate Answer",
        variant="primary"
    )

    feedback = gr.Markdown(label="Feedback")

    scorecard = gr.Markdown(
        "No questions answered yet.",
        label="Live Scorecard"
    )

    next_button = gr.Button("Select Next Question")
    next_button.click(
        next_question,
        inputs=question_index,
        outputs=question_index
    )

    evaluate_button.click(
        evaluate,
        inputs=[session, question_index, answer],
        outputs=[feedback, scorecard, session]
    )

    gr.Markdown("## Ask Your Coach")

    meta_question = gr.Textbox(
        label="Ask about your progress",
        placeholder="How am I doing so far? What's my weakest area?"
    )

    ask_button = gr.Button("Ask Coach")
    meta_answer = gr.Markdown()

    ask_button.click(
        ask_coach,
        inputs=[session, meta_question],
        outputs=meta_answer
    )

    gr.Markdown("## Final Report")

    report_button = gr.Button("Generate Final Report")
    report_output = gr.Markdown()

    report_button.click(
        final_report,
        inputs=session,
        outputs=report_output
    )


if __name__ == "__main__":
    demo.launch()
