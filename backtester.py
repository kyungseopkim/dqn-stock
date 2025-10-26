"""
Backtesting Framework for Trading Strategies

This module provides a backtesting engine for testing trading strategies
against historical data with realistic portfolio management.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass

from asset_manager import AssetManager


@dataclass
class Trade:
    """Represents a trade signal from a strategy"""
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: int
    price: float
    timestamp: datetime
    reason: str = ""  # Optional reason for the trade


class Strategy(ABC):
    """
    Abstract base class for trading strategies.

    Subclass this to implement your own trading strategies.
    """

    def __init__(self, name: str):
        self.name = name
        self.data_history = []  # Store historical bars for analysis

    @abstractmethod
    def on_data(self, bar: pd.Series, portfolio: AssetManager) -> Optional[List[Trade]]:
        """
        Called for each bar of data during backtesting.

        Args:
            bar: Current bar data with OHLCV columns
            portfolio: Current portfolio state (read-only for decision making)

        Returns:
            List of Trade objects to execute, or None/empty list for no action
        """
        pass

    def on_start(self, initial_data: pd.DataFrame):
        """
        Called once at the start of backtesting with initial data window.

        Args:
            initial_data: Initial historical data for warming up indicators
        """
        pass

    def on_finish(self, portfolio: AssetManager):
        """
        Called once at the end of backtesting.

        Args:
            portfolio: Final portfolio state
        """
        pass


class BacktestResult:
    """
    Contains the results of a backtest run.
    """

    def __init__(
        self,
        strategy_name: str,
        initial_capital: float,
        final_value: float,
        equity_curve: pd.Series,
        trades: List[Dict],
        daily_returns: pd.Series,
        positions_history: List[Dict]
    ):
        self.strategy_name = strategy_name
        self.initial_capital = initial_capital
        self.final_value = final_value
        self.equity_curve = equity_curve
        self.trades = trades
        self.daily_returns = daily_returns
        self.positions_history = positions_history

    @property
    def total_return(self) -> float:
        """Total return in dollars"""
        return self.final_value - self.initial_capital

    @property
    def total_return_pct(self) -> float:
        """Total return as percentage"""
        return (self.total_return / self.initial_capital) * 100

    @property
    def num_trades(self) -> int:
        """Total number of trades executed"""
        return len(self.trades)

    @property
    def max_drawdown(self) -> float:
        """Maximum drawdown percentage"""
        if len(self.equity_curve) < 2:
            return 0.0

        # Calculate running maximum
        running_max = self.equity_curve.expanding().max()
        drawdown = (self.equity_curve - running_max) / running_max * 100
        return abs(drawdown.min())

    @property
    def sharpe_ratio(self) -> float:
        """
        Sharpe ratio (annualized, assuming daily data).
        Using 0% risk-free rate for simplicity.
        """
        if len(self.daily_returns) < 2:
            return 0.0

        mean_return = self.daily_returns.mean()
        std_return = self.daily_returns.std()

        if std_return == 0:
            return 0.0

        # Annualize (252 trading days)
        sharpe = (mean_return / std_return) * np.sqrt(252)
        return sharpe

    @property
    def win_rate(self) -> float:
        """Percentage of winning trades"""
        if not self.trades:
            return 0.0

        winning_trades = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        return (winning_trades / len(self.trades)) * 100

    def get_metrics(self) -> Dict:
        """Get all performance metrics as a dictionary"""
        return {
            'strategy': self.strategy_name,
            'initial_capital': self.initial_capital,
            'final_value': self.final_value,
            'total_return': self.total_return,
            'total_return_pct': self.total_return_pct,
            'num_trades': self.num_trades,
            'max_drawdown_pct': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'win_rate': self.win_rate,
        }

    def print_summary(self):
        """Print a formatted summary of backtest results"""
        metrics = self.get_metrics()

        print("=" * 70)
        print(f"BACKTEST RESULTS: {self.strategy_name}")
        print("=" * 70)
        print(f"Initial Capital:      ${metrics['initial_capital']:,.2f}")
        print(f"Final Value:          ${metrics['final_value']:,.2f}")
        print(f"Total Return:         ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:+.2f}%)")
        print("-" * 70)
        print(f"Number of Trades:     {metrics['num_trades']}")
        print(f"Win Rate:             {metrics['win_rate']:.2f}%")
        print(f"Max Drawdown:         {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio:         {metrics['sharpe_ratio']:.2f}")
        print("=" * 70)


class Backtester:
    """
    Backtesting engine for trading strategies.

    Simulates trading with historical data and realistic portfolio management.
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_per_trade: float = 0.0,
        max_position_size: float = 0.25,
    ):
        """
        Initialize the backtester.

        Args:
            initial_capital: Starting capital
            commission_per_trade: Commission per trade
            max_position_size: Maximum position size as fraction of portfolio
        """
        self.initial_capital = initial_capital
        self.commission_per_trade = commission_per_trade
        self.max_position_size = max_position_size

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        symbol: str,
        warmup_period: int = 0
    ) -> BacktestResult:
        """
        Run a backtest with the given strategy and data.

        Args:
            strategy: Strategy instance to test
            data: Historical OHLCV data with datetime index
            symbol: Stock symbol being traded
            warmup_period: Number of initial bars to use for indicator warmup

        Returns:
            BacktestResult with performance metrics
        """
        # Initialize portfolio
        portfolio = AssetManager(
            initial_cash=self.initial_capital,
            commission_per_trade=self.commission_per_trade,
            max_position_size=self.max_position_size
        )

        # Ensure data is sorted by time
        data = data.sort_index()

        # Track metrics
        equity_curve = []
        trades_executed = []
        positions_history = []

        # Warm up strategy with initial data
        if warmup_period > 0:
            warmup_data = data.iloc[:warmup_period]
            strategy.on_start(warmup_data)
            start_idx = warmup_period
        else:
            strategy.on_start(data.head(1))
            start_idx = 0

        # Iterate through historical data
        for i in range(start_idx, len(data)):
            bar = data.iloc[i]
            timestamp = bar.name if isinstance(bar.name, datetime) else datetime.now()

            # Get current price for this bar
            current_price = float(bar['Close'])

            # Update portfolio with current prices
            portfolio.update_prices({symbol: current_price})

            # Get trading signals from strategy
            signals = strategy.on_data(bar, portfolio)

            # Execute trades
            if signals:
                for trade in signals:
                    if trade.action.lower() == 'buy':
                        success, msg = portfolio.buy(
                            trade.symbol,
                            trade.quantity,
                            trade.price,
                            timestamp
                        )
                        if success:
                            trades_executed.append({
                                'timestamp': timestamp,
                                'symbol': trade.symbol,
                                'action': 'BUY',
                                'quantity': trade.quantity,
                                'price': trade.price,
                                'reason': trade.reason
                            })

                    elif trade.action.lower() == 'sell':
                        success, msg = portfolio.sell(
                            trade.symbol,
                            trade.quantity,
                            trade.price,
                            timestamp
                        )
                        if success:
                            trades_executed.append({
                                'timestamp': timestamp,
                                'symbol': trade.symbol,
                                'action': 'SELL',
                                'quantity': trade.quantity,
                                'price': trade.price,
                                'reason': trade.reason
                            })

            # Record portfolio value
            equity_curve.append({
                'timestamp': timestamp,
                'portfolio_value': portfolio.portfolio_value,
                'cash': portfolio.cash,
                'positions_value': portfolio.positions_value
            })

            # Record positions
            if portfolio.positions:
                for sym, pos in portfolio.positions.items():
                    positions_history.append({
                        'timestamp': timestamp,
                        'symbol': sym,
                        'quantity': pos.quantity,
                        'price': pos.current_price,
                        'value': pos.market_value
                    })

        # Close all positions at end
        final_bar = data.iloc[-1]
        final_price = float(final_bar['Close'])
        portfolio.update_prices({symbol: final_price})

        if symbol in portfolio.positions:
            portfolio.close_position(symbol, final_price)

        # Finalize strategy
        strategy.on_finish(portfolio)

        # Create equity curve DataFrame
        equity_df = pd.DataFrame(equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        equity_series = equity_df['portfolio_value']

        # Calculate daily returns
        daily_returns = equity_series.pct_change().dropna()

        # Add P&L to trades (match buys with sells)
        # This is simplified - just marks realized P&L from portfolio
        for i, trade in enumerate(trades_executed):
            if trade['action'] == 'SELL':
                # Find the realized P&L from this point
                trade['pnl'] = portfolio.realized_pnl

        # Create result
        result = BacktestResult(
            strategy_name=strategy.name,
            initial_capital=self.initial_capital,
            final_value=portfolio.portfolio_value,
            equity_curve=equity_series,
            trades=trades_executed,
            daily_returns=daily_returns,
            positions_history=positions_history
        )

        return result
