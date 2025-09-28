import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

from data_source.yfinance import YFinanceDataSource


class TestYFinanceDataSource(unittest.TestCase):
    
    def setUp(self):
        self.data_source = YFinanceDataSource()
    
    def test_init(self):
        """Test YFinanceDataSource initialization"""
        self.assertEqual(self.data_source.name, "Yahoo Finance")
    
    @patch('data_source.yfinance.yf.download')
    def test_fetch_one_day_data_success(self, mock_download):
        """Test successful fetch_one_day_data call"""
        # Mock successful response
        mock_df = pd.DataFrame({
            'Open': [150.0, 151.0],
            'High': [152.0, 153.0],
            'Low': [149.0, 150.0],
            'Close': [151.0, 152.0],
            'Volume': [1000000, 1100000]
        }, index=pd.DatetimeIndex(['2025-08-06 09:30:00', '2025-08-06 09:31:00']))
        
        mock_download.return_value = mock_df
        
        result = self.data_source.fetch_one_day_data("AAPL", "2025-08-06", "1m")
        
        # Verify yf.download was called with correct parameters
        mock_download.assert_called_once_with(
            "AAPL", 
            start="2025-08-06", 
            end="2025-08-07", 
            interval="1m"
        )
        
        # Verify result has reset index
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('Open', result.columns)
        self.assertIn('High', result.columns)
        self.assertIn('Low', result.columns)
        self.assertIn('Close', result.columns)
        self.assertIn('Volume', result.columns)
        self.assertEqual(len(result), 2)
    
    @patch('data_source.yfinance.yf.download')
    @patch('builtins.print')
    def test_fetch_one_day_data_exception(self, mock_print, mock_download):
        """Test fetch_one_day_data when yfinance raises exception"""
        # Mock exception
        mock_download.side_effect = Exception("Network error")
        
        result = self.data_source.fetch_one_day_data("AAPL", "2025-08-06", "1m")
        
        # Verify error was printed and None returned
        mock_print.assert_called_once_with(
            "Error fetching one day data for AAPL on 2025-08-06 from Yahoo Finance: Network error"
        )
        self.assertIsNone(result)
    
    @patch('data_source.yfinance.yf.download')
    def test_fetch_one_day_data_different_intervals(self, mock_download):
        """Test fetch_one_day_data with different interval parameters"""
        # Test different intervals
        intervals = ["1m", "5m", "15m", "1h", "1d"]
        for interval in intervals:
            with self.subTest(interval=interval):
                # Create fresh mock DataFrame for each test
                mock_df = pd.DataFrame({
                    'Open': [150.0],
                    'High': [152.0],
                    'Low': [149.0],
                    'Close': [151.0],
                    'Volume': [1000000]
                }, index=pd.DatetimeIndex(['2025-08-06']))
                
                mock_download.return_value = mock_df
                
                result = self.data_source.fetch_one_day_data("AAPL", "2025-08-06", interval)
                
                # Verify correct parameters passed to yf.download
                mock_download.assert_called_with("AAPL", start="2025-08-06", end="2025-08-07", interval=interval)
                
                self.assertIsInstance(result, pd.DataFrame)
    
    @patch('data_source.yfinance.yf.download')
    def test_fetch_one_day_data_different_symbols(self, mock_download):
        """Test fetch_one_day_data with different stock symbols"""
        # Test different symbols
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                # Create fresh mock DataFrame for each test
                mock_df = pd.DataFrame({
                    'Open': [100.0],
                    'High': [102.0],
                    'Low': [99.0],
                    'Close': [101.0],
                    'Volume': [500000]
                }, index=pd.DatetimeIndex(['2025-08-06']))
                
                mock_download.return_value = mock_df
                
                result = self.data_source.fetch_one_day_data(symbol, "2025-08-06", "1m")
                
                # Verify correct symbol passed to yf.download
                mock_download.assert_called_with(
                    symbol, 
                    start="2025-08-06", 
                    end="2025-08-07", 
                    interval="1m"
                )
                
                self.assertIsInstance(result, pd.DataFrame)
    
    @patch('data_source.yfinance.yf.download')
    def test_fetch_one_day_data_date_calculation(self, mock_download):
        """Test that date calculation correctly adds one day for end date"""
        # Test various dates
        test_dates = [
            ("2025-01-01", "2025-01-02"),
            ("2025-02-28", "2025-03-01"),  # Non-leap year
            ("2025-12-31", "2026-01-01"),  # Year boundary
        ]
        
        for input_date, expected_end_date in test_dates:
            with self.subTest(date=input_date):
                # Create fresh mock DataFrame for each test
                mock_df = pd.DataFrame({
                    'Open': [150.0],
                    'High': [152.0],
                    'Low': [149.0],
                    'Close': [151.0],
                    'Volume': [1000000]
                }, index=pd.DatetimeIndex([input_date]))
                
                mock_download.return_value = mock_df
                
                result = self.data_source.fetch_one_day_data("AAPL", input_date, "1m")
                
                mock_download.assert_called_with(
                    "AAPL", 
                    start=input_date, 
                    end=expected_end_date, 
                    interval="1m"
                )
    
    @patch('data_source.yfinance.yf.download')
    def test_fetch_one_day_data_empty_dataframe(self, mock_download):
        """Test fetch_one_day_data when yfinance returns empty DataFrame"""
        # Mock empty DataFrame
        mock_download.return_value = pd.DataFrame()
        
        result = self.data_source.fetch_one_day_data("INVALID", "2025-08-06", "1m")
        
        # Should still return DataFrame (empty) without error
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    @patch('data_source.yfinance.yf.download')
    def test_fetch_one_day_data_reset_index_called(self, mock_download):
        """Test that reset_index is called on the returned DataFrame"""
        # Create DataFrame with DatetimeIndex
        mock_df = pd.DataFrame({
            'Open': [150.0, 151.0],
            'High': [152.0, 153.0],
            'Low': [149.0, 150.0],
            'Close': [151.0, 152.0],
            'Volume': [1000000, 1100000]
        }, index=pd.DatetimeIndex(['2025-08-06 09:30:00', '2025-08-06 09:31:00'], name='Datetime'))
        
        mock_download.return_value = mock_df
        
        result = self.data_source.fetch_one_day_data("AAPL", "2025-08-06", "1m")
        
        # Verify that the index was reset (should now be default integer index)
        self.assertIsInstance(result.index, pd.RangeIndex)
        # The original index should now be a column
        self.assertIn('Datetime', result.columns)


if __name__ == '__main__':
    unittest.main()