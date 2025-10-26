"""
Visualization tools for backtest results.

This module provides functions to visualize backtesting performance.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List
from backtester import BacktestResult


def plot_equity_curve(result: BacktestResult, show: bool = True):
    """
    Plot the equity curve from a backtest result.

    Args:
        result: BacktestResult object
        show: Whether to display the plot immediately
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot equity curve
    ax.plot(result.equity_curve.index, result.equity_curve.values,
            label=result.strategy_name, linewidth=2)

    # Add horizontal line for initial capital
    ax.axhline(y=result.initial_capital, color='gray', linestyle='--',
               alpha=0.7, label='Initial Capital')

    # Format
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax.set_title(f'Equity Curve: {result.strategy_name}', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Add performance text
    textstr = f'Total Return: ${result.total_return:,.2f} ({result.total_return_pct:+.2f}%)\n'
    textstr += f'Max Drawdown: {result.max_drawdown:.2f}%\n'
    textstr += f'Sharpe Ratio: {result.sharpe_ratio:.2f}'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def plot_drawdown(result: BacktestResult, show: bool = True):
    """
    Plot the drawdown curve from a backtest result.

    Args:
        result: BacktestResult object
        show: Whether to display the plot immediately
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Calculate drawdown
    running_max = result.equity_curve.expanding().max()
    drawdown = (result.equity_curve - running_max) / running_max * 100

    # Plot drawdown
    ax.fill_between(drawdown.index, drawdown.values, 0,
                     alpha=0.3, color='red', label='Drawdown')
    ax.plot(drawdown.index, drawdown.values, color='red', linewidth=1)

    # Format
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.set_title(f'Drawdown: {result.strategy_name}', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Add max drawdown text
    textstr = f'Max Drawdown: {result.max_drawdown:.2f}%'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', bbox=props)

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def plot_returns_distribution(result: BacktestResult, show: bool = True):
    """
    Plot the distribution of daily returns.

    Args:
        result: BacktestResult object
        show: Whether to display the plot immediately
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot histogram
    ax.hist(result.daily_returns.values * 100, bins=50, alpha=0.75,
            edgecolor='black', color='steelblue')

    # Add vertical line at 0
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Return')

    # Format
    ax.set_xlabel('Daily Return (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Daily Returns Distribution: {result.strategy_name}',
                 fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, axis='y')

    # Add statistics text
    mean_return = result.daily_returns.mean() * 100
    std_return = result.daily_returns.std() * 100
    textstr = f'Mean: {mean_return:.3f}%\nStd Dev: {std_return:.3f}%'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.98, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def plot_comparison(results: List[BacktestResult], show: bool = True):
    """
    Plot equity curves for multiple strategies for comparison.

    Args:
        results: List of BacktestResult objects
        show: Whether to display the plot immediately
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot each equity curve
    for result in results:
        # Normalize to percentage returns
        normalized = (result.equity_curve / result.initial_capital - 1) * 100
        ax.plot(normalized.index, normalized.values,
                label=result.strategy_name, linewidth=2)

    # Add horizontal line at 0%
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7, label='Break Even')

    # Format
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Return (%)', fontsize=12)
    ax.set_title('Strategy Comparison', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def plot_trade_analysis(result: BacktestResult, price_data: pd.DataFrame, show: bool = True):
    """
    Plot price chart with buy/sell markers.

    Args:
        result: BacktestResult object
        price_data: Original price DataFrame with Close column
        show: Whether to display the plot immediately
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot price
    ax.plot(price_data.index, price_data['Close'], label='Price',
            linewidth=1.5, color='black', alpha=0.7)

    # Mark buy and sell points
    buys = [t for t in result.trades if t['action'] == 'BUY']
    sells = [t for t in result.trades if t['action'] == 'SELL']

    if buys:
        buy_dates = [t['timestamp'] for t in buys]
        buy_prices = [t['price'] for t in buys]
        ax.scatter(buy_dates, buy_prices, marker='^', color='green',
                   s=100, label='Buy', zorder=5)

    if sells:
        sell_dates = [t['timestamp'] for t in sells]
        sell_prices = [t['price'] for t in sells]
        ax.scatter(sell_dates, sell_prices, marker='v', color='red',
                   s=100, label='Sell', zorder=5)

    # Format
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.set_title(f'Trade Analysis: {result.strategy_name}', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def create_performance_report(result: BacktestResult, price_data: pd.DataFrame):
    """
    Create a comprehensive performance report with multiple charts.

    Args:
        result: BacktestResult object
        price_data: Original price DataFrame
    """
    fig = plt.figure(figsize=(16, 12))

    # Equity curve
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(result.equity_curve.index, result.equity_curve.values, linewidth=2)
    ax1.axhline(y=result.initial_capital, color='gray', linestyle='--', alpha=0.7)
    ax1.set_title('Equity Curve', fontweight='bold')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # Drawdown
    ax2 = plt.subplot(3, 2, 2)
    running_max = result.equity_curve.expanding().max()
    drawdown = (result.equity_curve - running_max) / running_max * 100
    ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    ax2.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
    ax2.set_title('Drawdown', fontweight='bold')
    ax2.set_ylabel('Drawdown (%)')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    # Returns distribution
    ax3 = plt.subplot(3, 2, 3)
    ax3.hist(result.daily_returns.values * 100, bins=40, alpha=0.75,
             edgecolor='black', color='steelblue')
    ax3.axvline(x=0, color='red', linestyle='--', linewidth=2)
    ax3.set_title('Daily Returns Distribution', fontweight='bold')
    ax3.set_xlabel('Daily Return (%)')
    ax3.set_ylabel('Frequency')
    ax3.grid(True, alpha=0.3, axis='y')

    # Trade markers
    ax4 = plt.subplot(3, 2, 4)
    ax4.plot(price_data.index, price_data['Close'], linewidth=1.5,
             color='black', alpha=0.7)
    buys = [t for t in result.trades if t['action'] == 'BUY']
    sells = [t for t in result.trades if t['action'] == 'SELL']
    if buys:
        buy_dates = [t['timestamp'] for t in buys]
        buy_prices = [t['price'] for t in buys]
        ax4.scatter(buy_dates, buy_prices, marker='^', color='green', s=100, zorder=5)
    if sells:
        sell_dates = [t['timestamp'] for t in sells]
        sell_prices = [t['price'] for t in sells]
        ax4.scatter(sell_dates, sell_prices, marker='v', color='red', s=100, zorder=5)
    ax4.set_title('Price with Trade Signals', fontweight='bold')
    ax4.set_ylabel('Price ($)')
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

    # Performance metrics table
    ax5 = plt.subplot(3, 2, (5, 6))
    ax5.axis('off')

    metrics = result.get_metrics()
    table_data = [
        ['Initial Capital', f"${metrics['initial_capital']:,.2f}"],
        ['Final Value', f"${metrics['final_value']:,.2f}"],
        ['Total Return', f"${metrics['total_return']:,.2f} ({metrics['total_return_pct']:+.2f}%)"],
        ['Number of Trades', f"{metrics['num_trades']}"],
        ['Win Rate', f"{metrics['win_rate']:.2f}%"],
        ['Max Drawdown', f"{metrics['max_drawdown_pct']:.2f}%"],
        ['Sharpe Ratio', f"{metrics['sharpe_ratio']:.2f}"],
    ]

    table = ax5.table(cellText=table_data, cellLoc='left',
                      colWidths=[0.4, 0.4], loc='center',
                      bbox=[0.1, 0.2, 0.8, 0.6])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)

    # Style the table
    for i in range(len(table_data)):
        table[(i, 0)].set_facecolor('#E8E8E8')
        table[(i, 0)].set_text_props(weight='bold')

    ax5.set_title('Performance Metrics', fontweight='bold', fontsize=14, pad=20)

    plt.suptitle(f'Backtest Report: {result.strategy_name}',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.show()

    return fig
