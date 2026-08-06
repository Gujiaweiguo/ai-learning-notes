# PT-W2 Day 5：Capability 抽取 — BCM 能力行 → LangChat Capability 映射

> 📅 2026-08-07（周五）| Business Semantic Architecture 并行轨道
>
> **本周目标**：从已有材料中抽取 Ontology 六维度语义
>
> **今天维度**：Capability（能力）— 从 CRE BCM 能力行和 capability-traceability-matrix 抽取，映射到 LangChat Capability / SkillRelease 体系

---

## 一、为什么 Capability 是 Ontology 的独立维度？

前四天我们抽取了 Entity、Relationship、Lifecycle/Event、Rule。今天抽取 **Capability**。

```
Entity     → 世界里有什么（名词）
Relationship → 事物怎么连接（连线）
Lifecycle  → 状态怎么变化（时间轴）
Event      → 什么触发了变化（动词）
Rule       → 为什么这样变化（约束条件）
Capability → 可以做什么（动作可能性）  ← 今天
```

**关键区分：Rule vs Capability**

| | Rule（规则） | Capability（能力） |
|---|---|---|
| 回答什么 | "什么条件下必须/不能做" | "什么动作是可以被执行的" |
| 例子 | "退租需完成 inspection" | "创建 Inspection Task" |
| 对 AI Agent 意义 | 约束推理（应不应该） | 行动空间（能做什么） |

> **对 AI Agent 的意义**：Agent 光知道规则不够，还得知道"我有哪些动作可调用"。Capability 就是 Agent 的**行动空间声明**。

---

## 二、你已有的两套 Capability 体系

### 2.1 CRE BCM Capability 行（business-ontology.yaml）

你的 `business-ontology.yaml` 里每个模块下的场景都绑定了 capability 标识符：

```yaml
铺位管理:
  capabilities:
    - L09          # 位置建档
    - L10          # 位置变更
    - L11          # 拆分合并
    - asset-resource-rent-control-ui  # 租控 UI
  scenarios:
    - name: 铺位建档
    - name: 铺位拆分合并
    - name: 铺位状态管理
    - name: 租控管理
```

**这些 capability 标识符的特征：**

| 特征 | 现状 | Ontology 视角评价 |
|------|------|-----------------|
| 粒度 | 模块级（一个 capability 覆盖整个功能域） | ❌ 太粗，Agent 无法直接调用"铺位管理" |
| 语义命名 | 混合命名（`L09` 编码 + `asset-resource-rent-control-ui` 描述） | ❌ 不一致，有时是编码，有时是描述 |
| 动作定义 | 只有名称，无输入/输出/前置条件声明 | ❌ Agent 不知道调用它需要什么参数 |
| 场景绑定 | 场景描述了业务流程但未结构化 | ⚠️ 有业务语义但缺形式化 |

### 2.2 capability-traceability-matrix.md（工程追溯矩阵）

你的 `capability-traceability-matrix.md` 是另一个层面——**工程实现追溯**：

```
Legacy Code → OpenSpec Target → Implementation Anchor → Verification Anchor → Status
```

| Capability Group | OpenSpec Target | Implementation Anchor | Status |
|---|---|---|---|
| Lease contract lifecycle | `lease-contract-management/spec.md` | `backend/internal/lease/` | accepted |
| Charge generation & billing | `billing-and-invoicing/spec.md` | `backend/internal/billing/` | accepted |
| Workflow / approval engine | `workflow-approvals/spec.md` | `backend/internal/workflow/` | accepted |

**这套追溯矩阵的特征：**

| 特征 | 现状 | Ontology 视角评价 |
|------|------|-----------------|
| 追溯链 | Legacy → Spec → Code → Test | ✅ 完整的工程追溯 |
| 状态管理 | excluded / spec-defined / implemented / accepted | ✅ 有生命周期状态 |
| 语义描述 | 用 Capability Group 名称描述（如 "Lease contract lifecycle"） | ⚠️ 有粗粒度语义 |
| Agent 可用性 | 面向工程师，不面向 AI Agent | ❌ Agent 无法直接消费 |

### 2.3 LangChat Capability / SkillRelease（ADR-001 §7）

LangChat ADR-001 定义了三层概念：

```
SkillRelease   → 面向 Agent Host 的对外消费单元（P0 唯一）
                  承载稳定业务语义，绑定底层执行

Capability     → 受治理的可复用执行依赖 / Provider 契约
                  描述原子或组合执行能力

Workflow       → LangChat 内部执行表示（可替换）
                  不对 Agent Host 暴露
```

**关键设计原则（来自 ADR-001 §7）：**

> "对 Agent Host 暴露的稳定契约是 SkillRelease，不是 Workflow。"
>
> "Capability 是 SkillRelease 与底层执行之间的受治理依赖与 Provider 契约。"

---

## 三、三套体系的映射关系

这是今天的核心产出——**BCM Capability → LangChat Capability/SkillRelease 映射表**：

```
CRE BCM Capability Row（业务能力行）
    ↓ 语义化分解
Ontology Capability（语义能力声明）
    ↓ Provider 契约绑定
LangChat Capability（受治理执行依赖）
    ↓ 业务语义封装
LangChat SkillRelease（Agent 可消费单元）
```

### 映射示例：以"铺位管理"为例

| 层级 | 内容 | 来源 |
|------|------|------|
| **BCM Capability Row** | `L09` + `L10` + `L11` + `asset-resource-rent-control-ui` | business-ontology.yaml |
| **Traceability** | OpenSpec: `supporting-domain-management/spec.md` → `backend/internal/structure/` → `accepted` | capability-traceability-matrix.md |
| **Ontology Capability**（抽取后） | `space.create` / `space.split` / `space.merge` / `space.lock` / `space.unlock` / `space.update-status` | 今天抽取 |
| **LangChat Capability** | Provider: MI → `space-management`（Contract） | 映射 |
| **LangChat SkillRelease** | `查询可用铺位` / `铺位状态变更` / `铺位拆合操作` | 映射 |

### 映射示例：以"合同管理"为例

| 层级 | 内容 | 来源 |
|------|------|------|
| **BCM Capability Row** | `lease-contract-management` + `workflow-approvals` + `L24-L26` | business-ontology.yaml |
| **Traceability** | OpenSpec: `lease-contract-management/spec.md` → `backend/internal/lease/` → `accepted` | capability-traceability-matrix.md |
| **Ontology Capability**（抽取后） | `lease.create` / `lease.modify` / `lease.terminate` / `lease.clear` / `lease.renew` | 今天抽取 |
| **LangChat Capability** | Provider: MI → `lease-management`（Contract） | 映射 |
| **LangChat SkillRelease** | `创建租赁合同` / `合同变更申请` / `合同终止与清算` / `查询合同台账` | 映射 |

---

## 四、Capability 抽取的四步法

从你已有的材料中抽取 Ontology Capability，遵循四步：

### Step 1：从 BCM 场景识别原子动作

```
场景：铺位拆分合并
  → 原子动作：space.split（拆分）、space.merge（合并）
  → 不是"铺位管理"这个模块级能力
```

**原则**：一个 Ontology Capability = 一个可独立执行的业务动作。

### Step 2：声明输入/输出/前置条件

每个 Capability 需要声明：

```yaml
capability: space.split
description: 将一个铺位拆分为多个铺位
actor: 招商
input:
  - source_space_id: string  # 被拆分铺位
  - target_spaces: array      # 拆分后的铺位列表
precondition:
  - source_space.status == 'vacant'  # 必须空置才能拆分
  - no_active_lease(source_space_id)  # 无有效合同
effect:
  - create: target_spaces
  - update: source_space.area
  - preserve: source_space.asset_info, source_space.account_info
governed_by: workflow-approvals  # 需审批
```

> **对比你的现状**：BCM 只写了 `capabilities: [L09, L10, L11]`。没有 input/precondition/effect 声明。Agent 看到这些编号，完全不知道怎么调用。

### Step 3：映射到 LangChat Provider 契约

```
Ontology Capability: space.split
    ↓ Provider
LangChat Capability: MI.space-management
    ↓ API binding
MI Backend: POST /api/v1/spaces/{id}/split
    ↓ 封装为 Agent 可消费单元
SkillRelease: 铺位拆合操作
```

### Step 4：追溯验证

用 capability-traceability-matrix 验证：
- OpenSpec target 是否覆盖？→ `supporting-domain-management/spec.md` ✅
- Implementation anchor 是否存在？→ `backend/internal/structure/` ✅
- Verification anchor 是否通过？→ `structure_test.go` ✅
- Status 是否 accepted？→ ✅

---

## 五、全景 Capability 抽取表（核心域）

从 BCM + traceability-matrix 抽取的主要 Ontology Capability：

| 业务域 | BCM Capability | Ontology Capability（抽取） | SkillRelease 候选 |
|--------|---------------|---------------------------|-------------------|
| 资源管理 | `asset-resource-rent-control-ui`, `L09-L11` | `space.create/split/merge/lock/unlock/update-status` | 铺位操作、租控查询 |
| 招商管理 | `brand-merchant-management`, `leasing-plan-management` | `brand.enroll/approve`, `prospect.track`, `quote.create/approve` | 品牌入库、招商报价、意向管理 |
| 合同管理 | `lease-contract-management`, `L24-L33` | `lease.create/modify/terminate/clear/renew/cancel` | 合同签约、合同变更、合同终止清算 |
| 财务管理 | `billing-and-invoicing`, `finance-reconciliation` | `billing.generate/adjust`, `payment.receive/writeoff`, `invoice.issue/cancel` | 出账、收款核销、发票管理 |
| 运营管理 | `move-in-management`, `exit-management`, `opening-management` | `tenant.movein/moveout`, `shop.open`, `inspection.create` | 进退场管理、开业管理 |
| 工作流 | `workflow-approvals` | `approval.submit/approve/reject/withdraw` | 审批提交、审批处理 |
| 报表 | `report-manager`, `generalize-reports` | `report.view/export/schedule` | 报表查询、报表导出 |

---

## 六、关键发现：Gap Analysis 更新

### 发现 1：BCM Capability 粒度太粗，Agent 无法直接消费

```
现状：BCM 写的是模块级能力（lease-contract-management）
问题：Agent 不知道"lease-contract-management"包含哪些可执行动作
需要：分解为原子能力（lease.create / lease.modify / lease.terminate...）
```

### 发现 2：Capability Traceability Matrix 有工程追溯，但缺语义声明

```
现状：Traceability Matrix 从 Legacy → Spec → Code → Test 完整追溯
问题：这是给工程师看的，不是给 Agent 看的
需要：在追溯之上叠加语义层（每个 capability 有 input/precondition/effect 声明）
```

### 发现 3：LangChat SkillRelease 是正确的封装层级，但 BCM 没有对应

```
现状：LangChat ADR-001 定义了 SkillRelease = Agent 可消费单元
问题：BCM 的 capability 行没有映射到 SkillRelease 层级
需要：建立 BCM Capability → Ontology Capability → SkillRelease 的映射链
```

### 发现 4：effect-registry 是 Capability 的 Effect 声明雏形

```
现状：effect-registry.yaml 定义了 Lifecycle Transition Effect
关联：这正是 Capability 的 effect 属性的结构化版本
价值：effect-registry 可以直接被复用为 Capability Effect 声明
```

---

## 七、架构师视角

```
以前：Capability = 功能模块名，写在 BCM 矩阵里给产品经理和工程师看
现在：Capability = Agent 行动空间的结构化声明，是 Ontology → Agent 的执行接口
```

**设计判断变化：**

1. **BCM Capability 行不是终点，而是起点** — 它们标记了"这里有一个能力"，但需要向下分解为原子能力
2. **Capability Traceability Matrix 需要升级** — 从工程追溯矩阵升级为"追溯 + 语义声明"双层
3. **SkillRelease 是 BCM Capability 的 Agent 面孔** — 同一个底层能力，对 Agent 展示为 SkillRelease，对工程师展示为 Implementation Anchor

---

## 八、连接思考

| 主线（Governance） | 并行轨道（Capability 抽取） |
|---|---|
| 治理 = 谁有权做什么 | Capability = 可以做什么 |
| Governance 定义 Policy（约束） | Capability 定义 Action（行动空间） |
| LangChat effect_policy / required_scopes | Ontology Capability precondition / effect |

**交汇点**：LangChat 的 `required_scopes` + `effect_policy`（ADR-003 HC-4/HC-9）本质就是 Ontology 的 Policy + Capability 的组合。你的 Capability 声明可以直接驱动 LangChat 的 scope 校验。

---

## 九、练习（5 分钟）

选择 CRE BCM 中的一个域（如"财务管理"），完成以下练习：

1. 找到该域在 `business-ontology.yaml` 中的 capability 行
2. 找到该域在 `capability-traceability-matrix.md` 中的追溯记录
3. 尝试用四步法抽取 3 个 Ontology Capability（声明 capability name + input + precondition + effect）

**思考题**：如果 Agent 要回答"A101 铺位为什么不能出租？"，它需要调用哪些 Capability？这些 Capability 在你的 BCM 里有吗？在 LangChat 里有对应的 SkillRelease 吗？

---

## 十、本日小结

| 维度 | 已有资产 | 抽取结果 | 缺口 |
|------|---------|---------|------|
| Capability | BCM capability 行 + traceability-matrix | 7 个核心域约 35+ 原子能力 | 缺 input/precondition/effect 声明；BCM 到 SkillRelease 无映射链 |

**今天的产出**为 Week 3 的 Ontology → Agent Architecture 奠定了基础：

```
Ontology Capability（今天抽取）
    ↓ Week 3
LangChat SkillRelease（Agent 可消费）
    ↓ Week 3
Digital Employee（数字员工定义）
```

明天 Day 6：Policy 抽取 + Ontology Compiler 初探 — 把审批流变成 Policy 声明。
