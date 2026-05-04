# -*- coding: utf-8 -*-
"""
完整量化交易流程演示
- 无需 MongoDB
- 使用 Akshare 获取真实数据
- Backtrader 回测
- 结果可视化
"""

import backtrader as bt
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 70)
print("     完整量化交易流程演示 - 双均线策略")
print("=" * 70)
print()

# ============ 1. 策略定义 ============
class DualMAStrategy(bt.Strategy):
    """双均线交叉策略"""
    
    params = (
        ('fast_period', 5),
        ('slow_period', 20),
        ('printlog', True),
    )
    
    def __init__(self):
        self.fast_ma = bt.indicators.SMA(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SMA(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.trade_count = 0
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'  [买入] 价格: {order.executed.price:.2f}')
            else:
                print(f'  [卖出] 价格: {order.executed.price:.2f}')
                self.trade_count += 1
        self.order = None
        
    def next(self):
        if self.order:
            return
        if not self.position:
            if self.crossover > 0:
                print(f'{self.data.datetime.date()} 金叉信号')
                self.order = self.buy()
        else:
            if self.crossover < 0:
                print(f'{self.data.datetime.date()} 死叉信号')
                self.order = self.sell()


# ============ 2. 数据获取 ============
print("【步骤1】获取股票数据...")
print()

# 尝试从多个来源获取数据
df = None
stock_code = "002285"  # 世联行

# 方案A: Akshare
try:
    print(f"尝试 Akshare 获取 {stock_code}...")
    df = ak.stock_zh_a_hist(
        symbol=stock_code,
        period="daily",
        start_date="20250101",
        end_date="20260430",
        adjust="qfq"
    )
    
    df = df.rename(columns={
        '日期': 'datetime',
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
    })
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    print(f"  [成功] Akshare 获取 {len(df)} 条数据")
except Exception as e:
    print(f"  [失败] Akshare: {e}")

# 如果网络失败，使用模拟数据
if df is None or len(df) == 0:
    print()
    print("网络不可用，使用模拟数据演示...")
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=200, freq='B')
    base_price = 3.0
    returns = np.random.randn(200) * 0.02 + 0.001
    prices = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(200) * 0.005),
        'high': prices * (1 + abs(np.random.randn(200)) * 0.01),
        'low': prices * (1 - abs(np.random.randn(200)) * 0.01),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 200),
    }, index=dates)
    df['high'] = df[['open', 'close', 'high']].max(axis=1)
    df['low'] = df[['open', 'close', 'low']].min(axis=1)
    print(f"  [成功] 生成 {len(df)} 条模拟数据")

print(f"  时间范围: {df.index[0].date()} ~ {df.index[-1].date()}")
print(f"  价格范围: {df['close'].min():.2f} ~ {df['close'].max():.2f}")
print()


# ============ 3. 回测配置 ============
print("【步骤2】配置回测引擎...")

cerebro = bt.Cerebro()
cerebro.addstrategy(DualMAStrategy, fast_period=5, slow_period=20)

data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

cerebro.broker.setcash(100000.0)
cerebro.broker.setcommission(commission=0.0003)

cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

print(f"  初始资金: 100,000.00")
print(f"  策略: 双均线交叉 (MA5/MA20)")
print(f"  手续费: 万分之三")
print()


# ============ 4. 执行回测 ============
print("【步骤3】执行回测...")
print("-" * 70)

initial = cerebro.broker.getvalue()
results = cerebro.run()
final = cerebro.broker.getvalue()

print("-" * 70)
print()


# ============ 5. 结果分析 ============
print("【步骤4】回测结果")
print("=" * 70)

strat = results[0]

print(f"  初始资金: {initial:,.2f}")
print(f"  期末资金: {final:,.2f}")
print(f"  总收益:   {final - initial:,.2f}")
print(f"  收益率:   {(final / initial - 1) * 100:.2f}%")
print()

# 夏普比率
sharpe = strat.analyzers.sharpe.get_analysis()
sharpe_val = sharpe.get('sharperatio')
print(f"  夏普比率: {sharpe_val:.3f}" if sharpe_val else "  夏普比率: N/A")

# 最大回撤
dd = strat.analyzers.drawdown.get_analysis()
print(f"  最大回撤: {dd.get('max', {}).get('drawdown', 0):.2f}%")

# 交易统计
trades = strat.analyzers.trades.get_analysis()
total = trades.get('total', {}).get('total', 0)
won = trades.get('won', {}).get('total', 0)
lost = trades.get('lost', {}).get('total', 0)
print(f"  总交易:   {total} 次")
print(f"  盈利:     {won} 次")
print(f"  亏损:     {lost} 次")
if total > 0:
    print(f"  胜率:     {won / total * 100:.1f}%")

print()
print("=" * 70)
print("回测完成!")
