#!/bin/bash
# Start CrossFit Performance App Services

set -e
cd /var/www/crossfit-app

echo "🚀 Starting CrossFit Performance App..."

# Activate virtual environment
source venv/bin/activate

# Start backend with systemd
echo "📝 Setting up systemd service..."
cat > /etc/systemd/system/crossfit-api.service << 'EOF'
[Unit]
Description=CrossFit Performance API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/crossfit-app/backend
Environment="PATH=/var/www/crossfit-app/venv/bin"
ExecStart=/var/www/crossfit-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Fix permissions
chown -R www-data:www-data /var/www/crossfit-app

# Setup nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/crossfit << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend - serve static files
    location / {
        root /var/www/crossfit-app/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
EOF

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/crossfit /etc/nginx/sites-enabled/

# Test nginx config
nginx -t

# Reload services
systemctl daemon-reload
systemctl enable crossfit-api
systemctl restart crossfit-api
systemctl restart nginx

echo ""
echo "✅ Services started!"
echo "🌐 Your app is now running at: http://$(curl -s ifconfig.me)"
echo ""
echo "📊 Check status:"
echo "   systemctl status crossfit-api"
echo "   systemctl status nginx"
echo ""
echo "📋 View logs:"
echo "   journalctl -u crossfit-api -f"
