"""VNPT AI API Client - Lightweight HTTP client for LLM APIs."""

import json
import os
import sys
import time
from typing import Dict, List

import requests

# Custom exception for rate limiting
class RateLimitException(Exception):
    """Raised when API rate limit is hit"""
    pass

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.api_config import api_config

# Import rate limiter
try:
    from modules.utils.rate_limiter import rate_limiter
    RATE_LIMITER_ENABLED = True
except ImportError:
    RATE_LIMITER_ENABLED = False
    print("WARN: Rate limiter not available")


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

    def _env_int(self, name: str, default: int) -> int:
        try:
            return int(os.getenv(name, str(default)).strip())
        except Exception:
            return default

    def _env_str(self, name: str, default: str) -> str:
        val = os.getenv(name)
        return (val.strip() if isinstance(val, str) else default) or default

    def _sleep_with_heartbeat(self, seconds: int):
        """Sleep with optional heartbeat logs to show progress during long waits."""
        heartbeat = self._env_int("VNPT_RATE_LIMIT_HEARTBEAT_SECONDS", 0)
        if heartbeat <= 0 or seconds <= heartbeat:
            time.sleep(max(seconds, 0))
            return

        remaining = max(seconds, 0)
        while remaining > 0:
            chunk = min(heartbeat, remaining)
            time.sleep(chunk)
            remaining -= chunk
            if remaining > 0:
                print(f"  WARN Waiting... {remaining}s remaining")

    def retry_api_call(max_retries=10):
        """Retry decorator with exponential backoff.

        Behavior can be tuned via env vars:
        - VNPT_RATE_LIMIT_MODE: 'wait' (default) or 'failfast'
        - VNPT_RATE_LIMIT_MAX_RETRIES: overrides decorator max_retries
        - VNPT_RATE_LIMIT_BASE_WAIT_SECONDS: base wait for rate limits (default: 60)
        - VNPT_RATE_LIMIT_MAX_WAIT_SECONDS: cap per-wait (default: 600)
        - VNPT_RATE_LIMIT_HEARTBEAT_SECONDS: prints a countdown during long waits
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                self_obj = args[0] if args else None
                if hasattr(self_obj, "_env_int"):
                    effective_max_retries = self_obj._env_int("VNPT_RATE_LIMIT_MAX_RETRIES", max_retries)
                    rate_limit_mode = self_obj._env_str("VNPT_RATE_LIMIT_MODE", "wait").lower()
                    base_wait = self_obj._env_int("VNPT_RATE_LIMIT_BASE_WAIT_SECONDS", 60)
                    max_wait = self_obj._env_int("VNPT_RATE_LIMIT_MAX_WAIT_SECONDS", 600)
                else:
                    effective_max_retries = max_retries
                    rate_limit_mode = (os.getenv("VNPT_RATE_LIMIT_MODE") or "wait").strip().lower()
                    base_wait = 60
                    max_wait = 600

                for attempt in range(max(1, effective_max_retries)):
                    try:
                        result = func(*args, **kwargs)
                        if result and len(str(result).strip()) > 0:
                            time.sleep(0.5)  # Small delay after success
                            return result
                        # Empty result, retry
                        if attempt < max_retries - 1:
                            wait = 2 ** attempt
                            print(f"  WARN Empty response, retry in {wait}s...")
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
                            except Exception:
                                pass
                        
                        if is_rate_limit:
                            if rate_limit_mode == "failfast":
                                raise RateLimitException("Rate limit detected (failfast)")

                            # Backoff for rate limit: base_wait, 2*base_wait, ... capped.
                            wait = min(max_wait, base_wait * (attempt + 1))
                            print(f"  WARN Rate limit detected, wait {wait}s...")
                            if hasattr(self_obj, "_sleep_with_heartbeat"):
                                self_obj._sleep_with_heartbeat(wait)
                            else:
                                time.sleep(wait)

                            if attempt == effective_max_retries - 1:
                                # After all retries, raise exception to allow the pipeline fallback.
                                raise RateLimitException("Rate limit exceeded after retries")
                        elif attempt < max_retries - 1:
                            print("  WARN HTTP error, retry...")
                            time.sleep(2 ** attempt)
                        else:
                            return ""
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"  WARN Error: {e}, retry...")
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
                except Exception:
                    pass
                print("API returned error response (possibly content filter)")
                # Return a special string to avoid retrying content filter errors
                # and to allow caching of this result (so we don't hit the filter again)
                return "CONTENT_FILTERED"

            print("API Error: Unexpected response format")
            print(f"Response keys: {list(result.keys())}")
            return ""

        if not result['choices']:
            print("API Error: Empty choices in response")
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
        # Apply rate limiting
        if RATE_LIMITER_ENABLED:
            api_type = "small" if model == "small" else "large"
            rate_limiter.wait_if_needed(api_type)

        messages = [{"role": "user", "content": prompt}]
        result = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Record the call
        if RATE_LIMITER_ENABLED:
            api_type = "small" if model == "small" else "large"
            rate_limiter.record_call(api_type)

        return result

    def embed(self, text: str) -> List[float]:
        """
        Get embedding for text

        Args:
            text: Input text

        Returns:
            Embedding vector (list of floats)
        """
        # Apply rate limiting
        if RATE_LIMITER_ENABLED:
            rate_limiter.wait_if_needed("embed")

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
            embedding = result['data'][0]['embedding']

            # Record the call
            if RATE_LIMITER_ENABLED:
                rate_limiter.record_call("embed")

            return embedding

        except requests.exceptions.RequestException as e:
            print(f"Embedding API Error: {e}")
            return []


# Singleton
llm_client = VNPTClient()
