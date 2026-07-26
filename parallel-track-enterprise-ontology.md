# 并行学习轨道：Business Semantic Architecture（企业业务语义架构）

> **定位**：主线学习计划的并行轨道，不修改主线。
>
> **创建日期**：2026-07-26
>
> **冻结状态**：✅ 已冻结（v4 最终版 — 经外部教练四轮确认）
>
> **目标角色**：AI Native Enterprise Software Architect
>
> **核心转变**：不是"学 Ontology"，而是"用 Ontology 视角重新理解并升级已有 Domain Model"

---

## 什么是 Business Semantic Architecture

```
Business Semantic Architecture

= AI 时代企业软件架构中，
  用于描述业务世界、能力和规则的语义设计方法
```

它不是单一理论，而是一个能力栈：

```
Ontology          描述"是什么"
DDD               描述"如何实现"
Capability Model  描述"能做什么"
Policy Model      描述"什么条件下允许做"
Skill Model       描述"Agent 如何执行"
```

> **Ontology = 描述企业业务世界的语义操作系统。**
> 不是六个模块的清单，而是一个让 AI 能理解企业业务的统一语义层。

---

## 为什么开这个轨道

Jason 已经做出了大量 Ontology 雏形，只是没用这个词：

| 已有资产 | 位置 | Ontology 对应 |
|---------|------|--------------|
| MI Domain Model v1.0（17 个 Bounded Context） | `docs/lanlnk/out/prd/商管系统/output/domain-model/` | Bounded Context 划分（DDD 战略设计） |
| Object Ownership Matrix | Domain Model §3 | Concept + Ownership 归属 |
| ADR-006 四类对象关系 | `docs/lanlnk/config/ontology/cre-business-capability-matrix/` | Relationship 分类 |
| effect-registry.yaml（5 类冻结） | CRE BCM 目录 | Lifecycle Transition Effect |
| CRE BCM 14 域 + 6 个 ADR published | `docs/lanlnk/config/ontology/cre-business-capability-matrix/` | Business Rule + Capability |
| business-ontology.yaml | `docs/lanlnk/config/ontology/` | Ontology 模块→能力→场景结构 |
| MI 代码（307 表 + Go 模块化单体） | `/root/mi` | Domain Model 代码实现 |
| LangChat ADR-001~008 | `docs/lanlnk/out/prd/langchat/output/review/` | AI 平台架构 |

**缺的不是 Ontology 知识，缺的是一个统一语义层，把 DDD → Ontology → Agent → Digital Employee 串起来。**

所以路线不是"从零学"，而是：

```
已有业务模型
    ↓
Ontology 视角重新解释
    ↓
补充缺失语义
    ↓
形成 Enterprise Semantic Model
    ↓
驱动 LangChat Agent + Digital Employee
```

---

## Ontology 定位

```
企业现实业务世界
    ↓
Ontology / Semantic Model（描述：有什么、什么关系、什么约束）
    ↓                        ↓
Domain Model              Knowledge Model
（怎么软件实现）            （什么知识需要被检索）
    ↓                        ↓
Code                      RAG / Knowledge Base
```

---

## 学习者画像

### 优势

- 26 年 ERP 领域经验，熟悉企业软件全流程
- **已经做出了 MI Domain Model v1.0 + CRE BCM + 6 个 ADR + effect-registry**
- 正在设计 LangChat Digital Employee 平台
- 已有三套 ADR 体系在并行（LangChat + CRE BCM + MI Domain Model）

### 需要补建的认知

- ❌ 不熟悉 DDD（领域驱动设计）形式化方法论
- ❌ 缺少 Ontology → Agent 的统一语义层视角

### 教学策略

**战略设计为主（80%），战术设计为辅（20%）。**
**用真实材料（MI Domain Model + CRE BCM + LangChat ADR）做案例，不用虚构例子。**

---

## 学习原则

### 所有概念必须回答

> "这个东西未来如何帮助 AI Agent 理解企业？"

### 每天绑定真实材料

不停留在理论。**每天必须对照 MI Domain Model 或 CRE BCM 的实际文件。** 用你的真实产出做案例。

### 严格控制范围

4 周内**不涉及**：RDF / OWL / SPARQL / 图数据库 / 向量数据库实现细节。

---

## 关键认知：Ontology 不是六个模块

⚠️ **Ontology 不是一份清单：Concept ✅ Relationship ✅ Lifecycle ✅ 就算完成了。**

Ontology 是描述企业业务世界的**语义操作系统**，关注：

| 维度 | 问什么 | 代码里长什么样 | Ontology 要变成什么 |
|------|--------|-------------|------------------|
| Entity | 世界里有什么东西？ | `table: lease` | Lease 是一个业务实体，不是一条记录 |
| Identity | 它如何被唯一识别？ | `id: 12345` | Space = Building → Floor → Unit → Shop（业务身份） |
| Relationship | 事物如何连接？ | `lease.space_id FK` | Lease **occupies** Space（语义关系，不是外键） |
| State / Event | 业务如何变化？ | `status='terminated'` | Lease: Created → Activated → Expired → Terminated，effects: release Space, stop Billing |
| Rule | 为什么这样变化？ | `if-else code` | "Lease 过期后 Space 释放，但需 inspection 完成才可用" |
| Capability | 可以做什么？ | `API endpoint` | Lease Management Capability: Create/Renew/Calculate/Generate |

---

## 4 周总览

```
Week 1（7/27-8/2）：   DDD → Semantic Model（重新认识已有 Domain Model）
Week 2（8/3-8/9）：    Business Ontology Extraction（从已有材料抽取语义）
Week 3（8/10-8/16）：  Ontology → Agent Architecture（含 Ontology Compiler）
Week 4（8/17-8/23）：  Semantic Model + Digital Employee Validation
```

与主线对应关系：

| 日期 | 主线 | 并行轨道 | 认知关联 |
|------|------|---------|---------|
| 7/27-8/2 | W9: Domain Deep Dive | PT-W1: DDD → Semantic Model | 对象为什么存在 ↔ 语义层重新解释 |
| 8/3-8/9 | W10: Governance | PT-W2: Ontology Extraction | 治理规则 ↔ 从已有材料抽取 Rule/Policy |
| 8/10-8/16 | W11: Code Reality | PT-W3: Ontology → Agent | 现实 Gap ↔ Ontology Compiler + Agent |
| 8/17-8/23 | W12: Vision Intelligence | PT-W4: Semantic Model | 新领域 ↔ 完整 Semantic Model + 验证 |

---

## 每日学习要求

- **时间**：每天 ≤ 30 分钟
- **推送**：和主线 6:00 合并推送

### 每日推送格式

```
📅 Week X - Day Y

今日主题：XXX

━━━【主线 · LangChat】━━━
[主线学习内容]

━━━【Business Semantic Architecture】━━━
[并行轨道学习内容]

━━━【连接思考】━━━
今天两个主题在认知上有什么关联？

━━━【架构师视角】━━━
今天改变什么设计判断？
以前：XXX
现在：XXX

━━━【练习】━━━
一个思考题（5分钟）
```

---

## Week 1：DDD → Semantic Model（7/27 - 8/2）

### 目标

**不是"学什么是 Domain Model"，而是"你已经做了 Domain Model，现在用 Ontology 视角重新认识它"。**

### 输出

**《MI CRE Semantic Gap Analysis v0.1》**

| Ontology 元素 | 已有资产 | 缺口 |
|--------------|---------|------|
| Entity | MI Domain Model Object Ownership Matrix | 缺业务定义（只有技术定义） |
| Identity | 表 ID / 编码 | 缺业务身份层级 |
| Relationship | ADR-006 四类关系 | 缺语义命名（occupies/signs/governs） |
| Lifecycle | status 字段 + effect-registry | 缺完整状态机 + Event 声明 |
| Rule | 部分代码 + BCM 规则 | 未显式化（AI 不可推理） |
| Capability | CRE BCM capability 行 + MI traceability | 缺 Skill 映射 |
| Policy | 审批流代码 | 缺 AI 执行约束声明 |

这份 Gap Analysis 成为后续三周的导航。

### 每日安排

| Day | 日期 | 主题 | 核心问题 | 真实材料 |
|-----|------|------|---------|---------|
| D1 | 7/27 周日 | **你已经做了 Domain Model** | 我做的 17 个 Context 就是 DDD？ | 读 MI Domain Model v1.0 §2 Context Coverage Matrix。对照"什么是 Domain Model"定义。P0 的 9 个 Full Model = Core Domain |
| D2 | 7/28 周一 | **DDD 战略设计 — 你已经做了** | 我的 Bounded Context 划分对不对？ | 读 MI Domain Model §2 + §3。17 个 Context 的边界划分。对照 DDD 战略设计原则验证 |
| D3 | 7/29 周二 | **DDD 战术速览 + 你的 Aggregate** | Entity / Value Object / Aggregate 在 MI 里长什么样？ | 读 MI Domain Model §3 Object Ownership Matrix。看你的 Aggregate 根和不变量。对照 DDD 战术概念 |
| D4 | 7/30 周三 | **为什么 Domain Model 不够（核心课）** | AI 读你的 Domain Model 能读懂吗？ | 读 ADR-006 四类对象关系。AI 能看到 Identity Reference，但"Lease 终止后影响什么"需要跨 ADR 推理。语义仍然隐式 |
| D5 | 7/31 周四 | **Ontology 能补充什么** | Ontology 视角看你的资产，缺了什么？ | 读 business-ontology.yaml。它已有模块→能力→场景结构。对照 Ontology 六维度（Entity/Identity/Relationship/State/Rule/Capability），识别缺口 |
| D6 | 8/1 周五 | **Ontology vs Knowledge Model vs RAG** | 三者在 LangChat + MI 里各自什么角色？ | 对照 LangChat RAG 实现 + MI 的数据查询能力 |
| D7 | 8/2 周六 | ⚡ **输出 MI CRE Semantic Gap Analysis v0.1** | 已有 vs 缺失的全景 | 汇总一周发现，输出 Gap Analysis 表 + Ontology 层级图（企业世界 → Ontology → 你的 Domain Model + Knowledge Model → Code） |

### W1 DDD 补课范围

**战略设计 80%（用 MI Domain Model 验证）：**

| DDD 概念 | 讲不讲 | MI 对照 |
|----------|--------|---------|
| Bounded Context | ✅ 重点 | 你的 17 个 Context |
| Context Map | ✅ 讲 | 你的跨 Context 集成契约（Domain Model §4） |
| Core / Supporting Domain | ✅ 讲 | P0（Core）vs P1（Supporting） |
| Subdomain | ✅ 讲 | 你的 14 个 CRE BCM 域 |

**战术设计 20%（速览）：**

| DDD 概念 | 讲不讲 | MI 对照 |
|----------|--------|---------|
| Entity / Value Object | ✅ 速览 | 你的 Object Ownership 里的对象 |
| Aggregate | ✅ 速览 | 你的 Aggregate 根 + 不变量 |
| Domain Event | ✅ 速览 | 你的 effect-registry |

---

## Week 2：Business Ontology Extraction（8/3 - 8/9）

### 目标

**不是"设计 Ontology"，而是"从已有材料中抽取 Ontology 语义"。**

```
MI Domain Model   → Entity Extraction
ADR-006           → Relationship Extraction
effect-registry   → Event Extraction
CRE BCM 域文件     → Rule Extraction
capability 行      → Capability Extraction
审批流             → Policy Extraction
```

### 输出

**MI CRE Ontology Graph v0.1** — 从已有材料抽取的语义图。

### 每日安排

| Day | 日期 | 构件 | 核心问题 | 真实材料 |
|-----|------|------|---------|---------|
| D1 | 8/3 周日 | **Entity + Identity 抽取** | 你的 Concept 清单全不全？业务身份是什么？ | MI Domain Model §3 Object Ownership Matrix。Property/Building/Space/Tenant/Lease/Contract/Billing/Payment。不只是表名，要看业务身份 |
| D2 | 8/4 周一 | **Relationship 抽取** | ADR-006 四类关系覆盖全了吗？语义命名够不够？ | ADR-006 四类关系。Identity Reference / Structural Composition / Hierarchical Containment / Lifecycle Transition Effect。检查是否覆盖所有 Concept 对 |
| D3 | 8/5 周二 | **Lifecycle + Event 抽取** | 状态机完整吗？Event 声明够不够？ | effect-registry.yaml（5 类冻结）+ MI Domain Model 状态定义。Lease: Draft→Signed→Active→Expiring→Expired→Terminated |
| D4 | 8/6 周三 | **Rule 抽取** | 业务规则在代码里还是在 Ontology 里？ | CRE BCM 域文件（01-06）。每个域的业务规则。看哪些是显式声明的、哪些还在代码 if-else 里 |
| D5 | 8/7 周四 | **Capability 抽取** | BCM capability 行 → LangChat Capability 映射 | capability-traceability-matrix.md + CRE BCM capability 行。对比 LangChat Capability 概念 |
| D6 | 8/8 周五 | **Policy 抽取 + Ontology Compiler 初探** | 审批流怎么变成 Policy？Ontology 怎么变成编译输入？ | MI 审批流（合同审批/减免审批）+ LangChat BCM ADR-001 业务组合编译器 |
| D7 | 8/9 周六 | ⚡ **组装 MI CRE Ontology Graph v0.1** | 六维度抽取的全景图 | 汇总六天抽取结果，输出 Ontology Graph v0.1 |

---

## Week 3：Ontology → Agent Architecture（8/10 - 8/16）

### 目标

理解 Ontology 在 AI Agent 架构中的角色，**特别加入 Ontology Compiler 概念**。

你的 LangChat + CRE BCM 实际上已经在做：

```
Business Model → Semantic Model → Capability → SkillRelease → ExecutionPlanIR
```

这本质就是 **Semantic Compiler** — 把业务语义编译成 Agent 可执行的指令。

### 完整架构链路

```
Ontology（企业业务世界模型）
    ↓ 编译输入
Ontology Compiler（语义→能力的编译器）
    ↓ 生成
Domain Model → Capability → Policy → Skill
    ↓ 编排
Agent Execution（数字员工执行）
    ↓ 调用
MCP Tool / Connector → Enterprise System
```

### 每日安排

| Day | 日期 | 主题 | 核心问题 | 真实材料 |
|-----|------|------|---------|---------|
| D1 | 8/10 周日 | **Agent 如何利用 Ontology** | Agent 规划任务时，Ontology 在起什么作用？ | LangChat Agent 架构 + MI 数字员工场景 |
| D2 | 8/11 周一 | **Ontology Compiler** | 你的 BCM ADR-001 就是 Semantic Compiler 的雏形 | CRE BCM ADR-001 业务组合编译器原则 + LangChat Compiler。语义→能力的编译链路 |
| D3 | 8/12 周二 | **Ontology 如何约束 Agent 认知** | Bounded Context = Agent 认知边界 | MI Domain Model 的 Context 边界 = Agent 应该遵循的认知边界 |
| D4 | 8/13 周三 | **Policy 如何约束 Agent 执行** | 即使知道怎么做，没有授权也不能做 | LangChat ApplicationContract 的 effect_policy / required_scopes + MI 审批流 |
| D5 | 8/14 周四 | **Ontology 驱动 Digital Employee** | 招商员工 / 运营员工 / 财务员工的语义定义 | 每个 Digital Employee 对应哪些 Context + Capability + Policy |
| D6 | 8/15 周五 | **三套 ADR 在 Ontology 层统一** | LangChat ADR + CRE BCM ADR + MI Domain Model 怎么统一？ | 你已有的三套 ADR 体系。看它们在 Ontology 层的统一视图 |
| D7 | 8/16 周六 | ⚡ **输出：LangChat × Ontology × Compiler 集成方案** | Ontology + Compiler 在你的架构里放哪里？ | 集成方案文档 |

---

## Week 4：Semantic Model + Digital Employee Validation（8/17 - 8/23）

### 目标

输出 **MI CRE Enterprise Semantic Model v0.1**（毕业作品），并通过数字员工验证。

### 毕业作品结构

```
MI CRE Enterprise Semantic Model v0.1

├── Domain Model         — 17 个 Bounded Context（已有，升级）
├── Ontology Model       — Entity + Identity + Relationship（已有 ADR-006，补语义命名）
├── Capability Model     — 能力地图（已有 BCM，补 Skill 映射）
├── Rule Model           — 业务规则（从代码抽取，显式化）
├── Event Model          — Lifecycle + Event（已有 effect-registry，补完整状态机）
├── Policy Model         — 执行策略（从审批流抽取，补 AI 约束声明）
└── Agent Mapping        — 数字员工定义映射（新增）
```

这不是"从零创建"，而是**把已有的 Domain Model v1.0 + BCM + ADR-006 升级为完整 Semantic Model**。

### 每日安排

| Day | 日期 | 任务 | 输出 |
|-----|------|------|------|
| D1 | 8/17 周日 | **升级 Ontology Model**：基于 Object Ownership + ADR-006，补语义命名和业务身份 | Entity + Identity + Relationship 模型 |
| D2 | 8/18 周一 | **升级 Lifecycle + Event**：基于 effect-registry，补完整状态机和 Event 声明 | Lifecycle 状态机 + Event 清单 |
| D3 | 8/19 周二 | **补 Rule Model**：从 BCM 域文件 + 代码抽取，显式化为 AI 可推理格式 | Business Rule 清单 |
| D4 | 8/20 周三 | **升级 Capability + Policy**：基于 BCM + capability-traceability，补 Policy 层和 Skill 映射 | Capability Map + Policy 规则 + Skill Mapping |
| D5 | 8/21 周四 | **Agent Mapping**：定义数字员工（招商/运营/财务），每个对应哪些 Context + Capability + Policy | Digital Employee 定义 |
| D6 | 8/22 周五 | **组装 Semantic Model v0.1 + 验证设计** | 完整文档 + 验证场景设计 |
| D7 | 8/23 周六 | **🔄 Digital Employee Validation** | 验证报告 |

### 最终验证：Digital Employee Validation

设计一个数字员工场景验证 Semantic Model 是否可用：

**场景：招商运营数字员工**

输入一个业务问题：

> "A101 铺位为什么不能出租？"

Agent 需要能够：

1. **查 Entity** — 定位 Space A101
2. **查 Relationship** — A101 关联了哪些 Lease / Contract
3. **查 Lifecycle** — 当前 Lease 处于什么状态
4. **查 Rule** — "存在未完成退租流程的 Space 不可出租"
5. **查 Policy** — 是否有特殊豁免条件
6. **调用 Capability** — 创建 Inspection Task 推进流程

**输出**：

```
原因：该空间存在未完成退租流程
依据：Lease Termination Rule #003
当前状态：Lease 已提交终止申请，Inspection 未完成
建议动作：创建 Inspection Task，完成后 Space 自动释放
```

**验证标准**：

| 级别 | 能力 | 必达/加分 |
|------|------|----------|
| L1 语义理解 | Agent 能定位 Entity + Relationship | ✅ 必达 |
| L2 业务链推理 | Agent 能从 Lifecycle 推断当前可用性 | ✅ 必达 |
| L3 规则判断 | Agent 能根据 Rule 判断"能不能" | ⚠️ 加分 |
| L4 Policy 判断 | Agent 能根据 Policy 判断审批路径 | ⚠️ 加分 |
| L5 动作建议 | Agent 能调用 Capability 建议下一步 | ⭐ 超额 |

---

## 4 周交付物

```
Week 1: MI CRE Semantic Gap Analysis v0.1（已有 vs 缺失的全景）
Week 2: MI CRE Ontology Graph v0.1（从已有材料抽取的语义图）
Week 3: LangChat × Ontology × Compiler 集成方案
Week 4: MI CRE Enterprise Semantic Model v0.1 + Digital Employee Validation 报告
```

---

## 信息源（全部使用真实材料）

| 来源 | 路径 | 用途 |
|------|------|------|
| MI Domain Model v1.0 | `docs/lanlnk/out/prd/商管系统/output/domain-model/MI-CRE-ERP-Domain-Model-v1.0.md` | Context 划分 + Object Ownership + Aggregate |
| CRE BCM Master Matrix | `docs/lanlnk/config/ontology/cre-business-capability-matrix/00-Master-Matrix.md` | 14 域总览 + 域边界 |
| CRE BCM ADR-001~006 | `docs/lanlnk/config/ontology/cre-business-capability-matrix/ADR-*.md` | 业务语义层架构决策 |
| effect-registry.yaml | `docs/lanlnk/config/ontology/cre-business-capability-matrix/effect-registry.yaml` | Lifecycle Transition Effect |
| business-ontology.yaml | `docs/lanlnk/config/ontology/business-ontology.yaml` | 模块→能力→场景结构 |
| MI 代码仓库 | `/root/mi` | 实际代码事实（表结构/业务逻辑） |
| LangChat ADR-001~008 | `docs/lanlnk/out/prd/langchat/output/review/ADR-*.md` | AI 平台架构 |
| capability-traceability-matrix | `mi/docs/capability-traceability-matrix.md` | 能力追溯矩阵 |
| MI Domain Model Gap Analysis | `docs/lanlnk/out/prd/商管系统/output/domain-model/MI-Domain-Model-Gap-Analysis-*.md` | 已有的差距分析 |

---

## 最终目标

具备 **AI Native Enterprise Software Architect** 能力：

- 能用 Ontology 视角审视和升级已有 Domain Model
- 能设计 Ontology Compiler（语义→能力的编译链路）
- 能把 CRE BCM + Domain Model 升级为 Enterprise Semantic Model
- 能设计 Capability + Policy 约束体系
- 能定义 Digital Employee 并验证其业务能力
- 能在 LangChat / MI CRE 产品中落地 Semantic Model

---

## 与主线的关系

```
主线（LangChat Mental Model）：
  "平台架构怎么设计？"

并行轨道（Business Semantic Architecture）：
  "AI Agent 怎么理解企业业务？"

交汇点：
  LangChat Capability         ↔ Ontology Capability
  LangChat Digital Employee   ↔ Agent Mapping（Semantic Model）
  LangChat ApplicationContract ↔ Policy Model
  LangChat Compiler           ↔ Ontology Compiler（BCM ADR-001）
  LangChat Governance (W10)   ↔ Policy Model
  MI Domain Model             ↔ Enterprise Semantic Model
  CRE BCM ADR-006             ↔ Ontology Relationship + Lifecycle
  effect-registry             ↔ Ontology Event Model
```

两条轨道最终汇聚到同一个产品：**AI Native Enterprise Software**。

未来路线：

```
Week 8    LangChat End-to-End ✅
Week 9    Domain Deep Dive + BSA W1 (DDD → Semantic Model)
Week 10   Governance + BSA W2 (Ontology Extraction)
Week 11   Code Reality + BSA W3 (Ontology → Agent + Compiler)
Week 12   Vision Intelligence + BSA W4 (Semantic Model + Validation)
Week 14+  MI CRE AI Native ERP
```
