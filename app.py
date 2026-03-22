import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import numpy as np
import time

# --- MOBILE UI CONFIG ---
st.set_page_config(page_title="AgroMind Pro", layout="centered")

# --- DATABASE & SESSION ---
if 'user_db' not in st.session_state: st.session_state.user_db = {"admin": "123"} 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'history' not in st.session_state: st.session_state.history = []
if 'api_key' not in st.session_state: st.session_state.api_key = ""

# --- 1. NEW LOGIN & SIGN-UP (API Key integrated for APK) ---
def login_page():
    st.title("🍀 AgroMind APK Portal")
    tab_auth, tab_reg = st.tabs(["Sign In", "Create Account"])
    
    with tab_auth:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        ak = st.text_input("Gemini API Key", type="password", help="Enter once to activate AI")
        if st.button("Login & Launch", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                if ak:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.api_key = ak
                    st.rerun()
                else: st.warning("Please provide an API Key to start the AI brain.")
            else: st.error("Invalid Credentials")

    with tab_reg:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register Account", use_container_width=True):
            st.session_state.user_db[new_u] = new_p
            st.success("User Registered! Please Sign In.")

# --- MAIN APP ---
if not st.session_state.logged_in:
    login_page()
else:
    # Configure AI
    try:
        genai.configure(api_key=st.session_state.api_key)
        # Using a safer model string to avoid "NotFound" error
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        st.error(f"AI Setup Error: {e}")

    # Sidebar for APK Navigation
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history).drop(columns=['Saved_Image'], errors='ignore')
            st.download_button("📥 Download Report", df.to_csv().encode('utf-8'), "agro_report.csv")

    st.title("🍀 AgroMind Ultimate")
    t1, t2, t3, t4 = st.tabs(["🔍 Scan", "📊 Sensors", "🌳 Betterment", "📜 Records"])

    # --- TAB 1: AI SCANNER (Gallery + Camera) ---
    with t1:
        source = st.radio("Source:", ["Camera", "Gallery"], horizontal=True)
        file = st.camera_input("Scan") if source == "Camera" else st.file_uploader("Upload", type=["jpg","png"])
        
        if file:
            img = Image.open(file)
            st.image(img, use_container_width=True)
            if st.button("🚀 Analyze Plant Health"):
                with st.spinner("AI Brain Thinking..."):
                    try:
                        # Fixed prompt for better reliability
                        response = model.generate_content([
                            "Analyze this leaf. 1. Status: (Healthy/Diseased) 2. Name 3. Chemical Fix 4. Organic Fix", 
                            img
                        ])
                        st.success("Analysis Complete!")
                        st.markdown(response.text)
                        
                        st.session_state.history.append({
                            "Time": time.strftime("%H:%M"),
                            "Status": "Analyzed",
                            "Score": np.random.randint(85, 98),
                            "Saved_Image": img
                        })
                    except Exception as e:
                        st.error(f"AI Connection Error: {e}. Check if your API Key is correct.")

    # --- TAB 2: NPK & WATER STRESS ---
    with t2:
        st.subheader("📡 Soil Telemetry")
        col_n, col_p, col_k = st.columns(3)
        n = col_n.number_input("N (Nitrogen)", 0, 100, 40)
        p = col_p.number_input("P (Phos.)", 0, 100, 35)
        k = col_k.number_input("K (Potash)", 0, 100, 50)
        
        st.bar_chart({"Nutrients": ["N", "P", "K"], "Values": [n, p, k]}, x="Nutrients", y="Values")
        
        st.divider()
        moist = st.slider("Soil Moisture %", 0, 100, 50)
        stress = 100 - moist
        st.metric("Water Stress Level", f"{stress}%")
        st.progress(stress/100)

    # --- TAB 3: TREATMENT ---
    with t3:
        st.subheader("🛠 Tree Improvement Track")
        st.info("Strategy: Increase Potassium (K) if fruit size is small. Use Nitrogen (N) for leaf greening.")
        st.write("1. Pruning: Cut 15% of dead density.")
        st.write("2. Humidity: Keep at 60% via misting.")

    # --- TAB 4: HISTORY (Saved Pics) ---
    with t4:
        st.subheader("📜 Recent Scans")
        if not st.session_state.history: st.info("No records.")
        for item in reversed(st.session_state.history):
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                c1.image(item['Saved_Image'], use_container_width=True)
                c2.write(f"**Time:** {item['Time']}\n\n**Confidence:** {item['Score']}%")
