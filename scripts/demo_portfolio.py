#!/usr/bin/env python3
"""
Demo script for Risk MC Portfolio Simulation

Loads sample risk register, runs Monte Carlo simulation,
generates analytics and visualizations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
from risk_mc import (
    load_register,
    simulate_portfolio,
    summary,
    lec_points,
    save_quantified_register,
    quantify_register
)
from risk_mc.metrics import (
    portfolio_summary,
    contribution_analysis,
    tornado_data,
    marginal_contribution_to_var
)
from risk_mc.lec import plot_lec_matplotlib
from risk_mc.plots import (
    loss_histogram,
    plot_tornado,
    plot_dual_tornado,
    save_figure
)
from risk_mc.dashboard_kri import (
    calculate_kpi_kri_summary,
    print_kpi_kri_summary,
    residual_vs_inherent_heatmap,
    plot_top_exposures,
    generate_trend_data,
    plot_trend_chart
)
from risk_mc.simulate import simulate_risk_batch


def main():
    """Run portfolio simulation demo."""
    
    print("=" * 70)
    print("RISK MC - ENTERPRISE RISK QUANTIFICATION ENGINE")
    print("=" * 70)
    print()
    
    # Configuration
    data_dir = Path(__file__).parent.parent / "data"
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    register_path = data_dir / "sample_risk_register.csv"
    n_sims = 50_000
    seed = 42
    
    # Load risk register
    print(f"📁 Loading risk register from: {register_path}")
    register_df = load_register(str(register_path))
    print(f"   ✓ Loaded {len(register_df)} risks")
    print()
    
    # Display risk register
    print("📋 Risk Register Summary:")
    print("-" * 70)
    print(register_df[["RiskID", "Category", "FrequencyModel", "SeverityModel"]].to_string(index=False))
    print()
    
    # Run simulation
    print(f"🎲 Running Monte Carlo simulation with {n_sims:,} iterations...")
    portfolio_df = simulate_portfolio(register_df, n_sims=n_sims, seed=seed)
    print(f"   ✓ Simulation complete")
    print()
    
    # Portfolio-level metrics
    print("📊 Portfolio-Level Risk Metrics:")
    print("=" * 70)
    portfolio_losses = portfolio_df["portfolio_loss"].values
    portfolio_stats = summary(portfolio_losses, "Portfolio")
    
    print(f"Expected Loss (Mean):      ${portfolio_stats['mean']:>15,.0f}")
    print(f"Median Loss:               ${portfolio_stats['median']:>15,.0f}")
    print(f"Standard Deviation:        ${portfolio_stats['std']:>15,.0f}")
    print(f"Maximum Simulated Loss:    ${portfolio_stats['max']:>15,.0f}")
    print()
    print("Percentiles:")
    print(f"  50th (Median):           ${portfolio_stats['p50']:>15,.0f}")
    print(f"  90th:                    ${portfolio_stats['p90']:>15,.0f}")
    print(f"  95th:                    ${portfolio_stats['p95']:>15,.0f}")
    print(f"  99th:                    ${portfolio_stats['p99']:>15,.0f}")
    print()
    print("Risk Measures:")
    print(f"  VaR 95%:                 ${portfolio_stats['var_95']:>15,.0f}")
    print(f"  VaR 99%:                 ${portfolio_stats['var_99']:>15,.0f}")
    print(f"  TVaR 95% (ES):           ${portfolio_stats['tvar_95']:>15,.0f}")
    print(f"  TVaR 99% (ES):           ${portfolio_stats['tvar_99']:>15,.0f}")
    print()
    
    # Individual risk contributions
    print("🎯 Top Risk Contributors (by Mean Loss):")
    print("=" * 70)
    contrib_df = contribution_analysis(portfolio_df, top_n=10)
    print(contrib_df[["risk_id", "mean_loss", "var_95", "contribution_pct"]].to_string(index=False))
    print()
    
    # Calculate tornado data with dVaR
    print("⚡ Marginal VaR Contributions (dVaR):")
    print("=" * 70)
    
    # Extract individual risk losses
    by_risk_losses = {}
    for col in portfolio_df.columns:
        if col.startswith("by_risk:"):
            risk_id = col.replace("by_risk:", "")
            by_risk_losses[risk_id] = portfolio_df[col].values
    
    # Calculate tornado data
    tornado_df = tornado_data(register_df, portfolio_losses, by_risk_losses, q=0.95, top_n=10)
    
    print("Top Contributors by Mean Loss and Tail Contribution:")
    print(tornado_df[["risk_id", "category", "mean_loss", "dvar"]].to_string(index=False))
    print()
    
    # Loss Exceedance Curve
    print("📈 Loss Exceedance Curve:")
    print("=" * 70)
    lec_df = lec_points(portfolio_losses, probs=[0.5, 0.2, 0.1, 0.05, 0.01])
    print("Exceedance Probabilities:")
    for _, row in lec_df.iterrows():
        prob_pct = row["prob"] * 100
        loss_val = row["loss"]
        return_period = 1 / row["prob"] if row["prob"] > 0 else float("inf")
        print(f"  {prob_pct:5.1f}% chance of loss ≥ ${loss_val:>15,.0f}  (Return period: {return_period:>6.1f} years)")
    print()
    
    # Generate visualizations
    print("📊 Generating visualizations...")
    
    # 1. Portfolio loss histogram
    print("   → Portfolio loss histogram...")
    fig_hist = loss_histogram(
        portfolio_losses,
        title="Portfolio Annual Loss Distribution",
        bins=60,
        kde=True,
        mark_percentiles=[0.95, 0.99]
    )
    hist_path = artifacts_dir / "portfolio_hist.png"
    save_figure(fig_hist, str(hist_path))
    
    # 2. Loss Exceedance Curve
    print("   → Loss Exceedance Curve...")
    fig_lec = plot_lec_matplotlib(
        portfolio_losses,
        title="Portfolio Loss Exceedance Curve",
        n_points=100,
        mark_percentiles=[0.95, 0.99]
    )
    lec_path = artifacts_dir / "lec.png"
    save_figure(fig_lec, str(lec_path))
    
    # 3. Tornado chart (mean loss)
    print("   → Tornado chart (mean loss)...")
    fig_tornado_mean = plot_tornado(
        tornado_df,
        metric="mean_loss",
        title="Top Risk Contributors by Mean Annual Loss"
    )
    tornado_path = artifacts_dir / "tornado.png"
    save_figure(fig_tornado_mean, str(tornado_path))
    
    # 4. Tornado chart (dVaR)
    print("   → Tornado chart (dVaR)...")
    fig_tornado_dvar = plot_tornado(
        tornado_df,
        metric="dvar",
        title="Top Risk Contributors by Tail Contribution (dVaR)"
    )
    tornado_dvar_path = artifacts_dir / "tornado_dvar.png"
    save_figure(fig_tornado_dvar, str(tornado_dvar_path))
    
    # 5. Dual tornado chart
    print("   → Dual tornado chart...")
    fig_dual = plot_dual_tornado(tornado_df)
    dual_tornado_path = artifacts_dir / "tornado_dual.png"
    save_figure(fig_dual, str(dual_tornado_path))
    
    print()
    
    # KPI/KRI Dashboard Components
    print("📊 Generating KPI/KRI Dashboard Components...")
    print("=" * 70)
    
    # Quantify register for KPI/KRI analysis
    quantified_df = quantify_register(register_df, n_sims=n_sims, seed=seed)
    
    # 6. Residual vs Inherent Heatmap
    print("   → Residual vs Inherent heatmap...")
    fig_heatmap = residual_vs_inherent_heatmap(quantified_df, use_plotly=False)
    heatmap_path = artifacts_dir / "residual_inherent_heatmap.png"
    save_figure(fig_heatmap, str(heatmap_path))
    
    # 7. Top Exposures Chart
    print("   → Top 5 exposures chart...")
    fig_top_exp = plot_top_exposures(quantified_df, metric='mean', top_n=5)
    top_exp_path = artifacts_dir / "top_exposures.png"
    save_figure(fig_top_exp, str(top_exp_path))
    
    # 8. Trend Chart
    print("   → Risk exposure trends...")
    trend_df = generate_trend_data(quantified_df, n_periods=8, period_label="Quarter")
    fig_trend = plot_trend_chart(trend_df)
    trend_path = artifacts_dir / "risk_trends.png"
    save_figure(fig_trend, str(trend_path))
    
    # 9. Calculate KPI/KRI Summary
    print("   → Calculating KPI/KRI metrics...")
    kpi_kri = calculate_kpi_kri_summary(quantified_df)
    
    print()
    
    # Save quantified register
    print("💾 Saving quantified risk register...")
    quantified_path = artifacts_dir / "quantified_register.csv"
    quantified_df.to_csv(quantified_path, index=False)
    print()
    
    # Summary
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Artifacts generated:")
    print(f"  • {hist_path}")
    print(f"  • {lec_path}")
    print(f"  • {tornado_path}")
    print(f"  • {tornado_dvar_path}")
    print(f"  • {dual_tornado_path}")
    print(f"  • {heatmap_path}")
    print(f"  • {top_exp_path}")
    print(f"  • {trend_path}")
    print(f"  • {quantified_path}")
    print()
    
    # Print KPI/KRI Summary
    print_kpi_kri_summary(kpi_kri)
    print()
    
    print("Quick Findings:")
    print(f"  • Portfolio Expected Annual Loss: ${portfolio_stats['mean']:,.0f}")
    print(f"  • 95% VaR (worst case in 19/20 years): ${portfolio_stats['var_95']:,.0f}")
    print(f"  • 99% TVaR (expected loss in worst 1% scenarios): ${portfolio_stats['tvar_99']:,.0f}")
    print(f"  • Top risk contributor: {contrib_df.iloc[0]['risk_id']} ({contrib_df.iloc[0]['contribution_pct']:.1f}% of expected loss)")
    print(f"  • Mitigation effectiveness: {kpi_kri['mitigation_effectiveness_pct']:.1f}%")
    print(f"  • Risk concentration (top 3): {kpi_kri['concentration_ratio_pct']:.1f}%")
    print()


if __name__ == "__main__":
    main()
