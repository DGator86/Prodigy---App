# ✅ Deployment Verification Checklist

Quick reference for verifying your CrossFit Performance App deployment.

---

## 🔍 Immediate Checks (Run on Droplet)

### 1. Service Status
```bash
systemctl status crossfit-api
systemctl status nginx
```
**Expected:** Both show `● active (running)` in green

### 2. API Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"ok"}`

### 3. Nginx Configuration
```bash
nginx -t
```
**Expected:** `syntax is ok` and `test is successful`

### 4. Check Listening Ports
```bash
ss -tlnp | grep -E ':(80|8000)'
```
**Expected:**
- Port 80: nginx
- Port 8000: uvicorn (Python API)

---

## 🌐 Browser Checks (From Your Computer)

Open these URLs in your browser:

1. **Frontend:** http://167.99.52.204
   - Should show the CrossFit Performance App login page

2. **API Documentation:** http://167.99.52.204/docs
   - Should show FastAPI Swagger UI

3. **Health Endpoint:** http://167.99.52.204/health
   - Should display: `{"status":"ok"}`

---

## 📊 Log Verification

### View Last 20 API Logs
```bash
journalctl -u crossfit-api -n 20 --no-pager
```
**Look for:** No error messages, clean startup

### View Nginx Error Log
```bash
tail -20 /var/log/nginx/error.log
```
**Expected:** Empty or only notices, no critical errors

---

## 🧪 Functional Tests

### Test 1: User Registration
```bash
curl -X POST http://167.99.52.204/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'
```
**Expected:** Returns user object with ID and email

### Test 2: Login
```bash
curl -X POST http://167.99.52.204/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=test@example.com&password=TestPass123!'
```
**Expected:** Returns JWT access token

### Test 3: Frontend Loads Assets
```bash
curl -I http://167.99.52.204/assets/index.js
```
**Expected:** HTTP 200 OK response

---

## 🔧 File System Checks

### 1. Application Directory
```bash
ls -la /var/www/crossfit-app/
```
**Expected:** Should see: backend/, frontend/, deploy/, etc.

### 2. Frontend Build
```bash
ls -la /var/www/crossfit-app/frontend/dist/
```
**Expected:** Should see: index.html, assets/, etc.

### 3. Python Virtual Environment
```bash
/var/www/crossfit-app/venv/bin/python --version
```
**Expected:** Python 3.x.x

### 4. Permissions
```bash
stat -c '%U:%G' /var/www/crossfit-app
```
**Expected:** `www-data:www-data`

---

## 🚨 Troubleshooting Quick Fixes

### If API service fails:
```bash
journalctl -u crossfit-api -n 50
systemctl restart crossfit-api
```

### If nginx shows errors:
```bash
nginx -t
tail -50 /var/log/nginx/error.log
systemctl restart nginx
```

### If frontend shows 404:
```bash
ls -la /var/www/crossfit-app/frontend/dist/
# If missing, rebuild:
cd /var/www/crossfit-app/frontend
npm run build
```

### If database errors:
```bash
ls -la /var/www/crossfit-app/backend/app.db
# Reinitialize if needed:
cd /var/www/crossfit-app/backend
/var/www/crossfit-app/venv/bin/python -c "from app.db.base import init_db; init_db()"
```

---

## ✅ Success Criteria

Your deployment is successful if:

- [x] Both systemd services are active
- [x] Health check returns OK
- [x] Frontend loads in browser
- [x] API docs are accessible
- [x] Can register a new user
- [x] Can log in and get JWT token
- [x] No errors in logs

---

## 📈 Next Steps

After verifying deployment:

1. **Create your first account** in the browser
2. **Log a test workout** to verify the scoring engine
3. **Check the dashboard** to see EWU calculations
4. **Set up HTTPS** for production use
5. **Configure monitoring** and alerts

---

## 🎯 Performance Checks (Optional)

### API Response Time
```bash
time curl -s http://localhost:8000/health > /dev/null
```
**Expected:** < 100ms

### Memory Usage
```bash
ps aux | grep -E '(uvicorn|nginx)' | grep -v grep
```
**Expected:** Reasonable memory usage (< 500MB combined)

### Disk Space
```bash
df -h /var/www
```
**Expected:** Sufficient free space (> 1GB)

---

## 📞 Support

If any check fails:
1. Review the specific error message
2. Check the relevant logs
3. Restart the affected service
4. Verify file permissions and paths
5. Re-run the deployment script if needed

**Most issues** can be resolved by restarting services or re-running the deployment script.
