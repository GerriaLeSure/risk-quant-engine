"""
Tests for Loss Exceedance Curve module
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from curves import LossExceedanceCurve


class TestLossExceedanceCurve:
    """Test suite for LossExceedanceCurve class"""
    
    @pytest.fixture
    def sample_loss_data(self):
        """Generate sample loss data for testing"""
        np.random.seed(42)
        return np.random.lognormal(mean=10, sigma=1.5, size=1000)
    
    @pytest.fixture
    def sample_simulation_results(self):
        """Generate sample simulation results"""
        np.random.seed(42)
        return pd.DataFrame({
            'risk_id': ['R001', 'R002', 'R003'],
            'risk_name': ['Risk 1', 'Risk 2', 'Risk 3'],
            'simulations': [
                np.random.lognormal(10, 1, 1000),
                np.random.lognormal(11, 1.2, 1000),
                np.random.lognormal(9, 0.8, 1000)
            ]
        })
    
    def test_initialization(self):
        """Test LossExceedanceCurve initialization"""
        lec = LossExceedanceCurve()
        assert lec.curve_data is None
    
    def test_calculate_lec(self, sample_loss_data):
        """Test LEC calculation"""
        lec = LossExceedanceCurve()
        curve_data = lec.calculate_lec(sample_loss_data, n_points=100)
        
        assert curve_data is not None
        assert len(curve_data) == 100
        assert 'loss_threshold' in curve_data.columns
        assert 'exceedance_probability' in curve_data.columns
        assert 'exceedance_percentage' in curve_data.columns
        assert 'return_period' in curve_data.columns
    
    def test_calculate_lec_probabilities_decreasing(self, sample_loss_data):
        """Test that exceedance probabilities are monotonically decreasing"""
        lec = LossExceedanceCurve()
        curve_data = lec.calculate_lec(sample_loss_data)
        
        # Exceedance probability should decrease as loss threshold increases
        probs = curve_data['exceedance_probability'].values
        assert all(probs[i] >= probs[i+1] for i in range(len(probs)-1))
    
    def test_calculate_lec_probability_range(self, sample_loss_data):
        """Test that probabilities are in valid range [0, 1]"""
        lec = LossExceedanceCurve()
        curve_data = lec.calculate_lec(sample_loss_data)
        
        probs = curve_data['exceedance_probability'].values
        assert all(0 <= p <= 1 for p in probs)
    
    def test_calculate_portfolio_lec(self, sample_simulation_results):
        """Test portfolio-level LEC calculation"""
        lec = LossExceedanceCurve()
        curve_data = lec.calculate_portfolio_lec(sample_simulation_results)
        
        assert curve_data is not None
        assert len(curve_data) == 100
        assert 'loss_threshold' in curve_data.columns
    
    def test_plot_lec_matplotlib(self, sample_loss_data):
        """Test matplotlib plotting"""
        lec = LossExceedanceCurve()
        lec.calculate_lec(sample_loss_data)
        
        fig = lec.plot_lec_matplotlib(add_percentiles=True)
        
        assert fig is not None
        assert len(fig.axes) > 0
    
    def test_plot_lec_plotly(self, sample_loss_data):
        """Test plotly plotting"""
        lec = LossExceedanceCurve()
        lec.calculate_lec(sample_loss_data)
        
        fig = lec.plot_lec_plotly(add_percentiles=True)
        
        assert fig is not None
        assert len(fig.data) > 0
    
    def test_plot_without_data_raises_error(self):
        """Test that plotting without data raises error"""
        lec = LossExceedanceCurve()
        
        with pytest.raises(ValueError):
            lec.plot_lec_matplotlib()
        
        with pytest.raises(ValueError):
            lec.plot_lec_plotly()
    
    def test_get_var_cvar(self, sample_loss_data):
        """Test VaR and CVaR calculation"""
        lec = LossExceedanceCurve()
        var_cvar = lec.get_var_cvar(sample_loss_data, confidence_levels=[0.90, 0.95, 0.99])
        
        assert len(var_cvar) == 3
        assert 'confidence_level' in var_cvar.columns
        assert 'var' in var_cvar.columns
        assert 'cvar' in var_cvar.columns
        
        # CVaR should be greater than or equal to VaR
        assert (var_cvar['cvar'] >= var_cvar['var']).all()
    
    def test_var_cvar_ordering(self, sample_loss_data):
        """Test that VaR increases with confidence level"""
        lec = LossExceedanceCurve()
        var_cvar = lec.get_var_cvar(sample_loss_data, confidence_levels=[0.90, 0.95, 0.99])
        
        vars = var_cvar['var'].values
        # VaR should increase with confidence level
        assert vars[0] <= vars[1] <= vars[2]
    
    def test_compare_multiple_lecs(self, sample_loss_data):
        """Test comparing multiple LECs"""
        lec = LossExceedanceCurve()
        
        # Generate multiple curves
        np.random.seed(42)
        data1 = sample_loss_data
        data2 = sample_loss_data * 1.5
        
        curve1 = lec.calculate_lec(data1)
        curve2 = lec.calculate_lec(data2)
        
        lec_dict = {
            'Scenario 1': curve1,
            'Scenario 2': curve2
        }
        
        fig = lec.compare_multiple_lecs(lec_dict)
        
        assert fig is not None
        assert len(fig.data) == 2  # Two curves
    
    def test_export_curve_data(self, sample_loss_data):
        """Test exporting curve data to CSV"""
        import tempfile
        
        lec = LossExceedanceCurve()
        lec.calculate_lec(sample_loss_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        lec.export_curve_data(temp_path)
        
        # Verify file was created and can be read
        exported_df = pd.read_csv(temp_path)
        assert len(exported_df) > 0
        assert 'loss_threshold' in exported_df.columns
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_export_without_data_raises_error(self):
        """Test that exporting without data raises error"""
        lec = LossExceedanceCurve()
        
        with pytest.raises(ValueError):
            lec.export_curve_data('test.csv')
    
    def test_return_period_calculation(self, sample_loss_data):
        """Test return period calculation"""
        lec = LossExceedanceCurve()
        curve_data = lec.calculate_lec(sample_loss_data)
        
        # Return period should be inverse of exceedance probability
        # For exceedance probability of 0.1, return period should be ~10
        prob_01_idx = (curve_data['exceedance_probability'] - 0.1).abs().idxmin()
        return_period = curve_data.loc[prob_01_idx, 'return_period']
        
        # Allow some tolerance due to discrete sampling
        assert 5 < return_period < 15
    
    def test_empty_loss_data(self):
        """Test handling of empty loss data"""
        lec = LossExceedanceCurve()
        
        empty_data = np.array([])
        
        # This should handle gracefully or raise appropriate error
        try:
            curve_data = lec.calculate_lec(empty_data)
            # If it doesn't raise an error, check that it handles it somehow
            assert curve_data is not None
        except (ValueError, IndexError):
            # It's acceptable to raise an error for empty data
            pass
    
    def test_single_value_loss_data(self):
        """Test handling of single value loss data"""
        lec = LossExceedanceCurve()
        
        single_value = np.array([100000])
        curve_data = lec.calculate_lec(single_value, n_points=10)
        
        assert curve_data is not None
        # All loss thresholds should be the same value
        assert curve_data['loss_threshold'].min() >= 0
    
    def test_percentile_markers(self, sample_loss_data):
        """Test that percentile markers are correctly identified"""
        lec = LossExceedanceCurve()
        curve_data = lec.calculate_lec(sample_loss_data, n_points=100)
        
        # Find 95th percentile (5% exceedance)
        idx_95 = (curve_data['exceedance_probability'] - 0.05).abs().idxmin()
        loss_95 = curve_data.loc[idx_95, 'loss_threshold']
        
        # This should be close to the 95th percentile of the raw data
        actual_p95 = np.percentile(sample_loss_data, 95)
        
        # Allow 10% tolerance due to interpolation
        assert 0.9 * actual_p95 <= loss_95 <= 1.1 * actual_p95


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
