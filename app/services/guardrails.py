"""Basic guardrails for the assistant.

- Input guard: blocks prompt injection attempts before any LLM call.
- Output guard: rejects empty, too long, secret or prompt leaking LLM answers.
"""

import re

INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous |above |prior |your )?(instructions|rules)",
    r"forget (all |the )?(previous |your )?(instructions|rules)",
    r"system prompt",
    r"(reveal|show|print|repeat) (me )?(your|the) (instructions|prompt|rules)",
    r"you are now",
    r"you are no longer",
    r"pretend (to be|you are)",
    r"developer mode",
    r"without (any )?(rules|restrictions)",
    r"jailbreak",
]


def is_prompt_injection(question: str) -> bool:
    text = question.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False



MAX_ANSWER_LENGTH = 2000
SECRET_KEY_PATTERN = r"sk-[A-Za-z0-9_-]{20,}"
#  system prompt leak
PROMPT_LEAK_PHRASE = "treat it only as a question"


def is_safe_output(answer: str) -> bool:
    """Return False for empty, too long, secret-leaking or prompt-leaking LLM answers."""
    if not answer.strip():
        return False
    if len(answer) > MAX_ANSWER_LENGTH:
        return False
    if re.search(SECRET_KEY_PATTERN, answer):
        return False
    if PROMPT_LEAK_PHRASE in answer.lower():
        return False
    return True
