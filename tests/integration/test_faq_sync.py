import pytest

from app.services.faq_sync import sync_faq

pytestmark = pytest.mark.integration


class FakeEmbedder:
    """Mock up real embedder to count embeddings."""

    def __init__(self):
        self.count = 0

    def embed_documents(self, texts):
        self.count += len(texts)
        return [[0.1] * 1536 for _ in texts]


def sample_faq():
    return [
        {"question": "How do I reset my password?", "answer": "Settings.", "category": "security"},
        {"question": "Can I get a refund?", "answer": "Within 14 days.", "category": "billing"},
    ]


def test_first_load_adds_all_items(db_session):
    embeddings = FakeEmbedder()

    result = sync_faq(db_session, sample_faq(), embeddings, collection="test")

    assert result == {"added": 2, "updated": 0, "removed": 0}
    assert embeddings.count == 2


def test_loading_same_items_again_does_nothing(db_session):
    sync_faq(db_session, sample_faq(), FakeEmbedder(), collection="test")

    embeddings = FakeEmbedder()
    result = sync_faq(db_session, sample_faq(), embeddings, collection="test")

    assert result == {"added": 0, "updated": 0, "removed": 0}
    assert embeddings.count == 0


def test_new_answer_is_saved_without_embedding(db_session):
    sync_faq(db_session, sample_faq(), FakeEmbedder(), collection="test")

    items = sample_faq()
    items[1]["answer"] = "Within 30 days."
    embeddings = FakeEmbedder()
    result = sync_faq(db_session, items, embeddings, collection="test")

    assert result == {"added": 0, "updated": 1, "removed": 0}
    assert embeddings.count == 0


def test_new_question_is_embedded(db_session):
    sync_faq(db_session, sample_faq(), FakeEmbedder(), collection="test")

    items = sample_faq()
    items[1]["question"] = "How do I get my money back?"
    embeddings = FakeEmbedder()
    result = sync_faq(db_session, items, embeddings, collection="test")

    assert result == {"added": 1, "updated": 0, "removed": 1}
    assert embeddings.count == 1
