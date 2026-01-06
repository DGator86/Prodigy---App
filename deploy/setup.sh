#!/bin/bash
# CrossFit Performance App - Server Setup Script
# Run this on your DigitalOcean droplet

set -e

echo "=========================================="
echo "CrossFit Performance App - Server Setup"
echo "=========================================="

# Update system
echo "Updating system..."
apt update && apt upgrade -y

# Install required packages
echo "Installing dependencies..."
apt install -y python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx git

# Create app directory
echo "Creating app directory..."
mkdir -p /var/www/crossfit-app
cd /var/www/crossfit-app

# Create Python virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-jose passlib bcrypt python-multipart email-validator

echo "=========================================="
echo "Server setup complete!"
echo "Now upload your application files to /var/www/crossfit-app"
echo "=========================================="
