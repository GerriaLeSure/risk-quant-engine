"""
Tests for Risk Register module
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from risk_register import RiskRegister


class TestRiskRegister:
    """Test suite for RiskRegister class"""
    
    @pytest.fixture
    def sample_risk_df(self):
        """Create sample risk DataFrame for testing"""
        return pd.DataFrame({
            'risk_id': ['R001', 'R002', 'R003'],
            'risk_name': ['Cyber Attack', 'Supply Chain', 'Regulatory'],
            'category': ['Technology', 'Operational', 'Compliance'],
            'likelihood': [0.35, 0.25, 0.20],
            'impact': [500000, 800000, 1200000],
            'likelihood_std': [0.12, 0.10, 0.08],
            'impact_min': [200000, 300000, 500000],
            'impact_most_likely': [500000, 800000, 1200000],
            'impact_max': [1500000, 2000000, 3000000],
            'owner': ['CISO', 'COO', 'CCO'],
            'status': ['Active', 'Active', 'Active'],
            'inherent_risk_score': [175000, 200000, 240000],
            'residual_risk_score': [122500, 140000, 168000]
        })
    
    def test_initialization(self):
        """Test RiskRegister initialization"""
        rr = RiskRegister()
        assert rr.risks_df is None
        assert rr.original_df is None
    
    def test_load_from_dataframe(self, sample_risk_df):
        """Test loading from DataFrame"""
        rr = RiskRegister()
        df = rr.load_from_dataframe(sample_risk_df)
        
        assert df is not None
        assert len(df) == 3
        assert 'risk_id' in df.columns
        assert 'risk_name' in df.columns
    
    def test_load_from_csv(self, sample_risk_df):
        """Test loading from CSV file"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_risk_df.to_csv(f.name, index=False)
            temp_path = f.name
        
        rr = RiskRegister()
        df = rr.load_from_csv(temp_path)
        
        assert df is not None
        assert len(df) == 3
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_validate_and_clean_minimal_data(self):
        """Test validation with minimal required data"""
        rr = RiskRegister()
        
        # Minimal DataFrame
        minimal_df = pd.DataFrame({
            'risk_id': ['R001'],
            'risk_name': ['Test Risk'],
            'likelihood': [0.3],
            'impact': [500000]
        })
        
        df = rr.load_from_dataframe(minimal_df)
        
        # Check that missing columns were added
        assert 'likelihood_std' in df.columns
        assert 'impact_min' in df.columns
        assert 'impact_max' in df.columns
        assert 'inherent_risk_score' in df.columns
        assert 'residual_risk_score' in df.columns
        assert 'category' in df.columns
    
    def test_get_risks(self, sample_risk_df):
        """Test getting risks"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        df = rr.get_risks()
        assert len(df) == 3
        assert isinstance(df, pd.DataFrame)
    
    def test_get_risks_before_loading(self):
        """Test that get_risks raises error when no data loaded"""
        rr = RiskRegister()
        
        with pytest.raises(ValueError):
            rr.get_risks()
    
    def test_filter_by_category(self, sample_risk_df):
        """Test filtering by category"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        filtered = rr.filter_by_category('Technology')
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['risk_id'] == 'R001'
    
    def test_filter_by_status(self, sample_risk_df):
        """Test filtering by status"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        filtered = rr.filter_by_status('Active')
        
        assert len(filtered) == 3
    
    def test_get_high_priority_risks(self, sample_risk_df):
        """Test getting high priority risks"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        high_priority = rr.get_high_priority_risks(threshold=0.5)
        
        # Should return top 50% of risks
        assert len(high_priority) >= 1
        assert (high_priority['residual_risk_score'] >= 
                sample_risk_df['residual_risk_score'].quantile(0.5)).all()
    
    def test_get_summary_statistics(self, sample_risk_df):
        """Test summary statistics"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        stats = rr.get_summary_statistics()
        
        assert stats['total_risks'] == 3
        assert stats['active_risks'] == 3
        assert 'avg_likelihood' in stats
        assert 'avg_impact' in stats
        assert 'categories' in stats
        assert stats['categories'] == 3
    
    def test_export_to_csv(self, sample_risk_df):
        """Test CSV export"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        rr.export_to_csv(temp_path)
        
        # Verify file was created and can be read
        exported_df = pd.read_csv(temp_path)
        assert len(exported_df) == 3
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_get_risk_matrix_data(self, sample_risk_df):
        """Test risk matrix data preparation"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        matrix_data = rr.get_risk_matrix_data()
        
        assert 'risk_id' in matrix_data.columns
        assert 'likelihood' in matrix_data.columns
        assert 'impact' in matrix_data.columns
        assert len(matrix_data) == 3
    
    def test_add_risk(self, sample_risk_df):
        """Test adding a new risk"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        new_risk = {
            'risk_id': 'R004',
            'risk_name': 'New Risk',
            'category': 'Strategic',
            'likelihood': 0.4,
            'impact': 600000,
            'owner': 'CEO',
            'status': 'Active'
        }
        
        rr.add_risk(new_risk)
        
        df = rr.get_risks()
        assert len(df) == 4
        assert 'R004' in df['risk_id'].values
    
    def test_update_risk(self, sample_risk_df):
        """Test updating an existing risk"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        rr.update_risk('R001', {'likelihood': 0.5, 'status': 'Mitigated'})
        
        df = rr.get_risks()
        updated_risk = df[df['risk_id'] == 'R001'].iloc[0]
        
        assert updated_risk['likelihood'] == 0.5
        assert updated_risk['status'] == 'Mitigated'
    
    def test_delete_risk(self, sample_risk_df):
        """Test deleting a risk"""
        rr = RiskRegister()
        rr.load_from_dataframe(sample_risk_df)
        
        rr.delete_risk('R001')
        
        df = rr.get_risks()
        assert len(df) == 2
        assert 'R001' not in df['risk_id'].values
    
    def test_load_invalid_csv(self):
        """Test loading invalid CSV file"""
        rr = RiskRegister()
        
        with pytest.raises(ValueError):
            rr.load_from_csv('nonexistent_file.csv')
    
    def test_numeric_conversion(self):
        """Test that numeric columns are properly converted"""
        rr = RiskRegister()
        
        # DataFrame with string numbers
        df = pd.DataFrame({
            'risk_id': ['R001'],
            'risk_name': ['Test'],
            'likelihood': ['0.3'],
            'impact': ['500000']
        })
        
        result_df = rr.load_from_dataframe(df)
        
        assert result_df['likelihood'].dtype in [np.float64, np.float32]
        assert result_df['impact'].dtype in [np.float64, np.float32, np.int64, np.int32]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
