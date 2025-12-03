# Deployment Guide (Auto-generated)

Project root: `/deepshield_premium`

Detected backend: **FastAPI** (Python).  
Detected frontend folder: `deepshield_premium/frontend`.

## Backend (Render.com)
1. Ensure `requirements.txt` includes `uvicorn[standard]` and `gunicorn` (Render uses gunicorn; we'll use uvicorn worker).
   - If not present, add them: `uvicorn[standard]\ngunicorn`

2. Start command for Render (example):
   - **Start Command:** `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
   - This assumes the FastAPI app instance is named `app` in `main.py` inside the backend folder.

3. Steps to deploy on Render:
   - Push only the `backend` folder to a GitHub repo (or push whole project and point Render to the backend directory).
   - On Render dashboard → New → Web Service → Connect repo → Root directory: `/deepshield_premium/backend`
   - Set Build Command: `pip install -r requirements.txt`
   - Set Start Command: `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`

## Frontend (Vercel)
1. Push the frontend folder to GitHub (or the whole repo and choose the frontend directory in Vercel).
2. If this is a Vite/React project, Vercel auto-detects it. Ensure `package.json` has script `build` (e.g., `vite build`) and `start` if previewing.
3. Set Environment Variable in Vercel:
   - `VITE_API_URL` = `https://<your-backend>.onrender.com`
4. Deploy: Vercel → Add New Project → Select repo → Set Root Directory: `/deepshield_premium/frontend` → Deploy

## CORS & API URL
- Make sure backend allows CORS for the Vercel domain. For FastAPI, add:
```py
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], # replace '*' with your Vercel domain for production
    allow_methods=['*'],
    allow_headers=['*']
)
```

## Files added
- `DEPLOY_README.md` (this file)
- `deepshield_premium/backend/start_render.sh` — helper script to run locally with gunicorn
- `vercel.json` — optional Vercel config to set build output if needed

## What I need from you now
1. Confirm the FastAPI entry file is `main.py` and the app variable is `app` (I detected `main.py` but confirm if different).
2. Tell me the exact frontend folder name if different from what's in this README.
3. Do you want me to pack the modified repo into a ZIP for you to download (ready to push to GitHub)?
