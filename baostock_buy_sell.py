# -*- coding: utf-8 -*-
"""
Find Buy/Sell Points - Using BaoStock Real Data
BaoStock provides free China stock historical data
"""

import baostock as bs
import pandas as pd
import numpy as np

print("=" * 70)
print("       买卖点分析 - BaoStock 实时数据")
print("=" * 70)
print()

# ============================================================================
# Step 1: Login and get real data
# ============================================================================
print("[Step 1] Login to BaoStock...")
lg = bs.login()
if lg.error_code != '0':
    print("Login failed:", lg.error_msg)
    exit()
print("    Login: " + lg.error_msg)
print()

# Get stock code from user or default
stock_code = "002285"
# BaoStock format: sh.600000 (上交所) / sz.002285 (深交所)
bs_code = "sz." + stock_code if not stock_code.startswith('sh') and not stock_code.startswith('60') else "sh." + stock_code

# For 60xxxx stocks use sh, for 00xxxx use sz
if stock_code.startswith('00'):
    bs_code = "sz." + stock_code
elif stock_code.startswith('60') or stock_code.startswith('68'):
    bs_code = "sh." + stock_code
else:
    bs_code = "sz." + stock_code

print("[Step 2] Fetching data for " + stock_code + " (" + bs_code + ")")
print("-" * 70)

# Fetch 6 months of daily data
rs = bs.query_history_k_data_plus(bs_code,
    'date,open,high,low,close,volume,amount,turn',
    start_date='2024-11-01',  # 6 months ago
    end_date='2025-05-02',
    frequency='d')

data_list = []
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())

bs.logout()

if len(data_list) == 0:
    print("    No data found!")
    exit()

# Convert to DataFrame
df = pd.DataFrame(data_list, columns=['date','open','high','low','close','volume','amount','turn'])
df['close'] = df['close'].astype(float)
df['open'] = df['open'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)
df['volume'] = df['volume'].astype(float)

print("    Loaded " + str(len(df)) + " trading days")
print("    Date range: " + df['date'].iloc[0] + " to " + df['date'].iloc[-1])
print()

# ============================================================================
# Step 2: Calculate Technical Indicators
# ============================================================================
print("[Step 3] Calculate Technical Indicators")
print("-" * 70)

close = df['close']

# Moving Averages
df['MA5'] = close.rolling(5).mean()
df['MA10'] = close.rolling(10).mean()
df['MA20'] = close.rolling(20).mean()
df['MA60'] = close.rolling(60).mean()

# RSI
delta = close.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs_val = gain / loss
df['RSI'] = 100 - (100 / (1 + rs_val))

# MACD
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
df['DIF'] = ema12 - ema26
df['DEA'] = df['DIF'].ewm(span=9).mean()
df['MACD'] = (df['DIF'] - df['DEA']) * 2

# KDJ (RSV -> K -> D -> J)
low_9 = df['low'].rolling(9).min()
high_9 = df['high'].rolling(9).max()
rsv = (close - low_9) / (high_9 - low_9) * 100
rsv = rsv.fillna(50)
df['K'] = rsv.ewm(com=2).mean()
df['D'] = df['K'].ewm(com=2).mean()
df['J'] = 3 * df['K'] - 2 * df['D']

print("    [OK] MA5, MA10, MA20, MA60, RSI(14), MACD, KDJ(9,3,3)")
print()

# ============================================================================
# Step 3: Generate Signals
# ============================================================================
print("[Step 4] Generate Buy/Sell Signals")
print("-" * 70)

signals = []
position = None

for i in range(len(df)):
    date = df.iloc[i]['date']
    price = df.iloc[i]['close']
    
    # Skip if not enough data
    if i < 60:
        signals.append({'date': date, 'close': price, 'signal': 'N/A', 'reason': 'Insufficient data'})
        continue
    
    ma5 = df.iloc[i]['MA5']
    ma10 = df.iloc[i]['MA10']
    ma20 = df.iloc[i]['MA20']
    rsi = df.iloc[i]['RSI']
    dif = df.iloc[i]['DIF']
    dea = df.iloc[i]['DEA']
    macd = df.iloc[i]['MACD']
    k = df.iloc[i]['K']
    d = df.iloc[i]['D']
    j = df.iloc[i]['J']
    
    ma5_prev = df.iloc[i-1]['MA5']
    ma10_prev = df.iloc[i-1]['MA10']
    dif_prev = df.iloc[i-1]['DIF']
    dea_prev = df.iloc[i-1]['DEA']
    k_prev = df.iloc[i-1]['K']
    d_prev = df.iloc[i-1]['D']
    
    sig = 'HOLD'
    reason = ''
    
    # ===== BUY CONDITIONS =====
    # 1. MA5 Golden Cross (above MA10)
    if ma5_prev <= ma10_prev and ma5 > ma10 and ma5 > ma20:
        sig = 'BUY'
        reason = 'MA5 Golden Cross (trend up)'
    
    # 2. RSI Oversold
    elif rsi < 30 and rsi > 0:
        sig = 'BUY'
        reason = f'RSI oversold ({rsi:.1f})'
    
    # 3. KDJ Oversold (K < 20, J < 10)
    elif k < 20 and j < 10:
        sig = 'BUY'
        reason = f'KDJ oversold (K={k:.1f}, J={j:.1f})'
    
    # 4. MACD Golden Cross (both negative)
    elif dif_prev <= dea_prev and dif > dea and dif < 0 and dea < 0:
        sig = 'BUY'
        reason = 'MACD Golden Cross (oversold zone)'
    
    # 5. Price below MA20 and RSI < 40 (potential bounce)
    elif price < ma20 and rsi < 40 and rsi > 0:
        sig = 'BUY'
        reason = f'Near MA20 support, RSI={rsi:.1f}'
    
    # ===== SELL CONDITIONS =====
    # 1. MA5 Dead Cross (below MA10)
    elif ma5_prev >= ma10_prev and ma5 < ma10:
        sig = 'SELL'
        reason = 'MA5 Dead Cross (trend down)'
    
    # 2. RSI Overbought
    elif rsi > 70:
        sig = 'SELL'
        reason = f'RSI overbought ({rsi:.1f})'
    
    # 3. KDJ Overbought
    elif k > 80 and j > 90:
        sig = 'SELL'
        reason = f'KDJ overbought (K={k:.1f}, J={j:.1f})'
    
    # 4. MACD Dead Cross (both positive)
    elif dif_prev >= dea_prev and dif < dea and dif > 0 and dea > 0:
        sig = 'SELL'
        reason = 'MACD Dead Cross (overbought zone)'
    
    # 5. Price above MA20 and RSI > 60
    elif price > ma20 and rsi > 60:
        sig = 'SELL'
        reason = f'Near MA20 resistance, RSI={rsi:.1f}'
    
    signals.append({'date': date, 'close': price, 'signal': sig, 'reason': reason})

signals_df = pd.DataFrame(signals)
df = pd.concat([df, signals_df[['signal', 'reason']]], axis=1)

# ============================================================================
# Step 4: Display Results
# ============================================================================
print()

buy_signals = df[df['signal'] == 'BUY']
sell_signals = df[df['signal'] == 'SELL']

print("  >>> BUY signals: " + str(len(buy_signals)) + " 次")
print()
if len(buy_signals) > 0:
    for idx, row in buy_signals.iterrows():
        print(f"    {row['date']} | 价格: {row['close']:.2f} | {row['reason']}")
        print(f"         MA5={row['MA5']:.2f} MA10={row['MA10']:.2f} RSI={row['RSI']:.1f} MACD={row['MACD']:.4f}")

print()
print("  >>> SELL signals: " + str(len(sell_signals)) + " 次")
print()
if len(sell_signals) > 0:
    for idx, row in sell_signals.iterrows():
        print(f"    {row['date']} | 价格: {row['close']:.2f} | {row['reason']}")
        print(f"         MA5={row['MA5']:.2f} MA10={row['MA10']:.2f} RSI={row['RSI']:.1f} MACD={row['MACD']:.4f}")

print()

# ============================================================================
# Step 5: Simulate Trading
# ============================================================================
print("[Step 5] Simulated Trading Results")
print("-" * 70)

initial_cash = 100000.0
cash = initial_cash
shares = 0
trades = []

for i in range(1, len(df)):
    row = df.iloc[i]
    if row['signal'] == 'BUY' and shares == 0:
        buy_price = row['close']
        shares = int(cash / buy_price / 100) * 100
        cost = shares * buy_price
        cash -= cost
        trades.append(('BUY', row['date'], round(buy_price, 2), shares))
    elif row['signal'] == 'SELL' and shares > 0:
        sell_price = row['close']
        proceeds = shares * sell_price
        profit = proceeds - cost
        cash += proceeds
        trades.append(('SELL', row['date'], round(sell_price, 2), round(profit, 2)))
        shares = 0

# Close at last price
last_price = df.iloc[-1]['close']
final_value = cash + shares * last_price
profit = final_value - initial_cash
profit_pct = (final_value / initial_cash - 1) * 100

print()
print("  Trade history:")
for t in trades:
    if t[0] == 'BUY':
        print(f"    [买入] {t[1]} @ {t[2]} | {t[3]}股")
    else:
        color = "赚" if t[3] > 0 else "亏"
        print(f"    [卖出] {t[1]} @ {t[2]} | {color}{abs(t[3]):.2f}元")

print()
print("  Portfolio:")
print(f"    Initial: {initial_cash:.2f}元")
print(f"    Cash:   {cash:.2f}元")
print(f"    Shares: {shares} (value: {shares*last_price:.2f})")
print(f"    Final:  {final_value:.2f}元")
print()
color = "赚" if profit > 0 else "亏"
print(f"  Total Profit: {color}{abs(profit):.2f}元 ({'+' if profit>0 else ''}{profit_pct:.2f}%)")
print()

# ============================================================================
# Step 6: Current Signal
# ============================================================================
print("[Step 6] Current Status (" + df.iloc[-1]['date'] + ")")
print("-" * 70)

latest = df.iloc[-1]
print(f"  Price:  {latest['close']:.2f}")
print(f"  MA5:    {latest['MA5']:.2f}")
print(f"  MA10:   {latest['MA10']:.2f}")
print(f"  MA20:   {latest['MA20']:.2f}")
print(f"  RSI:    {latest['RSI']:.1f}")
print(f"  MACD:   {latest['MACD']:.4f}")
print(f"  K:      {latest['K']:.1f}  D: {latest['D']:.1f}  J: {latest['J']:.1f}")
print()

# Determine current signal
trend = "上涨" if latest['MA5'] > latest['MA10'] else "下跌"
rsi_status = "超卖" if latest['RSI'] < 30 else "超买" if latest['RSI'] > 70 else "中性"

print(f"  Trend: {trend}")
print(f"  RSI:   {rsi_status} ({latest['RSI']:.1f})")
print()

signal = latest['signal']
if signal == 'BUY':
    print(f"  ===> 当前信号: 【买入】{latest['reason']}")
elif signal == 'SELL':
    print(f"  ===> 当前信号: 【卖出】{latest['reason']}")
else:
    print(f"  ===> 当前信号: 【观望】")

print()
print("=" * 70)
print("  Data source: BaoStock (Free)")
print("=" * 70)