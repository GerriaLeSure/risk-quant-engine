"""
Tests for Monte Carlo simulation module
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from monte_carlo import MonteCarloSimulator, run_sensitivity_analysis


class TestMonteCarloSimulator:
    """Test suite for MonteCarloSimulator class"""

    def test_initialization(self):
        """Test simulator initialization"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)
        assert simulator.n_simulations == 1000

    def test_simulate_risk_event_shape(self):
        """Test that simulation returns correct array shape"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        losses = simulator.simulate_risk_event(
            likelihood_mean=0.3,
            likelihood_std=0.1,
            impact_min=100000,
            impact_most_likely=500000,
            impact_max=1000000,
        )

        assert len(losses) == 1000
        assert isinstance(losses, np.ndarray)

    def test_simulate_risk_event_values(self):
        """Test that simulated values are within expected ranges"""
        simulator = MonteCarloSimulator(n_simulations=10000, random_seed=42)

        likelihood_mean = 0.3
        impact_min = 100000
        impact_max = 1000000

        losses = simulator.simulate_risk_event(
            likelihood_mean=likelihood_mean,
            likelihood_std=0.1,
            impact_min=impact_min,
            impact_most_likely=500000,
            impact_max=impact_max,
        )

        # Check that all losses are non-negative
        assert np.all(losses >= 0)

        # Check that losses don't exceed maximum possible value
        assert np.all(losses <= impact_max)

    def test_simulate_risk_event_distributions(self):
        """Test different distribution types"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        distributions = ["triangular", "normal", "lognormal"]

        for dist_type in distributions:
            losses = simulator.simulate_risk_event(
                likelihood_mean=0.5,
                likelihood_std=0.1,
                impact_min=100000,
                impact_most_likely=500000,
                impact_max=1000000,
                distribution_type=dist_type,
            )

            assert len(losses) == 1000
            assert np.all(losses >= 0)

    def test_simulate_portfolio(self):
        """Test portfolio simulation"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        # Create sample risk register
        risks_df = pd.DataFrame(
            {
                "risk_id": ["R001", "R002", "R003"],
                "risk_name": ["Risk 1", "Risk 2", "Risk 3"],
                "category": ["Tech", "Ops", "Financial"],
                "likelihood": [0.3, 0.4, 0.2],
                "impact": [500000, 300000, 800000],
                "likelihood_std": [0.1, 0.1, 0.08],
                "impact_min": [200000, 100000, 300000],
                "impact_most_likely": [500000, 300000, 800000],
                "impact_max": [1000000, 600000, 1500000],
            }
        )

        results = simulator.simulate_portfolio(risks_df)

        # Check that results DataFrame has expected columns
        assert "risk_id" in results.columns
        assert "mean_loss" in results.columns
        assert "p95_loss" in results.columns
        assert "simulations" in results.columns

        # Check that we have results for all risks
        assert len(results) == len(risks_df)

        # Check that all statistics are non-negative
        assert (results["mean_loss"] >= 0).all()
        assert (results["p95_loss"] >= 0).all()

    def test_aggregate_portfolio_risk(self):
        """Test portfolio risk aggregation"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        # Create sample results
        risks_df = pd.DataFrame(
            {
                "risk_id": ["R001", "R002"],
                "risk_name": ["Risk 1", "Risk 2"],
                "category": ["Tech", "Ops"],
                "likelihood": [0.3, 0.4],
                "impact": [500000, 300000],
                "likelihood_std": [0.1, 0.1],
                "impact_min": [200000, 100000],
                "impact_most_likely": [500000, 300000],
                "impact_max": [1000000, 600000],
            }
        )

        results = simulator.simulate_portfolio(risks_df)
        portfolio_stats = simulator.aggregate_portfolio_risk(results)

        # Check that portfolio stats have expected keys
        assert "total_mean_loss" in portfolio_stats
        assert "total_p95_loss" in portfolio_stats
        assert "total_var_95" in portfolio_stats
        assert "n_simulations" in portfolio_stats

        # Check that values are reasonable
        assert portfolio_stats["total_mean_loss"] >= 0
        assert portfolio_stats["total_p95_loss"] >= portfolio_stats["total_mean_loss"]
        assert portfolio_stats["n_simulations"] == 1000

    def test_beta_params_from_moments(self):
        """Test beta distribution parameter calculation"""
        simulator = MonteCarloSimulator()

        mean = 0.5
        std = 0.1

        alpha, beta = simulator._beta_params_from_moments(mean, std)

        # Check that parameters are positive
        assert alpha > 0
        assert beta > 0

    def test_sample_likelihood(self):
        """Test likelihood sampling"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        likelihood = simulator._sample_likelihood(0.5, 0.1)

        # Check shape
        assert len(likelihood) == 1000

        # Check that values are probabilities (0-1)
        assert np.all(likelihood >= 0)
        assert np.all(likelihood <= 1)

    def test_sample_impact(self):
        """Test impact sampling"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        min_val = 100000
        most_likely = 500000
        max_val = 1000000

        impact = simulator._sample_impact(min_val, most_likely, max_val, "triangular")

        # Check shape
        assert len(impact) == 1000

        # Check that values are within range
        assert np.all(impact >= min_val)
        assert np.all(impact <= max_val)

    def test_invalid_distribution_type(self):
        """Test that invalid distribution type raises error"""
        simulator = MonteCarloSimulator()

        with pytest.raises(ValueError):
            simulator.simulate_risk_event(
                likelihood_mean=0.3,
                likelihood_std=0.1,
                impact_min=100000,
                impact_most_likely=500000,
                impact_max=1000000,
                distribution_type="invalid_type",
            )

    def test_reproducibility_with_seed(self):
        """Test that results are reproducible with same seed"""
        # Reset the seed before each simulation
        np.random.seed(42)
        simulator1 = MonteCarloSimulator(n_simulations=1000)
        losses1 = simulator1.simulate_risk_event(
            likelihood_mean=0.3,
            likelihood_std=0.1,
            impact_min=100000,
            impact_most_likely=500000,
            impact_max=1000000,
        )

        # Reset the seed again to get same results
        np.random.seed(42)
        simulator2 = MonteCarloSimulator(n_simulations=1000)
        losses2 = simulator2.simulate_risk_event(
            likelihood_mean=0.3,
            likelihood_std=0.1,
            impact_min=100000,
            impact_most_likely=500000,
            impact_max=1000000,
        )

        # Results should be identical with same seed
        np.testing.assert_array_equal(losses1, losses2)


class TestSensitivityAnalysis:
    """Test suite for sensitivity analysis"""

    def test_run_sensitivity_analysis(self):
        """Test sensitivity analysis function"""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        base_risk = {
            "likelihood_mean": 0.3,
            "likelihood_std": 0.1,
            "impact_min": 100000,
            "impact_most_likely": 500000,
            "impact_max": 1000000,
        }

        results = run_sensitivity_analysis(
            simulator, base_risk, "likelihood_mean", (0.1, 0.5), n_steps=5
        )

        # Check that results DataFrame has expected shape
        assert len(results) == 5
        assert "likelihood_mean" in results.columns
        assert "mean_loss" in results.columns
        assert "p95_loss" in results.columns

        # Check that parameter values are within range
        assert results["likelihood_mean"].min() >= 0.1
        assert results["likelihood_mean"].max() <= 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
