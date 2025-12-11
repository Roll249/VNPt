"""
VNPT AI API Client - Lightweight HTTP client for LLM APIs
"""
import requests
import time
import json
from typing import Dict, List, Optional, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.api_config import api_config


class VNPTClient:
    """Client for VNPT AI APIs"""

    def __init__(self):
        self.config = api_config
        self.session = requests.Session()  # Reuse connections

    def retry_api_call(max_retries=3):
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
                        if e.response.status_code == 429:  # Rate limit
                            wait = 2 ** (attempt + 2)
                            print(f"  ⚠ Rate limit (429), wait {wait}s...")
                            time.sleep(wait)
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

    @retry_api_call(max_retries=3)
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

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: 'small' or 'large'
            temperature: Sampling temperature
            top_p: Top-p sampling
            top_k: Top-k sampling
            max_tokens: Max completion tokens

        Returns:
            Generated text response
        """
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

        try:
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
                    return ""

                print(f"API Error: Unexpected response format")
                print(f"Response keys: {list(result.keys())}")
                return ""

            if not result['choices']:
                print(f"API Error: Empty choices in response")
                return ""

            return result['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"Error details: {error_detail}")
                except:
                    print(f"Response text: {e.response.text[:500]}")
            return ""

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
