"""
Loss Exceedance Curve (LEC) utilities.

LEC shows the probability of losses exceeding various thresholds.
"""

import numpy as np
import pandas as pd
from typing import List, Optional
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def lec_points(
    losses: np.ndarray,
    probs: Optional[List[float]] = None,
    n_points: int = 100
) -> pd.DataFrame:
    """
    Calculate Loss Exceedance Curve points.
    
    Args:
        losses: Array of loss values
        probs: Optional list of specific probabilities to return (0-1)
               If None, returns n_points evenly spaced
        n_points: Number of points if probs not specified
        
    Returns:
        DataFrame with columns: prob (exceedance probability), loss (threshold)
        Sorted by probability descending
    """
    sorted_losses = np.sort(losses)
    n = len(sorted_losses)
    
    if probs is not None:
        # Calculate loss at specific probabilities
        results = []
        for p in probs:
            if not 0 <= p <= 1:
                raise ValueError(f"Probability must be in [0, 1], got {p}")
            
            # Exceedance probability p means (1-p) percentile
            percentile = (1 - p) * 100
            loss_at_prob = np.percentile(sorted_losses, percentile)
            results.append({"prob": p, "loss": loss_at_prob})
        
        df = pd.DataFrame(results)
    else:
        # Generate n_points evenly spaced
        # Create loss thresholds from min to max
        min_loss = sorted_losses[0]
        max_loss = sorted_losses[-1]
        
        if min_loss == max_loss:
            # All losses are the same
            return pd.DataFrame({
                "prob": [1.0, 0.0],
                "loss": [min_loss, min_loss]
            })
        
        thresholds = np.linspace(min_loss, max_loss, n_points)
        
        # Calculate exceedance probability for each threshold
        results = []
        for threshold in thresholds:
            n_exceeding = np.sum(sorted_losses >= threshold)
            prob = n_exceeding / n
            results.append({"prob": prob, "loss": threshold})
        
        df = pd.DataFrame(results)
    
    # Sort by probability descending
    df = df.sort_values("prob", ascending=False).reset_index(drop=True)
    
    return df


def plot_lec_matplotlib(
    losses: np.ndarray,
    title: str = "Loss Exceedance Curve",
    figsize: tuple = (10, 6),
    n_points: int = 100,
    mark_percentiles: Optional[List[float]] = None
) -> plt.Figure:
    """
    Plot Loss Exceedance Curve using matplotlib.
    
    Args:
        losses: Array of loss values
        title: Plot title
        figsize: Figure size (width, height)
        n_points: Number of points for curve
        mark_percentiles: Optional list of percentiles to mark (e.g., [0.95, 0.99])
        
    Returns:
        matplotlib Figure object
    """
    lec_df = lec_points(losses, n_points=n_points)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot main curve
    ax.plot(lec_df["loss"], lec_df["prob"], linewidth=2, color="#2E86AB", label="LEC")
    
    # Mark specific percentiles if requested
    if mark_percentiles:
        for pctl in mark_percentiles:
            loss_val = np.percentile(losses, pctl * 100)
            prob_val = 1 - pctl
            
            ax.axvline(loss_val, color="red", linestyle="--", alpha=0.5, linewidth=1)
            ax.axhline(prob_val, color="red", linestyle="--", alpha=0.5, linewidth=1)
            ax.plot(loss_val, prob_val, "ro", markersize=8)
            
            # Annotate
            label_text = f"P{int(pctl*100)}: ${loss_val:,.0f}"
            ax.annotate(
                label_text,
                xy=(loss_val, prob_val),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7)
            )
    
    ax.set_xlabel("Loss Threshold ($)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Exceedance Probability", fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend()
    
    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.1%}"))
    
    # Format x-axis as currency
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    
    plt.tight_layout()
    return fig


def plot_lec_plotly(
    losses: np.ndarray,
    title: str = "Loss Exceedance Curve",
    n_points: int = 100,
    mark_percentiles: Optional[List[float]] = None
) -> go.Figure:
    """
    Plot Loss Exceedance Curve using plotly (interactive).
    
    Args:
        losses: Array of loss values
        title: Plot title
        n_points: Number of points for curve
        mark_percentiles: Optional list of percentiles to mark (e.g., [0.95, 0.99])
        
    Returns:
        plotly Figure object
    """
    lec_df = lec_points(losses, n_points=n_points)
    
    fig = go.Figure()
    
    # Main curve
    fig.add_trace(go.Scatter(
        x=lec_df["loss"],
        y=lec_df["prob"],
        mode="lines",
        name="LEC",
        line=dict(color="#2E86AB", width=3),
        hovertemplate="Loss: $%{x:,.0f}<br>Probability: %{y:.2%}<extra></extra>"
    ))
    
    # Mark specific percentiles if requested
    if mark_percentiles:
        for pctl in mark_percentiles:
            loss_val = np.percentile(losses, pctl * 100)
            prob_val = 1 - pctl
            
            # Vertical line
            fig.add_vline(
                x=loss_val,
                line_dash="dash",
                line_color="red",
                opacity=0.5,
                annotation_text=f"P{int(pctl*100)}"
            )
            
            # Marker
            fig.add_trace(go.Scatter(
                x=[loss_val],
                y=[prob_val],
                mode="markers+text",
                name=f"P{int(pctl*100)}",
                marker=dict(size=10, color="red"),
                text=[f"${loss_val:,.0f}"],
                textposition="top right",
                hovertemplate=f"P{int(pctl*100)}<br>Loss: $%{{x:,.0f}}<br>Probability: %{{y:.2%}}<extra></extra>"
            ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title="Loss Threshold ($)",
        yaxis_title="Exceedance Probability",
        hovermode="x unified",
        template="plotly_white",
        height=500,
        yaxis=dict(tickformat=".1%")
    )
    
    return fig


def return_period(losses: np.ndarray, loss_threshold: float) -> float:
    """
    Calculate return period for a given loss threshold.
    
    Return period is the inverse of exceedance probability.
    E.g., if exceedance prob is 0.01 (1%), return period is 100 years.
    
    Args:
        losses: Array of annual loss values
        loss_threshold: Loss threshold to calculate return period for
        
    Returns:
        Return period in years
    """
    n_exceeding = np.sum(losses >= loss_threshold)
    prob = n_exceeding / len(losses)
    
    if prob == 0:
        return float("inf")
    
    return 1.0 / prob


def exceedance_prob(losses: np.ndarray, loss_threshold: float) -> float:
    """
    Calculate probability of exceeding a given loss threshold.
    
    Args:
        losses: Array of loss values
        loss_threshold: Loss threshold
        
    Returns:
        Exceedance probability (0-1)
    """
    n_exceeding = np.sum(losses >= loss_threshold)
    return n_exceeding / len(losses)
