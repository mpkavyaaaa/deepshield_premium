# DeepShield - DeepFake Detector (Premium UI + Video)

This package updates the previous demo with:
- Premium responsive frontend UI (image + video).
- Backend endpoint `/predict-video` which samples frames and aggregates predictions.

Quick start:
1. Start backend:
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
2. Serve frontend:
   python3 -m http.server 3000 --directory frontend
3. Open http://localhost:3000
