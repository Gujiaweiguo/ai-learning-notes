# W15-D6 · 双 Demo 实战：Semantic Model 导入验证 × A101 依据链问答 + W16 Brief

> 开发期 · Week 15「LnkChatBI 精读 × Semantic Model 第一个消费方」Day 6（2026-09-12 周六 · 实战日）
> Today's Question：**这个 Demo 距离生产环境还差几层，每层差的是什么？**
> 昨日 D5 铺垫：chatbi 白名单 20 对象把"生产"的第一层硬边界（数据库权限）画了出来；D6 前置（lnkcre pull 199 commits + 指纹复验）已执行。
> 配套实验：`第15周-Day6-双Demo实战-导入验证与W16Brief.ipynb`（11 cell 全绿，本文所有数字出自其中）。

---

## 0. 今日开发目标

① 实验③生成物**导入 LnkChatBI**：白名单合规复查 → import-pack 物化 → 镜像导入演练（幂等收敛）→ mallcre 种子**问答覆盖率 A/B 复测**；② **A101 依据链问答走 L1-L3**（D1 判定梯机器复核，L4/L5/L1' 显式 TODO）；③ **W16 开发 brief 定稿**（D5 四批 backlog 的 W16 批次 → 目标/范围/验收）；④ Demo 录入 engineering-journal；⑤ 用五层差距框架回答 Today's Question。

---

## 1. 完成事实①：白名单合规复查——两个对象宇宙，0 交集

D6 前置先行：lnkcre `a56e8b07 → d580ebd5`（落后 199 已清，openspec specs 306→307），ontology SoT 指纹复验 `bf550bc24de66813` **未漂移**。

复查结果（ipynb §1，白名单 20 对象先逐个在 `chatbi-governed-account-boundary/spec.md` 文本中验证在册）：

| 维度 | 结果 |
|---|---|
| 落生产白名单（lnk_chatbi_ro · analysis 域 20 对象） | **0/11** |
| mallcre demo 域合法（mallcre.sql + postgres_demo_schema.sql 634 对象内） | **11/11** |
| demo→prod 初判映射 | 9 个对象建立映射，其中 **4 个映射缺口**：bi_b_tenant（商户维度未入白名单）、bisubject（费用科目无承接）、bipreddeposit（→mv_collection_summary 粒度丢失）、fact_parking_daily（停车域生产侧无对象） |

**这不是 Demo 失败，是 Demo 的第一个发现**：11 条示例按 specific_ds=true 生成于 mallcre demo 数据源（D3 设计使然），D5 改写验收口径后揭示的真相是——demo 与生产是**两个对象宇宙，0 交集**。走到生产不是"把 demo 数据源换成生产数据源"，而是以白名单 20 对象为绑定目标**重生成**（映射表已建，即 W16 ③ 的输入；图 1 `w15d6_object_universe.png`）。

---

## 2. 完成事实②：导入物化 + 镜像演练 + 覆盖率 A/B（Demo① 主件）

**导入通道**：物化为 starter-pack 同构格式（`setup_mall_ops_starter_pack.py` 消费的 terminology.json / sql_examples.json，字段 word/other_words/description + question/description=SQL）——零适配成本。落盘 `semantic-model/consumers/lnkchatbi/import-pack/` 四件（含 README + import-receipt）。

**导入执行**：服务器无 PG，执行面为 SQLite 镜像，表结构对齐 `Terminology`/`DataTraining` SQLModel 定义（**术语别名=同表父子行 pid 结构**，D2 读码结论的结构复刻），upsert 语义复刻 starter 脚本：

- 语义包导入 (14 父组, 81 别名, 11 示例)；**第二遍全 0 = 幂等收敛 PASS**（starter 脚本"重复执行收敛"要求的本地证明）
- 镜像终态 25 组 / 114 别名 / 29 示例；specific_ds=1 绑定 datasource_ids=[1]（CRE BI Demo），SET_AT_IMPORT 正式解析，共享池隔离未破
- D2 教训落地检查：14 组 description + 11 条 SQL 的 XML 特殊字符扫描——全部干净（to_xml_string 反转义面无暴露）

**覆盖率 A/B 复测**（21 题电池：Q=11 示例原问 / V=5 口语变体 / P=3 生产白名单域 / S=2 starter 域守恒题；检索语义复刻 D1/D2 读码结论：术语=单向子串+命中任一别名拉全组，示例=双向子串）：

| 指标 | 基线（仅 starter） | +语义包导入后 |
|---|---|---|
| 术语命中（21 题） | 2 | **19** |
| 示例命中（21 题） | 2 | **13** |
| 端到端（11 题：示例命中+SQL 真跑） | 0 | **11/11 合法执行** |
| S 组守恒（防回归） | — | S1/S2 双态命中，**无回归** |

三个诚实的细节（都是新发现）：

1. **术语层精确率缺口**：19/19 里的 P2/P3（"各项目工单完成率"、"当前项目租赁结构指标"）是**通用词『项目』误触**——单向子串对高频通用词无区分度，命中≠可答。这是 G-04 术语消歧的新形态素材：不只同义歧义，还有通用词噪声（触发词长度/停用词门槛）。
2. **V1/V3/V4/V5 术语命中但示例 MISS**：口语改写超出示例双向子串半径 → 落入 LLM 自由组装区（概率性）。D2"分界线在错误归因"今天有了量化对照：术语层管住的 19 题 vs 示例层管住的 13 题，中间 6 题的差就是**校准的覆盖半径**。
3. **V2 全 MISS**："空着的铺"——"铺"单字与"空着"口语变体都不在别名表 → v0.2 别名补录第一候选。

**执行面真跑**（mallcre 种子装载：ERP 镜像 16 表 + BI demo schema dim/fact + 两视图 SQLite 翻译 + `fact_shop_daily_operation` 按 CTE 的 CASE 规则忠实物化 business_date=2024-12-17 单日快照）：11/11 SQL 合法执行，其中 #10 空铺汇总返回 **2 行真实空置**（shop 1012=合同终止 lease_end 2024-08-31、shop 1018=无合同）——视图翻译链路端到端成立。0 行 5 条各有归因：#7 押金表种子无行、#9 停车 CTE 种子未复刻、#8 种子无 12 月账单、#11 business_date=2024-12-17 时 90 天窗口内无到期合同（最早到期 2026-01，距 410 天）、以及最重要的——

**示例 #2 值域口径不一致（真发现）**：谓词 `POSITION_STATE = '空置'`，而 mallcre DDL 数据字典是 `1:在租/2:空置` 枚举。D3 验证器只锚表/列存在性，**值域枚举未校验** → 验证器 v0.1 边界第二项登记（第一项是裸列名未校验），change 候选包+1（与 G-01/G-05/权限概率性/attribute_mapping 同宗："语义漂移无机器告警"，第五件）。修正走 D3 生成器源头（description 的值域口径本身错了），不在 pack 里静默改写——S6 回执律。

---

## 3. 完成事实③：A101 依据链问答（Demo②）——L1-L3 全过

五步全真跑（ipynb §4）：

1. **术语检索**："A101" ∈ 『铺位』组 16 别名 → 全组归并进 prompt；
2. **注入块**：description 随组注入，含编码映射规则（A101 型 → LOC_DEMO_L1xx 前缀）与双口径警示；
3. **SQL 组装**：示例 Q1 作校准 + L2 扩展（LEFT JOIN bi_d_contract ON CONT_NO）；
4. **种子真跑**：主行 LOC_DEMO_L101 = 星河购物中心/A座/L1 首层，**在租**（CONT_DEMO_001，云巷咖啡，2024-01-01~2024-12-31）；对照行 LOC_DEMO_L202 快闪铺 **空置**（STATE=2，CONT_NO='-'，END_DATE=2099）；
5. **答案组装**：A101 不能出租的原因 = **已有有效租约**（问题的预设被证据链纠正），对照空置铺可招商，并引用双口径警示。

判定（D1 口径机器复核，图 3 `w15d6_a101_ladder.png`）：

| 级 | 判定 | 证据 |
|---|---|---|
| L1 身份路径 | **PASS** | POSITION_CODE 谓词（经别名映射）+ STORE/BUILDING/FLOOR/POSITION 四级列真实行值 |
| L2 业务链 | **PASS** | CONT_NO→合同→租户 join；POSITION_STATE/END_DATE 引用；对照行空置证据 |
| L3 规则判断 | **PASS** | description 双口径注入 + 答案显式引用（Rule 构件 L3 接口第二次实证） |
| L4 Policy | TODO | D4 约束声明 v0.1-draft 未评审（W18 ⑧），不得消费 |
| L5 动作建议 | TODO | 超出 Text-to-SQL 形态（数字员工 2.0 域） |
| L1' 权限护栏 | TODO | 需真实行权限栈；D1 已证概率性执行 gap（change 候选在案） |

**通过线 L0+L1+L2+L3：达标。** 对齐 PT-W4"L1-L3 是地板"；D1 决策"走别名映射而非补种"被完整验证——种子无字面 A101，映射规则本身经 description 通道进 prompt，是 Semantic Model 可消费性的最强证据。

---

## 4. 完成事实④：W16 开发 brief 定稿（`semantic-model/w16-dev-brief.md`）

D5 批次一（治理地基+消费面事实化）扩为四工作项：G-01 治理头 change / G-05 registry 锚点+frozen CI / chatbi 白名单 20 对象登记 Identity + **D3 生成物修订**（示例#2 值域修正，今日新增）/ 周一 S1 首次正式 digest（核查第二个 ontology.yaml）。范围红线（不做消费链扩展、不动主仓代码）与验收度量逐项落纸，见 brief 原文。

---

## 5. Today's Question：这个 Demo 距离生产环境还差几层，每层差的是什么？

**答案：五层，且每层今天都有了实证数字**（ipynb §5，图 4 `w15d6_production_gap.png`）：

| 层 | Demo 现状（今日实证） | 生产要求 |
|---|---|---|
| ① 对象宇宙 | 11/11 落 mallcre bi_*，生产白名单 **0/11 交集**，4 映射缺口 | 白名单 20 对象绑定重生成（W16 ③） |
| ② 数据与编码 | A101→LOC_DEMO 是 demo 种子规则；停车/日历 CTE 未复刻；示例#2 值域口径差 | 编码规则注册表 + 值域枚举校验 + 真实数据量校验 |
| ③ 权限与护栏 | L1' 未测（需 lnk_chatbi_ro+行权限+LLM 真栈）；权限下推概率性 gap 在案 | AST 表提取 + 谓词存在性断言 |
| ④ 组装确定性 | 6 题落 LLM 自由组装区（术语命中/示例 MISS）；V2 全 MISS | 示例扩容 + 口语别名补录 + AST 加固 |
| ⑤ 治理与同步 | S6 回执今日闭环（manifest+数字+指纹）；G-01 治理头未过 change | W16 ① 治理头 change + S1 正式 digest |

**框架本身比清单更重要**：不看功能像不像，看**每一层的失败模式在 demo 里是否已被消掉**。Demo 证明的是机制闭环（术语归并→注入→组装→执行→判定全程可机器复核），生产要求的是每层失败模式归零——第一层 0 交集恰恰说明 Demo 的价值不在"能上生产"，而在把"距离生产多远"从感觉变成**可度量、可排期的差距清单**。这正是 D5"依赖排序≠价值排序"的延伸：W16 批次为什么是治理地基+消费面事实化，因为五层差距里有三层（①③⑤）的修复动作都压在 W16 批次上。

---

## 6. 遗留 / 风险

- **示例 #2 值域修正**回 D3 生成器（description 值域口径改 1:在租/2:空置 + 生成 SQL 谓词改枚举），W16 ③ 一并做，pack 不手改。
- **通用词误触**（P2/P3『项目』）与 **V2 口语缺口**登记 G-04 v0.2 素材；示例覆盖半径（19→13 的差）提示示例库扩容优先级高于术语扩容。
- LnkChatBI **真库导入**（PG 环境 upsert + pgvector embedding + 真实问答）是 W16 候选项——今日 SQLite 镜像证明了 upsert 语义与幂等性，embedding 生成与 LLM 组装仍属未测层。
- 明日 D7 Virtual CTO Review（两周总复盘）：学习期→开发期切换评估、v0.1→v0.2 方向裁决、五维评分趋势 + D5 新增的"同步健康"首查（三仓 behind 数/指纹 diff）。
- 微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响。

## 7. 明日连接（D7 周日 · 两周总复盘）

Virtual CTO Review：W14-W15 双周交付物对账（Semantic Model v0.1.1 定稿包 / LnkChatBI 认知补齐 / 第一个消费方闭环 / W16 brief）；五维评分趋势与两周 Today's Question 复盘；v0.2 方向裁决输入=今日五层差距+D5 四批 backlog+今日三个新发现（值域校验、通用词误触、示例半径）。

---

### 附：今日证据清单

| 证据 | 来源 |
|---|---|
| 白名单 20 对象在册验证 | `lnkcre/openspec/specs/chatbi-governed-account-boundary/spec.md`（HEAD d580ebd5） |
| 0/11 白名单交集、11/11 demo 合法、4 映射缺口 | ipynb §1（对象宇宙 634 对象扫描） |
| 幂等收敛 (0,0,0)、25 组/114 别名/29 示例、specific_ds=[1] | ipynb §2（SQLite 镜像，结构对齐 Terminology/DataTraining SQLModel） |
| 覆盖率 2→19 / 2→13 / 端到端 11/11 | ipynb §3（21 题电池 + 检索语义复刻） |
| #10 返回 2 行真实空置（1012/1018） | ipynb §3.2（CTE 规则忠实物化 business_date 单日快照） |
| 示例 #2 值域口径不一致 | ipynb §3.2 + mallcre.sql:18885 DDL 注释（1:在租/2:空置） |
| A101 L1-L3 PASS 五步链 | ipynb §4（真实行值：CONT_DEMO_001/云巷咖啡/2024-12-31） |
| SoT 指纹 bf550bc24de66813 未漂移 | ipynb cell1（D6 前置复验） |
| 消费回执 | `semantic-model/consumers/lnkchatbi/import-pack/import-receipt.json`（S6 律） |
