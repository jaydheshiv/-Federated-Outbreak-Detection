# Federated Outbreak Detection System - Architecture Overview

## System Design: Early Risk Detection of Infectious Disease

### 1. Epidemiological Data Layer
```
┌─────────────────────────────────────────────────┐
│     Distributed Clinic Data Sources              │
├─────────────────────────────────────────────────┤
│ Clinic_A: Urban Center (1000 patients)           │
│   - Moderate travel exposure (0.3)               │
│   - Baseline infection rate: 15%                 │
│                                                  │
│ Clinic_B: Rural Area (1000 patients)             │
│   - Low travel exposure (0.1)                    │
│   - Baseline infection rate: 10.5%               │
│                                                  │
│ Clinic_C: Travel Hub (1000 patients)             │
│   - High travel exposure (0.8)                   │
│   - Baseline infection rate: 19.5%               │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────▼──────────────┐
        │ Epidemiological Data  │
        │ Generator             │
        │ (temporal, contact    │
        │  tracing, vacc.)      │
        └────────┬──────────────┘
                 │
        ┌────────▼──────────────────────┐
        │   Feature Engineering          │
        │   - Temporal patterns          │
        │   - Outbreak clusters          │
        │   - Days symptomatic tracking   │
        └────────┬──────────────────────┘
                 │
        ┌────────▼──────────────────────┐
        │   Preprocessing                │
        │   - Scaling                    │
        │   - Categorical encoding       │
        │   - Date handling              │
        └────────┬──────────────────────┘
                 │
        ┌────────▼──────────────┐
        │   Train/Test Split   │
        │   (80% / 20%)         │
        └────────┬──────────────┘
```

### 2. Federated Model Training Layer
```
┌──────────────────────────────────────────────────┐
│    Local Infection Risk Detection Models         │
│     (Privacy-Preserving Training)                │
├──────────────────────────────────────────────────┤
│                                                  │
│ ┌─────────────────────────────────────────────┐ │
│ │        CLINIC_A (Urban Center)              │ │
│ │                                             │ │
│ │ Local Data (1000 patients)                  │ │
│ │    ↓                                        │ │
│ │ Train InfectionRiskDetectionModel          │ │
│ │    ↓                                        │ │
│ │ Feature Importances Extracted              │ │
│ │    ↓                                        │ │
│ │ Metrics: Accuracy, Recall, AUC, etc.      │ │
│ └──────────────┬────────────────────────────┘ │
│                │                              │
│                │ (NO DATA SHARED)            │
│                │ (MODELS ONLY)               │
│                │                              │
│ ┌──────────────▼────────────────────────────┐ │
│ │        CLINIC_B (Rural Area)              │ │
│ │                                           │ │
│ │ Local Data (1000 patients)                │ │
│ │    ↓                                      │ │
│ │ Train InfectionRiskDetectionModel        │ │
│ │    ↓                                      │ │
│ │ Feature Importances Extracted             │ │
│ └──────────────┬────────────────────────────┘ │
│                │                              │
│ ┌──────────────▼────────────────────────────┐ │
│ │        CLINIC_C (Travel Hub)              │ │
│ │                                           │ │
│ │ Local Data (1000 patients)                │ │
│ │    ↓                                      │ │
│ │ Train InfectionRiskDetectionModel        │ │
│ │    ↓                                      │ │
│ │ Feature Importances Extracted             │ │
│ └──────────────┬────────────────────────────┘ │
│                                               │
│                │                             │
│                └──────────────┬───────────────│
│                               │               │
│                      Feature Importances     │
│                      (Aggregated, No Data)   │
│                               │               │
│                        ┌──────▼──────────┐   │
│                        │ Aggregator      │   │
│                        │ (Federated)     │   │
│                        │ Weighted Avg    │   │
│                        └──────┬──────────┘   │
│                               │              │
│                    Aggregated Weights       │
│                               │              │
│                        ┌──────▼──────────┐   │
│                        │ Consolidated    │   │
│                        │ Ensemble Model  │   │
│                        │ (All Clinics)   │   │
│                        └──────┬──────────┘   │
│                               │              │
└───────────────────────────────┼──────────────┘
```

### 3. Outbreak Detection Inference Layer
```
┌──────────────────────────────────────────────┐
│     Outbreak Detection Engine                  │
│     (Population-Level Surveillance)            │
├──────────────────────────────────────────────┤
│                                              │
│ Individual Patient Assessment                 │
│                                              │
│  Input Patient Data:                         │
│  ├─ Demographics (age, age_group)            │
│  ├─ Clinical Symptoms                        │
│  │  ├─ fever, cough, respiratory_distress   │
│  │  └─ loss_of_taste_smell (KEY INDICATOR)  │
│  ├─ Epidemiological Factors                  │
│  │  ├─ Vaccination Status (0-3)             │
│  │  ├─ Proximity to Confirmed (0-2)         │
│  │  ├─ Travel History (0-3)                 │
│  │  └─ Days Symptomatic                     │
│  └─ Host Factors                             │
│     └─ Comorbidities (immunocompromised)    │
│           │                                 │
│           ├──────────┬────────────┐         │
│           │          │            │         │
│           ▼          ▼            ▼         │
│      ┌─────────┐ ┌────────────┐ ┌──────┐  │
│      │Epi Risk │ │   Model    │ │Risk  │  │
│      │Scoring  │ │ Prediction │ │Score │  │
│      │(0-4)    │ │ (0-3)      │ │Rules │  │
│      └────┬────┘ └──────┬─────┘ └──┬───┘  │
│           │             │           │     │
│           └─────────────┼───────────┘     │
│                         │                 │
│                    ┌────▼─────────┐      │
│                    │  Ensemble    │      │
│                    │  Prediction  │      │
│                    │  50% + 50%   │      │
│                    └────┬─────────┘      │
│                         │                 │
│                    ┌────▼──────────────┐ │
│                    │ Infection Risk    │ │
│                    │ Level (0-3)       │ │
│                    │ ├─ 0: Low         │ │
│                    │ ├─ 1: Moderate    │ │
│                    │ ├─ 2: High        │ │
│                    │ └─ 3: Critical    │ │
│                    └────┬──────────────┘ │
│                         │                 │
│                    ┌────▼──────────────┐ │
│                    │ Risk Factors      │ │
│                    │ Explanation       │ │
│                    └────┬──────────────┘ │
│                         │                 │
│                    ┌────▼──────────────┐ │
│                    │ Clinical Report   │ │
│                    │ & Recommendations │ │
│                    │ - Testing         │ │
│                    │ - Isolation       │ │
│                    │ - Contact Tracing │ │
│                    └───────────────────┘ │
│                                          │
│ Outbreak Cluster Detection                │
│                                          │
│  Monitor High-Risk Cases per Clinic:     │
│                                          │
│  Count high-risk patients (Level 2-3)   │
│  In temporal window (7 days)             │
│           │                             │
│           ├─ < 5 cases: Monitor         │
│           ├─ 5-9 cases: MODERATE alert  │
│           └─ ≥ 10 cases: HIGH alert     │
│                │                        │
│           ┌────▼────────┐              │
│           │ Public Health             │
│           │ Notification              │
│           └───────────────┘            │
└──────────────────────────────────────────┘
```

## Data Flow: From Patient Presentation to Outbreak Alert

```
Multiple Patients Present
├─ Clinic_A patients (Urban)
├─ Clinic_B patients (Rural)
└─ Clinic_C patients (Travel Hub)

                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼

LOCAL Processing (Each Clinic Independent)
├─ Clinic_A:
│  ├─ Extract epidemiological features
│  ├─ Run through local infection risk model
│  ├─ Calculate epidemiological risk score
│  ├─ Assess individual patient (Risk 0-3)
│  └─ Log high-risk cases
│
├─ Clinic_B:
│  ├─ Extract epidemiological features
│  ├─ Run through local infection risk model
│  ├─ Calculate epidemiological risk score
│  ├─ Assess individual patient (Risk 0-3)
│  └─ Log high-risk cases
│
└─ Clinic_C:
   ├─ Extract epidemiological features
   ├─ Run through local infection risk model
   ├─ Calculate epidemiological risk score
   ├─ Assess individual patient (Risk 0-3)
   └─ Log high-risk cases

                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼

AGGREGATED Processing (No Patient Data)
├─ Aggregate model outputs
├─ Count high-risk patients per clinic
├─ Detect temporal clusters (7-day window)
├─ Analyze geographic patterns
└─ Generate outbreak signals

                │
    ┌───────────▼───────────┐
    
POPULATION ALERTS
├─ Clinic_A: 18% high-risk ──→ OUTBREAK SIGNAL
├─ Clinic_B: 10% high-risk ──→ Monitor
└─ Clinic_C: 25% high-risk ──→ OUTBREAK SIGNAL + 
                               Contact Tracing Alert +
                               Travel Hub Alert

                │
    ┌───────────▼───────────┐
    
PUBLIC HEALTH ACTION
├─ Increase testing at alert clinics
├─ Deploy contact tracing teams
├─ Border health screening (if travel hub)
└─ Activate outbreak response protocol
```

## Class Hierarchy: Outbreak Detection Components

```
EpidemiologicalDataGenerator
├─ generate_clinic_data(clinic_name, n_samples)
├─ generate_all_clinics(n_samples)
├─ _generate_infection_risk_labels()
├─ _identify_outbreak_clusters()
└─ save_clinic_data()

EpidemiologicalDataProcessor
├─ preprocess_data()
├─ split_data()
├─ get_feature_names()
└─ get_metadata()

InfectionRiskDetectionModel
├─ __init__(clinic_name, clinic_type)
├─ train(X_train, y_train, X_val, y_val)
├─ predict(X)
├─ predict_proba(X)
├─ evaluate(X_test, y_test)
├─ get_feature_importance()
├─ get_high_risk_features()
└─ save_model()

FederatedOutbreakAggregator
├─ register_clinic(clinic_name, model)
├─ aggregate_models(clinic_sizes)
├─ _weighted_average_aggregation()
├─ _simple_average_aggregation()
├─ _median_aggregation()
├─ detect_outbreak_signals(high_risk_pcts, threshold)
├─ get_aggregated_model_info()
└─ get_round_history()

ConsolidatedOutbreakDetectionModel
├─ predict_ensemble(X)
├─ evaluate_ensemble(X_test, y_test)
├─ compare_individual_vs_ensemble()
└─ ensemble_auc

OutbreakDetectionEngine
├─ assess_patient(patient_features)
├─ _calculate_epidemiological_risk()
├─ _identify_risk_factors()
├─ detect_cluster_outbreak()
├─ generate_assessment_report()
└─ risk_weights dict

FederatedOutbreakDetectionSystem
├─ generate_epidemiological_data()
├─ train_clinic_infection_models()
├─ aggregate_models_federated()
├─ create_consolidated_outbreak_model()
├─ evaluate_infection_models()
├─ create_outbreak_detection_engine()
├─ demo_outbreak_scenarios()
├─ detect_population_level_outbreaks()
├─ save_results()
└─ run_full_pipeline()
```

## Algorithm: Epidemiological Risk Scoring

```
Input: Patient features
       contact_tracing (0-2)
       vaccination_status (0-3)
       travel_history (0-3)
       age, symptoms, comorbidities

Process:
1. Calculate contact tracing risk
   contact_risk = proximity_to_confirmed × 0.7
   
2. Calculate vaccination protection
   vaccination_risk = (3 - vaccination_status) × 0.4 / 3
   
3. Calculate travel exposure
   travel_risk = travel_history × 0.3 / 3
   
4. Age risk factor
   if age < 20: age_risk = 0.1
   if 20 ≤ age < 40: age_risk = 0.3
   if 40 ≤ age < 65: age_risk = 0.7
   if age ≥ 65: age_risk = 1.0
   
5. Symptom severity
   symptom_risk = sum of indicator weights:
     - fever: 0.3
     - cough: 0.3
     - shortness_of_breath: 0.5
     - loss_of_taste_smell: 0.8  (KEY)
     - respiratory_distress: 1.0 (CRITICAL)
   symptom_risk = min(symptom_risk, 1.0)
   
6. Comorbidity risk
   if comorbidities: comorbidity_risk = 0.5
   else: comorbidity_risk = 0
   
7. Normalize epidemiological risk
   raw_risk = (contact_risk + vaccination_risk + travel_risk + 
               age_risk + symptom_risk + comorbidity_risk)
   epi_risk = raw_risk / 4.0  (normalize to 0-1)

Output: epidemiological_risk (0-4 scale)
```

## Algorithm: Outbreak Cluster Detection

```
Input: High-risk patients (Level 2-3) per clinic
       Temporal data (dates)
       Time window = 7 days

Process:
1. For each clinic:
   
2. Find temporal clusters
   For each patient presentation date:
      count = sum of high-risk cases in ±3.5 day window
      
3. Identify clusters
   if count ≥ 5:
      CLUSTER_DETECTED = TRUE
      alert_level = MODERATE (5-9) or HIGH (≥10)
      
4. Generate alert
   if CLUSTER_DETECTED:
      ├─ Clinic name
      ├─ Alert level
      ├─ Number of high-risk cases
      ├─ Time window
      └─ Recommended actions

Output: Outbreak signals with public health recommendations
```

## Algorithm: Federated Aggregation

```
Input: Models from clinics A, B, C
       Data sizes: size_A, size_B, size_C

Process:
1. Extract feature importances
   importance_A = model_A.feature_importances_
   importance_B = model_B.feature_importances_
   importance_C = model_C.feature_importances_

2. Calculate clinic weights (by data size)
   total_size = size_A + size_B + size_C
   weight_A = size_A / total_size
   weight_B = size_B / total_size
   weight_C = size_C / total_size

3. Compute weighted average
   aggregated = (weight_A × importance_A +
                 weight_B × importance_B +
                 weight_C × importance_C)

Output: aggregated_importances (population-level insights)
        No patient data was shared
```

## Algorithm: Ensemble Infection Risk Prediction

```
Input: Patient features X
       Models: clinic_A_model, clinic_B_model, clinic_C_model

Process:
1. Get probability predictions from each clinic model
   proba_A = clinic_A_model.predict_proba(X)  [n_samples, 4]
   proba_B = clinic_B_model.predict_proba(X)  [n_samples, 4]
   proba_C = clinic_C_model.predict_proba(X)  [n_samples, 4]

2. Average probabilities (soft voting)
   avg_proba = (proba_A + proba_B + proba_C) / 3
   
3. Get predicted infection risk level
   prediction = argmax(avg_proba, axis=1)  [0-3]
   confidence = max(avg_proba, axis=1)     [0-1]

4. Combine with epidemiological risk
   combined_risk = 0.5 × prediction + 0.5 × epi_risk
   
5. Map to final risk level
   if combined_risk < 0.4: final_risk = 0
   if 0.4 ≤ combined_risk < 1.5: final_risk = 1
   if 1.5 ≤ combined_risk < 2.5: final_risk = 2
   if combined_risk ≥ 2.5: final_risk = 3

Output: infection_risk_level (0-3)
        confidence_score (0-1)
        epidemiological_risk (0-4)
```

## Performance Metrics Flow

```
Test Data (20% of 3000 total = 600 samples)
└─ 200 per clinic distributed by risk level

                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼

Clinic Models Predictions
├─ Clinic_A: predictions, probabilities
├─ Clinic_B: predictions, probabilities
└─ Clinic_C: predictions, probabilities

                │
    ┌───────────▼───────────┐
    
Ensemble Predictions
├─ Soft voting
├─ Confidence scores
└─ Outbreak cluster detection

                │
    ┌───────────▼───────────┐

Evaluation Metrics
├─ Accuracy: (TP+TN)/(Total)
├─ Precision: TP/(TP+FP)
├─ Recall: TP/(TP+FN)  ← CRITICAL for outbreak detection
├─ F1 Score: 2×(Precision×Recall)/(Precision+Recall)
├─ AUC: Area under ROC curve
└─ High-Risk Detection Rate: Detected High-Risk / Actual High-Risk
```

## Privacy & Security: Federated Architecture

```
PATIENT DATA (Never Centralized)
│
├─ Clinic_A ────────────┐
│  (Local Data Only)    │
│                       ├─→ [Train Locally]
├─ Clinic_B ────────────┤   └─→ [Extract Importances Only]
│  (Local Data Only)    │
│                       ├─→ [Train Locally]
├─ Clinic_C ────────────┤   └─→ [Extract Importances Only]
│  (Local Data Only)    │
│                       └─→ [Train Locally]
│                           └─→ [Extract Importances Only]

                        │
        AGGREGATION (No Patient Data)
        │
        ├─ Feature importances (numbers only)
        ├─ Model parameters (learned patterns)
        └─ Outbreak signals (statistical summaries)

                        │
        CONSOLIDATED INSIGHTS
        │
        ├─ Population-level infection trends
        ├─ Outbreak cluster detection
        ├─ Geographic risk patterns
        └─ Public health recommendations
        
Privacy Guarantees:
✓ No raw data centralization
✓ Only aggregated models shared
✓ No patient identifiers exposed
✓ Audit trail of all operations
✓ Ready for differential privacy enhancement
```

---

For implementation details and usage examples, refer to code documentation and README.md.
