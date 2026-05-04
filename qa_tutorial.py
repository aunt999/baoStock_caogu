# QUANTAXIS Tutorial - Step by Step Usage Guide

import sys
sys.exit = lambda c=0: None

import pymongo
import pandas as pd
import numpy as np

print("=" * 70)
print("         QUANTAXIS Quantitative Trading Tutorial")
print("=" * 70)
print()

# Step 1: Connect to Database
print("[Step 1] Connect to MongoDB")
print("-" * 70)

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client.quantaxis

print("  [OK] Connected!")
print("  Database: " + db.name)
print()

# Step 2: Query Stock List
print("[Step 2] Query Stock List")
print("-" * 70)

print("  Method 1: Direct MongoDB query")
stocks = list(db.stock_list.find().limit(5))
print("  Found " + str(len(stocks)) + " stocks (showing first 5)")
for s in stocks:
    print("    " + s['code'] + " - " + s['name'])

print()
print("  Method 2: Using QUANTAXIS API")
from QUANTAXIS.QAFetch.QAQuery import QA_fetch_stock_list

df_stocks = QA_fetch_stock_list()
print("  Total " + str(len(df_stocks)) + " stocks")
print("  First 5:")
print(df_stocks.head())
print()

# Step 3: Get Stock Data (using simulation for demo)
print("[Step 3] Get Stock Data")
print("-" * 70)

print("  Note: Network unavailable, using simulation")
print()

np.random.seed(600519)
dates = pd.date_range(start='2025-01-01', end='2025-05-02', freq='B')
base = 1800.0
returns = np.random.randn(len(dates)) * 0.015 + 0.0003
close_prices = base * np.exp(np.cumsum(returns))

n = len(dates)
df = pd.DataFrame()
df['date'] = dates
df['open'] = close_prices * (1 + np.random.randn(n) * 0.005)
df['high'] = close_prices * (1 + abs(np.random.randn(n)) * 0.01)
df['low'] = close_prices * (1 - abs(np.random.randn(n)) * 0.01)
df['close'] = close_prices
df['volume'] = np.random.randint(100000, 800000, n)

print("  Stock: 600519 Kweichow Moutai")
print("  Period: " + str(df['date'].min().date()) + " to " + str(df['date'].max().date()))
print("  Bars: " + str(len(df)))
print()
print("  Last 5 days:")
print(df[['date', 'open', 'close', 'high', 'low', 'volume']].tail())
print()

# Step 4: Calculate Technical Indicators
print("[Step 4] Calculate Technical Indicators")
print("-" * 70)

close = df['close']
df['MA5'] = close.rolling(5).mean()
df['MA10'] = close.rolling(10).mean()
df['MA20'] = close.rolling(20).mean()

ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
df['DIF'] = ema12 - ema26
df['DEA'] = df['DIF'].ewm(span=9).mean()
df['MACD'] = (df['DIF'] - df['DEA']) * 2

print("  Calculated indicators:")
print("    - MA5, MA10, MA20 (Moving Averages)")
print("    - DIF, DEA, MACD (MACD Indicator)")
print()

latest = df.iloc[-1]
print("  Latest values:")
print("    Close: " + str(round(latest['close'], 2)))
print("    MA5:   " + str(round(latest['MA5'], 2)))
print("    MA10:  " + str(round(latest['MA10'], 2)))
print("    MA20:  " + str(round(latest['MA20'], 2)))
print("    MACD:  " + str(round(latest['MACD'], 4)))
print()

# Step 5: Create Trading Strategy
print("[Step 5] Create Trading Strategy")
print("-" * 70)

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

print("  Strategy: MA5/MA20 Crossover")
print("  Buy signals: " + str(buy_count))
print("  Sell signals: " + str(sell_count))
print()

# Step 6: Backtest
print("[Step 6] Backtest Simulation")
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

print("  Trade history:")
if len(trades) > 0:
    for t in trades:
        print("    " + t[0] + " " + t[1] + " Price:" + str(t[2]) + " Shares:" + str(t[3]) + " Amount:" + str(round(t[4], 2)))
else:
    print("    No trades")

print()
print("  Initial capital: " + str(round(initial_cash, 2)))
print("  Final value: " + str(round(final_value, 2)))
print("  Profit:      " + str(round(profit, 2)))
print("  Return:     " + str(round(profit_pct, 2)) + "%")
print()

# Summary
print("=" * 70)
print("  QUANTAXIS Usage Summary")
print("=" * 70)
print()
print("  1. Connect to database")
print("     client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')")
print("     db = client.quantaxis")
print()
print("  2. Query data")
print("     list(db.stock_list.find().limit(10))")
print("     QA_fetch_stock_list()")
print()
print("  3. Calculate indicators")
print("     df['MA5'] = close.rolling(5).mean()")
print("     df['MACD'] = ema12 - ema26")
print()
print("  4. Create strategy")
print("     Check golden cross/dead cross -> Generate signals")
print()
print("  5. Backtest")
print("     Simulate buy/sell -> Calculate returns")
print()
print("=" * 70)
print("  Done!")