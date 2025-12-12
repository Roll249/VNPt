"""
VNPT AI API Client - Lightweight HTTP client for LLM APIs
"""
import requests
import time
import json
from typing import Dict, List, Optional, Any
import sys
import os

# Custom exception for rate limiting
class RateLimitException(Exception):
    """Raised when API rate limit is hit"""
    pass

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.api_config import api_config


class VNPTClient:
    """Client for VNPT AI APIs"""

    def __init__(self):
        self.config = api_config
        self.session = requests.Session()  # Reuse connections
        self.cache_file = "api_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, str]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _get_cache_key(self, messages: List[Dict], model: str) -> str:
        """Generate cache key from messages and model"""
        # Create a stable string representation
        return f"{model}:{json.dumps(messages, sort_keys=True)}"

    def retry_api_call(max_retries=10):
        """Retry decorator with exponential backoff"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        result = func(*args, **kwargs)
                        if result and len(str(result).strip()) > 0:
                            time.sleep(0.5)  # Small delay after success
                            return result
                        # Empty result, retry
                        if attempt < max_retries - 1:
                            wait = 2 ** attempt
                            print(f"  ⚠ Empty response, retry in {wait}s...")
                            time.sleep(wait)
                    except requests.exceptions.HTTPError as e:
                        # Check if it's rate limit (429 or 401 with "rate limit" message)
                        is_rate_limit = False
                        
                        if e.response.status_code == 429:
                            is_rate_limit = True
                        elif e.response.status_code == 401:
                            # VNPT API returns 401 with "Rate limit exceed" message
                            try:
                                error_data = e.response.json()
                                error_msg = str(error_data.get('error', '')).lower()
                                message = str(error_data.get('message', '')).lower()
                                if 'rate limit' in error_msg or 'rate limit' in message:
                                    is_rate_limit = True
                            except:
                                pass
                        
                        if is_rate_limit:
                            # Aggressive backoff for rate limit: 60s, 120s, 180s...
                            wait = 60 * (attempt + 1)
                            print(f"  ⚠ Rate limit detected, wait {wait}s...")
                            time.sleep(wait)
                            if attempt == max_retries - 1:
                                # After all retries, raise exception to stop script
                                raise RateLimitException("Rate limit exceeded after retries")
                        elif attempt < max_retries - 1:
                            print(f"  ⚠ HTTP error, retry...")
                            time.sleep(2 ** attempt)
                        else:
                            return ""
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"  ⚠ Error: {e}, retry...")
                            time.sleep(2 ** attempt)
                        else:
                            return ""
                return ""
            return wrapper
        return decorator

    @retry_api_call(max_retries=10)
    def chat_completion(
        self,
        messages: List[Dict],
        model: str = "small",
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 20,
        max_tokens: int = 512
    ) -> str:
        """
        Call chat completion API
        """
        # Check cache first
        cache_key = self._get_cache_key(messages, model)
        if cache_key in self.cache:
            # print(f"  ✓ Cache hit!") # Optional log
            return self.cache[cache_key]

        endpoint = self.config.get_endpoint(model)
        headers = self.config.get_headers(model)

        payload = {
            "model": self.config.models[model],
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "n": 1,
            "max_completion_tokens": max_tokens
        }

        # Remove internal try-except to let decorator handle exceptions
        response = self.session.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()

        # Check if response has expected format
        if 'choices' not in result:
            # Check if it's an error response
            if 'error' in result or 'dataBase64' in result:
                # Try to decode error message
                try:
                    import base64
                    if 'dataBase64' in result:
                        error_data = base64.b64decode(result['dataBase64']).decode('utf-8')
                        error_json = json.loads(error_data)
                        if 'error' in error_json and 'message' in error_json['error']:
                            print(f"API Content Filter: {error_json['error']['message'][:200]}")
                except:
                    pass
                print(f"API returned error response (possibly content filter)")
                # Return a special string to avoid retrying content filter errors
                # and to allow caching of this result (so we don't hit the filter again)
                return "CONTENT_FILTERED"

            print(f"API Error: Unexpected response format")
            print(f"Response keys: {list(result.keys())}")
            return ""

        if not result['choices']:
            print(f"API Error: Empty choices in response")
            return ""

        content = result['choices'][0]['message']['content']
        
        # Save to cache
        if content:
            self.cache[cache_key] = content
            self._save_cache()
            
        return content

    def generate(
        self,
        prompt: str,
        model: str = "small",
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        """
        Simple generate method (wraps chat_completion)

        Args:
            prompt: User prompt
            model: 'small' or 'large'
            temperature: Sampling temperature
            max_tokens: Max tokens

        Returns:
            Generated response
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def embed(self, text: str) -> List[float]:
        """
        Get embedding for text

        Args:
            text: Input text

        Returns:
            Embedding vector (list of floats)
        """
        endpoint = self.config.get_endpoint("embedding")
        headers = self.config.get_headers("embedding")

        payload = {
            "model": self.config.models["embedding"],
            "input": text,
            "encoding_format": "float"
        }

        try:
            response = self.session.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()

            result = response.json()
            return result['data'][0]['embedding']

        except requests.exceptions.RequestException as e:
            print(f"Embedding API Error: {e}")
            return []


# Singleton
llm_client = VNPTClient()
