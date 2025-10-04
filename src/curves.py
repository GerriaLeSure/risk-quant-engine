"""
Loss Exceedance Curve (LEC) Generation
Visualize the probability of exceeding various loss thresholds
"""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go


class LossExceedanceCurve:
    """Generate and visualize Loss Exceedance Curves"""

    def __init__(self):
        self.curve_data: Optional[pd.DataFrame] = None

    def calculate_lec(self, loss_data: np.ndarray, n_points: int = 100) -> pd.DataFrame:
        """
        Calculate Loss Exceedance Curve from simulation data

        Args:
            loss_data: Array of simulated losses
            n_points: Number of points for the curve

        Returns:
            DataFrame with loss thresholds and exceedance probabilities
        """
        # Sort losses
        sorted_losses = np.sort(loss_data)
        n = len(sorted_losses)

        # Create loss thresholds from min to max
        min_loss = max(sorted_losses.min(), 0)
        max_loss = sorted_losses.max()

        thresholds = np.linspace(min_loss, max_loss, n_points)

        # Calculate exceedance probability for each threshold
        exceedance_probs = []
        for threshold in thresholds:
            prob = np.sum(sorted_losses >= threshold) / n
            exceedance_probs.append(prob)

        # Create DataFrame
        self.curve_data = pd.DataFrame(
            {
                "loss_threshold": thresholds,
                "exceedance_probability": exceedance_probs,
                "exceedance_percentage": np.array(exceedance_probs) * 100,
                "return_period": 1 / (np.array(exceedance_probs) + 1e-10),  # Avoid division by zero
            }
        )

        return self.curve_data

    def calculate_portfolio_lec(
        self, simulation_results: pd.DataFrame, n_points: int = 100
    ) -> pd.DataFrame:
        """
        Calculate portfolio-level Loss Exceedance Curve

        Args:
            simulation_results: Results from Monte Carlo simulation
            n_points: Number of points for the curve

        Returns:
            DataFrame with loss thresholds and exceedance probabilities
        """
        # Sum all simulations across risks
        n_simulations = len(simulation_results.iloc[0]["simulations"])
        total_losses = np.zeros(n_simulations)

        for _, row in simulation_results.iterrows():
            total_losses += row["simulations"]

        return self.calculate_lec(total_losses, n_points)

    def plot_lec_matplotlib(
        self,
        curve_data: Optional[pd.DataFrame] = None,
        title: str = "Loss Exceedance Curve",
        figsize: tuple[int, int] = (10, 6),
        add_percentiles: bool = True,
    ) -> plt.Figure:
        """
        Plot Loss Exceedance Curve using Matplotlib

        Args:
            curve_data: Curve data (uses self.curve_data if None)
            title: Plot title
            figsize: Figure size
            add_percentiles: Whether to add percentile markers

        Returns:
            Matplotlib figure
        """
        if curve_data is None:
            curve_data = self.curve_data

        if curve_data is None:
            raise ValueError("No curve data available")

        fig, ax = plt.subplots(figsize=figsize)

        # Plot main curve
        ax.plot(
            curve_data["loss_threshold"],
            curve_data["exceedance_percentage"],
            linewidth=2,
            color="#2E86AB",
            label="Exceedance Curve",
        )

        # Add percentile markers if requested
        if add_percentiles:
            percentiles = [90, 95, 99]
            for p in percentiles:
                prob = (100 - p) / 100
                idx = (curve_data["exceedance_probability"] - prob).abs().idxmin()
                loss_val = curve_data.loc[idx, "loss_threshold"]

                ax.axvline(loss_val, color="red", linestyle="--", alpha=0.5, linewidth=1)
                ax.axhline(100 - p, color="red", linestyle="--", alpha=0.5, linewidth=1)
                ax.plot(loss_val, 100 - p, "ro", markersize=6)
                ax.annotate(
                    f"P{p}: ${loss_val:,.0f}",
                    xy=(loss_val, 100 - p),
                    xytext=(10, 10),
                    textcoords="offset points",
                    fontsize=9,
                    bbox={"boxstyle": "round,pad=0.3", "facecolor": "yellow", "alpha": 0.5},
                )

        ax.set_xlabel("Loss Threshold ($)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Exceedance Probability (%)", fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.legend()

        # Format x-axis as currency
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

        plt.tight_layout()
        return fig

    def plot_lec_plotly(
        self,
        curve_data: Optional[pd.DataFrame] = None,
        title: str = "Loss Exceedance Curve",
        add_percentiles: bool = True,
    ) -> go.Figure:
        """
        Plot Loss Exceedance Curve using Plotly (interactive)

        Args:
            curve_data: Curve data (uses self.curve_data if None)
            title: Plot title
            add_percentiles: Whether to add percentile markers

        Returns:
            Plotly figure
        """
        if curve_data is None:
            curve_data = self.curve_data

        if curve_data is None:
            raise ValueError("No curve data available")

        fig = go.Figure()

        # Main curve
        fig.add_trace(
            go.Scatter(
                x=curve_data["loss_threshold"],
                y=curve_data["exceedance_percentage"],
                mode="lines",
                name="Exceedance Curve",
                line={"color": "#2E86AB", "width": 3},
                hovertemplate="Loss: $%{x:,.0f}<br>Probability: %{y:.2f}%<extra></extra>",
            )
        )

        # Add percentile markers
        if add_percentiles:
            percentiles = [90, 95, 99]
            for p in percentiles:
                prob = (100 - p) / 100
                idx = (curve_data["exceedance_probability"] - prob).abs().idxmin()
                loss_val = curve_data.loc[idx, "loss_threshold"]

                # Vertical line
                fig.add_vline(
                    x=loss_val,
                    line_dash="dash",
                    line_color="red",
                    opacity=0.5,
                    annotation_text=f"P{p}",
                    annotation_position="top",
                )

                # Marker
                fig.add_trace(
                    go.Scatter(
                        x=[loss_val],
                        y=[100 - p],
                        mode="markers+text",
                        name=f"P{p}",
                        marker={"size": 10, "color": "red"},
                        text=[f"${loss_val:,.0f}"],
                        textposition="top right",
                        hovertemplate=f"P{p}<br>Loss: $%{{x:,.0f}}<br>Probability: %{{y:.2f}}%<extra></extra>",
                    )
                )

        fig.update_layout(
            title={"text": title, "font": {"size": 18, "color": "#333"}},
            xaxis_title="Loss Threshold ($)",
            yaxis_title="Exceedance Probability (%)",
            hovermode="x unified",
            template="plotly_white",
            font={"size": 12},
            height=500,
        )

        return fig

    def get_var_cvar(
        self, loss_data: np.ndarray, confidence_levels: list[float] = None
    ) -> pd.DataFrame:
        """
        Calculate Value at Risk (VaR) and Conditional VaR (CVaR)

        Args:
            loss_data: Array of simulated losses
            confidence_levels: List of confidence levels

        Returns:
            DataFrame with VaR and CVaR values
        """
        if confidence_levels is None:
            confidence_levels = [0.9, 0.95, 0.99]
        results = []

        for cl in confidence_levels:
            percentile = cl * 100
            var = np.percentile(loss_data, percentile)
            cvar = np.mean(loss_data[loss_data >= var])

            results.append(
                {
                    "confidence_level": cl,
                    "confidence_percentage": percentile,
                    "var": var,
                    "cvar": cvar,
                }
            )

        return pd.DataFrame(results)

    def compare_multiple_lecs(
        self,
        lec_data_dict: dict[str, pd.DataFrame],
        title: str = "Loss Exceedance Curves Comparison",
    ) -> go.Figure:
        """
        Compare multiple Loss Exceedance Curves

        Args:
            lec_data_dict: Dictionary with {name: curve_data}
            title: Plot title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        colors = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E"]

        for idx, (name, data) in enumerate(lec_data_dict.items()):
            color = colors[idx % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=data["loss_threshold"],
                    y=data["exceedance_percentage"],
                    mode="lines",
                    name=name,
                    line={"color": color, "width": 2},
                    hovertemplate=f"{name}<br>Loss: $%{{x:,.0f}}<br>Probability: %{{y:.2f}}%<extra></extra>",
                )
            )

        fig.update_layout(
            title={"text": title, "font": {"size": 18, "color": "#333"}},
            xaxis_title="Loss Threshold ($)",
            yaxis_title="Exceedance Probability (%)",
            hovermode="x unified",
            template="plotly_white",
            font={"size": 12},
            height=500,
            legend={"yanchor": "top", "y": 0.99, "xanchor": "right", "x": 0.99},
        )

        return fig

    def export_curve_data(self, filepath: str):
        """Export curve data to CSV"""
        if self.curve_data is None:
            raise ValueError("No curve data available")

        self.curve_data.to_csv(filepath, index=False)
