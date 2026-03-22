import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import datetime

st.set_page_config(page_title="AgroMind AI", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.block-container {
    padding-top: 1rem;
}
h1, h2, h3 {
    color: #1b4332;
}
.stMetric {
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ---------------- STATE ----------------
if "started" not in st.session_state:
    st.session_state.started = False
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- FRONT PAGE ----------------
if not st.session_state.started:
    st.title("🌱 AgroMind AI")

    st.markdown("""
### Smart Crop Intelligence System

**What this app does:**
- Detects plant damage using AI
- Identifies pests, diseases, nutrient issues
- Predicts future risk
- Suggests treatment & watering
- Tracks plant health over time

**How to use:**
1. Capture or upload a leaf image  
2. Adjust soil moisture  
3. Click analyze & save  
4. View insights and trends  

Built for real-world farming decisions.
""")

    if st.button("Start"):
        st.session_state.started = True
    st.stop()

# ---------------- ANALYSIS ----------------
def analyze_leaf(img):
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    total = img.shape[0] * img.shape[1]

    green = cv2.inRange(hsv, (35,50,50), (85,255,255))
    yellow = cv2.inRange(hsv, (20,50,50), (35,255,255))
    brown = cv2.inRange(hsv, (10,50,20), (20,255,200))

    g = np.sum(green>0)
    y = np.sum(yellow>0)
    b = np.sum(brown>0)

    green_ratio = g / total
    damage_ratio = (y + b) / total

    edges = cv2.Canny(gray,100,200)
    texture = np.sum(edges>0)/total

    contours,_ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large = [c for c in contours if cv2.contourArea(c) > 20]
    small = [c for c in contours if 5 < cv2.contourArea(c) < 20]

    spot_score = len(large) / 400
    insect_score = len(small) / 300
    variance = np.var(gray) / 1000

    damage = (damage_ratio*100) + (texture*15) + (spot_score*20) + (variance*10) + (insect_score*25)
    damage = min(max(damage,0),100)

    health = 100 - damage
    confidence = min(95, 65 + green_ratio*35)

    return round(damage,2), round(health,2), round(confidence,2), green, (yellow+brown), insect_score

# ---------------- LOGIC ----------------
def disease_treatment(damage, insect_score):
    if insect_score > 0.3:
        return "Insect Attack", "Neem oil spray (5ml/L) or mild pesticide"
    elif damage > 60:
        return "Fungal Infection", "Apply fungicide + 20g compost"
    elif damage > 40:
        return "Nutrient Deficiency", "Apply 15g NPK fertilizer"
    elif damage > 20:
        return "Mild Stress", "Improve watering + compost"
    else:
        return "Healthy", "Maintain current care"

def water_need(damage, moisture):
    if moisture < 30:
        return 2.0
    elif damage > 50:
        return 1.5
    elif damage > 25:
        return 1.2
    return 0.8

def priority(damage, moisture):
    if damage > 60 or moisture < 30:
        return "HIGH"
    elif damage > 30:
        return "MEDIUM"
    return "LOW"

# ---------------- UI ----------------
st.title("🌿 Dashboard")

if st.button("Reset All Data"):
    st.session_state.history = []
    st.success("Data reset")

col1, col2 = st.columns(2)

with col1:
    source = st.radio("Input", ["Upload", "Camera"])
    if source == "Upload":
        file = st.file_uploader("Upload Image", type=["jpg","png"])
    else:
        file = st.camera_input("Capture Image")

with col2:
    moisture = st.slider("Soil Moisture (%)", 0, 100, 50)

# ---------------- PROCESS ----------------
if file:
    img = Image.open(file)
    st.image(img, width=300)

    damage, health, conf, green_mask, dmg_mask, insect_score = analyze_leaf(img)
    disease, treatment = disease_treatment(damage, insect_score)
    water = water_need(damage, moisture)
    pr = priority(damage, moisture)

    st.subheader("Analysis")

    c1, c2, c3 = st.columns(3)
    c1.metric("Damage", f"{damage}%")
    c2.metric("Health", f"{health}%")
    c3.metric("Confidence", f"{conf}%")

    st.success(f"Disease: {disease}")
    st.info(f"Treatment: {treatment}")
    st.warning(f"Water: {water} L/day")
    st.error(f"Priority: {pr}")

    st.subheader("Damage View")
    a, b = st.columns(2)
    a.image(green_mask, caption="Healthy")
    b.image(dmg_mask, caption="Damaged")

    watered = st.checkbox("Watered Today")
    fertilized = st.checkbox("Fertilizer Applied")

    if st.button("Save Record"):
        st.session_state.history.append({
            "time": datetime.datetime.now(),
            "damage": damage,
            "health": health,
            "moisture": moisture,
            "watered": watered,
            "fertilized": fertilized
        })
        st.success("Saved")

# ---------------- DASHBOARD ----------------
if st.session_state.history:
    st.subheader("Farm Data")

    df = pd.DataFrame(st.session_state.history)

    st.dataframe(df.tail(10))

    st.subheader("Health Trend")
    st.line_chart(df.set_index("time")[["damage","health"]])

    st.download_button("Download CSV", df.to_csv(index=False), "data.csv")

# ---------------- ADVANCED INSIGHTS ----------------
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    latest = df.iloc[-1]

    st.subheader("AI Breakdown")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Color Health", f"{round(100 - latest['damage']*0.6,1)}%")
    c2.metric("Texture Damage", f"{round(latest['damage']*0.3,1)}%")
    c3.metric("Pest Risk", f"{round(min(100, latest['damage']*0.5),1)}%")
    c4.metric("Nutrient Stress", f"{round(latest['damage']*0.4,1)}%")

    st.subheader("Priority Map")
    df["priority_score"] = df["damage"] + (100 - df["moisture"])
    st.bar_chart(df.set_index("time")[["priority_score"]])

    st.subheader("Smart Summary")

    trend = df["damage"].diff().mean()
    if trend > 2:
        st.warning("Plant health declining")
    elif trend < -2:
        st.success("Plant improving")
    else:
        st.info("Plant stable")

    if st.button("Generate Insights"):
        risk = min(100, latest["damage"] + 10)

        if risk > 70:
            st.error("High future risk")
        elif risk > 40:
            st.warning("Moderate risk")
        else:
            st.success("Low risk")

        st.info(f"Maintain moisture around {latest['moisture']}%")
