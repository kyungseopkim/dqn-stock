"""
Example: Using the Asset Manager for Day Trading

This example demonstrates how to use the AssetManager class for:
- Portfolio initialization
- Executing buy/sell orders
- Tracking positions and P&L
- Risk management
- Integration with data sources for real-time pricing
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asset_manager import AssetManager, Position, Transaction, OrderSide
from data_source.yfinance import YFinanceDataSource


def basic_trading_example():
    """Basic example of buying and selling stocks"""
    print("=" * 60)
    print("BASIC TRADING EXAMPLE")
    print("=" * 60)

    # Initialize asset manager with $100,000
    manager = AssetManager(
        initial_cash=100000.0,
        max_position_size=0.25,  # Max 25% per position
        commission_per_trade=0.0  # No commission for this example
    )

    print(f"\nInitial cash: ${manager.cash:,.2f}")
    print(f"Portfolio value: ${manager.portfolio_value:,.2f}\n")

    # Buy some stocks
    print("EXECUTING TRADES:")
    print("-" * 60)

    # Buy AAPL
    success, msg = manager.buy("AAPL", 100, 180.50)
    print(f"1. {msg}")

    # Buy GOOGL
    success, msg = manager.buy("GOOGL", 50, 140.25)
    print(f"2. {msg}")

    # Buy TSLA
    success, msg = manager.buy("TSLA", 75, 250.00)
    print(f"3. {msg}")

    # Try to buy too much (should fail due to position limit)
    success, msg = manager.buy("MSFT", 1000, 380.00)
    if not success:
        print(f"4. REJECTED: {msg}")

    # Update prices (simulate price changes)
    print("\n\nPRICE UPDATE (End of Day):")
    print("-" * 60)
    new_prices = {
        "AAPL": 182.00,  # +$1.50
        "GOOGL": 138.50,  # -$1.75
        "TSLA": 255.00,   # +$5.00
    }
    manager.update_prices(new_prices)
    print(f"AAPL: ${new_prices['AAPL']:.2f} (+0.83%)")
    print(f"GOOGL: ${new_prices['GOOGL']:.2f} (-1.25%)")
    print(f"TSLA: ${new_prices['TSLA']:.2f} (+2.00%)")

    # Print portfolio summary
    print("\n")
    manager.print_summary()

    # Sell some positions
    print("\n\nCLOSING POSITIONS:")
    print("-" * 60)

    # Sell half of AAPL
    success, msg = manager.sell("AAPL", 50, 182.00)
    print(f"1. {msg}")

    # Close entire TSLA position
    success, msg = manager.close_position("TSLA", 255.00)
    print(f"2. {msg}")

    # Final summary
    print("\n")
    manager.print_summary()

    # Show transaction history
    print("\n\nTRANSACTION HISTORY:")
    print("-" * 60)
    for i, txn in enumerate(manager.transactions, 1):
        print(f"{i}. {txn}")

    print("\n" + "=" * 60)


def live_data_trading_example():
    """Example using live market data from YFinance"""
    print("\n\n" + "=" * 60)
    print("LIVE DATA TRADING EXAMPLE")
    print("=" * 60)

    # Initialize components
    data_source = YFinanceDataSource()
    manager = AssetManager(
        initial_cash=50000.0,
        max_position_size=0.20,
        commission_per_trade=1.0  # $1 commission per trade
    )

    # Symbols to trade
    symbols = ["AAPL", "MSFT", "GOOGL"]

    print(f"\nInitial portfolio value: ${manager.portfolio_value:,.2f}")
    print(f"Symbols to trade: {', '.join(symbols)}\n")

    # Fetch recent data to get current prices
    print("Fetching market data...")
    date = datetime.now() - timedelta(days=1)
    # Find most recent trading day
    while date.weekday() >= 5:  # Skip weekends
        date -= timedelta(days=1)
    date_str = date.strftime("%Y-%m-%d")

    print(f"Using data from: {date_str}")
    print("-" * 60)

    current_prices = {}
    for symbol in symbols:
        df = data_source.fetch_one_day_data(symbol, date_str, "1d")
        if df is not None and not df.empty:
            # Handle MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                close_col = ('Close', symbol)
            else:
                close_col = 'Close'

            price = df[close_col].iloc[-1] if close_col in df.columns else df.iloc[-1]['Close']
            current_prices[symbol] = float(price)
            print(f"{symbol}: ${price:.2f}")
        else:
            print(f"{symbol}: No data available")

    if not current_prices:
        print("\nNo market data available. Using simulated prices.")
        current_prices = {
            "AAPL": 180.00,
            "MSFT": 380.00,
            "GOOGL": 140.00
        }

    # Execute trades based on simple strategy
    print("\n\nEXECUTING TRADES:")
    print("-" * 60)

    # Buy equal amounts of each stock
    allocation_per_stock = manager.cash / len(symbols)

    for symbol in symbols:
        if symbol in current_prices:
            price = current_prices[symbol]
            # Calculate quantity (leaving some buffer for commission)
            quantity = int((allocation_per_stock - 10) / price)

            if quantity > 0:
                success, msg = manager.buy(symbol, quantity, price)
                print(f"{msg}")

    # Update prices to current
    manager.update_prices(current_prices)

    # Show portfolio
    print("\n")
    manager.print_summary()

    # Show positions as DataFrame
    print("\n\nPOSITIONS TABLE:")
    print("-" * 60)
    import pandas as pd
    pd.options.display.float_format = '{:,.2f}'.format
    positions_df = manager.get_positions_df()
    if not positions_df.empty:
        print(positions_df.to_string(index=False))

    print("\n" + "=" * 60)


def risk_management_example():
    """Example demonstrating risk management features"""
    print("\n\n" + "=" * 60)
    print("RISK MANAGEMENT EXAMPLE")
    print("=" * 60)

    # Initialize with strict position limits
    manager = AssetManager(
        initial_cash=100000.0,
        max_position_size=0.15,  # Max 15% per position (strict)
        commission_per_trade=5.0
    )

    print(f"\nPortfolio value: ${manager.portfolio_value:,.2f}")
    print(f"Max position size: {manager.max_position_size * 100}%")
    print(f"Max position value: ${manager.portfolio_value * manager.max_position_size:,.2f}\n")

    print("TESTING RISK LIMITS:")
    print("-" * 60)

    # Test 1: Try to buy within limits (should succeed)
    print("\n1. Buy within limits:")
    success, msg = manager.buy("AAPL", 80, 180.00)  # $14,400
    print(f"   {msg}")
    print(f"   Position value: ${80 * 180:.2f}")

    # Test 2: Try to exceed position limit (should fail)
    print("\n2. Try to exceed position limit:")
    success, msg = manager.buy("AAPL", 100, 180.00)  # Would bring total to $32,400
    if not success:
        print(f"   REJECTED: {msg}")
    else:
        print(f"   {msg}")

    # Test 3: Try to buy with insufficient funds (should fail)
    print("\n3. Try to buy with insufficient funds:")
    success, msg = manager.buy("TSLA", 500, 250.00)  # $125,000
    if not success:
        print(f"   REJECTED: {msg}")

    # Test 4: Try to sell more than owned (should fail)
    print("\n4. Try to sell more shares than owned:")
    success, msg = manager.sell("AAPL", 100, 185.00)
    if not success:
        print(f"   REJECTED: {msg}")

    # Test 5: Valid sell within limits
    print("\n5. Valid sell:")
    success, msg = manager.sell("AAPL", 40, 185.00)
    print(f"   {msg}")

    # Final summary
    print("\n")
    manager.print_summary()

    print("\n" + "=" * 60)


def portfolio_analytics_example():
    """Example showing portfolio analytics and reporting"""
    print("\n\n" + "=" * 60)
    print("PORTFOLIO ANALYTICS EXAMPLE")
    print("=" * 60)

    manager = AssetManager(initial_cash=200000.0)

    # Simulate a day of trading
    trades = [
        ("BUY", "AAPL", 200, 180.00),
        ("BUY", "MSFT", 150, 380.00),
        ("BUY", "GOOGL", 100, 140.00),
        ("BUY", "TSLA", 50, 250.00),
        ("SELL", "AAPL", 50, 182.00),  # Small profit
        ("SELL", "GOOGL", 100, 138.00),  # Small loss
    ]

    print("\nExecuting trades...")
    for side, symbol, qty, price in trades:
        if side == "BUY":
            manager.buy(symbol, qty, price)
        else:
            manager.sell(symbol, qty, price)

    # Update end-of-day prices
    eod_prices = {
        "AAPL": 183.50,
        "MSFT": 385.00,
        "TSLA": 245.00,
    }
    manager.update_prices(eod_prices)

    # Get comprehensive analytics
    print("\n")
    manager.print_summary()

    # Transaction report
    print("\n\nTRANSACTION REPORT:")
    print("-" * 60)
    import pandas as pd
    pd.options.display.float_format = '{:,.2f}'.format
    txn_df = manager.get_transactions_df()
    if not txn_df.empty:
        print(txn_df.to_string(index=False))

    # Position breakdown
    print("\n\nPOSITION BREAKDOWN:")
    print("-" * 60)
    pos_df = manager.get_positions_df()
    if not pos_df.empty:
        print(pos_df.to_string(index=False))

    # Performance metrics
    summary = manager.get_portfolio_summary()
    print("\n\nPERFORMANCE METRICS:")
    print("-" * 60)
    print(f"Initial Capital:       ${manager.initial_cash:,.2f}")
    print(f"Current Value:         ${summary['portfolio_value']:,.2f}")
    print(f"Total Return:          ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.2f}%)")
    print(f"Realized P&L:          ${summary['realized_pnl']:,.2f}")
    print(f"Unrealized P&L:        ${summary['unrealized_pnl']:,.2f}")
    print(f"Cash Remaining:        ${summary['cash']:,.2f}")
    print(f"Portfolio Allocation:  {(summary['positions_value'] / summary['portfolio_value'] * 100):.1f}% invested")

    print("\n" + "=" * 60)


def main():
    """Run all examples"""
    print("\nASSET MANAGER EXAMPLES")
    print("=" * 60)

    # Import pandas for DataFrame display
    import pandas as pd

    # Run examples
    basic_trading_example()
    risk_management_example()
    portfolio_analytics_example()

    # Optional: Run live data example (requires market data)
    print("\n\n")
    response = input("Run live data example? (y/n): ").strip().lower()
    if response == 'y':
        live_data_trading_example()

    print("\n\nAll examples completed!")
    print("\nNext steps:")
    print("- Integrate with real-time data sources")
    print("- Implement trading strategies")
    print("- Add stop-loss and take-profit orders")
    print("- Build backtesting framework")
    print("- Connect to Alpaca API for live trading")


if __name__ == "__main__":
    main()
