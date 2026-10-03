from app.core.config import settings


def choose_route(similarity: float | None, threshold: float | None = None) -> str:
    """Return "local" if the best FAQ match is similar, otherwise "openai".

    ``similarity`` is None when the FAQ has no items.
    """
    if threshold is None:
        threshold = settings.similarity_threshold

    if similarity is not None and similarity >= threshold:
        return "local"
    return "openai"
