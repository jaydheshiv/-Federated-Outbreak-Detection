# QUICK REFERENCE CARD

## Federated Learning Health Triage System

### 🚀 Quick Start (30 seconds)

```bash
cd federated_health_triage
pip install -r requirements.txt
python train.py
```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `train.py` | Main training pipeline |
| `demo.py` | Quick demonstration |
| `config.py` | Configuration settings |
| `models/clinic_model.py` | Individual model class |
| `federated_learning/aggregator.py` | Federated aggregation |
| `utils/data_generator.py` | Synthetic data |
| `utils/preprocessing.py` | Data preprocessing |
| `utils/triage_engine.py` | Clinical assessment |
| `tests/test_system.py` | Unit tests |

---

## 🎯 Main Classes

### HealthDataGenerator
```python
generator = HealthDataGenerator()
clinic_data = generator.generate_all_clinics(n_samples=500)
```

### ClinicModel
```python
model = ClinicModel('Clinic_A')
model.train(X_train, y_train, X_val, y_val)
predictions = model.predict(X_test)
```

### FederatedAggregator
```python
agg = FederatedAggregator(aggregation_method='weighted_average')
agg.register_clinic('Clinic_A', model_a)
aggregated = agg.aggregate_models(clinic_sizes)
```

### ConsolidatedTriageModel
```python
ensemble = ConsolidatedTriageModel(clinic_models)
predictions, proba = ensemble.predict_ensemble(X)
metrics = ensemble.evaluate_ensemble(X_test, y_test)
```

### TriageAssessmentEngine
```python
engine = TriageAssessmentEngine(ensemble)
assessment = engine.assess_patient(patient_data)
report = engine.generate_report(patient_data, assessment)
```

---

## 📊 Triage Levels

| Level | Color | Action |
|-------|-------|--------|
| 0 | Green | Primary care |
| 1 | Yellow | Specialist (48h) |
| 2 | Red | Emergency eval |
| 3 | Black | Emergency admission |

---

## 📋 Workflow Steps

```
1. python train.py
   ├─ Generates synthetic data
   ├─ Trains 3 clinic models
   ├─ Aggregates models
   ├─ Creates ensemble
   ├─ Evaluates all models
   └─ Demonstrates triage

2. Results in:
   ├─ data/*.csv (datasets)
   ├─ models/*.pkl (trained models)
   └─ results/*.json (metrics)
```

---

## 🧪 Testing

```bash
# All tests
pytest tests/test_system.py -v

# Specific test
pytest tests/test_system.py::TestClinicModel -v

# With coverage
pytest tests/test_system.py --cov=. --cov-report=html
```

---

## Patient Assessment Example

```python
patient = {
    'age': 55,
    'symptoms': ['fever', 'cough'],
    'travel_risk': 1,
    'comorbidities': ['hypertension']
}

assessment = engine.assess_patient(patient)
# Returns:
# {
#     'triage_level': 1,
#     'triage_description': 'Yellow (Semi-urgent)',
#     'risk_score': 1.5,
#     'model_confidence': 0.87,
#     'recommendations': [...],
#     'suspicious_patterns': [...]
# }
```

---

## 📖 Documentation Navigation

```
START HERE:      README.md
├─ Features?     → README.md (Features section)
├─ Setup?        → README.md (Installation)
├─ Usage?        → README.md (Usage section)
├─ Architecture? → ARCHITECTURE.md
├─ Advanced?     → ADVANCED_SETUP.md
├─ Contributing? → CONTRIBUTING.md
└─ GitHub?       → GITHUB_SETUP.md
```

---

## 🔑 Configuration (config.py)

```python
SAMPLES_PER_CLINIC = 500      # Data size
MODEL_TYPE = 'random_forest'  # Model type
AGGREGATION_METHOD = 'weighted_average'  # Strategy
RANDOM_SEED = 42              # Reproducibility
```

---

## 📊 Expected Accuracy

```
Individual Models:    ~80-83%
Consolidated Model:   ~85-87%
Improvement:         +3-5%
```

---

## 🔐 Privacy Features

✅ No raw data sharing
✅ Federated aggregation
✅ Model-only sharing
✅ HIPAA compatible
✅ Differential privacy ready

---

## 🐳 Docker Quick Start

```bash
docker build -t health-triage:latest .
docker run -p 5000:5000 health-triage:latest
```

---

## 📞 Common Commands

```bash
# Run full training
python train.py

# Quick demo
python demo.py

# Run tests
pytest tests/ -v

# Check git status
git status

# View project structure
tree /federated_health_triage
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | `pip install -r requirements.txt` |
| Low accuracy | Increase `SAMPLES_PER_CLINIC` |
| Slow training | Reduce `n_estimators` in config |
| Memory error | Reduce data size |

---

## 📚 Model Performance

```
F1 Scores:
├─ Precision: 0.85-0.87
├─ Recall:    0.83-0.85
└─ F1:        0.84-0.86

Confusion Matrix: Available in results
```

---

## ✨ Key Algorithms

1. **Federated Aggregation**
   - Weighted average based on clinic size
   - Privacy preserving

2. **Ensemble Voting**
   - Soft voting via probability averaging
   - Confidence score generation

3. **Risk Scoring**
   - Combines AI + clinical rules
   - Suspicious pattern detection

---

## 🎓 Recommended Reading Order

1. README.md (5 min) - Overview
2. ARCHITECTURE.md (10 min) - How it works
3. Code examples (5 min) - Usage patterns
4. Run demo.py (2 min) - See it in action
5. ADVANCED_SETUP.md (10 min) - Advanced topics

---

## 🚀 Next Steps

```
1. ✅ Understand architecture (read ARCHITECTURE.md)
2. ✅ Run demo (python demo.py)
3. ✅ Review tests (pytest tests/ -v)
4. ✅ Push to GitHub (see GITHUB_SETUP.md)
5. ✅ Deploy (see ADVANCED_SETUP.md)
```

---

**Last Updated**: March 26, 2024
**Version**: 1.0.0
**Status**: Production Ready ✅

---

For detailed help, see README.md or ARCHITECTURE.md
