# -*- coding: utf-8 -*-
"""
QUANTAXIS 数据初始化脚本
- 填充 MongoDB 数据库
- 使用 Akshare 获取数据
"""

import sys
sys.exit = lambda c=0: None  # 拦截 QUANTAXIS 版本警告

import pymongo
import akshare as ak
import pandas as pd
from datetime import datetime

print("=" * 60)
print("    QUANTAXIS 数据初始化")
print("=" * 60)
print()

# 连接到 MongoDB
print("【1】连接 MongoDB...")
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client.quantaxis
print(f"    [OK] 连接成功")
print(f"    数据库: {db.name}")
print()

# 清空旧数据
print("【2】清空旧数据...")
db.stock_list.delete_many({})
db.stock_day.delete_many({})
print("    [OK] 已清空 stock_list 和 stock_day")
print()

# 使用 Akshare 获取股票列表
print("【3】获取股票列表...")
try:
    df = ak.stock_info_sh_name_code(symbol="主板A股")
    print(f"    [OK] 沪市主板: {len(df)} 只")
except Exception as e:
    print(f"    [失败] {e}")
    df = pd.DataFrame()

try:
    df2 = ak.stock_info_sh_name_code(symbol="科创板")
    print(f"    [OK] 科创板: {len(df2)} 只")
    df = pd.concat([df, df2], ignore_index=True)
except Exception as e:
    print(f"    [失败] {e}")

try:
    df3 = ak.stock_info_sz_name_code(symbol="主板A股")
    print(f"    [OK] 深市主板: {len(df3)} 只")
    df = pd.concat([df, df3], ignore_index=True)
except Exception as e:
    print(f"    [失败] {e}")

try:
    df4 = ak.stock_info_sz_name_code(symbol="创业板")
    print(f"    [OK] 创业板: {len(df4)} 只")
    df = pd.concat([df, df4], ignore_index=True)
except Exception as e:
    print(f"    [失败] {e}")

if len(df) == 0:
    print("    [警告] 网络不可用，使用模拟数据")
    df = pd.DataFrame({
        '证券代码': ['002285'],
        '公司简称': ['世联行'],
    })

print(f"    共获取 {len(df)} 只股票")
print()

# 转换列名并保存到 MongoDB
print("【4】保存股票列表到 MongoDB...")
df_sh = df.copy()

# 转换格式
records = []
for _, row in df_sh.iterrows():
    ipo_date = row.get('上市日期', '')
    # 转换日期对象为字符串
    if hasattr(ipo_date, 'strftime'):
        ipo_date = ipo_date.strftime('%Y-%m-%d')
    records.append({
        'code': str(row['证券代码']),
        'name': str(row['公司简称']),
        'ipoDate': str(ipo_date),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if records:
    db.stock_list.insert_many(records)
    print(f"    [OK] 已保存 {len(records)} 条股票信息")
else:
    # 添加测试数据
    db.stock_list.insert_one({
        'code': '002285',
        'name': '世联行',
        'ipoDate': '2009-12-03',
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    print("    [OK] 已保存测试数据: 002285 世联行")

# 查询验证
print()
print("【5】验证数据...")
count = db.stock_list.count_documents({})
print(f"    stock_list 文档数: {count}")

# 查询几只股票
cursor = db.stock_list.find().limit(5)
print("    前5只股票:")
for doc in cursor:
    print(f"      {doc.get('code', 'N/A')} - {doc.get('name', 'N/A')}")

print()
print("=" * 60)
print("数据初始化完成!")
print("=" * 60)