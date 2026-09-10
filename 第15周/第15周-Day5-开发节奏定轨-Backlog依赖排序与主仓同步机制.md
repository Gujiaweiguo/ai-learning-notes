# W15-D5 · 开发节奏定轨：W16+ backlog 依赖排序 × lnkcre 主仓同步机制

> 开发期 · Week 15「LnkChatBI 精读 × Semantic Model 第一个消费方」Day 5（2026-09-11 周五）
> Today's Question：**学习期的雷达机制，开发期保留什么、砍掉什么？**
> 昨日 D4 铺垫：Policy 构件 known_gaps 三条（断链修复 > 策略载体版本化 > 通道注入实测）是 backlog 排序的现成素材；今天再叠加一份新输入——主仓这两周到底演进了什么。

---

## 0. 今日开发目标

① 实跑**第一次三仓 digest**（lnkcre / docs / LnkChatBI fetch 对账——8/28 快照分别落后 199 / 57 / 14 commits），产出 wave 主题表 + 语义影响 P0-P3 评级；② W16+ backlog 按 **Semantic Model 依赖排序**（不是价值排序）定稿为四个批次；③ 主仓同步机制定稿（周频 digest + 日探针 + 事件触发 + 落后挡板 + 归档律 + 消费回执，S1-S6）；④ 用裁决标准回答 Today's Question；⑤ ipynb 量化验证：DAG 拓扑序证明排序合法、真实日提交分布驱动同步策略模拟、孤儿表稀释模拟。

---

## 1. 完成事实①：第一次三仓 digest（2026-08-28 → 09-11）

| 仓 | 本地 HEAD（8/28 快照） | 落后 origin | 两周新提交 | 对语义资产的影响 |
|---|---|---|---|---|
| lnkcre | a56e8b07（mcp-write-path-hardening archive） | **199** | 211 | openspec specs 273→**306**（+33 新增 / 12 修改） |
| docs | 349f07d（8/28 备份） | 57 | — | SoT 未漂移（ontology 指纹复验 `bf550bc24de66813`，BCM 零变更）；**但产品侧出现第二个 ontology.yaml**（`30-products/lnkchat/ontology.yaml`） |
| LnkChatBI | 10e6d66e（ports 迁移） | 14 | — | 消费方稳定，MI context provider 集成线未动 |

两周 211 个提交、日提交分布 `[12,27,17,17,15,13,2,7,11,26,19,13,18,14]`（均值 15.1/天，突发 27、低谷 2）——**计划里"避免再落后 714 commits"不是过虑，两周就积了 199**。新增 spec 归为四个 wave：

| wave | 证据（新 spec） | 对 Semantic Model 的影响 | 评级 |
|---|---|---|---|
| ① analysis 平台纵深 | analysis-schema-foundation / core-metrics / u1-store-customer-grain / wave2-business-metrics / wave3-property-metrics / runtime-readiness / consumption-readiness / new-report-consumer-contract（8 个） | analysis schema 的 dim/mv 对象域在快速成形 = Identity 构件**未来的 analysis 锚点层**；同时 G-07「新表无 Context 挡板」正被这波放大 | **P0** |
| ② chatbi 治理账户 | chatbi-governed-account-boundary | **第一个消费方的可见面从假设变成数据库事实**（详见下） | **P0** |
| ③ MCP 查询收敛 | mcp-query-scope / mcp-query-thinning-batch1/2/tail | 工具面收敛 + `Deps.ProjectAccess` 单一 seam（fail-closed）→ plan 方向②「MCP 工具描述生成」的接入点就绪，目标集合变小变清晰 | P1 |
| ④ 前端模板化 × 测试经济 | resource-center-console / resource-page-template / resource-list-contract / resource-list-selection / resource-column-sizing / spatial-resource×3 / area-management-page / parking-page-template / navigation-shell-density / frontend-eslint-baseline / e2e-evidence-path-hygiene / bs-ticket-ledger-hygiene / openapi-documentation-sync / test-infrastructure-observability / test-iteration-economy / unit-approval-experience / report-manager-retirement | 对语义资产无直接影响；resource-list-contract 的字段契约可能触达术语层，登记待查 | P3 |

### chatbi 白名单细节（对 D6/W16 最重要的一条）

`lnk_chatbi_ro` 治理账户与 `lnk_analysis_ro` 独立（独立爆炸半径 + 凭证轮换），**恰好持有**：`USAGE` on schema `analysis`；`SELECT` on 16 个白名单 open 对象（dim_project / dim_date / dim_trade / dim_unit / dim_store / mv_ops_daily / mv_store_ops_daily / mv_collection_summary / mv_customer_receivable_daily / mv_contract_summary / mv_leasing_structure / mv_target_tracking / mv_leads_funnel / mv_campaign_summary / mv_resource_summary / mv_property_summary）；`SELECT` on 3 个 gov 视图（gov_snap_lease_daily / gov_snap_lease_monthly / gov_lease_expiry_summary）；`EXECUTE` on `gov_ar_aging_summary`。禁止 schema-wide grant、禁止 default privileges、provisioning 幂等无凭证。

三个含义：

1. **D6 Demo 验收口径被改写**：W15-D3 生成的 11 条 SQL 示例必须落在 20 个对象内——引用白名单外对象 = 生产环境直接权限报错。D6 导入前先做白名单合规复查。
2. **「白名单外新对象不可见」就是语义挡板的现成范本**：spec 场景明文"新对象默认不可见，直到 citing OpenSpec action 授予"——G-07「新表无挡板」可以直接抄这个模式：新 canonical 表无 Context 归属 action 就不进语义资产索引。
3. **analysis 域的对象命名是天然锚点**：dim_/mv_/gov_/fact_ 前缀自带语义角色（维度/物化/治理视图/受限事实）——Entity 构件扩展 analysis 域时白名单 20 对象就是第一份登记清单。

另登记一个分叉信号：docs 仓产品侧出现第二个 ontology.yaml（`30-products/lnkchat/ontology.yaml` vs SoT 的 `config/ontology/business-ontology.yaml`）——SoT 唯一性问题，G-01 同宗，W16 digest 持续跟踪。

---

## 2. 完成事实②：W16+ backlog 按 Semantic Model 依赖排序（主交付物）

**排序原则先立规矩**：依赖排序 ≠ 价值排序。一项工作能启动 ⇔ 它**消费的构件已可信**（有证据锚 + 可校验）；能验收 ⇔ 它**反哺的缺口有度量**。排序输入是三份事实清单：v0.1 的 G-01~G-10、D4 的 GAP-P1~P3 + 三断链、本次 digest 的 P0/P1 信号。

| 批次 | 工作项 | 消费的构件（依赖为什么成立） | 反哺缺口 | 验收度量 |
|---|---|---|---|---|
| **W16 L0 治理地基 + 消费面事实化** | ① G-01 治理头走 openspec change 提交主仓 | frontmatter 模板已在 v0.1.1 固化（五键含计数口径） | G-01（P0） | 主仓 merge + 指纹登记入 SoT 指纹链 |
| | ② G-05 effect-registry 代码锚点 + frozen CI | registry 5 类冻结清单（W14-D4 对账） | G-05 + ORE-1 零告警 | CI 红绿可测：改 frozen effect 不带 change 即红 |
| | ③ chatbi 白名单 20 对象登记进 Identity 构件 + D3 生成物合规复查 | digest 事实（本日 §1） | Identity 构件 analysis 域 | 11 条 SQL 示例 100% 落白名单内（或修订后复验） |
| **W17 L1 消费链扩展 + 挡板** | ④ G-07 新表挡板（citing action 模式） | ③的白名单范本 + G-01 治理头（挡板登记进受治理的 SoT，无治理头的挡板=第二套无主清单） | G-07 | analysis wave 新对象 100% 带归属或显式挂起 |
| | ⑤ G-04 术语消歧第二批（白名单域内子集） | ③的 20 对象域（先知道消费面才知先消歧哪些术语） | G-04（91 条复用） | 白名单域内术语歧义组清零 |
| | ⑥ MCP 工具描述生成第一份 change | G-01 治理头（术语引用落受治理 SoT）+ digest ③号 wave 的 query-scope seam | plan 方向② | 工具面（收敛后集合）描述覆盖率 + openspec change 立案 |
| **W18 L2 规则显式化（v0.2 主菜第一批）** | ⑦ lease→cash 链 Rule 显式化 | ②的 registry 锚点（frozen 无 CI 时显式化=往漏桶加水）+ MI-AC-001+ 验收语料 | Rule 构件覆盖 | lease→cash 链规则显式化条数 / 验收用例对账率 |
| | ⑧ Policy 约束声明 draft→0.1 评审 | ②的锚点格式（evidence 载体锚定）+ D4 draft | GAP-P2/P3 | 评审通过 + 机检全绿升级 |
| | ⑨ G-06 双迁移分叉裁决 | ②的锚点（锚定了才知道分叉多大） | G-06 | 分叉清单 + 裁决记录 |
| **W19 收口** | ⑩ 策略载体版本化统一裁决 | ⑧的声明格式（version_binding 字段定了才知道要版本化什么） | GAP-P1 + G-09 | 版本化方案 + 两处同病同治记录 |
| | ⑪ 三断链修复提案（lnkcre change 候选） | ⑧的证据格式（提案引用约束声明） | D4 断链①②③ | change 立案受理（裁决权在主仓） |

**哪个 Context 先接入的裁决：租赁域 × analysis 消费面**。理由按证据密度 × 消费方就绪度：① 规则语料最厚——lease 8 态生命周期 + amendment 9 类矩阵 + MI-AC 验收链 + D4 审批四载体全部落在租赁→财务链；② 消费方就绪——chatbi 白名单 20 对象中 lease 直接相关过半（mv_contract_summary / mv_leasing_structure / gov_snap_lease_daily/monthly / gov_lease_expiry_summary，加上受限的 fact_lease_signed/expiry 恰好构成"可见/不可见"的完整对照教学集）；财务管理 Context 第二顺位（amendment 应收重算 + ar_rebalance 两个事务耦合点已在 Relationship 构件登记）。

拓扑合法性由 ipynb §1 验证：11 项工作 + 12 条依赖边做 Kahn 拓扑排序，md 批次划分通过验证；最长依赖链 = 3 节点且不止一条（G-05 → Policy 声明 → 版本化裁决、CHATBI → 新表挡板 → lease→cash 显式化等），最少串行批次 3 批、md 划 4 批 = 留一周缓冲。两条关键链的起点都在 W16 批次——治理地基（G-05）和消费面事实化（chatbi 白名单）不是可选项，它们卡着 v0.2 主菜的进度。

---

## 3. 完成事实③：主仓同步机制定稿（防「再落后 714」）

| # | 机制 | 频率 / 触发 | 动作 | 防什么 |
|---|---|---|---|---|
| S1 | 周频 digest | 每周一 D1 开工前 | 三仓 fetch + 落后数 + spec 增量 + wave 主题 + P0-P3 评级 → `semantic-model/sync/digest-<YYYY-WW>.md` | 199→714 重演（本次实证两周积 199） |
| S2 | 日探针 | 每天开发开始前 | 秒级 fetch + behind 计数（不读 diff） | 周频粒度漏掉架构级突变 |
| S3 | 事件触发深 digest | S2 探针单仓 behind > 100，或 S1 发现新 wave / 大件 archive | 当天定向跟读（只读该 wave 的 specs + 关键代码） | analysis/chatbi 这种一夜改写消费面的变更（8/29 单日 27 commits 的实证突发） |
| S4 | 落后挡板 | behind > 300（约一个 R-wave 的量） | 暂停消费链开发 → 全量对齐 + 重跑 v0.1 校验（指纹 diff）再继续 | 语义资产建立在过期事实上 |
| S5 | openspec change 归档律 | 每次对主仓提案 | 走 change 流程（proposal → 对账报告 → 合入），禁止无 diff 报告直改 | 学习轨道与主仓演进脱节、不可追溯 |
| S6 | 消费回执 | 每次喂入消费方 | import-manifest + 验证数字 + SoT 指纹 | 消费物无版本无追溯（D3 已建立，升格为律） |

设计依据（量化见 ipynb §2/§3）：实证速率 15.1 commits/天且突发明显（max 27，模拟含压力段）——纯周扫的常规感知延迟均值 3.6 天/最大 6 天，压力段未感知积压可达 ~300 commits；日探针把「危险积压（>100）的暴露时间」压到 ≤1 天而成本秒级，常规感知节奏仍由周深读决定（均值 ~2.2 天），深读成本约为日扫的 1/4（20 vs 84 次）。**「便宜的高频探针 + 昂贵的低频深读」是正确分层**，等价于把 W15-D2 学到的"检索层便宜、生成层昂贵才值得缓存"应用到雷达自身。挡板阈值 300 介于「一个 wave」（~211/两周）和「失控线 714」之间，留一个 wave 的处理缓冲。

---

## 4. Today's Question：学习期的雷达机制，开发期保留什么、砍掉什么？

**裁决标准先行**：不看机制「有没有用」，看它防不防开发期的两类死法——**语义资产被主仓稀释**（漂移：本次 199 落后、8 月 98 张新表、G-07 无挡板）和 **AI/资产越界**（安全：D4 三断链全是"声明无执法"）。防 → 保留（必要时改造形态）；只服务心智模型建立 → 学习期使命已完成 → 砍或降频。

| 学习期机制 | 裁决 | 形态变化 | 理由 |
|---|---|---|---|
| Daily Digest 雷达（每日 pull + P0-P3 扫描） | **保留但改造** | 拆成 S1 周频深 digest + S2 日探针 + S3 事件触发 + S4 挡板 | 雷达本质从「学习输入」变成「开发安全网」：学习期每天深扫是为了建心智模型（已完成、17 Context 472 表认知在手），开发期的真实威胁是漂移（199 落后是今天的实证）。**降频不降能力**——探针日日在线，深读按需触发 |
| Today's Question | **保留** | 不变（日频一问） | D4 三断链的发现全部来自"为什么"追问；判断力是开发期的稀缺品，不是学习期的消耗品 |
| 周日 Virtual CTO Review | **保留** | 增「同步健康」检查项（三仓 behind 数 / 指纹 diff / 挡板触发记录 / backlog 排序是否需对调） | 开发期唯一质量闸门，也是唯一能裁决"依赖排序要不要改"的机制 |
| 10 段式推送模板 | 砍（W14 已宣布） | 三段式（目标/事实/连接） | 已落地两周，信息密度验证更高 |
| 逐对象精读 | 砍 | 按需查证 | 对象认知已建立；digest P0/P1 项触发定向精读（S3 就是它的合法形态——精读从「日程驱动」变成「事件响应」） |
| （新增）S5 归档律 + S6 消费回执 | **新增** | — | 学习期没有"资产被稀释""消费物失联"的死法，开发期有——死法清单决定机制清单 |

一句话答案：**保留的是雷达的功能（感知漂移、防止越界），砍掉的是雷达的仪式（每日定时深扫）**。学习期雷达是望远镜——每天主动看新东西建星图；开发期雷达是烟雾报警器——平时只做秒级嗅探保持安静，阈值响了才灭火。判断标准不是"这机制我习惯了"，而是"砍掉它之后，两类死法哪一类会找上门"。

---

## 5. 遗留 / 风险

- **分叉信号**：docs 仓产品侧第二个 ontology.yaml——若它是消费侧副本可以接受（消费不改变 SoT），若在长出新语义就是双 SoT 事故。W16 第一次正式 digest 重点核查，必要时并入 G-01 change 一起裁决。
- **D3 生成物白名单合规未复查**：今天只登记了约束事实，11 条 SQL 示例的复查放在 D6 导入前（避免今天重复跑导入链）。
- **D6 前置动作**：lnkcre 本地 pull 到 origin/main（199 commits）+ ontology 指纹复验——Demo 用的白名单细节和 mallcre 种子数据都以最新为准。
- backlog 是 v1：依赖排序基于当前缺口快照，W15-D7 两周总复盘时若 v0.1.1 指纹漂移或 digest 出新 P0，批次对调走周日 Review 裁决，不中途自改。
- 微信通道 9/8 起中断（NOTICE-2026-09-09 已留），落盘链路不受影响。

## 6. 明日连接（D6 周六 · 实战日：双 Demo + W16 brief）

① term-aliases / SQL 示例导入 LnkChatBI（mallcre 种子数据）+ **白名单合规复查** + 覆盖率复测；② A101 依据链问答走 L1-L3（L4/L5 标 TODO）；③ W16 开发 brief 定稿（今天的四批 backlog → 目标/范围/验收三件套，W16 批次 = 治理地基 + 消费面事实化）。Today's Question：**这个 Demo 距离生产环境还差几层，每层差的是什么？** 今天的输入：chatbi 白名单已经给出了"生产"的第一层硬边界（数据库权限），Demo 与生产的差距从今天起可以逐层点名。

---

### 附：今日证据清单

| 证据 | 来源 |
|---|---|
| 三仓落后数 | lnkcre `git rev-list --count HEAD..origin/main` = 199（HEAD a56e8b07）；docs = 57（HEAD 349f07d）；LnkChatBI = 14（HEAD 10e6d66e），2026-09-11 fetch |
| 两周 211 commits + 日分布 | `git log origin/main --since=2026-08-28`：`[12,27,17,17,15,13,2,7,11,26,19,13,18,14]` |
| specs 273→306 | `git ls-tree origin/main openspec/specs/` = 306；diff HEAD..origin/main：+33 A / 12 M |
| chatbi 白名单 | origin/main `openspec/specs/chatbi-governed-account-boundary/spec.md`（16 open 对象 + 3 gov 视图 + 1 函数 + 引用式授权场景 + 幂等无凭证） |
| MCP 收敛 | origin/main `openspec/specs/mcp-query-scope/spec.md`（Deps.ProjectAccess 单 seam、org-foundation resolver、fail-closed、admin bypass、query_contract 三路径过滤）+ thinning batch1/2/tail |
| SoT 未漂移 | docs 仓 `sha256sum business-ontology.yaml` 前缀 = `bf550bc24de66813`（与 v0.1 登记一致）；BCM 零变更；漂移文件为 `30-products/lnkchat/ontology.yaml` + 对齐消费 prompt |
| 缺口清单 | v0.1 YAML known_gaps G-01~G-10 + D4 GAP-P1/P2/P3 + 三断链①②③ |
| 拓扑验证 / 策略模拟 | 配套 ipynb：11 节点 12 边 Kahn 拓扑排序 + 批次校验 + 关键路径；真实日分布驱动的四种同步策略对比；孤儿表稀释模拟 |

*配套实验：`第15周-Day5-开发节奏定轨-Backlog依赖与同步机制模拟.ipynb` —— DAG 拓扑验证、同步策略量化对比（感知延迟/成本）、表增长稀释模拟，全部代码 cell 执行通过 verify_ipynb。*
