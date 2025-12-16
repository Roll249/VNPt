"""
Simple Knowledge Retriever for Compulsory Questions
Uses keyword matching on crawled knowledge base
"""
import json
import os
import re
from typing import List, Dict, Tuple

class SimpleRetriever:
    """Simple keyword-based retriever for knowledge base"""
    
    def __init__(self, knowledge_path: str = "data/crawled/merged_knowledge.jsonl"):
        self.documents = []
        self.load_knowledge(knowledge_path)
    
    def load_knowledge(self, path: str):
        """Load knowledge base from JSONL"""
        if not os.path.exists(path):
            print(f"⚠ Knowledge base not found: {path}")
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        doc = json.loads(line)
                        self.documents.append(doc)
                    except:
                        pass
        
        print(f"  📚 Loaded {len(self.documents)} documents for retrieval")
    
    def tokenize(self, text: str) -> List[str]:
        """Simple Vietnamese tokenization"""
        # Remove punctuation and split
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        # Filter short tokens
        return [t for t in tokens if len(t) > 2]
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict]]:
        """Search for relevant documents using keyword matching"""
        if not self.documents:
            return []
        
        query_tokens = set(self.tokenize(query))
        if not query_tokens:
            return []
        
        results = []
        for doc in self.documents:
            # Combine title and content for matching
            doc_text = doc.get('title', '') + ' ' + doc.get('content', '')
            doc_tokens = set(self.tokenize(doc_text))
            
            # Calculate overlap score
            overlap = len(query_tokens & doc_tokens)
            if overlap > 0:
                # Normalize by query length
                score = overlap / len(query_tokens)
                results.append((score, doc))
        
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        return results[:top_k]
    
    def get_context(self, query: str, max_chars: int = 2000) -> str:
        """Get context string for a query"""
        results = self.search(query, top_k=3)
        
        if not results:
            return ""
        
        context_parts = []
        total_chars = 0
        
        for score, doc in results:
            title = doc.get('title', '')
            content = doc.get('content', '')[:500]  # Limit per doc
            
            part = f"[{title}]: {content}"
            if total_chars + len(part) > max_chars:
                break
            
            context_parts.append(part)
            total_chars += len(part)
        
        return '\n\n'.join(context_parts)


# Global instance for easy import
_retriever = None

def get_retriever() -> SimpleRetriever:
    """Get or create global retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = SimpleRetriever()
    return _retriever


def retrieve_context(query: str, max_chars: int = 2000) -> str:
    """Helper function to retrieve context for a query"""
    retriever = get_retriever()
    return retriever.get_context(query, max_chars)


if __name__ == "__main__":
    # Test the retriever
    retriever = SimpleRetriever()
    
    test_queries = [
        "Điện Biên Phủ",
        "Hiến pháp Việt Nam",
        "Sông Mê Kông",
        "Quan họ Bắc Ninh",
    ]
    
    for q in test_queries:
        print(f"\n🔍 Query: {q}")
        results = retriever.search(q, top_k=2)
        for score, doc in results:
            print(f"  [{score:.2f}] {doc['title']}")
