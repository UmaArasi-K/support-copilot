"""Add tweet text to the golden set from your own copy of twcs.csv.

The text is not in this repo. Download "Customer Support on Twitter" from
Kaggle (CC BY-NC-SA 4.0), then run:

    python scripts/attach_text.py --twcs path/to/twcs.csv

Writes data/golden_with_text.jsonl, which is git-ignored. Never commit it.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
MENTION = re.compile(r"@\w+")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--twcs", required=True)
    args = ap.parse_args()

    golden = [json.loads(line) for line in open(DATA / "golden_tickets.jsonl", encoding="utf-8")]
    wanted = {g["tweet_id"] for g in golden}
    text = {}
    csv.field_size_limit(sys.maxsize)
    with open(args.twcs, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["tweet_id"] in wanted:
                text[r["tweet_id"]] = MENTION.sub("@user", r["text"])

    missing = wanted - text.keys()
    out = DATA / "golden_with_text.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for g in golden:
            if g["tweet_id"] in text:
                f.write(json.dumps({**g, "text": text[g["tweet_id"]]}) + "\n")
    print(f"wrote {len(golden) - len(missing)} rows to {out}; missing {len(missing)}")


if __name__ == "__main__":
    main()
