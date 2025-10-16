# DQN Stock Trading Application

A Deep Q-Network (DQN) stock trading application that fetches stock data from multiple sources and generates technical indicators for algorithmic trading analysis.

## Features

- **Multiple Data Sources**: Yahoo Finance, MySQL Database, and Alpaca Markets API
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, and more
- **Flexible Intervals**: 1m, 5m, 15m, 30m, 1h, 1d support across data sources
- **Modular Architecture**: Abstract data source pattern for easy extensibility
- **Comprehensive Testing**: Unit tests for all data sources
- **Example Scripts**: Ready-to-use examples for data fetching and analysis

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd dqn-stock

# Install dependencies
uv sync
```

### Environment Setup

Copy `.env.example` to `.env` and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```env
# Database Configuration (optional)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Alpaca Markets API (optional)
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### Basic Usage

```python
from data_source import YFinanceDataSource, AlpacaDataSource
from indicators import generate_technical_indicators

# Use Yahoo Finance (no API key required)
yf_source = YFinanceDataSource()
data = yf_source.fetch_one_day_data("AAPL", "2024-01-15", "5m")

# Use Alpaca Markets (API key required)
alpaca_source = AlpacaDataSource()
data = alpaca_source.fetch_one_day_data("AAPL", "2024-01-15", "1m")

# Generate technical indicators
df_with_indicators = generate_technical_indicators(data)
```

## Data Sources

### 1. Yahoo Finance (`YFinanceDataSource`)
- **Free**: No API key required
- **Intervals**: 1m, 2m, 5m, 15m, 30m, 1h, 1d
- **Limitations**: Intraday data limited to last 60 days
- **Best for**: Testing, development, and basic analysis

### 2. Alpaca Markets (`AlpacaDataSource`)
- **Professional**: Requires API credentials
- **Intervals**: 1m, 2m, 5m, 15m, 30m, 1h, 1d, 1W, 1M
- **Features**: Real-time quotes, extended historical data
- **Best for**: Production trading applications

### 3. Database (`DatabaseDataSource`)
- **Local**: MySQL database storage
- **Intervals**: Any interval with resampling support
- **Features**: Custom data storage and retrieval
- **Best for**: Backtesting with custom datasets

## Technical Indicators

Powered by the `stockstats` library with support for:

- **Moving Averages**: SMA, EMA (5, 10, 20, 50 periods)
- **Momentum**: RSI (6, 14 periods), Williams %R, CCI
- **Trend**: MACD, Bollinger Bands, ADX
- **Volume**: On Balance Volume (OBV)
- **Volatility**: Average True Range (ATR)

```python
# Generate common indicators
df_with_indicators = generate_technical_indicators(data)

# Generate custom indicators
df_custom = generate_custom_indicators(
    data,
    sma_periods=[10, 20, 50],
    rsi_periods=[14, 21]
)
```

## Examples

Run the comprehensive data fetching example:

```bash
python examples/fetch_historical_data.py
```

This example demonstrates:
- Single-day data fetching with multiple intervals
- Multi-symbol performance comparison
- Technical indicator integration
- Error handling and data validation

## Testing

Run the complete test suite:

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific data source tests
python -m unittest tests.test_yfinance -v
python -m unittest tests.test_alpaca -v
```
