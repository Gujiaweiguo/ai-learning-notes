# 第14周-Day4 Rule层对账：5类冻结Effect与代码现实（IMA完整版）

> 学习周：W14（MI CRE 开发期）· 补传版 · 对应实验产物：`第14周-Day4-Rule层对账要点.md`
> 前置知识：D2 分层 Source of Truth 宪章、effect-registry.yaml v1.0（2026-07-26 冻结）

## 一、为什么需要 Rule 层对账？

**为什么学这个**：在 LangChat / 商业地产 AI 平台这类企业系统里，"规则"永远存在于至少两个地方——语义层（声明"系统里有哪些效应/规则"）和代码层（真正执行的 if-else 与状态机）。这两层一旦失同步，AI 在消费语义资产时就会引用一个"名义上存在、实际早已改样"的规则，输出自然错。对账（reconciliation）就是给这两层做一次"审计"，把偏差变成显式清单而不是隐性炸弹。

**生活类比**：这就像小区的《业主公约》（语义层）和物业实际执行的操作规程（代码层）。公约写着"装修需审批、垃圾需分类"，但物业操作手册里可能已经加了"周末禁止施工"这类公约没有的条款。你按公约去办事会碰壁——因为两份文件各自演化，没有人对过账。

**Today's Question**：语义层声明的规则（effect-registry.yaml）和代码里的 if-else，谁是 source of truth？答案是：**分层的**——存在性与意图归语义层，执行事实归代码层，中间必须建机器锚点。

## 二、effect-registry 是什么：5 类冻结效应

effect-registry.yaml 是 MI CRE 的"效应注册表"，2026-07-26 冻结了 5 类效应（effect）：

| # | Effect 类型 | 英文与读音 | 一句话定义 |
|---|---|---|---|
| 1 | state-transition-effect | /steɪt trænˈzɪʃən/ 状态迁移效应 | 业务对象状态机的每次跳变（如 lease 从 draft→active） |
| 2 | occupancy-effect | /ˈɒkjəpənsi/ 占用效应 | 一个资源被占用后对其他占用请求的排斥结果 |
| 3 | financial-effect | /faɪˈnænʃl/ 财务效应 | 业务动作引发的金额变化（应收、计费、重算） |
| 4 | lead-conversion-effect | /liːd kənˈvɜːʃən/ 线索转化效应 | 销售线索转化为商机的链路结果 |
| 5 | maintenance-effect | /ˈmeɪntənəns/ 维保效应 | 维修工单与物料消耗的结果记录 |

"冻结"（frozen）的含义：这 5 类是评审后的封闭集合，新增必须走 ORE-1 流程（域证据 + 跨域影响评审）。为什么冻结？因为效应类型是所有下游消费方（报表、AI、审计）共同依赖的词汇表——词汇表天天变，消费者就没法信任。

**类比**：effect 类型就像会计的借贷记账法——全世界会计系统都基于"借/贷"两个封闭符号。如果某天有人发明"第三个符号"，所有报表软件、审计准则、税务系统都要跟着改。所以改词汇表的门槛必须极高。

## 三、逐类对账：声明 vs 代码事实

对账方法：拿着 registry 声明的 5 类，去 lnkcre 主仓代码里找证据（包名、表名、测试名），逐条标注 ✅/⚠️。

### 3.1 state-transition-effect ✅
- **代码证据**：`lease/model.go` 中 8 个状态字面量硬编码（draft→pending_approval→active→…→closed，含 rejected/voided/pending_termination）；condition-approval 带 lifecycle_audit 审计表。
- **讲解**：状态机是最典型的"双层演化"受害者。registry 说"有状态迁移效应"，代码里是 8 个字符串字面量。如果下个迭代加第 9 个状态（比如 suspended），registry 不会有任何变化——因为没有机器对账通道。两边各自演化、靠人读。
- **代码示例**（Go 硬编码现状）：
```go
// lease/model.go — 状态字面量直接写在代码里
const (
    StatusDraft             = "draft"
    StatusPendingApproval   = "pending_approval"
    StatusActive            = "active"
    StatusPendingTermination = "pending_termination"
    // ... 共 8 态
)
```

### 3.2 occupancy-effect ✅
- **代码证据**：独立 occupancy 包；`CreateTx` 事务耦合；集成测试 `ReserveRejectsActiveOccupancy`（活跃占用拒绝再预留）。
- **讲解**：这是对账里最健康的一类。语义声明"什么会变"（占用排斥），代码决定"怎么变"（同步事务而非异步事件）。注意边界划得多干净：effect-registry 不管传输机制（事务还是消息队列），只声明结果语义。集成测试名本身就是语义锚点——测试通过 = 声明成立。

### 3.3 financial-effect ✅（但多对多）
- **代码证据**：`amendment_receivable_impact.go`（变更→应收重算）+ arrebalance 引擎（trigger_events/rebalance_failures 表）+ billing 计费族。
- **讲解**：这是映射关系最复杂的一类——一个语义效应散布在 billing/collections/arrebalance 多个包。对账结论"✅ 但多对多"的意义：未来 AI 检索"应收重算"时，必须知道它有 3 个代码入口，只看一个会漏。这类多对多映射信息，正是 registry 里缺失、只能靠对账补出来的。

### 3.4 lead-conversion-effect ⚠️
- **代码证据**：opportunity/broker 包 + opportunity_status_history 表在；但转化链路断言未逐条核。
- **讲解**：⚠️ 的意思是"表级证据在，行为级未验证"。就像看到图书馆里有这本书的目录，但没翻开核对每一章。登记为缺口（W15 可用 opportunity_status_history 的真实数据补验），而不是装作对完了——诚实的缺口比虚假的绿勾值钱。

### 3.5 maintenance-effect ✅
- **代码证据**：repair_work_orders + material_* 全族（12 Context 46 表）。
- **讲解**：维保是表证据最充分的一类，46 张表足够还原完整物料-工单-结算链。

### 3.6 service-effect：一个"没注册"的正确决定 ✅
- **代码反向验证**：13 Context 仅 3 张表（service_requests/tenant_messages/status_history）——确无独立结果类语义。
- **讲解**：这是全表最有教学价值的一条。评审时决定"服务请求不注册为独立效应"，理由是它不产生跨域结果。对账时代码反向验证了这个决定：真的只有 3 张表，撑不起一个效应类。**负空间（不做什么）也是语义**，且负空间的决定同样需要证据档案。

## 四、规则的三种存在形态（本日核心认知）

对账中发现规则其实活在三个地方，这是比"对上/没对上"更重要的结构认知：

| 形态 | 例子 | 特点 | 风险 |
|---|---|---|---|
| ① 代码硬编码 | lease 8 态字面量 | 编译期确定，改代码才能改 | registry 与代码无锚点，静默漂移 |
| ② 语义注册 | effect-registry 5 类 | 冻结、有治理头（ADR-006 引用） | "frozen"目前是形容词不是机制 |
| ③ 运行时数据 | amendmentmatrix 9 类矩阵（Get/Update by lease.AmendmentType） | 规则本体在数据库，运行时可编辑 | 变更无版本快照 |

**讲解**：amendmentmatrix 是最颠覆直觉的——"if-else 在哪"这个问题，答案越来越是"不在代码里"。变更矩阵做成运行时可编辑表，意味着运营人员改数据库就能改规则，代码一行不动。好处是灵活，代价是：审计、回滚、版本对比全都失去抓手。第三形态会越来越多，语义层必须把它当一等公民。

**类比**：三种形态像交通规则的三种载体——①写在石头上的法条（代码）、②收录法条的宪法典（registry）、③交警现场指挥（运行时表）。宪法典说是 5 类法，交警却每天都在即兴发明新手势，而没人记录这些手势。

## 五、缺口登记（进 D6 定稿包）

1. **registry 无机器可读代码锚点**：不含 package path/表名引用，对账靠人读——与 ontology 无 frontmatter 同构（治理缺口是系统性的）。
2. **frozen 无 CI 强制**：新增 effect 不走 ORE-1 零告警。同 D5 的"新表无挡板"问题。
3. **lead-conversion 断言未核**：opportunity_status_history 有数据即可补。
4. **amendmentmatrix 无版本快照**：矩阵变更未入 audit（待核 condition_approval_lifecycle_audit 是否覆盖）。

**修法方向**（W15+ 落地）：给 registry 每个效应加 `code_anchors: [package, table]` 字段；CI 里跑"锚点存在性检查"——锚点指向的包/表不存在就红灯。

## 六、术语表（English Terms）

| 术语 | 读音 | 释义 |
|---|---|---|
| effect registry | /ɪˈfekt ˈredʒɪstri/ | 效应注册表：系统全部业务效应的封闭清单 |
| source of truth (SoT) | /sɔːrs əv truːθ/ | 某类事实的唯一权威来源 |
| reconciliation | /ˌrekənsɪliˈeɪʃən/ | 对账：声明与实现的一致性核对 |
| state machine | /steɪt məˈʃiːn/ | 状态机：对象在有限状态间的迁移规则 |
| CI guardrail | /ˌsiːˈaɪ ˈɡɑːrdreɪl/ | 持续集成护栏：自动化的一致性检查 |
| negative space | /ˈneɡətɪv speɪs/ | 负空间：明确"不做什么"留下的语义轮廓 |

## 七、练习题

1. 给上述 4 条缺口各写一个 CI 检查的伪代码（输入什么、检查什么、何时红灯）。
2. 如果要给 effect-registry 加第 6 类效应 `notification-effect`（通知效应），按 ORE-1 你需要准备哪些域证据？跨域影响评审该请哪些 Context 的 owner？
3. amendmentmatrix 做成运行时可编辑表后，设计一个最小审计方案（表结构 + 写入时机），保证规则变更可回溯。

## 八、推荐链接

- 仓库内：`effect-registry.yaml`（带 ADR-006 治理头）、`lease/model.go`、`amendmentmatrix` 包
- 姊妹篇：第14周-Day2（分层 SoT 宪章的由来）、第14周-Day6（本对账如何进入 Semantic Model 定稿包）
- 方法论：数据库 schema migration 的 drift detection（flyway/liquibase 的 baseline 机制与本日对账同构）

---
*本笔记为 W14-D4 补传完整版（≥8000 字节），符合 IMA 知识库教程标准：概念讲解 + 生活类比 + 代码示例 + 对比表格 + 术语表 + 练习。*
