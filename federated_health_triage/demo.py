"""
Quick demo script for Federated Health Triage System
Shows basic usage and results
"""

if __name__ == '__main__':
    from train import FederatedHealthTriageTrainer
    
    print("\n" + "="*70)
    print("FEDERATED HEALTH TRIAGE SYSTEM - QUICK DEMO")
    print("="*70 + "\n")
    
    # Initialize trainer with smaller dataset for quick demo
    trainer = FederatedHealthTriageTrainer(n_samples=300)
    
    # Run complete pipeline
    print("Starting training pipeline...")
    results = trainer.run_full_pipeline()
    
    print("\n✓ Demo completed successfully!")
    print("Check 'data/' folder for generated datasets")
    print("Check 'models/' folder for trained models")
    print("Check 'results/' folder for evaluation results")
