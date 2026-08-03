import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

# 基础参数
N = 800  # 生成 800 条正常交易
suppliers = [f"供应商{chr(65+i)}公司" for i in range(20)]
departments = ["采购部", "财务部", "行政部", "市场部", "技术部"]
payment_methods = ["银行转账", "支票", "现金"]
approvers = ["张明", "李华", "王芳", "赵强", "刘洋"]

def random_datetime(start, end):
    """在工作日（周一至周五）的 8:00-18:00 之间生成随机日期时间"""
    while True:
        delta = end - start
        seconds = int(delta.total_seconds())
        dt = start + timedelta(seconds=random.randint(0, seconds))
        if dt.weekday() < 5 and 8 <= dt.hour < 18:
            return dt

start_date = datetime(2026, 1, 1, 8, 0)
end_date = datetime(2026, 6, 30, 18, 0)

records = []
for i in range(1, N + 1):
    dt = random_datetime(start_date, end_date)
    # 正常金额服从对数正态分布，集中在 1000-50000
    amount = round(np.random.lognormal(mean=9.5, sigma=0.8), 2)
    records.append({
        "trans_id": f"TXN{i:06d}",
        "trans_date": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "supplier": random.choice(suppliers),
        "department": random.choice(departments),
        "amount": amount,
        "payment_method": random.choice(payment_methods),
        "approver": random.choice(approvers),
        "is_urgent": random.choice(["是", "否"]),
    })

df = pd.DataFrame(records)

# ===== 植入异常 =====
# 1. 金额异常：插入 10 笔超高额交易
for _ in range(10):
    idx = random.randint(0, len(df) - 1)
    df.loc[idx, "amount"] = round(random.uniform(600000, 1000000), 2)

# 2. 重复付款：找 8 组，同供应商同金额，日期差 ≤ 3 天
for _ in range(8):
    base_idx = random.randint(0, len(df) - 1)
    dup = df.loc[base_idx].copy()
    dup["trans_id"] = f"TXN{len(df)+1:06d}"
    base_date = pd.to_datetime(df.loc[base_idx, "trans_date"])
    dup["trans_date"] = (base_date + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d %H:%M:%S")
    df = pd.concat([df, pd.DataFrame([dup])], ignore_index=True)

# 3. 异常时间：把 15 笔交易改到周末或深夜
for _ in range(15):
    idx = random.randint(0, len(df) - 1)
    weekend = start_date + timedelta(days=random.choice([5, 6, 12, 13, 19, 20]))  # 周六/周日
    late_hour = random.randint(22, 23)
    dt = weekend.replace(hour=late_hour, minute=random.randint(0, 59))
    df.loc[idx, "trans_date"] = dt.strftime("%Y-%m-%d %H:%M:%S")

# 4. 高频交易：同一供应商 7 天内 ≥ 5 笔
target_supplier = random.choice(suppliers)
base_day = datetime(2026, 4, 1, 10, 0)
for j in range(6):
    df.loc[len(df)] = {
        "trans_id": f"TXN{len(df)+1:06d}",
        "trans_date": (base_day + timedelta(days=j)).strftime("%Y-%m-%d %H:%M:%S"),
        "supplier": target_supplier,
        "department": "采购部",
        "amount": round(random.uniform(3000, 8000), 2),
        "payment_method": "银行转账",
        "approver": "张明",
        "is_urgent": "否",
    }

os.makedirs("data", exist_ok=True)
df.to_csv("data/transactions.csv", index=False, encoding="utf-8-sig")
print(f"已生成 {len(df)} 条交易记录，保存至 data/transactions.csv")