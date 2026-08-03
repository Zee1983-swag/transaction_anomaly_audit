import pandas as pd
import sqlite3
import os
from datetime import datetime

# 1. 导入 SQLite
conn = sqlite3.connect("audit.db")
df = pd.read_csv("data/transactions_cleaned.csv", encoding="utf-8-sig")
risk_df = pd.read_csv("data/risk_items.csv", encoding="utf-8-sig")

df.to_sql("transactions", conn, if_exists="replace", index=False)
risk_df.to_sql("risk_items", conn, if_exists="replace", index=False)

# 2. SQL 查询高风险事项
print("=== 高风险交易（等级=高）===")
query_high = """
SELECT supplier, risk_type, COUNT(*) as 次数, ROUND(SUM(amount), 2) as 涉及金额
FROM risk_items
WHERE risk_level = '高'
GROUP BY supplier, risk_type
ORDER BY 涉及金额 DESC
"""
print(pd.read_sql_query(query_high, conn))

print("\n=== 各风险类型分布 ===")
query_dist = """
SELECT risk_type, COUNT(*) as 次数
FROM risk_items
GROUP BY risk_type
ORDER BY 次数 DESC
"""
print(pd.read_sql_query(query_dist, conn))

print("\n=== 金额 TOP10 交易 ===")
query_top = """
SELECT trans_id, trans_date, supplier, amount
FROM transactions
ORDER BY amount DESC
LIMIT 10
"""
print(pd.read_sql_query(query_top, conn))

conn.close()

# 3. 导出 Excel
os.makedirs("output", exist_ok=True)
with pd.ExcelWriter("output/risk_items.xlsx", engine="openpyxl") as writer:
    risk_df.to_excel(writer, sheet_name="风险清单", index=False)
    risk_df.groupby("risk_type").size().to_excel(writer, sheet_name="类型分布")
    risk_df.groupby("supplier").size().sort_values(ascending=False).to_excel(writer, sheet_name="供应商分布")

# 4. 生成 Markdown 报告
total_risk = len(risk_df)
type_dist = risk_df["risk_type"].value_counts().to_dict()
high_risk = len(risk_df[risk_df["risk_level"] == "高"])
top_suppliers = risk_df["supplier"].value_counts().head(5).to_dict()

report = f"""# 审计风险分析报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 一、总体概况

本次分析共检测交易 {len(df)} 笔，检出风险记录 {total_risk} 条，其中高风险 {high_risk} 条。

## 二、风险类型分布

| 风险类型 | 检出次数 |
|---------|---------|
"""
for rtype, count in type_dist.items():
    report += f"| {rtype} | {count} |\n"

report += f"""
## 三、风险最高的供应商（前5）

| 供应商 | 风险次数 |
|--------|---------|
"""
for sup, count in top_suppliers.items():
    report += f"| {sup} | {count} |\n"

report += """
## 四、建议关注点

1. 金额异常交易金额显著偏离均值，建议逐笔核实业务合理性及审批流程是否完整。
2. 重复付款需重点排查是否为系统重复发起或供应商重复请款，确认后及时冲销。
3. 异常时间交易（周末/深夜）应核实经办人身份与授权情况，排查非工作时间操作风险。
4. 高频交易供应商建议结合合同与历史记录，评估是否存在拆分采购规避审批的情形。

> 本报告基于模拟数据生成，所有风险提示仅供初步筛查参考，最终判断需人工复核。
"""

with open("output/audit_report.md", "w", encoding="utf-8") as f:
    f.write(report)

# 5. 导出供 PowerBI 使用的 CSV 文件
df.to_csv("output/transactions_for_powerbi.csv", index=False, encoding="utf-8-sig")
risk_df.to_csv("output/risk_items_for_powerbi.csv", index=False, encoding="utf-8-sig")
print("\n报告已生成：output/audit_report.md")
print("风险清单已导出：output/risk_items.xlsx")
print("已导出 PowerBI 数据源：output/transactions_for_powerbi.csv, output/risk_items_for_powerbi.csv")