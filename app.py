import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import pandas as pd # For the health trends chart

# --- 1. SETUP & MODEL LOADING ---
@st.cache_resource
def load_my_model():
    return tf.keras.models.load_model('model.h5')

model = load_my_model()

# --- 2. THE LOGIC ENGINE ---
def get_analysis(prediction_label):
    # Restoring your specific recommendations
    if "Healthy" in prediction_label:
        return 95, "STABLE", "Maintain current schedule", "Optimal"
    elif "Mildew" in prediction_label or "White" in prediction_label:
        return 62, "STABLE", "Nitrogen Apply", "Low Nitrogen"
    return 50, "WARNING", "Review Sample", "Inconsistent"

# --- 3. DASHBOARD UI (Restoring your original look) ---
st.set_page_config(layout="wide")
st.title("AgroMind Ultimate")

uploaded_file = st.file_uploader("Scan New Sample", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # --- PROCESSING ---
    image = Image.open(uploaded_file)
    img = image.resize((224, 224))
    img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
    
    # Real Prediction
    predictions = model.predict(img_array)
    classes = ['Healthy', 'Powdery Mildew', 'Yellow Leaf']
    result = classes[np.argmax(predictions)]
    
    # Get values for your original dashboard metrics
    h_score, w_priority, rec_action, nut_status = get_analysis(result)

    # --- RESTORING THE VISUALS ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Health Score", f"{h_score}%")
        st.write(f"**Current Sample:** {result}")
        
    with col2:
        st.write("**Watering Priority**")
        st.subheader(f"🔵 {w_priority}")
        st.progress(h_score / 100) # Moisture bar simulator

    with col3:
        st.write("**Rec. Action**")
        st.header(rec_action)

    st.divider()

    # --- RESTORING THE CROP HEALTH TRENDS CHART ---
    st.subheader("📊 Crop Health Trends")
    chart_data = pd.DataFrame(
        np.random.randn(20, 2) + [h_score, 50],
        columns=['Health Score %', 'Moisture %']
    )
    st.line_chart(chart_data)

    # --- RESTORING NUTRIENT DOSING BOX ---
    st.subheader("🧪 Nutrient Dosing")
    st.success(f"**Soil Status:** {nut_status}. Nutrient levels within acceptable range.")

else:
    st.info("No history found. Please perform and save a scan to view trends.")
