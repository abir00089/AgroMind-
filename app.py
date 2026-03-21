import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import pandas as pd

# --- 1. SET PAGE CONFIG (Must be the first Streamlit command) ---
st.set_page_config(page_title="AgroMind Ultimate", layout="wide")

# --- 2. LOAD THE BRAIN (Your AI Model) ---
@st.cache_resource
def load_my_model():
    # Make sure your file on GitHub is named exactly 'model.h5'
    return tf.keras.models.load_model('model.h5')

try:
    model = load_my_model()
except Exception as e:
    st.error(f"Brain failed to load. Error: {e}")

# --- 3. THE ADVICE LOGIC ---
def get_analysis(prediction_label):
    """Matches the AI result to the Dashboard data"""
    if "Healthy" in prediction_label:
        return 95, "STABLE", "Maintain current schedule", "Optimal"
    elif "Mildew" in prediction_label or "White" in prediction_label:
        return 62, "STABLE", "Apply Fungicide", "Low Potassium"
    elif "Yellow" in prediction_label:
        return 45, "WARNING", "Apply Nitrogen", "Nitrogen Deficiency"
    
    return 50, "MODERATE", "Consult Expert", "Inconsistent"

# --- 4. DASHBOARD UI ---
st.title("AgroMind Ultimate")
st.write("Professional Crop Health Monitoring System")

uploaded_file = st.file_uploader("Scan New Sample", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # --- IMAGE PROCESSING ---
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Sample', width=400)
    
    # Pre-processing for the AI (Resize to match your training)
    img = image.resize((224, 224)) 
    img_array = np.expand_dims(np.array(img) / 255.0, axis=0)

    # --- THE BRAIN AT WORK ---
    predictions = model.predict(img_array)
    # IMPORTANT: Change these names to match your dataset folders!
    classes = ['Powdery Mildew', 'Yellow Leaf', 'Healthy'] 
    result = classes[np.argmax(predictions)]
    
    # Get dashboard values
    h_score, w_priority, rec_action, nut_status = get_analysis(result)

    # --- DISPLAY METRICS (TOP ROW) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Health Score", f"{h_score}%")
        st.write(f"**Condition:** {result}")
    with col2:
        st.write("**Watering Priority**")
        st.subheader(f"🔵 {w_priority}")
        st.progress(h_score / 100)
    with col3:
        st.write("**Rec. Action**")
        st.info(rec_action)

    st.divider()

    # --- CROP HEALTH TRENDS (CHART) ---
    st.subheader("📊 Crop Health Trends")
    chart_data = pd.DataFrame(
        np.random.randn(20, 2) + [h_score, 50],
        columns=['Health Score %', 'Moisture %']
    )
    st.line_chart(chart_data)

    # --- NUTRIENT DOSING ---
    st.subheader("🧪 Nutrient Dosing")
    st.success(f"**Soil Status:** {nut_status}. System ready for dosing.")

else:
    st.info("Please perform a scan to view data trends.")
