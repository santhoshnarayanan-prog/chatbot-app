# MCUBE LUNA AI - Deployment Guide

## Deploy to Render (Free)

### Prerequisites
- GitHub account
- Render account (free at render.com)

### Steps to Deploy

#### 1. Push Code to GitHub
```bash
cd /Volumes/Santhosh\ _\ Developments/chatbot-app
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/chatbot-app.git
git branch -M main
git push -u origin main
```

#### 2. Create Render Service
1. Go to https://render.com
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Select your `chatbot-app` repository
5. Configure:
   - **Name**: `mcube-luna-ai` (or any name)
   - **Environment**: `Python 3.11`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

#### 3. Set Environment Variables (if needed)
1. Go to Service Settings → Environment
2. Add if using custom AI providers:
   - `GROQ_API_KEY=your_key`
   - `OPENAI_API_KEY=your_key` (optional)
   - `AI_PROVIDER=groq` (default)

#### 4. Deploy
- Click "Deploy"
- Wait 2-3 minutes
- Your URL will be: `https://mcube-luna-ai.onrender.com`

### Share with Team
```
🎯 Chat Interface: https://mcube-luna-ai.onrender.com
📊 Admin Panel: https://mcube-luna-ai.onrender.com/admin.html
📖 API Docs: https://mcube-luna-ai.onrender.com/docs
```

---

## Alternative: Using Ngrok (Quick Demo - 2 hours)

### Setup Ngrok
1. Download from https://ngrok.com
2. Authenticate: `ngrok config add-authtoken YOUR_TOKEN`
3. Run:
```bash
cd /Volumes/Santhosh\ _\ Developments/chatbot-app/backend
./venv311/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 &
ngrok http 8000
```

You get a public URL like: `https://abc123.ngrok.io`

---

## Deploy to Railway (Also Free)

1. Go to https://railway.app
2. Sign in with GitHub
3. Create new project → Import from GitHub
4. Select your repository
5. Add environment variables if needed
6. Deploy

Your URL will be: `https://your-project.up.railway.app`

---

## Important Notes

⚠️ **Free Tier Limitations:**
- Render: Auto-sleeps after 15 mins of inactivity (wakes on request)
- Railway: Limited to $5/month free credit
- Knowledge base persists but uses local SQLite
- Chat history resets if service restarts

💾 **Database:**
- Currently using SQLite (local file)
- For production, upgrade to PostgreSQL

🔐 **Security:**
- Change `allow_origins=["*"]` to specific domains before production
- Set strong environment variables
- Use HTTPS (auto-enabled on Render/Railway)

---

## Quick Start Commands

### Local Development
```bash
cd backend
./venv311/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access: `http://your-local-ip:8000`

### Check Your Local IP
```bash
# macOS/Linux
ipconfig getifaddr en0    # or en1, en2, etc.

# Get all options
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Share with team: `http://YOUR_LOCAL_IP:8000`

