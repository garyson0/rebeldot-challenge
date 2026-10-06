import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.routes import ask
from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError
from app.main import app
from app.schemas.ask import AskResponse

client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}


@pytest.fixture(autouse=True)
def api_token(monkeypatch):
    monkeypatch.setattr(settings, "api_token", SecretStr("test-token"))


def test_returns_answer(monkeypatch):
    def mock_ask_question(db, question):
        return AskResponse(source="local", matched_question="Reset password?", answer="Do X.")

    monkeypatch.setattr(ask, "ask_question", mock_ask_question)

    response = client.post(
        "/ask-question", json={"user_question": "How do I reset my password?"}, headers=HEADERS
    )

    assert response.status_code == 200
    assert response.json() == {
        "source": "local",
        "matched_question": "Reset password?",
        "answer": "Do X.",
    }


def test_missing_question_is_rejected():
    response = client.post("/ask-question", json={}, headers=HEADERS)

    assert response.status_code == 422


def test_empty_question_is_rejected():
    response = client.post("/ask-question", json={"user_question": ""}, headers=HEADERS)

    assert response.status_code == 422


def test_openai_down_returns_503(monkeypatch):
    def ask_question(db, question):
        raise ServiceUnavailableError

    monkeypatch.setattr(ask, "ask_question", ask_question)

    response = client.post("/ask-question", json={"user_question": "question"}, headers=HEADERS)

    assert response.status_code == 503


def test_code_bug_returns_500_without_details(monkeypatch):
    def ask_question(db, question):
        raise KeyError("secret detail")

    monkeypatch.setattr(ask, "ask_question", ask_question)
    client_500 = TestClient(app, raise_server_exceptions=False)

    response = client_500.post("/ask-question", json={"user_question": "question"}, headers=HEADERS)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}


def test_missing_token_returns_401():
    response = client.post("/ask-question", json={"user_question": "question"})

    assert response.status_code == 401


def test_wrong_token_returns_401():
    headers = {"Authorization": "Bearer wrong-token"}

    response = client.post("/ask-question", json={"user_question": "question"}, headers=headers)

    assert response.status_code == 401
