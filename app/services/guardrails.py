"""Basic input guard against prompt injection attempts."""

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
