"""
Quick test script for backtesting framework

Run this to quickly test if everything is working.
"""

from backtester import Backtester
from strategies import SMAStrategy
from data_source.yfinance import YFinanceDataSource

print("=" * 70)
print("QUICK BACKTEST TEST")
print("=" * 70)

# Fetch data
print("\n📊 Fetching AAPL data for 2024...")
data_source = YFinanceDataSource()
df = data_source.fetch_data("AAPL", "2024-01-01", "2024-12-01")

if df is None or df.empty:
    print("❌ Failed to fetch data")
    exit(1)

print(f"✅ Loaded {len(df)} days of data")
print(f"   Date range: {df.index[0]} to {df.index[-1]}")

# Run backtest
print("\n🔄 Running SMA(20/50) strategy...")
backtester = Backtester(initial_capital=100000.0, commission_per_trade=1.0)
strategy = SMAStrategy(symbol="AAPL", short_window=20, long_window=50)

result = backtester.run(strategy, df, "AAPL", warmup_period=50)

# Print results
print("\n")
result.print_summary()

print("\n✅ Backtesting framework is working correctly!")
print("\nNext steps:")
print("- Run 'python examples/backtest_example.py' for full examples")
print("- Try different strategies and symbols")
print("- View the visualizations that were generated")
