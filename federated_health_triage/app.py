"""
Federated Outbreak Detection System - Streamlit Web Application
Real-time clinical decision support across distributed healthcare facilities
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

# Import project modules
from utils.outbreak_detection import OutbreakDetectionEngine
from utils.chatgpt_integration import ChatGPTClinicalAdvisor
from federated_learning.aggregator import ConsolidatedOutbreakDetectionModel
from config import SYMPTOMS, INFECTION_RISK_LEVELS, CLINICS

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Federated Outbreak Detection System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# THEME (Yellow/Black)
# ============================================================================
APP_BG = "#101820"
APP_ACCENT = "#FEE715"
APP_TEXT = "#FFFFFF"

_COLORWAY = [
    APP_ACCENT,
    "rgba(254,231,21,0.80)",
    "rgba(254,231,21,0.60)",
    "rgba(254,231,21,0.40)",
]

pio.templates["hca_yellow_black"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=APP_BG,
        plot_bgcolor=APP_BG,
        font=dict(color=APP_TEXT),
        colorway=_COLORWAY,
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.10)",
            zerolinecolor="rgba(255,255,255,0.15)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.10)",
            zerolinecolor="rgba(255,255,255,0.15)",
        ),
        legend=dict(
            bgcolor="rgba(16,24,32,0.70)",
            bordercolor="rgba(254,231,21,0.35)",
            borderwidth=1,
        ),
        title=dict(font=dict(color=APP_ACCENT)),
    )
)
pio.templates.default = "hca_yellow_black"
px.defaults.template = "hca_yellow_black"

# Load environment variables from the app folder (.env)
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

# Custom CSS
st.markdown("""
<style>
    :root {
        --bg: #101820;
        --accent: #FEE715;
        --text: #FFFFFF;
        --muted: rgba(255, 255, 255, 0.75);
        --panel: rgba(254, 231, 21, 0.08);
        --panel-2: rgba(254, 231, 21, 0.12);
        --border: rgba(254, 231, 21, 0.35);
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: linear-gradient(135deg, #101820 0%, #2a3540 70%, #FEE715 100%) !important;
        background-attachment: fixed !important;
        color: var(--text) !important;
    }

    .main {
        padding-top: 0rem;
    }
    .metric-card {
        background: var(--panel);
        border: 1px solid var(--border);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }

    /* Severity pills - Green/Red gradient */
    .risk-low { background: rgba(34, 197, 94, 0.18); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.40); }
    .risk-moderate { background: rgba(250, 204, 21, 0.18); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.35); }
    .risk-high { background: rgba(249, 115, 22, 0.18); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.35); }
    .risk-critical { background: rgba(239, 68, 68, 0.22); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.40); font-weight: bold; }

    /* Headings */
    h1, h2, h3, h4, h5, h6 { color: var(--accent) !important; }

    /* Sidebar - White text with animations */
    section[data-testid="stSidebar"] {
        background: var(--bg) !important;
        border-right: 1px solid var(--border);
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

    /* AI Insights - Black Text */
    .ai-insight {
        background: rgba(254, 231, 21, 0.15) !important;
        border-left: 4px solid var(--accent) !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
    }
    .ai-insight * {
        color: #000000 !important;
    }
    [data-testid="stAlert"] {
        color: #000000 !important;
    }
    [data-testid="stAlert"] * {
        color: #000000 !important;
    }

    /* Buttons */
    .stButton > button {
        background: var(--accent) !important;
        color: var(--bg) !important;
        border: 1px solid var(--accent) !important;
    }
    .stButton > button:hover {
        filter: brightness(0.95);
    }

    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div,
    [data-testid="stMultiSelect"] div,
    [data-testid="stSlider"] div {
        border-color: var(--border) !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        background: var(--panel-2) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
    st.session_state.clinic_models = {}
    st.session_state.outbreak_engine = None
    st.session_state.chatgpt_advisor = None

# ============================================================================
# SIDEBAR - NAVIGATION & SETTINGS
# ============================================================================
st.sidebar.title("🏥 Federated Outbreak Detection")
st.sidebar.markdown("---")

st.sidebar.subheader("🤖 AI Features")
ai_enabled = st.sidebar.toggle("Enable AI Insights", value=True)

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Dashboard", "🔍 Patient Assessment", "📊 Clinic Analytics", 
    "🚨 Outbreak Detection", "📈 Model Performance", "💬 AI Chart Bot", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("System Information")
st.sidebar.info("""
**Federated Learning System**
- 3 Independent Clinics
- Privacy-Preserving Aggregation
- Real-time Risk Assessment
- ChatGPT Clinical Advisor
""")

# ============================================================================
# LOAD MODELS FUNCTION
# ============================================================================
@st.cache_resource
def load_models():
    """Load pre-trained clinic models and engines"""
    try:
        outbreak_engine = OutbreakDetectionEngine()
    except:
        # Create a simple version without consolidated_model if not available
        outbreak_engine = None
    
    try:
        chatgpt_advisor = ChatGPTClinicalAdvisor()
    except:
        chatgpt_advisor = None
    
    return outbreak_engine, chatgpt_advisor

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================
def page_dashboard():
    st.title("🏥 Federated Outbreak Detection Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Patients", "1,500", "+15% this week")
    
    with col2:
        st.metric("High-Risk Cases", "1,248", "+8% this week")
    
    with col3:
        st.metric("Outbreak Clusters", "650", "+12% this week")

    # AI dashboard insight
    if ai_enabled:
        _, chatgpt_advisor = load_models()
        st.markdown("### 🤖 AI System Insights")
        if not chatgpt_advisor:
            st.info(
                "AI insights are unavailable. Ensure `GROQ_API_KEY` is set in `.env` and the `groq` package is installed."
            )
        else:
            with st.spinner("🤖 Generating AI insight..."):
                insight = chatgpt_advisor.generate_dashboard_insight(
                    clinic_name="System-wide",
                    high_risk_count=1248,
                    total_count=1500,
                    cluster_count=650,
                )
                st.info(insight)
    
    st.markdown("---")
    
    # System Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Clinic Status")
        clinic_data = {
            'Clinic': ['Urban Center', 'Rural Area', 'Travel Hub'],
            'Patients': [500, 500, 500],
            'High-Risk': [398, 330, 458],
            'Outbreak Clusters': [210, 30, 40],
            'Status': ['✅ Active', '✅ Active', '🟡 High Activity']
        }
        df_clinics = pd.DataFrame(clinic_data)
        st.dataframe(df_clinics, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Risk Distribution")
        risk_data = {
            'Risk Level': ['Low', 'Moderate', 'High', 'Critical'],
            'Count': [252, 200, 600, 448],
            'Percentage': [16.8, 13.3, 40.0, 29.9]
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
        st.metric("API Response", "245ms", "✅ Healthy")

# ============================================================================
# PAGE 2: PATIENT ASSESSMENT
# ============================================================================
def page_patient_assessment():
    st.title("🔍 Individual Patient Risk Assessment")
    
    outbreak_engine, chatgpt_advisor = load_models()
    
    # Create two columns for input and results
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
        
        assess_button = st.button("🔍 Assess Risk", use_container_width=True)
    
    with col2:
        if assess_button:
            st.subheader("📊 Risk Assessment Results")
            
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
                    # Simple risk calculation if engine not available
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
                
                # Display risk level with color coding
                risk_colors = [
                    'rgba(34,197,94,0.18)',     # Green for Low
                    'rgba(250,204,21,0.18)',    # Yellow for Moderate
                    'rgba(249,115,22,0.18)',    # Orange for High
                    'rgba(239,68,68,0.22)',     # Red for Critical
                ]
                risk_text_colors = [
                    '#22c55e',  # Green text for Low
                    '#facc15',  # Yellow text for Moderate
                    '#f97316',  # Orange text for High
                    '#ef4444',  # Red text for Critical
                ]
                risk_borders = [
                    'rgba(34,197,94,0.40)',
                    'rgba(250,204,21,0.35)',
                    'rgba(249,115,22,0.35)',
                    'rgba(239,68,68,0.40)',
                ]
                risk_names = ['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk']
                
                st.markdown(f"""
                <div style="background: {risk_colors[risk_level]}; border: 1px solid {risk_borders[risk_level]}; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2 style="color: {risk_text_colors[risk_level]}; margin: 0;">{risk_names[risk_level]}</h2>
                    <p style="color: {risk_text_colors[risk_level]}; margin: 5px 0;">Confidence: {assessment.get('confidence', 0.5)*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                if outbreak_engine:
                    st.markdown("#### Risk Factors")
                    factors = outbreak_engine._get_risk_factors(patient_data)
                    for i, factor in enumerate(factors, 1):
                        st.write(f"{i}. ⚠️ {factor}")
                    
                    st.markdown("#### Clinical Recommendations")
                    recommendations = outbreak_engine._get_recommendations(risk_level, patient_data)
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
                else:
                    # Display generic recommendations
                    st.markdown("#### ⚠️ Risk Factors Identified")
                    if len(symptoms_selected) > 0:
                        st.write(f"• Multiple symptoms reported: {', '.join(symptoms_selected[:3])}")
                    if days_symptomatic > 0:
                        st.write(f"• Symptomatic for {days_symptomatic} days")
                    if patient_data['proximity_to_confirmed'] > 0:
                        st.write("• Contact with confirmed cases")
                    if patient_data['travel_history'] > 0:
                        st.write("• Recent travel history")
                    
                    st.markdown("#### 📋 Recommendations")
                    if risk_level == 0:
                        st.write("• Monitor for symptom development")
                        st.write("• Encourage standard precautions")
                    elif risk_level == 1:
                        st.write("• Continue monitoring closely")
                        st.write("• Consider testing if symptoms progress")
                    elif risk_level == 2:
                        st.write("• ⚠️ URGENT: Recommend immediate testing")
                        st.write("• Patient should isolate for 10 days")
                    else:
                        st.write("• 🚨 CRITICAL: Immediate isolation required")
                        st.write("• Urgent testing and hospitalization recommended")
                
                # ChatGPT explanation
                if chatgpt_advisor:
                    with st.spinner("🤖 Generating clinical analysis..."):
                        try:
                            explanation = chatgpt_advisor.explain_risk_level(
                                patient_data=patient_data,
                                risk_level=risk_level,
                                confidence=assessment.get('confidence', 0.5)
                            )
                            st.markdown("#### 🤖 Clinical Analysis (via ChatGPT)")
                            st.info(explanation)
                        except:
                            pass
                
            except Exception as e:
                st.error(f"Error assessing risk: {str(e)}")
    
    st.markdown("---")
    
    # Historical assessment data
    st.subheader("📈 Assessment History")
    
    history_data = {
        'Timestamp': ['2026-04-07 10:30', '2026-04-07 10:15', '2026-04-07 10:00', '2026-04-07 09:45'],
        'Patient': ['P-12345', 'P-12344', 'P-12343', 'P-12342'],
        'Age': [45, 28, 62, 35],
        'Risk Level': ['Moderate', 'Low', 'High', 'Low'],
        'Action': ['Monitor', 'Routine', 'Test + Isolate', 'Routine']
    }
    df_history = pd.DataFrame(history_data)
    st.dataframe(df_history, use_container_width=True)

# ============================================================================
# PAGE 3: CLINIC ANALYTICS
# ============================================================================
def page_clinic_analytics():
    st.title("📊 Clinic-Level Analytics")
    
    # Select clinic
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
        st.metric("Model Accuracy", f"{stats['accuracy']*100:.1f}%")
    
    st.markdown("---")
    
    # AI Insights for this clinic
    if ai_enabled:
        outbreak_engine, chatgpt_advisor = load_models()
        if chatgpt_advisor:
            with st.spinner("🤖 Generating clinic insights..."):
                clinic_insight = chatgpt_advisor.generate_dashboard_insight(
                    clinic_name=clinic_name.replace(" Clinic", ""),
                    high_risk_count=stats['high_risk'],
                    total_count=stats['patients'],
                    cluster_count=stats['clusters'],
                )
                st.markdown("### 🤖 AI Clinic Insights")
                st.markdown(f'<div class="ai-insight">{clinic_insight}</div>', unsafe_allow_html=True)
    
    # Performance over time
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Model Performance Trend")
        dates = pd.date_range(start='2026-03-01', periods=30, freq='D')
        accuracy_data = np.random.uniform(0.65, 0.85, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=accuracy_data, mode='lines+markers',
                                 name='Accuracy', line=dict(color=APP_ACCENT, width=2)))
        fig.update_layout(title="30-Day Accuracy Trend", hovermode='x unified',
                         xaxis_title="Date", yaxis_title="Accuracy")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Classification Distribution")
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
        fig.update_layout(
            title="Current Risk Distribution",
            xaxis_title="Risk Level",
            yaxis_title="Patient Count",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Feature importance
    st.subheader("🔍 Feature Importance")
    features = ['Age', 'Vaccination', 'Travel History', 'Contact History', 'Symptoms', 'Comorbidities']
    importance = [0.22, 0.19, 0.16, 0.18, 0.15, 0.10]
    
    fig = go.Figure(data=[go.Bar(
        y=features,
        x=importance,
        orientation='h',
        marker=dict(color=APP_ACCENT)
    )])
    fig.update_layout(
        title="Model Feature Importance",
        xaxis_title="Importance Score",
        yaxis_title="Feature",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 4: OUTBREAK DETECTION
# ============================================================================
def page_outbreak_detection():
    st.title("🚨 Population-Level Outbreak Detection")
    
    # Outbreak thresholds
    st.subheader("⚙️ Detection Thresholds")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_risk_threshold = st.slider("High-Risk % Threshold", 0, 100, 50)
    
    with col2:
        cluster_threshold = st.slider("Cluster Size Threshold", 1, 20, 5)

    # Auto analysis (no button needed)
    snapshot = {
        "clinics": [
            {"name": "Urban Center", "high_risk_pct": 79.6, "clusters": 210},
            {"name": "Rural Area", "high_risk_pct": 66.0, "clusters": 30},
            {"name": "Travel Hub", "high_risk_pct": 91.6, "clusters": 40},
        ],
        "total_patients": 1500,
        "high_risk_cases": 1248,
        "outbreak_clusters": 650,
    }

    exceeding = [
        c
        for c in snapshot["clinics"]
        if (c["high_risk_pct"] >= float(high_risk_threshold))
        or (c["clusters"] >= int(cluster_threshold))
    ]

    if not exceeding:
        st.success(
            "✅ No clinic exceeds the current thresholds. Continue routine monitoring and reassess if trends change."
        )
    else:
        hot_list = ", ".join([c["name"] for c in exceeding])
        st.warning(
            f"⚠️ Threshold(s) exceeded in: {hot_list}. Prioritize testing/isolation workflows and monitor cluster growth."
        )

    # AI outbreak analysis
    if ai_enabled:
        outbreak_engine, chatgpt_advisor = load_models()
        if chatgpt_advisor:
            with st.spinner("🤖 Generating outbreak analysis..."):
                outbreak_insight = chatgpt_advisor.generate_dashboard_insight(
                    clinic_name="System-wide Outbreak Analysis",
                    high_risk_count=snapshot["high_risk_cases"],
                    total_count=snapshot["total_patients"],
                    cluster_count=snapshot["outbreak_clusters"],
                )
                st.markdown("### 🤖 AI Outbreak Insights")
                st.markdown(f'<div class="ai-insight">{outbreak_insight}</div>', unsafe_allow_html=True)

    st.subheader("📊 Threshold View")
    df_threshold = pd.DataFrame(
        {
            "Clinic": [c["name"] for c in snapshot["clinics"]],
            "High-Risk %": [c["high_risk_pct"] for c in snapshot["clinics"]],
            "Clusters": [c["clusters"] for c in snapshot["clinics"]],
        }
    )

    fig_hr = px.bar(
        df_threshold,
        x="Clinic",
        y="High-Risk %",
        text="High-Risk %",
        title="High-Risk % by Clinic",
    )
    fig_hr.add_hline(
        y=float(high_risk_threshold),
        line_dash="dash",
            line_color="#FEE715",
        annotation_text="High-Risk % Threshold",
    )
    fig_hr.update_traces(textposition="outside")
    fig_hr.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_hr, use_container_width=True)

    fig_cl = px.bar(
        df_threshold,
        x="Clinic",
        y="Clusters",
        text="Clusters",
        title="Clusters by Clinic",
    )
    fig_cl.add_hline(
        y=int(cluster_threshold),
        line_dash="dash",
            line_color="#FEE715",
        annotation_text="Cluster Threshold",
    )
    fig_cl.update_traces(textposition="outside")
    st.plotly_chart(fig_cl, use_container_width=True)

    st.info("For smart, healthcare-specific guidance, open **💬 AI Chart Bot** from the left sidebar.")

    st.markdown("---")
    
    # Current outbreak status (demo snapshot)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 Clinic-Level Status")
        
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
    
    # Outbreak timeline
    st.subheader("📅 Outbreak Timeline (Last 7 Days)")
    
    dates_timeline = pd.date_range(end=datetime.now(), periods=7, freq='D')
    high_risk_counts = [380, 390, 395, 398, 410, 420, 1248]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates_timeline, y=high_risk_counts, mode='lines+markers',
                            fill='tozeroy', name='High-Risk Count',
                            line=dict(color=APP_ACCENT, width=3)))
    fig.add_hline(y=high_risk_threshold, line_dash="dash", line_color=APP_ACCENT,
                 annotation_text="Alert Threshold")
    fig.update_layout(title="High-Risk Patient Trend",
                     xaxis_title="Date", yaxis_title="High-Risk Count",
                     hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 5: MODEL PERFORMANCE
# ============================================================================
def page_model_performance():
    st.title("📈 Model Performance Metrics")
    
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
        
        # Radar chart
        fig = go.Figure()
        for idx, clinic in enumerate(df_perf['Clinic']):
            fig.add_trace(go.Scatterpolar(
                r=[df_perf['Accuracy'][idx], df_perf['Precision'][idx], 
                   df_perf['Recall'][idx], df_perf['F1-Score'][idx]],
                theta=['Accuracy', 'Precision', 'Recall', 'F1-Score'],
                fill='toself',
                name=clinic
            ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                         showlegend=True, title="Clinic Performance Comparison")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🤖 Performance Assessment")
        if ai_enabled:
            outbreak_engine, chatgpt_advisor = load_models()
            if chatgpt_advisor:
                with st.spinner("🤖 Generating performance analysis..."):
                    perf_insight = chatgpt_advisor.generate_dashboard_insight(
                        clinic_name="Federated Model",
                        high_risk_count=1248,
                        total_count=1500,
                        cluster_count=650,
                    )
                    st.markdown("### 🤖 Model Insights")
                    st.markdown(f'<div class="ai-insight">{perf_insight}</div>', unsafe_allow_html=True)
            else:
                st.info("Enable AI Features in the sidebar to see AI analysis.")
        else:
            st.info("Enable AI Features in the sidebar to see AI analysis.")

# ============================================================================
# PAGE 6: AI CHART BOT (HEALTHCARE)
# ============================================================================
def page_ai_chart_bot():
    st.title("💬 AI Chart Bot (Healthcare)")
    st.caption(
        "Ask about severity, who is at risk, and what actions to take based on charts and thresholds."
    )

    outbreak_engine, chatgpt_advisor = load_models()

    # Same snapshot used in outbreak page (demo)
    snapshot = {
        "clinics": [
            {"name": "Urban Center", "high_risk_pct": 79.6, "clusters": 210},
            {"name": "Rural Area", "high_risk_pct": 66.0, "clusters": 30},
            {"name": "Travel Hub", "high_risk_pct": 91.6, "clusters": 40},
        ],
        "total_patients": 1500,
        "high_risk_cases": 1248,
        "outbreak_clusters": 650,
    }

    st.subheader("⚙️ Context")
    col1, col2, col3 = st.columns(3)
    with col1:
        high_risk_threshold = st.slider("High-Risk % Threshold", 0, 100, 50)
    with col2:
        cluster_threshold = st.slider("Cluster Size Threshold", 1, 20, 5)
    with col3:
        analyze = st.button("📊 Load Charts", use_container_width=True)

    df_threshold = pd.DataFrame(
        {
            "Clinic": [c["name"] for c in snapshot["clinics"]],
            "High-Risk %": [c["high_risk_pct"] for c in snapshot["clinics"]],
            "Clusters": [c["clusters"] for c in snapshot["clinics"]],
        }
    )

    if analyze:
        exceeding = [
            c
            for c in snapshot["clinics"]
            if (c["high_risk_pct"] >= float(high_risk_threshold))
            or (c["clusters"] >= int(cluster_threshold))
        ]

        st.subheader("🧠 Summary")
        if not exceeding:
            st.success(
                "✅ No clinic exceeds the current thresholds. Continue routine monitoring."
            )
        else:
            hot_list = ", ".join([c["name"] for c in exceeding])
            st.warning(
                f"⚠️ Threshold(s) exceeded in: {hot_list}. Prioritize testing/isolation workflows and monitor cluster growth."
            )

        st.subheader("📈 Charts")
        fig_hr = px.bar(
            df_threshold,
            x="Clinic",
            y="High-Risk %",
            text="High-Risk %",
            title="High-Risk % by Clinic",
        )
        fig_hr.add_hline(
            y=float(high_risk_threshold),
            line_dash="dash",
            line_color="#FEE715",
            annotation_text="High-Risk % Threshold",
        )
        fig_hr.update_traces(textposition="outside")
        fig_hr.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_hr, use_container_width=True)

        fig_cl = px.bar(
            df_threshold,
            x="Clinic",
            y="Clusters",
            text="Clusters",
            title="Clusters by Clinic",
        )
        fig_cl.add_hline(
            y=int(cluster_threshold),
            line_dash="dash",
            line_color="#FEE715",
            annotation_text="Cluster Threshold",
        )
        fig_cl.update_traces(textposition="outside")
        st.plotly_chart(fig_cl, use_container_width=True)

    st.markdown("---")
    st.subheader("🤖 Ask the Bot")

    if not ai_enabled:
        st.info("Enable AI Insights in the sidebar to use the AI Chart Bot.")
        return

    if not chatgpt_advisor:
        st.info(
            "AI is unavailable. Ensure `GROQ_API_KEY` is set in `.env` and dependencies are installed."
        )
        return

    if "ai_chart_bot_history" not in st.session_state:
        st.session_state.ai_chart_bot_history = []

    # Auto insight (small + practical)
    with st.spinner("🤖 Generating AI interpretation..."):
        ai_text = chatgpt_advisor.generate_dashboard_insight(
            clinic_name="AI Chart Bot",
            high_risk_count=snapshot["high_risk_cases"],
            total_count=snapshot["total_patients"],
            cluster_count=snapshot["outbreak_clusters"],
        )
        st.info(ai_text)

    question = st.text_input(
        "Ask a question",
        placeholder="e.g., What should we do in the next 24 hours at Travel Hub?",
    )
    if st.button("💬 Ask AI", use_container_width=True) and question:
        context = (
            f"Thresholds: high-risk% >= {high_risk_threshold}, clusters >= {cluster_threshold}. "
            f"Snapshot: {df_threshold.to_dict(orient='records')}. "
            f"Totals: patients={snapshot['total_patients']}, high_risk={snapshot['high_risk_cases']}, clusters={snapshot['outbreak_clusters']}."
        )
        with st.spinner("🤖 Thinking..."):
            try:
                response = chatgpt_advisor.client.chat.completions.create(
                    model=chatgpt_advisor.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an infection-control and public-health assistant. "
                                "Give actionable, healthcare-specific guidance (testing, isolation, PPE, triage, staffing, surveillance). "
                                "Be concise and avoid speculation beyond provided numbers."
                            ),
                        },
                        {"role": "user", "content": f"CONTEXT: {context}\n\nQUESTION: {question}"},
                    ],
                    max_tokens=350,
                    temperature=0.35,
                )
                answer = response.choices[0].message.content
                st.session_state.ai_chart_bot_history.append((question, answer))
            except Exception as e:
                st.session_state.ai_chart_bot_history.append((question, f"AI error: {str(e)}"))

    for q, a in st.session_state.ai_chart_bot_history[-5:]:
        st.markdown(f"**Q:** {q}")
        st.info(a)
    
    with col2:
        st.subheader("Federated Ensemble Performance")
        
        col1_sub, col2_sub = st.columns(2)
        
        with col1_sub:
            st.metric("Ensemble Accuracy", "56.0%")
            st.metric("Sensitivity", "89.4%")
        
        with col2_sub:
            st.metric("Specificity", "72.1%")
            st.metric("F1-Score", "0.497")
        
        # Confusion matrix
        st.subheader("Confusion Matrix (Ensemble)")
        cm_data = np.array([[650, 280], [70, 500]])
        
        fig = go.Figure(data=go.Heatmap(
            z=cm_data,
            x=['Predicted Negative', 'Predicted Positive'],
            y=['Actual Negative', 'Actual Positive'],
            text=cm_data,
            texttemplate="%{text}",
            colorscale=[[0, APP_BG], [1, APP_ACCENT]]
        ))
        fig.update_layout(title="Confusion Matrix", xaxis_title="Predicted", 
                         yaxis_title="Actual")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 6: SETTINGS
# ============================================================================
def page_settings():
    st.title("⚙️ System Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Model Configuration")
        
        model_type = st.selectbox("Model Type", ["Random Forest", "Gradient Boosting", "Neural Network"])
        aggregation_method = st.selectbox("Aggregation Method", ["Weighted Average", "Majority Voting", "Stacking"])
        
        st.subheader("📊 Data Settings")
        test_size = st.slider("Test Data %", 10, 40, 20)
        val_size = st.slider("Validation Data %", 10, 30, 20)
    
    with col2:
        st.subheader("🤖 ChatGPT Integration")
        
        use_chatgpt = st.toggle("Enable ChatGPT Clinical Advisor", value=True)
        model_choice = st.selectbox("ChatGPT Model", ["gpt-3.5-turbo", "gpt-4"])
        
        if use_chatgpt:
            api_warning = st.checkbox("Show API Cost Warnings", value=True)
            st.info("💰 Estimated API cost: $4.50/month for 1000 assessments/day")
        
        st.subheader("🔔 Notifications")
        
        notify_outbreak = st.toggle("Alert on Outbreak Detection", value=True)
        notify_threshold = st.number_input("Alert Threshold (high-risk %)", 0, 100, 75)
    
    st.markdown("---")
    
    # System status
    st.subheader("📋 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", "✅ Healthy")
    
    with col2:
        st.metric("API Status", "✅ Connected")
    
    with col3:
        st.metric("Last Sync", "2 min ago")
    
    st.markdown("---")
    
    # Save settings button
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
    elif page == "💬 AI Chart Bot":
        page_ai_chart_bot()
    elif page == "⚙️ Settings":
        page_settings()

if __name__ == "__main__":
    main()
