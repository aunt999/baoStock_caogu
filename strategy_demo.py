# -*- coding: utf-8 -*-
"""
Backtrader 均线交叉策略完整演示
- 使用 Akshare 获取数据
- 双均线金叉/死叉策略
- 完整回测输出
"""

import backtrader as bt
import akshare as ak
import pandas as pd
from datetime import datetime

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
        
        # 记录订单和交易
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                if self.params.printlog:
                    print(f'  【买入执行】价格: {order.executed.price:.2f}, '
                          f'成本: {order.executed.value:.2f}, '
                          f'手续费: {order.executed.comm:.2f}')
            else:
                if self.params.printlog:
                    print(f'  【卖出执行】价格: {order.executed.price:.2f}, '
                          f'成本: {order.executed.value:.2f}, '
                          f'手续费: {order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('  订单取消/保证金不足/拒绝')
            
        self.order = None
        
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        print(f'  【交易盈亏】毛利: {trade.pnl:.2f}, 净利: {trade.pnlcomm:.2f}')
        
    def next(self):
        if self.order:
            return
            
        # 没有持仓
        if not self.position:
            # 金叉买入
            if self.crossover > 0:
                if self.params.printlog:
                    print(f'{self.data.datetime.date()} 【金叉信号】'
                          f'快线{self.fast_ma[0]:.2f} > 慢线{self.slow_ma[0]:.2f}')
                self.order = self.buy()
        else:
            # 死叉卖出
            if self.crossover < 0:
                if self.params.printlog:
                    print(f'{self.data.datetime.date()} 【死叉信号】'
                          f'快线{self.fast_ma[0]:.2f} < 慢线{self.slow_ma[0]:.2f}')
                self.order = self.sell()


# ============ 2. 获取数据 ============
print("【步骤1】从 Akshare 获取股票数据...")
try:
    # 获取世联行 2025年数据（更长周期用于回测）
    df = ak.stock_zh_a_hist(
        symbol="002285",
        period="daily",
        start_date="20250101",
        end_date="20260430",
        adjust="qfq"
    )
    
    # 重命名列以适配 backtrader
    df = df.rename(columns={
        '日期': 'datetime',
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
        '成交额': 'amount',
        '振幅': 'amplitude',
        '涨跌幅': 'change_pct',
        '涨跌额': 'change',
        '换手率': 'turnover'
    })
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    print(f"  获取到 {len(df)} 条数据")
    print(f"  时间范围: {df.index[0].date()} ~ {df.index[-1].date()}")
    print()
    
except Exception as e:
    print(f"  数据获取失败: {e}")
    exit(1)


# ============ 3. 创建回测引擎 ============
print("【步骤2】配置回测引擎...")
cerebro = bt.Cerebro()

# 添加策略
cerebro.addstrategy(DualMAStrategy, fast_period=5, slow_period=20)

# 添加数据
data = bt.feeds.PandasData(
    dataname=df,
    fromdate=datetime(2025, 1, 1),
    todate=datetime(2026, 4, 30)
)
cerebro.adddata(data)

# 设置初始资金
cerebro.broker.setcash(100000.0)

# 设置手续费（万分之三）
cerebro.broker.setcommission(commission=0.0003)

# 添加分析指标
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

print(f"  初始资金: {cerebro.broker.getvalue():.2f}")
print(f"  策略: 双均线交叉 (5日/20日)")
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
print(f"  夏普比率: {sharpe.get('sharperatio', 'N/A')}")

# 最大回撤
dd = strat.analyzers.drawdown.get_analysis()
print(f"  最大回撤: {dd.get('max', {}).get('drawdown', 0):.2f}%")

# 交易统计
trades = strat.analyzers.trades.get_analysis()
print(f"  总交易次数: {trades.get('total', {}).get('total', 0)}")
print(f"  盈利交易:   {trades.get('won', {}).get('total', 0)}")
print(f"  亏损交易:   {trades.get('lost', {}).get('total', 0)}")
if trades.get('won', {}).get('total', 0) + trades.get('lost', {}).get('total', 0) > 0:
    win_rate = trades.get('won', {}).get('total', 0) / (
        trades.get('won', {}).get('total', 0) + trades.get('lost', {}).get('total', 0)
    ) * 100
    print(f"  胜率:       {win_rate:.1f}%")

print()
print("=" * 60)
print("回测完成!")
