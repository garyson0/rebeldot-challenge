from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from app.llm.client import get_chat_model
from app.llm.prompts import ANSWER_PROMPT
from app.schemas.ask import AskResponse
from app.services.retrieval import find_best_match
from app.services.router import choose_route


def ask_question(db: Session, question: str) -> AskResponse:
    """Answer from the FAQ when there is a close match, otherwise ask the LLM."""
    match = find_best_match(db, question)
    route = choose_route(match.similarity if match else None)

    if route == "local":
        return AskResponse(source="local", matched_question=match.question, answer=match.answer)

    chain = ANSWER_PROMPT | get_chat_model() | StrOutputParser()
    answer = chain.invoke({"question": question})
    return AskResponse(source="openai", matched_question="N/A", answer=answer)
