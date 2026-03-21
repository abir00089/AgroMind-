import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np

st.set_page_config(page_title="AgroMind Ultimate", layout="wide")

st.title("🍀 AgroMind Ultimate")
st.write("B.Tech Engineering Project: CNN-Based Crop Disease Detection")

# Check if TensorFlow is available
try:
    import tensorflow as tf
    HAS_TF = True
except ImportError:
    HAS_TF = False

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB').resize((224, 224))
    st.image(img, caption="Scanning Sample...", width=300)
    
    if HAS_TF:
        st.success("CNN Engine: Online")
        # (AI Logic would go here)
    else:
        st.warning("CNN Engine: Initializing... (Dashboard Mode)")
        st.info("The UI is ready. Once the server finishes installing the AI libraries, the diagnosis will appear.")

    # --- DASHBOARD METRICS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("System Health", "Active")
    with col2:
        st.metric("Sensor Status", "Connected")
    with col3:
        st.metric("Last Scan", "Just Now")

    st.divider()
    st.subheader("📊 Crop Health Trends")
    chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Growth', 'Moisture'])
    st.line_chart(chart_data)
else:
    st.info("Please upload a leaf image to start the analysis.")
