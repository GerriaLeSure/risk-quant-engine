# Risk Register CSV Schema

## Overview

This directory contains sample risk register data for the Enterprise Risk Quantification Engine. The risk register uses a frequency/severity modeling approach where each risk is characterized by:
- Event frequency (how often events occur)
- Event severity (loss amount per event)
- Control effectiveness (risk mitigation)

## File Format

**File**: `sample_risk_register.csv`
**Format**: CSV with comma delimiters
**Encoding**: UTF-8

## Schema Definition

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `RiskID` | String | Unique risk identifier | R1, R2, R3 |
| `Category` | String | Risk category/domain | Cyber, Operations, Financial |
| `Description` | String | Brief risk description | "Phishing attack" |
| `FrequencyModel` | String | Event frequency distribution | Poisson, NegBin |
| `FreqParam1` | Float | First frequency parameter | λ (Poisson), r (NegBin) |
| `FreqParam2` | Float | Second frequency parameter (optional) | p (NegBin only) |
| `SeverityModel` | String | Loss severity distribution | Lognormal, Normal, PERT |
| `SevParam1` | Float | First severity parameter | μ (Lognormal/Normal), min (PERT) |
| `SevParam2` | Float | Second severity parameter | σ (Lognormal/Normal), mode (PERT) |
| `SevParam3` | Float | Third severity parameter (optional) | max (PERT only) |
| `ControlEffectiveness` | Float | Control effectiveness (0-1) | 0.6 = 60% effective |
| `ResidualFactor` | Float | Residual risk multiplier (0-1) | 0.7 = 30% reduction |

### Distribution Parameters

#### Frequency Distributions

**Poisson(λ)**
- `FrequencyModel`: "Poisson"
- `FreqParam1`: λ (lambda) - mean event rate per year
- `FreqParam2`: Leave empty
- Example: `Poisson,2,` means 2 events/year on average

**Negative Binomial(r, p)**
- `FrequencyModel`: "NegBin"
- `FreqParam1`: r - number of successes parameter
- `FreqParam2`: p - success probability (0-1)
- Example: `NegBin,3,0.6` for overdispersed events

#### Severity Distributions

**Lognormal(μ, σ)**
- `SeverityModel`: "Lognormal"
- `SevParam1`: μ (mu) - mean on log scale
- `SevParam2`: σ (sigma) - std deviation on log scale
- `SevParam3`: Leave empty
- Example: `Lognormal,12.0,0.9,` 
- Note: Use `log(median_loss)` for μ

**Normal(μ, σ)**
- `SeverityModel`: "Normal"
- `SevParam1`: μ (mu) - mean loss amount
- `SevParam2`: σ (sigma) - standard deviation
- `SevParam3`: Leave empty
- Example: `Normal,20000,12000,`
- Note: Truncated at 0 (no negative losses)

**PERT(min, mode, max)**
- `SeverityModel`: "PERT"
- `SevParam1`: min - minimum loss amount
- `SevParam2`: mode - most likely loss amount
- `SevParam3`: max - maximum loss amount
- Example: `PERT,50000,1500000,4000000`
- Note: Three-point estimate using Beta distribution

### Control Parameters

**ControlEffectiveness** (0-1)
- Represents the effectiveness of implemented controls
- 0 = no control effectiveness
- 1 = 100% effective (eliminates risk)
- Applied as: `loss × (1 - ControlEffectiveness)`

**ResidualFactor** (0-1)
- Multiplier for residual risk after controls
- 1 = no reduction
- 0.7 = 30% reduction
- Applied as: `loss × ResidualFactor`

**Combined Effect**:
```
Effective Loss = Base Loss × ResidualFactor × (1 - ControlEffectiveness)
```

## Example CSV

```csv
RiskID,Category,Description,FrequencyModel,FreqParam1,FreqParam2,SeverityModel,SevParam1,SevParam2,SevParam3,ControlEffectiveness,ResidualFactor
R1,Cyber,Phishing attack,Poisson,2,,Lognormal,12.0,0.9,,0.6,0.7
R2,Cyber,Ransomware event,Poisson,0.3,,Lognormal,14.5,1.1,,0.4,0.6
R3,Operations,Data center outage,NegBin,2,0.3,PERT,50000,1500000,4000000,0.5,0.8
R4,Fraud,Account takeover,Poisson,1.2,,Normal,20000,12000,,0.5,0.8
R5,ThirdParty,Vendor breach,Poisson,0.6,,Lognormal,13.4,1.0,,0.5,0.75
R6,Legal,Regulatory fine,Poisson,0.2,,PERT,200000,1000000,5000000,0.3,0.85
R7,Market,Commodity price spike,NegBin,3,0.6,Normal,150000,80000,,0.3,0.9
R8,Operations,Payment system outage,Poisson,0.9,,Lognormal,12.8,0.8,,0.6,0.8
R9,Reputation,PR crisis,Poisson,0.15,,PERT,100000,800000,3000000,0.4,0.85
R10,Physical,Facility incident,Poisson,0.7,,Normal,35000,20000,,0.5,0.85
```

## Sample Data Explained

### R1: Phishing Attack (Cyber)
- **Frequency**: Poisson(2) - 2 incidents per year
- **Severity**: Lognormal(12.0, 0.9) - $163k median, high variability
- **Controls**: 60% effective, 70% residual → 28% effective loss
- **Interpretation**: Frequent but well-controlled cyber risk

### R3: Data Center Outage (Operations)
- **Frequency**: NegBin(2, 0.3) - ~4.7 events/year (overdispersed)
- **Severity**: PERT(50k, 1.5M, 4M) - Three-point estimate
- **Controls**: 50% effective, 80% residual → 40% effective loss
- **Interpretation**: High-frequency operational risk with large potential losses

### R6: Regulatory Fine (Legal)
- **Frequency**: Poisson(0.2) - Once every 5 years
- **Severity**: PERT(200k, 1M, 5M) - Wide range of potential fines
- **Controls**: 30% effective, 85% residual → 59.5% effective loss
- **Interpretation**: Rare but severe compliance risk

## Usage

### Load and Validate
```python
from risk_mc import load_register

# Load with automatic validation
register = load_register("data/sample_risk_register.csv")

# Inspect
print(f"Loaded {len(register)} risks")
print(register[["RiskID", "Category", "FrequencyModel", "SeverityModel"]])
```

### Quantify Risks
```python
from risk_mc import quantify_register

# Run Monte Carlo simulation
quantified = quantify_register(register, n_sims=50_000, seed=42)

# View results
print(quantified[["RiskID", "SimMean", "SimVaR95", "SimTVaR95"]])
```

## Creating Your Own Register

### Step 1: Define Risks
List all material risks with:
- Unique IDs
- Clear categories
- Descriptive names

### Step 2: Select Distributions

**For Frequency**:
- **Poisson**: Regular, independent events
- **NegBin**: Clustered or overdispersed events

**For Severity**:
- **Lognormal**: Right-skewed, no upper limit (most operational risks)
- **Normal**: Symmetric, bounded by nature (truncated at 0)
- **PERT**: Expert judgment with min/mode/max estimates

### Step 3: Parameterize

**Tips**:
- For Lognormal: Use `μ = log(median_loss)`, σ controls spread
- For Normal: Use realistic mean and std dev
- For PERT: Get min/mode/max from SMEs or historical data
- For Poisson: Use historical frequency data
- For NegBin: Use when variance > mean (overdispersion)

### Step 4: Model Controls
- **ControlEffectiveness**: Based on control maturity/effectiveness
- **ResidualFactor**: Net effect of all risk responses
- Combined: Should reflect realistic post-control risk profile

## Validation Rules

The `load_register()` function enforces:

1. **Required Columns**: All 12 columns must be present
2. **Frequency Models**: Only "Poisson" or "NegBin" allowed
3. **Severity Models**: Only "Lognormal", "Normal", or "PERT" allowed
4. **Parameter Ranges**:
   - ControlEffectiveness ∈ [0, 1]
   - ResidualFactor ∈ [0, 1]
   - Frequency parameters > 0
   - Severity parameters appropriate for distribution
5. **Required Parameters**:
   - NegBin requires FreqParam2
   - PERT requires SevParam3

## Best Practices

1. **Start Simple**: Begin with 5-10 key risks
2. **Use Historical Data**: Parameterize from actual incidents when available
3. **Get SME Input**: Use expert judgment for rare events
4. **Validate Results**: Check if simulated losses align with expectations
5. **Iterate**: Refine parameters based on validation results
6. **Document Assumptions**: Keep notes on parameter sources

## References

- **Lognormal Parameters**: If median = M and P95/M ≈ k, then σ ≈ ln(k)/1.645
- **Poisson vs NegBin**: Use NegBin when variance > mean
- **PERT λ**: Standard PERT uses λ=4; adjust for confidence in mode
- **Control Modeling**: Distinguish inherent (no controls) from residual (with controls)

---

**For questions or issues with the schema, please refer to the project README or documentation.**
