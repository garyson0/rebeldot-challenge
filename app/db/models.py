from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# text-embedding-3-small
EMBEDDING_DIMENSIONS = 1536


class FaqItem(Base):
    __tablename__ = "faq_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))

    def __repr__(self) -> str:
        return f"FaqItem(id={self.id!r}, question={self.question!r})"
