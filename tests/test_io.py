"""
Tests for I/O utilities.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc.io import load_register, save_quantified_register, validate_register_format


class TestLoadRegister:
    """Tests for load_register function."""
    
    def test_load_valid_csv(self, tmp_path):
        """Test loading valid CSV file."""
        # Create temporary CSV
        csv_content = """RiskID,FrequencyModel,FreqParam1,FreqParam2,SeverityModel,SevParam1,SevParam2
R1,Poisson,2.0,,Lognormal,12.0,0.8
R2,NegBin,3.0,0.6,Normal,100000,30000"""
        
        csv_path = tmp_path / "test_register.csv"
        csv_path.write_text(csv_content)
        
        df = load_register(str(csv_path))
        
        assert len(df) == 2
        assert "RiskID" in df.columns
        assert df["RiskID"].tolist() == ["R1", "R2"]
    
    def test_load_adds_defaults(self, tmp_path):
        """Test that load_register adds default columns."""
        csv_content = """RiskID,FrequencyModel,FreqParam1,SeverityModel,SevParam1,SevParam2
R1,Poisson,1.0,Lognormal,10.0,0.5"""
        
        csv_path = tmp_path / "test_register.csv"
        csv_path.write_text(csv_content)
        
        df = load_register(str(csv_path))
        
        assert "ControlEffectiveness" in df.columns
        assert "ResidualFactor" in df.columns
        assert df["ControlEffectiveness"].iloc[0] == 0.0
        assert df["ResidualFactor"].iloc[0] == 1.0
    
    def test_load_missing_required_column_raises(self, tmp_path):
        """Test that missing required column raises error."""
        csv_content = """RiskID,FrequencyModel,FreqParam1
R1,Poisson,1.0"""
        
        csv_path = tmp_path / "test_register.csv"
        csv_path.write_text(csv_content)
        
        with pytest.raises(ValueError, match="Missing required columns"):
            load_register(str(csv_path))
    
    def test_load_nonexistent_file_raises(self):
        """Test that nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_register("nonexistent_file.csv")
    
    def test_load_validates_frequency_model(self, tmp_path):
        """Test validation of frequency models."""
        csv_content = """RiskID,FrequencyModel,FreqParam1,SeverityModel,SevParam1,SevParam2
R1,InvalidModel,1.0,Lognormal,10.0,0.5"""
        
        csv_path = tmp_path / "test_register.csv"
        csv_path.write_text(csv_content)
        
        with pytest.raises(ValueError, match="Invalid frequency models"):
            load_register(str(csv_path))
    
    def test_load_validates_severity_model(self, tmp_path):
        """Test validation of severity models."""
        csv_content = """RiskID,FrequencyModel,FreqParam1,SeverityModel,SevParam1,SevParam2
R1,Poisson,1.0,InvalidModel,10.0,0.5"""
        
        csv_path = tmp_path / "test_register.csv"
        csv_path.write_text(csv_content)
        
        with pytest.raises(ValueError, match="Invalid severity models"):
            load_register(str(csv_path))
    
    def test_load_validates_control_effectiveness_range(self, tmp_path):
        """Test validation of ControlEffectiveness range."""
        csv_content = """RiskID,FrequencyModel,FreqParam1,SeverityModel,SevParam1,SevParam2,ControlEffectiveness
R1,Poisson,1.0,Lognormal,10.0,0.5,1.5"""
        
        csv_path = tmp_path / "test_register.csv"
        csv_path.write_text(csv_content)
        
        with pytest.raises(ValueError, match="ControlEffectiveness out of range"):
            load_register(str(csv_path))


class TestSaveQuantifiedRegister:
    """Tests for save_quantified_register function."""
    
    def test_save_creates_file(self, tmp_path):
        """Test that save creates output file."""
        register_df = pd.DataFrame({
            "RiskID": ["R1", "R2"],
            "Category": ["Cyber", "Ops"],
            "FrequencyModel": ["Poisson", "Poisson"],
            "FreqParam1": [1.0, 2.0],
            "SeverityModel": ["Lognormal", "Normal"],
            "SevParam1": [10.0, 100000],
            "SevParam2": [0.5, 30000]
        })
        
        portfolio_df = pd.DataFrame({
            "portfolio_loss": np.random.lognormal(12, 1, 1000),
            "by_risk:R1": np.random.lognormal(11, 0.8, 1000),
            "by_risk:R2": np.random.lognormal(11.5, 0.9, 1000)
        })
        
        out_path = tmp_path / "quantified.csv"
        
        save_quantified_register(register_df, portfolio_df, str(out_path))
        
        assert out_path.exists()
        
        # Load and verify
        result_df = pd.read_csv(out_path)
        assert "SimMean" in result_df.columns
        assert "SimVaR95" in result_df.columns
        assert len(result_df) == 3  # 2 risks + portfolio total
    
    def test_save_includes_portfolio_total(self, tmp_path):
        """Test that saved file includes portfolio total row."""
        register_df = pd.DataFrame({
            "RiskID": ["R1"],
            "Category": ["Test"],
            "FrequencyModel": ["Poisson"],
            "FreqParam1": [1.0],
            "SeverityModel": ["Lognormal"],
            "SevParam1": [10.0],
            "SevParam2": [0.5]
        })
        
        portfolio_df = pd.DataFrame({
            "portfolio_loss": np.ones(1000) * 100000,
            "by_risk:R1": np.ones(1000) * 100000
        })
        
        out_path = tmp_path / "quantified.csv"
        save_quantified_register(register_df, portfolio_df, str(out_path))
        
        result_df = pd.read_csv(out_path)
        
        # Last row should be portfolio total
        assert result_df.iloc[-1]["RiskID"] == "PORTFOLIO_TOTAL"
        assert result_df.iloc[-1]["Category"] == "Portfolio"


class TestValidateRegisterFormat:
    """Tests for validate_register_format function."""
    
    def test_valid_register_passes(self):
        """Test that valid register passes validation."""
        df = pd.DataFrame({
            "RiskID": ["R1"],
            "FrequencyModel": ["Poisson"],
            "FreqParam1": [1.0],
            "SeverityModel": ["Lognormal"],
            "SevParam1": [10.0],
            "SevParam2": [0.5]
        })
        
        is_valid, errors = validate_register_format(df)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_column_fails(self):
        """Test that missing column fails validation."""
        df = pd.DataFrame({
            "RiskID": ["R1"],
            "FrequencyModel": ["Poisson"]
        })
        
        is_valid, errors = validate_register_format(df)
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_empty_register_fails(self):
        """Test that empty register fails validation."""
        df = pd.DataFrame({
            "RiskID": [],
            "FrequencyModel": [],
            "FreqParam1": [],
            "SeverityModel": [],
            "SevParam1": [],
            "SevParam2": []
        })
        
        is_valid, errors = validate_register_format(df)
        
        assert not is_valid
        assert any("empty" in e.lower() for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
