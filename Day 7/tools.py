import re


FILLER_WORDS = [
    "um", "uh", "erm", "basically",
    "literally", "actually", "like",
    "you know", "i mean", "sort of",
    "kind of"
]


def detect_filler_words(answer: str) -> dict:
    """Find filler words and count their occurrences."""

    found = {}

    for filler in FILLER_WORDS:
        pattern = r"\b" + re.escape(filler) + r"\b"
        matches = re.findall(pattern, answer, flags=re.IGNORECASE)

        if matches:
            found[filler] = len(matches)

    total = sum(found.values())

    return {
        "tool": "detect_filler_words",
        "total_filler_count": total,
        "fillers_found": found,
        "feedback": (
            "Try to replace filler words with short pauses."
            if total else
            "Great job! No common filler words detected."
        )
    }


def check_star_structure(answer: str) -> dict:
    """Check whether the answer contains the four STAR elements."""

    patterns = {
        "Situation": [
            r"\bwhen\b", r"\bwhile\b", r"\bduring\b",
            r"\bin my project\b", r"\bat work\b"
        ],
        "Task": [
            r"\bmy task\b", r"\bmy responsibility\b",
            r"\bI needed to\b", r"\bI had to\b",
            r"\bgoal\b", r"\bobjective\b"
        ],
        "Action": [
            r"\bI implemented\b", r"\bI developed\b",
            r"\bI analyzed\b", r"\bI fixed\b",
            r"\bI created\b", r"\bI worked\b",
            r"\bI investigated\b", r"\bI improved\b"
        ],
        "Result": [
            r"\bas a result\b", r"\btherefore\b",
            r"\bimproved\b", r"\breduced\b",
            r"\bincreased\b", r"\bsaved\b",
            r"\bachieved\b", r"\bsuccessfully\b"
        ]
    }

    detected = {}

    for element, keywords in patterns.items():
        detected[element] = any(
            re.search(pattern, answer, re.IGNORECASE)
            for pattern in keywords
        )

    missing = [
        element for element, present in detected.items()
        if not present
    ]

    return {
        "tool": "check_star_structure",
        "star_elements": detected,
        "covered_count": sum(detected.values()),
        "missing_elements": missing,
        "feedback": (
            "Your answer covers all four STAR elements."
            if not missing else
            "Consider adding: " + ", ".join(missing) + "."
        )
    }


def score_relevance(
    question: str,
    answer: str,
    expected_keywords: list
) -> dict:
    """Score how many expected concepts appear in the answer."""

    answer_lower = answer.lower()

    matched = [
        keyword for keyword in expected_keywords
        if keyword.lower() in answer_lower
    ]

    missing = [
        keyword for keyword in expected_keywords
        if keyword.lower() not in answer_lower
    ]

    score = (
        round(len(matched) / len(expected_keywords) * 100)
        if expected_keywords else 0
    )

    return {
        "tool": "score_relevance",
        "question": question,
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "feedback": (
            "Excellent relevance."
            if score >= 75 else
            "Good start. Include more question-specific concepts."
            if score >= 40 else
            "Try to address the question more directly."
        )
    }
