from app.utils.clean_faq import clean_item, clean_text


def make_item(question: str, answer: str = "Some answer.") -> dict:
    return {"question": question, "answer": answer, "category": "security"}


def test_normal_item_is_kept_unchanged():
    item = make_item("How do I add a payment method?")

    assert clean_item(item) == item


def test_special_hyphens_are_replaced():
    item = make_item("Delete my account", answer="Permanent after a 7‑day grace period.")

    assert clean_item(item)["answer"] == "Permanent after a 7-day grace period."


def test_one_word_question_is_skipped():
    assert clean_item(make_item("x")) is None


def test_item_with_emoji_answer_is_skipped():
    item = make_item("help!!! my account is locked", answer="pls help me unlock it ASAP!!! 🔓🔓🔓")

    assert clean_item(item) is None


def test_clean_text_removes_emoji_and_extra_spaces():
    assert clean_text("help!!!  😭😭😭 my account") == "help!!! my account"
