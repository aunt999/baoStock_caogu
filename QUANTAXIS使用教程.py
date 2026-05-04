# -*- coding: utf-8 -*-
"""
QUANTAXIS 完整使用教程 - 一步步教你用量化交易工具
"""

import sys
sys.exit = lambda c=0: None

import pymongo
import pandas as pd
import numpy as np

print("=" * 70)
print("         QUANTAXIS 量化交易 - 完整使用教程")
print("=" * 70)
print()

# ===================== 第一步：连接数据库 =====================
print("[第一步] 连接 MongoDB 数据库")
print("-" * 70)

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client.quantaxis

print("  连接成功!")
print("  数据库: " + db.name)
print()

# ===================== 第二步：查询股票列表 =====================
print("[第二步] 查询股票列表")
print("-" * 70)

print("  方法1: 直接查询 MongoDB")
stocks = list(db.stock_list.find().limit(5))
print("  查询到 " + str(len(stocks)) + " 只股票 (显示前5只)")
for s in stocks:
    print("    " + s['code'] + " - " + s['name'])

print()
print("  方法2: 使用 QUANTAXIS API")
from QUANTAXIS.QAFetch.QAQuery import QA_fetch_stock_list

df_stocks = QA_fetch_stock_list()
print("  共 " + str(len(df_stocks)) + " 只股票")
print("  前5只:")
print(df_stocks.head())
print()

# ===================== 第三步：模拟股票数据 =====================
print("[第三步] 获取股票数据")
print("-" * 70)

print("  注意: 当前网络不可用，使用模拟数据演示")
print()

# 模拟数据
np.random.seed(600519)
dates = pd.date_range(start='2025-01-01', end='2025-05-02', freq='B')
base = 1800.0
returns = np.random.randn(len(dates)) * 0.015 + 0.0003
close_prices = base * np.exp(np.cumsum(returns))

n = len(dates)
df = pd.DataFrame()
df['date'] = dates
df['open'] = close_prices * (1 + np.random.randn(n) * 0.005)
df['high'] = close_prices * (1 + abs(np.random.randn(n)) * 0.01
df['low'] = close_prices * (1 - abs(np.random.randn(n)) * 0.01
df['close'] = close_prices
df['volume'] = np.random.randint(100000, 800000, n)

print("  股票代码: 600519 贵州茅台")
print("  数据区间: " + str(df['date'].min().date()) + " ~ " + str(df['date'].max().date()))
print("  数据条数: " + str(len(df)))
print()
print("  最近5天数据:")
print(df[['date', 'open', 'close', 'high', 'low', 'volume']].tail())
print()

# ===================== 第四步：计算技术指标 =====================
print("[第四步] 计算技术指标")
print("-" * 70)

close = df['close']
df['MA5'] = close.rolling(5).mean()
df['MA10'] = close.rolling(10).mean()
df['MA20'] = close.rolling(20).mean()

# MACD
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
df['DIF'] = ema12 - ema26
df['DEA'] = df['DIF'].ewm(span=9).mean()
df['MACD'] = (df['DIF'] - df['DEA']) * 2

print("  已计算指标:")
print("    - MA5, MA10, MA20 (移动平均线)")
print("    - DIF, DEA, MACD (MACD指标)")
print()

latest = df.iloc[-1]
print("  最新指标值 (最后交易日):")
print("    收盘价: " + str(round(latest['close'], 2)))
print("    MA5:   " + str(round(latest['MA5'], 2)))
print("    MA10:  " + str(round(latest['MA10'], 2)))
print("    MA20:  " + str(round(latest['MA20'], 2)))
print("    MACD:  " + str(round(latest['MACD'], 4)))
print()

# ===================== 第五步：创建交易策略 =====================
print("[第五步] 创建交易策略")
print("-" * 70)

# 策略: MA5 MA20 金叉买入，死叉卖出
signals = []
for i in range(1, len(df)):
    ma5_prev = df.iloc[i-1]['MA5']
    ma20_prev = df.iloc[i-1]['MA20']
    ma5_curr = df.iloc[i]['MA5']
    ma20_curr = df.iloc[i]['MA20']
    
    if ma5_prev <= ma20_prev and ma5_curr > ma20_curr:
        signals.append('BUY')
    elif ma5_prev >= ma20_prev and ma5_curr < ma20_curr:
        signals.append('SELL')
    else:
        signals.append('HOLD')

signals.insert(0, 'HOLD')
df['signal'] = signals

buy_count = (df['signal'] == 'BUY').sum()
sell_count = (df['signal'] == 'SELL').sum()

print("  策略: MA5/MA20 交叉策略")
print("  买入信号: " + str(buy_count) + " 次")
print("  卖出信号: " + str(sell_count) + " 次")
print()

# ===================== 第六步：模拟回测 =====================
print("[第六步] 模拟回测")
print("-" * 70)

initial_cash = 100000.0
cash = initial_cash
shares = 0
position = None

trades = []
for i in range(len(df)):
    row = df.iloc[i]
    
    if row['signal'] == 'BUY' and position is None:
        shares = int(cash / row['close'] / 100) * 100
        cost = shares * row['close']
        cash = cash - cost
        position = 'HOLD'
        trades.append(('BUY', str(row['date'].date()), row['close'], shares, cost))
    
    elif row['signal'] == 'SELL' and position == 'HOLD':
        proceeds = shares * row['close']
        cash = cash + proceeds
        trades.append(('SELL', str(row['date'].date()), row['close'], shares, proceeds))
        shares = 0
        position = None

final_value = cash + shares * df.iloc[-1]['close']
profit = final_value - initial_cash
profit_pct = (final_value / initial_cash - 1) * 100

print("  交易记录:")
if len(trades) > 0:
    for t in trades:
        print("    " + t[0] + " " + t[1] + " 价格:" + str(t[2]) + " 数量:" + str(t[3]) + " 金额:" + str(round(t[4], 2))
else:
    print("    无交易")

print()
print("  初始资金: " + str(round(initial_cash, 2)))
print("  最终价值: " + str(round(final_value, 2)))
print("  总收益:   " + str(round(profit, 2)))
print("  收益率:  " + str(round(profit_pct, 2)) + "%")
print()

# ===================== 总结 =====================
print("=" * 70)
print("  QUANTAXIS 使用总结")
print("=" * 70)
print()
print("  1. 连接数据库")
print("     client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')")
print("     db = client.quantaxis")
print()
print("  2. 查询数据")
print("     list(db.stock_list.find().limit(10))")
print("     QA_fetch_stock_list()")
print()
print("  3. 计算指标")
print("     df['MA5'] = close.rolling(5).mean()")
print("     df['MACD'] = ema12 - ema26")
print()
print("  4. 创建策略")
print("     判断金叉/死叉 -> 生成信号")
print()
print("  5. 回测")
print("     模拟买入卖出 -> 计算收益")
print()
print("=" * 70)
print("  运行完成!")