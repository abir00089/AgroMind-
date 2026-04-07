import streamlit as st
import requests
import joblib
from PIL import Image
import numpy as np
import pandas as pd
import datetime
import cv2

# ================= CONFIG =================
st.set_page_config(page_title="AgroMind", layout="wide")

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

# ================= FETCH SENSOR =================
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

# ================= FUNCTIONS =================
def get_soil_fertility(ph):
    if ph < 5.5:
        return ("Strongly Acidic", "Poor", "red", "Add lime")
    elif 5.5 <= ph < 6.5:
        return ("Slightly Acidic", "Good", "orange", "Good for crops")
    elif 6.5 <= ph <= 7.5:
        return ("Neutral", "Excellent", "green", "Best condition")
    elif 7.5 < ph <= 8.5:
        return ("Alkaline", "Moderate", "blue", "Add compost")
    else:
        return ("Strongly Alkaline", "Poor", "red", "Use sulfur")

def preprocess(img):
    img = img.resize((256,256))
    arr = np.array(img)
    blur = cv2.GaussianBlur(arr,(5,5),0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    return arr, hsv, gray

def analyze_leaf(img, dryness):
    arr, hsv, gray = preprocess(img)

    if model:
        try:
            small = cv2.resize(arr,(64,64)).flatten().reshape(1,-1)
            pred = model.predict(small)[0]
        except:
            pred = "Unknown"
    else:
        pred = "Model not loaded"

    green = cv2.inRange(hsv,(30,40,40),(90,255,255))
    yellow = cv2.inRange(hsv,(15,50,50),(35,255,255))
    brown = cv2.inRange(hsv,(5,50,50),(20,255,200))
    edges = cv2.Canny(gray,50,150)

    total = 256*256
    g = np.sum(green>0)/total
    y = np.sum(yellow>0)/total
    b = np.sum(brown>0)/total
    p = np.sum(edges>0)/total

    health = g*100 - b*150 - p*120 - y*80 - dryness*0.15
    health = max(5,min(100,health))

    return {
        "health": health,
        "damage": 100-health,
        "pest": p,
        "yellow": y,
        "brown": b,
        "prediction": pred,
        "array": arr
    }

def detect_disease(res, dryness):
    diseases = []

    if res["brown"] > 0.15:
        diseases.append(("Fungal Infection","High","Carbendazim"))

    if res["pest"] > 0.05:
        diseases.append(("Pest Attack","Medium","Neem Oil"))

    if res["yellow"] > 0.25:
        diseases.append(("Nutrient Deficiency","Medium","NPK"))

    if dryness > 60:
        diseases.append(("Water Stress","High","Increase irrigation"))

    if not diseases:
        diseases.append(("Healthy Leaf","Low","No action needed"))

    return diseases

# ================= UI =================
st.title("🌱 AgroMind Smart Farming System")

menu = st.sidebar.radio("Menu",[
    "Analysis","History","Water Tracker","Batch Summary","Guide","Instructions"
])

dryness = st.sidebar.slider("Dryness Level",0,100,10)

# ================= ANALYSIS =================
if menu == "Analysis":

    st.subheader("📡 Live Sensor Dashboard")

    if sensor_data:
        moisture = sensor_data.get("moisture",0)
        temp = sensor_data.get("temperature",0)
        humidity = sensor_data.get("humidity",0)
        ph = sensor_data.get("ph",0)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🌱 Moisture",f"{moisture}%")
        c2.metric("🌡 Temp",f"{temp}°C")
        c3.metric("💧 Humidity",f"{humidity}%")
        c4.metric("⚗️ pH",ph)

        # ================= RESULT SECTION =================
        st.markdown("---")
        st.subheader("🧠 Smart Soil Analysis Result")

        # Water stress
        if moisture < 30:
            stress = "High"
        elif moisture < 60:
            stress = "Moderate"
        else:
            stress = "Low"

        soil_type, fertility, color, advice = get_soil_fertility(ph)

        col1,col2,col3 = st.columns(3)

        col1.metric("💧 Soil Moisture",f"{moisture}%")
        col2.metric("🌊 Water Stress",stress)
        col3.metric("🌱 Soil Fertility",fertility)

        st.markdown(f"**Soil Type:** :{color}[{soil_type}]")
        st.markdown(f"**Advice:** {advice}")

        # ===== NPK GRAPH =====
        st.subheader("📊 NPK Level Graph")

        n = sensor_data.get("nitrogen",40)
        p = sensor_data.get("phosphorus",30)
        k = sensor_data.get("potassium",50)

        df = pd.DataFrame({
            "Nutrient":["Nitrogen","Phosphorus","Potassium"],
            "Level":[n,p,k]
        })

        st.bar_chart(df.set_index("Nutrient"))

    else:
        st.warning("Waiting for live data...")

    # ================= IMAGE =================
    st.subheader("📷 Leaf Analysis")

    mode = st.radio("Select Input",["Upload Image","Use Camera"])

    img = None

    if mode == "Upload Image":
        f = st.file_uploader("Upload",type=["jpg","png","jpeg"])
        if f:
            img = Image.open(f)
    else:
        cam = st.camera_input("Capture")
        if cam:
            img = Image.open(cam)

    if img:
        st.image(img)

        res = analyze_leaf(img,dryness)

        st.subheader("🌿 Leaf Metrics")
        c1,c2,c3 = st.columns(3)
        c1.metric("Health",f"{round(res['health'],2)}%")
        c2.metric("Damage",f"{round(res['damage'],2)}%")
        c3.metric("Pest Ratio",f"{round(res['pest']*100,2)}%")

        st.subheader("🔥 Thermal View")
        st.image(cv2.applyColorMap(res["array"],cv2.COLORMAP_JET))

        st.subheader("🦠 Disease Analysis")
        for d,p,m in detect_disease(res,dryness):
            st.error(d)
            st.write("Priority:",p)
            st.write("Medicine:",m)

# ================= GUIDE =================
elif menu == "Guide":
    st.header("🌾 Crop Guide")
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

    st.subheader("❓ Ask Farming Question")
    q = st.text_input("Type your question")
    if st.button("Ask"):
        if q:
            st.success("🌿 Advice:")
            st.write("Ensure proper irrigation and nutrient balance.")
        else:
            st.warning("Enter a question")

# ================= INSTRUCTIONS =================
elif menu == "Instructions":
    st.header("📖 Farming Instructions & Tips")
    st.markdown("""
🌱 Water plants early morning or evening  
🧪 Use balanced fertilizers  
🍃 Monitor leaves regularly  
🌞 Ensure sunlight  
🧹 Remove damaged leaves  
💧 Use mulching  
🧴 Apply pesticide carefully  
""")

# ================= OTHERS =================
elif menu == "History":
    st.dataframe(pd.DataFrame(st.session_state.history))

elif menu == "Water Tracker":
    w = st.number_input("Water (ml)")
    if st.button("Save"):
        st.session_state.water_logs.append({"date":datetime.datetime.now(),"water":w})
    st.write(st.session_state.water_logs)

elif menu == "Batch Summary":
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.write("Avg Health:",df["health"].mean())
        st.write("Avg Damage:",df["damage"].mean())

# ================= REFRESH =================
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
