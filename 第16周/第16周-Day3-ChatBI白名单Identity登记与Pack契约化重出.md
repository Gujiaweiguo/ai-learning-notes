# W16-D3 · ChatBI 白名单 Identity 登记 × 生成器 v0.1.2 值域修正 × Pack 契约化重出

> 开发期 · Week 16「治理地基 + 消费面事实化」（2026-09-16 周三，W16 brief 工作项 ③）
> Today's Question：**W15-D6 发现示例 #2 值域口径错误时说「不在 pack 里静默改写」——为什么修正必须回到生成器源头，而不是改一下 pack 文件了事？**
>
> 📌 计划来源说明：w14-plus 无 W16 逐日条目，按其 W15-D6 交付的 `semantic-model/w16-dev-brief.md` 工作项 ③（"chatbi 白名单 20 对象登记 Identity 构件 + D3 生成物修订：20 对象登记为 analysis 域锚点清单；修订示例 #2 值域口径回 D3 生成器并重出 pack"）执行；与 D2 明日连接一致（含 D1 digest P0 契约对齐 + P2 字典待查两项今日输入）。
>
> 配套实验：`第16周-Day3-ChatBI白名单Identity登记与Pack契约化重出.ipynb`（10 code cell 全绿，本文所有数字出自其中或生成器/脚本实测）。

---

## 0. 今日开发目标

① S2 日探针；② Identity 主菜：白名单 20 对象（16 open + 3 gov 视图 + 1 函数）登记为 analysis 域锚点清单（含 W15-D6 demo→prod 映射 9 条 + 4 缺口）+ P2 字典待查一并核；③ 生成器 v0.1.2：示例 #2 值域修正回 D3 生成器源头 + 全量值域复验 + pack 重出对齐 domain-semantic-pack-contract（D1 digest P0）+ S6 回执换新（manifest+数字+指纹+契约对照项）。

## 1. 完成事实①：S2 日探针与 Identity 锚点登记（20/20 + 6 负锚点）

| 仓 | behind | 处置 |
|---|---|---|
| lnkcre | 0（HEAD `0392e107`，与 G-05 锚定基线同头——**锚点零漂移窗口**） | 无需动作 |
| docs | 10（HEAD `c3d08d6`） | 记录，W39 digest 统一盘点（S2 只数数不分析） |
| LnkChatBI | 0（`c8927267`） | — |

挡板未触发（max 10 << 300）。

**Identity 登记设计**（`semantic-model/governance/identity-analysis-anchors.yaml`）：锚点三元组 `(file, line, expect)` 与 G-05 完全同门——行号=首次观测值，expect=该行必须包含的子串，OK/DRIFTED/BROKEN 三级判决，**从今日起进 S1 周验基线**。与 G-05 的差别在锚定对象：G-05 锚"冻结 effect 的实现证据"（Go 代码），Identity 锚"生产对象宇宙的权限事实"（openspec spec 文本）——spec 里 `lnk_chatbi_ro` 白名单一行增删，登记即 BROKEN，须带 change 才绿。

| 维度 | 数字 |
|---|---|
| spec 在册验证（`chatbi-governed-account-boundary/spec.md`，指纹 `80c720f39832e44d`） | 16 open 表 + 3 gov 视图 + 1 函数 = **20/20 全锚定** |
| 负锚点（白名单显式排除：SELECT 必须为 false） | 5 restricted 基对象 + `refresh_run` = **6 个**（边界的一半是"不能看见什么"） |
| demo→prod 血缘（W15-D6 §1 初判映射倒排） | **9/20 有血缘**（5 条干净：dim_unit/dim_store/mv_contract_summary/gov_snap_lease_daily/mv_customer_receivable_daily/gov_ar_aging_summary/mv_resource_summary/gov_lease_expiry_summary；1 条缺口血缘：mv_collection_summary ← bipreddeposit 粒度丢失+bisubject 仅结果承接） |
| 无 demo 血缘 | **11/20**（W17+ 生产绑定重生成时需逐个补白皮书——清单本身就是 backlog） |
| 4 个 demo 缺口对象 | bi_b_tenant（商户维度未入白名单）/bisubject/bipreddeposit/fact_parking_daily——**显式登记，不隐藏** |

**P2 待查裁决（D1 digest 遗留）**：trade/industry 字典波次**零新增 canonical 表**——`industry_dict_aliases`（000196 迁移）与 `trade_definitions` 均在 8/28 快照内已入册。canonical_tables 真实增量是另一回事：**472 → 477**（+工程条件库 5 张 + `store_change_records` 门店变更台账 1 张 − 退役 `mig_000202_hazard_default_due_days_backup` 1 张）——语义模型 v0.1.1 的 table_total=472 已过期，熵基线刷新登记进 W39 digest 议程（不静默改 SoT 计数）。

## 2. 完成事实②：生成器 v0.1.2——修正回源 + 值域验证器 + 契约元数据（generate_pack.py）

W15-D6 裁决今日兑现：生成器从 W15-D3 ipynb 实验3 **提升为可执行脚本**（`semantic-model/consumers/lnkchatbi/generate_pack.py`，fail-closed 退出码——任一验证失败 exit 1，与 D2 frozen CI 同门）。changelog 三处修正 + 两项新增：

| # | 修正 | 证据 |
|---|---|---|
| ① | 示例 #2 谓词 `POSITION_STATE = '空置'` → `= 2` | mallcre.sql:18896 DDL：`decimal(1,0) COMMENT '铺位状态(1:在租;2:空置......)'`；种子实测 STATE=1×3 / 2×1 |
| ② | **示例 #8 谓词 `BILLMONTH = 12` → `BILLYEAR = '2024' AND BILLMONTH = '12'`** | **复验新发现，与 #2 同病**：BILLMONTH 为 `varchar(32)`（种子值 `'6'` 型月份串）——裸数字谓词在 PG 直接类型报错、在 SQLite 静默恒 false。W15-D6 归因"种子无 12 月账单"只对了表层：即使有 12 月数据，旧谓词也永远查不到 |
| ③ | 铺位组 caliber / 空置组 definition 值域口径同步改 DDL 枚举 | 术语层与示例层口径同源，description 是注入 prompt 的唯一通道 |
| ④ | 新增值域验证器：DDL COMMENT 枚举 + 列类型 + 种子值域三层对账 | 回归哨兵断言：`= 2` 必须在、`= '空置'` 必须不在（防脚手架自身回归） |
| ⑤ | pack 契约元数据（domain-semantic-pack-contract R1） | pack_id `lnkcre-mall-ops-demo-pack` v0.1.2 + compatibility 声明 |

**值域复验 11/11**（brief 验收③第二项）：9 PASS + 2 N/A（#9/#10 无字面量谓词），0 FAIL。生成器自报与 ipynb **独立复算**（不共用代码）一致。最有力的一组对照是**真跑行数**：

| 示例 | 旧谓词 | 新谓词 |
|---|---|---|
| #2 空置铺位 | 0 行（W15-D6 即以此发现 bug） | **1 行：LOC_DEMO_L202 / L2-02 快闪铺 / 87㎡ / STATE=2** |
| #8 12 月账单 | 0 行（类型错位静默——**永远**查不到） | 0 行（种子月份={'6'}，**数据未覆盖但口径正确**——归因干净） |

同样 0 行，语义完全不同：一个是"坏了"，一个是"没数据"。这正是 W14-D1"错误归因决定治理动作"的值域版。

## 3. 完成事实③：S6 验证链全量重跑 + 回执换新（含契约对照项）

brief §4 S6 消费回执律执行：pack 重出（指纹换新：terminology `2deb9b63→8137b094`、sql_examples `9d3fbb38→0af3cb1f`）后，W15-D6 验证链全部重跑：

| 验证项 | 结果 | 与 W15-D6 对照 |
|---|---|---|
| upsert 幂等收敛 | 第一遍 (14, 81, 11)，第二遍 **全 0 PASS** | 同构 |
| 镜像终态 | 25 父组 / 114 别名 / 29 示例 | **数字守恒**（数量不变、内容换新——修正不扩容，只纠口径） |
| 21 题电池 | 术语命中 2→**19**、示例命中 2→**13** | 与基线一致（修正不改变检索面） |
| e2e 执行 | **11/11 合法执行** | #2 从"合法但 0 行"升级为"返回真实空置行" |
| A101 依据链 | L1/L2/L3 **PASS**（L4/L5/L1' TODO 不变） | L3 注入内容升级：DDL 枚举口径随『空置』组 description 进入 prompt |
| S 组守恒 | S1/S2 双态命中，无回归 | — |

**契约对照项 8 条**（D1 digest P0 兑现——回执新增 `contract_alignment`）：R1 身份/版本/兼容 **ALIGNED**（demo profile 未注册的诚实标注：先于 governed framework 存在，fail-closed 注册路径留给生产 pack）；R2 术语映射在允许清单内 PARTIAL（demo 域 11/11，生产白名单 0/11——血缘桥已登记，即 W17 重生成输入）；R3 语义路由 PARTIAL；R4 能力解释 PARTIAL；R5 治理函数 N/A-demo（生产侧 `gov_ar_aging_summary` 已入今日 Identity 登记）；R6 不越权 / R7 不跨域共享 / R8 dev-scoped **ALIGNED**。4 ALIGNED + 3 PARTIAL + 1 N/A——**契约不是打勾练习，PARTIAL 项就是 W17 的 backlog**。

## 4. S1 周验基线登记（D2 明日连接兑现）

`semantic-model/sync/s1-baseline-checklist.yaml`：W39 digest 检查单从 2 项扩到 **5 项**——三仓对账 / SoT 指纹复验（`bf550bc2…`）/**G-05 锚点漂移**（15 锚，frozen_effect_ci.py anchors 门）/**Identity 锚点复验**（20 对象，今日新增）/canonical 漂移（477 基线）。基线头：lnkcre `0392e107` / docs `c3d08d6` / LnkChatBI `c8927267`。

## 5. Today's Question 的回答

**为什么修正必须回生成器源头？因为 pack 是投影，不是源。** `terminology.json`/`sql_examples.json` 是生成器从 TIER1 源数据 + ontology SoT 推导出的产物；直接改 pack = 在投影上打补丁 = 下次重生成时补丁必然丢失，且没有任何机器证据能区分"手改的 pack"和"生成的 pack"——**漂移从此无声开始**。修正回源后得到三重保障：① 修正进 changelog（人可审计）；② 回归哨兵进断言（`POSITION_STATE = 2` 必须在、`= '空置'` 必须不在——机器可防再犯）；③ 全链指纹换新、S6 回执与生成物重新自洽（漂移可检测）。这是分层 SoT 宪章在消费面的实例化：**改投影是漂移，改源是演进**。今天 #8 的发现是最好的注脚——正因为修在了源、验证器也建在了源，复验时才会顺带揪出第二处同病（类型口径）；如果只是手改 pack，#8 会永远藏在"种子没数据"的错误归因里。

## 6. 遗留 / 风险

- **G-01 提案**继续等主仓立案窗口（docs behind 10 未消化，W39 digest 一并核查受理状态；对账报告格式可参照 docs 仓 evidence-chain 范本深化——D4 事项）。
- 无血缘的 11 个白名单对象（dim_date/dim_trade/mv_ops_daily 等）在 W17 生产绑定重生成时需逐个补对象白皮书——今日登记已把它们显式列名。
- LnkChatBI 真库导入（PG + pgvector embedding + LLM 真栈）仍是未测层，W16 候选项不变。
- G-04 v0.2 素材再 +1 证据：电池复现 V2 全 MISS（"空着的铺"）与通用词『项目』误触（P2/P3 命中≠可答）。

## 7. 明日连接（W16-D4）

G-01 立案窗口跟进（docs 仓受理状态核查 + 对账报告深化）；两套锚点（G-05 × 15 + Identity × 20+6）跑一次**周验预演**（anchors 门 + identity 复验全流程，为 W39 digest 排练并暴露格式问题）；G-04 v0.2 别名批次素材定稿（V2 口语缺口补录候选 + 通用词门槛设计）。周日 Review 增查同步健康（三仓 behind / 指纹 diff / 挡板记录 / backlog 对调评估）。

## 8. 理解变化（保留学习期传统）

以前以为：语义包的"值"在内容里——术语对、SQL 能跑，包就是对的。现在知道：语义包的"值"在**口径的可验证性**里——`POSITION_STATE = '空置'` 在 SQLite 镜像里"合法执行"了整整一周（W15-D6 的 11/11 里就藏着它），没有任何执行错误暴露它是错的；错误只在**谓词字面量与 DDL 数据字典对账**时现形。以前还以为：demo 与生产的差距是"换数据源"。现在知道：差距是**三个对象宇宙**（demo 11 对象 / 生产白名单 20 对象 / 映射 9 条+缺口 4 个），而 Identity 登记就是把这三个宇宙的边界从"spec 文本里的一段英文"变成"带行号锚点、周验漂移检查、变更须带 change 的机器事实"——**权限边界也是语义资产，且是最不该靠人读的那一种**。
