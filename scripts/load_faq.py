"""Load the knowledge base into Postgres with embeddings."""

import json
from pathlib import Path

from sqlalchemy import delete

from app.db.models import FaqItem
from app.db.session import SessionLocal
from app.llm.client import get_embeddings

FAQ_FILE = Path("data/faq.json")


def load_faq() -> int:
    with FAQ_FILE.open(encoding="utf-8") as f:
        items = json.load(f)["knowledge_base_items"]

    vectors = get_embeddings().embed_documents([item["question"] for item in items])

    with SessionLocal() as db:
        db.execute(delete(FaqItem))
        db.add_all(
            FaqItem(
                question=item["question"],
                answer=item["answer"],
                category=item["category"],
                embedding=vector,
            )
            for item, vector in zip(items, vectors, strict=True)
        )
        db.commit()

    return len(items)


if __name__ == "__main__":
    print(f"Loaded {load_faq()} faq items")
