#!/bin/bash
# CrossFit Performance App - Deployment Script
# Run this AFTER uploading files to the server

set -e

APP_DIR="/var/www/crossfit-app"

echo "=========================================="
echo "CrossFit Performance App - Deployment"
echo "=========================================="

cd $APP_DIR

# Activate virtual environment
source venv/bin/activate

# Install/update Python dependencies
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Set permissions
echo "Setting permissions..."
cd $APP_DIR
chown -R www-data:www-data .
chmod -R 755 .

# Setup systemd service
echo "Setting up systemd service..."
cp deploy/crossfit-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable crossfit-api
systemctl restart crossfit-api

# Setup nginx
echo "Setting up nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/crossfit-app
ln -sf /etc/nginx/sites-available/crossfit-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo "=========================================="
echo "Deployment complete!"
echo "Your app should be available at: http://167.99.52.204"
echo ""
echo "Check status with:"
echo "  systemctl status crossfit-api"
echo "  systemctl status nginx"
echo "=========================================="
