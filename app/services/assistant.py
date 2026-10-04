from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from app.llm.client import get_chat_model
from app.llm.prompts import ANSWER_PROMPT
from app.schemas.ask import AskResponse
from app.services.retrieval import find_best_match
from app.services.router import choose_route

COMPLIANCE_ANSWER = (
    "This is not really what I was trained for, therefore I cannot answer. Try again."
)


def ask_question(db: Session, question: str) -> AskResponse:
    """Answer from the FAQ, from the LLM, or refuse if the question is off topic."""
    match = find_best_match(db, question)
    route = choose_route(question, match.similarity if match else None)

    if route == "local":
        return AskResponse(source="local", matched_question=match.question, answer=match.answer)

    if route == "compliance":
        return AskResponse(source="compliance", matched_question="N/A", answer=COMPLIANCE_ANSWER)

    chain = ANSWER_PROMPT | get_chat_model() | StrOutputParser()
    answer = chain.invoke({"question": question})
    return AskResponse(source="openai", matched_question="N/A", answer=answer)
