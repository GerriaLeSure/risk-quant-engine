"""
Risk MC - Monte Carlo Engine for Enterprise Risk Quantification

A modular library for frequency/severity risk modeling and portfolio simulation.
"""

__version__ = "1.0.0"

from .simulate import simulate_annual_loss, simulate_portfolio
from .metrics import summary, var, tvar
from .lec import lec_points, plot_lec
from .io import load_register, save_quantified_register

__all__ = [
    "simulate_annual_loss",
    "simulate_portfolio",
    "summary",
    "var",
    "tvar",
    "lec_points",
    "plot_lec",
    "load_register",
    "save_quantified_register",
]
