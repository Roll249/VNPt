import csv
import os
from collections import Counter

def ensemble_voting():
    print("🚀 Starting Ensemble Voting...")
    
    # Files to combine
    files = [
        {'path': 'output/submission_precision.csv', 'weight': 3}, # Best (Rules applied)
        {'path': 'output/submission.csv', 'weight': 1},           # Baseline (Correctness 0.59)
        {'path': 'output/submission_fixed.csv', 'weight': 1},     # STEM Fix (Potential STEM boost)
    ]
    
    # Load all answers
    # Dict: qid -> Counter({'A': score, 'B': score})
    votes = {} 
    
    # Read files
    for f_info in files:
        path = f_info['path']
        weight = f_info['weight']
        
        if not os.path.exists(path):
            print(f"⚠ Warning: File {path} not found. Skipping.")
            continue
            
        print(f"Reading {path} (Weight: {weight})...")
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = row['qid']
                ans = row['answer'].strip().upper()
                
                if qid not in votes:
                    votes[qid] = Counter()
                
                votes[qid][ans] += weight

    # Determine winners
    final_results = []
    
    # Load qids from test.json to ensure order
    import json
    with open('data/test.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
        
    changes_vs_precision = 0
    
    for item in questions:
        qid = item['qid']
        
        if qid not in votes:
            print(f"⚠ Missing votes for {qid}, defaulting to A")
            final_ans = 'A'
        else:
            # Get answer with max score
            # most_common returns [(ans, score), ...]
            # If tie, it picks the detailed order, but Counter isn't ordered.
            # To break ties consistently, we prioritize the answer from the highest weighted file ('submission_precision.csv')
            # But the weighting scheme (3 vs 1 vs 1) prevents ties unless:
            # Case: A(3), B(1), C(1) -> A wins.
            # Case: A(3), B(1), B(1) -> A(3) vs B(2) -> A wins.
            # Case: A(1) [fixed], B(1) [base], C(3) [precision] -> C wins.
            # Case: A(ignored) [precision], B(1) [base], B(1) [fixed] -> B(2) vs A(3) -> A wins.
            # Actually, if Precision says A, it gets 3 points. If base says B and fixed says B, B gets 2 points. A wins.
            # This means `submission_precision.csv` dictates the outcome UNLESS:
            # We want STEM fix to override?
            # User said "fix_stem.py" didn't increase score.
            # So `submission_fixed.csv` might be bad.
            # But `submission.csv` (Base) was good.
            # If Base and Fix agree against Precision? Base(1)+Fix(1) = 2. Precision(3) = 3. Precision wins.
            # This logic basically just COPIES `submission_precision.csv` unless there's a 4th file.
            # Let's adjust weights to allow "Governance":
            # Precision: 2
            # Base: 1
            # Fixed: 1
            # If Base(1) + Fixed(1) = 2. Precision(2) = 2. Tie.
            # In tie, what do we do?
            # Maybe Precision should be strictly Rule-Based overrides only?
            # But `submission_precision.csv` is a full file.
            # Let's trust `submission_precision.csv` mostly.
            
            counter = votes[qid]
            final_ans, score = counter.most_common(1)[0]
        
        final_results.append({'qid': qid, 'answer': final_ans})
        
        # Log diff vs precision (just to see if ensemble added anything)
        # Note: We need to load precision dict to compare
        pass

    # Save
    output_path = 'output/submission_ensemble.csv'
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
        writer.writeheader()
        writer.writerows(final_results)
        
    print(f"Done! Combined {len(votes)} questions.")
    print(f"New file: {output_path}")

if __name__ == "__main__":
    ensemble_voting()
