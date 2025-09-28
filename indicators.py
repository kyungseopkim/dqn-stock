import pandas as pd
from stockstats import StockDataFrame
from typing import List, Optional, Dict, Any

def generate_technical_indicators(
    df: pd.DataFrame,
    indicators: Optional[List[str]] = None,
    price_columns: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Generate technical indicators for stock data using stockstats
    
    Args:
        df (pd.DataFrame): Stock data with OHLCV columns
        indicators (List[str], optional): List of indicators to generate. 
                                        If None, generates common indicators
        price_columns (Dict[str, str], optional): Column mapping for price data.
                                                Default: {'open': 'open', 'high': 'high', 
                                                         'low': 'low', 'close': 'close', 
                                                         'volume': 'volume'}
    
    Returns:
        pd.DataFrame: DataFrame with original data and technical indicators
    """
    # Make a copy of the original dataframe
    data = df.copy()
    
    # Default column mapping
    if price_columns is None:
        price_columns = {
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        }
    
    # Rename columns to stockstats standard format if needed
    column_mapping = {}
    for std_name, actual_name in price_columns.items():
        if actual_name in data.columns:
            column_mapping[actual_name] = std_name
    
    if column_mapping:
        data = data.rename(columns=column_mapping)
    
    # Convert to StockDataFrame
    stock_df = StockDataFrame.retype(data)
    
    # Default indicators if none specified
    if indicators is None:
        indicators = [
            # Moving Averages
            'close_5_sma',    # 5-day Simple Moving Average
            'close_10_sma',   # 10-day Simple Moving Average
            'close_20_sma',   # 20-day Simple Moving Average
            'close_50_sma',   # 50-day Simple Moving Average
            'close_5_ema',    # 5-day Exponential Moving Average
            'close_10_ema',   # 10-day Exponential Moving Average
            'close_20_ema',   # 20-day Exponential Moving Average
            
            # Bollinger Bands
            'boll_ub',        # Bollinger Upper Band
            'boll_lb',        # Bollinger Lower Band
            
            # RSI
            'rsi_14',         # 14-day RSI
            'rsi_6',          # 6-day RSI
            
            # MACD
            'macd',           # MACD line
            'macds',          # MACD signal line
            'macdh',          # MACD histogram
            
            # Stochastic
            'kdjk',           # %K
            'kdjd',           # %D
            'kdjj',           # %J
            
            # Other indicators
            'wr_14',          # Williams %R
            'cci_14',         # Commodity Channel Index
            'atr_14',         # Average True Range
            'obv',            # On Balance Volume
        ]
    
    # Generate indicators
    for indicator in indicators:
        try:
            # Access the indicator to trigger calculation
            _ = stock_df[indicator]
        except Exception as e:
            print(f"Warning: Could not calculate {indicator}: {str(e)}")
            continue
    
    return stock_df

def get_common_indicators() -> Dict[str, List[str]]:
    """
    Get categorized list of common technical indicators
    
    Returns:
        Dict[str, List[str]]: Dictionary with indicator categories
    """
    return {
        'moving_averages': [
            'close_5_sma', 'close_10_sma', 'close_20_sma', 'close_50_sma',
            'close_5_ema', 'close_10_ema', 'close_20_ema', 'close_50_ema'
        ],
        'bollinger_bands': [
            'boll', 'boll_ub', 'boll_lb'
        ],
        'momentum': [
            'rsi_6', 'rsi_14', 'rsi_21',
            'wr_6', 'wr_10', 'wr_14',
            'cci_14', 'cci_20'
        ],
        'macd': [
            'macd', 'macds', 'macdh'
        ],
        'stochastic': [
            'kdjk', 'kdjd', 'kdjj'
        ],
        'volume': [
            'obv', 'volume_delta'
        ],
        'volatility': [
            'atr_14', 'atr_20'
        ],
        'trend': [
            'adx', 'adxr', 'dx'
        ]
    }

def generate_custom_indicators(
    df: pd.DataFrame,
    sma_periods: List[int] = [5, 10, 20, 50],
    ema_periods: List[int] = [5, 10, 20],
    rsi_periods: List[int] = [6, 14],
    bollinger_period: int = 20,
    macd_params: tuple = (12, 26, 9)
) -> pd.DataFrame:
    """
    Generate custom technical indicators with specific periods
    
    Args:
        df (pd.DataFrame): Stock data
        sma_periods (List[int]): Periods for Simple Moving Averages
        ema_periods (List[int]): Periods for Exponential Moving Averages
        rsi_periods (List[int]): Periods for RSI
        bollinger_period (int): Period for Bollinger Bands
        macd_params (tuple): MACD parameters (fast, slow, signal)
    
    Returns:
        pd.DataFrame: DataFrame with custom indicators
    """
    data = df.copy()
    stock_df = StockDataFrame.retype(data)
    
    indicators = []
    
    # Simple Moving Averages
    for period in sma_periods:
        indicators.append(f'close_{period}_sma')
    
    # Exponential Moving Averages
    for period in ema_periods:
        indicators.append(f'close_{period}_ema')
    
    # RSI
    for period in rsi_periods:
        indicators.append(f'rsi_{period}')
    
    # Bollinger Bands
    indicators.extend([f'boll_{bollinger_period}', f'boll_{bollinger_period}_ub', f'boll_{bollinger_period}_lb'])
    
    # MACD with custom parameters
    fast, slow, signal = macd_params
    indicators.extend([f'macd_{fast}_{slow}_{signal}', f'macds_{fast}_{slow}_{signal}', f'macdh_{fast}_{slow}_{signal}'])
    
    # Generate indicators
    for indicator in indicators:
        try:
            _ = stock_df[indicator]
        except Exception as e:
            print(f"Warning: Could not calculate {indicator}: {str(e)}")
            continue
    
    return stock_df

def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add basic price-based features to the dataframe
    
    Args:
        df (pd.DataFrame): Stock data with OHLCV
    
    Returns:
        pd.DataFrame: DataFrame with additional price features
    """
    data = df.copy()
    
    # Price change features
    data['price_change'] = data['close'] - data['open']
    data['price_change_pct'] = (data['close'] - data['open']) / data['open'] * 100
    data['high_low_pct'] = (data['high'] - data['low']) / data['low'] * 100
    
    # Previous day features
    data['prev_close'] = data['close'].shift(1)
    data['gap'] = data['open'] - data['prev_close']
    data['gap_pct'] = (data['open'] - data['prev_close']) / data['prev_close'] * 100
    
    # Volatility features
    data['true_range'] = data[['high', 'low', 'close']].apply(
        lambda x: max(x['high'] - x['low'], 
                     abs(x['high'] - data['close'].shift(1).loc[x.name]) if pd.notna(data['close'].shift(1).loc[x.name]) else 0,
                     abs(x['low'] - data['close'].shift(1).loc[x.name]) if pd.notna(data['close'].shift(1).loc[x.name]) else 0), 
        axis=1
    )
    
    return data