# KẾ HOẠCH CHI TIẾT DỰ ÁN VNPT AI HACKATHON - TRACK 2

## 📅 TIMELINE TỔNG QUAN
- **Thời gian**: 05/12/2025 - 17/12/2025 (13 ngày)
- **Deadline nộp bài**: 19/12/2025 trước 23:59 (UTC+7)
- **Thời gian còn lại**: ~13 ngày

---

## 🎯 MỤC TIÊU CHÍNH
Xây dựng hệ thống RAG (Retrieval-Augmented Generation) để trả lời chính xác các câu hỏi trắc nghiệm tiếng Việt về:
- Văn hóa, lịch sử, địa lý, chính trị Việt Nam
- Toán học và tư duy logic
- Đọc hiểu văn bản dài
- Phân biệt câu hỏi cần từ chối trả lời

---

## 📊 PHÂN TÍCH BỘ DỮ LIỆU

### Dữ liệu có sẵn:
- **Validation set**: 100 câu hỏi (có đáp án) - để test và đánh giá
- **Test set**: 400 câu hỏi (không có đáp án) - để submit

### Các loại câu hỏi:
1. **Câu hỏi từ chối**: Không được trả lời (vi phạm pháp luật/đạo đức)
2. **Câu hỏi bắt buộc đúng**: Kiến thức chính xác về VN
3. **Câu hỏi đọc hiểu**: Có đoạn văn dài kèm theo
4. **Câu hỏi toán/logic**: Cần tính toán
5. **Câu hỏi đa lĩnh vực**: Kiến thức tổng hợp

---

## 🗓️ KẾ HOẠCH THEO GIAI ĐOẠN

### GIAI ĐOẠN 1: PHÂN TÍCH & THIẾT KẾ (Ngày 1-2)
**Thời gian**: 2 ngày

#### Task 1.1: Phân tích dữ liệu validation set
- [ ] Đọc và phân loại 100 câu hỏi trong val.json
- [ ] Thống kê tỷ lệ từng loại câu hỏi
- [ ] Xác định độ khó và pattern của từng loại
- [ ] Phân tích các câu hỏi cần từ chối (refusal questions)

**Output**: File `data_analysis.md` với thống kê chi tiết

#### Task 1.2: Thiết kế kiến trúc hệ thống
- [ ] Vẽ sơ đồ pipeline RAG
- [ ] Xác định các module cần thiết:
  - Question Classification
  - Refusal Detection
  - RAG Retrieval
  - Answer Generation
  - Math Solver
- [ ] Thiết kế flow xử lý cho từng loại câu hỏi

**Output**: File `ARCHITECTURE.md` với sơ đồ và mô tả

#### Task 1.3: Lập kế hoạch thu thập dữ liệu
- [ ] Liệt kê nguồn dữ liệu tiếng Việt:
  - Wikipedia tiếng Việt
  - Trang thông tin chính phủ
  - Sách giáo khoa
  - Tài liệu lịch sử, địa lý VN
- [ ] Xác định phương pháp crawl và xử lý

**Output**: File `DATA_SOURCES.md`

---

### GIAI ĐOẠN 2: THU THẬP & XỬ LÝ DỮ LIỆU (Ngày 3-5)
**Thời gian**: 3 ngày

#### Task 2.1: Crawl dữ liệu
- [ ] Viết script crawl Wikipedia tiếng Việt
  - Các bài viết về lịch sử VN
  - Các bài viết về địa lý VN
  - Các bài viết về văn hóa VN
  - Các bài viết về chính trị VN
- [ ] Crawl dữ liệu từ nguồn chính thống
- [ ] Lưu trữ dữ liệu thô

**Output**:
- Script `crawlers/wikipedia_crawler.py`
- Folder `raw_data/` chứa dữ liệu

#### Task 2.2: Xử lý và làm sạch dữ liệu
- [ ] Viết script làm sạch text
- [ ] Loại bỏ noise, format đặc biệt
- [ ] Chuẩn hóa tiếng Việt (dấu, encoding)
- [ ] Chia nhỏ văn bản thành chunks phù hợp

**Output**:
- Script `data_processing/clean_data.py`
- Folder `processed_data/` chứa dữ liệu đã xử lý

#### Task 2.3: Tạo Vector Database
- [ ] Chunking văn bản (chunk size: 256-512 tokens)
- [ ] Sử dụng Embedding API để vector hóa
- [ ] Chọn vector database (FAISS/ChromaDB/Qdrant)
- [ ] Build index và lưu trữ
- [ ] Test tốc độ retrieval

**Output**:
- Script `vector_db/build_index.py`
- File index: `vector_db/index.faiss` hoặc tương đương

---

### GIAI ĐOẠN 3: XÂY DỰNG PIPELINE (Ngày 6-9)
**Thời gian**: 4 ngày

#### Task 3.1: Module Question Classification
- [ ] Viết classifier để phân loại câu hỏi:
  - Knowledge-based (cần RAG)
  - Math/Logic (cần solver)
  - Reading comprehension (có context sẵn)
  - Refusal (cần từ chối)
- [ ] Test trên validation set

**Output**: File `modules/question_classifier.py`

#### Task 3.2: Module Refusal Detection
- [ ] Xây dựng rule-based filter cho câu hỏi vi phạm:
  - Câu hỏi về vi phạm pháp luật
  - Câu hỏi về gian lận
  - Câu hỏi không phù hợp đạo đức
- [ ] Prompt LLM để detect refusal cases
- [ ] Test và tune threshold

**Output**: File `modules/refusal_detector.py`

#### Task 3.3: Module RAG Retrieval
- [ ] Implement retrieval pipeline:
  - Query preprocessing
  - Embedding query
  - Similarity search (top-k documents)
  - Reranking nếu cần
- [ ] Test với validation questions
- [ ] Optimize số lượng documents retrieve

**Output**: File `modules/rag_retriever.py`

#### Task 3.4: Module Answer Generation
- [ ] Viết prompt template cho LLM:
  - System prompt
  - Context injection
  - Question formatting
  - Answer format (A/B/C/D)
- [ ] Implement retry logic nếu API fail
- [ ] Handle rate limiting
- [ ] Test với cả LLM Small và Large

**Output**: File `modules/answer_generator.py`

#### Task 3.5: Module Math Solver
- [ ] Phát hiện câu hỏi toán học
- [ ] Extract công thức và số liệu
- [ ] Sử dụng LLM với chain-of-thought prompting
- [ ] Verify kết quả tính toán

**Output**: File `modules/math_solver.py`

#### Task 3.6: Main Pipeline Integration
- [ ] Tích hợp tất cả modules
- [ ] Implement routing logic
- [ ] Xử lý edge cases
- [ ] Logging và error handling

**Output**: File `predict.py`

---

### GIAI ĐOẠN 4: TESTING & OPTIMIZATION (Ngày 10-12)
**Thời gian**: 3 ngày

#### Task 4.1: Testing trên Validation Set
- [ ] Run pipeline trên 100 câu val
- [ ] Tính accuracy cho từng loại câu hỏi
- [ ] Phân tích câu sai
- [ ] Identify patterns của lỗi

**Output**: File `evaluation/val_results.json`

#### Task 4.2: Prompt Engineering
- [ ] Thử nghiệm nhiều prompt templates
- [ ] A/B testing prompts
- [ ] Optimize cho từng loại câu hỏi
- [ ] Few-shot examples

**Output**: File `prompts/optimized_prompts.json`

#### Task 4.3: Hyperparameter Tuning
- [ ] Tune retrieval parameters:
  - Top-k documents
  - Similarity threshold
  - Chunk size
- [ ] Tune generation parameters:
  - Temperature
  - Top-p
  - Max tokens
- [ ] Experiment LLM Small vs Large
- [ ] Balance cost vs accuracy

**Output**: File `config/best_params.yaml`

#### Task 4.4: Error Analysis & Fix
- [ ] Phân loại các lỗi:
  - Retrieval failure
  - Generation error
  - Classification error
  - Refusal error
- [ ] Fix từng loại lỗi
- [ ] Re-test sau fix

**Output**: File `evaluation/error_analysis.md`

---

### GIAI ĐOẠN 5: DOCKERIZATION & SUBMISSION (Ngày 13)
**Thời gian**: 1 ngày

#### Task 5.1: Tạo Dockerfile
- [ ] Base image: nvidia/cuda:12.2.0-devel-ubuntu20.04
- [ ] Install dependencies
- [ ] Copy source code
- [ ] Setup entry point

**Output**: File `Dockerfile`

#### Task 5.2: Tạo Requirements & Scripts
- [ ] List tất cả dependencies
- [ ] Pin versions
- [ ] Tạo inference.sh script
- [ ] Test local build

**Output**:
- File `requirements.txt`
- File `inference.sh`

#### Task 5.3: Documentation
- [ ] Viết README.md chi tiết:
  - Pipeline flow
  - Data processing steps
  - How to run
  - Architecture diagram
- [ ] Comment code
- [ ] Add docstrings

**Output**: File `README.md`

#### Task 5.4: Build & Test Docker
- [ ] Build Docker image locally
- [ ] Test với validation set
- [ ] Verify output format
- [ ] Check resource usage

#### Task 5.5: Push to DockerHub
- [ ] Tag image
- [ ] Push to DockerHub
- [ ] Verify push success

#### Task 5.6: Submission
- [ ] Push code to GitHub (public repo)
- [ ] Submit GitHub link
- [ ] Submit DockerHub image name
- [ ] Verify submission before deadline

---

## 📦 CẤU TRÚC THỨ MỤC DỰ KIẾN

```
VNPT/
├── data/
│   ├── val.json
│   ├── test.json
│   ├── raw_data/
│   └── processed_data/
├── vector_db/
│   ├── index.faiss
│   └── build_index.py
├── modules/
│   ├── __init__.py
│   ├── question_classifier.py
│   ├── refusal_detector.py
│   ├── rag_retriever.py
│   ├── answer_generator.py
│   └── math_solver.py
├── crawlers/
│   └── wikipedia_crawler.py
├── data_processing/
│   └── clean_data.py
├── prompts/
│   └── optimized_prompts.json
├── config/
│   ├── best_params.yaml
│   └── api_config.py
├── evaluation/
│   ├── evaluate.py
│   ├── val_results.json
│   └── error_analysis.md
├── predict.py
├── inference.sh
├── requirements.txt
├── Dockerfile
├── README.md
├── api-keys.json
└── PROJECT_PLAN.md (file này)
```

---

## 🔧 CÔNG NGHỆ & TOOLS

### Core Libraries:
- **LangChain**: RAG framework
- **FAISS** / **ChromaDB**: Vector database
- **Requests**: API calls
- **BeautifulSoup4**: Web crawling
- **Pandas**: Data processing
- **NumPy**: Numerical operations

### Optional Libraries:
- **Sentence-Transformers**: Local embeddings (nếu cần)
- **Transformers**: Model utilities
- **PyTorch**: Deep learning (nếu cần fine-tune)
- **Scikit-learn**: ML utilities

---

## ⚠️ RỦI RO & GIẢI PHÁP

### Rủi ro 1: API Quota hết
**Giải pháp**:
- Sử dụng cache cho các query giống nhau
- Optimize số lần gọi API
- Ưu tiên LLM Small, chỉ dùng Large cho câu khó
- Test kỹ trước khi submit để không lãng phí quota

### Rủi ro 2: Retrieval không chính xác
**Giải pháp**:
- Cải thiện chất lượng chunking
- Thử nghiệm nhiều embedding strategies
- Implement reranking
- Hybrid search (keyword + semantic)

### Rủi ro 3: Docker build failed
**Giải pháp**:
- Test Docker build sớm (ngày 10-11)
- Có backup plan với lighter dependencies
- Document troubleshooting steps

### Rủi ro 4: Accuracy thấp
**Giải pháp**:
- Ensemble multiple approaches
- Fallback mechanism
- Human-in-the-loop cho validation set
- Prompt engineering intensive

---

## 📈 KPI & METRICS

### Metrics chính:
1. **Overall Accuracy**: Target > 70%
2. **Refusal Precision**: 100% (không được trả lời câu cần từ chối)
3. **Refusal Recall**: > 90% (phát hiện được hầu hết câu cần từ chối)
4. **Per-category Accuracy**:
   - Knowledge-based: > 75%
   - Math/Logic: > 65%
   - Reading comprehension: > 80%

### Metrics phụ:
- API call efficiency (calls per question)
- Average response time
- Cost per question (API quota usage)

---

## 👥 PHÂN CÔNG CÔNG VIỆC (Nếu có team)

### Role 1: Data Engineer
- Thu thập dữ liệu
- Xử lý và làm sạch
- Build vector database

### Role 2: ML Engineer
- Xây dựng pipeline
- Prompt engineering
- Model optimization

### Role 3: DevOps
- Docker setup
- CI/CD nếu có
- Deployment & submission

**Lưu ý**: Nếu làm 1 mình, ưu tiên theo thứ tự timeline

---

## 📝 DAILY CHECKLIST

### Mỗi ngày cần:
- [ ] Commit code lên GitHub
- [ ] Update progress vào file này
- [ ] Test incremental changes
- [ ] Document findings
- [ ] Track API usage

### Mỗi 2 ngày cần:
- [ ] Review toàn bộ pipeline
- [ ] Run validation test
- [ ] Measure accuracy improvement

---

## 🎓 TÀI LIỆU THAM KHẢO

### RAG Resources:
- LangChain Documentation
- FAISS Documentation
- Prompt Engineering Guide

### Vietnamese NLP:
- PhoBERT papers
- Vietnamese Wikipedia dump
- VnCoreNLP tools

### Competition-specific:
- Tài liệu mô tả APIs LLM_Embedding Track 2.pdf
- Tài liệu mô tả phương thức nộp bài Track 2 The Builder.pdf
- Thể lệ cuộc thi (todo.txt)

---

## 🏁 DEFINITION OF DONE

### Tiêu chí hoàn thành project:
- [ ] Code chạy được end-to-end trong Docker
- [ ] Accuracy trên val set > 70%
- [ ] Không có refusal false negative
- [ ] Docker image < 10GB
- [ ] README.md hoàn chỉnh
- [ ] Code có comments đầy đủ
- [ ] Đã test build Docker local thành công
- [ ] Đã push lên DockerHub
- [ ] Đã submit đúng deadline

---

## 📞 LƯU Ý QUAN TRỌNG

1. **Không sử dụng external API** (ChatGPT, Gemini) trong inference
2. **Image phải push lên DockerHub trước 23:59 ngày 19/12/2025**
3. **GitHub repo phải public và không sửa sau deadline**
4. **Maximum 5 submissions per day**
5. **Test kỹ với GPU (CUDA 12.2)**

---

**Ngày tạo**: 06/12/2025
**Cập nhật lần cuối**: 06/12/2025
