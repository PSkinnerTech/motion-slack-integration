# Motion to Slack Integration

A simple integration that monitors your Motion tasks and automatically posts to Slack when you complete them. Perfect for keeping your team updated on your progress without manual updates.

This is a **one-way integration** that:
- 🔍 Polls Motion every minute for newly completed tasks
- 📢 Posts formatted notifications to your chosen Slack channel
- 🚫 Prevents duplicate notifications with state tracking
- 🔄 Automatically retries on failures
- 🚀 Deploys easily to Railway (or any Python host)

## Quick Start

1. **Clone this repo**
   ```bash
   git clone https://github.com/PSkinnerTech/motion-slack-integration.git
   cd motion-slack-integration
   ```

2. **Set up credentials** (see detailed instructions below)
   - Get Motion API key from Motion settings
   - Create a Slack bot with `chat:write` permission
   - Find your Motion workspace ID

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Deploy to Railway**
   ```bash
   railway login
   railway init
   railway up
   ```

That's it! The bot will start posting your completed Motion tasks to Slack.

## Features

- ✅ Polls Motion API every 60 seconds for newly completed tasks
- 📢 Posts task details to Slack with rich formatting
- 🔄 Tracks state to avoid duplicate notifications
- 🚀 Railway-ready deployment
- 🛡️ Built-in error handling and retry logic

## Setup Instructions

### 1. Prerequisites

- **Motion account** with API access (Team or Enterprise plan - API not available on Individual plans)
- **Slack workspace** where you have permission to create apps
- **Python 3.9+** installed locally for development
- **Railway account** (free tier works) or another hosting solution

### 2. Getting Your Motion API Credentials

#### API Key
1. Log into [Motion](https://usemotion.com)
2. Go to **Settings** → **API & Integrations**
3. Click **"Create New API Key"**
4. Copy the key immediately (it won't be shown again)
5. Save it as `MOTION_API_KEY` in your .env file

#### Workspace ID

#### Workspace ID

**Option 1: Use the helper script** (Recommended)
```bash
# After setting up your .env with MOTION_API_KEY
python find_workspace_id.py
```

**Option 2: Manual method**
1. Go to Motion and open your browser's Developer Tools (F12)
2. Navigate to the Network tab
3. Refresh the page or click around in Motion
4. Look for API calls to `api.usemotion.com`
5. Find a request that includes `workspaceId` in the URL or response
6. Copy that workspace ID (it should be a UUID like `12345678-1234-1234-1234-123456789012`)
7. Save it as `MOTION_WORKSPACE_ID` in your .env file

### 3. Setting Up Slack Bot

This integration only needs a simple Slack bot that can post messages. Here's exactly what to do:

#### Create the Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Choose **"From scratch"** (not from manifest)
4. Enter:
   - **App Name**: `Motion Task Notifier` (or your preferred name)
   - **Workspace**: Select your workspace
5. Click **"Create App"**

#### Configure Bot Permissions

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll down to **"Scopes"** section
3. Under **"Bot Token Scopes"**, click **"Add an OAuth Scope"**
4. Add these permissions:
   - `chat:write` - Allows the bot to send messages
   - `chat:write.public` - Allows posting to public channels without joining them

#### Install the App to Your Workspace

1. Scroll back to the top of the **"OAuth & Permissions"** page
2. Click **"Install to Workspace"**
3. Review the permissions and click **"Allow"**
4. You'll now see a **"Bot User OAuth Token"** that starts with `xoxb-`
5. **Copy this token** - this is your `SLACK_BOT_TOKEN` for the .env file

#### Add the Bot to Your Channel

In Slack, go to your target channel (e.g., #dev-rel) and type:
```
/invite @Motion Task Notifier
```
(Use whatever name you gave your app)

#### What You DON'T Need

This is a simple posting bot, so you can ignore these Slack app features:
- ❌ Event Subscriptions
- ❌ Interactivity & Shortcuts
- ❌ Slash Commands
- ❌ Incoming Webhooks
- ❌ Socket Mode
- ❌ Verification Token
- ❌ Client ID/Secret
- ❌ Signing Secret

These features are for receiving data FROM Slack or building interactive apps. We only need to POST to Slack.

#### Test Your Bot Token

To verify your setup works, you can run this quick test:
```python
import requests

token = "xoxb-YOUR-BOT-TOKEN-HERE"
response = requests.post(
    "https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {token}"},
    json={"channel": "#your-channel", "text": "Test message from Motion integration! 🚀"}
)
print(response.json())  # Should show "ok": true
```

### 4. Deploy to Railway

1. **Fork or clone this repository**

2. **Install Railway CLI** (optional but recommended):
   ```bash
   npm install -g @railway/cli
   ```

3. **Create a new Railway project**:
   ```bash
   railway login
   railway init
   ```

4. **Set environment variables in Railway**:
   ```bash
   railway variables set MOTION_API_KEY=your_motion_api_key
   railway variables set MOTION_WORKSPACE_ID=your_workspace_id
   railway variables set SLACK_BOT_TOKEN=xoxb-your-token
   railway variables set SLACK_CHANNEL=#dev-rel
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

   Or deploy via GitHub:
   - Connect your GitHub repo to Railway
   - Railway will auto-deploy on push

### 5. Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd motion-slack-integration
   ```

2. **Quick start** (Linux/Mac):
   ```bash
   chmod +x quickstart.sh
   ./quickstart.sh
   ```

   Or manually:

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. **Run locally**:
   ```bash
   python main.py
   ```

## Configuration

All configuration is done via environment variables. Create a `.env` file with:

```bash
# Required
MOTION_API_KEY=your_motion_api_key_here
MOTION_WORKSPACE_ID=12345678-1234-1234-1234-123456789012
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Optional
SLACK_CHANNEL=#dev-rel  # Default: #dev-rel
POLL_INTERVAL=60        # Default: 60 seconds
```

| Variable | Description | Default |
|----------|-------------|---------|
| `MOTION_API_KEY` | Your Motion API key | Required |
| `MOTION_WORKSPACE_ID` | Your Motion workspace ID (UUID format) | Required |
| `SLACK_BOT_TOKEN` | Slack bot OAuth token (starts with xoxb-) | Required |
| `SLACK_CHANNEL` | Slack channel to post to | #dev-rel |
| `POLL_INTERVAL` | Seconds between checks | 60 |

## Message Format

When a task is completed, the bot posts:

```
✅ Task Completed: Design new landing page
📝 Description: Create mockups for the new product landing page
📁 Project: Website Redesign
⏱️ Duration: 2h 30m
📊 Status: Done
✓ Completed at: 3:45 PM
```

## Example Use Cases

- **Team Visibility**: Keep your team updated on what you're completing without manual status updates
- **Daily Standups**: Review yesterday's completions easily in Slack
- **Time Tracking**: See how long tasks actually took vs estimates
- **Project Progress**: Track completion velocity for specific projects
- **Accountability**: Create a record of completed work

## Troubleshooting

### Motion API Access
- **"Unauthorized" errors?** Make sure you have a Team or Enterprise Motion plan - Individual plans don't include API access
- **Can't find API settings?** Look under Settings → API & Integrations (only visible on Team/Enterprise plans)

### Bot not posting messages?
1. Check Railway logs: `railway logs`
2. Ensure bot is invited to the channel: `/invite @Your Bot Name`
3. Verify environment variables are set correctly
4. Check that your Slack bot token starts with `xoxb-`

### Getting rate limited?
- The integration respects Motion's rate limits (12 req/min for individuals, 120 for teams)
- If you see rate limit errors, the app will automatically retry

### State file issues?
- Delete `state.json` to reset and check all tasks from the last hour
- The app will recreate the state file automatically

### Can't find workspace ID?
- Try the `find_workspace_id.py` script first
- Check browser DevTools Network tab for `workspaceId` in Motion API calls
- Look for URLs like: `api.usemotion.com/v1/tasks?workspaceId=...`

## Architecture

- **main.py**: Core polling loop and orchestration
- **motion_client.py**: Motion API wrapper with retry logic
- **slack_client.py**: Slack API wrapper
- **state.json**: Tracks last check timestamp (created automatically)

## Support

For Motion API issues, contact Motion support (teams only).
For integration issues, check the logs or open an issue.

## Contributing

Contributions are welcome! This project is open source and we'd love your help making it better.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions

- **Features**:
  - Add support for task creation/update notifications
  - Filter notifications by project or label
  - Customizable message formats
  - Slack thread support for related tasks
  - Daily/weekly summary reports
  
- **Improvements**:
  - Add tests
  - Docker support
  - More deployment options (Heroku, AWS Lambda, etc.)
  - Web UI for configuration
  - Better error messages
  
- **Integrations**:
  - Support for other chat platforms (Discord, Teams, etc.)
  - Two-way sync (create Motion tasks from Slack)
  - Webhook support if/when Motion adds it

### Development Setup

1. Fork and clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Install in development mode: `pip install -e .`
4. Run tests: `pytest` (once tests are added)

## License

MIT License - feel free to use this in your own projects!