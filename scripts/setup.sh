#!/bin/bash

# Retail & CPG Chatbot Setup Script
# =================================
# This script automates the setup process for the chatbot template

set -e  # Exit on any error

echo "🚀 Setting up Retail & CPG Customer Service Chatbot..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "🧠 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Set up environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.template .env
    echo "📝 Please edit the .env file with your configuration"
else
    echo "⚙️ Environment file already exists"
fi

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p logs data backups

# Set permissions
echo "🔒 Setting file permissions..."
chmod +x scripts/*.sh
chmod 600 .env 2>/dev/null || true

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your configuration"
echo "2. Run the application: python app.py"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "For Docker deployment:"
echo "  docker-compose up -d"
