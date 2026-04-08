# 🤝 Ensemble Models & Federated Learning - Complete Guide

## Part 1: What is Federated Learning?

### Traditional Approach (CENTRALIZED)
```
All Clinics Send Patient Data
        ↓
    Central Server
        ↓
  Train One Model
        ↓
  Share Results
        
❌ Problems:
  - Privacy violation (raw data shared)
  - HIPAA risk
  - Data theft risk
  - Network bottleneck
```

### Federated Learning Approach (DISTRIBUTED)
```
Clinic A: Train locally
Clinic B: Train locally  
Clinic C: Train locally
        ↓
Share only WEIGHTS (not data!)
        ↓
   Aggregate Weights
        ↓
Better Combined Model
        
✅ Benefits:
  - Privacy preserved
  - HIPAA compliant
  - Data stays local
  - Faster aggregation
```

---

## Part 2: The Federated Learning Process (Step by Step)

### **STEP 1: Register Clinic Models**

**File:** `federated_learning/aggregator.py` (Lines 20-25)

```python
class FederatedOutbreakAggregator:
    def register_clinic(self, clinic_name: str, model: InfectionRiskDetectionModel):
        """Register a clinic's infection risk detection model"""
        self.clinic_models[clinic_name] = model
        print(f"Registered {model.clinic_name} ({model.clinic_type})")
```

**How it's called in train.py:**
```python
def train_clinic_infection_models(self):
    for clinic_key, clinic_info in CLINICS.items():
        # Train clinic model
        model = InfectionRiskDetectionModel(...)
        model.train(X_train, y_train, X_val, y_val)
        
        # Register with aggregator
        self.aggregator.register_clinic(clinic_info['name'], model)
        #                              ↑
        #                     Adds to federation!
```

**Result:**
```
Aggregator now has:
├─ clinic_models['Urban Center Clinic'] = Model_A
├─ clinic_models['Rural Area Clinic'] = Model_B
└─ clinic_models['Travel Hub Clinic'] = Model_C
```

---

### **STEP 2: Extract Feature Importances**

**File:** `federated_learning/aggregator.py` (Lines 31-53)

```python
def aggregate_models(self, clinic_sizes: Dict[str, int]):
    """
    Aggregate feature importances from clinic models
    This is the FEDERATED LEARNING step!
    """
    
    # Extract feature importances from all models
    all_importances = {}
    
    for clinic_name, model in self.clinic_models.items():
        # Get importance of each feature from that clinic's model
        importances = model.get_feature_importance([])
        #           ↓
        # Example: [('age', 0.25), ('fever', 0.18), ('vaccination', 0.15), ...]
        
        if importances:
            all_importances[clinic_name] = importances
```

**What are feature importances?**
```
RandomForest learns which features are most important:

Model_A (Urban):
  ├─ age: 0.25 (25% importance)
  ├─ fever: 0.18 (18% importance)
  ├─ vaccination: 0.15 (15% importance)
  └─ ...

Model_B (Rural):
  ├─ age: 0.22 (different importance!)
  ├─ fever: 0.20
  ├─ vaccination: 0.12
  └─ ...

Model_C (Travel Hub):
  ├─ age: 0.28
  ├─ fever: 0.15
  ├─ vaccination: 0.18
  └─ ...

These are MODEL WEIGHTS (no patient data!)
```

---

### **STEP 3: Aggregate (Combine) the Weights**

**File:** `federated_learning/aggregator.py` (Lines 54-65)

```python
# Choose aggregation method
if self.aggregation_method == 'weighted_average':
    aggregated = self._weighted_average_aggregation(all_importances, clinic_sizes)
elif self.aggregation_method == 'median':
    aggregated = self._median_aggregation(all_importances)
else:
    aggregated = self._simple_average_aggregation(all_importances)
```

#### **Method 1: Weighted Average (Default)**

```python
def _weighted_average_aggregation(self, all_importances, clinic_sizes):
    """Weighted by clinic size (more patients = more influence)"""
    
    total_size = sum(clinic_sizes.values())
    # total_size = 500 (A) + 500 (B) + 500 (C) = 1500
    
    aggregated = None
    
    for clinic_name, importances in all_importances.items():
        importance_values = np.array([imp[1] for imp in importances])
        
        # Weight by clinic size
        weight = clinic_sizes.get(clinic_name, 1) / total_size
        # Urban: 500/1500 = 0.33
        # Rural: 500/1500 = 0.33
        # Travel: 500/1500 = 0.33
        
        weighted = importance_values * weight
        
        if aggregated is None:
            aggregated = weighted
        else:
            aggregated += weighted  # Add to running total
    
    return aggregated
```

**Example with numbers:**
```
Feature: "Age"

Urban importance:   0.25 × 0.33 = 0.0825
Rural importance:   0.22 × 0.33 = 0.0726
Travel importance:  0.28 × 0.33 = 0.0924
                    ───────────────────
AGGREGATED:         0.25 (average from all 3!)

Same patient size → Simply average
Different patient size → Weight by size
```

#### **Method 2: Simple Average**

```python
def _simple_average_aggregation(self, all_importances):
    """Simple average (all clinics weighted equally)"""
    
    aggregated = None
    count = 0
    
    for clinic_name, importances in all_importances.items():
        importance_values = np.array([imp[1] for imp in importances])
        
        if aggregated is None:
            aggregated = importance_values
        else:
            aggregated += importance_values
        count += 1
    
    return aggregated / count  # Divide by number of clinics
```

#### **Method 3: Median (Robust)**

```python
def _median_aggregation(self, all_importances):
    """Median aggregation (resists outliers)"""
    
    all_importance_arrays = []
    
    for clinic_name, importances in all_importances.items():
        importance_values = np.array([imp[1] for imp in importances])
        all_importance_arrays.append(importance_values)
    
    stacked = np.array(all_importance_arrays)
    return np.median(stacked, axis=0)  # Middle value across clinics
```

**Visual:**
```
Urban:   [0.25, 0.18, 0.15, 0.10, ...]
Rural:   [0.22, 0.20, 0.12, 0.08, ...]  → median of each position
Travel:  [0.28, 0.15, 0.18, 0.12, ...]

Median:  [0.25, 0.18, 0.15, 0.10, ...]
         (middle value for each feature)
```

---

### **STEP 4: Store Aggregated Weights**

```python
self.aggregated_weights = aggregated
self.training_rounds += 1
self.round_history.append(aggregated.copy())

print(f"Federated Aggregation Complete:")
print(f"  Clinics aggregated: {len(self.clinic_models)}")  # 3
print(f"  Population size: {total_size}")  # 1500
```

---

## Part 3: How Ensemble Models Are Created

### **What is an Ensemble?**

```
Ensemble = Multiple models working together

Instead of:  "What does Model_A say?"
             
Use:         "What do Model_A, B, and C all say?"
             "Let them VOTE on the answer!"
```

---

### **Creating the Ensemble**

**File:** `federated_learning/aggregator.py` (Lines 145-160)

```python
class ConsolidatedOutbreakDetectionModel:
    """
    Consolidated ensemble model combining predictions from all clinics
    Uses soft voting (probability averaging)
    """
    
    def __init__(self, clinic_models: Dict[str, InfectionRiskDetectionModel], 
                 aggregation_weights=None):
        self.clinic_models = clinic_models  # All 3 models!
        self.aggregation_weights = aggregation_weights
        self.ensemble_auc = None
```

**Called in train.py:**
```python
def create_consolidated_outbreak_model(self):
    """Create ensemble from all clinic models"""
    
    consolidated = ConsolidatedOutbreakDetectionModel(
        clinic_models=self.clinic_models,
        # This dict contains:
        # {
        #   'Urban Center Clinic': Model_A,
        #   'Rural Area Clinic': Model_B,
        #   'Travel Hub Clinic': Model_C
        # }
        aggregation_weights=self.aggregator.aggregated_weights
    )
    
    return consolidated
```

---

### **How Ensemble Makes Predictions**

**File:** `federated_learning/aggregator.py` (Lines 162-197)

```python
def predict_ensemble(self, X):
    """
    Ensemble predictions using SOFT VOTING
    (Average probabilities from all clinics)
    """
    
    n_classes = 4  # Risk levels 0-3
    all_predictions = {}
    
    # Step 1: Get predictions from ALL clinics
    for clinic_name, model in self.clinic_models.items():
        proba = model.predict_proba(X)  # Get probabilities (not just class)
        
        # Ensure all models output 4 classes
        if proba.shape[1] < n_classes:
            padded_proba = np.zeros((proba.shape[0], n_classes))
            padded_proba[:, :proba.shape[1]] = proba
            padded_proba /= padded_proba.sum(axis=1, keepdims=True)
            proba = padded_proba
        
        all_predictions[clinic_name] = proba
```

**Visual: Getting Probabilities**

```
Patient: 65 year old, unvaccinated, fever

Model_A (Urban) says:
  Risk 0 (Low):     0.05 (5% chance)
  Risk 1 (Moderate): 0.10 (10% chance)
  Risk 2 (High):    0.60 (60% chance) ← Highest!
  Risk 3 (Critical): 0.25 (25% chance)
  Prediction: Risk 2 (HIGH)

Model_B (Rural) says:
  Risk 0 (Low):     0.15 (15% chance)
  Risk 1 (Moderate): 0.40 (40% chance) ← Highest!
  Risk 2 (High):    0.30 (30% chance)
  Risk 3 (Critical): 0.15 (15% chance)
  Prediction: Risk 1 (MODERATE)

Model_C (Travel) says:
  Risk 0 (Low):     0.08 (8% chance)
  Risk 1 (Moderate): 0.12 (12% chance)
  Risk 2 (High):    0.55 (55% chance) ← Highest!
  Risk 3 (Critical): 0.25 (25% chance)
  Prediction: Risk 2 (HIGH)
```

**Step 2: Average the Probabilities (Soft Voting)**

```python
# Average probability predictions
avg_proba = None
for clinic_name, proba in all_predictions.items():
    if avg_proba is None:
        avg_proba = proba.copy()
    else:
        avg_proba += proba  # Add probabilities

avg_proba /= len(all_predictions)  # Divide by number of clinics (3)
```

**Calculation:**
```
Risk 0: (0.05 + 0.15 + 0.08) / 3 = 0.09 (9%)
Risk 1: (0.10 + 0.40 + 0.12) / 3 = 0.21 (21%)
Risk 2: (0.60 + 0.30 + 0.55) / 3 = 0.48 (48%) ← Highest!
Risk 3: (0.25 + 0.15 + 0.25) / 3 = 0.22 (22%)

ENSEMBLE PREDICTION: Risk 2 (HIGH) with 48% confidence
```

**Step 3: Get Final Prediction**

```python
ensemble_predictions = np.argmax(avg_proba, axis=1)
# argmax finds the highest probability
# Risk 2 (0.48) is highest → argmax = 2

ensemble_confidence = np.max(avg_proba, axis=1)
# Maximum probability = 0.48 (48% confidence)

return ensemble_predictions, avg_proba, ensemble_confidence
```

---

## Part 4: Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│         FEDERATED LEARNING + ENSEMBLE WORKFLOW              │
└─────────────────────────────────────────────────────────────┘

PHASE 1: LOCAL TRAINING
┌───────────┐         ┌───────────┐         ┌───────────┐
│ Clinic A  │         │ Clinic B  │         │ Clinic C  │
│ 500 urban │         │ 500 rural │         │ 500 travel│
├───────────┤         ├───────────┤         ├───────────┤
│ Train     │         │ Train     │         │ Train     │
│ Model_A   │         │ Model_B   │         │ Model_C   │
└─────┬─────┘         └─────┬─────┘         └─────┬─────┘
      │                     │                     │
      └─────────────────────┼─────────────────────┘
                            │
PHASE 2: FEDERATED AGGREGATION
                            ↓
              Register models with aggregator
              ├─ aggregator.register_clinic('Urban', Model_A)
              ├─ aggregator.register_clinic('Rural', Model_B)
              └─ aggregator.register_clinic('Travel', Model_C)
                            ↓
              Extract feature importances
              ├─ Model_A importances: [0.25, 0.18, ...]
              ├─ Model_B importances: [0.22, 0.20, ...]
              └─ Model_C importances: [0.28, 0.15, ...]
                            ↓
              Aggregate weights (weighted average)
              └─ Aggregated: [0.25, 0.18, ...] (averaged!)
                            
PHASE 3: ENSEMBLE CREATION
                            ↓
              ConsolidatedOutbreakDetectionModel(
                  clinic_models={
                      'Urban': Model_A,
                      'Rural': Model_B,
                      'Travel': Model_C
                  }
              )
                            ↓
PHASE 4: ENSEMBLE PREDICTION (When user submits patient)
                            ↓
              Input: Patient data
                    ├─ Age: 65
                    ├─ Fever: Yes
                    ├─ Vaccination: No
                    └─ ...
                            ↓
              Model_A.predict_proba(X) → [0.05, 0.10, 0.60, 0.25]
              Model_B.predict_proba(X) → [0.15, 0.40, 0.30, 0.15]
              Model_C.predict_proba(X) → [0.08, 0.12, 0.55, 0.25]
                            ↓
              Average Probabilities (SOFT VOTING)
              [0.09, 0.21, 0.48, 0.22]
                            ↓
              argmax([0.09, 0.21, 0.48, 0.22]) = 2
              max([0.09, 0.21, 0.48, 0.22]) = 0.48
                            ↓
              ENSEMBLE OUTPUT:
              ├─ Risk Level: 2 (HIGH)
              ├─ Confidence: 48%
              └─ Consensus: 2 out of 3 models said HIGH!
```

---

## Part 5: Key Code Locations

### **Federated Learning Files**

| Component | File | Purpose |
|-----------|------|---------|
| **Aggregator Class** | `federated_learning/aggregator.py` (Lines 1-50) | Manages federated aggregation |
| **Register Clinics** | `federated_learning/aggregator.py` (Lines 20-25) | Register clinic models |
| **Aggregate Models** | `federated_learning/aggregator.py` (Lines 27-65) | Federated learning aggregation |
| **Weighted Average** | `federated_learning/aggregator.py` (Lines 67-87) | Weight by clinic size |
| **Simple Average** | `federated_learning/aggregator.py` (Lines 89-105) | Equal weighting |
| **Median Aggregation** | `federated_learning/aggregator.py` (Lines 107-119) | Robust aggregation |

### **Ensemble Files**

| Component | File | Purpose |
|-----------|------|---------|
| **Ensemble Class** | `federated_learning/aggregator.py` (Lines 145-160) | Ensemble model container |
| **Ensemble Predict** | `federated_learning/aggregator.py` (Lines 162-197) | Soft voting prediction |
| **Evaluate** | `federated_learning/aggregator.py` (Lines 199-234) | Measure performance |
| **Compare** | `federated_learning/aggregator.py` (Lines 236-270) | Individual vs ensemble |

### **Training Integration**

| Step | File | Function |
|------|------|----------|
| **Step 1: Register** | `train.py` | `train_clinic_infection_models()` (Lines 115-148) |
| **Step 2: Aggregate** | `train.py` | `aggregate_models_federated()` (Lines 150-170) |
| **Step 3: Create Ensemble** | `train.py` | `create_consolidated_outbreak_model()` (Lines 172-190) |
| **Step 4: Evaluate** | `train.py` | `evaluate_infection_models()` (Lines 192-220) |

---

## Part 6: Privacy Preservation

### **What Data is Shared?**

```
Traditional (BAD):
Clinic A sends → [Patient 1: age 65, symptoms..., address...]
Clinic B sends → [Patient 2: age 42, symptoms..., address...]
Clinic C sends → [Patient 3: age 58, symptoms..., address...]

❌ Complete patient data exposed!

Federated (GOOD):
Clinic A sends → [Weight: 0.25, Weight: 0.18, ...]
Clinic B sends → [Weight: 0.22, Weight: 0.20, ...]
Clinic C sends → [Weight: 0.28, Weight: 0.15, ...]

✅ Only model weights (numbers)!
✅ No patient information!
```

### **Why This is Secure**

```
Model weights are just numbers:
[0.25, 0.18, 0.15, 0.10, 0.08, 0.07, ...]

Cannot reverse-engineer to get:
├─ Patient names
├─ Ages
├─ Symptoms
├─ Medical history
├─ Addresses
└─ Any personal information
```

---

## Part 7: How Streamlit Uses It All

### **Dashboard Page**
```python
# Uses ENSEMBLE to show aggregated metrics
ensemble = load_ensemble()
all_data = load_all_clinic_data()
predictions = ensemble.predict_ensemble(all_data)
high_risk = (predictions >= 2).sum()
st.metric("High Risk Cases", high_risk)  # 1248 (from ensemble!)
```

### **Patient Assessment Page**
```python
# Uses ENSEMBLE voting
patient_data = get_user_input()
predictions, proba, confidence = ensemble.predict_ensemble([patient_data])
risk_level = predictions[0]  # 0-3
st.write(f"Risk Level: {RISK_NAMES[risk_level]}")
st.write(f"Confidence: {confidence[0]:.1%}")
# 2 votes for HIGH, 1 for MODERATE → HIGH wins!
```

### **Model Performance Page**
```python
# Compares all 3 models + ensemble
for clinic_name, model in models.items():
    acc = model.score(X_test, y_test)
    st.bar_chart({clinic_name: acc})

ensemble_acc = ensemble.evaluate_ensemble(X_test, y_test)['accuracy']
st.bar_chart({"Ensemble": ensemble_acc})
# Shows ensemble often beats individual models!
```

---

## Summary

```
FEDERATED LEARNING:
└─ Train locally on clinic data
└─ Extract model weights
└─ Aggregate weights (average them)
└─ Create better combined model
└─ Privacy preserved! (no data shared)

ENSEMBLE MODELS:
└─ Bundle all 3 clinic models together
└─ For each prediction: ask all 3 models
└─ Get probability from each
└─ Average the probabilities (soft voting)
└─ Consensus wins!

RESULT:
└─ More accurate than any single model
└─ Better outbreak detection
└─ Privacy-preserving
└─ No patient data leaked!
```

---

