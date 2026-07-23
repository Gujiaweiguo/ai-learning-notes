# 🧱 LangChat 心智模型｜第8周-Day4：Runtime 无状态执行

> **为什么 Runtime 不保存状态？**
> 从用户意图到执行结果，我们已经走过了 ApplicationContract（Day2）、Blueprint→Compiler→ExecutionPlanIR（Day3）。今天走到链路的核心：Runtime。Runtime 是"手术室"不是"病房"——病人带着所有信息进来，做完手术带着结果出去，手术室本身不保存任何病人数据。

---

## 📅 学习进度

```
W1-W7  ████████████████████ ✅ AI基础（已完成）
W8     ████████████░░░░░░░ 🔥 LangChat End-to-End Journey (Day4/7)
  D1   ✅ 用户意图：Agent Host 怎么连进来？
  D2   ✅ ApplicationContract：业务契约不是 API 文档
  D3   ✅ Blueprint → Compiler → ExecutionPlanIR：意图变成可执行的
  D4   🔥 Runtime：执行计划怎么跑起来的？
  D5   ⬜ Capability + Connector：怎么连到业务系统？
  D6   ⬜ ⚡ 画完整链路图
  D7   ⬜ 🔄 Virtual CTO Review
```

**进度: Week8 Day4/7 | 总体 33/126**

---

## 🔄 往期回顾

| Day | 主题 | 核心认知 |
|-----|------|----------|
| D1 | 用户意图 | LangChat 是企业能力平台，Agent Host 直接调用，不经 Orchestrator |
| D2 | ApplicationContract | Contract 是业务治理一等对象，不可变版本，传输无关 |
| D3 | Blueprint→Compiler→IR | Blueprint 是制品，Compiler 确定性翻译，IR 内部不可编辑 |

### 今日与前面的关联

- **D2 的 ApplicationContract** → Contract 的 `effect_policy` / `required_scopes` 今天进入 FrozenExecutionContext，由 Runtime 执行时遵守
- **D3 的 ExecutionPlanIR** → IR 打包进 SkillRelease v2 manifest，Runtime 只装载 SkillRelease，不直接读 IR
- **D1 的 Agent Host 直连** → Agent Host 不直接调 Runtime；请求经过 Gateway/Contract 层，构造 FrozenExecutionContext 后才进入 Runtime

---

## 📚 Part 1：为什么 Runtime 不保存状态？

### 通俗类比

**Runtime = 手术室，不是病房。**

- **病房**（有状态）：病人住进来，医生每天查房，病历堆在床头柜，护士记住谁吃什么药。状态 = 病人信息 + 历史记录。
- **手术室**（无状态）：病人推入时带着所有术前信息（病历、手术方案、过敏记录），手术室本身不保存任何病人数据。手术结束，病人推出去带走所有结果。

如果手术室变成病房——存了上一个病人的信息，下一个病人进来可能拿到错药。这在医疗里是灾难，在 AI Runtime 里同样是灾难。

### 为什么需要无状态？

| 需求 | 有状态 Runtime 的风险 | 无状态 Runtime 的优势 |
|------|----------------------|---------------------|
| **水平扩展** | 请求必须路由到同一个实例（sticky session） | 任意实例处理任意请求，弹性伸缩 |
| **安全性** | 前一个请求的上下文可能泄露到下一个请求 | 每次执行完全隔离，零信息泄漏 |
| **可审计** | 状态在内存中变化，无法复现 | FrozenExecutionContext 是不可变的，可完整审计 |
| **故障恢复** | 实例崩溃丢失所有进行中状态 | 无状态 = 无丢失，直接重试 |
| **确定性** | 隐藏状态让"同输入同输出"无法保证 | 所有信息显式传入，行为完全可预测 |

---

## 📚 Part 2：ADR 如何设计 Runtime？

### 2.1 FrozenExecutionContext（冻结执行上下文）

ADR-007（`ADR-007-RuntimeABI-CompatMatrix-FrozenExecutionContext-wire.md`）§7 冻结了 FrozenExecutionContext 的完整 wire JSON schema。

**核心思想**：所有执行所需的信息，在执行前一次性"冻结"成不可变对象，Runtime 只读取，永不修改。

**Wire JSON 顶层结构**（ADR-007 §7.2）：

```json
{
  "schema_version": "v1",
  "profile": "runtime_application | operation",
  "identity": {
    "tenant": "...",
    "workspace": "...",
    "caller_identity": {...},
    "delegation_chain": [...]
  },
  "policy": {
    "effect_policy_snapshot": {...},
    "call_chain_depth_limit": 8,
    "scope_constraints": [...]
  },
  "contract_route": {
    "application_contract_version": "sha256:...",
    "deployment_id": "...",
    "deployment_revision_id": "..."
  },
  "artifact_digests": {
    "skill_release_digest": "sha256:...",
    "runtime_abi_version": "runtime_abi_v1.0.0"
  },
  "knowledge_capability": {
    "knowledge_snapshot_digests": ["sha256:..."],
    "capability_release_digests": ["sha256:..."]
  },
  "trace_audit": {
    "request_id": "...",
    "trace_id": "..."
  },
  "timing_order": {
    "frozen_at": "2026-07-19T10:30:00Z",
    "execution_sequence": 1
  },
  "execution_boundary": {
    "max_execution_duration": "PT30S",
    "max_total_cost": "..."
  },
  "audit": {
    "frozen_context_id": "...",
    "context_integrity_proof": {...}
  }
}
```

**九大字段组，每一组都有明确职责**：

| 字段组 | 职责 | ADR 来源 |
|--------|------|----------|
| `identity` | 谁？租户、工作空间、调用者身份、委托链 | ADR-002 D1 统一委托 |
| `policy` | 能做什么？效果策略快照、调用深度限制、scope 约束 | Charter §6.1 |
| `contract_route` | 做哪份契约？精确 ApplicationContractVersion digest + Deployment | ADR-005 D-1 |
| `artifact_digests` | 用哪些制品？SkillRelease digest、RuntimeABI 版本 | ADR-007 D-1/D-2 |
| `knowledge_capability` | 需要哪些知识和能力？知识快照、能力 Release digest | Domain Model §7.7/7.9 |
| `trace_audit` | 怎么追踪？request_id、trace_id、session_id | ADR-004 OpenTelemetry |
| `timing_order` | 什么时候？冻结时间、执行序号、生效策略版本 | AS §14.1 |
| `execution_boundary` | 什么时候停？最大执行时长、最大成本 | AS §14.1 |
| `audit` | 怎么审计？frozen_context_id、完整性证明、构建者身份 | AS §14.2 |

### 2.2 三大不可协商原则

ADR-007 §11（Explicit Non-Goals）与 Charter §6 共同冻结了三大原则：

| 原则 | 含义 | 硬约束编号 |
|------|------|-----------|
| **无状态** | Runtime 不保存任何跨请求的状态。所有信息通过 FrozenExecutionContext 传入，结果通过 ExecutionResult 传出 | HC-1 |
| **FEC 不可变** | FrozenExecutionContext 创建后不可修改。任何变更必须生成新 FEC，不通过原地修改完成 | HC-1, AS §14.1 |
| **封闭性（零 Workflow import）** | Runtime 包不 import `langchat.workflow`，执行框架通过参数注入，是可替换的插件 | ADR-005 D-5 |

### 2.3 Profile 区分

FrozenExecutionContext 有两种 profile（ADR-007 §7.6）：

| Profile | 用途 | contract_route 字段 |
|---------|------|---------------------|
| `runtime_application` | Runtime 业务执行 | 必需：deployment_id, deployment_revision_id, traffic_policy_version |
| `operation` | Build、Simulation、ReleaseEvaluation、批处理、定时器、Webhook、人审回写 | 省略：由 operation input digest 替代 |

**关键洞察**：不只是"请求执行"需要 FEC，连 Build（编译）和 Evaluation（评估）都在 FrozenExecutionContext 内运行。这保证了所有平台操作都有统一的审计和策略约束。

### 2.4 execute() 签名：Runtime 的唯一入口

ADR-007 继承 AS §13.1，Runtime 的 canonical 入口是：

```python
execute(deployment_revision, frozen_context, input,
        *, runtime_factory, kb_search_fn, llm_chat_fn, tool_call_fn)
```

**四个 keyword-only 参数是封闭性的体现**：

| 参数 | 作用 | 为什么不能有默认值 |
|------|------|-------------------|
| `runtime_factory` | 创建 Workflow 执行器 | 有默认值 = Runtime 自带 Workflow 依赖 = 违反封闭性 |
| `kb_search_fn` | 知识库搜索 | 有默认值 = Runtime 依赖 KB 实现 = 违反封闭性 |
| `llm_chat_fn` | LLM 对话 | 有默认值 = Runtime 依赖 LLM 提供者 = 违反封闭性 |
| `tool_call_fn` | 工具调用 | 有默认值 = Runtime 依赖工具实现 = 违反封闭性 |

### 2.5 七字段 Fallback 契约

`execute()` **永不抛异常**。所有失败都返回结构化的七字段 fallback 结果：

```python
_SEVEN_FIELD_KEYS = (
    "summary",
    "details",
    "references",
    "assumptions",
    "human_review_required",
    "next_actions",
    "risk_flags",
)
```

这是 ADR-003 v1.2 SkillReleaseResult 的 wire 格式。即使 Runtime 内部出错，调用者也永远收到一个合法的七字段结构——`human_review_required=True`，`summary` 说明失败原因。

**为什么永不抛异常？** 因为调用者可能是远程 Agent Host，异常传播跨网络不可靠。结构化 fallback 让调用者可以统一处理所有结果，无需 try/catch。

---

## 📚 Part 3：当前代码如何实现？

### 3.1 Runtime 包结构

```
apps/backend/langchat/runtime/
├── canonical_entry.py      # execute() 入口，七字段输出
├── frozen_execution_context.py  # FEC 不可变 dataclass
├── loader.py               # RuntimeLoader（WP-05 stub）
├── types.py                # 类型别名（RuntimeFactory, KbSearchFn 等）
├── deployment_revision.py   # DeploymentRevision 闭包
├── deployment.py            # Deployment 聚合
├── skill_loader.py         # Skill 加载
├── skill_bindings.py        # skill_id → 模板绑定映射
└── production.py            # ProductionFrozenExecutionContext
```

### 3.2 canonical_entry.py：execute() 实现

文件路径：`apps/backend/langchat/runtime/canonical_entry.py`

```python
"""Canonical Runtime entry: execute(deployment_revision, frozen_context, input).
...
execute() MUST NEVER raise to the caller. When the skill_id is missing, 
the skill is not in _BINDINGS, or the workflow runtime raises, execute() 
returns a fallback ExecutionResult whose output is a valid 7-field dict
(human_review_required=False).
"""
```

关键行为：
1. 接收 `DeploymentRevision` + `FrozenExecutionContext` + input
2. 从 `frozen_context.policy_snapshot.skill_id` 查找 SkillBinding
3. 通过注入的 `runtime_factory` 实例化 Workflow 模板
4. 执行并解析流式输出为七字段 dict
5. 任何失败 → 返回 fallback，永不抛异常

### 3.3 frozen_execution_context.py：不可变 dataclass

文件路径：`apps/backend/langchat/runtime/frozen_execution_context.py`

```python
@dataclass(frozen=True)
class EvaluationFrozenExecutionContext:
    frozen_context_id: str
    subject_closure_digest: str
    policy_floor_digest: str
    policy_overlay_digest: str
    constructed_by: str
    constructed_at: str
    trace_id: str
    policy_snapshot: Mapping[str, object]
    evaluation_only: bool = True
    schema_version: str = "v1-evaluation"
```

`frozen=True` 使 Python dataclass 不可变——任何属性赋值都会抛 `FrozenInstanceError`。测试 `test_frozen_context_not_mutated.py` 验证了这一点。

### 3.4 loader.py：RuntimeLoader（WP-05 Stub）

文件路径：`apps/backend/langchat/runtime/loader.py`

```python
class RuntimeLoader:
    def load(self, revision: DeploymentRevision) -> DeploymentRevision:
        if not isinstance(revision, DeploymentRevision):
            raise BareDigestRejectedError(...)
        return revision  # WP-05 stub: 直接返回已实例化的对象
```

**Gap**：这是 WP-05 阶段的 stub。真实的 RuntimeLoader 应该执行：
- OCI pull（从 Registry 按 digest 拉取 SkillRelease）
- Layer/Digest 验证
- Compatibility Matrix Load check（AS §15.4 三点校验）
- Sigstore 签名验证

当前是"被投喂"模式——调用者负责实例化 DeploymentRevision。

### 3.5 types.py：封闭性类型别名

文件路径：`apps/backend/langchat/runtime/types.py`

```python
RuntimeFactory = Callable[..., Any]
KbSearchFn = Callable[..., Any]
LlmChatFn = Callable[..., Any]
ToolCallFn = Callable[..., Any]
```

只用 `Callable[..., Any]`，不 import 任何 workflow 包。这是 WP-10a（WorkflowSpec 退役）封闭性的体现。

### 3.6 关键测试验证

| 测试文件 | 验证内容 |
|---------|---------|
| `test_runtime_hermetic_api.py` | AST 扫描 runtime/ 包零 workflow import；execute() 签名有 4 个 keyword-only 参数且无默认值 |
| `test_frozen_context_not_mutated.py` | FEC 不可变：赋值抛 ImmutableObjectError |
| `test_runtime_loader_digest_only.py` | RuntimeLoader 只接受 DeploymentRevision 对象，拒绝裸 digest |
| `test_operation_frozen_execution_context.py` | Build/Operation 必须在 operation FEC profile 内执行 |
| `test_build_rejects_workflow_spec.py` | Build 拒绝 WorkflowSpec 类型输入 |

---

## 📚 Part 4：Gap Analysis

### 目标态 vs 代码现实

| 维度 | 目标态（ADR-007） | 当前代码（WP-05/07） | Gap |
|------|-------------------|---------------------|-----|
| **RuntimeLoader** | OCI pull + layer 验证 + Compat Matrix 三点校验 | Stub：直接返回已实例化的对象 | 🔴 核心能力未实现 |
| **FrozenExecutionContext wire** | 完整 9 组字段（identity/policy/contract_route/artifact_digests/knowledge/trace/timing/boundary/audit） | Evaluation + Production 两个简化 profile | 🟡 字段子集已实现 |
| **Signature 验证** | Sigstore cosign 两点验签（pre-publication + pre-load） | 未实现 | 🔴 安全关键 |
| **Compatibility Matrix** | RuntimeABI semver + 弃用窗口 + 366 天 Deprecated | 基础 CompatCell 注册存在 | 🟡 框架存在，治理未填充 |
| **AIBOM** | CycloneDX 1.6 + langchat 扩展 | 未实现 | 🟡 P1 优先级 |
| **封闭性** | Runtime 零 workflow import | ✅ 已通过 test_runtime_hermetic_api.py | 🟢 已实现 |
| **execute() 永不抛异常** | 所有失败返回七字段 fallback | ✅ canonical_entry.py 实现 | 🟢 已实现 |
| **FEC 不可变** | frozen=True + ImmutableObjectError | ✅ dataclass frozen=True | 🟢 已实现 |

### 最大 Gap

**RuntimeLoader 是最大的 Gap。** 当前 stub 模式下：
1. 无法验证 SkillRelease 的 OCI 完整性
2. 无法执行 Compatibility Matrix 检查
3. 无法验证 Signature
4. 调用者必须自己实例化 DeploymentRevision，等于绕过了整个制品链的安全门

这意味着当前的"无状态"设计是结构正确的，但安全链路没有闭合。

---

## 📚 Part 5：今天多理解了什么？

### 以前以为 → 现在知道

| 以前以为 | 现在知道 |
|---------|---------|
| Runtime 就是"跑代码的引擎" | Runtime 是"手术室"——封闭、无状态、所有信息通过 FEC 传入 |
| 无状态就是"不存数据库" | 无状态是更深层的设计：所有执行信息都显式传入 FrozenExecutionContext，可审计、可复现、可水平扩展 |
| Runtime 直接加载 Blueprint 或 Workflow 执行 | Runtime 只装载 SkillRelease（通过 DeploymentRevision 闭包），不读 Blueprint / Channel / Catalog（HC-4） |
| 异常应该直接抛给调用者 | execute() 永不抛异常，所有失败返回七字段结构化 fallback |
| Runtime 需要知道怎么调用 LLM、搜索知识库 | Runtime 通过 keyword-only 参数注入这些能力，自身不 import 任何具体实现 |

### 🔮 如果重新设计，还会这样做吗？

**三大原则不可协商，必须保留**：
1. **无状态** → 水平扩展的前提，是平台级 AI 系统的根基
2. **FEC 不可变** → 审计和复现的基础，没有它就无法证明"某次执行确实用了某份策略"
3. **封闭性** → 可替换性的前提，Runtime 不绑定具体执行框架

**可能的改进**：
- FrozenExecutionContext 的 wire JSON 九组字段可能过于庞大。如果实际使用中某些字段（如 `execution_boundary.max_total_cost`）总是空，可以考虑拆分为"核心 FEC"和"扩展 FEC"
- 七字段 fallback 的 `human_review_required` 字段语义需要更细化——当前 Boolean 值可能不够表达"需要哪种类型的人审"

---

## 📚 Part 6：课堂练习

### 练习 1：画一张 FrozenExecutionContext 数据流图

画出从 Agent Host 请求到 Runtime execute() 调用，FrozenExecutionContext 的构造和传递路径。

**提示**：
- Agent Host → Gateway/Contract 层：构造 FEC
- FEC 包含哪些信息从哪来？
- Runtime 只读取 FEC，不修改

### 练习 2：对比"有状态 Runtime"和"无状态 Runtime"

假设 Runtime 保存了上一次执行的结果（作为"上下文"），列出可能出现的问题：

1. 租户 A 的执行结果被租户 B 看到 → ?
2. Runtime 实例崩溃 → ?
3. 同一请求在不同实例上结果不同 → ?
4. 安全审计需要复现某次执行 → ?

### 练习 3：阅读真实代码

打开以下文件，理解它们的关系：
- `runtime/canonical_entry.py` → execute() 入口
- `runtime/frozen_execution_context.py` → FEC dataclass
- `runtime/loader.py` → RuntimeLoader stub
- `runtime/types.py` → 类型别名

---

## 📚 Part 7：课后测试

### 选择题

**Q1. LangChat Runtime 为什么不保存状态？（核心问题）**
- A) 为了节省内存
- B) 为了支持水平扩展、安全隔离和确定性执行
- C) 因为当前版本还没实现
- D) 因为有状态会导致 LLM 输出质量下降

> ✅ B。无状态是平台架构级决策，支持水平扩展、零信息泄漏、完整审计。

**Q2. FrozenExecutionContext 的 `profile` 字段有哪些取值？**
- A) `production` 和 `staging`
- B) `runtime_application` 和 `operation`
- C) `online` 和 `offline`
- D) `sync` 和 `async`

> ✅ B。ADR-007 §7.6 定义了两种 profile。

**Q3. execute() 为什么"永不抛异常"？**
- A) 因为代码没有 bug
- B) 因为所有失败都返回七字段结构化 fallback
- C) 因为 Python 的异常机制被禁用了
- D) 因为 Runtime 不处理任何可能失败的操作

> ✅ B。调用者可能是远程 Agent Host，结构化 fallback 比 HTTP 500 更可靠。

**Q4. RuntimeLoader 当前（WP-05）是什么状态？**
- A) 完整实现：OCI pull + layer 验证 + Compat Matrix
- B) Stub：直接返回已实例化的 DeploymentRevision
- C) 未实现：文件不存在
- D) 完整实现但未测试

> ✅ B。`loader.py` 是 WP-05 stub，核心装载能力待 WP-07 填充。

**Q5. Runtime 的封闭性（零 Workflow import）意味着什么？**
- A) Runtime 不能执行任何工作流
- B) Runtime 通过参数注入执行框架，自身不依赖具体实现
- C) Runtime 必须用不同的编程语言
- D) WorkflowSpec 已被完全删除

> ✅ B。封闭性 = 可替换性，Runtime 通过 `runtime_factory` 等参数接收执行框架。

---

## 📖 术语表

| 英文 | 音标 | 中文 |
|------|------|------|
| Runtime | /ˈraɪntaɪm/ | 运行时：执行 ExecutionPlanIR 的环境 |
| FrozenExecutionContext | /ˈfroʊzən ɪkˈsɛkjuːʃən ˈkɒntɛkst/ | 冻结执行上下文：执行前构造的不可变信息包 |
| DeploymentRevision | /dɪˈplɔɪmənt rɪˈvɪʒən/ | 部署修订：完整运行时闭包，digest-pin 所有依赖 |
| RuntimeABI | /ˈraɪntaɪm eɪ biː aɪ/ | 运行时应用二进制接口：Runtime 版本兼容性契约 |
| Compatibility Matrix | /kəmˌpætəˈbɪləti ˈmeɪtrɪks/ | 兼容性矩阵：Runtime × SkillRelease 兼容组合声明 |
| execute() | /ɪkˈsækjuːt/ | 执行入口：Runtime 的唯一 canonical 调用方法 |
| Fallback | /ˈfɔːlbæk/ | 降级回退：失败时返回的安全结构化结果 |
| Hermetic | /hɜːrˈmɛtɪk/ | 封闭的：不依赖外部包的隔离设计 |
| SkillRelease | /skɪl rɪˈliːs/ | 能力发布：唯一可部署 OCI 制品 |
| Signature | /ˈsɪɡnətʃə/ | 签名：制品的密码学完整性证明 |

---

## 📚 Part 8：真实参考

| 文档 | 路径 | 用途 |
|------|------|------|
| ADR-007 | `langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-007-RuntimeABI-CompatMatrix-FrozenExecutionContext-wire.md` | RuntimeABI、Compatibility Matrix、FEC wire schema |
| ADR-005 | `langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-005-Blueprint-artifact-chain-and-ApplicationContract.md` | 制品链、封闭性原则 |
| ADR-001 | `langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-001-LangChat-direct-to-agent-capability-platform.md` | 平台定位 |
| Charter 01 | `langchat-docs/lanlnk/out/prd/langchat/output/review/v2-strategy/01-LangChat-v2-Architecture-Charter.md` | AI Native 原则 |
| Artifact Spec 03 | `langchat-docs/lanlnk/out/prd/langchat/output/review/v2-strategy/03-LangChat-v2-Artifact-and-Execution-Specification.md` | §14 FEC 契约、§15 Compat Matrix |
| canonical_entry.py | `langchat/apps/backend/langchat/runtime/canonical_entry.py` | execute() 实现 |
| frozen_execution_context.py | `langchat/apps/backend/langchat/runtime/frozen_execution_context.py` | FEC dataclass |
| loader.py | `langchat/apps/backend/langchat/runtime/loader.py` | RuntimeLoader stub |
| test_runtime_hermetic_api.py | `langchat/apps/backend/tests/unit_tests/test_runtime_hermetic_api.py` | 封闭性验证 |

---

## 📝 Daily Engineering Log

### 2026-07-23（Week8-Day4：Runtime 无状态执行）

| 类别 | 内容 |
|------|------|
| **新增** | 理解 FrozenExecutionContext 九组字段结构（identity/policy/contract_route/artifact_digests/knowledge/trace/timing/boundary/audit） |
| **确认** | execute() 永不抛异常，所有失败返回七字段 fallback；Runtime 零 workflow import（test_runtime_hermetic_api.py 通过） |
| **修改** | — |
| **确认** | RuntimeLoader 是 WP-05 stub，只接受 DeploymentRevision 对象，拒绝裸 digest |
| **遗留** | RuntimeLoader 真实 OCI pull + layer 验证 + Compat Matrix + Signature 验证尚未实现 |
| **技术债** | FrozenExecutionContext wire JSON 目前只有简化 profile，完整九组字段待 v2 填充 |
| **下一步** | Day5：Capability + Connector → Enterprise System，理解执行时怎么连到业务系统 |
