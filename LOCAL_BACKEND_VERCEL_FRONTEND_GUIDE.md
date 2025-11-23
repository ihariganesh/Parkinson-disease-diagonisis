# 🚀 Run Backend Locally + Deploy Frontend to Vercel

## ✅ What You Want:
- ✅ Backend running on your computer (VS Code)
- ✅ Frontend deployed on Vercel (public access)
- ✅ Others can access the frontend
- ✅ Frontend connects to your local backend

---

## 🎯 **The Challenge**

**Problem:** Vercel frontend (public) can't directly access `localhost:8000` (your computer)

**Why?** `localhost` only works on YOUR computer. Others can't reach it.

**Solution:** Use a **tunnel service** (ngrok/localtunnel) to expose your local backend temporarily.

---

## 🚀 **Method 1: Using ngrok (RECOMMENDED)**

### **Step 1: Install ngrok**

**On Linux/Mac:**
```bash
# Download ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok

# Or use snap (easier)
sudo snap install ngrok
```

**Or download directly:**
```bash
cd ~/Downloads
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### **Step 2: Sign up for ngrok (Free)**

1. Go to: https://dashboard.ngrok.com/signup
2. Sign up (free account)
3. Get your **authtoken** from dashboard
4. Run:
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
   ```

### **Step 3: Start Your Backend**

In VS Code terminal:
```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Step 4: Expose Backend with ngrok**

Open a **NEW terminal** and run:
```bash
ngrok http 8000
```

You'll see output like:
```
ngrok                                                                                                                                                                   
Session Status                online                                                                                                                                    
Account                       your-email@example.com (Plan: Free)                                                                                                       
Version                       3.5.0                                                                                                                                     
Region                        United States (us)                                                                                                                        
Latency                       -                                                                                                                                         
Web Interface                 http://127.0.0.1:4040                                                                                                                     
Forwarding                    https://abc123def.ngrok-free.app -> http://localhost:8000                                                                                

Connections                   ttl     opn     rt1     rt5     p50     p90                                                                                               
                              0       0       0.00    0.00    0.00    0.00                                                                                              
```

**Copy the HTTPS URL:** `https://abc123def.ngrok-free.app`

### **Step 5: Update CORS in Backend**

Edit `backend/.env`:
```bash
# Add ngrok URL to CORS
CORS_ORIGINS=https://abc123def.ngrok-free.app,https://your-vercel-app.vercel.app,http://localhost:5173
ALLOWED_ORIGINS=https://abc123def.ngrok-free.app,https://your-vercel-app.vercel.app,http://localhost:5173
```

**Restart your backend** (Ctrl+C and run uvicorn again)

### **Step 6: Update Vercel Environment Variable**

1. Go to **Vercel Dashboard**
2. Your project → **Settings** → **Environment Variables**
3. Update `VITE_API_URL`:
   ```
   Value: https://abc123def.ngrok-free.app
   Environment: Production
   ```
4. Click **"Save"**
5. **Redeploy** frontend

### **Step 7: Test!**

Visit your Vercel frontend → It now talks to your local backend! ✅

---

## 🚀 **Method 2: Using LocalTunnel (Simpler, No Signup)**

### **Step 1: Install localtunnel**

```bash
npm install -g localtunnel
```

### **Step 2: Start Your Backend**

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Step 3: Expose Backend with LocalTunnel**

Open a **NEW terminal**:
```bash
lt --port 8000 --subdomain parkinson-backend
```

You'll get a URL like:
```
your url is: https://parkinson-backend.loca.lt
```

**Note:** Free tier gives random subdomain if `parkinson-backend` is taken.

### **Step 4: Update CORS & Vercel**

Same as ngrok method above (Step 5 & 6)

---

## 🚀 **Method 3: VS Code Port Forwarding (GitHub Codespaces/Remote)**

If using **VS Code Remote Development** or **GitHub Codespaces**:

### **Step 1: Start Backend**

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Step 2: Forward Port**

1. VS Code → **"PORTS"** tab (bottom panel)
2. Click **"Forward a Port"**
3. Enter: `8000`
4. Right-click port → **"Port Visibility"** → **"Public"**
5. Copy the forwarded URL

### **Step 3: Update Vercel**

Use the forwarded URL as `VITE_API_URL` in Vercel

---

## 📋 **Quick Setup Commands (ngrok)**

```bash
# Terminal 1: Start Backend
cd /home/hari/Downloads/parkinson/parkinson-app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Expose with ngrok
ngrok http 8000

# Copy the ngrok HTTPS URL (e.g., https://abc123.ngrok-free.app)

# Update backend/.env:
# CORS_ORIGINS=https://abc123.ngrok-free.app,https://your-app.vercel.app

# Restart backend (Ctrl+C in Terminal 1, then rerun uvicorn)

# Update Vercel:
# Dashboard → Settings → Environment Variables
# VITE_API_URL = https://abc123.ngrok-free.app
# Redeploy frontend

# Done! ✅
```

---

## ⚠️ **Important Considerations**

### **1. ngrok URL Changes Every Restart**

**Problem:** Each time you restart ngrok, you get a NEW URL
**Solutions:**
- **Free Tier:** Update Vercel env var each time (annoying)
- **Paid Tier** ($10/month): Get permanent subdomain
- **Alternative:** Use localtunnel with fixed subdomain

### **2. CORS Must Include Tunnel URL**

Backend `.env` must have:
```bash
CORS_ORIGINS=https://your-ngrok-url.ngrok-free.app,https://your-vercel-app.vercel.app,http://localhost:5173
```

### **3. Performance**

Requests go: **Vercel → ngrok → Your Computer → ngrok → Vercel**
- Adds ~100-300ms latency
- Fine for development/testing
- Not for production

### **4. Your Computer Must Stay On**

- Backend running locally = Your computer must be on
- Close laptop = Backend stops = Frontend breaks
- For 24/7 access, deploy backend to Render/Railway

---

## 💡 **Better Long-Term Solution**

### **For Development:**
✅ **Current Setup:** Local backend + tunnel + Vercel frontend

### **For Others to Test:**
✅ **Better:** Deploy backend to Render (free) + Vercel frontend
- No tunnel needed
- 24/7 availability
- More reliable

### **For Production:**
✅ **Best:** Deploy both backend (Render) + frontend (Vercel)
- Professional setup
- Fast, reliable
- Scalable

---

## 🎯 **Recommended Workflow**

### **Option 1: Development Phase (You Only)**
```
Your Computer:
- Backend: localhost:8000 (VS Code)
- Frontend: localhost:5173 (npm run dev)
```

### **Option 2: Testing Phase (Share with Others)**
```
Your Computer:
- Backend: localhost:8000 → ngrok → https://abc.ngrok-free.app

Cloud:
- Frontend: https://your-app.vercel.app (uses ngrok URL)
```

### **Option 3: Demo/Production Phase**
```
Cloud:
- Backend: https://parkinson-backend.onrender.com (Render)
- Frontend: https://your-app.vercel.app (Vercel)
```

---

## 🚀 **Quick Start: Set Up ngrok NOW**

### **1. Install ngrok:**
```bash
sudo snap install ngrok
```

### **2. Sign up (free):**
https://dashboard.ngrok.com/signup

### **3. Authenticate:**
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### **4. Start backend:**
```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **5. Start ngrok (new terminal):**
```bash
ngrok http 8000
```

### **6. Copy the HTTPS URL and use it in Vercel!**

---

## 📊 **Comparison Table**

| Method | Free? | Setup Time | URL Changes? | Best For |
|--------|-------|------------|--------------|----------|
| **ngrok** | ✅ Yes | 5 min | Yes (every restart) | Quick testing |
| **LocalTunnel** | ✅ Yes | 2 min | Yes (random) | One-time demos |
| **VS Code Forward** | ✅ Yes | 1 min | Yes | Remote dev |
| **Render Deploy** | ✅ Yes | 15 min | ❌ No (permanent) | Long-term testing |

---

## 🆘 **Common Issues**

### **Issue 1: "ERR_NGROK_6022: Account limit exceeded"**
**Cause:** Free tier allows 1 tunnel at a time
**Solution:** Stop other ngrok instances or upgrade

### **Issue 2: CORS errors even with tunnel URL**
**Cause:** Forgot to add ngrok URL to CORS_ORIGINS
**Solution:** Update backend/.env and restart backend

### **Issue 3: Tunnel URL not working**
**Cause:** Backend not running or wrong port
**Solution:** Ensure backend is on port 8000

### **Issue 4: ngrok URL changes constantly**
**Cause:** Restarting ngrok generates new URL
**Solution:** 
- Keep ngrok running (don't close terminal)
- Or upgrade to paid tier for permanent URL
- Or deploy backend to Render (permanent URL)

---

## ✅ **Summary**

**Yes, you can run backend locally + deploy frontend to Vercel!**

**Setup:**
1. ✅ Install ngrok or localtunnel
2. ✅ Run backend on localhost:8000
3. ✅ Expose with tunnel (get public HTTPS URL)
4. ✅ Update CORS in backend
5. ✅ Update VITE_API_URL in Vercel
6. ✅ Others can access your frontend!

**Pros:**
- ✅ You can debug backend in real-time
- ✅ Easy to test changes
- ✅ Others can access the app

**Cons:**
- ❌ Your computer must stay on
- ❌ Tunnel URL changes each restart
- ❌ Slight performance overhead

**Better for long-term:** Deploy backend to Render (free, permanent URL)

**Need help setting up ngrok? Let me know!** 🚀
