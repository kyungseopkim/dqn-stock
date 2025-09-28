import pandas as pd

from .data_source import DataSource, ABC
import yfinance as yf

# convert MultiIndex ('Price', 'Ticker') to Simple Index ('Price)
def convert_columns(df):
    # create new dataframe
    new_df = pd.DataFrame()

    for col in df.columns.values.tolist():
        new_df[col[0]] = df[col]

    new_df.set_index("Datetime", inplace=True)
    return new_df

class YFinanceDataSource(DataSource):
    def __init__(self):
        self.name = "Yahoo Finance"

    def fetch_data(self, symbol, start_date, end_date):
        """
        Fetch data for a symbol within a specific date range from Yahoo Finance

        Args:
            symbol (str): Stock symbol
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format

        Returns:
            pandas.DataFrame: Data within the specified date range
        """
        try:
            df = yf.download(symbol, start=start_date, end=end_date)
            df.reset_index(inplace=True)
            return convert_columns(df)
        except Exception as e:
            print(f"Error fetching data for {symbol} from {self.name}: {str(e)}")
            return None

    def fetch_one_day_data(self, symbol, date, interval):
        """
        Fetch data for a symbol for a single day from Yahoo Finance

        Args:
            symbol (str): Stock symbol
            date (str): Date in 'YYYY-MM-DD' format
            interval (str): Data interval (e.g., '1m', '5m', '15m', '1h', '1d')

        Returns:
            pandas.DataFrame: Data for the specified day
        """
        try:
            today = pd.to_datetime(date)
            tomorrow = today + pd.Timedelta(days=1)
            df = yf.download(symbol, start=today.strftime('%Y-%m-%d'), end=tomorrow.strftime('%Y-%m-%d'), interval=interval)
            df.reset_index(inplace=True)
            return convert_columns(df)
        except Exception as e:
            print(f"Error fetching one day data for {symbol} on {date} from {self.name}: {str(e)}")
            return None