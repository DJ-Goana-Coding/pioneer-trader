# Trading Dashboard

A minimalist trading interface with core mathematical analysis for cryptocurrency markets.

## Features

- **Market Analysis Engine**: Technical indicators (RSI, SMA crossovers)
- **5-Line Rolling Trade Feed**: Real-time trade log with win/loss tracking
- **Trade Aggression Slider**: 0-10 scale to control trading strategy
- **Market Sync Control**: Enable/disable market data synchronization
- **Clean, Intuitive UI**: Minimalist design focused on essential metrics

## Installation

1. **Clone or download this folder**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Dashboard

Start the Streamlit application:

```bash
streamlit run app.py
```

The dashboard will open in your web browser at `http://localhost:8501`

### Interface Controls

**Sidebar:**
- **Trade Aggression Level (0-10)**: Adjusts trading strategy aggressiveness
  - 0-3: Conservative
  - 4-6: Moderate
  - 7-10: Aggressive
  
- **Market Data Sync**: Toggle to enable/disable market updates

**Main Interface:**
- **Market Analysis Tab**: 
  - Enter a trading symbol (e.g., BTC/USDT)
  - Click "Analyze" to see technical indicators and signals
  - View RSI, SMA indicators, and trading signals
  
- **Trade Log Tab**:
  - View the 5 most recent trades
  - See trade statistics (wins, losses, win rate)

## Technical Analysis

The dashboard implements the following strategies:

### Indicators
- **RSI (Relative Strength Index)**: 14-period momentum indicator
- **SMA 20**: 20-period simple moving average
- **SMA 50**: 50-period simple moving average

### Signals
- **BUY Signal**: Golden Cross (SMA 20 crosses above SMA 50)
- **SELL Signal**: Death Cross (SMA 20 crosses below SMA 50)
- **NEUTRAL**: No significant crossover detected

## Data Source

This distribution uses **mock data generation** for demonstration purposes. To connect to real market data:

1. Integrate with a cryptocurrency exchange API (e.g., Binance, Coinbase)
2. Replace the `generate_mock_data()` function with real API calls
3. Add API key management and authentication

## Customization

### Adding New Indicators

Edit the `calculate_indicators()` function in `app.py`:

```python
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df.ta.rsi(length=14, append=True)
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)
    # Add your indicators here
    df.ta.macd(append=True)  # Example: MACD
    return df
```

### Modifying Trading Signals

Edit the `check_signal()` function to implement your own strategy logic.

## Requirements

- Python 3.8+
- Streamlit 1.25.0+
- pandas 2.0.0+
- pandas_ta 0.3.14b0+
- numpy 1.24.0+

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

**This software is for educational and research purposes only.**

- NOT financial advice
- NOT a recommendation to buy or sell securities
- Trading cryptocurrencies carries substantial risk
- You may lose all invested capital
- Always do your own research and consult with financial advisors

## Support

For issues or questions:
1. Check the code comments in `app.py`
2. Review pandas_ta documentation for indicator details
3. Consult Streamlit documentation for UI customizations

## Architecture

```
Trading Dashboard
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── LICENSE               # MIT License
└── README.md            # This file
```

## Quick Start Example

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py

# Open your browser to http://localhost:8501
# Enter a symbol (e.g., BTC/USDT) and click Analyze
```

---

Built with ❤️ for traders who value simplicity and mathematical rigor.
