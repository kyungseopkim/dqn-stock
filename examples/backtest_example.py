"""
Example: Backtesting Trading Strategies

This example demonstrates how to:
- Load historical data
- Run backtests with different strategies
- Compare strategy performance
- Visualize results
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtester import Backtester
from strategies import BuyAndHoldStrategy, SMAStrategy, RSIStrategy, MomentumStrategy
from backtest_viz import (
    plot_equity_curve, plot_drawdown, plot_returns_distribution,
    plot_comparison, plot_trade_analysis, create_performance_report
)
from data_source.yfinance import YFinanceDataSource


def convert_columns(df):
    """Convert MultiIndex columns to simple index"""
    import pandas as pd
    if isinstance(df.columns, pd.MultiIndex):
        new_df = pd.DataFrame()
        for col in df.columns.values.tolist():
            new_df[col[0]] = df[col]
        # Preserve the index from original dataframe
        new_df.index = df.index
        return new_df
    return df


def basic_backtest_example():
    """Basic example of running a single backtest"""
    print("=" * 70)
    print("BASIC BACKTEST EXAMPLE")
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
        return

    # Convert columns if needed
    df = convert_columns(df)

    print(f"✅ Loaded {len(df)} days of data for {symbol}")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    print(f"   Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")

    # Initialize backtester
    backtester = Backtester(
        initial_capital=100000.0,
        commission_per_trade=1.0,  # $1 per trade
        max_position_size=0.95
    )

    # Create and run strategy
    print(f"\n🔄 Running SMA Crossover Strategy...")
    strategy = SMAStrategy(symbol=symbol, short_window=20, long_window=50)

    result = backtester.run(
        strategy=strategy,
        data=df,
        symbol=symbol,
        warmup_period=50  # Warm up indicators with 50 days
    )

    # Print results
    print("\n")
    result.print_summary()

    # Plot results
    print("\n📈 Generating visualizations...")
    plot_equity_curve(result, show=False)
    plot_drawdown(result, show=False)
    plot_trade_analysis(result, df)

    print("\n" + "=" * 70)


def strategy_comparison_example():
    """Compare multiple strategies on the same data"""
    print("\n\n" + "=" * 70)
    print("STRATEGY COMPARISON EXAMPLE")
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
        return

    df = convert_columns(df)
    print(f"✅ Loaded {len(df)} days of data")

    # Initialize backtester
    backtester = Backtester(
        initial_capital=100000.0,
        commission_per_trade=1.0
    )

    # Define strategies to test
    strategies = [
        BuyAndHoldStrategy(symbol=symbol),
        SMAStrategy(symbol=symbol, short_window=20, long_window=50),
        RSIStrategy(symbol=symbol, period=14, oversold=30, overbought=70),
        MomentumStrategy(symbol=symbol, lookback=20)
    ]

    print(f"\n🔄 Running {len(strategies)} strategies...")
    print("-" * 70)

    results = []

    for strategy in strategies:
        print(f"\n  Testing: {strategy.name}...")

        result = backtester.run(
            strategy=strategy,
            data=df,
            symbol=symbol,
            warmup_period=50
        )

        results.append(result)

        # Print brief summary
        metrics = result.get_metrics()
        print(f"    Return: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:+.2f}%)")
        print(f"    Sharpe: {metrics['sharpe_ratio']:.2f}")
        print(f"    Max DD: {metrics['max_drawdown_pct']:.2f}%")
        print(f"    Trades: {metrics['num_trades']}")

    # Print comparison table
    print("\n\n📊 STRATEGY COMPARISON")
    print("-" * 70)

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

    # Plot comparison
    print("\n📈 Generating comparison chart...")
    plot_comparison(results)

    print("\n" + "=" * 70)


def detailed_analysis_example():
    """Detailed analysis of a single strategy"""
    print("\n\n" + "=" * 70)
    print("DETAILED ANALYSIS EXAMPLE")
    print("=" * 70)

    # Fetch historical data
    print("\n📊 Fetching historical data...")
    data_source = YFinanceDataSource()
    symbol = "TSLA"
    start_date = "2024-01-01"
    end_date = "2024-12-01"

    df = data_source.fetch_data(symbol, start_date, end_date)

    if df is None or df.empty:
        print("❌ Failed to fetch data")
        return

    df = convert_columns(df)
    print(f"✅ Loaded {len(df)} days of data for {symbol}")

    # Initialize backtester
    backtester = Backtester(
        initial_capital=50000.0,
        commission_per_trade=5.0  # $5 per trade
    )

    # Run RSI strategy
    print(f"\n🔄 Running RSI Mean Reversion Strategy...")
    strategy = RSIStrategy(
        symbol=symbol,
        period=14,
        oversold=30,
        overbought=70
    )

    result = backtester.run(
        strategy=strategy,
        data=df,
        symbol=symbol,
        warmup_period=20
    )

    # Print detailed results
    print("\n")
    result.print_summary()

    # Show trades
    print("\n\n📋 TRADE HISTORY:")
    print("-" * 70)

    if result.trades:
        for i, trade in enumerate(result.trades[:10], 1):  # Show first 10 trades
            print(f"{i}. {trade['timestamp'].strftime('%Y-%m-%d')} | "
                  f"{trade['action']:<4} | {trade['quantity']:>3} shares @ ${trade['price']:.2f}")
            if trade.get('reason'):
                print(f"   Reason: {trade['reason']}")

        if len(result.trades) > 10:
            print(f"\n   ... and {len(result.trades) - 10} more trades")
    else:
        print("   No trades executed")

    # Create comprehensive report
    print("\n📈 Generating comprehensive performance report...")
    create_performance_report(result, df)

    print("\n" + "=" * 70)


def custom_strategy_example():
    """Example of creating and testing a custom strategy"""
    print("\n\n" + "=" * 70)
    print("CUSTOM STRATEGY EXAMPLE")
    print("=" * 70)

    from backtester import Strategy, Trade
    from asset_manager import AssetManager
    import pandas as pd
    from typing import Optional, List

    class SimpleTrendStrategy(Strategy):
        """
        Simple trend-following strategy:
        - Buy when price > 20-day MA
        - Sell when price < 20-day MA
        """

        def __init__(self, symbol: str, ma_period: int = 20):
            super().__init__(f"Simple Trend ({ma_period}-day MA)")
            self.symbol = symbol
            self.ma_period = ma_period
            self.prices = []

        def on_start(self, initial_data: pd.DataFrame):
            if len(initial_data) > 0:
                self.prices = list(initial_data['Close'].values)

        def on_data(self, bar: pd.Series, portfolio: AssetManager) -> Optional[List[Trade]]:
            import numpy as np

            price = float(bar['Close'])
            self.prices.append(price)

            if len(self.prices) < self.ma_period:
                return None

            ma = np.mean(self.prices[-self.ma_period:])
            position = portfolio.get_position(self.symbol)

            # Buy signal
            if price > ma and position is None:
                quantity = int((portfolio.cash * 0.95) / price)
                if quantity > 0:
                    return [Trade(
                        symbol=self.symbol,
                        action='buy',
                        quantity=quantity,
                        price=price,
                        timestamp=bar.name,
                        reason=f"Price ${price:.2f} > MA ${ma:.2f}"
                    )]

            # Sell signal
            elif price < ma and position is not None:
                return [Trade(
                    symbol=self.symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=price,
                    timestamp=bar.name,
                    reason=f"Price ${price:.2f} < MA ${ma:.2f}"
                )]

            return None

    # Fetch data
    print("\n📊 Fetching historical data...")
    data_source = YFinanceDataSource()
    symbol = "MSFT"
    start_date = "2024-01-01"
    end_date = "2024-12-01"

    df = data_source.fetch_data(symbol, start_date, end_date)

    if df is None or df.empty:
        print("❌ Failed to fetch data")
        return

    df = convert_columns(df)
    print(f"✅ Loaded {len(df)} days of data for {symbol}")

    # Run custom strategy
    backtester = Backtester(initial_capital=100000.0)

    print(f"\n🔄 Running Custom Trend Strategy...")
    strategy = SimpleTrendStrategy(symbol=symbol, ma_period=20)

    result = backtester.run(
        strategy=strategy,
        data=df,
        symbol=symbol,
        warmup_period=20
    )

    # Print results
    print("\n")
    result.print_summary()

    # Visualize
    print("\n📈 Generating visualizations...")
    plot_equity_curve(result, show=False)
    plot_trade_analysis(result, df)

    print("\n" + "=" * 70)


def main():
    """Run all examples"""
    print("\n🚀 BACKTESTING EXAMPLES")
    print("=" * 70)

    try:
        basic_backtest_example()
        strategy_comparison_example()
        detailed_analysis_example()
        custom_strategy_example()

        print("\n\n✅ All examples completed!")
        print("\n📝 Next Steps:")
        print("- Try different symbols and date ranges")
        print("- Experiment with strategy parameters")
        print("- Create your own custom strategies")
        print("- Optimize strategies using parameter sweeps")
        print("- Test on out-of-sample data")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
