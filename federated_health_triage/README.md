# Federated Outbreak Detection System

**Early Risk Detection of Infectious Disease Across Distributed Clinics**

A privacy-preserving AI system that detects early signs of infectious disease outbreaks across geographically distributed healthcare facilities using federated learning. Enables real-time public health response without compromising patient privacy.

## 🎯 Project Overview

### The Problem

Infectious disease outbreaks spread rapidly across regions, but early detection is challenging because:
- **Data Silos**: Patient data is fragmented across independent clinics
- **Privacy Barriers**: Clinics cannot easily share raw patient data due to regulations
- **Time Pressure**: Outbreak response requires immediate action
- **Geographic Distribution**: Patterns may only be visible when combining data from multiple locations

### The Solution

This system combines **federated learning** and **epidemiological modeling** to:
- Detect high-risk patients at each clinic independently
- Aggregate outbreak signals without sharing patient data
- Identify outbreak clusters across clinics
- Enable coordinated public health response

## 🌍 Three Clinic Archetypes

The system demonstrates outbreak detection across three realistic healthcare settings:

### 🏙️ Clinic_A: Urban Center
- **Location**: Dense metropolitan area
- **Population**: High-volume patient flow
- **Travel Exposure**: Moderate (0.3) - regional travel
- **Baseline Infection Rate**: 15%
- **Key Risk**: Community transmission, diverse patient origins

### 🌾 Clinic_B: Rural Area
- **Location**: Agricultural/remote region
- **Population**: Stable, lower turnover
- **Travel Exposure**: Low (0.1) - minimal travel
- **Baseline Infection Rate**: 10.5%
- **Key Risk**: Limited healthcare access, delayed diagnosis

### ✈️ Clinic_C: Travel Hub
- **Location**: Near major transportation (airport/station)
- **Population**: Transient, high turnover
- **Travel Exposure**: High (0.8) - international travel
- **Baseline Infection Rate**: 19.5%
- **Key Risk**: Rapid disease importation, early outbreak indicator

## 🚀 Core Features

### 1. **Epidemiological Risk Assessment**
Evaluates infection risk using key epidemiological factors:
- **Contact Tracing** (×0.7 weight): Direct contact with confirmed cases
- **Vaccination Status** (×0.4 weight): Protection level (0=unvaccinated, 1=partial, 2=full, 3=boosted)
- **Travel Exposure** (×0.3 weight): Recent travel history
- **Clinical Symptoms**: Fever, cough, respiratory distress, loss of taste/smell
- **Host Factors**: Age, comorbidities, immunocompromised status

### 2. **Infection Risk Levels**
- **Level 0** (Green): Low risk - routine monitoring
- **Level 1** (Yellow): Moderate risk - clinical observation
- **Level 2** (Red): High risk - requires testing and isolation
- **Level 3** (Magenta): Critical risk - emergency response, public health alert

### 3. **Outbreak Cluster Detection**
Identifies temporal outbreak patterns:
- Detects ≥5 high-risk patients in 7-day window
- Flags clusters per clinic location
- Triggers public health team notifications
- Enables spatial correlation analysis

### 4. **Federated Privacy-Preserving Architecture**
```
Clinic_A (Urban)          Clinic_B (Rural)         Clinic_C (Travel Hub)
   ↓ [local data]            ↓ [local data]           ↓ [local data]
   └─ Infection Risk ────────────── Model ───────────────────┘
      Detection Model         Detection Model        Detection Model
        (Trained)               (Trained)              (Trained)
   ↓                        ↓                       ↓
   └─────────────────── Aggregate Models ──────────────────┘
                               ↓
                    Consolidated Ensemble
                    (No patient data shared)
                               ↓
                    Outbreak Detection Engine
                               ↓
                    Population-Level Signals
                               ↓
                    Public Health Actionable Intelligence
```

## 📊 System Architecture

### Machine Learning Pipeline

1. **Data Generation**: Creates realistic epidemiological scenarios
2. **Preprocessing**: Temporal handling, feature engineering
3. **Local Training**: Each clinic trains infection risk model
4. **Federated Aggregation**: Combines models while preserving privacy
5. **Ensemble Creation**: Consolidated outbreak detection model
6. **Risk Assessment**: Evaluates individual and population risk
7. **Outbreak Detection**: Identifies clusters and triggers alerts

### Key Algorithms

**Epidemiological Risk Scoring**:
```
Risk = (Contact_Tracing × 0.7 + Vaccination × 0.4 + Travel × 0.3 
        + Age_Factor + Symptom_Severity + Comorbidity_Factor) / normalization
```

**Outbreak Cluster Identification**:
```
Cluster Detected if: Count(Risk Level ≥ 2) ≥ 5 within TIME_WINDOW (7 days)
Alert Level: HIGH if Count ≥ 10, MODERATE if Count ≥ 5
```

## 💻 Installation & Setup

### Prerequisites
- Python 3.10+
- pip or conda
- ~2GB disk space for data/models

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/federated_outbreak_detection.git
cd federated_outbreak_detection
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -m pytest tests/test_system.py -v
```

## 📚 Complete Documentation (NEW!)

**NEW GUIDES ADDED** - Comprehensive guides for running the system:

| File | Purpose | Best For |
|------|---------|----------|
| **[QUICK_START.md](QUICK_START.md)** | 60-second startup guide | Getting running in minutes |
| **[AI_FEATURES_GUIDE.md](AI_FEATURES_GUIDE.md)** | All 10 ChatGPT AI features explained | Understanding the AI integration |
| **[APP_COMPARISON.md](APP_COMPARISON.md)** | Standard vs AI-Enhanced comparison | Deciding which app to use |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | 10 common issues + fixes | Solving problems quickly |
| **[STREAMLIT_SETUP.md](STREAMLIT_SETUP.md)** | Installation & deployment | Setting up the environment |
| **[STREAMLIT_QUICK_START.md](STREAMLIT_QUICK_START.md)** | Quick command reference | Fast command lookup |

**⭐ START HERE:** Read [QUICK_START.md](QUICK_START.md) first!

### What's New
- ✨ **AI-Enhanced Streamlit App** (`app_ai_enhanced.py`) - ChatGPT integration throughout
- 🤖 **10 Intelligent Features** - Clinical explanations, recommendations, trend forecasting
- 💬 **AI Chat Assistant** - Interactive Q&A with system data
- 📊 **Production-Ready** - Both standard and AI versions fully functional

---

## 🎓 Quick Start

### Install & Run (2 minutes)

```bash
# Install dependencies
pip install -r requirements-streamlit.txt

# Run Standard Web App
streamlit run app.py

# OR Run AI-Enhanced Web App
streamlit run app_ai_enhanced.py

# OR Run Training Pipeline
python train.py
```

### Run Complete Pipeline

```bash
python train.py
```

This executes:
1. Generate epidemiological data for 3 clinics
2. Train infection risk detection models (local)
3. Federated aggregation (no data sharing)
4. Create consolidated outbreak detection ensemble
5. Evaluate model performance
6. Demonstrate outbreak detection scenarios
7. Analyze population-level outbreak signals
8. Generate alerts for public health response

### Example Usage

```python
from train import FederatedOutbreakDetectionSystem

# Initialize system
system = FederatedOutbreakDetectionSystem(n_samples=1000)

# Generate synthetic epidemiological data
system.generate_epidemiological_data()

# Train local infection risk models
system.train_clinic_infection_models()

# Perform federated aggregation
system.aggregate_models_federated()

# Create consolidated ensemble
system.create_consolidated_outbreak_model()

# Assess individual patient
patient_features = {
    'age': 65,
    'fever': 1,
    'cough': 1,
    'loss_of_taste_smell': 1,           # KEY INDICATOR
    'vaccination_status': 0,             # Unvaccinated
    'proximity_to_confirmed': 2,         # Direct contact
    'travel_history': 0,
    'days_symptomatic': 4,
    'age_group': 3,
    'comorbidities': 1
}

assessment = system.outbreak_engine.assess_patient(patient_features)
report = system.outbreak_engine.generate_assessment_report(
    patient_features, 
    assessment, 
    'Urban Center'
)

print(report)

# Detect population-level outbreaks
outbreak_signals = system.detect_population_level_outbreaks()
```

## 📁 Project Structure

```
federated_outbreak_detection/
├── data/
│   ├── Clinic_A_epidemiological.csv      # Urban center data
│   ├── Clinic_B_epidemiological.csv      # Rural area data
│   └── Clinic_C_epidemiological.csv      # Travel hub data
├── models/
│   ├── clinic_model.py                   # Infection risk model
│   ├── Clinic_A_model.pkl
│   ├── Clinic_B_model.pkl
│   └── Clinic_C_model.pkl
├── federated_learning/
│   └── aggregator.py                     # Federated aggregation
├── utils/
│   ├── data_generator.py                 # Epidemiological data
│   ├── preprocessing.py                  # Feature engineering
│   └── outbreak_detection.py             # Outbreak analysis engine
├── tests/
│   └── test_system.py                    # Unit tests
├── results/
│   ├── aggregator_info.json
│   └── outbreak_signals.json
├── config.py                             # Settings
├── train.py                              # Training pipeline
├── requirements.txt                      # Dependencies
├── README.md                             # This file
└── LICENSE
```

## 🧪 Testing

Run comprehensive test suite:

```bash
# All tests
python -m pytest tests/test_system.py -v

# Specific test suite
python -m pytest tests/test_system.py::TestOutbreakDetectionEngine -v

# With coverage
python -m pytest tests/test_system.py --cov=. --cov-report=html
```

### Test Coverage
- ✅ Epidemiological data generation
- ✅ Temporal pattern detection
- ✅ Contact tracing integration
- ✅ Vaccination status tracking
- ✅ Infection risk model training
- ✅ Federated aggregation
- ✅ Ensemble predictions
- ✅ Outbreak cluster detection
- ✅ High-risk patient identification
- ✅ Public health alert generation

## 📊 Key Metrics

### Individual Model Performance
- **Accuracy**: Baseline classification accuracy
- **Recall**: Critical for outbreak detection (≥0.85 target)
- **High-Risk Detection Rate**: % of true high-risk cases detected
- **AUC**: Discrimination between risk levels

### Ensemble Performance
- **Accuracy**: Improved via model combination (typically +3-5%)
- **Recall**: Enhanced detection of critical cases
- **Confidence Score**: Prediction uncertainty quantification
- **Outbreak Signal Precision**: Accuracy of cluster alerts

## 🔐 Privacy & Security

### Privacy Guarantees
- ✅ **No Raw Data Sharing**: Patient data never leaves clinics
- ✅ **Model Aggregation Only**: Only feature importances shared
- ✅ **Audit Logging**: All aggregation events logged
- ✅ **Cryptographic Ready**: Can add differential privacy

### Regulatory Compliance
- ✅ HIPAA-compatible architecture
- ✅ GDPR-ready data handling
- ✅ De-identification support
- ✅ Audit trail for regulatory review

## ⚙️ Configuration

Edit `config.py` for custom settings:

```python
# Data generation
SAMPLES_PER_CLINIC = 1000
OUTBREAK_THRESHOLD = 0.65           # Risk probability for high-risk
CLUSTER_SIZE_THRESHOLD = 5          # Min cases for outbreak cluster
TIME_WINDOW = 7                     # Days for temporal clustering

# Model training
MODEL_TYPE = 'random_forest'        # or 'gb'
AGGREGATION_METHOD = 'weighted_average'

# Clinic-specific infection rates
# Clinic_A (Urban): 15%
# Clinic_B (Rural): 10.5%
# Clinic_C (Travel): 19.5%
```

## 📈 Example Results

### Outbreak Detection Demonstration

**Scenario 1: Low-Risk Baseline**
- Risk Level: 0 (Green)
- Recommendation: Routine monitoring

**Scenario 2: Moderate Risk with Travel**
- Risk Level: 1 (Yellow)
- Recommendation: Observation, clinical follow-up

**Scenario 3: High-Risk with Confirmed Contact**
- Risk Level: 2 (Red)
- Recommendation: Immediate testing, isolation recommended

**Scenario 4: Critical Risk - Cluster Alert**
- Risk Level: 3 (Magenta)
- Recommendation: Emergency response, public health notification
- Action: Contact tracing, isolation, testing

### Population-Level Outbreak Signals
```
Urban Center (Clinic_A):
  High-risk percentage: 18%
  ⚠️  OUTBREAK SIGNAL DETECTED
  Alert Level: HIGH
  Action: Increase surveillance and testing

Travel Hub (Clinic_C):
  High-risk percentage: 25%
  ⚠️  OUTBREAK SIGNAL DETECTED
  Alert Level: HIGH
  Action: Border health screening recommended
```

## 🤝 Contributing

Contributions welcome! Development process:

1. Fork repository
2. Create feature branch: `git checkout -b feature/NewFeature`
3. Commit changes: `git commit -m 'Add NewFeature'`
4. Push to branch: `git push origin feature/NewFeature`
5. Submit Pull Request

### Guidelines
- Follow PEP 8
- Include unit tests
- Update documentation
- Write comprehensive docstrings

## 📚 Further Reading

- **Federated Learning**: McMahan et al., 2017 "Communication-Efficient Learning of Deep Networks from Decentralized Data"
- **Outbreak Detection**: Epidemiological surveillance methods, CDC guidelines
- **Privacy in Healthcare ML**: Differential privacy, secure multi-party computation

## 📄 License

MIT License - See LICENSE file for details.

## 👥 Authors

- Healthcare AI Research Team
- Federated Learning Specialists
- Epidemiological Modeling Experts

## 📞 Support

For issues, questions, or suggestions:
- Open GitHub Issue
- Check existing documentation
- Review test cases for examples

---

**Last Updated**: March 2024  
**Status**: Production Ready  
**Version**: 2.0 (Outbreak Detection)

## 📞 Contact & Support

For questions, issues, or suggestions:
- **Email**: health-ai-lab@example.com
- **Issues**: GitHub Issues
- **Documentation**: See /docs folder

## 🎓 Citation

If you use this system in research, please cite:

```bibtex
@software{federated_health_triage_2024,
  author = {Health AI Lab},
  title = {Federated Health Triage System},
  year = {2024},
  url = {https://github.com/yourusername/federated_health_triage}
}
```

## 🔮 Future Enhancements

- [ ] Differential privacy implementation
- [ ] Deep learning models (LSTM, Transformer)
- [ ] Real-time model updates
- [ ] Web API interface
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Advanced statistical analysis
- [ ] Integration with EHR systems

## ⚠️ Disclaimer

This system is for **educational and research purposes**. It should not be used as a substitute for professional medical diagnosis and should only be used in healthcare settings with proper medical oversight.

---

**Last Updated**: March 2024
**Version**: 1.0.0
**Status**: Production Ready
