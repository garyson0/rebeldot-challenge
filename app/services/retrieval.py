from dataclasses import dataclass

from langchain_core.embeddings import Embeddings
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FaqItem
from app.llm.client import get_embeddings


@dataclass
class FaqMatch:
    question: str
    answer: str
    category: str
    similarity: float


def find_best_match(
    db: Session, question: str, embeddings: Embeddings | None = None
) -> FaqMatch | None:
    """Returns the most similar item to ``question`` or None if the FAQ is empty.

    Using cosine similarity (1 - cosine distance), 1.0 = identical.
    """
    embeddings = embeddings or get_embeddings()
    query_vector = embeddings.embed_query(question)

    distance = FaqItem.embedding.cosine_distance(query_vector)
    row = db.execute(select(FaqItem, distance).order_by(distance).limit(1)).first()
    if row is None:
        return None

    item, best_distance = row
    return FaqMatch(
        question=item.question,
        answer=item.answer,
        category=item.category,
        similarity=1 - best_distance,
    )
