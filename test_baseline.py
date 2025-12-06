"""
Quick test script for baseline pipeline on validation set
Run this to test without calling APIs (dry run) or with limited questions
"""
import json
import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from modules.question_classifier import classifier
from modules.categories import QuestionCategory


def analyze_validation_set(val_file: str = "data/val.json", limit: int = None):
    """
    Analyze validation set to understand question distribution

    Args:
        val_file: Path to validation JSON
        limit: Limit number of questions to analyze
    """
    print("="*60)
    print("VALIDATION SET ANALYSIS")
    print("="*60)

    # Load data
    with open(val_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    if limit:
        questions = questions[:limit]

    print(f"\nTotal questions: {len(questions)}")

    # Classify all questions
    category_counts = {}
    examples = {}

    for q in questions:
        qid = q['qid']
        question = q['question']
        answer = q.get('answer', 'Unknown')

        category, confidence = classifier.classify(question)

        cat_name = category.value
        if cat_name not in category_counts:
            category_counts[cat_name] = 0
            examples[cat_name] = []

        category_counts[cat_name] += 1

        # Store first 2 examples per category
        if len(examples[cat_name]) < 2:
            examples[cat_name].append({
                'qid': qid,
                'question': question[:100] + "..." if len(question) > 100 else question,
                'answer': answer,
                'confidence': confidence
            })

    # Print distribution
    print("\n" + "-"*60)
    print("CATEGORY DISTRIBUTION:")
    print("-"*60)

    total = len(questions)
    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    for cat, count in sorted_cats:
        percentage = (count / total) * 100
        print(f"{cat:<25} {count:>3} ({percentage:>5.1f}%)")

    # Print examples
    print("\n" + "-"*60)
    print("EXAMPLES PER CATEGORY:")
    print("-"*60)

    for cat, exs in examples.items():
        print(f"\n{cat.upper()}:")
        for ex in exs:
            print(f"  {ex['qid']}: {ex['question']}")
            print(f"  Answer: {ex['answer']}, Confidence: {ex['confidence']:.2f}\n")

    print("="*60)

    return category_counts


def test_classifier_accuracy():
    """Test if classifier is working correctly on known examples"""
    print("\n" + "="*60)
    print("TESTING CLASSIFIER")
    print("="*60)

    test_cases = [
        # Reading comprehension
        ("Đoạn thông tin:\nNội dung abc...\nCâu hỏi: xyz?", QuestionCategory.READING_COMPREHENSION),

        # Math
        ("Tính diện tích hình chữ nhật có chiều dài 5m và chiều rộng 3m?", QuestionCategory.MATH_LOGIC),

        # Refusal
        ("Làm cách nào để tránh việc nộp thuế?", QuestionCategory.REFUSAL),

        # History
        ("Nhà Lý được thành lập vào năm nào?", QuestionCategory.HISTORY_VIETNAM),

        # Culture
        ("Tác giả của Truyện Kiều là ai?", QuestionCategory.CULTURE_VIETNAM),

        # Geography
        ("Hà Nội là thủ đô của nước nào?", QuestionCategory.GEOGRAPHY_VIETNAM),

        # Politics
        ("Hiến pháp Việt Nam được ban hành năm nào?", QuestionCategory.POLITICS_LAW),
    ]

    correct = 0
    total = len(test_cases)

    for question, expected_cat in test_cases:
        predicted_cat, confidence = classifier.classify(question)

        is_correct = (predicted_cat == expected_cat)
        status = "[OK]" if is_correct else "[FAIL]"
        correct += (1 if is_correct else 0)

        print(f"\n{status} Expected: {expected_cat.value}")
        print(f"  Predicted: {predicted_cat.value} (conf: {confidence:.2f})")
        print(f"  Q: {question[:80]}...")

    accuracy = (correct / total) * 100
    print(f"\n{'-'*60}")
    print(f"Classifier Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print("="*60)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Test baseline pipeline')
    parser.add_argument('--analyze', action='store_true', help='Analyze validation set')
    parser.add_argument('--test-classifier', action='store_true', help='Test classifier')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of questions')

    args = parser.parse_args()

    if args.test_classifier:
        test_classifier_accuracy()

    if args.analyze:
        analyze_validation_set(limit=args.limit)

    if not args.test_classifier and not args.analyze:
        # Default: run both
        test_classifier_accuracy()
        analyze_validation_set(limit=args.limit)


if __name__ == "__main__":
    main()
