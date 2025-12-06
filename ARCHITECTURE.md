# KIẾN TRÚC HỆ THỐNG - MULTI-SPECIALIZED RAG

## 🎯 TỔNG QUAN

Hệ thống sử dụng **Multi-Specialized RAG Architecture** với:
- **Question Classifier**: Phân loại câu hỏi thành 7 categories
- **Specialized Handlers**: Mỗi category có handler riêng, tối ưu cho loại đó
- **Domain-Specific Vector DBs**: Mỗi lĩnh vực có vector database riêng
- **Smart Routing**: Route câu hỏi đến handler phù hợp

---

## 📊 TAXONOMY CÂU HỎI

Dựa trên phân tích validation set, chia thành **7 CATEGORIES**:

### 1. READING_COMPREHENSION (15-20%)
**Đặc điểm**:
- Câu hỏi có đoạn văn dài kèm theo
- Pattern: "Đoạn thông tin:" hoặc "-- Đoạn văn X --"
- Context đã có sẵn trong question

**Handler**: ReadingComprehensionHandler
**Không cần RAG**: Chỉ cần LLM đọc hiểu context có sẵn

**Ví dụ**:
```
val_0001: "Đoạn thông tin:\n[1] Tiêu đề: Khỉ thí nghiệm..."
val_0007: "Đoạn thông tin:\n-- Đoạn văn 1 --..."
```

---

### 2. MATH_LOGIC (15-20%)
**Đặc điểm**:
- Câu hỏi toán học, vật lý, logic
- Có công thức, số liệu, phép tính
- Keywords: "tính", "xác định", "công thức", "giải", số học

**Handler**: MathLogicHandler
**Không cần RAG**: Dùng Chain-of-Thought với LLM Large

**Ví dụ**:
```
val_0004: "độ co giãn của cầu theo giá"
val_0005: "Điện trở tương đương khi..."
```

**Strategy**:
1. Extract numbers và formulas
2. Chain-of-thought prompting
3. Step-by-step reasoning
4. Sử dụng LLM Large (tốt hơn cho math)

---

### 3. REFUSAL (5-10%)
**Đặc điểm**:
- Câu hỏi vi phạm pháp luật, đạo đức
- Keywords: "trốn", "tránh", "lừa đảo", "gian lận", "vi phạm"
- Intent xấu, hướng dẫn làm điều sai

**Handler**: RefusalHandler
**Không cần RAG**: Rule-based + LLM classifier

**Ví dụ**:
```
test_0001: "Làm cách nào để tránh việc cung cấp thông tin..."
```

**Strategy**:
1. Rule-based keyword matching
2. LLM intent classification
3. Return chuẩn: "Tôi không thể chia sẻ nội dung liên quan đến vấn đề này"

---

### 4. HISTORY_VIETNAM (20-25%)
**Đặc điểm**:
- Lịch sử Việt Nam
- Triều đại, vua, sự kiện lịch sử, kháng chiến
- Ngày tháng, địa điểm lịch sử

**Handler**: HistoryHandler
**CẦN RAG**: Vector DB riêng cho lịch sử

**Ví dụ**:
```
val_0002: "Ngôi chùa Ba La Mật được khai dựng vào năm nào?"
```

**Vector DB**: `vector_dbs/history_db/`
- Documents: Wikipedia lịch sử VN (500-800 docs)
- Retrieval strategy: Semantic search + date/name matching

---

### 5. CULTURE_VIETNAM (15-20%)
**Đặc điểm**:
- Văn hóa, văn học, nghệ thuật VN
- Lễ hội, tập quán, ẩm thực
- Tác giả, tác phẩm văn học
- Di sản UNESCO

**Handler**: CultureHandler
**CẦN RAG**: Vector DB riêng cho văn hóa

**Ví dụ**:
```
val_0006: "Bạn nên làm gì khi bắt tay?" (văn hóa giao tiếp)
```

**Vector DB**: `vector_dbs/culture_db/`
- Documents: Wikipedia văn hóa, văn học (400-600 docs)
- Retrieval strategy: Semantic search + entity matching

---

### 6. GEOGRAPHY_VIETNAM (10-15%)
**Đặc điểm**:
- Địa lý VN: tỉnh thành, sông núi
- Dân số, diện tích, khí hậu
- Vùng kinh tế

**Handler**: GeographyHandler
**CẦN RAG**: Vector DB riêng cho địa lý

**Vector DB**: `vector_dbs/geography_db/`
- Documents: 63 tỉnh/thành + địa lý tự nhiên (200-300 docs)
- Retrieval strategy: Location-aware search

---

### 7. POLITICS_LAW (10-15%)
**Đặc điểm**:
- Chính trị, pháp luật VN
- Hiến pháp, luật, nghị định
- Hệ thống chính trị
- Quan hệ quốc tế

**Handler**: PoliticsHandler
**CẦN RAG**: Vector DB riêng cho chính trị

**Ví dụ**:
```
val_0003: "Việc đưa ra các quy định về thuế, pháp luật..."
```

**Vector DB**: `vector_dbs/politics_db/`
- Documents: Wikipedia chính trị + pháp luật (150-250 docs)
- Retrieval strategy: Law/policy aware search

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT QUESTION                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               QUESTION CLASSIFIER                            │
│  - Rule-based patterns (reading, math, refusal)             │
│  - LLM-based classification (domain categories)             │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────────────┐
        │              │                      │
        ▼              ▼                      ▼
  ┌─────────┐   ┌──────────┐         ┌──────────────┐
  │ READING │   │   MATH   │         │   REFUSAL    │
  │ HANDLER │   │ HANDLER  │         │   HANDLER    │
  └─────────┘   └──────────┘         └──────────────┘
        │              │                      │
        │         (No RAG)             (No RAG)
        ▼
  Extract context
  from question
        │
        ▼
  ┌──────────────┐
  │ LLM Generate │
  └──────────────┘


                       ▼
        ┌──────────────┼──────────────────────┐
        │              │              │       │
        ▼              ▼              ▼       ▼
  ┌─────────┐   ┌──────────┐   ┌──────────┐ ┌──────────┐
  │ HISTORY │   │ CULTURE  │   │GEOGRAPHY │ │ POLITICS │
  │ HANDLER │   │ HANDLER  │   │ HANDLER  │ │ HANDLER  │
  └────┬────┘   └────┬─────┘   └────┬─────┘ └────┬─────┘
       │             │              │            │
       │             │              │            │
       ▼             ▼              ▼            ▼
  ┌─────────┐   ┌──────────┐   ┌──────────┐ ┌──────────┐
  │History  │   │ Culture  │   │Geography │ │ Politics │
  │VectorDB │   │VectorDB  │   │VectorDB  │ │VectorDB  │
  └────┬────┘   └────┬─────┘   └────┬─────┘ └────┬─────┘
       │             │              │            │
       │      Retrieve Top-K Docs   │            │
       │             │              │            │
       └─────────────┼──────────────┼────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Context Builder │
            │ (Merge + Rank)  │
            └────────┬─────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Prompt Builder  │
            │ (Category-aware)│
            └────────┬─────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  LLM Generate   │
            │ (Small/Large)   │
            └────────┬─────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Answer Extractor│
            │  (A/B/C/D)      │
            └────────┬─────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  FINAL ANSWER   │
            └─────────────────┘
```

---

## 📂 CẤU TRÚC THƯ MỤC

```
VNPT/
├── config/
│   ├── api_config.py           # API keys, endpoints
│   ├── category_config.yaml    # Config cho từng category
│   └── model_config.yaml       # LLM parameters
│
├── modules/
│   ├── __init__.py
│   ├── question_classifier.py  # Main classifier
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base_handler.py            # Base class
│   │   ├── reading_handler.py         # Đọc hiểu
│   │   ├── math_handler.py            # Toán/Logic
│   │   ├── refusal_handler.py         # Từ chối
│   │   ├── history_handler.py         # Lịch sử (RAG)
│   │   ├── culture_handler.py         # Văn hóa (RAG)
│   │   ├── geography_handler.py       # Địa lý (RAG)
│   │   └── politics_handler.py        # Chính trị (RAG)
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_store.py      # FAISS wrapper
│   │   └── retriever.py         # Retrieval logic
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── api_client.py        # VNPT API client
│   │   └── prompt_templates.py  # Prompts cho từng category
│   │
│   └── utils/
│       ├── __init__.py
│       ├── text_processing.py   # Clean, normalize
│       └── answer_extraction.py # Extract A/B/C/D
│
├── vector_dbs/
│   ├── history_db/
│   │   ├── index.faiss
│   │   └── metadata.json
│   ├── culture_db/
│   ├── geography_db/
│   └── politics_db/
│
├── data/
│   ├── raw_data/
│   │   ├── history/
│   │   ├── culture/
│   │   ├── geography/
│   │   └── politics/
│   ├── processed_data/
│   └── chunks/
│
├── crawlers/
│   ├── wikipedia_crawler.py
│   └── data_processor.py
│
├── evaluation/
│   ├── evaluate.py
│   └── error_analysis.py
│
├── predict.py                  # Main entry point
├── inference.sh                # Bash script
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🔄 WORKFLOW CHI TIẾT

### Step 1: Question Classification
```python
def classify_question(question: str) -> Category:
    # Rule-based checks first (fast)
    if "Đoạn thông tin:" in question:
        return Category.READING

    if contains_math_keywords(question):
        return Category.MATH

    if contains_refusal_keywords(question):
        return Category.REFUSAL

    # LLM-based classification (for domain categories)
    category = llm_classify(question)
    return category  # HISTORY, CULTURE, GEOGRAPHY, POLITICS
```

### Step 2: Route to Handler
```python
def route_to_handler(question: str, category: Category) -> Handler:
    handlers = {
        Category.READING: ReadingHandler(),
        Category.MATH: MathHandler(),
        Category.REFUSAL: RefusalHandler(),
        Category.HISTORY: HistoryHandler(vector_db="history_db"),
        Category.CULTURE: CultureHandler(vector_db="culture_db"),
        Category.GEOGRAPHY: GeographyHandler(vector_db="geography_db"),
        Category.POLITICS: PoliticsHandler(vector_db="politics_db"),
    }
    return handlers[category]
```

### Step 3: Handler Processing

**For RAG-based handlers** (History, Culture, Geography, Politics):
```python
class HistoryHandler(BaseHandler):
    def __init__(self, vector_db_path):
        self.vector_db = FAISSVectorStore(vector_db_path)
        self.llm = VNPTClient()

    def handle(self, question: str, choices: List[str]) -> str:
        # 1. Retrieve relevant documents
        docs = self.vector_db.search(
            query=question,
            top_k=5,
            filters={"category": "history"}
        )

        # 2. Build context
        context = self.build_context(docs)

        # 3. Build prompt
        prompt = self.build_prompt(
            question=question,
            context=context,
            choices=choices
        )

        # 4. Generate answer
        response = self.llm.generate(
            prompt=prompt,
            model="vnptai_hackathon_small"  # or large
        )

        # 5. Extract answer (A/B/C/D)
        answer = extract_answer(response)

        return answer
```

**For Non-RAG handlers**:
```python
class ReadingHandler(BaseHandler):
    def handle(self, question: str, choices: List[str]) -> str:
        # Extract context from question itself
        context = extract_context_from_question(question)

        # Build prompt
        prompt = build_reading_prompt(question, context, choices)

        # Generate
        response = self.llm.generate(prompt)

        return extract_answer(response)
```

---

## ⚡ OPTIMIZATION STRATEGIES

### 1. Vector DB Optimization

**Per-category DBs advantages**:
- ✅ Smaller index size → Faster search
- ✅ Better precision (không bị nhiễu từ other domains)
- ✅ Category-specific embeddings strategies
- ✅ Can use different chunking strategies

**Example**:
- History DB: Chunk by events/dates
- Geography DB: Chunk by locations
- Culture DB: Chunk by topics/works

### 2. Retrieval Optimization

**Hybrid search**:
```python
# Semantic search
semantic_results = vector_db.similarity_search(query, k=10)

# Keyword boost (cho dates, names, locations)
keyword_results = keyword_search(query)

# Merge and rerank
final_results = rerank(semantic_results, keyword_results, top_k=5)
```

**Metadata filtering**:
```python
# For history: filter by time period
docs = vector_db.search(
    query="Nhà Lý",
    filters={"time_period": "medieval", "topic": "dynasty"}
)
```

### 3. LLM Selection Strategy

**Smart model selection**:
```python
def select_model(category: Category, complexity: str) -> str:
    # Math → always use Large (better reasoning)
    if category == Category.MATH:
        return "vnptai_hackathon_large"

    # Simple factual → Small (save quota)
    if complexity == "simple":
        return "vnptai_hackathon_small"

    # Complex reasoning → Large
    if complexity == "complex":
        return "vnptai_hackathon_large"

    return "vnptai_hackathon_small"  # default
```

### 4. Caching Strategy

**Cache frequently asked patterns**:
```python
cache = {}

def get_answer_with_cache(question: str):
    # Check cache
    question_hash = hash_question(question)
    if question_hash in cache:
        return cache[question_hash]

    # Generate
    answer = pipeline.predict(question)

    # Cache
    cache[question_hash] = answer
    return answer
```

---

## 📊 EXPECTED PERFORMANCE

### Accuracy Targets by Category:

| Category | Target Acc | Strategy | LLM Model |
|----------|-----------|----------|-----------|
| Reading | 85% | Direct LLM | Small |
| Math | 65% | CoT + Large | Large |
| Refusal | 100% (Prec) | Rules + LLM | Small |
| History | 75% | RAG + history_db | Small/Large |
| Culture | 75% | RAG + culture_db | Small |
| Geography | 80% | RAG + geo_db | Small |
| Politics | 70% | RAG + politics_db | Small |

### API Usage Optimization:

**Per question estimate**:
- Classifier: 0 calls (rule-based mostly)
- Retrieval: 1 embedding call
- Generation: 1 LLM call

**Total per 400 questions**:
- Embeddings: ~400 calls (< 500/min quota)
- LLM Small: ~300 calls (< 1000/day quota)
- LLM Large: ~100 calls (< 500/day quota)

---

## 🚀 DEPLOYMENT FLOW

1. **Build Vector DBs** (one-time):
   ```bash
   python crawlers/wikipedia_crawler.py
   python data_processing/build_vector_dbs.py
   ```

2. **Test on validation**:
   ```bash
   python predict.py --input data/val.json --output val_predictions.csv
   python evaluation/evaluate.py
   ```

3. **Optimize**:
   - Tune retrieval k
   - Adjust prompts
   - Balance Small/Large model usage

4. **Dockerize**:
   ```bash
   docker build -t vnpt_solution .
   docker run -v /data:/code/data vnpt_solution
   ```

---

## 📈 MONITORING & METRICS

**Track per category**:
- Classification accuracy
- Retrieval success rate
- Generation accuracy
- API usage per category
- Latency per category

**Continuous improvement**:
1. Error analysis by category
2. Identify weak categories
3. Improve retrieval for that domain
4. Tune prompts for that category
5. Re-test

---

**Version**: 1.0
**Created**: 06/12/2025
**Last Updated**: 06/12/2025
