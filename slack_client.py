import requests
import logging
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SlackClient:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict] = None) -> Dict:
        """Make a request to the Slack API with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(3):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    timeout=30
                )
                
                response.raise_for_status()
                data = response.json()
                
                if not data.get("ok"):
                    error = data.get("error", "Unknown error")
                    logger.error(f"Slack API error: {error}")
                    if error == "ratelimited":
                        retry_after = int(response.headers.get("Retry-After", 10))
                        logger.warning(f"Rate limited, waiting {retry_after} seconds...")
                        time.sleep(retry_after)
                        continue
                    else:
                        raise Exception(f"Slack API error: {error}")
                
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def post_message(self, channel: str, text: str, blocks: Optional[list] = None) -> Dict:
        """Post a message to a Slack channel"""
        payload = {
            "channel": channel,
            "text": text,
            "mrkdwn": True  # Enable markdown formatting
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        try:
            response = self._make_request("POST", "chat.postMessage", json_data=payload)
            logger.info(f"Message posted to {channel}")
            return response
        except Exception as e:
            logger.error(f"Error posting message to Slack: {e}")
            raise
    
    def test_auth(self) -> bool:
        """Test the Slack authentication"""
        try:
            response = self._make_request("GET", "auth.test")
            if response.get("ok"):
                logger.info(f"Slack auth successful: {response.get('team')} - {response.get('user')}")
                return True
            return False
        except Exception as e:
            logger.error(f"Slack auth test failed: {e}")
            return False