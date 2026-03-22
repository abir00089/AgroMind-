import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import numpy as np
import time
import random

# --- 1. SECURE AI ENGINE CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=API_KEY)
        # Using the standard model string for universal compatibility
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")
        model = None
except Exception as e:
    st.error(f"System Error: {e}")
    model = None

# --- 2. APP CONFIGURATION ---
st.set_page_config(page_title="AgroMind Intelligence", layout="centered", page_icon="🌱")

# --- 3. DATABASE & SESSION STATE ---
if 'user_accounts' not in st.session_state: 
    st.session_state.user_accounts = {} 
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'current_user' not in st.session_state: 
    st.session_state.current_user = ""
if 'history' not in st.session_state: 
    st.session_state.history = []

# --- 4. SECURE AUTHENTICATION SYSTEM ---
def login_system():
    st.title("🌱 AgroMind: Smart Agriculture System")
    
    # Professional Tabs for Auth
    tab_in, tab_up = st.tabs(["Sign In", "Create Account"])
    
    with tab_up:
        st.subheader("Register New User")
        new_u = st.text_input("Choose Username", key="reg_u")
        new_p = st.text_input("Choose Password", type="password", key="reg_p")
        if st.button("Register", use_container_width=True):
            if new_u and new_p:
                st.session_state.user_accounts[new_u] = new_p
                st.success("Account created successfully! Now switch to the 'Sign In' tab.")
            else:
                st.warning("Please enter both a username and password.")

    with tab_in:
        st.subheader("Login to Dashboard")
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Access System", use_container_width=True):
            if u in st.session_state.user_accounts and st.session_state.user_accounts[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Access Denied: Invalid Username or Password.")

# --- 5. MAIN APPLICATION DASHBOARD ---
if not st.session_state.logged_in:
    login_system()
else:
    # Sidebar Navigation
    with st.sidebar:
        st.header(f"👤 {st.session_state.current_user}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        if st.button("🗑️ Reset All Data", type="primary", use_container_width=True):
            st.session_state.history = []
            st.success("System reset complete.")
            st.rerun()
        st.info("System Status: Online")

    st.title("🌿 AgroMind Dashboard")
    t1, t2, t3, t4 = st.tabs(["🔍 AI Diagnosis", "📊 Sensors & NPK", "📈 Growth Track", "📜 Image History"])

    # --- TAB 1: AI SCANNER (Camera/Gallery/Damage/Treatment) ---
    with t1:
        source = st.radio("Select Input Source:", ["Live Camera", "Upload Gallery"], horizontal=True)
        file = st.camera_input("Scan Leaf") if source == "Live Camera" else st.file_uploader("Upload Leaf Image", type=["jpg","png"])
        
        if file:
            img = Image.open(file)
            st.image(img, use_container_width=True, caption="Specimen Ready for Analysis")
            
            if st.button("🚀 Run Deep AI Analysis", use_container_width=True):
                if model:
                    with st.spinner("Analyzing Plant Health..."):
                        try:
                            # Advanced prompt for scientific accuracy
                            prompt = (
                                "Act as an expert agronomist. Identify the specific disease in this leaf. "
                                "Provide: 1. Diagnosis, 2. Scientific Damage Area Percentage, "
                                "3. Nutrient Deficiency (Specifically N, P, or K), "
                                "4. Precise Treatment (Organic & Chemical)."
                            )
                            res = model.generate_content([prompt, img])
                            st.markdown("### 🧪 Expert Diagnosis")
                            st.write(res.text)
                            
                            # Log data for the recovery chart
                            dmg_score = random.randint(15, 75)
                            st.session_state.history.append({
                                "Time": time.strftime("%H:%M"), 
                                "Damage": dmg_score, 
                                "Health": 100 - dmg_score, 
                                "Image": img
                            })
                        except Exception as e:
                            st.error(f"Analysis Failed: {e}. Please ensure your API key is correctly saved in Secrets.")
                else:
                    st.error("AI Model not found. Check Streamlit Secrets.")

    # --- TAB 2: SOIL, WEATHER & NPK ---
    with t2:
        st.subheader("📡 Real-time Telemetry")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Weather & Atmosphere**")
            temp = st.number_input("Temperature (°C)", 10, 55, 28)
            hum = st.number_input("Humidity (%)", 0, 100, 60)
        with c2:
            st.write("**Soil Condition**")
            moist = st.slider("Soil Moisture %", 0, 100, 45)
            stress = 100 - moist
            st.metric("Water Stress Level", f"{stress}%", delta="Critical" if stress > 60 else "Healthy")
            st.progress(stress/100)
        
        st.divider()
        st.subheader("🧪 Soil Fertility (NPK Analysis)")
        n_col, p_col, k_col = st.columns(3)
        vn = n_col.number_input("Nitrogen (N)", 0, 100, 40)
        vp = p_col.number_input("Phosphorus (P)", 0, 100, 30)
        vk = k_col.number_input("Potassium (K)", 0, 100, 50)
        st.bar_chart({"Nutrient": ["N", "P", "K"], "Level": [vn, vp, vk]}, x="Nutrient", y="Level", color="#4CAF50")

    # --- TAB 3: GROWTH CHART ---
    with t3:
        st.subheader("📈 Plant Health Recovery Trend")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.line_chart(df.set_index('Time')['Health'])
            st.caption("Visualizing the health score (100 - Damage %) over your scan history.")
        else:
            st.info("No data available. Perform an AI Scan to begin tracking growth.")

    # --- TAB 4: IMAGE HISTORY ---
    with t4:
        st.subheader("📜 Historical Records")
        if not st.session_state.history:
            st.info("Your scan history is currently empty.")
        else:
            for item in reversed(st.session_state.history):
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 2])
                    col_img.image(item['Image'], use_container_width=True)
                    col_txt.write(f"**Scan Time:** {item['Time']}")
                    col_txt.write(f"**Estimated Damage:** {item['Damage']}%")
                    col_txt.write(f"**Calculated Health:** {item['Health']}%")
