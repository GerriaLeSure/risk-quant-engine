# 🎨 Streamlit Dashboard User Guide

## Overview

The Risk MC Streamlit Dashboard provides an interactive web interface for enterprise risk quantification and analysis.

---

## 🚀 Launching the Dashboard

### Option 1: Command Line
```bash
streamlit run src/risk_mc_dashboard.py
```

### Option 2: Shell Script
```bash
./scripts/run_dashboard.sh       # Linux/Mac
scripts\run_dashboard.bat        # Windows
```

### Option 3: Makefile
```bash
make run-dashboard
```

The dashboard will open automatically in your browser at: **http://localhost:8501**

---

## 📱 Dashboard Interface

### Sidebar Navigation

The sidebar contains 5 main sections:

1. **📋 Risk Register** - Upload and manage risk data
2. **🎲 Monte Carlo Simulation** - Analyze individual risks
3. **📈 Loss Exceedance Curve** - Portfolio tail risk analysis
4. **📊 KPI/KRI Dashboard** - Risk metrics and visualizations
5. **📤 Export Results** - Download reports and data

---

## 📋 Tab 1: Risk Register

### Features

**Upload Risk Register**
- Drag and drop CSV or Excel file
- Automatic schema validation
- Displays loaded risks in table

**Load Sample Data**
- Click "Load Sample Register" button
- Instantly loads 10 example risks
- Great for testing and learning

**View Risk Data**
- See all risks in table format
- Summary metrics (total risks, categories, models)
- Distribution breakdown

**Run Quantification**
- Adjust number of simulations (default: 50,000)
- Click "Run Quantification" button
- View results with all metrics (Mean, VaR, TVaR)

### Screenshot Placeholder
```
[Risk Register Tab]
┌─────────────────────────────────────────────────┐
│ Upload Risk Register                            │
│ [Drag and drop CSV/Excel file here]            │
│                                                 │
│ Risk Metrics Summary:                           │
│ Total Risks: 10  Categories: 8  Models: 5      │
│                                                 │
│ RiskID │ Category │ Frequency │ Severity       │
│ ────────────────────────────────────────────── │
│ R01    │ Cyber    │ Poisson   │ Lognormal     │
│ R02    │ Cyber    │ Poisson   │ Lognormal     │
│ ...                                             │
│                                                 │
│ [🎲 Run Quantification]                        │
└─────────────────────────────────────────────────┘
```

---

## 🎲 Tab 2: Monte Carlo Simulation

### Features

**Risk Selection**
- Dropdown menu to select any risk from register
- Shows risk details (category, description, parameters)

**Simulation Controls**
- Slider to adjust simulation count (1K - 100K)
- Run button to execute simulation

**Results Display**
- Key metrics: Mean, 95% VaR, 99% VaR, 95% TVaR
- Interactive histogram with VaR markers
- Detailed statistics table (expandable)

### Screenshot Placeholder
```
[Monte Carlo Simulation Tab]
┌─────────────────────────────────────────────────┐
│ Select Risk: [R01 - Phishing attack ▼]         │
│                                                 │
│ Risk Details:                                   │
│ Category: Cyber                                 │
│ Frequency: Poisson(2)                          │
│ Severity: Lognormal(12.0, 0.9)                │
│                                                 │
│ Simulations: [====|=====] 10,000              │
│ [Run Simulation]                               │
│                                                 │
│ Results:                                        │
│ Mean: $221,043  │ 95% VaR: $630,359           │
│                                                 │
│ [Loss Distribution Histogram with VaR lines]   │
└─────────────────────────────────────────────────┘
```

---

## 📈 Tab 3: Loss Exceedance Curve

### Features

**Interactive LEC Plot**
- Plotly interactive chart
- Shows probability of exceeding loss thresholds
- Annotated with 1-in-20 and 1-in-100 year losses

**Key Metrics Cards**
- Expected Loss (mean)
- 95% VaR (1-in-20 year loss)
- 99% VaR (1-in-100 year loss)
- 95% TVaR (tail average)

**Exceedance Probabilities Table**
- Specific thresholds: 50%, 20%, 10%, 5%, 1%
- Loss amounts at each threshold
- Return periods in years

### Screenshot Placeholder
```
[Loss Exceedance Curve Tab]
┌─────────────────────────────────────────────────┐
│ Loss Exceedance Curve                           │
│                                                 │
│ [Interactive chart showing probability curve]   │
│                                                 │
│ Expected │  95% VaR  │  99% VaR  │  95% TVaR  │
│ $2.3M    │  $4.5M    │  $7.5M    │  $6.6M     │
│                                                 │
│ Exceedance Probabilities:                       │
│ 50.0% → $2.0M (Return: 2.0 years)              │
│  5.0% → $4.5M (Return: 20.0 years)             │
│  1.0% → $7.5M (Return: 100.0 years)            │
└─────────────────────────────────────────────────┘
```

---

## 📊 Tab 4: KPI/KRI Dashboard

### Features

**Portfolio Overview**
- Total risks count
- Expected annual loss
- 95% VaR and 99% TVaR

**Top 5 Risk Exposures**
- Horizontal bar chart
- Color-coded by loss amount
- Shows mean annual loss per risk

**Risk Distribution by Category**
- Pie chart showing category breakdown
- Percentage of total expected loss

**Control Effectiveness**
- Inherent vs Residual risk comparison
- Bar chart showing risk factors

**VaR Distribution**
- Box plot showing VaR95 across all risks
- Identifies outliers

### Screenshot Placeholder
```
[KPI/KRI Dashboard Tab]
┌─────────────────────────────────────────────────┐
│ Portfolio Overview                              │
│ Risks: 10 │ Expected: $2.3M │ VaR95: $4.5M    │
│                                                 │
│ ┌─────────────────────┬─────────────────────┐  │
│ │ Top 5 Exposures     │ Category Breakdown  │  │
│ │ [Bar Chart]         │ [Pie Chart]        │  │
│ └─────────────────────┴─────────────────────┘  │
│                                                 │
│ ┌─────────────────────┬─────────────────────┐  │
│ │ Control Analysis    │ VaR Distribution    │  │
│ │ [Grouped Bars]      │ [Box Plot]         │  │
│ └─────────────────────┴─────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 📤 Tab 5: Export Results

### Features

**Download Quantified Register (CSV)**
- Click "Download CSV" button
- Gets timestamped filename
- Includes all original data + quantified metrics

**Generate Executive Summary**
- Click "Generate Executive Summary" button
- Shows formatted text report
- Download as TXT file
- Includes:
  - Portfolio overview
  - Risk measures (VaR, TVaR)
  - Top contributors
  - Recommendations

**Quick Summary Table**
- View key portfolio metrics
- Copy-paste friendly format

### Screenshot Placeholder
```
[Export Results Tab]
┌─────────────────────────────────────────────────┐
│ Export Quantified Register (CSV)                │
│ Download complete risk register with metrics    │
│ [📥 Download CSV]                               │
│                                                 │
│ ─────────────────────────────────────────────── │
│                                                 │
│ Executive Summary                               │
│ Generate comprehensive text report              │
│ [Generate Executive Summary]                    │
│                                                 │
│ ┌───────────────────────────────────────────┐  │
│ │ Executive Summary Report                  │  │
│ │                                           │  │
│ │ Portfolio Overview: $2.3M expected loss   │  │
│ │ 95% VaR: $4.5M                            │  │
│ │ Top Risk: R03 (69% of expected loss)      │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ [📥 Download Summary (TXT)]                    │
└─────────────────────────────────────────────────┘
```

---

## 📖 Step-by-Step Tutorial

### Getting Started (5 minutes)

**Step 1: Launch Dashboard**
```bash
streamlit run src/risk_mc_dashboard.py
```

**Step 2: Load Data**
- Go to "Risk Register" tab
- Click "Load Sample Register" button
- Verify 10 risks loaded

**Step 3: Run Quantification**
- Keep default 50,000 simulations
- Click "Run Quantification"
- Wait ~2 seconds for completion

**Step 4: View Monte Carlo**
- Go to "Monte Carlo Simulation" tab
- Select risk (e.g., "R01")
- Click "Run Simulation"
- View histogram and statistics

**Step 5: Analyze LEC**
- Go to "Loss Exceedance Curve" tab
- View interactive chart
- Check key metrics
- Review exceedance probabilities

**Step 6: Review KPIs**
- Go to "KPI/KRI Dashboard" tab
- Explore portfolio overview
- Check top risk exposures
- Analyze category breakdown

**Step 7: Export Results**
- Go to "Export Results" tab
- Click "Download CSV" for data
- Generate executive summary
- Download reports

---

## 💡 Tips and Best Practices

### Performance
- Start with 10K simulations for fast iteration
- Use 50K simulations for final analysis
- 100K simulations for high precision (slower)

### Data Upload
- Ensure CSV has all required columns (see data/SCHEMA.md)
- Verify numeric fields have proper values
- Check that ControlEffectiveness and ResidualFactor are in [0, 1]

### Analysis Workflow
1. Load data → Quantify register
2. Review individual risks in Monte Carlo tab
3. Analyze portfolio with LEC
4. Check KPIs for insights
5. Export results

### Troubleshooting
- **"Please load risk register first"**: Go to Risk Register tab and load data
- **"Please run quantification first"**: Click "Run Quantification" in Risk Register tab
- **Slow performance**: Reduce simulation count or simplify risk register

---

## 🎨 Customization

### Modify Simulation Defaults

Edit `src/risk_mc_dashboard.py`:
```python
# Change default simulation count
n_sims = st.number_input(..., value=100000)  # Increase to 100K

# Change seed for different random results
quantified = quantify_register(register, seed=None)  # Random each time
```

### Add Custom Charts

Add to any tab function:
```python
import plotly.express as px

fig = px.scatter(data, x='mean_loss', y='var_95')
st.plotly_chart(fig)
```

---

## 🔧 Technical Details

### Session State Variables
- `register_df`: Loaded risk register
- `quantified_df`: Quantified results
- `portfolio_df`: Portfolio simulation data
- `sim_losses_{RiskID}`: Individual risk simulation results

### Dependencies
- streamlit ≥ 1.31.0
- plotly ≥ 5.14.0
- pandas ≥ 2.0.0
- numpy ≥ 1.24.0

### Port Configuration
- Default: 8501
- Change with: `streamlit run ... --server.port=8502`

---

## 📞 Support

**Issues?**
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify sample data exists: `ls data/sample_risk_register.csv`
3. Run tests: `pytest tests/test_dashboard.py -v`
4. Check Streamlit docs: https://docs.streamlit.io

**Questions?**
- Review this guide
- Check the code examples
- Run the demo: `python scripts/quantify_demo.py`

---

## 🎉 Next Steps

After mastering the dashboard:
1. Upload your own risk register
2. Adjust simulation parameters
3. Export results for presentations
4. Integrate with other tools via CSV export
5. Automate with Python API (see Quick Start #2)

---

**Enjoy quantifying your enterprise risks with the interactive dashboard!** 🚀
