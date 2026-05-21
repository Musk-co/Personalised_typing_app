# Railway Deployment Guide for Personalised Typing App

This guide walks you through deploying the full-stack typing trainer app to Railway.app.

## Overview

Your app consists of:
- **Backend**: FastAPI (Python) - REST API server
- **Frontend**: React + TypeScript - Web UI
- **Database**: SQLite (dev) / PostgreSQL (production)

Railway will deploy both as separate services and manage communication between them.

---

## Step 1: Prepare Your Repository ✅

Your repo is already configured with:
- ✅ `backend/Dockerfile` - Backend container configuration
- ✅ `frontend/Dockerfile` - Frontend container configuration
- ✅ `docker-compose.yml` - Local testing configuration
- ✅ `backend/.env.example` - Environment template

**Verify the files exist in your repo**:
```bash
git log --oneline -5
# You should see recent commits about Dockerfile and docker-compose
```

---

## Step 2: Create Railway Project

1. **Go to [Railway.app](https://railway.app)**
2. **Sign up/Login** with GitHub
3. **Create new project**:
   - Click "Create New Project"
   - Select "Deploy from GitHub repo"
   - Choose `Musk-co/Personalised_typing_app`
   - Select "Deploy Now"

---

## Step 3: Deploy Backend Service

### 3a. Create Backend Service

1. In Railway dashboard, click **"+ Add Service"**
2. Select **"GitHub Repo"**
3. Choose your `Personalised_typing_app` repo
4. Railway will auto-detect and build

### 3b. Configure Backend

1. **Rename service** (optional): Right-click service → Rename to `backend`
2. **Set environment variables**:
   - Click your backend service
   - Go to **Variables** tab
   - Add these variables:

```
DEBUG=False
ADAPTER_TYPE=rule_based
DATABASE_URL=sqlite:///./typing_trainer.db
SECRET_KEY=generate-a-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. **Generate SECRET_KEY**:
   - Run this locally or use an online generator:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   - Copy the output to `SECRET_KEY` variable

4. **Set build/start commands**:
   - Go to **Settings** tab
   - Set **Build Command**: `cd backend && pip install -r requirements.txt`
   - Set **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Deploy**: Click "Deploy" button (Railway auto-deploys on git push)

6. **Get backend URL**:
   - Once deployed, click service
   - Copy the domain URL (e.g., `https://typing-app-backend-prod.railway.app`)
   - Save this for frontend configuration

---

## Step 4: Deploy Frontend Service

### 4a. Create Frontend Service

1. In Railway dashboard, click **"+ Add Service"**
2. Select **"GitHub Repo"**
3. Choose the same repo again
4. Railway will auto-detect and build

### 4b. Configure Frontend

1. **Rename service**: Right-click → Rename to `frontend`

2. **Set environment variables**:
   - Go to **Variables** tab
   - Add this variable (use backend URL from Step 3.6):

```
VITE_API_URL=https://your-backend-url.railway.app/api/v1
```

Example:
```
VITE_API_URL=https://typing-app-backend-prod-8f3e.railway.app/api/v1
```

3. **Set build/start commands**:
   - Go to **Settings** tab
   - Set **Build Command**: `cd frontend && npm install && npm run build`
   - Set **Start Command**: `cd frontend && npm install -g serve && serve -s dist -l $PORT`

4. **Verify Node version**:
   - Go to **Settings** → **Build Logs**
   - Ensure Node 18+ is used

5. **Deploy**: Click "Deploy"

6. **Get frontend URL**:
   - Once deployed, copy the domain URL
   - This is your public app URL! 🎉

---

## Step 5: Connect Frontend to Backend

The frontend needs to communicate with the backend API.

### Update Backend CORS (if needed)

In your backend API file, ensure CORS is configured for the frontend domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.railway.app",
        "http://localhost:5173",  # Local development
        "http://localhost:3000"   # Local production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Then:**
1. Commit this change
2. Push to GitHub
3. Railway auto-redeploys backend ✅

---

## Step 6: Test Your Deployment

### 6a. Test Backend API

```bash
# Replace with your backend URL
curl https://your-backend-url.railway.app/docs

# Or open in browser:
# https://your-backend-url.railway.app/docs (Swagger UI)
# https://your-backend-url.railway.app/redoc (ReDoc)
```

### 6b. Test Frontend

1. Open your frontend URL in browser
2. Navigate to login/register page
3. Verify API calls work (check browser Network tab)
4. If errors, check logs:
   - Railway Dashboard → Service → Logs

---

## Step 7: Production Database Setup (Optional)

For production, use PostgreSQL instead of SQLite:

### 7a. Add PostgreSQL to Railway

1. In Railway project, click **"+ Add Service"**
2. Select **"PostgreSQL"**
3. Railway creates a managed database
4. Copy the connection string from variables

### 7b. Update Backend

1. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
# Add to requirements.txt
```

2. Update backend environment variable:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

3. Commit and push:
```bash
git add .
git commit -m "Add PostgreSQL support for production"
git push
```

4. Railway auto-redeploys ✅

---

## Step 8: Monitoring & Logs

### View Logs

1. Go to Railway dashboard
2. Click each service (backend/frontend)
3. Go to **Logs** tab
4. Monitor real-time logs

### Common Issues

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check backend logs; ensure start command is correct |
| CORS errors | Update `allow_origins` in backend CORS middleware |
| Frontend can't reach API | Verify `VITE_API_URL` environment variable matches backend URL |
| Build fails | Check build logs; ensure Node/Python versions are correct |
| "Module not found" | Ensure `package.json` and `requirements.txt` are correct |

---

## Step 9: Custom Domain (Optional)

1. Go to frontend service **Settings**
2. Scroll to **Domains**
3. Click **"Add Custom Domain"**
4. Follow DNS setup instructions
5. Point to Railway domain

---

## Step 10: Deployment Checklist

- [ ] Backend deployed and API docs working (`/docs` endpoint)
- [ ] Frontend deployed and accessible
- [ ] Frontend can reach backend API (no CORS errors)
- [ ] Environment variables set correctly
- [ ] PostgreSQL configured (if using production DB)
- [ ] Custom domain set up (if applicable)
- [ ] Logs monitored and no errors
- [ ] Backend SECRET_KEY is secure and unique

---

## Quick Reference: URLs After Deployment

| Service | URL Format | Example |
|---------|-----------|---------|
| Backend API | `https://your-backend-service.railway.app` | `https://typing-app-backend-prod.railway.app` |
| Backend Docs | `https://your-backend-service.railway.app/docs` | `https://typing-app-backend-prod.railway.app/docs` |
| Frontend | `https://your-frontend-service.railway.app` | `https://typing-app-frontend-prod.railway.app` |

---

## Redeploy After Changes

```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push origin main

# Railway automatically detects and redeploys!
# Monitor in Dashboard → Logs
```

---

## Environment Variables Summary

### Backend
```env
DEBUG=False
ADAPTER_TYPE=rule_based
DATABASE_URL=postgresql://user:pass@host:5432/db  # or sqlite:///./db.db
SECRET_KEY=your-secure-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend
```env
VITE_API_URL=https://your-backend.railway.app/api/v1
```

---

## Support

- **Railway Docs**: https://docs.railway.app/
- **Your Backend Docs**: Access via `/docs` on backend URL
- **GitHub Issues**: Create issue in your repo if deployment fails

---

**Congratulations! 🚀 Your app is now live on Railway!**

Next steps:
1. Share your frontend URL with friends
2. Monitor logs for any issues
3. Collect user feedback
4. Plan Phase 2: WebSockets, advanced charts, etc.
