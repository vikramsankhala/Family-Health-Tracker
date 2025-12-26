# Railway.app Deployment Guide

## ✅ Step 1: Code is on GitHub
Your code is successfully pushed to: **https://github.com/vikramsankhala/Family-Health-Tracker.git**

## 🚂 Step 2: Deploy to Railway

### Quick Setup (5 minutes)

1. **Go to Railway**
   - Visit: https://railway.app
   - Click "Start a New Project" or "Login"
   - Sign in with your **GitHub account**

2. **Create New Project**
   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Authorize Railway to access GitHub if prompted
   - Select repository: **vikramsankhala/Family-Health-Tracker**

3. **Railway Auto-Detection**
   - Railway will automatically detect Python
   - It will use `requirements.txt` for dependencies
   - It will use `Procfile` for start command

4. **Configure Start Command** (if needed)
   - Go to **Settings** → **Deploy**
   - Verify Start Command is: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Railway sets `$PORT` automatically

5. **Add Environment Variables** ⚠️ **CRITICAL**
   - Go to **Variables** tab
   - Click **"New Variable"**
   - Add these variables:

   **Variable 1:**
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `your-openai-api-key-here` (Get from https://platform.openai.com/api-keys)

   **Variable 2:**
   - **Name:** `SECRET_KEY`
   - **Value:** `vikram-health-tracker-secret-key-2025-railway`

6. **Deploy**
   - Railway will automatically start deploying
   - Wait 3-5 minutes for build to complete
   - Check **Logs** tab for progress

7. **Get Your URL**
   - Go to **Settings** → **Networking**
   - Railway generates a URL automatically
   - Example: `https://family-health-tracker.up.railway.app`
   - Click **"Generate Domain"** if not already generated

8. **Upgrade to Always-On** (Recommended)
   - Go to **Settings** → **Plan**
   - Select **"Developer"** plan ($5/month)
   - You get $5 free credit monthly = **FREE!**
   - This ensures 24/7 uptime (no sleeping)

## 🎉 Your App is Live!

Your Health Tracker is now accessible at: `https://your-app-name.up.railway.app`

### Default Login Credentials
- **Username:** `vikramsankhala`
- **Password:** `vikramsankhala`
- **Email:** `vikramsankhala@healthtracker.com` (optional)

## 📋 What's Included

✅ Health Tracker Data (from Excel files)  
✅ Diet Plan  
✅ Exercise Plan  
✅ To Do List  
✅ CGM (Continuous Glucose Monitoring)  
✅ AI Query Assistant (Health, Food, Lifestyle, Fitness)  
✅ Health Reports  
✅ Budget & Expense Tracking  
✅ Wearables Integration Guide  
✅ Mobile Streaming Guide  

## 🔧 Troubleshooting

### App Won't Start
- Check **Logs** tab in Railway dashboard
- Verify environment variables are set
- Ensure `gunicorn` is in requirements.txt
- Check start command is correct

### Database Issues
- Railway provides persistent storage
- Database file (`health_tracker.db`) is created automatically
- Data persists across deployments

### Environment Variables Not Working
- Double-check variable names (case-sensitive)
- Ensure no extra spaces
- Redeploy after adding variables

### API Key Issues
- Verify `OPENAI_API_KEY` is set correctly
- Check API usage limits on OpenAI dashboard

## 📊 Monitoring

- **Logs:** View real-time logs in Railway dashboard
- **Metrics:** Check CPU/Memory usage
- **Deployments:** See deployment history

## 🔄 Updating Your App

Railway automatically deploys when you push to GitHub:
```bash
git add .
git commit -m "Your changes"
git push
```

Railway will detect the push and redeploy automatically!

## 💰 Cost

- **Free Tier:** $5 credit/month (enough for small apps)
- **Developer Plan:** $5/month for always-on (recommended)
- **Pro Plan:** $20/month for more resources

**With $5 free credit monthly, Developer plan = FREE!**

## 📞 Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check application logs in Railway dashboard

---

**Your Health Tracker is now live 24/7! 🚀**

Share the Railway URL with your family members to access the tracker.

