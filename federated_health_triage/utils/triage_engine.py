"""
Health Triage Prediction Engine
Implements intelligent triage assessment based on symptoms, age, and travel history
"""

import numpy as np
from config import SYMPTOMS, TRIAGE_LEVELS, AGE_GROUPS, TRAVEL_RISK_LEVELS


class TriageAssessmentEngine:
    """
    Provides triage assessment using both model predictions and clinical rules
    Combines AI predictions with medical knowledge
    """
    
    def __init__(self, consolidated_model):
        self.model = consolidated_model
        self.assessment_history = []
        
    def assess_patient(self, patient_data):
        """
        Assess patient triage level
        
        Args:
            patient_data: dict with keys:
                - age: int (0-100)
                - symptoms: list of symptom names
                - travel_risk: int (0-3)
                - comorbidities: list of comorbidity names
        
        Returns:
            Assessment with triage level, confidence, and recommendations
        """
        # Calculate risk score from patient features
        risk_score = self._calculate_risk_score(patient_data)
        
        # Get model prediction
        X = self._prepare_patient_features(patient_data)
        try:
            model_pred, probas = self.model.predict_ensemble(X)
            model_triage = model_pred[0]
            confidence = probas[0][model_triage]
        except:
            model_triage = 0
            confidence = 0.5
        
        # Combine risk score and model prediction
        final_triage = self._combine_risk_and_prediction(risk_score, model_triage)
        
        # Get clinical recommendations
        recommendations = self._get_recommendations(final_triage, patient_data)
        
        assessment = {
            'triage_level': int(final_triage),
            'triage_description': TRIAGE_LEVELS[int(final_triage)],
            'risk_score': risk_score,
            'model_confidence': float(confidence),
            'recommendations': recommendations,
            'suspicious_patterns': self._identify_suspicious_patterns(patient_data)
        }
        
        self.assessment_history.append(assessment)
        return assessment
    
    def _calculate_risk_score(self, patient_data):
        """Calculate clinical risk score from patient features"""
        score = 0.0
        
        # Age risk
        age = patient_data.get('age', 40)
        if age > 70:
            score += 2.0
        elif age > 60:
            score += 1.5
        elif age > 50:
            score += 0.5
        
        # Symptom risk
        symptoms = patient_data.get('symptoms', [])
        critical_symptoms = ['shortness_of_breath', 'loss_of_taste']
        for symptom in symptoms:
            if symptom in critical_symptoms:
                score += 2.0
            else:
                score += 0.3
        
        # Travel risk
        travel_risk = patient_data.get('travel_risk', 0)
        score += travel_risk * 0.5
        
        # Comorbidities
        comorbidities = patient_data.get('comorbidities', [])
        score += len(comorbidities) * 0.8
        
        return np.clip(score, 0, 4)
    
    def _prepare_patient_features(self, patient_data):
        """Convert patient data to model feature format"""
        # This is a simplified version - in production, match exact feature order
        features = []
        
        # Placeholder for age and gender
        features.append(patient_data.get('age', 40))
        features.append(1)  # gender (M=1, F=0)
        
        # Symptoms
        symptoms = patient_data.get('symptoms', [])
        for symptom in SYMPTOMS:
            features.append(1 if symptom in symptoms else 0)
        
        # Travel risk
        features.append(patient_data.get('travel_risk', 0))
        
        # Comorbidities
        comorbidities = patient_data.get('comorbidities', [])
        features.append(1 if 'hypertension' in comorbidities else 0)
        features.append(1 if 'diabetes' in comorbidities else 0)
        features.append(1 if 'respiratory_issues' in comorbidities else 0)
        
        return np.array([features])
    
    def _combine_risk_and_prediction(self, risk_score, model_triage):
        """Combine clinical risk score with model prediction"""
        # Weight: 60% model, 40% clinical risk
        model_score = model_triage
        combined = 0.6 * model_score + 0.4 * (risk_score / 4 * 3)  # Scale risk to 0-3
        return np.clip(np.round(combined), 0, 3)
    
    def _get_recommendations(self, triage_level, patient_data):
        """Get clinical recommendations based on triage level"""
        recommendations = {
            0: [
                "Patient can be managed in primary care",
                "Schedule routine follow-up appointment",
                "Monitor symptoms for any changes"
            ],
            1: [
                "Refer to specialist for evaluation",
                "May need diagnostic tests",
                "Follow-up within 48 hours"
            ],
            2: [
                "Urgent evaluation required",
                "Consider hospital admission",
                "Immediate diagnostic tests needed"
            ],
            3: [
                "CRITICAL - Emergency admission required",
                "Multi-specialty assessment needed",
                "Intensive care may be necessary"
            ]
        }
        
        return recommendations.get(triage_level, [])
    
    def _identify_suspicious_patterns(self, patient_data):
        """Identify suspicious symptom patterns that may indicate serious conditions"""
        patterns = []
        symptoms = patient_data.get('symptoms', [])
        age = patient_data.get('age', 40)
        
        # Pattern 1: Respiratory symptoms in elderly
        if age > 65 and 'shortness_of_breath' in symptoms:
            patterns.append("Respiratory distress in elderly patient - high risk")
        
        # Pattern 2: Multiple critical symptoms
        critical_symptoms = ['shortness_of_breath', 'loss_of_taste', 'sore_throat']
        critical_count = sum(1 for s in critical_symptoms if s in symptoms)
        if critical_count >= 2:
            patterns.append(f"Multiple critical symptoms detected ({critical_count})")
        
        # Pattern 3: Fever + respiratory symptoms
        if 'fever' in symptoms and 'cough' in symptoms:
            patterns.append("Classic respiratory infection pattern")
        
        # Pattern 4: High-risk travel + symptoms
        if patient_data.get('travel_risk', 0) >= 2 and len(symptoms) >= 3:
            patterns.append("Recent travel with multiple symptoms - monitor for endemic diseases")
        
        return patterns
    
    def generate_report(self, patient_data, assessment):
        """Generate detailed assessment report"""
        report = f"""
{'='*70}
PATIENT HEALTH TRIAGE ASSESSMENT REPORT
{'='*70}

PATIENT INFORMATION:
  Age: {patient_data.get('age', 'N/A')} years
  Comorbidities: {', '.join(patient_data.get('comorbidities', [])) or 'None'}
  Travel Risk Level: {TRAVEL_RISK_LEVELS.get(patient_data.get('travel_risk', 0), 'Unknown')}

PRESENTING SYMPTOMS:
  {chr(10).join('  - ' + s for s in patient_data.get('symptoms', [])) or '  None'}

TRIAGE ASSESSMENT:
  Level: {assessment['triage_level']} - {assessment['triage_description']}
  Clinical Risk Score: {assessment['risk_score']:.2f}/4.0
  Model Confidence: {assessment['model_confidence']:.2%}

CLINICAL RECOMMENDATIONS:
{chr(10).join('  • ' + r for r in assessment['recommendations'])}

SUSPICIOUS PATTERNS:
{chr(10).join('  ⚠ ' + p for p in assessment['suspicious_patterns']) if assessment['suspicious_patterns'] else '  None identified'}

{'='*70}
"""
        return report
