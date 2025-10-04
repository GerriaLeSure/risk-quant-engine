"""
Streamlit Dashboard for Enterprise Risk Quantification & Analytics Engine

A comprehensive web interface for risk analysis using Monte Carlo simulation.
"""

import io
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from risk_mc import (
    lec_points,
    load_register,
    quantify_register,
    simulate_annual_loss,
    simulate_portfolio,
)
from risk_mc.lec import plot_lec_plotly

# Page configuration
st.set_page_config(
    page_title="Risk MC - Enterprise Risk Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #2E86AB;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "register_df" not in st.session_state:
    st.session_state.register_df = None
if "quantified_df" not in st.session_state:
    st.session_state.quantified_df = None
if "portfolio_df" not in st.session_state:
    st.session_state.portfolio_df = None


def load_sample_data():
    """Load sample risk register"""
    sample_path = Path(__file__).parent.parent / "data" / "sample_risk_register.csv"
    if sample_path.exists():
        try:
            df = load_register(str(sample_path))
            return df
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")
            return None
    return None


def risk_register_tab():
    """Risk Register Upload and Display"""
    st.header("📋 Risk Register Management")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Upload Risk Register")
        uploaded_file = st.file_uploader(
            "Choose CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Upload your risk register with required columns",
        )

    with col2:
        st.subheader("Or Use Sample Data")
        if st.button("Load Sample Register", type="primary"):
            sample_df = load_sample_data()
            if sample_df is not None:
                st.session_state.register_df = sample_df
                st.success(f"✅ Loaded {len(sample_df)} sample risks")
                st.rerun()

    # Load uploaded file
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Validate and load
            st.session_state.register_df = load_register(io.BytesIO(uploaded_file.getvalue()))
            st.success(f"✅ Successfully loaded {len(df)} risks")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

    # Display register if loaded
    if st.session_state.register_df is not None:
        st.markdown("---")
        st.subheader("Current Risk Register")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Risks", len(st.session_state.register_df))
        with col2:
            n_cats = st.session_state.register_df["Category"].nunique()
            st.metric("Categories", n_cats)
        with col3:
            freq_models = st.session_state.register_df["FrequencyModel"].value_counts()
            st.metric("Freq Models", f"{len(freq_models)} types")
        with col4:
            sev_models = st.session_state.register_df["SeverityModel"].value_counts()
            st.metric("Sev Models", f"{len(sev_models)} types")

        # Display dataframe
        display_cols = [
            "RiskID",
            "Category",
            "Description",
            "FrequencyModel",
            "SeverityModel",
            "ControlEffectiveness",
            "ResidualFactor",
        ]
        st.dataframe(
            st.session_state.register_df[display_cols], use_container_width=True, height=400
        )

        # Run quantification
        st.markdown("---")
        col1, col2 = st.columns([1, 3])

        with col1:
            n_sims = st.number_input(
                "Simulations",
                min_value=1000,
                max_value=100000,
                value=50000,
                step=5000,
                help="Number of Monte Carlo simulations",
            )

        with col2:
            if st.button("🎲 Run Quantification", type="primary", use_container_width=True):
                with st.spinner(f"Running {n_sims:,} Monte Carlo simulations..."):
                    try:
                        quantified = quantify_register(
                            st.session_state.register_df, n_sims=n_sims, seed=42
                        )
                        st.session_state.quantified_df = quantified
                        st.success("✅ Quantification complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during quantification: {str(e)}")

        # Display quantified results
        if st.session_state.quantified_df is not None:
            st.markdown("---")
            st.subheader("Quantified Risk Metrics")

            result_cols = [
                "RiskID",
                "Category",
                "SimMean",
                "SimP95",
                "SimVaR95",
                "SimVaR99",
                "SimTVaR95",
                "SimTVaR99",
            ]

            # Format numeric columns
            display_df = st.session_state.quantified_df[result_cols].copy()

            st.dataframe(
                display_df.style.format(
                    {
                        "SimMean": "${:,.0f}",
                        "SimP95": "${:,.0f}",
                        "SimVaR95": "${:,.0f}",
                        "SimVaR99": "${:,.0f}",
                        "SimTVaR95": "${:,.0f}",
                        "SimTVaR99": "${:,.0f}",
                    }
                ),
                use_container_width=True,
                height=400,
            )


def monte_carlo_tab():
    """Monte Carlo Simulation for Individual Risk"""
    st.header("🎲 Monte Carlo Simulation")

    if st.session_state.register_df is None:
        st.warning("⚠️ Please load a risk register first")
        return

    # Risk selection
    risk_ids = st.session_state.register_df["RiskID"].tolist()
    selected_risk_id = st.selectbox(
        "Select Risk to Analyze", risk_ids, help="Choose a risk for detailed Monte Carlo analysis"
    )

    risk_row = st.session_state.register_df[
        st.session_state.register_df["RiskID"] == selected_risk_id
    ].iloc[0]

    # Display risk details
    st.subheader(f"Risk Details: {selected_risk_id}")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Category:** {risk_row['Category']}")
        st.markdown(f"**Description:** {risk_row['Description']}")

    with col2:
        st.markdown(f"**Frequency:** {risk_row['FrequencyModel']}({risk_row['FreqParam1']})")
        st.markdown(f"**Severity:** {risk_row['SeverityModel']}")

    with col3:
        st.markdown(f"**Control Eff:** {risk_row['ControlEffectiveness']:.1%}")
        st.markdown(f"**Residual Factor:** {risk_row['ResidualFactor']:.1%}")

    # Simulation controls
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        n_sims = st.slider(
            "Number of Simulations", min_value=1000, max_value=100000, value=10000, step=1000
        )

    with col2:
        if st.button("Run Simulation", type="primary"):
            with st.spinner("Running simulation..."):
                try:
                    losses = simulate_annual_loss(risk_row, n_sims=n_sims, seed=42)
                    st.session_state[f"sim_losses_{selected_risk_id}"] = losses
                    st.success("✅ Simulation complete!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Display results
    if f"sim_losses_{selected_risk_id}" in st.session_state:
        losses = st.session_state[f"sim_losses_{selected_risk_id}"]

        st.markdown("---")
        st.subheader("Simulation Results")

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Loss", f"${np.mean(losses):,.0f}")
        with col2:
            st.metric("95% VaR", f"${np.percentile(losses, 95):,.0f}")
        with col3:
            st.metric("99% VaR", f"${np.percentile(losses, 99):,.0f}")
        with col4:
            var95 = np.percentile(losses, 95)
            tail = losses[losses >= var95]
            tvar95 = np.mean(tail) if len(tail) > 0 else var95
            st.metric("95% TVaR", f"${tvar95:,.0f}")

        # Histogram
        st.subheader("Loss Distribution")
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=losses, nbinsx=60, name="Loss Distribution", marker_color="#2E86AB", opacity=0.75
            )
        )

        # Add VaR lines
        var95 = np.percentile(losses, 95)
        var99 = np.percentile(losses, 99)

        fig.add_vline(
            x=var95,
            line_dash="dash",
            line_color="red",
            annotation_text="95% VaR",
            annotation_position="top",
        )
        fig.add_vline(
            x=var99,
            line_dash="dash",
            line_color="darkred",
            annotation_text="99% VaR",
            annotation_position="top",
        )

        fig.update_layout(
            title=f"Annual Loss Distribution - {selected_risk_id}",
            xaxis_title="Loss Amount ($)",
            yaxis_title="Frequency",
            height=500,
            template="plotly_white",
        )

        st.plotly_chart(fig, use_container_width=True)

        # Detailed statistics
        with st.expander("📊 Detailed Statistics"):
            stats_df = pd.DataFrame(
                {
                    "Metric": [
                        "Mean",
                        "Median",
                        "Std Dev",
                        "Min",
                        "Max",
                        "P90",
                        "P95",
                        "P99",
                        "VaR95",
                        "VaR99",
                        "TVaR95",
                        "TVaR99",
                    ],
                    "Value": [
                        np.mean(losses),
                        np.median(losses),
                        np.std(losses),
                        np.min(losses),
                        np.max(losses),
                        np.percentile(losses, 90),
                        np.percentile(losses, 95),
                        np.percentile(losses, 99),
                        var95,
                        var99,
                        tvar95,
                        np.mean(losses[losses >= var99]) if np.sum(losses >= var99) > 0 else var99,
                    ],
                }
            )

            st.dataframe(stats_df.style.format({"Value": "${:,.2f}"}), use_container_width=True)


def lec_tab():
    """Loss Exceedance Curve Analysis"""
    st.header("📈 Loss Exceedance Curve")

    if st.session_state.quantified_df is None:
        st.warning("⚠️ Please run quantification first")
        return

    st.markdown(
        """
    The Loss Exceedance Curve shows the probability of annual losses exceeding various thresholds.
    This helps understand tail risk and plan capital allocation.
    """
    )

    # Get portfolio losses from quantification
    if st.session_state.register_df is not None:
        with st.spinner("Generating Loss Exceedance Curve..."):
            try:
                # Run portfolio simulation for LEC
                portfolio_df = simulate_portfolio(
                    st.session_state.register_df, n_sims=50000, seed=42
                )
                portfolio_losses = portfolio_df["portfolio_loss"].values

                # Calculate LEC points
                lec_points(portfolio_losses, n_points=100)

                # Plot interactive LEC
                st.subheader("Interactive Loss Exceedance Curve")
                fig = plot_lec_plotly(portfolio_losses, mark_percentiles=[0.95, 0.99])
                st.plotly_chart(fig, use_container_width=True)

                # Key metrics
                st.markdown("---")
                st.subheader("Key Risk Metrics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Expected Loss",
                        f"${np.mean(portfolio_losses):,.0f}",
                        help="Mean annual portfolio loss",
                    )

                with col2:
                    p95 = np.percentile(portfolio_losses, 95)
                    st.metric("95% VaR", f"${p95:,.0f}", help="1-in-20 year loss")

                with col3:
                    p99 = np.percentile(portfolio_losses, 99)
                    st.metric("99% VaR", f"${p99:,.0f}", help="1-in-100 year loss")

                with col4:
                    tail95 = portfolio_losses[portfolio_losses >= p95]
                    tvar95 = np.mean(tail95) if len(tail95) > 0 else p95
                    st.metric("95% TVaR", f"${tvar95:,.0f}", help="Expected loss in tail scenarios")

                # Exceedance probabilities table
                st.markdown("---")
                st.subheader("Exceedance Probabilities")

                specific_probs = [0.5, 0.2, 0.1, 0.05, 0.01]
                lec_specific = lec_points(portfolio_losses, probs=specific_probs)

                display_df = lec_specific.copy()
                display_df["prob_pct"] = display_df["prob"] * 100
                display_df["return_period"] = 1 / display_df["prob"]
                display_df = display_df[["prob_pct", "loss", "return_period"]]
                display_df.columns = [
                    "Probability (%)",
                    "Loss Threshold ($)",
                    "Return Period (years)",
                ]

                st.dataframe(
                    display_df.style.format(
                        {
                            "Probability (%)": "{:.1f}%",
                            "Loss Threshold ($)": "${:,.0f}",
                            "Return Period (years)": "{:.1f}",
                        }
                    ),
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"Error generating LEC: {str(e)}")


def kpi_dashboard_tab():
    """KPI/KRI Dashboard with Risk Analytics"""
    st.header("📊 KPI/KRI Dashboard")

    if st.session_state.quantified_df is None:
        st.warning("⚠️ Please run quantification first")
        return

    quantified = st.session_state.quantified_df
    register = st.session_state.register_df

    # Portfolio overview
    st.subheader("Portfolio Overview")

    portfolio_row = quantified[quantified["RiskID"] == "PORTFOLIO_TOTAL"].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Risks", len(register))
    with col2:
        st.metric("Expected Annual Loss", f"${portfolio_row['SimMean']:,.0f}")
    with col3:
        st.metric("95% VaR", f"${portfolio_row['SimVaR95']:,.0f}")
    with col4:
        st.metric("99% TVaR", f"${portfolio_row['SimTVaR99']:,.0f}")

    st.markdown("---")

    # Top risk exposures
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 5 Risk Exposures")

        individual_risks = quantified[quantified["RiskID"] != "PORTFOLIO_TOTAL"].copy()
        top5 = individual_risks.nlargest(5, "SimMean")

        fig = go.Figure(
            go.Bar(
                x=top5["SimMean"],
                y=top5["RiskID"],
                orientation="h",
                marker={
                    "color": top5["SimMean"],
                    "colorscale": "Reds",
                    "showscale": True,
                    "colorbar": {"title": "Mean Loss"},
                },
                text=[f"${x:,.0f}" for x in top5["SimMean"]],
                textposition="auto",
            )
        )

        fig.update_layout(
            title="Mean Annual Loss by Risk",
            xaxis_title="Mean Loss ($)",
            yaxis_title="Risk ID",
            height=400,
            template="plotly_white",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk Distribution by Category")

        cat_summary = (
            individual_risks.groupby("Category")["SimMean"].sum().sort_values(ascending=False)
        )

        fig = go.Figure(
            go.Pie(
                labels=cat_summary.index,
                values=cat_summary.values,
                hole=0.4,
                textinfo="label+percent",
                marker={"colors": px.colors.qualitative.Set3},
            )
        )

        fig.update_layout(title="Expected Loss by Category", height=400)

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Control effectiveness analysis
    st.subheader("Control Effectiveness Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Inherent vs Residual comparison
        comparison_data = []
        for _, row in register.iterrows():
            inherent = 1.0 / (1 - row["ControlEffectiveness"])  # Reverse engineer
            residual = row["ResidualFactor"]
            comparison_data.append(
                {"RiskID": row["RiskID"], "Inherent": inherent, "Residual": residual}
            )

        comp_df = pd.DataFrame(comparison_data).head(10)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name="Inherent",
                x=comp_df["RiskID"],
                y=comp_df["Inherent"],
                marker_color="lightcoral",
            )
        )
        fig.add_trace(
            go.Bar(
                name="Residual",
                x=comp_df["RiskID"],
                y=comp_df["Residual"],
                marker_color="lightgreen",
            )
        )

        fig.update_layout(
            title="Inherent vs Residual Risk Factors",
            xaxis_title="Risk ID",
            yaxis_title="Risk Factor",
            barmode="group",
            height=400,
            template="plotly_white",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # VaR distribution
        st.markdown("**VaR95 Distribution Across Risks**")

        fig = go.Figure(
            go.Box(
                y=individual_risks["SimVaR95"], name="VaR95", marker_color="#2E86AB", boxmean="sd"
            )
        )

        fig.update_layout(
            title="VaR95 Distribution", yaxis_title="VaR95 ($)", height=400, template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)


def export_tab():
    """Export Results and Reports"""
    st.header("📤 Export Results")

    if st.session_state.quantified_df is None:
        st.warning("⚠️ Please run quantification first")
        return

    st.markdown(
        """
    Export your risk quantification results in various formats for reporting and analysis.
    """
    )

    st.markdown("---")

    # CSV Export
    st.subheader("📊 Export Quantified Register (CSV)")
    st.markdown("Download the complete risk register with all quantified metrics.")

    csv_buffer = io.StringIO()
    st.session_state.quantified_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    col1, col2 = st.columns([2, 1])
    with col1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"quantified_register_{timestamp}.csv",
            mime="text/csv",
            type="primary",
        )

    st.markdown("---")

    # Executive Summary
    st.subheader("📄 Executive Summary")

    if st.button("Generate Executive Summary", type="primary"):
        with st.spinner("Generating summary..."):
            try:
                summary_text = generate_executive_summary(
                    st.session_state.quantified_df, st.session_state.register_df
                )

                st.text_area("Executive Summary", summary_text, height=400)

                st.download_button(
                    label="📥 Download Summary (TXT)",
                    data=summary_text,
                    file_name=f"executive_summary_{timestamp}.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")

    st.markdown("---")

    # Risk summary table
    st.subheader("📋 Quick Summary Table")

    portfolio_row = st.session_state.quantified_df[
        st.session_state.quantified_df["RiskID"] == "PORTFOLIO_TOTAL"
    ].iloc[0]

    summary_data = {
        "Metric": [
            "Expected Annual Loss",
            "95% Value at Risk",
            "99% Value at Risk",
            "95% Tail VaR (Expected Shortfall)",
            "99% Tail VaR (Expected Shortfall)",
            "Number of Risks",
            "Risk Categories",
        ],
        "Value": [
            f"${portfolio_row['SimMean']:,.0f}",
            f"${portfolio_row['SimVaR95']:,.0f}",
            f"${portfolio_row['SimVaR99']:,.0f}",
            f"${portfolio_row['SimTVaR95']:,.0f}",
            f"${portfolio_row['SimTVaR99']:,.0f}",
            f"{len(st.session_state.register_df)}",
            f"{st.session_state.register_df['Category'].nunique()}",
        ],
    }

    st.table(pd.DataFrame(summary_data))


def generate_executive_summary(quantified_df, register_df):
    """Generate executive summary text"""
    portfolio = quantified_df[quantified_df["RiskID"] == "PORTFOLIO_TOTAL"].iloc[0]
    individual = quantified_df[quantified_df["RiskID"] != "PORTFOLIO_TOTAL"].copy()
    top_risk = individual.nlargest(1, "SimMean").iloc[0]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary = f"""
ENTERPRISE RISK QUANTIFICATION
Executive Summary Report
Generated: {timestamp}

{'='*80}
PORTFOLIO OVERVIEW
{'='*80}

Total Risks Analyzed: {len(register_df)}
Risk Categories: {register_df['Category'].nunique()}

Expected Annual Loss:      ${portfolio['SimMean']:>15,.0f}
Median Annual Loss:        ${portfolio['SimMedian']:>15,.0f}
Standard Deviation:        ${portfolio['SimStd']:>15,.0f}

{'='*80}
RISK MEASURES
{'='*80}

Value at Risk (VaR):
  95th Percentile (1-in-20 year):   ${portfolio['SimVaR95']:>15,.0f}
  99th Percentile (1-in-100 year):  ${portfolio['SimVaR99']:>15,.0f}

Tail Value at Risk (TVaR / Expected Shortfall):
  95% TVaR:                          ${portfolio['SimTVaR95']:>15,.0f}
  99% TVaR:                          ${portfolio['SimTVaR99']:>15,.0f}

{'='*80}
TOP RISK CONTRIBUTORS
{'='*80}

Top Risk: {top_risk['RiskID']} - {top_risk['Category']}
  Expected Loss:                     ${top_risk['SimMean']:>15,.0f}
  95% VaR:                           ${top_risk['SimVaR95']:>15,.0f}
  Contribution to Portfolio:         {(top_risk['SimMean']/portfolio['SimMean']*100):>15.1f}%

Top 5 Risks by Expected Loss:
"""

    top5 = individual.nlargest(5, "SimMean")
    for idx, (_, row) in enumerate(top5.iterrows(), 1):
        pct = (row["SimMean"] / portfolio["SimMean"]) * 100
        summary += f"\n{idx}. {row['RiskID']:<10} ${row['SimMean']:>12,.0f}  ({pct:>5.1f}%)"

    summary += f"""

{'='*80}
RECOMMENDATIONS
{'='*80}

1. Capital Allocation
   - Allocate ${portfolio['SimVaR95']:,.0f} for 95% VaR coverage
   - Consider ${portfolio['SimTVaR95']:,.0f} for tail risk capital

2. Risk Mitigation Priority
   - Focus on {top_risk['RiskID']} ({pct:.1f}% of expected loss)
   - Review control effectiveness for top 5 contributors

3. Monitoring
   - Implement quarterly risk assessments
   - Track actual losses vs. expected loss budget
   - Update risk register parameters based on new data

{'='*80}
END OF REPORT
{'='*80}
"""

    return summary


def main():
    """Main application"""

    # Header
    st.markdown(
        '<div class="main-header">🎯 Enterprise Risk Quantification & Analytics Engine</div>',
        unsafe_allow_html=True,
    )

    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")

    selected_tab = st.sidebar.radio(
        "Select View",
        [
            "📋 Risk Register",
            "🎲 Monte Carlo Simulation",
            "📈 Loss Exceedance Curve",
            "📊 KPI/KRI Dashboard",
            "📤 Export Results",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        """
    **Risk MC Engine**

    A comprehensive Monte Carlo simulation engine for enterprise risk quantification.

    **Features:**
    - Frequency/Severity modeling
    - 50,000+ simulations
    - VaR, TVaR, LEC analysis
    - Interactive dashboards
    """
    )

    # Route to selected tab
    if selected_tab == "📋 Risk Register":
        risk_register_tab()
    elif selected_tab == "🎲 Monte Carlo Simulation":
        monte_carlo_tab()
    elif selected_tab == "📈 Loss Exceedance Curve":
        lec_tab()
    elif selected_tab == "📊 KPI/KRI Dashboard":
        kpi_dashboard_tab()
    elif selected_tab == "📤 Export Results":
        export_tab()


if __name__ == "__main__":
    main()
