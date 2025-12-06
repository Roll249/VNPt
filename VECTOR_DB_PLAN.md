# KẾ HOẠCH XÂY DỰNG VECTOR DATABASE

## 🎯 MỤC TIÊU

Xây dựng Vector Database để:
1. **Giảm API calls**: Từ ~93 calls xuống ~20-30 calls
2. **Tránh rate limit**: 60 req/hour không đủ cho 93 câu
3. **Tăng accuracy**: Cung cấp context chính xác cho domain questions
4. **Độc lập hơn**: Không phụ thuộc hoàn toàn vào LLM API

---

## ❓ VẤN ĐỀ HIỆN TẠI

### Rate Limit Issue
```
Current: 93 questions × 1 API call = 93 API calls
Rate limit: 60 calls/hour
Result: Chạy hết quota ở câu ~60, phải đợi 1 tiếng
```

### Phân tích API Usage
```
Reading Comprehension: 20 câu × 1 call = 20 calls
Math/Logic:           15 câu × 1 call = 15 calls
Domain Questions:     58 câu × 1 call = 58 calls  ← ĐÂY LÀ VẤN ĐỀ!
----------------------------------------------
Total:                                93 calls

Trong đó Domain Questions chiếm 62% API calls!
```

### Solution: Vector DB cho Domain Questions
```
Thay vì:
Question → LLM API → Answer (1 API call)

Dùng:
Question → Vector DB Retrieval → Context → LLM API → Answer
           (0 API calls)       (chỉ 1 API call nếu cần)
```

**Giảm được**: 58 calls xuống ~10-15 calls (khi cần LLM synthesize)

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### 1. Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      INPUT QUESTION                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Question Classifier (Rule-based)                │
│  → Reading, Math, Refusal, History, Culture, Geo, Politics  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                 │
        ▼                ▼                 ▼
┌──────────────┐  ┌─────────────┐  ┌─────────────────────────┐
│   Reading    │  │    Math     │  │   Domain Questions      │
│   (No VDB)   │  │  (No VDB)   │  │   (USE VECTOR DB!)      │
│              │  │             │  │                         │
│  → LLM API   │  │  → LLM API  │  │  → Vector DB Retrieval  │
└──────────────┘  └─────────────┘  └────────┬────────────────┘
                                             │
                                             ▼
                                   ┌──────────────────────────┐
                                   │  FAISS Vector Search     │
                                   │  Top-K relevant docs     │
                                   └────────┬─────────────────┘
                                            │
                                            ▼
                                   ┌──────────────────────────┐
                                   │  Build Prompt w/ Context │
                                   │  → LLM API (if needed)   │
                                   └────────┬─────────────────┘
                                            │
                                            ▼
                                   ┌──────────────────────────┐
                                   │     ANSWER              │
                                   └──────────────────────────┘
```

### 2. Vector DB Components

```
Data Pipeline:
├── 1. Data Collection (Crawl Wikipedia, textbooks)
├── 2. Document Processing (Clean, chunk)
├── 3. Embedding Generation (VNPT Embedding API)
├── 4. FAISS Index Building
└── 5. Retrieval Integration

Runtime:
├── Question → Embedding
├── FAISS Search (Top-K)
├── Context Ranking
└── Answer Extraction (direct or LLM)
```

---

## 📊 DATA COLLECTION STRATEGY

### Domain Coverage

#### 1. Lịch sử Việt Nam (History)
**Sources:**
- Wikipedia tiếng Việt: Các triều đại, sự kiện lịch sử
- Sách giáo khoa lịch sử lớp 10, 11, 12
- Thời kỳ: Từ Hồng Bàng → Hiện đại

**Example queries:**
```
- "Nhà Lý được thành lập năm nào?"
- "Ai là người sáng lập nhà Trần?"
- "Chiến thắng Bạch Đằng năm 1288 do ai chỉ huy?"
```

**Data format:**
```json
{
  "domain": "history",
  "topic": "Nhà Lý",
  "content": "Nhà Lý (1009-1225) được Lý Công Uẩn thành lập...",
  "key_facts": [
    "Năm thành lập: 1009",
    "Người sáng lập: Lý Công Uẩn",
    "Thủ đô: Thăng Long (Hà Nội)"
  ]
}
```

#### 2. Văn hóa Việt Nam (Culture)
**Sources:**
- Wikipedia: Văn học, nghệ thuật, lễ hội
- Sách giáo khoa Ngữ văn
- Di sản văn hóa UNESCO

**Example data:**
```json
{
  "domain": "culture",
  "topic": "Truyện Kiều",
  "content": "Truyện Kiều (Đoạn Trường Tân Thanh) của Nguyễn Du...",
  "key_facts": [
    "Tác giả: Nguyễn Du",
    "Số câu: 3254 câu thơ lục bát",
    "Thời gian: Đầu thế kỷ 19"
  ]
}
```

#### 3. Địa lý Việt Nam (Geography)
**Sources:**
- Wikipedia: Các tỉnh thành, sông ngòi, núi non
- Sách giáo khoa Địa lý

**Example data:**
```json
{
  "domain": "geography",
  "topic": "Sông Mekong",
  "content": "Sông Cửu Long (Mekong) chảy qua 9 tỉnh miền Tây...",
  "key_facts": [
    "Chiều dài tại VN: ~220 km",
    "9 cửa sông: Tiền Giang, Hậu Giang...",
    "Diện tích: ~40,000 km²"
  ]
}
```

#### 4. Chính trị & Pháp luật (Politics/Law)
**Sources:**
- Hiến pháp 2013
- Các luật quan trọng
- Wikipedia: Tổ chức nhà nước

**Example data:**
```json
{
  "domain": "politics",
  "topic": "Quốc hội Việt Nam",
  "content": "Quốc hội là cơ quan đại biểu cao nhất của nhân dân...",
  "key_facts": [
    "Nhiệm kỳ: 5 năm",
    "Số đại biểu: 500",
    "Vai trò: Lập hiến, lập pháp, giám sát"
  ]
}
```

### Data Volume Estimate

| Domain | Wikipedia Articles | Est. Chunks (512 tokens) | Est. Size |
|--------|-------------------|-------------------------|-----------|
| History | ~500 articles | ~5,000 chunks | ~10 MB |
| Culture | ~300 articles | ~3,000 chunks | ~6 MB |
| Geography | ~200 articles | ~2,000 chunks | ~4 MB |
| Politics | ~100 articles | ~1,000 chunks | ~2 MB |
| **TOTAL** | **~1,100 articles** | **~11,000 chunks** | **~22 MB** |

**Embeddings size**: 11,000 chunks × 768 dims × 4 bytes = ~33 MB
**FAISS index**: ~50 MB (with IVF compression)

**Total Vector DB size**: ~100 MB

---

## 🛠️ IMPLEMENTATION PLAN

### Phase 1: Data Collection (2-3 giờ)

#### Step 1.1: Wikipedia Crawler
```python
# modules/data_collection/wikipedia_crawler.py

import requests
from bs4 import BeautifulSoup

class VietnameseWikiCrawler:
    BASE_URL = "https://vi.wikipedia.org/wiki/"

    def __init__(self):
        self.session = requests.Session()

    def crawl_article(self, title: str) -> dict:
        """Crawl single Wikipedia article"""
        url = self.BASE_URL + title
        response = self.session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main content
        content = soup.find('div', {'id': 'mw-content-text'})
        paragraphs = content.find_all('p')
        text = '\n'.join([p.get_text() for p in paragraphs])

        return {
            'title': title,
            'url': url,
            'content': text,
            'domain': self._classify_domain(title)
        }

    def crawl_category(self, category: str, max_articles: int = 100):
        """Crawl all articles in a category"""
        # Implementation here
        pass
```

#### Step 1.2: Article Lists
```python
# data/article_lists.py

HISTORY_ARTICLES = [
    "Nhà_Lý", "Nhà_Trần", "Nhà_Lê", "Nhà_Nguyễn",
    "Lý_Công_Uẩn", "Trần_Hưng_Đạo", "Lê_Lợi", "Nguyễn_Huệ",
    "Cách_mạng_tháng_Tám", "Chiến_thắng_Điện_Biên_Phủ",
    # ... 500 articles
]

CULTURE_ARTICLES = [
    "Truyện_Kiều", "Nguyễn_Du", "Hồ_Chí_Minh_(thơ_văn)",
    "Chùa_Một_Cột", "Văn_Miếu_Quốc_Tử_Giám",
    "Ca_trù", "Hát_quan_họ", "Đờn_ca_tài_tử",
    # ... 300 articles
]

GEOGRAPHY_ARTICLES = [
    "Sông_Hồng", "Sông_Mekong", "Vịnh_Hạ_Long",
    "Đèo_Hải_Vân", "Núi_Phú_Sĩ_Việt_Nam",
    # ... 200 articles
]

POLITICS_ARTICLES = [
    "Quốc_hội_Việt_Nam", "Chính_phủ_Việt_Nam",
    "Hiến_pháp_Việt_Nam", "Đảng_Cộng_sản_Việt_Nam",
    # ... 100 articles
]
```

#### Step 1.3: Run Crawler
```bash
# Script to crawl all articles
python scripts/crawl_wikipedia.py \
  --domains history,culture,geography,politics \
  --output data/raw_articles.jsonl
```

**Expected output**: `data/raw_articles.jsonl` (~50 MB)

---

### Phase 2: Document Processing (1-2 giờ)

#### Step 2.1: Text Cleaning
```python
# modules/data_processing/text_cleaner.py

import re

class VietnameseTextCleaner:
    def clean(self, text: str) -> str:
        """Clean Vietnamese text"""
        # Remove citations [1], [2]
        text = re.sub(r'\[\d+\]', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters
        text = re.sub(r'[^\w\s\dÀ-ỹ.,!?;:\-()]', '', text)

        return text.strip()
```

#### Step 2.2: Document Chunking
```python
# modules/data_processing/chunker.py

class DocumentChunker:
    def __init__(self, chunk_size=512, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: dict) -> list:
        """Split document into chunks"""
        text = doc['content']
        chunks = []

        # Split by sentences
        sentences = self._split_sentences(text)

        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_len = len(sentence.split())

            if current_length + sentence_len > self.chunk_size:
                # Save current chunk
                chunks.append({
                    'text': ' '.join(current_chunk),
                    'metadata': {
                        'source': doc['title'],
                        'domain': doc['domain']
                    }
                })

                # Start new chunk with overlap
                current_chunk = current_chunk[-self.overlap:] + [sentence]
                current_length = len(' '.join(current_chunk).split())
            else:
                current_chunk.append(sentence)
                current_length += sentence_len

        return chunks

    def _split_sentences(self, text: str) -> list:
        """Split text into sentences"""
        return re.split(r'[.!?]+', text)
```

#### Step 2.3: Process All Documents
```python
# scripts/process_documents.py

from modules.data_processing.text_cleaner import VietnameseTextCleaner
from modules.data_processing.chunker import DocumentChunker
import json

def process_documents():
    cleaner = VietnameseTextCleaner()
    chunker = DocumentChunker(chunk_size=512, overlap=50)

    # Load raw articles
    with open('data/raw_articles.jsonl', 'r') as f:
        articles = [json.loads(line) for line in f]

    all_chunks = []
    for article in articles:
        # Clean text
        article['content'] = cleaner.clean(article['content'])

        # Chunk document
        chunks = chunker.chunk_document(article)
        all_chunks.extend(chunks)

    # Save chunks
    with open('data/processed_chunks.jsonl', 'w') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')

    print(f"Processed {len(all_chunks)} chunks from {len(articles)} articles")

if __name__ == '__main__':
    process_documents()
```

**Expected output**: `data/processed_chunks.jsonl` (~30 MB, 11,000 chunks)

---

### Phase 3: Embedding Generation (3-4 giờ)

#### Step 3.1: VNPT Embedding API Wrapper
```python
# modules/llm/embedding_client.py

import requests
import time

class VNPTEmbeddingClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vnpt.ai/v1/embeddings"

    def embed(self, text: str, retry=3) -> list:
        """Generate embedding for text"""
        for attempt in range(retry):
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"input": text}
                )

                if response.status_code == 200:
                    return response.json()['data'][0]['embedding']

                # Rate limit handling
                if response.status_code == 429:
                    print(f"Rate limit, waiting 60s...")
                    time.sleep(60)
                    continue

            except Exception as e:
                print(f"Error: {e}, retry {attempt+1}/{retry}")
                time.sleep(2)

        return None

    def embed_batch(self, texts: list, batch_size=10) -> list:
        """Embed multiple texts with batching"""
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]

            for text in batch:
                emb = self.embed(text)
                if emb:
                    embeddings.append(emb)
                time.sleep(0.1)  # Rate limit safety

            print(f"Progress: {i+batch_size}/{len(texts)}")

        return embeddings
```

#### Step 3.2: Generate Embeddings for All Chunks
```python
# scripts/generate_embeddings.py

from modules.llm.embedding_client import VNPTEmbeddingClient
import json
import numpy as np

def generate_embeddings():
    # Load API key
    with open('api-keys.json', 'r') as f:
        api_keys = json.load(f)

    client = VNPTEmbeddingClient(api_key=api_keys['embedding_api_key'])

    # Load chunks
    with open('data/processed_chunks.jsonl', 'r') as f:
        chunks = [json.loads(line) for line in f]

    print(f"Generating embeddings for {len(chunks)} chunks...")

    # Extract texts
    texts = [chunk['text'] for chunk in chunks]

    # Generate embeddings (with rate limit handling)
    embeddings = client.embed_batch(texts, batch_size=10)

    # Save embeddings
    np.save('data/embeddings.npy', np.array(embeddings))

    # Save metadata
    with open('data/chunk_metadata.jsonl', 'w') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk['metadata'], ensure_ascii=False) + '\n')

    print(f"✓ Saved {len(embeddings)} embeddings")

if __name__ == '__main__':
    generate_embeddings()
```

**Note**: Embedding API cũng có rate limit! Estimate:
- 11,000 chunks × 0.5s/chunk = ~1.5 giờ
- Với rate limit: có thể cần 3-4 giờ

**Expected output**:
- `data/embeddings.npy` (~33 MB)
- `data/chunk_metadata.jsonl` (~5 MB)

---

### Phase 4: FAISS Index Building (30 phút)

#### Step 4.1: Build FAISS Index
```python
# scripts/build_faiss_index.py

import faiss
import numpy as np

def build_index():
    # Load embeddings
    embeddings = np.load('data/embeddings.npy')

    print(f"Building FAISS index for {embeddings.shape[0]} vectors...")
    print(f"Dimension: {embeddings.shape[1]}")

    # Normalize vectors (for cosine similarity)
    faiss.normalize_L2(embeddings)

    # Build index
    dimension = embeddings.shape[1]

    # Option 1: Flat index (exact search, small dataset)
    index = faiss.IndexFlatIP(dimension)  # Inner Product = Cosine Similarity

    # Option 2: IVF index (faster, approximate search)
    # nlist = 100  # Number of clusters
    # quantizer = faiss.IndexFlatIP(dimension)
    # index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
    # index.train(embeddings)

    # Add vectors to index
    index.add(embeddings)

    # Save index
    faiss.write_index(index, 'data/faiss_index.bin')

    print(f"✓ FAISS index saved: data/faiss_index.bin")
    print(f"✓ Index size: {index.ntotal} vectors")

if __name__ == '__main__':
    build_index()
```

**Expected output**: `data/faiss_index.bin` (~50 MB)

---

### Phase 5: Retrieval Integration (1-2 giờ)

#### Step 5.1: Vector DB Manager
```python
# modules/vector_db/vector_db_manager.py

import faiss
import numpy as np
import json
from typing import List, Dict
from modules.llm.embedding_client import VNPTEmbeddingClient

class VectorDBManager:
    def __init__(
        self,
        index_path: str,
        metadata_path: str,
        embedding_client: VNPTEmbeddingClient
    ):
        self.index = faiss.read_index(index_path)
        self.embedding_client = embedding_client

        # Load metadata
        with open(metadata_path, 'r') as f:
            self.metadata = [json.loads(line) for line in f]

        print(f"✓ Loaded FAISS index: {self.index.ntotal} vectors")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        # Generate query embedding
        query_emb = self.embedding_client.embed(query)
        if query_emb is None:
            return []

        # Normalize
        query_vec = np.array([query_emb], dtype=np.float32)
        faiss.normalize_L2(query_vec)

        # Search
        scores, indices = self.index.search(query_vec, top_k)

        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'metadata': self.metadata[idx],
                    'score': float(score)
                })

        return results
```

#### Step 5.2: Update Pipeline to Use Vector DB
```python
# predict.py - Modified _handle_domain_question

def _handle_domain_question(
    self,
    question: str,
    choices: List[str],
    category: QuestionCategory
) -> str:
    """Handle domain-specific questions using Vector DB"""

    # NEW: Retrieve from Vector DB
    if hasattr(self, 'vector_db'):
        retrieved_docs = self.vector_db.search(question, top_k=3)

        if retrieved_docs:
            # Build context from retrieved docs
            context = "\n\n".join([
                f"Thông tin {i+1}: {doc['metadata']['text'][:200]}..."
                for i, doc in enumerate(retrieved_docs)
            ])

            # Try to answer directly from context
            answer = self._answer_from_context(question, choices, context)
            if answer:
                return answer

    # Fallback: Use simple facts (OLD way)
    base_prompt = self._build_domain_prompt(question, choices, category)
    augmented_prompt = augment_prompt_with_facts(question, base_prompt)

    # Use LLM only if needed
    response = self.llm.generate(augmented_prompt, model="small", temperature=0.3)
    answer = self._extract_answer(response, choices)
    return answer

def _answer_from_context(
    self,
    question: str,
    choices: List[str],
    context: str
) -> str:
    """Try to answer directly from retrieved context"""
    # Simple heuristic: check if choice text appears in context
    scores = []
    for i, choice in enumerate(choices):
        score = 0
        choice_lower = choice.lower()
        context_lower = context.lower()

        # Exact match
        if choice_lower in context_lower:
            score += 10

        # Word overlap
        choice_words = set(choice_lower.split())
        context_words = set(context_lower.split())
        overlap = len(choice_words & context_words)
        score += overlap

        scores.append((chr(65 + i), score))

    # If high confidence, return answer without LLM
    scores.sort(key=lambda x: x[1], reverse=True)
    if scores[0][1] >= 10:  # High confidence threshold
        print(f"  → Answered from context (no LLM needed)")
        return scores[0][0]

    return None  # Need LLM
```

#### Step 5.3: Update Main Pipeline Initialization
```python
# predict.py - SimplePipeline.__init__

def __init__(self):
    self.classifier = classifier
    self.llm = llm_client

    # Load Vector DB if exists
    try:
        from modules.vector_db.vector_db_manager import VectorDBManager
        from modules.llm.embedding_client import VNPTEmbeddingClient
        import json

        # Load API key for embeddings
        with open('api-keys.json', 'r') as f:
            api_keys = json.load(f)

        embedding_client = VNPTEmbeddingClient(
            api_key=api_keys.get('embedding_api_key', '')
        )

        self.vector_db = VectorDBManager(
            index_path='data/faiss_index.bin',
            metadata_path='data/chunk_metadata.jsonl',
            embedding_client=embedding_client
        )

        print("✓ Vector DB loaded successfully")
    except Exception as e:
        print(f"⚠ Vector DB not available: {e}")
        self.vector_db = None
```

---

## 📈 EXPECTED IMPACT

### API Call Reduction

#### Before Vector DB:
```
93 questions breakdown:
- Reading: 20 questions × 1 call = 20 calls
- Math: 15 questions × 1 call = 15 calls
- Domain: 58 questions × 1 call = 58 calls
----------------------------------------
Total: 93 API calls → HIT RATE LIMIT!
```

#### After Vector DB:
```
93 questions breakdown:
- Reading: 20 questions × 1 call = 20 calls
- Math: 15 questions × 1 call = 15 calls
- Domain: 58 questions × (20% need LLM) = 12 calls
  (80% answered from context directly)
----------------------------------------
Total: 47 API calls → KHÔNG HIT RATE LIMIT!

Giảm 50% API calls!
```

### Accuracy Improvement

| Category | Current | With Vector DB | Improvement |
|----------|---------|----------------|-------------|
| Reading | 80% | 80% | 0% (no change) |
| Math | 0% | 0% | 0% (LLM limitation) |
| History | 50% | **75%** | +25% |
| Culture | 60% | **80%** | +20% |
| Geography | 40% | **70%** | +30% |
| Politics | 100% | 100% | 0% |
| **Overall** | **60%** | **~75%** | **+15%** |

### Performance

| Metric | Current | With Vector DB |
|--------|---------|----------------|
| Processing Time | 8-10 min | 10-12 min (+2 min for retrieval) |
| API Calls | 93 calls | 47 calls (-50%) |
| Rate Limit Hit | Yes (60/hour) | No |
| Docker Size | 2.6 GB | 2.7 GB (+100 MB) |

---

## ⏱️ TIMELINE ESTIMATE

### Total Time: ~8-10 giờ

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| **1** | Data Collection | 2-3h | Internet, Wikipedia |
| **2** | Document Processing | 1-2h | Phase 1 |
| **3** | Embedding Generation | 3-4h | Phase 2, API quota |
| **4** | FAISS Index Building | 0.5h | Phase 3 |
| **5** | Integration | 1-2h | Phase 4 |
| **6** | Testing | 1h | All phases |

**Critical path**: Embedding generation (3-4h) do rate limit

### Parallel Tasks
- Có thể crawl data trong khi test code khác
- Document processing có thể chạy background
- Index building rất nhanh (30 phút)

---

## 📦 DOCKER IMAGE IMPACT

### Size Increase

```
Current Docker size: 2.6 GB

Adding Vector DB:
+ FAISS library: ~50 MB
+ Vector DB data: ~100 MB
+ Code overhead: ~10 MB
-----------------------
New Docker size: ~2.76 GB

Still well under 10 GB limit!
```

### Dockerfile Updates
```dockerfile
# Add to requirements.txt
faiss-cpu==1.7.4

# Add data files to Docker
COPY data/faiss_index.bin /code/data/
COPY data/chunk_metadata.jsonl /code/data/
COPY data/chunks.jsonl /code/data/
```

---

## ✅ PROS & CONS

### Pros
✅ **Giảm 50% API calls** → Tránh rate limit
✅ **Tăng accuracy lên ~75%** → Tốt hơn 15%
✅ **Độc lập hơn với API** → Ít phụ thuộc vào LLM
✅ **Có thể offline** → Answer từ context không cần API
✅ **Docker size OK** → Chỉ +100 MB

### Cons
❌ **Mất thời gian build** → 8-10 giờ total
❌ **Cần API quota cho embedding** → ~11,000 embeds
❌ **Tăng complexity** → Thêm data pipeline
❌ **Chậm hơn 2 phút** → Retrieval overhead

---

## 🎯 RECOMMENDATION

### Option A: Build Full Vector DB (Recommended)
**When**: Còn >= 1 ngày trước deadline
**Why**:
- Tăng accuracy lên ~75%
- Tránh rate limit hoàn toàn
- Professional solution

**Steps**:
1. Crawl Wikipedia (2-3h)
2. Process documents (1-2h)
3. Generate embeddings (3-4h) - Chạy overnight
4. Build index (30 min)
5. Integrate (1-2h)
6. Test (1h)

**Timeline**: 1 ngày (8-10 giờ)

---

### Option B: Minimal Vector DB (Quick Fix)
**When**: Còn < 1 ngày, cần fix rate limit nhanh
**Why**:
- Giảm được 30-40% API calls
- Nhanh hơn (3-4 giờ)
- Đủ để tránh rate limit

**Steps**:
1. Chỉ crawl TOP 200 articles quan trọng nhất
2. Chunk đơn giản (no overlap)
3. Generate embeddings (~2,000 embeds, 1-2h)
4. Build FAISS index
5. Integrate

**Timeline**: 3-4 giờ

---

### Option C: Không dùng Vector DB (Current)
**When**: Không có thời gian
**Why**:
- Hệ thống đã work (60% accuracy)
- Docker ready to submit

**Workaround for rate limit**:
- Chạy predict.py nhiều lần (incremental CSV đã fix)
- Đợi 1 giờ giữa các lần chạy
- Merge results manually

---

## 🚀 NEXT STEPS

Bạn muốn:

### A. Build Full Vector DB (Option A)
→ Tôi sẽ tạo full code cho 5 phases

### B. Build Minimal Vector DB (Option B)
→ Tôi sẽ tạo lightweight version

### C. Không build Vector DB
→ Giữ nguyên, submit Docker hiện tại

### D. Hỏi thêm về kế hoạch
→ Clarify bất kỳ phần nào

---

Bạn chọn option nào? (A/B/C/D)
