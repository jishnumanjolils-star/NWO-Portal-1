# NWO Portal - Render Deployment Guide

## Quick Start

### Prerequisites
- GitHub account with your code repository
- Render account (render.com)
- Your repo: https://github.com/jishnusudhakaran89/NWO-Portal

### Deployment Steps

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in with your GitHub account

2. **Create from Blueprint**
   - Click "Blueprints" in sidebar
   - Click "New Blueprint Instance"
   - Connect your GitHub repository
   - Select: `jishnusudhakaran89/NWO-Portal`
   - Click "Apply"

3. **Auto-provisioned Services**
   - PostgreSQL database (ofcnet_db)
   - Web service (nwo-portal)
   - All environment variables configured

4. **Deployment Process**
   - Build starts automatically
   - Dependencies installed (build.sh)
   - Migrations run (start.sh)
   - App launches on dynamic port
   - Available at: `https://nwo-portal.onrender.com`

---

## Troubleshooting Failed Deployments

### Check Deployment Logs

1. Go to **Render Dashboard**
2. Click on **nwo-portal** service
3. Check **Logs** tab for error messages

### Common Issues & Fixes

#### 1. **Build Fails - "Python Version Not Found"**
**Error:** `Python 3.11.9 not found`

**Solution:**
- Render uses: `3.11.9`, `3.12.x`, `3.13.x`
- Check `render.yaml` line 16:
```yaml
runtimeVersion: "3.11.9"
```
- If error persists, try removing this line (uses default Python)

#### 2. **Migrations Fail - "Database Connection Error"**
**Error:** `psycopg2 error` or `database connection failed`

**Steps:**
1. Wait 30-60 seconds after creation (DB needs to initialize)
2. Check if database service has status "Available" (green)
3. Verify DATABASE_URL is populated in service env vars
4. Manually retry from Render dashboard (Manual Deploy)

#### 3. **Static Files Missing**
**Symptoms:** CSS/images not loading, 404 errors

**Fix:**
- Already handled by WhiteNoise
- Check `STATIC_ROOT` in settings.py: `BASE_DIR / 'staticfiles'`
- Verify no errors in build.sh output

#### 4. **Import/Module Errors**
**Error:** `ModuleNotFoundError` or `ImportError`

**Solution:**
- Verify `requirements.txt` is complete
- Check for missing dependencies:
```bash
pip install -r requirements.txt  # Test locally first
```
- Common missing packages:
  - `gunicorn` ✓ (in requirements.txt)
  - `dj-database-url` ✓ (in requirements.txt)
  - `psycopg2-binary` ✓ (in requirements.txt)

#### 5. **App Crashes on Startup**
**Error:** App starts but immediately crashes

**Debug Steps:**
1. Check both build and start logs
2. Look for Python exceptions
3. Verify Django settings.py environment variables
4. Test locally:
```bash
export DEBUG=False
export ALLOWED_HOSTS="*"
export DATABASE_URL="postgresql://user:pass@localhost/db"
python manage.py runserver
```

#### 6. **Port Binding Error**
**Error:** `Address already in use` or `bind failed`

**Solution:**
- Render provides PORT via env var
- start.sh uses: `${PORT:-8000}`
- This automatically adapts to Render's port
- Should work without changes

---

## Manual Deployment Retry

If deployment fails but you've fixed the issue:

1. Go to **nwo-portal** service in Render
2. Click **Manual Deploy** button
3. Select **Deploy latest commit**
4. Watch logs in real-time

---

## Environment Variables

All automatically configured by render.yaml:

| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | `postgres://...` | PostgreSQL connection (auto from database service) |
| `SECRET_KEY` | `(auto-generated)` | Django secret key for security |
| `DEBUG` | `False` | Disable debug mode in production |
| `ALLOWED_HOSTS` | `*` | Allow all Render domains |
| `USE_GIS` | `False` | Disable GeoDjango (not needed) |
| `PYTHONUNBUFFERED` | `1` | Real-time log output |

---

## What Happens During Deployment

### Build Phase (build.sh)
```
1. Upgrade pip
2. Install requirements from requirements.txt
3. Collect static files (CSS, JS, images)
```

### Start Phase (start.sh)
```
1. Validate DATABASE_URL environment variable
2. Run Django migrations on PostgreSQL
3. Start Gunicorn with 3 worker processes
4. Listen on PORT (provided by Render)
```

### Failed Build Examples

**Example 1: Missing Requirement**
```
Collecting django-leaflet==0.33.0
ERROR: Could not find a version that satisfies the requirement
```
→ Fix: Update `requirements.txt` with correct version

**Example 2: Database Not Ready**
```
psycopg2.OperationalError: could not translate host name "ofcnet_db"
```
→ Fix: Wait 1 minute for DB initialization, then manual deploy

**Example 3: Module Import Error**
```
ModuleNotFoundError: No module named 'inventory'
```
→ Fix: Check `INSTALLED_APPS` in settings.py, verify inventory/ folder exists

---

## Testing Before Deployment

Run these commands locally to catch issues early:

```bash
# 1. Test requirements
pip install -r requirements.txt

# 2. Test migrations
python manage.py migrate

# 3. Test static files collection
python manage.py collectstatic --noinput

# 4. Test settings
python manage.py check

# 5. Create superuser (optional)
python manage.py createsuperuser
```

---

## Accessing the Deployed App

Once deployed successfully:

1. **Web URL:** `https://nwo-portal.onrender.com`
2. **Admin Panel:** `https://nwo-portal.onrender.com/admin`
3. **API Endpoints:** `https://nwo-portal.onrender.com/api/`

---

## Database Access

PostgreSQL database is **private** by default (good for security).

To access from local machine:
1. ⚠️ Not recommended for free tier (Render free tier doesn't support external connections)
2. Use Render's built-in terminal or backups
3. For production, upgrade to paid plan for database tunneling

---

## Monitoring

### View Real-time Logs
1. Go to **nwo-portal** service
2. Click **Logs** tab
3. Logs auto-update every second

### Common Log Patterns

**Healthy Startup:**
```
[start.sh] Starting NWO Portal application
[start.sh] Database URL: postgres://***
[start.sh] Running Django migrations
[start.sh] Migrations completed successfully
[start.sh] Launching Gunicorn with python -m
```

**Build Successful:**
```
Step 1/3: Upgrading pip
Step 2/3: Installing Python dependencies
Step 3/3: Collecting static files
NWO PORTAL BUILD COMPLETED
```

---

## Performance Tips

### For Free Tier
- ⚠️ App spins down after 15 min of inactivity
- First request after inactivity takes 30 seconds
- 0.5 GB RAM limit
- ~1 GB storage

### Improve Performance
1. Upgrade to paid plan ($7/month)
2. Optimize database queries
3. Enable caching
4. Use CDN for static files

---

## Rollback (If Needed)

If latest commit breaks deployment:

### Option 1: Revert Commit
```bash
git revert HEAD
git push origin main
# Then click "Manual Deploy" on Render
```

### Option 2: Deploy Previous Commit
```bash
git reset --hard <commit-hash>
git push --force origin main
# Then click "Manual Deploy" on Render
```

### Option 3: Check Git Log
```bash
git log --oneline -10
```

---

## Support & Resources

- **Render Docs:** https://render.com/docs
- **Render Blueprints:** https://render.com/docs/blueprints
- **Django Deployment:** https://docs.djangoproject.com/en/6.0/howto/deployment/
- **Gunicorn:** https://gunicorn.org/
- **WhiteNoise:** https://whitenoise.evans.io/

---

## Quick Command Reference

```bash
# View recent commits
git log --oneline -5

# Push changes to trigger auto-deploy
git push origin main

# Check git status
git status

# View what changed
git diff

# View remote URL
git remote -v

# Manually check if deployment ready (local test)
bash build.sh
bash start.sh
```

---

## File Structure

```
NWO-Portal/
├── render.yaml          # Render deployment blueprint
├── start.sh             # Start script with migrations
├── build.sh             # Build script with dependencies
├── manage.py            # Django management
├── requirements.txt     # Python dependencies
├── nwo_portal/
│   ├── settings.py      # Django settings (production-ready)
│   ├── wsgi.py          # WSGI application
│   └── urls.py
├── inventory/           # Main app
├── db.sqlite3           # Local SQLite (not used in production)
└── staticfiles/         # Collected static files (generated)
```

---

**Last Updated:** 2026-05-24  
**Status:** ✅ Ready for Production Deployment
