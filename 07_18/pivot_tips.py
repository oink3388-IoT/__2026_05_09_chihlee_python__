import pandas as pd
import numpy as np

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.float_format', '{:.2f}'.format)

data = {
    'total_bill': [16.99,10.34,21.01,23.68,24.59,25.29,8.77,26.88,15.04,14.78,10.27,35.26,15.42,18.43],
    'tip':        [1.01,1.66,3.5,3.31,3.61,4.71,2.0,3.12,1.96,3.23,1.71,5.0,1.57,3.0],
    'smoker':     ['No','No','No','No','No','No','No','No','No','No','No','No','No','No'],
    'day':        ['Sun','Sun','Sun','Sun','Sun','Sun','Sun','Sun','Sun','Sun','Sun','Sun','Sun','Sun'],
    'time':       ['Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner','Dinner'],
    'size':       [2,3,3,2,4,4,2,4,2,2,2,4,2,4]
}

df = pd.DataFrame(data)

print("=== 原始資料 ===")
print(df)

print("\n=== 1. 按 day 分組，計算 total_bill 和 tip 的平均 ===")
pivot1 = df.pivot_table(
    values=['total_bill', 'tip'],
    index='day',
    aggfunc='mean'
).round(2)
print(pivot1)

print("\n=== 2. 按 day 和 time 分組，計算 tip 的平均 ===")
pivot2 = df.pivot_table(
    values='tip',
    index='day',
    columns='time',
    aggfunc='mean'
).round(2)
print(pivot2)

print("\n=== 3. 按 size 分組，計算 total_bill 的總和與平均 ===")
pivot3 = df.pivot_table(
    values='total_bill',
    index='size',
    aggfunc=['sum', 'mean', 'count']
).round(2)
print(pivot3)

print("\n=== 4. 按 day 和 smoker 分組，計算 tip 的平均 ===")
pivot4 = df.pivot_table(
    values='tip',
    index='day',
    columns='smoker',
    aggfunc='mean'
).round(2)
print(pivot4)

print("\n=== 5. 多重統計：按 day 分組 ===")
pivot5 = df.pivot_table(
    values=['total_bill', 'tip'],
    index='day',
    aggfunc=['mean', 'max', 'min']
).round(2)
print(pivot5)
