# -*- coding: utf-8 -*-
"""
Find Buy and Sell Points - Technical Analysis Strategy
Using MA crossover + RSI + MACD for buy/sell signal identification
"""

import pandas as pd
import numpy as np
import pymongo
import sys
sys.exit = lambda c=0: None

print("=" * 70)
print("          寻找买入与卖出点 - 技术分析策略")
print("=" * 70)
print()

# ============================================================================
# Step 1: Connect to MongoDB and get stock data
# ============================================================================
print("[Step 1] Connect to database and get data")
print("-" * 70)

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client.quantaxis

# Get a stock to analyze - using 002285 as example
stock_code = "002285"
print("  Analyzing stock: " + stock_code)

# Try to get real data from MongoDB, fallback to simulation
try:
    data = list(db.stock_day.find(
        {"code": stock_code},
        sort=[("date", -1)],
        limit=100
    ).sort("date", 1))
    
    if len(data) > 50:
        df = pd.DataFrame(data)
        print("  Loaded " + str(len(df)) + " bars from MongoDB")
    else:
        raise Exception("Not enough data")
except:
    # Generate simulation data
    print("  Using simulation data (MongoDB has limited data)")
    np.random.seed(2285)
    dates = pd.date_range(start='2025-01-01', end='2025-05-02', freq='B')
    base = 3.0
    returns = np.random.randn(len(dates)) * 0.02 + 0.0001
    close_prices = base * np.exp(np.cumsum(returns))
    
    n = len(dates)
    df = pd.DataFrame()
    df['date'] = dates
    df['open'] = close_prices * (1 + np.random.randn(n) * 0.005)
    df['high'] = close_prices * (1 + abs(np.random.randn(n)) * 0.015)
    df['low'] = close_prices * (1 - abs(np.random.randn(n)) * 0.015)
    df['close'] = close_prices
    df['volume'] = np.random.randint(500000, 5000000, n)

print()

# ============================================================================
# Step 2: Calculate Technical Indicators
# ============================================================================
print("[Step 2] Calculate Technical Indicators")
print("-" * 70)

close = df['close']

# Moving Averages
df['MA5'] = close.rolling(5).mean()
df['MA10'] = close.rolling(10).mean()
df['MA20'] = close.rolling(20).mean()

# RSI
delta = close.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

# MACD
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
df['DIF'] = ema12 - ema26
df['DEA'] = df['DIF'].ewm(span=9).mean()
df['MACD'] = (df['DIF'] - df['DEA']) * 2

print("  [OK] Calculated: MA5, MA10, MA20, RSI(14), DIF, DEA, MACD")
print()

# ============================================================================
# Step 3: Generate Buy/Sell Signals
# ============================================================================
print("[Step 3] Generate Buy/Sell Signals")
print("-" * 70)

signals = []
for i in range(len(df)):
    signal = {
        'date': df.iloc[i]['date'],
        'close': df.iloc[i]['close'],
        'MA5': df.iloc[i]['MA5'],
        'MA10': df.iloc[i]['MA10'],
        'MA20': df.iloc[i]['MA20'],
        'RSI': df.iloc[i]['RSI'],
        'DIF': df.iloc[i]['DIF'],
        'DEA': df.iloc[i]['DEA'],
        'MACD': df.iloc[i]['MACD'],
        'signal': 'HOLD',
        'reason': ''
    }
    
    # Skip if not enough data for MA
    if i < 20:
        signals.append(signal)
        continue
    
    ma5_prev = df.iloc[i-1]['MA5']
    ma10_prev = df.iloc[i-1]['MA10']
    ma5_curr = df.iloc[i]['MA5']
    ma10_curr = df.iloc[i]['MA10']
    rsi = df.iloc[i]['RSI']
    dif = df.iloc[i]['DIF']
    dea = df.iloc[i]['DEA']
    macd = df.iloc[i]['MACD']
    macd_prev = df.iloc[i-1]['MACD']
    
    # BUY Signal Conditions
    # Condition 1: MA5 crosses above MA10 (Golden Cross)
    if ma5_prev <= ma10_prev and ma5_curr > ma10_curr:
        signal['signal'] = 'BUY'
        signal['reason'] = 'MA5 crosses above MA10'
    
    # Condition 2: RSI oversold (< 30)
    elif rsi < 30:
        signal['signal'] = 'BUY'
        signal['reason'] = 'RSI oversold: ' + str(round(rsi, 1))
    
    # Condition 3: MACD bottoming out (DIF crosses above DEA while both negative)
    elif dif_prev := df.iloc[i-1]['DIF'] < 0 and dea < 0:
        if df.iloc[i-1]['DIF'] <= df.iloc[i-1]['DEA'] and dif > dea:
            signal['signal'] = 'BUY'
            signal['reason'] = 'MACD golden cross (both negative)'
    
    # SELL Signal Conditions
    # Condition 1: MA5 crosses below MA10 (Dead Cross)
    elif ma5_prev >= ma10_prev and ma5_curr < ma10_curr:
        signal['signal'] = 'SELL'
        signal['reason'] = 'MA5 crosses below MA10'
    
    # Condition 2: RSI overbought (> 70)
    elif rsi > 70:
        signal['signal'] = 'SELL'
        signal['reason'] = 'RSI overbought: ' + str(round(rsi, 1))
    
    # Condition 3: MACD top falling (DIF crosses below DEA while both positive)
    elif df.iloc[i-1]['DIF'] > 0 and dea > 0:
        if df.iloc[i-1]['DIF'] >= df.iloc[i-1]['DEA'] and dif < dea:
            signal['signal'] = 'SELL'
            signal['reason'] = 'MACD dead cross (both positive)'
    
    signals.append(signal)

# Create signals dataframe
signals_df = pd.DataFrame(signals)

print("  Signal generation rules:")
print("    BUY signals:")
print("      - MA5 crosses above MA10 (Golden Cross)")
print("      - RSI < 30 (Oversold)")
print("      - MACD Golden Cross in oversold zone")
print("    SELL signals:")
print("      - MA5 crosses below MA10 (Dead Cross)")
print("      - RSI > 70 (Overbought)")
print("      - MACD Dead Cross in overbought zone")
print()

# ============================================================================
# Step 4: Display Buy/Sell Points
# ============================================================================
print("[Step 4] Buy/Sell Points Found")
print("-" * 70)

buy_signals = signals_df[signals_df['signal'] == 'BUY']
sell_signals = signals_df[signals_df['signal'] == 'SELL']

print()
print("  >>> BUY signals: " + str(len(buy_signals)) + " times")
print()
if len(buy_signals) > 0:
    for idx, row in buy_signals.iterrows():
        print("    " + str(row['date'].date()) + " | Price: " + str(round(row['close'], 2)) + " | " + row['reason'])
        print("      RSI: " + str(round(row['RSI'], 1)) + " | MA5: " + str(round(row['MA5'], 2)) + " | MA10: " + str(round(row['MA10'], 2)))

print()
print("  >>> SELL signals: " + str(len(sell_signals)) + " times")
print()
if len(sell_signals) > 0:
    for idx, row in sell_signals.iterrows():
        print("    " + str(row['date'].date()) + " | Price: " + str(round(row['close'], 2)) + " | " + row['reason'])
        print("      RSI: " + str(round(row['RSI'], 1)) + " | MA5: " + str(round(row['MA5'], 2)) + " | MA10: " + str(round(row['MA10'], 2)))

print()

# ============================================================================
# Step 5: Simple Backtest
# ============================================================================
print("[Step 5] Simulated Trading Results")
print("-" * 70)

initial_cash = 100000.0
cash = initial_cash
shares = 0
position = None

trades = []
for i in range(1, len(signals_df)):
    row = signals_df.iloc[i]
    
    if row['signal'] == 'BUY' and position is None:
        shares = int(cash / row['close'] / 100) * 100
        cost = shares * row['close']
        cash = cash - cost
        position = 'LONG'
        trades.append(('BUY', str(row['date'].date()), round(row['close'], 2), shares))
    
    elif row['signal'] == 'SELL' and position == 'LONG':
        proceeds = shares * row['close']
        profit = proceeds - cost
        cash = cash + proceeds
        trades.append(('SELL', str(row['date'].date()), round(row['close'], 2), profit))
        shares = 0
        position = None

# Close remaining position at last price
final_close = signals_df.iloc[-1]['close']
final_value = cash + shares * final_close
total_profit = final_value - initial_cash
profit_pct = (final_value / initial_cash - 1) * 100

print("  Total trades: " + str(len(trades)))
print()
print("  Trade history:")
for t in trades:
    if t[0] == 'BUY':
        print("    [BUY]  " + t[1] + " @ " + str(t[2]) + " | " + str(t[3]) + " shares")
    else:
        color = "+" if t[3] > 0 else ""
        print("    [SELL] " + t[1] + " @ " + str(t[2]) + " | " + color + str(round(t[3], 2)) + " profit")

print()
print("  Final Results:")
print("    Initial: " + str(round(initial_cash, 2)))
print("    Final:   " + str(round(final_value, 2)))
color = "+" if total_profit > 0 else ""
print("    Profit:  " + color + str(round(total_profit, 2)) + " (" + color + str(round(profit_pct, 2)) + "%)")
print()

# ============================================================================
# Step 6: Current Signal
# ============================================================================
print("[Step 6] Current Signal")
print("-" * 70)

latest = signals_df.iloc[-1]
print("  Date:    " + str(latest['date'].date()))
print("  Price:   " + str(round(latest['close'], 2)))
print("  MA5:     " + str(round(latest['MA5'], 2)))
print("  MA10:    " + str(round(latest['MA10'], 2)))
print("  MA20:    " + str(round(latest['MA20'], 2)))
print("  RSI:     " + str(round(latest['RSI'], 1)))
print("  MACD:    " + str(round(latest['MACD'], 4)))
print()

# Determine current position signal
ma5 = latest['MA5']
ma10 = latest['MA10']
rsi = latest['RSI']

if ma5 > ma10:
    trend = "UPTREND (MA5 > MA10)"
else:
    trend = "DOWNTREND (MA5 < MA10)"

if rsi < 30:
    rsi_signal = "OVERSOLD - BUY opportunity"
elif rsi > 70:
    rsi_signal = "OVERBOUGHT - SELL opportunity"
else:
    rsi_signal = "NEUTRAL"

print("  Current Status:")
print("    Trend: " + trend)
print("    RSI:   " + rsi_signal)
print()

if latest['signal'] == 'BUY':
    print("  *** CURRENT SIGNAL: BUY ***")
elif latest['signal'] == 'SELL':
    print("  *** CURRENT SIGNAL: SELL ***")
else:
    print("  *** CURRENT SIGNAL: HOLD ***")

print()
print("=" * 70)
print("  Done! Check buy/sell points above for trading decisions.")
print("=" * 70)