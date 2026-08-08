# PT-W2-D7：⚡ 组装 MI CRE Ontology Graph v0.1

> 📅 Week 2 - Day 7（8/9 周六）
>
> **并行轨道：Business Semantic Architecture**
>
> **今天是 W2 收官日**：把六天抽取的六维度语义构件组装成一张全景图。
>
> **核心问题**：六维度抽取的全景图长什么样？AI Agent 拿到它能做什么？

---

## 一、为什么要"组装"？

过去六天，我们逐维度抽取了 Entity、Relationship、Lifecycle/Event、Rule、Capability、Policy。但这些构件目前是**六张独立的清单**。

Ontology 的力量不在于清单本身，而在于**清单之间的交叉引用**：

```
Entity ←→ Relationship      （谁和谁连接）
Entity ←→ Lifecycle         （每个实体的状态轴）
Lifecycle ←→ Event          （每次迁移发出什么事件）
Event ←→ Rule               （什么规则约束这次迁移）
Rule ←→ Capability          （规则触发什么动作）
Capability ←→ Policy        （动作需要什么授权）
```

> **AI Agent 需要的不是六张表，而是一张可遍历的语义图。** 它从任何一个节点出发，都能找到所有关联信息。

---

## 二、MI CRE Ontology Graph v0.1 全景

### 2.1 六维度抽取汇总

| 维度 | 抽取来源 | 构件数量 | 成熟度 | 关键缺口 |
|------|---------|---------|--------|---------|
| **Entity + Identity** | Domain Model §3 Object Ownership Matrix | P0: 25 个 / P1: 20 个 → 分为 4 种本体类型 | ★★★★☆ | 缺业务身份路径声明（仅有技术 ID） |
| **Relationship** | ADR-006 §3 四类关系 | 4 类关系框架 + 部分语义谓词 | ★★★☆☆ | 缺完整语义谓词清单（部分仍是 FK） |
| **Lifecycle + Event** | effect-registry.yaml + 域矩阵状态定义 | 5 类冻结 Effect + 资源七态 + 合同六态 | ★★★★☆ | 合同状态机缺显式合法迁移路径声明 |
| **Rule** | CRE BCM 域文件 01-06 业务规则列 | ~40 条规则（3 类：校验/联动/不变量） | ★★☆☆☆ | 大量规则仍埋在代码 if-else，未显式声明 |
| **Capability** | BCM capability 行 + capability-traceability-matrix | 14 域 × 平均 5 能力 ≈ 70 个 capability 标识 | ★★★☆☆ | 粒度太粗，缺 Skill 映射；BCM 编码与 LangChat Capability 未对齐 |
| **Policy** | MI 审批流 + LangChat ApplicationContract §4.2 | 5 类审批流 × 3 个 Policy 字段 | ★★☆☆☆ | Policy 隐式在 K2/BPM 配置中，未声明到 Ontology 层 |

### 2.2 Ontology Graph 结构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                  MI CRE Ontology Graph v0.1                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Entity Layer                              │   │
│  │                                                              │   │
│  │  组织实体    空间实体     主体实体     契约实体    财务实体   │   │
│  │  Project     Resource     Merchant     Contract     Bill/AR  │   │
│  │  ───────     ────────     ────────     ────────     ───────  │   │
│  │  (1个)       Unit(层级)   Lead/Opp     Clause       Payment  │   │
│  │              Building     Customer     Occupancy    Invoice  │   │
│  │              Floor/Zone   Member                    AcctEntry│   │
│  │                                                              │   │
│  │  + 事实构件: RevenueEvidence, EnergyReading, ContractClause  │   │
│  │  + 活动实体: OperationTask, ServiceTicket, Campaign         │   │
│  └────────────────────────┬────────────────────────────────────┘   │
│                           │                                         │
│           ┌───────────────┼───────────────┐                        │
│           ▼               ▼               ▼                        │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │ Identity    │ │ Relationship │ │  Lifecycle   │                │
│  │ Layer       │ │ Layer        │ │  Layer       │                │
│  │             │ │              │ │              │                │
│  │ 空间路径    │ │ 身份引用     │ │ 资源七态     │                │
│  │ Project→    │ │ is_signed_by │ │ 合同六态     │                │
│  │  Building→  │ │ applies_to   │ │ 账单状态机   │                │
│  │  Floor→     │ │              │ │              │                │
│  │  Unit       │ │ 结构组成     │ │ 迁移声明:    │                │
│  │             │ │ contains     │ │ available    │                │
│  │ 证件路径    │ │              │ │  → reserved  │                │
│  │ 统一社会    │ │ 层级包含     │ │  → in-use    │                │
│  │ 信用代码    │ │ is_located_in│ │  → available │                │
│  │             │ │              │ │              │                │
│  │ D-014 唯一  │ │ 迁移效应     │ │ Event 来源:  │                │
│  │  真值来源   │ │ emits        │ │ transition_  │                │
│  │             │ │ effect       │ │ emitted      │                │
│  │             │ │              │ │ externally_  │                │
│  │             │ │              │ │ observed     │                │
│  │             │ │              │ │ command_     │                │
│  │             │ │              │ │ result       │                │
│  │             │ │              │ │ policy_      │                │
│  │             │ │              │ │ derived      │                │
│  └─────────────┘ └──────────────┘ └──────┬───────┘                │
│                                          │                          │
│                          ┌───────────────┼──────────┐              │
│                          ▼               ▼          ▼              │
│                 ┌──────────────┐ ┌────────────┐ ┌──────────┐      │
│                 │ Effect       │ │ Rule       │ │ Policy   │      │
│                 │ Registry     │ │ Layer      │ │ Layer    │      │
│                 │              │ │            │ │          │      │
│                 │ 5 类冻结:    │ │ 校验规则   │ │ 审批流   │      │
│                 │ state-trans  │ │ 联动规则   │ │ → scope  │      │
│                 │ occupancy    │ │ 不变量规则 │ │ → review │      │
│                 │ financial    │ │            │ │   gate   │      │
│                 │ lead-convert │ │ ~40条抽取  │ │          │      │
│                 │ maintenance  │ │ (3类型)    │ │ 5类审批  │      │
│                 │              │ │            │ │ 流抽取   │      │
│                 └──────────────┘ └─────┬──────┘ └────┬─────┘      │
│                                        │             │             │
│                                        └──────┬──────┘             │
│                                               ▼                    │
│                                      ┌────────────────┐            │
│                                      │  Capability    │            │
│                                      │  Layer         │            │
│                                      │                │            │
│                                      │ 14域 × ~5能力  │            │
│                                      │ = ~70 capability│           │
│                                      │                │            │
│                                      │ 缺口:          │            │
│                                      │ Skill 映射     │            │
│                                      │ 粒度细化       │            │
│                                      │ LangChat 对齐  │            │
│                                      └────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、以"铺位 A101"为例：六维度交叉引用

这是 Ontology Graph 最核心的价值——**从任何一个 Entity 出发，沿六维度遍历**。

```
Entity: Resource Unit "A101"
│
├─[Identity]
│  类型: 空间实体（可租赁最小单元）
│  业务身份路径: 龙湖时代天街 → A栋 → 1F → A101
│  技术身份: resource_code = "A101"
│  真值主人: Asset Foundation Context（D-014）
│
├─[Relationship]
│  ├─ is_located_in → Floor "1F"（层级包含）
│  ├─ contains → Energy Meter #EM-001（结构组成）
│  ├─ is_referenced_by → Contract #CT2026-0888（身份引用）
│  └─ emits_effect_when → Contract signed→active（迁移效应）
│
├─[Lifecycle]
│  当前状态: delivered/in-use（使用中）
│  状态机: planned → created → available → reserved → in-use
│  合法迁移: in-use → available（需退场完成）
│
├─[Event]
│  当前事件: ContractActivated（合同生效触发）
│  事件来源: transition_emitted（合同状态迁移自然发出）
│  产出 Effect: occupancy-effect（A101 被占用）
│
├─[Rule]
│  ├─ 不变量: 面积 > 0；resource_code 全局唯一
│  ├─ 联动: 合同 active 时，铺位不可重新出租
│  └─ 校验: 退场需 inspection 完成才可恢复 available
│
├─[Capability]
│  ├─ 可调用: 创建退场工单、查询铺位状态、变更铺位属性
│  └─ 不可调用: 直接改状态为 available（需走退场流程）
│
└─[Policy]
   ├─ required_scopes: ["lease:write", "asset:read"]
   ├─ effect_policy: conditional_write（会改铺位状态）
   └─ human_review_gate: mandatory（退场需人审确认）
```

> **这就是 AI Agent 理解"A101"所需的完整语义。** 有了这张图，Agent 可以回答：
> - "A101 现在能不能出租？" → 查 Lifecycle + Rule
> - "为什么不能？" → 查 Relationship + Event + Effect
> - "需要做什么才能出租？" → 查 Capability + Policy
> - "谁有权操作？" → 查 Policy → required_scopes

---

## 四、六维度交叉引用矩阵

| 从＼到 | Entity | Relationship | Lifecycle | Rule | Capability | Policy |
|--------|--------|-------------|-----------|------|-----------|--------|
| **Entity** | — | 每个实体有哪些关系 | 每个实体有什么状态机 | 每个实体的不变量 | 每个实体可执行什么操作 | 每个实体的操作需什么授权 |
| **Relationship** | 关系连接哪些实体 | — | 关系的状态变化（如 Occupancy 生灭） | 关系的存在性约束 | 关系操作（创建/解除关系） | 关系操作授权 |
| **Lifecycle** | 状态属于哪个实体 | 迁移影响哪些实体 | — | 哪些规则守卫这个迁移 | 迁移触发什么 Capability | 迁移需什么审批 |
| **Rule** | 规则约束哪个实体 | 规则涉及哪些关系 | 规则守卫哪个迁移 | — | 规则触发什么动作 | 规则的例外由谁审批 |
| **Capability** | 操作哪个实体 | 操作什么关系 | 引起什么迁移 | 受什么规则约束 | — | 需什么授权 |
| **Policy** | 授权哪个实体的操作 | 授权什么关系操作 | 授权什么迁移 | 覆盖哪些规则例外 | 约束哪些 Capability | — |

> **这张矩阵就是 Ontology Compiler 的遍历规则**——下一周（PT-W3）会深入。

---

## 五、成熟度评估与下周导航

### 5.1 各维度成熟度雷达图

```
          Entity (★★★★)
             ╱╲
            ╱  ╲
           ╱    ╲
Lifecycle ╱      ╲ Relationship
(★★★★)   ╱        ╲ (★★★)
         ╱──────────╲
Capability ╲        ╱ Rule
  (★★★)    ╲      ╱  (★★)
            ╲    ╱
             ╲  ╱
          Policy (★★)
```

**解读**：
- **强项**（★★★★）：Entity 和 Lifecycle — 你已经有了完整的对象清单和状态定义
- **中等**（★★★）：Relationship 和 Capability — 框架有了，但语义谓词和 Skill 映射不完整
- **弱项**（★★）：Rule 和 Policy — 大量内容还隐式在代码和 K2 配置中

### 5.2 W2 输出物清单

| 输出 | 状态 | 价值 |
|------|------|------|
| Entity 分类体系（4 种本体类型） | ✅ 完成 | Agent 知道"这是什么类型的东西" |
| Identity 业务身份路径模板 | ✅ 完成 | Agent 能按业务路径定位对象 |
| Relationship 语义谓词清单 | ⚠️ 部分完成 | Agent 知道"它们怎么连"，但部分仍是 FK |
| Lifecycle 状态机 + Event 声明 | ✅ 完成（资源/合同） | Agent 能沿状态链推理 |
| Effect 交叉引用（迁移→影响） | ✅ 完成 | Agent 知道"状态变了会影响谁" |
| Rule 三类分类 + 抽取模板 | ✅ 完成（模板），⚠️ 部分（内容） | Agent 知道"什么约束推理" |
| Capability → Skill 映射缺口 | ⚠️ 识别但未补齐 | Agent 知道"能做什么"但粒度不够 |
| Policy 抽取六步法 | ✅ 完成（方法论） | Agent 知道"需要什么授权" |

### 5.3 对 PT-W3 的导航

下周（PT-W3: Ontology → Agent Architecture）将基于今天的 Ontology Graph v0.1，解决：

| W2 发现的缺口 | W3 怎么解决 |
|-------------|-----------|
| Rule 和 Policy 大量隐式 | Ontology Compiler 如何把显式声明编译为 Agent 可消费的规则 |
| Capability 粒度太粗 | Compiler 如何把 BCM 能力行细化为 Agent 可调用的 Skill |
| 六维度交叉引用 | Compiler 如何自动推导交叉引用（如迁移→Effect→Rule 三链路） |
| 三套 ADR 分离 | LangChat ADR + CRE BCM ADR + MI Domain Model 在 Ontology 层统一 |

---

## 六、架构师视角：本周认知变化总结

```
本周开始时（W2 D1）：
  "我有 Domain Model + BCM + ADR-006 + effect-registry，
   但不知道怎么让 AI Agent 用上这些。"

本周结束时（W2 D7）：
  "我发现这些资产恰好覆盖了 Ontology 六维度的大部分构件。
   强项是 Entity 和 Lifecycle（已有资产可以直接复用），
   弱项是 Rule 和 Policy（需要从代码和审批流中抽取显式声明）。

   关键不是'设计一套新的 Ontology'，
   而是把这些已有资产用统一的语义层串起来，
   形成一张 AI Agent 可遍历的语义图。"
```

### 认知转变清单

| # | 以前 | 现在 |
|---|------|------|
| 1 | Entity = 数据库表 | Entity = 业务世界中独立存在的概念，有本体类型（实体/关系实体/事实构件/活动实体） |
| 2 | Identity = 主键 ID | Identity = 业务身份路径（空间路径、证件路径、时间路径） |
| 3 | Relationship = 外键 | Relationship = 四类语义关系，每类有不同的 Agent 推理价值 |
| 4 | status = 字段值 | Lifecycle = 状态机 + 合法迁移 + 守卫条件 |
| 5 | 联动逻辑 = 代码 if-else | Effect = 声明式迁移影响规则，类型已冻结 |
| 6 | 业务规则 = 散落在代码和文档里 | Rule = 三类显式声明（校验/联动/不变量），AI 可推理 |
| 7 | 能力 = API 端点 | Capability = Ontology 行动空间声明，需细化并映射 Skill |
| 8 | 审批流 = K2/BPM 配置 | Policy = Ontology 授权层声明，Compiler 编译为 ApplicationContract |
| 9 | 六套资产各管各的 | Ontology Graph = 六维度交叉引用的语义图 |
| 10 | AI Agent 要理解企业 = 读代码 | AI Agent 要理解企业 = 遍历 Ontology Graph |

---

## 七、练习（10 分钟）

**组装练习**：选择一个你熟悉的业务对象（如 Merchant 商户），尝试仿照 §三 的格式，写出它的六维度交叉引用。

重点感受：
1. 哪些维度你写得很快？（= 已有资产覆盖好）
2. 哪些维度你卡住了？（= 需要回去补的真实缺口）
3. 如果你是 AI Agent，拿到这张图你能回答什么问题？还差什么？

> **下周预告（PT-W3）**：Ontology → Agent Architecture。本周我们得到了 Ontology Graph v0.1（语义图），下周看 **Ontology Compiler** 如何把这张图编译成 Agent 可执行的指令。你的 BCM ADR-001 就是 Compiler 的雏形，LangChat ApplicationContract 就是编译产物。
