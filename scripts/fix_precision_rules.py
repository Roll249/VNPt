import json
import csv
import os

def fix_precision_rules():
    print("🚀 Starting Precision Rule-Based Fix...")
    
    # 1. Load data
    # We start from the 'optimized' one if we want to keep some goods, 
    # OR start from 'submission.csv' (cleanest). 
    # Given the optimization output was bad (0.55), let's start from 'submission.csv' (0.59) if possible, 
    # OR just apply this rule on top of the 'optimization' to see if it fixes the Precision component.
    # User said "nộp rồi nhưng bị giảm điểm", implying the optimization file was bad.
    # Best strategy: Take submission.csv (The 0.59 one) and apply ONLY this rule.
    
    submission_path = 'output/submission.csv' 
    output_path = 'output/submission_precision.csv'

    current_answers = {}
    if os.path.exists(submission_path):
        with open(submission_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                current_answers[row['qid']] = row['answer']
    
    with open('data/test.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # 2. Define Refusal Patterns (in choices)
    REFUSAL_PHRASES = [
        "không thể chia sẻ",
        "tôi không thể",
        "không thể cung cấp",
        "vi phạm pháp luật",
        "trái pháp luật",
        "không hỗ trợ",
        "từ chối trả lời",
        "vấn đề nhạy cảm",
        "không phù hợp",
        "bất hợp pháp",
        "phi pháp",
        "gian lận",
        "lừa đảo"
    ]

    updated_count = 0

    for item in questions:
        qid = item['qid']
        choices = item['choices']
        
        # Check choices for refusal patterns
        refusal_idx = -1
        
        for idx, choice in enumerate(choices):
            choice_lower = choice.lower()
            for phrase in REFUSAL_PHRASES:
                if phrase in choice_lower:
                    refusal_idx = idx
                    break
            if refusal_idx != -1:
                break
        
        if refusal_idx != -1:
            # Construct answer letter
            refusal_ans = chr(65 + refusal_idx)
            
            # Check if we need to update
            old_ans = current_answers.get(qid, "")
            if old_ans != refusal_ans:
                print(f"[{qid}] Found Refusal Choice: '{choices[refusal_idx][:50]}...'")
                print(f"   -> Updating: {old_ans} -> {refusal_ans}")
                current_answers[qid] = refusal_ans
                updated_count += 1

    # 3. Save
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
        writer.writeheader()
        for item in questions:
            qid = item['qid']
            ans = current_answers.get(qid, 'A')
            writer.writerow({'qid': qid, 'answer': ans})

    print(f"Done! Updated {updated_count} answers based on Strict Refusal Rules.")
    print(f"New file: {output_path}")

if __name__ == "__main__":
    fix_precision_rules()
