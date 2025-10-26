"""
Example Trading Strategies for Backtesting

This module provides ready-to-use trading strategies for backtesting.
"""

from typing import Optional, List
import pandas as pd
import numpy as np

from backtester import Strategy, Trade
from asset_manager import AssetManager


class BuyAndHoldStrategy(Strategy):
    """
    Simple buy-and-hold strategy.

    Buys on the first bar and holds until the end.
    """

    def __init__(self, symbol: str, position_size: float = 1.0):
        """
        Args:
            symbol: Stock symbol to trade
            position_size: Fraction of capital to invest (0.0-1.0)
        """
        super().__init__("Buy and Hold")
        self.symbol = symbol
        self.position_size = position_size
        self.bought = False

    def on_data(self, bar: pd.Series, portfolio: AssetManager) -> Optional[List[Trade]]:
        """Buy once at the start and hold"""
        if not self.bought:
            price = float(bar['Close'])
            cash_to_invest = portfolio.cash * self.position_size
            quantity = int(cash_to_invest / price)

            if quantity > 0:
                self.bought = True
                return [Trade(
                    symbol=self.symbol,
                    action='buy',
                    quantity=quantity,
                    price=price,
                    timestamp=bar.name,
                    reason="Initial buy and hold"
                )]

        return None


class SMAStrategy(Strategy):
    """
    Simple Moving Average Crossover Strategy.

    Buy when short SMA crosses above long SMA.
    Sell when short SMA crosses below long SMA.
    """

    def __init__(
        self,
        symbol: str,
        short_window: int = 20,
        long_window: int = 50,
        position_size: float = 0.95
    ):
        """
        Args:
            symbol: Stock symbol to trade
            short_window: Short SMA period
            long_window: Long SMA period
            position_size: Fraction of capital to use per trade
        """
        super().__init__(f"SMA({short_window}/{long_window})")
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.position_size = position_size

        self.short_sma = []
        self.long_sma = []
        self.prices = []

    def on_start(self, initial_data: pd.DataFrame):
        """Initialize with historical prices"""
        if len(initial_data) > 0:
            self.prices = list(initial_data['Close'].values)

    def on_data(self, bar: pd.Series, portfolio: AssetManager) -> Optional[List[Trade]]:
        """Execute SMA crossover logic"""
        price = float(bar['Close'])
        self.prices.append(price)

        # Need enough data for long SMA
        if len(self.prices) < self.long_window:
            return None

        # Calculate SMAs
        short_sma = np.mean(self.prices[-self.short_window:])
        long_sma = np.mean(self.prices[-self.long_window:])

        # Previous SMAs for crossover detection
        if len(self.prices) > self.long_window:
            prev_short_sma = np.mean(self.prices[-self.short_window-1:-1])
            prev_long_sma = np.mean(self.prices[-self.long_window-1:-1])
        else:
            # First time we have enough data
            return None

        position = portfolio.get_position(self.symbol)

        # Buy signal: short crosses above long
        if prev_short_sma <= prev_long_sma and short_sma > long_sma:
            if position is None:  # No position yet
                cash_to_invest = portfolio.cash * self.position_size
                quantity = int(cash_to_invest / price)

                if quantity > 0:
                    return [Trade(
                        symbol=self.symbol,
                        action='buy',
                        quantity=quantity,
                        price=price,
                        timestamp=bar.name,
                        reason=f"SMA crossover: buy signal ({short_sma:.2f} > {long_sma:.2f})"
                    )]

        # Sell signal: short crosses below long
        elif prev_short_sma >= prev_long_sma and short_sma < long_sma:
            if position is not None:  # Have a position
                return [Trade(
                    symbol=self.symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=price,
                    timestamp=bar.name,
                    reason=f"SMA crossover: sell signal ({short_sma:.2f} < {long_sma:.2f})"
                )]

        return None


class RSIStrategy(Strategy):
    """
    RSI (Relative Strength Index) Mean Reversion Strategy.

    Buy when RSI drops below oversold level.
    Sell when RSI rises above overbought level.
    """

    def __init__(
        self,
        symbol: str,
        period: int = 14,
        oversold: float = 30,
        overbought: float = 70,
        position_size: float = 0.95
    ):
        """
        Args:
            symbol: Stock symbol to trade
            period: RSI calculation period
            oversold: RSI level to trigger buy (typically 30)
            overbought: RSI level to trigger sell (typically 70)
            position_size: Fraction of capital to use per trade
        """
        super().__init__(f"RSI({period})")
        self.symbol = symbol
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.position_size = position_size

        self.prices = []
        self.gains = []
        self.losses = []

    def _calculate_rsi(self) -> Optional[float]:
        """Calculate RSI value"""
        if len(self.prices) < self.period + 1:
            return None

        # Calculate price changes
        recent_prices = self.prices[-(self.period + 1):]
        changes = [recent_prices[i] - recent_prices[i-1] for i in range(1, len(recent_prices))]

        # Separate gains and losses
        gains = [max(0, change) for change in changes]
        losses = [abs(min(0, change)) for change in changes]

        # Average gain and loss
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def on_start(self, initial_data: pd.DataFrame):
        """Initialize with historical prices"""
        if len(initial_data) > 0:
            self.prices = list(initial_data['Close'].values)

    def on_data(self, bar: pd.Series, portfolio: AssetManager) -> Optional[List[Trade]]:
        """Execute RSI mean reversion logic"""
        price = float(bar['Close'])
        self.prices.append(price)

        rsi = self._calculate_rsi()
        if rsi is None:
            return None

        position = portfolio.get_position(self.symbol)

        # Buy signal: RSI oversold
        if rsi < self.oversold and position is None:
            cash_to_invest = portfolio.cash * self.position_size
            quantity = int(cash_to_invest / price)

            if quantity > 0:
                return [Trade(
                    symbol=self.symbol,
                    action='buy',
                    quantity=quantity,
                    price=price,
                    timestamp=bar.name,
                    reason=f"RSI oversold: {rsi:.2f} < {self.oversold}"
                )]

        # Sell signal: RSI overbought
        elif rsi > self.overbought and position is not None:
            return [Trade(
                symbol=self.symbol,
                action='sell',
                quantity=position.quantity,
                price=price,
                timestamp=bar.name,
                reason=f"RSI overbought: {rsi:.2f} > {self.overbought}"
            )]

        return None


class MomentumStrategy(Strategy):
    """
    Momentum Strategy.

    Buy when price momentum is positive over a lookback period.
    Sell when momentum turns negative.
    """

    def __init__(
        self,
        symbol: str,
        lookback: int = 20,
        position_size: float = 0.95
    ):
        """
        Args:
            symbol: Stock symbol to trade
            lookback: Number of periods for momentum calculation
            position_size: Fraction of capital to use per trade
        """
        super().__init__(f"Momentum({lookback})")
        self.symbol = symbol
        self.lookback = lookback
        self.position_size = position_size
        self.prices = []

    def on_start(self, initial_data: pd.DataFrame):
        """Initialize with historical prices"""
        if len(initial_data) > 0:
            self.prices = list(initial_data['Close'].values)

    def on_data(self, bar: pd.Series, portfolio: AssetManager) -> Optional[List[Trade]]:
        """Execute momentum logic"""
        price = float(bar['Close'])
        self.prices.append(price)

        if len(self.prices) < self.lookback + 1:
            return None

        # Calculate momentum (% change over lookback period)
        momentum = (price / self.prices[-self.lookback-1] - 1) * 100

        position = portfolio.get_position(self.symbol)

        # Buy signal: positive momentum
        if momentum > 0 and position is None:
            cash_to_invest = portfolio.cash * self.position_size
            quantity = int(cash_to_invest / price)

            if quantity > 0:
                return [Trade(
                    symbol=self.symbol,
                    action='buy',
                    quantity=quantity,
                    price=price,
                    timestamp=bar.name,
                    reason=f"Positive momentum: {momentum:.2f}%"
                )]

        # Sell signal: negative momentum
        elif momentum < 0 and position is not None:
            return [Trade(
                symbol=self.symbol,
                action='sell',
                quantity=position.quantity,
                price=price,
                timestamp=bar.name,
                reason=f"Negative momentum: {momentum:.2f}%"
            )]

        return None
