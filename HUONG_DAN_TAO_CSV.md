# HƯỚNG DẪN TẠO FILE CSV ĐỂ NỘP

## 📋 File CSV Là Gì?

File CSV (submission.csv) là kết quả dự đoán của hệ thống bạn trên test set.

**Format**:
```csv
qid,answer
test_0001,A
test_0002,B
test_0003,C
...
test_0400,D
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

**File CSV KHÔNG phải file nộp chính!**

Theo quy định cuộc thi, bạn phải nộp **DOCKER IMAGE**, không phải file CSV.

Docker image sẽ:
1. Nhận input: `/code/data/private_test.json` (400 câu của BTC)
2. Chạy code của bạn
3. Tạo output: `/code/output/submission.csv`

---

## 🎯 CÁC TRƯỜNG HỢP

### ✅ Trường hợp 1: NỘP DOCKER IMAGE (Đúng theo quy định)

**Làm gì:** Nộp Docker image `vnpt-qa-system`

**Cách nộp:**
```bash
# Push lên Docker Hub
docker push YOUR_USERNAME/vnpt-qa-system:latest

# Hoặc save file
docker save vnpt-qa-system > vnpt-qa-system.tar
```

**File CSV sẽ được tạo tự động** khi BTC chạy Docker của bạn!

---

### 📝 Trường hợp 2: Muốn TEST LOCAL (Tạo CSV để xem trước)

**Bước 1: Chuẩn bị test data**
```bash
mkdir test_data test_output
copy data\val_10.json test_data\private_test.json
```

**Bước 2: Chạy Docker**
```bash
docker run --rm ^
  -v "%cd%\test_data:/code/data" ^
  -v "%cd%\test_output:/code/output" ^
  vnpt-qa-system
```

**Bước 3: Lấy file CSV**
```bash
# File ở đây:
test_output\submission.csv
```

---

### 🔧 Trường hợp 3: Tạo CSV từ code Python (Không dùng Docker)

**Chạy trực tiếp:**
```bash
cd D:\Khang\Thi\VNPT
python predict.py
```

**Output:** `submission.csv` (trong thư mục hiện tại)

**Lưu ý:** Cần có API quota (hiện đã hết quota hôm nay)

---

## 📊 FILE CSV MẪU ĐÃ CÓ

### submission_10.csv (từ test 10 câu)

Location: `D:\Khang\Thi\VNPT\submission_10.csv`

```csv
qid,answer
val_0001,B
val_0002,C
val_0003,B
val_0004,C
val_0005,A
val_0006,C
val_0007,A
val_0008,B
val_0009,B
val_0010,A
```

**Accuracy:** 60% (6/10 correct)

---

## 🚀 CÁCH TẠO FILE CSV THỰC (400 CÂU)

### Option 1: Đợi API quota reset (1 tiếng)

```bash
# Sau 1 tiếng (từ lần test cuối)
cd D:\Khang\Thi\VNPT
python predict.py
```

Sẽ tạo `submission.csv` với 93 câu (hoặc 400 nếu có file test.json)

### Option 2: Dùng Docker (khi có test set thực)

```bash
# BTC sẽ mount private_test.json vào /code/data
# Docker sẽ tự động tạo submission.csv
```

### Option 3: Tạo template (cho demo)

Tôi có thể tạo file CSV mẫu với 400 dòng (answer mặc định 'A')

**Lưu ý:** File này CHỈ để demo format, không phải kết quả thực!

---

## ❓ BẠN MUỐN GÌ?

### A. File CSV test (10 câu đã chạy)
→ File `submission_10.csv` đã có sẵn

### B. Chạy lại để tạo CSV mới
→ Cần đợi API quota reset (1 tiếng nữa)

### C. Template CSV 400 câu (demo)
→ Tôi tạo ngay (tất cả answer = 'A')

### D. Hướng dẫn nộp Docker
→ Đọc file `README_NOP_BAI.txt`

---

## ✅ KHUYẾN NGHỊ

**NỘP DOCKER IMAGE, KHÔNG NỘP CSV!**

Lý do:
- Quy định cuộc thi: Nộp Docker image
- File CSV sẽ tự động được tạo khi BTC chạy Docker
- Docker của bạn đã sẵn sàng: `vnpt-qa-system:latest`

**Chỉ cần:**
```bash
docker push YOUR_USERNAME/vnpt-qa-system:latest
```

---

Bạn muốn tôi làm gì tiếp theo?
- Tạo template CSV 400 câu?
- Hướng dẫn test Docker local?
- Hay gì khác?
