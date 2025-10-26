# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DQN (Deep Q-Network) stock trading application that fetches stock data from multiple sources, generates technical indicators, provides portfolio management capabilities for day trading, and includes a comprehensive backtesting framework for strategy evaluation. The project uses Python with pandas for data manipulation and implements a modular architecture with data sources, technical indicators, asset management, and strategy backtesting.

## Development Commands

### Environment Setup
```bash
# Install dependencies with uv
uv sync

# Run the main application
python main.py
```

### Environment Configuration
- Copy `.env.example` to `.env` and configure credentials
- Required environment variables for **Database**:
  - `DB_HOST` (default: localhost)
  - `DB_PORT` (default: 3306)
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
- Required environment variables for **Alpaca Markets**:
  - `ALPACA_API_KEY` - Your Alpaca API key
  - `ALPACA_SECRET_KEY` - Your Alpaca secret key
  - `ALPACA_BASE_URL` (optional, defaults to paper trading: https://paper-api.alpaca.markets)

## Architecture Overview

### Data Source Pattern
The application implements an abstract `DataSource` class with three concrete implementations:

- **YFinanceDataSource**: Fetches live data from Yahoo Finance API
- **DatabaseDataSource**: Retrieves historical data from MySQL database with resampling capabilities
- **AlpacaDataSource**: Fetches data from Alpaca Markets API (supports both live and paper trading)

All implementations provide:
- `fetch_data(symbol, start_date, end_date)` - Multi-day data retrieval
- `fetch_one_day_data(symbol, date, interval)` - Single day with specific intervals

AlpacaDataSource additionally provides:
- `get_latest_quote(symbol)` - Real-time bid/ask quote data
- `validate_symbol(symbol)` - Symbol validation
- `get_supported_intervals()` - List of supported time intervals (1m, 2m, 5m, 15m, 30m, 1h, 1d, 1W, 1M)

### Key Components

**data_source/** - Data acquisition layer
- `data_source.py` - Abstract base class defining the data source interface
- `yfinance.py` - Yahoo Finance implementation using yfinance library
- `database.py` - MySQL database implementation with SQLAlchemy and resampling logic
- `alpaca.py` - Alpaca Markets implementation using alpaca-py library

**indicators.py** - Technical indicator generation
- Uses stockstats library for technical analysis
- Provides preset and custom indicator configurations
- Includes moving averages, RSI, MACD, Bollinger Bands, stochastic oscillators

**asset_manager.py** - Portfolio and position management for day trading
- `AssetManager` class - Main portfolio manager with buy/sell execution
- `Position` class - Tracks individual stock positions with P&L
- `Transaction` class - Records trade executions
- Features:
  - Portfolio tracking (cash, positions, buying power)
  - Order execution with validation
  - Risk management (position size limits)
  - P&L calculation (realized and unrealized)
  - Transaction history logging
  - Portfolio analytics and reporting

**backtester.py** - Backtesting framework for strategy evaluation
- `Backtester` class - Main backtesting engine
- `Strategy` abstract class - Base class for custom strategies
- `BacktestResult` class - Performance metrics and analytics
- Features:
  - Historical simulation with realistic execution
  - Strategy interface for easy customization
  - Performance metrics (returns, Sharpe ratio, max drawdown, win rate)
  - Equity curve and trade history tracking
  - Integration with AssetManager for portfolio management

**strategies.py** - Pre-built trading strategies
- `BuyAndHoldStrategy` - Simple buy and hold benchmark
- `SMAStrategy` - Moving average crossover (20/50 default)
- `RSIStrategy` - RSI mean reversion (14-period default)
- `MomentumStrategy` - Momentum-based trading

**backtest_viz.py** - Visualization tools for backtest results
- Equity curve plotting
- Drawdown analysis
- Returns distribution
- Strategy comparison charts
- Trade signal visualization
- Comprehensive performance reports

**examples/** - Example scripts and usage demonstrations
- `simple_chart_example.py` - Simple OHLC chart visualization example
  - Demonstrates data fetching and visualization using mplfinance
  - Basic usage of AlpacaDataSource
- `fetch_historical_data.py` - Comprehensive examples of using YFinanceDataSource
  - Single day data fetching with multiple intervals
  - Detailed trading day analysis with technical indicators
  - Multi-symbol comparison functionality
- `asset_manager_example.py` - Asset manager usage demonstrations
  - Basic trading operations (buy/sell)
  - Integration with live market data
  - Risk management features
  - Portfolio analytics and reporting
- `backtest_example.py` - Backtesting framework demonstrations
  - Running single strategy backtests
  - Comparing multiple strategies
  - Detailed performance analysis with visualizations
  - Creating custom strategies
- `quick_test.py` - Quick test script for backtesting framework
  - Fast way to verify backtesting is working
  - Simple SMA strategy example

**tests/** - Test suite
- `test_yfinance.py` - Tests for Yahoo Finance data source
- `test_alpaca.py` - Tests for Alpaca Markets data source

### Data Flow
1. Data sources fetch OHLCV (Open, High, Low, Close, Volume) data
2. `convert_columns()` transforms Yahoo Finance MultiIndex format to simple columns
3. Technical indicators are generated using stockstats library
4. Data visualization using mplfinance for OHLC charts

### Database Schema
- Each stock symbol has its own table with columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`
- DatabaseDataSource supports interval resampling (1m, 5m, 15m, 30m, 1h, 1d)
- Uses pandas resample functionality for aggregating minute-level data

## Key Dependencies

- **Data Sources**: yfinance, alpaca-py, sqlalchemy, pymysql
- **Data Processing**: pandas, pandas-stubs, stockstats
- **Visualization**: mplfinance, matplotlib
- **Environment**: python-dotenv
- **Display**: tabulate

### Dependency Details
- `yfinance==0.2.65` - Yahoo Finance market data
- `alpaca-py>=0.29.2` - Alpaca Markets API client
- `sqlalchemy` - Database ORM for MySQL integration
- `pymysql` - MySQL database driver
- `pandas` - Data manipulation and analysis
- `stockstats` - Technical indicator generation
- `mplfinance>=0.12.10b0` - Financial charts and candlestick plotting

## Running Examples and Tests

### Running Example Scripts
```bash
# Quick test - verify backtesting framework is working
python examples/quick_test.py

# Run the comprehensive YFinance data fetching example
python examples/fetch_historical_data.py

# Run the asset manager trading example
python examples/asset_manager_example.py

# Run the backtesting examples
python examples/backtest_example.py

# Run simple chart visualization example
python examples/simple_chart_example.py
```

**quick_test.py** demonstrates:
- Quick verification that backtesting framework works
- Simple SMA strategy on AAPL
- Fast way to test installation and setup

**fetch_historical_data.py** demonstrates:
- Fetching single-day data with multiple time intervals (1m, 5m, 15m, 1h)
- Detailed trading day analysis with statistics and technical indicators
- Multi-symbol comparison for analyzing multiple stocks simultaneously

**asset_manager_example.py** demonstrates:
- Basic buy/sell operations and portfolio tracking
- Risk management and position limits
- Portfolio analytics with P&L calculations
- Integration with live market data sources

**backtest_example.py** demonstrates:
- Single strategy backtesting with performance analysis
- Comparing multiple strategies (Buy & Hold, SMA, RSI, Momentum)
- Detailed analysis with equity curves and drawdown charts
- Creating custom trading strategies

**simple_chart_example.py** demonstrates:
- Basic OHLC chart visualization with mplfinance
- Simple usage of AlpacaDataSource for fetching intraday data

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_yfinance.py
python -m pytest tests/test_alpaca.py
```

## Usage Patterns

### Choosing a Data Source

**YFinanceDataSource** - Best for:
- Quick prototyping and testing
- Free historical and intraday data
- No API registration required
- Supports most common stock symbols

**AlpacaDataSource** - Best for:
- Real-time quote data
- Paper trading integration
- Production-ready applications
- More reliable API with authentication

**DatabaseDataSource** - Best for:
- Offline analysis of pre-downloaded data
- Custom interval resampling
- High-frequency data queries
- When you've already collected historical data

### Data Source Usage Example
```python
from data_source.yfinance import YFinanceDataSource
from data_source.alpaca import AlpacaDataSource
from data_source.database import DatabaseDataSource

# Choose your data source
source = YFinanceDataSource()
# source = AlpacaDataSource()  # Requires API credentials
# source = DatabaseDataSource()  # Requires database setup

# Fetch multi-day data
df = source.fetch_data("AAPL", "2024-01-01", "2024-01-31")

# Fetch single-day intraday data
df = source.fetch_one_day_data("AAPL", "2024-01-15", "5m")
```

### Asset Manager Usage Example
```python
from asset_manager import AssetManager

# Initialize portfolio with $100,000
manager = AssetManager(
    initial_cash=100000.0,
    max_position_size=0.25,  # Max 25% per position
    commission_per_trade=0.0
)

# Execute buy order
success, msg = manager.buy("AAPL", 100, 180.50)
print(msg)  # "Bought 100 shares of AAPL @ $180.50"

# Update current prices
manager.update_prices({"AAPL": 182.00})

# Check position
position = manager.get_position("AAPL")
print(position.unrealized_pnl)  # Shows profit/loss

# Execute sell order
success, msg = manager.sell("AAPL", 50, 182.00)

# View portfolio summary
manager.print_summary()

# Get portfolio metrics
summary = manager.get_portfolio_summary()
print(f"Total P&L: ${summary['total_pnl']:.2f}")

# Get positions as DataFrame
positions_df = manager.get_positions_df()
transactions_df = manager.get_transactions_df()
```

### Backtesting Usage Example
```python
from backtester import Backtester
from strategies import SMAStrategy, RSIStrategy, BuyAndHoldStrategy
from data_source.yfinance import YFinanceDataSource
from backtest_viz import plot_equity_curve, plot_comparison

# Fetch historical data
data_source = YFinanceDataSource()
df = data_source.fetch_data("AAPL", "2024-01-01", "2024-12-01")

# Initialize backtester
backtester = Backtester(
    initial_capital=100000.0,
    commission_per_trade=1.0
)

# Create strategy
strategy = SMAStrategy(symbol="AAPL", short_window=20, long_window=50)

# Run backtest
result = backtester.run(
    strategy=strategy,
    data=df,
    symbol="AAPL",
    warmup_period=50
)

# View results
result.print_summary()

# Get metrics
metrics = result.get_metrics()
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")

# Visualize
plot_equity_curve(result)

# Compare multiple strategies
strategies = [
    BuyAndHoldStrategy("AAPL"),
    SMAStrategy("AAPL", 20, 50),
    RSIStrategy("AAPL", period=14)
]

results = [backtester.run(s, df, "AAPL", 50) for s in strategies]
plot_comparison(results)
```

## Important Notes

- The project includes data acquisition, technical indicators, portfolio management, and backtesting
- **Asset Manager** provides complete portfolio management for day trading with risk controls
- **Backtesting Framework** enables strategy evaluation with historical data
- DQN implementation is not yet present in the codebase
- Database tables are expected to exist; table creation logic is not implemented
- Error handling is implemented for data source failures with fallback messaging

### Asset Manager Features
- **Portfolio Tracking**: Real-time cash balance, positions, and buying power
- **Order Execution**: Market orders with buy/sell validation
- **Risk Management**: Position size limits (configurable % of portfolio)
- **P&L Calculation**: Tracks both realized and unrealized profit/loss
- **Transaction Logging**: Complete history of all trades
- **Analytics**: Portfolio summaries, position reports, transaction DataFrames
- **Integration Ready**: Works seamlessly with all data sources (YFinance, Alpaca, Database)

### Backtesting Features
- **Strategy Framework**: Abstract base class for creating custom strategies
- **Pre-built Strategies**: Buy & Hold, SMA Crossover, RSI, Momentum
- **Performance Metrics**: Total return, Sharpe ratio, max drawdown, win rate
- **Realistic Simulation**: Uses AssetManager for accurate portfolio management
- **Visualization Tools**: Equity curves, drawdown charts, trade analysis, strategy comparison
- **Easy Customization**: Simple interface for implementing and testing new strategies

### Data Source Specific Notes

**Alpaca Markets**:
- Free API account required (sign up at https://app.alpaca.markets/)
- Paper trading mode available for testing without real money
- API rate limits apply (check Alpaca documentation)
- Market data access may vary based on account type

**Yahoo Finance**:
- No authentication required
- Rate limits may apply for high-frequency requests
- Data is best-effort and may have slight delays
- Some symbols may have limited historical data

**Database**:
- Tables must be created manually before use
- Each symbol requires its own table with proper schema
- Recommended for storing and reusing frequently accessed data