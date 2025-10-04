#!/usr/bin/env python3
"""
Demo: Risk Register Quantification

Shows how to use quantify_register() for simple risk quantification workflow.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from risk_mc import load_register, quantify_register


def main():
    print("=" * 80)
    print("RISK REGISTER QUANTIFICATION DEMO")
    print("=" * 80)
    print()
    
    # Load sample risk register
    data_dir = Path(__file__).parent.parent / "data"
    register_path = data_dir / "sample_risk_register.csv"
    
    print(f"📁 Loading risk register: {register_path}")
    register = load_register(str(register_path))
    print(f"   ✓ Loaded {len(register)} risks")
    print()
    
    # Display input register
    print("📋 Input Risk Register:")
    print("-" * 80)
    display_cols = ["RiskID", "Category", "FrequencyModel", "SeverityModel"]
    print(register[display_cols].to_string(index=False))
    print()
    
    # Run quantification
    print("🎲 Running quantification (50,000 simulations)...")
    quantified = quantify_register(register, n_sims=50_000, seed=42)
    print("   ✓ Quantification complete!")
    print()
    
    # Display results
    print("=" * 80)
    print("📊 QUANTIFIED RISK REGISTER")
    print("=" * 80)
    print()
    
    # Summary table
    result_cols = ["RiskID", "Category", "SimMean", "SimP95", "SimVaR95", "SimTVaR95"]
    result_display = quantified[result_cols].copy()
    
    print("Risk Metrics Summary:")
    print("-" * 80)
    print(f"{'RiskID':<10} {'Category':<15} {'Mean Loss':>15} {'P95':>15} "
          f"{'VaR95':>15} {'TVaR95':>15}")
    print("-" * 80)
    
    for _, row in result_display.iterrows():
        print(f"{row['RiskID']:<10} {row['Category']:<15} "
              f"${row['SimMean']:>14,.0f} ${row['SimP95']:>14,.0f} "
              f"${row['SimVaR95']:>14,.0f} ${row['SimTVaR95']:>14,.0f}")
    
    print()
    
    # Portfolio summary
    portfolio = quantified[quantified["RiskID"] == "PORTFOLIO_TOTAL"].iloc[0]
    print("=" * 80)
    print("💼 PORTFOLIO SUMMARY")
    print("=" * 80)
    print()
    print(f"Expected Annual Loss:    ${portfolio['SimMean']:>15,.0f}")
    print(f"Median:                  ${portfolio['SimMedian']:>15,.0f}")
    print(f"90th Percentile:         ${portfolio['SimP90']:>15,.0f}")
    print(f"95th Percentile (VaR):   ${portfolio['SimP95']:>15,.0f}")
    print(f"99th Percentile (VaR):   ${portfolio['SimP99']:>15,.0f}")
    print(f"95% TVaR (Expected Shortfall): ${portfolio['SimTVaR95']:>15,.0f}")
    print(f"99% TVaR (Expected Shortfall): ${portfolio['SimTVaR99']:>15,.0f}")
    print()
    
    # Save to CSV
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    output_path = artifacts_dir / "quantified_register_demo.csv"
    quantified.to_csv(output_path, index=False)
    print(f"💾 Saved to: {output_path}")
    print()
    
    # Top contributors
    individual_risks = quantified[quantified["RiskID"] != "PORTFOLIO_TOTAL"].copy()
    individual_risks = individual_risks.sort_values("SimMean", ascending=False)
    
    print("🎯 Top 5 Risk Contributors (by Mean Loss):")
    print("-" * 80)
    for idx, (_, row) in enumerate(individual_risks.head(5).iterrows(), 1):
        pct = (row["SimMean"] / portfolio["SimMean"]) * 100
        print(f"{idx}. {row['RiskID']} - ${row['SimMean']:,.0f} ({pct:.1f}% of total)")
    print()
    
    print("✅ Demo complete!")


if __name__ == "__main__":
    main()
