import pandas as pd
import numpy as np

df = pd.read_csv("data/transactions_cleaned.csv", encoding="utf-8-sig")
df["trans_date"] = pd.to_datetime(df["trans_date"])

risk_records = []

mean_amt = df["amount"].mean()
std_amt = df["amount"].std()
THRESHOLD = 100000  # 固定阈值，可自行调整

# ===== 规则1：金额异常 =====
def check_amount_anomaly(row):
    if row["amount"] > mean_amt + 3 * std_amt or row["amount"] > THRESHOLD:
        return True
    return False

# ===== 规则2：重复付款（修正：必须金额相同）=====
def find_duplicate_payments(df):
    """同一供应商 + 金额相同 + 日期差 ≤ 3 天"""
    dups = []
    df_sorted = df.sort_values(["supplier", "amount", "trans_date"])
    for supplier, group in df_sorted.groupby("supplier"):
        group = group.reset_index()
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                # 修正：金额不同则跳过（已按金额排序，后续金额只会更大）
                if group.loc[j, "amount"] != group.loc[i, "amount"]:
                    break
                if group.loc[j, "trans_date"] - group.loc[i, "trans_date"] <= pd.Timedelta(days=3):
                    dups.append(group.loc[j, "trans_id"])
                    dups.append(group.loc[i, "trans_id"])
                else:
                    break  # 同金额内已按日期排序，后续日期差只会更大
    return list(set(dups))

dup_ids = find_duplicate_payments(df)

# ===== 规则3：异常时间 =====
def check_abnormal_time(row):
    """周末或 22:00-6:00 交易"""
    if row["trans_date"].weekday() >= 5:  # 5=周六, 6=周日
        return True
    hour = row["trans_date"].hour
    if hour >= 22 or hour < 6:
        return True
    return False

# ===== 规则4：高频交易（阈值调整为6次）=====
def find_high_frequency(df):
    """同一供应商 7 天内交易次数 ≥ 6"""
    high_freq_ids = []
    df_sorted = df.sort_values(["supplier", "trans_date"])
    for supplier, group in df_sorted.groupby("supplier"):
        group = group.reset_index()
        for i in range(len(group)):
            window_end = group.loc[i, "trans_date"] + pd.Timedelta(days=7)
            count = group[(group["trans_date"] >= group.loc[i, "trans_date"]) &
                          (group["trans_date"] <= window_end)]
            if len(count) >= 6:
                high_freq_ids.extend(count["trans_id"].tolist())
    return list(set(high_freq_ids))

high_freq_ids = find_high_frequency(df)

# ===== 汇总打标 =====
for _, row in df.iterrows():
    risks = []
    if check_amount_anomaly(row):
        risks.append(("金额异常", "高", f"金额 {row['amount']:.2f} 超过均值+3σ({mean_amt+3*std_amt:.2f}) 或固定阈值 {THRESHOLD}"))
    if row["trans_id"] in dup_ids:
        risks.append(("重复付款", "高", "同一供应商存在相同金额且日期差≤3天的交易"))
    if check_abnormal_time(row):
        risks.append(("异常时间", "中", f"交易发生在周末或深夜（{row['trans_date'].strftime('%H:%M')}）"))
    if row["trans_id"] in high_freq_ids:
        risks.append(("高频交易", "中", "同一供应商 7 天内交易次数 ≥ 6"))

    for risk_type, risk_level, reason in risks:
        risk_records.append({
            "trans_id": row["trans_id"],
            "trans_date": row["trans_date"],
            "supplier": row["supplier"],
            "department": row["department"],
            "amount": row["amount"],
            "risk_type": risk_type,
            "risk_level": risk_level,
            "trigger_reason": reason,
        })

risk_df = pd.DataFrame(risk_records)
risk_df.to_csv("data/risk_items.csv", index=False, encoding="utf-8-sig")
print(f"共检出 {len(risk_df)} 条风险记录")
print(risk_df["risk_type"].value_counts())