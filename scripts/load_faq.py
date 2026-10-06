"""Load the knowledge base into Postgres with embeddings.

Only new or changed question/category pairs are embedded.
"""

import json
from pathlib import Path

from app.db.session import SessionLocal
from app.llm.client import get_embeddings
from app.services.faq_sync import sync_faq
from app.utils.clean_faq import clean_item

FAQ_FILE = Path("data/faq.json")
COLLECTION = "default"


def load_faq() -> dict[str, int]:
    with FAQ_FILE.open(encoding="utf-8") as f:
        raw_items = json.load(f)["knowledge_base_items"]

    cleaned = (clean_item(item) for item in raw_items)
    items = [item for item in cleaned if item is not None]

    with SessionLocal() as db:
        return sync_faq(db, items, get_embeddings(), COLLECTION)


if __name__ == "__main__":
    print(load_faq())
