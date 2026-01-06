#!/bin/bash
# CrossFit Performance App - Complete Deployment Script
# Run on your DigitalOcean Droplet (167.99.52.204)

set -e

DROPLET_IP="167.99.52.204"
APP_DIR="/var/www/crossfit-app"
REPO_URL="https://github.com/DGator86/Prodigy---App.git"

echo "=========================================="
echo "CrossFit Performance App - Full Deployment"
echo "Droplet: $DROPLET_IP"
echo "=========================================="

# Step 1: System Updates & Dependencies
echo ""
echo "[1/7] Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv nginx git curl

# Step 2: Clone Repository
echo ""
echo "[2/7] Cloning repository..."
rm -rf $APP_DIR
git clone $REPO_URL $APP_DIR
cd $APP_DIR

# Step 3: Python Virtual Environment
echo ""
echo "[3/7] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Step 4: Build Frontend
echo ""
echo "[4/7] Building frontend..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
cd frontend
npm install
npm run build
cd ..

# Step 5: Configure systemd service
echo ""
echo "[5/7] Configuring API service..."
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

systemctl daemon-reload
systemctl enable crossfit-api

# Step 6: Configure nginx
echo ""
echo "[6/7] Configuring nginx..."
cat > /etc/nginx/sites-available/crossfit-app << 'EOF'
server {
    listen 80;
    server_name 167.99.52.204;

    # Frontend - serve static files
    location / {
        root /var/www/crossfit-app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API - proxy to FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
    }
    
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
    }
}
EOF

ln -sf /etc/nginx/sites-available/crossfit-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Step 7: Set permissions and start services
echo ""
echo "[7/7] Starting services..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

nginx -t && systemctl restart nginx
systemctl restart crossfit-api

# Verify
sleep 3
echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Your app is now live at: http://$DROPLET_IP"
echo ""
echo "📊 Quick checks:"
curl -s http://localhost:8000/health && echo " - API is healthy"
echo ""
echo "📝 Useful commands:"
echo "  systemctl status crossfit-api  - Check API status"
echo "  systemctl status nginx         - Check nginx status"
echo "  journalctl -u crossfit-api -f  - View API logs"
echo "=========================================="
