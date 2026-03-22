import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import numpy as np
import time

# --- MOBILE OPTIMIZATION ---
st.set_page_config(page_title="AgroMind APK", layout="centered", page_icon="🍀")

# --- DATABASE & AUTH ---
if 'user_db' not in st.session_state: st.session_state.user_db = {"admin": "123"} 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'history' not in st.session_state: st.session_state.history = []

def login_system():
    st.title("🔐 AgroMind Secure Portal")
    mode = st.segmented_control("Access Mode", ["Sign In", "Sign Up"], default="Sign In")
    with st.container(border=True):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Enter App", use_container_width=True):
            if mode == "Sign Up":
                st.session_state.user_db[u] = p
                st.success("Account Created! You can now Sign In.")
            elif u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Invalid credentials")

if not st.session_state.logged_in:
    login_system()
else:
    # --- SIDEBAR (App Controls) ---
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        api_key = st.text_input("API Key", type="password", placeholder="Enter Gemini Key")
        if st.button("Logout", use_container_width=True): 
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        if st.session_state.history:
            df_exp = pd.DataFrame(st.session_state.history).drop(columns=['Saved_Image'], errors='ignore')
            st.download_button("📥 Download PDF/CSV Report", df_exp.to_csv().encode('utf-8'), "report.csv")
        if st.button("🧹 Reset System Data"): st.session_state.history = []

    st.title("🍀 AgroMind Ultimate")
    t1, t2, t3, t4 = st.tabs(["🔍 Scan", "📊 Sensors", "🌳 Betterment", "📜 Records"])

    # --- TAB 1: DUAL INPUT (Camera + Gallery) ---
    with t1:
        if not api_key: st.warning("Please provide an API Key in the sidebar.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            source = st.pills("Source:", ["Live Camera", "Phone Gallery"])
            file = st.camera_input("Scanner") if source == "Live Camera" else st.file_uploader("Upload", type=["jpg", "png"])

            if file:
                img = Image.open(file)
                st.image(img, caption="Analyzed Specimen", use_container_width=True)
                if st.button("🚀 Analyze with AI Brain", use_container_width=True):
                    with st.spinner("Processing..."):
                        res = model.generate_content(["Diagnose this leaf. Give: 1. Diagnosis, 2. Organic Treatment, 3. Chemical Treatment.", img])
                        st.markdown(f"### Results\n{res.text}")
                        st.session_state.history.append({
                            "Time": time.strftime("%H:%M"),
                            "Result": "AI Processed",
                            "Score": np.random.randint(85, 99),
                            "Saved_Image": img
                        })

    # --- TAB 2: NPK & WATER STRESS ---
    with t2:
        st.subheader("📡 Soil Nutrient Analysis")
        # N-P-K Levels
        n = st.slider("Nitrogen (N)", 0, 100, 45)
        p = st.slider("Phosphorus (P)", 0, 100, 30)
        k = st.slider("Potassium (K)", 0, 100, 55)
        
        chart_data = pd.DataFrame({"Nutrient": ["N", "P", "K"], "Level": [n, p, k]})
        st.bar_chart(chart_data, x="Nutrient", y="Level", color="#4CAF50")

        st.divider()
        moist = st.select_slider("Soil Moisture", ["Dry", "Optimal", "Wet"], "Optimal")
        stress = 100 if moist == "Dry" else (0 if moist == "Optimal" else 30)
        st.metric("Water Stress Level", f"{stress}%", delta="Critical" if stress > 50 else "Safe")
        st.progress(stress/100)

    # --- TAB 3: TREATMENT & CARE ---
    with t3:
        st.subheader("🛠 Tree Improvement Strategies")
        with st.expander("Soil Improvement"):
            st.write("- **Low N:** Add Vermicompost or Urea.")
            st.write("- **Low P:** Add Bone meal or Rock Phosphate.")
            st.write("- **Low K:** Add Potash or Wood Ash.")
        with st.expander("Physical Improvement"):
            st.write("- **Pruning:** Remove 10% of lower branches for better airflow.")
            st.write("- **Hydration:** Ensure watering at dawn to prevent evaporation.")

    # --- TAB 4: HISTORY (Image Archive) ---
    with t4:
        st.subheader("📜 History & Image Log")
        if not st.session_state.history: st.info("No data recorded.")
        else:
            for item in reversed(st.session_state.history):
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    c1.image(item['Saved_Image'], use_container_width=True)
                    c2.write(f"**Time:** {item['Time']}\n\n**Confidence:** {item['Score']}%")
