import streamlit as st
import numpy as np
from PIL import Image
import zipfile
import os

# 1. AUTO-UNZIP THE BRAIN
def get_model():
    zip_path = "converted_keras.zip"
    model_path = "keras_model.h5"
    
    # Check if we need to unzip
    if not os.path.exists(model_path) and os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
            
    # Load the model using TensorFlow
    import tensorflow as tf
    return tf.keras.models.load_model(model_path, compile=False)

# Try to load the model once
try:
    model = get_model()
    HAS_MODEL = True
except:
    HAS_MODEL = False

def analyze_leaf(image):
    if HAS_MODEL:
        # --- ONLINE ACCURATE MODE ---
        # Resize image for the AI
        img = image.resize((224, 224))
        img_array = np.array(img.convert('RGB')) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict
        prediction = model.predict(img_array)
        
        # Assuming Index 0 is Healthy, Index 1 is Unhealthy
        # We return the Healthy confidence as the score
        health_score = int(prediction[0][0] * 100)
        return health_score
    else:
        # --- OFFLINE FALLBACK (If unzipping fails) ---
        img_array = np.array(image.convert('RGB'))
        avg_r, avg_g = np.mean(img_array[:,:,0]), np.mean(img_array[:,:,1])
        return 90 if avg_g > avg_r else 35
