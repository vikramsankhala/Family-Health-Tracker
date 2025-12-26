# Quick Deployment Guide

## Recommended: Render.com (Easiest & Free)

### Step-by-Step Instructions:

1. **Prepare Your Code**
   - Make sure all files are committed to a Git repository (GitHub, GitLab, or Bitbucket)

2. **Sign Up for Render**
   - Go to https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub (recommended) or email

3. **Create New Web Service**
   - Click "New +" button → Select "Web Service"
   - Connect your Git repository
   - Select the repository containing this health tracker

4. **Configure Settings**
   ```
   Name: health-tracker (or any name you prefer)
   Environment: Python 3
   Region: Choose closest to you
   Branch: main (or master)
   Root Directory: (leave empty)
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

5. **Advanced Settings** (Optional)
   - Plan: Free (sufficient for this app)
   - Auto-Deploy: Yes (deploys on every push)

6. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Your app will be live at: `https://health-tracker.onrender.com` (or your chosen name)

7. **Share the URL**
   - Once deployed, share the Render URL with your family members
   - Example: `https://health-tracker.onrender.com`

### Important Notes for Render:
- Free tier apps sleep after 15 minutes of inactivity (first request may be slow)
- Upgrade to paid plan ($7/month) for always-on service
- Files in Content/ directory will be included in deployment
- Comments.json will be created automatically

---

## Alternative: Railway.app

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python
6. Add start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
7. Deploy automatically happens
8. Get your URL from Railway dashboard

---

## Alternative: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly launch`
3. Follow prompts
4. Deploy: `fly deploy`
5. Get URL: `fly open`

---

## Testing Locally Before Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open browser to http://localhost:5000
```

---

## After Deployment Checklist

- [ ] Test the URL works
- [ ] Verify files in Content/ are accessible
- [ ] Test adding a comment
- [ ] Test AI assistant query
- [ ] Test report generation
- [ ] Share URL with family members

---

## Troubleshooting

**App won't start:**
- Check that `gunicorn` is in requirements.txt
- Verify Procfile exists with correct command
- Check Render/Railway logs for errors

**Files not showing:**
- Ensure Content/ directory is committed to Git
- Check file permissions

**AI not working:**
- Verify OpenAI API key is correct in app.py
- Check API usage limits on OpenAI dashboard

**Comments not saving:**
- Check that comments.json has write permissions
- Verify file is not in .gitignore (it shouldn't be)

---

## Need Help?

- Render Support: https://render.com/docs
- Railway Support: https://docs.railway.app
- Check application logs in your deployment platform dashboard

