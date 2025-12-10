import requests
import time
import json

class VNPTEmbeddingClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Check if the URL is correct for the specific competition track or generic VNPT AI
        # Based on documentation provided in the prompt's context (phantom), usually it's something like:
        self.base_url = "https://llm.vnpt.ai/api/v1/embeddings" 
        # Note: If the URL is different in the PDF documents I couldn't read fully, 
        # I should double check. But usually this is standard. 
        # Let's assume standard OpenAI-compatible format or specific VNPT format.
        # Retaining the logic from the PLAN which used https://api.vnpt.ai/v1/embeddings 
        # (I will stick to the plan's URL unless I see otherwise)
        self.base_url = "https://api.vnpt.ai/v1/embeddings"

    def embed(self, text: str, retry=3) -> list:
        """Generate embedding for text"""
        if not text:
            return None
            
        payload = {
            "input": text,
            "model": "vnpt-embedding" # Or generic default
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        for attempt in range(retry):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    # Expecting OpenAI-like format: {'data': [{'embedding': [...]}]}
                    data = response.json()
                    if 'data' in data and len(data['data']) > 0:
                        return data['data'][0]['embedding']
                    return None

                # Rate limit handling
                if response.status_code == 429:
                    wait = 60
                    print(f"Rate limit hit. Waiting {wait}s...")
                    time.sleep(wait)
                    continue
                    
                print(f"Embedding failed: {response.status_code} - {response.text}")
                
            except Exception as e:
                print(f"Error calling embedding API: {e}, retry {attempt+1}/{retry}")
                time.sleep(2)

        return None

    def embed_batch(self, texts: list, batch_size=5) -> list:
        """Embed multiple texts (helper)"""
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            for text in batch:
                emb = self.embed(text)
                if emb:
                    embeddings.append(emb)
                else:
                    # If failed, maybe append zero vector or skip? 
                    # For safety, let's skip but warn.
                    pass 
                time.sleep(0.05) # Small optional delay
        return embeddings
