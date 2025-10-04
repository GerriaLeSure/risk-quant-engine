"""
Tests for distribution functions.

Tests verify statistical properties and parameter constraints.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc.distributions import (
    sample_frequency_negbin,
    sample_frequency_poisson,
    sample_severity_lognormal,
    sample_severity_normal,
    sample_severity_pert,
)


class TestPoissonDistribution:
    """Tests for Poisson frequency distribution."""

    def test_poisson_returns_integers(self):
        """Test that Poisson returns integer event counts."""
        rng = np.random.default_rng(42)
        samples = sample_frequency_poisson(2.5, 1000, rng)

        assert all(s == int(s) for s in samples)

    def test_poisson_negative_lambda_raises(self):
        """Test that negative lambda raises error."""
        with pytest.raises(ValueError, match="lambda must be >= 0"):
            sample_frequency_poisson(-1.0, 100)

    def test_poisson_zero_lambda_gives_zeros(self):
        """Test that lambda=0 gives all zeros."""
        rng = np.random.default_rng(42)
        samples = sample_frequency_poisson(0.0, 500, rng)

        assert np.all(samples == 0)


class TestNegBinDistribution:
    """Tests for Negative Binomial frequency distribution."""

    def test_negbin_returns_integers(self):
        """Test that NegBin returns integer event counts."""
        rng = np.random.default_rng(42)
        samples = sample_frequency_negbin(3.0, 0.6, 1000, rng)

        assert all(s == int(s) for s in samples)

    def test_negbin_invalid_r_raises(self):
        """Test that invalid r raises error."""
        with pytest.raises(ValueError, match="r must be > 0"):
            sample_frequency_negbin(0.0, 0.5, 100)

    def test_negbin_invalid_p_raises(self):
        """Test that invalid p raises error."""
        with pytest.raises(ValueError, match="p must be in"):
            sample_frequency_negbin(3.0, 1.5, 100)

        with pytest.raises(ValueError, match="p must be in"):
            sample_frequency_negbin(3.0, 0.0, 100)

    def test_negbin_mean_variance_match_theory(self):
        """Test that NegBin mean/variance match expected within tolerance."""
        rng = np.random.default_rng(42)
        r, p = 5.0, 0.6

        # Theoretical values for NegBin(r, p)
        # Mean = r * (1-p) / p
        # Variance = r * (1-p) / p^2
        expected_mean = r * (1 - p) / p
        expected_var = r * (1 - p) / (p**2)

        # Large sample
        samples = sample_frequency_negbin(r, p, 50000, rng)

        sample_mean = np.mean(samples)
        sample_var = np.var(samples)

        # Check within 5% tolerance
        assert abs(sample_mean - expected_mean) / expected_mean < 0.05
        assert abs(sample_var - expected_var) / expected_var < 0.05


class TestLognormalDistribution:
    """Tests for Lognormal severity distribution."""

    def test_lognormal_all_positive(self):
        """Test that lognormal returns only positive values."""
        rng = np.random.default_rng(42)
        samples = sample_severity_lognormal(10.0, 1.0, 1000, rng)

        assert np.all(samples > 0)

    def test_lognormal_increasing_sigma_increases_p99(self):
        """Test that increasing sigma increases p99."""
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)

        mu = 11.0
        sigma_low = 0.5
        sigma_high = 1.5

        samples_low = sample_severity_lognormal(mu, sigma_low, 10000, rng1)
        samples_high = sample_severity_lognormal(mu, sigma_high, 10000, rng2)

        p99_low = np.percentile(samples_low, 99)
        p99_high = np.percentile(samples_high, 99)

        assert p99_high > p99_low

    def test_lognormal_zero_events_returns_empty(self):
        """Test that zero events returns empty array."""
        samples = sample_severity_lognormal(10.0, 0.5, 0)

        assert len(samples) == 0

    def test_lognormal_negative_sigma_raises(self):
        """Test that negative sigma raises error."""
        with pytest.raises(ValueError, match="sigma must be > 0"):
            sample_severity_lognormal(10.0, -0.5, 100)


class TestNormalDistribution:
    """Tests for Normal severity distribution."""

    def test_normal_truncated_at_zero(self):
        """Test that normal is truncated at zero (non-negative)."""
        rng = np.random.default_rng(42)
        # Use small mean to get some truncation
        samples = sample_severity_normal(50000, 100000, 10000, rng)

        assert np.all(samples >= 0)

    def test_normal_negative_sigma_raises(self):
        """Test that negative sigma raises error."""
        with pytest.raises(ValueError, match="sigma must be > 0"):
            sample_severity_normal(100000, -10000, 100)

    def test_normal_zero_events_returns_empty(self):
        """Test that zero events returns empty array."""
        samples = sample_severity_normal(100000, 20000, 0)

        assert len(samples) == 0


class TestPERTDistribution:
    """Tests for PERT severity distribution."""

    def test_pert_returns_values_in_range(self):
        """Test that PERT returns values in [min, max]."""
        rng = np.random.default_rng(42)
        min_val, mode, max_val = 50000, 100000, 300000

        samples = sample_severity_pert(min_val, mode, max_val, 5000, rng)

        assert np.all(samples >= min_val)
        assert np.all(samples <= max_val)

    def test_pert_invalid_order_raises(self):
        """Test that invalid min/mode/max order raises error."""
        with pytest.raises(ValueError, match="min <= mode <= max"):
            sample_severity_pert(100000, 50000, 200000, 100)

    def test_pert_degenerate_case(self):
        """Test PERT when min=mode=max."""
        rng = np.random.default_rng(42)
        constant = 100000

        samples = sample_severity_pert(constant, constant, constant, 100, rng)

        assert np.all(samples == constant)

    def test_pert_mode_affects_distribution(self):
        """Test that mode parameter affects distribution shape."""
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)

        min_val, max_val = 50000, 300000
        mode_low = 75000  # Skewed left
        mode_high = 250000  # Skewed right

        samples_low = sample_severity_pert(min_val, mode_low, max_val, 5000, rng1)
        samples_high = sample_severity_pert(min_val, mode_high, max_val, 5000, rng2)

        # Median should be higher when mode is higher
        assert np.median(samples_high) > np.median(samples_low)

    def test_pert_zero_events_returns_empty(self):
        """Test that zero events returns empty array."""
        samples = sample_severity_pert(50000, 100000, 300000, 0)

        assert len(samples) == 0


class TestDistributionMonotonicity:
    """Tests for statistical monotonicity properties."""

    def test_lognormal_percentile_ordering(self):
        """Test that p99 >= p95 >= p90 >= p50 for lognormal."""
        rng = np.random.default_rng(42)
        samples = sample_severity_lognormal(11.0, 0.8, 10000, rng)

        p50 = np.percentile(samples, 50)
        p90 = np.percentile(samples, 90)
        p95 = np.percentile(samples, 95)
        p99 = np.percentile(samples, 99)

        assert p50 <= p90 <= p95 <= p99

    def test_normal_percentile_ordering(self):
        """Test that p99 >= p95 >= p90 >= p50 for normal."""
        rng = np.random.default_rng(42)
        samples = sample_severity_normal(200000, 50000, 10000, rng)

        p50 = np.percentile(samples, 50)
        p90 = np.percentile(samples, 90)
        p95 = np.percentile(samples, 95)
        p99 = np.percentile(samples, 99)

        assert p50 <= p90 <= p95 <= p99

    def test_pert_percentile_ordering(self):
        """Test that p99 >= p95 >= p90 >= p50 for PERT."""
        rng = np.random.default_rng(42)
        samples = sample_severity_pert(50000, 150000, 400000, 10000, rng)

        p50 = np.percentile(samples, 50)
        p90 = np.percentile(samples, 90)
        p95 = np.percentile(samples, 95)
        p99 = np.percentile(samples, 99)

        assert p50 <= p90 <= p95 <= p99


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
