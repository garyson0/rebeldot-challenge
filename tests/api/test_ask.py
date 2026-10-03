from fastapi.testclient import TestClient

from app.api.routes import ask
from app.main import app
from app.schemas.ask import AskResponse

client = TestClient(app)


def test_returns_answer(monkeypatch):
    def mock_ask_question(db, question):
        return AskResponse(source="local", matched_question="Reset password?", answer="Do X.")

    monkeypatch.setattr(ask, "ask_question", mock_ask_question)

    response = client.post("/ask-question", json={"user_question": "How do I reset my password?"})

    assert response.status_code == 200
    assert response.json() == {
        "source": "local",
        "matched_question": "Reset password?",
        "answer": "Do X.",
    }


def test_missing_question_is_rejected():
    response = client.post("/ask-question", json={})

    assert response.status_code == 422


def test_empty_question_is_rejected():
    response = client.post("/ask-question", json={"user_question": ""})

    assert response.status_code == 422
