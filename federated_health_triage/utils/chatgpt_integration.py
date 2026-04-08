"""
ChatGPT Clinical Advisor Integration
Enhanced clinical explanations and reports using OpenAI's GPT models
Provides natural language interpretations of infection risk predictions
"""

import os
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq library not installed. Run: pip install groq")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatGPTClinicalAdvisor:
    """
    Integrate Groq AI for clinical explanations and epidemiological analysis
    Free tier: 14,400 requests/day, extremely fast inference
    
    Provides:
    - Natural language risk explanations
    - Outbreak report generation
    - Symptom extraction from text
    - Clinical decision support
    - Public health messaging
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq Clinical Advisor
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Groq model id (defaults to CHATGPT_MODEL env var)
        """
        if not GROQ_AVAILABLE:
            raise ImportError(
                "Groq library not available. "
                "Install with: pip install groq"
            )
        
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. "
                "Please set GROQ_API_KEY environment variable "
                "or pass api_key parameter. "
                "Get free key at: https://console.groq.com"
            )

        self.client = Groq(api_key=self.api_key)
        self.model = (model or os.getenv("CHATGPT_MODEL") or "llama-3.3-70b-versatile")
        self.request_count = 0
        self.cache = {}  # Simple in-memory cache

        logger.info(f"✅ Groq Clinical Advisor initialized with {self.model} (FREE TIER)")
    
    def _create_cache_key(self, request_type: str, **kwargs) -> str:
        """Create cache key from request parameters"""
        params = f"{request_type}_" + "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return params
    
    def explain_risk_level(self, 
                          patient_data: Dict,
                          risk_level: int,
                          confidence: float) -> str:
        """
        Generate clinical explanation for predicted infection risk
        
        Args:
            patient_data: Dictionary with patient features
            risk_level: Predicted risk (0-3)
            confidence: Model confidence (0-1)
        
        Returns:
            Clinical explanation as string
        """
        # Check cache
        cache_key = self._create_cache_key(
            "risk_level",
            age=patient_data.get('age', 0),
            risk_level=risk_level,
            confidence=int(confidence * 100)
        )
        
        if cache_key in self.cache:
            logger.info(f"📦 Using cached response")
            return self.cache[cache_key]
        
        risk_labels = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "CRITICAL"}
        risk_label = risk_labels.get(risk_level, "UNKNOWN")
        
        # Extract key patient features
        symptoms = []
        if patient_data.get('fever', 0):
            symptoms.append("fever")
        if patient_data.get('cough', 0):
            symptoms.append("cough")
        if patient_data.get('shortness_of_breath', 0):
            symptoms.append("shortness of breath")
        if patient_data.get('loss_of_taste_smell', 0):
            symptoms.append("loss of taste/smell")
        if patient_data.get('respiratory_distress', 0):
            symptoms.append("respiratory distress")
        
        symptoms_str = ", ".join(symptoms) if symptoms else "no acute symptoms"
        
        prompt = f"""
You are an experienced clinical epidemiologist. Provide a brief, professional clinical assessment of this patient's infection risk.

PATIENT PROFILE:
- Age: {patient_data.get('age', 'Unknown')} years
- Symptoms: {symptoms_str}
- Vaccination Status: {patient_data.get('vaccination_status', 'Unknown')} (0=Unvaccinated, 1=Partial, 2=Fully)
- Contact with Confirmed Cases: {patient_data.get('proximity_to_confirmed', 0)} (0=None, 1=Possible, 2=Direct)
- Travel History: {patient_data.get('travel_history', 0)} (0=None, 1=Local, 2=Regional, 3=International)
- Days Symptomatic: {patient_data.get('days_symptomatic', 0)}
- Pre-existing Conditions: {'Yes' if patient_data.get('comorbidities', 0) else 'None reported'}

MODEL PREDICTION:
- Risk Assessment: {risk_label} ({risk_level}/3)
- Confidence Level: {confidence*100:.1f}%

Please provide:
1. Brief risk summary (2-3 sentences)
2. Top 3 contributing factors (with brief explanation)
3. Immediate recommended actions
4. Monitoring timeline

Keep response concise and clinically actionable. Use professional medical language.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a clinical epidemiologist providing brief, accurate, and actionable clinical assessments for infectious disease risk. Always prioritize patient safety."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low = more consistent/deterministic
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            self.cache[cache_key] = result
            self.request_count += 1
            
            logger.info(f"✅ Generated risk explanation with Groq (Request #{self.request_count})")
            return result
            
        except Exception as e:
            logger.error(f"⚠️  Groq API Error: {e}")
            return self._get_fallback_risk_explanation(risk_level, confidence)
    
    def generate_outbreak_report(self,
                                clinic_name: str,
                                num_cases: int,
                                avg_age: float,
                                symptoms_profile: Dict,
                                vaccination_coverage: float,
                                case_timeline: List[int]) -> str:
        """
        Generate professional epidemiological outbreak report
        
        Args:
            clinic_name: Name of clinic
            num_cases: Number of confirmed cases
            avg_age: Average age of cases
            symptoms_profile: Dict of symptom frequencies
            vaccination_coverage: % of population vaccinated
            case_timeline: When cases occurred (7-day rolling)
        
        Returns:
            Formatted outbreak report
        """
        cache_key = self._create_cache_key(
            "outbreak_report",
            clinic=clinic_name,
            cases=num_cases,
            avg_age=int(avg_age)
        )
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        alert_level = "CRITICAL" if num_cases >= 10 else "HIGH" if num_cases >= 5 else "MODERATE"
        
        top_symptoms = sorted(symptoms_profile.items(), key=lambda x: x[1], reverse=True)[:3]
        symptoms_str = ", ".join([f"{k} ({v*100:.0f}%)" for k, v in top_symptoms])
        
        prompt = f"""
Generate a professional public health outbreak report for this situation:

OUTBREAK INFORMATION:
- Facility: {clinic_name}
- Alert Status: {alert_level}
- Confirmed Cases: {num_cases} over past 7 days
- Average Age: {avg_age:.1f} years
- Timeline: {sum(case_timeline)} total patients in analysis period

CLINICAL PATTERNS:
- Most Common Symptoms: {symptoms_str}
- Vaccination Coverage: {vaccination_coverage*100:.1f}%
- Case Distribution (daily): {case_timeline}

Generate a professional outbreak response report including:
1. EXECUTIVE SUMMARY (2-3 sentences)
2. EPIDEMIOLOGICAL ASSESSMENT
   - Disease pattern analysis
   - Risk factors identified
   - Comparison to baseline

3. PUBLIC HEALTH RECOMMENDATIONS
   - Immediate actions
   - Testing strategy
   - Isolation protocols
   - Contact tracing scope

4. MONITORING PLAN
   - Key metrics to track
   - Timeline for follow-up
   - Escalation criteria

5. RESOURCE REQUIREMENTS
   - Estimated resource needs

Format as professional medical report suitable for public health authorities.
Use data-driven language and clear clinical reasoning.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a public health epidemiologist preparing official outbreak reports. Be professional, thorough, and action-oriented."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Very deterministic for reports
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            self.cache[cache_key] = result
            self.request_count += 1
            
            logger.info(f"✅ Generated outbreak report with Groq (Request #{self.request_count})")
            return result
            
        except Exception as e:
            logger.error(f"⚠️  Groq API Error generating outbreak report: {e}")
            return self._get_fallback_outbreak_report(clinic_name, num_cases)

    def generate_dashboard_insight(
        self,
        clinic_name: str,
        high_risk_count: int,
        total_count: int,
        cluster_count: int,
    ) -> str:
        """Generate a short dashboard insight for staff.

        This is intentionally compact (2-4 sentences) so it fits well in a
        Streamlit info box and loads fast.
        """
        cache_key = self._create_cache_key(
            "dashboard_insight",
            clinic=clinic_name,
            high_risk=high_risk_count,
            total=total_count,
            clusters=cluster_count,
        )
        if cache_key in self.cache:
            return self.cache[cache_key]

        high_risk_pct = (high_risk_count / total_count) * 100 if total_count else 0.0

        prompt = f"""
You are an infection-control epidemiologist supporting a clinical operations dashboard.

DASHBOARD SNAPSHOT:
- Scope: {clinic_name}
- Total patients monitored: {total_count}
- High-risk cases: {high_risk_count} ({high_risk_pct:.1f}%)
- Outbreak clusters detected: {cluster_count}

Write a concise insight for staff:
- 1 sentence: situation/urgency
- 1 sentence: likely operational focus (testing/isolation/contact tracing)
- 1 sentence: what to watch in the next 24-48h

Keep it practical and non-alarmist; no speculation beyond the numbers.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a clinical epidemiologist producing brief operational insights for hospital staff.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.25,
                max_tokens=220,
            )

            result = response.choices[0].message.content
            self.cache[cache_key] = result
            self.request_count += 1
            return result
        except Exception as e:
            logger.error(f"⚠️  Groq API Error generating dashboard insight: {e}")
            return (
                "AI insight unavailable right now. "
                "Proceed with standard monitoring: prioritize testing and isolation for high-risk cases, "
                "and monitor cluster count changes over the next 24–48 hours."
            )
    
    def extract_symptoms_from_text(self, patient_description: str) -> Dict:
        """
        Extract structured symptom data from patient's natural language description
        
        Args:
            patient_description: Free-text patient description
        
        Returns:
            Structured symptom dictionary
        """
        prompt = f"""
Extract medical information from this patient's description. 
Return response as valid JSON only, no other text.

PATIENT DESCRIPTION:
"{patient_description}"

Extract and return this JSON structure:
{{
    "fever_present": true/false,
    "cough_present": true/false,
    "shortness_of_breath": true/false,
    "loss_of_taste_smell": true/false,
    "respiratory_distress": true/false,
    "total_symptoms": number,
    "severity_level": "mild/moderate/severe",
    "duration_days": number,
    "vaccination_status": 0/1/2,
    "recent_contact_with_confirmed": true/false,
    "travel_history": true/false,
    "has_comorbidities": true/false,
    "summary": "Brief clinical summary"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract medical information accurately from patient descriptions. Response must be valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Very deterministic for data extraction
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            self.request_count += 1
            
            logger.info(f"✅ Extracted symptoms (Request #{self.request_count})")
            return result
            
        except json.JSONDecodeError:
            logger.error("❌ Failed to parse JSON response from symptom extraction")
            return {"error": "JSON parsing failed", "raw_response": response_text}
        except Exception as e:
            logger.error(f"⚠️  Groq API Error extracting symptoms: {e}")
            return {"error": f"API Error: {str(e)}"}
    
    def generate_clinical_summary(self, 
                                 patient_data: Dict,
                                 risk_level: int) -> str:
        """
        Generate concise clinical summary for patient record
        
        Args:
            patient_data: Patient feature dictionary
            risk_level: Predicted risk level
        
        Returns:
            Clinical summary string
        """
        risk_labels = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "CRITICAL"}
        risk_text = risk_labels.get(risk_level, "UNKNOWN")
        
        prompt = f"""
Write a brief clinical note (2-3 sentences) for the patient's medical record.

Key Info:
- Age: {patient_data.get('age', 'Unknown')}
- Risk Assessment: {risk_text}
- Vaccination: {patient_data.get('vaccination_status', 'Unknown')}
- Exposure: {patient_data.get('proximity_to_confirmed', 0)}
- Has symptoms: {any(patient_data.get(s, 0) for s in ['fever', 'cough', 'shortness_of_breath'])}

Write in professional medical note style.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Write brief clinical notes in standard medical format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=150
            )
            
            self.request_count += 1
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating clinical summary: {e}")
            return f"Patient Risk Level: {risk_text}"
    
    # Fallback methods for when API is unavailable
    def _get_fallback_risk_explanation(self, risk_level: int, confidence: float) -> str:
        """Fallback explanation when API unavailable"""
        risk_labels = {
            0: "LOW RISK - Patient has minimal infection risk indicators",
            1: "MODERATE RISK - Patient shows some infection risk factors requiring monitoring",
            2: "HIGH RISK - Patient shows significant infection risk factors; testing recommended",
            3: "CRITICAL RISK - Patient shows critical risk factors; immediate action required"
        }
        
        return f"""
⚠️  [ChatGPT API unavailable - showing fallback response]

{risk_labels.get(risk_level, 'UNKNOWN RISK')}

Confidence: {confidence*100:.1f}%

RECOMMENDATIONS:
- If HIGH/CRITICAL: Arrange testing immediately
- Implement isolation precautions
- Daily health monitoring
- Follow clinic protocols for positive cases

Note: Full clinical assessment not available without API connection.
"""
    
    def _get_fallback_outbreak_report(self, clinic_name: str, num_cases: int) -> str:
        """Fallback report when API unavailable"""
        alert_level = "CRITICAL" if num_cases >= 10 else "HIGH" if num_cases >= 5 else "MODERATE"
        
        return f"""
⚠️  [ChatGPT API unavailable - showing template response]

OUTBREAK REPORT - {clinic_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

ALERT LEVEL: {alert_level}
Confirmed Cases (7-day): {num_cases}

SUMMARY:
{alert_level} alert status triggered with {num_cases} confirmed infection cases.
Investigation ongoing. Recommendations:
1. Activate outbreak response protocols
2. Increase testing capacity
3. Establish isolation zones
4. Perform contact tracing

Note: Full analysis not available without API connection.
"""
    
    def get_statistics(self) -> Dict:
        """Get usage statistics"""
        return {
            "requests_made": self.request_count,
            "cache_size": len(self.cache),
            "model": self.model,
            "status": "active" if GROQ_AVAILABLE else "unavailable"
        }


# Example usage and testing
if __name__ == "__main__":
    # This only runs if module is executed directly (not imported)
    
    print("\n" + "="*70)
    print("ChatGPT Clinical Advisor - Test Mode")
    print("="*70)
    
    try:
        advisor = ChatGPTClinicalAdvisor()
        
        # Test 1: Risk explanation
        print("\n[Test 1] Risk Explanation")
        print("-" * 70)
        patient = {
            'age': 52,
            'fever': 1,
            'cough': 1,
            'vaccination_status': 1,
            'proximity_to_confirmed': 2,
            'travel_history': 2,
            'comorbidities': 1
        }
        
        explanation = advisor.explain_risk_level(patient, risk_level=2, confidence=0.617)
        print(explanation)
        
        # Test 2: Symptom extraction
        print("\n[Test 2] Symptom Extraction from Text")
        print("-" * 70)
        description = """
        Patient reports fever for 3 days, persistent cough, shortness of breath,
        and loss of taste. Just returned from international trip. Partially vaccinated.
        """
        
        symptoms = advisor.extract_symptoms_from_text(description)
        print(json.dumps(symptoms, indent=2))
        
        # Test 3: Statistics
        print("\n[Test 3] Usage Statistics")
        print("-" * 70)
        stats = advisor.get_statistics()
        print(json.dumps(stats, indent=2))
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nTo use ChatGPT features, set your API key:")
        print("  export OPENAI_API_KEY='sk-proj-your-key-here'")
    except Exception as e:
        print(f"❌ Error: {e}")
