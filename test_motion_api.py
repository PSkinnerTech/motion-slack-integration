#!/usr/bin/env python3
"""
Test script to validate Motion API connection
"""

import os
from dotenv import load_dotenv
from motion_client import MotionClient

# Load environment variables
load_dotenv()

def test_motion_api():
    print("🧪 Testing Motion API Connection...\n")
    
    # Check if API key exists
    api_key = os.environ.get('MOTION_API_KEY')
    workspace_id = os.environ.get('MOTION_WORKSPACE_ID')
    
    if not api_key:
        print("❌ MOTION_API_KEY not found in environment")
        return False
    
    if not workspace_id:
        print("❌ MOTION_WORKSPACE_ID not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print(f"✅ Workspace ID: {workspace_id}\n")
    
    try:
        # Initialize client
        client = MotionClient(api_key)
        
        # Test 1: Get user info
        print("🔍 Test 1: Getting user info...")
        user_info = client.get_user_info()
        if user_info:
            print(f"✅ User: {user_info.get('name')} ({user_info.get('email')})")
        else:
            print("❌ Failed to get user info")
            return False
        
        # Test 2: List workspaces
        print("\n🔍 Test 2: Listing workspaces...")
        workspaces = client.get_workspaces()
        if workspaces:
            print(f"✅ Found {len(workspaces)} workspace(s):")
            for workspace in workspaces:
                status = "✅" if workspace.get('id') == workspace_id else "⚪"
                print(f"  {status} {workspace.get('name')} ({workspace.get('id')})")
        else:
            print("❌ No workspaces found")
            return False
        
        # Test 3: Check specific workspace
        print(f"\n🔍 Test 3: Checking workspace {workspace_id}...")
        workspace_found = any(w.get('id') == workspace_id for w in workspaces)
        if workspace_found:
            print("✅ Workspace ID is valid and accessible")
        else:
            print("❌ Workspace ID not found in your accessible workspaces")
            return False
        
        # Test 4: Get tasks from workspace
        print(f"\n🔍 Test 4: Getting tasks from workspace...")
        tasks = client.get_tasks(workspace_id, include_all_statuses=True)
        print(f"✅ Found {len(tasks)} tasks in workspace")
        
        # Show a few completed tasks if any
        completed_tasks = [t for t in tasks if t.get('completed')]
        if completed_tasks:
            print(f"✅ Found {len(completed_tasks)} completed tasks")
            # Show the most recent 3 completed tasks
            recent_completed = sorted(completed_tasks, 
                                    key=lambda x: x.get('completedTime', ''), 
                                    reverse=True)[:3]
            for task in recent_completed:
                name = task.get('name', 'Unnamed')
                completed_time = task.get('completedTime', 'Unknown time')
                print(f"  📋 {name} (completed: {completed_time})")
        else:
            print("ℹ️  No completed tasks found (this is normal if you haven't completed any recently)")
        
        print("\n🎉 All Motion API tests passed! The API is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Motion API test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_motion_api()
    if not success:
        print("\n💡 Common fixes:")
        print("1. Check your Motion API key is correct")
        print("2. Ensure you have a Team or Enterprise Motion plan (Individual plans don't have API access)")
        print("3. Verify the workspace ID is correct")
        print("4. Check your internet connection")
        exit(1)
    else:
        print("\n✅ Motion API is ready for deployment!") 