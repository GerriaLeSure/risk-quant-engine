"""
Risk MC - Monte Carlo Engine for Enterprise Risk Quantification

A modular library for frequency/severity risk modeling and portfolio simulation.
"""

__version__ = "1.0.0"

from .dashboard_kri import (
    calculate_kpi_kri_summary,
    generate_trend_data,
    plot_top_exposures,
    plot_trend_chart,
    residual_vs_inherent_heatmap,
    top_exposures,
)
from .io import load_register, quantify_register, save_quantified_register
from .lec import lec_points, plot_lec_matplotlib, plot_lec_plotly
from .metrics import marginal_contribution_to_var, summary, tornado_data, tvar, var
from .simulate import simulate_annual_loss, simulate_portfolio

__all__ = [
    "simulate_annual_loss",
    "simulate_portfolio",
    "summary",
    "var",
    "tvar",
    "tornado_data",
    "marginal_contribution_to_var",
    "lec_points",
    "plot_lec_matplotlib",
    "plot_lec_plotly",
    "load_register",
    "quantify_register",
    "save_quantified_register",
    "calculate_kpi_kri_summary",
    "residual_vs_inherent_heatmap",
    "top_exposures",
    "plot_top_exposures",
    "generate_trend_data",
    "plot_trend_chart",
]
