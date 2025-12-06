"""
Evaluation script for validation set
"""
import json
import csv
import sys
import os
from collections import defaultdict
from typing import Dict, List

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.question_classifier import classifier
from modules.categories import QuestionCategory


def load_ground_truth(val_file: str = "data/val.json") -> List[Dict]:
    """Load validation set with ground truth"""
    with open(val_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_predictions(pred_file: str = "submission.csv") -> Dict[str, str]:
    """Load predictions from CSV"""
    predictions = {}
    with open(pred_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            predictions[row['qid']] = row['answer']
    return predictions


def calculate_accuracy(ground_truth: List[Dict], predictions: Dict[str, str]) -> Dict:
    """
    Calculate overall and per-category accuracy

    Returns:
        Dict with accuracy metrics
    """
    total = 0
    correct = 0
    category_stats = defaultdict(lambda: {'total': 0, 'correct': 0})

    for item in ground_truth:
        qid = item['qid']
        true_answer = item['answer']
        question = item['question']

        # Get prediction
        pred_answer = predictions.get(qid, 'A')  # Default A if missing

        # Classify question
        category, _ = classifier.classify(question)

        # Update stats
        total += 1
        category_stats[category.value]['total'] += 1

        if pred_answer == true_answer:
            correct += 1
            category_stats[category.value]['correct'] += 1

    # Calculate accuracies
    overall_acc = (correct / total * 100) if total > 0 else 0

    category_accs = {}
    for cat, stats in category_stats.items():
        if stats['total'] > 0:
            category_accs[cat] = {
                'accuracy': stats['correct'] / stats['total'] * 100,
                'correct': stats['correct'],
                'total': stats['total']
            }

    return {
        'overall_accuracy': overall_acc,
        'total_questions': total,
        'correct_answers': correct,
        'category_breakdown': category_accs
    }


def print_results(results: Dict):
    """Pretty print results"""
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)

    print(f"\nOverall Accuracy: {results['overall_accuracy']:.2f}%")
    print(f"Correct: {results['correct_answers']}/{results['total_questions']}")

    print("\n" + "-"*60)
    print("Per-Category Breakdown:")
    print("-"*60)

    # Sort by total questions
    categories = sorted(
        results['category_breakdown'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )

    print(f"{'Category':<20} {'Accuracy':<12} {'Correct/Total':<15}")
    print("-"*60)

    for cat, stats in categories:
        acc = stats['accuracy']
        correct = stats['correct']
        total = stats['total']

        # Color coding
        if acc >= 80:
            status = "🟢"
        elif acc >= 70:
            status = "🟡"
        else:
            status = "🔴"

        print(f"{cat:<20} {status} {acc:>6.2f}%    {correct:>3}/{total:<3}")

    print("="*60 + "\n")


def find_errors(ground_truth: List[Dict], predictions: Dict[str, str]) -> List[Dict]:
    """Find all incorrect predictions"""
    errors = []

    for item in ground_truth:
        qid = item['qid']
        true_answer = item['answer']
        question = item['question']

        pred_answer = predictions.get(qid, 'A')

        if pred_answer != true_answer:
            category, confidence = classifier.classify(question)

            errors.append({
                'qid': qid,
                'question': question[:100] + "..." if len(question) > 100 else question,
                'true_answer': true_answer,
                'pred_answer': pred_answer,
                'category': category.value,
                'confidence': confidence
            })

    return errors


def save_error_analysis(errors: List[Dict], output_file: str = "evaluation/errors.json"):
    """Save error analysis to file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(errors, f, ensure_ascii=False, indent=2)

    print(f"Error analysis saved to: {output_file}")


def main():
    """Main evaluation"""
    # Paths
    val_file = "data/val.json"
    pred_file = "submission.csv"

    # Check files exist
    if not os.path.exists(val_file):
        print(f"Error: {val_file} not found!")
        return

    if not os.path.exists(pred_file):
        print(f"Error: {pred_file} not found!")
        print("Run predict.py first to generate predictions.")
        return

    print("Loading data...")
    ground_truth = load_ground_truth(val_file)
    predictions = load_predictions(pred_file)

    print(f"Loaded {len(ground_truth)} validation questions")
    print(f"Loaded {len(predictions)} predictions")

    # Calculate accuracy
    print("\nCalculating accuracy...")
    results = calculate_accuracy(ground_truth, predictions)

    # Print results
    print_results(results)

    # Find errors
    print("Analyzing errors...")
    errors = find_errors(ground_truth, predictions)
    print(f"Found {len(errors)} errors")

    # Save error analysis
    save_error_analysis(errors)

    # Print some example errors
    if errors:
        print("\nSample Errors (first 3):")
        print("-"*60)
        for err in errors[:3]:
            print(f"\nQID: {err['qid']}")
            print(f"Category: {err['category']} (confidence: {err['confidence']:.2f})")
            print(f"Question: {err['question']}")
            print(f"True: {err['true_answer']}, Predicted: {err['pred_answer']}")

    # Return results
    return results


if __name__ == "__main__":
    main()
