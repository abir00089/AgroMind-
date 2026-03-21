import streamlit as st
from PIL import Image, ImageStat
import pandas as pd
import numpy as np
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="AgroMind Ultimate", layout="wide", page_icon="🍀")

# --- 1. USER DATABASE & LOGIN LOGIC ---
# Initialize a mock database in session state if it doesn't exist
if 'user_db' not in st.session_state:
    st.session_state.user_db = {"admin": "agromind2026"} # Default account

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def auth_page():
    st.title("🔐 AgroMind Secure Portal")
    
    choice = st.radio("Select Action:", ["Sign In", "Sign Up"], horizontal=True)
    
    if choice == "Sign Up":
        with st.form("Signup Form"):
            st.subheader("Create a New Account")
            new_user = st.text_input("Choose Username")
            new_pw = st.text_input("Choose Password", type="password")
            confirm_pw = st.text_input("Confirm Password", type="password")
            signup_submit = st.form_submit_button("Create Account")
            
            if signup_submit:
                if new_user in st.session_state.user_db:
                    st.error("Username already exists!")
                elif new_pw != confirm_pw:
                    st.error("Passwords do not match!")
                elif len(new_user) < 3 or len(new_pw) < 4:
                    st.warning("Please enter a valid username/password.")
                else:
                    st.session_state.user_db[new_user] = new_pw
                    st.success("Account created! You can now Sign In.")
                    
    else:
        with st.form("Login Form"):
            st.subheader("Sign In to Access System")
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Sign In")
            
            if login_submit:
                if user in st.session_state.user_db and st.session_state.user_db[user] == pw:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.success(f"Welcome back, {user}!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

# --- 2. THE MAIN APP ---
if not st.session_state.logged_in:
    auth_page()
else:
    # Initialize session data for the app
    if 'history' not in st.session_state:
        st.session_state.history = []

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"👤 User: {st.session_state.current_user}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        if st.button("🧹 Clear All Data"):
            st.session_state.history = []
            st.success("History Purged.")
        
        if st.session_state.history:
            df_report = pd.DataFrame(st.session_state.history)
            csv = df_report.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Scan Report (CSV)", csv, "agromind_report.csv", "text/csv")
        
        st.divider()
        st.subheader("📖 Instructions")
        st.write("Scan leaves using Camera/Upload and monitor sensor telemetry below.")

    # --- APP TABS ---
    st.title("🍀 AgroMind Ultimate: Smart Farm Suite")
    tab1, tab2, tab3 = st.tabs(["🔍 AI Diagnosis", "📊 Sensors & Graphs", "🌳 Tree Care Guide"])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            mode = st.radio("Source:", ["Camera", "Upload File"])
            img_file = st.camera_input("Scan Leaf") if mode == "Camera" else st.file_uploader("Upload Image", type=["jpg", "png"])

        if img_file:
            img = Image.open(img_file).convert('RGB')
            with col_b:
                st.image(img, caption="Input Data", use_container_width=True)
            
            # Simulated CNN Feature extraction
            stat = ImageStat.Stat(img)
            r, g, b = stat.mean
            if g > r and g > b:
                diag, conf = "Healthy", 97.8
            elif r > g:
                diag, conf = "Yellow Leaf", 85.3
            else:
                diag, conf = "Powdery Mildew", 77.4

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Diagnosis", diag)
            c2.metric("Confidence", f"{conf}%")
            c3.metric("Status", "Saved")
            st.session_state.history.append({"User": st.session_state.current_user, "Time": time.strftime("%H:%M:%S"), "Result": diag})

    with tab2:
        st.subheader("📡 Real-time Environmental Telemetry")
        m1, m2, m3 = st.columns(3)
        soil = m1.slider("Soil Moisture (%)", 0, 100, 50)
        hum = m2.slider("Humidity (%)", 0, 100, 65)
        m3.progress(soil/100, text="Water Stress Index")
        st.line_chart(pd.DataFrame(np.random.randn(20, 2), columns=['Soil', 'Hum']))
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

    with tab3:
        st.subheader("🌳 Growth Optimization")
        st.info("Ensure Soil Moisture stays above 40% to avoid Water Stress.")
        st.success("For 'Yellow Leaf', apply Nitrogen-rich fertilizer (NPK 10-10-10).")
        st.warning("Maintain tree spacing to prevent humidity-based Mildew.")
