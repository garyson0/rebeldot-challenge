# rebeldot-challenge

Semantic FAQ assistant: vector search (pgvector) with LLM fallback.

### Evaluation

- Script used to evaluate results: `scripts/evaluate.py`
- 22 test qeustions in `data/eval_questions.json`:
  - 16 questions that should match a concrete FAQ question
  - 6 questions that should not match anything

Two numbers:
- Correct match count: how many questions get the expected match, when we do retrieval
- Correct route count: how many questions go to the right place (FAQ answer when there is a match, OpenAI when there is no match)

### First evaluation: retrieval

- Cleaned the FAQ data (skip "x" and emoji, fix wrong hyphens)
- Embedded the category with question
- Changed threshold from 0.70 (initial guess) to 0.50

- Before: raw question text embedded
- After: cleaned data, category + question embedded, threshold 0.50

| Result                          | Before | After |
| ------------------------------- | ------ | ----- |
| Correct match (out of 16)       |   14   |  15   |
| Correct route (out of 22)       |   20   |  21   | # threshold 0.5

- Lowest score of a correct match changed from 0.585 to 0.567
- Highest score of a non-match changed from 0.388 to 0.341
- Minor improvement from 14 to 15 correct match and from 20 to 21 correct route

### Second evaluation: LLM router

- Added a third route: compliance, for questions that are not related to the topic
- If there is no FAQ match, checks with gpt-5.4-nano if the question is on topic
- Updated test questions: 16 local, 3 openai, 3 compliance

- Before: threshold only, questions without a FAQ match went to OpenAI
- After: threshold + LLM topic check

| Result                    | Before | After |
| ------------------------- | ------ | ----- |
| Correct route (out of 22) |   18   |  21   |

- Before 3 off-topic questions were sent to OpenAI
- The 1 remaining miss is the profile picture question (wrong FAQ match)

