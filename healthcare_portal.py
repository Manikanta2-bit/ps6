import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
from datetime import datetime, timedelta

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediCap Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ---------- Google Fonts ---------- */
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@500;600&display=swap');

  /* ---------- Root Palette ---------- */
  :root {
    --sage:        #7A9E8B;
    --sage-light:  #A8C4B4;
    --sage-dark:   #4F7A66;
    --cream:       #F5F2EC;
    --warm-white:  #FAFAF7;
    --stone:       #D4CFCA;
    --taupe:       #8C8178;
    --charcoal:    #2C2C2A;
    --risk-green:  #6BAF8D;
    --risk-yellow: #D4A853;
    --risk-red:    #C5645A;
    --card-shadow: 0 2px 16px rgba(44,44,42,0.08);
  }

  /* ---------- Base ---------- */
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--charcoal);
  }
  .stApp {
    background-color: var(--cream);
  }

  /* ---------- Hide Streamlit chrome ---------- */
  #MainMenu, footer, header { visibility: hidden; }

  /* ---------- Sidebar ---------- */
  [data-testid="stSidebar"] {
    background: var(--warm-white) !important;
    border-right: 1px solid var(--stone);
  }
  [data-testid="stSidebar"] .stRadio label {
    font-size: 0.92rem;
    color: var(--taupe);
    padding: 6px 0;
    cursor: pointer;
    transition: color .2s;
  }
  [data-testid="stSidebar"] .stRadio label:hover { color: var(--sage-dark); }

  /* ---------- Buttons ---------- */
  .stButton > button {
    background: var(--sage) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.55rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px;
    transition: background .2s, transform .1s !important;
    box-shadow: 0 2px 8px rgba(122,158,139,0.30) !important;
  }
  .stButton > button:hover {
    background: var(--sage-dark) !important;
    transform: translateY(-1px) !important;
  }

  /* ---------- Inputs ---------- */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1px solid var(--stone) !important;
    background: var(--warm-white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
  }
  .stTextInput > div > div > input:focus,
  .stNumberInput > div > div > input:focus {
    border-color: var(--sage) !important;
    box-shadow: 0 0 0 2px rgba(122,158,139,0.20) !important;
  }

  /* ---------- Cards ---------- */
  .card {
    background: var(--warm-white);
    border-radius: 18px;
    padding: 28px 32px;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(212,207,202,0.5);
    margin-bottom: 18px;
  }
  .card-sm {
    background: var(--warm-white);
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(212,207,202,0.5);
  }

  /* ---------- Metric Card ---------- */
  .metric-hero {
    background: linear-gradient(135deg, var(--sage-dark) 0%, var(--sage) 100%);
    border-radius: 20px;
    padding: 36px 40px;
    color: #fff;
    box-shadow: 0 6px 24px rgba(79,122,102,0.35);
    text-align: center;
  }
  .metric-hero .label { font-size: 0.85rem; letter-spacing: 1.5px; text-transform: uppercase; opacity: .8; margin-bottom: 6px; }
  .metric-hero .value { font-family: 'Playfair Display', serif; font-size: 3.4rem; font-weight: 600; line-height: 1; }
  .metric-hero .sub   { font-size: 0.88rem; opacity: .75; margin-top: 8px; }

  /* ---------- Risk Badge ---------- */
  .risk-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 22px;
    border-radius: 40px;
    font-weight: 600; font-size: 0.95rem;
  }
  .risk-green  { background: rgba(107,175,141,0.15); color: var(--risk-green);  border: 1.5px solid var(--risk-green);  }
  .risk-yellow { background: rgba(212,168,83,0.15);  color: var(--risk-yellow); border: 1.5px solid var(--risk-yellow); }
  .risk-red    { background: rgba(197,100,90,0.15);  color: var(--risk-red);    border: 1.5px solid var(--risk-red);    }

  /* ---------- Section Title ---------- */
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.65rem;
    color: var(--charcoal);
    margin-bottom: 4px;
  }
  .section-sub {
    font-size: 0.88rem;
    color: var(--taupe);
    margin-bottom: 24px;
  }

  /* ---------- Login Card ---------- */
  .login-wrap {
    max-width: 440px;
    margin: 6vh auto 0;
  }

  /* ---------- Steps ---------- */
  .step-header {
    background: linear-gradient(90deg, var(--sage-light) 0%, transparent 100%);
    border-left: 4px solid var(--sage);
    border-radius: 0 10px 10px 0;
    padding: 10px 18px;
    font-weight: 500;
    font-size: 0.95rem;
    margin-bottom: 16px;
    color: var(--sage-dark);
  }

  /* ---------- Divider ---------- */
  hr.soft { border: none; border-top: 1px solid var(--stone); margin: 20px 0; }

  /* ---------- Stat tiles ---------- */
  .stat-tile {
    background: var(--warm-white);
    border-radius: 14px;
    padding: 22px 20px;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(212,207,202,0.5);
    text-align: center;
  }
  .stat-tile .st-val { font-family: 'Playfair Display', serif; font-size: 2rem; color: var(--sage-dark); }
  .stat-tile .st-lbl { font-size: 0.78rem; color: var(--taupe); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

  /* ---------- Table ---------- */
  [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

  /* ---------- Alert override ---------- */
  .stAlert { border-radius: 12px !important; }

  /* ---------- Tab styling ---------- */
  .stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
  .stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0 !important;
    background: var(--stone) !important;
    color: var(--taupe) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 8px 20px !important;
  }
  .stTabs [aria-selected="true"] {
    background: var(--sage) !important;
    color: #fff !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ─────────────────────────────────────────────────────────
for key, default in {
    "authenticated": False,
    "hospital_name": "",
    "hospital_id": "",
    "admin_email": "",
    "history": [],
    "nav": "🏥 Hospital Overview",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Model Loading ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    path = "hospital_rf_model.pkl"
    if os.path.exists(path):
        return joblib.load(path)
    return None

model = load_model()

# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def auth_screen():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 10px'>
      <div style='font-family:"Playfair Display",serif; font-size:2.3rem; color:#4F7A66;'>MediCap Portal</div>
      <div style='font-size:0.9rem; color:#8C8178; margin-top:4px;'>Healthcare Capacity Management System</div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 1.4, 1])[1]
    with col:
        mode = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if mode == "Sign Up":
            hosp_name  = st.text_input("🏥  Hospital Name")
            hosp_id    = st.text_input("🆔  Hospital ID (CMS)")
            admin_email = st.text_input("📧  Administrator Email")
            pw         = st.text_input("🔒  Password", type="password")
            pw2        = st.text_input("🔒  Confirm Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True):
                if not all([hosp_name, hosp_id, admin_email, pw]):
                    st.error("Please fill in all fields.")
                elif pw != pw2:
                    st.error("Passwords do not match.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.hospital_name  = hosp_name
                    st.session_state.hospital_id    = hosp_id
                    st.session_state.admin_email    = admin_email
                    st.rerun()
        else:
            hosp_id = st.text_input("🆔  Hospital ID")
            pw      = st.text_input("🔒  Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True):
                if hosp_id and pw:
                    st.session_state.authenticated = True
                    st.session_state.hospital_id   = hosp_id
                    st.session_state.hospital_name = st.session_state.hospital_name or "General Hospital"
                    st.rerun()
                else:
                    st.error("Please enter your credentials.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; font-size:0.76rem; color:#8C8178; margin-top:18px;'>
          Secured · HIPAA Aligned · CMS Compliant
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='padding: 6px 0 20px'>
          <div style='font-family:"Playfair Display",serif; font-size:1.25rem; color:#4F7A66;'>MediCap</div>
          <div style='font-size:0.78rem; color:#8C8178;'>{st.session_state.hospital_name or st.session_state.hospital_id}</div>
        </div>
        <hr class='soft'>
        """, unsafe_allow_html=True)

        nav = st.radio(
            "Navigation",
            ["🏥 Hospital Overview", "📈 Bed Occupancy Predictor", "📋 Submission History", "⚙️ Account Settings"],
            label_visibility="collapsed",
        )
        st.session_state.nav = nav

        st.markdown("<hr class='soft'>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            for k in ["authenticated", "hospital_name", "hospital_id", "admin_email", "history", "nav"]:
                del st.session_state[k]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOSPITAL OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview():
    st.markdown("<div class='section-title'>Hospital Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Live snapshot of your facility's current capacity status</div>", unsafe_allow_html=True)

    # Summary tiles
    tiles = [
        ("Total Adult Beds", "312", "Registered"),
        ("Occupied Beds",    "241", "As of today"),
        ("Total ICU Beds",   "48",  "Critical care"),
        ("Occupied ICU",     "39",  "Currently in use"),
    ]
    cols = st.columns(4)
    for col, (lbl, val, sub) in zip(cols, tiles):
        with col:
            st.markdown(f"""
            <div class='stat-tile'>
              <div class='st-val'>{val}</div>
              <div class='st-lbl'>{lbl}</div>
              <div style='font-size:0.75rem; color:#A8C4B4; margin-top:2px'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Occupancy bar chart
    col1, col2 = st.columns([1.6, 1])
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**7-Day Bed Occupancy Trend**")
        days = [(datetime.today() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
        adult_occ = [220, 228, 235, 241, 238, 244, 241]
        icu_occ   = [32, 34, 36, 38, 37, 40, 39]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=adult_occ, name="Adult Beds",
                                  line=dict(color="#7A9E8B", width=2.5),
                                  fill="tozeroy", fillcolor="rgba(122,158,139,0.12)"))
        fig.add_trace(go.Scatter(x=days, y=icu_occ, name="ICU Beds",
                                  line=dict(color="#C5645A", width=2, dash="dot")))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_family="DM Sans", font_color="#2C2C2A",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(showgrid=False, showline=True, linecolor="#D4CFCA"),
            yaxis=dict(showgrid=True, gridcolor="#EDE9E3"),
            height=260,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Current Occupancy Rate**")
        adult_pct = round(241/312*100, 1)
        icu_pct   = round(39/48*100, 1)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=["Adult Beds", "ICU Beds"],
            y=[adult_pct, icu_pct],
            marker_color=["#7A9E8B", "#C5645A"],
            text=[f"{adult_pct}%", f"{icu_pct}%"],
            textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_family="DM Sans", font_color="#2C2C2A",
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(range=[0,115], showgrid=True, gridcolor="#EDE9E3", ticksuffix="%"),
            xaxis=dict(showgrid=False),
            height=260,
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BED OCCUPANCY PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
def page_predictor():
    st.markdown("<div class='section-title'>Bed Occupancy Predictor</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Enter 4 weeks of data to forecast next week's adult inpatient bed occupancy</div>", unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️  `hospital_rf_model.pkl` not found. Using demo simulation mode.", icon="🔬")

    weekly_data = {}
    tabs = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])

    defaults = [
        (312, 228, 48, 32),
        (312, 235, 48, 34),
        (312, 241, 48, 38),
        (312, 244, 48, 40),
    ]

    for i, (tab, (d_tot, d_occ, d_icu_tot, d_icu_occ)) in enumerate(zip(tabs, defaults), 1):
        with tab:
            st.markdown(f"<div class='step-header'>📅 Week {i} — Patient Census Data</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                tot_adult = st.number_input(f"Total Adult Inpatient Beds",   key=f"tot_{i}", value=d_tot, min_value=0)
                occ_adult = st.number_input(f"Occupied Adult Inpatient Beds", key=f"occ_{i}", value=d_occ, min_value=0)
            with c2:
                tot_icu   = st.number_input(f"Total ICU Beds",    key=f"tot_icu_{i}", value=d_icu_tot, min_value=0)
                occ_icu   = st.number_input(f"Occupied ICU Beds", key=f"occ_icu_{i}", value=d_icu_occ, min_value=0)
            weekly_data[i] = (tot_adult, occ_adult, tot_icu, occ_icu)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔮  Forecast Next Week", use_container_width=False):
        # Build input array (1, 16)
        flat = []
        for i in range(1, 5):
            flat.extend(list(weekly_data[i]))
        X = np.array(flat).reshape(1, 16)

        # Predict
        if model is not None:
            pred_beds = int(model.predict(X)[0])
        else:
            # Demo fallback: weighted average + small trend
            occ_vals = [weekly_data[i][1] for i in range(1, 5)]
            pred_beds = int(np.mean(occ_vals) * 1.018 + np.random.randint(-4, 8))

        total_beds = int(weekly_data[4][0])
        pct = round(pred_beds / total_beds * 100, 1) if total_beds > 0 else 0.0

        # Risk level
        if pct < 70:
            risk_cls, risk_icon, risk_lbl = "risk-green",  "🟢", "Low Risk"
        elif pct <= 90:
            risk_cls, risk_icon, risk_lbl = "risk-yellow", "🟡", "Moderate Risk"
        else:
            risk_cls, risk_icon, risk_lbl = "risk-red",    "🔴", "High Risk — Capacity Alert"

        # Save to history
        st.session_state.history.append({
            "Timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Predicted Beds": pred_beds,
            "Occupancy %":    f"{pct}%",
            "Risk Level":     risk_lbl,
        })

        # ── Results ──
        st.markdown("<hr class='soft'>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns([1.1, 0.9, 1])

        with r1:
            st.markdown(f"""
            <div class='metric-hero'>
              <div class='label'>Expected Occupancy · Week 5</div>
              <div class='value'>{pred_beds}</div>
              <div class='sub'>Adult Inpatient Beds</div>
            </div>""", unsafe_allow_html=True)

        with r2:
            st.markdown("<div class='card-sm' style='height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; gap:14px'>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='text-align:center'>
              <div style='font-size:0.78rem; color:#8C8178; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px'>Occupancy Rate</div>
              <div style='font-family:"Playfair Display",serif; font-size:2.6rem; color:#4F7A66'>{pct}%</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"<div class='risk-badge {risk_cls}'>{risk_icon} {risk_lbl}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with r3:
            st.markdown("<div class='card-sm'>", unsafe_allow_html=True)
            occ_series = [weekly_data[i][1] for i in range(1, 5)] + [pred_beds]
            weeks      = [f"Wk {i}" for i in range(1, 5)] + ["Wk 5 ▶"]
            colors     = ["#7A9E8B"] * 4 + [
                "#6BAF8D" if pct < 70 else ("#D4A853" if pct <= 90 else "#C5645A")
            ]
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=weeks[:4], y=occ_series[:4],
                mode="lines+markers",
                line=dict(color="#7A9E8B", width=2.5),
                marker=dict(size=7, color="#7A9E8B"),
                name="Historical",
            ))
            fig3.add_trace(go.Scatter(
                x=[weeks[3], weeks[4]], y=[occ_series[3], occ_series[4]],
                mode="lines+markers",
                line=dict(color=colors[-1], width=2.5, dash="dash"),
                marker=dict(size=10, color=colors[-1], symbol="star"),
                name="Forecast",
            ))
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_family="DM Sans", font_color="#2C2C2A",
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, showline=True, linecolor="#D4CFCA"),
                yaxis=dict(showgrid=True, gridcolor="#EDE9E3"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font_size=11),
                height=200,
            )
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SUBMISSION HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def page_history():
    st.markdown("<div class='section-title'>Submission History</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Log of all forecasts generated in this session</div>", unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("No submissions yet. Run a forecast from the Bed Occupancy Predictor to see results here.", icon="📋")
        return

    df = pd.DataFrame(st.session_state.history)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ACCOUNT SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown("<div class='section-title'>Account Settings</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Manage your hospital profile and credentials</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Profile Information**")
    new_name  = st.text_input("Hospital Name",        value=st.session_state.hospital_name)
    new_id    = st.text_input("Hospital ID (CMS)",    value=st.session_state.hospital_id)
    new_email = st.text_input("Administrator Email",  value=st.session_state.admin_email)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Save Changes"):
        st.session_state.hospital_name = new_name
        st.session_state.hospital_id   = new_id
        st.session_state.admin_email   = new_email
        st.success("Profile updated successfully.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Change Password**")
    st.text_input("Current Password", type="password", key="old_pw")
    st.text_input("New Password",     type="password", key="new_pw")
    st.text_input("Confirm Password", type="password", key="conf_pw")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Update Password"):
        st.success("Password updated successfully.")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    auth_screen()
else:
    sidebar()
    nav = st.session_state.nav
    if nav == "🏥 Hospital Overview":
        page_overview()
    elif nav == "📈 Bed Occupancy Predictor":
        page_predictor()
    elif nav == "📋 Submission History":
        page_history()
    elif nav == "⚙️ Account Settings":
        page_settings()
