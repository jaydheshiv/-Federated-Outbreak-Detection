"""
Epidemiological Data Generator for Infectious Disease Outbreak Detection
Generates realistic infectious disease patient data for three distributed clinics
with transmission patterns, outbreak clusters, and temporal dynamics
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from config import SYMPTOMS, INFECTION_RISK_LEVELS, CLINICS, SAMPLES_PER_CLINIC
import os


class EpidemiologicalDataGenerator:
    """Generates realistic epidemiological data for infectious disease detection"""
    
    def __init__(self, seed=42, start_date=None):
        self.seed = seed
        np.random.seed(seed)
        self.scaler = StandardScaler()
        self.start_date = start_date or datetime(2024, 1, 1)
        
    def generate_clinic_data(self, clinic_name, n_samples=500, infection_rate=0.15):
        """
        Generate epidemiological data for a clinic
        Includes realistic disease transmission patterns and outbreak clusters
        """
        clinic_info = CLINICS[clinic_name]
        np.random.seed(self.seed + hash(clinic_name) % 100)
        
        data = {
            'clinic': [clinic_name] * n_samples,
            'clinic_type': [clinic_info['location_type']] * n_samples,
            'date': [self.start_date + timedelta(days=int(i/10)) for i in range(n_samples)],
            'age': np.clip(np.random.normal(45, 20, n_samples), 0, 100),
            'gender': np.random.choice(['M', 'F'], n_samples, p=[0.45, 0.55]),
        }
        
        # Vaccination status (affects severity)
        data['vaccination_status'] = np.random.choice([0, 1, 2, 3], n_samples, 
                                                       p=[0.15, 0.20, 0.40, 0.25])
        
        # Recent travel history (varies by clinic type)
        travel_probs = {
            'urban': [0.3, 0.4, 0.2, 0.1],
            'rural': [0.6, 0.25, 0.1, 0.05],
            'transit_hub': [0.1, 0.2, 0.3, 0.4]
        }
        travel_p = travel_probs[clinic_info['location_type']]
        data['travel_history'] = np.random.choice([0, 1, 2, 3], n_samples, p=travel_p)
        
        # Contact with confirmed cases (epidemiological risk)
        data['proximity_to_confirmed'] = np.random.choice([0, 1, 2, 3], n_samples, 
                                                           p=[0.6, 0.25, 0.10, 0.05])
        
        # Add symptoms with realistic correlations
        for symptom in SYMPTOMS:
            base_prevalence = np.random.uniform(0.05, 0.25)
            symptom_presence = np.random.random(n_samples) < base_prevalence
            data[symptom] = symptom_presence.astype(int)
        
        # Comorbidities (risk factors for severe disease)
        data['has_hypertension'] = (np.random.random(n_samples) < 0.15).astype(int)
        data['has_diabetes'] = (np.random.random(n_samples) < 0.08).astype(int)
        data['has_respiratory_issues'] = (np.random.random(n_samples) < 0.12).astype(int)
        data['immunocompromised'] = (np.random.random(n_samples) < 0.05).astype(int)
        
        # Symptom onset duration (days)
        data['days_symptomatic'] = np.random.poisson(lam=3, size=n_samples)
        
        # Create infection risk labels based on epidemiological factors
        data['infection_risk'] = self._generate_infection_risk_labels(data, clinic_info)
        
        # Create outbreak indicators (clustering)
        data['in_outbreak_cluster'] = self._identify_outbreak_clusters(data, clinic_name)
        
        df = pd.DataFrame(data)
        return df
    
    def _generate_infection_risk_labels(self, data, clinic_info):
        """
        Generate infection risk labels based on epidemiological features
        Level 0: Low Risk
        Level 1: Moderate Risk
        Level 2: High Risk
        Level 3: Critical Risk (immediate isolation)
        """
        n_samples = len(data['age'])
        risk_scores = np.zeros(n_samples)
        
        # Age risk (older = higher risk)
        ages = data['age']
        risk_scores += (ages > 60).astype(float) * 0.5
        risk_scores += (ages > 75).astype(float) * 1.0
        
        # Symptom burden (number of symptoms)
        symptoms = sum(data[symptom] for symptom in SYMPTOMS)
        risk_scores += symptoms * 0.1
        
        # Travel history (highest for international)
        risk_scores += data['travel_history'] * 0.3
        
        # Proximity to confirmed cases (highest risk)
        risk_scores += data['proximity_to_confirmed'] * 0.5
        
        # Vaccination status (unvaccinated = higher risk)
        risk_scores += (4 - np.array(data['vaccination_status'])) * 0.2
        
        # Comorbidities multiply risk
        comorbidity_count = (data['has_hypertension'] + data['has_diabetes'] + 
                            data['has_respiratory_issues'] + data['immunocompromised'])
        risk_scores += comorbidity_count * 0.5
        
        # Critical symptoms
        for symptom in ['shortness_of_breath', 'loss_of_taste', 'loss_of_smell']:
            if symptom in data:
                risk_scores += data[symptom] * 1.0
        
        # Clinic type baseline (transit hub has baseline higher risk)
        if clinic_info['location_type'] == 'transit_hub':
            risk_scores += 0.3
        elif clinic_info['location_type'] == 'urban':
            risk_scores += 0.1
        
        # Symptom duration (acute = higher risk)
        risk_scores += np.array(data['days_symptomatic']) * 0.05
        
        # Convert to risk levels (0-3)
        risk_scores = np.clip(risk_scores, 0, 3)
        risk_labels = np.round(risk_scores).astype(int)
        
        return np.minimum(risk_labels, 3)
    
    def _identify_outbreak_clusters(self, data, clinic_name):
        """
        Identify potential outbreak clusters based on temporal and symptom patterns
        Returns boolean array indicating if patient is in potential cluster
        """
        n_samples = len(data['age'])
        dates = pd.to_datetime(data['date'])
        
        # Sum symptoms across all symptom columns for each patient
        symptoms = np.zeros(n_samples)
        for symptom in SYMPTOMS:
            symptoms += np.array(data[symptom])
        
        # Simple clustering: patients with same date + high symptoms + same clinic
        clusters = []
        for i in range(n_samples):
            same_date_count = np.sum((dates.values == dates.values[i]) & (symptoms > 2))
            clusters.append(same_date_count >= 3)  # Cluster if 3+ severe cases same date
        
        return np.array(clusters).astype(int)
    
    def generate_all_clinics(self, n_samples=500, infection_rate=0.15):
        """Generate data for all three clinics with realistic variation"""
        all_data = []
        
        # Clinic-specific infection rates
        infection_rates = {
            'Clinic_A': infection_rate,
            'Clinic_B': infection_rate * 0.7,  # Rural: lower transmission
            'Clinic_C': infection_rate * 1.3   # Transit: higher transmission
        }
        
        for clinic_name in CLINICS.keys():
            clinic_data = self.generate_clinic_data(
                clinic_name, 
                n_samples,
                infection_rate=infection_rates[clinic_name]
            )
            all_data.append(clinic_data)
        
        return all_data

    def save_clinic_data(self, clinic_dataframes, data_dir='data'):
        """Save clinic data to CSV files"""
        os.makedirs(data_dir, exist_ok=True)
        
        saved_files = []
        for clinic_df, clinic_name in zip(clinic_dataframes, CLINICS.keys()):
            filepath = os.path.join(data_dir, f'{clinic_name}_data.csv')
            clinic_df.to_csv(filepath, index=False)
            saved_files.append(filepath)
            print(f"Saved {CLINICS[clinic_name]['name']}: {filepath} ({len(clinic_df)} records)")
        
        return saved_files

    def load_clinic_data(self, data_dir='data'):
        """Load clinic data from CSV files"""
        clinic_data = {}
        for clinic in CLINICS.keys():
            filepath = os.path.join(data_dir, f'{clinic}_data.csv')
            if os.path.exists(filepath):
                clinic_data[clinic] = pd.read_csv(filepath)
            else:
                print(f"Warning: {filepath} not found")
        
        return clinic_data

