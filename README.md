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

### 1. Run Demo Simulation

```bash
make run-demo
```

This will:
- Load the sample risk register (10 risks)
- Run 50,000 Monte Carlo simulations
- Generate analytics and visualizations in `artifacts/`
- Save quantified risk register with VaR/TVaR metrics

### 2. Basic Usage

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

## 📊 Risk Register Format

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

### Example Risk Register

```csv
RiskID,Category,Description,FrequencyModel,FreqParam1,FreqParam2,SeverityModel,SevParam1,SevParam2,SevParam3,ControlEffectiveness,ResidualFactor
R01,Cyber,Phishing attack,Poisson,2.0,,Lognormal,12.0,0.8,,0.3,0.7
R02,Cyber,Ransomware incident,Poisson,0.5,,Lognormal,14.0,1.2,,0.4,0.6
R03,Operational,Supply chain disruption,Poisson,1.5,,Normal,500000,150000,,0.2,0.8
R04,Operational,Equipment failure,NegBin,3.0,0.6,PERT,50000,100000,300000,0.1,0.9
```

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
│   └── sample_risk_register.csv # Sample risk data (10 risks)
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

## 📚 API Reference

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
