# -*- coding: utf-8 -*-
"""QUANTAXIS + Akshare 数据获取示例"""

import akshare as ak
import pandas as pd

print("=== Akshare 直接获取数据（无需MongoDB）===")
print()

# 1. 获取A股股票列表
print("【1. A股股票列表】")
stocks = ak.stock_zh_a_spot_em()
print(f"   股票总数: {len(stocks)}")
print(f"   列名: {list(stocks.columns)}")
print()

# 2. 获取世联行日K线
print("【2. 世联行(002285) 日K线】")
df = ak.stock_zh_a_hist(symbol="002285", period="daily", start_date="20260301", end_date="20260430", adjust="qfq")
print(f"   数据行数: {len(df)}")
print(df.tail(10).to_string())
print()

# 3. 获取实时行情
print("【3. 实时行情快照】")
realtime = ak.stock_zh_a_spot_em()
target = realtime[realtime["代码"] == "002285"]
if len(target) > 0:
    row = target.iloc[0]
    print(f"   世联行: {row['最新价']}元  涨跌幅: {row['涨跌幅']}%  成交额: {row['成交额']}")
