# PT-W2 Day 6：Policy 抽取 + Ontology Compiler 初探

> 📅 2026-08-08（周六）| Business Semantic Architecture 并行轨道
>
> **本周目标**：从已有材料中抽取 Ontology 六维度语义
>
> **今天维度**：Policy（策略）+ Ontology Compiler 概念初探
>
> **核心问题**：审批流怎么变成 Policy？Ontology 怎么变成编译输入？

---

## 一、为什么 Policy 是独立维度？

前五天我们抽取了 Entity、Relationship、Lifecycle/Event、Rule、Capability。今天抽取最后一个维度：**Policy**。

```
Entity       → 世界里有什么（名词）
Relationship → 事物怎么连接（连线）
Lifecycle    → 状态怎么变化（时间轴）
Event        → 什么触发了变化（动词）
Rule         → 为什么这样变化（业务约束）
Capability   → 可以做什么（动作可能性）
Policy       → 谁被允许做、什么条件下才能做（执行许可） ← 今天
```

### Rule vs Policy：关键区分

| | Rule（规则） | Policy（策略） |
|---|---|---|
| 回答什么 | "什么条件下业务必须/不能这样" | "谁在什么前提下被授权执行什么" |
| 例子 | "退租需完成 inspection" | "减免审批需区域经理 + 财务双重确认" |
| 对 AI Agent | 约束推理（业务逻辑层） | 执行授权（行动许可层） |
| 类比 | 交通规则"红灯停" | 驾照"只有持驾照者才能开车" |

> **对 AI Agent 的意义**：Agent 即使知道 Rule（应该怎么做）和 Capability（能做什么），没有 Policy 授权也不能执行。Policy 是 Agent 执行前的**最后一道门禁**。

---

## 二、你的 MI 审批流里藏着什么 Policy？

### 2.1 合同审批流（02-合同管理.md）

从 CRE BCM 合同域文件中，我们能看到至少 **5 条审批流**：

| 审批流 | 触发场景 | 审批节点 | Policy 语义 |
|--------|---------|---------|------------|
| 新签合同审批 | 新合同申请提交 | 录入→11种条款→审批→生效 | "合同签订需经过条款合规审查" |
| 合同变更审批 | 变更申请（9类变更） | 变更类型决定审批路径和可编辑字段 | "不同变更类型对应不同审批严格度" |
| 终止申请审批 | 终止/解约申请 | 终止申请需审批，终止操作本身不需 | "终止决策需审批，执行终止不需要" |
| 费用减免审批 | 清算时费用减免 | K2 审批流 | "财务减免需独立审批" |
| 合同作废审批 | 已签未进场合同作废 | 区别于解约（已进场经营中） | "作废vs解约走不同路径" |

### 2.2 这些审批流的 Policy 本质

以**合同变更审批**为例（CRE-CON-021）：

```
当前代码里（隐式 Policy）：
  if change_type == "price_change":
      require_approval("区域经理", "财务")
      editable_fields = ["rent_amount", "payment_cycle"]
  elif change_type == "area_change":
      require_approval("区域经理")
      editable_fields = ["leased_area"]
  elif change_type == "brand_change":
      require_approval("招商总监")
      editable_fields = ["brand_name", "brand_category"]
```

```
Ontology Policy 层（显式声明）：

Policy: 合同变更审批策略
  WHEN: BusinessEventType = 合同变更申请
  GUARANTEES:
    - change_type = "price_change"
      → requires: [区域经理, 财务]
      → modifiable: [rent_amount, payment_cycle]
      → effect: 产生费用差异 → 进入待结算周期
    - change_type = "area_change"
      → requires: [区域经理]
      → modifiable: [leased_area]
      → effect: 铺位面积更新（→ 03 租赁域）
    - change_type = "brand_change"
      → requires: [招商总监]
      → modifiable: [brand_name, brand_category]
      → effect: 无费用影响
```

> **关键洞察**：你的 K2/BPM 审批引擎是 **Policy 执行机制**，不是 Policy 声明。当前 Policy 隐藏在审批流程配置和代码 if-else 中。Ontology 要做的是把它**显式声明**出来，让 AI Agent 可以读取"我有没有权限做这件事"。

---

## 三、从审批流抽取 Policy 的六步法

```
Step 1: 识别触发条件 → 哪个 BusinessEventType 触发了审批
Step 2: 识别审批角色 → 哪些 Role 参与审批
Step 3: 识别审批路径 → 串行/并行/条件分支
Step 4: 识别字段约束 → 审批通过后哪些字段可修改
Step 5: 识别副作用 → 审批通过触发什么 Effect
Step 6: 声明为 Policy → 写成 Agent 可读取的格式
```

### 实战：合同终止审批的六步抽取

| Step | 内容 | 出处 |
|------|------|------|
| 1. 触发条件 | `BusinessEventType = 合同终止申请` | 02-合同管理 CRE-CON-024 |
| 2. 审批角色 | 终止申请需审批（角色未显式声明，归 14 企业管理 K2/BPM 底座） | §跨域协调表 |
| 3. 审批路径 | 终止申请→审批→通过→执行终止（终止操作本身无需审批） | "合同终止无需审批、终止申请需审批" |
| 4. 字段约束 | 终止类型（正常到期/提前终止/违约终止）决定后续清算路径 | CRE-CON-024 |
| 5. 副作用 | 解约生效期之后的应收被抹除→04；铺位变空置→03；待进场任务取消→05 | CRE-CON-024 跨域联动 |
| 6. Policy 声明 | 见下方 | — |

```
Policy: 合同终止策略
  WHEN: BusinessEventType = 合同终止申请
  CONDITION:
    - termination_type ∈ {normal_expiry, early_termination, breach_termination}
  REQUIRES_APPROVAL: true（终止申请）
  APPROVAL_PATH: K2/BPM（归 14 企业管理域）
  ON_APPROVED:
    - effect: state-transition-effect → 合同状态 = terminated
    - effect: financial-effect → 解约日后应收抹除（→ 04 财务域）
    - effect: occupancy-effect → 铺位状态 = 空置（→ 03 租赁域）
    - effect: lead-conversion-effect → 招商节点标记（→ 01 招商域）
  PROHIBITED_WHEN:
    - 存在未完成 inspection 的退租流程（Rule 约束）
```

---

## 四、LangChat ApplicationContract 里已有的 Policy 三要素

这一步是关键发现：**LangChat ADR-005 已经在 ApplicationContract 层定义了 Policy 的执行机制**，只是没有从 Ontology 视角解释。

### ADR-005 §4.2 定义的三个 Policy 字段

| ApplicationContract 字段 | Policy 语义 | 对 Agent 意义 |
|--------------------------|------------|--------------|
| `effect_policy` | 副作用策略：`read_only` / `conditional_write` / `write` | Agent 知道调用这个能力会不会改数据 |
| `required_scopes` | 授权范围：调用方必须持有哪些 scope | Agent 知道自己有没有权限调用 |
| `human_review_gate` | 人审门：`none` / `conditional` / `mandatory` | Agent 知道是否需要等待人类确认 |

### 三要素的破坏性变更规则

ADR-005 §4.2 还定义了这些字段的**变更策略**，本质就是 Policy 版本治理：

| 变更 | 分类 | 理由 |
|------|------|------|
| effect_policy: read_only → conditional_write | **破坏（MAJOR）** | Agent 原来以为安全的调用变得有副作用 |
| effect_policy: conditional_write → read_only | 兼容（MINOR） | 收紧，更安全 |
| required_scopes 新增 | **破坏（MAJOR）** | 原来 Agent 的权限不再够用 |
| human_review_gate: mandatory → none | **破坏（MAJOR）** | 原来需要人审，现在不需要了，信任模型变了 |

> **架构师视角的洞察**：你的 LangChat ApplicationContract 已经是一个 **Policy 执行载体**。每个 ApplicationContractVersion 就是一份"能力使用策略契约"。缺的不是 Policy 机制，而是把 MI 业务审批流**翻译**到这一层。

---

## 五、Ontology Compiler 初探：你的 BCM ADR-001 就是雏形

### 5.1 什么是 Ontology Compiler？

```
Ontology（业务语义模型）
    ↓ 编译输入
Ontology Compiler（语义→能力的编译器）
    ↓ 生成
Capability + Policy + Skill + Design Artifact
    ↓ 编排
Agent / Digital Employee 执行
```

**Ontology Compiler 不是软件编译器**，不产出二进制。它是一个**语义转换过程**：

```
输入：业务语义（Entity / Relationship / Lifecycle / Rule / Capability / Policy）
输出：Agent 可消费的执行指令（Skill 候选 / 触发条件 / 交付物 / 约束）
```

### 5.2 你的 BCM ADR-001 就在描述这个过程

CRE BCM ADR-001 定义的 **Business Composition Compiler 三原则**，本质上就是 Ontology Compiler 的宪法：

| ADR-001 原则 | Ontology Compiler 语义 |
|---|---|
| **D-1：业务事实与运行时分离** | Ontology 描述业务世界，Compiler 输出 Design Artifact，不直接产出运行时对象 |
| **D-2：对象优先** | Compiler 以 BusinessObjectType + LifecycleVersion 为锚点编译，状态不散落 |
| **D-3：绑定优先** | Compiler 通过 Typed Binding 连接能力与 Skill，不用无类型关系 |

### 5.3 编译器的产物：Design Artifact（ADR-005）

ADR-005 §7.1 定义了 Compiler 的最小输出格式——**Minimum Design Artifact 八字段**：

| 字段 | 语义 | Ontology 来源 |
|------|------|--------------|
| `goal` | 这个 Skill 要完成什么业务目标 | Capability 的业务描述 |
| `capability_refs` | 引用哪些业务能力 | Capability（BCM 能力行） |
| `trigger_event_refs` | 被哪些业务事件触发 | BusinessEventType + 事件来源标注 |
| `input_artifact_refs` | 输入需要什么 | Entity + Relationship |
| `output_artifact_type_refs` | 产出什么交付物 | BusinessDeliverableType |
| `skill_candidate_refs` | 候选 Skill 是什么 | SkillCandidate（矩阵 A 列推导） |
| `governance` | 受什么治理约束 | Policy（effect_policy / required_scopes / human_review_gate） |
| `review_status` | 评审状态 | Compiler 评审流程（ADR-005 §5.2） |

> **关键发现**：这八个字段恰好覆盖了 Ontology 六维度！Design Artifact 就是 Ontology 的**编译投影**。

### 5.4 编译链路全景图

```
                    ┌─────────────────────────────────┐
                    │     Business Ontology           │
                    │  (Entity / Identity / Relation  │
                    │   / Lifecycle / Event / Rule    │
                    │   / Capability / Policy)        │
                    └───────────┬─────────────────────┘
                                │
                    ┌───────────▼─────────────────────┐
                    │   Ontology Compiler             │
                    │   (BCM ADR-001 三原则)           │
                    │   Parse → Validate → Normalize   │
                    │   → Resolve → Policy Check       │
                    │   → Plan → Lower → Package       │
                    └───────────┬─────────────────────┘
                                │
                    ┌───────────▼─────────────────────┐
                    │   Design Artifact               │
                    │   (ADR-005 八字段)               │
                    │   goal / capability_refs /       │
                    │   trigger_event_refs /           │
                    │   input/output / skill /         │
                    │   governance / review_status     │
                    └───────────┬─────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                  ▼
    ┌─────────────┐   ┌─────────────┐    ┌─────────────┐
    │ Application │   │ SkillRelease│    │ Digital     │
    │ Contract    │   │ (v2)        │    │ Employee    │
    │ (Policy)    │   │ (Capability)│    │ Definition  │
    └─────────────┘   └─────────────┘    └─────────────┘
```

---

## 六、连接思考：Policy × Governance × Compiler

### 主线 W10 Governance 与今天 Policy 抽取的关系

主线第10周学了 LangChat 的 Permission / Audit / Trace / Approval / Fail-closed 等治理机制。今天的 Policy 抽取是它们的**业务语义源头**：

```
主线 W10 学的（执行层）         并行轨道今天学的（语义层）

Permission（谁能调用）    ←    Policy: required_scopes
Approval（人审门）        ←    Policy: human_review_gate
Fail-closed（拒绝策略）   ←    Policy: effect_policy
Audit（审计追溯）         ←    Policy 执行记录

主线学"怎么执行"               并行轨道学"怎么声明"
```

### 架构师视角

```
以前：审批流是 K2/BPM 引擎里的配置，和 AI 无关
现在：审批流是 Ontology Policy 层的声明，Compiler 把它编译成
      ApplicationContract 的 human_review_gate + required_scopes，
      Agent 执行时自动遵守

变化：
  - Policy 从"代码里"变成"Ontology 里"
  - 审批从"人操作 ERP 时触发"变成"Agent 调用能力时强制检查"
  - 授权从"角色-菜单"变成"scope-capability-version"三元组
```

---

## 七、今日架构师视角

**以前**：审批流 = K2/BPM 配置 + 代码 if-else，Policy 隐式

**现在**：审批流 = Ontology Policy 层的显式声明 → Compiler 编译为 ApplicationContract 的 governance 字段 → Agent 执行时强制遵守

**为什么重要**：当数字员工需要执行合同变更时，它不需要"理解"审批流程代码。它只需要：
1. 查 ApplicationContract 的 `required_scopes`（我有没有权限？）
2. 查 `effect_policy`（这个操作会改数据吗？）
3. 查 `human_review_gate`（需不需要等人审？）
4. 执行或等待

Policy 从隐式变为显式，从人读变为 Agent 读。

---

## 八、练习（5分钟）

从你的 MI 系统中选择一个审批流（合同变更审批、费用减免审批或终止审批），尝试用六步法抽取：

1. 触发条件是什么 BusinessEventType？
2. 哪些角色参与审批？
3. 审批路径长什么样？
4. 审批通过后可修改哪些字段？
5. 审批通过触发哪些 Effect（对应 effect-registry 的哪类 effect）？
6. 如果让 AI Agent 执行这个操作，它需要知道什么 Policy？

> **明天**：⚡ 汇总六天抽取结果，组装 **MI CRE Ontology Graph v0.1**——六维度全景图。
