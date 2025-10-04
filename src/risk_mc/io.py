"""
Input/output utilities for risk register and results.

Supports CSV and Excel formats with validation.
"""

import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


def load_register(path: str, required_columns: Optional[list[str]] = None) -> pd.DataFrame:
    """
    Load risk register from CSV or Excel file.

    Performs type coercion and validation.

    Args:
        path: Path to CSV or Excel file
        required_columns: Optional list of required column names

    Returns:
        DataFrame with validated risk register

    Raises:
        ValueError: If file format unsupported or validation fails
    """
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Risk register file not found: {path}")

    # Load based on extension
    suffix = path_obj.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv, .xlsx, or .xls")

    # Validate required columns
    if required_columns is None:
        required_columns = [
            "RiskID",
            "FrequencyModel",
            "FreqParam1",
            "SeverityModel",
            "SevParam1",
            "SevParam2",
        ]

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Type coercion
    df = _coerce_types(df)

    # Validation
    df = _validate_register(df)

    return df


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce columns to appropriate types."""
    df = df.copy()

    # Numeric columns
    numeric_cols = [
        "FreqParam1",
        "FreqParam2",
        "SevParam1",
        "SevParam2",
        "SevParam3",
        "ControlEffectiveness",
        "ResidualFactor",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # String columns
    string_cols = ["RiskID", "Category", "Description", "FrequencyModel", "SeverityModel"]

    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Set defaults for optional columns
    if "ControlEffectiveness" not in df.columns:
        df["ControlEffectiveness"] = 0.0
    else:
        df["ControlEffectiveness"] = df["ControlEffectiveness"].fillna(0.0)

    if "ResidualFactor" not in df.columns:
        df["ResidualFactor"] = 1.0
    else:
        df["ResidualFactor"] = df["ResidualFactor"].fillna(1.0)

    if "SevParam3" not in df.columns:
        df["SevParam3"] = None

    return df


def _validate_register(df: pd.DataFrame) -> pd.DataFrame:
    """Validate risk register data."""
    errors = []

    # Check for missing values in required numeric columns
    required_numeric = ["FreqParam1", "SevParam1", "SevParam2"]

    for col in required_numeric:
        if col in df.columns:
            n_missing = df[col].isna().sum()
            if n_missing > 0:
                errors.append(f"Column {col} has {n_missing} missing values")

    # Validate frequency models
    valid_freq_models = ["poisson", "negbin"]
    if "FrequencyModel" in df.columns:
        invalid = df[~df["FrequencyModel"].str.lower().isin(valid_freq_models)]
        if len(invalid) > 0:
            errors.append(f"Invalid frequency models in rows: {invalid.index.tolist()}")

    # Validate severity models
    valid_sev_models = ["lognormal", "normal", "pert"]
    if "SeverityModel" in df.columns:
        invalid = df[~df["SeverityModel"].str.lower().isin(valid_sev_models)]
        if len(invalid) > 0:
            errors.append(f"Invalid severity models in rows: {invalid.index.tolist()}")

    # Validate parameter ranges
    if "ControlEffectiveness" in df.columns:
        invalid = df[(df["ControlEffectiveness"] < 0) | (df["ControlEffectiveness"] > 1)]
        if len(invalid) > 0:
            errors.append(
                f"ControlEffectiveness out of range [0,1] in rows: {invalid.index.tolist()}"
            )

    if "ResidualFactor" in df.columns:
        invalid = df[(df["ResidualFactor"] < 0) | (df["ResidualFactor"] > 1)]
        if len(invalid) > 0:
            errors.append(f"ResidualFactor out of range [0,1] in rows: {invalid.index.tolist()}")

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(errors))

    return df


def quantify_register(
    register_df: pd.DataFrame, n_sims: int = 50_000, seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Quantify risk register by running Monte Carlo simulation.

    For each risk, computes key metrics: mean, median, std, percentiles, VaR, TVaR.

    Args:
        register_df: Risk register DataFrame with required columns
        n_sims: Number of Monte Carlo simulations (default: 50,000)
        seed: Random seed for reproducibility (default: None)

    Returns:
        DataFrame with original risk data plus quantified metrics:
            - SimMean: Mean annual loss
            - SimMedian: Median annual loss
            - SimStd: Standard deviation of annual loss
            - SimP90, SimP95, SimP99: Percentiles
            - SimVaR95, SimVaR99: Value at Risk
            - SimTVaR95, SimTVaR99: Tail Value at Risk (Expected Shortfall)
    """
    from .simulate import simulate_portfolio

    # Run simulation
    portfolio_df = simulate_portfolio(register_df, n_sims=n_sims, seed=seed)

    # Start with original register
    quantified_df = register_df.copy()

    # Extract risk columns from portfolio simulation
    risk_columns = [col for col in portfolio_df.columns if col.startswith("by_risk:")]

    # Calculate metrics for each risk
    for col in risk_columns:
        risk_id = col.replace("by_risk:", "")
        losses = portfolio_df[col].values

        # Find matching row in register
        mask = quantified_df["RiskID"] == risk_id

        if not mask.any():
            warnings.warn(f"Risk {risk_id} in simulation but not in register", stacklevel=2)
            continue

        # Calculate all metrics
        quantified_df.loc[mask, "SimMean"] = np.mean(losses)
        quantified_df.loc[mask, "SimMedian"] = np.median(losses)
        quantified_df.loc[mask, "SimStd"] = np.std(losses)
        quantified_df.loc[mask, "SimP90"] = np.percentile(losses, 90)
        quantified_df.loc[mask, "SimP95"] = np.percentile(losses, 95)
        quantified_df.loc[mask, "SimP99"] = np.percentile(losses, 99)
        quantified_df.loc[mask, "SimVaR95"] = np.percentile(losses, 95)
        quantified_df.loc[mask, "SimVaR99"] = np.percentile(losses, 99)

        # TVaR (Expected Shortfall)
        var95 = np.percentile(losses, 95)
        tail95 = losses[losses >= var95]
        quantified_df.loc[mask, "SimTVaR95"] = np.mean(tail95) if len(tail95) > 0 else var95

        var99 = np.percentile(losses, 99)
        tail99 = losses[losses >= var99]
        quantified_df.loc[mask, "SimTVaR99"] = np.mean(tail99) if len(tail99) > 0 else var99

    # Add portfolio total row
    portfolio_losses = portfolio_df["portfolio_loss"].values
    portfolio_row = {
        "RiskID": "PORTFOLIO_TOTAL",
        "Category": "Portfolio",
        "Description": "Total portfolio loss",
        "SimMean": np.mean(portfolio_losses),
        "SimMedian": np.median(portfolio_losses),
        "SimStd": np.std(portfolio_losses),
        "SimP90": np.percentile(portfolio_losses, 90),
        "SimP95": np.percentile(portfolio_losses, 95),
        "SimP99": np.percentile(portfolio_losses, 99),
        "SimVaR95": np.percentile(portfolio_losses, 95),
        "SimVaR99": np.percentile(portfolio_losses, 99),
    }

    var95 = np.percentile(portfolio_losses, 95)
    tail95 = portfolio_losses[portfolio_losses >= var95]
    portfolio_row["SimTVaR95"] = np.mean(tail95) if len(tail95) > 0 else var95

    var99 = np.percentile(portfolio_losses, 99)
    tail99 = portfolio_losses[portfolio_losses >= var99]
    portfolio_row["SimTVaR99"] = np.mean(tail99) if len(tail99) > 0 else var99

    quantified_df = pd.concat([quantified_df, pd.DataFrame([portfolio_row])], ignore_index=True)

    return quantified_df


def save_quantified_register(
    register_df: pd.DataFrame,
    portfolio_df: pd.DataFrame,
    out_path: str,
    metrics_to_include: Optional[list[str]] = None,
) -> None:
    """
    Save quantified risk register with simulation metrics.

    Args:
        register_df: Original risk register
        portfolio_df: Simulation results from simulate_portfolio
        out_path: Output path for CSV file
        metrics_to_include: List of metrics to calculate (default: standard set)
    """
    if metrics_to_include is None:
        metrics_to_include = ["mean", "var_95", "var_99", "tvar_95", "tvar_99"]

    # Start with original register
    output_df = register_df.copy()

    # Calculate metrics for each risk
    risk_columns = [col for col in portfolio_df.columns if col.startswith("by_risk:")]

    for col in risk_columns:
        risk_id = col.replace("by_risk:", "")
        losses = portfolio_df[col].values

        # Find matching row in register
        mask = output_df["RiskID"] == risk_id

        if not mask.any():
            warnings.warn(f"Risk {risk_id} in simulation but not in register", stacklevel=2)
            continue

        # Calculate and store metrics
        if "mean" in metrics_to_include:
            output_df.loc[mask, "SimMean"] = np.mean(losses)

        if "median" in metrics_to_include:
            output_df.loc[mask, "SimMedian"] = np.median(losses)

        if "std" in metrics_to_include:
            output_df.loc[mask, "SimStd"] = np.std(losses)

        if "var_95" in metrics_to_include:
            output_df.loc[mask, "SimVaR95"] = np.percentile(losses, 95)

        if "var_99" in metrics_to_include:
            output_df.loc[mask, "SimVaR99"] = np.percentile(losses, 99)

        if "tvar_95" in metrics_to_include:
            var95 = np.percentile(losses, 95)
            tail = losses[losses >= var95]
            output_df.loc[mask, "SimTVaR95"] = np.mean(tail) if len(tail) > 0 else var95

        if "tvar_99" in metrics_to_include:
            var99 = np.percentile(losses, 99)
            tail = losses[losses >= var99]
            output_df.loc[mask, "SimTVaR99"] = np.mean(tail) if len(tail) > 0 else var99

    # Add portfolio total row
    portfolio_losses = portfolio_df["portfolio_loss"].values
    portfolio_row = {
        "RiskID": "PORTFOLIO_TOTAL",
        "Category": "Portfolio",
        "Description": "Total portfolio loss",
        "SimMean": np.mean(portfolio_losses),
        "SimVaR95": np.percentile(portfolio_losses, 95),
        "SimVaR99": np.percentile(portfolio_losses, 99),
    }

    var95 = np.percentile(portfolio_losses, 95)
    tail95 = portfolio_losses[portfolio_losses >= var95]
    portfolio_row["SimTVaR95"] = np.mean(tail95) if len(tail95) > 0 else var95

    var99 = np.percentile(portfolio_losses, 99)
    tail99 = portfolio_losses[portfolio_losses >= var99]
    portfolio_row["SimTVaR99"] = np.mean(tail99) if len(tail99) > 0 else var99

    output_df = pd.concat([output_df, pd.DataFrame([portfolio_row])], ignore_index=True)

    # Save to CSV
    output_df.to_csv(out_path, index=False)
    print(f"Quantified register saved to: {out_path}")


def validate_register_format(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Check if DataFrame has valid risk register format.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    required_cols = [
        "RiskID",
        "FrequencyModel",
        "FreqParam1",
        "SeverityModel",
        "SevParam1",
        "SevParam2",
    ]

    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if len(df) == 0:
        errors.append("Register is empty")

    return (len(errors) == 0, errors)
