import json
import csv
import os

def finalize_submission():
    input_path = "data/test.json"
    output_path = "output/submission.csv"

    # Read questions
    with open(input_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Read existing submission
    existing_answers = {}
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_answers[row['qid']] = row['answer']
    
    print(f"Total questions: {len(questions)}")
    print(f"Answered: {len(existing_answers)}")
    
    # identify missing
    missing_count = 0
    with open(output_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
        # If file was empty (unlikely), write header
        if os.stat(output_path).st_size == 0:
            writer.writeheader()
            
        for q in questions:
            qid = q['qid']
            if qid not in existing_answers:
                # Default to A for missing
                writer.writerow({'qid': qid, 'answer': 'A'})
                missing_count += 1
                
    print(f"Filled {missing_count} missing questions with default 'A'.")
    print("Submission finalized!")

if __name__ == "__main__":
    finalize_submission()
