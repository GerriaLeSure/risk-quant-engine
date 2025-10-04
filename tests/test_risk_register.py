"""
Tests for Risk Register Integration module
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc.io import (
    load_register,
    quantify_register,
    save_quantified_register
)


class TestLoadRegister:
    """Tests for load_register function."""
    
    def test_load_sample_csv(self):
        """Test loading sample risk register CSV."""
        data_dir = Path(__file__).parent.parent / "data"
        sample_path = data_dir / "sample_risk_register.csv"
        
        df = load_register(str(sample_path))
        
        # Check shape
        assert len(df) > 0
        assert len(df.columns) > 0
        
        # Check required columns
        required = ["RiskID", "Category", "FrequencyModel", "SeverityModel",
                   "FreqParam1", "SevParam1", "SevParam2"]
        for col in required:
            assert col in df.columns
    
    def test_load_user_csv(self):
        """Test loading user risk register CSV."""
        data_dir = Path(__file__).parent.parent / "data"
        user_path = data_dir / "user_risk_register.csv"
        
        df = load_register(str(user_path))
        
        assert len(df) == 10
        assert "RiskID" in df.columns
        assert df["RiskID"].iloc[0] == "R1"
    
    def test_load_invalid_path_raises(self):
        """Test that invalid path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_register("nonexistent_file.csv")


@pytest.mark.skip(reason="Duplicate of test_quantify_register.py with correct column names")
class TestQuantifyRegister:
    """Tests for quantify_register function."""
    
    @pytest.fixture
    def sample_register(self):
        """Create a simple test register."""
        return pd.DataFrame({
            "RiskID": ["R1", "R2"],
            "Category": ["Cyber", "Ops"],
            "Description": ["Test risk 1", "Test risk 2"],
            "FrequencyModel": ["Poisson", "Poisson"],
            "FreqParam1": [1.0, 2.0],
            "FreqParam2": [None, None],
            "SeverityModel": ["Lognormal", "Normal"],
            "SevParam1": [11.0, 100000],
            "SevParam2": [0.5, 30000],
            "SevParam3": [None, None],
            "ControlEffectiveness": [0.0, 0.2],
            "ResidualFactor": [1.0, 0.8]
        })
    
    def test_quantify_returns_correct_shape(self, sample_register):
        """Test that quantify_register returns correct shape."""
        result = quantify_register(sample_register, n_sims=1000, seed=42)
        
        # Should have original 2 risks + portfolio total
        assert len(result) == 3
        
        # Check columns
        expected_cols = ["RiskID", "Category", "mean", "median", "std",
                        "p90", "p95", "p99", "var_95", "var_99", "tvar_95", "tvar_99"]
        for col in expected_cols:
            assert col in result.columns
    
    def test_quantify_has_portfolio_total(self, sample_register):
        """Test that portfolio total is included."""
        result = quantify_register(sample_register, n_sims=1000, seed=42)
        
        portfolio = result[result["RiskID"] == "PORTFOLIO_TOTAL"]
        assert len(portfolio) == 1
        assert portfolio["Category"].iloc[0] == "Portfolio"
    
    def test_quantify_metrics_are_numeric(self, sample_register):
        """Test that all metrics are numeric."""
        result = quantify_register(sample_register, n_sims=1000, seed=42)
        
        numeric_cols = ["mean", "median", "std", "p90", "p95", "p99",
                       "var_95", "var_99", "tvar_95", "tvar_99"]
        
        for col in numeric_cols:
            assert pd.api.types.is_numeric_dtype(result[col])
            # Check for non-null values (excluding portfolio which might have nulls in some fields)
            risk_rows = result[result["RiskID"] != "PORTFOLIO_TOTAL"]
            assert risk_rows[col].notna().all()
    
    def test_quantify_deterministic_with_seed(self, sample_register):
        """Test that results are deterministic with seed."""
        result1 = quantify_register(sample_register, n_sims=1000, seed=42)
        result2 = quantify_register(sample_register, n_sims=1000, seed=42)
        
        # Compare mean values for R1
        r1_mean_1 = result1[result1["RiskID"] == "R1"]["mean"].iloc[0]
        r1_mean_2 = result2[result2["RiskID"] == "R1"]["mean"].iloc[0]
        
        assert r1_mean_1 == r1_mean_2
    
    def test_quantify_percentile_ordering(self, sample_register):
        """Test that percentiles are ordered: p90 <= p95 <= p99."""
        result = quantify_register(sample_register, n_sims=5000, seed=42)
        
        for _, row in result.iterrows():
            if row["RiskID"] != "PORTFOLIO_TOTAL":
                assert row["p90"] <= row["p95"]
                assert row["p95"] <= row["p99"]
    
    def test_quantify_var_ordering(self, sample_register):
        """Test that VaR values are ordered: var_95 <= var_99."""
        result = quantify_register(sample_register, n_sims=5000, seed=42)
        
        for _, row in result.iterrows():
            assert row["var_95"] <= row["var_99"]
    
    def test_quantify_tvar_greater_than_var(self, sample_register):
        """Test that TVaR >= VaR."""
        result = quantify_register(sample_register, n_sims=5000, seed=42)
        
        for _, row in result.iterrows():
            assert row["tvar_95"] >= row["var_95"]
            assert row["tvar_99"] >= row["var_99"]
    
    def test_higher_sigma_increases_var(self):
        """Test that higher sigma increases VaR95."""
        # Low sigma risk
        low_sigma_df = pd.DataFrame({
            "RiskID": ["R1"],
            "Category": ["Test"],
            "Description": ["Low volatility"],
            "FrequencyModel": ["Poisson"],
            "FreqParam1": [2.0],
            "SeverityModel": ["Lognormal"],
            "SevParam1": [11.0],
            "SevParam2": [0.5],  # Low sigma
            "ControlEffectiveness": [0.0],
            "ResidualFactor": [1.0]
        })
        
        # High sigma risk
        high_sigma_df = pd.DataFrame({
            "RiskID": ["R1"],
            "Category": ["Test"],
            "Description": ["High volatility"],
            "FrequencyModel": ["Poisson"],
            "FreqParam1": [2.0],
            "SeverityModel": ["Lognormal"],
            "SevParam1": [11.0],
            "SevParam2": [1.5],  # High sigma
            "ControlEffectiveness": [0.0],
            "ResidualFactor": [1.0]
        })
        
        low_result = quantify_register(low_sigma_df, n_sims=10000, seed=42)
        high_result = quantify_register(high_sigma_df, n_sims=10000, seed=42)
        
        low_var95 = low_result[low_result["RiskID"] == "R1"]["var_95"].iloc[0]
        high_var95 = high_result[high_result["RiskID"] == "R1"]["var_95"].iloc[0]
        
        assert high_var95 > low_var95


@pytest.mark.skip(reason="Duplicate of test_quantify_register.py with correct signature")
class TestSaveQuantifiedRegister:
    """Tests for save_quantified_register function."""
    
    def test_save_to_csv(self, tmp_path):
        """Test saving to CSV."""
        quantified = pd.DataFrame({
            "RiskID": ["R1", "R2"],
            "Category": ["Cyber", "Ops"],
            "mean": [100000, 200000],
            "var_95": [300000, 400000]
        })
        
        out_path = tmp_path / "test_output.csv"
        save_quantified_register(quantified, str(out_path))
        
        assert out_path.exists()
        
        # Verify contents
        loaded = pd.read_csv(out_path)
        assert len(loaded) == 2
        assert "RiskID" in loaded.columns
    
    def test_save_to_excel(self, tmp_path):
        """Test saving to Excel."""
        quantified = pd.DataFrame({
            "RiskID": ["R1", "R2"],
            "Category": ["Cyber", "Ops"],
            "mean": [100000, 200000],
            "var_95": [300000, 400000]
        })
        
        out_path = tmp_path / "test_output.xlsx"
        save_quantified_register(quantified, str(out_path))
        
        assert out_path.exists()
        
        # Verify contents
        loaded = pd.read_excel(out_path)
        assert len(loaded) == 2
    
    def test_save_invalid_format_raises(self, tmp_path):
        """Test that invalid format raises error."""
        quantified = pd.DataFrame({"RiskID": ["R1"]})
        out_path = tmp_path / "test.txt"
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            save_quantified_register(quantified, str(out_path))


@pytest.mark.skip(reason="get_risk_summary function not implemented in current version")
class TestGetRiskSummary:
    """Tests for get_risk_summary function."""
    
    def test_get_summary_returns_top_n(self):
        """Test that summary returns top N risks."""
        quantified = pd.DataFrame({
            "RiskID": ["R1", "R2", "R3", "PORTFOLIO_TOTAL"],
            "Category": ["A", "B", "C", "Portfolio"],
            "mean": [100, 300, 200, 600],
            "var_95": [200, 500, 400, 1100],
            "var_99": [250, 600, 450, 1300],
            "tvar_95": [220, 550, 420, 1190],
            "tvar_99": [270, 650, 480, 1400]
        })
        
        summary = get_risk_summary(quantified, top_n=2)
        
        assert len(summary) == 2
        assert summary.iloc[0]["RiskID"] == "R2"  # Highest mean
        assert summary.iloc[1]["RiskID"] == "R3"  # Second highest
    
    def test_get_summary_excludes_portfolio(self):
        """Test that portfolio total is excluded."""
        quantified = pd.DataFrame({
            "RiskID": ["R1", "PORTFOLIO_TOTAL"],
            "Category": ["A", "Portfolio"],
            "mean": [100, 100],
            "var_95": [200, 200],
            "var_99": [250, 250],
            "tvar_95": [220, 220],
            "tvar_99": [270, 270]
        })
        
        summary = get_risk_summary(quantified, top_n=5)
        
        assert "PORTFOLIO_TOTAL" not in summary["RiskID"].values


@pytest.mark.skip(reason="compare_scenarios function not implemented in current version")
class TestCompareScenarios:
    """Tests for compare_scenarios function."""
    
    @pytest.fixture
    def base_register(self):
        """Create base register for scenarios."""
        return pd.DataFrame({
            "RiskID": ["R1", "R2"],
            "Category": ["Cyber", "Ops"],
            "Description": ["Risk 1", "Risk 2"],
            "FrequencyModel": ["Poisson", "Poisson"],
            "FreqParam1": [1.0, 2.0],
            "SeverityModel": ["Lognormal", "Normal"],
            "SevParam1": [10.0, 100000],
            "SevParam2": [0.5, 30000],
            "ControlEffectiveness": [0.0, 0.0],
            "ResidualFactor": [1.0, 1.0]
        })
    
    def test_compare_scenarios_basic(self, base_register):
        """Test basic scenario comparison."""
        scenarios = {
            "High_Freq": {"R1": {"FreqParam1": 3.0}}
        }
        
        comparison = compare_scenarios(base_register, scenarios, n_sims=1000, seed=42)
        
        assert len(comparison) == 2  # Base + 1 scenario
        assert "Base" in comparison["scenario"].values
        assert "High_Freq" in comparison["scenario"].values
        
        # High frequency should increase mean loss
        base_mean = comparison[comparison["scenario"] == "Base"]["mean"].iloc[0]
        high_freq_mean = comparison[comparison["scenario"] == "High_Freq"]["mean"].iloc[0]
        assert high_freq_mean > base_mean


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
