"""
Risk Register Management - Load and manage risk data from CSV/XLS
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List
import io


class RiskRegister:
    """Risk register management and data loading"""
    
    def __init__(self):
        self.risks_df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None
    
    def load_from_csv(self, filepath: str) -> pd.DataFrame:
        """
        Load risk register from CSV file
        
        Args:
            filepath: Path to CSV file
        
        Returns:
            DataFrame with risk data
        """
        try:
            self.risks_df = pd.read_csv(filepath)
            self.original_df = self.risks_df.copy()
            self._validate_and_clean()
            return self.risks_df
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {str(e)}")
    
    def load_from_excel(self, filepath: str, sheet_name: str = 0) -> pd.DataFrame:
        """
        Load risk register from Excel file
        
        Args:
            filepath: Path to Excel file
            sheet_name: Sheet name or index (default: 0)
        
        Returns:
            DataFrame with risk data
        """
        try:
            self.risks_df = pd.read_excel(filepath, sheet_name=sheet_name)
            self.original_df = self.risks_df.copy()
            self._validate_and_clean()
            return self.risks_df
        except Exception as e:
            raise ValueError(f"Error loading Excel file: {str(e)}")
    
    def load_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Load risk register from DataFrame
        
        Args:
            df: DataFrame with risk data
        
        Returns:
            Cleaned DataFrame
        """
        self.risks_df = df.copy()
        self.original_df = df.copy()
        self._validate_and_clean()
        return self.risks_df
    
    def _validate_and_clean(self):
        """Validate and clean risk register data"""
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        
        # Ensure required columns exist
        required_cols = ['risk_id', 'risk_name', 'likelihood', 'impact']
        missing_cols = [col for col in required_cols if col not in self.risks_df.columns]
        
        if missing_cols:
            # Try to create missing columns with defaults
            if 'risk_id' not in self.risks_df.columns:
                self.risks_df['risk_id'] = [f"R{i:03d}" for i in range(1, len(self.risks_df) + 1)]
            if 'risk_name' not in self.risks_df.columns:
                self.risks_df['risk_name'] = [f"Risk {i}" for i in range(1, len(self.risks_df) + 1)]
        
        # Ensure numeric columns
        numeric_cols = ['likelihood', 'impact', 'likelihood_std', 'impact_min', 
                       'impact_most_likely', 'impact_max', 'inherent_risk_score', 
                       'residual_risk_score']
        
        for col in numeric_cols:
            if col in self.risks_df.columns:
                self.risks_df[col] = pd.to_numeric(self.risks_df[col], errors='coerce')
        
        # Fill missing values with defaults
        if 'likelihood_std' not in self.risks_df.columns:
            self.risks_df['likelihood_std'] = 0.1
        
        if 'impact_min' not in self.risks_df.columns:
            self.risks_df['impact_min'] = self.risks_df['impact'] * 0.5
        
        if 'impact_most_likely' not in self.risks_df.columns:
            self.risks_df['impact_most_likely'] = self.risks_df['impact']
        
        if 'impact_max' not in self.risks_df.columns:
            self.risks_df['impact_max'] = self.risks_df['impact'] * 1.5
        
        # Calculate risk scores if not present
        if 'inherent_risk_score' not in self.risks_df.columns:
            self.risks_df['inherent_risk_score'] = (
                self.risks_df['likelihood'] * self.risks_df['impact']
            )
        
        if 'residual_risk_score' not in self.risks_df.columns:
            # Assume 30% risk reduction after controls
            self.risks_df['residual_risk_score'] = (
                self.risks_df['inherent_risk_score'] * 0.7
            )
        
        # Add default category if missing
        if 'category' not in self.risks_df.columns:
            self.risks_df['category'] = 'General'
        
        # Add default owner if missing
        if 'owner' not in self.risks_df.columns:
            self.risks_df['owner'] = 'Unassigned'
        
        # Add status if missing
        if 'status' not in self.risks_df.columns:
            self.risks_df['status'] = 'Active'
    
    def get_risks(self) -> pd.DataFrame:
        """Get current risk register"""
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        return self.risks_df
    
    def filter_by_category(self, category: str) -> pd.DataFrame:
        """Filter risks by category"""
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        return self.risks_df[self.risks_df['category'] == category]
    
    def filter_by_status(self, status: str) -> pd.DataFrame:
        """Filter risks by status"""
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        return self.risks_df[self.risks_df['status'] == status]
    
    def get_high_priority_risks(self, threshold: float = 0.7) -> pd.DataFrame:
        """
        Get high priority risks based on residual risk score
        
        Args:
            threshold: Threshold percentile (0-1)
        
        Returns:
            DataFrame with high priority risks
        """
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        
        threshold_value = self.risks_df['residual_risk_score'].quantile(threshold)
        return self.risks_df[self.risks_df['residual_risk_score'] >= threshold_value]
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics for risk register"""
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        
        stats = {
            'total_risks': len(self.risks_df),
            'active_risks': len(self.risks_df[self.risks_df['status'] == 'Active']),
            'avg_likelihood': self.risks_df['likelihood'].mean(),
            'avg_impact': self.risks_df['impact'].mean(),
            'avg_inherent_score': self.risks_df['inherent_risk_score'].mean(),
            'avg_residual_score': self.risks_df['residual_risk_score'].mean(),
            'total_potential_impact': self.risks_df['impact'].sum(),
            'categories': self.risks_df['category'].nunique(),
            'category_breakdown': self.risks_df['category'].value_counts().to_dict()
        }
        
        return stats
    
    def export_to_csv(self, filepath: str, include_quantified: bool = False,
                     quantified_df: Optional[pd.DataFrame] = None):
        """
        Export risk register to CSV
        
        Args:
            filepath: Output file path
            include_quantified: Whether to include quantified results
            quantified_df: DataFrame with quantified results
        """
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        
        if include_quantified and quantified_df is not None:
            # Merge original risk data with quantified results
            export_df = self.risks_df.merge(
                quantified_df,
                on='risk_id',
                how='left',
                suffixes=('', '_quantified')
            )
        else:
            export_df = self.risks_df
        
        export_df.to_csv(filepath, index=False)
    
    def get_risk_matrix_data(self) -> pd.DataFrame:
        """
        Prepare data for risk matrix visualization
        
        Returns:
            DataFrame with likelihood and impact for plotting
        """
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        
        matrix_data = self.risks_df[[
            'risk_id', 'risk_name', 'category', 'likelihood', 'impact',
            'inherent_risk_score', 'residual_risk_score'
        ]].copy()
        
        return matrix_data
    
    def add_risk(self, risk_data: Dict):
        """Add a new risk to the register"""
        if self.risks_df is None:
            self.risks_df = pd.DataFrame()
        
        new_risk = pd.DataFrame([risk_data])
        self.risks_df = pd.concat([self.risks_df, new_risk], ignore_index=True)
        self._validate_and_clean()
    
    def update_risk(self, risk_id: str, updates: Dict):
        """Update an existing risk"""
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        
        mask = self.risks_df['risk_id'] == risk_id
        for key, value in updates.items():
            if key in self.risks_df.columns:
                self.risks_df.loc[mask, key] = value
    
    def delete_risk(self, risk_id: str):
        """Delete a risk from the register"""
        if self.risks_df is None:
            raise ValueError("No risk data loaded")
        
        self.risks_df = self.risks_df[self.risks_df['risk_id'] != risk_id]
