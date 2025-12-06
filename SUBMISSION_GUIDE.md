# 📦 HƯỚNG DẪN NỘP BÀI - VNPT AI HACKATHON

## 🎯 Tổng Quan Hệ Thống

**Accuracy baseline**: 60% (tested on 10 questions)
**Docker size**: ~2.6GB
**Performance**: Optimized (fast, low memory)

---

## 📁 CÁC FILE CẦN NỘP

### 1. Dockerfile
**Location**: `D:\Khang\Thi\VNPT\Dockerfile`

```dockerfile
FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY config/ ./config/
COPY modules/ ./modules/
COPY predict.py .
COPY api-keys.json .

# Create output directory
RUN mkdir -p /code/output

# Entry point
CMD ["python3", "predict.py"]
```

### 2. requirements.txt
**Location**: `D:\Khang\Thi\VNPT\requirements.txt`

```txt
requests==2.31.0
numpy==1.24.3
faiss-cpu==1.7.4
pandas==2.0.3
```

### 3. Source Code Structure
```
D:\Khang\Thi\VNPT\
├── Dockerfile              ← File Docker chính
├── requirements.txt        ← Dependencies
├── api-keys.json          ← API credentials (QUAN TRỌNG!)
├── predict.py             ← Main entry point
├── config/
│   └── api_config.py      ← API configuration loader
└── modules/
    ├── categories.py               ← Question taxonomy
    ├── question_classifier.py      ← Rule-based classifier
    ├── simple_knowledge.py         ← Knowledge cache
    ├── llm/
    │   └── api_client.py          ← VNPT API client
    └── utils/
        └── text_processing.py      ← Text utilities
```

---

## 🚀 CÁCH BUILD VÀ TEST DOCKER

### Bước 1: Build Docker Image

```bash
cd D:\Khang\Thi\VNPT

# Build image
docker build -t vnpt-qa-system .
```

**Expected output**:
```
Successfully built xxxxx
Successfully tagged vnpt-qa-system:latest
```

**Expected size**: ~2.6GB

### Bước 2: Test Local

```bash
# Prepare test data
mkdir -p test_data test_output

# Copy test file
copy data\val_10.json test_data\private_test.json

# Run container
docker run --rm \
  -v "%cd%\test_data:/code/data" \
  -v "%cd%\test_output:/code/output" \
  vnpt-qa-system

# Check output
type test_output\submission.csv
```

**Expected output**: File CSV có format:
```csv
qid,answer
val_0001,B
val_0002,C
val_0003,B
...
```

### Bước 3: Verify Results

```bash
# Check file exists
dir test_output\submission.csv

# Count lines (should be 11: header + 10 questions)
find /c /v "" test_output\submission.csv
```

---

## 📋 FORMAT FILE SUBMISSION

### submission.csv
```csv
qid,answer
test_0001,A
test_0002,B
test_0003,C
...
```

**Lưu ý**:
- Header: `qid,answer`
- Mỗi dòng: `<question_id>,<answer_letter>`
- Answer phải là A-J (tùy số lượng choices)
- Không có khoảng trắng thừa
- Encoding: UTF-8

---

## 🐳 DOCKER REQUIREMENTS (Theo Quy Định Cuộc Thi)

### Input
- Mount point: `/code/data/private_test.json`
- Format: JSON array of questions
```json
[
  {
    "qid": "test_0001",
    "question": "...",
    "choices": ["A", "B", "C", "D"]
  }
]
```

### Output
- File path: `/code/output/submission.csv`
- Format: CSV (qid,answer)

### Container Specs
- Base image: `nvidia/cuda:12.2.0-runtime-ubuntu20.04` ✅
- Memory: Recommend 2GB
- CPU: No GPU needed (CPU only)
- Timeout: 30 minutes for 400 questions (dự kiến 10 phút)

---

## 📤 CÁCH NỘP

### Option 1: Docker Hub (Recommended)

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag vnpt-qa-system <your-dockerhub-username>/vnpt-qa-system:latest

# Push
docker push <your-dockerhub-username>/vnpt-qa-system:latest
```

Submit link: `<your-dockerhub-username>/vnpt-qa-system:latest`

### Option 2: Docker Save/Load

```bash
# Save image to file
docker save vnpt-qa-system > vnpt-qa-system.tar

# Compress (optional)
gzip vnpt-qa-system.tar

# Submit file: vnpt-qa-system.tar.gz (~1.5GB compressed)
```

### Option 3: Registry Khác

Theo hướng dẫn của ban tổ chức (nếu có private registry)

---

## ✅ CHECKLIST TRƯỚC KHI NỘP

- [ ] Docker image build thành công
- [ ] Test local với data mẫu → có file submission.csv
- [ ] File CSV đúng format (header + data rows)
- [ ] Answers nằm trong valid range (A-J)
- [ ] Docker image size < 10GB (hiện tại: 2.6GB ✅)
- [ ] api-keys.json có trong image (QUAN TRỌNG!)
- [ ] Không có hardcoded paths (/code/data, /code/output)

---

## 🔧 TROUBLESHOOTING

### Issue 1: "Module not found"
```bash
# Kiểm tra structure trong container
docker run --rm vnpt-qa-system ls -la /code
docker run --rm vnpt-qa-system ls -la /code/modules
```

**Fix**: Đảm bảo COPY đúng trong Dockerfile

### Issue 2: "API Error 401"
```bash
# Kiểm tra api-keys.json
docker run --rm vnpt-qa-system cat /code/api-keys.json
```

**Fix**: COPY api-keys.json trong Dockerfile

### Issue 3: "No such file /code/data/private_test.json"
```bash
# Kiểm tra mount
docker run --rm -v "%cd%\test_data:/code/data" vnpt-qa-system ls -la /code/data
```

**Fix**: Đảm bảo -v mount đúng path

### Issue 4: "Rate limit exceeded"
**Lý do**: Đã vượt quota 60 req/hour

**Fix**: Đợi 1 tiếng hoặc test với data nhỏ hơn

---

## 📊 EXPECTED PERFORMANCE

### On Test Set (400 questions)
```
Expected accuracy: 60-65%
Runtime: 8-12 minutes
API calls: ~400-450
Memory: ~500MB peak
```

### Breakdown:
- Reading comprehension: 75-80%
- Math/Logic: 40-50% (giới hạn LLM)
- Domain questions: 60-70%

---

## 📞 CONTACT & SUPPORT

**Deadline**: 19/12/2025

**Platform**: Submit theo hướng dẫn ban tổ chức

**Last updated**: 06/12/2025

---

## 🎯 QUICK START - NỘP NGAY

```bash
# 1. Build
cd D:\Khang\Thi\VNPT
docker build -t vnpt-qa-system .

# 2. Test
mkdir test_data test_output
copy data\val_10.json test_data\private_test.json
docker run --rm -v "%cd%\test_data:/code/data" -v "%cd%\test_output:/code/output" vnpt-qa-system

# 3. Verify
type test_output\submission.csv

# 4. Submit
# Push to Docker Hub hoặc save file theo hướng dẫn ban tổ chức
```

**Xong! Hệ thống sẵn sàng nộp.**
