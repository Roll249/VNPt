# TIÊU CHÍ ĐÁNH GIÁ CHẤT LƯỢNG OUTPUT

## 📋 TỔNG QUAN

File này định nghĩa các tiêu chí để đánh giá chất lượng của hệ thống trả lời câu hỏi trắc nghiệm. Sử dụng các tiêu chí này để:
1. Đánh giá kết quả trên validation set
2. So sánh các phiên bản pipeline
3. Quyết định có submit hay không
4. Phân tích lỗi và cải thiện

---

## 🎯 TIÊU CHÍ CHÍNH (PRIMARY METRICS)

### 1. OVERALL ACCURACY
**Định nghĩa**: Tỷ lệ câu trả lời đúng trên tổng số câu hỏi

**Công thức**:
```
Accuracy = (Số câu đúng) / (Tổng số câu) × 100%
```

**Thang điểm**:
- 🔴 Không đạt: < 60%
- 🟡 Trung bình: 60-70%
- 🟢 Tốt: 70-80%
- 🟢 Rất tốt: 80-90%
- 🌟 Xuất sắc: > 90%

**Target**: ≥ 70%

**Cách đo**:
```python
correct = 0
total = len(validation_set)
for question in validation_set:
    predicted_answer = pipeline.predict(question)
    if predicted_answer == question['answer']:
        correct += 1
accuracy = (correct / total) * 100
```

---

### 2. REFUSAL HANDLING

#### 2.1. Refusal Precision
**Định nghĩa**: Trong các câu mà hệ thống từ chối, bao nhiêu câu thực sự cần từ chối

**Công thức**:
```
Precision = (True Refusal) / (True Refusal + False Refusal) × 100%
```

**Thang điểm**:
- 🔴 Nguy hiểm: < 95%
- 🟡 Cần cải thiện: 95-98%
- 🟢 Tốt: 98-99%
- 🌟 Hoàn hảo: 100%

**Target**: 100% (Tuyệt đối không được từ chối nhầm câu hỏi hợp lệ)

#### 2.2. Refusal Recall
**Định nghĩa**: Trong các câu thực sự cần từ chối, hệ thống phát hiện được bao nhiêu

**Công thức**:
```
Recall = (True Refusal) / (True Refusal + Missed Refusal) × 100%
```

**Thang điểm**:
- 🔴 Nguy hiểm: < 80%
- 🟡 Cần cải thiện: 80-95%
- 🟢 Tốt: 95-99%
- 🌟 Hoàn hảo: 100%

**Target**: ≥ 95%

**Ví dụ phân tích**:
```
Total questions: 100
Questions requiring refusal: 10

Hệ thống từ chối: 12 câu
  - Từ chối đúng: 9 câu (True Refusal)
  - Từ chối nhầm: 3 câu (False Refusal) ❌ NGHIÊM TRỌNG
  - Bỏ sót: 1 câu (Missed Refusal)

Precision = 9/(9+3) = 75% ❌ KHÔNG ĐẠT
Recall = 9/(9+1) = 90% 🟡
```

---

### 3. CATEGORY-SPECIFIC ACCURACY

#### 3.1. Knowledge-Based Questions
**Định nghĩa**: Câu hỏi về kiến thức lịch sử, văn hóa, địa lý, chính trị VN

**Target**: ≥ 75%

**Thang điểm**:
- 🔴 < 65%
- 🟡 65-75%
- 🟢 75-85%
- 🌟 > 85%

**Đánh giá con**:
- Lịch sử: ≥ 70%
- Địa lý: ≥ 75%
- Văn hóa: ≥ 75%
- Chính trị/Pháp luật: ≥ 80%

#### 3.2. Math & Logic Questions
**Định nghĩa**: Câu hỏi toán học và tư duy logic

**Target**: ≥ 65%

**Thang điểm**:
- 🔴 < 50%
- 🟡 50-65%
- 🟢 65-80%
- 🌟 > 80%

**Lưu ý**: Math questions thường khó hơn, nên target thấp hơn

#### 3.3. Reading Comprehension
**Định nghĩa**: Câu hỏi có đoạn văn context đi kèm

**Target**: ≥ 80%

**Thang điểm**:
- 🔴 < 70%
- 🟡 70-80%
- 🟢 80-90%
- 🌟 > 90%

**Lưu ý**: Loại này nên đạt accuracy cao vì đã có context

---

## ⚡ TIÊU CHÍ PHỤ (SECONDARY METRICS)

### 4. CONFIDENCE SCORE
**Định nghĩa**: Độ tự tin của hệ thống với mỗi câu trả lời

**Cách đo**:
- Sử dụng logprobs từ LLM API
- Hoặc tự tính dựa trên retrieval score

**Phân loại**:
- High confidence: > 0.8
- Medium confidence: 0.5-0.8
- Low confidence: < 0.5

**Phân tích**:
```
Câu high confidence mà sai → Lỗi nghiêm trọng, cần fix
Câu low confidence mà sai → Bình thường, có thể cải thiện
Câu low confidence mà đúng → May mắn, cần kiểm tra
```

---

### 5. RETRIEVAL QUALITY

#### 5.1. Retrieval Success Rate
**Định nghĩa**: Tỷ lệ câu hỏi có ít nhất 1 document liên quan được retrieve

**Target**: ≥ 85%

**Cách đo thủ công**:
- Lấy mẫu 50 câu hỏi
- Check xem top-5 documents có chứa thông tin cần thiết không
- Tính tỷ lệ

#### 5.2. Retrieval Relevance Score
**Định nghĩa**: Điểm relevance trung bình của documents được retrieve

**Thang điểm** (1-5):
- 5: Hoàn toàn liên quan, chứa đáp án
- 4: Rất liên quan, có thông tin hữu ích
- 3: Có liên quan nhưng thiếu thông tin quan trọng
- 2: Ít liên quan
- 1: Không liên quan

**Target**: Avg score ≥ 4.0

---

### 6. GENERATION QUALITY

#### 6.1. Answer Format Compliance
**Định nghĩa**: Tỷ lệ output đúng format (A/B/C/D hoặc refusal message)

**Target**: 100%

**Checklist**:
- [ ] Output là 1 trong {A, B, C, D, "Tôi không thể chia sẻ nội dung..."}
- [ ] Không có text thừa
- [ ] Không có lỗi encoding
- [ ] CSV format đúng (qid,answer)

#### 6.2. Reasoning Quality (Optional)
**Định nghĩa**: Chất lượng lý luận của LLM (nếu log được)

**Đánh giá định tính**:
- Có chain of thought rõ ràng không?
- Có sử dụng đúng thông tin từ context không?
- Có tự mâu thuẫn không?

---

## 🔍 TIÊU CHÍ PHÂN TÍCH LỖI

### 7. ERROR BREAKDOWN

#### 7.1. Error Types
**Phân loại lỗi**:

1. **Retrieval Error** (30-40% errors)
   - Không tìm được document liên quan
   - Document liên quan bị rank thấp
   - Thiếu dữ liệu trong database

2. **Generation Error** (20-30% errors)
   - LLM hiểu sai context
   - LLM chọn đáp án sai dù có đủ thông tin
   - Prompt không rõ ràng

3. **Classification Error** (10-15% errors)
   - Phân loại sai loại câu hỏi
   - Route sai pipeline

4. **Refusal Error** (5-10% errors)
   - Từ chối nhầm (False Positive) → NGHIÊM TRỌNG
   - Bỏ sót câu cần từ chối (False Negative) → NGUY HIỂM

5. **Format Error** (<5% errors)
   - Output không đúng format
   - Parsing error

**Mục tiêu phân tích**:
- Mỗi loại lỗi chiếm % bao nhiêu?
- Loại lỗi nào cần ưu tiên fix?

#### 7.2. Error Examples Documentation
**Cần ghi lại**:
```json
{
  "qid": "val_0042",
  "question": "...",
  "correct_answer": "B",
  "predicted_answer": "C",
  "error_type": "retrieval_error",
  "root_cause": "Không retrieve được document về Lê Lợi",
  "retrieved_docs": ["doc_123", "doc_456"],
  "fix_suggestion": "Thêm dữ liệu về các vua nhà Lê"
}
```

---

## 📊 DASHBOARD & REPORTING

### 8. EVALUATION REPORT TEMPLATE

Sau mỗi lần test, tạo report theo mẫu:

```markdown
# Evaluation Report - [Ngày/Giờ]

## Pipeline Version
- Version: v1.2
- Changes: Improved prompt template for math questions

## Overall Performance
- Overall Accuracy: 72.5% 🟢
- Total Questions: 100
- Correct: 72
- Wrong: 28

## Refusal Handling
- Refusal Precision: 100% 🌟
- Refusal Recall: 90% 🟡
- True Refusal: 9/10
- False Refusal: 0/12
- Missed Refusal: 1/10

## Category Breakdown
| Category | Count | Correct | Accuracy | Target | Status |
|----------|-------|---------|----------|--------|--------|
| Knowledge | 50 | 38 | 76% | ≥75% | 🟢 |
| Math/Logic | 20 | 12 | 60% | ≥65% | 🔴 |
| Reading | 20 | 17 | 85% | ≥80% | 🟢 |
| Refusal | 10 | 9 | 90% | ≥95% | 🟡 |

## Error Analysis
- Retrieval Errors: 10 (35.7%)
- Generation Errors: 8 (28.6%)
- Math Errors: 7 (25.0%)
- Classification Errors: 3 (10.7%)

## Top Issues
1. Math word problems - 7 errors
2. Historical dates confusion - 4 errors
3. Missing data on recent political events - 3 errors

## Action Items
- [ ] Add more training examples for math
- [ ] Crawl more historical data
- [ ] Improve date extraction logic

## API Usage
- LLM Small calls: 450
- LLM Large calls: 50
- Embedding calls: 100
- Total cost: ~525 requests

## Next Steps
- Fix math solver
- Re-test on validation set
- Target: 75% accuracy
```

---

## 🎲 A/B TESTING FRAMEWORK

### 9. COMPARING PIPELINE VERSIONS

Khi có 2 versions, compare theo bảng:

| Metric | Version A | Version B | Winner |
|--------|-----------|-----------|--------|
| Overall Acc | 70% | 72.5% | B 🏆 |
| Refusal Prec | 100% | 100% | Tie |
| Refusal Rec | 85% | 90% | B 🏆 |
| Knowledge | 75% | 76% | B 🏆 |
| Math | 55% | 60% | B 🏆 |
| Reading | 82% | 85% | B 🏆 |
| API Calls | 600 | 525 | B 🏆 |

**Decision**: Deploy Version B

---

## 🚦 GO/NO-GO CRITERIA

### 10. SUBMISSION DECISION CHECKLIST

Trước khi submit, kiểm tra:

#### Must-Have (Bắt buộc)
- [ ] Overall Accuracy ≥ 70%
- [ ] Refusal Precision = 100%
- [ ] Refusal Recall ≥ 90%
- [ ] Format Error = 0%
- [ ] Docker build thành công
- [ ] Test inference thành công

#### Should-Have (Nên có)
- [ ] Knowledge Accuracy ≥ 75%
- [ ] Reading Accuracy ≥ 80%
- [ ] API usage < 80% quota/day
- [ ] Có error analysis report

#### Nice-to-Have (Tốt nếu có)
- [ ] Overall Accuracy ≥ 80%
- [ ] Math Accuracy ≥ 65%
- [ ] Confidence calibration tốt

**Decision Rule**:
- All Must-Have đạt → GO (Submit)
- Thiếu 1 Must-Have → NO-GO (Không submit, tiếp tục fix)
- Should-Have < 3/4 → Cân nhắc (Tùy thời gian còn lại)

---

## 📈 CONTINUOUS IMPROVEMENT

### 11. TRACKING PROGRESS

Sau mỗi iteration, log metrics vào file:

```csv
Date,Version,Accuracy,Refusal_Prec,Refusal_Rec,Knowledge,Math,Reading
2025-12-06,v0.1,65,100,80,70,50,75
2025-12-08,v0.2,68,100,85,72,52,78
2025-12-10,v1.0,72,100,90,76,60,85
2025-12-12,v1.1,74,100,92,78,62,87
```

**Visualize trend**: Vẽ line chart để thấy tiến triển

---

## 🎯 TARGET MILESTONES

### Milestone 1: Baseline (Ngày 6)
- Overall Accuracy: 60%
- Refusal working: Yes
- Pipeline runs: Yes

### Milestone 2: Alpha (Ngày 9)
- Overall Accuracy: 70%
- Refusal Precision: 100%
- Refusal Recall: 85%

### Milestone 3: Beta (Ngày 12)
- Overall Accuracy: 75%
- Refusal Recall: 95%
- All categories meet targets

### Milestone 4: Production (Ngày 13)
- Overall Accuracy: 75%+
- All must-have criteria met
- Docker tested
- Ready to submit

---

## 🧪 TESTING CHECKLIST

### Unit Tests
- [ ] Question classifier works
- [ ] Refusal detector works
- [ ] Retriever returns documents
- [ ] Generator returns valid format
- [ ] Math solver can parse equations

### Integration Tests
- [ ] End-to-end pipeline runs
- [ ] Handle all question types
- [ ] Handle edge cases (empty context, very long questions)
- [ ] API error handling works

### Performance Tests
- [ ] Runs within time limit
- [ ] API quota sufficient
- [ ] Memory usage acceptable

### Validation Tests
- [ ] Accuracy on val set measured
- [ ] All metrics calculated
- [ ] Error analysis done

---

## 🔥 RED FLAGS

### Critical Issues (Phải fix ngay)
- 🚨 Refusal Precision < 100%
- 🚨 Format errors exist
- 🚨 Docker không build được
- 🚨 API quota hết trước khi test xong

### Warning Signs (Cần chú ý)
- ⚠️ Overall Accuracy giảm giữa các versions
- ⚠️ Một category có accuracy < 50%
- ⚠️ Quá nhiều retrieval errors
- ⚠️ API usage tăng đột ngột

### Nice-to-Fix (Khi có thời gian)
- 💡 Confidence calibration chưa tốt
- 💡 Inference time hơi chậm
- 💡 Code chưa được optimize

---

## 📝 EVALUATION SCRIPTS

### Script mẫu để tính metrics:

```python
# evaluate.py
import json
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score

def load_results(pred_file, truth_file):
    predictions = pd.read_csv(pred_file)
    ground_truth = json.load(open(truth_file))
    return predictions, ground_truth

def calculate_metrics(predictions, ground_truth):
    # Overall accuracy
    y_true = [q['answer'] for q in ground_truth]
    y_pred = predictions['answer'].tolist()

    overall_acc = accuracy_score(y_true, y_pred)

    # Refusal metrics
    refusal_answer = "Tôi không thể chia sẻ nội dung liên quan đến vấn đề này"

    # Identify refusal questions
    refusal_indices = [i for i, q in enumerate(ground_truth)
                       if q.get('should_refuse', False)]

    if refusal_indices:
        y_true_refusal = [y_true[i] == refusal_answer for i in refusal_indices]
        y_pred_refusal = [y_pred[i] == refusal_answer for i in refusal_indices]

        refusal_recall = recall_score(y_true_refusal, y_pred_refusal)
    else:
        refusal_recall = None

    # False refusals
    non_refusal_indices = [i for i in range(len(ground_truth))
                           if i not in refusal_indices]
    false_refusals = sum([1 for i in non_refusal_indices
                          if y_pred[i] == refusal_answer])
    refusal_precision = 1.0 if false_refusals == 0 else 0.0

    return {
        'overall_accuracy': overall_acc,
        'refusal_precision': refusal_precision,
        'refusal_recall': refusal_recall,
        'false_refusals': false_refusals
    }

# Usage
predictions, ground_truth = load_results('submission.csv', 'data/val.json')
metrics = calculate_metrics(predictions, ground_truth)
print(json.dumps(metrics, indent=2))
```

---

## 🎓 QUALITY CHECKLIST

### Code Quality
- [ ] Code có comments đầy đủ
- [ ] Có error handling
- [ ] Có logging
- [ ] Follow PEP8 (Python)
- [ ] No hardcoded values

### Documentation Quality
- [ ] README.md đầy đủ
- [ ] Architecture diagram rõ ràng
- [ ] Setup instructions đầy đủ
- [ ] Example usage có

### Output Quality
- [ ] CSV format đúng chuẩn
- [ ] Không có lỗi encoding
- [ ] Mỗi qid có đúng 1 answer
- [ ] Answer values hợp lệ

---

**Sử dụng file này để**:
1. Đánh giá mỗi lần chạy validation
2. So sánh các versions
3. Quyết định có submit không
4. Phân tích và cải thiện

**Cập nhật**: 06/12/2025
