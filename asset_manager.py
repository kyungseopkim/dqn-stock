"""
Asset Manager for Day Trading

This module provides portfolio management capabilities for day trading, including:
- Position tracking and management
- Order execution (buy/sell)
- Transaction history logging
- P&L calculation
- Risk management (position limits, validation)
"""

from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import pandas as pd


class OrderType(Enum):
    """Order types supported by the asset manager"""
    MARKET = "market"
    LIMIT = "limit"


class OrderSide(Enum):
    """Order side (buy or sell)"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Transaction:
    """
    Represents a single transaction (trade execution)

    Attributes:
        timestamp: When the transaction occurred
        symbol: Stock symbol
        side: Buy or sell
        quantity: Number of shares
        price: Execution price per share
        commission: Trading commission/fees
        total_value: Total transaction value (quantity * price + commission)
    """
    timestamp: datetime
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    commission: float = 0.0

    @property
    def total_value(self) -> float:
        """Calculate total transaction value including commission"""
        base_value = self.quantity * self.price
        if self.side == OrderSide.BUY:
            return base_value + self.commission
        else:  # SELL
            return base_value - self.commission

    def __repr__(self) -> str:
        return (f"Transaction({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"{self.symbol}, {self.side.value.upper()}, "
                f"{self.quantity}@${self.price:.2f}, total=${self.total_value:.2f})")


@dataclass
class Position:
    """
    Represents a position in a single stock

    Attributes:
        symbol: Stock symbol
        quantity: Number of shares held
        average_price: Average cost basis per share
        current_price: Current market price per share
    """
    symbol: str
    quantity: int
    average_price: float
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        """Current market value of the position"""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        """Total cost basis of the position"""
        return self.quantity * self.average_price

    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss"""
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_pct(self) -> float:
        """Unrealized P&L as percentage"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100

    def update_price(self, new_price: float):
        """Update the current market price"""
        self.current_price = new_price

    def __repr__(self) -> str:
        return (f"Position({self.symbol}, qty={self.quantity}, "
                f"avg=${self.average_price:.2f}, curr=${self.current_price:.2f}, "
                f"P&L=${self.unrealized_pnl:.2f} ({self.unrealized_pnl_pct:+.2f}%))")


class AssetManager:
    """
    Asset Manager for day trading portfolio management

    Features:
    - Track cash balance and buying power
    - Manage stock positions
    - Execute buy/sell orders
    - Track transaction history
    - Calculate P&L and portfolio metrics
    - Risk management (position limits)
    """

    def __init__(
        self,
        initial_cash: float = 100000.0,
        max_position_size: float = 0.25,  # Max 25% of portfolio per position
        commission_per_trade: float = 0.0,  # Commission per trade
    ):
        """
        Initialize the Asset Manager

        Args:
            initial_cash: Starting cash balance
            max_position_size: Maximum position size as fraction of portfolio (0.0-1.0)
            commission_per_trade: Commission/fee per trade
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.max_position_size = max_position_size
        self.commission_per_trade = commission_per_trade

        # Portfolio state
        self.positions: Dict[str, Position] = {}
        self.transactions: List[Transaction] = []
        self.realized_pnl = 0.0

    @property
    def portfolio_value(self) -> float:
        """Total portfolio value (cash + positions)"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value

    @property
    def buying_power(self) -> float:
        """Available buying power (currently just cash)"""
        return self.cash

    @property
    def positions_value(self) -> float:
        """Total value of all positions"""
        return sum(pos.market_value for pos in self.positions.values())

    @property
    def unrealized_pnl(self) -> float:
        """Total unrealized P&L across all positions"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())

    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)"""
        return self.realized_pnl + self.unrealized_pnl

    @property
    def total_pnl_pct(self) -> float:
        """Total P&L as percentage of initial capital"""
        return (self.total_pnl / self.initial_cash) * 100

    def update_prices(self, prices: Dict[str, float]):
        """
        Update current market prices for all positions

        Args:
            prices: Dictionary mapping symbols to current prices
        """
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.update_price(prices[symbol])

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol, or None if no position exists"""
        return self.positions.get(symbol)

    def _validate_buy_order(self, symbol: str, quantity: int, price: float) -> tuple[bool, str]:
        """
        Validate a buy order

        Returns:
            (is_valid, error_message)
        """
        if quantity <= 0:
            return False, "Quantity must be positive"

        total_cost = (quantity * price) + self.commission_per_trade

        if total_cost > self.cash:
            return False, f"Insufficient funds: need ${total_cost:.2f}, have ${self.cash:.2f}"

        # Check position size limit
        position_value = quantity * price
        max_allowed = self.portfolio_value * self.max_position_size

        if symbol in self.positions:
            current_value = self.positions[symbol].market_value
            new_total_value = current_value + position_value
            if new_total_value > max_allowed:
                return False, (f"Position size limit exceeded: new position would be "
                             f"${new_total_value:.2f}, max allowed ${max_allowed:.2f}")
        elif position_value > max_allowed:
            return False, (f"Position size limit exceeded: ${position_value:.2f} "
                         f"exceeds max ${max_allowed:.2f}")

        return True, ""

    def _validate_sell_order(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """
        Validate a sell order

        Returns:
            (is_valid, error_message)
        """
        if quantity <= 0:
            return False, "Quantity must be positive"

        if symbol not in self.positions:
            return False, f"No position in {symbol} to sell"

        position = self.positions[symbol]
        if quantity > position.quantity:
            return False, (f"Insufficient shares: trying to sell {quantity}, "
                         f"but only have {position.quantity}")

        return True, ""

    def buy(
        self,
        symbol: str,
        quantity: int,
        price: float,
        timestamp: Optional[datetime] = None
    ) -> tuple[bool, str]:
        """
        Execute a buy order

        Args:
            symbol: Stock symbol to buy
            quantity: Number of shares to buy
            price: Price per share
            timestamp: Transaction timestamp (defaults to now)

        Returns:
            (success, message)
        """
        # Validate order
        is_valid, error_msg = self._validate_buy_order(symbol, quantity, price)
        if not is_valid:
            return False, error_msg

        # Calculate costs
        cost = quantity * price
        total_cost = cost + self.commission_per_trade

        # Update cash
        self.cash -= total_cost

        # Update or create position
        if symbol in self.positions:
            position = self.positions[symbol]
            # Calculate new average price
            total_shares = position.quantity + quantity
            total_cost_basis = position.cost_basis + cost
            new_avg_price = total_cost_basis / total_shares

            position.quantity = total_shares
            position.average_price = new_avg_price
            position.current_price = price
        else:
            # Create new position
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                average_price=price,
                current_price=price
            )

        # Record transaction
        transaction = Transaction(
            timestamp=timestamp or datetime.now(),
            symbol=symbol,
            side=OrderSide.BUY,
            quantity=quantity,
            price=price,
            commission=self.commission_per_trade
        )
        self.transactions.append(transaction)

        return True, f"Bought {quantity} shares of {symbol} @ ${price:.2f}"

    def sell(
        self,
        symbol: str,
        quantity: int,
        price: float,
        timestamp: Optional[datetime] = None
    ) -> tuple[bool, str]:
        """
        Execute a sell order

        Args:
            symbol: Stock symbol to sell
            quantity: Number of shares to sell
            price: Price per share
            timestamp: Transaction timestamp (defaults to now)

        Returns:
            (success, message)
        """
        # Validate order
        is_valid, error_msg = self._validate_sell_order(symbol, quantity)
        if not is_valid:
            return False, error_msg

        position = self.positions[symbol]

        # Calculate proceeds and realized P&L
        proceeds = quantity * price - self.commission_per_trade
        cost_basis = quantity * position.average_price
        realized_pnl = proceeds - cost_basis

        # Update cash and realized P&L
        self.cash += proceeds
        self.realized_pnl += realized_pnl

        # Update position
        position.quantity -= quantity

        # Remove position if fully closed
        if position.quantity == 0:
            del self.positions[symbol]
        else:
            position.current_price = price

        # Record transaction
        transaction = Transaction(
            timestamp=timestamp or datetime.now(),
            symbol=symbol,
            side=OrderSide.SELL,
            quantity=quantity,
            price=price,
            commission=self.commission_per_trade
        )
        self.transactions.append(transaction)

        return True, (f"Sold {quantity} shares of {symbol} @ ${price:.2f}, "
                     f"realized P&L: ${realized_pnl:.2f}")

    def close_position(self, symbol: str, price: float) -> tuple[bool, str]:
        """
        Close entire position in a symbol

        Args:
            symbol: Stock symbol
            price: Current price to sell at

        Returns:
            (success, message)
        """
        if symbol not in self.positions:
            return False, f"No position in {symbol}"

        quantity = self.positions[symbol].quantity
        return self.sell(symbol, quantity, price)

    def close_all_positions(self, prices: Dict[str, float]) -> List[str]:
        """
        Close all positions at given prices

        Args:
            prices: Dictionary mapping symbols to current prices

        Returns:
            List of result messages
        """
        results = []
        symbols_to_close = list(self.positions.keys())

        for symbol in symbols_to_close:
            if symbol in prices:
                success, msg = self.close_position(symbol, prices[symbol])
                results.append(msg)
            else:
                results.append(f"No price provided for {symbol}, skipping")

        return results

    def get_portfolio_summary(self) -> Dict:
        """
        Get comprehensive portfolio summary

        Returns:
            Dictionary with portfolio metrics
        """
        return {
            'cash': self.cash,
            'positions_value': self.positions_value,
            'portfolio_value': self.portfolio_value,
            'buying_power': self.buying_power,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_pnl': self.total_pnl,
            'total_pnl_pct': self.total_pnl_pct,
            'num_positions': len(self.positions),
            'num_transactions': len(self.transactions),
        }

    def get_positions_df(self) -> pd.DataFrame:
        """
        Get positions as a pandas DataFrame

        Returns:
            DataFrame with position details
        """
        if not self.positions:
            return pd.DataFrame()

        data = []
        for symbol, pos in self.positions.items():
            data.append({
                'Symbol': symbol,
                'Quantity': pos.quantity,
                'Avg Price': pos.average_price,
                'Current Price': pos.current_price,
                'Market Value': pos.market_value,
                'Cost Basis': pos.cost_basis,
                'Unrealized P&L': pos.unrealized_pnl,
                'Unrealized P&L %': pos.unrealized_pnl_pct,
            })

        return pd.DataFrame(data)

    def get_transactions_df(self) -> pd.DataFrame:
        """
        Get transaction history as a pandas DataFrame

        Returns:
            DataFrame with transaction history
        """
        if not self.transactions:
            return pd.DataFrame()

        data = []
        for txn in self.transactions:
            data.append({
                'Timestamp': txn.timestamp,
                'Symbol': txn.symbol,
                'Side': txn.side.value.upper(),
                'Quantity': txn.quantity,
                'Price': txn.price,
                'Commission': txn.commission,
                'Total Value': txn.total_value,
            })

        return pd.DataFrame(data)

    def print_summary(self):
        """Print a formatted portfolio summary"""
        summary = self.get_portfolio_summary()

        print("=" * 60)
        print("PORTFOLIO SUMMARY")
        print("=" * 60)
        print(f"Cash:                ${summary['cash']:,.2f}")
        print(f"Positions Value:     ${summary['positions_value']:,.2f}")
        print(f"Portfolio Value:     ${summary['portfolio_value']:,.2f}")
        print(f"Buying Power:        ${summary['buying_power']:,.2f}")
        print("-" * 60)
        print(f"Unrealized P&L:      ${summary['unrealized_pnl']:,.2f}")
        print(f"Realized P&L:        ${summary['realized_pnl']:,.2f}")
        print(f"Total P&L:           ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.2f}%)")
        print("-" * 60)
        print(f"Positions:           {summary['num_positions']}")
        print(f"Transactions:        {summary['num_transactions']}")
        print("=" * 60)

        if self.positions:
            print("\nCURRENT POSITIONS:")
            print("-" * 60)
            for symbol, pos in self.positions.items():
                print(f"  {pos}")
