"""
KPI/KRI Dashboard Utilities for Enterprise Risk Quantification.

Provides functions for generating Key Performance Indicators (KPIs)
and Key Risk Indicators (KRIs) for risk management dashboards.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta

# Seaborn is optional
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False


def residual_vs_inherent_heatmap(
    quantified_df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 8),
    use_plotly: bool = False
) -> plt.Figure:
    """
    Create heatmap comparing residual vs inherent risk exposure.
    
    Args:
        quantified_df: Quantified risk register with SimMean and control metrics
        figsize: Figure size for matplotlib
        use_plotly: Use Plotly instead of matplotlib/seaborn
        
    Returns:
        matplotlib Figure or plotly Figure
    """
    # Calculate inherent risk (before controls)
    # Inherent = Residual / ResidualFactor / (1 - ControlEffectiveness)
    df = quantified_df[quantified_df['RiskID'] != 'PORTFOLIO_TOTAL'].copy()
    
    # Estimate inherent loss (reverse the control effectiveness)
    df['InherentLoss'] = df['SimMean'] / (df['ResidualFactor'] * (1 - df['ControlEffectiveness'] + 0.01))
    df['ResidualLoss'] = df['SimMean']
    df['Mitigation'] = ((df['InherentLoss'] - df['ResidualLoss']) / df['InherentLoss'] * 100)
    
    if use_plotly:
        # Create plotly scatter plot
        fig = go.Figure()
        
        # Add scatter points
        fig.add_trace(go.Scatter(
            x=df['InherentLoss'],
            y=df['ResidualLoss'],
            mode='markers+text',
            text=df['RiskID'],
            textposition='top center',
            marker=dict(
                size=df['SimMean'] / df['SimMean'].max() * 50 + 10,
                color=df['Mitigation'],
                colorscale='RdYlGn',
                colorbar=dict(title="Mitigation %"),
                line=dict(width=2, color='black'),
                showscale=True
            ),
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Inherent: $%{x:,.0f}<br>" +
                "Residual: $%{y:,.0f}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Add diagonal line (y=x)
        max_val = max(df['InherentLoss'].max(), df['ResidualLoss'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(dash='dash', color='gray', width=2),
            name='No Mitigation Line',
            showlegend=True
        ))
        
        fig.update_layout(
            title="Residual vs Inherent Risk Exposure",
            xaxis_title="Inherent Loss (Before Controls) ($)",
            yaxis_title="Residual Loss (After Controls) ($)",
            template='plotly_white',
            height=600,
            hovermode='closest'
        )
        
        return fig
    
    else:
        # Create matplotlib/seaborn plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create scatter plot with size proportional to loss
        scatter = ax.scatter(
            df['InherentLoss'],
            df['ResidualLoss'],
            s=df['SimMean'] / df['SimMean'].max() * 500 + 100,
            c=df['Mitigation'],
            cmap='RdYlGn',
            alpha=0.6,
            edgecolors='black',
            linewidth=2
        )
        
        # Add diagonal line (y=x)
        max_val = max(df['InherentLoss'].max(), df['ResidualLoss'].max())
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='No Mitigation')
        
        # Add risk ID labels
        for _, row in df.iterrows():
            ax.annotate(
                row['RiskID'],
                (row['InherentLoss'], row['ResidualLoss']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=9,
                fontweight='bold'
            )
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Mitigation Effectiveness (%)', fontsize=12)
        
        ax.set_xlabel('Inherent Loss (Before Controls) ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Residual Loss (After Controls) ($)', fontsize=12, fontweight='bold')
        ax.set_title('Residual vs Inherent Risk Exposure', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format axes as currency
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'${y:,.0f}'))
        
        plt.tight_layout()
        return fig


def top_exposures(
    quantified_df: pd.DataFrame,
    metric: str = "mean",
    top_n: int = 5
) -> pd.DataFrame:
    """
    Get top N risk exposures by selected metric.
    
    Args:
        quantified_df: Quantified risk register
        metric: Metric to rank by ('mean', 'var_95', 'var_99', 'tvar_95')
        top_n: Number of top risks to return
        
    Returns:
        DataFrame with top risks sorted by metric
    """
    # Map metric names to column names
    metric_map = {
        'mean': 'SimMean',
        'var_95': 'SimVaR95',
        'var_99': 'SimVaR99',
        'tvar_95': 'SimTVaR95',
        'tvar_99': 'SimTVaR99'
    }
    
    col_name = metric_map.get(metric, 'SimMean')
    
    # Filter out portfolio total
    df = quantified_df[quantified_df['RiskID'] != 'PORTFOLIO_TOTAL'].copy()
    
    # Sort and get top N
    df_sorted = df.nlargest(top_n, col_name)
    
    # Calculate percentage of total
    total = quantified_df[quantified_df['RiskID'] == 'PORTFOLIO_TOTAL'][col_name].values[0]
    df_sorted['pct_of_total'] = (df_sorted[col_name] / total * 100)
    
    return df_sorted[['RiskID', 'Category', col_name, 'pct_of_total']]


def plot_top_exposures(
    quantified_df: pd.DataFrame,
    metric: str = "mean",
    top_n: int = 5,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot bar chart of top N risk exposures.
    
    Args:
        quantified_df: Quantified risk register
        metric: Metric to plot ('mean', 'var_95', etc.)
        top_n: Number of top risks
        figsize: Figure size
        
    Returns:
        matplotlib Figure
    """
    top_df = top_exposures(quantified_df, metric=metric, top_n=top_n)
    
    metric_map = {
        'mean': ('SimMean', 'Mean Annual Loss'),
        'var_95': ('SimVaR95', '95% VaR'),
        'var_99': ('SimVaR99', '99% VaR'),
        'tvar_95': ('SimTVaR95', '95% TVaR'),
        'tvar_99': ('SimTVaR99', '99% TVaR')
    }
    
    col_name, label = metric_map.get(metric, ('SimMean', 'Mean Loss'))
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create bar chart
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_df)))
    bars = ax.barh(top_df['RiskID'], top_df[col_name], color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, (_, row) in zip(bars, top_df.iterrows()):
        width = bar.get_width()
        ax.text(
            width * 1.02,
            bar.get_y() + bar.get_height() / 2,
            f"${width:,.0f}\n({row['pct_of_total']:.1f}%)",
            va='center',
            fontsize=9,
            fontweight='bold'
        )
    
    # Add category labels
    for i, (_, row) in enumerate(top_df.iterrows()):
        ax.text(
            0,
            i,
            f"  [{row['Category']}]",
            va='center',
            ha='left',
            fontsize=8,
            color='white',
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.7)
        )
    
    ax.set_xlabel(f'{label} ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Risk ID', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Risk Exposures by {label}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Format x-axis as currency
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    
    plt.tight_layout()
    return fig


def generate_trend_data(
    quantified_df: pd.DataFrame,
    n_periods: int = 8,
    period_label: str = "Quarter",
    volatility: float = 0.15
) -> pd.DataFrame:
    """
    Generate simulated quarterly trend data for demo/visualization.
    
    Args:
        quantified_df: Quantified risk register
        n_periods: Number of time periods
        period_label: Label for time period (Quarter, Month, etc.)
        volatility: Volatility factor for random walk (0.1 = 10%)
        
    Returns:
        DataFrame with columns: period, period_label, mean_loss, var_95, concentration
    """
    # Get portfolio metrics
    portfolio = quantified_df[quantified_df['RiskID'] == 'PORTFOLIO_TOTAL'].iloc[0]
    base_mean = portfolio['SimMean']
    base_var95 = portfolio['SimVaR95']
    
    # Calculate initial concentration (top 3 / total)
    individual = quantified_df[quantified_df['RiskID'] != 'PORTFOLIO_TOTAL'].copy()
    top3_sum = individual.nlargest(3, 'SimMean')['SimMean'].sum()
    base_concentration = top3_sum / base_mean * 100
    
    np.random.seed(42)
    
    periods = []
    for i in range(n_periods):
        # Random walk with mean reversion
        mean_factor = 1 + np.random.normal(0, volatility) - volatility * 0.5
        var_factor = 1 + np.random.normal(0, volatility * 1.2) - volatility * 0.6
        conc_factor = 1 + np.random.normal(0, volatility * 0.5)
        
        periods.append({
            'period': i + 1,
            'period_label': f'{period_label} {i + 1}',
            'mean_loss': base_mean * mean_factor * (1 + i * 0.02),  # Slight upward trend
            'var_95': base_var95 * var_factor * (1 + i * 0.025),
            'concentration': min(100, base_concentration * conc_factor)
        })
    
    return pd.DataFrame(periods)


def plot_trend_chart(
    trend_df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot risk exposure trends over time.
    
    Args:
        trend_df: DataFrame from generate_trend_data
        figsize: Figure size
        
    Returns:
        matplotlib Figure
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # Plot 1: Mean Loss and VaR95
    ax1.plot(trend_df['period'], trend_df['mean_loss'], 'o-', linewidth=2, 
             markersize=8, label='Mean Loss', color='#2E86AB')
    ax1.plot(trend_df['period'], trend_df['var_95'], 's-', linewidth=2,
             markersize=8, label='95% VaR', color='#E63946')
    
    ax1.set_ylabel('Loss Amount ($)', fontsize=12, fontweight='bold')
    ax1.set_title('Risk Exposure Trends', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'${y:,.0f}'))
    
    # Plot 2: Concentration Ratio
    ax2.plot(trend_df['period'], trend_df['concentration'], 'D-', linewidth=2,
             markersize=8, label='Top 3 Concentration', color='#F77F00')
    ax2.axhline(y=60, color='red', linestyle='--', alpha=0.5, label='Warning Threshold (60%)')
    
    ax2.set_xlabel(trend_df['period_label'].iloc[0].split()[0], fontsize=12, fontweight='bold')
    ax2.set_ylabel('Concentration (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Risk Concentration (Top 3 / Total)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1f}%'))
    
    # Set x-axis labels
    ax2.set_xticks(trend_df['period'])
    ax2.set_xticklabels(trend_df['period_label'], rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def calculate_kpi_kri_summary(
    quantified_df: pd.DataFrame,
    by_risk_losses: Optional[Dict[str, np.ndarray]] = None
) -> Dict[str, any]:
    """
    Calculate comprehensive KPI/KRI summary metrics.
    
    Args:
        quantified_df: Quantified risk register
        by_risk_losses: Optional dict of individual risk losses for advanced metrics
        
    Returns:
        Dictionary with KPIs and KRIs
    """
    # Get portfolio totals
    portfolio = quantified_df[quantified_df['RiskID'] == 'PORTFOLIO_TOTAL'].iloc[0]
    individual = quantified_df[quantified_df['RiskID'] != 'PORTFOLIO_TOTAL'].copy()
    
    # Calculate inherent risk (reverse engineering)
    total_residual = portfolio['SimMean']
    
    # Estimate total inherent (simplified)
    avg_control_eff = individual['ControlEffectiveness'].mean()
    avg_residual_factor = individual['ResidualFactor'].mean()
    total_inherent = total_residual / (avg_residual_factor * (1 - avg_control_eff + 0.01))
    
    # Calculate mitigation effectiveness
    mitigation_pct = ((total_inherent - total_residual) / total_inherent * 100) if total_inherent > 0 else 0
    
    # Top risk driver
    top_risk = individual.nlargest(1, 'SimMean').iloc[0]
    top_risk_contribution = (top_risk['SimMean'] / total_residual * 100)
    
    # Concentration ratio (top 3 / total)
    top3_sum = individual.nlargest(3, 'SimMean')['SimMean'].sum()
    concentration_ratio = (top3_sum / total_residual * 100)
    
    # Diversification metrics
    n_risks = len(individual)
    avg_risk_size = total_residual / n_risks
    
    return {
        # KPIs (Performance Indicators)
        'total_inherent_loss': total_inherent,
        'total_residual_loss': total_residual,
        'mitigation_effectiveness_pct': mitigation_pct,
        'mitigation_amount': total_inherent - total_residual,
        'avg_control_effectiveness': avg_control_eff * 100,
        'avg_residual_factor': avg_residual_factor * 100,
        
        # KRIs (Risk Indicators)
        'portfolio_var_95': portfolio['SimVaR95'],
        'portfolio_var_99': portfolio['SimVaR99'],
        'portfolio_tvar_95': portfolio['SimTVaR95'],
        'portfolio_tvar_99': portfolio['SimTVaR99'],
        'top_risk_id': top_risk['RiskID'],
        'top_risk_category': top_risk['Category'],
        'top_risk_mean': top_risk['SimMean'],
        'top_risk_contribution_pct': top_risk_contribution,
        'concentration_ratio_pct': concentration_ratio,
        'number_of_risks': n_risks,
        'average_risk_size': avg_risk_size,
        'expected_loss': portfolio['SimMean'],
        'median_loss': portfolio['SimMedian'],
        'std_dev': portfolio['SimStd']
    }


def print_kpi_kri_summary(kpi_kri: Dict[str, any]):
    """
    Print formatted KPI/KRI summary.
    
    Args:
        kpi_kri: Dictionary from calculate_kpi_kri_summary
    """
    print("=" * 80)
    print("KPI/KRI DASHBOARD SUMMARY")
    print("=" * 80)
    print()
    
    print("📊 KEY PERFORMANCE INDICATORS (KPIs)")
    print("-" * 80)
    print(f"Total Inherent Loss (Before Controls):  ${kpi_kri['total_inherent_loss']:>15,.0f}")
    print(f"Total Residual Loss (After Controls):   ${kpi_kri['total_residual_loss']:>15,.0f}")
    print(f"Mitigation Amount:                       ${kpi_kri['mitigation_amount']:>15,.0f}")
    print(f"Mitigation Effectiveness:                {kpi_kri['mitigation_effectiveness_pct']:>15.1f}%")
    print(f"Average Control Effectiveness:           {kpi_kri['avg_control_effectiveness']:>15.1f}%")
    print()
    
    print("⚠️  KEY RISK INDICATORS (KRIs)")
    print("-" * 80)
    print(f"Expected Annual Loss:                    ${kpi_kri['expected_loss']:>15,.0f}")
    print(f"95% Value at Risk (1-in-20 year):       ${kpi_kri['portfolio_var_95']:>15,.0f}")
    print(f"99% Value at Risk (1-in-100 year):      ${kpi_kri['portfolio_var_99']:>15,.0f}")
    print(f"95% Tail VaR (Expected Shortfall):      ${kpi_kri['portfolio_tvar_95']:>15,.0f}")
    print()
    
    print("🎯 CONCENTRATION METRICS")
    print("-" * 80)
    print(f"Top Risk Driver:                         {kpi_kri['top_risk_id']} ({kpi_kri['top_risk_category']})")
    print(f"Top Risk Mean Loss:                      ${kpi_kri['top_risk_mean']:>15,.0f}")
    print(f"Top Risk Contribution:                   {kpi_kri['top_risk_contribution_pct']:>15.1f}%")
    print(f"Concentration Ratio (Top 3 / Total):    {kpi_kri['concentration_ratio_pct']:>15.1f}%")
    print(f"Number of Risks:                         {kpi_kri['number_of_risks']:>15}")
    print(f"Average Risk Size:                       ${kpi_kri['average_risk_size']:>15,.0f}")
    print()
    print("=" * 80)
