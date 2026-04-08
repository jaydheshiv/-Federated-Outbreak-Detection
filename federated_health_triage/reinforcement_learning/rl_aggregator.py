"""
Reinforcement Learning Module for Federated Outbreak Detection
Implements multi-model RL-based aggregation with dynamic learner selection
Uses Thompson Sampling for model selection and meta-learning for consolidation
"""

import numpy as np
import joblib
import os
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import logging

logger = logging.getLogger(__name__)


class ThompsonSamplingBandit:
    """
    Thompson Sampling Bandit for model selection
    Learns which model is best for each clinic over time
    """
    
    def __init__(self, n_arms: int = 3, alpha: float = 1.0, beta: float = 1.0):
        """
        Args:
            n_arms: Number of models to choose from (3)
            alpha: Beta distribution alpha parameter
            beta: Beta distribution beta parameter
        """
        self.n_arms = n_arms
        self.alphas = np.ones(n_arms) * alpha
        self.betas = np.ones(n_arms) * beta
        self.successes = np.zeros(n_arms)
        self.failures = np.zeros(n_arms)
        self.total_trials = 0
    
    def select_arm(self) -> int:
        """Thompson Sampling: sample from Beta distribution for each arm"""
        samples = np.random.beta(self.alphas, self.betas)
        return np.argmax(samples)
    
    def update(self, arm: int, reward: float):
        """
        Update bandit with observed reward
        
        Args:
            arm: Selected model index
            reward: Performance metric (0-1, where 1 is best)
        """
        if reward > 0.5:  # Success threshold
            self.successes[arm] += 1
            self.alphas[arm] += 1
        else:
            self.failures[arm] += 1
            self.betas[arm] += 1
        
        self.total_trials += 1
    
    def get_arm_weights(self) -> np.ndarray:
        """Get current weight for each arm based on performance"""
        successes = self.successes + 1  # Add 1 to avoid division by zero
        total = successes + self.failures + 2
        return successes / total


class ClinicRLModel:
    """
    Reinforcement Learning Model for a single clinic
    Trains three different models and uses RL to select/weight them
    """
    
    def __init__(self, clinic_name: str, clinic_type: str, random_state: int = 42):
        """
        Initialize clinic RL model with three learners
        
        Args:
            clinic_name: Name of the clinic (e.g., 'Clinic_A')
            clinic_type: Type of clinic (Urban, Rural, Travel Hub)
            random_state: Random seed for reproducibility
        """
        self.clinic_name = clinic_name
        self.clinic_type = clinic_type
        self.random_state = random_state
        
        # Initialize three different models
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=-1,
                class_weight='balanced'
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=7,
                random_state=random_state,
                verbose=0
            ),
            'mlp': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                max_iter=500,
                random_state=random_state,
                early_stopping=True,
                validation_fraction=0.1,
                verbose=0
            )
        }
        
        # Thompson Sampling bandit for model selection
        self.bandit = ThompsonSamplingBandit(n_arms=3)
        
        # Performance history
        self.model_performance = {
            'random_forest': [],
            'gradient_boosting': [],
            'mlp': []
        }
        
        # Training state
        self.is_trained = False
        self.best_model_name = None
        self.n_features = None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray):
        """
        Train all three models and use RL to determine best weighting
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
        """
        print(f"\n{'='*70}")
        print(f"RL TRAINING: {self.clinic_name} ({self.clinic_type})")
        print(f"{'='*70}")
        print(f"Training data: {len(X_train)} samples")
        print(f"Validation data: {len(X_val)} samples\n")
        
        self.n_features = X_train.shape[1]
        
        # Train each model
        model_names = list(self.models.keys())
        
        for model_name, model in self.models.items():
            print(f"  Training {model_name}...")
            
            # Train
            model.fit(X_train, y_train)
            
            # Evaluate on validation set
            val_preds = model.predict(X_val)
            val_proba = model.predict_proba(X_val)
            
            # Calculate metrics
            accuracy = accuracy_score(y_val, val_preds)
            recall = recall_score(y_val, val_preds, average='weighted', zero_division=0)
            f1 = f1_score(y_val, val_preds, average='weighted', zero_division=0)
            
            # Use F1 as reward for bandit
            reward = f1  # Normalize to 0-1 range
            
            # Update bandit
            arm_idx = model_names.index(model_name)
            self.bandit.update(arm_idx, reward)
            
            # Store performance
            self.model_performance[model_name] = {
                'accuracy': accuracy,
                'recall': recall,
                'f1': f1
            }
            
            print(f"    Accuracy: {accuracy:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        # Determine best model based on F1 score
        best_model_idx = np.argmax([
            self.model_performance[name]['f1'] for name in model_names
        ])
        self.best_model_name = model_names[best_model_idx]
        
        print(f"\n  ✓ Best individual model: {self.best_model_name}")
        
        # Get RL weights for ensemble voting
        rl_weights = self.bandit.get_arm_weights()
        print(f"  RL Model Weights: RF={rl_weights[0]:.3f}, GB={rl_weights[1]:.3f}, MLP={rl_weights[2]:.3f}")
        
        self.is_trained = True
    
    def predict(self, X: np.ndarray, use_ensemble: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions using ensemble or best model
        
        Args:
            X: Input features
            use_ensemble: If True, use weighted ensemble; else use best model
        
        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.is_trained:
            raise ValueError(f"{self.clinic_name} not trained yet")
        
        if use_ensemble:
            # Use RL weighted ensemble
            rl_weights = self.bandit.get_arm_weights()
            rl_weights = rl_weights / np.sum(rl_weights)  # Normalize
            
            ensemble_proba = np.zeros_like(self.models['random_forest'].predict_proba(X))
            
            for (model_name, model), weight in zip(self.models.items(), rl_weights):
                proba = model.predict_proba(X)
                ensemble_proba += weight * proba
            
            predictions = np.argmax(ensemble_proba, axis=1)
            return predictions, ensemble_proba
        else:
            # Use best individual model
            model = self.models[self.best_model_name]
            predictions = model.predict(X)
            probabilities = model.predict_proba(X)
            return predictions, probabilities
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate all models and ensemble"""
        predictions, probabilities = self.predict(X_test, use_ensemble=True)
        
        metrics = {
            'accuracy': accuracy_score(y_test, predictions),
            'recall': recall_score(y_test, predictions, average='weighted', zero_division=0),
            'precision': precision_score(y_test, predictions, average='weighted', zero_division=0),
            'f1': f1_score(y_test, predictions, average='weighted', zero_division=0)
        }
        
        try:
            metrics['auc'] = roc_auc_score(y_test, probabilities, multi_class='ovr', labels=np.arange(4))
        except:
            metrics['auc'] = 0.0
        
        return metrics
    
    def get_model_probabilities(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """Get individual model probabilities for consolidation"""
        model_probs = {}
        for model_name, model in self.models.items():
            model_probs[model_name] = model.predict_proba(X)
        return model_probs


class FederatedRLAggregator:
    """
    Federated aggregation with Reinforcement Learning
    Consolidates predictions from all three clinics' RL models
    Uses meta-learning to optimize consolidation
    """
    
    def __init__(self, clinic_models: Dict[str, ClinicRLModel]):
        """
        Args:
            clinic_models: Dictionary of clinic name -> ClinicRLModel
        """
        self.clinic_models = clinic_models
        self.clinic_names = list(clinic_models.keys())
        self.n_clinics = len(clinic_models)
        
        # Meta-learner for consolidation
        self.meta_learner = None
        self.consolidation_weights = None
        self.feature_importances = None
    
    def train_meta_learner(self, X_combined: np.ndarray, y_combined: np.ndarray,
                          val_split: float = 0.2):
        """
        Train a meta-learner that consolidates outputs from all clinic models
        
        Args:
            X_combined: Combined features from all clinics
            y_combined: Combined labels from all clinics
            val_split: Validation split ratio
        """
        print(f"\n{'='*70}")
        print("TRAINING META-LEARNER FOR CONSOLIDATION")
        print(f"{'='*70}")
        
        # Generate predictions from each clinic model
        print("\nGenerating consolidated feature set from clinic models...")
        
        consolidated_features = []
        clinic_predictions = {clinic: None for clinic in self.clinic_names}
        
        for clinic_name, clinic_model in self.clinic_models.items():
            if not clinic_model.is_trained:
                raise ValueError(f"{clinic_name} not trained")
            
            predictions, probabilities = clinic_model.predict(X_combined, use_ensemble=True)
            clinic_predictions[clinic_name] = probabilities
            
            # Use class probabilities as features for meta-learner
            consolidated_features.append(probabilities)
            print(f"  ✓ {clinic_name}: Generated {probabilities.shape[1]} probability features")
        
        # Stack all clinic predictions
        X_meta = np.hstack(consolidated_features)
        print(f"\nMeta-learner input shape: {X_meta.shape}")
        
        # Train meta-learner using a simple XGBoost or Neural Network
        try:
            from xgboost import XGBClassifier
            self.meta_learner = XGBClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=7,
                random_state=42,
                verbose=0
            )
        except ImportError:
            # Fallback to Gradient Boosting
            from sklearn.ensemble import GradientBoostingClassifier
            self.meta_learner = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=7,
                random_state=42
            )
        
        print(f"Training meta-learner...")
        self.meta_learner.fit(X_meta, y_combined)
        
        # Calculate consolidation weights based on clinic importance
        if hasattr(self.meta_learner, 'feature_importances_'):
            importances = self.meta_learner.feature_importances_
            
            # Group importances by clinic
            n_classes = consolidated_features[0].shape[1]
            clinic_weights = {}
            
            start_idx = 0
            for clinic_name in self.clinic_names:
                end_idx = start_idx + n_classes
                clinic_importance = np.sum(importances[start_idx:end_idx])
                clinic_weights[clinic_name] = clinic_importance
                start_idx = end_idx
            
            # Normalize weights
            total_importance = sum(clinic_weights.values())
            self.consolidation_weights = {
                clinic: weight / total_importance 
                for clinic, weight in clinic_weights.items()
            }
            
            print(f"\nConsolidation Weights (learned by meta-learner):")
            for clinic, weight in self.consolidation_weights.items():
                print(f"  {clinic}: {weight:.4f}")
        
        print(f"\n✓ Meta-learner trained successfully!")
    
    def predict_consolidated(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make consolidated predictions using meta-learner
        
        Args:
            X: Input features
        
        Returns:
            Tuple of (predictions, probabilities)
        """
        if self.meta_learner is None:
            raise ValueError("Meta-learner not trained yet. Call train_meta_learner first.")
        
        # Get predictions from each clinic model
        consolidated_features = []
        
        for clinic_name in self.clinic_names:
            clinic_model = self.clinic_models[clinic_name]
            _, probabilities = clinic_model.predict(X, use_ensemble=True)
            consolidated_features.append(probabilities)
        
        # Stack and predict with meta-learner
        X_meta = np.hstack(consolidated_features)
        predictions = self.meta_learner.predict(X_meta)
        probabilities = self.meta_learner.predict_proba(X_meta)
        
        return predictions, probabilities
    
    def evaluate_consolidated(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate consolidated model"""
        predictions, probabilities = self.predict_consolidated(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, predictions),
            'recall': recall_score(y_test, predictions, average='weighted', zero_division=0),
            'precision': precision_score(y_test, predictions, average='weighted', zero_division=0),
            'f1': f1_score(y_test, predictions, average='weighted', zero_division=0)
        }
        
        try:
            metrics['auc'] = roc_auc_score(y_test, probabilities, multi_class='ovr', labels=np.arange(4))
        except:
            metrics['auc'] = 0.0
        
        return metrics
    
    def compare_models(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Compare performance of individual clinic models vs consolidated model
        """
        comparison = {
            'individual_clinics': {},
            'consolidated': self.evaluate_consolidated(X_test, y_test)
        }
        
        for clinic_name, clinic_model in self.clinic_models.items():
            comparison['individual_clinics'][clinic_name] = clinic_model.evaluate(X_test, y_test)
        
        return comparison


if __name__ == "__main__":
    print("Reinforcement Learning Module for Federated Outbreak Detection")
    print("Ready to use in training pipeline")
