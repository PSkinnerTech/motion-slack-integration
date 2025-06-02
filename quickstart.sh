#!/bin/bash

echo "🚀 Motion-Slack Integration Quick Start"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  Please edit .env and add your:"
    echo "   - Motion API Key"
    echo "   - Motion Workspace ID"
    echo "   - Slack Bot Token"
    echo ""
    echo "Then run this script again!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if user wants to find workspace ID
echo ""
read -p "Do you need help finding your Motion Workspace ID? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python find_workspace_id.py
    echo ""
    read -p "Press any key to continue..."
fi

# Run the integration
echo ""
echo "🎯 Starting Motion-Slack integration..."
echo "Press Ctrl+C to stop"
echo ""
python main.py