import os
from abc import ABC

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

from .data_source import DataSource

# Load environment variables
load_dotenv()

def get_database_engine():
    """Create and return a SQLAlchemy database engine"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    if not all([db_name, db_user, db_password]):
        raise ValueError("Database credentials not found. Please set DB_NAME, DB_USER, and DB_PASSWORD in your .env file")
    
    connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    return engine

def check_table_exists(symbol):
    """
    Check if a table exists for the given symbol
    
    Args:
        symbol (str): Stock symbol to check
    
    Returns:
        bool: True if table exists, False otherwise
    """
    engine = get_database_engine()
    
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :symbol"),
                {"symbol": symbol}
            )
            count = result.scalar()
            return count > 0
    except Exception as e:
        print(f"Error checking table existence for {symbol}: {str(e)}")
        return False
    finally:
        engine.dispose()


class DatabaseDataSource(DataSource):
    def __init__(self):
        self.name = "Database"
        self.engine = get_database_engine()

    def _fetch_data_in_date_range(self, symbol, start_date, end_date):
        """
        Fetch data for a symbol within a specific date range

        Args:
            symbol (str): Stock symbol
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format

        Returns:
            pandas.DataFrame: Data within the specified date range
        """
        engine = self.engine
        start_timestamp = pd.to_datetime(start_date)
        end_timestamp = pd.to_datetime(end_date)
        try:
            query = f"""
            SELECT * FROM `{symbol}`
            WHERE timestamp >= :start_timestamp AND timestamp <= :end_timestamp
            ORDER BY timestamp ASC
            """

            with engine.connect() as connection:
                df = pd.read_sql(
                    text(query),
                    connection,
                    params={"start_timestamp": start_timestamp, "end_timestamp": end_timestamp}
                )
                return df
        except Exception as e:
            print(f"Error fetching data for {symbol} in date range: {str(e)}")
            return None
        finally:
            engine.dispose()

    def fetch_data(self, symbol, start_date, end_date):
        return self._fetch_data_in_date_range(symbol, start_date, end_date)

    def fetch_one_day_data(self, symbol, date, interval):
        """
        Fetch data for a symbol for a single day

        Args:
            symbol (str): Stock symbol
            date (str): Date in 'YYYY-MM-DD' format
            interval (str): Data interval (e.g., '1m', '5m', '15m', '1h', '1d')

        Returns:
            pandas.DataFrame: Data for the specified day
        """
        if interval not in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d']:
            print(f"Unsupported interval: {interval}. Supported intervals are: ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d']")
            return None

        engine = self.engine
        start_timestamp = pd.to_datetime(date)
        end_timestamp = start_timestamp + pd.Timedelta(days=1)

        try:
            query = f"""
            SELECT * FROM `{symbol}`
            WHERE timestamp >= :start_timestamp AND timestamp < :end_timestamp
            ORDER BY timestamp ASC
            """

            with engine.connect() as connection:
                df = pd.read_sql(
                    text(query),
                    connection,
                    params={"start_timestamp": start_timestamp, "end_timestamp": end_timestamp}
                )

                if df.empty:
                    print(f"No data found for {symbol} on {date}")
                    return None

                # Resample data based on the specified interval
                df.set_index('timestamp', inplace=True)
                if interval == '1d':
                    resampled_df = df.resample('D').agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    }).dropna().reset_index()
                else:
                    resample_rule = interval.replace('m', 'T').replace('h', 'H')
                    resampled_df = df.resample(resample_rule).agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    }).dropna().reset_index()

                return resampled_df

        except Exception as e:
            print(f"Error fetching one day data for {symbol} on {date}: {str(e)}")
            return None
        finally:
            engine.dispose()