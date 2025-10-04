"""
Tests for risk register quantification.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc import load_register, quantify_register


class TestQuantifyRegister:
    """Tests for quantify_register function."""

    @pytest.fixture
    def sample_register(self):
        """Create sample risk register."""
        return pd.DataFrame(
            {
                "RiskID": ["R1", "R2", "R3"],
                "Category": ["Cyber", "Ops", "Financial"],
                "Description": ["Phishing", "Outage", "Market loss"],
                "FrequencyModel": ["Poisson", "Poisson", "Poisson"],
                "FreqParam1": [2.0, 1.5, 3.0],
                "FreqParam2": [None, None, None],
                "SeverityModel": ["Lognormal", "Normal", "Lognormal"],
                "SevParam1": [11.0, 100000, 10.5],
                "SevParam2": [0.8, 30000, 0.6],
                "SevParam3": [None, None, None],
                "ControlEffectiveness": [0.3, 0.2, 0.0],
                "ResidualFactor": [0.7, 0.8, 1.0],
            }
        )

    def test_quantify_returns_dataframe(self, sample_register):
        """Test that quantify_register returns DataFrame."""
        result = quantify_register(sample_register, n_sims=1000, seed=42)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4  # 3 risks + 1 portfolio total

    def test_quantify_has_required_columns(self, sample_register):
        """Test that result has all required metric columns."""
        result = quantify_register(sample_register, n_sims=1000, seed=42)

        required_cols = [
            "SimMean",
            "SimMedian",
            "SimStd",
            "SimP90",
            "SimP95",
            "SimP99",
            "SimVaR95",
            "SimVaR99",
            "SimTVaR95",
            "SimTVaR99",
        ]

        for col in required_cols:
            assert col in result.columns

    def test_quantify_metrics_are_numeric(self, sample_register):
        """Test that all metric columns are numeric."""
        result = quantify_register(sample_register, n_sims=1000, seed=42)

        metric_cols = [
            "SimMean",
            "SimMedian",
            "SimStd",
            "SimP90",
            "SimP95",
            "SimP99",
            "SimVaR95",
            "SimVaR99",
            "SimTVaR95",
            "SimTVaR99",
        ]

        for col in metric_cols:
            assert pd.api.types.is_numeric_dtype(result[col])

    def test_quantify_deterministic_with_seed(self, sample_register):
        """Test that results are deterministic with seed."""
        result1 = quantify_register(sample_register, n_sims=1000, seed=42)
        result2 = quantify_register(sample_register, n_sims=1000, seed=42)

        # Check that SimMean values match
        np.testing.assert_array_almost_equal(result1["SimMean"].values, result2["SimMean"].values)

    def test_quantify_percentile_ordering(self, sample_register):
        """Test that percentiles are properly ordered."""
        result = quantify_register(sample_register, n_sims=5000, seed=42)

        # For each risk (excluding portfolio total)
        for idx in range(len(sample_register)):
            p90 = result.loc[idx, "SimP90"]
            p95 = result.loc[idx, "SimP95"]
            p99 = result.loc[idx, "SimP99"]

            # Check ordering
            assert p90 <= p95 <= p99, f"Risk {idx}: P90={p90}, P95={p95}, P99={p99}"

    def test_quantify_var_equals_percentile(self, sample_register):
        """Test that VaR equals corresponding percentile."""
        result = quantify_register(sample_register, n_sims=5000, seed=42)

        for idx in range(len(result)):
            # VaR95 should equal P95
            np.testing.assert_almost_equal(
                result.loc[idx, "SimVaR95"], result.loc[idx, "SimP95"], decimal=2
            )

            # VaR99 should equal P99
            np.testing.assert_almost_equal(
                result.loc[idx, "SimVaR99"], result.loc[idx, "SimP99"], decimal=2
            )

    def test_quantify_tvar_greater_than_var(self, sample_register):
        """Test that TVaR >= VaR (tail average should be at least threshold)."""
        result = quantify_register(sample_register, n_sims=5000, seed=42)

        for idx in range(len(result)):
            assert result.loc[idx, "SimTVaR95"] >= result.loc[idx, "SimVaR95"]
            assert result.loc[idx, "SimTVaR99"] >= result.loc[idx, "SimVaR99"]

    def test_quantify_higher_sigma_increases_var(self):
        """Test that higher sigma increases VaR95."""
        # Create two identical risks except for sigma
        register_low = pd.DataFrame(
            {
                "RiskID": ["R1"],
                "Category": ["Test"],
                "Description": ["Low volatility"],
                "FrequencyModel": ["Poisson"],
                "FreqParam1": [2.0],
                "FreqParam2": [None],
                "SeverityModel": ["Lognormal"],
                "SevParam1": [11.0],
                "SevParam2": [0.5],  # Low sigma
                "SevParam3": [None],
                "ControlEffectiveness": [0.0],
                "ResidualFactor": [1.0],
            }
        )

        register_high = pd.DataFrame(
            {
                "RiskID": ["R1"],
                "Category": ["Test"],
                "Description": ["High volatility"],
                "FrequencyModel": ["Poisson"],
                "FreqParam1": [2.0],
                "FreqParam2": [None],
                "SeverityModel": ["Lognormal"],
                "SevParam1": [11.0],
                "SevParam2": [1.5],  # High sigma
                "SevParam3": [None],
                "ControlEffectiveness": [0.0],
                "ResidualFactor": [1.0],
            }
        )

        result_low = quantify_register(register_low, n_sims=10000, seed=42)
        result_high = quantify_register(register_high, n_sims=10000, seed=42)

        # Higher sigma should lead to higher VaR
        assert result_high.loc[0, "SimVaR95"] > result_low.loc[0, "SimVaR95"]

    def test_quantify_includes_portfolio_total(self, sample_register):
        """Test that result includes portfolio total row."""
        result = quantify_register(sample_register, n_sims=1000, seed=42)

        # Last row should be portfolio total
        assert result.iloc[-1]["RiskID"] == "PORTFOLIO_TOTAL"
        assert result.iloc[-1]["Category"] == "Portfolio"

    def test_quantify_portfolio_total_is_sum(self, sample_register):
        """Test that portfolio mean approximately equals sum of risk means."""
        result = quantify_register(sample_register, n_sims=10000, seed=42)

        # Sum of individual risk means
        risk_means_sum = result.iloc[:-1]["SimMean"].sum()

        # Portfolio mean
        portfolio_mean = result.iloc[-1]["SimMean"]

        # Should be approximately equal (within 5%)
        assert abs(portfolio_mean - risk_means_sum) / risk_means_sum < 0.05

    def test_quantify_with_sample_data(self):
        """Test quantify with actual sample data file."""
        data_path = Path(__file__).parent.parent / "data" / "sample_risk_register.csv"

        if not data_path.exists():
            pytest.skip("Sample data file not found")

        register = load_register(str(data_path))
        result = quantify_register(register, n_sims=5000, seed=42)

        # Should have 10 risks + 1 portfolio total
        assert len(result) == 11

        # All metrics should be non-negative
        assert (result["SimMean"] >= 0).all()
        assert (result["SimVaR95"] >= 0).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
