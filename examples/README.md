# Examples

This directory contains example scripts demonstrating how to use the DQN Stock Trading application components.

## Available Examples

### `fetch_historical_data.py`

Comprehensive example showing how to use `YFinanceDataSource.fetch_one_day_data()` method.

**Features demonstrated:**
- Basic single-day data fetching with different intervals
- Detailed trading day analysis with statistics
- Multi-symbol comparison
- Technical indicator integration
- Error handling and data validation

**Usage:**
```bash
python examples/fetch_historical_data.py
```

**Example outputs:**
- Data fetching for different time intervals (1m, 5m, 15m, 1h)
- Daily trading statistics (price changes, volume, volatility)
- Technical indicators (RSI, SMA)
- Multi-stock performance comparison

## Running Examples

Make sure you have the required dependencies installed:
```bash
uv sync
```

Then run any example:
```bash
python examples/fetch_historical_data.py
```

## Notes

- Examples use recent dates for better data availability
- Some data may not be available for weekends/holidays
- Modify symbols and dates in the scripts to test different scenarios
- Examples demonstrate both successful data fetching and error handling