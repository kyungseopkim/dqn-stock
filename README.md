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
## Architecture

### Data Source Pattern

All data sources implement the abstract `DataSource` interface:

```python
class DataSource(ABC):
    @abstractmethod
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch multi-day data"""
        pass

    @abstractmethod
    def fetch_one_day_data(self, symbol: str, date: str, interval: str) -> pd.DataFrame:
        """Fetch single-day data with specific interval"""
        pass
```

### Project Structure

```
dqn_stock/
 data_source/           # Data acquisition layer
    data_source.py     # Abstract base class
    yfinance.py        # Yahoo Finance implementation
    alpaca.py          # Alpaca Markets implementation
    database.py        # MySQL database implementation
 examples/              # Usage examples
    fetch_historical_data.py
 tests/                 # Unit tests
    test_yfinance.py
    test_alpaca.py
 indicators.py          # Technical indicator generation
 main.py                # Application entry point
 CLAUDE.md              # Development guide
```

## API Credentials

### Alpaca Markets

1. Sign up at [Alpaca Markets](https://app.alpaca.markets/)
2. For paper trading: [Paper Dashboard](https://app.alpaca.markets/paper/dashboard/overview)
3. Generate API keys in your dashboard
4. Add to `.env` file

### Yahoo Finance

No API credentials required. Uses the `yfinance` library which accesses Yahoo's public data.

## Development

### Adding New Data Sources

1. Create a new class inheriting from `DataSource`
2. Implement `fetch_data()` and `fetch_one_day_data()` methods
3. Add error handling and data validation
4. Create comprehensive unit tests
5. Add to `data_source/__init__.py`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Roadmap

- [ ] DQN model implementation
- [ ] Real-time trading simulation
- [ ] Additional data sources (IEX, Polygon)
- [ ] Advanced technical indicators
- [ ] Portfolio management features
- [ ] Web-based dashboard

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the examples directory for usage patterns
- Review the test files for implementation details
