"""
Tests for KPI/KRI dashboard functionality.
"""

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc.dashboard_kri import (
    residual_vs_inherent_heatmap,
    top_exposures,
    plot_top_exposures,
    generate_trend_data,
    plot_trend_chart,
    calculate_kpi_kri_summary,
    print_kpi_kri_summary
)


@pytest.fixture
def sample_quantified_df():
    """Create sample quantified risk register for testing."""
    return pd.DataFrame({
        'RiskID': ['R01', 'R02', 'R03', 'R04', 'R05', 'PORTFOLIO_TOTAL'],
        'Category': ['Cyber', 'Ops', 'Financial', 'Legal', 'Market', 'Portfolio'],
        'SimMean': [500000, 300000, 400000, 200000, 150000, 1550000],
        'SimMedian': [450000, 280000, 380000, 180000, 140000, 1430000],
        'SimStd': [250000, 150000, 200000, 100000, 75000, 775000],
        'SimVaR95': [1000000, 600000, 800000, 400000, 300000, 3100000],
        'SimVaR99': [1500000, 900000, 1200000, 600000, 450000, 4650000],
        'SimTVaR95': [1200000, 700000, 900000, 450000, 350000, 3600000],
        'SimTVaR99': [1600000, 950000, 1250000, 625000, 475000, 4900000],
        'ControlEffectiveness': [0.6, 0.5, 0.4, 0.3, 0.2, 0.0],
        'ResidualFactor': [0.7, 0.8, 0.75, 0.85, 0.9, 1.0]
    })


class TestResidualInherentHeatmap:
    """Test residual vs inherent heatmap functionality."""
    
    def test_creates_matplotlib_figure(self, sample_quantified_df):
        """Test that matplotlib figure is created."""
        fig = residual_vs_inherent_heatmap(sample_quantified_df, use_plotly=False)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    def test_creates_plotly_figure(self, sample_quantified_df):
        """Test that plotly figure is created."""
        fig = residual_vs_inherent_heatmap(sample_quantified_df, use_plotly=True)
        assert hasattr(fig, 'data')  # Plotly Figure has 'data' attribute
    
    def test_excludes_portfolio_total(self, sample_quantified_df):
        """Test that PORTFOLIO_TOTAL is excluded."""
        fig = residual_vs_inherent_heatmap(sample_quantified_df, use_plotly=False)
        # Should have 5 risks, not 6
        assert len(fig.axes[0].collections[0].get_offsets()) == 5
        plt.close(fig)
    
    def test_diagonal_line_present(self, sample_quantified_df):
        """Test that diagonal reference line is present."""
        fig = residual_vs_inherent_heatmap(sample_quantified_df, use_plotly=False)
        # Should have a line plot for diagonal
        lines = fig.axes[0].get_lines()
        assert len(lines) > 0
        plt.close(fig)


class TestTopExposures:
    """Test top exposures functionality."""
    
    def test_returns_dataframe(self, sample_quantified_df):
        """Test that function returns a DataFrame."""
        result = top_exposures(sample_quantified_df, metric='mean', top_n=3)
        assert isinstance(result, pd.DataFrame)
    
    def test_returns_correct_number(self, sample_quantified_df):
        """Test that correct number of risks are returned."""
        result = top_exposures(sample_quantified_df, metric='mean', top_n=3)
        assert len(result) == 3
    
    def test_sorted_descending(self, sample_quantified_df):
        """Test that results are sorted descending by metric."""
        result = top_exposures(sample_quantified_df, metric='mean', top_n=5)
        means = result['SimMean'].values
        assert all(means[i] >= means[i+1] for i in range(len(means)-1))
    
    def test_excludes_portfolio_total(self, sample_quantified_df):
        """Test that PORTFOLIO_TOTAL is not included."""
        result = top_exposures(sample_quantified_df, metric='mean', top_n=10)
        assert 'PORTFOLIO_TOTAL' not in result['RiskID'].values
    
    def test_percentage_calculation(self, sample_quantified_df):
        """Test that percentage of total is calculated correctly."""
        result = top_exposures(sample_quantified_df, metric='mean', top_n=1)
        top_risk_mean = result['SimMean'].iloc[0]
        portfolio_mean = sample_quantified_df[
            sample_quantified_df['RiskID'] == 'PORTFOLIO_TOTAL'
        ]['SimMean'].values[0]
        
        expected_pct = (top_risk_mean / portfolio_mean * 100)
        assert abs(result['pct_of_total'].iloc[0] - expected_pct) < 0.01
    
    def test_different_metrics(self, sample_quantified_df):
        """Test that different metrics work."""
        for metric in ['mean', 'var_95', 'var_99', 'tvar_95']:
            result = top_exposures(sample_quantified_df, metric=metric, top_n=3)
            assert len(result) == 3
    
    def test_plot_top_exposures_creates_figure(self, sample_quantified_df):
        """Test that plot function creates a figure."""
        fig = plot_top_exposures(sample_quantified_df, metric='mean', top_n=3)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestTrendData:
    """Test trend data generation."""
    
    def test_generates_correct_periods(self, sample_quantified_df):
        """Test that correct number of periods are generated."""
        trend_df = generate_trend_data(sample_quantified_df, n_periods=8)
        assert len(trend_df) == 8
    
    def test_has_required_columns(self, sample_quantified_df):
        """Test that all required columns are present."""
        trend_df = generate_trend_data(sample_quantified_df, n_periods=5)
        required_cols = ['period', 'period_label', 'mean_loss', 'var_95', 'concentration']
        assert all(col in trend_df.columns for col in required_cols)
    
    def test_period_numbers_sequential(self, sample_quantified_df):
        """Test that period numbers are sequential."""
        trend_df = generate_trend_data(sample_quantified_df, n_periods=6)
        assert list(trend_df['period']) == [1, 2, 3, 4, 5, 6]
    
    def test_deterministic_with_seed(self, sample_quantified_df):
        """Test that results are deterministic (seed is set internally)."""
        trend1 = generate_trend_data(sample_quantified_df, n_periods=4)
        trend2 = generate_trend_data(sample_quantified_df, n_periods=4)
        pd.testing.assert_frame_equal(trend1, trend2)
    
    def test_concentration_bounded(self, sample_quantified_df):
        """Test that concentration stays within 0-100%."""
        trend_df = generate_trend_data(sample_quantified_df, n_periods=10)
        assert all(trend_df['concentration'] >= 0)
        assert all(trend_df['concentration'] <= 100)
    
    def test_plot_trend_chart_creates_figure(self, sample_quantified_df):
        """Test that plot function creates a figure."""
        trend_df = generate_trend_data(sample_quantified_df, n_periods=6)
        fig = plot_trend_chart(trend_df)
        assert isinstance(fig, plt.Figure)
        # Should have 2 subplots
        assert len(fig.axes) == 2
        plt.close(fig)


class TestKPIKRISummary:
    """Test KPI/KRI summary calculations."""
    
    def test_returns_dictionary(self, sample_quantified_df):
        """Test that function returns a dictionary."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        assert isinstance(result, dict)
    
    def test_has_required_keys(self, sample_quantified_df):
        """Test that all required KPI/KRI keys are present."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        
        required_keys = [
            'total_inherent_loss',
            'total_residual_loss',
            'mitigation_effectiveness_pct',
            'portfolio_var_95',
            'portfolio_var_99',
            'top_risk_id',
            'concentration_ratio_pct'
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_mitigation_percentage_calculation(self, sample_quantified_df):
        """Test that mitigation percentage is calculated correctly."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        
        # Mitigation should be positive (inherent > residual)
        assert result['mitigation_effectiveness_pct'] > 0
        
        # Should be less than 100%
        assert result['mitigation_effectiveness_pct'] < 100
        
        # Verify formula
        inherent = result['total_inherent_loss']
        residual = result['total_residual_loss']
        expected_pct = ((inherent - residual) / inherent * 100)
        
        assert abs(result['mitigation_effectiveness_pct'] - expected_pct) < 0.01
    
    def test_residual_equals_portfolio_mean(self, sample_quantified_df):
        """Test that residual loss equals portfolio mean."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        portfolio_mean = sample_quantified_df[
            sample_quantified_df['RiskID'] == 'PORTFOLIO_TOTAL'
        ]['SimMean'].values[0]
        
        assert result['total_residual_loss'] == portfolio_mean
    
    def test_top_risk_identified(self, sample_quantified_df):
        """Test that top risk is correctly identified."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        
        # Get actual top risk
        individual = sample_quantified_df[
            sample_quantified_df['RiskID'] != 'PORTFOLIO_TOTAL'
        ]
        actual_top = individual.nlargest(1, 'SimMean').iloc[0]
        
        assert result['top_risk_id'] == actual_top['RiskID']
        assert result['top_risk_mean'] == actual_top['SimMean']
    
    def test_concentration_ratio_calculation(self, sample_quantified_df):
        """Test that concentration ratio is calculated correctly."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        
        # Get top 3 risks
        individual = sample_quantified_df[
            sample_quantified_df['RiskID'] != 'PORTFOLIO_TOTAL'
        ]
        top3_sum = individual.nlargest(3, 'SimMean')['SimMean'].sum()
        portfolio_total = result['total_residual_loss']
        
        expected_concentration = (top3_sum / portfolio_total * 100)
        
        assert abs(result['concentration_ratio_pct'] - expected_concentration) < 0.01
    
    def test_concentration_ratio_bounded(self, sample_quantified_df):
        """Test that concentration ratio is between 0 and 100."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        assert 0 <= result['concentration_ratio_pct'] <= 100
    
    def test_number_of_risks_correct(self, sample_quantified_df):
        """Test that number of risks is counted correctly."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        expected = len(sample_quantified_df[
            sample_quantified_df['RiskID'] != 'PORTFOLIO_TOTAL'
        ])
        assert result['number_of_risks'] == expected
    
    def test_print_summary_runs(self, sample_quantified_df, capsys):
        """Test that print function runs without error."""
        result = calculate_kpi_kri_summary(sample_quantified_df)
        print_kpi_kri_summary(result)
        
        captured = capsys.readouterr()
        assert 'KPI/KRI DASHBOARD SUMMARY' in captured.out
        assert 'KEY PERFORMANCE INDICATORS' in captured.out
        assert 'KEY RISK INDICATORS' in captured.out


class TestIntegration:
    """Integration tests for dashboard KRI module."""
    
    def test_full_workflow(self, sample_quantified_df):
        """Test complete workflow with all functions."""
        # 1. Calculate KPI/KRI
        kpi_kri = calculate_kpi_kri_summary(sample_quantified_df)
        assert isinstance(kpi_kri, dict)
        
        # 2. Get top exposures
        top_exp = top_exposures(sample_quantified_df, metric='mean', top_n=3)
        assert len(top_exp) == 3
        
        # 3. Generate trend data
        trend_df = generate_trend_data(sample_quantified_df, n_periods=6)
        assert len(trend_df) == 6
        
        # 4. Create visualizations
        fig_heatmap = residual_vs_inherent_heatmap(sample_quantified_df)
        assert isinstance(fig_heatmap, plt.Figure)
        plt.close(fig_heatmap)
        
        fig_top = plot_top_exposures(sample_quantified_df, top_n=3)
        assert isinstance(fig_top, plt.Figure)
        plt.close(fig_top)
        
        fig_trend = plot_trend_chart(trend_df)
        assert isinstance(fig_trend, plt.Figure)
        plt.close(fig_trend)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
