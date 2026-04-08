"""
Enhanced Streamlit App with ChatGPT AI Features
Adds intelligent insights, clinical analysis, and automated recommendations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit.components.v1 as components

# Load environment variables from .env file
load_dotenv()

# Import project modules
from utils.outbreak_detection import OutbreakDetectionEngine
from utils.chatgpt_integration import ChatGPTClinicalAdvisor
from config import SYMPTOMS, INFECTION_RISK_LEVELS, CLINICS

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="AI Outbreak Detection System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lightweight parallax (mouse-based) for layered UI.
# NOTE: Streamlit components render inside an iframe; update CSS variables on the
# parent document so main-page CSS can read them.
components.html(
        """
<script>
(() => {
    const getRoot = () => {
        try {
            return window.parent?.document?.documentElement || document.documentElement;
        } catch (e) {
            return document.documentElement;
        }
    };

    const root = getRoot();
    let raf = null;
    let mx = 0, my = 0;

    const update = () => {
        raf = null;
        root.style.setProperty('--mx', String(mx));
        root.style.setProperty('--my', String(my));
    };

    const bindWindow = () => {
        try {
            return window.parent || window;
        } catch (e) {
            return window;
        }
    };

    const w = bindWindow();
    w.addEventListener('mousemove', (e) => {
        const vw = w.innerWidth || window.innerWidth;
        const vh = w.innerHeight || window.innerHeight;
        const cx = vw / 2;
        const cy = vh / 2;

        // Range roughly -14..14 (more visible)
        mx = Math.max(-14, Math.min(14, (e.clientX - cx) / 50));
        my = Math.max(-14, Math.min(14, (e.clientY - cy) / 50));
        if (!raf) raf = requestAnimationFrame(update);
    }, { passive: true });
})();
</script>
""",
        height=0,
)

# Custom CSS
st.markdown("""
<style>
    :root {
        /* Theme palette (matches .streamlit/config.toml) */
        --bg: #101820;
        --ink: #FFFFFF;
        --muted: rgba(255, 255, 255, 0.72);
        --card: rgba(255, 255, 255, 0.06);
        --card2: rgba(255, 255, 255, 0.08);
        --border: rgba(255, 255, 255, 0.14);
        --soft: rgba(255, 255, 255, 0.06);
        --info: rgba(254, 231, 21, 0.12);
        --accent: #FEE715;
        --accent2: #101820;
        --mx: 0;
        --my: 0;
    }

    body, .stApp {
        background-color: var(--bg) !important;
        background-image: linear-gradient(135deg, #101820 0%, #2a3540 75%, #FEE715 100%) !important;
        background-attachment: fixed !important;
    }
    .stApp, .main { color: var(--ink); }
    .main { padding-top: 0rem; }

    /* Subtle texture */
    .stApp {
        background-image:
            linear-gradient(135deg, #101820 0%, #2a3540 70%, #FEE715 100%),
            radial-gradient(900px 300px at 20% 8%, rgba(254, 231, 21, 0.14) 0%, rgba(254, 231, 21, 0.00) 60%),
            radial-gradient(800px 320px at 85% 12%, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.00) 60%),
            linear-gradient(0deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
        background-size: auto, auto, auto, 56px 56px, 56px 56px;
        background-position: 0 0;
        background-attachment: fixed;
        animation: bgPan 10s ease-in-out infinite;
    }

    @keyframes bgPan {
        0% { background-position: 0 0, 0 0, 0 0, 0 0; }
        50% { background-position: -40px 10px, 30px -10px, 0 0, 0 0; }
        100% { background-position: 0 0, 0 0, 0 0, 0 0; }
    }

    /* Scrapbook hero */
    .hero-wrap {
        position: relative;
        padding: 26px 22px;
        margin: 8px 0 18px 0;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 100%), var(--card);
        overflow: hidden;
    }
    .hero-title {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.05;
    }
    .hero-sub {
        margin-top: 8px;
        color: var(--muted);
        font-size: 14px;
    }

    /* Layered papers */
    .paper-stack {
        position: absolute;
        right: 14px;
        top: 14px;
        width: 320px;
        height: 150px;
        pointer-events: none;
        will-change: transform;
        transform: translate3d(calc(var(--mx) * 0.6px), calc(var(--my) * 0.6px), 0);
    }
    .paper {
        position: absolute;
        inset: 0;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: var(--card2);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.32);
        transform-origin: 30% 70%;
        will-change: transform;
    }
    .paper.p1 { transform: rotate(-3deg) translate(-6px, 4px); opacity: 0.95; }
    .paper.p2 { transform: rotate(2deg) translate(8px, 10px); opacity: 0.92; }
    .paper.p3 { transform: rotate(-1deg) translate(0px, 0px); }
    .paper .paper-inner {
        padding: 14px 14px 12px 14px;
        font-size: 12px;
        color: var(--muted);
        line-height: 1.35;
    }
    .paper .chip {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 999px;
        background: rgba(254, 231, 21, 0.14);
        border: 1px solid rgba(254, 231, 21, 0.35);
        color: var(--ink);
        font-weight: 700;
        font-size: 11px;
        margin-bottom: 8px;
    }

    /* (Sticker removed per UX request) */

    .paper.p1 { animation: paperDrift1 6.2s ease-in-out infinite; }
    .paper.p2 { animation: paperDrift2 5.6s ease-in-out infinite; }
    .paper.p3 { animation: paperDrift3 7.4s ease-in-out infinite; }
    @keyframes paperDrift1 { 0%,100% { transform: rotate(-4deg) translate(-10px, 6px); } 50% { transform: rotate(-2deg) translate(-4px, 2px);} }
    @keyframes paperDrift2 { 0%,100% { transform: rotate(3deg) translate(12px, 14px); } 50% { transform: rotate(1deg) translate(7px, 9px);} }
    @keyframes paperDrift3 { 0%,100% { transform: rotate(-1deg) translate(0px, 0px); } 50% { transform: rotate(1deg) translate(3px, -3px);} }

    /* Respect reduced motion */
    @media (prefers-reduced-motion: reduce) {
        .paper.p1, .paper.p2, .paper.p3 { animation: none !important; }
        .stApp { animation: none !important; }
    }

    /* Existing cards */
    .metric-card { background-color: rgba(255,255,255,0.06); padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid var(--border); }
    .ai-insight {
        background-color: rgba(254, 231, 21, 0.15);
        border-left: 4px solid var(--accent);
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        border: 1px solid rgba(254, 231, 21, 0.35);
        transition: transform 180ms ease, box-shadow 180ms ease;
    }
    .ai-insight,
    .ai-insight * {
        color: #000000 !important;
    }
    .ai-insight:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.35);
    }

    /* Sidebar - White text with animations */
    section[data-testid="stSidebar"] {
        background: var(--bg) !important;
        display: block !important;
        visibility: visible !important;
        width: 300px !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] a {
        color: #FFFFFF !important;
        display: block !important;
        visibility: visible !important;
        transition: all 300ms ease !important;
    }

    /* Sidebar radio buttons & items hover animation */
    section[data-testid="stSidebar"] [role="radio"],
    section[data-testid="stSidebar"] [role="option"],
    section[data-testid="stSidebar"] button {
        transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Sidebar radio hover glow */
    section[data-testid="stSidebar"] [role="radio"]:hover,
    section[data-testid="stSidebar"] button:hover {
        background: rgba(254, 231, 21, 0.12) !important;
        box-shadow: 0 0 12px rgba(254, 231, 21, 0.25) !important;
        transform: translateX(4px) !important;
    }

    /* Sidebar toggle switch animation */
    section[data-testid="stSidebar"] [role="switch"] {
        transition: all 300ms ease !important;
    }
    section[data-testid="stSidebar"] [role="switch"]:hover {
        filter: brightness(1.15) !important;
    }

    .risk-low { background: rgba(34, 197, 94, 0.18); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.40); }
    .risk-moderate { background: rgba(250, 204, 21, 0.18); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.35); }
    .risk-high { background: rgba(249, 115, 22, 0.18); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.35); }
    .risk-critical { background: rgba(239, 68, 68, 0.22); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.40); font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
    st.session_state.outbreak_engine = None
    st.session_state.chatgpt_advisor = None

# ============================================================================
# SIDEBAR - NAVIGATION & AI SETTINGS
# ============================================================================
st.sidebar.title("🤖 AI Outbreak Detection")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Dashboard", "🔍 Patient Assessment", "📊 Clinic Analytics", 
     "🚨 Outbreak Detection", "📈 Model Performance", "💬 AI Assistant", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Features")
ai_enabled = st.sidebar.toggle("Enable ChatGPT Features", value=True)
ai_detail_level = st.sidebar.select_slider(
    "AI Analysis Depth",
    options=["Brief", "Normal", "Detailed"],
    value="Normal"
)

st.sidebar.markdown("---")
st.sidebar.subheader("System Information")
st.sidebar.info("""
**Federated Learning + AI System**
- 3 Independent Clinics
- Privacy-Preserving Aggregation
- Real-time Risk Assessment
- 🤖 ChatGPT Clinical Insights
- AI-powered Recommendations
""")

# ============================================================================
# LOAD MODELS
# ============================================================================
@st.cache_resource
def load_models():
    """Load pre-trained clinic models and AI engines"""
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
# AI INSIGHT GENERATOR
# ============================================================================
@st.cache_data(ttl=3600)
def generate_dashboard_insights(chatgpt_advisor):
    """Generate AI insights for dashboard"""
    if not chatgpt_advisor or not ai_enabled:
        return None
    
    try:
        prompt = """
        Analyze this outbreak detection system performance:
        - Total patients: 1500
        - High-risk cases: 1248 (83.2%)
        - Outbreak clusters: 650
        
        Provide 2-3 key clinical insights about the current situation in 2 sentences.
        """
        
        response = chatgpt_advisor.generate_outbreak_report(
            clinic_name="System-wide",
            high_risk_count=1248,
            total_count=1500,
            cluster_count=650
        )
        return response
    except:
        return None

# ============================================================================
# PAGE 1: DASHBOARD WITH AI INSIGHTS
# ============================================================================
def page_dashboard():
    st.markdown(
        """
                <div class="hero-wrap">
                    <div class="paper-stack" aria-hidden="true">
                        <div class="paper p1"></div>
                        <div class="paper p2"></div>
                        <div class="paper p3">
                            <div class="paper-inner">
                                <div class="chip">Live snapshot</div>
                                <div><b>3 clinics</b> · <b>1,500</b> monitored</div>
                                <div>High-risk focus · Cluster signals</div>
                            </div>
                        </div>
                    </div>
                    <h1 class="hero-title">🤖 AI‑Powered Outbreak Detection Dashboard</h1>
                                            <div class="hero-sub">Scrapbook‑layered insights (animated) · Yellow/Black theme</div>
                </div>
                """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Patients", "1,500", "+15% this week")
    with col2:
        st.metric("High-Risk Cases", "1,248", "+8% this week")
    with col3:
        st.metric("Outbreak Clusters", "650", "+12% this week")
    
    st.markdown("---")
    
    # AI System Insights
    if ai_enabled:
        outbreak_engine, chatgpt_advisor = load_models()
        with st.spinner("🤖 Generating AI insights..."):
            try:
                st.markdown("### 🤖 AI System Insights")
                
                insight_prompt = f"""
                Analyze this epidemiological data:
                - 1500 total patients monitored
                - 1248 classified as high-risk
                - 650 outbreak clusters detected across 3 clinics
                - Model accuracy: 76.8%
                
                Provide 3 actionable clinical insights (each 1-2 sentences):
                1. Current threat level assessment
                2. Key population at risk
                3. Recommended intervention strategy
                """
                
                if chatgpt_advisor:
                    response = chatgpt_advisor.client.chat.completions.create(
                        model=os.getenv("CHATGPT_MODEL", "llama-3.3-70b-versatile"),
                        messages=[
                            {"role": "system", "content": "You are an epidemiologist analyzing disease outbreak patterns."},
                            {"role": "user", "content": insight_prompt},
                        ],
                        max_tokens=300,
                        temperature=0.7,
                    )

                    insights = response.choices[0].message.content
                    st.markdown(
                        f"""
                    <div class="ai-insight">
                    <b>🤖 AI Analysis:</b><br>
                    {insights}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                st.info("💡 AI insights unavailable - proceeding with standard analysis")
    
    st.markdown("---")
    
    # Clinic Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Clinic Status")
        clinic_data = {
            'Clinic': ['Urban Center', 'Rural Area', 'Travel Hub'],
            'Patients': [500, 500, 500],
            'High-Risk': [398, 330, 458],
            'Clusters': [210, 30, 40]
        }
        df_clinics = pd.DataFrame(clinic_data)
        st.dataframe(df_clinics, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Risk Distribution")
        risk_data = {
            'Risk Level': ['Low', 'Moderate', 'High', 'Critical'],
            'Count': [252, 200, 600, 448]
        }
        df_risk = pd.DataFrame(risk_data)
        fig = px.pie(df_risk, names='Risk Level', values='Count',
                     color='Risk Level',
                     color_discrete_map={
                         'Low': '#22c55e',           # Bright green
                         'Moderate': '#eab308',     # Bright yellow
                         'High': '#f97316',         # Bright orange
                         'Critical': '#dc2626'      # Bright red
                     })
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Real-time metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model Accuracy", "76.8%", "+2.3%")
    with col2:
        st.metric("Sensitivity", "89.4%", "+1.2%")
    with col3:
        st.metric("Specificity", "72.1%", "-0.5%")
    with col4:
        st.metric("API Status", "✅ Active", "Healthy")

# ============================================================================
# PAGE 2: PATIENT ASSESSMENT WITH AI EXPLANATIONS
# ============================================================================
def page_patient_assessment():
    st.title("🔍 AI-Enhanced Patient Risk Assessment")
    
    outbreak_engine, chatgpt_advisor = load_models()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Patient Information")
        
        # Demographics
        age = st.number_input("Age (years)", min_value=0, max_value=120, value=45)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        st.markdown("### 💊 Medical History")
        vaccination_status = st.select_slider(
            "Vaccination Status",
            options=["Unvaccinated", "Partially Vaccinated", "Fully Vaccinated", "Boosted"],
            value="Fully Vaccinated"
        )
        
        comorbidities = st.multiselect(
            "Comorbidities",
            ["None", "Hypertension", "Diabetes", "Respiratory Issues", "Immunocompromised"],
            default=["None"]
        )
        
        st.markdown("### 🦠 Exposure History")
        travel_history = st.select_slider(
            "Travel History",
            options=["None", "Local", "Regional", "International"],
            value="None"
        )
        
        proximity_to_confirmed = st.select_slider(
            "Contact with Confirmed Cases",
            options=["None", "Indirect Contact", "Direct Contact"],
            value="None"
        )
        
        st.markdown("### 🤒 Current Symptoms")
        symptoms_selected = st.multiselect(
            "Symptoms",
            SYMPTOMS,
            default=[]
        )
        
        days_symptomatic = st.number_input(
            "Days Since Symptom Onset",
            min_value=0,
            max_value=30,
            value=0
        )
        
        assess_button = st.button("🔍 AI Risk Assessment", use_container_width=True)
    
    with col2:
        if assess_button:
            st.subheader("📊 AI-Powered Risk Assessment")
            
            # Prepare patient data
            patient_data = {
                'age': age,
                'gender': gender,
                'vaccination_status': ["Unvaccinated", "Partially Vaccinated", "Fully Vaccinated", "Boosted"].index(vaccination_status),
                'travel_history': ["None", "Local", "Regional", "International"].index(travel_history),
                'proximity_to_confirmed': ["None", "Indirect Contact", "Direct Contact"].index(proximity_to_confirmed),
                'days_symptomatic': days_symptomatic,
                'comorbidities': 1 if "None" not in comorbidities else 0,
                'symptoms': symptoms_selected
            }
            
            # Get assessment
            try:
                if outbreak_engine:
                    assessment = outbreak_engine.assess_patient_risk(patient_data)
                    risk_level = assessment.get('risk_level', 0)
                else:
                    # Simple risk calculation
                    risk_score = (
                        len(symptoms_selected) * 0.5 +
                        days_symptomatic * 0.2 +
                        patient_data['proximity_to_confirmed'] * 1.0 +
                        patient_data['travel_history'] * 0.5 +
                        (1 if patient_data['vaccination_status'] == 0 else 0) * 0.8
                    )
                    risk_level = min(3, int(risk_score / 2))
                    assessment = {
                        'risk_level': risk_level,
                        'confidence': 0.75
                    }
                
                # Display risk level
                risk_bg = [
                    "rgba(34, 197, 94, 0.18)",    # Green for Low
                    "rgba(250, 204, 21, 0.18)",   # Yellow for Moderate
                    "rgba(249, 115, 22, 0.18)",   # Orange for High
                    "rgba(239, 68, 68, 0.22)",    # Red for Critical
                ]
                risk_text = ["#22c55e", "#facc15", "#f97316", "#ef4444"]
                risk_borders = [
                    "rgba(34, 197, 94, 0.40)",
                    "rgba(250, 204, 21, 0.35)",
                    "rgba(249, 115, 22, 0.35)",
                    "rgba(239, 68, 68, 0.40)",
                ]
                risk_names = ['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk']
                
                st.markdown(f"""
                <div style="background-color: {risk_bg[risk_level]}; border: 1px solid {risk_borders[risk_level]}; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2 style="color: {risk_text[risk_level]}; margin: 0;">{risk_names[risk_level]}</h2>
                    <p style="color: {risk_text[risk_level]}; margin: 5px 0;">Confidence: {assessment.get('confidence', 0.5)*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # AI Clinical Explanation
                if ai_enabled and chatgpt_advisor:
                    with st.spinner("🤖 Generating clinical analysis..."):
                        try:
                            explanation = chatgpt_advisor.explain_risk_level(
                                patient_data=patient_data,
                                risk_level=risk_level,
                                confidence=assessment.get('confidence', 0.5)
                            )
                            st.markdown("#### 🤖 Clinical Analysis")
                            st.markdown(f"""
                            <div class="ai-insight">
                            {explanation}
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.info("💡 AI analysis temporarily unavailable")
                
                # Recommendations
                st.markdown("#### 📋 Recommendations")
                if risk_level == 0:
                    st.success("✅ Standard monitoring - No immediate action required")
                elif risk_level == 1:
                    st.warning("⚠️ Continue monitoring - Reassess in 7 days")
                elif risk_level == 2:
                    st.error("🚨 URGENT - Recommend immediate testing & isolation")
                else:
                    st.error("🚨 CRITICAL - Immediate hospitalization recommended")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Assessment History
    st.subheader("📈 Assessment History")
    history_data = {
        'Time': ['10:30', '10:15', '10:00', '09:45'],
        'Age': [45, 28, 62, 35],
        'Risk': ['Moderate', 'Low', 'High', 'Low'],
        'Action': ['Monitor', 'Routine', 'Test+Isolate', 'Routine']
    }
    df_history = pd.DataFrame(history_data)
    st.dataframe(df_history, use_container_width=True)

# ============================================================================
# PAGE 3: CLINIC ANALYTICS WITH AI INSIGHTS
# ============================================================================
def page_clinic_analytics():
    st.title("📊 AI-Powered Clinic Analytics")
    
    clinic_name = st.selectbox(
        "Select Clinic",
        ["Urban Center Clinic", "Rural Area Clinic", "Travel Hub Clinic"]
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    clinic_stats = {
        'Urban Center Clinic': {'patients': 500, 'high_risk': 398, 'clusters': 210, 'accuracy': 0.77},
        'Rural Area Clinic': {'patients': 500, 'high_risk': 330, 'clusters': 30, 'accuracy': 0.72},
        'Travel Hub Clinic': {'patients': 500, 'high_risk': 458, 'clusters': 40, 'accuracy': 0.85}
    }
    
    stats = clinic_stats[clinic_name]
    
    with col1:
        st.metric("Total Patients", stats['patients'])
    with col2:
        st.metric("High-Risk", stats['high_risk'], f"{stats['high_risk']/stats['patients']*100:.1f}%")
    with col3:
        st.metric("Clusters", stats['clusters'])
    with col4:
        st.metric("Accuracy", f"{stats['accuracy']*100:.1f}%")
    
    st.markdown("---")
    
    # AI Recommendations for clinic
    if ai_enabled:
        with st.spinner("🤖 Generating clinic recommendations..."):
            try:
                outbreak_engine, chatgpt_advisor = load_models()
                if chatgpt_advisor:
                    recommendation_prompt = f"""
                    As an epidemiologist, provide 3 key recommendations for {clinic_name}:
                    - Population: {stats['patients']} patients
                    - High-risk: {stats['high_risk']} ({stats['high_risk']/stats['patients']*100:.1f}%)
                    - Outbreak clusters: {stats['clusters']}
                    - Model accuracy: {stats['accuracy']*100:.1f}%
                    
                    Provide specific, actionable strategies (2-3 sentences total).
                    """

                    response = chatgpt_advisor.client.chat.completions.create(
                        model=os.getenv("CHATGPT_MODEL", "llama-3.3-70b-versatile"),
                        messages=[
                            {"role": "system", "content": "You are an infection control specialist."},
                            {"role": "user", "content": recommendation_prompt}
                        ],
                        max_tokens=250,
                        temperature=0.7
                    )
                    
                    recommendations = response.choices[0].message.content
                    st.markdown("### 🤖 AI Recommendations")
                    st.markdown(f"""
                    <div class="ai-insight">
                    {recommendations}
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.info("💡 AI recommendations unavailable")
    
    st.markdown("---")
    
    # Performance trend
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Performance Trend")
        dates = pd.date_range(start='2026-03-01', periods=30, freq='D')
        accuracy_data = np.random.uniform(0.70, 0.88, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=accuracy_data, mode='lines+markers',
                                 name='Accuracy', line=dict(color='#FEE715', width=2)))
        fig.update_layout(title="30-Day Accuracy Trend", hovermode='x unified',
                         xaxis_title="Date", yaxis_title="Accuracy", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Risk Distribution")
        risk_dist = {
            'Low': np.random.randint(50, 100),
            'Moderate': np.random.randint(80, 120),
            'High': np.random.randint(120, 180),
            'Critical': np.random.randint(80, 150)
        }
        fig = go.Figure(data=[
            go.Bar(x=list(risk_dist.keys()), 
                   y=list(risk_dist.values()),
                   marker=dict(color=[
                       '#22c55e',       # Bright green
                       '#eab308',       # Bright yellow
                       '#f97316',       # Bright orange
                       '#dc2626',       # Bright red
                   ]))
        ])
        fig.update_layout(title="Risk Distribution", height=350)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 4: OUTBREAK DETECTION WITH AI ANALYSIS
# ============================================================================
def page_outbreak_detection():
    st.title("🚨 AI-Powered Outbreak Detection")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_risk_threshold = st.slider("High-Risk % Threshold", 0, 100, 50)
    with col2:
        cluster_threshold = st.slider("Cluster Size Threshold", 1, 20, 5)
    with col3:
        analyze_button = st.button("🤖 AI Analysis", use_container_width=True)
    
    st.markdown("---")
    
    # AI Outbreak Analysis
    if ai_enabled and analyze_button:
        with st.spinner("🤖 Performing AI outbreak analysis..."):
            try:
                outbreak_engine, chatgpt_advisor = load_models()
                
                if chatgpt_advisor:
                    outbreak_prompt = """
                    Analyze this outbreak scenario:
                    - Travel Hub Clinic: 458 high-risk patients (91.6%)
                    - Urban Center: 398 high-risk patients (79.6%)
                    - Rural Area: 330 high-risk patients (66.0%)
                    - Total clusters detected: 650
                    
                    Provide:
                    1. Outbreak severity assessment
                    2. Affected populations at highest risk
                    3. Immediate public health actions needed
                    """

                    response = chatgpt_advisor.client.chat.completions.create(
                        model=os.getenv("CHATGPT_MODEL", "llama-3.3-70b-versatile"),
                        messages=[
                            {"role": "system", "content": "You are a public health epidemiologist responding to disease outbreaks."},
                            {"role": "user", "content": outbreak_prompt}
                        ],
                        max_tokens=400,
                        temperature=0.7
                    )
                    
                    analysis = response.choices[0].message.content
                    st.markdown("### 🚨 AI Outbreak Analysis")
                    st.markdown(f"""
                    <div class="ai-insight">
                    {analysis}
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.info("💡 AI analysis temporarily unavailable")
    
    st.markdown("---")
    
    # Clinic Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 Clinic Status")
        outbreak_status = {
            'Clinic': ['Urban Center', 'Rural Area', 'Travel Hub'],
            'Status': ['🟢 Normal', '🟢 Normal', '🟡 Alert'],
            'High-Risk %': [79.6, 66.0, 91.6],
            'Clusters': [210, 30, 40]
        }
        df_status = pd.DataFrame(outbreak_status)
        st.dataframe(df_status, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("🚨 Active Alerts")
        alerts_data = {
            'Time': ['10 min ago', '25 min ago', '1 hour ago'],
            'Clinic': ['Travel Hub', 'Urban Center', 'Rural Area'],
            'Alert': ['High-risk surge', 'Cluster detected', 'Cluster resolved'],
            'Severity': ['🟡 Medium', '🟡 Medium', '🟢 Resolved']
        }
        df_alerts = pd.DataFrame(alerts_data)
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE 5: MODEL PERFORMANCE
# ============================================================================
def page_model_performance():
    st.title("📈 Model Performance & AI Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Individual Clinic Performance")
        
        performance_data = {
            'Clinic': ['Urban Center', 'Rural Area', 'Travel Hub'],
            'Accuracy': [0.77, 0.72, 0.85],
            'Precision': [0.76, 0.71, 0.86],
            'Recall': [0.77, 0.72, 0.85],
            'F1-Score': [0.76, 0.71, 0.85]
        }
        df_perf = pd.DataFrame(performance_data)
        st.dataframe(df_perf, use_container_width=True)
    
    with col2:
        # AI Performance Interpretation
        if ai_enabled:
            st.subheader("🤖 AI Performance Interpretation")
            with st.spinner("🤖 Analyzing model performance..."):
                try:
                    outbreak_engine, chatgpt_advisor = load_models()
                    if not chatgpt_advisor:
                        raise RuntimeError("AI advisor not available")
                    
                    perf_prompt = """
                    Interpret these ML model metrics:
                    - Travel Hub: 85% accuracy (best performer)
                    - Urban Center: 77% accuracy
                    - Rural Area: 72% accuracy (needs improvement)
                    
                    Provide 2-3 insights about what these metrics mean clinically.
                    """

                    response = chatgpt_advisor.client.chat.completions.create(
                        model=os.getenv("CHATGPT_MODEL", "llama-3.3-70b-versatile"),
                        messages=[
                            {"role": "system", "content": "You are an AI/ML expert in healthcare."},
                            {"role": "user", "content": perf_prompt}
                        ],
                        max_tokens=250,
                        temperature=0.7
                    )
                    
                    insights = response.choices[0].message.content
                    st.markdown(f"""
                    <div class="ai-insight">
                    {insights}
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    st.info("💡 Performance insights unavailable")

# ============================================================================
# PAGE 6: AI CHAT ASSISTANT
# ============================================================================
def page_ai_assistant():
    st.title("💬 AI Clinical Assistant")
    
    st.info("""
    🤖 **AI Assistant is ready to help!**
    
    Ask questions about:
    - Patient risk profiles
    - Disease trends
    - Clinical recommendations
    - Outbreak analysis
    - Model insights
    """)
    
    # Chat history
    if 'chat_history' not in st.session_state:
        st. session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    user_question = st.chat_input("Ask the AI clinical assistant...")
    
    if user_question:
        # Add to history
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        # Get AI response
        with st.spinner("🤖 AI Assistant thinking..."):
            try:
                from groq import Groq
                client = Groq(api_key=os.getenv('GROQ_API_KEY'))
                
                system_prompt = """
                You are an experienced epidemiologist and clinical AI assistant.
                Provide evidence-based medical advice and insights about disease outbreaks, 
                patient risk assessment, and public health interventions.
                Be concise but thorough. Include relevant clinical context.
                """
                
                response = client.chat.completions.create(
                    model=os.getenv("CHATGPT_MODEL", "llama-3.3-70b-versatile"),
                    messages=[
                        {"role": "system", "content": system_prompt}
                    ] + [
                        {"role": msg['role'], "content": msg["content"]} 
                        for msg in st.session_state.chat_history
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                assistant_message = response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_message})
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================================================
# PAGE 7: SETTINGS
# ============================================================================
def page_settings():
    st.title("⚙️ System Settings & AI Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 AI Configuration (Groq)")
        
        enable_chatgpt = st.toggle("Enable AI Integration", value=True)
        current_model = os.getenv("CHATGPT_MODEL", "llama-3.3-70b-versatile")
        chatgpt_model = st.selectbox(
            "Groq Model",
            [
                "llama-3.3-70b-versatile (Best quality)",
                "llama-3.1-8b-instant (Fast)",
                "qwen/qwen3-32b (Strong reasoning)",
            ],
            index=0,
        )
        
        if enable_chatgpt:
            st.info("""
            🆓 **Groq Free Tier:**
            - No billing required (within free tier limits)
            - Extremely fast inference
            """)
        
    with col2:
        st.subheader("🔧 System Configuration")
        
        model_type = st.selectbox("Model Type", ["Random Forest", "Gradient Boosting", "Neural Network"])
        aggregation_method = st.selectbox("Aggregation Method", ["Weighted Average", "Majority Voting", "Stacking"])
        
        test_size = st.slider("Test Data %", 10, 40, 20)
        val_size = st.slider("Validation Data %", 10, 30, 20)
    
    st.markdown("---")
    
    # System Status
    st.subheader("📋 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Status", "✅ Healthy")
    with col2:
        st.metric("API Status", "✅ Connected")
    with col3:
        st.metric("AI Model", os.getenv("CHATGPT_MODEL", "llama-3.3-70b-versatile"))
    with col4:
        st.metric("Last Sync", "2 min ago")
    
    st.markdown("---")
    
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✅ Settings saved successfully!")

# ============================================================================
# MAIN APP ROUTER
# ============================================================================
def main():
    if page == "🏠 Dashboard":
        page_dashboard()
    elif page == "🔍 Patient Assessment":
        page_patient_assessment()
    elif page == "📊 Clinic Analytics":
        page_clinic_analytics()
    elif page == "🚨 Outbreak Detection":
        page_outbreak_detection()
    elif page == "📈 Model Performance":
        page_model_performance()
    elif page == "💬 AI Assistant":
        page_ai_assistant()
    elif page == "⚙️ Settings":
        page_settings()

if __name__ == "__main__":
    main()
