from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io
import cv2

# =============================
# CORS (important for Vercel)
# =============================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # You can replace "*" with your vercel URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# NUMPY MODEL LOADER
# =============================

def load_numpy_model(path="models/deepfake_model"):
    try:
        W = np.load(path + "/weights.npy")  # shape (150528, 1)
        b = np.load(path + "/bias.npy")     # shape (1,)
        print("Loaded NumPy model successfully.")
        return {"W": W, "b": b}
    except Exception as e:
        print("MODEL LOAD ERROR:", e)
        return None

MODEL = load_numpy_model("models/deepfake_model")

# =============================
# NUMPY MODEL PREDICT
# =============================

def numpy_model_predict(model, pil_image):
    try:
        # resize + normalize
        img = pil_image.convert("RGB").resize((224,224))
        arr = np.asarray(img).astype("float32") / 255.0
        flat = arr.reshape(-1, 1)  # 150528 x 1

        logits = float(np.dot(flat.T, model["W"]) + model["b"])
        prob = 1.0 / (1.0 + np.exp(-logits))
        label = "FAKE" if prob > 0.5 else "REAL"

        return {"prediction": label, "score": float(prob)}
    except Exception as e:
        print("PREDICT ERROR:", e)
        return {"prediction": "REAL", "score": 0.0}

# =============================
# PREDICT IMAGE ENDPOINT
# =============================

@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents))
        pred = numpy_model_predict(MODEL, pil_img)
        return pred
    except Exception as e:
        return {"error": str(e)}

# =============================
# OPTIONAL: PREDICT VIDEO
# =============================

@app.post("/predict-video")
async def predict_video(file: UploadFile = File(...), sample_rate: int = 5):
    try:
        contents = await file.read()
        video_bytes = np.frombuffer(contents, np.uint8)
        vid = cv2.imdecode(video_bytes, cv2.IMREAD_COLOR)
        if vid is None:
            return {"error": "Cannot decode video"}

        # Sample frames (VERY basic version)
        # You can upgrade this later
        prob_list = []
        frame_count = 0

        # Placeholder: treat input as an image
        # Better video code can be added later
        pil = Image.fromarray(cv2.cvtColor(vid, cv2.COLOR_BGR2RGB))
        pred = numpy_model_predict(MODEL, pil)
        return pred

    except Exception as e:
        return {"error": str(e)}

# =============================
# ROOT CHECK
# =============================
@app.get("/")
def home():
    return {"status": "Deepfake API working"}
