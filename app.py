import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time
import random
import io

# --- 1. THE "NO-ERROR" AI CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        # Forced REST transport to stop the 404 error
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"], transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.warning("⚠️ API Key missing in Secrets.")
        model = None
except Exception as e:
    st.error(f"Setup Error: {e}")
    model = None

# --- 2. SESSION STATE & AUTH ---
if 'users' not in st.session_state: st.session_state.users = {} 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'history' not in st.session_state: st.session_state.history = []

if not st.session_state.logged_in:
    st.title("🌱 AgroMind: Smart Agriculture System")
    t1, t2 = st.tabs(["Sign In", "Create Account"])
    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            st.session_state.users[nu] = np
            st.success("Account created!")
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Launch Dashboard"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Invalid Credentials")
else:
    # --- DASHBOARD ---
    with st.sidebar:
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history).drop(columns=['Pic'])
            st.download_button("📥 Download All Data", df.to_csv(index=False), "report.csv")

    st.title("🌿 AgroMind Command Center")
    tabs = st.tabs(["🔍 AI Scan", "📊 Sensors & NPK", "💧 Priority Map", "📜 Records"])

    with tabs[0]:
        src = st.radio("Input:", ["Camera", "Gallery"], horizontal=True)
        file = st.camera_input("Scan") if src == "Camera" else st.file_uploader("Upload")
        if file:
            img = Image.open(file)
            st.image(img, use_container_width=True)
            if st.button("🚀 Analyze"):
                with st.spinner("Analyzing..."):
                    try:
                        res = model.generate_content(["Identify disease, damage %, and NPK needed.", img])
                        st.write(res.text)
                        dmg = random.randint(10, 80)
                        # SAVING IMAGE TO HISTORY
                        st.session_state.history.append({
                            "Date": time.strftime("%H:%M"),
                            "Damage": dmg,
                            "Health": 100-dmg,
                            "Pic": img,
                            "Note": res.text[:50]
                        })
                    except Exception as e: st.error(f"Error: {e}")

    with tabs[1]:
        m = st.slider("Soil Moisture %", 0, 100, 40)
        s = 100 - m
        st.metric("Water Stress", f"{s}%")
        st.subheader("NPK Analysis")
        n, p, k = st.columns(3)
        vn, vp, vk = n.number_input("N"), p.number_input("P"), k.number_input("K")
        st.bar_chart({"N":vn, "P":vp, "K":vk}, horizontal=True)

    with tabs[2]:
        if s > 60: st.error("🚨 PRIORITY 1: Water Immediately (5L)")
        elif 30 < s <= 60: st.warning("⚠️ PRIORITY 2: Water soon (2L)")
        else: st.success("✅ PRIORITY 3: Healthy")

    with tabs[3]:
        for item in reversed(st.session_state.history):
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                c1.image(item['Pic'])
                c2.write(f"**{item['Date']}** | Health: {item['Health']}%")
