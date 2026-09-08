# ⚡ W15-D3 · 实验3：Semantic Model v0.1.1 → LnkChatBI term-aliases / SQL 示例生成与校准

> 开发期 · Week 15「LnkChatBI 精读 × Semantic Model 第一个消费方」Day 3（2026-09-09 周三 · 动手实验日）
> 昨日 D2 定稿了生成规格（父行/子行/作用域/验收断言）并留了两件前置：v0.1.1 三件套小修（挂账两天）+ 导入前基线（D7 护栏）。今天全部收口。
> Today's Question：**同一份 ontology，喂"术语库"和喂"表结构注释"效果差在哪？**

---

## 0. 今日开发目标

① 前置：v0.1.1 三件套原位 patch + 机器复验；② 实验3 主体：从 v0.1 六构件（术语层 + Entity 锚点）批量生成 LnkChatBI 术语库条目 + SQL 示例校准集，对照 mallcre 模式/种子数据做三级验证；③ 量化生成前后召回差，回答 Today's Question 的另一半；④ 产物带指纹落盘 `semantic-model/consumers/lnkchatbi/`——Semantic Model 的**第一个真实消费物**。

---

## 1. 前置完成：v0.1.1 三件套落地（挂账两天，今晨收口）

按 W14-D7 整改清单原位 patch `mi-cre-semantic-model-v0.1.yaml`（不重发版）：

| 项 | 内容 | 机器检查 |
|---|---|---|
| R2 场景层冻结 | `capability_policy.scenario_layer_frozen: true` | 生成器开工前 assert 通过；scenario 名仅用于排除校验（生成词与 15 条场景名不相交断言过） |
| R3 Context 别名表 | 14 条 D3 短名→D5 全名（含 02 Party Core↔02 Merchant），规范名以 D5 全名为准 | 别名表全解析（14/14 落到 entity.contexts 键） |
| G-01 提案模板 | `governance_proposals.ontology_frontmatter` 四键（version/status/maintainer/change_process） | 四键断言过；待主仓 change 流程提交 |
| 指纹锚 | ontology sha256_16 复验 = `bf550bc24de66813` | 未漂移（patch 不触碰 SoT） |

---

## 2. 实验3 完成事实

### 2.1 导入前基线（D7 护栏：没有基线的 Demo 是展示不是验证）

starter pack 11 组 × 14 探针（10 条 P0 验收问句 + 4 条 ERP 侧探针），检索模拟忠实复现 LnkChatBI 真实行为（单向子串 terminology.py:913 语义 + 字符 n-gram 余弦模拟 pgvector 双路，阈值 0.4）：

- **BI-P0：8/10**（MISS：空铺面积问句、招商线索问句——starter 没有铺位/空置/招商词汇）
- **ERP-对象：0/4**（A101 / L1-01 / 合同铺位 / 空置面积全部 MISS——starter 词汇层完全不覆盖 ERP 对象域）

### 2.2 术语层收割与口径复算（意外发现）

复算 business-ontology.yaml：术语出现 **963**（sf 条目 883 + **模块级 alias 80**）｜唯一词 **844**｜跨模块复用 40（「项目」×16 居首）。健康报告口径 883/792/91 → **差异全部来自模块级 aliases 未入报告计数**（80 出现 / 52 唯一）。教训进 G-01：治理头不仅要补，还必须**声明计数口径**——同一个文件两种数法，半年后没人说得清 883 还是 963 是对的。

### 2.3 生成：14 组 / 81 别名 / 11 条 SQL 示例

按 D2 定稿规格执行（配套实验 `第15周-Day3-TermAliases生成与校准.ipynb` §3-§4）：

- **父行** = 规范词 + description（定义+口径+映射），全部绑定已核实的物理锚（`bi_d_position`/`bi_b_tenant`/`bi_d_contract`/`bibillrecvinfo`/`bipreddeposit`/`bisubject`/`bisaledtl` + BI 侧 `vw_mall_ops_*`/`fact_*`/`dim_*`）；
- **子行** = ontology 术语自动归并（tier-2：组词子串吸收）+ 人工编码风格值（**A101→LOC_DEMO_L101、L1-01/L2-02、BLDG_A、MALL_DEMO_001**——D2 证明这类映射两路检索都救不了，预喂子别名是唯一确定性出路）；
- **护栏全过**：XML 特殊字符全角化（to_xml_string 反转义面）、词长≤8/别名≤12、跨模块歧义词不回避（「项目」组 description 声明 demo 消歧口径——G-04 的消费侧示范）、与 starter 组零冲突（merge-suggestions 0 条）；
- **消费率诚实数**：术语层 844 唯一词 → 被组词归并 51（**6.0%**）——mallcre demo 靶只覆盖部分域，**消费率低是靶子问题不是资产问题**，机制由 A101 组闭环证明。

### 2.4 三级验证全绿（先校准验证器，再裁决生成物）

对照 `mallcre_postgres.sql` + `postgres_demo_schema.sql`（解析出 634 个对象）+ `mallcre_seed_realistic.sql`：

| 验证套件 | 条目 | 失败 |
|---|---|---|
| starter 术语（验证器校准） | 11 | 0 |
| starter SQL 示例（验证器校准） | 18 | 0 |
| 生成术语（description 绑定 + 显式锚点） | 14 组 / 39 锚点 | **0** |
| 生成 SQL 示例（对象/列/种子字面量） | 11 | **0** |

验证器先在 starter pack 上校准通过，生成物的全绿才可归因于生成物本身。**验证器抓住一个真错误**：初版绑定 `bipossaledtl.POSITIONCODE` 失败——POS 通道流水表根本没有铺位列（实际列：POSNO/FLOWNO/CONTRACT_CODE/BUSDATE/TOTAL），铺位维度必须经合同桥接。这条已写进「销售明细」组 description：**口径警示只能靠术语通道送进 prompt，表结构注释送不进去**。

D2 验收断言同步通过：问「A101 铺位为什么不能出租」拉出铺位组，组内含 POSITION_CODE 映射说明与空置口径 description。

### 2.5 生成前后召回对比（覆盖率提升量化）

| 类别 | 基线 | 生成后 |
|---|---|---|
| BI-P0 | 8/10 | **9/10**（空铺问句经「空置」组别名「空铺」命中） |
| ERP-对象 | **0/4** | **4/4**（A101→铺位组；L1-01→铺位组；合同 CONT→租赁合同+铺位；空置面积→空置+铺位） |

剩余 MISS：招商线索问句（vw_mall_ops_leasing_lead 有锚未建组，v0.2 候选第一顺位）。

### 2.6 Today's Question：另一半答案（差的不是内容是通道能力，今天量化了）

1. **归并能力**：表结构注释（M-Schema 通道）是表/字段级静态文本，ontology 844 个唯一词进不去；术语库通道把 51 个词归并进 14 个语义组——**命中任一别名拉全组**，A101 这类检索救不了的编码映射只有这条通道能确定性预喂（0/4→4/4 的来源）。
2. **口径注入能力**：description 是 Rule 构件的注入口（D1 结论 L3 接口）——空置双口径、押金两粒度、合同状态两套值域、POS 表无铺位需合同桥接，这些警示写进表注释组装时无人拉取；写进 description，命中即进 prompt。
3. **作用域能力**：术语库有 specific_ds/datasource_ids 闸（项目级资产不污染 oid 级共享池）；表结构注释天然锁死单数据源——**无法承载跨 ERP/BI 双侧的词-物归并**，而那正是 Semantic Model 的本职。
4. **代价与对冲**：术语库是易失资产（库内行、无版本）；对冲 = 产物带指纹 manifest（4 个文件各带 sha256_16 + 源头 ontology 指纹）——**消费不改变 SoT 地位，只改变消费物的可追溯性**（分层 SoT 宪章第一次实战）。

---

## 3. 遗留 / 风险

- **导入实测未做**（D6 实战日）：生成物落盘≠导入验证，specific_ds/datasource_ids 标 `SET_AT_IMPORT`（防共享池污染，宁缺勿错）；D6 导入 mallcre 数据源后跑 L1-L3 验收。
- **招商线索组缺失**：BI-P0 唯一 MISS 项；vw_mall_ops_leasing_lead 有锚，v0.2 候选。
- **验证器 v0 边界**：只校验限定名引用/FROM-JOIN 对象/种子字面量，裸列名未校验；列名比对大小写不敏感（近似）——真实导入需确认 mallcre PG 侧带引号大写列的折叠行为。
- **计数口径差**（883 vs 963）并入 G-01 提案：治理头四行之外加第五行「计数口径声明」。
- 微信通道 9/8 起中断（运维通告已留 NOTICE-2026-09-09，等 owner 重配对），不影响落盘链路。

## 4. 明日连接（D4 · Policy 语义化）

审批流（mi workflow / condition-approval / approval matrix）→ Policy Model 抽取规则；对照 BCM ADR-004 Binding Model，定义 AI 执行约束声明格式。Today's Question：**AI 需要知道"谁审批"，还是需要知道"为什么找他审批"？** 今天的铺垫：description 注入口已验证能把「口径警示」送进 prompt——Policy 声明格式应该设计成同一条通道能送的东西（D4 检验它的上限）。

---

### 附：今日证据清单

| 证据 | 来源 |
|---|---|
| v0.1.1 patch + 机器复验（R2/R3/G-01/指纹） | `semantic-model/mi-cre-semantic-model-v0.1.yaml`（meta.version=0.1.1）+ 人读版 patch 记录 |
| 消费物 4 件 + 指纹 | `semantic-model/consumers/lnkchatbi/`：term-aliases.generated.json（`39c553b4e497fb49`）/ sql-examples.generated.json（`5fdbe1f329bf4734`）/ alias-merge-suggestions.json（`4f53cda18c2baa0c`）/ import-manifest.json（`4329c91088693e2c`） |
| 基线/召回对比/三级验证/漏斗 | 配套实验 ipynb（11 code cells 全部执行通过 verify_ipynb）+ w15d3_消费漏斗 / w15d3_召回前后对比 / w15d3_验证通过率 三图 |
| 口径复算（963/844/40 vs 报告 883/792/91） | 配套实验 §2（模块级 alias 80 处未入报告口径） |
| POS 通道无铺位列（合同桥接警示） | mallcre_postgres.sql bipossaledtl 实测列 + 验证器失败记录（初版绑定被抓住后修正） |
| starter pack 格式契约（word/other_words/description + question/description） | LnkChatBI backend/scripts/mall_ops_starter_pack/{terminology,sql_examples,acceptance_questions}.json |
| 检索机制忠实模拟依据 | D2 精读行号证据（terminology.py:913 单向子串、pgvector 0.4 阈值、命中拉全组）沿用 |

*配套实验：`第15周-Day3-TermAliases生成与校准.ipynb` —— v0.1.1 机器复验、导入前基线、14 组生成（词-物归并+编码映射预喂）、三级验证（先校准后裁决）、召回前后对比、指纹 manifest 落盘，11 个代码 cell 全部执行通过。*
