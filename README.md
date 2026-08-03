# 企业交易数据异常检测与审计分析系统

> 用规则化方法把审计经验变成代码，让每一笔风险预警都可解释、可复现。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-✓-150458.svg)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](#)

---

## 项目简介

针对企业财务交易数据规模增长后，传统人工抽查覆盖范围有限、效率不足的问题，本项目模拟真实审计数据分析场景，设计并实现一套轻量级交易异常检测与风险识别系统。

系统完整覆盖 **"数据生成 → 清洗分析 → 规则检测 → SQL 查询 → 可视化"** 全流程，所有检测规则均可解释、可复现，贴合真实审计业务逻辑。814 条模拟交易中检出 98 条风险记录，植入异常 100% 命中。

---

## 核心特性

- **四类风险规则**：金额异常、重复付款、异常时间、高频交易，每条预警附带 `trigger_reason` 说明触发依据
- **可复现**：固定随机种子（`seed(42)`），每次运行结果一致
- **多格式输出**：Excel 风险清单、Markdown 报告、PowerBI 交互式仪表盘
- **纯本地运行**：无需任何 API 或云服务，Python + Pandas + SQLite 即可跑通
- **阈值可调**：所有规则参数集中定义，方便适配不同业务场景

---

## 技术栈

| 类别 | 工具 | 用途 |
|------|------|------|
| 语言 | Python 3.10+ | 主开发语言 |
| 数据处理 | Pandas、NumPy | 清洗、统计、规则筛选 |
| 数据库 | SQLite（`sqlite3`） | 结构化存储与 SQL 查询 |
| 可视化 | Matplotlib | 直方图、箱线图 |
| 交互可视化 | Power BI Desktop | 审计风险仪表盘 |
| 数据导出 | openpyxl | Excel 风险清单 |

---

## 快速开始

### 环境准备

```bash
pip install pandas numpy matplotlib openpyxl faker
```

> `sqlite3` 是 Python 标准库自带模块，无需单独安装。

### 运行流水线

```bash
# 1. 生成 814 条模拟交易数据（含植入异常）
python scripts/01_generate_data.py

# 2. 数据清洗与基础分析，生成统计图表
python scripts/02_clean_and_analyze.py

# 3. 运行四类风险检测规则，给每条交易打风险标签
python scripts/03_detect_risks.py

# 4. SQL 查询 + 导出 Excel 风险清单与 Markdown 报告
python scripts/04_export_report.py
```

运行完成后，`output/` 目录下会生成风险清单、分布图表和分析报告，`audit.db` 为本地 SQLite 数据库。

PowerBI 可视化在 Power BI Desktop 中导入 `output/` 下的 CSV 文件完成。

---

## 项目结构

```
transaction_anomaly_audit/
├── data/                            # 模拟数据
│   ├── transactions.csv             # 原始交易数据（814条，含植入异常）
│   ├── transactions_cleaned.csv     # 清洗后交易数据
│   └── risk_items.csv               # 风险检测结果（98条）
├── scripts/
│   ├── 01_generate_data.py          # 数据生成
│   ├── 02_clean_and_analyze.py      # 清洗与分析
│   ├── 03_detect_risks.py           # 风险检测规则
│   └── 04_export_report.py          # SQL 查询与报告输出
├── output/
│   ├── amount_distribution.png      # 金额分布直方图
│   ├── amount_boxplot.png           # 金额箱线图
│   ├── risk_items.xlsx              # 风险清单（3 个 sheet）
│   ├── audit_report.md              # 审计分析报告
│   ├── transactions_for_powerbi.csv # PowerBI 数据源
│   └── risk_items_for_powerbi.csv   # PowerBI 数据源
├── audit.db                         # SQLite 数据库（运行后生成）
└── README.md
```

---

## 风险检测规则

| 规则 | 判定条件 | 等级 | 设计依据 |
|------|---------|------|---------|
| 金额异常 | 金额 > 均值 + 3σ **或** > 10万 | 高 | 3σ 准则覆盖 99.7% 正常数据 |
| 重复付款 | 同供应商 + 同金额 + 日期差 ≤ 3天 | 高 | 三条件叠加降低误报 |
| 异常时间 | 周末 **或** 22:00-6:00 | 中 | 非工作时间可能越权操作 |
| 高频交易 | 同供应商 7天内 ≥ 6次 | 中 | 拆分采购规避审批 |

每条风险记录都附带 `trigger_reason` 字段，记录"为什么被判定为风险"，满足审计可解释性要求。

---

## 检测结果

| 风险类型 | 检出 | 植入 | 命中率 |
|---------|------|------|--------|
| 高频交易 | 48 | 6 | 100% |
| 异常时间 | 18 | 15 | 100% |
| 重复付款 | 16 | 16 | 100% |
| 金额异常 | 16 | 10 | 100% |
| **合计** | **98** | **47** | **100%** |

植入异常全部命中，无漏报。高频交易和金额异常额外检出的记录为数据自然分布产生的边缘情况。

---

## 数据流

```
01_generate_data.py    →    02_clean_and_analyze.py    →    03_detect_risks.py    →    04_export_report.py
   生成 814 条交易          清洗 + 统计 + 图表              四条规则逐笔打标          SQL 查询 + Excel + MD
        ↓                          ↓                           ↓                        ↓
   data/transactions.csv     data/transactions_cleaned.csv  data/risk_items.csv     output/risk_items.xlsx
                                                                                    output/audit_report.md
                                                                                    output/*.png
```

---

## PowerBI 仪表盘

将 `output/` 下的 CSV 导入 Power BI Desktop，建立 `transactions` 与 `risk_items` 的一对多关系，制作含切片器联动的交互式仪表盘：

- 月度金额折线图
- 风险类型饼图
- 供应商交易额条形图
- 部门 / 日期 / 风险等级 三个切片器联动

---

## 诚实边界声明

- 所有交易数据均为**模拟生成**，不涉及任何真实企业数据
- 风险检测采用**规则化方法**，能筛出"符合预设条件的交易"，但不等同于"确认存在问题"——最终判断需人工复核
- 四条规则覆盖了审计实践中常见的四类风险点，但**并非穷举**
- PowerBI 仪表盘基于模拟数据，用于展示可视化能力，**不反映任何真实企业的经营状况**

---

## License

MIT License - 详见 [LICENSE](LICENSE)
