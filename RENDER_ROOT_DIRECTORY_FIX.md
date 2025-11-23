# 🔥 RENDER ROOT DIRECTORY FIX - SOLVED!

## ❌ Error You Saw:
```
Service Root Directory "/opt/render/project/src/parkinson-app/backend" is missing.
builder.sh: line 61: cd: /opt/render/project/src/parkinson-app/backend: No such file or directory
```

## ✅ THE FIX

**Your GitHub repository structure is:**
```
Parkinson-disease-diagonisis/    ← GitHub repo root
├── backend/                      ← Backend is HERE (at root level)
│   ├── app/
│   ├── requirements.txt
│   ├── Procfile
│   └── ...
├── frontend/                     ← Frontend at root level
└── [other files]
```

**NOT:**
```
Parkinson-disease-diagonisis/
└── parkinson-app/
    └── backend/              ← It's NOT nested like this!
```

## 🎯 CORRECT RENDER SETTINGS

When setting up Render Web Service, use:

### **Root Directory:**
```
backend
```

**NOT** `parkinson-app/backend`!

### **Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

### **Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🚀 HOW TO FIX IN RENDER DASHBOARD

### **Option 1: Update Existing Service**
1. Go to Render Dashboard
2. Click on your `parkinson-backend` service
3. Go to **"Settings"** tab
4. Find **"Root Directory"** section
5. Change from `parkinson-app/backend` to just: **`backend`**
6. Click **"Save Changes"**
7. Render will auto-redeploy with the correct path!

### **Option 2: Delete and Recreate (Easier)**
1. Go to Render Dashboard
2. Delete the failing service
3. Click **"New +"** → **"Web Service"**
4. Connect repo: `ihariganesh/Parkinson-disease-diagonisis`
5. Configure:
   ```
   Name: parkinson-backend
   Runtime: Python 3
   Root Directory: backend          ← CORRECT!
   Build: pip install -r requirements.txt
   Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
6. Add environment variables
7. Create Web Service

---

## 📁 render.yaml File (Already Created!)

I've created `render.yaml` in your repo root with the **correct path**:

```yaml
services:
  - type: web
    name: parkinson-backend
    runtime: python
    rootDir: backend                ← CORRECT!
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
```

This file tells Render exactly where to find your backend!

---

## ✅ VERIFICATION

After fixing, Render should successfully:
1. ✅ Clone your repo
2. ✅ Navigate to `/opt/render/project/src/backend`
3. ✅ Find `requirements.txt`
4. ✅ Find `app/main.py`
5. ✅ Build successfully!

---

## 🎯 QUICK FIX CHECKLIST

- [ ] Delete failing Render service (or update Root Directory in Settings)
- [ ] Create new Web Service
- [ ] Root Directory = **`backend`** (not `parkinson-app/backend`)
- [ ] Build Command = `pip install -r requirements.txt`
- [ ] Start Command = `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Add environment variables (DATABASE_URL, SECRET_KEY, etc.)
- [ ] Deploy!

---

## 💡 WHY THIS HAPPENED

**Local structure (on your computer):**
```
/home/hari/Downloads/parkinson/
└── parkinson-app/            ← Extra folder locally
    ├── backend/
    └── frontend/
```

**GitHub structure (in repo):**
```
Parkinson-disease-diagonisis/  ← Repo root
├── backend/                    ← Directly in root!
└── frontend/
```

When you pushed to GitHub, you were **inside** the `parkinson-app` folder, so Git pushed the contents (backend/ and frontend/) to the repo root!

---

## 🚀 DEPLOY NOW

**Correct Root Directory: `backend`**

That's it! This will fix the error. Go update your Render service settings now! ✅
