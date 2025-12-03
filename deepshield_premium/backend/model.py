# model.py (unchanged from skeleton) - kept for compatibility
import os
from pathlib import Path

def build_simple_cnn(input_shape=(224,224,3)):
    try:
        from tensorflow.keras import layers, models
    except Exception:
        return None
    inputs = layers.Input(shape=input_shape)
    x = layers.Rescaling(1./255)(inputs)
    x = layers.Conv2D(16,3,activation='relu')(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(32,3,activation='relu')(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Flatten()(x)
    x = layers.Dense(64, activation='relu')(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    model = models.Model(inputs, outputs)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def load_model_or_none():
    model_path = Path(__file__).parent / 'models' / 'model.h5'
    if not model_path.exists():
        return None
    try:
        from tensorflow.keras.models import load_model
        return load_model(str(model_path))
    except Exception as e:
        print("Could not load model (tensorflow missing or model incompatible):", e)
        return None

def model_predict(model, pil_image):
    import numpy as np
    img = pil_image.resize((224,224))
    arr = np.array(img).astype('float32') / 255.0
    arr = arr[None,...]
    score = float(model.predict(arr)[0,0])
    label = "real" if score >= 0.5 else "fake"
    return {"label": label, "score": score}
