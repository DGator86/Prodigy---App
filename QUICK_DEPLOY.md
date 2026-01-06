# 🚀 Quick Deploy Guide - CrossFit Performance App

## Prerequisites
- SSH access to your droplet: `root@167.99.52.204`
- Your SSH key configured or root password ready

---

## Step 1: SSH into Your Droplet

Open your terminal and connect:

```bash
ssh root@167.99.52.204
```

**Troubleshooting:**
- If prompted about fingerprint, type `yes` to continue
- If you don't have SSH access, check your DigitalOcean dashboard for the root password

---

## Step 2: Run the One-Command Deployment

Once connected, paste this command:

```bash
curl -fsSL https://raw.githubusercontent.com/DGator86/Prodigy---App/main/deploy/deploy.sh | bash
```

**What this does:**
1. Updates system packages
2. Installs Python, Node.js, nginx, git
3. Clones your repository to `/var/www/crossfit-app`
4. Sets up Python virtual environment
5. Builds the React frontend
6. Configures systemd service for the API
7. Configures nginx as reverse proxy
8. Starts all services

**Expected time:** 3-5 minutes

---

## Step 3: Monitor the Deployment

You'll see progress indicators like:

```
==========================================
CrossFit Performance App - Full Deployment
Droplet: 167.99.52.204
==========================================

[1/7] Installing system dependencies...
[2/7] Cloning repository...
[3/7] Setting up Python environment...
[4/7] Building frontend...
[5/7] Configuring API service...
[6/7] Configuring nginx...
[7/7] Starting services...
```

Wait for the "✅ DEPLOYMENT COMPLETE!" message.

---

## Step 4: Verify Deployment

### Check if services are running:

```bash
# Check API service
systemctl status crossfit-api

# Check nginx
systemctl status nginx
```

Both should show `active (running)` in green.

### Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"ok"}
```

### Test from your browser:

1. **Frontend:** http://167.99.52.204
2. **API Docs:** http://167.99.52.204/docs
3. **Health Check:** http://167.99.52.204/health

---

## Step 5: View Logs (Optional)

### View API logs in real-time:

```bash
journalctl -u crossfit-api -f
```

Press `Ctrl+C` to stop viewing logs.

### View nginx logs:

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🎉 Success Checklist

- [ ] SSH connected successfully
- [ ] Deployment script completed without errors
- [ ] Both services show "active (running)"
- [ ] Health check returns `{"status":"ok"}`
- [ ] Frontend loads in browser
- [ ] API docs accessible at /docs

---

## 🔧 Troubleshooting

### Problem: Deployment script fails

**Solution:** Run manual steps:

```bash
# Update system
apt update && apt install -y python3 python3-pip python3-venv nginx git curl

# Clone repository
rm -rf /var/www/crossfit-app
git clone https://github.com/DGator86/Prodigy---App.git /var/www/crossfit-app
cd /var/www/crossfit-app

# Run deployment script
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### Problem: API service won't start

**Check logs:**
```bash
journalctl -u crossfit-api -n 50
```

**Common fixes:**
```bash
# Restart the service
systemctl restart crossfit-api

# Check Python environment
/var/www/crossfit-app/venv/bin/python --version
```

### Problem: Frontend shows 502 Bad Gateway

**Cause:** API service not running

**Fix:**
```bash
systemctl start crossfit-api
systemctl status crossfit-api
```

### Problem: Port 80 already in use

**Fix:**
```bash
# Stop default nginx site
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

---

## 📋 Useful Commands

```bash
# Restart services
systemctl restart crossfit-api
systemctl restart nginx

# Stop services
systemctl stop crossfit-api
systemctl stop nginx

# View service status
systemctl status crossfit-api
systemctl status nginx

# Enable auto-start on boot
systemctl enable crossfit-api
systemctl enable nginx

# View logs
journalctl -u crossfit-api -f
tail -f /var/log/nginx/error.log

# Test nginx configuration
nginx -t

# Update application (pull latest code)
cd /var/www/crossfit-app
git pull origin main
systemctl restart crossfit-api
```

---

## 🔐 Security Notes

**Current setup is HTTP only** (not secure for production with real users)

For production, you should:
1. Enable HTTPS with Let's Encrypt SSL
2. Configure firewall (ufw)
3. Set up proper database passwords
4. Use environment variables for secrets
5. Enable rate limiting

**Want to add HTTPS?** Let me know and I'll provide the SSL setup guide!

---

## 📞 Need Help?

If something goes wrong:
1. Check the logs (commands above)
2. Verify all services are running
3. Try restarting services
4. Re-run the deployment script

**Common success:** Most deployments complete successfully on the first try!

---

## ✅ Next Steps After Deployment

1. **Test the app:** Create an account and log a workout
2. **Add HTTPS:** Secure with SSL certificate
3. **Configure domain:** Point your domain to 167.99.52.204
4. **Set up monitoring:** Track uptime and performance
5. **Configure backups:** Protect your data

Happy deploying! 🚀
