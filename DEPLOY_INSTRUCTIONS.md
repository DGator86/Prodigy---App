# Deploy to DigitalOcean Droplet

## Your Server Info
- IP: 167.99.52.204
- User: root (or your username)

## Step 1: SSH into your droplet
```bash
ssh root@167.99.52.204
```

## Step 2: Run these commands on the server

```bash
# Update and install dependencies
apt update && apt install -y python3 python3-pip python3-venv nginx git

# Create app directory
mkdir -p /var/www/crossfit-app
cd /var/www/crossfit-app

# Clone or download the app (we'll use git)
git clone https://github.com/YOUR_REPO/crossfit-app.git . 
# OR download directly - see below

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib bcrypt python-multipart email-validator
```

## Step 3: I'll create a one-liner setup for you

Run this single command on your server and it will set everything up automatically.
