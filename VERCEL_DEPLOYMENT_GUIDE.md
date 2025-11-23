# Deploying Parkinson's Disease Diagnosis System to Vercel

## 🎯 Overview

This guide will help you deploy the **frontend** of your Parkinson's diagnosis system to Vercel. Since this is a full-stack application with a Python backend, we'll deploy:

- **Frontend (React + Vite)** → Vercel
- **Backend (FastAPI + Python)** → Railway/Render/Fly.io (separate deployment)

---

## ⚠️ Important: Architecture Understanding

Your project structure:
```
parkinson-app/
├── frontend/        ← Deploy to Vercel
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/         ← Deploy separately (Railway/Render)
│   ├── app/
│   ├── requirements.txt
│   └── main.py
└── ml_models/       ← Include in backend deployment
```

**You CANNOT deploy the full project to Vercel** because:
- Vercel is optimized for frontend/Node.js
- Your backend is Python (FastAPI)
- Your ML models need Python runtime

**Solution:** Deploy frontend on Vercel, backend elsewhere.

---

## 🚀 STEP 1: Prepare Frontend for Vercel

### 1.1 Create Vercel Configuration

Create `vercel.json` in the `frontend` directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 1.2 Update Environment Variables

Create `.env.example` in `frontend/`:

```bash
# API URL - Replace with your backend URL after deployment
VITE_API_URL=http://localhost:8000

# Optional: Analytics, monitoring, etc.
VITE_APP_ENV=production
```

### 1.3 Update API Client Configuration

Ensure your API client uses the environment variable:

**frontend/src/services/api.ts** should have:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## 🔧 STEP 2: Deploy to Vercel (Frontend Only)

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel**
   - Visit: https://vercel.com
   - Sign in with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Select your GitHub repository: `ihariganesh/Parkinson-disease-diagonisis`
   - Click "Import"

3. **Configure Project Settings**

   **Project Name:**
   ```
   parkinson-disease-diagnosis
   ```

   **Framework Preset:**
   ```
   Vite
   ```

   **Root Directory:**
   ```
   parkinson-app/frontend
   ```
   ⚠️ **IMPORTANT:** Click "Edit" and set this!

   **Build Settings:**
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `dist` (auto-detected)
   - Install Command: `npm install` (auto-detected)

4. **Environment Variables**

   Click "Environment Variables" and add:

   | Name | Value | Environment |
   |------|-------|-------------|
   | `VITE_API_URL` | `https://your-backend-url.com` | Production |
   | `VITE_API_URL` | `http://localhost:8000` | Development |

   ⚠️ **You'll need to deploy backend first to get this URL!**

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)
   - Get your URL: `https://parkinson-disease-diagnosis.vercel.app`

---

### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Navigate to Frontend Directory**
   ```bash
   cd /home/hari/Downloads/parkinson/parkinson-app/frontend
   ```

4. **Deploy**
   ```bash
   vercel
   ```

5. **Answer Configuration Questions**
   ```
   ? Set up and deploy? Yes
   ? Which scope? Your account
   ? Link to existing project? No
   ? What's your project's name? parkinson-disease-diagnosis
   ? In which directory is your code located? ./
   ? Want to override settings? Yes
   ? Build Command: npm run build
   ? Output Directory: dist
   ? Development Command: npm run dev
   ```

6. **Deploy to Production**
   ```bash
   vercel --prod
   ```

---

## 🐍 STEP 3: Deploy Backend (Required!)

Your frontend won't work without the backend API. Here are your options:

### Option A: Railway (Recommended - Easy & Free Tier)

1. **Sign Up**
   - Go to: https://railway.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `ihariganesh/Parkinson-disease-diagonisis`

3. **Configure Service**
   - Service name: `parkinson-backend`
   - Root Directory: `parkinson-app/backend`
   - Build command: Auto-detected (Python)
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   ```
   DATABASE_URL=your-postgres-url
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-key
   CORS_ORIGINS=https://parkinson-disease-diagnosis.vercel.app
   ```

5. **Deploy**
   - Railway will auto-deploy
   - Get your backend URL: `https://parkinson-backend.railway.app`

6. **Update Vercel Environment Variable**
   - Go back to Vercel dashboard
   - Update `VITE_API_URL` to your Railway URL
   - Redeploy frontend

---

### Option B: Render (Free Tier)

1. **Sign Up**
   - Go to: https://render.com
   - Sign in with GitHub

2. **New Web Service**
   - Click "New" → "Web Service"
   - Connect repository: `ihariganesh/Parkinson-disease-diagonisis`

3. **Configure**
   ```
   Name: parkinson-backend
   Root Directory: parkinson-app/backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables** (same as Railway)

5. **Deploy** - Get URL and update Vercel

---

### Option C: Fly.io (Advanced)

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Navigate to Backend**
   ```bash
   cd /home/hari/Downloads/parkinson/parkinson-app/backend
   ```

4. **Create Fly App**
   ```bash
   fly launch --name parkinson-backend
   ```

5. **Set Environment Variables**
   ```bash
   fly secrets set DATABASE_URL=your-db-url
   fly secrets set SECRET_KEY=your-key
   fly secrets set GEMINI_API_KEY=your-key
   ```

6. **Deploy**
   ```bash
   fly deploy
   ```

---

## 📁 STEP 4: Required Files Setup

Let me create the necessary configuration files for you:

### 4.1 Frontend Vercel Configuration

**File: `frontend/vercel.json`**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 4.2 Backend Railway Configuration

**File: `backend/railway.json`**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 4.3 Backend Dockerfile (Optional - for any platform)

**File: `backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔐 STEP 5: Environment Variables Setup

### Frontend (.env.production)
```bash
VITE_API_URL=https://your-backend-url.railway.app
VITE_APP_ENV=production
```

### Backend
```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=your-super-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://parkinson-disease-diagnosis.vercel.app,http://localhost:5173

# AI Services
GEMINI_API_KEY=your-gemini-api-key-here

# File Storage
UPLOAD_DIR=/tmp/uploads
MAX_UPLOAD_SIZE=10485760

# ML Models
MODEL_PATH=/app/ml_models
```

---

## ✅ STEP 6: Deployment Checklist

### Pre-Deployment
- [ ] Frontend builds successfully locally (`npm run build`)
- [ ] Backend runs successfully locally (`uvicorn app.main:app`)
- [ ] Environment variables documented
- [ ] API endpoints tested
- [ ] CORS configured properly

### Frontend Deployment (Vercel)
- [ ] Repository pushed to GitHub
- [ ] Vercel account created
- [ ] Project imported to Vercel
- [ ] Root directory set to `parkinson-app/frontend`
- [ ] Framework set to "Vite"
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] Frontend URL works

### Backend Deployment (Railway/Render/Fly.io)
- [ ] Platform account created
- [ ] Project created from GitHub repo
- [ ] Root directory set to `parkinson-app/backend`
- [ ] Environment variables configured
- [ ] Database connected (if using)
- [ ] Deployment successful
- [ ] API endpoints accessible
- [ ] Health check endpoint works

### Integration
- [ ] Frontend `VITE_API_URL` updated with backend URL
- [ ] Frontend redeployed with new API URL
- [ ] CORS origins include frontend URL
- [ ] Backend redeployed with CORS update
- [ ] End-to-end testing successful

---

## 🧪 STEP 7: Testing Deployment

### Test Frontend
```bash
# Visit your Vercel URL
https://parkinson-disease-diagnosis.vercel.app

# Check these pages:
- Homepage loads ✓
- Login works ✓
- Registration works ✓
- Dashboard accessible ✓
```

### Test Backend API
```bash
# Health check
curl https://your-backend.railway.app/health

# API docs
https://your-backend.railway.app/docs

# Test endpoint
curl https://your-backend.railway.app/api/v1/status
```

### Test Integration
1. Open frontend in browser
2. Open Developer Console (F12)
3. Try to login
4. Check Network tab for API calls
5. Verify responses from backend

---

## 🐛 Common Issues & Solutions

### Issue 1: "Failed to fetch" errors
**Problem:** Frontend can't reach backend
**Solution:**
- Check CORS configuration in backend
- Verify `VITE_API_URL` is correct
- Check backend is running
- Verify backend URL is accessible

### Issue 2: Build fails on Vercel
**Problem:** npm dependencies or build errors
**Solution:**
- Check `package.json` is correct
- Verify all dependencies installed locally
- Check build command works locally
- Review Vercel build logs

### Issue 3: API returns 404
**Problem:** Backend routes not found
**Solution:**
- Check backend is deployed
- Verify API endpoints exist
- Check route prefixes match
- Review backend logs

### Issue 4: Environment variables not working
**Problem:** Config not loaded
**Solution:**
- Restart Vercel deployment
- Check variable names match exactly
- Verify variables in correct environment
- Check for typos

### Issue 5: ML models not loading
**Problem:** Models too large for serverless
**Solution:**
- Deploy backend on Railway/Render (not serverless)
- Use persistent storage
- Check model file paths
- Verify models included in deployment

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  USER BROWSER                                           │
│  │                                                      │
│  └──► Frontend (Vercel)                                │
│       https://parkinson-diagnosis.vercel.app           │
│       │                                                 │
│       │ API Calls                                       │
│       │                                                 │
│       └──► Backend API (Railway/Render)                │
│            https://parkinson-backend.railway.app       │
│            │                                            │
│            ├──► PostgreSQL Database                     │
│            ├──► ML Models (DaT, Voice, Handwriting)    │
│            ├──► Gemini AI (Recommendations)            │
│            └──► File Storage                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 💰 Cost Estimate

### Free Tier (Recommended for Testing)
```
Vercel (Frontend):
- Free tier: 100GB bandwidth/month
- Unlimited deployments
- Custom domain
Cost: $0/month

Railway (Backend):
- Free tier: $5 credit/month
- 500MB RAM
- 1GB disk
Cost: $0-5/month

Total: $0-5/month
```

### Production Tier
```
Vercel Pro:
- 1TB bandwidth
- Advanced analytics
Cost: $20/month

Railway Pro:
- 8GB RAM
- 100GB disk
- Priority support
Cost: $20/month

Total: $40/month
```

---

## 🚀 Quick Start Commands

### Deploy Frontend to Vercel
```bash
cd /home/hari/Downloads/parkinson/parkinson-app/frontend
npm install -g vercel
vercel login
vercel --prod
```

### Deploy Backend to Railway
```bash
# Via Railway Dashboard (easier)
# 1. Go to railway.app
# 2. Connect GitHub repo
# 3. Set root: parkinson-app/backend
# 4. Deploy!
```

---

## 📝 Post-Deployment Tasks

1. **Custom Domain (Optional)**
   - Vercel: Add custom domain in dashboard
   - Railway: Add custom domain in settings

2. **Monitoring Setup**
   - Vercel Analytics (built-in)
   - Railway Logs (built-in)
   - Set up error tracking (Sentry, LogRocket)

3. **Database Backup**
   - Enable automatic backups on Railway
   - Set backup schedule

4. **SSL Certificates**
   - Auto-enabled on Vercel
   - Auto-enabled on Railway

5. **Performance Optimization**
   - Enable Vercel Edge Network
   - Configure caching headers
   - Optimize images

---

## 🎯 Next Steps After Deployment

1. **Test thoroughly** - All features working?
2. **Share URL** - With team/stakeholders
3. **Monitor** - Check logs and performance
4. **Iterate** - Fix bugs, add features
5. **Scale** - Upgrade tiers as needed

---

## 📞 Support & Resources

**Vercel:**
- Docs: https://vercel.com/docs
- Support: https://vercel.com/support

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**This Project:**
- GitHub: https://github.com/ihariganesh/Parkinson-disease-diagonisis
- Issues: Report bugs via GitHub Issues

---

## ✅ Summary

**To deploy your project:**

1. ✅ **Frontend to Vercel**
   - Root: `parkinson-app/frontend`
   - Framework: Vite
   - Deploy!

2. ✅ **Backend to Railway**
   - Root: `parkinson-app/backend`
   - Add environment variables
   - Deploy!

3. ✅ **Connect them**
   - Update `VITE_API_URL` in Vercel
   - Update CORS in Railway
   - Test!

**Your app will be live at:**
- Frontend: `https://parkinson-diagnosis.vercel.app`
- Backend: `https://parkinson-backend.railway.app`

---

**Ready to deploy? Let's start with the frontend on Vercel!** 🚀
