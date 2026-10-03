from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ask import AskRequest, AskResponse
from app.services.assistant import ask_question

router = APIRouter()


@router.post("/ask-question")
def ask(request: AskRequest, db: Annotated[Session, Depends(get_db)]) -> AskResponse:
    """Answer a question from the user, using the FAQ or LLM fallback."""
    return ask_question(db, request.user_question)
