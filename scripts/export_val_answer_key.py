import argparse
import csv
import json
import os
from typing import Dict, List


def _load_val(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("val.json must be a list of items")
    return data


def _extract_key(items: List[dict]) -> Dict[str, str]:
    key: Dict[str, str] = {}
    for item in items:
        qid = str(item.get("qid", "")).strip()
        ans = str(item.get("answer", "")).strip().upper()
        if not qid:
            raise ValueError("Missing qid in an item")
        if ans not in list("ABCDEFG"):
            # val set should be clean; fail fast to avoid silent bugs
            raise ValueError(f"Invalid answer '{ans}' for qid={qid}")
        key[qid] = ans
    return key


def _write_csv(path: str, key: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "answer"])
        writer.writeheader()
        for qid in sorted(key.keys()):
            writer.writerow({"qid": qid, "answer": key[qid]})


def _write_json(path: str, key: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(key, f, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export answer key from AInicorns public val.json for offline scoring"
    )
    parser.add_argument(
        "--val",
        default=os.path.join("..", "..", "AInicorns_TheBuilder_public", "data", "val.json"),
        help="Path to val.json (default: ../../AInicorns_TheBuilder_public/data/val.json)",
    )
    parser.add_argument(
        "--out-csv",
        default=os.path.join("output", "val_answer_key.csv"),
        help="Output CSV path (default: output/val_answer_key.csv)",
    )
    parser.add_argument(
        "--out-json",
        default=os.path.join("output", "val_answer_key.json"),
        help="Output JSON path (default: output/val_answer_key.json)",
    )
    args = parser.parse_args()

    val_path = os.path.normpath(os.path.join(os.path.dirname(__file__), args.val))

    items = _load_val(val_path)
    key = _extract_key(items)

    _write_csv(args.out_csv, key)
    _write_json(args.out_json, key)

    print(f"Wrote {len(key)} answers")
    print(f"- {args.out_csv}")
    print(f"- {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
