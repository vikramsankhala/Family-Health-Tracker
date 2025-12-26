# Railway.app Deployment Guide

## Step-by-Step Deployment Instructions

### 1. Push Code to GitHub ✅
Your code is already pushed to: https://github.com/vikramsankhala/Family-Health-Tracker.git

### 2. Sign Up for Railway

1. Go to **https://railway.app**
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with your **GitHub account** (recommended)

### 3. Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub account if prompted
4. Select your repository: **vikramsankhala/Family-Health-Tracker**

### 4. Configure Deployment

Railway will auto-detect Python, but you need to configure:

1. **Go to Settings** → **Deploy**
2. **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
3. Railway automatically sets the `$PORT` environment variable

### 5. Add Environment Variables

Go to **Variables** tab and add:

```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your-secret-key-change-this-in-production
```

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 6. Upgrade to Always-On Plan (Optional but Recommended)

For 24/7 uptime:

1. Go to **Settings** → **Plan**
2. Select **"Developer"** plan ($5/month)
3. You get $5 free credit monthly, so it's effectively free!

### 7. Deploy

1. Railway will automatically deploy when you connect the repo
2. Wait 2-5 minutes for the build to complete
3. Your app will be live at: `https://your-app-name.up.railway.app`

### 8. Get Your URL

1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"** if not already generated
3. Copy your Railway URL (e.g., `https://family-health-tracker.up.railway.app`)

### 9. Share with Family

Share your Railway URL with family members:
- They can view all health files
- They can see comments and budgets
- Only you (with login) can add/edit/delete data

## Default Login Credentials

After deployment, use:
- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change the password after first login!

## Troubleshooting

### App Won't Start
- Check **Logs** tab in Railway dashboard
- Verify `gunicorn` is in `requirements.txt`
- Ensure start command is correct

### Database Issues
- Railway provides persistent storage
- Database file (`health_tracker.db`) will be created automatically
- Data persists across deployments

### Environment Variables Not Working
- Double-check variable names in Railway dashboard
- Ensure no extra spaces
- Redeploy after adding variables

## Monitoring

- **Logs**: View real-time logs in Railway dashboard
- **Metrics**: Check CPU/Memory usage
- **Deployments**: See deployment history

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

## Cost

- **Free Tier**: $5 credit/month (enough for small apps)
- **Developer Plan**: $5/month for always-on (recommended)
- **Pro Plan**: $20/month for more resources

Your app is now live 24/7! 🚀

