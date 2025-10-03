"""
Distribution sampling functions for frequency and severity modeling.

Frequency distributions: Poisson, Negative Binomial
Severity distributions: Lognormal, Normal, PERT
"""

import numpy as np
from scipy import stats
from typing import Optional


def sample_frequency_poisson(lam: float, n_sims: int, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Sample event counts from Poisson distribution.
    
    Args:
        lam: Lambda parameter (mean event rate per period)
        n_sims: Number of simulations
        rng: Random number generator (optional)
        
    Returns:
        Array of shape (n_sims,) with event counts
    """
    if rng is None:
        rng = np.random.default_rng()
    
    if lam < 0:
        raise ValueError(f"Poisson lambda must be >= 0, got {lam}")
    
    return rng.poisson(lam, size=n_sims)


def sample_frequency_negbin(r: float, p: float, n_sims: int, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Sample event counts from Negative Binomial distribution.
    
    Args:
        r: Number of successes parameter (dispersion)
        p: Success probability parameter
        n_sims: Number of simulations
        rng: Random number generator (optional)
        
    Returns:
        Array of shape (n_sims,) with event counts
    """
    if rng is None:
        rng = np.random.default_rng()
    
    if r <= 0:
        raise ValueError(f"NegBin r must be > 0, got {r}")
    if not 0 < p <= 1:
        raise ValueError(f"NegBin p must be in (0, 1], got {p}")
    
    return rng.negative_binomial(r, p, size=n_sims)


def sample_severity_lognormal(
    mu: float, 
    sigma: float, 
    n_events: int, 
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample loss severities from Lognormal distribution.
    
    Args:
        mu: Mean of underlying normal (log-scale)
        sigma: Std dev of underlying normal (log-scale)
        n_events: Number of events to sample
        rng: Random number generator (optional)
        
    Returns:
        Array of shape (n_events,) with loss amounts
    """
    if rng is None:
        rng = np.random.default_rng()
    
    if sigma <= 0:
        raise ValueError(f"Lognormal sigma must be > 0, got {sigma}")
    
    if n_events == 0:
        return np.array([])
    
    return rng.lognormal(mu, sigma, size=n_events)


def sample_severity_normal(
    mu: float, 
    sigma: float, 
    n_events: int, 
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample loss severities from Normal distribution (non-negative).
    
    Args:
        mu: Mean
        sigma: Standard deviation
        n_events: Number of events to sample
        rng: Random number generator (optional)
        
    Returns:
        Array of shape (n_events,) with loss amounts (clipped to >= 0)
    """
    if rng is None:
        rng = np.random.default_rng()
    
    if sigma <= 0:
        raise ValueError(f"Normal sigma must be > 0, got {sigma}")
    
    if n_events == 0:
        return np.array([])
    
    samples = rng.normal(mu, sigma, size=n_events)
    return np.maximum(samples, 0)  # Ensure non-negative


def sample_severity_pert(
    min_val: float, 
    mode: float, 
    max_val: float, 
    n_events: int,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample loss severities from PERT distribution (Program Evaluation and Review Technique).
    
    PERT is a special case of Beta distribution scaled to [min, max].
    Uses shape parameter lambda=4 (standard PERT).
    
    Args:
        min_val: Minimum loss amount
        mode: Most likely loss amount
        max_val: Maximum loss amount
        n_events: Number of events to sample
        rng: Random number generator (optional)
        
    Returns:
        Array of shape (n_events,) with loss amounts
    """
    if rng is None:
        rng = np.random.default_rng()
    
    if not (min_val <= mode <= max_val):
        raise ValueError(f"PERT requires min <= mode <= max, got {min_val}, {mode}, {max_val}")
    
    if min_val == max_val:
        return np.full(n_events, min_val)
    
    if n_events == 0:
        return np.array([])
    
    # PERT uses lambda=4 for shape
    lam = 4
    mu = (min_val + lam * mode + max_val) / (lam + 2)
    
    # Convert to beta distribution parameters
    if mu == min_val:
        alpha = 1
    else:
        alpha = ((mu - min_val) * (2 * mode - min_val - max_val)) / ((mode - mu) * (max_val - min_val))
    
    if mu == max_val:
        beta = 1
    else:
        beta = alpha * (max_val - mu) / (mu - min_val)
    
    # Ensure valid parameters
    alpha = max(alpha, 0.1)
    beta = max(beta, 0.1)
    
    # Sample from beta and scale to [min, max]
    beta_samples = rng.beta(alpha, beta, size=n_events)
    return min_val + beta_samples * (max_val - min_val)


def sample_frequency(
    model: str,
    param1: float,
    param2: Optional[float],
    n_sims: int,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Generic frequency sampler that dispatches to specific distribution.
    
    Args:
        model: Distribution name ('Poisson' or 'NegBin')
        param1: First parameter (lambda for Poisson, r for NegBin)
        param2: Second parameter (None for Poisson, p for NegBin)
        n_sims: Number of simulations
        rng: Random number generator (optional)
        
    Returns:
        Array of event counts
    """
    model_lower = model.lower()
    
    if model_lower == "poisson":
        return sample_frequency_poisson(param1, n_sims, rng)
    elif model_lower == "negbin":
        if param2 is None:
            raise ValueError("NegBin requires param2 (p)")
        return sample_frequency_negbin(param1, param2, n_sims, rng)
    else:
        raise ValueError(f"Unknown frequency model: {model}")


def sample_severity(
    model: str,
    param1: float,
    param2: float,
    param3: Optional[float],
    n_events: int,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Generic severity sampler that dispatches to specific distribution.
    
    Args:
        model: Distribution name ('Lognormal', 'Normal', or 'PERT')
        param1: First parameter (mu for Lognormal/Normal, min for PERT)
        param2: Second parameter (sigma for Lognormal/Normal, mode for PERT)
        param3: Third parameter (None for Lognormal/Normal, max for PERT)
        n_events: Number of events to sample
        rng: Random number generator (optional)
        
    Returns:
        Array of loss amounts
    """
    model_lower = model.lower()
    
    if model_lower == "lognormal":
        return sample_severity_lognormal(param1, param2, n_events, rng)
    elif model_lower == "normal":
        return sample_severity_normal(param1, param2, n_events, rng)
    elif model_lower == "pert":
        if param3 is None:
            raise ValueError("PERT requires param3 (max)")
        return sample_severity_pert(param1, param2, param3, n_events, rng)
    else:
        raise ValueError(f"Unknown severity model: {model}")
