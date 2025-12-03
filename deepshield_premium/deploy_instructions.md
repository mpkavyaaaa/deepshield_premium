Deploy backend (Render):
- Set service root to 'backend'
- Build command: pip install -r requirements.txt
- Start command: uvicorn main:app --host 0.0.0.0 --port $PORT

Deploy frontend (Vercel):
- Point project to /frontend directory (no build needed)
- Update app.js BACKEND to your backend URL
