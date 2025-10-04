"""
Risk Register Integration Module

Provides high-level functions for loading, quantifying, and saving risk registers
with Monte Carlo simulation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List
from .io import load_register as _load_register_base, validate_register_format
from .simulate import simulate_portfolio
from .metrics import summary, var, tvar


def load_register(path: str) -> pd.DataFrame:
    """
    Load risk register from CSV or Excel file with validation.
    
    Enforces schema and validates:
    - Required columns: RiskID, Category, Description, FrequencyModel, 
      FreqParam1, SeverityModel, SevParam1, SevParam2
    - Valid models: Poisson/NegBin for frequency, Lognormal/Normal/PERT for severity
    - Numeric parameter coercion
    - Default values for optional fields
    
    Args:
        path: Path to CSV or Excel file
        
    Returns:
        DataFrame with validated risk register
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If validation fails
        
    Example:
        >>> df = load_register("data/risk_register.csv")
        >>> print(df.columns)
        Index(['RiskID', 'Category', 'Description', 'FrequencyModel', 
               'FreqParam1', 'FreqParam2', 'SeverityModel', 'SevParam1', 
               'SevParam2', 'SevParam3', 'ControlEffectiveness', 'ResidualFactor'])
    """
    # Use base loader from io.py which already handles all validation
    return _load_register_base(path)


def quantify_register(
    register_df: pd.DataFrame,
    n_sims: int = 50_000,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Run Monte Carlo simulation on risk register and compute metrics for each risk.
    
    For each risk, runs n_sims simulations and calculates:
    - Central tendency: mean, median
    - Dispersion: std (standard deviation)
    - Percentiles: p90, p95, p99
    - Risk measures: VaR95, VaR99, TVaR95, TVaR99
    
    Args:
        register_df: Risk register DataFrame (from load_register)
        n_sims: Number of Monte Carlo simulations (default: 50,000)
        seed: Random seed for reproducibility (default: None)
        
    Returns:
        DataFrame with original risk data plus quantification columns:
        - mean: Expected annual loss
        - median: 50th percentile loss
        - std: Standard deviation of loss distribution
        - p90: 90th percentile loss
        - p95: 95th percentile loss
        - p99: 99th percentile loss
        - var_95: Value at Risk at 95% confidence
        - var_99: Value at Risk at 99% confidence
        - tvar_95: Tail Value at Risk at 95% confidence
        - tvar_99: Tail Value at Risk at 99% confidence
        
    Example:
        >>> register = load_register("data/risks.csv")
        >>> quantified = quantify_register(register, n_sims=50_000, seed=42)
        >>> print(quantified[['RiskID', 'mean', 'var_95', 'tvar_95']])
        RiskID       mean     var_95    tvar_95
        R1      150000.0   450000.0   600000.0
        R2      200000.0   550000.0   750000.0
    """
    # Validate input
    is_valid, errors = validate_register_format(register_df)
    if not is_valid:
        raise ValueError(f"Invalid risk register: {errors}")
    
    # Run portfolio simulation
    portfolio_df = simulate_portfolio(register_df, n_sims=n_sims, seed=seed)
    
    # Extract risk columns
    risk_columns = [col for col in portfolio_df.columns if col.startswith("by_risk:")]
    
    # Build quantification results
    quantified_rows = []
    
    for col in risk_columns:
        risk_id = col.replace("by_risk:", "")
        losses = portfolio_df[col].values
        
        # Find original risk data
        risk_row = register_df[register_df["RiskID"] == risk_id]
        if len(risk_row) == 0:
            continue
        
        # Calculate metrics
        metrics = {
            "RiskID": risk_id,
            "Category": risk_row["Category"].iloc[0],
            "Description": risk_row["Description"].iloc[0] if "Description" in risk_row.columns else "",
            "FrequencyModel": risk_row["FrequencyModel"].iloc[0],
            "FreqParam1": risk_row["FreqParam1"].iloc[0],
            "FreqParam2": risk_row["FreqParam2"].iloc[0] if "FreqParam2" in risk_row.columns else None,
            "SeverityModel": risk_row["SeverityModel"].iloc[0],
            "SevParam1": risk_row["SevParam1"].iloc[0],
            "SevParam2": risk_row["SevParam2"].iloc[0],
            "SevParam3": risk_row["SevParam3"].iloc[0] if "SevParam3" in risk_row.columns else None,
            "ControlEffectiveness": risk_row["ControlEffectiveness"].iloc[0] if "ControlEffectiveness" in risk_row.columns else 0.0,
            "ResidualFactor": risk_row["ResidualFactor"].iloc[0] if "ResidualFactor" in risk_row.columns else 1.0,
            "mean": float(np.mean(losses)),
            "median": float(np.median(losses)),
            "std": float(np.std(losses)),
            "p90": float(np.percentile(losses, 90)),
            "p95": float(np.percentile(losses, 95)),
            "p99": float(np.percentile(losses, 99)),
            "var_95": float(var(losses, 0.95)),
            "var_99": float(var(losses, 0.99)),
            "tvar_95": float(tvar(losses, 0.95)),
            "tvar_99": float(tvar(losses, 0.99))
        }
        
        quantified_rows.append(metrics)
    
    # Add portfolio total
    portfolio_losses = portfolio_df["portfolio_loss"].values
    portfolio_row = {
        "RiskID": "PORTFOLIO_TOTAL",
        "Category": "Portfolio",
        "Description": "Total portfolio loss",
        "FrequencyModel": "",
        "FreqParam1": None,
        "FreqParam2": None,
        "SeverityModel": "",
        "SevParam1": None,
        "SevParam2": None,
        "SevParam3": None,
        "ControlEffectiveness": None,
        "ResidualFactor": None,
        "mean": float(np.mean(portfolio_losses)),
        "median": float(np.median(portfolio_losses)),
        "std": float(np.std(portfolio_losses)),
        "p90": float(np.percentile(portfolio_losses, 90)),
        "p95": float(np.percentile(portfolio_losses, 95)),
        "p99": float(np.percentile(portfolio_losses, 99)),
        "var_95": float(var(portfolio_losses, 0.95)),
        "var_99": float(var(portfolio_losses, 0.99)),
        "tvar_95": float(tvar(portfolio_losses, 0.95)),
        "tvar_99": float(tvar(portfolio_losses, 0.99))
    }
    
    quantified_rows.append(portfolio_row)
    
    return pd.DataFrame(quantified_rows)


def save_quantified_register(df: pd.DataFrame, out_path: str) -> None:
    """
    Save quantified risk register to CSV or Excel.
    
    Args:
        df: Quantified risk register DataFrame (from quantify_register)
        out_path: Output file path (.csv or .xlsx)
        
    Example:
        >>> quantified = quantify_register(register, n_sims=50_000)
        >>> save_quantified_register(quantified, "output/quantified_risks.csv")
    """
    path_obj = Path(out_path)
    suffix = path_obj.suffix.lower()
    
    if suffix == ".csv":
        df.to_csv(out_path, index=False)
    elif suffix in [".xlsx", ".xls"]:
        df.to_excel(out_path, index=False)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .xlsx")
    
    print(f"Quantified register saved to: {out_path}")


def get_risk_summary(quantified_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get summary of top risks by expected loss.
    
    Args:
        quantified_df: Quantified risk register
        top_n: Number of top risks to return
        
    Returns:
        DataFrame with top N risks sorted by mean loss
    """
    # Exclude portfolio total
    risks_only = quantified_df[quantified_df["RiskID"] != "PORTFOLIO_TOTAL"].copy()
    
    # Sort by mean loss
    risks_only = risks_only.sort_values("mean", ascending=False)
    
    # Return top N with selected columns
    columns = ["RiskID", "Category", "mean", "var_95", "var_99", "tvar_95", "tvar_99"]
    return risks_only[columns].head(top_n)


def compare_scenarios(
    register_df: pd.DataFrame,
    scenarios: dict,
    n_sims: int = 50_000,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Compare multiple scenarios by modifying risk parameters.
    
    Args:
        register_df: Base risk register
        scenarios: Dict mapping scenario name to parameter modifications
                  Example: {"High_Freq": {"R1": {"FreqParam1": 3.0}}}
        n_sims: Number of simulations per scenario
        seed: Random seed
        
    Returns:
        DataFrame comparing portfolio metrics across scenarios
    """
    results = []
    
    # Base scenario
    base_quantified = quantify_register(register_df, n_sims=n_sims, seed=seed)
    base_portfolio = base_quantified[base_quantified["RiskID"] == "PORTFOLIO_TOTAL"].iloc[0]
    
    results.append({
        "scenario": "Base",
        "mean": base_portfolio["mean"],
        "var_95": base_portfolio["var_95"],
        "var_99": base_portfolio["var_99"],
        "tvar_95": base_portfolio["tvar_95"],
        "tvar_99": base_portfolio["tvar_99"]
    })
    
    # Modified scenarios
    for scenario_name, modifications in scenarios.items():
        modified_df = register_df.copy()
        
        for risk_id, changes in modifications.items():
            mask = modified_df["RiskID"] == risk_id
            for param, value in changes.items():
                if param in modified_df.columns:
                    modified_df.loc[mask, param] = value
        
        scenario_quantified = quantify_register(modified_df, n_sims=n_sims, seed=seed)
        scenario_portfolio = scenario_quantified[scenario_quantified["RiskID"] == "PORTFOLIO_TOTAL"].iloc[0]
        
        results.append({
            "scenario": scenario_name,
            "mean": scenario_portfolio["mean"],
            "var_95": scenario_portfolio["var_95"],
            "var_99": scenario_portfolio["var_99"],
            "tvar_95": scenario_portfolio["tvar_95"],
            "tvar_99": scenario_portfolio["tvar_99"]
        })
    
    return pd.DataFrame(results)
