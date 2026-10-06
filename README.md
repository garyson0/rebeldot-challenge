# rebeldot-challenge

Semantic FAQ assistant: vector search (pgvector) with LLM fallback.

A user asks a question, the assistant looks for the most similar question in the FAQ.
If it finds a close match, it answers from the FAQ, otherwise it asks OpenAI.
Questions that are not IT related get a fixed "I cannot answer" response.

## How it works

```
User question
     │
     ▼
Jailbreak phrase? ──yes──► Compliance answer
     │ no
     ▼
Embed question + search FAQ (pgvector)
     │
     ▼
Similarity >= 0.5? ──yes──► FAQ answer, personalized by the LLM
     │ no
     ▼
LLM router: IT related? ──yes──► Answer from OpenAI
     │ no
     ▼
Compliance answer
```

1. **Input guard**: questions with typical jailbreak phrases are refused before any API call.
2. **Search**: the question is embedded (`text-embedding-3-small`) and compared to the FAQ with cosine similarity in Postgres (pgvector, HNSW index).
3. **Router**: a close match (score >= 0.5) is answered from the FAQ. Otherwise a small LLM (`gpt-5.4-nano`) decides if the question is IT related: yes goes to OpenAI, no gets the compliance answer.
4. **Answer**: FAQ answers are rewritten to fit the question (`gpt-5.4-mini`), using only the facts from the FAQ. Every LLM answer goes through an output check.

Response format:

```json
{
  "source": "local",
  "matched_question": "How can I restore my account to its default settings?",
  "answer": "In your account settings, look for Restore Default..."
}
```

`source` is `local`, `openai` or `compliance`. `matched_question` is `N/A` when the answer is not from the FAQ.

## Project structure

```
app/
  main.py              FastAPI app, error handlers
  api/routes/          /ask-question and /health endpoints
  core/                settings, API token check, exceptions
  db/                  database session, FaqItem model
  llm/                 LangChain chat + embedding models, prompts
  services/            search, router, guardrails, answering, FAQ sync
  utils/clean_faq.py   FAQ data cleaning
alembic/               database migrations
scripts/               load_faq.py, evaluate.py
data/                  FAQ data and evaluation questions
tests/                 unit, api and integration tests
```

## Setup

Copy `.env.example` to `.env` and fill in:

| Variable               | Description                                        |
| ---------------------- | -------------------------------------------------- |
| `OPENAI_API_KEY`       | OpenAI API key                                     |
| `API_TOKEN`            | Token the clients must send to use the API         |
| `POSTGRES_*`           | Database settings (defaults work with Docker)      |
| `CHAT_MODEL`           | Model for answers (default `gpt-5.4-mini`)         |
| `ROUTER_MODEL`         | Model for the router (default `gpt-5.4-nano`)      |
| `EMBEDDING_MODEL`      | Embedding model (default `text-embedding-3-small`) |
| `SIMILARITY_THRESHOLD` | Minimum score for a FAQ answer (default `0.5`)     |

Generate an API token, e.g.: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### With Docker

```bash
docker compose up -d --build
docker compose exec api python scripts/load_faq.py   # first time: embed the FAQ
```

The API runs on http://localhost:8000 (docs: http://localhost:8000/docs).
Migrations run automatically when the container starts.

### Locally

Needs Python 3.14 and the Postgres container.

```bash
python -m venv .venv
.venv\Scripts\activate            
pip install -e ".[dev]"

docker compose up -d postgres
alembic upgrade head
python scripts/load_faq.py
uvicorn app.main:app --reload
```

## Usage

```bash
curl -X POST http://localhost:8000/ask-question \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"user_question": "How do I reset my account?"}'
```

| Status | When                                              |
| ------ | ------------------------------------------------- |
| 200    | Answer returned                                   |
| 401    | Missing or wrong API token                        |
| 422    | Missing or empty question (max 500 characters)    |
| 503    | OpenAI or the database is not available           |
| 500    | Unexpected error (details only in the server log) |

## Scripts

- `python scripts/load_faq.py`: cleans `data/faq.json` and loads it into the database. Only new or changed questions are embedded (checked with a content hash), so running it again costs no tokens. If only an answer changes, it is updated without a new embedding.
- `python scripts/evaluate.py`: runs the evaluation below.

## FAQ data cleaning

The FAQ data has some weird items:

- `"x"`: one-word question, skipped
- `"help!!! 😭😭😭 my account is locked"`: the answer is a user message, not an answer, skipped
- non-breaking hyphens (`7‑day`) are replaced with normal ones
- the category is embedded together with the question (`profile: Edit avatar?`), which gives short questions more context

## Guardrails and error handling

- **Input guard**: a list of typical jailbreak phrases ("ignore previous instructions", "system prompt", "you are now", ...). A match gets the compliance answer, without any API call.
- **Prompts**: the user's question is wrapped in `<question>` tags, and every prompt says it is only a question, never instructions.
- **Router**: off-topic questions and attempts to change the instructions go to compliance.
- **Output guard**: LLM answers that are empty, too long, contain an API key or leak the prompt are replaced (by the FAQ answer or a safe fallback message).
- **Errors**: OpenAI and database errors return 503. If the router or the personalization fails, the assistant falls back (to OpenAI or to the original FAQ answer). Other errors return 500 without details.
- **Auth**: `/ask-question` needs a Bearer token (`Depends(get_token)`); `/health` is open.

## Changing the model or provider

All models are created in `app/llm/client.py` with LangChain (`init_chat_model`, `OpenAIEmbeddings`).

- Another OpenAI model: change `CHAT_MODEL`, `ROUTER_MODEL` or `EMBEDDING_MODEL` in `.env`.
- Another provider: change `client.py` only, the rest of the code uses LangChain interfaces.
- The prompts are in `app/llm/prompts.py`.

A new embedding model with a different size needs a new migration (the vector column is 1536 long). Changing the model also changes the content hash, so `load_faq.py` embeds everything again.

## Tests and linting

```bash
ruff check .
ruff format --check .
pytest -m "not integration"   # no database or OpenAI needed
pytest                        # all tests
```

The tests never call OpenAI: LLMs and embeddings are replaced with fakes.

## Evaluation

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


### Third evaluation: guardrails

- Added a list of typical jailbreak phrases to check against before any embedding or LLM call
- The users question is wrapped in <question> tags in every prompt, and the prompts say it is only a question, never instructions


- Before: no guard, only the LLM router
- After: input guard + LLM router

| Result                                     | Before | After |
| ------------------------------------------ | ------ | ----- |
| Jailbreaks ending in compliance (out of 8) |   4    |   8   |
| Normal questions wrongly blocked (of 21)   |   -    |   0   |

## How to evaluate quality

What we measure now (objective):

- **Retrieval**: is the best FAQ match the expected one? (correct match)
- **Routing**: does each question go to the right place? (correct route)
- **Threshold**: chosen from the scores of correct matches and non-matches
- **Guardrails**: how many jailbreaks are blocked, and how many normal questions are wrongly blocked

What could be added (subjective):

- **Sticks to the FAQ**: does the personalized answer use only facts from the FAQ, without adding new ones?
- **Unseen jailbreaks**: a separate set of attacks that was not used to write the phrase list.
- **Real usage**: once real users ask questions, track how often each route is used and how often the output guard replaces an answer.

The core steps to evaluate from an AI/ML point of view: the embeddings (retrieval quality), the threshold, the router decision, and the generated answers.

## Known limitations

- *"How do I change my profile picture?"* matches *"How do I change my profile information?"* instead of *"Edit avatar?"*. The score is high, so no threshold fixes it.
- The jailbreak phrase list was written with the 8 test attacks in mind, so new wordings may get past it. The `<question>` tags, the router and the output guard are the next layers.
- The evaluation set is small (22 questions + 8 jailbreaks)
- LLM answers are not always the same, so the router results can change a little between runs.
