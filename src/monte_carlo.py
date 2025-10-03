"""
Monte Carlo Simulation Engine for Risk Quantification
Runs 10,000+ simulations to quantify risk impact and likelihood
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats


class MonteCarloSimulator:
    """Monte Carlo simulation engine for risk quantification"""
    
    def __init__(self, n_simulations: int = 10000, random_seed: Optional[int] = None):
        """
        Initialize Monte Carlo simulator
        
        Args:
            n_simulations: Number of simulations to run (default: 10000)
            random_seed: Random seed for reproducibility
        """
        self.n_simulations = n_simulations
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def simulate_risk_event(
        self,
        likelihood_mean: float,
        likelihood_std: float,
        impact_min: float,
        impact_most_likely: float,
        impact_max: float,
        distribution_type: str = "triangular"
    ) -> np.ndarray:
        """
        Simulate a single risk event using Monte Carlo
        
        Args:
            likelihood_mean: Mean probability of occurrence (0-1)
            likelihood_std: Standard deviation of likelihood
            impact_min: Minimum financial impact
            impact_most_likely: Most likely financial impact
            impact_max: Maximum financial impact
            distribution_type: Impact distribution type ('triangular', 'normal', 'lognormal')
        
        Returns:
            Array of simulated loss values
        """
        # Sample likelihood (probability of occurrence)
        # Use beta distribution bounded between 0 and 1
        likelihood = self._sample_likelihood(likelihood_mean, likelihood_std)
        
        # Sample impact (financial loss if event occurs)
        impact = self._sample_impact(
            impact_min, impact_most_likely, impact_max, distribution_type
        )
        
        # Calculate actual loss (likelihood * impact)
        # Use binomial to determine if event occurs
        occurs = np.random.binomial(1, likelihood, self.n_simulations)
        losses = occurs * impact
        
        return losses
    
    def _sample_likelihood(self, mean: float, std: float) -> np.ndarray:
        """Sample likelihood values using beta distribution"""
        # Clip to valid probability range
        mean = np.clip(mean, 0.01, 0.99)
        std = min(std, mean * (1 - mean) * 0.9)  # Ensure valid std
        
        # Convert mean and std to beta distribution parameters
        if std > 0:
            alpha, beta = self._beta_params_from_moments(mean, std)
            return np.random.beta(alpha, beta, self.n_simulations)
        else:
            return np.full(self.n_simulations, mean)
    
    def _beta_params_from_moments(self, mean: float, std: float) -> Tuple[float, float]:
        """Convert mean and std to beta distribution parameters"""
        var = std ** 2
        alpha = mean * ((mean * (1 - mean) / var) - 1)
        beta = (1 - mean) * ((mean * (1 - mean) / var) - 1)
        # Ensure valid parameters
        alpha = max(0.1, alpha)
        beta = max(0.1, beta)
        return alpha, beta
    
    def _sample_impact(
        self,
        min_val: float,
        most_likely: float,
        max_val: float,
        distribution_type: str
    ) -> np.ndarray:
        """Sample impact values based on distribution type"""
        if distribution_type == "triangular":
            return np.random.triangular(min_val, most_likely, max_val, self.n_simulations)
        elif distribution_type == "normal":
            mean = most_likely
            std = (max_val - min_val) / 6  # Approximate 3-sigma range
            samples = np.random.normal(mean, std, self.n_simulations)
            return np.clip(samples, min_val, max_val)
        elif distribution_type == "lognormal":
            # Use most_likely as median
            sigma = 0.5  # Shape parameter
            samples = np.random.lognormal(np.log(most_likely), sigma, self.n_simulations)
            return np.clip(samples, min_val, max_val)
        else:
            raise ValueError(f"Unknown distribution type: {distribution_type}")
    
    def simulate_portfolio(self, risks_df: pd.DataFrame) -> pd.DataFrame:
        """
        Simulate entire risk portfolio
        
        Args:
            risks_df: DataFrame with risk register data
        
        Returns:
            DataFrame with simulation results for each risk
        """
        results = []
        
        for idx, risk in risks_df.iterrows():
            # Extract risk parameters
            likelihood_mean = risk.get('likelihood', 0.5)
            likelihood_std = risk.get('likelihood_std', 0.1)
            impact_min = risk.get('impact_min', 0)
            impact_most_likely = risk.get('impact_most_likely', risk.get('impact', 0))
            impact_max = risk.get('impact_max', risk.get('impact', 0) * 2)
            
            # Run simulation
            losses = self.simulate_risk_event(
                likelihood_mean,
                likelihood_std,
                impact_min,
                impact_most_likely,
                impact_max
            )
            
            # Calculate statistics
            result = {
                'risk_id': risk.get('risk_id', idx),
                'risk_name': risk.get('risk_name', f'Risk {idx}'),
                'category': risk.get('category', 'Unknown'),
                'mean_loss': np.mean(losses),
                'median_loss': np.median(losses),
                'std_loss': np.std(losses),
                'min_loss': np.min(losses),
                'max_loss': np.max(losses),
                'p90_loss': np.percentile(losses, 90),
                'p95_loss': np.percentile(losses, 95),
                'p99_loss': np.percentile(losses, 99),
                'var_95': np.percentile(losses, 95),  # Value at Risk
                'cvar_95': np.mean(losses[losses >= np.percentile(losses, 95)]),  # Conditional VaR
                'simulations': losses
            }
            results.append(result)
        
        return pd.DataFrame(results)
    
    def aggregate_portfolio_risk(self, simulation_results: pd.DataFrame) -> Dict:
        """
        Aggregate portfolio-level risk metrics
        
        Args:
            simulation_results: Results from simulate_portfolio
        
        Returns:
            Dictionary with portfolio-level statistics
        """
        # Sum all simulations across risks
        all_simulations = np.zeros(self.n_simulations)
        for _, row in simulation_results.iterrows():
            all_simulations += row['simulations']
        
        portfolio_stats = {
            'total_mean_loss': np.mean(all_simulations),
            'total_median_loss': np.median(all_simulations),
            'total_std_loss': np.std(all_simulations),
            'total_min_loss': np.min(all_simulations),
            'total_max_loss': np.max(all_simulations),
            'total_p90_loss': np.percentile(all_simulations, 90),
            'total_p95_loss': np.percentile(all_simulations, 95),
            'total_p99_loss': np.percentile(all_simulations, 99),
            'total_var_95': np.percentile(all_simulations, 95),
            'total_cvar_95': np.mean(all_simulations[all_simulations >= np.percentile(all_simulations, 95)]),
            'all_simulations': all_simulations,
            'n_simulations': self.n_simulations
        }
        
        return portfolio_stats


def run_sensitivity_analysis(
    simulator: MonteCarloSimulator,
    base_risk: Dict,
    parameter: str,
    variation_range: Tuple[float, float],
    n_steps: int = 10
) -> pd.DataFrame:
    """
    Run sensitivity analysis by varying a single parameter
    
    Args:
        simulator: MonteCarloSimulator instance
        base_risk: Base risk parameters
        parameter: Parameter to vary
        variation_range: (min, max) range for parameter
        n_steps: Number of steps in the range
    
    Returns:
        DataFrame with sensitivity results
    """
    results = []
    param_values = np.linspace(variation_range[0], variation_range[1], n_steps)
    
    for val in param_values:
        risk = base_risk.copy()
        risk[parameter] = val
        
        losses = simulator.simulate_risk_event(
            risk['likelihood_mean'],
            risk['likelihood_std'],
            risk['impact_min'],
            risk['impact_most_likely'],
            risk['impact_max']
        )
        
        results.append({
            parameter: val,
            'mean_loss': np.mean(losses),
            'p95_loss': np.percentile(losses, 95)
        })
    
    return pd.DataFrame(results)
