"""Evaluation of FAQ search performance.

For every question it prints the best FAQ match and its score, then:
- counts how many retrieved matches align with the expected FAQ question
- for different thresholds: counts how many questions are routed correctly
- counts the correct routes for LLM router (local,openai,compliance)
"""

import json
from pathlib import Path

from app.db.session import SessionLocal
from app.services.retrieval import find_best_match
from app.services.router import choose_route

EVAL_FILE = Path("data/eval_questions.json")
THRESHOLDS = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]


def evaluate() -> None:
    with EVAL_FILE.open(encoding="utf-8") as f:
        cases = json.load(f)

    # best matches
    results = []
    with SessionLocal() as db:
        for case in cases:
            match = find_best_match(db, case["question"])
            results.append(
                {
                    "question": case["question"],
                    "expected": case["expected_match"],
                    "expected_route": case["expected_route"],
                    "matched": match.question,
                    "score": match.similarity,
                    "is_correct": match.question == case["expected_match"],
                }
            )

    # correct match count
    print("\n Correct match count")
    total = 0
    correct = 0
    for result in results:
        if result["expected"] is not None:
            total += 1
            if result["is_correct"]:
                correct += 1
    print(f"\nCorrect match: {correct}/{total}")

    # correct route counts for different thresholds
    print("\n Correct route counts")
    for threshold in THRESHOLDS:
        correct_route = 0
        for result in results:
            goes_to_faq = result["score"] >= threshold
            if result["expected"] is None and not goes_to_faq:
                correct_route += 1
            elif result["is_correct"] and goes_to_faq:
                correct_route += 1
        print(f"{threshold}       {correct_route}/{len(results)}")

    # router LLM
    print("\n Router")
    correct_route = 0
    for result in results:
        route = choose_route(result["question"], result["score"])
        if route == result["expected_route"] and (route != "local" or result["is_correct"]):
            correct_route += 1
        else:
            print(f"wrong: {result['question']} -> {route}, expected {result['expected_route']}")
    print(f"Correct route: {correct_route}/{len(results)}")


if __name__ == "__main__":
    evaluate()
