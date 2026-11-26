"""Build data/golden_tickets.jsonl from the hand-labelled tweets.

The output holds tweet IDs and labels only, never tweet text: the tweets
belong to their authors (Customer Support on Twitter, CC BY-NC-SA 4.0).

Usage:
    python scripts/build_golden.py --labels path/to/labels_clean.csv \
        --dev-ids path/to/dev_ids.txt --test-ids path/to/test_ids.txt
"""
import argparse
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "golden_tickets.jsonl"


def read_ids(path: str) -> set[str]:
    return {line.strip() for line in open(path, encoding="utf-8") if line.strip()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--dev-ids", required=True)
    ap.add_argument("--test-ids", required=True)
    args = ap.parse_args()

    dev, test = read_ids(args.dev_ids), read_ids(args.test_ids)
    rows = []
    with open(args.labels, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tid = r["tweet_id"]
            split = "dev" if tid in dev else "test" if tid in test else None
            if split is None:
                raise SystemExit(f"tweet {tid} is in neither dev nor test")
            rows.append({
                "tweet_id": tid,
                "topic": r["topic"],
                "urgency": r["urgency"],
                "multi_issue": r["multi_issue"] == "yes",
                "split": split,
            })

    rows.sort(key=lambda x: (x["split"], int(x["tweet_id"])))
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
