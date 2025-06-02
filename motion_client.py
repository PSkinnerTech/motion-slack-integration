import requests
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class MotionClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.usemotion.com/v1"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     json_data: Optional[Dict] = None) -> Dict:
        """Make a request to the Motion API with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(3):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=30
                )
                
                if response.status_code == 429:  # Rate limit
                    logger.warning("Rate limit hit, waiting 10 seconds...")
                    time.sleep(10)
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def get_tasks(self, workspace_id: str, include_all_statuses: bool = True, 
                  cursor: Optional[str] = None) -> List[Dict]:
        """Get all tasks from a workspace"""
        all_tasks = []
        
        while True:
            params = {
                "workspaceId": workspace_id,
                "includeAllStatuses": str(include_all_statuses).lower()
            }
            
            if cursor:
                params["cursor"] = cursor
            
            try:
                response = self._make_request("GET", "/tasks", params=params)
                
                tasks = response.get("tasks", [])
                all_tasks.extend(tasks)
                
                # Check if there are more pages
                meta = response.get("meta", {})
                cursor = meta.get("nextCursor")
                
                if not cursor:
                    break
                    
                logger.info(f"Retrieved {len(tasks)} tasks, fetching next page...")
                
            except Exception as e:
                logger.error(f"Error fetching tasks: {e}")
                break
        
        logger.info(f"Retrieved total of {len(all_tasks)} tasks")
        return all_tasks
    
    def get_user_info(self) -> Dict:
        """Get current user information"""
        try:
            return self._make_request("GET", "/users/me")
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            return {}
    
    def get_workspace(self, workspace_id: str) -> Dict:
        """Get workspace information"""
        try:
            return self._make_request("GET", f"/workspaces/{workspace_id}")
        except Exception as e:
            logger.error(f"Error fetching workspace info: {e}")
            return {}
    
    def get_task(self, task_id: str) -> Dict:
        """Get a specific task by ID"""
        try:
            return self._make_request("GET", f"/tasks/{task_id}")
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            return {}
    
    def get_workspaces(self, cursor: Optional[str] = None) -> List[Dict]:
        """Get all workspaces the user is part of"""
        all_workspaces = []
        
        while True:
            params = {}
            if cursor:
                params["cursor"] = cursor
            
            try:
                response = self._make_request("GET", "/workspaces", params=params)
                
                workspaces = response.get("workspaces", [])
                all_workspaces.extend(workspaces)
                
                # Check if there are more pages
                meta = response.get("meta", {})
                cursor = meta.get("nextCursor")
                
                if not cursor:
                    break
                    
                logger.info(f"Retrieved {len(workspaces)} workspaces, fetching next page...")
                
            except Exception as e:
                logger.error(f"Error fetching workspaces: {e}")
                break
        
        logger.info(f"Retrieved total of {len(all_workspaces)} workspaces")
        return all_workspaces