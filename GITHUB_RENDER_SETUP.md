# MCUBE LUNA AI - GitHub & Render Deployment

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website (Easiest)

1. Go to https://github.com/new
2. Create new repository:
   - **Repository name:** `chatbot-app` (or your name)
   - **Description:** "MCUBE LUNA AI Support Chatbot"
   - **Public** (so you can use free Render)
   - **Add .gitignore:** Python (already done)
   - **License:** MIT (optional)
3. Click **Create repository**

You'll see: `https://github.com/YOUR_USERNAME/chatbot-app`

---

## Step 2: Push Code to GitHub

### From Terminal

```bash
# Navigate to project
cd '/Volumes/Santhosh _ Developments/chatbot-app'

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: MCUBE LUNA AI Chatbot"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/chatbot-app.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**First time push will ask for credentials:**
- Use your GitHub username
- Use a Personal Access Token as password (not your password):
  1. Go to https://github.com/settings/tokens
  2. Click "Generate new token (classic)"
  3. Check: `repo`, `gist`
  4. Copy token and use as password

---

## Step 3: Deploy to Render

### Go to Render and Create Service

1. Open https://render.com
2. Click **Sign up** (use GitHub)
3. Authorize with GitHub
4. Click **New +** → **Web Service**
5. Select your `chatbot-app` repo
6. Configure:

```
Name:                    mcube-luna-ai
Environment:             Python 3.11
Region:                  (keep default)
Branch:                  main
Build Command:           pip install -r backend/requirements.txt
Start Command:           cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
Plan:                    Free
```

7. Click **Create Web Service**

---

## Step 4: Wait & Get Your URL

Render will:
- Build your app (2-3 mins)
- Deploy it
- Give you a public URL

Example: `https://mcube-luna-ai.onrender.com`

---

## Step 5: Share with Team

Once deployed, share these URLs:

```
🎯 Chat Interface:
https://mcube-luna-ai.onrender.com

📊 Admin Panel:
https://mcube-luna-ai.onrender.com/admin.html

📖 API Documentation:
https://mcube-luna-ai.onrender.com/docs
```

---

## Add Environment Variables (Optional)

If using Groq or OpenAI:

1. In Render dashboard, go to your service
2. Click **Settings** → **Environment**
3. Add:
   ```
   GROQ_API_KEY=your_key_here
   AI_PROVIDER=groq
   ```
4. Click **Save**
5. Render will auto-redeploy

---

## Troubleshooting

### Build Failed
Check the build logs in Render:
1. Click your service
2. **Logs** tab
3. Look for error message
4. Common issues:
   - Missing files in git
   - Wrong Python version
   - Missing dependencies

### App Not Working
1. Check Render logs
2. Verify `.env` variables are set
3. Try restarting the service (click **Restart**)

### Make Changes & Redeploy
```bash
# After making changes locally
git add .
git commit -m "Your message"
git push origin main
```
Render auto-deploys on push!

---

## Important Notes

⚠️ **Free Tier Info:**
- Service auto-sleeps after 15 mins inactivity
- Wakes up on first request (takes 30 secs)
- Can add paid plan if needed

💾 **Data:**
- Knowledge base data persists in Render's storage
- Chat history stored in SQLite (may reset with deployments)
- Consider upgrading to PostgreSQL for production

---

## Full Step-by-Step Command List

```bash
# 1. Initialize git
cd '/Volumes/Santhosh _ Developments/chatbot-app'
git init

# 2. Add files
git add .
git config user.email "your@email.com"
git config user.name "Your Name"

# 3. First commit
git commit -m "Initial commit: MCUBE LUNA AI"

# 4. Add GitHub remote (REPLACE YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/chatbot-app.git
git branch -M main

# 5. Push to GitHub
git push -u origin main

# Then go to Render.com and follow steps above
```

---

**Need help?**
- GitHub Issues: https://github.com/YOUR_USERNAME/chatbot-app/issues
- Render Support: https://render.com/support
