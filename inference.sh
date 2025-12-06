#!/bin/bash
# Inference script - runs the prediction pipeline

echo "Starting VNPT AI Hackathon inference..."
echo "================================================"

# Run prediction
python3 predict.py

echo "================================================"
echo "Inference complete!"

# Check if output was created
if [ -f "/code/output/submission.csv" ]; then
    echo "✓ Output file created: /code/output/submission.csv"
    wc -l /code/output/submission.csv
else
    echo "✗ Error: Output file not created"
    exit 1
fi
