# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DQN (Deep Q-Network) stock trading application that fetches stock data from multiple sources and generates technical indicators for algorithmic trading analysis. The project uses Python with pandas for data manipulation and implements a modular data source architecture.

## Development Commands

### Environment Setup
```bash
# Install dependencies with uv
uv sync

# Run the main application
python main.py
```

### Environment Configuration
- Copy `.env.example` to `.env` and configure database credentials
- Required environment variables:
  - `DB_HOST` (default: localhost)
  - `DB_PORT` (default: 3306)
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`

## Architecture Overview

### Data Source Pattern
The application implements an abstract `DataSource` class with two concrete implementations:

- **YFinanceDataSource**: Fetches live data from Yahoo Finance API
- **DatabaseDataSource**: Retrieves historical data from MySQL database with resampling capabilities

Both implement:
- `fetch_data(symbol, start_date, end_date)` - Multi-day data retrieval
- `fetch_one_day_data(symbol, date, interval)` - Single day with specific intervals

### Key Components

**data_source/** - Data acquisition layer
- `data_source.py` - Abstract base class defining the data source interface
- `yfinance.py` - Yahoo Finance implementation using yfinance library
- `database.py` - MySQL database implementation with SQLAlchemy and resampling logic

**indicators.py** - Technical indicator generation
- Uses stockstats library for technical analysis
- Provides preset and custom indicator configurations
- Includes moving averages, RSI, MACD, Bollinger Bands, stochastic oscillators

**main.py** - Application entry point
- Demonstrates data fetching and visualization using mplfinance
- Includes utility function `convert_columns()` for MultiIndex to simple index conversion

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

- **Data Sources**: yfinance, sqlalchemy, pymysql
- **Data Processing**: pandas, stockstats
- **Visualization**: mplfinance, matplotlib
- **Environment**: python-dotenv
- **Display**: tabulate

## Important Notes

- The project currently focuses on data acquisition and technical indicator generation
- DQN implementation is not yet present in the codebase
- Database tables are expected to exist; table creation logic is not implemented
- Error handling is implemented for data source failures with fallback messaging