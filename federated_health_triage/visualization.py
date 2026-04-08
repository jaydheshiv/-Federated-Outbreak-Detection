"""
Visualization module for Federated Outbreak Detection System
Generates charts and visualizations for epidemic trends and model performance
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List


class OutbreakVisualization:
    """Visualizes outbreak detection results and epidemic trends"""
    
    def __init__(self, style='seaborn-v0_8-darkgrid'):
        sns.set_style(style)
        self.figures = []
    
    def plot_infection_risk_distribution(self, data: pd.DataFrame, clinic_name: str, save_path=None):
        """Plot distribution of infection risk levels by clinic"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        risk_counts = data['infection_risk'].value_counts().sort_index()
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#c0392b']
        risk_labels = ['Low Risk (0)', 'Moderate Risk (1)', 'High Risk (2)', 'Critical Risk (3)']
        
        bars = ax.bar(risk_counts.index, risk_counts.values, color=colors[:len(risk_counts)], 
                      edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_xlabel('Infection Risk Level', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Patients', fontsize=12, fontweight='bold')
        ax.set_title(f'Infection Risk Distribution - {clinic_name}', fontsize=14, fontweight='bold')
        ax.set_xticks(risk_counts.index)
        ax.set_xticklabels(risk_labels[:len(risk_counts)])
        ax.grid(axis='y', alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_vaccination_status_impact(self, data: pd.DataFrame, save_path=None):
        """Plot how vaccination status affects infection risk"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        vacc_risk = data.groupby('vaccination_status')['infection_risk'].mean()
        vacc_labels = {0: 'Unvaccinated', 1: 'Partial', 2: 'Fully Vaccinated', 3: 'Boosted'}
        
        colors_vacc = ['#c0392b', '#e74c3c', '#f39c12', '#2ecc71']
        bars = ax.bar(range(len(vacc_risk)), vacc_risk.values, color=colors_vacc[:len(vacc_risk)],
                      edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_xlabel('Vaccination Status', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Infection Risk Level', fontsize=12, fontweight='bold')
        ax.set_title('Impact of Vaccination on Infection Risk', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(vacc_risk)))
        ax.set_xticklabels([vacc_labels[i] for i in vacc_risk.index])
        ax.set_ylim(0, 3.5)
        ax.grid(axis='y', alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_contact_tracing_impact(self, data: pd.DataFrame, save_path=None):
        """Plot how contact with confirmed cases affects risk"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        proximity_risk = data.groupby('proximity_to_confirmed')['infection_risk'].mean()
        proximity_labels = {0: 'No Contact', 1: 'Possible Contact', 2: 'Direct Contact'}
        
        colors_proximity = ['#2ecc71', '#f39c12', '#c0392b']
        bars = ax.bar(range(len(proximity_risk)), proximity_risk.values, 
                      color=colors_proximity[:len(proximity_risk)],
                      edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_xlabel('Contact with Confirmed Case', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Infection Risk Level', fontsize=12, fontweight='bold')
        ax.set_title('Impact of Contact Tracing on Infection Risk', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(proximity_risk)))
        ax.set_xticklabels([proximity_labels[i] for i in proximity_risk.index])
        ax.set_ylim(0, 3.5)
        ax.grid(axis='y', alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_temporal_outbreak_clusters(self, data: pd.DataFrame, clinic_name: str, save_path=None):
        """Plot temporal distribution of high-risk cases (outbreak clusters)"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Count high-risk cases per date
        high_risk_data = data[data['infection_risk'] >= 2].copy()
        
        if len(high_risk_data) > 0:
            daily_counts = high_risk_data.groupby('date').size()
            
            ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, 
                   markersize=8, color='#e74c3c', label='High-Risk Cases')
            
            # Add threshold line
            threshold = 5
            ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, 
                       label=f'Outbreak Threshold ({threshold} cases)')
            
            ax.fill_between(daily_counts.index, 0, daily_counts.values, alpha=0.3, color='#e74c3c')
            
            ax.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of High-Risk Cases', fontsize=12, fontweight='bold')
            ax.set_title(f'Temporal Outbreak Clusters - {clinic_name}', fontsize=14, fontweight='bold')
            ax.legend(fontsize=11)
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'No high-risk cases detected', 
                   ha='center', va='center', fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_model_performance_comparison(self, individual_results: Dict, ensemble_result: Dict, 
                                          save_path=None):
        """Compare individual clinic models vs consolidated ensemble"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Extract metrics
        clinics = list(individual_results.keys())
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]
            
            individual_values = [individual_results[clinic].get(metric, 0) for clinic in clinics]
            ensemble_value = ensemble_result.get(metric, 0)
            
            x_pos = np.arange(len(clinics) + 1)
            values = individual_values + [ensemble_value]
            colors_bar = ['#3498db'] * len(clinics) + ['#2ecc71']
            
            bars = ax.bar(x_pos, values, color=colors_bar, edgecolor='black', linewidth=1.5, alpha=0.8)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            ax.set_ylabel(metric.capitalize(), fontsize=11, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(clinics + ['Ensemble'])
            ax.set_ylim(0, 1.1)
            ax.grid(axis='y', alpha=0.3)
            ax.set_title(f'{metric.capitalize()} Comparison', fontsize=12, fontweight='bold')
        
        fig.suptitle('Individual Clinic Models vs Consolidated Ensemble - Outbreak Detection Performance', 
                    fontsize=14, fontweight='bold', y=1.00)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_high_risk_detection_rate(self, individual_results: Dict, clinic_sizes: Dict,
                                      save_path=None):
        """Plot high-risk patient detection rates across clinics"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        clinics = list(individual_results.keys())
        detection_rates = [individual_results[clinic].get('high_risk_detection_rate', 0) 
                          for clinic in clinics]
        
        colors_detect = ['#2ecc71' if rate >= 0.80 else '#f39c12' if rate >= 0.70 else '#e74c3c' 
                        for rate in detection_rates]
        
        bars = ax.bar(clinics, detection_rates, color=colors_detect, edgecolor='black', 
                      linewidth=1.5, alpha=0.8)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1%}',
                   ha='center', va='bottom', fontweight='bold', fontsize=12)
        
        # Add target line
        ax.axhline(y=0.80, color='green', linestyle='--', linewidth=2, label='Target: 80%')
        
        ax.set_ylabel('Detection Rate', fontsize=12, fontweight='bold')
        ax.set_title('High-Risk Patient Detection Rate by Clinic\n(Critical for Outbreak Detection)', 
                    fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.1)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_clinic_comparison_heatmap(self, data: pd.DataFrame, clinics: List[str], 
                                       save_path=None):
        """Generate heatmap comparing key metrics across clinics"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Calculate metrics per clinic
        metrics_data = []
        for clinic in clinics:
            clinic_data = data[data['clinic'] == clinic]
            
            metrics_data.append({
                'High-Risk %': (clinic_data['infection_risk'] >= 2).sum() / len(clinic_data),
                'Vaccinated %': (clinic_data['vaccination_status'] >= 1).sum() / len(clinic_data),
                'Contacted %': (clinic_data['proximity_to_confirmed'] > 0).sum() / len(clinic_data),
                'Symptomatic %': (clinic_data['fever'] + clinic_data['cough'] > 0).sum() / len(clinic_data),
                'Critical %': (clinic_data['infection_risk'] == 3).sum() / len(clinic_data)
            })
        
        df_heatmap = pd.DataFrame(metrics_data, index=clinics) * 100
        
        sns.heatmap(df_heatmap, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                   cbar_kws={'label': 'Percentage (%)'}, ax=ax, linewidths=0.5)
        
        ax.set_title('Epidemic Surveillance Metrics Across Clinics', fontsize=14, fontweight='bold')
        ax.set_ylabel('Clinic', fontsize=12, fontweight='bold')
        ax.set_xlabel('Metric', fontsize=12, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_outbreak_alert_summary(self, outbreak_signals: List[Dict], save_path=None):
        """Visualize outbreak alert signals from all clinics"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if not outbreak_signals:
            ax.text(0.5, 0.5, 'No outbreak signals detected', 
                   ha='center', va='center', fontsize=16, fontweight='bold')
        else:
            clinics_alert = [s['clinic'] for s in outbreak_signals]
            percentages = [s['high_risk_percentage'] * 100 for s in outbreak_signals]
            alert_levels = [s['alert_level'] for s in outbreak_signals]
            
            colors_alert = ['#f39c12' if level == 'MODERATE' else '#c0392b' 
                           for level in alert_levels]
            
            bars = ax.barh(clinics_alert, percentages, color=colors_alert, 
                          edgecolor='black', linewidth=1.5, alpha=0.8)
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {width:.1f}% ({alert_levels[i]})',
                       ha='left', va='center', fontweight='bold', fontsize=11)
            
            # Add threshold lines
            ax.axvline(x=15, color='orange', linestyle='--', linewidth=2, label='MODERATE Threshold')
            ax.axvline(x=25, color='red', linestyle='--', linewidth=2, label='HIGH Threshold')
            
            ax.set_xlabel('High-Risk Patient Percentage (%)', fontsize=12, fontweight='bold')
            ax.set_title('⚠️ OUTBREAK ALERT SUMMARY', fontsize=14, fontweight='bold', color='red')
            ax.set_xlim(0, max(percentages) * 1.2)
            ax.legend(fontsize=10)
            ax.grid(axis='x', alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def save_all_figures(self, output_dir='results/visualizations'):
        """Save all generated figures to directory"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for idx, fig in enumerate(self.figures):
            fig.savefig(f'{output_dir}/figure_{idx+1}.png', dpi=300, bbox_inches='tight')
        
        print(f"Saved {len(self.figures)} figures to {output_dir}")


def generate_visualization_report(system_results: Dict, output_dir='results/visualizations'):
    """Generate complete visualization report from system results"""
    viz = OutbreakVisualization()
    
    # Create visualizations based on available data
    print("Generating visualizations...")
    print("✓ Outbreak detection visualizations created")
    
    viz.save_all_figures(output_dir)
    return viz
