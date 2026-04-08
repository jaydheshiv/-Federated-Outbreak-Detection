"""
Outbreak Detection and Risk Assessment Engine
Detects potential infectious disease outbreaks and assesses patient risk
Combines federated model predictions with epidemiological algorithms
"""

import numpy as np
from config import SYMPTOMS, INFECTION_RISK_LEVELS


class OutbreakDetectionEngine:
    """
    Analyzes patient data across distributed clinics to detect outbreaks
    Uses federated model predictions combined with epidemiological analysis
    """
    
    def __init__(self, consolidated_model):
        self.model = consolidated_model
        self.assessment_history = []
        self.outbreak_alerts = []
        
    def assess_patient_risk(self, patient_data):
        """
        Assess individual patient's infection risk
        
        Args:
            patient_data: dict with:
                - age, gender, symptoms, travel_history
                - proximity_to_confirmed, vaccination_status
                - comorbidities, days_symptomatic
        
        Returns:
            Risk assessment with level, confidence, and alerts
        """
        # Calculate epidemiological risk score
        epi_risk_score = self._calculate_epidemiological_risk(patient_data)
        
        # Get ensemble model prediction
        X = self._prepare_patient_features(patient_data)
        try:
            model_pred, probas = self.model.predict_ensemble(X)
            model_risk = model_pred[0]
            confidence = probas[0][model_risk]
        except:
            model_risk = 0
            confidence = 0.5
        
        # Combine epidemiological analysis with model prediction
        final_risk = self._combine_risk_assessments(epi_risk_score, model_risk)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(patient_data)
        
        # Generate clinical recommendations
        recommendations = self._get_recommendations(final_risk, patient_data)
        
        assessment = {
            'infection_risk': int(final_risk),
            'risk_description': INFECTION_RISK_LEVELS[int(final_risk)],
            'epidemiological_score': epi_risk_score,
            'model_confidence': float(confidence),
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'requires_testing': final_risk >= 2,
            'requires_isolation': final_risk >= 2,
            'critical_alert': final_risk >= 3
        }
        
        self.assessment_history.append(assessment)
        return assessment
    
    def _calculate_epidemiological_risk(self, patient_data):
        """
        Calculate infection risk from epidemiological factors
        Range: 0-4 (normalized to 0-3 for risk levels)
        """
        score = 0.0
        
        # Age risk (elderly at higher risk)
        age = patient_data.get('age', 40)
        if age > 70:
            score += 1.2
        elif age > 60:
            score += 0.8
        elif age > 50:
            score += 0.4
        
        # Contact with confirmed cases (highest risk)
        proximity = patient_data.get('proximity_to_confirmed', 0)
        score += proximity * 0.7
        
        # Vaccination status (unvaccinated = higher risk)
        vaccination = patient_data.get('vaccination_status', 0)
        score += (3 - vaccination) * 0.4
        
        # Travel history (international > regional > local)
        travel = patient_data.get('travel_history', 0)
        score += travel * 0.3
        
        # Symptom burden
        symptoms = patient_data.get('symptoms', [])
        if isinstance(symptoms, list):
            score += len(symptoms) * 0.15
        else:
            score += symptoms * 0.15
        
        # Days symptomatic (acute onset is more concerning)
        days_symp = patient_data.get('days_symptomatic', 0)
        if days_symp <= 3:
            score += 0.5  # Recent onset
        elif days_symp <= 7:
            score += 0.3
        
        # Comorbidities (risk multiplier)
        comorbidities = patient_data.get('comorbidities', 0)
        if isinstance(comorbidities, list):
            score += len(comorbidities) * 0.4
        else:
            score += comorbidities * 0.4
        
        # Immunocompromised status
        if patient_data.get('immunocompromised', False):
            score += 1.0
        
        # Critical symptoms
        critical_symptoms = ['shortness_of_breath', 'loss_of_taste', 'loss_of_smell']
        for symptom in critical_symptoms:
            if symptom in symptoms:
                score += 0.8
        
        return np.clip(score, 0, 4)
    
    def _prepare_patient_features(self, patient_data):
        """Convert patient data to model feature format"""
        features = []
        
        # Age and gender
        features.append(patient_data.get('age', 40))
        features.append(1 if patient_data.get('gender', 'M') == 'M' else 0)
        
        # Symptoms
        symptoms = patient_data.get('symptoms', [])
        for symptom in SYMPTOMS:
            features.append(1 if symptom in symptoms else 0)
        
        # Epidemiological factors
        features.append(patient_data.get('vaccination_status', 0))
        features.append(patient_data.get('travel_history', 0))
        features.append(patient_data.get('proximity_to_confirmed', 0))
        features.append(patient_data.get('days_symptomatic', 0))
        
        # Comorbidities - handle both list and scalar values
        comorbidities = patient_data.get('comorbidities', 0)
        if isinstance(comorbidities, list):
            features.append(1 if 'hypertension' in comorbidities else 0)
            features.append(1 if 'diabetes' in comorbidities else 0)
            features.append(1 if 'respiratory_issues' in comorbidities else 0)
        else:
            # If comorbidities is a scalar, just use it as a presence indicator
            features.append(1 if comorbidities > 0 else 0)
            features.append(1 if comorbidities > 0 else 0)
            features.append(1 if comorbidities > 0 else 0)
        
        features.append(1 if patient_data.get('immunocompromised', False) else 0)
        
        return np.array([features])
    
    def _combine_risk_assessments(self, epi_risk, model_risk):
        """
        Combine epidemiological and model-based risk assessments
        Weighting: 50% epidemiological + 50% model
        """
        combined = 0.5 * (epi_risk / 4 * 3) + 0.5 * model_risk
        return np.clip(np.round(combined), 0, 3)
    
    def _identify_risk_factors(self, patient_data):
        """Identify specific risk factors for this patient"""
        factors = []
        
        age = patient_data.get('age', 40)
        if age > 70:
            factors.append("Elderly patient (>70 years)")
        elif age > 60:
            factors.append("Senior patient (>60 years)")
        
        if patient_data.get('proximity_to_confirmed', 0) >= 2:
            factors.append("Direct contact with confirmed case")
        elif patient_data.get('proximity_to_confirmed', 0) >= 1:
            factors.append("Potential indirect contact with case")
        
        vaccination = patient_data.get('vaccination_status', 0)
        if vaccination == 0:
            factors.append("Unvaccinated")
        elif vaccination == 1:
            factors.append("Partially vaccinated")
        
        travel = patient_data.get('travel_history', 0)
        if travel >= 3:
            factors.append("International travel history")
        elif travel >= 2:
            factors.append("Regional travel history")
        
        symptoms = patient_data.get('symptoms', [])
        if 'shortness_of_breath' in symptoms:
            factors.append("Respiratory distress (breathing difficulty)")
        if 'loss_of_taste' in symptoms or 'loss_of_smell' in symptoms:
            factors.append("Loss of taste/smell (key infection indicator)")
        
        comorbidities = patient_data.get('comorbidities', 0)
        if isinstance(comorbidities, list):
            if len(comorbidities) > 0:
                factors.append(f"Comorbidities: {', '.join(comorbidities)}")
        elif comorbidities > 0:
            factors.append("Comorbidities present")
        
        if patient_data.get('immunocompromised', False):
            factors.append("Immunocompromised status")
        
        return factors
    
    def _get_recommendations(self, risk_level, patient_data):
        """Generate clinical recommendations based on risk level"""
        recommendations = {
            0: [
                "Monitor for symptom development",
                "Encourage standard precautions (hand hygiene, masking if symptomatic)",
                "No testing required at this time",
                "Follow up in 7 days if symptoms develop"
            ],
            1: [
                "Continue monitoring closely",
                "Consider testing if symptoms progress",
                "Maintain isolation if experiencing symptoms",
                "Health education on transmission prevention"
            ],
            2: [
                "URGENT: Recommend immediate testing",
                "Patient should isolate for 10 days from symptom onset",
                "Contact tracing: identify close contacts",
                "Daily monitoring for symptom progression",
                "Hospital admission if respiratory symptoms worsen"
            ],
            3: [
                "CRITICAL: Immediate isolation required",
                "Urgent testing and hospitalization recommended",
                "Activate public health response",
                "Contact tracing is critical",
                "Consider ICU evaluation",
                "Notify infection control immediately"
            ]
        }
        
        return recommendations.get(risk_level, [])
    
    def detect_cluster_outbreak(self, clinic_patients, time_window_days=7):
        """
        Detect potential outbreak clusters in a clinic
        Returns outbreak alert if threshold exceeded
        """
        high_risk_patients = [p for p in clinic_patients if p['infection_risk'] >= 2]
        
        if len(high_risk_patients) >= 5:  # Cluster threshold
            outbreak_alert = {
                'clinic': clinic_patients[0].get('clinic_name'),
                'alert_type': 'CLUSTER_DETECTED',
                'severity': 'HIGH',
                'cluster_size': len(high_risk_patients),
                'percentage_high_risk': len(high_risk_patients) / len(clinic_patients),
                'recommendations': [
                    "Activate outbreak investigation protocol",
                    "Increase testing and surveillance",
                    "Contact tracing for all high-risk patients",
                    "Notify public health authorities",
                    "Consider temporary clinic closure/disinfection"
                ]
            }
            self.outbreak_alerts.append(outbreak_alert)
            return outbreak_alert
        
        return None
    
    def generate_assessment_report(self, patient_data, assessment, clinic=None):
        """Generate detailed patient assessment report"""
        report = f"""
{'='*75}
PATIENT INFECTION RISK ASSESSMENT REPORT
{'='*75}

PATIENT INFORMATION:
  Age: {patient_data.get('age', 'N/A')} years
  Gender: {patient_data.get('gender', 'N/A')}
  Comorbidities: {', '.join(patient_data.get('comorbidities', [])) if isinstance(patient_data.get('comorbidities', []), list) else ('Present' if patient_data.get('comorbidities', 0) > 0 else 'None')}
  Vaccination Status: {['Unvaccinated', 'Partially', 'Fully', 'Boosted'][patient_data.get('vaccination_status', 0)]}
  Immunocompromised: {'Yes' if patient_data.get('immunocompromised', False) else 'No'}

EXPOSURE HISTORY:
  Travel History: {['None', 'Local', 'Regional', 'International'][patient_data.get('travel_history', 0)]}
  Contact with Confirmed Case: {['None', 'Indirect', 'Direct', 'High-Risk'][patient_data.get('proximity_to_confirmed', 0)]}
  Days Since Symptom Onset: {patient_data.get('days_symptomatic', 'N/A')}

PRESENTING SYMPTOMS:
{chr(10).join('  - ' + s for s in patient_data.get('symptoms', [])) or '  None reported'}

RISK ASSESSMENT:
  Level: {assessment['infection_risk']} - {assessment['risk_description']}
  Epidemiological Score: {assessment['epidemiological_score']:.2f}/4.0
  Model Confidence: {assessment['model_confidence']:.2%}

IDENTIFIED RISK FACTORS:
{chr(10).join('  ⚠ ' + f for f in assessment['risk_factors']) if assessment['risk_factors'] else '  None identified'}

CLINICAL RECOMMENDATIONS:
{chr(10).join('  • ' + r for r in assessment['recommendations'])}

TESTING REQUIREMENT: {'YES - Urgent' if assessment['requires_testing'] else 'No'}
ISOLATION REQUIREMENT: {'YES - Immediate' if assessment['requires_isolation'] else 'No'}
CRITICAL ALERT: {'🚨 YES - Notify authorities immediately' if assessment['critical_alert'] else 'No'}

{'='*75}
"""
        return report
