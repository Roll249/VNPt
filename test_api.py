"""
Quick API test on 10 questions
"""
import json
import sys
import os
import csv

# Fix encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Import pipeline
from predict import SimplePipeline


def main():
    # Load 10 test questions
    input_file = "data/val_10.json"
    output_file = "submission_10.csv"

    print(f"Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions")
    print("="*60)

    # Initialize pipeline
    pipeline = SimplePipeline()

    # Predict
    results = []
    for i, q in enumerate(questions):
        qid = q['qid']
        question = q['question']
        choices = q['choices']
        true_answer = q.get('answer', '?')

        print(f"\n[{i+1}/{len(questions)}] {qid}")
        print(f"Question: {question[:80]}...")
        print(f"True answer: {true_answer}")

        try:
            answer = pipeline.predict_single(question, choices, qid)
            print(f"Predicted: {answer}")

            match = "[OK]" if answer == true_answer else "[FAIL]"
            print(match)

            results.append({'qid': qid, 'answer': answer, 'true': true_answer})

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({'qid': qid, 'answer': 'A', 'true': true_answer})

        print("-"*60)

    # Save results
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
        writer.writeheader()
        for r in results:
            writer.writerow({'qid': r['qid'], 'answer': r['answer']})

    print(f"\n✓ Saved to {output_file}")

    # Calculate accuracy
    correct = sum(1 for r in results if r['answer'] == r['true'])
    total = len(results)
    accuracy = (correct / total * 100) if total > 0 else 0

    print(f"\n{'='*60}")
    print(f"RESULTS: {correct}/{total} correct ({accuracy:.1f}%)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
