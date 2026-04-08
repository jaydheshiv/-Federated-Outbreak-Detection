# ADVANCED SETUP & CUSTOMIZATION GUIDE

## Advanced Configuration

### Custom Model Parameters

Edit `config.py` to customize model behavior:

```python
# Clinic-specific configurations
CLINIC_CONFIGS = {
    'Clinic_A': {
        'patient_volume': 500,
        'age_bias': 45,
        'severity_bias': 0.5
    },
    'Clinic_B': {
        'patient_volume': 500,
        'age_bias': 35,
        'severity_bias': 0.7
    },
    'Clinic_C': {
        'patient_volume': 500,
        'age_bias': 55,
        'severity_bias': 0.3
    }
}

# Model hyperparameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42
}

GRADIENT_BOOSTING_PARAMS = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 7,
    'random_state': 42
}
```

### Custom Data Generation

Generate data with specific distributions:

```python
from utils.data_generator import HealthDataGenerator

generator = HealthDataGenerator(seed=42)

# Generate custom clinic data
df = generator.generate_clinic_data(
    clinic_name='Clinic_A',
    n_samples=1000
)

# Customize prevalence of specific conditions
# Modify _generate_labels() method in HealthDataGenerator class
```

### Implementing Custom Aggregation

Create custom aggregation strategy:

```python
from federated_learning.aggregator import FederatedAggregator

class CustomAggregator(FederatedAggregator):
    def aggregate_models(self, clinic_sizes):
        # Your custom aggregation logic
        custom_weights = self._custom_aggregation_method()
        return custom_weights
    
    def _custom_aggregation_method(self):
        # Implement your strategy
        pass
```

## Integration with Real Data

### Loading Real Patient Data

```python
import pandas as pd
from utils.preprocessing import prepare_clinic_data

# Load real clinic data
clinic_a_df = pd.read_csv('path/to/clinic_a_data.csv')

# Ensure columns match expected format:
# Required: age, gender, fever, cough, ..., travel_risk, triage_level
# Optional: clinic, patient_id, timestamp

# Preprocess and prepare
data_split = prepare_clinic_data(clinic_a_df)

# Train model on real data
from models.clinic_model import ClinicModel

model = ClinicModel('Clinic_A')
model.train(
    data_split['X_train'],
    data_split['y_train'],
    data_split['X_val'],
    data_split['y_val']
)
```

### Data Format Requirements

Your data must include:

```csv
age,gender,fever,cough,shortness_of_breath,...,travel_risk,has_hypertension,has_diabetes,has_respiratory_issues,triage_level
45,M,1,0,0,...,1,0,0,0,1
65,F,1,1,1,...,2,1,1,0,3
...
```

## Performance Optimization

### Speed Improvements

1. **Reduce n_estimators** in Random Forest:
```python
# In config.py
RANDOM_FOREST_PARAMS = {
    'n_estimators': 50,  # instead of 100
    ...
}
```

2. **Use Gradient Boosting** for faster training:
```python
MODEL_TYPE = 'gradient_boosting'
```

3. **Parallel processing**:
```python
# In ClinicModel
n_jobs=-1  # Use all available cores
```

### Memory Optimization

```python
# Reduce sample size
SAMPLES_PER_CLINIC = 300  # instead of 500

# Use stratified sampling for imbalanced classes
from sklearn.model_selection import train_test_split
train_test_split(..., stratify=y)
```

## Advanced Features

### Differential Privacy

Add differential privacy to federated aggregation:

```python
import numpy as np

def add_differential_privacy(aggregated_weights, epsilon=0.1):
    """Add Laplace noise for differential privacy"""
    noise = np.random.laplace(0, 1/epsilon, len(aggregated_weights))
    return aggregated_weights + noise
```

### Custom Triage Rules

Implement domain-specific rules:

```python
from utils.triage_engine import TriageAssessmentEngine

class CustomTriageEngine(TriageAssessmentEngine):
    def _apply_clinical_rules(self, patient_data):
        """Apply institution-specific triage rules"""
        if patient_data['age'] > 80 and len(patient_data['symptoms']) >= 2:
            return 2  # Escalate to urgent
        return super()._apply_clinical_rules(patient_data)
```

### Model Persistence

Save and load models:

```python
# Save
model.save_model(model_dir='models')

# Load
model.load_model(model_dir='models')

# Load entire ensemble
import joblib
ensemble_models = joblib.load('models/ensemble.pkl')
```

## Monitoring & Logging

### Setup Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/triage_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Model Monitoring

```python
# Track model drift
class ModelMonitor:
    def __init__(self, baseline_accuracy):
        self.baseline = baseline_accuracy
    
    def detect_drift(self, current_accuracy):
        drift = self.baseline - current_accuracy
        if drift > 0.05:  # 5% drop
            logger.warning(f"Model drift detected: {drift:.2%}")
            return True
        return False
```

## Database Integration

### SQLite Backend

```python
import sqlite3

class HealthDataDB:
    def __init__(self, db_path='health_data.db'):
        self.conn = sqlite3.connect(db_path)
    
    def save_assessment(self, patient_id, assessment):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO assessments 
            (patient_id, triage_level, timestamp)
            VALUES (?, ?, datetime('now'))
        ''', (patient_id, assessment['triage_level']))
        self.conn.commit()
```

### PostgreSQL Integration

```python
import psycopg2

def save_to_postgresql(assessment, db_config):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO triage_results 
        (patient_id, triage_level, risk_score, confidence)
        VALUES (%s, %s, %s, %s)
    ''', (assessment['patient_id'], ...))
    conn.commit()
```

## API Development

### REST API with Flask

```python
from flask import Flask, request, jsonify
from train import FederatedHealthTriageTrainer

app = Flask(__name__)

# Initialize model
trainer = FederatedHealthTriageTrainer()
trainer.run_full_pipeline()

@app.route('/api/triage', methods=['POST'])
def triage_assessment():
    patient_data = request.json
    assessment = trainer.triage_engine.assess_patient(patient_data)
    return jsonify(assessment)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

## Model Deployment

### Docker Containerization

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### AWS Deployment

```bash
# Build Docker image
docker build -t health-triage:latest .

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag health-triage:latest <account>.dkr.ecr.us-east-1.amazonaws.com/health-triage:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/health-triage:latest

# Deploy to ECS/Lambda
```

## Troubleshooting

### Issue: Memory Error

```python
# Reduce data size
SAMPLES_PER_CLINIC = 200

# Use data generators instead of loading all at once
# Implement batch processing
```

### Issue: Low Accuracy

```python
# Increase model complexity
MODEL_TYPE = 'gradient_boosting'
TREE_DEPTH = 20

# Increase training data
SAMPLES_PER_CLINIC = 1000

# Add feature engineering
```

### Issue: Slow Training

```python
# Use fewer estimators
'n_estimators': 50

# Enable GPU acceleration
# Reduce data size
# Use simpler models
```

---

For more help, see main README.md or contact support.
