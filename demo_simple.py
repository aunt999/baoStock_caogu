# -*- coding: utf-8 -*-
"""QUANTAXIS 基础用法示例"""

import akshare as ak

print("=== QUANTAXIS + Akshare 使用示例 ===")
print()

# 示例1: 获取单只股票历史K线
print("【示例1】获取世联行(002285) 日K线")
try:
    df = ak.stock_zh_a_hist(
        symbol="002285", 
        period="daily", 
        start_date="20260401", 
        end_date="20260430", 
        adjust="qfq"  # 前复权
    )
    print(f"获取到 {len(df)} 条数据")
    print(df.tail(5))
except Exception as e:
    print(f"网络错误: {e}")
print()

# 示例2: 获取股票基本信息
print("【示例2】获取A股股票列表（简化版）")
try:
    # 这个接口更稳定
    df = ak.stock_info_sh_name_code(symbol="主板A股")
    print(f"沪市主板A股数量: {len(df)}")
    print(df.head(5))
except Exception as e:
    print(f"错误: {e}")
