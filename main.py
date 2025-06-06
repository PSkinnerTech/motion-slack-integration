import os
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

from motion_client import MotionClient
from slack_client import SlackClient

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for required environment variables
required_vars = ['MOTION_API_KEY', 'MOTION_WORKSPACE_ID', 'SLACK_BOT_TOKEN']
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please set these variables in Railway or create a .env file")
    logger.error("Current environment variables:")
    for key in sorted(os.environ.keys()):
        if not key.startswith('_'):
            logger.error(f"  {key}: {'***' if any(secret in key.upper() for secret in ['KEY', 'TOKEN', 'SECRET']) else os.environ[key][:20] + '...' if len(os.environ[key]) > 20 else os.environ[key]}")
    exit(1)

class MotionSlackIntegration:
    def __init__(self):
        self.motion = MotionClient(os.environ['MOTION_API_KEY'])
        self.slack = SlackClient(os.environ['SLACK_BOT_TOKEN'])
        self.workspace_id = os.environ['MOTION_WORKSPACE_ID']
        self.channel = os.environ.get('SLACK_CHANNEL', '#dev-rel')
        self.state_file = Path('state.json')
        self.poll_interval = int(os.environ.get('POLL_INTERVAL', 60))
        
    def load_state(self):
        """Load the last checked timestamp from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    return datetime.fromisoformat(state.get('last_checked'))
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        
        # Default to 1 hour ago if no state exists
        return datetime.now(timezone.utc).replace(hour=datetime.now().hour - 1)
    
    def save_state(self, timestamp):
        """Save the last checked timestamp to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_checked': timestamp.isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }, f)
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def format_duration(self, duration):
        """Format duration from minutes or string to readable format"""
        if isinstance(duration, (int, float)):
            hours = int(duration // 60)
            minutes = int(duration % 60)
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        elif duration == "NONE":
            return "No duration set"
        elif duration == "REMINDER":
            return "Reminder only"
        return str(duration)
    
    def format_slack_message(self, task):
        """Format task data into a Slack message"""
        # Extract task details
        name = task.get('name', 'Unnamed task')
        description = task.get('description', '').strip()
        project_name = task.get('project', {}).get('name', 'No project')
        duration = self.format_duration(task.get('duration', 'NONE'))
        status = task.get('status', {}).get('name', 'Completed')
        completed_time = task.get('completedTime', '')
        priority = task.get('priority', 'MEDIUM')
        
        # Enhanced HTML cleaning for description
        if description:
            # Remove common HTML tags and replace with appropriate formatting
            description = description.replace('<p>', '').replace('</p>', '\n')
            description = description.replace('<br>', '\n').replace('<br/>', '\n')
            description = description.replace('<div>', '').replace('</div>', '\n')
            description = description.replace('<strong>', '*').replace('</strong>', '*')
            description = description.replace('<b>', '*').replace('</b>', '*')
            description = description.replace('<em>', '_').replace('</em>', '_')
            description = description.replace('<i>', '_').replace('</i>', '_')
            description = description.replace('<ul>', '\n').replace('</ul>', '')
            description = description.replace('<li>', '• ').replace('</li>', '\n')
            description = description.replace('&nbsp;', ' ')
            description = description.replace('&amp;', '&')
            description = description.replace('&lt;', '<')
            description = description.replace('&gt;', '>')
            
            # Clean up extra whitespace and newlines
            description = '\n'.join(line.strip() for line in description.split('\n') if line.strip())
            
            # Truncate if too long but preserve formatting
            if len(description) > 300:
                description = description[:297] + "..."
        
        # Build the message with enhanced formatting
        message = f"✅ *Task Completed: {name}*\n"
        
        # Add description if available (this is the main enhancement)
        if description:
            message += f"📝 *Description:*\n_{description}_\n\n"
        
        message += f"📁 *Project:* {project_name}\n"
        message += f"⏱️ *Expected Duration:* {duration}\n"
        message += f"🎯 *Priority:* {priority}\n"
        message += f"📊 *Status:* {status}\n"
        
        if completed_time:
            try:
                completed_dt = datetime.fromisoformat(completed_time.replace('Z', '+00:00'))
                formatted_time = completed_dt.strftime('%I:%M %p')
                message += f"✓ *Completed at:* {formatted_time}"
            except:
                message += f"✓ *Completed at:* {completed_time}"
        
        return message
    
    def check_for_completed_tasks(self):
        """Check Motion for newly completed tasks"""
        last_checked = self.load_state()
        current_time = datetime.now(timezone.utc)
        
        logger.info(f"Checking for tasks completed since {last_checked}")
        
        try:
            # Get all tasks from the workspace
            tasks = self.motion.get_tasks(
                workspace_id=self.workspace_id,
                include_all_statuses=True
            )
            
            # Filter for newly completed tasks
            new_completions = []
            for task in tasks:
                if task.get('completed'):
                    completed_time_str = task.get('completedTime')
                    if completed_time_str:
                        completed_time = datetime.fromisoformat(
                            completed_time_str.replace('Z', '+00:00')
                        )
                        if completed_time > last_checked:
                            new_completions.append(task)
            
            logger.info(f"Found {len(new_completions)} newly completed tasks")
            
            # Post each completed task to Slack
            for task in new_completions:
                try:
                    message = self.format_slack_message(task)
                    self.slack.post_message(self.channel, message)
                    logger.info(f"Posted to Slack: {task.get('name')}")
                except Exception as e:
                    logger.error(f"Error posting task to Slack: {e}")
            
            # Update state
            self.save_state(current_time)
            
        except Exception as e:
            logger.error(f"Error checking for completed tasks: {e}")
    
    def run(self):
        """Main polling loop"""
        logger.info(f"Starting Motion-Slack integration (polling every {self.poll_interval}s)")
        logger.info(f"Workspace: {self.workspace_id}")
        logger.info(f"Slack channel: {self.channel}")
        
        while True:
            try:
                self.check_for_completed_tasks()
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
            
            time.sleep(self.poll_interval)

if __name__ == "__main__":
    integration = MotionSlackIntegration()
    integration.run()