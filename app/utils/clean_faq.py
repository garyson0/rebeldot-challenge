import re

EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")


def clean_text(text: str) -> str:
    """Replace the wrong hyphen, remove emoji + extra spaces."""
    text = text.replace("‑", "-")
    text = EMOJI.sub("", text)
    return " ".join(text.split())


def clean_item(item: dict) -> dict | None:
    """Return the cleaned item or None."""
    question = clean_text(item["question"])
    if len(question.split()) < 2 or EMOJI.search(item["answer"]):
        return None

    return {
        "question": question,
        "answer": item["answer"].replace("‑", "-"),
        "category": item["category"],
    }


def build_embedding_text(item: dict) -> str:
    """Embedding the category before the question for context."""
    category = item["category"].replace("_", " ")
    return f"{category}: {item['question']}"
