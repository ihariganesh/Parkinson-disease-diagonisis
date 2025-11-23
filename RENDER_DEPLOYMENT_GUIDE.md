# 🚀 Deploy Backend to Render (FREE Tier) - Complete Guide

## ✅ Why Render?

- ✅ **TRUE FREE TIER** (no credit card required initially)
- ✅ Supports Python/FastAPI
- ✅ Free PostgreSQL database included
- ✅ Handles large ML models (511MB is fine)
- ✅ Auto-deploys from GitHub
- ✅ Free SSL certificates
- ✅ Simple configuration

**Free Tier Limits:**
- 750 hours/month (enough for 1 app running 24/7)
- 512MB RAM
- Sleeps after 15 min of inactivity (wakes up on request)
- Perfect for development/testing!

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### **Step 1: Sign Up for Render**

1. Go to: https://render.com
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest - auto-connects your repos)
4. Authorize Render to access your GitHub

---

### **Step 2: Create PostgreSQL Database (FREE)**

**Do this FIRST before deploying backend!**

1. In Render Dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Configure:
   ```
   Name: parkinson-db
   Database: parkinson_db
   User: parkinson_user
   Region: Choose closest to you (e.g., Oregon/Frankfurt)
   Plan: FREE
   ```
4. Click **"Create Database"**
5. Wait 2-3 minutes for database creation
6. **IMPORTANT:** Copy the **"Internal Database URL"** (starts with `postgresql://`)
   - You'll need this for backend environment variables!

**Internal Database URL format:**
```
postgresql://parkinson_user:password@dpg-xxxx-a.oregon-postgres.render.com/parkinson_db
```

---

### **Step 3: Deploy Backend (Web Service)**

1. In Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Find and select: `ihariganesh/Parkinson-disease-diagonisis`
5. Click **"Connect"**

---

### **Step 4: Configure Web Service**

Fill in these settings **CAREFULLY:**

#### **Basic Settings:**
```
Name: parkinson-backend
Region: Same as your database (e.g., Oregon)
Branch: main
Runtime: Python 3
```

#### **Root Directory (CRITICAL!):**
```
parkinson-app/backend
```
⚠️ **This tells Render where your backend code is!**

#### **Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

#### **Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### **Plan:**
```
FREE
```

---

### **Step 5: Add Environment Variables**

Scroll down to **"Environment Variables"** section and add these:

#### **Required Variables:**

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | Paste your PostgreSQL Internal URL from Step 2 | ⚠️ CRITICAL! |
| `SECRET_KEY` | `_E_LtGF8CxjkDqxZ4f20Ifhh0aPIGmTHCzd-7rXSw-U` | Use the one I generated |
| `GEMINI_API_KEY` | Your new Gemini API key | Get from https://aistudio.google.com/app/apikey |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry |
| `ENVIRONMENT` | `production` | Environment mode |
| `DEBUG` | `false` | Turn off debug in production |
| `PYTHONUNBUFFERED` | `1` | See logs in real-time |
| `CORS_ORIGINS` | `http://localhost:5173` | Update after Vercel deployment |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Same as above |
| `UPLOAD_DIR` | `/tmp/uploads` | File upload directory |
| `MAX_FILE_SIZE` | `104857600` | 100MB max upload |
| `MODEL_PATH` | `/app/models` | ML models location |
| `ENABLE_GPU` | `false` | No GPU on free tier |

**⚠️ IMPORTANT:** The `DATABASE_URL` from your Render PostgreSQL is automatically secure and works immediately!

---

### **Step 6: Advanced Settings (Optional but Recommended)**

Click **"Advanced"** and configure:

#### **Health Check Path:**
```
/health
```

#### **Auto-Deploy:**
```
✓ Enable (checkbox checked)
```
This auto-deploys when you push to GitHub!

---

### **Step 7: Deploy!**

1. Click **"Create Web Service"** button at the bottom
2. Render will start building (this takes **5-10 minutes** due to ML models)
3. Watch the build logs - you'll see:
   ```
   ==> Downloading buildpack... done
   ==> Detected Python app
   ==> Installing Python 3.11
   ==> Installing dependencies from requirements.txt
   ==> Installing tensorflow, torch, etc. (this takes time!)
   ==> Build successful!
   ==> Deploying...
   ==> Service live at: https://parkinson-backend.onrender.com
   ```

4. **WAIT!** Don't refresh or cancel. ML model installation takes time.

---

## ✅ **After Successful Deployment**

### **Step 8: Get Your Backend URL**

Your backend will be live at:
```
https://parkinson-backend.onrender.com
```

Or similar (Render assigns a unique URL)

### **Step 9: Test Your Backend**

#### **Test 1: Health Check**
```bash
curl https://parkinson-backend.onrender.com/health
```

**Expected response:**
```json
{
  "success": true,
  "message": "ParkinsonCare API is running",
  "version": "1.0.0"
}
```

#### **Test 2: API Documentation**
Visit in browser:
```
https://parkinson-backend.onrender.com/docs
```

You should see FastAPI Swagger UI with all your endpoints!

---

### **Step 10: Update Frontend (Vercel)**

Now connect your frontend to the backend:

1. Go to **Vercel Dashboard**
2. Select your frontend project
3. Go to **Settings** → **Environment Variables**
4. Add or update:
   ```
   Key: VITE_API_URL
   Value: https://parkinson-backend.onrender.com
   Environment: Production
   ```
5. Click **"Save"**
6. Go to **"Deployments"** tab
7. Click **"Redeploy"** on the latest deployment
8. Select **"Use existing Build Cache"** → **"Redeploy"**

---

### **Step 11: Update CORS (CRITICAL!)**

After Vercel deployment, get your Vercel URL (e.g., `https://your-app.vercel.app`)

Then update backend CORS:

1. Go to **Render Dashboard** → Your backend service
2. Go to **"Environment"** tab
3. Update these variables:
   ```
   CORS_ORIGINS = https://your-app.vercel.app,http://localhost:5173
   ALLOWED_ORIGINS = https://your-app.vercel.app,http://localhost:5173
   ```
4. Click **"Save Changes"**
5. Render will **auto-redeploy** (takes 2-3 minutes)

---

## 🎯 **Complete Configuration Files**

I've already created these in your repo (they work for Render too!):

### **✅ Files Ready:**
- `backend/Procfile` ✅
- `backend/requirements.txt` ✅
- `backend/runtime.txt` ✅
- `backend/app/main.py` ✅

**Render auto-detects these!** No additional files needed.

---

## 🐛 **Troubleshooting Common Issues**

### **Issue 1: Build takes forever (10+ minutes)**
**Cause:** Large ML models (TensorFlow, PyTorch, etc.)
**Solution:** This is **normal**! Just wait. Free tier is slower.
**First deployment:** 10-15 minutes
**Subsequent deploys:** 3-5 minutes (cached)

### **Issue 2: "Service Unavailable" after deployment**
**Cause:** App is starting up (cold start on free tier)
**Solution:** Wait 30 seconds, refresh. First request wakes up the service.

### **Issue 3: Database connection error**
**Cause:** Wrong `DATABASE_URL` or database not created
**Solution:** 
- Go to Render → PostgreSQL database
- Copy **"Internal Database URL"** (not External!)
- Update `DATABASE_URL` in backend environment variables
- Redeploy

### **Issue 4: "No module named 'app'"**
**Cause:** Wrong root directory
**Solution:** 
- Settings → Root Directory = `parkinson-app/backend`
- Redeploy

### **Issue 5: CORS errors in frontend**
**Cause:** Vercel URL not in CORS_ORIGINS
**Solution:**
- Add your Vercel URL to `CORS_ORIGINS`
- Format: `https://your-app.vercel.app,http://localhost:5173`
- No spaces, comma-separated

---

## ⚡ **Free Tier Limitations & Solutions**

### **Limitation 1: Service Sleeps After 15 Min Inactivity**
**Impact:** First request after sleep takes 30-60 seconds
**Solutions:**
- Use a **free uptime monitoring service** (e.g., UptimeRobot) to ping your API every 14 minutes
- Accept the cold start (fine for demos/testing)
- Upgrade to paid tier ($7/month) for always-on

### **Limitation 2: 512MB RAM**
**Impact:** Might be tight for all 3 ML models at once
**Solutions:**
- Models load on-demand (should work fine)
- If crashes, reduce model size or upgrade
- Free tier is sufficient for testing!

### **Limitation 3: Limited Database Storage**
**Impact:** 1GB free database storage
**Solutions:**
- Clean up old files periodically
- Use external storage (AWS S3 free tier) for images
- Upgrade if needed ($7/month for 10GB)

---

## 💰 **Cost Comparison**

### **Render Free Tier (What You Get):**
```
✓ Web Service: FREE (750 hours/month)
✓ PostgreSQL: FREE (1GB storage)
✓ SSL Certificate: FREE
✓ Auto-deploys: FREE
✓ Custom domain: FREE
✓ No credit card required: YES!

Total: $0/month 🎉
```

### **Render Paid (If You Upgrade Later):**
```
Web Service: $7/month (always-on, 512MB RAM)
PostgreSQL: $7/month (10GB storage)
Total: $14/month
```

**vs Railway:**
```
Minimum: $5/month (credit required)
```

**Render wins for free tier!** ✅

---

## 📋 **Deployment Checklist**

### **Before Deploying:**
- [x] ✅ GitHub repo pushed (commit 4361683)
- [x] ✅ Configuration files ready
- [ ] 🟡 Render account created
- [ ] 🟡 PostgreSQL database created

### **During Deployment:**
- [ ] 🟡 Web Service created
- [ ] 🟡 Root directory set to `parkinson-app/backend`
- [ ] 🟡 Build command set
- [ ] 🟡 Start command set
- [ ] 🟡 Environment variables added (especially DATABASE_URL!)
- [ ] 🟡 Health check path set to `/health`

### **After Deployment:**
- [ ] 🟡 Backend URL obtained
- [ ] 🟡 Health check passes
- [ ] 🟡 API docs accessible
- [ ] 🟡 Vercel VITE_API_URL updated
- [ ] 🟡 CORS updated with Vercel URL
- [ ] 🟡 End-to-end test successful

---

## 🎓 **Quick Tips**

### **Tip 1: Monitor Logs**
- Render Dashboard → Your Service → **"Logs"** tab
- Real-time logs help debug issues

### **Tip 2: Manual Deploy**
- If auto-deploy fails, click **"Manual Deploy"** → **"Deploy latest commit"**

### **Tip 3: Environment Variables**
- Changes to environment variables trigger auto-redeploy
- No need to manually redeploy after changing vars

### **Tip 4: Database Backups**
- Free tier: Manual backups only
- Download backup: Dashboard → PostgreSQL → **"Backups"** tab

### **Tip 5: Keep Service Awake**
Use **UptimeRobot** (free):
1. Sign up at https://uptimerobot.com
2. Add monitor: `https://parkinson-backend.onrender.com/health`
3. Interval: 5 minutes
4. Service never sleeps! ✅

---

## 🚀 **Quick Start Commands Summary**

### **For Render Deployment:**
```bash
# No CLI needed! Everything via dashboard:

1. render.com → Sign up with GitHub
2. New + → PostgreSQL → Create (get DATABASE_URL)
3. New + → Web Service → Connect repo
4. Configure:
   - Root: parkinson-app/backend
   - Build: pip install -r requirements.txt
   - Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
5. Add environment variables (including DATABASE_URL)
6. Create Web Service → Wait 10 minutes → Done! ✅
```

---

## 📞 **Need Help?**

### **Render Resources:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Support: support@render.com

### **Your Environment Variables (Copy-Paste Ready):**
```bash
DATABASE_URL=<paste-from-render-postgresql>
SECRET_KEY=_E_LtGF8CxjkDqxZ4f20Ifhh0aPIGmTHCzd-7rXSw-U
GEMINI_API_KEY=<your-gemini-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=false
PYTHONUNBUFFERED=1
CORS_ORIGINS=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=104857600
MODEL_PATH=/app/models
ENABLE_GPU=false
```

**Remember to update CORS_ORIGINS after Vercel deployment!**

---

## ✅ **Summary**

**Render is PERFECT for your project because:**
1. ✅ Truly free (no credit card needed)
2. ✅ Supports Python + ML models
3. ✅ Free PostgreSQL included
4. ✅ Simple configuration
5. ✅ Auto-deploys from GitHub
6. ✅ Perfect for development/demo

**Next Steps:**
1. Create PostgreSQL database on Render (get DATABASE_URL)
2. Create Web Service (point to `parkinson-app/backend`)
3. Add environment variables (especially DATABASE_URL!)
4. Deploy and wait 10 minutes
5. Test with `/health` endpoint
6. Update Vercel with backend URL
7. Update CORS with Vercel URL
8. Done! 🎉

**Start here: https://render.com → Sign up with GitHub!** 🚀
