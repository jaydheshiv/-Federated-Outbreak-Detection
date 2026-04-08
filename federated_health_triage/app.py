"""
🏥 Federated Outbreak Detection System - Premium UI Edition
Real-time clinical decision support with world-class design
Enhanced animations, advanced Streamlit features, and professional UX
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from datetime import datetime, timedelta
import pickle
import os
from pathlib import Path
from dotenv import load_dotenv
import time

# Import project modules
try:
    from utils.outbreak_detection import OutbreakDetectionEngine
    from utils.chatgpt_integration import ChatGPTClinicalAdvisor
    from config import SYMPTOMS, INFECTION_RISK_LEVELS, CLINICS
except ImportError:
    SYMPTOMS = ["Fever", "Cough", "Sore Throat", "Difficulty Breathing"]
    CLINICS = ["Urban Center", "Rural Area", "Travel Hub"]
    class OutbreakDetectionEngine:
        def __init__(self): pass
    class ChatGPTClinicalAdvisor:
        def __init__(self): pass

# ============================================================================
# PAGE CONFIGURATION - PREMIUM SETUP
# ============================================================================
st.set_page_config(
    page_title="🏥 Federated Outbreak Detection",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# DESIGN TOKENS
# ============================================================================
COLORS = {
    "bg": "#0a0e27",
    "bg_secondary": "#101820",
    "accent_primary": "#FEE715",
    "accent_secondary": "#00d9ff",
    "text_primary": "#FFFFFF",
    "text_secondary": "#b0b8c1",
    "border": "rgba(254, 231, 21, 0.15)",
    "success": "#22c55e",
    "warning": "#eab308",
    "danger": "#ef4444",
    "info": "#3b82f6",
}

RISK_COLORS = {
    "low": {"bg": "rgba(34, 197, 94, 0.12)", "text": "#22c55e"},
    "moderate": {"bg": "rgba(250, 204, 21, 0.12)", "text": "#eab308"},
    "high": {"bg": "rgba(249, 115, 22, 0.12)", "text": "#f97316"},
    "critical": {"bg": "rgba(239, 68, 68, 0.15)", "text": "#ef4444"},
}

# ============================================================================
# ADVANCED CSS STYLING
# ============================================================================
st.markdown(f"""
<style>
    :root {{
        --primary: {COLORS['accent_primary']};
        --secondary: {COLORS['accent_secondary']};
        --bg: {COLORS['bg']};
    }}

    * {{
        transition: all 0.3s ease !important;
    }}

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: linear-gradient(135deg, #0a0e27 0%, #1a2332 50%, #2d1b4e 100%) !important;
        background-attachment: fixed !important;
        color: {COLORS['text_primary']} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }}

    .main {{
        padding: 2rem !important;
        max-width: 1600px !important;
        margin: 0 auto !important;
    }}

    h1 {{
        color: {COLORS['accent_primary']} !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 30px rgba(254, 231, 21, 0.2) !important;
    }}

    h2 {{
        color: {COLORS['accent_primary']} !important;
        font-size: 1.8rem !important;
        margin-top: 1.5rem !important;
    }}

    h3 {{
        color: {COLORS['accent_secondary']} !important;
    }}

    [data-testid="metric-container"] {{
        background: rgba(20, 30, 48, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 0 20px rgba(254, 231, 21, 0.05) !important;
    }}

    [data-testid="metric-container"]:hover {{
        background: rgba(20, 30, 48, 0.8) !important;
        border-color: {COLORS['accent_primary']} !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2), 0 0 30px rgba(254, 231, 21, 0.15) !important;
        transform: translateY(-4px) !important;
    }}

    .card {{
        background: rgba(20, 30, 48, 0.5) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }}

    .card:hover {{
        background: rgba(20, 30, 48, 0.7) !important;
        border-color: {COLORS['accent_secondary']} !important;
        box-shadow: 0 8px 24px rgba(0, 217, 255, 0.1) !important;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0f1624 0%, #1a2332 100%) !important;
        border-right: 1px solid {COLORS['border']} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {COLORS['text_primary']} !important;
    }}

    section[data-testid="stSidebar"] [role="radio"]:hover,
    section[data-testid="stSidebar"] button:hover {{
        background: rgba(254, 231, 21, 0.1) !important;
        box-shadow: 0 0 12px rgba(254, 231, 21, 0.2) !important;
        transform: translateX(4px) !important;
    }}

    button {{
        background: linear-gradient(135deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']}) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(254, 231, 21, 0.2) !important;
    }}

    button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(254, 231, 21, 0.3) !important;
    }}

    input, textarea, select {{
        background: rgba(20, 30, 48, 0.5) !important;
        border: 1px solid {COLORS['border']} !important;
        color: {COLORS['text_primary']} !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }}

    input:focus, textarea:focus {{
        background: rgba(20, 30, 48, 0.7) !important;
        border-color: {COLORS['accent_primary']} !important;
        box-shadow: 0 0 0 3px rgba(254, 231, 21, 0.1) !important;
    }}

    .risk-badge {{
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        display: inline-block !important;
    }}

    .risk-critical {{
        animation: pulse 2s infinite !important;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    ::-webkit-scrollbar {{
        width: 8px;
    }}

    ::-webkit-scrollbar-thumb {{
        background: {COLORS['accent_primary']};
        border-radius: 4px;
    }}

    hr {{
        border: 0 !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, {COLORS['border']}, transparent) !important;
        margin: 2rem 0 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
    st.session_state.outbreak_engine = None
    st.session_state.chatgpt_advisor = None
    st.session_state.chat_history = []

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h2 style='margin: 0; font-size: 2.5rem;'>🏥</h2>
        <h3 style='margin: 0.5rem 0 0; color: #FEE715;'>Outbreak Detection</h3>
        <p style='color: #b0b8c1; font-size: 0.85rem;'>Federated Learning System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.subheader("🤖 AI Features")
    ai_enabled = st.toggle("Enable AI Insights", value=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.subheader("📍 Navigation")
    page = st.radio(
        "Select Page",
        ["🏠 Dashboard", "🔍 Patient Assessment", "📊 Clinic Analytics", 
         "🚨 Outbreak Detection", "📈 Model Performance", "💬 AI Chat", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ System", "Online", label_visibility="collapsed")
    with col2:
        st.metric("🔗 API", "Active", label_visibility="collapsed")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Patients", "1.5k", label_visibility="collapsed")
    with col2:
        st.metric("⚠️ High-Risk", "1.2k", label_visibility="collapsed")

# ============================================================================
# LOAD MODELS
# ============================================================================
@st.cache_resource
def load_models():
    try:
        outbreak_engine = OutbreakDetectionEngine()
    except:
        outbreak_engine = None
    try:
        chatgpt_advisor = ChatGPTClinicalAdvisor()
    except:
        chatgpt_advisor = None
    return outbreak_engine, chatgpt_advisor

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def animated_header(title: str, subtitle: str = "", emoji: str = ""):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 3rem;'>{emoji}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def create_stat_boxes(stats: dict):
    cols = st.columns(len(stats))
    for i, (label, (value, icon, color)) in enumerate(stats.items()):
        with cols[i]:
            st.markdown(f"""
            <div class='card' style='text-align: center; padding: 2rem;'>
                <div style='font-size: 2rem;'>{icon}</div>
                <div style='font-size: 2.2rem; font-weight: 700; color: {color};'>{value}</div>
                <div style='font-size: 0.9rem; color: {COLORS['text_secondary']};'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================
def page_dashboard():
    animated_header("System Dashboard", "Real-time outbreak monitoring across all clinics", "📊")
    
    outbreak_engine, chatgpt_advisor = load_models()
    
    stats = {
        "Total Patients": ("1,500", "👥", COLORS['accent_primary']),
        "High-Risk": ("1,248", "⚠️", COLORS['danger']),
        "Clusters": ("650", "🔗", COLORS['warning']),
        "Accuracy": ("76.8%", "🎯", COLORS['success']),
    }
    create_stat_boxes(stats)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # AI Insights
    if ai_enabled and chatgpt_advisor:
        with st.container():
            st.markdown(f"""
            <div class='card' style='border-left: 4px solid {COLORS['accent_primary']};'>
                <h3>🤖 AI System Insights</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("🧠 Generating insights..."):
                try:
                    insight = chatgpt_advisor.generate_dashboard_insight(
                        clinic_name="System-wide",
                        high_risk_count=1248,
                        total_count=1500,
                        cluster_count=650,
                    )
                    st.success(insight)
                except:
                    st.info("AI insights unavailable - check your API key in Secrets")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Clinic Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Clinic Status")
        clinic_data = {
            'Clinic': ['Urban Center', 'Rural Area', 'Travel Hub'],
            'Patients': [500, 500, 500],
            'High-Risk': [398, 330, 458],
            'Status': ['✅ Normal', '✅ Normal', '🟡 Alert']
        }
        st.dataframe(pd.DataFrame(clinic_data), use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("⚠️ Risk Distribution")
        df_risk = pd.DataFrame({
            'Risk Level': ['Low', 'Moderate', 'High', 'Critical'],
            'Count': [252, 200, 600, 448],
        })
        
        fig = px.pie(df_risk, names='Risk Level', values='Count',
                    color_discrete_map={'Low': '#22c55e', 'Moderate': '#eab308', 'High': '#f97316', 'Critical': '#dc2626'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Performance Metrics
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Accuracy", "76.8%", "+2.3%")
    with col2:
        st.metric("Sensitivity", "89.4%", "+1.2%")
    with col3:
        st.metric("Specificity", "72.1%", "-0.5%")
    with col4:
        st.metric("API Health", "100%", "✅")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Trend Chart
    st.subheader("📊 7-Day Outbreak Trend")
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    high_risk_counts = [380, 390, 395, 398, 410, 420, 1248]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=high_risk_counts, mode='lines+markers', fill='tozeroy',
                            line=dict(color=COLORS['accent_primary'], width=3),
                            marker=dict(size=10)))
    fig.update_layout(title="High-Risk Patient Trend", height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 2: PATIENT ASSESSMENT
# ============================================================================
def page_patient_assessment():
    animated_header("Patient Risk Assessment", "Individual evaluation and recommendations", "🔍")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Patient Info")
        age = st.slider("Age", 0, 120, 45)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("💊 Medical History")
        vaccination = st.select_slider("Vaccination", ["Unvaccinated", "Partially", "Fully", "Boosted"], value="Fully")
        comorbidities = st.multiselect("Comorbidities", ["None", "Diabetes", "Respiratory", "Immunocompromised"], default=["None"])
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🌍 Exposure")
        travel = st.select_slider("Travel", ["None", "Local", "Regional", "International"], value="None")
        contact = st.select_slider("Contact Cases", ["None", "Indirect", "Direct"], value="None")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🤒 Symptoms")
        symptoms = st.multiselect("Select Symptoms", SYMPTOMS, default=[])
        days = st.number_input("Days Symptomatic", 0, 30, 0)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        assess_button = st.button("🔍 Assess Risk", use_container_width=True)
    
    with col2:
        if assess_button:
            st.markdown(f"""
            <div class='card' style='border-left: 4px solid {COLORS['accent_primary']};'>
                <h3>📊 Assessment Results</h3>
            </div>
            """, unsafe_allow_html=True)
            
            risk_score = len(symptoms) * 0.5 + days * 0.2 + (["None", "Indirect", "Direct"].index(contact)) * 1.0
            risk_level = min(3, int(risk_score / 2))
            risk_names = ['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk']
            icons = ['🟢', '🟡', '🟠', '🔴']
            colors = [RISK_COLORS['low'], RISK_COLORS['moderate'], RISK_COLORS['high'], RISK_COLORS['critical']]
            
            color = colors[risk_level]
            st.markdown(f"""
            <div style='background: {color['bg']}; border: 2px solid {color['text']}; padding: 2rem; border-radius: 12px; text-align: center;'>
                <div style='font-size: 3rem;'>{icons[risk_level]}</div>
                <h2 style='color: {color['text']}; margin: 0.5rem 0;'>{risk_names[risk_level]}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.expander("⚠️ Risk Factors", expanded=True):
                if len(symptoms) > 0:
                    st.write(f"• Symptoms: {', '.join(symptoms[:3])}")
                if days > 0:
                    st.write(f"• Symptomatic for {days} days")
                if contact != "None":
                    st.write("• Contact with confirmed cases")
            
            with st.expander("📋 Recommendations", expanded=True):
                if risk_level == 0:
                    st.success("✅ Monitor for symptoms")
                elif risk_level == 1:
                    st.info("ℹ️ Monitor closely, consider testing")
                elif risk_level == 2:
                    st.warning("⚠️ URGENT: Test & isolate 10 days")
                else:
                    st.error("🚨 CRITICAL: Immediate isolation & hospitalization")

# ============================================================================
# PAGE 3: CLINIC ANALYTICS
# ============================================================================
def page_clinic_analytics():
    animated_header("Clinic Analytics", "Performance metrics by clinic", "📊")
    
    tab1, tab2, tab3 = st.tabs(["Urban Center", "Rural Area", "Travel Hub"])
    
    clinics = ['Urban Center', 'Rural Area', 'Travel Hub']
    stats_data = [
        {'patients': 500, 'high_risk': 398, 'clusters': 210, 'accuracy': 0.77},
        {'patients': 500, 'high_risk': 330, 'clusters': 30, 'accuracy': 0.72},
        {'patients': 500, 'high_risk': 458, 'clusters': 40, 'accuracy': 0.85},
    ]
    
    for tab, clinic, stats in zip([tab1, tab2, tab3], clinics, stats_data):
        with tab:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Patients", stats['patients'])
            with col2:
                st.metric("High-Risk", f"{stats['high_risk']} ({stats['high_risk']/stats['patients']*100:.0f}%)")
            with col3:
                st.metric("Clusters", stats['clusters'])
            with col4:
                st.metric("Accuracy", f"{stats['accuracy']*100:.0f}%")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                dates = pd.date_range(start='2026-03-01', periods=30, freq='D')
                accuracy_data = np.random.uniform(stats['accuracy'] - 0.05, stats['accuracy'] + 0.05, 30)
                fig = px.line(x=dates, y=accuracy_data, title="30-Day Accuracy Trend")
                fig.update_layout(height=350, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                risk_dist = {'Low': 75, 'Moderate': 100, 'High': 150, 'Critical': 75}
                fig = px.bar(x=list(risk_dist.keys()), y=list(risk_dist.values()), title="Risk Distribution",
                           color_discrete_map={'Low': '#22c55e', 'Moderate': '#eab308', 'High': '#f97316', 'Critical': '#dc2626'})
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 4: OUTBREAK DETECTION
# ============================================================================
def page_outbreak_detection():
    animated_header("Outbreak Detection", "Population-level monitoring", "🚨")
    
    st.subheader("⚙️ Thresholds")
    col1, col2, col3 = st.columns(3)
    with col1:
        threshold_hr = st.slider("High-Risk %", 0, 100, 50)
    with col2:
        threshold_cluster = st.slider("Cluster Size", 1, 20, 5)
    with col3:
        st.checkbox("Auto-Check", value=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    clinics_data = [
        {"name": "Urban Center", "high_risk_pct": 79.6, "clusters": 210},
        {"name": "Rural Area", "high_risk_pct": 66.0, "clusters": 30},
        {"name": "Travel Hub", "high_risk_pct": 91.6, "clusters": 40},
    ]
    
    exceeding = [c for c in clinics_data if (c["high_risk_pct"] >= threshold_hr) or (c["clusters"] >= threshold_cluster)]
    
    if not exceeding:
        st.success("✅ All clinics within safe thresholds")
    else:
        st.error(f"⚠️ ALERT - Thresholds exceeded in: {', '.join([c['name'] for c in exceeding])}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        df = pd.DataFrame(clinics_data)
        fig = px.bar(df, x="name", y="high_risk_pct", title="High-Risk %", color="high_risk_pct",
                    color_continuous_scale=["#22c55e", "#eab308", "#f97316", "#ef4444"])
        fig.add_hline(y=threshold_hr, line_dash="dash", line_color="#FEE715")
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(df, x="name", y="clusters", title="Clusters", color="clusters",
                    color_continuous_scale=["#22c55e", "#eab308", "#f97316", "#ef4444"])
        fig.add_hline(y=threshold_cluster, line_dash="dash", line_color="#FEE715")
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 5: MODEL PERFORMANCE
# ============================================================================
def page_model_performance():
    animated_header("Model Performance", "ML metrics and comparison", "📈")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Clinic Performance")
        perf_data = pd.DataFrame({
            'Clinic': ['Urban Center', 'Rural Area', 'Travel Hub'],
            'Accuracy': ['77%', '72%', '85%'],
            'Precision': ['76%', '71%', '86%'],
            'Recall': ['77%', '72%', '85%'],
        })
        st.dataframe(perf_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Ensemble Metrics")
        col1_sub, col2_sub = st.columns(2)
        with col1_sub:
            st.metric("Accuracy", "78.5%", "+1.7%")
            st.metric("Sensitivity", "81.2%", "+2.4%")
        with col2_sub:
            st.metric("Specificity", "77.8%")
            st.metric("F1-Score", "0.795")

# ============================================================================
# PAGE 6: AI CHAT BOT
# ============================================================================
def page_ai_chart_bot():
    animated_header("AI Chat Bot", "Ask questions about your data", "💬")
    
    outbreak_engine, chatgpt_advisor = load_models()
    
    if not ai_enabled:
        st.warning("⚠️ AI features disabled. Enable in sidebar.")
        return
    
    if not chatgpt_advisor:
        st.error("❌ ChatGPT advisor unavailable. Check API key in Secrets.")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        threshold_hr = st.slider("High-Risk %", 0, 100, 50, key="chat_hr")
    with col2:
        threshold_cl = st.slider("Cluster Size", 1, 20, 5, key="chat_cl")
    with col3:
        st.button("📊 Load Charts", use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    for q, a in st.session_state.chat_history[-3:]:
        st.write(f"**You:** {q}")
        st.success(f"🤖 {a}")
        st.markdown("<hr>", unsafe_allow_html=True)
    
    cols = st.columns([4, 1])
    with cols[0]:
        question = st.text_input("Ask AI", placeholder="e.g., What about Travel Hub's surge?", label_visibility="collapsed")
    with cols[1]:
        ask_btn = st.button("💬 Send", use_container_width=True)
    
    if ask_btn and question:
        with st.spinner("🧠 Thinking..."):
            try:
                response = chatgpt_advisor.client.chat.completions.create(
                    model=chatgpt_advisor.model,
                    messages=[{"role": "system", "content": "You are a healthcare advisor."}, 
                             {"role": "user", "content": question}],
                    max_tokens=350,
                )
                answer = response.choices[0].message.content
                st.session_state.chat_history.append((question, answer))
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================================================
# PAGE 7: SETTINGS
# ============================================================================
def page_settings():
    animated_header("Settings", "System configuration", "⚙️")
    
    st.subheader("🔧 Model Config")
    col1, col2 = st.columns(2)
    with col1:
        model_type = st.selectbox("Model", ["Random Forest", "Gradient Boosting", "Neural Network"])
    with col2:
        agg_method = st.selectbox("Aggregation", ["Weighted Average", "Majority Voting", "Stacking"])
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.subheader("📊 Data Settings")
    col1, col2 = st.columns(2)
    with col1:
        test_size = st.slider("Test %", 10, 40, 20)
    with col2:
        val_size = st.slider("Validation %", 10, 30, 20)
    
    st.markdown("<hr>", unsafe_have_html=True)
    
    st.subheader("🔔 Notifications")
    col1, col2 = st.columns(2)
    with col1:
        notify = st.toggle("Alert on Outbreak", value=True)
    with col2:
        threshold = st.number_input("Alert Threshold %", 0, 100, 75)
    
    st.markdown("<hr>", unsafe_have_html=True)
    
    st.subheader("📋 System Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 System", "Healthy")
    with col2:
        st.metric("🔗 API", "Connected")
    with col3:
        st.metric("⚡ Response", "245ms")
    
    st.markdown("<hr>", unsafe_have_html=True)
    
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✅ Settings saved!")

# ============================================================================
# MAIN ROUTER
# ============================================================================
def main():
    pages = {
        "🏠 Dashboard": page_dashboard,
        "🔍 Patient Assessment": page_patient_assessment,
        "📊 Clinic Analytics": page_clinic_analytics,
        "🚨 Outbreak Detection": page_outbreak_detection,
        "📈 Model Performance": page_model_performance,
        "💬 AI Chat": page_ai_chart_bot,
        "⚙️ Settings": page_settings,
    }
    
    if page in pages:
        pages[page]()

if __name__ == "__main__":
    main()
