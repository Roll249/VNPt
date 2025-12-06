# HƯỚNG DẪN TEST BASELINE PIPELINE

## 🎯 MỤC TIÊU

Test baseline pipeline để:
1. Verify code chạy được
2. Phân tích phân phối câu hỏi
3. Test classifier accuracy
4. Đo baseline accuracy (nếu có API quota)

---

## 📋 BƯỚC 1: PHÂN TÍCH VALIDATION SET (KHÔNG CẦN API)

### Test Classifier:
```bash
cd D:\Khang\Thi\VNPT
python test_baseline.py --test-classifier
```

**Expected Output**:
```
==============================================================
TESTING CLASSIFIER
==============================================================

✓ Expected: reading
  Predicted: reading (conf: 1.00)
  Q: Đoạn thông tin:...

✓ Expected: math
  Predicted: math (conf: 0.90)
  Q: Tính diện tích hình chữ nhật...

--------------------------------------------------------------
Classifier Accuracy: 7/7 (100.0%)
==============================================================
```

### Phân tích Validation Set:
```bash
python test_baseline.py --analyze
```

**Expected Output**:
```
==============================================================
VALIDATION SET ANALYSIS
==============================================================

Total questions: 100

--------------------------------------------------------------
CATEGORY DISTRIBUTION:
--------------------------------------------------------------
reading                    25 ( 25.0%)
history                    22 ( 22.0%)
culture                    18 ( 18.0%)
geography                  15 ( 15.0%)
math                       12 ( 12.0%)
politics                    6 (  6.0%)
refusal                     2 (  2.0%)
```

### Phân tích giới hạn (nhanh hơn):
```bash
python test_baseline.py --analyze --limit 20
```

---

## 📋 BƯỚC 2: TEST VỚI API (SAMPLE)

### Test trên 5 câu đầu tiên:

1. **Tạo test file nhỏ**:
```bash
# Windows PowerShell
Get-Content data\val.json | ConvertFrom-Json | Select-Object -First 5 | ConvertTo-Json > data\val_small.json
```

Hoặc thủ công: Copy 5 câu đầu từ `data/val.json` vào `data/val_small.json`

2. **Update predict.py tạm thời**:
```python
# Line ~190 in predict.py, change:
input_path = "data/val_small.json"  # Test file
output_path = "submission_test.csv"
```

3. **Chạy**:
```bash
python predict.py
```

4. **Kiểm tra output**:
```bash
type submission_test.csv

# Should show:
# qid,answer
# val_0001,B
# val_0002,A
# ...
```

5. **Đánh giá**:
```bash
# Copy val_small.json answers to compare manually
```

---

## 📋 BƯỚC 3: TEST FULL VALIDATION SET (100 QUESTIONS)

⚠️ **WARNING**: Sẽ dùng ~100-150 API calls. Chỉ chạy khi sẵn sàng.

### Prepare:
```bash
# Make sure predict.py reads data/val.json
# Line ~190:
input_path = "data/val.json"
output_path = "submission.csv"
```

### Run:
```bash
python predict.py
```

**Expected time**: ~5-10 phút (tùy API latency)

### Evaluate:
```bash
python evaluation/evaluate.py
```

**Expected Output**:
```
==============================================================
EVALUATION RESULTS
==============================================================

Overall Accuracy: 68.50%
Correct: 68/100

--------------------------------------------------------------
Per-Category Breakdown:
--------------------------------------------------------------
Category             Accuracy     Correct/Total
--------------------------------------------------------------
reading              🟢  82.00%     20/25
geography            🟡  73.33%     11/15
culture              🟡  72.22%     13/18
math                 🔴  58.33%      7/12
history              🔴  59.09%     13/22
politics             🟡  66.67%      4/6
refusal              🟢 100.00%      2/2
==============================================================
```

---

## 📋 BƯỚC 4: ERROR ANALYSIS

Sau khi chạy evaluation, check file errors:
```bash
type evaluation\errors.json
```

Example error:
```json
{
  "qid": "val_0042",
  "question": "Nhà Lý được thành lập...",
  "true_answer": "C",
  "pred_answer": "A",
  "category": "history",
  "confidence": 0.75
}
```

### Identify patterns:
- Loại câu nào sai nhiều nhất?
- Category nào accuracy thấp nhất?
- Có pattern chung không? (e.g., dates, names, etc.)

---

## 📋 BƯỚC 5: DECISION POINT

### If Baseline Accuracy > 65%:
✅ **GOOD!** Có thể:
- Option A: Optimize prompts để lên 70%+
- Option B: Add RAG cho categories yếu nhất
- Option C: Submit baseline, iterate sau

### If Baseline Accuracy < 65%:
⚠️ **NEED IMPROVEMENT**:
- Priority 1: Add RAG for domain questions (history, culture, geography, politics)
- Priority 2: Improve prompts
- Priority 3: Use more Large model

---

## 🛠️ TROUBLESHOOTING

### "ModuleNotFoundError: No module named 'modules'"
```bash
# Make sure you're in project root:
cd D:\Khang\Thi\VNPT
python predict.py
```

### "FileNotFoundError: api-keys.json"
```bash
# Make sure api-keys.json exists in project root
dir api-keys.json
```

### "API Error: 401 Unauthorized"
```bash
# Check API keys in api-keys.json
# Verify authorization token is valid
```

### "API Error: 429 Too Many Requests"
```bash
# Hit API quota limit
# Wait for reset or reduce test size
```

### Low accuracy on specific category:
```
# Example: History accuracy is 45%
→ History needs RAG!
→ Build history vector DB next
```

---

## 📊 EXPECTED RESULTS SUMMARY

### Classifier Test:
- ✅ Should be 100% or close (it's rule-based)

### Validation Analysis:
- ✅ Should show distribution matching our taxonomy
- Expected: Reading ~20-25%, Domain questions ~60-70%, Math ~10-15%

### Baseline Accuracy (no RAG):
- Reading: **75-85%** (context in question)
- Math: **60-70%** (LLM Large reasoning)
- Refusal: **95-100%** (rule-based)
- History: **50-60%** (LLM knowledge only)
- Culture: **55-65%** (LLM knowledge only)
- Geography: **60-70%** (some factual)
- Politics: **50-60%** (LLM knowledge only)

**Overall: 65-70%**

---

## 🎯 NEXT STEPS BASED ON RESULTS

### Scenario 1: Accuracy 70%+
```
✅ Baseline is good!
Next: Optimize prompts → aim for 75%+
Then: Docker build → Submit
```

### Scenario 2: Accuracy 65-70%
```
🟡 Baseline is OK
Next: Add RAG for weakest category
Example: If History is 45%, build history_db
Re-test → should jump to 75%+
```

### Scenario 3: Accuracy < 65%
```
🔴 Baseline needs work
Next: Full RAG implementation
Build all 4 vector DBs
Expected jump: +8-10% → 73-78%
```

---

## 📝 CHECKLIST

Before moving to next step:

- [ ] Classifier test passed (100%)
- [ ] Validation analysis shows expected distribution
- [ ] Baseline accuracy measured (even if low)
- [ ] Error analysis completed
- [ ] Weak categories identified
- [ ] Decision made: RAG needed or not?

---

**Current Status**: Ready to test!
**Time needed**: 10-15 minutes (analysis) + 10 minutes (full test with API)
**API quota used**: ~100-150 calls for full validation test

---

Last updated: 06/12/2025
