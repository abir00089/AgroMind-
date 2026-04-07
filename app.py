import streamlit as st
import requests
import joblib
from PIL import Image
import numpy as np
import pandas as pd
import datetime
import cv2
import time

# ================= CONFIG =================
st.set_page_config(page_title="AgroMind", layout="wide")

# ================= BACKEND =================
API_URL = "https://agromind-server.onrender.com/data"

# ================= LOAD MODEL =================
try:
    model = joblib.load("leaf_model.pkl")
except:
    model = None

# ================= SESSION =================
if "history" not in st.session_state:
    st.session_state.history = []

if "water_logs" not in st.session_state:
    st.session_state.water_logs = []

# ================= FETCH SENSOR DATA =================
@st.cache_data(ttl=5)
def get_sensor_data():
    try:
        res = requests.get(API_URL, timeout=5)
        if res.status_code == 200:
            return res.json()
        return {}
    except:
        return {}

sensor_data = get_sensor_data()

# ================= SOIL FERTILITY =================
def get_soil_fertility(ph):
    if ph < 5.5:
        return ("Strongly Acidic", "Poor", "red", "Add lime to reduce acidity")
    elif 5.5 <= ph < 6.5:
        return ("Slightly Acidic", "Good", "orange", "Suitable for most crops")
    elif 6.5 <= ph <= 7.5:
        return ("Neutral", "Excellent", "green", "Best condition for farming")
    elif 7.5 < ph <= 8.5:
        return ("Slightly Alkaline", "Moderate", "blue", "Add organic compost")
    else:
        return ("Strongly Alkaline", "Poor", "red", "Use sulfur or organic matter")

# ================= PREPROCESS =================
def preprocess(img):
    img = img.resize((256,256))
    img_array = np.array(img)
    blur = cv2.GaussianBlur(img_array,(5,5),0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    return img_array, hsv, gray

# ================= ANALYZE =================
def analyze_leaf(img, dryness):
    img_array, hsv, gray = preprocess(img)

    if model:
        try:
            img_resized = cv2.resize(img_array, (64,64))
            img_flat = img_resized.flatten().reshape(1, -1)
            prediction = model.predict(img_flat)[0]
        except:
            prediction = "Unknown"
    else:
        prediction = "Model not loaded"

    green = cv2.inRange(hsv, (30,40,40), (90,255,255))
    yellow = cv2.inRange(hsv, (15,50,50), (35,255,255))
    brown = cv2.inRange(hsv, (5,50,50), (20,255,200))
    edges = cv2.Canny(gray, 50, 150)

    total = 256*256
    green_ratio = np.sum(green>0)/total
    yellow_ratio = np.sum(yellow>0)/total
    brown_ratio = np.sum(brown>0)/total
    pest_ratio = np.sum(edges>0)/total

    health = green_ratio*100 - brown_ratio*150 - pest_ratio*120 - yellow_ratio*80 - dryness*0.15
    health = max(5,min(100,health))
    damage = 100-health

    return {
        "health": health,
        "damage": damage,
        "pest_ratio": pest_ratio,
        "yellow_ratio": yellow_ratio,
        "brown_ratio": brown_ratio,
        "ai_prediction": prediction
    }

# ================= DISEASE =================
def detect_disease(res, dryness):
    diseases = []
    solutions = []

    if res["brown_ratio"] > 0.15:
        diseases.append("Fungal Infection")
        solutions.append("Use antifungal spray")

    if res["pest_ratio"] > 0.05:
        diseases.append("Pest Attack")
        solutions.append("Use neem oil")

    if res["yellow_ratio"] > 0.25:
        diseases.append("Nutrient Deficiency")
        solutions.append("Add fertilizer")

    if dryness > 60:
        diseases.append("Water Stress")
        solutions.append("Increase watering")

    if not diseases:
        diseases = ["Healthy Leaf"]
        solutions = ["No action needed"]

    return diseases, solutions

# ================= UI =================
st.title("🌱 AgroMind Smart Farming System")

# ================= MENU =================
menu = st.sidebar.radio("Menu",[
    "Analysis",
    "History",
    "Water Tracker",
    "Batch Summary",
    "Guide",
    "Instructions"
])

dryness = st.sidebar.slider("Dryness Level",0,100,10)

# ================= ANALYSIS =================
if menu == "Analysis":

    # ===== LIVE SENSOR (NOW ONLY HERE) =====
    st.subheader("📡 Live Sensor Dashboard")

    if sensor_data:
        moisture = sensor_data.get("moisture", 0)
        temperature = sensor_data.get("temperature", 0)
        humidity = sensor_data.get("humidity", 0)
        ph = sensor_data.get("ph", 0)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌱 Moisture", f"{moisture}%")
        col2.metric("🌡 Temp", f"{temperature}°C")
        col3.metric("💧 Humidity", f"{humidity}%")
        col4.metric("⚗️ pH", ph)
    else:
        st.warning("⏳ Waiting for ESP32 data...")

    # ===== RESULT =====
    if sensor_data:
        st.subheader("🧠 Smart Farm Result")

        if moisture < 30:
            soil_status = "Dry"
            irrigation = "💧 Water Needed"
            color = "red"
        elif 30 <= moisture <= 60:
            soil_status = "Optimal"
            irrigation = "✅ No Water Needed"
            color = "green"
        else:
            soil_status = "Wet"
            irrigation = "⚠️ Stop Watering"
            color = "blue"

        st.markdown(f"**Soil Condition:** :{color}[{soil_status}]")
        st.markdown(f"**Irrigation:** {irrigation}")

        status, fertility, f_color, advice = get_soil_fertility(ph)

        st.markdown("### 🌾 Soil Fertility")
        st.markdown(f"**Type:** :{f_color}[{status}]")
        st.markdown(f"**Fertility:** {fertility}")
        st.markdown(f"**Advice:** {advice}")

    # ===== IMAGE INPUT =====
    st.subheader("📷 Leaf Analysis")

    img_file = st.file_uploader("Upload Image")
    cam_img = st.camera_input("Or Capture Image")

    img = None

    if img_file:
        img = Image.open(img_file)
    elif cam_img:
        img = Image.open(cam_img)

    if img:
        st.image(img)

        res = analyze_leaf(img, dryness)

        st.write("Health:", round(res["health"],2))
        st.write("Damage:", round(res["damage"],2))
        st.write("AI Prediction:", res["ai_prediction"])

        diseases, solutions = detect_disease(res, dryness)

        for i in range(len(diseases)):
            st.warning(diseases[i])
            st.write("Solution:", solutions[i])

# ================= HISTORY =================
elif menu == "History":
    st.dataframe(pd.DataFrame(st.session_state.history))

# ================= WATER =================
elif menu == "Water Tracker":
    water = st.number_input("Water (ml)")
    if st.button("Save"):
        st.session_state.water_logs.append({
            "date": datetime.datetime.now(),
            "water": water
        })
    st.write(st.session_state.water_logs)

# ================= BATCH SUMMARY =================
elif menu == "Batch Summary":
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.write("Average Health:", df["health"].mean())
        st.write("Average Damage:", df["damage"].mean())
    else:
        st.info("No data available")

# ================= GUIDE =================
elif menu == "Guide":
    st.title("🌱 AgroMind System")
    st.subheader("🌾 Crop Guide")

    st.markdown("""
**Rice:** Maintain soil, monitor pests and nutrients regularly  
**Wheat:** Maintain soil, monitor pests and nutrients regularly  
**Maize:** Maintain soil, monitor pests and nutrients regularly  
**Potato:** Maintain soil, monitor pests and nutrients regularly  
**Tomato:** Maintain soil, monitor pests and nutrients regularly  
**Onion:** Maintain soil, monitor pests and nutrients regularly  
**Sugarcane:** Maintain soil, monitor pests and nutrients regularly  
**Carrot:** Maintain soil, monitor pests and nutrients regularly  
**Spinach:** Maintain soil, monitor pests and nutrients regularly  
**Soybean:** Maintain soil, monitor pests and nutrients regularly  
""")

    st.markdown("---")
    st.subheader("❓ Ask Farming Question")

    q = st.text_input("Type your question")

    if st.button("Ask"):
        if q:
            st.success("🌿 Advice:")
            st.write("Ensure proper irrigation, nutrients, and pest monitoring.")
        else:
            st.warning("Enter a question")

# ================= INSTRUCTIONS =================
elif menu == "Instructions":
    st.subheader("📖 Farming Instructions & Tips")

    st.markdown("""
🌱 Water plants early morning or evening  

🧪 Use balanced fertilizers  

🍃 Monitor leaves regularly  

🌞 Ensure sunlight  

🧹 Remove damaged leaves  

💧 Use mulching  

🧴 Apply pesticide carefully  
""")

# ================= AUTO REFRESH =================
time.sleep(5)
st.rerun()
