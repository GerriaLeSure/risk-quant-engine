# Data Directory

This directory contains risk register templates and sample data for the Risk MC Engine.

## 📄 Files

### 1. `sample_risk_register.csv`
**Purpose**: Demo and learning

- Contains 10 pre-filled example risks
- Covers multiple categories (Cyber, Operations, Financial, etc.)
- Uses various distribution types (Poisson, NegBin, Lognormal, Normal, PERT)
- Ready to load and quantify immediately

**Use this when:**
- First time using the system
- Learning how the dashboard works
- Understanding the CSV format
- Testing functionality
- Running demos

**Example:**
```bash
# In dashboard: Click "Load Sample Register"
# In Python:
from risk_mc import load_register, quantify_register
register = load_register("data/sample_risk_register.csv")
quantified = quantify_register(register, n_sims=50_000)
```

---

### 2. `blank_risk_register_template.csv`
**Purpose**: Create your own risk register

- Contains only column headers
- No data rows (empty template)
- Ready for you to fill with your organization's risks

**Use this when:**
- Building your risk register from scratch
- Importing data from another system
- Creating a custom risk portfolio
- Need a clean slate

**How to use:**
1. Open in Excel, Google Sheets, or any CSV editor
2. Fill in rows with your risks
3. Follow the column format (see SCHEMA.md for details)
4. Save as CSV
5. Upload to dashboard or load via Python API

**Example workflow:**
```bash
# 1. Copy template
cp data/blank_risk_register_template.csv my_risks.csv

# 2. Edit my_risks.csv with your data

# 3. Load and quantify
from risk_mc import load_register, quantify_register
register = load_register("my_risks.csv")
quantified = quantify_register(register, n_sims=50_000)
```

---

### 3. `SCHEMA.md`
**Purpose**: Detailed format documentation

- Complete column definitions
- Distribution parameter specifications
- Example values
- Validation rules

**Use this when:**
- Creating a new risk register
- Understanding distribution parameters
- Troubleshooting data loading errors
- Validating your CSV format

---

## 📋 Quick Reference: Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| RiskID | Text | Unique identifier | R01, CYBER-001 |
| Category | Text | Risk category | Cyber, Operations |
| Description | Text | Risk description | Phishing attack |
| FrequencyModel | Text | Poisson or NegBin | Poisson |
| FreqParam1 | Number | λ (Poisson) or r (NegBin) | 2.0 |
| FreqParam2 | Number | p (NegBin only) | 0.3 |
| SeverityModel | Text | Lognormal, Normal, or PERT | Lognormal |
| SevParam1 | Number | Distribution param 1 | 12.0 |
| SevParam2 | Number | Distribution param 2 | 0.9 |
| ControlEffectiveness | Number | 0.0 to 1.0 | 0.6 |
| ResidualFactor | Number | 0.0 to 1.0 | 0.7 |

**Note**: Leave FreqParam2 empty for Poisson. Use SevParam3 for PERT (max value).

---

## 🎯 Which Template Should I Use?

### Use `sample_risk_register.csv` if:
- ✅ First time user
- ✅ Learning the system
- ✅ Running demos
- ✅ Testing functionality
- ✅ Need examples

### Use `blank_risk_register_template.csv` if:
- ✅ Have your own risk data
- ✅ Creating from scratch
- ✅ Importing from another system
- ✅ Custom risk portfolio
- ✅ Production use

---

## 📊 Distribution Parameters Guide

### Frequency Models

**Poisson(λ)**
- `FreqParam1` = λ (average events per year)
- `FreqParam2` = (leave empty)
- Example: Poisson(2) → 2 events/year on average

**NegBin(r, p)**
- `FreqParam1` = r (number of successes)
- `FreqParam2` = p (success probability)
- Example: NegBin(2, 0.3) → over-dispersed count

### Severity Models

**Lognormal(μ, σ)**
- `SevParam1` = μ (mean of log)
- `SevParam2` = σ (std dev of log)
- Example: Lognormal(12.0, 0.9) → right-skewed loss

**Normal(μ, σ)**
- `SevParam1` = μ (mean)
- `SevParam2` = σ (std dev)
- Automatically truncated at 0
- Example: Normal(20000, 12000)

**PERT(min, mode, max)**
- `SevParam1` = min (minimum loss)
- `SevParam2` = mode (most likely loss)
- `SevParam3` = max (maximum loss)
- Example: PERT(50000, 1500000, 4000000)

---

## ✅ Validation

Your CSV must:
- ✅ Include all 11 required columns
- ✅ Have valid FrequencyModel (Poisson or NegBin)
- ✅ Have valid SeverityModel (Lognormal, Normal, or PERT)
- ✅ Use numeric values for parameters
- ✅ Keep ControlEffectiveness between 0.0 and 1.0
- ✅ Keep ResidualFactor between 0.0 and 1.0
- ✅ Have unique RiskID values

The `load_register()` function will validate your data automatically.

---

## 🚀 Getting Started

### Option 1: Dashboard (Easiest)
```bash
streamlit run src/risk_mc_dashboard.py
# Click "Load Sample Register" or upload your CSV
```

### Option 2: Python API
```python
from risk_mc import load_register, quantify_register

# Use sample data
register = load_register("data/sample_risk_register.csv")

# Or use your own data
# register = load_register("my_risks.csv")

quantified = quantify_register(register, n_sims=50_000)
print(quantified)
```

---

## 📞 Need Help?

- **Format questions**: See `SCHEMA.md`
- **Parameter help**: See distribution guides above
- **Dashboard help**: See `docs/DASHBOARD_GUIDE.md`
- **API help**: See main `README.md`

---

**Ready to quantify your enterprise risks!** 🎯
