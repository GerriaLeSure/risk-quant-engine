"""
Tests for Loss Exceedance Curve utilities.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc.lec import lec_points, exceedance_prob, return_period


class TestLECPoints:
    """Tests for lec_points function."""
    
    def test_lec_probabilities_monotonic_decreasing(self):
        """Test that exceedance probabilities decrease with loss threshold."""
        np.random.seed(42)
        losses = np.random.lognormal(10, 1, 10000)
        
        lec_df = lec_points(losses, n_points=100)
        
        # Probabilities should be sorted descending (loss ascending)
        probs = lec_df["prob"].values
        assert all(probs[i] >= probs[i+1] for i in range(len(probs)-1))
    
    def test_lec_with_specific_probs(self):
        """Test LEC calculation with specific probabilities."""
        np.random.seed(42)
        losses = np.random.lognormal(11, 0.8, 5000)
        
        probs = [0.5, 0.2, 0.1, 0.05, 0.01]
        lec_df = lec_points(losses, probs=probs)
        
        assert len(lec_df) == len(probs)
        assert list(lec_df["prob"]) == sorted(probs, reverse=True)
        
        # Higher probability should give lower loss threshold
        assert lec_df.iloc[0]["loss"] < lec_df.iloc[-1]["loss"]
    
    def test_lec_prob_range(self):
        """Test that probabilities are in valid range."""
        losses = np.random.lognormal(10, 0.5, 1000)
        
        lec_df = lec_points(losses, n_points=50)
        
        assert all(0 <= p <= 1 for p in lec_df["prob"])
    
    def test_lec_constant_losses(self):
        """Test LEC with constant losses."""
        losses = np.full(1000, 100000.0)
        
        lec_df = lec_points(losses, n_points=10)
        
        # All losses should be the same value
        assert len(lec_df["loss"].unique()) == 1
        assert lec_df["loss"].iloc[0] == 100000.0
    
    def test_lec_invalid_prob_raises(self):
        """Test that invalid probabilities raise error."""
        losses = np.random.lognormal(10, 0.5, 1000)
        
        with pytest.raises(ValueError):
            lec_points(losses, probs=[1.5])  # > 1
        
        with pytest.raises(ValueError):
            lec_points(losses, probs=[-0.1])  # < 0


class TestExceedanceProb:
    """Tests for exceedance_prob function."""
    
    def test_exceedance_prob_zero_threshold(self):
        """Test exceedance probability at zero threshold."""
        losses = np.array([100, 200, 300, 400, 500])
        
        prob = exceedance_prob(losses, 0)
        
        # All losses exceed 0
        assert prob == 1.0
    
    def test_exceedance_prob_high_threshold(self):
        """Test exceedance probability at very high threshold."""
        losses = np.array([100, 200, 300, 400, 500])
        
        prob = exceedance_prob(losses, 1000)
        
        # No losses exceed 1000
        assert prob == 0.0
    
    def test_exceedance_prob_median(self):
        """Test exceedance probability near median."""
        losses = np.arange(1, 101)  # 1 to 100
        
        prob = exceedance_prob(losses, 50)
        
        # About 50% should exceed median
        assert 0.45 <= prob <= 0.55


class TestReturnPeriod:
    """Tests for return_period function."""
    
    def test_return_period_common_event(self):
        """Test return period for common event."""
        # 10% of losses exceed threshold
        losses = np.concatenate([np.zeros(900), np.ones(100)])
        
        period = return_period(losses, 0.5)
        
        # Return period should be 1/0.1 = 10 years
        assert 9 < period < 11
    
    def test_return_period_rare_event(self):
        """Test return period for rare event."""
        # 1% of losses exceed threshold
        losses = np.concatenate([np.zeros(990), np.ones(10)])
        
        period = return_period(losses, 0.5)
        
        # Return period should be 1/0.01 = 100 years
        assert 90 < period < 110
    
    def test_return_period_never_exceeded(self):
        """Test return period when threshold never exceeded."""
        losses = np.zeros(1000)
        
        period = return_period(losses, 1.0)
        
        assert period == float("inf")
    
    def test_return_period_always_exceeded(self):
        """Test return period when threshold always exceeded."""
        losses = np.ones(1000)
        
        period = return_period(losses, 0.5)
        
        # Return period should be 1 year
        assert period == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
