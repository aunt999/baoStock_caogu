# -*- coding: utf-8 -*-
"""
Backtrader 均线交叉策略完整演示（本地数据版）
- 生成模拟数据演示回测流程
- 双均线金叉/死叉策略
- 完整回测输出
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("    Backtrader 双均线交叉策略回测演示")
print("=" * 60)
print()

# ============ 1. 定义策略 ============
class DualMAStrategy(bt.Strategy):
    """双均线交叉策略"""
    
    params = (
        ('fast_period', 5),   # 快线周期
        ('slow_period', 20),  # 慢线周期
        ('printlog', True),
    )
    
    def __init__(self):
        # 计算均线
        self.fast_ma = bt.indicators.SMA(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SMA(
            self.data.close, period=self.params.slow_period
        )
        
        # 均线交叉信号
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        
        # 记录订单
        self.order = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'  【买入执行】价格: {order.executed.price:.2f}')
            else:
                print(f'  【卖出执行】价格: {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('  订单取消/拒绝')
            
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        # 没有持仓
        if not self.position:
            # 金叉买入
            if self.crossover > 0:
                print(f'{self.data.datetime.date()} 【金叉信号】'
                      f' MA5={self.fast_ma[0]:.2f} > MA20={self.slow_ma[0]:.2f}')
                self.order = self.buy()
        else:
            # 死叉卖出
            if self.crossover < 0:
                print(f'{self.data.datetime.date()} 【死叉信号】'
                      f' MA5={self.fast_ma[0]:.2f} < MA20={self.slow_ma[0]:.2f}')
                self.order = self.sell()


# ============ 2. 生成模拟数据 ============
print("【步骤1】生成模拟股票数据...")

# 生成300个交易日的模拟数据
np.random.seed(42)
dates = pd.date_range(start='2025-01-01', periods=300, freq='B')  # 工作日

# 模拟股价：随机游走 + 趋势
base_price = 3.0
returns = np.random.randn(300) * 0.02 + 0.0005  # 日收益率
prices = base_price * np.exp(np.cumsum(returns))

# 生成OHLCV数据
df = pd.DataFrame({
    'open': prices * (1 + np.random.randn(300) * 0.005),
    'high': prices * (1 + abs(np.random.randn(300)) * 0.01),
    'low': prices * (1 - abs(np.random.randn(300)) * 0.01),
    'close': prices,
    'volume': np.random.randint(1000000, 10000000, 300),
}, index=dates)

# 确保high/low正确
df['high'] = df[['open', 'close', 'high']].max(axis=1)
df['low'] = df[['open', 'close', 'low']].min(axis=1)

print(f"  生成 {len(df)} 条模拟数据")
print(f"  时间范围: {df.index[0].date()} ~ {df.index[-1].date()}")
print(f"  价格范围: {df['close'].min():.2f} ~ {df['close'].max():.2f}")
print()


# ============ 3. 创建回测引擎 ============
print("【步骤2】配置回测引擎...")
cerebro = bt.Cerebro()

# 添加策略
cerebro.addstrategy(DualMAStrategy, fast_period=5, slow_period=20)

# 添加数据
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# 设置初始资金
cerebro.broker.setcash(100000.0)

# 设置手续费（万分之三）
cerebro.broker.setcommission(commission=0.0003)

# 添加分析指标
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

print(f"  初始资金: {cerebro.broker.getvalue():,.2f}")
print(f"  策略: 双均线交叉 (MA5/MA20)")
print(f"  手续费: 万分之三")
print()


# ============ 4. 运行回测 ============
print("【步骤3】执行回测...")
print("-" * 60)
results = cerebro.run()
print("-" * 60)
print()


# ============ 5. 输出结果 ============
print("【步骤4】回测结果分析")
print("=" * 60)

strat = results[0]

# 资金变化
final_value = cerebro.broker.getvalue()
print(f"  期末资金: {final_value:,.2f}")
print(f"  总收益:   {final_value - 100000:,.2f}")
print(f"  收益率:   {(final_value / 100000 - 1) * 100:.2f}%")
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
total_trades = trades.get('total', {}).get('total', 0)
won_trades = trades.get('won', {}).get('total', 0)
lost_trades = trades.get('lost', {}).get('total', 0)
print(f"  总交易次数: {total_trades}")
print(f"  盈利交易:   {won_trades}")
print(f"  亏损交易:   {lost_trades}")
if total_trades > 0:
    win_rate = won_trades / total_trades * 100
    print(f"  胜率:       {win_rate:.1f}%")

print()
print("=" * 60)
print("回测完成!")
print()
print("提示: 网络恢复后可运行 strategy_demo.py 使用真实数据")
