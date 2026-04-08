"""
Unit tests for federated learning infectious disease outbreak detection system
Tests data generation, preprocessing, model training, aggregation, and outbreak detection
"""

import unittest
import numpy as np
import pandas as pd
from utils.data_generator import EpidemiologicalDataGenerator
from utils.preprocessing import EpidemiologicalDataProcessor
from models.clinic_model import InfectionRiskDetectionModel
from federated_learning.aggregator import FederatedOutbreakAggregator, ConsolidatedOutbreakDetectionModel
from utils.outbreak_detection import OutbreakDetectionEngine
from config import CLINICS, INFECTION_RISK_LEVELS


class TestEpidemiologicalDataGeneration(unittest.TestCase):
    """Test epidemiological data generation for outbreak detection"""
    
    def setUp(self):
        self.generator = EpidemiologicalDataGenerator(seed=42)
    
    def test_clinic_data_shape(self):
        """Test that generated data has correct shape"""
        df = self.generator.generate_clinic_data('Clinic_A', n_samples=100)
        self.assertEqual(len(df), 100)
        self.assertIn('infection_risk', df.columns)
        self.assertIn('vaccination_status', df.columns)
        self.assertIn('proximity_to_confirmed', df.columns)
        self.assertIn('travel_history', df.columns)
    
    def test_all_clinics_generation(self):
        """Test generation for all three clinic archetypes"""
        clinic_data = self.generator.generate_all_clinics(n_samples=100)
        self.assertEqual(len(clinic_data), 3)
        for df in clinic_data:
            self.assertEqual(len(df), 100)
    
    def test_infection_risk_range(self):
        """Test that infection risk levels are in valid range"""
        df = self.generator.generate_clinic_data('Clinic_A', n_samples=100)
        self.assertTrue(df['infection_risk'].min() >= 0)
        self.assertTrue(df['infection_risk'].max() <= 3)
    
    def test_vaccination_status_values(self):
        """Test vaccination status has valid values"""
        df = self.generator.generate_clinic_data('Clinic_A', n_samples=100)
        valid_statuses = [0, 1, 2, 3]  # Unvaccinated, Partial, Full, Boosted
        self.assertTrue(all(v in valid_statuses for v in df['vaccination_status'].unique()))
    
    def test_outbreak_cluster_detection(self):
        """Test that outbreak clusters are detected in generated data"""
        df = self.generator.generate_clinic_data('Clinic_A', n_samples=500)
        has_clusters = (df['in_outbreak_cluster'] == 1).sum() > 0
        # With enough samples, should detect at least some clusters
        self.assertTrue(has_clusters or len(df) < 100)
    
    def test_temporal_data_generation(self):
        """Test that temporal data (dates) is generated"""
        df = self.generator.generate_clinic_data('Clinic_A', n_samples=100)
        self.assertIn('date', df.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['date']))


class TestEpidemiologicalDataPreprocessing(unittest.TestCase):
    """Test data preprocessing for outbreak detection"""
    
    def setUp(self):
        self.generator = EpidemiologicalDataGenerator(seed=42)
        self.processor = EpidemiologicalDataProcessor()
        self.df = self.generator.generate_clinic_data('Clinic_A', n_samples=100)
    
    def test_preprocessing_output_type(self):
        """Test preprocessing returns numpy arrays"""
        processed = self.processor.preprocess_data(self.df)
        self.assertIsInstance(processed['X_train'], np.ndarray)
        self.assertIsInstance(processed['y_train'], np.ndarray)
    
    def test_temporal_column_handling(self):
        """Test that temporal columns are properly handled"""
        processed = self.processor.preprocess_data(self.df)
        # Date column should be removed from features
        self.assertNotIn('date', processed['feature_names'])
    
    def test_infection_risk_target(self):
        """Test that infection_risk is used as target"""
        processed = self.processor.preprocess_data(self.df)
        # Target should be infection_risk values (0-3)
        self.assertTrue(all(y in [0, 1, 2, 3] for y in processed['y_train']))
        self.assertTrue(all(y in [0, 1, 2, 3] for y in processed['y_test']))
    
    def test_data_split_sizes(self):
        """Test that data split produces correct sizes"""
        processed = self.processor.preprocess_data(self.df)
        X_train = processed['X_train']
        X_test = processed['X_test']
        
        total_size = len(X_train) + len(X_test)
        self.assertEqual(total_size, len(self.df))


class TestInfectionRiskDetectionModel(unittest.TestCase):
    """Test infection risk detection models for individual clinics"""
    
    def setUp(self):
        self.generator = EpidemiologicalDataGenerator(seed=42)
        self.processor = EpidemiologicalDataProcessor()
        self.df = self.generator.generate_clinic_data('Clinic_A', n_samples=200)
        
        processed = self.processor.preprocess_data(self.df)
        
        self.model = InfectionRiskDetectionModel(
            clinic_name='Clinic_A',
            clinic_type='urban'
        )
        self.model.train(
            processed['X_train'],
            processed['y_train'],
            processed['X_test'],  # Using test as validation
            processed['y_test']
        )
        self.X_test = processed['X_test']
        self.y_test = processed['y_test']
    
    def test_model_training(self):
        """Test that model trains successfully"""
        self.assertTrue(self.model.is_trained)
    
    def test_model_prediction_shape(self):
        """Test prediction output shape"""
        predictions = self.model.predict(self.X_test)
        self.assertEqual(len(predictions), len(self.X_test))
    
    def test_model_prediction_range(self):
        """Test predictions are in valid infection risk range"""
        predictions = self.model.predict(self.X_test)
        self.assertTrue(np.all(predictions >= 0))
        self.assertTrue(np.all(predictions <= 3))
    
    def test_model_probability_predictions(self):
        """Test probability predictions for each risk level"""
        probas = self.model.predict_proba(self.X_test)
        self.assertEqual(probas.shape[0], len(self.X_test))
        self.assertEqual(probas.shape[1], 4)  # Four infection risk levels
        # Probabilities should sum to 1
        self.assertTrue(np.allclose(probas.sum(axis=1), 1))
    
    def test_model_evaluation(self):
        """Test model evaluation metrics"""
        metrics = self.model.evaluate(self.X_test, self.y_test)
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1', metrics)
        self.assertIn('auc', metrics)
        self.assertTrue(0 <= metrics['accuracy'] <= 1)


class TestFederatedOutbreakAggregation(unittest.TestCase):
    """Test federated learning aggregation for outbreak detection"""
    
    def setUp(self):
        self.generator = EpidemiologicalDataGenerator(seed=42)
        self.processor = EpidemiologicalDataProcessor()
        self.aggregator = FederatedOutbreakAggregator(aggregation_method='weighted_average')
        
        # Create and train clinic models
        self.clinic_models = {}
        self.clinic_sizes = {}
        
        clinic_list = [c['name'] for c in CLINICS]
        clinic_types = [c['location_type'] for c in CLINICS]
        
        for clinic_name, clinic_type in zip(clinic_list, clinic_types):
            df = self.generator.generate_clinic_data(clinic_name, n_samples=100)
            processed = self.processor.preprocess_data(df)
            
            model = InfectionRiskDetectionModel(
                clinic_name=clinic_name,
                clinic_type=clinic_type
            )
            model.train(
                processed['X_train'],
                processed['y_train'],
                processed['X_test'],
                processed['y_test']
            )
            
            self.clinic_models[clinic_name] = model
            self.clinic_sizes[clinic_name] = len(df)
            self.aggregator.register_clinic(clinic_name, model)
    
    def test_aggregator_clinic_registration(self):
        """Test that clinics are properly registered"""
        self.assertEqual(len(self.aggregator.clinic_models), 3)
    
    def test_aggregation_process(self):
        """Test aggregation produces model weights"""
        aggregated_weights = self.aggregator.aggregate_models(self.clinic_sizes)
        self.assertIsNotNone(aggregated_weights)
    
    def test_outbreak_signal_detection(self):
        """Test outbreak signal detection at population level"""
        high_risk_percentages = {
            'Clinic_A': 0.18,
            'Clinic_B': 0.10,
            'Clinic_C': 0.25
        }
        
        signals = self.aggregator.detect_outbreak_signals(high_risk_percentages, threshold=0.15)
        
        # Clinic_A and Clinic_C should trigger signals
        self.assertGreater(len(signals), 0)
        signal_clinics = [s['clinic'] for s in signals]
        self.assertIn('Clinic_A', signal_clinics)
        self.assertIn('Clinic_C', signal_clinics)


class TestConsolidatedOutbreakEnsemble(unittest.TestCase):
    """Test consolidated ensemble model for outbreak detection"""
    
    def setUp(self):
        self.generator = EpidemiologicalDataGenerator(seed=42)
        self.processor = EpidemiologicalDataProcessor()
        self.aggregator = FederatedOutbreakAggregator()
        
        # Create clinic models and data
        self.clinic_models = {}
        self.clinic_data = {}
        self.clinic_sizes = {}
        
        clinic_list = [c['name'] for c in CLINICS]
        clinic_types = [c['location_type'] for c in CLINICS]
        
        for clinic_name, clinic_type in zip(clinic_list, clinic_types):
            df = self.generator.generate_clinic_data(clinic_name, n_samples=100)
            processed = self.processor.preprocess_data(df)
            
            model = InfectionRiskDetectionModel(
                clinic_name=clinic_name,
                clinic_type=clinic_type
            )
            model.train(
                processed['X_train'],
                processed['y_train'],
                processed['X_test'],
                processed['y_test']
            )
            
            self.clinic_models[clinic_name] = model
            self.clinic_data[clinic_name] = processed
            self.clinic_sizes[clinic_name] = len(df)
            self.aggregator.register_clinic(clinic_name, model)
        
        # Create consolidated ensemble
        self.ensemble = ConsolidatedOutbreakDetectionModel(self.clinic_models)
    
    def test_ensemble_prediction_shape(self):
        """Test ensemble prediction shape"""
        test_data = self.clinic_data['Clinic_A']
        predictions, probas, confidence = self.ensemble.predict_ensemble(test_data['X_test'])
        
        self.assertEqual(len(predictions), len(test_data['X_test']))
        self.assertEqual(probas.shape[0], len(test_data['X_test']))
        self.assertEqual(probas.shape[1], 4)  # Four infection risk levels
        self.assertEqual(len(confidence), len(test_data['X_test']))
    
    def test_ensemble_probability_validity(self):
        """Test ensemble probabilities are valid"""
        test_data = self.clinic_data['Clinic_A']
        predictions, probas, confidence = self.ensemble.predict_ensemble(test_data['X_test'])
        
        # Probabilities should sum to 1
        self.assertTrue(np.allclose(probas.sum(axis=1), 1))
        
        # Confidence should be between 0 and 1
        self.assertTrue(np.all(confidence >= 0))
        self.assertTrue(np.all(confidence <= 1))
    
    def test_ensemble_evaluation(self):
        """Test ensemble evaluation metrics"""
        test_data = self.clinic_data['Clinic_A']
        metrics = self.ensemble.evaluate_ensemble(
            test_data['X_test'],
            test_data['y_test']
        )
        
        self.assertIn('accuracy', metrics)
        self.assertIn('recall', metrics)  # Important for outbreak detection
        self.assertTrue(0 <= metrics['accuracy'] <= 1)
        self.assertTrue(0 <= metrics['recall'] <= 1)


class TestOutbreakDetectionEngine(unittest.TestCase):
    """Test outbreak detection engine"""
    
    def setUp(self):
        # Create a simple ensemble model for testing
        self.generator = EpidemiologicalDataGenerator(seed=42)
        self.processor = EpidemiologicalDataProcessor()
        
        clinic_list = [c['name'] for c in CLINICS]
        clinic_types = [c['location_type'] for c in CLINICS]
        
        self.clinic_models = {}
        for clinic_name, clinic_type in zip(clinic_list, clinic_types):
            df = self.generator.generate_clinic_data(clinic_name, n_samples=100)
            processed = self.processor.preprocess_data(df)
            
            model = InfectionRiskDetectionModel(
                clinic_name=clinic_name,
                clinic_type=clinic_type
            )
            model.train(processed['X_train'], processed['y_train'])
            
            self.clinic_models[clinic_name] = model
        
        ensemble = ConsolidatedOutbreakDetectionModel(self.clinic_models)
        self.engine = OutbreakDetectionEngine(ensemble)
    
    def test_patient_risk_assessment(self):
        """Test patient infection risk assessment"""
        patient_features = {
            'age': 45,
            'fever': 1,
            'cough': 1,
            'shortness_of_breath': 0,
            'loss_of_taste_smell': 0,
            'respiratory_distress': 0,
            'vaccination_status': 2,
            'proximity_to_confirmed': 0,
            'travel_history': 1,
            'days_symptomatic': 2,
            'age_group': 2,
            'comorbidities': 0
        }
        
        assessment = self.engine.assess_patient(patient_features)
        
        self.assertIn('infection_risk', assessment)
        self.assertIn('epidemiological_risk', assessment)
        self.assertIn('risk_factors', assessment)
    
    def test_high_risk_patient_detection(self):
        """Test detection of high-risk patient with contact tracing"""
        patient_features = {
            'age': 65,
            'fever': 1,
            'cough': 1,
            'shortness_of_breath': 1,
            'loss_of_taste_smell': 1,  # KEY INDICATOR
            'respiratory_distress': 0,
            'vaccination_status': 0,  # Unvaccinated
            'proximity_to_confirmed': 2,  # Direct contact with confirmed case
            'travel_history': 0,
            'days_symptomatic': 4,
            'age_group': 3,
            'comorbidities': 1
        }
        
        assessment = self.engine.assess_patient(patient_features)
        
        # Should detect as high-risk due to multiple indicators
        self.assertGreaterEqual(assessment['infection_risk'], 2)
    
    def test_outbreak_report_generation(self):
        """Test that report generation produces valid outbreak assessment"""
        patient_features = {
            'age': 50,
            'fever': 1,
            'cough': 1,
            'shortness_of_breath': 0,
            'loss_of_taste_smell': 0,
            'respiratory_distress': 0,
            'vaccination_status': 1,
            'proximity_to_confirmed': 1,
            'travel_history': 0,
            'days_symptomatic': 2,
            'age_group': 2,
            'comorbidities': 0
        }
        
        assessment = self.engine.assess_patient(patient_features)
        report = self.engine.generate_assessment_report(
            patient_features,
            assessment,
            'Urban Center'
        )
        
        self.assertIsInstance(report, str)
        self.assertIn('INFECTION RISK ASSESSMENT', report)


def run_tests():
    """Run all unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestEpidemiologicalDataGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestEpidemiologicalDataPreprocessing))
    suite.addTests(loader.loadTestsFromTestCase(TestInfectionRiskDetectionModel))
    suite.addTests(loader.loadTestsFromTestCase(TestFederatedOutbreakAggregation))
    suite.addTests(loader.loadTestsFromTestCase(TestConsolidatedOutbreakEnsemble))
    suite.addTests(loader.loadTestsFromTestCase(TestOutbreakDetectionEngine))
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == '__main__':
    run_tests()
