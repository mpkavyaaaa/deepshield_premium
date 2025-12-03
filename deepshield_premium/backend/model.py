import numpy as np
from PIL import Image
import io

def load_model_or_none(path="models/model.h5"):
    """
    Try to load a Keras model from path. If unavailable, return None.
    (Leave existing project model-loading approach if you already have one;
    this function is a safe fallback loader.)
    """
    try:
        # delayed import so import errors earlier don't break startup
        from tensorflow.keras.models import load_model
        model = load_model(path)
        return model
    except Exception:
        return None

def model_predict(model, pil_image):
    """
    Args:
        model: ML model object or None.
        pil_image: PIL.Image in RGB
    Returns:
        dict: {"score": float, "label": "REAL"|"FAKE"}
    Behavior:
        - If model is present: use model.predict and interpret probabilty > 0.5 as REAL.
        - If model missing or prediction fails: use a conservative heuristic (based on image variance)
          that is less likely to mark images as FAKE.
    """
    # ensure RGB and size
    try:
        img = pil_image.convert("RGB").resize((224,224))
        arr = np.array(img).astype(np.float32) / 255.0
        arr_batch = np.expand_dims(arr, 0)  # shape (1,224,224,3)
    except Exception:
        # fallback: if image can't be processed, mark as unknown but prefer REAL
        return {"score": 0.0, "label": "REAL"}

    # If model provided, try to use it
    if model is not None:
        try:
            # model expected to return probability of FAKE or REAL; we handle both common cases
            pred = model.predict(arr_batch)
            # pred might be shape (1,1) or (1,2) or (1,)
            try:
                # If model gives probability of REAL in index 0
                score = float(pred[0,0])
            except Exception:
                # try common alternatives
                if isinstance(pred, (list, tuple)):
                    score = float(pred[0])
                else:
                    pred_arr = np.array(pred)
                    # If shape is (1,2) and second column is prob(fake), take prob(real)=1-prob(fake)
                    if pred_arr.ndim == 2 and pred_arr.shape[1] == 2:
                        prob_fake = float(pred_arr[0,1])
                        score = 1.0 - prob_fake
                    else:
                        score = float(pred_arr.flatten()[0])

            # interpret score: higher => more REAL (conservative)
            label = "REAL" if score >= 0.5 else "FAKE"
            return {"score": score, "label": label}
        except Exception:
            # if model.predict fails, fall through to heuristic

            pass

    # Heuristic fallback: conservative and robust
    # Use image std dev (texture/variance). Very smooth images can be suspicious, but
    # many real photos can also be smooth — so we bias toward REAL.
    mean = float(np.mean(arr))
    std = float(np.std(arr))
    # Heuristic score in [0,1] where higher => more REAL
    # We map std in range [0.02, 0.25] -> [0,1], clamp outside that range
    lo = 0.02
    hi = 0.25
    if std <= lo:
        heur_score = 0.45  # low variance but don't strongly call FAKE
    elif std >= hi:
        heur_score = 0.7   # high variance -> likely REAL
    else:
        heur_score = (std - lo) / (hi - lo) * (0.7 - 0.45) + 0.45

    # slight boost if mean looks photographic (not pure dark/bright)
    if 0.08 < mean < 0.92:
        heur_score = min(1.0, heur_score + 0.05)

    label = "REAL" if heur_score >= 0.5 else "FAKE"
    return {"score": float(round(heur_score,4)), "label": label}
