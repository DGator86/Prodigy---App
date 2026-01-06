#!/bin/bash
# CrossFit Performance App - Full Setup Script for Ubuntu
# Run as root on your DigitalOcean droplet

set -e

echo "🏋️ CrossFit Performance App - Full Setup"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt install -y python3 python3-pip python3-venv nginx curl unzip

# Create app directory
echo "📁 Creating app directory..."
mkdir -p /var/www/crossfit-app
cd /var/www/crossfit-app

# Create backend directory structure
mkdir -p backend/app/{api/v1,core,db,engine,models,schemas,services}

# Download backend files from our deployment package
echo "📥 Setting up backend..."

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt] bcrypt python-multipart email-validator python-dotenv

# Create frontend directory
mkdir -p frontend/dist

echo "✅ Dependencies installed!"
echo ""
echo "📋 Next steps:"
echo "1. Upload the crossfit-app.tar.gz to this server"
echo "2. Extract it: tar -xzf crossfit-app.tar.gz -C /var/www/crossfit-app"
echo "3. Run: ./deploy/start_services.sh"
echo ""
echo "Or use the simplified install below..."
