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
API_URL = "https://agromind-server.onrender.com"

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
        "yellow_mask": yellow,
        "brown_mask": brown,
        "pest_mask": edges,
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
st.title("🌱 AgroMind System")

# ================= LIVE DATA =================
st.subheader("📡 Live Sensor Data")

try:
    res = requests.get(API_URL, timeout=10)
    data = res.json()

    st.success("✅ Connected to Backend")
    st.json(data)

except:
    st.warning("⏳ Waiting for ESP32 data...")

# ================= MENU =================
menu = st.sidebar.radio("Menu",["Analysis","History","Water Tracker"])
dryness = st.sidebar.slider("Dryness Level",0,100,10)

# ================= ANALYSIS =================
if menu == "Analysis":

    img_file = st.file_uploader("Upload Leaf Image")

    if img_file:
        img = Image.open(img_file)
        st.image(img)

        res = analyze_leaf(img, dryness)

        st.write("Health:", round(res["health"],2))
        st.write("Damage:", round(res["damage"],2))

        diseases, solutions = detect_disease(res, dryness)

        for i in range(len(diseases)):
            st.warning(diseases[i])
            st.write("Solution:", solutions[i])

        if st.button("Save"):
            st.session_state.history.append({
                "date": datetime.datetime.now(),
                "health": res["health"],
                "damage": res["damage"]
            })

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

# ================= AUTO REFRESH =================
time.sleep(5)
st.rerun()
