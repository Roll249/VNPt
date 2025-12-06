"""
API Configuration for VNPT AI Hackathon
"""
import json
import os
from typing import Dict, List

class APIConfig:
    """Configuration for VNPT AI APIs"""

    def __init__(self, config_file: str = "api-keys.json"):
        self.config_file = config_file
        self.api_keys = self._load_api_keys()

        # Base URL
        self.base_url = "https://api.idg.vnpt.vn/data-service"

        # Endpoints
        self.endpoints = {
            "small": "/v1/chat/completions/vnptai-hackathon-small",
            "large": "/v1/chat/completions/vnptai-hackathon-large",
            "embedding": "/vnptai-hackathon-embedding"
        }

        # Model names
        self.models = {
            "small": "vnptai_hackathon_small",
            "large": "vnptai_hackathon_large",
            "embedding": "vnptai_hackathon_embedding"
        }

        # Quotas
        self.quotas = {
            "small": {"requests_per_day": 1000, "requests_per_hour": 60},
            "large": {"requests_per_day": 500, "requests_per_hour": 40},
            "embedding": {"requests_per_minute": 500}
        }

    def _load_api_keys(self) -> List[Dict]:
        """Load API keys from JSON file"""
        config_path = os.path.join(os.path.dirname(__file__), "..", self.config_file)
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_credentials(self, api_type: str) -> Dict:
        """
        Get credentials for specific API type

        Args:
            api_type: 'small', 'large', or 'embedding'

        Returns:
            Dict with authorization, token_id, token_key
        """
        api_name_map = {
            "small": "LLM small",
            "large": "LLM large",
            "embedding": "LLM embedings"
        }

        target_name = api_name_map.get(api_type)

        for key in self.api_keys:
            if key["llmApiName"] == target_name:
                return {
                    "authorization": key["authorization"],
                    "token_id": key["tokenId"],
                    "token_key": key["tokenKey"]
                }

        raise ValueError(f"API key not found for {api_type}")

    def get_endpoint(self, api_type: str) -> str:
        """Get full endpoint URL"""
        return self.base_url + self.endpoints[api_type]

    def get_headers(self, api_type: str) -> Dict:
        """Get headers for API request"""
        creds = self.get_credentials(api_type)
        return {
            "Content-Type": "application/json",
            "Authorization": creds["authorization"],
            "Token-id": creds["token_id"],
            "Token-key": creds["token_key"]
        }


# Singleton instance
api_config = APIConfig()
