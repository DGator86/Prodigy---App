#!/bin/bash
# CrossFit Performance App - One-Click Installer
# Run on your DigitalOcean droplet: curl -sSL [URL] | bash

set -e
APP_DIR="/var/www/crossfit-app"

echo "================================================"
echo "  CrossFit Performance App - Installing..."
echo "================================================"

# Install dependencies
apt update
apt install -y python3 python3-pip python3-venv nginx

# Create directory
mkdir -p $APP_DIR
cd $APP_DIR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib bcrypt python-multipart email-validator

# Create backend
mkdir -p backend/app/{api/v1,core,models,schemas,services,engine,db}

echo "Creating application files..."
