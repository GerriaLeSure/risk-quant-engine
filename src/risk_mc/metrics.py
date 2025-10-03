"""
Risk metrics and summary statistics.

Includes VaR, TVaR (Expected Shortfall), percentiles, and summary stats.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional


def var(losses: np.ndarray, confidence: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) at given confidence level.
    
    VaR is the loss threshold at the specified percentile.
    
    Args:
        losses: Array of loss values
        confidence: Confidence level (e.g., 0.95 for 95% VaR)
        
    Returns:
        VaR value
    """
    if not 0 < confidence < 1:
        raise ValueError(f"Confidence must be in (0, 1), got {confidence}")
    
    return np.percentile(losses, confidence * 100)


def tvar(losses: np.ndarray, confidence: float = 0.95) -> float:
    """
    Calculate Tail Value at Risk (TVaR) / Expected Shortfall at given confidence level.
    
    TVaR is the average loss beyond the VaR threshold.
    Also known as Conditional VaR (CVaR) or Expected Shortfall (ES).
    
    Args:
        losses: Array of loss values
        confidence: Confidence level (e.g., 0.95 for 95% TVaR)
        
    Returns:
        TVaR value
    """
    if not 0 < confidence < 1:
        raise ValueError(f"Confidence must be in (0, 1), got {confidence}")
    
    var_threshold = var(losses, confidence)
    tail_losses = losses[losses >= var_threshold]
    
    if len(tail_losses) == 0:
        return var_threshold
    
    return np.mean(tail_losses)


def summary(losses: np.ndarray, label: str = "Loss") -> pd.Series:
    """
    Generate comprehensive summary statistics for loss distribution.
    
    Args:
        losses: Array of loss values
        label: Label for the series name
        
    Returns:
        pandas Series with summary statistics
    """
    stats = {
        "mean": np.mean(losses),
        "median": np.median(losses),
        "std": np.std(losses),
        "min": np.min(losses),
        "max": np.max(losses),
        "p50": np.percentile(losses, 50),
        "p90": np.percentile(losses, 90),
        "p95": np.percentile(losses, 95),
        "p99": np.percentile(losses, 99),
        "var_95": var(losses, 0.95),
        "var_99": var(losses, 0.99),
        "tvar_95": tvar(losses, 0.95),
        "tvar_99": tvar(losses, 0.99),
    }
    
    return pd.Series(stats, name=label)


def percentiles(losses: np.ndarray, probs: List[float]) -> Dict[float, float]:
    """
    Calculate specific percentiles.
    
    Args:
        losses: Array of loss values
        probs: List of probabilities (0-1)
        
    Returns:
        Dictionary mapping probability to loss value
    """
    result = {}
    for p in probs:
        if not 0 <= p <= 1:
            raise ValueError(f"Probability must be in [0, 1], got {p}")
        result[p] = np.percentile(losses, p * 100)
    
    return result


def expected_loss(losses: np.ndarray) -> float:
    """
    Calculate expected loss (mean).
    
    Args:
        losses: Array of loss values
        
    Returns:
        Expected loss value
    """
    return float(np.mean(losses))


def portfolio_summary(
    portfolio_df: pd.DataFrame,
    risk_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Generate summary statistics for portfolio and individual risks.
    
    Args:
        portfolio_df: Output from simulate_portfolio
        risk_columns: List of risk column names (if None, auto-detect)
        
    Returns:
        DataFrame with summary stats for each risk and portfolio
    """
    if risk_columns is None:
        risk_columns = [col for col in portfolio_df.columns if col.startswith("by_risk:")]
    
    summaries = []
    
    # Portfolio total
    portfolio_summary_stats = summary(portfolio_df["portfolio_loss"].values, "Portfolio")
    summaries.append(portfolio_summary_stats)
    
    # Individual risks
    for col in risk_columns:
        risk_id = col.replace("by_risk:", "")
        risk_summary = summary(portfolio_df[col].values, risk_id)
        summaries.append(risk_summary)
    
    return pd.DataFrame(summaries)


def contribution_analysis(portfolio_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Analyze contribution of each risk to portfolio loss.
    
    Args:
        portfolio_df: Output from simulate_portfolio
        top_n: Number of top contributors to return
        
    Returns:
        DataFrame with risk contributions sorted by mean loss
    """
    contributions = []
    
    risk_columns = [col for col in portfolio_df.columns if col.startswith("by_risk:")]
    
    for col in risk_columns:
        risk_id = col.replace("by_risk:", "")
        losses = portfolio_df[col].values
        
        contributions.append({
            "risk_id": risk_id,
            "mean_loss": np.mean(losses),
            "std_loss": np.std(losses),
            "var_95": var(losses, 0.95),
            "contribution_pct": np.mean(losses) / np.mean(portfolio_df["portfolio_loss"]) * 100
        })
    
    df = pd.DataFrame(contributions)
    df = df.sort_values("mean_loss", ascending=False)
    
    return df.head(top_n)


def correlation_matrix(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix between risks.
    
    Note: In frequency/severity models with independent sampling,
    correlations will be near zero. This is useful for validation.
    
    Args:
        portfolio_df: Output from simulate_portfolio
        
    Returns:
        Correlation matrix DataFrame
    """
    risk_columns = [col for col in portfolio_df.columns if col.startswith("by_risk:")]
    risk_data = portfolio_df[risk_columns]
    
    # Rename columns to remove prefix
    risk_data = risk_data.rename(columns=lambda x: x.replace("by_risk:", ""))
    
    return risk_data.corr()


def marginal_contribution_to_var(
    by_risk_losses: Dict[str, np.ndarray],
    portfolio_losses: np.ndarray,
    q: float = 0.95
) -> Dict[str, float]:
    """
    Calculate each risk's marginal contribution to portfolio VaR.
    
    Uses Shapley-style approximation: correlate tail indicator with risk loss.
    This measures how much each risk contributes to tail events.
    
    Args:
        by_risk_losses: Dictionary mapping risk ID to loss array
        portfolio_losses: Array of portfolio total losses
        q: VaR confidence level (default: 0.95)
        
    Returns:
        Dictionary mapping risk ID to dVaR contribution
    """
    # Calculate portfolio VaR
    portfolio_var = var(portfolio_losses, q)
    
    # Create tail indicator (1 if in tail, 0 otherwise)
    tail_indicator = (portfolio_losses >= portfolio_var).astype(float)
    
    contributions = {}
    
    for risk_id, risk_losses in by_risk_losses.items():
        # Skip 'portfolio' key if present
        if risk_id == "portfolio":
            continue
        
        # Calculate correlation between tail indicator and risk loss
        # This measures how much this risk drives tail events
        if np.std(tail_indicator) > 0 and np.std(risk_losses) > 0:
            correlation = np.corrcoef(tail_indicator, risk_losses)[0, 1]
            
            # Scale by risk's contribution to portfolio
            # dVaR ≈ correlation * std(risk) * tail_indicator_mean
            mean_tail_contribution = np.mean(risk_losses[tail_indicator == 1])
            
            contributions[risk_id] = mean_tail_contribution if not np.isnan(mean_tail_contribution) else 0.0
        else:
            contributions[risk_id] = 0.0
    
    return contributions


def tornado_data(
    register_df: pd.DataFrame,
    portfolio_losses: np.ndarray,
    by_risk_losses: Dict[str, np.ndarray],
    q: float = 0.95,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Generate tornado chart data showing top risk contributors.
    
    Returns top risks by mean loss and by dVaR contribution.
    
    Args:
        register_df: Risk register DataFrame
        portfolio_losses: Array of portfolio total losses
        by_risk_losses: Dictionary mapping risk ID to loss array
        q: VaR confidence level for dVaR calculation
        top_n: Number of top risks to include
        
    Returns:
        DataFrame with columns: risk_id, category, mean_loss, dvar, rank_by_mean, rank_by_dvar
    """
    # Calculate marginal VaR contributions
    dvar_contrib = marginal_contribution_to_var(by_risk_losses, portfolio_losses, q)
    
    # Build results
    results = []
    
    for risk_id, risk_losses in by_risk_losses.items():
        if risk_id == "portfolio":
            continue
        
        # Get category from register
        risk_row = register_df[register_df["RiskID"] == risk_id]
        category = risk_row["Category"].iloc[0] if len(risk_row) > 0 else "Unknown"
        
        results.append({
            "risk_id": risk_id,
            "category": category,
            "mean_loss": np.mean(risk_losses),
            "dvar": dvar_contrib.get(risk_id, 0.0)
        })
    
    df = pd.DataFrame(results)
    
    # Add rankings
    df["rank_by_mean"] = df["mean_loss"].rank(ascending=False)
    df["rank_by_dvar"] = df["dvar"].rank(ascending=False)
    
    # Get top N by either metric
    top_by_mean = set(df.nlargest(top_n, "mean_loss")["risk_id"])
    top_by_dvar = set(df.nlargest(top_n, "dvar")["risk_id"])
    top_risks = top_by_mean | top_by_dvar
    
    # Filter and sort
    df_top = df[df["risk_id"].isin(top_risks)].copy()
    df_top = df_top.sort_values("mean_loss", ascending=False)
    
    return df_top
