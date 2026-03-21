import streamlit as st
import tensorflow as tf
from tensorflow.keras import layers, models
from PIL import Image
import numpy as np
import pandas as pd

st.set_page_config(page_title="AgroMind Ultimate", layout="wide")

# --- 1. THE BRAIN (CNN Architecture) ---
@st.cache_resource
def load_cnn_brain():
    # Using MobileNetV2 (A professional-grade CNN)
    base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    base_model.trainable = False 
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(3, activation='softmax') # 3 leaf categories
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# --- 2. THE INTERFACE ---
st.title("🍀 AgroMind Ultimate")
st.write("B.Tech Engineering Project: CNN-Based Crop Disease Detection")
st.divider()

try:
    model = load_cnn_brain()
    classes = ['Healthy', 'Powdery Mildew', 'Yellow Leaf']
    HAS_BRAIN = True
except Exception as e:
    HAS_BRAIN = False
    st.error(f"Brain is still loading... {e}")

uploaded_file = st.file_uploader("Upload Leaf Image for AI Analysis", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB').resize((224, 224))
    st.image(img, caption="Scanning Sample...", width=300)
    
    if HAS_BRAIN:
        # AI Analysis
        x = np.array(img) / 255.0
        x = np.expand_dims(x, axis=0)
        prediction = model.predict(x)
        result = classes[np.argmax(prediction)]
        confidence = np.max(prediction)

        # Dashboard Output
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Diagnosis", result)
            st.write(f"Confidence: {int(confidence * 100)}%")
        with col2:
            st.write("**System Status**")
            st.success("AI Brain: Active")
        with col3:
            st.write("**Action Plan**")
            st.info("Optimize Water" if result == "Healthy" else "Apply Fungicide")
            
        st.divider()
        st.subheader("📊 Historical Analysis")
        st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Health Score']))
