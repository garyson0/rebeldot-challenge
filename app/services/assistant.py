import logging

from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from app.core.exceptions import LLM_ERRORS, SEARCH_ERRORS, ServiceUnavailableError
from app.llm.client import get_chat_model
from app.llm.prompts import ANSWER_PROMPT, PERSONALIZE_PROMPT
from app.schemas.ask import AskResponse
from app.services.guardrails import is_prompt_injection, is_safe_output
from app.services.retrieval import find_best_match
from app.services.router import choose_route

logger = logging.getLogger(__name__)

COMPLIANCE_ANSWER = (
    "This is not really what I was trained for, therefore I cannot answer. Try again."
)
FALLBACK_ANSWER = "Sorry, I could not find a good answer. Please try again or contact support."


def personalize_answer(question: str, faq_answer: str) -> str:
    """Rewrite the FAQ answer to fit the question."""
    try:
        chain = PERSONALIZE_PROMPT | get_chat_model() | StrOutputParser()
        answer = chain.invoke({"question": question, "faq_answer": faq_answer})
    except LLM_ERRORS:
        logger.exception("Personalizing failed, returning the FAQ answer")
        return faq_answer

    if not is_safe_output(answer):
        logger.warning("Personalized answer failed the output check, returning the FAQ answer")
        return faq_answer
    return answer


def ask_question(db: Session, question: str) -> AskResponse:
    """Answer from the FAQ, from the LLM, or refuse if the question is off topic."""
    if is_prompt_injection(question):
        return AskResponse(source="compliance", matched_question="N/A", answer=COMPLIANCE_ANSWER)

    try:
        match = find_best_match(db, question)
    except SEARCH_ERRORS as error:
        raise ServiceUnavailableError("FAQ search failed") from error

    route = choose_route(question, match.similarity if match else None)

    if route == "local":
        answer = personalize_answer(question, match.answer)
        return AskResponse(source="local", matched_question=match.question, answer=answer)

    if route == "compliance":
        return AskResponse(source="compliance", matched_question="N/A", answer=COMPLIANCE_ANSWER)

    try:
        chain = ANSWER_PROMPT | get_chat_model() | StrOutputParser()
        answer = chain.invoke({"question": question})
    except LLM_ERRORS as error:
        raise ServiceUnavailableError("OpenAI answer failed") from error

    if not is_safe_output(answer):
        logger.warning("OpenAI answer failed the output check")
        answer = FALLBACK_ANSWER
    return AskResponse(source="openai", matched_question="N/A", answer=answer)
