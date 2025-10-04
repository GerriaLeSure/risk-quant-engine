"""
Smoke tests for Streamlit dashboard

Tests basic functionality without running the full Streamlit server.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import dashboard functions
import importlib.util

spec = importlib.util.spec_from_file_location(
    "risk_mc_dashboard", Path(__file__).parent.parent / "src" / "risk_mc_dashboard.py"
)
dashboard = importlib.util.module_from_spec(spec)
sys.modules["risk_mc_dashboard"] = dashboard
spec.loader.exec_module(dashboard)


class TestDashboardFunctions:
    """Test dashboard helper functions"""

    def test_generate_executive_summary(self):
        """Test executive summary generation"""
        # Create sample data
        register_df = pd.DataFrame(
            {
                "RiskID": ["R1", "R2"],
                "Category": ["Cyber", "Ops"],
                "Description": ["Test 1", "Test 2"],
            }
        )

        quantified_df = pd.DataFrame(
            {
                "RiskID": ["R1", "R2", "PORTFOLIO_TOTAL"],
                "Category": ["Cyber", "Ops", "Portfolio"],
                "SimMean": [100000, 200000, 300000],
                "SimMedian": [90000, 180000, 270000],
                "SimStd": [50000, 100000, 150000],
                "SimVaR95": [200000, 400000, 600000],
                "SimVaR99": [250000, 500000, 750000],
                "SimTVaR95": [220000, 440000, 660000],
                "SimTVaR99": [270000, 540000, 810000],
            }
        )

        # Generate summary
        summary = dashboard.generate_executive_summary(quantified_df, register_df)

        # Check that summary contains key elements
        assert "EXECUTIVE SUMMARY" in summary.upper()
        assert "PORTFOLIO OVERVIEW" in summary
        assert "R1" in summary or "R2" in summary
        assert "$" in summary
        assert "VaR" in summary

    def test_load_sample_data(self):
        """Test loading sample data"""
        df = dashboard.load_sample_data()

        if df is not None:
            # Verify it's a valid DataFrame
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            assert "RiskID" in df.columns


class TestDashboardImport:
    """Test that dashboard can be imported"""

    def test_import_dashboard_module(self):
        """Test that dashboard module imports without errors"""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "risk_mc_dashboard", Path(__file__).parent.parent / "src" / "risk_mc_dashboard.py"
            )
            module = importlib.util.module_from_spec(spec)
            # Don't execute, just check it can be loaded
            assert spec is not None
            assert module is not None
        except Exception as e:
            pytest.fail(f"Failed to import dashboard: {e}")

    def test_required_functions_exist(self):
        """Test that required functions are defined"""
        functions = [
            "risk_register_tab",
            "monte_carlo_tab",
            "lec_tab",
            "kpi_dashboard_tab",
            "export_tab",
            "generate_executive_summary",
            "load_sample_data",
            "main",
        ]

        for func_name in functions:
            assert hasattr(dashboard, func_name), f"Missing function: {func_name}"


class TestDataProcessing:
    """Test data processing for dashboard"""

    def test_portfolio_summary_calculation(self):
        """Test portfolio summary calculations"""
        # Sample quantified data
        data = pd.DataFrame(
            {
                "RiskID": ["R1", "R2", "PORTFOLIO_TOTAL"],
                "SimMean": [100000, 200000, 300000],
                "SimVaR95": [200000, 400000, 600000],
            }
        )

        portfolio = data[data["RiskID"] == "PORTFOLIO_TOTAL"]
        assert len(portfolio) == 1
        assert portfolio.iloc[0]["SimMean"] == 300000

    def test_top_risks_sorting(self):
        """Test sorting risks by mean loss"""
        data = pd.DataFrame(
            {
                "RiskID": ["R1", "R2", "R3", "PORTFOLIO_TOTAL"],
                "SimMean": [500000, 100000, 300000, 900000],
                "Category": ["Cyber", "Ops", "Financial", "Portfolio"],
            }
        )

        # Get individual risks only
        individual = data[data["RiskID"] != "PORTFOLIO_TOTAL"].copy()
        top_risks = individual.nlargest(2, "SimMean")

        assert len(top_risks) == 2
        assert top_risks.iloc[0]["RiskID"] == "R1"
        assert top_risks.iloc[1]["RiskID"] == "R3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
