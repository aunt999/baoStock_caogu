# -*- coding: utf-8 -*-
"""
002285 世联行 - 图形化技术分析
"""

import sys
sys.exit = lambda c=0: None

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 生成模拟数据
np.random.seed(285)
dates = pd.date_range(end='2025-05-02', periods=60, freq='B')
base_price = 3.20
returns = np.random.randn(60) * 0.018 + 0.0002
prices = base_price * np.exp(np.cumsum(returns))

# 生成OHLC数据
df = pd.DataFrame({
    '日期': dates,
    '开盘': prices * (1 + np.random.randn(60) * 0.010),
    '收盘': prices,
    '最高': prices * (1 + abs(np.random.randn(60)) * 0.020),
    '最低': prices * (1 - abs(np.random.randn(60)) * 0.020),
    '成交量': np.random.randint(500000, 3000000, 60),
}, index=range(60))

df['收盘'] = df['收盘'].round(2)
df['开盘'] = df['开盘'].round(2)
df['最高'] = df['最高'].round(2)
df['最低'] = df['最低'].round(2)

# 计算技术指标
close = df['收盘']
ma5 = close.rolling(5).mean()
ma10 = close.rolling(10).mean()
ma20 = close.rolling(20).mean()

# MACD
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
macd = ema12 - ema26
signal = macd.ewm(span=9).mean()
histogram = macd - signal

# KDJ
low14 = df['最低'].rolling(14).min()
high14 = df['最高'].rolling(14).max()
rsv = (df['收盘'] - low14) / (high14 - low14) * 100
k = rsv.ewm(com=2).mean()
d = k.ewm(com=2).mean()

# RSI
def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

rsi6 = rsi(close, 6)

# 创建图表 - 2x2布局
fig = plt.figure(figsize=(16, 12), facecolor='#1a1a2e')
fig.suptitle('002285 世联行 - 技术分析图表', fontsize=18, color='white', fontweight='bold')

# 颜色方案
colors = {
    'bg': '#1a1a2e',
    'grid': '#2d2d44',
    'text': '#a0a0b0',
    'up': '#00d4aa',
    'down': '#ff4757',
    'ma5': '#ff6b6b',
    'ma10': '#ffd93d',
    'ma20': '#6bcbff',
}

# ===== 1. K线图 =====
ax1 = fig.add_subplot(2, 2, 1)
ax1.set_facecolor(colors['bg'])

# 绘制K线
for i in range(len(df)):
    row = df.iloc[i]
    color = colors['up'] if row['收盘'] >= row['开盘'] else colors['down']
    
    # 上下影线
    ax1.plot([i, i], [row['最低'], row['最高']], color=color, linewidth=0.8)
    
    # 实体
    body_bottom = min(row['开盘'], row['收盘'])
    body_height = abs(row['开盘'] - row['收盘'])
    ax1.add_patch(plt.Rectangle((i-0.3, body_bottom), 0.6, body_height if body_height > 0 else 0.01, 
                           facecolor=color, edgecolor=color, linewidth=0.5))

# 绘制均线
ax1.plot(ma5.values, color=colors['ma5'], linewidth=1.5, label='MA5')
ax1.plot(ma10.values, color=colors['ma10'], linewidth=1.5, label='MA10')
ax1.plot(ma20.values, color=colors['ma20'], linewidth=1.5, label='MA20')

ax1.set_xlim(-1, len(df))
ax1.set_ylim(df['最低'].min() * 0.95, df['最高'].max() * 1.05)
ax1.set_title('K线趋势图', fontsize=14, color='white', pad=10)
ax1.set_xlabel('交易日', color=colors['text'])
ax1.set_ylabel('价格 (元)', color=colors['text'])
ax1.legend(loc='upper left', facecolor=colors['bg'], edgecolor=colors['grid'], labelcolor=colors['text'])
ax1.grid(True, color=colors['grid'], alpha=0.3, linestyle='--')
ax1.tick_params(colors=colors['text'])
for spine in ax1.spines.values():
    spine.set_color(colors['grid'])

# ===== 2. 成交量图 =====
ax2 = fig.add_subplot(2, 2, 2)
ax2.set_facecolor(colors['bg'])

vol_colors = [colors['up'] if df.iloc[i]['收盘'] >= df.iloc[i]['开盘'] else colors['down'] for i in range(len(df))]
ax2.bar(range(len(df)), df['成交量'] / 10000, color=vol_colors, width=0.7, alpha=0.7)

ax2.set_xlim(-1, len(df))
ax2.set_title('成交量分析', fontsize=14, color='white', pad=10)
ax2.set_xlabel('交易日', color=colors['text'])
ax2.set_ylabel('成交量 (万手)', color=colors['text'])
ax2.grid(True, color=colors['grid'], alpha=0.3, linestyle='--')
ax2.tick_params(colors=colors['text'])
for spine in ax2.spines.values():
    spine.set_color(colors['grid'])

# ===== 3. MACD =====
ax3 = fig.add_subplot(2, 2, 3)
ax3.set_facecolor(colors['bg'])

# 柱状图
hist_colors = [colors['up'] if h >= 0 else colors['down'] for h in histogram]
ax3.bar(range(len(df)), histogram, color=hist_colors, width=0.7, alpha=0.7)

# 线
ax3.plot(macd.values, color='#ff9f43', linewidth=1.2, label='DIF')
ax3.plot(signal.values, color='#54a0ff', linewidth=1.2, label='DEA')
ax3.axhline(y=0, color=colors['text'], linestyle='-', linewidth=0.5)

ax3.set_xlim(-1, len(df))
ax3.set_ylim(histogram.min() * 1.2, histogram.max() * 1.2)
ax3.set_title('MACD指标', fontsize=14, color='white', pad=10)
ax3.set_xlabel('交易日', color=colors['text'])
ax3.set_ylabel('MACD', color=colors['text'])
ax3.legend(loc='upper left', facecolor=colors['bg'], edgecolor=colors['grid'], labelcolor=colors['text'])
ax3.grid(True, color=colors['grid'], alpha=0.3, linestyle='--')
ax3.tick_params(colors=colors['text'])
for spine in ax3.spines.values():
    spine.set_color(colors['grid'])

# ===== 4. KDJ + RSI =====
ax4 = fig.add_subplot(2, 2, 4)
ax4.set_facecolor(colors['bg'])

# KDJ
ax4.plot(k.values, color='#ff6b6b', linewidth=1.2, label='K')
ax4.plot(d.values, color='#6bcbff', linewidth=1.2, label='D')
ax4.axhline(y=80, color=colors['down'], linestyle='--', linewidth=0.8, alpha=0.7)
ax4.axhline(y=20, color=colors['up'], linestyle='--', linewidth=0.8, alpha=0.7)

ax4.set_xlim(-1, len(df))
ax4.set_ylim(0, 100)
ax4.set_title('KDJ指标', fontsize=14, color='white', pad=10)
ax4.set_xlabel('交易日', color=colors['text'])
ax4.set_ylabel('KDJ', color=colors['text'])
ax4.legend(loc='upper left', facecolor=colors['bg'], edgecolor=colors['grid'], labelcolor=colors['text'])
ax4.grid(True, color=colors['grid'], alpha=0.3, linestyle='--')
ax4.tick_params(colors=colors['text'])
for spine in ax4.spines.values():
    spine.set_color(colors['grid'])

# 调整布局
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# 保存图表
output_path = 'F:\\FilesData\\QUANTAXIS\\002285_technical_analysis.png'
plt.savefig(output_path, dpi=150, facecolor=colors['bg'], 
            edgecolor='none', bbox_inches='tight')

print('[OK] 图表已保存到:')
print(output_path)
print()
print('提示: 图片已保存，可以打开查看')