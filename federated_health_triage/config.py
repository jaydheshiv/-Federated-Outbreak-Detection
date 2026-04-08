"""
Configuration for Federated Learning - Infectious Disease Outbreak Detection
Three distributed clinics: Urban Center (A), Rural Area (B), Travel Hub (C)
"""

# Disease Symptoms (COVID-like respiratory illness focus)
SYMPTOMS = [
    'fever', 'cough', 'shortness_of_breath', 'sore_throat', 'headache',
    'fatigue', 'body_ache', 'nausea', 'loss_of_taste', 'loss_of_smell'
]

# Infection Risk Levels (replacing generic triage)
INFECTION_RISK_LEVELS = {
    0: 'Low Risk - No indicators',
    1: 'Moderate Risk - Monitor closely', 
    2: 'High Risk - Early detection needed',
    3: 'Critical Risk - Immediate isolation + Testing'
}

# Clinical Severity Scores
SEVERITY_SCORES = {
    'mild': 0,
    'moderate': 1,
    'severe': 2,
    'critical': 3
}

# Age Groups (for epidemiological analysis)
AGE_GROUPS = {
    'child': (0, 12),
    'adolescent': (13, 19),
    'adult': (20, 59),
    'senior': (60, 150)
}

# Clinic Locations & Characteristics
CLINICS = {
    'Clinic_A': {
        'name': 'Urban Center Clinic',
        'location_type': 'urban',
        'patient_volume': 500,
        'travel_exposure': 0.3,  # Moderate exposure
        'description': 'High-density urban area, moderate patient flow'
    },
    'Clinic_B': {
        'name': 'Rural Area Clinic',
        'location_type': 'rural',
        'patient_volume': 500,
        'travel_exposure': 0.1,  # Low exposure
        'description': 'Isolated rural region, low travel patterns'
    },
    'Clinic_C': {
        'name': 'Travel Hub Clinic',
        'location_type': 'transit_hub',
        'patient_volume': 500,
        'travel_exposure': 0.8,  # High exposure (bus/rail station)
        'description': 'Near transportation hub, high exposure to travelers'
    }
}

CLINIC_NAMES = list(CLINICS.keys())
SAMPLES_PER_CLINIC = 500
# Disease Transmission Factors
TRANSMISSION_RISK = {
    'none': 0,
    'low': 1,
    'medium': 2,
    'high': 3
}

# Vaccination Status
VACCINATION_STATUS = {
    'unvaccinated': 0,
    'partially': 1,
    'fully_vaccinated': 2,
    'boosted': 3
}

# Epidemiological Proximity (contact with confirmed cases)
PROXIMITY_RISK = {
    'no_contact': 0,
    'indirect_contact': 1,
    'direct_contact': 2,
    'high_risk_contact': 3
}

# Travel History (recent travel patterns)
TRAVEL_HISTORY = {
    'no_travel': 0,
    'local_travel': 1,
    'regional_travel': 2,
    'international_travel': 3
}

# Model Configuration
MODEL_TYPE = 'random_forest'  # Options: 'random_forest', 'gb', 'neural_network'
RANDOM_SEED = 42
TEST_SIZE = 0.2
VAL_SIZE = 0.1

# Federated Learning Configuration
AGGREGATION_METHOD = 'weighted_average'  # Options: 'average', 'weighted_average', 'median'
ROUNDS = 5
LOCAL_EPOCHS = 5
LEARNING_RATE = 0.001

# Outbreak Detection Thresholds
OUTBREAK_THRESHOLD = 0.65  # Risk score threshold for outbreak alert
CLUSTER_SIZE_THRESHOLD = 5  # Minimum patients for outbreak cluster
TIME_WINDOW = 7  # Days for cluster analysis
SPATIAL_CORRELATION_THRESHOLD = 0.7

# Paths
DATA_DIR = 'data'
MODELS_DIR = 'models'
RESULTS_DIR = 'results'
ALERTS_DIR = 'alerts'

# Logging
ENABLE_LOGGING = True
LOG_LEVEL = 'INFO'

