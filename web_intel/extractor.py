"""
LLM extraction using OpenAI structured outputs + Pydantic.

The schema is derived programmatically from CompanyIntel.model_json_schema().
The prompt only tells the LLM *what* to look for, not *how* to format it.
Adding a new field = adding it to models.py. Zero prompt changes.
"""

from openai import OpenAI

from .config import MODEL, OPENAI_API_KEY
from .models import CompanyIntel

SYSTEM_PROMPT = """You are a company research assistant. Extract structured information from the provided webpage content.

Rules:
- Only include information explicitly present in the content.
- Use empty string for missing text fields, empty list for missing lists.
- Do NOT fabricate or hallucinate any information.
- For founders/team: extract anyone listed with a leadership or founding role.
- For social links: extract all platform URLs found anywhere on the page.
- For pricing: extract all tiers with their prices and features."""

USER_PROMPT = "Extract all company intelligence from this webpage content:\n\n{content}"


def extract(content: str) -> CompanyIntel:
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(content=content)},
        ],
        temperature=0,
        response_format=CompanyIntel,
    )

    return completion.choices[0].message.parsed
