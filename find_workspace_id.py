#!/usr/bin/env python3
"""
Helper script to find your Motion workspace ID
Run this after setting up your .env file with MOTION_API_KEY
"""

import os
import sys
from dotenv import load_dotenv
from motion_client import MotionClient

# Load environment variables
load_dotenv()

def main():
    api_key = os.environ.get('MOTION_API_KEY')
    
    if not api_key:
        print("❌ Error: MOTION_API_KEY not found in environment variables")
        print("Please create a .env file with your Motion API key")
        sys.exit(1)
    
    print("🔍 Finding your Motion workspaces...\n")
    
    try:
        client = MotionClient(api_key)
        
        # Get current user info
        user_info = client.get_user_info()
        if user_info:
            print(f"👤 Logged in as: {user_info.get('name', 'Unknown')}")
            print(f"📧 Email: {user_info.get('email', 'Unknown')}\n")
        
        # Get workspaces using the API
        print("🔍 Fetching your workspaces from Motion API...")
        workspaces = client.get_workspaces()
        
        if not workspaces:
            print("❌ No workspaces found or unable to fetch workspaces")
            print("\n💡 If you're sure you have access to workspaces, try these manual methods:")
            print("1. Check Motion in your browser URL for workspace IDs")
            print("2. Contact Motion support if the API isn't returning your workspaces")
            return
        
        print(f"✅ Found {len(workspaces)} workspace(s):\n")
        
        for i, workspace in enumerate(workspaces, 1):
            workspace_id = workspace.get('id', 'Unknown')
            workspace_name = workspace.get('name', 'Unnamed')
            workspace_type = workspace.get('type', 'Unknown')
            team_id = workspace.get('teamId', 'Unknown')
            
            print(f"🏢 Workspace {i}:")
            print(f"   📛 Name: {workspace_name}")
            print(f"   🆔 ID: {workspace_id}")
            print(f"   📊 Type: {workspace_type}")
            print(f"   👥 Team ID: {team_id}")
            
            # Show labels if available
            labels = workspace.get('labels', [])
            if labels:
                try:
                    if isinstance(labels, list) and labels:
                        # Handle case where labels are objects with 'name' property
                        if isinstance(labels[0], dict):
                            label_names = [label.get('name', 'Unnamed') for label in labels]
                        else:
                            # Handle case where labels are just strings
                            label_names = [str(label) for label in labels]
                        print(f"   🏷️  Labels: {', '.join(label_names)}")
                except Exception as e:
                    print(f"   🏷️  Labels: {labels} (raw)")
            
            # Show statuses if available
            statuses = workspace.get('statuses', [])
            if statuses:
                try:
                    if isinstance(statuses, list) and statuses:
                        # Handle case where statuses are objects with 'name' property
                        if isinstance(statuses[0], dict):
                            status_names = [status.get('name', 'Unnamed') for status in statuses]
                        else:
                            # Handle case where statuses are just strings
                            status_names = [str(status) for status in statuses]
                        print(f"   📋 Statuses: {', '.join(status_names)}")
                except Exception as e:
                    print(f"   📋 Statuses: {statuses} (raw)")
            
            print()
        
        print("💡 To use a workspace, add its ID to your .env file:")
        if len(workspaces) == 1:
            # If only one workspace, suggest it directly
            workspace_id = workspaces[0].get('id')
            print(f"MOTION_WORKSPACE_ID={workspace_id}")
        else:
            # If multiple workspaces, show the format
            print("MOTION_WORKSPACE_ID=<copy-the-workspace-id-from-above>")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your Motion API key is valid and has the necessary permissions")

if __name__ == "__main__":
    main()