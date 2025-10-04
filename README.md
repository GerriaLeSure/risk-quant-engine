# Risk MC - Monte Carlo Engine for Enterprise Risk Quantification

A Python library for enterprise risk quantification using frequency/severity Monte Carlo simulation with advanced analytics and visualization.

## 🎯 Features

- **Frequency/Severity Modeling**: Separate distributions for event frequency and loss severity
- **Multiple Distributions**:
  - Frequency: Poisson, Negative Binomial
  - Severity: Lognormal, Normal (truncated), PERT
- **Portfolio Simulation**: Aggregate multiple risks with 50,000+ simulations
- **Risk Metrics**: VaR, TVaR (Expected Shortfall), percentiles, summary statistics
- **Loss Exceedance Curves**: Probability of exceeding loss thresholds
- **Sensitivity Analysis**: Marginal VaR contributions (dVaR), tornado charts
- **Control Effectiveness**: Model impact of risk controls and residual factors
- **Visualization**: Matplotlib and Plotly charts (histograms, LECs, tornado charts)
- **I/O Support**: CSV and Excel risk register import/export

## 📦 Installation

```bash
# Clone or download the repository
cd risk-mc

# Install dependencies
make install
# or
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Streamlit Web Dashboards (Easiest!)

**TWO Professional Dashboards Available:**

#### Option A: Risk MC Dashboard (Monte Carlo Engine)
```bash
# Launch Risk MC dashboard (Frequency × Severity Monte Carlo)
streamlit run src/risk_mc_dashboard.py

# Or use shortcuts
./scripts/run_dashboard.sh
make run-dashboard
```

**Dashboard Features:**
1. 📋 Upload risk register (CSV/Excel)
2. 🎲 Run Monte Carlo simulations (50K+)
3. 📈 View Loss Exceedance Curves
4. 📊 Explore KPI/KRI dashboards (VaR, TVaR, dVaR)
5. 📤 Export results and reports

#### Option B: Original Dashboard (Likelihood × Impact)
```bash
# Launch original dashboard (Traditional risk scoring)
streamlit run src/dashboard.py
```

**Dashboard Features:**
1. 📋 Risk register with likelihood × impact scoring
2. 🎲 Monte Carlo simulation with triangular/lognormal
3. 📈 Loss Exceedance Curves
4. 📊 KPI/KRI Dashboard with risk appetite gauge
5. 📤 Export CSV, TXT, and **PowerPoint** presentations

**Both dashboards:** http://localhost:8501

### 2. Simple Risk Register Quantification (Python API)

```python
from risk_mc import load_register, quantify_register

# Load your risk register
register = load_register("data/sample_risk_register.csv")

# Run quantification (50,000 simulations)
quantified = quantify_register(register, n_sims=50_000, seed=42)

# View results
print(quantified[["RiskID", "SimMean", "SimVaR95", "SimTVaR95"]])

# Save results
quantified.to_csv("quantified_risks.csv", index=False)
```

### 2. Run Demo Simulation

```bash
make run-demo
# or
python scripts/demo_portfolio.py
```

This will:
- Load the sample risk register (10 risks)
- Run 50,000 Monte Carlo simulations
- Generate analytics and visualizations in `artifacts/`
- Save quantified risk register with VaR/TVaR metrics

### 3. Basic Usage

```python
from risk_mc import load_register, simulate_portfolio, summary

# Load risk register
register_df = load_register("data/sample_risk_register.csv")

# Run simulation
portfolio_df = simulate_portfolio(register_df, n_sims=50_000, seed=42)

# Get portfolio metrics
portfolio_losses = portfolio_df["portfolio_loss"].values
stats = summary(portfolio_losses)

print(f"Expected Loss: ${stats['mean']:,.0f}")
print(f"95% VaR: ${stats['var_95']:,.0f}")
print(f"99% TVaR: ${stats['tvar_99']:,.0f}")
```

### 3. Loss Exceedance Curve

```python
from risk_mc import lec_points
from risk_mc.plots import plot_lec_matplotlib

# Calculate LEC
lec_df = lec_points(portfolio_losses, probs=[0.5, 0.2, 0.1, 0.05, 0.01])

# Plot
fig = plot_lec_matplotlib(portfolio_losses, mark_percentiles=[0.95, 0.99])
fig.savefig("lec.png")
```

### 4. Sensitivity Analysis

```python
from risk_mc.metrics import tornado_data
from risk_mc.plots import plot_tornado

# Extract individual risk losses
by_risk_losses = {}
for col in portfolio_df.columns:
    if col.startswith("by_risk:"):
        risk_id = col.replace("by_risk:", "")
        by_risk_losses[risk_id] = portfolio_df[col].values

# Generate tornado data
tornado_df = tornado_data(
    register_df, 
    portfolio_losses, 
    by_risk_losses, 
    q=0.95, 
    top_n=10
)

# Plot
fig = plot_tornado(tornado_df, metric="mean_loss")
fig.savefig("tornado.png")
```

## 📋 Risk Register Integration

### Overview

The `risk_register` module provides high-level functions for end-to-end risk quantification:

1. **Load** risk register from CSV/Excel
2. **Quantify** all risks with Monte Carlo simulation
3. **Analyze** results with summary statistics
4. **Save** quantified register with metrics
5. **Compare** scenarios with different parameters

### Quick Example

```python
from risk_mc import (
    load_register,
    quantify_register,
    get_risk_summary,
    save_quantified_register
)

# Load and quantify
register = load_register("data/risks.csv")
quantified = quantify_register(register, n_sims=50_000, seed=42)

# View top risks
top_risks = get_risk_summary(quantified, top_n=10)
print(top_risks)

# Save results
save_quantified_register(quantified, "output/quantified.csv")
```

### Scenario Comparison

```python
from risk_mc import compare_scenarios

scenarios = {
    "Enhanced_Controls": {
        "R01": {"ControlEffectiveness": 0.6},
        "R02": {"ResidualFactor": 0.5}
    },
    "High_Frequency": {
        "R03": {"FreqParam1": 3.0}
    }
}

comparison = compare_scenarios(register, scenarios, n_sims=20_000, seed=42)
print(comparison)
```

**Output:**
```
     scenario        mean     var_95    tvar_95
         Base  2,292,100  4,480,423  6,649,507
Enhanced_...  2,079,734  3,828,323  5,382,366
High_Freq...  2,768,472  4,979,651  7,298,766
```

## 📊 Risk Register Format

### Templates Available

Two CSV templates are provided in the `data/` directory:

1. **`sample_risk_register.csv`** - Demo-ready template with 10 example risks
   - Use this to explore the dashboard and learn the system
   - Contains realistic risk examples across different categories
   - Ready to load and quantify immediately

2. **`blank_risk_register_template.csv`** - Empty template for your own risks
   - Use this to create your own risk register from scratch
   - Contains only column headers, no data rows
   - Fill in with your organization's risk data

### Required Columns

CSV/Excel file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `RiskID` | Unique identifier | R01 |
| `Category` | Risk category | Cyber, Operational, Financial |
| `Description` | Risk description | Phishing attack leading to data breach |
| `FrequencyModel` | Distribution for event count | Poisson, NegBin |
| `FreqParam1` | First parameter | λ for Poisson, r for NegBin |
| `FreqParam2` | Second parameter (optional) | p for NegBin |
| `SeverityModel` | Distribution for loss amount | Lognormal, Normal, PERT |
| `SevParam1` | First parameter | μ for Lognormal/Normal, min for PERT |
| `SevParam2` | Second parameter | σ for Lognormal/Normal, mode for PERT |
| `SevParam3` | Third parameter (optional) | max for PERT |
| `ControlEffectiveness` | Control reduction (0-1) | 0.3 = 30% reduction |
| `ResidualFactor` | Residual multiplier (0-1) | 0.7 = 30% reduction |

### Example Input CSV

```csv
RiskID,Category,Description,FrequencyModel,FreqParam1,FreqParam2,SeverityModel,SevParam1,SevParam2,SevParam3,ControlEffectiveness,ResidualFactor
R01,Cyber,Phishing attack,Poisson,2.0,,Lognormal,12.0,0.8,,0.3,0.7
R02,Cyber,Ransomware incident,Poisson,0.5,,Lognormal,14.0,1.2,,0.4,0.6
R03,Operational,Supply chain disruption,Poisson,1.5,,Normal,500000,150000,,0.2,0.8
R04,Operational,Equipment failure,NegBin,3.0,0.6,PERT,50000,100000,300000,0.1,0.9
```

### Example Output (Quantified Register)

After running `quantify_register()`, you get:

| RiskID | Category | mean | median | std | p90 | p95 | p99 | var_95 | var_99 | tvar_95 | tvar_99 |
|--------|----------|------|--------|-----|-----|-----|-----|--------|--------|---------|---------|
| R01 | Cyber | 221,043 | 187,092 | 167,421 | 418,926 | 630,359 | 973,896 | 630,359 | 973,896 | 841,694 | 1,202,487 |
| R02 | Cyber | 449,181 | 0 | 1,346,823 | 917,877 | 2,297,463 | 5,415,995 | 2,297,463 | 5,415,995 | 4,531,480 | 9,346,549 |
| R03 | Operational | 479,453 | 479,618 | 199,871 | 731,234 | 1,244,722 | 1,662,909 | 1,244,722 | 1,662,909 | 1,505,673 | 1,898,048 |
| **PORTFOLIO_TOTAL** | **Portfolio** | **2,292,100** | **2,011,135** | **1,500,990** | **3,613,576** | **4,480,423** | **7,532,116** | **4,480,423** | **7,532,116** | **6,649,507** | **11,312,135** |

**Interpretation:**
- **mean**: Budget this amount annually
- **var_95**: 1-in-20 year loss (95th percentile)
- **var_99**: 1-in-100 year loss (99th percentile)
- **tvar_95**: Average loss when exceeding VaR95 (regulatory capital)
- **tvar_99**: Average loss in worst 1% scenarios

### Distribution Parameters

**Frequency Distributions:**
- **Poisson(λ)**: λ = mean annual event count
- **NegBin(r, p)**: r = number of successes, p = success probability

**Severity Distributions:**
- **Lognormal(μ, σ)**: μ, σ on log scale (use `log(median)` for μ)
- **Normal(μ, σ)**: μ = mean, σ = standard deviation (truncated at 0)
- **PERT(min, mode, max)**: Three-point estimate using Beta distribution

## 🏗️ Project Structure

```
risk-mc/
├── src/risk_mc/
│   ├── __init__.py              # Main exports
│   ├── distributions.py         # Frequency/severity distributions
│   ├── simulate.py              # Core simulation engine
│   ├── metrics.py               # Risk metrics (VaR, TVaR, dVaR)
│   ├── lec.py                   # Loss Exceedance Curve utilities
│   ├── plots.py                 # Visualization helpers
│   └── io.py                    # CSV/Excel I/O
├── data/
│   ├── sample_risk_register.csv        # Sample with 10 example risks
│   ├── blank_risk_register_template.csv # Empty template for custom risks
│   └── SCHEMA.md                       # Detailed schema documentation
├── tests/
│   ├── test_simulate.py         # Simulation tests
│   ├── test_lec.py              # LEC tests
│   ├── test_io.py               # I/O tests
│   └── test_distributions.py    # Distribution tests
├── scripts/
│   └── demo_portfolio.py        # Demo script
├── artifacts/                   # Generated outputs
├── requirements.txt             # Dependencies
├── pyproject.toml               # Project config (ruff, black)
├── Makefile                     # Build commands
└── README.md                    # This file
```

## 📊 Dashboards & KPI/KRI Features

### Two Complete Dashboard Options:

#### 1. Risk MC Dashboard (`src/risk_mc_dashboard.py`)

**Best for:** Quantitative Monte Carlo analysis

**5 Tabs:**
- 📋 **Risk Register**: Upload CSV/Excel, quantify risks
- 🎲 **Monte Carlo**: Individual risk deep-dive (1K-100K sims)
- 📈 **Loss Exceedance Curve**: Interactive LEC with percentiles
- 📊 **KPI/KRI Dashboard**: Portfolio metrics, top exposures, category breakdown
- 📤 **Export**: CSV download, executive summary

**Launch:** `streamlit run src/risk_mc_dashboard.py`

#### 2. Original Dashboard (`src/dashboard.py`)

**Best for:** Traditional risk scoring with likelihood × impact

**4 Tabs:**
- 📋 **Risk Register**: Upload and manage risk data
- 🎲 **Monte Carlo**: Triangular/lognormal simulation
- 📈 **Loss Exceedance Curve**: Portfolio LEC
- 📊 **KPI/KRI Dashboard**: Inherent vs Residual, trends, gauge

**Export Options:**
- CSV, TXT, and **PowerPoint** (3-slide executive deck) ⭐

**Launch:** `streamlit run src/dashboard.py`

### KPI/KRI Metrics (Available in Both Dashboards)

1. Total Inherent vs Residual Loss
2. Mitigation Effectiveness %
3. Portfolio VaR95, VaR99
4. Top Risk Driver
5. Concentration Ratio (top 3 / total)
6. Expected Annual Loss
7. Tornado charts (dVaR) - Risk MC dashboard

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_simulate.py -v
```

### Test Coverage

**149 tests total, 100% passing** ✅

- **Risk MC Library** (70 tests): Distributions, simulation, LEC, I/O, quantification
- **Dashboard KRI** (27 tests): KPI/KRI calculations, visualizations, metrics
- **Original Dashboard** (46 tests): Monte Carlo, risk register, curves
- **Risk MC Dashboard** (6 tests): Smoke tests, imports

**Quality Checks:**
- **Deterministic with seed**: All simulations reproducible
- **Shape validation**: Output dimensions correct
- **Monotonicity**: Percentiles ordered (p99 ≥ p95 ≥ p90 ≥ p50)
- **Hand-calculated cases**: Zero frequency → zero loss
- **Distribution properties**: Mean/variance match theory
- **Parameter validation**: Invalid inputs raise errors

## 🎨 Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Run all checks
make all
```

Configuration in `pyproject.toml`:
- **Black**: Code formatting (line length 100)
- **Ruff**: Fast Python linter (E, W, F, I, B, C4, UP rules)
- **Pytest**: Test framework with coverage support

## 📈 Methodology

### Frequency/Severity Approach

For each risk and simulation:

1. **Sample frequency**: Draw annual event count from frequency distribution
2. **Sample severities**: For each event, draw loss amount from severity distribution
3. **Apply controls**: Multiply by `ResidualFactor × (1 - ControlEffectiveness)`
4. **Aggregate**: Sum to get annual loss for this risk
5. **Portfolio**: Sum all risks to get total portfolio loss

### Risk Metrics

- **VaR (Value at Risk)**: Loss threshold at given confidence level (e.g., 95th percentile)
- **TVaR (Tail VaR)**: Mean loss in tail beyond VaR (aka Expected Shortfall, CVaR)
- **dVaR (Marginal VaR)**: Risk's contribution to portfolio tail events
  - Calculated as mean loss contribution in tail scenarios (portfolio loss ≥ VaR)

### Loss Exceedance Curve (LEC)

Shows probability of annual loss exceeding various thresholds:
- **X-axis**: Loss threshold ($)
- **Y-axis**: Exceedance probability (%)
- **Interpretation**: For threshold $X, curve shows P(Loss ≥ $X)

## 📊 Risk Register Integration

### Input CSV Format

Your risk register should be a CSV/Excel file with these columns:

```csv
RiskID,Category,Description,FrequencyModel,FreqParam1,FreqParam2,SeverityModel,SevParam1,SevParam2,SevParam3,ControlEffectiveness,ResidualFactor
R01,Cyber,Phishing attack,Poisson,2.0,,Lognormal,12.0,0.8,,0.3,0.7
R02,Ops,Data center outage,NegBin,2,0.3,PERT,50000,1500000,4000000,0.5,0.8
R03,Financial,Market volatility,Poisson,3.0,,Lognormal,11.5,0.6,,0.0,1.0
```

**Required Columns:**
- `RiskID`: Unique risk identifier
- `FrequencyModel`: 'Poisson' or 'NegBin'
- `FreqParam1`: λ (Poisson) or r (NegBin)
- `SeverityModel`: 'Lognormal', 'Normal', or 'PERT'
- `SevParam1`, `SevParam2`: Distribution parameters

**Optional Columns:**
- `FreqParam2`: p for NegBin (required for NegBin)
- `SevParam3`: max for PERT (required for PERT)
- `ControlEffectiveness`: 0-1, default 0
- `ResidualFactor`: 0-1, default 1

### Quantify Your Register

```python
from risk_mc import load_register, quantify_register

# Load register
register = load_register("my_risks.csv")

# Quantify (runs Monte Carlo simulation)
quantified = quantify_register(
    register, 
    n_sims=50_000,  # Number of simulations
    seed=42          # For reproducibility
)

# View results
print(quantified)
```

### Output Format

`quantify_register()` returns a DataFrame with all original columns plus:

| Column | Description |
|--------|-------------|
| `SimMean` | Mean annual loss |
| `SimMedian` | Median annual loss |
| `SimStd` | Standard deviation |
| `SimP90` | 90th percentile |
| `SimP95` | 95th percentile |
| `SimP99` | 99th percentile |
| `SimVaR95` | Value at Risk (95%) |
| `SimVaR99` | Value at Risk (99%) |
| `SimTVaR95` | Tail VaR (95%) / Expected Shortfall |
| `SimTVaR99` | Tail VaR (99%) / Expected Shortfall |

**Example Output:**

```
RiskID  Category  SimMean     SimVaR95    SimTVaR95
R01     Cyber     221,043     630,359     841,694
R02     Cyber     449,181     2,297,463   4,531,480
R03     Ops       479,453     1,244,722   1,505,673
...
PORTFOLIO_TOTAL   2,292,100   4,480,423   6,649,507
```

The last row (`PORTFOLIO_TOTAL`) shows aggregate portfolio metrics.

### Save Results

```python
# Save to CSV
quantified.to_csv("quantified_register.csv", index=False)

# Save to Excel
quantified.to_excel("quantified_register.xlsx", index=False)
```

## 📚 API Reference

### Risk Register

```python
load_register(path) -> pd.DataFrame
  # Load risk register from CSV or Excel
  # Validates schema and coerces data types
  
quantify_register(register_df, n_sims=50_000, seed=None) -> pd.DataFrame
  # Run Monte Carlo simulation on risk register
  # Returns DataFrame with all metrics for each risk
  # Includes PORTFOLIO_TOTAL row
```

### Simulation

```python
simulate_annual_loss(risk_row, n_sims=50_000, seed=None) -> np.ndarray
simulate_portfolio(register_df, n_sims=50_000, seed=None) -> pd.DataFrame
```

### Metrics

```python
summary(losses) -> pd.Series  # mean, median, std, percentiles, VaR, TVaR
var(losses, confidence=0.95) -> float
tvar(losses, confidence=0.95) -> float
marginal_contribution_to_var(by_risk_losses, portfolio_losses, q=0.95) -> Dict
tornado_data(register_df, portfolio_losses, by_risk_losses, q=0.95, top_n=10) -> pd.DataFrame
```

### Loss Exceedance Curve

```python
lec_points(losses, probs=None, n_points=100) -> pd.DataFrame
exceedance_prob(losses, loss_threshold) -> float
return_period(losses, loss_threshold) -> float
plot_lec_matplotlib(losses, n_points=100, mark_percentiles=[0.95, 0.99]) -> plt.Figure
plot_lec_plotly(losses, n_points=100, mark_percentiles=[0.95, 0.99]) -> go.Figure
```

### Plots

```python
loss_histogram(losses, bins=50, kde=True, mark_percentiles=[0.95, 0.99]) -> plt.Figure
plot_tornado(tornado_df, metric="mean_loss") -> plt.Figure
plot_dual_tornado(tornado_df) -> plt.Figure
```

### I/O

```python
load_register(path) -> pd.DataFrame
save_quantified_register(register_df, portfolio_df, out_path)
```

## 🔧 Configuration

Default simulation parameters:
- **n_sims**: 50,000 (adjustable 1,000 - 1,000,000+)
- **seed**: None (set for reproducibility)
- **VaR confidence**: 95% and 99%
- **LEC points**: 100

## 💡 Examples

See `scripts/demo_portfolio.py` for a complete example that:
- Loads 10-risk portfolio
- Runs 50,000 simulations
- Prints detailed metrics
- Generates 5 visualizations
- Saves quantified register

Output includes:
- Portfolio loss histogram (`artifacts/portfolio_hist.png`)
- Loss Exceedance Curve (`artifacts/lec.png`)
- Tornado chart by mean loss (`artifacts/tornado.png`)
- Tornado chart by dVaR (`artifacts/tornado_dvar.png`)
- Dual comparison chart (`artifacts/tornado_dual.png`)
- Quantified register (`artifacts/quantified_register.csv`)

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make all` to check formatting, linting, and tests
5. Submit a pull request

## 📞 Support

For issues or questions:
- Review the examples in `scripts/demo_portfolio.py`
- Check test files for usage patterns
- Run `make test` to verify installation

## 🎓 References

- **Frequency/Severity Modeling**: Standard actuarial approach for operational risk
- **VaR/TVaR**: Basel II/III regulatory risk measures
- **Loss Exceedance Curves**: Common in insurance and reinsurance
- **PERT Distribution**: Project management three-point estimates

---

**Built for enterprise risk quantification with Python, NumPy, Pandas, and SciPy.**
