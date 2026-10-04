import logging

from pydantic import BaseModel

from app.core.config import settings
from app.llm.client import get_chat_model
from app.llm.prompts import ROUTER_PROMPT

logger = logging.getLogger(__name__)


class TopicCheck(BaseModel):
    on_topic: bool


def check_topic(question: str) -> bool:
    """Ask the LLM if the question fits."""
    llm = get_chat_model(settings.router_model).with_structured_output(TopicCheck)
    result = (ROUTER_PROMPT | llm).invoke({"question": question})
    return result.on_topic


def choose_route(question: str, similarity: float | None, threshold: float | None = None) -> str:
    """Question handling: "local", "openai" or "compliance" """
    if threshold is None:
        threshold = settings.similarity_threshold

    # FAQ match
    if similarity is not None and similarity >= threshold:
        return "local"

    # Compliance check
    try:
        on_topic = check_topic(question)
    except Exception:
        logger.exception("Topic check failed, falling back to openai")
        return "openai"

    if on_topic:
        return "openai"
    return "compliance"
