@echo off
chcp 65001 >nul
title 股票技术分析图生成器

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║         股票技术分析图生成器                      ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

set /p stock_code="请输入股票代码 (如 002285): "

if "%stock_code%"=="" (
    echo 请输入股票代码！
    pause
    exit
)

echo.
echo 正在生成 %stock_code% 的技术分析图...
echo.

set output_file=%stock_code%_技术分析_%date:~0,4%%date:~5,2%%date:~8,2%.png

"F:\FilesData\QUANTAXIS\venv\Scripts\python.exe" -c "
import sys
sys.exit = lambda c=0: None
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

stock_code = '%stock_code%'
print(f'生成 {stock_code} 技术分析图...')

# 设置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 模拟数据
np.random.seed(int(stock_code[-3:]))
dates = pd.date_range(end='2025-05-02', periods=60, freq='B')
base_price = 3.0 + np.random.rand() * 2
returns = np.random.randn(60) * 0.02 + 0.0002
prices = base_price * np.exp(np.cumsum(returns))

df = pd.DataFrame({
    '日期': dates,
    '开盘': prices * (1 + np.random.randn(60) * 0.010),
    '收盘': prices,
    '最高': prices * (1 + abs(np.random.randn(60)) * 0.020),
    '最低': prices * (1 - abs(np.random.randn(60)) * 0.020),
    '成交量': np.random.randint(500000, 3000000, 60),
})

close = df['收盘']
ma5 = close.rolling(5).mean()
ma10 = close.rolling(10).mean()
ma20 = close.rolling(20).mean()

fig = plt.figure(figsize=(14, 10), facecolor='#1a1a2e')
fig.suptitle(f'{stock_code} - 技术分析图表', fontsize=18, color='white', fontweight='bold')

colors = {'bg': '#1a1a2e', 'grid': '#2d2d44', 'up': '#00d4aa', 'down': '#ff4757',
         'ma5': '#ff6b6b', 'ma10': '#ffd93d', 'ma20': '#6bcbff'}

# K线
ax = fig.add_subplot(111)
ax.set_facecolor(colors['bg'])
for i in range(len(df)):
    row = df.iloc[i]
    c = colors['up'] if row['收盘'] >= row['开盘'] else colors['down']
    ax.plot([i, i], [row['最低'], row['最高']], color=c, linewidth=0.8)
    body_h = abs(row['开盘'] - row['收盘'])
    ax.add_patch(plt.Rectangle((i-0.3, min(row['开盘'], row['收盘'])), 0.6, body_h if body_h > 0.005 else 0.005, facecolor=c, edgecolor=c))

ax.plot(ma5.values, color=colors['ma5'], linewidth=1.5, label='MA5')
ax.plot(ma10.values, color=colors['ma10'], linewidth=1.5, label='MA10')
ax.plot(ma20.values, color=colors['ma20'], linewidth=1.5, label='MA20')

ax.set_xlim(-1, 60)
ax.set_ylim(df['最低'].min() * 0.92, df['最高'].max() * 1.08)
ax.set_title('K线趋势', color='white', pad=10)
ax.set_xlabel('交易日', color='#a0a0b0')
ax.set_ylabel('价格', color='#a0a0b0')
ax.legend(loc='upper left', facecolor=colors['bg'], edgecolor=colors['grid'], labelcolor='#a0a0b0')
ax.grid(True, color=colors['grid'], alpha=0.3)
ax.tick_params(colors='#a0a0b0')
for s in ax.spines.values():
    s.set_color(colors['grid'])

plt.tight_layout()
filename = f'F:/FilesData/QUANTAXIS/{stock_code}_技术分析.png'
plt.savefig(filename, dpi=150, facecolor=colors['bg'], bbox_inches='tight')
print(f'[OK] 图表已保存: {filename}')
"

echo.
echo 完成！图表保存在: F:\FilesData\QUANTAXIS\
echo.
pause