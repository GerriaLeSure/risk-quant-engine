# 🎯 Enterprise Risk Quantification & Analytics Engine

A comprehensive Python Streamlit application for quantifying and analyzing enterprise risks using Monte Carlo simulations, Loss Exceedance Curves, and advanced risk analytics.

## 📋 Features

- **Risk Register Management**: Load and manage risk data from CSV/Excel files
- **Monte Carlo Simulation**: Run 10,000+ simulations to quantify risk impact and likelihood
- **Loss Exceedance Curves (LEC)**: Visualize probability of exceeding various loss thresholds
- **Interactive Dashboard**: 
  - Risk Register Overview with heat maps and categorization
  - Monte Carlo Simulation results with portfolio-level metrics
  - Loss Exceedance Curve visualization (Matplotlib & Plotly)
  - KPI/KRI Dashboard with risk trends and inherent vs residual risk analysis
- **Export Capabilities**: 
  - CSV export of quantified risk register
  - Executive summary report generation
- **Comprehensive Testing**: Full pytest test suite for all core modules
- **Docker Support**: Containerized deployment for easy setup

## 🏗️ Project Structure

```
.
├── src/
│   ├── monte_carlo.py      # Monte Carlo simulation engine
│   ├── risk_register.py    # Risk register management
│   ├── curves.py           # Loss Exceedance Curve generation
│   └── dashboard.py        # Streamlit dashboard UI
├── data/
│   └── sample_risk_register.csv  # Sample risk data (10 risks)
├── tests/
│   ├── test_monte_carlo.py       # Monte Carlo tests
│   ├── test_risk_register.py     # Risk register tests
│   └── test_curves.py            # LEC tests
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

## 🚀 Quick Start

### Option 1: Local Installation

#### Prerequisites
- Python 3.9 or higher
- pip package manager

#### Installation Steps

1. **Clone the repository** (or navigate to the project directory):
```bash
cd /workspace
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
streamlit run src/dashboard.py
```

5. **Access the dashboard**:
Open your browser and navigate to:
```
http://localhost:8501
```

### Option 2: Docker Deployment

#### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for advanced setups)

#### Docker Steps

1. **Build the Docker image**:
```bash
docker build -t risk-analytics-engine .
```

2. **Run the container**:
```bash
docker run -p 8501:8501 risk-analytics-engine
```

3. **Access the dashboard**:
Open your browser and navigate to:
```
http://localhost:8501
```

#### Advanced Docker Options

**Run with volume mount** (to use your own data files):
```bash
docker run -p 8501:8501 -v $(pwd)/data:/app/data risk-analytics-engine
```

**Run in detached mode**:
```bash
docker run -d -p 8501:8501 --name risk-analytics risk-analytics-engine
```

**View logs**:
```bash
docker logs -f risk-analytics
```

**Stop the container**:
```bash
docker stop risk-analytics
```

## 📊 Using the Application

### 1. Load Risk Register

**Using Sample Data:**
- Check the "Use Sample Data" checkbox in the sidebar
- Click "Load Sample Data"
- The application will load 10 example risks covering various categories

**Using Your Own Data:**
- Uncheck "Use Sample Data"
- Upload a CSV or Excel file with your risk register
- Required columns: `risk_id`, `risk_name`, `likelihood`, `impact`
- Optional columns: `category`, `owner`, `status`, `likelihood_std`, `impact_min`, `impact_most_likely`, `impact_max`

### 2. Explore Risk Register Overview

The **Risk Register** tab shows:
- Summary statistics (total risks, active risks, averages)
- Risk distribution by category (pie chart)
- Inherent vs Residual risk comparison
- Risk heat map (likelihood × impact)
- Detailed risk table with filters

### 3. Run Monte Carlo Simulations

Navigate to the **Monte Carlo Simulation** tab:
1. Select number of simulations (1,000 - 100,000)
2. Click "🚀 Run Simulation"
3. View results:
   - Portfolio-level metrics (mean, median, VaR, CVaR)
   - Loss distribution histogram
   - Risk contribution by category
   - Individual risk simulation results
   - Top 5 risks waterfall chart

### 4. Analyze Loss Exceedance Curves

The **Loss Exceedance Curve** tab displays:
- Interactive LEC plot (Plotly or Matplotlib)
- Value at Risk (VaR) and Conditional VaR (CVaR) table
- Return period analysis
- Percentile markers (P90, P95, P99)

### 5. Review KPI/KRI Dashboard

The **KPI/KRI Dashboard** tab shows:
- Key Risk Indicators (KRIs)
- Inherent vs Residual risk comparison
- Risk trends over time
- Risk appetite analysis with gauge chart
- Top risks by category

### 6. Export Results

From the sidebar:
- **Export Risk Register (CSV)**: Download quantified risk data
- **Generate Executive Summary**: Download comprehensive report

## 🧪 Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run specific test modules:
```bash
# Test Monte Carlo module
pytest tests/test_monte_carlo.py -v

# Test Risk Register module
pytest tests/test_risk_register.py -v

# Test Loss Exceedance Curves
pytest tests/test_curves.py -v
```

### View coverage report:
After running with coverage, open `htmlcov/index.html` in your browser.

## 📝 Sample Risk Register Format

Your CSV/Excel file should follow this format:

```csv
risk_id,risk_name,category,description,likelihood,impact,owner,status
R001,Cybersecurity Breach,Technology,Risk of data breach,0.35,500000,CISO,Active
R002,Supply Chain Disruption,Operational,Supplier failure,0.25,800000,COO,Active
```

**Column Definitions:**
- `risk_id`: Unique identifier (required)
- `risk_name`: Descriptive name (required)
- `category`: Risk category (optional)
- `description`: Detailed description (optional)
- `likelihood`: Probability of occurrence, 0-1 (required)
- `impact`: Financial impact in dollars (required)
- `likelihood_std`: Standard deviation of likelihood (optional, default: 0.1)
- `impact_min`: Minimum financial impact (optional, default: impact × 0.5)
- `impact_most_likely`: Most likely impact (optional, default: impact)
- `impact_max`: Maximum financial impact (optional, default: impact × 1.5)
- `owner`: Risk owner (optional)
- `status`: Risk status (optional, default: 'Active')
- `inherent_risk_score`: Score before controls (optional, calculated)
- `residual_risk_score`: Score after controls (optional, calculated)

## 🎓 Monte Carlo Simulation Methodology

The application uses a sophisticated Monte Carlo approach:

1. **Likelihood Modeling**: Beta distribution bounded between 0-1
2. **Impact Modeling**: Triangular, Normal, or Lognormal distributions
3. **Event Occurrence**: Binomial distribution based on likelihood
4. **Portfolio Aggregation**: Sum of individual risk simulations
5. **Risk Metrics**:
   - Mean/Median loss
   - Standard deviation
   - Value at Risk (VaR) at 90%, 95%, 99%
   - Conditional VaR (CVaR)
   - Loss Exceedance Curves

## 📈 Loss Exceedance Curve (LEC)

The LEC shows the probability of losses exceeding various thresholds:

- **X-axis**: Loss threshold (dollars)
- **Y-axis**: Exceedance probability (%)
- **Interpretation**: For any given loss amount, the curve shows the probability that total losses will exceed that amount

**Key Metrics:**
- **VaR (Value at Risk)**: Maximum expected loss at a given confidence level
- **CVaR (Conditional VaR)**: Average loss beyond the VaR threshold
- **Return Period**: Expected time between events of a given magnitude

## 🔧 Configuration

### Streamlit Configuration

Create a `.streamlit/config.toml` file for custom settings:

```toml
[theme]
primaryColor = "#2E86AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true
enableCORS = false
```

### Environment Variables

You can set the following environment variables:

```bash
# Streamlit configuration
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Application settings
export DEFAULT_SIMULATIONS=10000
export RANDOM_SEED=42
```

## 🐛 Troubleshooting

### Common Issues

**Issue: Module not found error**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue: Port 8501 already in use**
```bash
# Solution: Use a different port
streamlit run src/dashboard.py --server.port 8502
```

**Issue: Docker container won't start**
```bash
# Solution: Check logs
docker logs risk-analytics

# Rebuild image
docker build --no-cache -t risk-analytics-engine .
```

**Issue: CSV file won't load**
- Ensure the file has the required columns: `risk_id`, `risk_name`, `likelihood`, `impact`
- Check for proper CSV formatting (commas as delimiters)
- Verify numeric columns contain valid numbers

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest tests/ -v`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualizations powered by [Plotly](https://plotly.com/) and [Matplotlib](https://matplotlib.org/)
- Statistical computations using [NumPy](https://numpy.org/) and [SciPy](https://scipy.org/)

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

### v1.0.0 (2025-10-03)
- Initial release
- Monte Carlo simulation engine (10k+ simulations)
- Risk register management (CSV/Excel support)
- Loss Exceedance Curves with interactive visualization
- Multi-tab Streamlit dashboard
- Export functionality (CSV, text reports)
- Comprehensive test suite
- Docker support

---

**Built with ❤️ for Enterprise Risk Management**
