import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
import hashlib
from datetime import datetime
from pymongo import MongoClient
import random

# ── 1. Force Light Theme & High Contrast CSS ──────────────────────────────────
st.set_page_config(page_title="MediCap Portal", page_icon="🏥", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp { background-color: #FFFFFF !important; }
    
    h1, h2, h3, p, label, .stMarkdown, .stTextInput label, .stNumberInput label {
        color: #1A1A1A !important;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #F8F5FF !important;
        border-right: 1px solid #EBE4F7;
    }
    [data-testid="stSidebar"] * { color: #3B1C73 !important; }

    .card {
        background: #FFFFFF !important;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(94, 44, 165, 0.08);
        border: 1px solid #EBE4F7;
        color: #1A1A1A !important;
        margin-bottom: 20px;
    }

    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #3B1C73 !important;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }

    .stButton > button {
        background-color: #5E2CA5 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 30px !important;
        border: none !important;
        width: 100%;
        padding: 0.7rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #4A158C !important;
        box-shadow: 0 6px 15px rgba(94, 44, 165, 0.3);
    }

    [data-testid="stMetricValue"] {
        color: #5E2CA5 !important;
        font-weight: 800 !important;
    }
/* 1. Make the Sidebar Title Big and Bold */
    [data-testid="stSidebar"] h3 {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #3B1C73 !important;
        margin-bottom: 2rem;
        padding-left: 10px;
    }

    /* 2. Hide the ugly radio button circles completely */
    div[role="radiogroup"] div[data-testid="stRadioCircle"] {
        display: none !important;
    }

    /* 3. Style the Navigation Items (Bigger padding, rounded corners) */
    div[role="radiogroup"] > label {
        padding: 16px 20px !important; 
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        cursor: pointer;
        transition: all 0.3s ease;
        background-color: transparent;
    }

    /* 4. Make the text inside the navigation BIG and clear */
    div[role="radiogroup"] > label p {
        font-size: 1.25rem !important; /* Increased font size! */
        font-weight: 600 !important;
        color: #8C8C8C !important;
    }

    /* 5. Hover Effect for inactive buttons */
    div[role="radiogroup"] > label:hover {
        background-color: #F8F5FF !important;
    }
    div[role="radiogroup"] > label:hover p {
        color: #5E2CA5 !important;
    }

    /* 6. The ACTIVE Selected Item (Solid Purple Pill Shape!) */
    div[role="radiogroup"] > label:has(input:checked) {
        background-color: #5E2CA5 !important;
        box-shadow: 0 4px 15px rgba(94, 44, 165, 0.2) !important;
    }
    div[role="radiogroup"] > label:has(input:checked) p {
        color: #FFFFFF !important;
    }

    /* 7. Style the Logout Button to look like the subtle bottom element */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #8C8C8C !important;
        border: 1px solid #EBE4F7 !important;
        margin-top: 40px;
        font-size: 1.1rem !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #FFF0F0 !important;
        color: #D32F2F !important;
        border-color: #FFCDD2 !important;
    }           
</style>
""", unsafe_allow_html=True)

# ── 2. Database Connection (Safe Mode) ────────────────────────────────────────
@st.cache_resource
def get_db_connection():
    try:
        client = MongoClient("mongodb://localhost:27017/", 
                             serverSelectionTimeoutMS=2000,
                             connectTimeoutMS=2000)
        client.admin.command('ping') 
        return client
    except Exception:
        return None

client = get_db_connection()

if client is None:
    st.error("### 🛑 MongoDB Connection Failed")
    st.info("Please open MongoDB Compass and click 'Connect', then refresh this page.")
    st.stop()

db = client["medicap_db"]
hospitals_col = db["hospitals"]
history_col = db["predictions"]

# ── 3. Session State & Logic ──────────────────────────────────────────────────
for key, default in {
    "authenticated": False, "hospital_name": "", "hospital_id": "", "nav": "🏥 Overview"
}.items():
    if key not in st.session_state: st.session_state[key] = default

def hash_pw(password): 
    return hashlib.sha256(str.encode(password)).hexdigest()

@st.cache_resource
def load_model():
    if os.path.exists("hospital_rf_model.pkl"):
        return joblib.load("hospital_rf_model.pkl")
    return None

model = load_model()

# ── 4. Auth Screen ────────────────────────────────────────────────────────────
def auth_screen():
    st.markdown("<h1 style='text-align:center; color:#3B1C73;'>MediCap Admin Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>Healthcare Capacity Management System</p>", unsafe_allow_html=True)
    
    col = st.columns([1, 1.2, 1])[1]
    with col:
        mode = st.radio("Access Mode", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if mode == "Sign Up":
            name = st.text_input("Hospital Name", placeholder="e.g. City General")
            h_id = st.text_input("Hospital ID (CMS)", placeholder="CMSXXXXX")
            pw = st.text_input("Create Password", type="password")
            if st.button("Create Account"):
                if not name or not h_id or not pw:
                    st.warning("Please fill all fields")
                elif hospitals_col.find_one({"hospital_id": h_id}):
                    st.error("This ID is already registered.")
                else:
                    hospitals_col.insert_one({"hospital_name": name, "hospital_id": h_id, "password": hash_pw(pw)})
                    st.success("Account created! Switch to Login.")
        else:
            h_id = st.text_input("Hospital ID")
            pw = st.text_input("Password", type="password")
            if st.button("Sign In"):
                user = hospitals_col.find_one({"hospital_id": h_id, "password": hash_pw(pw)})
                if user:
                    st.session_state.authenticated = True
                    st.session_state.hospital_id = h_id
                    st.session_state.hospital_name = user["hospital_name"]
                    st.rerun()
                else:
                    st.error("Invalid Hospital ID or Password.")
        st.markdown("</div>", unsafe_allow_html=True)

# ── 5. Main Application Pages ─────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown(f"### 🏥 {st.session_state.hospital_name}")
        st.markdown("---")
        st.session_state.nav = st.radio("Navigation", ["🏥 Overview", "📈 Predictor", "📋 History"])
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

def page_overview():
    st.markdown("<div class='section-title'>Managing Capacity in a more <br><span style='color: #8C52FF;'>Effective Manner.</span></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1.2rem; color: #555; margin-bottom: 40px;'>Welcome, <b>{st.session_state.hospital_name}</b>. Your facility is securely connected to the MediCap AI network.</p>", unsafe_allow_html=True)
    
    # ── FETCH ACTUAL DATA FROM MONGODB ──
    latest_record = history_col.find_one(
        {"hospital_id": st.session_state.hospital_id},
        sort=[("timestamp", -1)]
    )

    # Use actual data if available, else placeholders
    if latest_record:
        disp_occ = latest_record.get("predicted", 0)
        disp_pct = latest_record.get("occupancy", "0%")
        status_label = "AI Forecasted"
    else:
        disp_occ = "N/A"
        disp_pct = "No Data"
        status_label = "Waiting for Input"

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Facility Capacity", "312 Beds", "Operational")
    with col2:
        st.metric("Latest Prediction", str(disp_occ), disp_pct)
    with col3:
        model_status = "Online" if model else "Offline"
        st.metric("AI Engine", model_status, "Random Forest")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if not latest_record:
        st.info("👋 New here? Go to the **Predictor** tab to generate your first capacity forecast.")

def page_predictor():
    st.markdown("<div class='section-title'>Bed Occupancy Predictor</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("Enter the last 4 weeks of census data to give the AI the historical trend needed for forecasting.")
    
    cols = st.columns(4)
    features = []
    latest_capacity = 0 
    
    for i in range(4):
        with cols[i]:
            st.markdown(f"*Week {i+1}*")
            t_beds = st.number_input("Total Beds", value=312, key=f"tb_{i}")
            o_beds = st.number_input("Occ. Beds", value=220 + (i*10), key=f"ob_{i}")
            t_icu = st.number_input("Total ICU", value=40, key=f"ticu_{i}")
            o_icu = st.number_input("Occ. ICU", value=25 + (i*2), key=f"oicu_{i}")
            features.extend([t_beds, o_beds, t_icu, o_icu])
            if i == 3: latest_capacity = t_beds

    if st.button("🔮 Generate Forecast"):
        if model:
            input_array = np.array(features).reshape(1, -1)
            pred = int(model.predict(input_array)[0]) 
            pred = max(0, min(pred, int(latest_capacity)))
            
            # ICU Logic
            week4_occ_beds = features[-3] 
            week4_occ_icu = features[-1]  
            icu_ratio = (week4_occ_icu / week4_occ_beds) if week4_occ_beds > 0 else 0.15
            predicted_icu = int(pred * icu_ratio)
            
            pct = round((pred/latest_capacity)*100, 1)
            
            # Save to MongoDB
            history_col.insert_one({
                "hospital_id": st.session_state.hospital_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "predicted": pred, 
                "occupancy": f"{pct}%"
            })
            
            st.markdown("---")
            st.success(f"### 🛏️ Predicted Total Occupied Beds: {pred}")
            st.warning(f"### 🚨 Predicted ICU Beds Needed: {predicted_icu}")
            st.info(f"Estimated General Occupancy Rate: {pct}%")
        else:
            st.error("Error: 'hospital_rf_model.pkl' not found.")
    st.markdown("</div>", unsafe_allow_html=True)

def page_history():
    st.markdown("<div class='section-title'>Submission History</div>", unsafe_allow_html=True)
    data = list(history_col.find({"hospital_id": st.session_state.hospital_id}))
    if data:
        df = pd.DataFrame(data).drop(columns=["_id", "hospital_id"])
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.table(df)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No prediction history found.")

# ── 6. App Router ─────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    auth_screen()
else:
    sidebar()
    if st.session_state.nav == "🏥 Overview": page_overview()
    elif st.session_state.nav == "📈 Predictor": page_predictor()
    elif st.session_state.nav == "📋 History": page_history()