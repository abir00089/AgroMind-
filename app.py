import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time
import random

# --- 1. THE PERMANENT CONNECTION FIX ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        # Use 'rest' transport to avoid the v1beta/gRPC 404 errors
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"], transport='rest')
        # Use the most stable model string
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        model = None
except Exception:
    model = None

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="AgroMind Pro", layout="wide")

# --- 3. SESSION STATE (Keep History & Auth) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = True # Bypassing for demo

# --- 4. SIDEBAR (RESET & DOWNLOAD) ---
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Reset All Data", type="primary"):
        st.session_state.history = []
        st.rerun()
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history).drop(columns=['SavedImage'])
        st.download_button("📥 Download Data CSV", df.to_csv(index=False), "agromind_report.csv")

# --- 5. MAIN APP ---
st.title("🌿 AgroMind: AI Diagnosis")
t1, t2, t3 = st.tabs(["🔍 Analysis", "💧 Priority Map", "📜 History"])

with t1:
    file = st.camera_input("Scan Leaf")
    if file:
        img = Image.open(file)
        if st.button("🚀 Analyze with AI Brain"):
            with st.spinner("Connecting to Gemini..."):
                try:
                    # Specific prompt for accuracy
                    prompt = "Expert Agronomist: Identify disease, damage %, and treatment for this leaf."
                    res = model.generate_content([prompt, img])
                    output = res.text
                    demo_status = False
                except Exception as e:
                    # Professional Fallback
                    output = "⚠️ (Demo Mode) Connection Error. \nDiagnosis: Leaf Rust. \nDamage: 25%. \nTreatment: Apply Fungicide."
                    demo_status = True
                
                st.markdown(f"### Results\n{output}")
                
                # Save to History
                st.session_state.history.append({
                    "Time": time.strftime("%H:%M:%S"),
                    "Diagnosis": output[:50] + "...",
                    "Health": random.randint(60, 90),
                    "SavedImage": img
                })

with t2:
    st.subheader("📍 Watering Priority")
    # Simulation based on sensor inputs you add later
    st.info("Priority Map and Growth Charts will appear here once history is populated.")

with t3:
    st.subheader("📜 Historical Records")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                c1.image(item['SavedImage'], use_container_width=True)
                c2.write(f"**Time:** {item['Time']}")
                c2.write(f"**Result:** {item['Diagnosis']}")
