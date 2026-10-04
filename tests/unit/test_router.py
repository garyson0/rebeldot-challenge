from app.services import router
from app.services.router import choose_route


def test_close_match_goes_to_faq():
    assert choose_route("question", 0.9, threshold=0.5) == "local"


def test_it_question_goes_to_openai(monkeypatch):
    monkeypatch.setattr(router, "check_topic", lambda question: True)

    assert choose_route("How does DNS work?", 0.2, threshold=0.5) == "openai"


def test_off_topic_question_goes_to_compliance(monkeypatch):
    monkeypatch.setattr(router, "check_topic", lambda question: False)

    assert choose_route("Best lasagna recipe?", 0.2, threshold=0.5) == "compliance"


def test_failed_topic_check_goes_to_openai(monkeypatch):
    def broken_check(question):
        raise TimeoutError

    monkeypatch.setattr(router, "check_topic", broken_check)

    assert choose_route("question", 0.2, threshold=0.5) == "openai"
