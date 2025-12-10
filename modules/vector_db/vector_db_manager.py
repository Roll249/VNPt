import faiss
import numpy as np
import json
import os
from typing import List, Dict
try:
    from modules.llm.api_client import VNPTClient
except ImportError:
    # Fallback for relative import if run as script
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from modules.llm.api_client import VNPTClient

class VectorDBManager:
    def __init__(
        self,
        index_path: str,
        metadata_path: str,
        embedding_client: VNPTClient
    ):
        self.embedding_client = embedding_client
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []
        
        self.load_db()

    def load_db(self):
        """Load FAISS index and metadata"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = [json.loads(line) for line in f]
                print(f"✓ Loaded Vector DB: {self.index.ntotal} vectors")
            except Exception as e:
                print(f"⚠ Failed to load Vector DB: {e}")
                self.index = None
        else:
            print(f"⚠ Vector DB files not found at {self.index_path}")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant documents"""
        if not self.index or not self.embedding_client:
            return []

        # Generate query embedding
        query_emb = self.embedding_client.embed(query)
        if query_emb is None:
            return []

        # Normalize for cosine similarity (if index was trained on normalized vectors)
        # Assuming we normalize at build time, we must normalize query too.
        query_vec = np.array([query_emb], dtype=np.float32)
        faiss.normalize_L2(query_vec)

        # Search
        scores, indices = self.index.search(query_vec, top_k)

        # Format results
        results = []
        if len(scores) > 0 and len(indices) > 0:
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and idx < len(self.metadata):
                    results.append({
                        'metadata': self.metadata[idx],
                        'score': float(score)
                    })

        return results
