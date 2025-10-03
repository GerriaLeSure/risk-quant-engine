"""
Plotting utilities for risk analysis.

Provides matplotlib and plotly helpers for histograms and distributions.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Optional, Tuple
from scipy import stats


def loss_histogram(
    losses: np.ndarray,
    title: str = "Loss Distribution",
    bins: int = 50,
    figsize: Tuple[int, int] = (10, 6),
    kde: bool = True,
    mark_percentiles: Optional[list] = None
) -> plt.Figure:
    """
    Plot loss distribution histogram with optional KDE overlay.
    
    Args:
        losses: Array of loss values
        title: Plot title
        bins: Number of histogram bins
        figsize: Figure size (width, height)
        kde: Whether to overlay kernel density estimate
        mark_percentiles: Optional list of percentiles to mark (e.g., [0.95, 0.99])
        
    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot histogram
    n, bins_edges, patches = ax.hist(
        losses,
        bins=bins,
        density=True,
        alpha=0.7,
        color="#2E86AB",
        edgecolor="black",
        label="Loss Distribution"
    )
    
    # Overlay KDE if requested
    if kde:
        kde_obj = stats.gaussian_kde(losses)
        x_range = np.linspace(losses.min(), losses.max(), 200)
        ax.plot(x_range, kde_obj(x_range), "r-", linewidth=2, label="KDE")
    
    # Mark percentiles
    if mark_percentiles:
        for pctl in mark_percentiles:
            pctl_val = np.percentile(losses, pctl * 100)
            ax.axvline(
                pctl_val,
                color="red",
                linestyle="--",
                linewidth=2,
                alpha=0.7,
                label=f"P{int(pctl*100)}: ${pctl_val:,.0f}"
            )
    
    ax.set_xlabel("Loss Amount ($)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Density", fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend()
    
    # Format x-axis as currency
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    
    plt.tight_layout()
    return fig


def loss_histogram_plotly(
    losses: np.ndarray,
    title: str = "Loss Distribution",
    bins: int = 50,
    mark_percentiles: Optional[list] = None
) -> go.Figure:
    """
    Plot interactive loss distribution histogram using plotly.
    
    Args:
        losses: Array of loss values
        title: Plot title
        bins: Number of histogram bins
        mark_percentiles: Optional list of percentiles to mark (e.g., [0.95, 0.99])
        
    Returns:
        plotly Figure object
    """
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=losses,
        nbinsx=bins,
        name="Loss Distribution",
        marker_color="#2E86AB",
        opacity=0.7,
        histnorm="probability density"
    ))
    
    # Mark percentiles
    if mark_percentiles:
        for pctl in mark_percentiles:
            pctl_val = np.percentile(losses, pctl * 100)
            fig.add_vline(
                x=pctl_val,
                line_dash="dash",
                line_color="red",
                line_width=2,
                annotation_text=f"P{int(pctl*100)}: ${pctl_val:,.0f}",
                annotation_position="top"
            )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title="Loss Amount ($)",
        yaxis_title="Density",
        template="plotly_white",
        height=500,
        showlegend=True
    )
    
    return fig


def risk_contribution_chart(
    contributions_df: pd.DataFrame,
    metric: str = "mean_loss",
    top_n: int = 10,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot risk contribution bar chart.
    
    Args:
        contributions_df: DataFrame from metrics.contribution_analysis
        metric: Metric to plot (e.g., 'mean_loss', 'var_95')
        top_n: Number of top risks to show
        figsize: Figure size
        
    Returns:
        matplotlib Figure object
    """
    df = contributions_df.head(top_n).copy()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    bars = ax.barh(df["risk_id"], df[metric], color="#2E86AB", edgecolor="black")
    
    # Color code by contribution percentage if available
    if "contribution_pct" in df.columns:
        colors = plt.cm.RdYlGn_r(df["contribution_pct"] / df["contribution_pct"].max())
        for bar, color in zip(bars, colors):
            bar.set_color(color)
    
    ax.set_xlabel(metric.replace("_", " ").title(), fontsize=12, fontweight="bold")
    ax.set_ylabel("Risk ID", fontsize=12, fontweight="bold")
    ax.set_title(f"Top {top_n} Risks by {metric.replace('_', ' ').title()}", 
                 fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--", axis="x")
    
    # Format x-axis as currency if it's a loss metric
    if "loss" in metric.lower() or "var" in metric.lower() or "tvar" in metric.lower():
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    
    plt.tight_layout()
    return fig


def frequency_severity_scatter(
    register_df: pd.DataFrame,
    portfolio_df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot frequency vs severity scatter for risks.
    
    Args:
        register_df: Risk register DataFrame
        portfolio_df: Simulation results
        figsize: Figure size
        
    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    frequencies = []
    mean_severities = []
    risk_ids = []
    
    for _, risk in register_df.iterrows():
        risk_id = risk["RiskID"]
        col_name = f"by_risk:{risk_id}"
        
        if col_name in portfolio_df.columns:
            losses = portfolio_df[col_name].values
            
            # Estimate frequency as proportion of non-zero losses
            freq = np.sum(losses > 0) / len(losses)
            
            # Estimate mean severity as mean of non-zero losses
            non_zero = losses[losses > 0]
            mean_sev = np.mean(non_zero) if len(non_zero) > 0 else 0
            
            frequencies.append(freq)
            mean_severities.append(mean_sev)
            risk_ids.append(risk_id)
    
    scatter = ax.scatter(
        mean_severities,
        frequencies,
        s=200,
        alpha=0.6,
        c=range(len(risk_ids)),
        cmap="viridis",
        edgecolors="black",
        linewidth=1.5
    )
    
    # Annotate points
    for i, risk_id in enumerate(risk_ids):
        ax.annotate(
            risk_id,
            (mean_severities[i], frequencies[i]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5)
        )
    
    ax.set_xlabel("Mean Severity ($)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Frequency (Annual Probability)", fontsize=12, fontweight="bold")
    ax.set_title("Risk Map: Frequency vs Severity", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--")
    
    # Format x-axis as currency
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.1%}"))
    
    plt.tight_layout()
    return fig


def compare_distributions(
    distributions: dict,
    title: str = "Distribution Comparison",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Compare multiple loss distributions side by side.
    
    Args:
        distributions: Dictionary mapping label to loss array
        title: Plot title
        figsize: Figure size
        
    Returns:
        matplotlib Figure object
    """
    fig, axes = plt.subplots(1, len(distributions), figsize=figsize, sharey=True)
    
    if len(distributions) == 1:
        axes = [axes]
    
    for ax, (label, losses) in zip(axes, distributions.items()):
        ax.hist(losses, bins=50, density=True, alpha=0.7, color="#2E86AB", edgecolor="black")
        ax.set_xlabel("Loss ($)", fontsize=10, fontweight="bold")
        ax.set_title(label, fontsize=12)
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    
    axes[0].set_ylabel("Density", fontsize=10, fontweight="bold")
    fig.suptitle(title, fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    return fig


def save_figure(fig: plt.Figure, path: str, dpi: int = 300) -> None:
    """
    Save matplotlib figure to file.
    
    Args:
        fig: matplotlib Figure
        path: Output file path
        dpi: Resolution in dots per inch
    """
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    print(f"Figure saved to: {path}")
