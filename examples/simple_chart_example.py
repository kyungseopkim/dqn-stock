import pandas as pd

from data_source import AlpacaDataSource
#import plotly.graph_objects as go

from data_source.yfinance import YFinanceDataSource
import mplfinance as mpf
#from tabulate import tabulate




def main():
    print("Hello from dqn-stock!")
    alpaca = AlpacaDataSource()
    ticker = "AAPL"
    df = alpaca.fetch_one_day_data(ticker, "2025-09-12", "1m")

    if df is not None:
        mpf.plot(
            df,
            type="ohlc",  # Use OHLC (open, high, low, close) to create the bars
            volume=True,
            title=f"{ticker} OHLC Chart",
        )

if __name__ == "__main__":
    main()
