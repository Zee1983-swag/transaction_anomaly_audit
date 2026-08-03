import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

# 解决中文显示问题（Windows）
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

# 1. 读取数据
df = pd.read_csv("data/transactions.csv", encoding="utf-8-sig")
print(f"原始记录数：{len(df)}")
print(df.dtypes)

# 2. 检查缺失值与重复值
print("\n=== 缺失值统计 ===")
print(df.isnull().sum())
print(f"\n重复记录数：{df.duplicated().sum()}")

# 3. 数据类型转换
df["trans_date"] = pd.to_datetime(df["trans_date"])
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# 4. 处理缺失值（本例若有缺失则删除）
df = df.dropna(subset=["amount", "trans_date", "supplier"]).reset_index(drop=True)

# 5. 基础统计
print("\n=== 金额统计 ===")
print(f"均值：{df['amount'].mean():.2f}")
print(f"中位数：{df['amount'].median():.2f}")
print(f"标准差：{df['amount'].std():.2f}")
print(f"最大值：{df['amount'].max():.2f}")
print(f"最小值：{df['amount'].min():.2f}")

print("\n=== 各部门交易汇总 ===")
print(df.groupby("department")["amount"].agg(["count", "sum", "mean"]).round(2))

print("\n=== 各供应商交易汇总（前10）===")
print(df.groupby("supplier")["amount"].agg(["count", "sum"]).round(2).sort_values("sum", ascending=False).head(10))

# 6. 可视化
os.makedirs("output", exist_ok=True)

plt.figure(figsize=(10, 5))
plt.hist(df["amount"], bins=50, edgecolor="black")
plt.title("交易金额分布直方图")
plt.xlabel("金额（元）")
plt.ylabel("交易笔数")
plt.tight_layout()
plt.savefig("output/amount_distribution.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 5))
plt.boxplot(df["amount"], vert=True)
plt.title("交易金额箱线图")
plt.ylabel("金额（元）")
plt.tight_layout()
plt.savefig("output/amount_boxplot.png", dpi=150)
plt.close()

# 保存清洗后数据
df.to_csv("data/transactions_cleaned.csv", index=False, encoding="utf-8-sig")
print("\n清洗完成，已保存 data/transactions_cleaned.csv")