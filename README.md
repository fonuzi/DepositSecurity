# Banking Sector Loss Distribution Model

A sophisticated web-based financial modeling tool for advanced creditor hierarchy and loss distribution analysis.

## Features
- Interactive scenario-based loss distribution calculations
- Direct creditor name editing
- Predefined financial scenarios (FOLTF, Resolution Valuation, Liquidation Valuation)
- Dynamic visualization of loss absorption
- Responsive design for precise financial modeling

## Setup Instructions

1. Install Python 3.10 or higher
2. Install the required packages:
```bash
pip install streamlit streamlit-sortables pandas plotly
```

3. Create a `.streamlit` folder and add a `config.toml` file with the following content:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

4. Run the application:
```bash
streamlit run main.py
```

The application will be available at `http://localhost:5000`

## Project Structure
- `main.py`: Main application file
- `styles.py`: Custom CSS styles
- `utils.py`: Utility functions
- `data_models.py`: Data models and default values
- `.streamlit/config.toml`: Streamlit configuration

## Scenarios
- **Default**: Manual loss percentage adjustment
- **FOLTF**: Redistributes 20% of assets to liabilities
- **Resolution Valuation**: Redistributes 30% of assets to liabilities
- **Liquidation Valuation**: Redistributes 40% of assets to liabilities
