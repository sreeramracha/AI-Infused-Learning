from agent import InterviewAgent
from interview_bank import INTERVIEW_QUESTIONS


def main():
    agent = InterviewAgent()

    for item in INTERVIEW_QUESTIONS:
        print("\nQuestion:", item["question"])
        answer = input("Your answer: ").strip()

        if not answer:
            continue

        result = agent.evaluate_answer(
            question=item["question"],
            answer=answer,
            expected_keywords=item["expected_keywords"]
        )

        print("\nFeedback:", result["feedback"])
        print("Relevance:", result["relevance_score"], "/100")

        print("\nAsk your coach anything, or press Enter to continue.")
        meta_question = input("Coach: ").strip()

        if meta_question:
            print(agent.ask_agent(meta_question))

    print("\nFinal Report")
    print(agent.generate_final_report()["summary"])


if __name__ == "__main__":
    main()
