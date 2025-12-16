import argparse
import csv
import json
import os
from typing import Dict, Tuple


VALID_ANSWERS = set("ABCDEFGHIJ")


def _load_key(path: str) -> Dict[str, str]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Key JSON must be a dict: {qid: answer}")
        key = {str(k): str(v).strip().upper() for k, v in data.items()}
    else:
        key = {}
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "qid" not in reader.fieldnames or "answer" not in reader.fieldnames:
                raise ValueError("Key CSV must have columns: qid, answer")
            for row in reader:
                qid = str(row.get("qid", "")).strip()
                ans = str(row.get("answer", "")).strip().upper()
                if qid:
                    key[qid] = ans

    bad = [(qid, ans) for qid, ans in key.items() if ans not in VALID_ANSWERS]
    if bad:
        sample = ", ".join([f"{qid}={ans}" for qid, ans in bad[:5]])
        raise ValueError(f"Key contains invalid answers (sample: {sample})")

    return key


def _load_pred_csv(path: str) -> Dict[str, str]:
    pred: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "qid" not in reader.fieldnames or "answer" not in reader.fieldnames:
            raise ValueError("Prediction CSV must have columns: qid, answer")
        for row in reader:
            qid = str(row.get("qid", "")).strip()
            ans = str(row.get("answer", "")).strip().upper()
            if qid:
                pred[qid] = ans
    return pred


def _score(key: Dict[str, str], pred: Dict[str, str]) -> Tuple[int, int, int, int]:
    total = len(key)
    correct = 0
    missing = 0
    invalid = 0

    for qid, gold in key.items():
        if qid not in pred:
            missing += 1
            continue
        ans = pred[qid]
        if ans not in VALID_ANSWERS:
            invalid += 1
            continue
        if ans == gold:
            correct += 1

    return total, correct, missing, invalid


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a prediction CSV against a ground-truth answer key")
    parser.add_argument(
        "--pred",
        default=os.path.join("output", "submission.csv"),
        help="Prediction CSV path (default: output/submission.csv)",
    )
    parser.add_argument(
        "--key",
        default=os.path.join("output", "val_answer_key.csv"),
        help="Answer key path (.csv or .json). Default: output/val_answer_key.csv",
    )
    parser.add_argument(
        "--show-wrong",
        type=int,
        default=0,
        help="Print up to N wrong items (qid, pred, gold). Default: 0",
    )
    args = parser.parse_args()

    key = _load_key(args.key)
    pred = _load_pred_csv(args.pred)

    # Diagnostics: overlap check (common mistake: scoring test_* against val_* key)
    overlap = set(key.keys()) & set(pred.keys())
    if not overlap:
        # Print a short, actionable hint and still compute the score (will be all-missing)
        key_sample = next(iter(key.keys())) if key else "(empty)"
        pred_sample = next(iter(pred.keys())) if pred else "(empty)"
        key_prefix = key_sample.split("_", 1)[0] if "_" in key_sample else key_sample
        pred_prefix = pred_sample.split("_", 1)[0] if "_" in pred_sample else pred_sample
        print("\nWARN No overlapping qids between --pred and --key")
        print(f"  Sample key qid:  {key_sample} (prefix: {key_prefix})")
        print(f"  Sample pred qid: {pred_sample} (prefix: {pred_prefix})")
        print("  Tip: `val_answer_key.*` only matches predictions generated from val.json (qid starts with val_*)")
        print("       Your `output/submission.csv` is from test.json (qid starts with test_*), so it can't be scored here.")

    total, correct, missing, invalid = _score(key, pred)
    answered = total - missing
    denom = max(total, 1)

    print(f"Key size: {total}")
    print(f"Pred rows: {len(pred)}")
    print(f"Correct: {correct}")
    print(f"Missing: {missing}")
    print(f"Invalid answers: {invalid}")
    print(f"Accuracy (correct/total): {correct}/{total} = {correct/denom:.4f}")
    if answered > 0:
        print(f"Accuracy on answered only: {correct}/{answered} = {correct/answered:.4f}")

    if args.show_wrong > 0:
        shown = 0
        for qid, gold in key.items():
            if qid not in pred:
                continue
            pa = pred[qid].strip().upper()
            if pa not in VALID_ANSWERS or pa != gold:
                print(f"WRONG {qid}: pred={pa} gold={gold}")
                shown += 1
                if shown >= args.show_wrong:
                    break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
