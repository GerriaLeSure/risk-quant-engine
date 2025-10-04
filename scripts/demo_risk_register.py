#!/usr/bin/env python3
"""
Demo: Risk Register Integration

Shows how to use the high-level risk_register module for quick analysis.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk_mc import (
    compare_scenarios,
    get_risk_summary,
    load_register,
    quantify_register,
    save_quantified_register,
)


def main():
    print("=" * 80)
    print("RISK MC - RISK REGISTER INTEGRATION DEMO")
    print("=" * 80)
    print()

    # Paths
    data_dir = Path(__file__).parent.parent / "data"
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    # Step 1: Load Risk Register
    print("Step 1: Load Risk Register")
    print("-" * 80)

    register_path = data_dir / "sample_risk_register.csv"
    print(f"Loading: {register_path}")

    register = load_register(str(register_path))
    print(f"✓ Loaded {len(register)} risks")
    print()

    print("Risk Register Preview:")
    print(register[["RiskID", "Category", "FrequencyModel", "SeverityModel"]].head())
    print()

    # Step 2: Quantify Risks
    print("Step 2: Quantify Risks with Monte Carlo")
    print("-" * 80)
    print("Running 50,000 simulations per risk...")

    quantified = quantify_register(register, n_sims=50_000, seed=42)
    print(f"✓ Quantified {len(quantified)} risks (including portfolio total)")
    print()

    # Step 3: Display Summary Table
    print("Step 3: Summary Table - Top Risks by Expected Loss")
    print("-" * 80)

    summary = get_risk_summary(quantified, top_n=5)

    print(f"{'RiskID':<10} {'Category':<15} {'Mean Loss':>15} {'VaR 95%':>15} {'TVaR 95%':>15}")
    print("-" * 80)
    for _, row in summary.iterrows():
        print(
            f"{row['RiskID']:<10} {row['Category']:<15} "
            f"${row['mean']:>14,.0f} ${row['var_95']:>14,.0f} ${row['tvar_95']:>14,.0f}"
        )
    print()

    # Step 4: Portfolio Total
    print("Step 4: Portfolio-Level Metrics")
    print("-" * 80)

    portfolio = quantified[quantified["RiskID"] == "PORTFOLIO_TOTAL"].iloc[0]

    print(f"Expected Annual Loss:      ${portfolio['mean']:>15,.0f}")
    print(f"Median Loss:               ${portfolio['median']:>15,.0f}")
    print(f"Standard Deviation:        ${portfolio['std']:>15,.0f}")
    print()
    print(f"90th Percentile:           ${portfolio['p90']:>15,.0f}")
    print(f"95th Percentile:           ${portfolio['p95']:>15,.0f}")
    print(f"99th Percentile:           ${portfolio['p99']:>15,.0f}")
    print()
    print(f"VaR 95% (1-in-20 year):    ${portfolio['var_95']:>15,.0f}")
    print(f"VaR 99% (1-in-100 year):   ${portfolio['var_99']:>15,.0f}")
    print(f"TVaR 95% (Tail Average):   ${portfolio['tvar_95']:>15,.0f}")
    print(f"TVaR 99% (Tail Average):   ${portfolio['tvar_99']:>15,.0f}")
    print()

    # Step 5: Save Results
    print("Step 5: Save Quantified Register")
    print("-" * 80)

    out_path = artifacts_dir / "quantified_register_demo.csv"
    save_quantified_register(quantified, str(out_path))
    print()

    # Step 6: Scenario Comparison
    print("Step 6: Scenario Analysis")
    print("-" * 80)
    print("Comparing: Base vs. Enhanced Controls vs. High Frequency")

    scenarios = {
        "Enhanced_Controls": {
            "R01": {"ControlEffectiveness": 0.5},
            "R02": {"ControlEffectiveness": 0.6},
        },
        "High_Frequency": {"R05": {"FreqParam1": 8.0}},
    }

    comparison = compare_scenarios(register, scenarios, n_sims=20_000, seed=42)

    print()
    print(f"{'Scenario':<20} {'Mean Loss':>15} {'VaR 95%':>15} {'TVaR 95%':>15}")
    print("-" * 80)
    for _, row in comparison.iterrows():
        print(
            f"{row['scenario']:<20} ${row['mean']:>14,.0f} "
            f"${row['var_95']:>14,.0f} ${row['tvar_95']:>14,.0f}"
        )
    print()

    # Summary
    print("=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print(f"  • Portfolio Expected Loss: ${portfolio['mean']:,.0f}")
    print(f"  • 95% VaR Capital Requirement: ${portfolio['var_95']:,.0f}")
    print(f"  • Top Risk: {summary.iloc[0]['RiskID']} - ${summary.iloc[0]['mean']:,.0f}")
    print(f"  • Quantified register saved to: {out_path}")
    print()
    print("Next Steps:")
    print("  • Review artifacts/quantified_register_demo.csv")
    print("  • Modify controls or parameters in your CSV")
    print("  • Re-run: python scripts/demo_risk_register.py")
    print()


if __name__ == "__main__":
    main()
