import argparse
import csv
import json
import os
import sys
from typing import Dict, List, Set

# Ensure repo root is importable when run from anywhere
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from predict import SimplePipeline  # noqa: E402
from modules.llm.api_client import RateLimitException  # noqa: E402


def _load_val_items(val_path: str) -> List[dict]:
    with open(val_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("val.json must be a list")
    return data


def _load_answered(output_csv: str) -> Set[str]:
    answered: Set[str] = set()
    if not os.path.exists(output_csv):
        return answered

    with open(output_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "qid" not in reader.fieldnames:
            return answered
        for row in reader:
            qid = str(row.get("qid", "")).strip()
            if qid:
                answered.add(qid)
    return answered


def _append_rows(output_csv: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    file_exists = os.path.exists(output_csv)
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "answer"])
        if not file_exists or os.stat(output_csv).st_size == 0:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run pipeline on public val.json and write predictions CSV")
    parser.add_argument(
        "--val",
        default=os.path.join("..", "..", "AInicorns_TheBuilder_public", "data", "val.json"),
        help="Path to val.json (default: ../../AInicorns_TheBuilder_public/data/val.json)",
    )
    parser.add_argument(
        "--out",
        default=os.path.join("output", "val_pred.csv"),
        help="Output CSV path (default: output/val_pred.csv)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="If >0, only process first N questions (useful for quick checks)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip qids already present in --out",
    )
    args = parser.parse_args()

    val_path = os.path.normpath(os.path.join(os.path.dirname(__file__), args.val))
    out_csv = args.out

    items = _load_val_items(val_path)
    if args.limit and args.limit > 0:
        items = items[: args.limit]

    pipeline = SimplePipeline()

    answered = _load_answered(out_csv) if args.resume else set()
    to_write: List[Dict[str, str]] = []

    processed = 0
    skipped = 0

    for idx, item in enumerate(items, start=1):
        qid = str(item.get("qid", "")).strip()
        question = item.get("question", "")
        choices = item.get("choices", [])

        if not qid:
            continue
        if qid in answered:
            skipped += 1
            continue

        print(f"[{idx}/{len(items)}] {qid}")
        try:
            ans = pipeline.predict_single(question, choices, qid)
        except RateLimitException:
            print("🛑 Rate limit hit. Stop now; rerun later with --resume.")
            break
        except KeyboardInterrupt:
            print("\n🛑 Interrupted. Partial results kept.")
            break
        except Exception as e:
            # Keep this conservative: don't guess; mark as A to keep CSV valid
            print(f"  ⚠ Error: {e}")
            ans = "A"

        to_write.append({"qid": qid, "answer": str(ans).strip().upper()})
        processed += 1

        # flush every 10
        if len(to_write) >= 10:
            _append_rows(out_csv, to_write)
            to_write.clear()

    if to_write:
        _append_rows(out_csv, to_write)

    print(f"Done. processed={processed}, skipped={skipped}, out={out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
