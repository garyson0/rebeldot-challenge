import pytest
from sqlalchemy import delete

from app.db.models import FaqItem
from app.services.retrieval import find_best_match

pytestmark = pytest.mark.integration

PASSWORD_VECTOR = [1.0, 0.0] + [0.0] * 1534
BILLING_VECTOR = [0.0, 1.0] + [0.0] * 1534


class FakeEmbeddings:
    """Embeds every question as PASSWORD_VECTOR, no OpenAI call."""

    def embed_query(self, text: str) -> list[float]:
        return PASSWORD_VECTOR


def test_returns_most_similar_item(db_session):
    db_session.execute(delete(FaqItem))  # rolled back after test
    db_session.add_all(
        [
            FaqItem(question="Reset password?", answer="", category="", embedding=PASSWORD_VECTOR),
            FaqItem(question="Cancel plan?", answer="", category="", embedding=BILLING_VECTOR),
        ]
    )

    match = find_best_match(db_session, "I forgot my password", FakeEmbeddings())

    assert match.question == "Reset password?"
    assert match.similarity == pytest.approx(1.0)


def test_returns_none_when_faq_is_empty(db_session):
    db_session.execute(delete(FaqItem))

    assert find_best_match(db_session, "anything", FakeEmbeddings()) is None
