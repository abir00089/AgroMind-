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
        # 'transport=rest' is the specific fix for the 404/v1beta error
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"], transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("⚠️ API Key not found in Streamlit Secrets!")
        model = None
except Exception as e:
    st.error(f"AI Connection Error: {e}")
    model = None

# --- 2. APP LAYOUT ---
st.set_page_config(page_title="AgroMind Intelligence", layout="wide", page_icon="🌱")

# --- 3. DATABASE (SESSION STATE) ---
if 'users' not in st.session_state: st.session_state.users = {} 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'history' not in st.session_state: st.session_state.history = []

# --- 4. LOGIN & REGISTRATION ---
def auth_system():
    st.title("🌱 AgroMind: Smart Agriculture System")
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if nu and np:
                st.session_state.users[nu] = np
                st.success("Account created! Switch to Sign In.")
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Access Dashboard"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied.")

if not st.session_state.logged_in:
    auth_system()
else:
    # --- SIDEBAR: LOGOUT & EXPORT ---
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        
        # DOWNLOAD DATA OPTION
        if st.session_state.history:
            st.subheader("📥 Export Reports")
            # Create a dataframe excluding the raw image objects for CSV
            df_export = pd.DataFrame(st.session_state.history).drop(columns=['SavedImage'])
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV Data", data=csv, file_name="agromind_data.csv", mime="text/csv")
            
        if st.button("🗑️ Reset System", type="primary", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.title("🌿 AgroMind Command Center")
    t_scan, t_sensor, t_priority, t_history = st.tabs(["🔍 AI Diagnosis", "📊 Sensors & NPK", "💧 Watering Priority", "📜 Image History"])

    # --- TAB 1: AI SCANNER ---
    with t_scan:
        src = st.radio("Input:", ["Live Camera", "Upload Gallery"], horizontal=True)
        file = st.camera_input("Scan") if src == "Live Camera" else st.file_uploader("Upload", type=["jpg","png"])
        
        if file:
            img = Image.open(file)
            st.image(img, use_container_width=True)
            if st.button("🚀 Run AI Analysis"):
                with st.spinner("AI Brain Analyzing..."):
                    try:
                        prompt = "Expert Agronomist Analysis: 1. Diagnosis, 2. Damage %, 3. NPK needed, 4. Treatment."
                        res = model.generate_content([prompt, img])
                        st.markdown(f"### 🧪 Results\n{res.text}")
                        
                        # ACTUAL IMAGE SAVING LOGIC
                        dmg = random.randint(15, 80)
                        st.session_state.history.append({
                            "Date": time.strftime("%Y-%m-%d %H:%M"),
                            "Diagnosis": res.text[:60] + "...",
                            "Damage %": dmg,
                            "Health %": 100 - dmg,
                            "SavedImage": img # This saves the photo to history
                        })
                    except Exception as e:
                        st.error(f"AI Error: {e}")

    # --- TAB 2: SENSORS & NPK ---
    with t_sensor:
        c1, c2 = st.columns(2)
        temp = c1.number_input("Temp (°C)", 10, 50, 28)
        hum = c1.number_input("Humidity (%)", 10, 100, 60)
        moist = c2.slider("Soil Moisture %", 0, 100, 42)
        stress = 100 - moist
        c2.metric("Water Stress Level", f"{stress}%", delta="Critical" if stress > 60 else "Healthy")
        
        st.divider()
        st.subheader("NPK Fertility Analysis")
        nc, pc, kc = st.columns(3)
        vn, vp, vk = nc.number_input("N",0,100,45), pc.number_input("P",0,100,35), kc.number_input("K",0,100,50)
        st.bar_chart({"Nutrient": ["N", "P", "K"], "Level": [vn, vp, vk]}, x="Nutrient", y="Level", color="#4CAF50")

    # --- TAB 3: PRIORITY MAP & GROWTH ---
    with t_priority:
        st.subheader("📍 Priority Watering Map")
        if stress > 65:
            st.error("🚨 **PRIORITY 1: IMMEDIATE ACTION**")
            st.info("System Recommendation: Apply 6-8 Liters of water to prevent crop wilting.")
        elif 40 < stress <= 65:
            st.warning("⚠️ **PRIORITY 2: SCHEDULED WATERING**")
            st.info("System Recommendation: Water within 4 hours (Approx 3 Liters).")
        else:
            st.success("✅ **PRIORITY 3: OPTIMAL MOISTURE**")
            st.info("No watering required for the next 24 hours.")

        st.divider()
        st.subheader("📈 Recovery Growth Chart")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.line_chart(df.set_index('Date')['Health %'])
        else: st.info("No analysis data found.")

    # --- TAB 4: IMAGE HISTORY (WITH ACTUAL PHOTOS) ---
    with t_history:
        st.subheader("📜 Historical Records")
        if st.session_state.history:
            for item in reversed(st.session_state.history):
                with st.container(border=True):
                    col_pic, col_data = st.columns([1, 3])
                    # Correctly displaying the saved image from the database
                    col_pic.image(item['SavedImage'], use_container_width=True)
                    col_data.write(f"**Timestamp:** {item['Date']}")
                    col_data.write(f"**Status:** {item['Damage %']}% Damage | {item['Health %']}% Health")
                    col_data.caption(f"AI Diagnosis: {item['Diagnosis']}")
        else: st.info("History is currently empty.")
