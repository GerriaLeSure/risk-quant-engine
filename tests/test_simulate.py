"""
Tests for simulation functions.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc.simulate import simulate_annual_loss, simulate_portfolio


class TestSimulateAnnualLoss:
    """Tests for simulate_annual_loss function."""

    def test_zero_frequency_gives_zero_loss(self):
        """Test that Poisson(0) always gives zero loss."""
        risk = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "Poisson",
                "FreqParam1": 0.0,
                "FreqParam2": None,
                "SeverityModel": "Lognormal",
                "SevParam1": 12.0,
                "SevParam2": 1.0,
                "SevParam3": None,
                "ResidualFactor": 1.0,
                "ControlEffectiveness": 0.0,
            }
        )

        losses = simulate_annual_loss(risk, n_sims=1000, seed=42)

        assert len(losses) == 1000
        assert np.all(losses == 0.0)

    def test_deterministic_with_seed(self):
        """Test that same seed produces same results."""
        risk = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "Poisson",
                "FreqParam1": 2.0,
                "FreqParam2": None,
                "SeverityModel": "Lognormal",
                "SevParam1": 12.0,
                "SevParam2": 0.8,
                "SevParam3": None,
                "ResidualFactor": 1.0,
                "ControlEffectiveness": 0.0,
            }
        )

        losses1 = simulate_annual_loss(risk, n_sims=1000, seed=42)
        losses2 = simulate_annual_loss(risk, n_sims=1000, seed=42)

        np.testing.assert_array_equal(losses1, losses2)

    def test_output_shape(self):
        """Test output has correct shape."""
        risk = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "Poisson",
                "FreqParam1": 1.5,
                "FreqParam2": None,
                "SeverityModel": "Normal",
                "SevParam1": 100000,
                "SevParam2": 30000,
                "SevParam3": None,
                "ResidualFactor": 1.0,
                "ControlEffectiveness": 0.0,
            }
        )

        n_sims = 5000
        losses = simulate_annual_loss(risk, n_sims=n_sims, seed=42)

        assert losses.shape == (n_sims,)
        assert isinstance(losses, np.ndarray)

    def test_residual_factor_reduces_losses(self):
        """Test that residual factor < 1 reduces losses."""
        risk_full = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "Poisson",
                "FreqParam1": 3.0,
                "FreqParam2": None,
                "SeverityModel": "Lognormal",
                "SevParam1": 11.0,
                "SevParam2": 0.5,
                "SevParam3": None,
                "ResidualFactor": 1.0,
                "ControlEffectiveness": 0.0,
            }
        )

        risk_reduced = risk_full.copy()
        risk_reduced["ResidualFactor"] = 0.5

        losses_full = simulate_annual_loss(risk_full, n_sims=10000, seed=42)
        losses_reduced = simulate_annual_loss(risk_reduced, n_sims=10000, seed=42)

        # Mean of reduced should be less than full
        assert np.mean(losses_reduced) < np.mean(losses_full)

    def test_control_effectiveness_reduces_losses(self):
        """Test that control effectiveness reduces losses."""
        risk_no_control = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "Poisson",
                "FreqParam1": 2.5,
                "FreqParam2": None,
                "SeverityModel": "Normal",
                "SevParam1": 200000,
                "SevParam2": 50000,
                "SevParam3": None,
                "ResidualFactor": 1.0,
                "ControlEffectiveness": 0.0,
            }
        )

        risk_with_control = risk_no_control.copy()
        risk_with_control["ControlEffectiveness"] = 0.5

        losses_no_control = simulate_annual_loss(risk_no_control, n_sims=10000, seed=42)
        losses_with_control = simulate_annual_loss(risk_with_control, n_sims=10000, seed=42)

        assert np.mean(losses_with_control) < np.mean(losses_no_control)

    def test_negbin_frequency(self):
        """Test NegBin frequency model."""
        risk = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "NegBin",
                "FreqParam1": 3.0,  # r
                "FreqParam2": 0.6,  # p
                "SeverityModel": "Lognormal",
                "SevParam1": 10.0,
                "SevParam2": 0.5,
                "SevParam3": None,
                "ResidualFactor": 1.0,
                "ControlEffectiveness": 0.0,
            }
        )

        losses = simulate_annual_loss(risk, n_sims=1000, seed=42)

        assert len(losses) == 1000
        assert np.all(losses >= 0)

    def test_pert_severity(self):
        """Test PERT severity model."""
        risk = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "Poisson",
                "FreqParam1": 2.0,
                "FreqParam2": None,
                "SeverityModel": "PERT",
                "SevParam1": 50000,  # min
                "SevParam2": 100000,  # mode
                "SevParam3": 300000,  # max
                "ResidualFactor": 1.0,
                "ControlEffectiveness": 0.0,
            }
        )

        losses = simulate_annual_loss(risk, n_sims=5000, seed=42)

        assert len(losses) == 5000
        assert np.all(losses >= 0)

        # Non-zero losses should be within reasonable bounds
        # (accounting for sum of multiple events)
        non_zero = losses[losses > 0]
        if len(non_zero) > 0:
            # Each event is in [min, max], but annual loss is sum
            assert np.min(non_zero) >= 50000  # At least one event at min

    def test_invalid_residual_factor_raises(self):
        """Test that invalid residual factor raises error."""
        risk = pd.Series(
            {
                "RiskID": "R_TEST",
                "FrequencyModel": "Poisson",
                "FreqParam1": 1.0,
                "SeverityModel": "Lognormal",
                "SevParam1": 10.0,
                "SevParam2": 0.5,
                "ResidualFactor": 1.5,  # Invalid: > 1
            }
        )

        with pytest.raises(ValueError, match="ResidualFactor"):
            simulate_annual_loss(risk, n_sims=100, seed=42)


class TestSimulatePortfolio:
    """Tests for simulate_portfolio function."""

    @pytest.fixture
    def sample_register(self):
        """Create a sample risk register."""
        return pd.DataFrame(
            {
                "RiskID": ["R1", "R2", "R3"],
                "FrequencyModel": ["Poisson", "Poisson", "Poisson"],
                "FreqParam1": [1.0, 2.0, 0.5],
                "FreqParam2": [None, None, None],
                "SeverityModel": ["Lognormal", "Normal", "PERT"],
                "SevParam1": [11.0, 100000, 50000],
                "SevParam2": [0.5, 30000, 100000],
                "SevParam3": [None, None, 200000],
                "ResidualFactor": [1.0, 0.8, 0.7],
                "ControlEffectiveness": [0.0, 0.2, 0.1],
            }
        )

    def test_portfolio_output_shape(self, sample_register):
        """Test portfolio output has correct shape and columns."""
        n_sims = 1000
        result = simulate_portfolio(sample_register, n_sims=n_sims, seed=42)

        assert len(result) == n_sims
        assert "portfolio_loss" in result.columns
        assert "by_risk:R1" in result.columns
        assert "by_risk:R2" in result.columns
        assert "by_risk:R3" in result.columns

    def test_portfolio_is_sum_of_risks(self, sample_register):
        """Test that portfolio loss equals sum of individual risks."""
        result = simulate_portfolio(sample_register, n_sims=1000, seed=42)

        portfolio = result["portfolio_loss"].values
        risk_sum = (
            result["by_risk:R1"].values + result["by_risk:R2"].values + result["by_risk:R3"].values
        )

        np.testing.assert_array_almost_equal(portfolio, risk_sum)

    def test_portfolio_deterministic_with_seed(self, sample_register):
        """Test deterministic results with seed."""
        result1 = simulate_portfolio(sample_register, n_sims=500, seed=42)
        result2 = simulate_portfolio(sample_register, n_sims=500, seed=42)

        np.testing.assert_array_equal(
            result1["portfolio_loss"].values, result2["portfolio_loss"].values
        )

    def test_portfolio_all_zero_frequencies(self):
        """Test portfolio with all zero frequencies."""
        register = pd.DataFrame(
            {
                "RiskID": ["R1", "R2"],
                "FrequencyModel": ["Poisson", "Poisson"],
                "FreqParam1": [0.0, 0.0],
                "FreqParam2": [None, None],
                "SeverityModel": ["Lognormal", "Normal"],
                "SevParam1": [10.0, 100000],
                "SevParam2": [0.5, 20000],
                "SevParam3": [None, None],
                "ResidualFactor": [1.0, 1.0],
                "ControlEffectiveness": [0.0, 0.0],
            }
        )

        result = simulate_portfolio(register, n_sims=500, seed=42)

        assert np.all(result["portfolio_loss"].values == 0.0)
        assert np.all(result["by_risk:R1"].values == 0.0)
        assert np.all(result["by_risk:R2"].values == 0.0)

    def test_empty_register_raises(self):
        """Test that empty register raises error."""
        empty_register = pd.DataFrame()

        with pytest.raises(ValueError, match="empty"):
            simulate_portfolio(empty_register, n_sims=100)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
