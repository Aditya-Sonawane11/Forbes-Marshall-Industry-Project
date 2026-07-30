"""
API Client - Communicates with FastAPI backend
Acts as a drop-in replacement for the Database class
"""
import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user via API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("user")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error during authentication: {e}")
            raise Exception(f"Failed to connect to API server: {e}")

    # We can add other methods here as needed, but this is enough to test login!
