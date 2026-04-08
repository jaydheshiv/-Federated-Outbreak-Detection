# Federated Outbreak Detection System

A real-time clinical decision support system for detecting and managing disease outbreaks across distributed healthcare facilities using federated learning and AI.

## 🏥 Overview

The **Federated Outbreak Detection System** is a Streamlit-based web application that enables:
- **Individual Patient Risk Assessment** - Evaluate outbreak risk for each patient
- **Population-Level Outbreak Detection** - Identify disease clusters and trends across clinics
- **Privacy-Preserving Analysis** - Use federated learning so clinics keep their data private
- **AI-Powered Clinical Guidance** - Get actionable recommendations via ChatGPT clinical advisor
- **Real-time Monitoring** - Track disease spread with interactive dashboards and alerts

## 🎯 Key Features

### 1. **Dashboard** 🏠
- System-wide overview of patient metrics
- High-risk case tracking (1,500+ patients)
- Outbreak cluster detection
- AI-powered system insights

### 2. **Patient Assessment** 🔍
- Individual risk evaluation based on:
  - Age, gender, vaccination status
  - Symptoms, travel history
  - Contact with confirmed cases
- Risk classification (Low/Moderate/High/Critical)
- Clinical recommendations (isolation, testing, hospitalization)

### 3. **Clinic Analytics** 📊
- Clinic-specific performance metrics
- 30-day accuracy trends
- Risk distribution analysis
- Feature importance rankings

### 4. **Outbreak Detection** 🚨
- Population-level outbreak tracking
- Configurable alert thresholds
- 7-day trend analysis
- Multi-clinic status monitoring

### 5. **Model Performance** 📈
- Accuracy, Precision, Recall, F1-Score by clinic
- Federated ensemble performance
- Confusion matrix analysis
- Radar chart comparisons

### 6. **AI Chart Bot** 💬
- Interactive chatbot for chart interpretation
- Ask questions about severity, risk, and actions
- AI-powered healthcare-specific guidance

### 7. **Settings** ⚙️
- Model configuration (Random Forest, Gradient Boosting, Neural Network)
- ChatGPT integration settings
- Notification and alert thresholds
- System status monitoring

## 📋 Use Cases

### Pandemic Response
- Detect early outbreak signals before widespread spread
- Monitor hospital capacity and surge planning
- Guide isolation and testing prioritization
- Support public health decision-making

### Endemic Disease Monitoring
- Continuous surveillance for influenza, measles, TB
- Identify hotspots and high-risk populations
- Alert on anomalous case increases
- Evaluate intervention effectiveness

### Clinical Triage
- Risk-stratify patients at point of care
- Support isolation decisions
- Guide testing recommendations
- Validate clinical judgment with ML insights

## 🛠️ Tech Stack

- **Frontend:** Streamlit 1.34.0
- **Backend:** Python 3.12.6
- **Visualization:** Plotly 5.22.0
- **Data Processing:** Pandas, NumPy
- **AI:** ChatGPT via Groq API (Free tier, llama-3.3-70b-versatile)
- **ML:** Federated Learning (3 independent clinic models)
- **Architecture:** Federated Learning with privacy-preserving aggregation

## 📦 Installation

### Prerequisites
- Python 3.10+
- Virtual environment (venv)
- Git
- Active Groq API key (free at https://console.groq.com)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/jaydheshiv/-Federated-Outbreak-Detection.git
cd "Federated-Outbreak-Detection"
```

2. **Create virtual environment**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API key**
Create `.env` file in `federated_health_triage/` folder:
```
GROQ_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
streamlit run federated_health_triage/app.py
```

The app will open at `http://localhost:8501`

## 📊 Project Structure

```
.
├── federated_health_triage/
│   ├── app.py                      # Main Streamlit application
│   ├── app_ai_enhanced.py          # Enhanced UI variant
│   ├── config.py                   # Configuration (symptoms, clinics)
│   ├── .env                        # API keys (create this)
│   ├── .streamlit/
│   │   └── config.toml             # Streamlit theme config
│   └── utils/
│       ├── outbreak_detection.py   # Risk assessment engine
│       ├── chatgpt_integration.py  # AI advisor (Groq API)
│       └── ...
├── federated_learning/
│   ├── aggregator.py               # Federated model aggregation
│   └── ...
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🎨 Theme & Design

- **Color Palette:** 
  - Primary: `#FEE715` (Yellow accent)
  - Background: `#101820` (Dark navy)
  - Text: `#FFFFFF` (White)
  
- **Risk Levels:**
  - 🟢 Low Risk: `#22c55e` (Green)
  - 🟡 Moderate Risk: `#eab308` (Yellow)
  - 🟠 High Risk: `#f97316` (Orange)
  - 🔴 Critical Risk: `#dc2626` (Red)

- **Gradient Background:** `linear-gradient(135deg, #101820 0%, #2a3540 70%, #FEE715 100%)`

## 🔒 Privacy & Security

- **Federated Learning:** Each clinic trains models locally, only predictions are shared
- **No Raw Data Sharing:** Patient data never leaves clinic servers
- **API Protection:** Groq API ensures no data storage on external servers
- **HIPAA-Ready:** Architecture supports healthcare compliance requirements

## 📈 Disease Tracking Scenario

**Day 1:** 8% high-risk patients detected → 🟢 Normal
**Day 7:** 28% high-risk patients → 🟡 Alert  
**Day 14:** 83% high-risk patients → 🚨 Critical
**Day 21+:** Declining trend with interventions → Recovery phase

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/YourFeature`
3. Commit changes: `git commit -m 'Add YourFeature'`
4. Push to branch: `git push origin feature/YourFeature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

- Development Team: Federated Outbreak Detection Project
- Built with Streamlit, Plotly, and Groq API

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

## 🔗 Links

- **GitHub Repository:** https://github.com/jaydheshiv/-Federated-Outbreak-Detection
- **Streamlit Docs:** https://docs.streamlit.io
- **Groq API:** https://console.groq.com
- **Plotly Documentation:** https://plotly.com/python

---

**Last Updated:** April 8, 2026  
**Version:** 1.0.0
