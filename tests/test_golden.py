"""Checks on the golden set. No model calls: safe to run in CI."""
import json
from pathlib import Path
from typing import get_args

import pytest

from support_copilot.schemas import Topic, Urgency

GOLDEN = Path(__file__).resolve().parent.parent / "data" / "golden_tickets.jsonl"
FIELDS = {"tweet_id", "topic", "urgency", "multi_issue", "split"}


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line]


def test_fields_exact_and_no_text(rows):
    for r in rows:
        assert set(r) == FIELDS, r["tweet_id"]


def test_labels_are_valid(rows):
    for r in rows:
        assert r["topic"] in get_args(Topic), r
        assert r["urgency"] in get_args(Urgency), r
        assert isinstance(r["multi_issue"], bool), r


def test_ids_unique(rows):
    ids = [r["tweet_id"] for r in rows]
    assert len(ids) == len(set(ids))


def test_splits_valid_and_disjoint(rows):
    dev = {r["tweet_id"] for r in rows if r["split"] == "dev"}
    test = {r["tweet_id"] for r in rows if r["split"] == "test"}
    assert dev and test
    assert not dev & test
    assert len(dev) + len(test) == len(rows)


def test_every_topic_in_test_split(rows):
    in_test = {r["topic"] for r in rows if r["split"] == "test"}
    labelled = {r["topic"] for r in rows}
    assert labelled <= in_test
