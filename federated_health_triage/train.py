"""
Federated Learning Infectious Disease Outbreak Detection Training Pipeline
Orchestrates distributed training across three clinic archetypes while preserving patient privacy
Detects early outbreak signals and high-risk infection clusters
Enhanced with ChatGPT for clinical explanations and outbreak reporting
"""

import os
import sys
import json
import numpy as np
from utils.data_generator import EpidemiologicalDataGenerator
from utils.preprocessing import EpidemiologicalDataProcessor
from models.clinic_model import InfectionRiskDetectionModel
from federated_learning.aggregator import FederatedOutbreakAggregator, ConsolidatedOutbreakDetectionModel
from utils.outbreak_detection import OutbreakDetectionEngine
from config import CLINICS, SAMPLES_PER_CLINIC, MODEL_TYPE, AGGREGATION_METHOD

# ChatGPT Integration
try:
    from utils.chatgpt_integration import ChatGPTClinicalAdvisor
    CHATGPT_AVAILABLE = True
except (ImportError, ValueError) as e:
    CHATGPT_AVAILABLE = False
    print(f"⚠️  ChatGPT integration not available: {e}")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env file
except ImportError:
    pass


class FederatedOutbreakDetectionSystem:
    """
    Federated learning system for early detection of infectious disease outbreaks
    across geographically distributed clinics
    
    Architecture:
    - Urban Center (Clinic_A): Dense population, moderate travel exposure
    - Rural Area (Clinic_B): Low population, minimal travel exposure
    - Travel Hub (Clinic_C): High transit connectivity, maximum exposure risk
    
    Privacy Model: Only model parameters aggregated centrally, patient data remains local
    """
    
    def __init__(self, n_samples=SAMPLES_PER_CLINIC, model_type=MODEL_TYPE):
        self.n_samples = n_samples
        self.model_type = model_type
        self.clinic_data = {}
        self.clinic_models = {}
        self.aggregator = FederatedOutbreakAggregator(aggregation_method=AGGREGATION_METHOD)
        self.consolidated_model = None
        self.outbreak_engine = None
        self.clinic_sizes = {}
        self.outbreak_signals = []
        
        # Initialize ChatGPT advisor (optional)
        self.chatgpt_advisor = None
        if CHATGPT_AVAILABLE and os.getenv('ENABLE_CHATGPT', 'true').lower() == 'true':
            try:
                model = os.getenv('CHATGPT_MODEL', 'llama-3.3-70b-versatile')
                self.chatgpt_advisor = ChatGPTClinicalAdvisor(model=model)
                print(f"✅ ChatGPT integration enabled ({model})")
            except ValueError as e:
                print(f"⚠️  ChatGPT not available: {e}")
                print("   System will continue with local ML only")
        
    def generate_epidemiological_data(self):
        """Generate synthetic epidemiological data for all three clinics"""
        print("\n" + "="*70)
        print("STEP 1: GENERATING EPIDEMIOLOGICAL DATA")
        print("="*70)
        print("Simulating infectious disease surveillance across three clinic sites...")
        
        generator = EpidemiologicalDataGenerator()
        clinic_dataframes = generator.generate_all_clinics(self.n_samples)
        generator.save_clinic_data(clinic_dataframes)
        
        # Load and process data
        clinic_names = list(CLINICS.keys())
        for clinic_df, clinic_name in zip(clinic_dataframes, clinic_names):
            clinic_info = CLINICS[clinic_name]
            self.clinic_data[clinic_info['name']] = clinic_df
            self.clinic_sizes[clinic_info['name']] = len(clinic_df)
            
            # Check for outbreak clusters
            high_risk = (clinic_df['infection_risk'] >= 2).sum()
            high_risk_pct = (high_risk / len(clinic_df)) * 100
            
            print(f"\n  {clinic_name} ({clinic_info['location_type']}):")
            print(f"    Total patients: {len(clinic_df)}")
            print(f"    High-risk cases: {high_risk} ({high_risk_pct:.1f}%)")
            
            # Detect temporal clusters
            clusters = (clinic_df['in_outbreak_cluster'] == 1).sum()
            if clusters > 0:
                print(f"    ⚠️  Outbreak clusters detected: {clusters} cases")
        
        return self.clinic_data
    
    def train_clinic_infection_models(self):
        """Train local infection risk detection models for each clinic"""
        print("\n" + "="*70)
        print("STEP 2: TRAINING LOCAL INFECTION RISK DETECTION MODELS")
        print("="*70)
        print("Each clinic trains independently on local data (privacy-preserving)...\n")
        
        processor = EpidemiologicalDataProcessor()
        
        for clinic_key, clinic_info in CLINICS.items():
            clinic_name = clinic_info['name']
            clinic_type = clinic_info['location_type']
            
            # Prepare data
            clinic_df = self.clinic_data[clinic_name]
            X, y = processor.preprocess_data(clinic_df)
            X_train, X_val, X_test, y_train, y_val, y_test = processor.split_data(X, y)
            
            # Create and train infection risk model
            model = InfectionRiskDetectionModel(
                clinic_name=clinic_name,
                clinic_type=clinic_type,
                model_type=self.model_type
            )
            
            print(f"Training {clinic_name} ({clinic_type})...")
            model.train(X_train, y_train, X_val, y_val)
            
            # Store model and data
            feature_names = processor.get_feature_names(clinic_df)
            self.clinic_models[clinic_name] = {
                'model': model,
                'X_test': X_test,
                'y_test': y_test,
                'feature_names': feature_names,
                'clinic_type': clinic_type
            }
            
            # Register with aggregator
            self.aggregator.register_clinic(clinic_name, model)
        
        return self.clinic_models
    
    def aggregate_models_federated(self):
        """Perform federated aggregation across clinic models"""
        print("\n" + "="*70)
        print("STEP 3: FEDERATED MODEL AGGREGATION")
        print("="*70)
        print("Aggregating infection risk detection patterns across clinics...")
        
        aggregated_weights = self.aggregator.aggregate_models(self.clinic_sizes)
        
        print(f"\n✓ Federated aggregation complete!")
        print(f"  Aggregation method: {self.aggregator.aggregation_method}")
        print(f"  Clinics aggregated: {len(self.clinic_models)}")
        print(f"  Total population: {sum(self.clinic_sizes.values())} patients")
        
        return aggregated_weights
    
    def create_consolidated_outbreak_model(self):
        """Create consolidated ensemble combining predictions from all clinics"""
        print("\n" + "="*70)
        print("STEP 4: CREATING CONSOLIDATED OUTBREAK DETECTION ENSEMBLE")
        print("="*70)
        
        clinic_models_dict = {
            name: self.clinic_models[name]['model']
            for name in [c['name'] for c in CLINICS.values()]
        }
        
        self.consolidated_model = ConsolidatedOutbreakDetectionModel(
            clinic_models_dict,
            aggregation_weights=self.aggregator.aggregated_weights
        )
        
        print("✓ Consolidated outbreak detection model created successfully!")
        return self.consolidated_model
    
    def evaluate_infection_models(self):
        """Evaluate individual clinic models and consolidated ensemble"""
        print("\n" + "="*70)
        print("STEP 5: INFECTION RISK MODEL EVALUATION")
        print("="*70)
        
        # Evaluate individual clinic models
        print("\nIndividual Clinic Model Performance (High-Risk Detection Focus):")
        print("-" * 70)
        individual_results = {}
        
        for clinic_name, clinic_info in self.clinic_models.items():
            model = clinic_info['model']
            X_test = clinic_info['X_test']
            y_test = clinic_info['y_test']
            
            print(f"\n{clinic_name}:")
            metrics = model.evaluate(X_test, y_test)
            individual_results[clinic_name] = metrics
        
        # Evaluate consolidated ensemble
        print("\n")
        test_clinic_name = list(self.clinic_models.keys())[0]
        test_data = self.clinic_models[test_clinic_name]
        
        print("Consolidated Outbreak Detection Ensemble Performance:")
        print("-" * 70)
        ensemble_metrics = self.consolidated_model.evaluate_ensemble(
            test_data['X_test'],
            test_data['y_test']
        )
        
        # Compare individual vs ensemble
        print("\n")
        comparison = self.consolidated_model.compare_individual_vs_ensemble(
            test_data['X_test'],
            test_data['y_test']
        )
        
        return {
            'individual': individual_results,
            'ensemble': ensemble_metrics,
            'comparison': comparison
        }
    
    def create_outbreak_detection_engine(self):
        """Initialize the outbreak detection engine"""
        self.outbreak_engine = OutbreakDetectionEngine(self.consolidated_model)
        print("✓ Outbreak detection engine initialized!")
        return self.outbreak_engine
    
    def demo_outbreak_scenarios(self):
        """Demonstrate outbreak detection with realistic epidemiological scenarios"""
        print("\n" + "="*70)
        print("STEP 6: OUTBREAK DETECTION DEMONSTRATION")
        print("="*70)
        print("Simulating 4 clinical scenarios with varying infection risk profiles...\n")
        
        # Scenario 1: Low Risk (Baseline)
        scenario_1 = {
            'name': 'Scenario 1: Low-Risk Baseline Patient',
            'clinic': 'Urban Center',
            'features': {
                'age': 28,
                'fever': 0,
                'cough': 0,
                'shortness_of_breath': 0,
                'loss_of_taste_smell': 0,
                'respiratory_distress': 0,
                'vaccination_status': 2,  # Fully vaccinated
                'proximity_to_confirmed': 0,  # No contact with confirmed cases
                'travel_history': 0,  # No recent travel
                'days_symptomatic': 0,
                'age_group': 0,  # 20-39
                'comorbidities': 0  # No comorbidities
            }
        }
        
        # Scenario 2: Moderate Risk (Some exposure)
        scenario_2 = {
            'name': 'Scenario 2: Moderate-Risk With Recent Travel',
            'clinic': 'Travel Hub',
            'features': {
                'age': 45,
                'fever': 1,
                'cough': 1,
                'shortness_of_breath': 0,
                'loss_of_taste_smell': 0,
                'respiratory_distress': 0,
                'vaccination_status': 1,  # Partially vaccinated
                'proximity_to_confirmed': 1,  # Possible contact
                'travel_history': 3,  # International travel
                'days_symptomatic': 2,
                'age_group': 2,  # 40-59
                'comorbidities': 0
            }
        }
        
        # Scenario 3: High-Risk (Confirmed symptoms + contact)
        scenario_3 = {
            'name': 'Scenario 3: High-Risk With Confirmed Contact (TESTING REQUIRED)',
            'clinic': 'Urban Center',
            'features': {
                'age': 58,
                'fever': 1,
                'cough': 1,
                'shortness_of_breath': 1,
                'loss_of_taste_smell': 1,  # KEY INDICATOR
                'respiratory_distress': 0,
                'vaccination_status': 0,  # Unvaccinated
                'proximity_to_confirmed': 2,  # Direct contact with confirmed case
                'travel_history': 1,  # Local travel
                'days_symptomatic': 3,
                'age_group': 2,  # 40-59
                'comorbidities': 1  # Has comorbidities
            }
        }
        
        # Scenario 4: Critical-Risk (Multiple indicators + outbreak cluster)
        scenario_4 = {
            'name': 'Scenario 4: Critical-Risk Cluster Alert (PUBLIC HEALTH NOTIFICATION)',
            'clinic': 'Rural Area',
            'features': {
                'age': 72,
                'fever': 1,
                'cough': 1,
                'shortness_of_breath': 1,
                'loss_of_taste_smell': 1,
                'respiratory_distress': 1,  # CRITICAL
                'vaccination_status': 0,  # Unvaccinated
                'proximity_to_confirmed': 2,  # Direct contact with confirmed case
                'travel_history': 0,
                'days_symptomatic': 5,
                'age_group': 3,  # 60+
                'comorbidities': 1  # Has immunocompromised status
            }
        }
        
        scenarios = [scenario_1, scenario_2, scenario_3, scenario_4]
        results = []
        
        for scenario in scenarios:
            print(f"\n{'='*70}")
            print(f"{scenario['name']}")
            print(f"{'='*70}")
            
            # Get risk assessment
            assessment = self.outbreak_engine.assess_patient_risk(scenario['features'])
            report = self.outbreak_engine.generate_assessment_report(
                scenario['features'],
                assessment,
                scenario['clinic']
            )
            print(report)
            
            # Get ChatGPT clinical explanation (if available)
            if self.chatgpt_advisor:
                print("\n" + "─"*70)
                print("🤖 CLINICAL ANALYSIS (via ChatGPT)")
                print("─"*70)
                try:
                    # Extract risk level and confidence
                    risk_pred = assessment['risk_level']
                    confidence = assessment.get('confidence', 0.5)
                    
                    # Get ChatGPT explanation
                    explanation = self.chatgpt_advisor.explain_risk_level(
                        patient_data=scenario['features'],
                        risk_level=risk_pred,
                        confidence=confidence
                    )
                    print(explanation)
                except Exception as e:
                    print(f"⚠️  ChatGPT explanation unavailable: {e}")
            
            results.append({
                'scenario': scenario['name'],
                'assessment': assessment,
                'report': report
            })
        
        return results
    
    def detect_population_level_outbreaks(self):
        """Detect outbreak signals at population level using all clinic data"""
        print("\n" + "="*70)
        print("POPULATION-LEVEL OUTBREAK DETECTION ANALYSIS")
        print("="*70)
        print("Analyzing high-risk patient prevalence across all clinics...\n")
        
        high_risk_percentages = {}
        
        for clinic_name, clinic_info in self.clinic_models.items():
            y_test = clinic_info['y_test']
            high_risk_count = (y_test >= 2).sum()
            high_risk_pct = (high_risk_count / len(y_test)) * 100
            high_risk_percentages[clinic_name] = high_risk_pct
            
            print(f"{clinic_name}: {high_risk_pct:.1f}% of patients at high-risk level")
        
        # Detect outbreak signals
        signals = self.aggregator.detect_outbreak_signals(high_risk_percentages, threshold=0.15)
        self.outbreak_signals = signals
        
        if not signals:
            print("\n✓ No significant outbreak signals detected")
        
        return signals
    
    def generate_chatgpt_outbreak_reports(self):
        """Generate AI-enhanced outbreak reports using ChatGPT"""
        if not self.chatgpt_advisor:
            print("\n⚠️  ChatGPT not available. Skipping AI-enhanced reports.")
            return []
        
        print("\n" + "="*70)
        print("CHATGPT-ENHANCED OUTBREAK REPORTING")
        print("="*70)
        print("Generating professional epidemiological reports with AI analysis...\n")
        
        reports = []
        
        for clinic_name, clinic_info in self.clinic_models.items():
            y_test = clinic_info['y_test']
            
            # Calculate metrics
            high_risk_count = (y_test >= 2).sum()
            critical_count = (y_test >= 3).sum()
            high_risk_pct = (high_risk_count / len(y_test)) * 100
            
            # Determine if outbreak exists
            is_outbreak = high_risk_count >= 10
            
            if high_risk_count >= 5 or is_outbreak:  # Report if 5+ cases
                print(f"\n{clinic_name} - Generating report...")
                print("-"*70)
                
                try:
                    # Create symptom profile
                    symptoms_profile = {
                        'fever': 0.6,
                        'cough': 0.65,
                        'shortness_of_breath': 0.35,
                        'loss_of_taste_smell': 0.25
                    }
                    
                    # Generate 7-day case timeline (synthetic)
                    case_timeline = [
                        high_risk_count // 7 + (1 if i < high_risk_count % 7 else 0)
                        for i in range(7)
                    ]
                    
                    # Get ChatGPT report
                    report = self.chatgpt_advisor.generate_outbreak_report(
                        clinic_name=clinic_name,
                        num_cases=high_risk_count,
                        avg_age=45,
                        symptoms_profile=symptoms_profile,
                        vaccination_coverage=0.65,
                        case_timeline=case_timeline
                    )
                    
                    print(report)
                    
                    reports.append({
                        'clinic': clinic_name,
                        'cases': high_risk_count,
                        'report': report
                    })
                    
                except Exception as e:
                    print(f"⚠️  Error generating report: {e}")
        
        return reports
    
    def save_results(self, results_dir='results'):
        """Save training results, models, and outbreak analysis"""
        print("\n" + "="*70)
        print("SAVING MODELS AND OUTBREAK ANALYSIS RESULTS")
        print("="*70)
        
        os.makedirs(results_dir, exist_ok=True)
        
        # Save clinic models
        for clinic_name, clinic_info in self.clinic_models.items():
            clinic_info['model'].save_model('models')
        
        # Save aggregator metadata
        aggregator_info = self.aggregator.get_aggregated_model_info()
        with open(os.path.join(results_dir, 'aggregator_info.json'), 'w') as f:
            json.dump(aggregator_info, f, indent=2)
        
        # Save outbreak signals
        if self.outbreak_signals:
            signals_data = [
                {
                    'clinic': s['clinic'],
                    'high_risk_percentage': float(s['high_risk_percentage']),
                    'alert_level': s['alert_level']
                }
                for s in self.outbreak_signals
            ]
            with open(os.path.join(results_dir, 'outbreak_signals.json'), 'w') as f:
                json.dump(signals_data, f, indent=2)
        
        print(f"Results saved to {results_dir}")
    
    def run_full_pipeline(self):
        """Execute complete federated outbreak detection pipeline"""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*68 + "║")
        print("║" + "FEDERATED OUTBREAK DETECTION SYSTEM".center(68) + "║")
        print("║" + "Early Risk Detection Across Distributed Clinics".center(68) + "║")
        print("║" + " "*68 + "║")
        print("╚" + "="*68 + "╝")
        
        # Execute all training and evaluation steps
        self.generate_epidemiological_data()
        self.train_clinic_infection_models()
        self.aggregate_models_federated()
        self.create_consolidated_outbreak_model()
        evaluation_results = self.evaluate_infection_models()
        self.create_outbreak_detection_engine()
        self.demo_outbreak_scenarios()
        self.detect_population_level_outbreaks()
        self.generate_chatgpt_outbreak_reports()  # AI-enhanced reporting
        self.save_results()
        
        print("\n" + "="*70)
        print("PIPELINE COMPLETE - OUTBREAK DETECTION SYSTEM READY FOR DEPLOYMENT")
        print("="*70)
        
        return evaluation_results


if __name__ == '__main__':
    system = FederatedOutbreakDetectionSystem(
        n_samples=SAMPLES_PER_CLINIC,
        model_type=MODEL_TYPE
    )
    results = system.run_full_pipeline()
