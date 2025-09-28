import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from .data_source import DataSource

# Load environment variables
load_dotenv()


class AlpacaDataSource(DataSource):
    """
    Alpaca Markets data source implementation for fetching stock data.
    
    Requires API credentials stored in environment variables:
    - ALPACA_API_KEY: Your Alpaca API key
    - ALPACA_SECRET_KEY: Your Alpaca secret key
    - ALPACA_BASE_URL: Base URL (optional, defaults to paper trading)
    """
    
    def __init__(self):
        self.name = "Alpaca Markets"
        
        # Get API credentials from environment variables
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not self.api_key or not self.secret_key:
            raise ValueError(
                "Alpaca API credentials not found. Please set ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY in your .env file"
            )
        
        # Initialize the historical data client
        try:
            self.client = StockHistoricalDataClient(self.api_key, self.secret_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Alpaca client: {str(e)}")
    
    def _get_timeframe(self, interval: str) -> TimeFrame:
        """
        Convert interval string to Alpaca TimeFrame object.
        
        Args:
            interval (str): Time interval (e.g., '1m', '5m', '15m', '1h', '1d')
        
        Returns:
            TimeFrame: Alpaca TimeFrame object
        """
        interval_map = {
            '1m': TimeFrame(1, TimeFrameUnit.Minute),
            '2m': TimeFrame(2, TimeFrameUnit.Minute),
            '5m': TimeFrame(5, TimeFrameUnit.Minute),
            '15m': TimeFrame(15, TimeFrameUnit.Minute),
            '30m': TimeFrame(30, TimeFrameUnit.Minute),
            '1h': TimeFrame(1, TimeFrameUnit.Hour),
            '1d': TimeFrame(1, TimeFrameUnit.Day),
            '1W': TimeFrame(1, TimeFrameUnit.Week),
            '1M': TimeFrame(1, TimeFrameUnit.Month),
        }
        
        if interval not in interval_map:
            raise ValueError(
                f"Unsupported interval: {interval}. "
                f"Supported intervals: {list(interval_map.keys())}"
            )
        
        return interval_map[interval]
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a symbol within a specific date range.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'GOOGL')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
        
        Returns:
            pd.DataFrame: DataFrame with OHLCV data, or None if error
        """
        try:
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Create request for daily bars
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame(1, TimeFrameUnit.Day),
                start=start_dt,
                end=end_dt
            )
            
            # Fetch data
            bars = self.client.get_stock_bars(request)
            
            if symbol not in bars.data or not bars.data[symbol]:
                print(f"No data found for {symbol} from {start_date} to {end_date}")
                return None
            
            # Convert to DataFrame
            df = bars.df.reset_index()
            
            # Rename columns to match standard format
            df = df.rename(columns={
                'timestamp': 'Datetime',
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Ensure datetime column
            if 'Datetime' in df.columns:
                df['Datetime'] = pd.to_datetime(df['Datetime'])
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol} from {self.name}: {str(e)}")
            return None
    
    def fetch_one_day_data(self, symbol: str, date: str, interval: str) -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a single day with specified interval.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'GOOGL')
            date (str): Date in 'YYYY-MM-DD' format
            interval (str): Data interval (e.g., '1m', '5m', '15m', '1h', '1d')
        
        Returns:
            pd.DataFrame: DataFrame with OHLCV data, or None if error
        """
        try:
            # Parse date and create time range
            target_date = datetime.strptime(date, '%Y-%m-%d')
            
            # For intraday data, use market hours (9:30 AM to 4:00 PM ET)
            if interval != '1d':
                start_dt = target_date.replace(hour=9, minute=30, second=0, microsecond=0)
                end_dt = target_date.replace(hour=16, minute=0, second=0, microsecond=0)
            else:
                start_dt = target_date
                end_dt = target_date + timedelta(days=1)
            
            # Get timeframe
            timeframe = self._get_timeframe(interval)
            
            # Create request
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start_dt,
                end=end_dt
            )
            
            # Fetch data
            bars = self.client.get_stock_bars(request)
            
            if symbol not in bars.data or not bars.data[symbol]:
                print(f"No {interval} data found for {symbol} on {date}")
                return None
            
            # Convert to DataFrame
            df = bars.df.reset_index()
            
            # Rename columns to match standard format
            df = df.rename(columns={
                'timestamp': 'Datetime',
                'open': 'Open',
                'high': 'High',
                'low': 'Low', 
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Ensure datetime column
            if 'Datetime' in df.columns:
                df['Datetime'] = pd.to_datetime(df['Datetime'])

            df.set_index("Datetime", inplace=True)
            return df
            
        except Exception as e:
            print(f"Error fetching {interval} data for {symbol} on {date} from {self.name}: {str(e)}")
            return None
    
    def get_latest_quote(self, symbol: str) -> Optional[dict]:
        """
        Get the latest quote data for a symbol.
        
        Args:
            symbol (str): Stock symbol
        
        Returns:
            dict: Latest quote data with bid/ask prices and sizes
        """
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self.client.get_stock_latest_quote(request)
            
            if symbol not in quotes:
                print(f"No quote data found for {symbol}")
                return None
            
            quote = quotes[symbol]
            
            return {
                'symbol': symbol,
                'bid_price': quote.bid_price,
                'bid_size': quote.bid_size,
                'ask_price': quote.ask_price,
                'ask_size': quote.ask_size,
                'timestamp': quote.timestamp
            }
            
        except Exception as e:
            print(f"Error fetching latest quote for {symbol} from {self.name}: {str(e)}")
            return None
    
    def get_supported_intervals(self) -> list:
        """
        Get list of supported time intervals.
        
        Returns:
            list: List of supported interval strings
        """
        return ['1m', '2m', '5m', '15m', '30m', '1h', '1d', '1W', '1M']
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a symbol exists and is tradeable.
        
        Args:
            symbol (str): Stock symbol to validate
        
        Returns:
            bool: True if symbol is valid, False otherwise
        """
        try:
            # Try to get latest quote as a validation method
            quote = self.get_latest_quote(symbol)
            return quote is not None
            
        except Exception:
            return False