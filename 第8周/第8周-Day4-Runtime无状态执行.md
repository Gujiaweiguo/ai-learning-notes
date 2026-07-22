# 🧱 LangChat 心智模型｜第8周-Day4：Runtime 无状态执行

> **链路第四步：执行计划怎么跑起来的？**
>
> **日期**：2026-07-23（周四）
>
> **今日核心问题：为什么 Runtime 不保存状态？**

---

## 目录

1. [往期回顾与业务关联](#1-往期回顾与业务关联)
2. [为什么需要无状态 Runtime？](#2-为什么需要无状态-runtime)
3. [ADR/架构如何设计](#3-adr架构如何设计)
4. [当前代码如何实现](#4-当前代码如何实现)
5. [差距分析](#5-差距分析gap-analysis)
6. [今天多理解了什么](#6-今天多理解了什么)
7. [重新设计时是否仍这样做](#7-重新设计时是否仍这样做)
8. [每日工程日志](#8-每日工程日志)
9. [术语表](#9-术语表)
10. [课堂练习与课后测试](#10-课堂练习与课后测试)
11. [真实参考](#11-真实参考)

---

## 1. 往期回顾与业务关联

### W8 链路前三天

| Day | 主题 | 核心要点 | 与今天的关系 |
|-----|------|----------|--------------|
| Day1 | 用户意图 | Agent Host 直接调用 LangChat，不是 Orchestrator 编排 | Agent Host 的请求最终要到达 Runtime 执行 |
| Day2 | ApplicationContract | 传输无关的业务契约，定义"做什么" | Contract 版本作为 DeploymentRevision 闭包字段 |
| Day3 | Blueprint → Compiler → ExecutionPlanIR | 确定性编译，同一输入永远同一产出 | Compiler 产出的 IR 必须被 Runtime 装载执行 |

### 昨天的延续

昨天学到 ExecutionPlanIR 是 Compiler 的产物——内部不可编辑的中间表示。今天进入下一个核心问题：

**IR 被包装成 SkillRelease，部署为 DeploymentRevision 后，谁来执行它？执行时需要知道什么？执行完要不要记住什么？**

答案就是 Runtime Layer。而 Runtime 最反直觉的设计决策是：**它不保存任何状态**。

---

## 2. 为什么需要无状态 Runtime？

### 生活类比：手术室 vs 病房

想象一家医院：

| 角色 | 医院类比 | LangChat |
|------|----------|----------|
| 病房 | 患者长期住院、记录病史 | 数据库 / Knowledge Base / Channel 子系统 |
| 手术室 | 只做手术——所有患者信息从病历带进来，术后结果写回病历 | Runtime Layer |
| 病历 | 患者身份、病史、用药记录——手术室不保管病历 | FrozenExecutionContext |
| 手术器械包 | 无菌封装、版本号、一次性使用 | SkillRelease / DeploymentRevision |

**手术室不保管病历，不保管患者私人物品，不保管药品库存。** 手术室只做一件事：根据病历（FrozenExecutionContext）和手术方案（DeploymentRevision），完成手术（execute），然后把结果写回病历。

如果你让手术室保管病历，会发生什么？
- 手术室之间病历不一致（多实例不统一）
- 换手术室就要搬运病历（迁移困难）
- 手术室出事故，病历可能丢失（单点故障）
- 无法对手术室做独立扩缩容（状态绑死）

同理，如果 Runtime 保存状态：
- 多实例 Runtime 状态不一致
- 扩缩容需要状态迁移
- Runtime 崩溃丢失运行时状态
- 无法做无状态负载均衡

### Runtime 的"三不原则"

从 ADR-007 §11 和代码 `runtime/__init__.py` 文档注释中提取：

| 原则 | 含义 | 来源 |
|------|------|------|
| **不读 mutable name** | Runtime MUST NOT 在请求路径读 Blueprint / Channel / Catalog / latest / mutable name | AS §13.4、§18.2-17（HC-4） |
| **不存状态** | 所有执行所需信息从 FrozenExecutionContext 获取；执行结果通过 ExecutionResult 返回 | Charter 01 §6；AS §13 |
| **不做价值判断** | Runtime 不评估 Release、不调 LLM 做 Planning、不做 Policy 放宽 | HC-2；AS §18.3-14 |

### 为什么 Runtime 不能有状态？三个场景

**场景 1：水平扩容**

黑色星期五，流量暴增 10 倍。你需要瞬间启动 20 个 Runtime 实例。
- 如果 Runtime 有状态：每个新实例需要同步状态（会话、缓存、用户上下文），同步完成前不能接客。
- 如果 Runtime 无状态：新实例启动即就绪，负载均衡器立即分发请求。

**场景 2：灰度发布**

你想把 10% 流量切到新版 SkillRelease。
- 如果 Runtime 有状态：哪个实例跑新版、哪个跑旧版？状态怎么隔离？
- 如果 Runtime 无状态：TrafficPolicy 根据 cohort hash 决定路由，每个请求独立选择 DeploymentRevision，Runtime 实例不关心自己是"新版"还是"旧版"。

**场景 3：故障恢复**

Runtime 实例崩溃。正在执行的请求怎么办？
- 如果 Runtime 有状态：崩溃丢失运行时状态，恢复需要重放——但"重放"意味着什么？LLM 调用是有副作用的。
- 如果 Runtime 无状态：崩溃即丢弃当前请求；客户端重试，请求被路由到另一个实例，从头执行。FrozenExecutionContext 包含所有必需信息。

---

## 3. ADR/架构如何设计

### 3.1 Single Canonical Execution Path（Charter 01 §6.2）

> 所有执行必须经过唯一入口：`execute(deployment_revision, frozen_context, input)`

这意味着：
- 不存在"快速路径"绕过 `execute()`
- 不存在"内部模式"和"外部模式"
- ADR-007 D-7 的 v1 wire 适配层也只是把 v1 请求**转发**到这个 canonical 入口

代码中的实现（`runtime/canonical_entry.py`）：

```python
def execute(
    deployment_revision: DeploymentRevision,
    frozen_context: EvaluationFrozenExecutionContext | ProductionFrozenExecutionContext,
    input_payload: Mapping[str, object],
    *,
    runtime_factory: RuntimeFactory,
    kb_search_fn: KbSearchFn,
    llm_chat_fn: LlmChatFn,
    tool_call_fn: ToolCallFn,
    pre_loaded_spec: Any = None,
) -> ExecutionResult:
```

**关键设计：`execute()` 接收的是 DeploymentRevision 对象，不是 digest 字符串。** 如果你传一个 bare digest（如 `"sha256:abc123"`），它会抛出 `BareDigestRejectedError`：

```python
if not isinstance(deployment_revision, DeploymentRevision):
    raise BareDigestRejectedError(
        f"[bare_digest_rejected] execute() accepts only "
        f"DeploymentRevision objects, not bare digests or other types."
    )
```

为什么？因为 bare digest 意味着 Runtime 需要自己去 Registry 拉取并解析——这引入了不可控的 I/O 和缓存行为，破坏了无状态承诺。Materialization（实例化）是调用者的责任。

### 3.2 FrozenExecutionContext：一次冻结，不可修改（HC-1）

FrozenExecutionContext（冻结执行上下文）是 Runtime 执行的**唯一输入身份**。它包含：

| 字段类别 | 包含什么 | 为什么需要 |
|----------|----------|-----------|
| **identity** | tenant、workspace、caller_identity、delegation_chain | 知道"谁"在执行 |
| **policy** | effect_policy_snapshot、call_chain_depth_limit、scope_constraints | 知道"允许做什么" |
| **contract_route** | application_contract_version、deployment_id、traffic_policy_version | 知道"执行的是哪个版本" |
| **artifact_digests** | skill_release_digest、runtime_abi_version | 知道"运行的是哪个制品" |
| **trace_audit** | request_id、trace_id、session_id | 可审计 |
| **execution_boundary** | max_execution_duration、max_total_cost、provider_call_boundary | 安全边界 |

**铁律 HC-1：Frozen 后不可修改。** 任何运行时变更必须生成新的 FrozenExecutionContext，不能原地修改。

这就像手术室的"病历封印"——一旦病历被确认带入手术室，在手术过程中任何人不得修改病历内容。如果需要改（比如发现了新病情），必须停下来，重新确认新病历，开始新一轮手术。

### 3.3 Runtime 的封闭性约束（HC-4 + WP-10a）

`runtime/__init__.py` 的模块文档字符串明确写道：

> This package MUST NOT import `release_channel`, `catalog`, or `workflow` (AS §13.4, §18.3-17, ADR-005 §8 D-5).

这不是建议，是**编译级约束**。Runtime 包是一个"密封盒子"——它的所有外部依赖通过 `execute()` 的参数注入：

| 参数 | 注入者 | 用途 |
|------|--------|------|
| `runtime_factory` | 调度层（strangler/seam.py） | 创建 workflow runtime 实例 |
| `kb_search_fn` | 调度层 | 知识库搜索回调 |
| `llm_chat_fn` | 调度层 | LLM 对话回调 |
| `tool_call_fn` | 调度层 | 工具调用回调 |

**Runtime 自己不 import workflow 模块**。这意味着 Runtime 包可以独立测试、独立部署、独立替换——它不关心你用的是 LangGraph、自研引擎还是别的什么执行框架。

### 3.4 Runtime 不放宽 Policy（HC-2）

> Runtime MUST NOT 放宽 FrozenExecutionContext 中的 Policy。

Policy Floor（策略底线）在 Build 阶段锁定。Runtime Overlays（运行时覆盖层）只允许**收紧**，不允许放宽。

如果 FrozenExecutionContext 声明 `effect_policy = read_only`，Runtime 不能在执行中悄悄改成 `conditional_write`。这保证了安全边界在编译时确定，不在运行时漂移。

### 3.5 Compatibility Matrix 三点校验（HC-12）

Runtime Loader 在装载 SkillRelease 时执行三点校验：

| 检查点 | 时机 | 检查什么 |
|--------|------|----------|
| Build | 编译阶段 | Compiler 版本与 IR schema 兼容 |
| Deploy | 部署阶段 | DeploymentRevision 闭包与目标 Runtime ABI 兼容 |
| Load | 装载阶段 | SkillRelease manifest 与当前 Runtime 实例兼容 |

三点全部为 `Supported` 或 `Deprecated` 才能继续。任何一个为 `Unsupported` 则拒绝执行。

当前代码中的 `RuntimeLoader`（`runtime/loader.py`）是 WP-05 的 stub，接受已实例化的 Revision 直接返回。完整的 OCI pull + layer 验证 + Compat Matrix 检查留到 WP-07。

---

## 4. 当前代码如何实现

### 4.1 Runtime 包结构

代码位置：`apps/backend/langchat/runtime/`

```
runtime/
├── __init__.py              # 包入口 + 公开 API + 封闭性声明
├── canonical_entry.py       # execute() 唯一入口
├── deployment.py            # Deployment 聚合
├── deployment_revision.py   # DeploymentRevision（16字段闭包 + SHA-256 digest）
├── errors.py                # 错误类型层级
├── evaluation_only_guard.py # evaluation_only 守卫
├── frozen_execution_context.py  # Evaluation FEC
├── production.py            # Production FEC + 生产实例化
├── loader.py                # RuntimeLoader（WP-05 stub）
├── materialize.py           # 实例化器：digest → DeploymentRevision
├── skill_bindings.py        # skill_id → workflow 模板映射（过渡层）
├── traffic_policy.py        # TrafficPolicy + 确定性 cohort hash
└── types.py                 # 类型别名（RuntimeFactory / KbSearchFn 等）
```

### 4.2 DeploymentRevision：16 字段闭包

代码位置：`runtime/deployment_revision.py`

```python
CLOSURE_FIELDS = (
    "skill_release_digest",
    "application_contract_version",
    "runtime_abi_version",
    "runtime_profile",
    "manifest_schema_version",
    "execution_plan_ir_schema_version",
    "frozen_context_schema_version",
    "required_artifact_media_types",
    "knowledge_snapshot_digests",
    "capability_release_digests",
    "policy_bundle_digest",
    "prompt_artifacts",
    "model_artifacts",
    "runtime_artifacts",
    "environment",
    "binding_manifest_digest",
)
```

DeploymentRevision 是 `frozen=True` 的 dataclass——创建后不可修改。它的 `deployment_revision_digest` 属性计算 16 个闭包字段 canonical JSON 的 SHA-256。

**注意：`source_channel` 和 `evaluation_only` 不参与 digest 计算**（AS §11.3、ADR-008 D-2）。原因：
- `source_channel` 是溯源信息，不影响执行行为
- `evaluation_only` 是部署策略，不是执行身份

### 4.3 FrozenExecutionContext：两种 Profile

LangChat 定义了两种 FEC profile，对应两种执行场景：

| Profile | 类 | 场景 | evaluation_only |
|---------|---|------|-----------------|
| **Evaluation** | `EvaluationFrozenExecutionContext` | BuildRun / Simulation / ReleaseEvaluation | `True` |
| **Production** | `ProductionFrozenExecutionContext` | 生产业务执行 | `False` |

Evaluation FEC（`runtime/frozen_execution_context.py`）：

```python
@dataclass(frozen=True)
class EvaluationFrozenExecutionContext:
    frozen_context_id: str
    subject_closure_digest: str        # ← DeploymentRevision 的 digest
    policy_floor_digest: str
    policy_overlay_digest: str
    constructed_by: str
    constructed_at: str
    trace_id: str
    policy_snapshot: Mapping[str, object]
    evaluation_only: bool = True       # ← 强制为 True

    def __post_init__(self) -> None:
        if not self.evaluation_only:
            raise ValueError(
                "EvaluationFrozenExecutionContext.evaluation_only MUST be True."
            )
```

`__post_init__` 中的检查是防御性编程——如果有人尝试创建 `evaluation_only=False` 的 Evaluation FEC，直接报错。

Production FEC（`runtime/production.py`）：

```python
@dataclass(frozen=True)
class ProductionFrozenExecutionContext:
    # 同样的字段结构
    operation_profile: str = "production"
    evaluation_only: bool = False      # ← 生产模式
```

### 4.4 execute()：唯一执行入口

代码位置：`runtime/canonical_entry.py`

执行流程：

```
execute(deployment_revision, frozen_context, input, *, runtime_factory, ...)
  │
  ├─ 1. 类型检查：必须是 DeploymentRevision 对象（不是 bare digest）
  │
  ├─ 2. 锚定校验：frozen_context.subject_closure_digest == revision.digest
  │
  ├─ 3. 查找 SkillBinding：policy_snapshot.skill_id → 绑定元数据
  │    └─ 找不到 → 返回 fallback ExecutionResult（不抛异常！）
  │
  ├─ 4. 运行 workflow：
  │    ├─ 实例化 workflow template（或使用 pre_loaded_spec）
  │    ├─ 构造 context（user_message、tenant_id、workspace_id）
  │    ├─ 调用 runtime_factory(spec, kb_search_fn, llm_chat_fn, tool_call_fn)
  │    └─ 流式收集输出 → parse_seven_field_output
  │
  └─ 5. 返回 ExecutionResult（execution_id, trace_id, output, latency_ms）
```

**关键设计：`execute()` 永远不向调用者抛异常**。当 workflow 执行失败时（LLM 不可用、KB 缺失、解析错误），它返回一个 fallback `ExecutionResult`，其 `output` 是合法的七字段结构。

为什么？因为调用者（Gateway / strangler seam）不应该需要处理 Runtime 的内部异常。Runtime 自己处理失败，返回可消费的结构化结果。

### 4.5 Fallback 输出的七字段结构

每个 ExecutionResult.output 都包含七个字段（对应 CapabilityOutput schema）：

```python
_SEVEN_FIELD_KEYS = (
    "summary",                  # 摘要
    "details",                  # 详情
    "references",               # 引用来源
    "assumptions",              # 假设
    "human_review_required",    # 是否需要人工审核
    "next_actions",             # 后续动作
    "risk_flags",               # 风险标记
)
```

Fallback 逻辑中有一个**敏感关键词检查**：如果用户消息包含敏感词（如"投诉"、"赔偿"、"退款"），fallback 输出会标记 `human_review_required=True`——**绝不静默丢弃敏感查询**。

### 4.6 SkillBinding：过渡层桥接

代码位置：`runtime/skill_bindings.py`

当前 Runtime 通过 SkillBinding 过渡层桥接 v2 制品链世界和 v1 workflow-template 世界：

```python
_BINDINGS = {
    "langchat.w01.ops.anomaly": SkillBinding(
        skill_id="langchat.w01.ops.anomaly",
        kb_default="ops-faq",
        kb_setting_attr="SKILL_RELEASE_W01_KB_NAME",
        sensitive_keywords=(),
        skill_label="ops anomaly",
    ),
    # ... w02-w09 类似
}
```

模块文档字符串明确标注：

> This module is a **transitional layer**. It bridges the v2 DeploymentRevision world (content-addressed artifacts) to the v1 workflow-template world. When WP-07 full Runtime lands, this module is replaced by deterministic Build-pipeline-compiled artifacts loaded from OCI storage.

这意味着当前的 9 个 SkillBinding 最终会被 OCI Registry 中的 SkillRelease manifest 替代。

### 4.7 TrafficPolicy：确定性灰度路由

代码位置：`runtime/traffic_policy.py`

```python
def compute_cohort(tenant_id, workspace_id, digital_employee_id) -> int:
    """SHA-256 → 前8位hex → mod 100"""
    payload = f"{tenant_id}:{workspace_id}:{digital_employee_id}"
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % 100
```

TrafficPolicy 拒绝 `latest`、`stable`、`main`、`production`、`staging` 等 mutable name：

```python
_FORBIDDEN_REFERENCE_VALUES = frozenset(
    {"latest", "stable", "main", "production", "staging"}
)
```

这保证了灰度路由的确定性——同一个租户+工作区+数字员工组合永远落在同一个 cohort bucket，不受部署顺序、缓存状态、实例位置影响。

### 4.8 Runtime 包的封闭性验证

`runtime/__init__.py` 模块文档字符串中的封闭性声明：

> This package is hermetic — zero `langchat.workflow` imports at any scope.

并通过 WP-10a 工作计划强制执行：
- `runtime/` 目录下任何 `.py` 文件不得 `import langchat.workflow`
- workflow executor 通过 `execute()` 的 `runtime_factory` 参数注入
- 违反封闭性的代码会在 review 阶段被拒绝

### 4.9 Evaluation-Only Guard

代码位置：`runtime/evaluation_only_guard.py`

```python
def assert_not_evaluation_only(revision: DeploymentRevision, *, context: str) -> None:
    if revision.evaluation_only:
        raise EvaluationOnlyReferenceError(
            f"[evaluation_only_reference_forbidden] {context}: Revision "
            f"{revision.revision_id!r} is evaluation-only and cannot be used "
            f"in a production context."
        )
```

这防止了评估环境的 Revision 被误用于生产——一道安全阀。

---

## 5. 差距分析（Gap Analysis）

| 维度 | 当前态（WP-05/WP-07 部分） | 目标态（ADR-007 + AS） | Gap 评级 |
|------|---------------------------|----------------------|----------|
| `execute()` canonical 入口 | ✅ 已实现，接受 DeploymentRevision 对象 | 与目标态一致 | 🟢 低 |
| FrozenExecutionContext | Evaluation + Production 两种 profile | wire JSON v1 完整字段（D-4），含 context_integrity_proof | 🟡 中 |
| DeploymentRevision 16 字段闭包 | ✅ 完整，digest 计算正确 | 与目标态一致 | 🟢 低 |
| Runtime 无状态 | ✅ 无内部状态，所有依赖通过参数注入 | 与目标态一致 | 🟢 低 |
| Runtime 封闭性 | ✅ 零 workflow import（WP-10a） | 与目标态一致 | 🟢 低 |
| RuntimeLoader | Stub（接受 Revision 直接返回） | OCI pull + layer 验证 + Compat Matrix Load check | 🔴 高 |
| Compatibility Matrix 三点校验 | 未实现 | Build / Deploy / Load 三点全部检查（HC-12） | 🔴 高 |
| SkillBinding 过渡层 | 9 个硬编码绑定，桥接 v1 template | OCI manifest 驱动，无硬编码 | 🔴 高 |
| TrafficPolicy | ✅ 确定性 cohort hash + mutable name 拒绝 | 与目标态一致 | 🟢 低 |
| Evaluation-only guard | ✅ 已实现 | 与目标态一致 | 🟢 低 |
| Signature 验签（pre-load） | 未实现 | Sigstore cosign 两点验签（D-5） | 🔴 高 |
| AIBOM | 未实现 | CycloneDX 1.6 + langchat 扩展（D-6） | 🔴 高 |
| v1 wire 适配层 | 未实现 | D-7 薄适配层转发到 canonical execute() | 🟡 中 |

**最大 Gap**：RuntimeLoader 是 stub，没有真实的 OCI pull 和 Compatibility Matrix 检查。这意味着当前 Runtime 是"被投喂"模式——调用者负责实例化 Revision，Runtime 只接收并执行。未来需要 Runtime 自己具备从 Registry 拉取、验签、校验的能力。

---

## 6. 今天多理解了什么

**以前以为：** Runtime 就是"跑代码的引擎"——加载代码、执行、返回结果，中间维护一些会话状态、用户上下文。

**现在知道：**

1. **Runtime 是"手术室"不是"病房"**——所有信息从 FrozenExecutionContext 带进来，所有结果通过 ExecutionResult 带出去，不保存任何状态
2. **`execute()` 接收 DeploymentRevision 对象，不是 bare digest**——这阻止了 Runtime 自己去 Registry 拉取的不确定行为，把"实例化"和"执行"的关注点分离
3. **FrozenExecutionContext 是"封印的病历"**——一旦冻结不可修改（HC-1），任何变更必须生成新 FEC。Runtime 只能收紧 Policy 不能放宽（HC-2）
4. **Runtime 包是"密封盒子"**——零 workflow import，所有外部依赖通过参数注入。这使得 Runtime 可以独立测试、独立替换执行框架
5. **`execute()` 永不抛异常**——所有失败都返回 fallback ExecutionResult，调用者只需处理结构化结果。敏感查询不会被静默丢弃
6. **SkillBinding 是过渡层，最终会被 OCI manifest 替代**——当前的 9 个硬编码绑定是 v1→v2 的桥梁，不是终态

---

## 7. 重新设计时是否仍这样做

**会。每一个设计决策都会保留。**

原因：

1. **无状态是水平扩展的前提。** 如果 Runtime 有状态，扩容时需要状态迁移，10 倍流量时这就是瓶颈。无状态 Runtime 可以像 Nginx 一样瞬间扩容。

2. **FrozenExecutionContext 不可变性是审计的基础。** 如果 FEC 可以修改，就无法回答"执行时用的哪个版本的 Policy？"这个问题。不可变性让每一次执行可追溯、可复现。

3. **封闭性（零 workflow import）是可替换性的前提。** 如果 Runtime 直接 import workflow 模块，换执行框架就要改 Runtime 代码。通过参数注入，执行框架成为可替换的插件。

4. **execute() 不抛异常是 API 契约的典范。** 调用者不需要 try/except Runtime 内部失败——它总是返回结构化结果。这降低了集成成本，特别是对于 Agent Host 等外部调用方。

5. **DeploymentRevision 接收对象而非 digest 是边界清晰的体现。** "谁负责实例化"和"谁负责执行"是两件事。把实例化推给调用者，Runtime 保持纯粹。

6. **Sensitive keyword fallback 不是 hack，是安全设计。** 当 AI 无法回答时，对于敏感话题必须转人工——这不是"AI 失败了"，而是"安全网起作用了"。

---

## 8. 每日工程日志

| 类型 | 内容 |
|------|------|
| **新增** | 理解了 Runtime Layer 的完整结构：`execute()` canonical 入口、DeploymentRevision 16 字段闭包、FrozenExecutionContext 两种 profile、SkillBinding 过渡层 |
| **新增** | 理解了 Runtime "三不原则"：不读 mutable name（HC-4）、不存状态、不做价值判断（HC-2） |
| **新增** | 理解了 `execute()` 的 fallback 机制：永不抛异常，敏感关键词检测转人工审核 |
| **新增** | 理解了 TrafficPolicy 的确定性 cohort hash：SHA-256 → mod 100，同一身份永远落在同一 bucket |
| **新增** | 理解了 Runtime 包封闭性（WP-10a）：零 workflow import，通过参数注入执行框架 |
| **修改** | 以前认为 Runtime 就是"跑代码的引擎"；现在知道 Runtime 是"手术室"——无状态、封闭、所有信息通过 FEC 带入 |
| **确认** | DeploymentRevision 的 `source_channel` 和 `evaluation_only` 不参与 digest 计算——它们是溯源/策略信息，不是执行身份 |
| **确认** | Evaluation FEC 强制 `evaluation_only=True`，通过 `__post_init__` 防御性检查 |
| **遗留** | RuntimeLoader 是 WP-05 stub，无真实 OCI pull / layer 验证 / Compat Matrix Load check |
| **遗留** | SkillBinding 是过渡层，9 个硬编码绑定未来由 OCI manifest 替代 |
| **技术债** | Compatibility Matrix 三点校验未实现（HC-12） |
| **技术债** | Signature pre-load 验签未实现（D-5） |
| **技术债** | v1 wire 适配层（D-7）未实现 |
| **下一步** | 明天学习 Capability + Connector → Enterprise System：执行时怎么连到业务系统？为什么 Capability 不是 Plugin？ |

---

## 9. 术语表

| # | 英文术语 | 音标 | 中文释义 |
|---|----------|------|----------|
| 1 | **Runtime** | /ˈraɪntʌɪm/ | 运行时——执行 DeploymentRevision 的无状态层，所有依赖通过参数注入 |
| 2 | **DeploymentRevision** | /dɪˈplɔɪmənt rɪˈvɪʒn/ | 部署修订——16 字段闭包的不可变对象，Runtime 执行的输入身份 |
| 3 | **FrozenExecutionContext** | /ˈfroʊzən ɪksˈkjuːʃn ˈkɒntekst/ | 冻结执行上下文——执行前一次性构建的不可变身份/策略/审计包 |
| 4 | **RuntimeABI** | /ˈraɪntʌɪm ˌeɪ biː ˈaɪ/ | 运行时应用二进制接口——Runtime 与 SkillRelease 之间的版本兼容契约 |
| 5 | **Compatibility Matrix** | /kəmˌpætəˈbɪləti ˈmeɪtrɪks/ | 兼容性矩阵——显式声明哪些版本组合支持/弃用/不支持 |
| 6 | **TrafficPolicy** | /ˈtræfɪk ˈpɒləsi/ | 流量策略——基于确定性 cohort hash 的灰度路由规则 |
| 7 | **Cohort** | /ˈkoʊhɔːrt/ | 队列——由 SHA-256 hash 确定的 0-99 百分位桶，用于灰度发布 |
| 8 | **SkillBinding** | /skɪl ˈbaɪndɪŋ/ | 技能绑定——skill_id 到 workflow template 的映射（过渡层） |
| 9 | **Canonical Entry** | /kəˈnɒnɪkl ˈentri/ | 规范入口——所有执行必须经过的唯一函数 `execute()` |
| 10 | **Bare Digest** | /ber ˈdaɪdʒest/ | 裸摘要——只有 `"sha256:..."` 字符串没有对应的对象实例；`execute()` 拒绝裸摘要 |
| 11 | **Hermetic** | /hɜːrˈmetɪk/ | 密封的——Runtime 包不 import 外部业务模块，所有依赖通过参数注入 |
| 12 | **ExecutionResult** | /ˌeksɪˈkjuːʃn rɪˈzʌlt/ | 执行结果——包含 execution_id、trace_id、七字段 output、latency_ms 的不可变结构 |

---

## 10. 课堂练习与课后测试

### 课堂练习

**练习1：判断对错**

1. Runtime 可以在执行过程中修改 FrozenExecutionContext 的 Policy。 → ___
2. `execute()` 接受 `"sha256:abc123"` 字符串作为第一个参数。 → ___
3. Runtime 包可以 `import langchat.workflow.runtime` 来调用 workflow 执行器。 → ___
4. TrafficPolicy 允许 `revision_id="latest"` 作为引用值。 → ___
5. 当 workflow 执行抛出异常时，`execute()` 会把异常传播给调用者。 → ___

**练习2： FEC 锚定校验**

`execute()` 中的这行检查保证了什么？

```python
if frozen_context.subject_closure_digest != deployment_revision.deployment_revision_digest:
    raise ValueError(...)
```

A) 确保 FEC 和 Revision 是同一时间创建的
B) 确保 FEC 是为这个特定 Revision 构建的，不是复用其他 Revision 的 FEC
C) 确保 Revision 的 digest 算法是 SHA-256
D) 确保 FEC 的 schema version 正确

### 课后测试

**Q1:** 为什么 Runtime 不能保存会话状态？
- A) 因为技术限制，数据库不支持
- B) 因为保存状态会破坏水平扩展能力，且状态一致性在多实例间难以保证
- C) 因为用户不需要会话连续性
- D) 因为 FrozenExecutionContext 已经包含了所有信息

**Q2:** Runtime 包的"封闭性"（hermetic）意味着什么？
- A) Runtime 运行在沙箱容器中
- B) Runtime 包不 import workflow / channel / catalog 模块，所有外部依赖通过参数注入
- C) Runtime 包不对外暴露任何 API
- D) Runtime 包只能用 Rust 编写

**Q3:** 当 `execute()` 找不到 skill_id 对应的 SkillBinding 时，会发生什么？
- A) 抛出 `SkillNotBoundError` 异常
- B) 返回 HTTP 404
- C) 返回 fallback ExecutionResult，output 包含 reason="skill_not_bound"
- D) 创建一个新的 SkillBinding 并继续执行

---

## 11. 真实参考

| 来源 | 路径/章节 |
|------|-----------|
| Charter 01 §6 | AI Native Principles（FrozenExecutionContext / Single Canonical Execution Path） |
| Charter 01 §6.2 | Single Canonical Execution Path |
| Charter 01 §8 | Runtime Compatibility Matrix |
| Artifact Spec 03 §13 | Runtime Layer 行为规范 |
| Artifact Spec 03 §13.4 | HC-4：Runtime 不读 mutable name |
| Artifact Spec 03 §14 | FrozenExecutionContext 契约 |
| Artifact Spec 03 §15 | RuntimeABI 与 Compatibility Matrix |
| Artifact Spec 03 §18.2 | 22 项 MUST conformance floor |
| Artifact Spec 03 §18.3 | 17 项 MUST NOT conformance 红线 |
| ADR-007 §3.2 | HC-1 ~ HC-16 继承约束 |
| ADR-007 §7 | D-4：FrozenExecutionContext wire 表示 |
| ADR-007 §10 | D-7：canonical 端点 wire 演进 |
| ADR-007 §11 | 明确不做（14 项 Non-Goals） |
| 代码 | `apps/backend/langchat/runtime/__init__.py` |
| 代码 | `apps/backend/langchat/runtime/canonical_entry.py` |
| 代码 | `apps/backend/langchat/runtime/deployment_revision.py` |
| 代码 | `apps/backend/langchat/runtime/frozen_execution_context.py` |
| 代码 | `apps/backend/langchat/runtime/production.py` |
| 代码 | `apps/backend/langchat/runtime/loader.py` |
| 代码 | `apps/backend/langchat/runtime/materialize.py` |
| 代码 | `apps/backend/langchat/runtime/skill_bindings.py` |
| 代码 | `apps/backend/langchat/runtime/traffic_policy.py` |
| 代码 | `apps/backend/langchat/runtime/evaluation_only_guard.py` |
| 代码 | `apps/backend/langchat/runtime/types.py` |
| 代码 | `apps/backend/langchat/runtime/errors.py` |
