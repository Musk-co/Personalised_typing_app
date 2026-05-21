# Complete Free Deployment Guide: Vercel + Render.com

This is the **complete, detailed, step-by-step guide** for deploying your Personalised Typing App completely FREE using:
- **Vercel** for Frontend (React)
- **Render.com** for Backend (FastAPI)

**Total Cost: $0**
**Time: ~30 minutes**

---

## 🎯 PART A: PREPARE YOUR CODE (Do This First!)

### **Step A1: Create `.env.local` for Frontend**

1. Open your project in VS Code (or your editor)
2. Navigate to the `frontend` folder
3. Create a new file: `.env.local`
4. Add this (leave empty for now, we'll fill it after backend deploys):

```env
VITE_API_URL=http://localhost:8000/api/v1
```

Save the file.

### **Step A2: Verify Backend `.env.example`**

1. Go to `backend/.env.example`
2. Make sure it has these lines:

```env
DEBUG=False
ADAPTER_TYPE=rule_based
DATABASE_URL=sqlite:///./typing_trainer.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

✅ Already created!

### **Step A3: Generate a Secure SECRET_KEY**

Open your terminal and run:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Copy the output.** You'll need it later. Example output:
```
Drmhze6EPcv0fN_81Bj-nA-TUtfXXXXXXXXXXXXXXX
```

### **Step A4: Update Backend CORS**

1. Find your FastAPI main file: `backend/app/main.py` or similar
2. Add CORS configuration at the top of the app initialization:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",  # This will match any Vercel domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Save the file
4. Commit and push:

```bash
git add backend/
git commit -m "Add CORS configuration for production"
git push origin main
```

### **Step A5: Verify GitHub Connection**

Make sure your code is on GitHub:

```bash
git remote -v
# You should see something like:
# origin  https://github.com/Musk-co/Personalised_typing_app.git (fetch)
```

If not, set it up:

```bash
git remote add origin https://github.com/Musk-co/Personalised_typing_app.git
git push -u origin main
```

✅ **Now your code is ready!**

---

## 🌐 PART B: DEPLOY BACKEND TO RENDER.COM

### **Step B1: Create Render.com Account**

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"**
4. Click **"Authorize"** to connect your GitHub account
5. Complete profile setup

✅ Account created!

### **Step B2: Create Backend Service**

1. Once logged in, you'll see the dashboard
2. Click **"+ New +"** button (top left)
3. Select **"Web Service"**

![Render New Service](https://render.com/docs/images/select-web-service.png)

### **Step B3: Connect Your GitHub Repository**

1. Under **"Connect a repository"**, click **"Connect GitHub account"** (if not already connected)
2. Search for: `Personalised_typing_app`
3. Click **"Connect"** next to your repository

✅ Repository connected!

### **Step B4: Configure the Web Service**

Fill in these fields exactly:

| Field | Value |
|-------|-------|
| **Name** | `typing-app-backend` |
| **Environment** | `Python 3` |
| **Region** | `US East (Ohio)` or closest to you |
| **Branch** | `main` |
| **Build Command** | `cd backend && pip install -r requirements.txt` |
| **Start Command** | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### **Step B5: Add Environment Variables**

1. Scroll down to **"Environment"** section
2. Click **"Add Environment Variable"**
3. Add each variable one by one:

```
DEBUG = False
ADAPTER_TYPE = rule_based
DATABASE_URL = sqlite:///./typing_trainer.db
SECRET_KEY = <PASTE YOUR GENERATED SECRET_KEY HERE>
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

**Replace `SECRET_KEY` with the one you generated in Step A3**

Example:
```
SECRET_KEY = Drmhze6EPcv0fN_81Bj-nA-TUtfXXXXXXXXXXXXXXX
```

### **Step B6: Select Free Plan**

1. Scroll down to **"Plan"**
2. Select **"Free"** (should already be selected)
3. Features you get:
   - ✅ Shared CPU
   - ✅ 0.5 GB RAM
   - ✅ Free PostgreSQL (optional later)
   - ✅ Auto-deploy on git push

### **Step B7: Deploy!**

1. Click the blue **"Create Web Service"** button
2. **Wait 2-3 minutes** while Render builds your app
3. Watch the logs scroll by
4. You should see: ✅ `Service is live`

### **Step B8: Get Your Backend URL**

1. Once deployed, at the top of the page, you'll see a URL like:
   ```
   https://typing-app-backend-xxxx.onrender.com
   ```
2. **Copy this URL** and save it somewhere (Notes app, etc.)
3. Test it by going to:
   ```
   https://typing-app-backend-xxxx.onrender.com/docs
   ```
   You should see the Swagger API documentation!

✅ **Backend is live!**

**Example**: `https://typing-app-backend-xyz123.onrender.com`

---

## 🚀 PART C: DEPLOY FRONTEND TO VERCEL

### **Step C1: Create Vercel Account**

1. Go to **https://vercel.com**
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub
5. Complete setup

✅ Account created!

### **Step C2: Import Your Repository**

1. After login, click **"Add New..."** (top left)
2. Select **"Project"**
3. Click **"Continue with GitHub"**
4. Search for: `Personalised_typing_app`
5. Click **"Import"**

### **Step C3: Configure Project Settings**

Vercel will auto-detect many settings. Make these adjustments:

**Project Name**: Leave as is or change to `typing-app-frontend`

**Framework Preset**: Select **"Vite"** (or let it auto-detect)

**Root Directory**: Click **"Edit"** and change to `frontend`

**Build Command**: Should be `npm run build`

**Output Directory**: Should be `dist`

**Install Command**: Should be `npm install`

### **Step C4: Add Environment Variables**

1. Click **"Environment Variables"** (you should see this before deploying)
2. Add this variable:

```
VITE_API_URL = https://typing-app-backend-xxxx.onrender.com/api/v1
```

**Replace `xxxx` with your actual backend domain from Step B8**

Example:
```
VITE_API_URL = https://typing-app-backend-xyz123.onrender.com/api/v1
```

### **Step C5: Deploy!**

1. Click the blue **"Deploy"** button
2. **Wait 3-5 minutes** for build and deployment
3. Watch the deployment progress
4. You should see: ✅ `Congratulations! Your project is ready`

### **Step C6: Get Your Frontend URL**

1. Vercel will show you a URL like:
   ```
   https://typing-app-frontend.vercel.app
   ```
2. **Copy this URL** and save it
3. Click the link to open your live app! 🎉

✅ **Frontend is live!**

---

## 🔗 PART D: CONNECT FRONTEND TO BACKEND

### **Step D1: Update Frontend Environment Variable**

Now that we have both URLs, let's make them talk to each other.

1. Go back to **Vercel Dashboard**
2. Select your project: `typing-app-frontend`
3. Go to **Settings** → **Environment Variables**
4. Find the variable `VITE_API_URL`
5. Update it with your exact Render backend URL:

```
VITE_API_URL = https://typing-app-backend-xyz123.onrender.com/api/v1
```

6. Click **Save**

⚠️ **This will trigger a redeploy automatically** - wait 1-2 minutes

### **Step D2: Update Backend CORS (Already Done!)**

You already updated CORS in Step A4, but let's verify:

In your backend code (`backend/app/main.py`), check that you have:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",  # This matches your Vercel domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

✅ Already done from Step A4!

### **Step D3: Redeploy Backend (Force Update)**

1. Go to **Render Dashboard**
2. Select your service: `typing-app-backend`
3. Click **"Manual Deploy"** → **"Deploy latest commit"**
4. Wait 1-2 minutes for redeployment

✅ Both services now know each other!

---

## ✅ PART E: TEST YOUR LIVE APP

### **Step E1: Test Backend API**

1. Open this URL in your browser:
   ```
   https://typing-app-backend-xyz123.onrender.com/docs
   ```
2. You should see the **Swagger UI** (interactive API documentation)
3. Try one API endpoint:
   - Click on any endpoint (e.g., `/api/v1/auth/register`)
   - Click **"Try it out"**
   - Click **"Execute"**
   - You should see a response (200 OK or validation error)

✅ Backend is working!

### **Step E2: Test Frontend**

1. Open your frontend URL:
   ```
   https://typing-app-frontend.vercel.app
   ```
2. The app should load!
3. Try these actions:
   - Navigate to login/register
   - Open browser **Developer Tools** (F12 or right-click → Inspect)
   - Go to **Network** tab
   - Try to register/login
   - You should see API calls to your Render backend
   - If you see green checkmarks (200 status), it's working!

✅ Frontend is working!

### **Step E3: Check for CORS Errors**

1. In the same Developer Tools
2. Go to **Console** tab
3. Look for any red errors starting with "CORS"
4. If you see CORS errors:
   - Your CORS config in backend might need updating
   - Go to `backend/app/main.py`
   - Update `allow_origins` to include your Vercel domain
   - Commit, push, and redeploy on Render

✅ No CORS errors = You're good!

### **Step E4: Test Full User Flow**

1. **Register**: Create a new account on your frontend
2. **Check backend logs**: Go to Render → Your service → Logs
   - You should see requests logged
3. **Login**: Try logging in with the account you just created
4. **Use the app**: Navigate around, take a typing test
5. Everything working? 🎉

---

## 📊 PART F: MONITOR AND MAINTAIN

### **Step F1: View Backend Logs (Render)**

1. Go to **Render Dashboard**
2. Click your `typing-app-backend` service
3. Click **"Logs"** tab
4. See real-time logs of your API requests

**Check logs when:**
- Something breaks
- Users report errors
- You want to debug

### **Step F2: View Frontend Logs (Vercel)**

1. Go to **Vercel Dashboard**
2. Click your `typing-app-frontend` project
3. Go to **Deployments** tab
4. Click the latest deployment
5. See build logs and analytics

### **Step F3: Keep Backend Awake (Important!)**

Render's free tier puts services to sleep after 15 minutes of inactivity.

**Option 1: Use a ping service (FREE)**

1. Go to **https://cron-job.org**
2. Sign up (free)
3. Create new cron job:
   - **URL**: `https://typing-app-backend-xyz123.onrender.com/docs`
   - **Schedule**: Every 14 minutes
   - Click **"Create Cronjob"**

✅ Your backend will stay awake!

**Option 2: Upgrade to paid plan**

When you have users and can afford it:
- Render.io Pro: $7/month
- Vercel Pro: $20/month

---

## 🎯 PART G: AFTER DEPLOYMENT - WHAT'S NEXT?

### **Make Changes to Your App**

When you make changes:

```bash
# Make your changes locally
# Then...
git add .
git commit -m "Your change description"
git push origin main
```

**Auto-redeploy:**
- ✅ **Vercel**: Auto-redeploys frontend (1-2 minutes)
- ✅ **Render**: Auto-redeploys backend (2-3 minutes)

Check deployment status in their dashboards!

### **Share Your App**

Your live app URL:
```
https://typing-app-frontend.vercel.app
```

Share this with friends, family, or on social media!

---

## 🆘 TROUBLESHOOTING

### **Problem: 502 Bad Gateway on Frontend**

**Solution:**
1. Go to Vercel → Your project → Deployments
2. Check if the latest deployment succeeded (green checkmark)
3. If failed, click deployment to see build logs
4. Common issues:
   - Missing `package.json` in frontend folder
   - Wrong Node version
   - Missing environment variable

### **Problem: CORS Error in Browser Console**

**Error looks like:**
```
Access to XMLHttpRequest at 'https://backend-url/api/v1/...' 
from origin 'https://frontend-url.vercel.app' has been blocked by CORS policy
```

**Solution:**
1. Go to `backend/app/main.py`
2. Find the CORS middleware
3. Add your Vercel domain to `allow_origins`:
   ```python
   allow_origins=[
       "https://typing-app-frontend.vercel.app",
       "https://*.vercel.app",
   ]
   ```
4. Commit and push
5. Render auto-redeploys
6. Refresh frontend in browser

### **Problem: Backend Taking Too Long to Respond (30+ seconds)**

**Reason:** Free tier puts service to sleep

**Solution:**
1. Set up the ping service (Part F, Step F3)
2. Or upgrade to Render Pro ($7/month)

### **Problem: App Not Updating After I Pushed Code**

**Solution:**
1. Check Render/Vercel deployment status
2. If deployment is "in progress", wait
3. If failed, click to see logs and fix errors
4. Force redeploy:
   - **Render**: Settings → Manual Deploy
   - **Vercel**: Deployments → Redeploy

### **Problem: Build Fails with "Module not found"**

**Solution:**
1. Check `requirements.txt` (backend) or `package.json` (frontend)
2. Ensure all dependencies are listed
3. Commit and push
4. Try deploying again

---

## 📋 FINAL CHECKLIST - IS EVERYTHING WORKING?

- [ ] Render.com account created
- [ ] Backend deployed to Render (backend URL saved)
- [ ] Backend `/docs` endpoint works
- [ ] Vercel account created
- [ ] Frontend deployed to Vercel (frontend URL saved)
- [ ] Environment variables set on both platforms
- [ ] Frontend can reach backend API (no CORS errors)
- [ ] User registration works
- [ ] User login works
- [ ] Typing test functionality works
- [ ] Logs can be viewed on both platforms
- [ ] Ping service set up (to keep backend awake)
- [ ] App shared with at least one person 😄

---

## 🎉 CONGRATULATIONS!

Your app is now **live on the internet for FREE!**

**Your URLs:**
```
Frontend: https://typing-app-frontend.vercel.app
Backend API: https://typing-app-backend-xyz123.onrender.com
Backend Docs: https://typing-app-backend-xyz123.onrender.com/docs
```

**Share it with the world! 🚀**

---

## 💰 Cost Breakdown

| Service | Cost | What You Get |
|---------|------|-------------|
| Vercel | $0 | Unlimited deployments, 100GB bandwidth/month |
| Render.com | $0 | Unlimited deployments, auto-deploy, sleeps after 15 min |
| Total | **$0** | Complete full-stack app! |

**Optional upgrades when you have users:**
- Render Pro: $7/month (no sleep, more RAM)
- Vercel Pro: $20/month (more build time, analytics)

---

## 📞 SUPPORT & RESOURCES

- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

---

**Built with ❤️ - Now deployed with 💰 = $0**

Happy typing! ⌨️
