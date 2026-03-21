import streamlit as st
import numpy as np
from PIL import Image
import zipfile
import os

# 1. AUTO-UNZIP THE BRAIN
def get_model():
    zip_path = "converted_keras.zip"
    model_path = "keras_model.h5"
    if not os.path.exists(model_path) and os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
    
    import tensorflow as tf
    return tf.keras.models.load_model(model_path, compile=False)

# Load the model
try:
    model = get_model()
    HAS_MODEL = True
except:
    HAS_MODEL = False

# --- FUNCTION 1: Leaf Analysis ---
def analyze_leaf(image):
    if HAS_MODEL:
        img = image.resize((224, 224))
        img_array = np.array(img.convert('RGB')) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        import tensorflow as tf
        prediction = model.predict(img_array)
        # Healthy score is typically index 0 in Teachable Machine
        return int(prediction[0][0] * 100)
    else:
        # Fallback math if model fails
        img_array = np.array(image.convert('RGB'))
        return 90 if np.mean(img_array[:,:,1]) > np.mean(img_array[:,:,0]) else 40

# --- FUNCTION 2: Soil Logic (The missing piece!) ---
def get_soil_logic(moisture):
    if moisture < 30: return "Dry"
    elif 30 <= moisture <= 70: return "Ideal"
    else: return "Wet"

# --- FUNCTION 3: Nutrient Advice (The missing piece!) ---
def get_nutrient_advice(score):
    if score > 80: return "Plant is healthy. Keep up the good work!"
    elif 50 <= score <= 80: return "Minor nutrient deficiency. Add organic compost."
    else: return "Warning: High disease risk. Check for pests or fungal infection."
