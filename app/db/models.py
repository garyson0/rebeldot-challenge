from pgvector.sqlalchemy import Vector
from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# text-embedding-3-small
EMBEDDING_DIMENSIONS = 1536


class FaqItem(Base):
    __tablename__ = "faq_items"
    __table_args__ = (
        Index(
            "ix_faq_items_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))
    collection: Mapped[str] = mapped_column(String(50), default="default", server_default="default")
    # SHA-256: embedded text + model name
    content_hash: Mapped[str | None] = mapped_column(String(64))

    def __repr__(self) -> str:
        return f"FaqItem(id={self.id!r}, question={self.question!r})"
