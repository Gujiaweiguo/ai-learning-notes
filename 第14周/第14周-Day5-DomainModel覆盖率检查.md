# 第14周-Day5 Domain Model 覆盖率检查（实验2）——472 张表 vs 17 个 Context：过时、越界，还是第三种

> 补录说明：本日内容 9/6 晚由管线故障补填生成（9/3-9/6 推送管线静默跳过，已修复）。数据快照 lnkcre 8/28 canonical_tables。
> 配套实验：`第14周-Day5-DomainModel覆盖率检查.ipynb`（verify OK，10 code cells）
> 机器可读报告：`w14d5-context-coverage-report.yaml`；图：`w14d5_context分布.png`、`w14d5_月度增长热力图.png`

## Today's Question

计划问"307→336 的表增长和 17 Context 的错位，说明 Domain Model 过时了还是代码越界了"。实测之后答案是**两者都有，外加第三个发现**：增长正在涌向跨切面桶。

## 实验数字（快照事实）

- canonical_tables.txt 实测 **472 张表**（计划写的 336 已过时：307→336→472，四个月 +40%）
- 月度增长：4月+68 → 5月+4 → 6月+152 → 7月+148 → 8月+98（累计曲线见热力图）
- 472 张全部可追溯：双迁移体系并集 = canonical，**0 缺失**；孤儿表经三层启发式收敛 18→0
- 归类方法：L1 迁移名规则 417 张 / L3 表名规则 34 张 / L2 包名 grep（代码证据）21 张；53 条规则，12 个灰区显式登记
- 17/17 Context 全部有表；Platform/Shared 桶 54 张（11.4%）

## 四个发现

### 1. Domain Model 确实过时（且比模拟的快）
文档口径 336，现实 472。D3 熵增模拟假设"+10 spec/月"，现实是表层的 **+98~152/月**——模拟的稀释速度是乐观的。D3 的方向结论拿到实数背书：锚点稀释不需要任何人犯错，只需要继续建表。

### 2. 代码确实越界（方向：分析层吞业务事实）
17 BI & Analytics 以 70 张（14.8%）成为**最大** Context：sales_* 事实表 14 张、alert_* 预警、report_* 30+ 张全进了 BI 桶。"销售数据"的业务语义现在住在分析 Context 而不是商户/账单 Context——tenant_daily_sales 归 17 还是 02 是登记在案的灰区。

### 3. 增长正在涌向跨切面桶（第三发现）
BI 14.8% + Platform/Shared 11.4%（workflow 引擎 16 张、打印、编码、自定义字段）= **26.2%**——四分之一的 schema 领域不可归属。错位的真实方向不是"某个域越界"，是**跨切面能力增速 > 领域能力增速**，Domain Model 这种领域 taxonomy 天然接不住这类增长。

### 4. 语义层超额承诺
ontology 声明 12 模块/102 能力，但 13 Work Order Service 仅 3 张表（0.6%）、15 Customer/Member 仅 2 张（0.4%）。Context 覆盖密度极不均，且稀疏区与 D3 发现的 ontology 盲区（02/12/15/16 四个孤儿 Context）高度重叠——**访谈覆盖缺口在语义层和代码层是同一个缺口的两个投影**。

## 结构发现：双迁移体系

MySQL migrations（316，活跃子集）+ migrations-pg（472，全量基线），canonical testdata 并集做裁判。**同一 schema 双方言维护**：PG-only 表已出现（hazard/office_energy 族）。这是表层版本的"source of truth 分叉"——不治理就是下一个 D-001。

## 方法论复用

分类器（53 规则 + 包名证据链）与 D3 的 150 行体检同构：**语义资产配 CI**。落地方向：新表必须在 canonical diff 时携带 Context 归属注记，无归属 = 挡板告警。

## 与 D6 的连接

本报告作为 D6 定稿包直接输入：覆盖率进 Capability 构件；灰区 12 条 + 双迁移分叉进已知缺口列表；月度增长做熵增基线（替代模拟假设）。
