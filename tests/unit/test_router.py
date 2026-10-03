from app.services.router import choose_route


def test_similar_enough_match_is_answered_locally():
    assert choose_route(0.85, threshold=0.7) == "local"


def test_match_exactly_at_threshold_is_answered_locally():
    assert choose_route(0.7, threshold=0.7) == "local"


def test_weak_match_goes_to_openai():
    assert choose_route(0.69, threshold=0.7) == "openai"


def test_no_match_goes_to_openai():
    assert choose_route(None, threshold=0.7) == "openai"
