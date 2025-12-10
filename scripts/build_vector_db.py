import os
import sys
import json
import numpy as np
import faiss
import time
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_collection.wikipedia_crawler import VietnameseWikiCrawler
from modules.data_processing.text_cleaner import VietnameseTextCleaner
from modules.data_processing.chunker import DocumentChunker
from modules.llm.api_client import VNPTClient

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Topics to crawl (as examples, can be expanded)
TOPICS = {
    "history": [
        "Lịch sử Việt Nam", "Nhà Lý", "Nhà Trần", "Lê Lợi", "Quang Trung", 
        "Chiến tranh Việt Nam", "Cách mạng tháng Tám"
    ],
    "culture": [
        "Văn hóa Việt Nam", "Tết Nguyên Đán", "Truyện Kiều", "Nhã nhạc cung đình Huế",
        "Áo dài", "Phở"
    ],
    "geography": [
        "Địa lý Việt Nam", "Hà Nội", "Thành phố Hồ Chí Minh", "Vịnh Hạ Long", 
        "Sông Mê Kông", "Dãy Trường Sơn"
    ],
    "politics": [
        "Chính trị Việt Nam", "Quốc hội Việt Nam", "Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam"
    ]
}

def main():
    print("🚀 Starting Vector DB Build Process...")
    
    # 1. Crawl Data
    crawler = VietnameseWikiCrawler()
    raw_articles = []
    
    print("\n📦 Step 1: Crawling Wikipedia...")
    for category, topics in TOPICS.items():
        print(f"  Category: {category}")
        for topic in tqdm(topics, desc=f"Crawling {category}"):
            article = crawler.crawl_article(topic)
            if article:
                article['domain'] = category
                raw_articles.append(article)
                time.sleep(1) # Polite delay
    
    print(f"  ✓ Collected {len(raw_articles)} articles")
    
    # Save raw for debug
    with open(os.path.join(DATA_DIR, 'raw_articles.json'), 'w', encoding='utf-8') as f:
        json.dump(raw_articles, f, ensure_ascii=False, indent=2)

    # 2. Process & Chunk
    print("\n✂️ Step 2: Processing and Chunking...")
    cleaner = VietnameseTextCleaner()
    chunker = DocumentChunker(chunk_size=300, overlap=50) # Smaller chunks for better context
    
    all_chunks = []
    
    for article in raw_articles:
        # Clean
        article['content'] = cleaner.clean(article['content'])
        
        # Chunk
        chunks = chunker.chunk_document(article)
        for chunk in chunks:
            chunk['metadata']['domain'] = article['domain']
            all_chunks.append(chunk)
            
    print(f"  ✓ Generated {len(all_chunks)} chunks")
    
    # Save chunks metadata
    with open(os.path.join(DATA_DIR, 'chunk_metadata.jsonl'), 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')

    # 3. Generate Embeddings
    print("\n🧠 Step 3: Generating Embeddings...")
    client = VNPTClient()
    
    embeddings = []
    # Batch processing could be done here, but let's do simple loop for safety/rate limit
    # To speed up, we can use a small batch size if API permits, but 'embed' is single.
    # We'll use simple loop.
    
    valid_chunks = []
    
    # Check if we already have embeddings to resume? (Skip for simplicity now)
    
    for i, chunk in enumerate(tqdm(all_chunks, desc="Embedding")):
        text = chunk['text']
        emb = client.embed(text)
        
        if emb and len(emb) > 0:
            embeddings.append(emb)
            valid_chunks.append(chunk)
        else:
            print(f"  ⚠ Failed to embed chunk {i}")
            
        time.sleep(0.1) # Avoid rate limit
        
    embeddings_np = np.array(embeddings).astype('float32')
    
    # Update metadata to match valid embeddings
    with open(os.path.join(DATA_DIR, 'chunk_metadata.jsonl'), 'w', encoding='utf-8') as f:
        for chunk in valid_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
            
    print(f"  ✓ Generated {len(embeddings)} embeddings")

    # 4. Build FAISS Index
    print("\n🔍 Step 4: Building FAISS Index...")
    if len(embeddings) > 0:
        dimension = embeddings_np.shape[1]
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings_np)
        
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings_np)
        
        faiss.write_index(index, os.path.join(DATA_DIR, 'faiss_index.bin'))
        print(f"  ✓ Index saved to {os.path.join(DATA_DIR, 'faiss_index.bin')}")
    else:
        print("  ❌ No embeddings generated, skipping index build.")

    print("\n✨ Done! Vector DB is ready.")

if __name__ == "__main__":
    main()
