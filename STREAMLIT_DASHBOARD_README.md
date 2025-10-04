# 🎨 Streamlit Dashboard - Quick Reference

## Launch Dashboard

```bash
streamlit run src/risk_mc_dashboard.py
```

**Or use shortcuts:**
```bash
make run-dashboard              # Using Makefile
./scripts/run_dashboard.sh      # Using shell script
```

**Access at:** http://localhost:8501

---

## 5-Minute Quickstart

### Step 1: Launch (10 seconds)
```bash
make run-dashboard
```
Browser opens automatically to http://localhost:8501

### Step 2: Load Data (5 seconds)
- Click **"Load Sample Register"** button in sidebar
- See "✅ Loaded 10 sample risks" confirmation
- View 10 risks in table

### Step 3: Quantify (3 seconds)
- Keep default 50,000 simulations
- Click **"🎲 Run Quantification"** button
- See "✅ Quantification complete!" message
- View results table with VaR/TVaR metrics

### Step 4: Explore (2 minutes)
- **Monte Carlo Tab**: Select R01, run simulation, view histogram
- **LEC Tab**: See Loss Exceedance Curve with markers
- **KPI Tab**: Review portfolio dashboards
- **Export Tab**: Download CSV and summary

### Step 5: Export (10 seconds)
- Go to **Export Results** tab
- Click **"📥 Download CSV"**
- Click **"Generate Executive Summary"**
- Save files to your computer

**Total time: 5 minutes** ⏱️

---

## Tab Guide

### 📋 Tab 1: Risk Register

**What it does**: Load, view, and quantify your risk register

**How to use:**
1. Upload CSV/Excel OR click "Load Sample Register"
2. Review loaded risks in table
3. Adjust simulation count (default: 50,000)
4. Click "Run Quantification"
5. View results with SimMean, SimVaR95, SimTVaR95, etc.

**Key metrics shown:**
- Total risks, categories, distribution models
- Complete quantified register table

---

### 🎲 Tab 2: Monte Carlo Simulation

**What it does**: Deep-dive analysis of individual risks

**How to use:**
1. Select risk from dropdown (e.g., "R01")
2. Review risk details (category, parameters, controls)
3. Adjust simulation slider (1K-100K)
4. Click "Run Simulation"
5. View interactive histogram with VaR markers

**Key metrics shown:**
- Mean Loss, 95% VaR, 99% VaR, 95% TVaR
- Interactive histogram with zoom/pan
- Detailed statistics (expandable)

---

### 📈 Tab 3: Loss Exceedance Curve

**What it does**: Portfolio-level tail risk analysis

**How to use:**
1. Tab auto-generates LEC from quantified data
2. Hover over chart to see exact values
3. Review key metrics cards
4. Check exceedance probability table

**Key insights:**
- Expected Loss (mean annual)
- 95% VaR (1-in-20 year loss)
- 99% VaR (1-in-100 year loss)
- Return periods for various thresholds

**Chart shows:**
- X-axis: Loss threshold ($)
- Y-axis: Probability of exceeding
- Red markers: 95% and 99% percentiles

---

### 📊 Tab 4: KPI/KRI Dashboard

**What it does**: Portfolio overview and risk analytics

**How to use:**
1. Review portfolio overview metrics at top
2. Scroll through visualizations
3. Identify top risk exposures
4. Analyze category breakdown

**Visualizations:**
1. **Top 5 Risk Exposures** - Horizontal bar chart
2. **Risk Distribution by Category** - Pie chart with percentages
3. **Inherent vs Residual** - Control effectiveness comparison
4. **VaR Distribution** - Box plot showing spread

**Key insights:**
- Which risks contribute most to expected loss?
- How are risks distributed across categories?
- How effective are current controls?
- What's the VaR variability?

---

### 📤 Tab 5: Export Results

**What it does**: Download results and generate reports

**How to use:**
1. Click "📥 Download CSV" for quantified register
2. Click "Generate Executive Summary" for report
3. Review summary in text area
4. Click "📥 Download Summary (TXT)"

**Exports include:**
- **CSV**: All original data + quantified metrics
- **Summary**: Portfolio overview, top risks, recommendations
- **Filename**: Timestamped (e.g., `quantified_register_20251003_235959.csv`)

---

## 💡 Pro Tips

### Performance
- **Fast iteration**: Use 10K simulations
- **Final analysis**: Use 50K simulations
- **High precision**: Use 100K simulations (slower)

### Data Quality
- Ensure CSV has all 11 required columns (see data/SCHEMA.md)
- Use `blank_risk_register_template.csv` as a starting point
- Validate numeric fields are numbers
- Check ControlEffectiveness and ResidualFactor are in [0, 1]
- Reference `sample_risk_register.csv` for examples

### Analysis Workflow
1. Start with Risk Register tab (load and quantify)
2. Deep-dive in Monte Carlo tab (understand individual risks)
3. Portfolio view in LEC tab (tail risk)
4. KPIs for executive summary
5. Export for reporting

### Troubleshooting
- **"Please load risk register first"**: Go to Risk Register tab, load data
- **"Please run quantification first"**: Click "Run Quantification" button
- **Slow performance**: Reduce simulation count or number of risks
- **Import error**: Run `pip install -r requirements.txt`

---

## 🎓 Understanding the Charts

### Histogram (Monte Carlo Tab)
- Shows distribution of annual losses
- Red dashed lines = VaR thresholds
- Most likely outcomes in the peak
- Tail = rare but severe losses

### Loss Exceedance Curve (LEC Tab)
- Higher on Y-axis = more probable
- Further right on X-axis = larger loss
- Curve shows P(Loss ≥ Threshold)
- Use for: "What's the probability we lose more than $X?"

### Tornado Chart (KPI Tab)
- Longer bars = bigger contributors
- Compare mean loss vs tail contribution
- Identify mitigation priorities

### Pie Chart (KPI Tab)
- Category breakdown by expected loss
- Identify concentration risk
- Portfolio diversification insights

---

## 📊 Sample Output

After running quantification on 10 sample risks:

**Portfolio Metrics:**
- Expected Annual Loss: **$2,292,100**
- 95% VaR: **$4,480,423**
- 99% VaR: **$7,532,116**
- 95% TVaR: **$6,649,507**

**Top Contributors:**
1. R03 (Operations): $479,453 (20.9%)
2. R05 (Financial): $474,533 (20.7%)
3. R02 (Cyber): $449,181 (19.6%)

**Interpretation:**
- Budget $2.3M annually for risk reserves
- Allocate $4.5M capital for 95% confidence
- Focus mitigation on R03 (dominates portfolio)

---

## 🔗 Integration with Python API

The dashboard uses these Risk MC functions internally:

```python
from risk_mc import (
    load_register,
    quantify_register,
    simulate_annual_loss,
    lec_points
)
```

You can also use the API directly for automation:

```python
# Same analysis, via Python
register = load_register("data/sample_risk_register.csv")
quantified = quantify_register(register, n_sims=50_000, seed=42)
quantified.to_csv("results.csv")
```

Dashboard = Interactive UI for the same powerful engine!

---

## 📞 Support

**Getting Help:**
1. Review this guide
2. Check docs/DASHBOARD_GUIDE.md (detailed)
3. Run tests: `pytest tests/test_dashboard.py -v`
4. Try sample data first before uploading custom data

**Common Questions:**

**Q: Can I use my own risk register?**
A: Yes! Upload CSV/Excel with required columns (see data/SCHEMA.md)

**Q: How many simulations should I use?**
A: 50,000 is good balance. Use 10K for testing, 100K for final analysis.

**Q: What if my data doesn't load?**
A: Check the CSV format against data/SCHEMA.md. Ensure all required columns present.

**Q: Can I export charts?**
A: Plotly charts have built-in export (click camera icon). Or use Python API with `scripts/demo_portfolio.py`

---

## ✅ Checklist for First Use

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Launch dashboard: `make run-dashboard`
- [ ] Load sample data: Click "Load Sample Register"
- [ ] Run quantification: Click "Run Quantification"
- [ ] Explore Monte Carlo: Select R01, run simulation
- [ ] View LEC: Check Loss Exceedance Curve tab
- [ ] Review KPIs: See portfolio dashboards
- [ ] Export results: Download CSV and summary

**Once complete, you're ready to use with real data!**

---

**The Streamlit Dashboard makes enterprise risk quantification accessible to everyone!** 🎉

---

*For detailed documentation, see: docs/DASHBOARD_GUIDE.md*
