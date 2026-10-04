import hashlib

from langchain_core.embeddings import Embeddings
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import FaqItem
from app.utils.clean_faq import build_embedding_text


def content_hash(item: dict) -> str:
    """Return a SHA-256 hash of the category + question and the model name."""
    text = settings.embedding_model + ":" + build_embedding_text(item)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sync_faq(
    db: Session, items: list[dict], embeddings: Embeddings, collection: str = "default"
) -> dict[str, int]:
    """Update the collection to match ``items``, embedding only new or changed items."""
    file_items = {}
    for item in items:
        file_items[content_hash(item)] = item

    removed = 0
    updated = 0
    rows = db.scalars(select(FaqItem).where(FaqItem.collection == collection)).all()
    for row in rows:
        item = file_items.pop(row.content_hash, None)
        if item is None:
            # question/category changed or removed
            db.delete(row)
            removed += 1
        elif row.answer != item["answer"]:
            # update answer
            row.answer = item["answer"]
            updated += 1

    new_items = list(file_items.values())
    if new_items:
        texts = [build_embedding_text(item) for item in new_items]
        vectors = embeddings.embed_documents(texts)
        for item, vector in zip(new_items, vectors, strict=True):
            db.add(
                FaqItem(
                    question=item["question"],
                    answer=item["answer"],
                    category=item["category"],
                    collection=collection,
                    content_hash=content_hash(item),
                    embedding=vector,
                )
            )

    db.commit()
    return {"added": len(new_items), "updated": updated, "removed": removed}
