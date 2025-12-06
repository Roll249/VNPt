# YÊU CẦU VỀ DỮ LIỆU CHO DỰ ÁN VNPT AI HACKATHON

## 📋 TỔNG QUAN NHU CẦU

Dựa trên phân tích validation set và test set, dự án cần xây dựng **Vector Database** chứa kiến thức chính xác, chính thống về Việt Nam để hỗ trợ hệ thống RAG trả lời các câu hỏi.

---

## 🎯 PHÂN TÍCH THEO LOẠI CÂU HỎI

### 1. CÂU HỎI VỀ LỊCH SỬ VIỆT NAM (30-35% tổng câu hỏi)

#### Nhu cầu kiến thức:
- **Các triều đại**: Lý, Trần, Lê, Nguyễn, v.v.
  - Tên các vua, thời gian trị vì
  - Sự kiện lịch sử quan trọng
  - Thành tựu văn hóa, chính trị

- **Cuộc kháng chiến**:
  - Kháng chiến chống Pháp (1945-1954)
  - Kháng chiến chống Mỹ (1954-1975)
  - Các trận đánh lịch sử (Điện Biên Phủ, Hồ Chí Minh, v.v.)
  - Các anh hùng dân tộc

- **Lịch sử hiện đại**:
  - Thống nhất đất nước (1975)
  - Đổi mới (1986)
  - Hội nhập quốc tế

#### Nguồn dữ liệu đề xuất:
```
1. Wikipedia tiếng Việt
   - Danh mục: Lịch sử Việt Nam
   - Danh mục: Các triều đại Việt Nam
   - Danh mục: Kháng chiến chống Pháp
   - Danh mục: Kháng chiến chống Mỹ
   - URL: https://vi.wikipedia.org/wiki/Danh_mục:Lịch_sử_Việt_Nam

2. Sách giáo khoa (open source)
   - Lịch sử lớp 10, 11, 12
   - Nếu có bản điện tử công khai

3. Trang chính thức
   - Bảo tàng Lịch sử Việt Nam
   - Viện Nghiên cứu Lịch sử
```

#### Ước lượng khối lượng:
- **Số lượng documents**: ~500-800 bài viết
- **Tổng text**: ~2-3 triệu từ
- **Sau chunking**: ~5,000-8,000 chunks

---

### 2. CÂU HỎI VỀ ĐỊA LÝ VIỆT NAM (15-20%)

#### Nhu cầu kiến thức:
- **Địa lý tự nhiên**:
  - Các tỉnh/thành phố (63 tỉnh)
  - Sông ngòi (Sông Hồng, Sông Cửu Long, v.v.)
  - Núi non (Phan Xi Păng, Trường Sơn, v.v.)
  - Khí hậu, thời tiết

- **Địa lý kinh tế**:
  - Vùng kinh tế (Đông Nam Bộ, Đồng bằng sông Cửu Long, v.v.)
  - Sản xuất nông nghiệp
  - Công nghiệp, thương mại

- **Địa lý hành chính**:
  - Cơ cấu hành chính
  - Thủ phủ các tỉnh
  - Dân số, diện tích

#### Nguồn dữ liệu đề xuất:
```
1. Wikipedia tiếng Việt
   - Danh mục: Địa lý Việt Nam
   - Danh mục: Tỉnh thành Việt Nam
   - 63 bài viết về các tỉnh/thành

2. Tổng cục Thống kê (GSO)
   - https://www.gso.gov.vn (nếu có dữ liệu công khai)
   - Niên giám thống kê

3. OpenStreetMap Vietnam
   - Dữ liệu bản đồ mở
```

#### Ước lượng khối lượng:
- **Số lượng documents**: ~200-300 bài viết
- **Tổng text**: ~800k-1.2M từ
- **Sau chunking**: ~2,000-3,000 chunks

---

### 3. CÂU HỎI VỀ VĂN HÓA VIỆT NAM (20-25%)

#### Nhu cầu kiến thức:
- **Văn hóa truyền thống**:
  - Lễ hội (Tết, Lễ hội Hùng Vương, v.v.)
  - Tập quán, phong tục
  - Tín ngưỡng, tôn giáo
  - Nghề thủ công truyền thống

- **Văn học nghệ thuật**:
  - Tác giả nổi tiếng (Nguyễn Du, Hồ Xuân Hương, v.v.)
  - Tác phẩm văn học (Truyện Kiều, v.v.)
  - Ca dao, tục ngữ
  - Nghệ thuật truyền thống (tuồng, chèo, cải lương)

- **Ẩm thực**:
  - Món ăn đặc trưng
  - Đặc sản vùng miền

- **Di sản văn hóa**:
  - Di sản thế giới UNESCO tại VN
  - Danh lam thắng cảnh

#### Nguồn dữ liệu đề xuất:
```
1. Wikipedia tiếng Việt
   - Danh mục: Văn hóa Việt Nam
   - Danh mục: Văn học Việt Nam
   - Danh mục: Lễ hội Việt Nam
   - Danh mục: Ẩm thực Việt Nam

2. Wikisource tiếng Việt
   - Văn bản văn học cổ điển
   - Ca dao, tục ngữ

3. UNESCO Vietnam
   - Danh sách di sản thế giới
```

#### Ước lượng khối lượng:
- **Số lượng documents**: ~400-600 bài viết
- **Tổng text**: ~1.5-2M từ
- **Sau chunking**: ~4,000-6,000 chunks

---

### 4. CÂU HỎI VỀ CHÍNH TRỊ - PHÁP LUẬT VIỆT NAM (10-15%)

#### Nhu cầu kiến thức:
- **Hệ thống chính trị**:
  - Đảng Cộng sản Việt Nam
  - Quốc hội
  - Chính phủ
  - Tòa án, Viện kiểm sát
  - Chủ tịch nước

- **Hiến pháp**:
  - Hiến pháp 2013
  - Các quyền cơ bản của công dân

- **Pháp luật**:
  - Luật quan trọng (Dân sự, Hình sự, Lao động, v.v.)
  - Nghị định, Thông tư
  - Quy định hành chính

- **Quan hệ quốc tế**:
  - ASEAN
  - Liên hợp quốc
  - Quan hệ song phương

#### Nguồn dữ liệu đề xuất:
```
1. Wikipedia tiếng Việt
   - Danh mục: Chính trị Việt Nam
   - Hiến pháp Việt Nam

2. Cổng thông tin điện tử Chính phủ
   - https://chinhphu.vn
   - Văn bản pháp luật (công khai)

3. Thư viện pháp luật
   - https://thuvienphapluat.vn (nếu được phép)
   - Tóm tắt các luật quan trọng
```

#### Ước lượng khối lượng:
- **Số lượng documents**: ~150-250 bài viết
- **Tổng text**: ~600k-1M từ
- **Sau chunking**: ~1,500-2,500 chunks

---

### 5. CÂU HỎI TOÁN HỌC & TƯ DUY LOGIC (15-20%)

#### Nhu cầu kiến thức:
- **Toán học cơ bản**:
  - Đại số (phương trình, hệ phương trình)
  - Hình học (diện tích, thể tích, góc, v.v.)
  - Lượng giác
  - Xác suất, thống kê
  - Tổ hợp

- **Logic**:
  - Suy luận logic
  - Bài toán đố
  - Tư duy phản biện

#### Đặc điểm:
- **KHÔNG CẦN Vector Database** cho loại này
- Cần xử lý bằng **Math Solver** với:
  - Chain-of-thought prompting
  - Step-by-step reasoning
  - Calculator integration nếu cần

#### Nguồn tham khảo (optional):
```
1. Khan Academy (tiếng Việt nếu có)
2. Sách giáo khoa Toán
3. Few-shot examples cho prompt
```

---

### 6. CÂU HỎI ĐỌC HIỂU VÀN BẢN DÀI (10-15%)

#### Đặc điểm:
- **ĐÃ CÓ CONTEXT** trong câu hỏi
- **KHÔNG CẦN Vector Database**
- Chỉ cần LLM đọc hiểu và trích xuất thông tin

#### Ví dụ từ validation set:
```
Câu val_0001: Có đoạn text dài về "Khỉ thí nghiệm"
→ Không cần retrieve, chỉ cần đọc hiểu
```

---

### 7. CÂU HỎI CẦN TỪ CHỐI (5-10%)

#### Nhu cầu:
- **Rule-based detection** cho các câu:
  - Vi phạm pháp luật
  - Gian lận, lừa đảo
  - Trốn thuế
  - Hành vi phi đạo đức

#### Không cần database, cần:
```
1. Danh sách keywords từ chối:
   - "trốn", "tránh", "gian lận", "lừa đảo"
   - "vi phạm", "bất hợp pháp"
   - Context về hành vi sai trái

2. LLM classification:
   - Prompt LLM phát hiện intent xấu
   - Safety filter
```

---

## 📊 TỔNG HỢP NHU CẦU DỮ LIỆU

### Database cần xây dựng:

| Lĩnh vực | Documents | Text (words) | Chunks | Độ ưu tiên |
|----------|-----------|--------------|---------|------------|
| Lịch sử | 500-800 | 2M-3M | 5k-8k | ⭐⭐⭐⭐⭐ |
| Văn hóa | 400-600 | 1.5M-2M | 4k-6k | ⭐⭐⭐⭐⭐ |
| Địa lý | 200-300 | 800k-1.2M | 2k-3k | ⭐⭐⭐⭐ |
| Chính trị | 150-250 | 600k-1M | 1.5k-2.5k | ⭐⭐⭐ |

**TỔNG CỘNG**:
- **Documents**: ~1,250-1,950 bài viết
- **Text**: ~4.9M-7.2M từ (tiếng Việt)
- **Chunks**: ~12,500-19,500 chunks (với chunk size ~512 tokens)
- **Embeddings**: ~12,500-19,500 vectors

### Không cần database:
- ❌ Toán học & Logic (dùng Math Solver)
- ❌ Đọc hiểu (có context sẵn)
- ❌ Refusal questions (dùng rules + classifier)

---

## 🌐 NGUỒN DỮ LIỆU CHI TIẾT

### 1. Wikipedia tiếng Việt (Primary Source)

#### Ưu điểm:
- ✅ Dữ liệu mở, license CC-BY-SA
- ✅ Chất lượng cao, được kiểm duyệt
- ✅ Cập nhật thường xuyên
- ✅ Có API để crawl

#### Cách crawl:
```python
import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia(
    language='vi',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

# Categories to crawl
categories = [
    'Lịch_sử_Việt_Nam',
    'Địa_lý_Việt_Nam',
    'Văn_hóa_Việt_Nam',
    'Chính_trị_Việt_Nam',
    'Văn_học_Việt_Nam',
    'Các_tỉnh_thành_Việt_Nam',
    'Di_sản_thế_giới_tại_Việt_Nam'
]

# Crawl all pages in categories
for cat in categories:
    # Get all pages
    # Process and save
```

#### Ước lượng:
- **Số trang**: ~1,500-2,000 pages
- **Thời gian crawl**: 2-3 giờ với rate limiting
- **Storage**: ~500MB-1GB raw text

---

### 2. Wikisource tiếng Việt (Văn học cổ điển)

#### Nội dung:
- Văn bản văn học Việt Nam cổ điển
- Ca dao, tục ngữ
- Tác phẩm kinh điển

#### URL:
```
https://vi.wikisource.org/
```

#### Ước lượng:
- **Số văn bản**: ~100-200
- **Thời gian crawl**: 30-60 phút
- **Storage**: ~50-100MB

---

### 3. Wikidata tiếng Việt (Structured Knowledge)

#### Nội dung:
- Dữ liệu có cấu trúc (structured)
- Thông tin về người, địa điểm, sự kiện
- Có thể dùng để enrich context

#### URL:
```
https://www.wikidata.org/
```

---

### 4. Common Crawl - Vietnamese subset (Optional)

#### Nội dung:
- Web crawl lớn, có phần tiếng Việt
- Chất lượng không đồng đều
- Cần filter kỹ

#### Cân nhắc:
- ⚠️ Chất lượng thấp
- ⚠️ Noise nhiều
- ⚠️ Cần xử lý nặng

**Khuyến nghị**: Không dùng trừ khi thiếu data

---

### 5. Vietnamese Books Corpus (Nếu có)

#### Nguồn:
- Sách điện tử open source
- Project Gutenberg Vietnamese
- Free ebooks

#### Cân nhắc:
- ⚠️ Cần kiểm tra license
- ⚠️ Chất lượng OCR

---

### 6. Government Websites (Chính phủ VN)

#### Nguồn:
```
1. Cổng TTĐT Chính phủ: https://chinhphu.vn
2. Tổng cục Thống kê: https://gso.gov.vn
3. Bộ Văn hóa: https://bvhttdl.gov.vn
```

#### Cân nhắc:
- ⚠️ Cần kiểm tra robots.txt
- ⚠️ Rate limiting
- ⚠️ Chỉ lấy thông tin công khai

---

### 7. Educational Resources

#### Nguồn:
```
1. MOET - Bộ GD&ĐT (nếu có open data)
2. Sách giáo khoa điện tử (nếu được phép)
```

---

## 🛠️ CHIẾN LƯỢC THU THẬP DỮ LIỆU

### Phase 1: Core Data (Ngày 1-2)
**Mục tiêu**: 70% volume, 90% quality

1. **Wikipedia Categories** (Priority 1):
   ```
   - Lịch sử Việt Nam (500 pages)
   - Văn hóa Việt Nam (400 pages)
   - Địa lý Việt Nam (200 pages)
   - Chính trị Việt Nam (150 pages)
   ```

2. **63 Tỉnh/Thành phố**:
   ```
   - 63 bài viết chi tiết về mỗi tỉnh
   - Thông tin: lịch sử, địa lý, kinh tế, văn hóa
   ```

**Output**: ~1,250 documents, ~5M words

---

### Phase 2: Supplementary Data (Ngày 3)
**Mục tiêu**: 25% volume, coverage tốt

1. **Wikisource**:
   - Văn học cổ điển
   - Ca dao, tục ngữ

2. **Specific Topics**:
   - Di sản UNESCO tại VN
   - Các triều đại chi tiết
   - Lễ hội truyền thống

**Output**: +300 documents, +1M words

---

### Phase 3: Specialized Data (Ngày 3, nếu còn thiếu)
**Mục tiêu**: 5% volume, fill gaps

1. **Identified Gaps** từ validation set:
   - Topics chưa có trong Wikipedia
   - Câu hỏi bị sai nhiều

2. **Manual Collection**:
   - Search Google cho topics cụ thể
   - Lấy từ nguồn đáng tin cậy

**Output**: +100 documents, +500k words

---

## 📐 YÊU CẦU CHẤT LƯỢNG DỮ LIỆU

### 1. Độ chính xác (Accuracy)
- ✅ **Must**: Thông tin chính xác, có nguồn gốc rõ ràng
- ✅ **Must**: Không có thông tin sai lệch
- ✅ **Must**: Ưu tiên nguồn chính thống (Wikipedia, Gov sites)

### 2. Độ phủ (Coverage)
- ✅ Bao phủ tất cả topics trong validation set
- ✅ Có depth đủ sâu cho mỗi topic
- ✅ Balance giữa các lĩnh vực

### 3. Độ mới (Freshness)
- ✅ Thông tin cập nhật (Wikipedia thường mới)
- ✅ Ưu tiên articles được update gần đây

### 4. Chất lượng văn bản (Text Quality)
- ✅ Tiếng Việt chuẩn
- ✅ Không có lỗi chính tả nghiêm trọng
- ✅ Cấu trúc rõ ràng

---

## 🗃️ CẤU TRÚC LƯU TRỮ

### Raw Data Format:
```json
{
  "doc_id": "wiki_vietnam_history_001",
  "title": "Lịch sử Việt Nam",
  "url": "https://vi.wikipedia.org/wiki/Lịch_sử_Việt_Nam",
  "source": "wikipedia_vi",
  "category": "history",
  "content": "Lịch sử Việt Nam là...",
  "crawled_date": "2025-12-06",
  "language": "vi",
  "metadata": {
    "word_count": 5432,
    "char_count": 28901,
    "last_updated": "2024-11-15"
  }
}
```

### Processed Data Format:
```json
{
  "chunk_id": "chunk_001_0001",
  "doc_id": "wiki_vietnam_history_001",
  "chunk_index": 1,
  "content": "...",
  "metadata": {
    "source": "wikipedia_vi",
    "category": "history",
    "title": "Lịch sử Việt Nam",
    "section": "Thời kỳ Bắc thuộc"
  }
}
```

---

## 🔄 PIPELINE XỬ LÝ DỮ LIỆU

### Step 1: Crawling
```python
# Input: List of URLs/Categories
# Output: raw_data/*.json
# Time: 2-3 hours
```

### Step 2: Cleaning
```python
# Input: raw_data/*.json
# Process:
#   - Remove HTML tags
#   - Fix encoding issues
#   - Remove noise (navigation, footer, etc.)
#   - Normalize Vietnamese (diacritics)
# Output: cleaned_data/*.json
# Time: 1 hour
```

### Step 3: Chunking
```python
# Input: cleaned_data/*.json
# Process:
#   - Split by paragraphs/sections
#   - Target chunk size: 400-512 tokens
#   - Overlap: 50-100 tokens
#   - Preserve context
# Output: chunks/*.json
# Time: 30 minutes
```

### Step 4: Embedding
```python
# Input: chunks/*.json
# Process:
#   - Call VNPT Embedding API (500 req/min)
#   - Batch processing
#   - Rate limiting
# Output: embeddings/*.npy
# Time: 30-60 minutes (for 15k chunks)
```

### Step 5: Indexing
```python
# Input: embeddings/*.npy + chunks/*.json
# Process:
#   - Build FAISS index
#   - Save metadata
# Output: vector_db/index.faiss + metadata.json
# Time: 10 minutes
```

**TOTAL TIME**: ~4-6 hours for full pipeline

---

## 📏 CHUNKING STRATEGY

### Recommended Parameters:
```python
CHUNK_SIZE = 512 tokens (~400 words Vietnamese)
OVERLAP = 100 tokens (~80 words)
MIN_CHUNK_SIZE = 100 tokens
MAX_CHUNK_SIZE = 700 tokens
```

### Rationale:
- 512 tokens: Balance between context và retrieval precision
- Overlap: Tránh mất context giữa các chunks
- Min/Max: Tránh chunks quá nhỏ/lớn

### Chunking Methods:
1. **Paragraph-based** (Preferred):
   - Chia theo đoạn văn
   - Giữ nguyên semantic units

2. **Sentence-based**:
   - Chia theo câu
   - Tốt cho Q&A ngắn

3. **Section-based**:
   - Chia theo sections (h2, h3)
   - Tốt cho documents dài

**Recommendation**: Paragraph-based với overlap

---

## 🎯 METRICS ĐÁNH GIÁ DATA QUALITY

### Before Embedding:
```
1. Coverage Score:
   - % validation questions có liên quan đến data
   - Target: >90%

2. Diversity Score:
   - Số topics unique
   - Distribution across categories

3. Quality Score:
   - Manual review 100 random docs
   - Check accuracy, clarity
```

### After Embedding:
```
1. Retrieval Success Rate:
   - % validation questions retrieve được relevant docs
   - Target: >85%

2. Average Relevance Score:
   - Manual score top-5 docs cho 50 questions
   - Target: >4.0/5.0

3. Retrieval Time:
   - Average time per query
   - Target: <500ms
```

---

## ⚠️ RỦI RO & GIẢI PHÁP

### Rủi ro 1: Không đủ dữ liệu cho một số topics
**Giải pháp**:
- Xác định gaps sớm qua validation set
- Targeted crawling cho topics thiếu
- Manual collection nếu cần

### Rủi ro 2: Dữ liệu chất lượng thấp
**Giải pháp**:
- Chỉ crawl từ nguồn uy tín
- Quality check sau crawl
- Filter out low-quality docs

### Rủi ro 3: Embedding API quota hết
**Giải pháp**:
- Batch processing thông minh
- Cache embeddings
- Reuse embeddings nếu rebuild

### Rủi ro 4: Dữ liệu vi phạm license
**Giải pháp**:
- Chỉ dùng dữ liệu mở (Wikipedia, CC-BY)
- Document nguồn gốc rõ ràng
- Tránh scrape websites thương mại

---

## 📋 CHECKLIST THU THẬP DỮ LIỆU

### Trước khi crawl:
- [ ] Đã đọc robots.txt của websites
- [ ] Đã kiểm tra license
- [ ] Đã setup rate limiting
- [ ] Đã có error handling

### Trong quá trình:
- [ ] Monitor progress
- [ ] Check quality samples
- [ ] Log errors và skipped pages

### Sau khi crawl:
- [ ] Verify số lượng documents
- [ ] Check data quality (sample)
- [ ] Test retrieval trên validation set
- [ ] Document data sources

---

## 📊 DELIVERABLES

### Files cần tạo:
1. `data_sources.json`: List tất cả nguồn dữ liệu
2. `raw_data/`: Raw documents (JSON)
3. `processed_data/`: Cleaned documents (JSON)
4. `chunks/`: Chunked data (JSON)
5. `vector_db/`: FAISS index + metadata
6. `data_stats.json`: Thống kê về data

### Documentation:
1. `DATA_COLLECTION.md`: Process đã thực hiện
2. `DATA_SOURCES.md`: Nguồn dữ liệu chi tiết
3. `DATA_STATS.md`: Thống kê, metrics

---

## 🚀 QUICK START COMMANDS

### 1. Crawl Wikipedia:
```bash
python crawlers/wikipedia_crawler.py \
  --categories "Lịch_sử_Việt_Nam,Văn_hóa_Việt_Nam,Địa_lý_Việt_Nam" \
  --output raw_data/wikipedia/
```

### 2. Clean data:
```bash
python data_processing/clean_data.py \
  --input raw_data/ \
  --output cleaned_data/
```

### 3. Chunk data:
```bash
python data_processing/chunk_data.py \
  --input cleaned_data/ \
  --output chunks/ \
  --chunk_size 512 \
  --overlap 100
```

### 4. Build vector DB:
```bash
python vector_db/build_index.py \
  --input chunks/ \
  --output vector_db/ \
  --embedding_model vnptai_hackathon_embedding
```

### 5. Test retrieval:
```bash
python vector_db/test_retrieval.py \
  --index vector_db/index.faiss \
  --query "Ai là vị vua đầu tiên của nhà Lý?"
```

---

**Ước lượng tổng thời gian**: 4-6 giờ cho full pipeline
**Ước lượng storage**: ~2-3GB (raw + processed + embeddings)
**Ước lượng API calls**: ~15,000 embedding calls

---

**Ngày tạo**: 06/12/2025
