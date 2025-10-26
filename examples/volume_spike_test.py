"""
Test the BNF-inspired Volume Spike Strategy

This example demonstrates the Volume Spike Strategy which:
- Detects unusual volume activity (2x+ average volume)
- Enters on volume spikes with positive price momentum
- Confirms strength by checking if price is near bar highs
- Exits when volume normalizes or momentum reverses
- Includes 3% stop-loss protection
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtester import Backtester
from strategies import VolumeSpikeStrategy, BuyAndHoldStrategy
from data_source.yfinance import YFinanceDataSource
from backtest_viz import plot_equity_curve, plot_comparison, plot_trade_analysis

print("=" * 70)
print("BNF-INSPIRED VOLUME SPIKE STRATEGY TEST")
print("=" * 70)

# Fetch historical data
print("\n📊 Fetching historical data...")
data_source = YFinanceDataSource()
symbol = "AAPL"
start_date = "2024-01-01"
end_date = "2024-12-01"

df = data_source.fetch_data(symbol, start_date, end_date)

if df is None or df.empty:
    print("❌ Failed to fetch data")
    exit(1)

print(f"✅ Loaded {len(df)} days of data for {symbol}")
print(f"   Date range: {df.index[0]} to {df.index[-1]}")

# Initialize backtester
backtester = Backtester(
    initial_capital=100000.0,
    commission_per_trade=5.0,  # $5 per trade
    max_position_size=0.95
)

# Test Volume Spike Strategy with different parameters
print("\n" + "=" * 70)
print("Testing Volume Spike Strategy with different thresholds")
print("=" * 70)

strategies = [
    VolumeSpikeStrategy(
        symbol=symbol,
        volume_threshold=2.0,  # 2x average volume
        momentum_lookback=5,
        exit_volume_ratio=0.8
    ),
    VolumeSpikeStrategy(
        symbol=symbol,
        volume_threshold=2.5,  # 2.5x average volume (stricter)
        momentum_lookback=5,
        exit_volume_ratio=0.8
    ),
    VolumeSpikeStrategy(
        symbol=symbol,
        volume_threshold=3.0,  # 3x average volume (very strict)
        momentum_lookback=5,
        exit_volume_ratio=0.8
    ),
    BuyAndHoldStrategy(symbol=symbol)  # Benchmark
]

results = []

for strategy in strategies:
    print(f"\n🔄 Running: {strategy.name}...")

    result = backtester.run(
        strategy=strategy,
        data=df,
        symbol=symbol,
        warmup_period=25  # Warm up indicators
    )

    results.append(result)

    # Print brief summary
    metrics = result.get_metrics()
    print(f"   Return: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:+.2f}%)")
    print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"   Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
    print(f"   Trades: {metrics['num_trades']}")
    print(f"   Win Rate: {metrics['win_rate']:.2f}%")

# Detailed results for best strategy
print("\n\n" + "=" * 70)
print("DETAILED RESULTS: Volume Spike (2.0x)")
print("=" * 70)
results[0].print_summary()

# Show some trades
print("\n\n📋 SAMPLE TRADES:")
print("-" * 70)
trades = results[0].trades[:10]  # Show first 10 trades
for i, trade in enumerate(trades, 1):
    print(f"{i}. {trade['timestamp'].strftime('%Y-%m-%d')} | "
          f"{trade['action']:<4} | {trade['quantity']:>3} shares @ ${trade['price']:.2f}")
    print(f"   Reason: {trade['reason']}")

if len(results[0].trades) > 10:
    print(f"\n   ... and {len(results[0].trades) - 10} more trades")

# Performance comparison
print("\n\n" + "=" * 70)
print("STRATEGY COMPARISON")
print("=" * 70)

import pandas as pd
comparison_data = []

for result in results:
    metrics = result.get_metrics()
    comparison_data.append({
        'Strategy': metrics['strategy'],
        'Return': f"${metrics['total_return']:,.2f}",
        'Return %': f"{metrics['total_return_pct']:+.2f}%",
        'Sharpe': f"{metrics['sharpe_ratio']:.2f}",
        'Max DD': f"{metrics['max_drawdown_pct']:.2f}%",
        'Trades': metrics['num_trades'],
        'Win Rate': f"{metrics['win_rate']:.2f}%"
    })

comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))

# Visualizations
print("\n\n📈 Generating visualizations...")
print("   1. Equity curve comparison")
plot_comparison(results, show=False)

print("   2. Trade analysis for Volume Spike (2.0x)")
plot_trade_analysis(results[0], df, show=False)

print("   3. Individual equity curve")
plot_equity_curve(results[0])

print("\n\n" + "=" * 70)
print("STRATEGY INSIGHTS")
print("=" * 70)
print("""
The Volume Spike Strategy (BNF-inspired) works by:

1. ENTRY SIGNALS:
   - Volume exceeds 2x (or higher) the 20-day average
   - Price shows positive momentum over the last 5 days
   - Price closes in the upper 60% of the bar (strong buying)

2. EXIT SIGNALS:
   - Volume drops below 80% of average (activity normalizing)
   - Price momentum turns negative (-1% or worse)
   - Stop-loss triggered at -3% loss

3. RISK MANAGEMENT:
   - 95% position sizing (leaves cash buffer)
   - 3% stop-loss on every trade
   - Exits quickly when volume/momentum fade

This strategy is best suited for:
✓ Volatile stocks with high liquidity
✓ Stocks that experience news-driven spikes
✓ Markets with clear volume patterns
✓ Day trading or short-term swing trading

Compare the different thresholds (2x, 2.5x, 3x) to see the trade-off:
- Lower threshold (2x): More trades, more exposure
- Higher threshold (3x): Fewer trades, stronger signals
""")

print("\n✅ Volume Spike Strategy test completed!")
