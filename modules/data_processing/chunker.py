import re

class DocumentChunker:
    def __init__(self, chunk_size=512, overlap=50):
        """
        Args:
            chunk_size: Target size of chunk (in words roughly, or generic token estimation)
            overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: dict) -> list:
        """
        Split document into chunks.
        doc: {'title': str, 'content': str, ...}
        """
        text = doc['content']
        if not text:
            return []

        chunks = []
        
        # Split into sentences (simple regex for Vietnamese)
        # Note: This is an approximation. 
        # Using positive lookbehind to keep the delimiter? No, split usually removes it.
        # Let's use a simpler approach: split by typical end marks followed by space.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            # Estimate length by words (approximate tokens)
            words = sentence.split()
            sentence_len = len(words)
            
            if current_length + sentence_len > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'source': doc['title'],
                        'url': doc.get('url', ''),
                        # 'domain': doc.get('domain', 'general') # Optional
                    }
                })
                
                # Start new chunk with overlap
                # Overlap logic: keep last 'overlap' words? Or last few sentences?
                # Simple sliding window by sentences is harder to measure by words strictly.
                # Let's just keep the last sentence if it fits, or clear if too big.
                
                # Better overlap: keep enough sentences from end of previous chunk 
                # to meet overlap word count.
                overlap_buffer = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    s_len = len(s.split())
                    if overlap_len + s_len <= self.overlap:
                        overlap_buffer.insert(0, s)
                        overlap_len += s_len
                    else:
                        break
                
                current_chunk = list(overlap_buffer)
                current_length = overlap_len

            current_chunk.append(sentence)
            current_length += sentence_len
            
        # Add last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'source': doc['title'],
                    'url': doc.get('url', '')
                }
            })
            
        return chunks
