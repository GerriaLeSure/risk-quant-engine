#!/usr/bin/env python3
"""
Analyze User-Provided Risk Portfolio
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc import lec_points, load_register, save_quantified_register, simulate_portfolio, summary
from risk_mc.lec import plot_lec_matplotlib
from risk_mc.metrics import (
    contribution_analysis,
    tornado_data,
)
from risk_mc.plots import loss_histogram, plot_dual_tornado, plot_tornado, save_figure


def main():
    print("=" * 80)
    print("RISK MC - ANALYZING YOUR CUSTOM RISK PORTFOLIO")
    print("=" * 80)
    print()

    # Configuration
    data_dir = Path(__file__).parent.parent / "data"
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    register_path = data_dir / "user_risk_register.csv"
    n_sims = 50_000
    seed = 42

    # Load risk register
    print(f"📁 Loading risk register: {register_path}")
    register_df = load_register(str(register_path))
    print(f"   ✓ Loaded {len(register_df)} risks")
    print()

    # Display summary
    print("📋 Risk Portfolio Overview:")
    print("-" * 80)
    summary_view = register_df[["RiskID", "Category", "FrequencyModel", "SeverityModel"]].copy()
    print(summary_view.to_string(index=False))
    print()

    # Category breakdown
    print("Categories:")
    for cat, count in register_df["Category"].value_counts().items():
        print(f"  • {cat}: {count} risks")
    print()

    # Run simulation
    print(f"🎲 Running {n_sims:,} Monte Carlo simulations...")
    portfolio_df = simulate_portfolio(register_df, n_sims=n_sims, seed=seed)
    print("   ✓ Simulation complete!")
    print()

    # Portfolio metrics
    print("=" * 80)
    print("📊 PORTFOLIO RISK ANALYSIS")
    print("=" * 80)
    print()

    portfolio_losses = portfolio_df["portfolio_loss"].values
    stats = summary(portfolio_losses, "Portfolio")

    print("Expected Loss & Distribution:")
    print(f"  Mean (Expected Annual Loss):  ${stats['mean']:>15,.0f}")
    print(f"  Median (Typical Year):        ${stats['median']:>15,.0f}")
    print(f"  Standard Deviation:           ${stats['std']:>15,.0f}")
    print(f"  Maximum Simulated:            ${stats['max']:>15,.0f}")
    print()

    print("Percentiles:")
    print(f"  50th (Median):                ${stats['p50']:>15,.0f}")
    print(f"  90th:                         ${stats['p90']:>15,.0f}")
    print(f"  95th:                         ${stats['p95']:>15,.0f}")
    print(f"  99th:                         ${stats['p99']:>15,.0f}")
    print()

    print("Risk Measures (Capital Requirements):")
    print(f"  VaR 95% (1-in-20 year):       ${stats['var_95']:>15,.0f}")
    print(f"  VaR 99% (1-in-100 year):      ${stats['var_99']:>15,.0f}")
    print(f"  TVaR 95% (Tail Average):      ${stats['tvar_95']:>15,.0f}")
    print(f"  TVaR 99% (Tail Average):      ${stats['tvar_99']:>15,.0f}")
    print()

    # Individual risk contributions
    print("=" * 80)
    print("🎯 TOP RISK CONTRIBUTORS")
    print("=" * 80)
    print()

    contrib_df = contribution_analysis(portfolio_df, top_n=10)

    print("Ranked by Mean Annual Loss:")
    print("-" * 80)
    print(f"{'Rank':<6} {'RiskID':<8} {'Mean Loss':>15} {'VaR 95%':>15} {'% of Total':>12}")
    print("-" * 80)
    for idx, (_, row) in enumerate(contrib_df.iterrows(), 1):
        print(
            f"{idx:<6} {row['risk_id']:<8} ${row['mean_loss']:>14,.0f} "
            f"${row['var_95']:>14,.0f} {row['contribution_pct']:>11.1f}%"
        )
    print()

    # Extract by-risk losses for sensitivity analysis
    by_risk_losses = {}
    for col in portfolio_df.columns:
        if col.startswith("by_risk:"):
            risk_id = col.replace("by_risk:", "")
            by_risk_losses[risk_id] = portfolio_df[col].values

    # Tornado analysis
    print("=" * 80)
    print("⚡ SENSITIVITY ANALYSIS - TAIL RISK CONTRIBUTORS")
    print("=" * 80)
    print()

    tornado_df = tornado_data(register_df, portfolio_losses, by_risk_losses, q=0.95, top_n=10)

    print("Top Contributors to Portfolio Tail Risk (dVaR):")
    print("-" * 80)
    print(f"{'RiskID':<8} {'Category':<15} {'Mean Loss':>15} {'dVaR (Tail)':>15}")
    print("-" * 80)
    for _, row in tornado_df.iterrows():
        print(
            f"{row['risk_id']:<8} {row['category']:<15} "
            f"${row['mean_loss']:>14,.0f} ${row['dvar']:>14,.0f}"
        )
    print()

    # Loss Exceedance Curve
    print("=" * 80)
    print("📈 LOSS EXCEEDANCE ANALYSIS")
    print("=" * 80)
    print()

    lec_df = lec_points(portfolio_losses, probs=[0.5, 0.2, 0.1, 0.05, 0.01])

    print("Probability of Exceeding Loss Thresholds:")
    print("-" * 80)
    print(f"{'Probability':<15} {'Loss Threshold':>18} {'Return Period':>18}")
    print("-" * 80)
    for _, row in lec_df.iterrows():
        prob_pct = row["prob"] * 100
        loss_val = row["loss"]
        return_period = 1 / row["prob"] if row["prob"] > 0 else float("inf")
        print(f"{prob_pct:>6.1f}% chance   ${loss_val:>16,.0f}   {return_period:>10.1f} years")
    print()

    # Key insights
    print("=" * 80)
    print("💡 KEY INSIGHTS")
    print("=" * 80)
    print()

    top_risk = contrib_df.iloc[0]
    top_tail_risk = tornado_df.iloc[0]

    print(f"1. Expected Annual Loss: ${stats['mean']:,.0f}")
    print("   → Budget this amount for risk reserves")
    print()
    print(f"2. Worst Case Planning (95% VaR): ${stats['var_95']:,.0f}")
    print("   → 1-in-20 year loss scenario")
    print("   → Consider capital allocation or insurance above this level")
    print()
    print(f"3. Extreme Tail Risk (99% TVaR): ${stats['tvar_99']:,.0f}")
    print("   → Average loss in worst 1% of scenarios")
    print("   → Regulatory capital requirement benchmark")
    print()
    print(
        f"4. Top Risk Driver: {top_risk['risk_id']} ({top_risk['contribution_pct']:.1f}% of expected loss)"
    )
    print(
        f"   → Category: {register_df[register_df['RiskID']==top_risk['risk_id']]['Category'].values[0]}"
    )
    print("   → Prioritize mitigation efforts here")
    print()
    print(f"5. Top Tail Risk Driver: {top_tail_risk['risk_id']}")
    print(f"   → Drives worst-case scenarios (dVaR: ${top_tail_risk['dvar']:,.0f})")
    print("   → Focus on extreme risk reduction")
    print()

    # Generate visualizations
    print("=" * 80)
    print("📊 GENERATING VISUALIZATIONS")
    print("=" * 80)
    print()

    print("Creating charts...")

    # 1. Loss histogram
    fig_hist = loss_histogram(
        portfolio_losses,
        title="Portfolio Annual Loss Distribution",
        bins=60,
        kde=True,
        mark_percentiles=[0.95, 0.99],
    )
    hist_path = artifacts_dir / "user_portfolio_hist.png"
    save_figure(fig_hist, str(hist_path))

    # 2. LEC
    fig_lec = plot_lec_matplotlib(
        portfolio_losses, title="Loss Exceedance Curve", n_points=100, mark_percentiles=[0.95, 0.99]
    )
    lec_path = artifacts_dir / "user_lec.png"
    save_figure(fig_lec, str(lec_path))

    # 3. Tornado - mean loss
    fig_tornado = plot_tornado(
        tornado_df, metric="mean_loss", title="Top Risk Contributors by Mean Annual Loss"
    )
    tornado_path = artifacts_dir / "user_tornado_mean.png"
    save_figure(fig_tornado, str(tornado_path))

    # 4. Tornado - dVaR
    fig_tornado_dvar = plot_tornado(
        tornado_df, metric="dvar", title="Top Risk Contributors by Tail Risk (dVaR)"
    )
    tornado_dvar_path = artifacts_dir / "user_tornado_dvar.png"
    save_figure(fig_tornado_dvar, str(tornado_dvar_path))

    # 5. Dual tornado
    fig_dual = plot_dual_tornado(tornado_df)
    dual_path = artifacts_dir / "user_tornado_dual.png"
    save_figure(fig_dual, str(dual_path))

    print()

    # Save quantified register
    print("💾 Saving quantified risk register...")
    quantified_path = artifacts_dir / "user_quantified_register.csv"
    save_quantified_register(register_df, portfolio_df, str(quantified_path))
    print()

    # Summary
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Generated Artifacts:")
    print(f"  • {hist_path}")
    print(f"  • {lec_path}")
    print(f"  • {tornado_path}")
    print(f"  • {tornado_dvar_path}")
    print(f"  • {dual_path}")
    print(f"  • {quantified_path}")
    print()
    print("Recommendations:")
    print(f"  1. Review top contributor: {top_risk['risk_id']} - consider enhanced controls")
    print(f"  2. Allocate ${stats['var_95']:,.0f} for 95% VaR coverage")
    print(f"  3. Investigate tail driver: {top_tail_risk['risk_id']} - assess worst-case scenarios")
    print(f"  4. Annual risk budget: ${stats['mean']:,.0f}")
    print()


if __name__ == "__main__":
    main()
