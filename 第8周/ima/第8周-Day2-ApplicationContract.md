# 🧱 LangChat 心智模型｜第8周-Day2：ApplicationContract

> **用户要做什么？怎么描述？**
>
> 今天从链路的第二步出发：Agent Host 理解了用户意图之后，用什么"语言"把需求传给 LangChat？这就是 ApplicationContract 要解决的问题。但它不是 API 文档，不是 OpenAPI Spec，也不是函数签名——它是**业务契约**。

## 📅 学习进度

```text
W1  ████████████████████ ✅ Transformer 与大模型基础
W2  ████████████████████ ✅ Transformer 工程优化
W3  ████████████████████ ✅ 训练、SFT、RLHF、DPO
W4  ████████████████████ ✅ RAG 与知识增强
W5  ████████████████████ ✅ 推理与思维链
W6  ████████████████████ ✅ Agent 与工具使用
W7  ████████████████████ ✅ 数字员工架构深化
W8  ████░░░░░░░░░░░░░░░░ 🔥 LangChat 心智模型（Day2/7）
W9  ░░░░░░░░░░░░░░░░░░░░ 🧩 领域对象深挖
W10 ░░░░░░░░░░░░░░░░░░░░ 🛡 Governance 横切约束
W11 ░░░░░░░░░░░░░░░░░░░░ 💻 代码现实与实施路线图
W12 ░░░░░░░░░░░░░░░░░░░░ 👁 Vision Intelligence 全景
W13 ░░░░░░░░░░░░░░░░░░░░ 🚀 视觉智能能力蓝图
```

**进度：第8周 / 第13周｜链路第二天——需求怎么进来。**

---

# 🔄 往期回顾

## W7 知识脉络

| Day | 主题 | 与今天的关联 |
|-----|------|-------------|
| W7-D1 | 数字员工总览 | 数字员工需要一个"岗位说明书"来定义能力边界——Contract 就是这份说明书 |
| W7-D2 | 记忆系统 | 记忆是运行时状态，不是契约。Contract 不包含记忆，但声明"需要什么知识" |
| W7-D3 | 任务编排 | Workflow 是"怎么做"，Contract 是"做什么"。先有契约，再有编排 |
| W7-D4 | 多 Agent 协作 | Agent Host 可以跨系统协作，每个系统都有各自的 Contract |
| W7-D5 | 评估体系 | 评估的前提是有明确的输入输出契约——否则无法判定"成功" |

## 昨天（W8-D1）的延续

昨天建立了链路全景：Agent Host → LangChat → Provider。我们知道了**谁**在调用 LangChat。

今天进入第二个问题：Agent Host 拿着用户意图来敲门时，它说的"我要查运营异常日报"这件事，LangChat 怎么理解？用什么结构承载？

答案就是 **ApplicationContract**。

---

# 📚 Part 1：为什么需要 ApplicationContract？

## 🎯 Today's Question

> **为什么 Contract 不是 API 文档？**

先说一个直觉错误：很多人第一次看到 ApplicationContract，会想"这不就是 OpenAPI / Swagger 吗？定义接口、定义输入输出、定义权限"。

但两者有本质区别：

| 维度 | API 文档（OpenAPI/Swagger） | ApplicationContract |
|------|---------------------------|---------------------|
| **关注点** | 传输端点、HTTP 方法、路径参数 | 业务语义、能力需求、权限边界 |
| **变化频率** | 随实现变动（改路由就改文档） | 随业务变动（不改传输改语义才变） |
| **谁来读** | 开发者（对接 HTTP 调用） | Agent Host（理解业务能力）+ 平台（治理）+ 审计（追溯） |
| **版本含义** | 接口版本（v1/v2/v3） | 业务契约版本（MAJOR.MINOR.PATCH 语义化） |
| **传输绑定** | 绑定 HTTP/REST | **传输无关**——同一份契约可由 HTTP、MCP、gRPC 承载 |
| **不可变性** | 随时可改 | Version 创建后不可修改；破坏性变更必须新版本号 |

一句话总结：**API 文档描述"怎么调"；ApplicationContract 描述"做什么、需要什么、允许什么"。**

## 生活类比：餐厅菜单 vs 后厨流程图

把 LangChat 想象成一家大型餐厅：

- **ApplicationContract** = 菜单：客人（Agent Host）看到的菜品名称、价格、是否含过敏原、是否需要预约。菜单不关心后厨怎么炒。
- **Blueprint / Workflow** = 后厨流程图：先备料、再炒制、再摆盘。这是内部实现。
- **ExecutionPlanIR** = 具体的菜谱步骤：多少克盐、多少度火、多少分钟。
- **SkillRelease** = 实际端给客人的那盘菜：可追溯（有 digest）、有版本（厨师签名）。

菜单（Contract）不关心后厨用燃气灶还是电磁炉（传输方式），它只关心"客人点什么菜、菜有什么约束"。

## 为什么不能用 API 文档替代？

假设直接用 OpenAPI Spec 作为 Agent Host 和 LangChat 之间的唯一合同：

1. **传输耦合**：今天用 HTTP REST，明天要加 MCP 支持，所有 Contract 都要重写。因为 OpenAPI 的 path、method、requestBody 都和 HTTP 强绑定。
2. **缺少治理语义**：OpenAPI 没有 `effect_policy`（只读 vs 写入）、`human_review_gate`（是否需要人审）、`required_scopes`（权限范围）。这些是企业平台必须有的治理字段。
3. **版本演进不安全**：OpenAPI 的版本管理是松散的——改了 path 就算新版本，但没有"兼容性分类"（哪些变更破坏向后兼容，哪些不破坏）。
4. **Agent Host 理解困难**：Agent Host 需要的是"这个能力做什么、输入什么、输出什么、有什么风险"——而不是"GET /api/v1/skills/w09/execute"。

---

# 📚 Part 2：ADR 怎么设计的？

## ADR-005：Blueprint / 制品链与 ApplicationContract 边界

ADR-005 的核心是定义 v2 制品链。ApplicationContract 是这条链的**起点对象**之一。

### D-1 决策：ApplicationContract 与 ApplicationContractVersion 分层模型

ADR-005 §4（D-1）定稿了 Contract 的演进策略。核心设计是**两层分离**：

```
ApplicationContract（contract_id + 生命周期）
  └── ApplicationContractVersion 1.0（不可变，承载具体内容）
  └── ApplicationContractVersion 1.1（不可变，兼容性扩展）
  └── ApplicationContractVersion 2.0（不可变，破坏性变更）
```

**为什么分两层？**

| 层级 | 作用 | 类比 |
|------|------|------|
| ApplicationContract | 稳定业务标识，管理生命周期（Draft→Stable→Deprecated→Retired） | 一本书的 ISBN |
| ApplicationContractVersion | 不可变内容快照，承载具体契约内容 | 书的某一版次（第1版、第2版） |

同一个 Contract 可以有多个 Version 共存。Version 一经发布就不可修改——这是铁律（HC-10）。

### ApplicationContractVersion 的内容

根据 Domain Model §6.2 BD-02 和 §6.3 BD-03，一个 ApplicationContractVersion 承载：

| 内容 | 说明 | 当前代码中的对应 |
|------|------|-----------------|
| **输入输出 Schema** | 业务输入输出的结构化定义 | `SkillReleaseDescriptor.input_schema` / `output_schema` |
| **Capability 语义需求** | 这个能力需要哪些底层能力（如知识库、模型） | ❌ 当前未显式声明 |
| **权限边界（required_scopes）** | 调用此能力需要什么权限范围 | `SkillReleaseDescriptor.required_scopes` |
| **策略边界（effect_policy）** | 只读 / 条件写入 | `SkillReleaseDescriptor.effect_policy` |
| **人审门（human_review_gate）** | 不需要 / 条件性 / 强制 | `SkillReleaseDescriptor.human_review_gate` |

### 传输无关原则

ADR-005 §4.1 明确写道：

> ApplicationContract 不定义传输端点实现（HTTP/MCP/gRPC 适配归 ApplicationContract/Gateway/Connector 边界相关 ADR）。本 ADR 不定义 wire。

这意味着同一份 ApplicationContract 可以被不同传输协议承载：
- 今天 Agent Host 通过 HTTP 调用
- 明天通过 MCP 协议调用
- 后天通过 gRPC 调用

**Contract 不变。只有适配层变。**

### 破坏性变更分类（ADR-005 §4.2）

ADR-005 定义了 13 条可机械判定的变更分类规则：

| 变更类型 | 分类 | 版本递增 |
|----------|------|----------|
| 新增可选输入字段 | 兼容 | MINOR |
| 放宽输出 schema | 兼容 | MINOR |
| 删除输入/输出字段 | **破坏** | MAJOR |
| 收紧输入 schema | **破坏** | MAJOR |
| 修改字段语义 | **破坏** | MAJOR |
| effect_policy 从 read_only 升为 conditional_write | **破坏** | MAJOR |
| required_scopes 新增必需 scope | **破坏** | MAJOR |
| human_review_gate 从 mandatory 降为 none | **破坏** | MAJOR |

这套分类规则确保 Contract 演进是**可预测的**——调用方在升级前就知道是否兼容。

---

# 📚 Part 3：现有代码怎么实现的？

## 当前状态：SkillReleaseDescriptor 承载了部分 Contract 职责

代码位置：`apps/backend/langchat/skill_release/descriptor.py`

```python
class SkillReleaseDescriptor(BaseModel):
    model_config = ConfigDict(frozen=True)  # ← 不可变！

    skill_id: str                        # 能力标识
    version: str = "v1"                  # 版本
    lifecycle: _Lifecycle = "published"  # 生命周期
    required_scopes: list[str]           # 权限范围
    effect_policy: _EffectPolicy          # 只读 / 条件写入
    human_review_gate: _HumanReviewGate   # 人审门
    workflow_binding: dict               # 内部实现绑定
    input_schema: dict                   # 输入 schema
    output_schema: dict                  # 输出 schema
    visibility: _Visibility              # 可见性
```

### 已经做到的（✅）

| Contract 要求 | SkillReleaseDescriptor 中的对应 | 状态 |
|---------------|--------------------------------|------|
| 不可变性 | `frozen=True` Pydantic 配置 | ✅ |
| 权限边界 | `required_scopes` | ✅ |
| 策略边界 | `effect_policy: "read_only" | "conditional_write"` | ✅ |
| 人审门 | `human_review_gate: "none" | "conditional" | "required"` | ✅ |
| 输入输出定义 | `input_schema` / `output_schema` | ✅ |
| 版本 | `version: "v1"` | ✅ 基础版本 |
| 生命周期 | `lifecycle: "draft" | "published" | "deprecated"` | ✅ 基础生命周期 |

### 内置校验逻辑

SkillReleaseDescriptor 有三个 `model_validator` 校验：

1. **`_reject_read_only_in_scopes`**：`required_scopes` 不允许包含 `"read_only"`——因为 `read_only` 是 `effect_policy`，不是 scope（ADR-002 §6.2）
2. **`_conditional_write_requires_review`**：如果 `effect_policy = "conditional_write"`，则 `human_review_gate` 不能是 `"none"`——写操作必须有人审
3. **`_tenant_visibility_requires_owner`**：如果 `visibility = "tenant"`，必须设置 `owner_tenant_id`

这些校验正是 Contract 治理的雏形——不是等运行时才检查，而是在**描述符创建时就拒绝**不合法的组合。

## 真实绑定示例：W09 运营异常检测

代码位置：`apps/backend/langchat/skill_release/bindings/w09.py`

```python
_w09_descriptor = SkillReleaseDescriptor(
    skill_id="langchat.w09.internal.service",
    version="v1",
    lifecycle="published",
    required_scopes=["skill_release:invoke"],
    effect_policy="read_only",
    human_review_gate="conditional",
    workflow_binding={"workflow_id": "mall-internal-service", "schema_version": "v1"},
    display_name="Mall Internal Service",
    description="Mall internal employee service for administrative, "
                "finance, and HR inquiries with risk-sensitive flagging",
    input_schema={
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
    },
    output_schema=_SEVEN_FIELD_OUTPUT_SCHEMA,
)
```

分析这个绑定：

- **effect_policy = read_only**：P0 阶段只允许只读（ADR-002 HC-4）
- **human_review_gate = conditional**：虽然只读，但某些场景需要人审（如涉及敏感数据）
- **workflow_binding**：当前直接绑定 WorkflowSpec——这正是 v2 要解决的问题
- **input_schema / output_schema**：简单但有效的 JSON Schema

---

# 📚 Part 4：Gap Analysis

## 目标态 vs 代码现实

| 维度 | v2 目标态（ADR-005） | 当前代码 | Gap |
|------|---------------------|---------|-----|
| **Contract 对象** | 独立的 `ApplicationContract` + `ApplicationContractVersion` 两层模型 | 合并在 `SkillReleaseDescriptor` 里 | 🔴 缺少分层；需要拆分 |
| **版本语义** | MAJOR.MINOR.PATCH 语义化版本 | 简单 `"v1"` 字符串 | 🔴 缺少语义化版本管理 |
| **破坏性变更分类** | 13 条可机械判定规则 | 无分类工具 | 🔴 缺少自动化工具（V1 待验证） |
| **传输无关** | Contract 不绑定任何传输 | `workflow_binding` 直接绑定内部 Workflow | 🟡 部分实现（Descriptor 本身是传输无关的，但绑定方式耦合了 Workflow） |
| **Capability 语义需求** | 显式声明需要哪些底层能力 | 未声明 | 🔴 缺少 |
| **Contract 生命周期** | Draft → Stable → Deprecated → Retired | draft → published → deprecated | 🟡 缺少 Stable 和 Retired |
| **引用精确版本** | DigitalEmployeeDefinition 引用精确 ApplicationContractVersion | 直接引用 skill_id | 🔴 缺少精确版本引用 |
| **共存期管理** | 同一 Contract 下多 Version 共存 | 单一 version 字段 | 🔴 不支持多版本共存 |
| **不可变性** | Version 创建后不可修改 | `frozen=True` | ✅ Pydantic 层面已实现 |
| **治理校验** | Admission Validation + Source Review | 3 个 model_validator | 🟡 有基础校验，但远不及 ADR-005 规则集 |

## Gap 的本质

当前的 `SkillReleaseDescriptor` 实际上在**同时承担三个角色**：

```
目标态：ApplicationContract（业务语义）
              ↓
        BlueprintVersion（设计制品）
              ↓
        SkillRelease（可部署制品）
        
当前态：SkillReleaseDescriptor（混合体）
         ├── 业务语义（effect_policy, required_scopes）
         ├── 设计描述（input_schema, output_schema）
         └── 实现绑定（workflow_binding）
```

这不是"代码写得不好"，而是 v1 阶段的**合理简化**。在 P0 只需要几个只读能力的阶段，用一个对象同时承载三层语义是最高效的。

但随着能力数量增长、写入能力开放、多版本共存的到来，这种混合会成为演进的瓶颈：

- 修改 input_schema 需要新版本，但不能影响已有 DeploymentRevision 的闭包
- effect_policy 变更需要触发权限重新检查，但不应该修改已发布的 SkillRelease
- workflow_binding 需要被 Blueprint → Build → ExecutionPlanIR 链取代

---

# 📚 Part 5：今天多理解了什么？

## 📘 认知升级

**以前以为：** ApplicationContract 就是接口定义——写清楚输入输出就够了。

**现在知道：** Contract 是**业务治理的一等对象**。它不只是"接口长什么样"，而是：
1. **传输无关**——同一份契约可以由多种协议承载
2. **版本不可变**——每个 Version 创建后不能改，破坏性变更必须新版本
3. **治理语义嵌入**——effect_policy、required_scopes、human_review_gate 是 Contract 的一部分，不是运行时才检查
4. **分层分离**——Contract（稳定标识）+ ContractVersion（不可变内容）两层，让多版本共存成为可能

## 🔮 反问：如果今天重新设计，还会这样分层吗？

会。而且会更早落地。

原因是：**没有 ApplicationContract，就没有安全的版本演进**。

如果 Contract 和 SkillRelease 合在一起（当前状态），每次修改 input_schema 都面临两难：
- 改了 → 已有调用方可能断裂
- 不改 → 新需求无法响应

分层之后，答案是清晰的：**新 Version，老 Version 保持不变，共存期由 Compatibility Matrix 治理。**

但我会调整一个设计决策：**在 P0 阶段就引入 ContractVersion 概念**，即使只有一个版本。因为后期从"没有版本"迁移到"有版本"的改造成本，远大于一开始就加一层 Version 的复杂度。

---

# 🧪 课堂练习（5分钟）

1. 请说出 ApplicationContract 和 OpenAPI Spec 的三个本质区别。
2. ADR-005 §4.2 的破坏性变更分类中，为什么 `human_review_gate` 从 `mandatory` 降为 `none` 是破坏性变更？请从调用方角度解释。
3. 当前 `SkillReleaseDescriptor` 同时承担了哪三个角色？如果只拆出第一个角色，需要创建什么新对象？

## 📝 课后测试（15分钟）

1. ApplicationContract 的"传输无关"是什么意思？请举例说明同一份 Contract 如何被不同传输承载。
2. ApplicationContract 和 ApplicationContractVersion 的关系是什么？为什么要分两层？
3. ADR-005 §4.2 定义了多少条破坏性变更分类规则？请列出至少 4 条属于"破坏性（MAJOR）"的变更。
4. 当前代码中的 `SkillReleaseDescriptor` 有哪些校验逻辑？它们分别防止什么问题？
5. 开放题：如果你是 Agent Host 开发者，你更希望看到一个 API 文档还是一个 ApplicationContract？为什么？

---

# 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| ApplicationContract | /ˌæplɪˈkeɪʃn ˈkɒntrækt/ | 应用契约——声明业务能力、权限边界与策略边界的传输无关合同 |
| ApplicationContractVersion | /ˌæplɪˈkeɪʃn ˈkɒntrækt ˈvɜːrʒn/ | 应用契约版本——不可变的内容快照，承载具体契约内容 |
| Semantic Versioning | /sɪˈmæntɪk ˈvɜːrʒnɪŋ/ | 语义化版本——MAJOR.MINOR.PATCH 编号规则，标识变更的兼容性 |
| Breaking Change | /ˈbreɪkɪŋ tʃeɪndʒ/ | 破坏性变更——不向后兼容的修改，必须递增 MAJOR 版本 |
| Effect Policy | /ɪˈfekt ˈpɒləsi/ | 效果策略——声明能力是只读还是条件写入 |
| Human Review Gate | /ˈhjuːmən rɪˈvjuː ɡeɪt/ | 人审门——声明能力是否需要人工审核 |
| Required Scope | /rɪˈkwaɪərd skoʊp/ | 必需授权范围——调用此能力所需的权限集合 |
| Transmission Agnostic | /trænsˈmɪʃən æɡˈnɒstɪk/ | 传输无关——不绑定特定通信协议 |
| Compatibility Matrix | /kəmˌpætəˈbɪləti ˈmeɪtrɪks/ | 兼容性矩阵——管理多版本共存与弃用窗口 |
| Immutable | /ɪˈmjuːtəbl/ | 不可变——创建后不可修改 |

## 📎 真实参考

- ADR-005 §4（D-1）：ApplicationContract 与 ApplicationContractVersion 演进策略
- ADR-005 §4.2：破坏性变更分类规则（13 条）
- Domain Model §6.2 BD-02 ApplicationContract / §6.3 BD-03 ApplicationContractVersion
- `apps/backend/langchat/skill_release/descriptor.py` — SkillReleaseDescriptor
- `apps/backend/langchat/skill_release/bindings/w09.py` — W09 真实绑定
- `apps/backend/langchat/workflow/schema.py:11-12` — WorkflowSpec v1/v2 schema 字面量
