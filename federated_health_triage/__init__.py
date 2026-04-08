"""
Federated Health Triage System
AI-integrated federated learning for healthcare triage
"""

__version__ = '1.0.0'
__author__ = 'Health AI Lab'

from utils.data_generator import HealthDataGenerator
from utils.preprocessing import HealthDataProcessor, prepare_clinic_data
from models.clinic_model import ClinicModel
from federated_learning.aggregator import FederatedAggregator, ConsolidatedTriageModel
from utils.triage_engine import TriageAssessmentEngine
from train import FederatedHealthTriageTrainer
