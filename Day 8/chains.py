import json
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )

model = ChatOpenAI(
    model=os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    ),
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
    temperature=0,
)

classification_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You classify shipment exception reports.

Return ONLY a valid JSON object with these fields:
- category: delayed, damaged, lost, or unknown
- delay_days: non-negative integer or null
- damage_severity: minor, moderate, severe, or null
- reason: short explanation

Rules:
- Use delayed for late delivery.
- Use damaged for physical damage.
- Use lost for shipments confirmed missing or lost.
- Use unknown when the report is garbled, insufficient, or ambiguous.
- Do not invent facts that are not in the report.
- If the report mentions multiple categories and the primary issue
  cannot be determined, use unknown.
"""
    ),
    ("human", "Exception report:\n{report}"),
])

classify_chain = classification_prompt | model | StrOutputParser()


escalation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
Draft a concise internal escalation note for a logistics manager.
Include the category, shipment value, proposed compensation,
customer tier, reason for escalation, and recommended next action.
Do not claim a manager has approved the claim.
"""
    ),
    (
        "human",
        """
Report: {report}
Category: {category}
Shipment value: {shipment_value}
Customer tier: {customer_tier}
Proposed compensation: {compensation}
Reason: {reason}
"""
    ),
])

escalate_chain = escalation_prompt | model | StrOutputParser()


customer_email_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
Draft a professional, empathetic customer-facing email.
Explain the shipment issue and the proposed compensation.
Do not promise a payment date, claim a refund was paid,
or invent information not provided.
"""
    ),
    (
        "human",
        """
Report: {report}
Category: {category}
Shipment value: {shipment_value}
Customer tier: {customer_tier}
Proposed compensation: {compensation}
Reason: {reason}
"""
    ),
])

draft_email_chain = (
    customer_email_prompt | model | StrOutputParser()
)
