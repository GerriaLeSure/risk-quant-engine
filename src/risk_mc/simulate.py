"""
Core Monte Carlo simulation functions for risk quantification.

Implements frequency/severity modeling with control effectiveness.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict
from .distributions import sample_frequency, sample_severity


def simulate_annual_loss(
    risk_row: pd.Series,
    n_sims: int = 50_000,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Simulate annual losses for a single risk using frequency/severity approach.
    
    Process:
    1. Sample annual event count from frequency distribution
    2. For each event, sample severity from severity distribution
    3. Apply control effectiveness and residual factor
    4. Sum to get total annual loss
    
    Args:
        risk_row: pandas Series with columns:
            - FrequencyModel: 'Poisson' or 'NegBin'
            - FreqParam1: lambda (Poisson) or r (NegBin)
            - FreqParam2: None (Poisson) or p (NegBin)
            - SeverityModel: 'Lognormal', 'Normal', or 'PERT'
            - SevParam1: distribution parameter 1
            - SevParam2: distribution parameter 2
            - SevParam3: distribution parameter 3 (PERT only)
            - ControlEffectiveness: optional, fraction reduced (0-1)
            - ResidualFactor: multiplier for severity after controls
        n_sims: Number of Monte Carlo simulations
        seed: Random seed for reproducibility
        
    Returns:
        Array of shape (n_sims,) with annual loss values
    """
    rng = np.random.default_rng(seed)
    
    # Extract parameters with defaults
    freq_model = risk_row.get("FrequencyModel", "Poisson")
    freq_param1 = risk_row.get("FreqParam1", 1.0)
    freq_param2 = risk_row.get("FreqParam2", None)
    
    sev_model = risk_row.get("SeverityModel", "Lognormal")
    sev_param1 = risk_row.get("SevParam1", 10.0)
    sev_param2 = risk_row.get("SevParam2", 1.0)
    sev_param3 = risk_row.get("SevParam3", None)
    
    residual_factor = risk_row.get("ResidualFactor", 1.0)
    control_eff = risk_row.get("ControlEffectiveness", 0.0)
    
    # Validate parameters
    if not 0 <= residual_factor <= 1:
        raise ValueError(f"ResidualFactor must be in [0, 1], got {residual_factor}")
    if not 0 <= control_eff <= 1:
        raise ValueError(f"ControlEffectiveness must be in [0, 1], got {control_eff}")
    
    # Sample frequency (event counts per simulation)
    event_counts = sample_frequency(
        freq_model, freq_param1, freq_param2, n_sims, rng
    )
    
    # Initialize annual losses
    annual_losses = np.zeros(n_sims)
    
    # For each simulation, sample severities and sum
    for i in range(n_sims):
        n_events = int(event_counts[i])
        
        if n_events > 0:
            # Sample severities for all events in this simulation
            severities = sample_severity(
                sev_model, sev_param1, sev_param2, sev_param3, n_events, rng
            )
            
            # Apply controls: residual factor directly multiplies severity
            # ControlEffectiveness can be used for additional reduction if needed
            # Formula: effective_loss = severity * residual_factor * (1 - control_eff)
            effective_severities = severities * residual_factor * (1 - control_eff)
            
            # Sum to get annual loss
            annual_losses[i] = np.sum(effective_severities)
    
    return annual_losses


def simulate_portfolio(
    register_df: pd.DataFrame,
    n_sims: int = 50_000,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Simulate annual losses for entire risk portfolio.
    
    Args:
        register_df: DataFrame with risk register (one row per risk)
            Must contain columns for simulate_annual_loss
        n_sims: Number of Monte Carlo simulations
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with columns:
            - portfolio_loss: total portfolio loss per simulation
            - by_risk:<RiskID>: individual risk loss per simulation
    """
    if len(register_df) == 0:
        raise ValueError("Risk register is empty")
    
    # Initialize RNG for reproducible splits
    if seed is not None:
        base_rng = np.random.default_rng(seed)
        # Generate unique seeds for each risk
        risk_seeds = base_rng.integers(0, 2**31, size=len(register_df))
    else:
        risk_seeds = [None] * len(register_df)
    
    # Simulate each risk
    results = {}
    portfolio_total = np.zeros(n_sims)
    
    for idx, (_, risk_row) in enumerate(register_df.iterrows()):
        risk_id = risk_row.get("RiskID", f"Risk_{idx}")
        
        # Simulate this risk
        risk_losses = simulate_annual_loss(risk_row, n_sims=n_sims, seed=risk_seeds[idx])
        
        # Store individual risk results
        results[f"by_risk:{risk_id}"] = risk_losses
        
        # Add to portfolio total
        portfolio_total += risk_losses
    
    # Create result DataFrame
    result_df = pd.DataFrame(results)
    result_df.insert(0, "portfolio_loss", portfolio_total)
    
    return result_df


def simulate_risk_batch(
    register_df: pd.DataFrame,
    n_sims: int = 50_000,
    seed: Optional[int] = None,
    return_stats: bool = True
) -> Dict[str, np.ndarray]:
    """
    Simulate portfolio and return individual risk arrays.
    
    Convenience function for analysis that needs access to individual arrays.
    
    Args:
        register_df: Risk register DataFrame
        n_sims: Number of simulations
        seed: Random seed
        return_stats: If True, also compute basic stats per risk
        
    Returns:
        Dictionary mapping RiskID to loss array, plus 'portfolio' key for total
    """
    result_df = simulate_portfolio(register_df, n_sims, seed)
    
    # Extract arrays
    output = {"portfolio": result_df["portfolio_loss"].values}
    
    for col in result_df.columns:
        if col.startswith("by_risk:"):
            risk_id = col.replace("by_risk:", "")
            output[risk_id] = result_df[col].values
    
    return output
