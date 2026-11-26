# Support Copilot

A GenAI support copilot that triages tickets, answers questions from help docs with citations, and escalates to a human when needed.

**Status:** in progress (Nov 2026). Triage (`support_copilot/triage.py`) works end to end against Azure OpenAI. The API, the RAG answers and the agent are next.

## Features
- **Triage (done):** a ticket goes in, validated JSON comes out (`topic`, `urgency`, `summary`). Uses strict structured output, then Pydantic validation, and raises a clear error on invalid output.
- **Prompt-injection defences (done):** delimited ticket text, rules in the prompt, a leak check on the summary, a pre-filled-JSON check in code, and content-filter handling. Tested on 9 attack cases: see [docs/injection-testing.md](docs/injection-testing.md).
- `/classify` (planned): the triage step as a FastAPI endpoint.
- `/answer` (planned): answers from help docs, with citations.
- `/agent` (planned): a LangGraph agent that searches docs, looks up orders, or escalates.

## Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env         # then fill in your Azure OpenAI endpoint, key, API version and deployment
python -m support_copilot.triage   # classifies a few sample tickets
python -m pytest                   # golden-set checks, no model calls
```

## Golden set: how it was built
`data/golden_tickets.jsonl`: 111 real customer tweets, labelled by hand **before** any model was run on them.

| Split | Rows | Use |
|---|---|---|
| dev | 34 | Tune the prompt freely |
| test | 77 | Run once at the end; never tune on it |

- **Source:** first messages of conversations written by customers in *Customer Support on Twitter* (Kaggle), 40 to 400 characters, mostly English, duplicates removed.
- **Sampling:** keyword hints (login, payment, bug, order/delivery, plus no match) picked candidate rows so every topic is represented. The hints were not used as labels.
- **Labels:** `topic` (billing, account_access, bug, order_delivery, other, not_support), `urgency` (high, medium, low), `multi_issue`. The labelling rules are the same, word for word, as the prompt's `<topic_definitions>` and `<urgency_definitions>`.
- **Discards:** rows too vague to label, or about an employee rather than a customer, were dropped (3 more are still under review).
- **Split:** stratified by topic, 30% dev, seed 42.
- **Label review:** after the first pass, rows where similar tickets got different urgencies were reviewed 7 urgency labels were corrected and 1 missing urgency was filled in, all before any model run on the test split.
- **Topic counts (all rows):** order_delivery 29, bug 23, account_access 22, billing 21, other 16.

The file holds **tweet IDs and labels only, no tweet text.** To rebuild the text locally from your own download:

```bash
python scripts/attach_text.py --twcs path/to/twcs.csv
```

This writes `data/golden_with_text.jsonl`, which is git-ignored. To regenerate the label file from the labelling CSVs, use `scripts/build_golden.py`.

## Data and licences
- **Code:** MIT (see `LICENSE`).
- **Customer Support on Twitter** (Kaggle, by Thought Vector): CC BY-NC-SA 4.0. Credit to the dataset authors; non-commercial use only. The labels in `data/golden_tickets.jsonl` are a derivative work, so they are shared under the same licence (CC BY-NC-SA 4.0), not under MIT. Tweet text is not redistributed.

## Limitations
- **Small set.** On the 77-ticket test split, an accuracy figure has a margin of roughly ±8 to 9 points (95%), so small differences between prompts are noise.
- **Not the real topic mix.** Sampling picked rows per topic, so the class balance does not reflect real ticket volumes.
- **English only.** The sample filter kept mostly-English tweets. Other languages are untested for accuracy.
- **One labeller.** All labels are my own judgement; a self-agreement check is still to do.
- **Multi-company data.** Tickets come from many brands (phones, streaming, airlines, delivery). The categories are company-agnostic, so this tests whether triage generalises; it is not tuned to one company.
