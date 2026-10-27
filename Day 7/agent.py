import json
import os

from openai import OpenAI
from dotenv import load_dotenv

from tools import (
    detect_filler_words,
    check_star_structure,
    score_relevance,
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

TOOL_FUNCTIONS = {
    "detect_filler_words": detect_filler_words,
    "check_star_structure": check_star_structure,
    "score_relevance": score_relevance,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "detect_filler_words",
            "description": "Detect filler words in the candidate answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_star_structure",
            "description": "Check Situation, Task, Action, Result coverage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "score_relevance",
            "description": "Score answer relevance using expected keywords.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "expected_keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": [
                    "question", "answer", "expected_keywords"
                ],
                "additionalProperties": False
            }
        }
    }
]


class InterviewAgent:
    def __init__(self):
        self.history = []

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_keywords: list
    ) -> dict:
        if not answer.strip():
            raise ValueError("Please provide an answer.")

        tool_context = {
            "question": question,
            "answer": answer,
            "expected_keywords": expected_keywords,
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are InterviewIQ, an encouraging interview coach. "
                    "Evaluate the candidate's answer using the available "
                    "tools. Call all three tools for each non-empty answer. "
                    "Use their actual results to give concise, constructive "
                    "feedback. Never invent tool results."
                )
            },
            {
                "role": "user",
                "content": json.dumps(tool_context)
            }
        ]

        results = []

        # Tool-calling loop: execute tools and return their results.
        for _ in range(5):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.2
            )

            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                feedback = message.content or (
                    "Review the evaluation results below."
                )
                break

            for tool_call in message.tool_calls:
                name = tool_call.function.name

                if name not in TOOL_FUNCTIONS:
                    raise ValueError(f"Unknown tool: {name}")

                arguments = json.loads(
                    tool_call.function.arguments
                )

                # Use the original candidate input as the source of truth.
                arguments["answer"] = answer

                if name == "score_relevance":
                    arguments["question"] = question
                    arguments["expected_keywords"] = expected_keywords

                result = TOOL_FUNCTIONS[name](**arguments)
                results.append(result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        else:
            feedback = (
                "The evaluation reached its tool-call limit. "
                "Please try again."
            )

        # Save structured results, not just the latest turn.
        relevance = next(
            (
                item["score"] for item in results
                if item["tool"] == "score_relevance"
            ),
            0
        )

        evaluation = {
            "question": question,
            "answer": answer,
            "relevance_score": relevance,
            "tool_results": results,
            "feedback": feedback
        }

        self.history.append(evaluation)
        return evaluation

    def generate_final_report(self) -> dict:
        if not self.history:
            return {
                "total_questions": 0,
                "average_relevance": 0,
                "weakest_area": None,
                "summary": "No answers have been evaluated yet."
            }

        average = sum(
            item["relevance_score"] for item in self.history
        ) / len(self.history)

        weakest = min(
            self.history,
            key=lambda item: item["relevance_score"]
        )

        return {
            "total_questions": len(self.history),
            "average_relevance": round(average, 2),
            "weakest_area": {
                "question": weakest["question"],
                "score": weakest["relevance_score"]
            },
            "summary": (
                f"You answered {len(self.history)} questions. "
                f"Your average relevance score is {average:.2f}/100. "
                f"Your weakest area is '{weakest['question']}' "
                f"with a score of {weakest['relevance_score']}/100."
            )
        }

    def ask_agent(self, question: str) -> str:
        if not self.history:
            return "Answer at least one interview question first."

        # Calculate facts from memory before asking the LLM.
        report = self.generate_final_report()

        context = {
            "evaluations": [
                {
                    "question": item["question"],
                    "relevance_score": item["relevance_score"],
                    "feedback": item["feedback"],
                }
                for item in self.history
            ],
            "aggregated_report": report
        }

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are InterviewIQ, an interview coach. Answer "
                        "questions about progress using the supplied full "
                        "session history and computed statistics. The "
                        "weakest area is the question with the lowest "
                        "relevance score, not necessarily the latest "
                        "question. Do not invent scores. Be concise and "
                        "encouraging."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Session data:\n{json.dumps(context)}\n\n"
                        f"Candidate asks: {question}"
                    )
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content or (
            "I couldn't generate an answer. Please try again."
        )
