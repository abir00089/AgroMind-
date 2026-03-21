import streamlit as st
from PIL import Image
from database import init_db, create_account, login_user, save_scan, get_history, get_unique_trees, clear_all_data
from analysis import analyze_leaf, get_soil_logic, get_nutrient_advice

init_db()
st.set_page_config(page_title="AgroMind Ultimate", page_icon="🌱", layout="wide")

if "user" not in st.session_state: st.session_state.user = None

# --- AUTHENTICATION GATE ---
if not st.session_state.user:
    st.title("🚜 AgroMind Farmer Portal")
    mode = st.radio("Select Access Type:", ["Login", "Register New User"])
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Enter Dashboard"):
        if mode == "Register New User":
            if u and p and create_account(u, p): st.success("Account created! You can now login.")
            else: st.error("Username taken or fields empty.")
        else:
            if login_user(u, p): 
                st.session_state.user = u
                st.rerun()
            else: st.error("Access Denied: Invalid Credentials.")
    st.stop()

# --- MAIN DASHBOARD ---
st.sidebar.title(f"👤 {st.session_state.user}")

with st.expander("📖 OFFICIAL USER MANUAL", expanded=True):
    st.markdown("""
    1. **Identity**: Enter a unique **Tree/Plot ID** in the sidebar.
    2. **Input Mode**: Toggle **Camera** for live scans or **Gallery** for uploads.
    3. **Analysis**: View the **Health Score** and **Soil Status**.
    4. **Moisture**: Adjust the slider to match current soil conditions.
    5. **Save**: Click **'Save Record'** to archive the scan in the ledger.
    """)

st.title("🌱 Smart Crop Analysis & Management")

# Sidebar Controls
st.sidebar.divider()
tree_id = st.sidebar.text_input("📍 Tree/Plot ID", "Tree_01")
source = st.sidebar.radio("Image Source", ["Camera", "Gallery"])

if source == "Camera":
    file = st.sidebar.camera_input("Scan Leaf")
else:
    file = st.sidebar.file_uploader("Upload Leaf Image", type=['jpg', 'png', 'jpeg'])

# --- ANALYSIS WORKFLOW ---
if file:
    img = Image.open(file)
    st.image(img, width=350, caption="Processing Leaf Image...")
    
    score = analyze_leaf(img)
    nut, nut_adv = get_nutrient_advice(score)
    
    col1, col2 = st.columns(2)
    col1.metric("Plant Health", f"{score}%")
    col1.info(f"📋 **Nutrient Guide:** {nut_adv}")
    
    moisture = st.slider("💧 Set Soil Moisture (%)", 0, 100, 45)
    status, alert = get_soil_logic(moisture)
    col2.metric("Soil Status", status)
    
    if "🔴" in status: st.error(alert)
    elif "🔵" in status: st.warning(alert)
    else: st.success(alert)

    if st.button(f"💾 Save Record for {tree_id}"):
        save_scan(tree_id, score, moisture, status)
        st.toast("Record successfully archived!")
        st.rerun()

st.divider()

# --- HISTORY & LEDGER ---
st.subheader("📊 Farm Management Ledger")
selected = st.selectbox("Filter History:", ["All Trees"] + get_unique_trees())

df = get_history(selected)
if not df.empty:
    st.line_chart(df.set_index('date')[['health_score', 'moisture']])
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Download Report (CSV)", df.to_csv(index=False), f"AgroMind_Report.csv")
else:
    st.info("No records found. Perform a scan and save it to see trends.")

# --- ADMIN CONTROLS ---
st.sidebar.divider()
st.sidebar.subheader("⚠️ Management")
if st.sidebar.button("🗑️ Clear All Scan Data"):
    clear_all_data()
    st.sidebar.success("Database Wiped!")
    st.rerun()

if st.sidebar.button("🔓 Logout"):
    st.session_state.user = None
    st.rerun()