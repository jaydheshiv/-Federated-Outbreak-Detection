"""
Data preprocessing utilities for epidemiological data
Handles infectious disease data with temporal and categorical features
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from config import SYMPTOMS, TEST_SIZE, VAL_SIZE, RANDOM_SEED


class EpidemiologicalDataProcessor:
    """Process epidemiological data for model training"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def preprocess_data(self, df, fit_scaler=True):
        """
        Preprocess epidemiological data
        - Handle temporal features
        - Encode categorical variables
        - Scale numerical features
        """
        # Separate target variable
        X = df.drop(['infection_risk', 'clinic', 'date', 'clinic_type', 'in_outbreak_cluster'], 
                    axis=1, errors='ignore')
        y = df['infection_risk'].values
        
        # Encode categorical variables
        categorical_cols = ['gender']
        for col in categorical_cols:
            if col in X.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    X[col] = self.label_encoders[col].fit_transform(X[col])
                else:
                    X[col] = self.label_encoders[col].transform(X[col])
        
        # Convert to numpy
        X = X.values.astype(float)
        
        # Scale features
        if fit_scaler:
            X = self.scaler.fit_transform(X)
        else:
            X = self.scaler.transform(X)
        
        return X, y
    
    def split_data(self, X, y, test_size=TEST_SIZE, val_size=VAL_SIZE, random_state=RANDOM_SEED):
        """
        Split data into train, validation, and test sets
        """
        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Second split: train vs val
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=random_state, stratify=y_temp
        )
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def get_feature_names(self, df):
        """Get feature names for interpretation"""
        return df.drop(['infection_risk', 'clinic', 'date', 'clinic_type', 'in_outbreak_cluster'], 
                       axis=1, errors='ignore').columns.tolist()


def prepare_clinic_data(clinic_df, processor=None):
    """
    Prepare a single clinic's epidemiological data for training
    Returns preprocessed features, labels, and metadata
    """
    if processor is None:
        processor = EpidemiologicalDataProcessor()
    
    X, y = processor.preprocess_data(clinic_df, fit_scaler=True)
    X_train, X_val, X_test, y_train, y_val, y_test = processor.split_data(X, y)
    
    return {
        'X_train': X_train, 'X_val': X_val, 'X_test': X_test,
        'y_train': y_train, 'y_val': y_val, 'y_test': y_test,
        'processor': processor,
        'feature_names': processor.get_feature_names(clinic_df),
        'clinic_name': clinic_df['clinic'].iloc[0] if 'clinic' in clinic_df.columns else 'Unknown',
        'date_range': (clinic_df['date'].min(), clinic_df['date'].max()) if 'date' in clinic_df.columns else None
    }

