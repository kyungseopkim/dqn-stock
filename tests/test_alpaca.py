import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import pandas as pd
from datetime import datetime

from data_source.alpaca import AlpacaDataSource


class TestAlpacaDataSource(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock environment variables to prevent actual API calls during testing
        self.env_patcher = patch.dict('os.environ', {
            'ALPACA_API_KEY': 'test_api_key',
            'ALPACA_SECRET_KEY': 'test_secret_key',
            'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after each test method."""
        self.env_patcher.stop()
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_init_success(self, mock_client_class):
        """Test successful initialization with valid credentials"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        data_source = AlpacaDataSource()
        
        self.assertEqual(data_source.name, "Alpaca Markets")
        self.assertEqual(data_source.api_key, "test_api_key")
        self.assertEqual(data_source.secret_key, "test_secret_key")
        self.assertEqual(data_source.base_url, "https://paper-api.alpaca.markets")
        
        # Verify client was initialized with correct credentials
        mock_client_class.assert_called_once_with("test_api_key", "test_secret_key")
        self.assertEqual(data_source.client, mock_client)
    
    @patch.dict('os.environ', {}, clear=True)
    def test_init_missing_credentials(self):
        """Test initialization failure when API credentials are missing"""
        with self.assertRaises(ValueError) as context:
            AlpacaDataSource()
        
        self.assertIn("Alpaca API credentials not found", str(context.exception))
    
    @patch.dict('os.environ', {'ALPACA_API_KEY': 'test_key'}, clear=True)
    def test_init_partial_credentials(self):
        """Test initialization failure when only partial credentials are provided"""
        with self.assertRaises(ValueError) as context:
            AlpacaDataSource()
        
        self.assertIn("Alpaca API credentials not found", str(context.exception))
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_init_client_failure(self, mock_client_class):
        """Test initialization failure when client creation fails"""
        mock_client_class.side_effect = Exception("Client initialization failed")
        
        with self.assertRaises(ValueError) as context:
            AlpacaDataSource()
        
        self.assertIn("Failed to initialize Alpaca client", str(context.exception))
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_get_timeframe_valid_intervals(self, mock_client_class):
        """Test _get_timeframe method with valid intervals"""
        data_source = AlpacaDataSource()
        
        # Test different interval types
        test_cases = [
            ('1m', '1 Minute'),
            ('5m', '5 Minute'),
            ('15m', '15 Minute'),
            ('1h', '1 Hour'),
            ('1d', '1 Day')
        ]
        
        for interval, expected_str in test_cases:
            with self.subTest(interval=interval):
                timeframe = data_source._get_timeframe(interval)
                # TimeFrame objects have string representation
                self.assertIsNotNone(timeframe)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_get_timeframe_invalid_interval(self, mock_client_class):
        """Test _get_timeframe method with invalid interval"""
        data_source = AlpacaDataSource()
        
        with self.assertRaises(ValueError) as context:
            data_source._get_timeframe('invalid_interval')
        
        self.assertIn("Unsupported interval", str(context.exception))
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_fetch_data_success(self, mock_client_class):
        """Test successful fetch_data call"""
        # Create mock client and response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the bars response
        mock_bars = MagicMock()
        mock_bars.data = {
            'AAPL': [
                MagicMock(timestamp=datetime(2024, 1, 15, 9, 30), open=150.0, high=152.0, low=149.0, close=151.0, volume=1000000),
                MagicMock(timestamp=datetime(2024, 1, 16, 9, 30), open=151.0, high=153.0, low=150.0, close=152.0, volume=1100000)
            ]
        }
        
        # Mock DataFrame conversion
        mock_df = pd.DataFrame({
            'timestamp': [datetime(2024, 1, 15), datetime(2024, 1, 16)],
            'open': [150.0, 151.0],
            'high': [152.0, 153.0],
            'low': [149.0, 150.0],
            'close': [151.0, 152.0],
            'volume': [1000000, 1100000],
            'symbol': ['AAPL', 'AAPL']
        })
        
        mock_bars.df.reset_index.return_value = mock_df
        mock_client.get_stock_bars.return_value = mock_bars
        
        data_source = AlpacaDataSource()
        result = data_source.fetch_data("AAPL", "2024-01-15", "2024-01-16")
        
        # Verify the request was made
        mock_client.get_stock_bars.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('Datetime', result.columns)
        self.assertIn('Open', result.columns)
        self.assertIn('High', result.columns)
        self.assertIn('Low', result.columns)
        self.assertIn('Close', result.columns)
        self.assertIn('Volume', result.columns)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_fetch_data_no_data(self, mock_client_class):
        """Test fetch_data when no data is returned"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock empty response
        mock_bars = MagicMock()
        mock_bars.data = {}
        mock_client.get_stock_bars.return_value = mock_bars
        
        data_source = AlpacaDataSource()
        result = data_source.fetch_data("INVALID", "2024-01-15", "2024-01-16")
        
        self.assertIsNone(result)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    @patch('builtins.print')
    def test_fetch_data_exception(self, mock_print, mock_client_class):
        """Test fetch_data when an exception occurs"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock exception
        mock_client.get_stock_bars.side_effect = Exception("Network error")
        
        data_source = AlpacaDataSource()
        result = data_source.fetch_data("AAPL", "2024-01-15", "2024-01-16")
        
        # Verify error was printed and None returned
        mock_print.assert_called_once()
        self.assertIn("Error fetching data for AAPL from Alpaca Markets", mock_print.call_args[0][0])
        self.assertIsNone(result)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_fetch_one_day_data_success(self, mock_client_class):
        """Test successful fetch_one_day_data call"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the bars response
        mock_bars = MagicMock()
        mock_bars.data = {
            'AAPL': [
                MagicMock(timestamp=datetime(2024, 1, 15, 9, 30), open=150.0, high=152.0, low=149.0, close=151.0, volume=1000000),
                MagicMock(timestamp=datetime(2024, 1, 15, 9, 35), open=151.0, high=153.0, low=150.0, close=152.0, volume=1100000)
            ]
        }
        
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'timestamp': [datetime(2024, 1, 15, 9, 30), datetime(2024, 1, 15, 9, 35)],
            'open': [150.0, 151.0],
            'high': [152.0, 153.0],
            'low': [149.0, 150.0],
            'close': [151.0, 152.0],
            'volume': [1000000, 1100000],
            'symbol': ['AAPL', 'AAPL']
        })
        
        mock_bars.df.reset_index.return_value = mock_df
        mock_client.get_stock_bars.return_value = mock_bars
        
        data_source = AlpacaDataSource()
        result = data_source.fetch_one_day_data("AAPL", "2024-01-15", "5m")
        
        # Verify the request was made
        mock_client.get_stock_bars.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('Datetime', result.columns)
        self.assertEqual(len(result), 2)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_fetch_one_day_data_daily_interval(self, mock_client_class):
        """Test fetch_one_day_data with daily interval"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock daily data response
        mock_bars = MagicMock()
        mock_bars.data = {
            'AAPL': [
                MagicMock(timestamp=datetime(2024, 1, 15), open=150.0, high=155.0, low=148.0, close=154.0, volume=50000000)
            ]
        }
        
        mock_df = pd.DataFrame({
            'timestamp': [datetime(2024, 1, 15)],
            'open': [150.0],
            'high': [155.0],
            'low': [148.0],
            'close': [154.0],
            'volume': [50000000],
            'symbol': ['AAPL']
        })
        
        mock_bars.df.reset_index.return_value = mock_df
        mock_client.get_stock_bars.return_value = mock_bars
        
        data_source = AlpacaDataSource()
        result = data_source.fetch_one_day_data("AAPL", "2024-01-15", "1d")
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_fetch_one_day_data_different_intervals(self, mock_client_class):
        """Test fetch_one_day_data with different valid intervals"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create mock response for each test
        intervals = ["1m", "5m", "15m", "1h", "1d"]
        
        for interval in intervals:
            with self.subTest(interval=interval):
                # Reset mock for each iteration
                mock_bars = MagicMock()
                mock_bars.data = {
                    'AAPL': [
                        MagicMock(timestamp=datetime(2024, 1, 15, 9, 30), open=150.0, high=152.0, low=149.0, close=151.0, volume=1000000)
                    ]
                }
                
                mock_df = pd.DataFrame({
                    'timestamp': [datetime(2024, 1, 15, 9, 30)],
                    'open': [150.0],
                    'high': [152.0],
                    'low': [149.0],
                    'close': [151.0],
                    'volume': [1000000],
                    'symbol': ['AAPL']
                })
                
                mock_bars.df.reset_index.return_value = mock_df
                mock_client.get_stock_bars.return_value = mock_bars
                
                data_source = AlpacaDataSource()
                result = data_source.fetch_one_day_data("AAPL", "2024-01-15", interval)
                
                self.assertIsInstance(result, pd.DataFrame)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    @patch('builtins.print')
    def test_fetch_one_day_data_invalid_interval(self, mock_print, mock_client_class):
        """Test fetch_one_day_data with invalid interval"""
        data_source = AlpacaDataSource()
        
        # Invalid interval should be caught and return None with error message
        result = data_source.fetch_one_day_data("AAPL", "2024-01-15", "invalid_interval")
        
        # Should return None and print error message
        self.assertIsNone(result)
        mock_print.assert_called_once()
        self.assertIn("Error fetching invalid_interval data for AAPL", mock_print.call_args[0][0])
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_get_latest_quote_success(self, mock_client_class):
        """Test successful get_latest_quote call"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock quote response
        mock_quote_data = MagicMock()
        mock_quote_data.bid_price = 150.50
        mock_quote_data.bid_size = 100
        mock_quote_data.ask_price = 150.55
        mock_quote_data.ask_size = 200
        mock_quote_data.timestamp = datetime(2024, 1, 15, 10, 30)
        
        mock_quotes = {'AAPL': mock_quote_data}
        mock_client.get_stock_latest_quote.return_value = mock_quotes
        
        data_source = AlpacaDataSource()
        result = data_source.get_latest_quote("AAPL")
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['bid_price'], 150.50)
        self.assertEqual(result['bid_size'], 100)
        self.assertEqual(result['ask_price'], 150.55)
        self.assertEqual(result['ask_size'], 200)
        self.assertEqual(result['timestamp'], datetime(2024, 1, 15, 10, 30))
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_get_latest_quote_no_data(self, mock_client_class):
        """Test get_latest_quote when no quote data is returned"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock empty response
        mock_client.get_stock_latest_quote.return_value = {}
        
        data_source = AlpacaDataSource()
        result = data_source.get_latest_quote("INVALID")
        
        self.assertIsNone(result)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    @patch('builtins.print')
    def test_get_latest_quote_exception(self, mock_print, mock_client_class):
        """Test get_latest_quote when an exception occurs"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock exception
        mock_client.get_stock_latest_quote.side_effect = Exception("API error")
        
        data_source = AlpacaDataSource()
        result = data_source.get_latest_quote("AAPL")
        
        # Verify error was printed and None returned
        mock_print.assert_called_once()
        self.assertIn("Error fetching latest quote for AAPL", mock_print.call_args[0][0])
        self.assertIsNone(result)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_get_supported_intervals(self, mock_client_class):
        """Test get_supported_intervals method"""
        data_source = AlpacaDataSource()
        intervals = data_source.get_supported_intervals()
        
        expected_intervals = ['1m', '2m', '5m', '15m', '30m', '1h', '1d', '1W', '1M']
        self.assertEqual(intervals, expected_intervals)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_validate_symbol_valid(self, mock_client_class):
        """Test validate_symbol with valid symbol"""
        data_source = AlpacaDataSource()
        
        # Mock get_latest_quote to return data
        with patch.object(data_source, 'get_latest_quote', return_value={'symbol': 'AAPL', 'bid_price': 150.0}):
            result = data_source.validate_symbol("AAPL")
            self.assertTrue(result)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_validate_symbol_invalid(self, mock_client_class):
        """Test validate_symbol with invalid symbol"""
        data_source = AlpacaDataSource()
        
        # Mock get_latest_quote to return None
        with patch.object(data_source, 'get_latest_quote', return_value=None):
            result = data_source.validate_symbol("INVALID")
            self.assertFalse(result)
    
    @patch('data_source.alpaca.StockHistoricalDataClient')
    def test_validate_symbol_exception(self, mock_client_class):
        """Test validate_symbol when exception occurs"""
        data_source = AlpacaDataSource()
        
        # Mock get_latest_quote to raise exception
        with patch.object(data_source, 'get_latest_quote', side_effect=Exception("API error")):
            result = data_source.validate_symbol("AAPL")
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()