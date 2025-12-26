# 24/7 Always-On Deployment Guide

## 🏆 Best Options for Never-Sleeping Deployment

### Option 1: **Koyeb** ⭐ RECOMMENDED (Free & Never Sleeps)

**Why Koyeb?**
- ✅ **FREE tier that NEVER sleeps** - Perfect for your use case!
- ✅ No credit card required
- ✅ Automatic HTTPS/SSL
- ✅ Easy deployment from GitHub
- ✅ Great for Flask applications
- ✅ Global CDN included

**Deployment Steps:**

1. **Sign Up**
   - Go to https://www.koyeb.com
   - Sign up with GitHub (free account)

2. **Create New App**
   - Click "Create App"
   - Select "GitHub" as source
   - Choose your repository

3. **Configure**
   ```
   Name: health-tracker
   Region: Choose closest (e.g., US East)
   Build Command: pip install -r requirements.txt
   Run Command: gunicorn app:app --bind 0.0.0.0:$PORT --port $PORT
   ```

4. **Environment Variables** (if needed)
   - Add any required env vars in settings

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your app will be live at: `https://health-tracker-<random>.koyeb.app`

**Cost:** FREE (never sleeps!)

---

### Option 2: **Railway.app** ($5/month - Always On)

**Why Railway?**
- ✅ Very easy to use
- ✅ $5/month for always-on service
- ✅ Automatic deployments from GitHub
- ✅ Great developer experience
- ✅ Free $5 credit monthly (effectively free for small apps)

**Deployment Steps:**

1. **Sign Up**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure**
   - Railway auto-detects Python
   - Add start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Railway automatically sets PORT environment variable

4. **Upgrade to Always-On**
   - Go to Settings → Plan
   - Select "Developer" plan ($5/month)
   - This ensures 24/7 uptime

**Cost:** $5/month (but you get $5 free credit monthly = effectively free!)

---

### Option 3: **Fly.io** (Free Tier - Good for Small Apps)

**Why Fly.io?**
- ✅ Generous free tier
- ✅ Doesn't sleep (runs continuously)
- ✅ Global edge deployment
- ✅ Great performance

**Deployment Steps:**

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Or download from https://fly.io/docs/getting-started/installing-flyctl/
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Create fly.toml** (I'll create this for you)
   ```toml
   app = "health-tracker"
   primary_region = "iad"

   [build]

   [http_service]
     internal_port = 5000
     force_https = true
     auto_stop_machines = false
     auto_start_machines = true
     min_machines_running = 1

   [[services]]
     protocol = "tcp"
     internal_port = 5000
   ```

4. **Deploy**
   ```bash
   fly launch
   fly deploy
   ```

**Cost:** FREE (with generous limits)

---

### Option 4: **Render.com** ($7/month - Always On)

**Why Render?**
- ✅ Very user-friendly
- ✅ Reliable infrastructure
- ✅ Easy GitHub integration
- ✅ $7/month for always-on

**Deployment Steps:**

1. **Sign Up**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo

3. **Configure**
   ```
   Name: health-tracker
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Upgrade Plan**
   - Go to Settings → Plan
   - Select "Starter" plan ($7/month)
   - This ensures 24/7 uptime (no sleeping)

**Cost:** $7/month

---

### Option 5: **PythonAnywhere** (Free Tier Available)

**Why PythonAnywhere?**
- ✅ Specifically designed for Python apps
- ✅ Free tier available
- ✅ Easy Flask deployment
- ✅ Web-based IDE included

**Deployment Steps:**

1. **Sign Up**
   - Go to https://www.pythonanywhere.com
   - Create free account

2. **Upload Files**
   - Use web-based file manager or Git
   - Upload your project files

3. **Configure Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Select Flask
   - Point to your app.py

4. **Set Up**
   - Configure WSGI file
   - Reload web app

**Cost:** FREE (with some limitations) or $5/month for better plan

---

## 🎯 My Recommendation

**For FREE 24/7 hosting:** Use **Koyeb** - it's the best free option that never sleeps.

**For paid ($5/month):** Use **Railway.app** - excellent value and very easy to use.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All files are committed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `Procfile` exists (for some platforms)
- [ ] Database file (`health_tracker.db`) is in `.gitignore` (it will be created on server)
- [ ] Content directory is committed
- [ ] Environment variables are documented

---

## 🔧 Platform-Specific Configurations

### For Koyeb:
Create `koyeb.toml` (optional):
```toml
[build]
  builder = "nixpacks"

[deploy]
  type = "web"
  command = "gunicorn app:app --bind 0.0.0.0:$PORT --port $PORT"
```

### For Railway:
Create `railway.json` (optional):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### For Fly.io:
Create `fly.toml`:
```toml
app = "health-tracker"
primary_region = "iad"

[build]

[env]
  PORT = "5000"

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[services]]
  protocol = "tcp"
  internal_port = 5000
```

---

## 🚀 Quick Start Commands

### Koyeb (Recommended)
1. Sign up at koyeb.com
2. Connect GitHub repo
3. Deploy!

### Railway
```bash
# Install Railway CLI (optional)
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Fly.io
```bash
fly launch
fly deploy
```

---

## 💡 Tips for 24/7 Deployment

1. **Database Persistence**: Ensure your database file persists. Most platforms provide persistent storage.

2. **Environment Variables**: Store sensitive data (like API keys) as environment variables, not in code.

3. **Logs**: Check platform logs regularly to monitor your app.

4. **Monitoring**: Set up basic monitoring/alerting if available.

5. **Backups**: Regularly backup your database file.

---

## 📞 Support

- **Koyeb**: https://www.koyeb.com/docs
- **Railway**: https://docs.railway.app
- **Fly.io**: https://fly.io/docs
- **Render**: https://render.com/docs

---

## 🎉 After Deployment

Once deployed:
1. Test all features
2. Share URL with family
3. Monitor for any issues
4. Set up regular backups

Your health tracker will now be accessible 24/7! 🚀

