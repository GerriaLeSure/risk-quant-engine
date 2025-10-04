# ⚡ Quick Start Guide - Enterprise Risk Quantification

## 🎯 Two Systems Available

### Option 1: Streamlit Dashboard (Interactive UI)
```bash
streamlit run src/dashboard.py
# Opens browser at http://localhost:8501
```

### Option 2: Risk MC Library (Python API)
```bash
python scripts/demo_portfolio.py
# Generates 6 artifacts in artifacts/
```

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## 🚀 Risk MC Library (Recommended for Analysis)

### 1. Basic Simulation

```python
from risk_mc import load_register, simulate_portfolio, summary

# Load risk register
register = load_register("data/sample_risk_register.csv")

# Run 50,000 simulations
results = simulate_portfolio(register, n_sims=50_000, seed=42)

# Get portfolio metrics
portfolio_losses = results["portfolio_loss"].values
stats = summary(portfolio_losses)

print(f"Expected Loss: ${stats['mean']:,.0f}")
print(f"95% VaR: ${stats['var_95']:,.0f}")
print(f"99% TVaR: ${stats['tvar_99']:,.0f}")
```

### 2. Loss Exceedance Curve

```python
from risk_mc import lec_points
from risk_mc.lec import plot_lec_matplotlib

# Calculate LEC
lec_df = lec_points(portfolio_losses, probs=[0.5, 0.2, 0.1, 0.05, 0.01])
print(lec_df)

# Plot
fig = plot_lec_matplotlib(portfolio_losses, mark_percentiles=[0.95, 0.99])
fig.savefig("lec.png")
```

### 3. Sensitivity Analysis (Tornado Chart)

```python
from risk_mc.metrics import tornado_data
from risk_mc.plots import plot_tornado

# Extract individual risks
by_risk_losses = {}
for col in results.columns:
    if col.startswith("by_risk:"):
        risk_id = col.replace("by_risk:", "")
        by_risk_losses[risk_id] = results[col].values

# Generate tornado data
tornado_df = tornado_data(
    register, 
    portfolio_losses, 
    by_risk_losses, 
    q=0.95, 
    top_n=10
)

# Plot
fig = plot_tornado(tornado_df, metric="mean_loss")
fig.savefig("tornado.png")
```

---

## 🌐 Streamlit Dashboard

### Features
1. **Risk Register Tab** - Upload CSV/Excel, view heat maps
2. **Monte Carlo Tab** - Run simulations, view results
3. **LEC Tab** - Interactive Loss Exceedance Curves
4. **KPI Dashboard** - Risk trends, inherent vs residual

### Usage
1. Start: `streamlit run src/dashboard.py`
2. Load sample data or upload your own
3. Run simulation (adjust iterations)
4. Export results

---

## 📊 Sample Risk Register Format

```csv
RiskID,Category,Description,FrequencyModel,FreqParam1,FreqParam2,SeverityModel,SevParam1,SevParam2,SevParam3,ControlEffectiveness,ResidualFactor
R01,Cyber,Phishing attack,Poisson,2.0,,Lognormal,12.0,0.8,,0.3,0.7
R02,Operational,Supply chain,Poisson,1.5,,Normal,500000,150000,,0.2,0.8
R03,Financial,Market loss,Poisson,4.0,,Lognormal,11.5,0.6,,0.0,1.0
```

**Required Columns:**
- `RiskID`, `FrequencyModel`, `FreqParam1`, `SeverityModel`, `SevParam1`, `SevParam2`

**Optional Columns:**
- `FreqParam2` (for NegBin), `SevParam3` (for PERT)
- `ControlEffectiveness`, `ResidualFactor` (defaults: 0, 1)

---

## 🧪 Testing

```bash
# Risk MC tests (105 tests)
pytest tests/test_distributions.py tests/test_simulate.py tests/test_lec.py tests/test_io.py -v

# Streamlit tests (46 tests)
pytest tests/test_monte_carlo.py tests/test_risk_register.py tests/test_curves.py -v

# All tests
pytest tests/ -v
```

---

## 🛠️ Makefile Commands (Risk MC)

```bash
make install      # Install dependencies
make test         # Run tests
make lint         # Run ruff linter
make format       # Format with black
make run-demo     # Run full demo
make clean        # Clean artifacts
make all          # Format, lint, test, demo
```

---

## 📈 Key Metrics Explained

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **Mean** | Average annual loss | Expected value |
| **Median** | 50th percentile | Typical year |
| **VaR 95%** | 95th percentile | 1-in-20 year loss |
| **VaR 99%** | 99th percentile | 1-in-100 year loss |
| **TVaR 95%** | Mean beyond VaR | Tail risk average |
| **dVaR** | Marginal contribution | Risk's tail impact |

---

## 📁 Output Files

### Risk MC Demo Generates:
- `artifacts/portfolio_hist.png` - Loss distribution
- `artifacts/lec.png` - Loss Exceedance Curve
- `artifacts/tornado.png` - Mean contributors
- `artifacts/tornado_dvar.png` - Tail contributors
- `artifacts/tornado_dual.png` - Comparison
- `artifacts/quantified_register.csv` - Results data

### Streamlit Exports:
- Quantified risk register (CSV)
- Executive summary (TXT)

---

## 🎓 Distribution Guide

### Frequency (Event Counts)
- **Poisson(λ)**: Standard, λ = mean events/year
- **NegBin(r, p)**: Overdispersed, r = successes, p = probability

### Severity (Loss Amounts)
- **Lognormal(μ, σ)**: μ, σ on log scale, right-skewed
- **Normal(μ, σ)**: μ = mean, σ = std, truncated at 0
- **PERT(min, mode, max)**: Three-point estimate

---

## 🔗 Quick Links

- **Streamlit README**: `README.md` (original dashboard docs)
- **Risk MC Guide**: `RISK_MC_SUMMARY.md` (library details)
- **Full Summary**: `FINAL_PROJECT_SUMMARY.md` (complete overview)
- **Sample Data**: `data/sample_risk_register.csv`
- **Demo Script**: `scripts/demo_portfolio.py`

---

## ⚠️ Common Issues

**Import errors?**
```bash
export PYTHONPATH=/workspace:$PYTHONPATH
```

**Missing dependencies?**
```bash
pip install -r requirements.txt
```

**Old test cache?**
```bash
make clean
pytest tests/ -v
```

---

## 💡 Best Practices

1. **Always use seeds** for reproducibility: `seed=42`
2. **Start with 10K simulations** for fast iteration
3. **Use 50K+ simulations** for final analysis
4. **Validate input data** before running
5. **Check test results** match expectations
6. **Export artifacts** for documentation

---

## 🎯 Typical Workflow

1. **Prepare Data**: Create/upload risk register CSV
2. **Load & Validate**: Use `load_register()` or Streamlit UI
3. **Run Simulation**: 50,000 iterations recommended
4. **Analyze Metrics**: Review VaR, TVaR, distributions
5. **Sensitivity Analysis**: Identify top contributors (dVaR)
6. **Visualize**: Generate charts (LEC, tornado, histogram)
7. **Export**: Save quantified register and charts
8. **Present**: Use Streamlit for interactive exploration

---

## 📞 Support

**Documentation:**
- API docstrings: `help(risk_mc.simulate_portfolio)`
- Examples: `scripts/demo_portfolio.py`
- Tests: `tests/` directory

**Verification:**
- Run demo: `python scripts/demo_portfolio.py`
- Run tests: `pytest tests/ -v`
- Check artifacts: `ls -lh artifacts/`

---

**Choose your tool:**
- 🎨 **Interactive?** → Streamlit Dashboard
- 🔬 **Analytical?** → Risk MC Library
- 🏢 **Enterprise?** → Both!

*Ready to quantify your risks in minutes!* 🚀
