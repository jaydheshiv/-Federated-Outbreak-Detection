"""
Federated outbreak detection aggregator
Combines models from multiple clinics while preserving privacy
Detects population-level outbreak patterns
"""

import numpy as np
import os
from typing import Dict, List
from models.clinic_model import InfectionRiskDetectionModel
from config import CLINICS, AGGREGATION_METHOD


class FederatedOutbreakAggregator:
    """
    Aggregates infection risk models from multiple clinics
    Enables outbreak detection across distributed healthcare facilities
    """
    
    def __init__(self, aggregation_method='weighted_average'):
        self.aggregation_method = aggregation_method
        self.clinic_models: Dict[str, InfectionRiskDetectionModel] = {}
        self.aggregated_weights = None
        self.training_rounds = 0
        self.round_history = []
        self.outbreak_signals = []
        
    def register_clinic(self, clinic_name: str, model: InfectionRiskDetectionModel):
        """Register a clinic's infection risk detection model"""
        self.clinic_models[clinic_name] = model
        print(f"Registered {model.clinic_name} ({model.clinic_type})")
    
    def aggregate_models(self, clinic_sizes: Dict[str, int]):
        """
        Aggregate feature importances from clinic models
        Uses privacy-preserving weighted averaging
        """
        if not self.clinic_models:
            raise ValueError("No clinic models registered")
        
        # Extract feature importances from all models
        all_importances = {}
        total_size = sum(clinic_sizes.values())
        
        for clinic_name, model in self.clinic_models.items():
            importances = model.get_feature_importance([])
            if importances:
                all_importances[clinic_name] = importances
        
        if not all_importances:
            print("Warning: No feature importances available for aggregation")
            return None
        
        # Aggregate based on method
        if self.aggregation_method == 'weighted_average':
            aggregated = self._weighted_average_aggregation(all_importances, clinic_sizes)
        elif self.aggregation_method == 'median':
            aggregated = self._median_aggregation(all_importances)
        else:
            aggregated = self._simple_average_aggregation(all_importances)
        
        self.aggregated_weights = aggregated
        self.training_rounds += 1
        self.round_history.append(aggregated.copy())
        
        print(f"\nFederated Aggregation Complete:")
        print(f"  Method: {self.aggregation_method}")
        print(f"  Clinics aggregated: {len(self.clinic_models)}")
        print(f"  Population size: {total_size}")
        
        return aggregated
    
    def _weighted_average_aggregation(self, all_importances, clinic_sizes):
        """Weighted average based on clinic patient volume"""
        total_size = sum(clinic_sizes.values())
        aggregated = None
        
        for clinic_name, importances in all_importances.items():
            if importances:
                importance_values = np.array([imp[1] for imp in importances])
                weight = clinic_sizes.get(clinic_name, 1) / total_size
                
                if aggregated is None:
                    aggregated = importance_values * weight
                else:
                    aggregated += importance_values * weight
        
        return aggregated if aggregated is not None else np.array([])
    
    def _simple_average_aggregation(self, all_importances):
        """Simple average aggregation"""
        aggregated = None
        count = 0
        
        for clinic_name, importances in all_importances.items():
            if importances:
                importance_values = np.array([imp[1] for imp in importances])
                if aggregated is None:
                    aggregated = importance_values
                else:
                    aggregated += importance_values
                count += 1
        
        return aggregated / count if aggregated is not None else np.array([])
    
    def _median_aggregation(self, all_importances):
        """Median aggregation (robust to outliers)"""
        all_importance_arrays = []
        
        for clinic_name, importances in all_importances.items():
            if importances:
                importance_values = np.array([imp[1] for imp in importances])
                all_importance_arrays.append(importance_values)
        
        if all_importance_arrays:
            stacked = np.array(all_importance_arrays)
            return np.median(stacked, axis=0)
        
        return np.array([])
    
    def detect_outbreak_signals(self, high_risk_percentages: Dict[str, float], threshold=0.15):
        """
        Detect outbreak signals from clinic-level high-risk patient percentages
        threshold: percentage of high-risk patients to trigger alert
        """
        alerts = []
        
        for clinic_name, percentage in high_risk_percentages.items():
            if percentage >= threshold:
                alert = {
                    'clinic': clinic_name,
                    'high_risk_percentage': percentage,
                    'alert_level': 'HIGH' if percentage >= 0.25 else 'MODERATE',
                    'timestamp': np.datetime64('today'),
                    'action': 'Increase surveillance and testing' if percentage >= threshold else 'Monitor'
                }
                alerts.append(alert)
                self.outbreak_signals.append(alert)
                
                print(f"\n⚠️  OUTBREAK SIGNAL DETECTED at {clinic_name}")
                print(f"   High-risk patients: {percentage:.1%}")
                print(f"   Alert Level: {alert['alert_level']}")
        
        return alerts
    
    def get_aggregated_model_info(self):
        """Get information about aggregated model"""
        return {
            'aggregation_method': self.aggregation_method,
            'training_rounds': self.training_rounds,
            'num_clinics': len(self.clinic_models),
            'clinic_names': list(self.clinic_models.keys()),
            'outbreak_signals_detected': len(self.outbreak_signals)
        }
    
    def get_round_history(self):
        """Get aggregation history across rounds"""
        return self.round_history


class ConsolidatedOutbreakDetectionModel:
    """
    Consolidated ensemble model combining predictions from all clinics
    Focuses on detecting high-risk patients and outbreak patterns
    """
    
    def __init__(self, clinic_models: Dict[str, InfectionRiskDetectionModel], aggregation_weights=None):
        self.clinic_models = clinic_models
        self.aggregation_weights = aggregation_weights
        self.ensemble_auc = None
        
    def predict_ensemble(self, X):
        """
        Ensemble predictions using all clinic models
        Implements soft voting via probability averaging
        """
        n_samples = len(X)
        n_classes = 4  # Risk levels 0-3
        
        # Collect predictions from all clinics
        all_predictions = {}
        n_classes = 4  # infection_risk has 4 levels (0-3)
        
        for clinic_name, model in self.clinic_models.items():
            try:
                proba = model.predict_proba(X)
                # Ensure all models output same number of classes
                if proba.shape[1] < n_classes:
                    # Pad with zeros for missing classes
                    padded_proba = np.zeros((proba.shape[0], n_classes))
                    padded_proba[:, :proba.shape[1]] = proba
                    # Renormalize to sum to 1
                    padded_proba /= padded_proba.sum(axis=1, keepdims=True)
                    proba = padded_proba
                all_predictions[clinic_name] = proba
            except Exception as e:
                print(f"Warning: Could not get predictions from {clinic_name}: {e}")
        
        if not all_predictions:
            raise ValueError("No valid predictions from clinics")
        
        # Average probability predictions (soft voting)
        avg_proba = None
        for clinic_name, proba in all_predictions.items():
            if avg_proba is None:
                avg_proba = proba.copy()
            else:
                avg_proba += proba
        
        avg_proba /= len(all_predictions)
        
        # Get predicted risk level
        ensemble_predictions = np.argmax(avg_proba, axis=1)
        ensemble_confidence = np.max(avg_proba, axis=1)
        
        return ensemble_predictions, avg_proba, ensemble_confidence
    
    def evaluate_ensemble(self, X_test, y_test):
        """Evaluate ensemble performance"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        predictions, probas, confidence = self.predict_ensemble(X_test)
        
        try:
            auc = roc_auc_score(y_test, probas[:, 1:].max(axis=1), multi_class='ovr')
        except:
            auc = 0.0
        
        metrics = {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, average='weighted', zero_division=0),
            'recall': recall_score(y_test, predictions, average='weighted', zero_division=0),
            'f1': f1_score(y_test, predictions, average='weighted', zero_division=0),
            'auc': auc
        }
        
        self.ensemble_auc = auc
        
        print("\nConsolidated Outbreak Detection Model Test Metrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f} (Critical for outbreak detection)")
        print(f"  F1 Score:  {metrics['f1']:.4f}")
        print(f"  AUC:       {metrics['auc']:.4f}")
        
        # High-risk detection rate
        high_risk_actual = np.sum(y_test >= 2)
        if high_risk_actual > 0:
            high_risk_detected = np.sum((predictions >= 2) & (y_test >= 2))
            detection_rate = high_risk_detected / high_risk_actual
            print(f"  High-Risk Detection Rate: {detection_rate:.2%} ({high_risk_detected}/{high_risk_actual})")
        
        return metrics
    
    def compare_individual_vs_ensemble(self, X_test, y_test):
        """Compare individual clinic models with ensemble"""
        from sklearn.metrics import accuracy_score
        
        print("\n" + "="*70)
        print("FEDERATED CLINICS VS CONSOLIDATED ENSEMBLE COMPARISON")
        print("="*70)
        
        results = {}
        
        # Individual clinic accuracies
        for clinic_name, model in self.clinic_models.items():
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            results[clinic_name] = accuracy
            print(f"{clinic_name:20} Accuracy: {accuracy:.4f}")
        
        # Ensemble accuracy
        ensemble_preds, _, _ = self.predict_ensemble(X_test)
        ensemble_acc = accuracy_score(y_test, ensemble_preds)
        results['ensemble'] = ensemble_acc
        
        print("-" * 70)
        print(f"{'Consolidated Ensemble':20} Accuracy: {ensemble_acc:.4f}")
        print("-" * 70)
        
        # Calculate improvement
        base_accuracy = np.mean(list(results.values())[:-1])
        improvement = ensemble_acc - base_accuracy
        improvement_pct = (improvement / base_accuracy * 100) if base_accuracy > 0 else 0
        
        print(f"Average Individual Accuracy: {base_accuracy:.4f}")
        print(f"Ensemble Improvement: +{improvement:.4f} ({improvement_pct:.2f}%)")
        print("="*70 + "\n")
        
        return results

