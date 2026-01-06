#!/bin/bash
# CrossFit Performance App - Complete One-Command Installation
# Usage: curl -sSL http://YOUR_URL/install.sh | bash

set -e

echo "🏋️ CrossFit Performance App - Complete Installation"
echo "===================================================="

# Variables
APP_DIR="/var/www/crossfit-app"
BACKEND_PORT=8000

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo bash $0"
    exit 1
fi

# Update and install dependencies
echo "📦 Installing system dependencies..."
apt update -qq
apt install -y python3 python3-pip python3-venv nginx curl

# Create app directory
echo "📁 Creating app directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip -q
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings \
    python-jose[cryptography] passlib[bcrypt] bcrypt python-multipart \
    email-validator python-dotenv -q

echo "✅ Dependencies installed!"
echo ""
echo "📋 Now extract the app files:"
echo "   1. Upload crossfit-app.tar.gz to $APP_DIR"
echo "   2. tar -xzf crossfit-app.tar.gz"
echo "   3. bash deploy/start_services.sh"
