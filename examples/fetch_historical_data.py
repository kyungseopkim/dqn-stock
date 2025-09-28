"""
Example: Fetching Historical Stock Data using YFinanceDataSource

This example demonstrates how to use the YFinanceDataSource class to fetch
historical stock data for a single trading day with different time intervals.
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Add parent directory to path to import data_source module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_source.yfinance import YFinanceDataSource
from indicators import generate_technical_indicators


def convert_columns(df):
    """
    Convert MultiIndex ('Price', 'Ticker') to Simple Index ('Price')
    This is needed when Yahoo Finance returns MultiIndex columns
    """
    if isinstance(df.columns, pd.MultiIndex):
        new_df = pd.DataFrame()
        for col in df.columns.values.tolist():
            new_df[col[0]] = df[col]
        new_df.set_index("Datetime", inplace=True)
        return new_df
    return df

def get_prior_trading_day(today=datetime.now()):
    yesterday = today - timedelta(days=1)
    # check if yesterday is a trading date (not holiday)
    if yesterday.weekday() < 5:
        return yesterday.strftime("%Y-%m-%d")
    else:
        return get_prior_trading_day(yesterday)

def fetch_stock_data_example():
    """
    Example function showing how to fetch stock data for a single day
    """
    print("=== YFinance Data Source Example ===\n")
    
    # Initialize the data source
    data_source = YFinanceDataSource()
    print(f"Data source initialized: {data_source.name}")
    
    # Configuration
    symbol = "AAPL"  # Apple Inc.
    # date = "2024-12-13"  # Trading date (use a recent weekday)
    # set prior 7 days trading date
    date = get_prior_trading_day()
    intervals = ["1m", "5m", "15m", "1h"]  # Different time intervals
    
    print(f"\nFetching data for {symbol} on {date}")
    print("-" * 50)
    
    # Fetch data for different intervals
    for interval in intervals:
        print(f"\n📊 Fetching {interval} interval data...")
        
        try:
            df = data_source.fetch_one_day_data(symbol, date, interval)
            
            if df is not None and not df.empty:
                # Convert columns if needed (MultiIndex to simple)
                df = convert_columns(df)
                
                print(f"✅ Successfully fetched {len(df)} data points")
                print(f"   Time range: {df.index[0]} to {df.index[-1]}")
                print(f"   Columns: {list(df.columns)}")
                print(f"   Price range: ${df['Low'].min():.2f} - ${df['High'].max():.2f}")
                
                # Display first few rows
                print("\n📈 Sample data:")
                print(df.head(3).to_string())
                
            else:
                print(f"❌ No data returned for {interval} interval")
                print("   This might be due to:")
                print("   - Weekend/holiday (markets closed)")
                print("   - Invalid symbol")
                print("   - Network issues")
                
        except Exception as e:
            print(f"❌ Error fetching {interval} data: {str(e)}")
    
    print("\n" + "="*60)


def analyze_trading_day_example():
    """
    Example function showing detailed analysis of a trading day
    """
    print("\n=== Detailed Trading Day Analysis ===\n")
    
    data_source = YFinanceDataSource()
    
    # Configuration for detailed analysis
    symbol = "TSLA"  # Tesla Inc.
    date = "2024-12-13"  # Recent trading date
    interval = "5m"  # 5-minute intervals for good detail
    
    print(f"Analyzing {symbol} trading day: {date} (5-minute intervals)")
    print("-" * 60)
    
    try:
        # Fetch the data
        df = data_source.fetch_one_day_data(symbol, date, interval)
        
        if df is not None and not df.empty:
            df = convert_columns(df)
            
            print(f"✅ Data fetched successfully:")
            print(f"   📊 Data points: {len(df)}")
            print(f"   ⏰ Trading hours: {df.index[0]} to {df.index[-1]}")
            print(f"   💰 Opening price: ${df['Open'].iloc[0]:.2f}")
            print(f"   💰 Closing price: ${df['Close'].iloc[-1]:.2f}")
            print(f"   📈 Day's high: ${df['High'].max():.2f}")
            print(f"   📉 Day's low: ${df['Low'].min():.2f}")
            print(f"   📊 Total volume: {df['Volume'].sum():,}")
            
            # Calculate daily statistics
            daily_change = df['Close'].iloc[-1] - df['Open'].iloc[0]
            daily_change_pct = (daily_change / df['Open'].iloc[0]) * 100
            price_volatility = ((df['High'].max() - df['Low'].min()) / df['Open'].iloc[0]) * 100
            
            print(f"\n📊 Daily Statistics:")
            print(f"   💹 Daily change: ${daily_change:.2f} ({daily_change_pct:+.2f}%)")
            print(f"   📊 Price volatility: {price_volatility:.2f}%")
            print(f"   🔄 Average volume per 5min: {df['Volume'].mean():,.0f}")
            
            # Generate technical indicators
            print(f"\n🔧 Generating technical indicators...")
            df_with_indicators = generate_technical_indicators(df)
            
            # Display some key indicators
            if 'rsi_14' in df_with_indicators.columns:
                latest_rsi = df_with_indicators['rsi_14'].iloc[-1]
                print(f"   📈 Latest RSI (14): {latest_rsi:.2f}")
            
            if 'close_20_sma' in df_with_indicators.columns:
                latest_sma = df_with_indicators['close_20_sma'].iloc[-1]
                print(f"   📊 20-period SMA: ${latest_sma:.2f}")
            
            # Show trading pattern analysis
            print(f"\n📈 Trading Pattern Analysis:")
            morning_data = df.iloc[:len(df)//3]  # First third of day
            afternoon_data = df.iloc[len(df)//3:]  # Last two thirds
            
            morning_vol = morning_data['Volume'].mean()
            afternoon_vol = afternoon_data['Volume'].mean()
            
            print(f"   🌅 Morning avg volume: {morning_vol:,.0f}")
            print(f"   🌆 Afternoon avg volume: {afternoon_vol:,.0f}")
            print(f"   📊 Volume trend: {'Higher afternoon' if afternoon_vol > morning_vol else 'Higher morning'}")
            
        else:
            print(f"❌ No data available for {symbol} on {date}")
            print("   Possible reasons:")
            print("   - Market was closed (weekend/holiday)")
            print("   - Symbol doesn't exist or is delisted")
            print("   - Date is too recent/future")
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
    
    print("\n" + "="*60)


def multi_symbol_comparison_example():
    """
    Example function showing how to compare multiple stocks on the same day
    """
    print("\n=== Multi-Symbol Comparison ===\n")
    
    data_source = YFinanceDataSource()
    
    # Configuration
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]  # Tech giants
    date = "2024-12-13"  # Recent trading date
    interval = "1h"  # Hourly data for overview
    
    print(f"Comparing tech stocks on {date} (hourly data)")
    print("-" * 50)
    
    stock_data = {}
    
    # Fetch data for each symbol
    for symbol in symbols:
        print(f"\n🔍 Fetching {symbol} data...")
        
        try:
            df = data_source.fetch_one_day_data(symbol, date, interval)
            
            if df is not None and not df.empty:
                df = convert_columns(df)
                stock_data[symbol] = df
                
                # Calculate key metrics
                opening = df['Open'].iloc[0]
                closing = df['Close'].iloc[-1]
                change_pct = ((closing - opening) / opening) * 100
                volume = df['Volume'].sum()
                
                print(f"   ✅ {symbol}: {change_pct:+.2f}% | Volume: {volume:,}")
                
            else:
                print(f"   ❌ No data for {symbol}")
                
        except Exception as e:
            print(f"   ❌ Error fetching {symbol}: {str(e)}")
    
    # Summary comparison
    if stock_data:
        print(f"\n📊 Daily Performance Summary:")
        print("-" * 40)
        
        performance = []
        for symbol, df in stock_data.items():
            opening = df['Open'].iloc[0]
            closing = df['Close'].iloc[-1]
            change_pct = ((closing - opening) / opening) * 100
            volume = df['Volume'].sum()
            
            performance.append({
                'Symbol': symbol,
                'Change%': change_pct,
                'Volume': volume,
                'Open': opening,
                'Close': closing
            })
        
        # Sort by performance
        performance.sort(key=lambda x: x['Change%'], reverse=True)
        
        print("   Rank | Symbol | Change% | Volume     | Open    | Close")
        print("   -----|--------|---------|------------|---------|--------")
        
        for i, stock in enumerate(performance, 1):
            print(f"   #{i:<3} | {stock['Symbol']:<6} | {stock['Change%']:+6.2f}% | "
                  f"{stock['Volume']:>9,} | ${stock['Open']:>6.2f} | ${stock['Close']:>6.2f}")
    
    print("\n" + "="*60)


def main():
    """
    Main function to run all examples
    """
    print("🚀 Stock Data Fetching Examples")
    print("=" * 60)
    
    # Run examples
    fetch_stock_data_example()
    analyze_trading_day_example()
    multi_symbol_comparison_example()
    
    print("\n📝 Notes:")
    print("- Use recent weekdays for better data availability")
    print("- Some intervals may not have data for all symbols")
    print("- Market hours: typically 9:30 AM - 4:00 PM ET")
    print("- Weekend/holiday data will be empty")
    print("\n🎯 Next steps:")
    print("- Try different dates and symbols")
    print("- Experiment with technical indicators")
    print("- Combine with database storage for historical analysis")


if __name__ == "__main__":
    main()