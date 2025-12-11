"""Quick fix script for invalid answers"""
import csv

input_file = r"d:\VNPT AI\VNPt\output\submission.csv"

rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['answer'] not in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            print(f"Fixing {row['qid']}: {row['answer']} → G")
            row['answer'] = 'G'
        rows.append(row)

with open(input_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✓ Fixed!")