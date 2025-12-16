import json
import os
import sys
import pandas as pd
from typing import List

# Setup path to import predict.py
# Assuming script is in d:/VNPT AI/VNPt/scripts/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import SimplePipeline
try:
    from predict import SimplePipeline
except ImportError:
    print("Error: Could not import predict.py. Make sure you run this from the project root.")
    sys.exit(1)

def main():
    val_path = os.path.join(project_root, "data", "val.json")
    
    if not os.path.exists(val_path):
        print(f"Error: Validation file not found at {val_path}")
        return

    # Load data
    print(f"Loading validation data from: {val_path}")
    with open(val_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} validation questions.")

    # Init Pipeline
    print("Initializing Pipeline...")
    pipeline = SimplePipeline()
    
    results = []
    correct_count = 0
    total_count = 0
    
    print("\n" + "="*50)
    print("STARTING VALIDATION RUN")
    print("="*50 + "\n")

    for i, item in enumerate(data):
        qid = item.get('qid', f'val_{i}')
        question = item['question']
        choices = item['choices']
        ground_truth = item.get('answer') # Expecting "A", "B", "C", "D"
        
        if not ground_truth:
            print(f"Skipping {qid}: No ground truth answer.")
            continue

        print(f"[{i+1}/{len(data)}] Processing {qid}...")
        
        # Predict
        try:
            # predict_single(self, question: str, choices: List[str], qid: str) -> str
            pred = pipeline.predict_single(question, choices, qid)
        except Exception as e:
            print(f"Error on {qid}: {e}")
            pred = "A" # Fallback
            
        # Check correctness
        # Ground truth might be "A" or "A. Content". Usually "A".
        # Ensure clean comparison
        clean_truth = ground_truth.strip()[0].upper()
        clean_pred = pred.strip()[0].upper()
        
        is_correct = (clean_pred == clean_truth)
        if is_correct:
            correct_count += 1
            print(f"  ✅ CORRECT ({clean_pred})")
        else:
            print(f"  ❌ WRONG (Pred: {clean_pred} | True: {clean_truth})")
            
        total_count += 1
        
        results.append({
            "qid": qid,
            "question": question[:100],
            "prediction": clean_pred,
            "ground_truth": clean_truth,
            "is_correct": is_correct
        })
        
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    
    accuracy = correct_count / total_count if total_count > 0 else 0
    print(f"Total Questions: {total_count}")
    print(f"Correct:         {correct_count}")
    print(f"Wrong:           {total_count - correct_count}")
    print(f"ACCURACY:        {accuracy:.2%}")
    print("="*50)
    
    # Save CSV
    output_path = os.path.join(project_root, "output", "validation_results.csv")
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Detailed results saved to: {output_path}")

if __name__ == "__main__":
    main()
