from agent import InterviewAgent


def main():
    agent = InterviewAgent()

    strong_question = "Describe a challenging project."
    strong_answer = (
        "During a project, my task was to solve a performance challenge. "
        "I analyzed database queries, implemented caching, worked with "
        "the team, and reduced latency by 40%. As a result, performance "
        "improved and the team achieved its goal."
    )

    weak_question = "Describe a production incident."
    weak_answer = "I fixed something."

    later_question = "How do you improve application performance?"
    later_answer = (
        "I improved performance by optimizing database queries, "
        "using caching, testing latency, and measuring the results."
    )

    keywords = {
        strong_question: [
            "challenge", "task", "database", "team", "result"
        ],
        weak_question: [
            "incident", "root cause", "debugging",
            "logs", "resolution", "prevention"
        ],
        later_question: [
            "performance", "optimization", "database",
            "caching", "latency", "testing"
        ]
    }

    for question, answer in [
        (strong_question, strong_answer),
        (weak_question, weak_answer),
        (later_question, later_answer),
    ]:
        result = agent.evaluate_answer(
            question,
            answer,
            keywords[question]
        )
        print(question, "->", result["relevance_score"])

    report = agent.generate_final_report()
    print("\nReport:", report)

    assert report["weakest_area"]["question"] == weak_question, (
        "FAIL: The weakest question was not identified correctly."
    )

    # Also verify the mid-session meta-question entry point.
    meta = agent.ask_agent("What is my weakest area?")
    print("\nCoach:", meta)

    print("\nPASS: Session aggregation identified the weak answer.")


if __name__ == "__main__":
    main()
