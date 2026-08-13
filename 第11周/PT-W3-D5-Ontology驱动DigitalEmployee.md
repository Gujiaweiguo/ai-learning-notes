# PT-W3-D5：Ontology 驱动 Digital Employee — "数字员工的语义定义"

> 📅 Week 3 - Day 5 | 2026-08-14 周四
>
> **并行轨道：Business Semantic Architecture**
>
> **今日主题：每个数字员工 = 一组 Context + Capability + Policy 的语义绑定**

---

## 一句话开篇

> **数字员工不是"一个 ChatBot 加上一些 Prompt"，而是企业 Ontology 中一组被显式定义的业务能力集合——它知道自己管辖哪些 Context（认知），能调用哪些 Capability（技能），受哪些 Policy 约束（权限）。**

---

## 二、先纠正一个直觉错误

### 2.1 常见的"数字员工"理解

很多人（包括很多 AI 产品）定义数字员工的方式：

```
数字员工 = LLM + 角色 Prompt + 工具列表 + 知识库
```

这种定义方式的问题：

| 问题 | 后果 |
|------|------|
| 角色靠 Prompt 描述，没有结构化语义 | 换个 Prompt 版本，"员工"就变了，无法治理 |
| 工具列表是扁平的，没有业务语义 | Agent 知道有 20 个 API，但不知道哪些归它管 |
| 知识库是文件堆叠，没有边界 | Agent 可能引用不属于自己业务域的知识 |
| 没有显式 Policy | 任何人可以让 Agent 做任何事 |

### 2.2 Ontology 视角的数字员工定义

你在 LangChat ADR-006 里已经给出了正确答案：

```
DigitalEmployeeDefinition
  = 产品语义聚合（Product Semantic Aggregate）
  = 引用关系_holder（Reference Holder）
  ≠ 巨型聚合根（NOT Monolithic Aggregate Root）
```

翻译成 Ontology 语言：

```
数字员工 = 一组语义引用的命名集合

它引用：
  ├── ApplicationContractVersion  → 这个员工对外提供什么业务 API
  ├── BlueprintVersion            → 这个员工的能力谱系（从源到可执行）
  ├── 发布策略 scope               → 这个员工在哪些环境/通道可部署
  └── 发现元数据                   → 展示名、描述、负责团队

它不持有：
  ✗ 知识内容字节（引用 KnowledgeSnapshot）
  ✗ 策略内容字节（引用 PolicyBundle）
  ✗ 部署状态（归 Deployment）
  ✗ 运行时状态（归 Session/State/Memory）
```

**关键洞察**：数字员工是一个**语义锚点（Semantic Anchor）**——它把散落在多个层、多个制品中的语义"指向"收束为一个命名的、可管理的业务实体。

---

## 三、Ontology 层面的数字员工定义模板

把 ADR-006 的 D-1 决策翻译成 Ontology 模板：

```
DigitalEmployeeDefinition（语义层）

├── Identity（身份）
│   ├── digital_employee_id: 稳定业务标识
│   ├── definition_version: 单调递增
│   └── tenant + workspace: 归属约束
│
├── Cognitive Scope（认知范围 = 哪些 Bounded Context）
│   ├── 管辖的 Context 列表（来自 MI Domain Model 17 个 Context）
│   └── 禁止越界规则（来自 D-014 跨域协作边界）
│
├── Capability Set（能力集 = 能做什么）
│   ├── 引用的 ApplicationContractVersion 声明的 Capability 清单
│   ├── 每个 Capability 映射到 CRE BCM 的能力行
│   └── 每个 Capability 对应的 SkillRelease（可执行制品）
│
├── Policy Bundle（策略集 = 什么条件下允许做）
│   ├── effect_policy: read_only / conditional_write
│   ├── required_scopes: 能力级授权
│   ├── human_review_gate: none / conditional / mandatory
│   └── approval_flow: 审批路径（映射 MI 审批流）
│
├── Knowledge Scope（知识范围 = 需要检索什么知识）
│   ├── 引用的 KnowledgeCollection → KnowledgeSnapshot
│   └── 知识边界与 Cognitive Scope 对齐
│
└── Lifecycle（生命周期）
    └── Draft → Published → Deprecated → Retired
        （注意：无 Activated 状态——激活是 Deployment 的职责）
```

**这份模板就是 Ontology 驱动数字员工的"蓝图"。** 下一节用三个真实角色来填充它。

---

## 四、三个真实数字员工的语义定义

### 4.1 招商运营数字员工

**业务场景**：协助招商团队管理铺位资源、跟踪招商漏斗、处理意向客户。

```
DigitalEmployeeDefinition: 招商运营数字员工

├── Identity
│   ├── digital_employee_id: "de-leasing-ops"
│   └── tenant: "(当前租户)"
│
├── Cognitive Scope（管辖哪些 Bounded Context）
│   ├── ✅ Context 01: 招商管理（品牌库、招商计划、意向洽谈、报价）
│   ├── ✅ Context 03: 租赁管理（铺位可用性、预定/锁定/释放）
│   ├── ⚠️ Context 02: 合同管理（只读——需要看合同条款理解招商条件）
│   ├── ⚠️ Context 06: 商户管理（只读——需要看商户主数据）
│   └── ❌ Context 04: 财务管理（禁止——不属于招商员工的认知范围）
│
├── Capability Set（从 CRE BCM 能力行映射）
│   ├── CRE-SAL-001: 维护品牌库 → 查询品牌信息
│   ├── CRE-SAL-003: 管理招商漏斗 → 查询/更新意向客户状态
│   ├── CRE-LEA-001: 查询铺位可用性 → 查询空置/已租/锁定状态
│   ├── CRE-LEA-002: 铺位锁定/释放 → 锁定铺位（conditional_write）
│   └── CRE-CON-001: 查询合同摘要 → 只读查询合同基本信息
│
├── Policy Bundle
│   ├── 查询类能力: effect_policy=read_only, gate=none
│   ├── 锁定铺位: effect_policy=conditional_write, gate=conditional
│   │   └── 条件: 招商总监审批（映射 MI 审批流）
│   └── 合同条款修改: ❌ 禁止（不在认知范围内）
│
├── Knowledge Scope
│   ├── 招商政策文档、品牌库资料、铺位平面图
│   └── 不包含：财务报表、合同正文（超出认知范围）
│
└── Lifecycle: Draft → Published → Deprecated → Retired
```

### 4.2 财务运营数字员工

**业务场景**：协助财务团队处理账单生成、收款核销、对账查询。

```
DigitalEmployeeDefinition: 财务运营数字员工

├── Identity
│   ├── digital_employee_id: "de-finance-ops"
│   └── tenant: "(当前租户)"
│
├── Cognitive Scope
│   ├── ✅ Context 04: 财务管理（算费、出账、收款、核销、对账）
│   ├── ⚠️ Context 02: 合同管理（只读——消费合同条款做算费）
│   ├── ⚠️ Context 03: 租赁管理（只读——消费资源状态做计费依据）
│   ├── ⚠️ Context 05: 运营管理（只读——消费营业额/抄表数据）
│   └── ❌ Context 01: 招商管理（禁止——不属于财务员工的认知范围）
│
├── Capability Set
│   ├── CRE-FIN-001: 按合同条款生成账单 → 生成应收账单
│   ├── CRE-FIN-002: 收款核销 → 处理收款记录
│   ├── CRE-FIN-003: 对账查询 → 查询账单/收款/余额
│   └── CRE-FIN-004: 保证金管理 → 查询保证金状态
│
├── Policy Bundle
│   ├── 查询类能力: effect_policy=read_only, gate=none
│   ├── 账单生成: effect_policy=conditional_write, gate=conditional
│   │   └── 条件: 财务主管审核（大额账单）
│   ├── 收款核销: effect_policy=conditional_write, gate=mandatory
│   │   └── 条件: 必须人审（涉及资金流）
│   └── 退款操作: effect_policy=conditional_write, gate=mandatory
│       └── 条件: 财务总监 + 总经理双审（MI 审批流映射）
│
├── Knowledge Scope
│   ├── 财务制度、收费标准、会计科目映射
│   └── 不包含：招商策略、铺位平面图（超出认知范围）
│
└── Lifecycle: Draft → Published → Deprecated → Retired
```

### 4.3 商户服务数字员工

**业务场景**：响应商户咨询、处理报修工单、查询商户履约情况。

```
DigitalEmployeeDefinition: 商户服务数字员工

├── Identity
│   ├── digital_employee_id: "de-merchant-service"
│   └── tenant: "(当前租户)"
│
├── Cognitive Scope
│   ├── ✅ Context 06: 商户管理（商户主数据、证照、履约考核）
│   ├── ✅ Context 08: 客服管理（咨询、投诉、报修工单受理）
│   ├── ⚠️ Context 04: 财务管理（只读——查询账单/欠费情况）
│   ├── ⚠️ Context 02: 合同管理（只读——查询合同基本信息回答商户）
│   └── ❌ Context 01: 招商管理（禁止）
│
├── Capability Set
│   ├── CRE-MER-001: 查询商户档案 → 商户基本信息、证照
│   ├── CRE-MER-002: 查询履约情况 → 营业额报送、缴费记录
│   ├── CRE-CS-001: 受理咨询 → 自然语言问答
│   ├── CRE-CS-002: 受理投诉 → 创建投诉工单
│   └── CRE-CS-003: 受理报修 → 创建维修工单（转工程管理域）
│
├── Policy Bundle
│   ├── 查询类能力: effect_policy=read_only, gate=none
│   ├── 创建工单: effect_policy=conditional_write, gate=conditional
│   │   └── 条件: 自动创建（低风险）但通知对应主管
│   └── 修改商户信息: ❌ 禁止（由商户管理域的人类员工操作）
│
├── Knowledge Scope
│   ├── 商户服务指南、常见问题 FAQ、物业管理制度
│   └── 不包含：财务报表正文、招商底价（超出认知范围）
│
└── Lifecycle: Draft → Published → Deprecated → Retired
```

---

## 五、对比三个数字员工的语义差异

| 维度 | 招商运营 | 财务运营 | 商户服务 |
|------|---------|---------|---------|
| **管辖 Context** | 招商 + 租赁 | 财务 | 商户 + 客服 |
| **只读 Context** | 合同、商户 | 合同、租赁、运营 | 财务、合同 |
| **禁止 Context** | 财务 | 招商 | 招商 |
| **写操作能力** | 锁定铺位（conditional） | 出账、核销、退款（mandatory） | 创建工单（conditional） |
| **人审等级** | conditional | mandatory（涉及资金） | conditional |
| **知识范围** | 招商政策、品牌库 | 财务制度、收费标准 | 服务指南、FAQ |

**关键洞察**：三个数字员工共享同一个企业 Ontology，但各自"看到"的世界不同——这就是 **Bounded Context 作为 Agent 认知边界**的实际体现。

---

## 六、为什么 ADR-006 说"DigitalEmployeeDefinition 不是聚合根"？

这是 Ontology 视角下一个非常精妙的设计决策。回顾 ADR-006 §4.1 D-1：

> **DigitalEmployeeDefinition 是引用语义锚点，不是巨型聚合根。**

用 Ontology 视角解释为什么：

### 如果是聚合根（❌ 错误设计）

```
DigitalEmployeeDefinition（巨型聚合根）
  ├── 包含 ApplicationContract 内容
  ├── 包含 Blueprint 内容
  ├── 包含 Knowledge 内容
  ├── 包含 Policy 内容
  └── 包含 Deployment 状态
```

问题：

| 问题 | 后果 |
|------|------|
| 子对象有独立生命周期，强行捆绑 | Knowledge 更新需要发新版本数字员工？ |
| 不可变性冲突 | Blueprint 是不可变的，但 KnowledgeCollection 是可变的 |
| 跨层违规 | Deployment 归 Runtime Layer，不能被 Business Domain 对象持有 |

### 作为语义锚点（✅ 正确设计）

```
DigitalEmployeeDefinition（语义锚点）
  ├── 引用 ApplicationContractVersion digest
  ├── 引用 BlueprintVersion digest
  ├── 声明 scope 集合
  └── 提供发现元数据

各自独立生命周期：
  ApplicationContractVersion → 不可变，版本演进
  BlueprintVersion → 不可变，经评审后冻结
  KnowledgeSnapshot → 可变集合的不可变快照
  PolicyBundle → 独立演进，Runtime Overlay 可单调收紧
  Deployment → Runtime 层独立管理
```

**Ontology 原则**：数字员工是一个**命名实体**，它**指向前而非包含**。这与 Ontology 中 Entity 的设计原则一致——Entity 有唯一身份，通过 Relationship 连接其他 Entity，而不是把所有东西塞进一个对象。

---

## 七、Ontology Compiler 的角色回顾

昨天（D2）讲了 Ontology Compiler。今天看它在数字员工定义中的位置：

```
企业 Ontology（Context + Entity + Relationship + Rule + Capability + Policy）
    ↓
    ↓ Ontology Compiler 输入
    ↓
    ↓ 编译器根据 Ontology 约束：
    ↓   1. 检查 Cognitive Scope 是否只包含已定义的 Context
    ↓   2. 检查 Capability Set 是否在 CRE BCM 中有对应能力行
    ↓   3. 检查 Policy Bundle 是否满足 effect_policy / scope / gate 约束
    ↓   4. 检查 Knowledge Scope 是否在 Cognitive Scope 范围内
    ↓
    ↓ 编译输出
    ↓
ApplicationContractVersion（声明 API + Capability + Policy 需求）
    ↓
BlueprintVersion → ExecutionPlanIR → SkillRelease
    ↓
DigitalEmployeeDefinition（引用上述制品的 digest）
    ↓
Deployment（在 Runtime 执行）
```

**Ontology Compiler 是数字员工的"入职培训系统"**——它确保数字员工的定义在企业 Ontology 的约束范围内，不能自己声明超出认知范围的能力。

---

## 八、连接前四天

```
Day 1: Agent 如何利用 Ontology
  → Ontology 是 Agent 的企业认知地图

Day 2: Ontology Compiler
  → 把认知地图编译成可执行的能力组合

Day 3: Bounded Context 约束 Agent 认知
  → Agent 只在自己的工位上工作

Day 4: Policy 约束 Agent 执行
  → 即使在自己的工位上，也要检查权限

Day 5: Ontology 驱动 Digital Employee ← 今天
  → 把前四天整合为一个命名的、可管理的数字员工定义
```

**五天的全景**：

```
一个数字员工 =
  Ontology（Day 1）提供认知
  + Compiler（Day 2）编译能力
  + Bounded Context（Day 3）限定认知边界
  + Policy（Day 4）约束执行权限
  + DigitalEmployeeDefinition（Day 5）收束为语义锚点
```

---

## 九、架构师视角

**以前**：数字员工 = 一个 Assistant 对象，Prompt + 工具 + 知识库全塞在一起。定义模糊，治理困难。

**现在**：数字员工 = Ontology 中一组语义引用的命名集合。每个引用指向一个独立的、不可变的制品。数字员工本身只是"语义锚点"，轻量但精确。

这个设计带来的实际好处：

```
1. 独立演进：Knowledge 更新不需要重新发布整个数字员工
2. 可治理：每个引用都有 digest，可审计、可回滚
3. 可组合：不同数字员工可以引用同一个 Capability / Knowledge
4. 边界清晰：Cognitive Scope 防止 Agent 越权认知
5. Policy 内嵌：每个数字员工的权限是声明式的，不是代码 if-else
```

---

## 十、练习（5 分钟）

基于今天的三个数字员工定义，回答：

1. **如果你想新增一个"物业管理数字员工"，它的 Cognitive Scope 应该包含哪些 Context？禁止哪些 Context？至少列出 3 个核心 Capability 和对应的 Policy 配置。**

2. **招商运营数字员工的 Cognitive Scope 包含"合同管理（只读）"。这意味着它能看到合同的哪些信息、不能看到哪些信息？如果你来设计这个只读边界，用 Ontology 语言怎么表达？**

3. **ADR-006 说 DigitalEmployeeDefinition 的生命周期是 `Draft → Published → Deprecated → Retired`，没有 `Activated` 状态。为什么？如果数字员工定义是 Published 但没有 Active Deployment，它处于什么状态？这对 Agent 有什么影响？**

> 思考这些问题的目的：**把数字员工从"Prompt + 工具"升级为"Ontology 中显式定义的语义实体"，为明天的三套 ADR 统一做铺垫。**

---

## 本日小结

| Ontology 维度 | 数字员工对应 | 你的系统里 |
|--------------|------------|----------|
| Entity | DigitalEmployeeDefinition | ADR-006 BD-01 |
| Identity | `(tenant, workspace, digital_employee_id, definition_version)` | ADR-006 D-1 |
| Cognitive Scope | 管辖的 Bounded Context 子集 | MI Domain Model 17 Context |
| Capability Set | CRE BCM 能力行 + ApplicationContract | BCM 域文件 + ADR-005 |
| Policy Bundle | effect_policy + scopes + gate + approval_flow | ADR-002 + MI 审批流 |
| Knowledge Scope | KnowledgeCollection → KnowledgeSnapshot | ADR-006 D-3 |
| Lifecycle | Draft → Published → Deprecated → Retired | ADR-006 D-1 |
| Semantic Anchor | 引用而非持有 | "不是聚合根"原则 |

**一句话总结**：

> **数字员工不是"一个 ChatBot"，而是企业 Ontology 中一组被显式定义的语义引用集合。它通过 Cognitive Scope 知道自己管辖哪些 Context，通过 Capability Set 知道自己能做什么，通过 Policy Bundle 知道自己在什么条件下可以做。ADR-006 的核心设计——"语义锚点而非聚合根"——确保了数字员工定义轻量、可演进、可治理。这正是 Ontology 驱动 AI Agent 架构的精髓：Agent 不是独立的智能体，而是企业语义世界中的一个命名视角。**
