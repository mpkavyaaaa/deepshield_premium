from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uvicorn
import numpy as np
from PIL import Image
import io
import os

from model import load_model_or_none, model_predict

app = FastAPI(title="DeepFake Premium Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = load_model_or_none()  # may be None if no weights provided

@app.get('/health')
def health():
    return {"status":"ok"}

@app.post('/predict-image')
async def predict_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        img = Image.open(io.BytesIO(content)).convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

    if MODEL is not None:
        pred = model_predict(MODEL, img)
        return {"prediction": pred["label"], "score": float(pred["score"]), "source":"model"}

    arr = np.array(img).astype(np.float32)
    mean = arr.mean()
    if mean > 127:
        label = "real"
        score = min(0.99, (mean - 127) / 128 + 0.5)
    else:
        label = "fake"
        score = min(0.99, (127 - mean) / 128 + 0.5)
    return {"prediction": label, "score": float(score), "source":"heuristic", "mean_pixel": float(mean)}

@app.post('/predict-video')
async def predict_video(file: UploadFile = File(...), sample_rate: int = 5):
    """Accepts a video file, extracts frames using OpenCV and aggregates frame predictions.
       sample_rate: take one frame every `sample_rate` frames to reduce work (default 5).
    """
    # save uploaded video temporarily
    tmp_dir = Path("tmp_videos")
    tmp_dir.mkdir(exist_ok=True)
    video_path = tmp_dir / file.filename
    try:
        with open(video_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded video: {e}")

    # try to import cv2
    try:
        import cv2
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenCV not available on server: {e}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        video_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Cannot open video file")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    sample_rate = max(1, int(sample_rate))
    scores = []
    frames_processed = 0
    read_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if read_idx % sample_rate == 0:
            # convert BGR -> RGB and to PIL Image
            try:
                from PIL import Image
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                if MODEL is not None:
                    pred = model_predict(MODEL, img)
                    scores.append(float(pred["score"]) if pred["label"]=="real" else 1.0 - float(pred["score"]))
                else:
                    arr = np.array(img).astype(np.float32)
                    mean = arr.mean()
                    if mean > 127:
                        score = min(0.99, (mean - 127) / 128 + 0.5)
                    else:
                        score = min(0.99, (127 - mean) / 128 + 0.5)
                    # keep probability-of-real
                    scores.append(score if mean > 127 else 1.0 - score)
                frames_processed += 1
            except Exception:
                pass
        read_idx += 1
    cap.release()
    # remove temp file
    try:
        video_path.unlink(missing_ok=True)
    except Exception:
        pass

    if frames_processed == 0:
        raise HTTPException(status_code=400, detail="No frames extracted from video")

    # aggregate: average probability-of-real across sampled frames
    avg_prob_real = float(sum(scores) / len(scores))
    label = "real" if avg_prob_real >= 0.5 else "fake"
    return {"prediction": label, "score": avg_prob_real, "frames_sampled": frames_processed, "source":"video_aggregate"}

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
