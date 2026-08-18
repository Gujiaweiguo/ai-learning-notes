# 🧱 LangChat 心智模型｜第8周-Day3：Blueprint → Compiler → ExecutionPlanIR

> **意图怎么变成可执行的？**
>
> **日期**：2026-07-22（周三）
>
> **今日核心问题：为什么 Blueprint（蓝图制品）不能直接运行？**
>
> Agent Host 带着 ApplicationContract 来敲门了。LangChat 怎么把这个"做什么"的契约，变成一份机器可以确定性执行的运行计划？这就是今天的主角：制品链的核心三环——Blueprint → Compiler → ExecutionPlanIR。

## 📅 学习进度

```text
W1  ████████████████████ ✅ Transformer 与大模型基础
W2  ████████████████████ ✅ Transformer 工程优化
W3  ████████████████████ ✅ 训练、SFT、RLHF、DPO
W4  ████████████████████ ✅ RAG 与知识增强
W5  ████████████████████ ✅ 推理与思维链
W6  ████████████████████ ✅ Agent 与工具使用
W7  ████████████████████ ✅ 数字员工架构深化
W8  ██████░░░░░░░░░░░░░░ 🔥 LangChat 心智模型（Day3/7）
W9  ░░░░░░░░░░░░░░░░░░░░ 🧩 领域对象深挖
W10 ░░░░░░░░░░░░░░░░░░░░ 🛡 Governance 横切约束
W11 ░░░░░░░░░░░░░░░░░░░░ 💻 代码现实与实施路线图
W12 ░░░░░░░░░░░░░░░░░░░░ 👁 Vision Intelligence 全景
W13 ░░░░░░░░░░░░░░░░░░░░ 🚀 视觉智能能力蓝图
```

**进度：第8周 / 第13周｜链路第三天——意图怎么变成可执行的。**

---

# 🔄 往期回顾

## W8 链路前两天

| Day | 主题 | 核心要点 | 与今天的关系 |
|-----|------|----------|--------------|
| Day1 | 用户意图 | Agent Host 直接调用 LangChat，不是 Orchestrator 编排 | Agent Host 的请求需要被翻译成可执行计划 |
| Day2 | ApplicationContract | 传输无关的业务契约，定义"做什么" | Contract 是 Blueprint 的输入约束，不是 Blueprint 本身 |

## 昨天的延续

昨天学到 ApplicationContract 是"做什么"的业务契约。今天进入下一个核心问题：

**有了契约之后，"怎么做"的执行逻辑从哪里来？谁来把设计意图翻译成机器可执行的表示？**

答案就是制品链的核心三环：**Blueprint → Compiler → ExecutionPlanIR**。

## W7 关联

| Day | 关联 |
|-----|------|
| W7-D3 任务编排 | Workflow 是"怎么做"，但 LangChat v2 制品链用 Blueprint + IR 取代了 WorkflowSpec |
| W7-D5 评估体系 | 评估发生在 Release Gate（ReleaseEvaluation），不发生在 Build 阶段 |

---

# 第一部分：为什么 Blueprint（蓝图制品）不能直接运行？

## 🎯 今日核心问题

> **为什么 Blueprint 不能直接运行？**

### 生活类比：建筑设计图 vs 施工计划

想象你在盖一栋楼：

| 角色 | 建筑行业 | LangChat |
|------|----------|----------|
| 设计草图 | 建筑师的手绘概念图 | BlueprintCandidate |
| 审核通过的设计图 | 盖章的施工蓝图 | BlueprintVersion |
| 施工组织计划 | 分阶段施工方案（先地基、再框架、再装修） | ExecutionPlanIR |
| 盖好的楼 | 交付的可入住建筑 | SkillRelease v2 |

**你能拿设计图直接盖楼吗？不能。**设计图说"这里要有一面墙"，但施工计划还需要决定：先浇混凝土还是先砌砖？哪个工序可以并行？哪些材料要提前采购？

同理，Blueprint 是人可读的、声明式的、描述"要做什么"的制品；ExecutionPlanIR 是机器可执行的、过程式的、描述"怎么做"的内部表示。中间的转换过程就是 Compiler（编译器）。

### 三个关键对象的边界

| 对象 | 层级 | 可人工编辑？ | 可直接执行？ | 可直接部署？ |
|------|------|-------------|-------------|-------------|
| BlueprintCandidate | 作者提交的草案 | ✅ 是（Draft 阶段） | ❌ 否 | ❌ 否 |
| BlueprintVersion | 评审通过的快照 | ❌ 否（不可变） | ❌ 否 | ❌ 否 |
| ExecutionPlanIR | Compiler 产物 | ❌ 否（不可变） | ❌ 否（需 SkillRelease 包装） | ❌ 否（需 DeploymentRevision） |

**链上每一环不可跳过、不可逆序**（ADR-005 §9，HC-3）。

### 为什么不能跳过 Compiler？

如果 Blueprint 可以直接运行，意味着：

1. **设计即执行**——每次运行的逻辑取决于谁写了 Blueprint，没有标准化编译过程
2. **没有确定性**——同一份 Blueprint 在不同环境可能跑出不同结果
3. **没有可审计性**——无法在 Build 阶段做 Policy Check、Resolve、Optimize
4. **没有可复现性**——缺少 Compiler 版本+参数+依赖锁的完整输入身份

Compiler 的存在不是多余的翻译层，而是**确定性的保证**：同一完整输入身份永远产出同一 ExecutionPlanIR digest。

---

# 第二部分：ADR-005 如何设计？

## 2.1 D-2：BlueprintCandidate 评审流程（ADR-005 §5）

### 背景：为什么需要评审？

BlueprintCandidate 是作者（人或工具）在 External Authoring Client 中提交的草案。草案质量参差不齐——可能有结构错误、引用不存在的 Contract、声明了不允许的 Policy。如果不做入口检查，这些错误要到 Runtime 才会暴露，排查成本极高。

### 第一段：Admission Validation（机器判定）

Admission Validation 是 Candidate 进入评审流程之前的"安检门"。它由 5 项机器可判定的检查组成：

| 检查项 | 判定规则 | 失败行为 |
|--------|----------|----------|
| 结构完整性 | Candidate canonical bytes 能被解析为合法 schema；缺失必填字段拒绝 | 拒绝；返回结构错误码；不进入 In Review |
| 引用合法性 | Candidate 引用的 ApplicationContractVersion、Capability、Knowledge、Policy 等必须在对应 Registry 中存在且 caller 有引用权 | 拒绝；返回引用错误码；不进入 In Review |
| Policy floor 合规 | Candidate 声明的 Policy floor 不放宽 Charter §6.1 / ADR-002 HC-4 的最低约束 | 拒绝；返回 policy 错误码；不进入 In Review |
| Self-Reference 禁止 | Candidate canonical bytes 不包含自身 digest | 拒绝；返回结构错误码 |
| 内容寻址可计算 | Candidate 在 Admission 阶段必须能产出稳定 digest | 拒绝；返回结构错误码 |

**关键设计决策**：Admission 是机器判定，**不允许人工覆盖**。任何 Admission 失败的 Candidate 不进入评审，不可被强行 Promoted。这一规则确保了入口检查的客观性和可重复性。

### 第二段：Source Review（人工 + 规则组合评审）

通过 Admission 的 Candidate 进入 `In Review` 态，由 Supply Chain governance 评审。评审由三类 Reviewer 组合承担：

| Reviewer 类 | 职责 | 强制性 |
|-------------|------|--------|
| 结构评审（Structural Reviewer） | 复核 Admission 自动检查未覆盖的结构性风险：不可变字段误用、引用版本范围而非精确版本、缺 Source Map 等 | 强制（每个 Candidate 至少 1 个） |
| 合规评审（Compliance Reviewer） | 复核 Policy floor、effect_policy、required_scopes、人审门配置 | 强制（每个 Candidate 至少 1 个） |
| 业务评审（Business Reviewer） | 提供业务上下文建议 | 可选；不构成 Promote 阻塞条件 |

### 评审准则：不评业务正确性

这是一个关键决策。评审只承担三个维度的判定：

| 评审维度 | 是否属于 Source Review |
|----------|----------------------|
| 结构完整性（补 Admission 未覆盖项） | ✅ 是 |
| 引用合法性（补 Admission 未覆盖项） | ✅ 是 |
| Policy floor 合规 | ✅ 是 |
| 谱系完整性 | ✅ 是 |
| 业务正确性（prompt 是否最优、KB 是否完备） | ❌ 否，归 ReleaseEvaluation |
| 性能、效果、回归测试结果 | ❌ 否，归 ReleaseEvaluation / DeploymentEvaluation |

**为什么不让评审评业务正确性？** 因为业务正确性是主观的、依赖场景的、不可机械重复的。如果把业务正确性放入评审，每次评审结果可能不同，评审就不具备可审计性。业务效果由独立的 EvaluationSuite 在 Release Gate 阶段客观评估。

### 拒绝路径

Candidate 不存在"Pend + Resubmit 同一对象"路径：

| 路径 | 触发条件 | Candidate 状态迁移 | 后续 |
|------|----------|-------------------|------|
| Admission 拒绝 | §5.2.1 任一检查失败 | `Draft → Rejected` | 作者修改后必须重新提交新 Candidate |
| Source Review 拒绝 | 任一强制 Reviewer 拒绝 | `In Review → Rejected` | 作者修改后必须重新提交新 Candidate |

任何修改都必须产新 Candidate——旧 Rejected Candidate 保留为历史证据，不可复活。

## 2.2 D-3：Build / BuildRun Compiler 版本治理（ADR-005 §6）

### 背景：为什么需要确定性 Build？

在传统软件开发中，编译器是可复现的：同一份源代码 + 同一编译器版本 = 同一份二进制。但 AI 应用的"编译"涉及更多变量——prompt、知识库、策略、模型版本。如果不严格治理这些变量，就无法保证可复现性。

### Compiler 的 10 个阶段（Artifact Spec §7.2）

BuildRun 一旦启动，按以下固定顺序执行。每个阶段都是确定性的纯函数：

| 阶段 | 输入 | 输出 | 确定性约束 |
|------|------|------|-----------|
| Parse | BlueprintVersion bytes | AST 或等价中间表示 | 同 bytes 同 AST |
| Validate | AST | 校验报告 + 终止/继续 | 校验规则集版本化 |
| Normalize | AST | 规范化 AST | 规范化规则版本化 |
| Resolve | 规范化 AST + Dependency 声明 | 解析后的依赖 digest 列表 | 依赖锁定到精确 digest，不接受 range |
| Policy Check | 解析后 AST + Policy floor | Policy 校验结果 | Policy floor 版本化；只收紧不放宽 |
| Deterministic Planning | 解析后 AST | 调度计划（IR plan） | Planning 算法版本化、无随机性、**无外部 LLM 调用** |
| Lower | 调度计划 | ExecutionPlanIR 中间形式 | Lowering 规则版本化 |
| Optimize | ExecutionPlanIR 中间形式 | 优化后 ExecutionPlanIR | 优化规则版本化、确定性 |
| Package | ExecutionPlanIR + Dependency Lock + Source Map + Behavioral Assets | SkillRelease Candidate manifest + layers | 输出 digest 由前面所有阶段唯一决定 |
| Provenance | 全阶段记录 | Provenance artifact | Provenance 是 detached attestation |

### Compiler 版本号：EPOCH.MAJOR.MINOR

| 递增类型 | 含义 | 升级要求 |
|----------|------|----------|
| EPOCH | 阶段大重构（阶段重排、新阶段引入、IR schema 不兼容变更） | 必须先修订 AS §7.2 与 ADR-005 |
| MAJOR | 单阶段实现内的不兼容变更（如 Normalize 规则改变） | 新 BuildRun 产出新 digest |
| MINOR | bug 修复或可观察行为不变的实现修订 | 新 BuildRun（但产出可能相同） |

**铁律**：同一 `EPOCH.MAJOR.MINOR` 版本号的 Compiler 实现**字节级**确定。任意 BuildRun 引用同版本号 Compiler 必须得到相同产出 digest。不允许"同版本号下偷改实现"。

### Build 输入身份完整性

Build 必须显式声明全部影响产出的输入：

```
BlueprintVersion digest
  + Compiler EPOCH.MAJOR.MINOR
  + 确定性构建参数集
  + 精确依赖锁（每条依赖是精确 <algo>:<hex> digest，不允许 tag/range/latest）
  + PolicyBundle digest
```

**以下字段不进入 hashed bytes，只进入 detached Provenance**：
- `build_run_id`（运行标识）
- 构建时间戳
- 构建机器标识
- Operator 身份
- Registry 分配的 upload UUID

### Build 的铁律（HC-7）

- Build **MUST NOT** 进行 Release 评估 → 归 ReleaseEvaluation
- Build **MUST NOT** 进行 Release 审批 → 归 Supply Chain governance
- Build **MUST NOT** 进行 Production signing → 归 detached signature
- Build **MUST NOT** 进行 ReleaseChannel promotion → 归独立控制面操作
- Build **MUST NOT** 调用 LLM 进行 Planning / Authoring / IR 重写 → 归 External Authoring Client
- Build **MUST NOT** 以 WorkflowSpec 为输入 → HC-2

一句话：**Build 只负责确定性编译，不做价值判断。**

## 2.3 D-4：ExecutionPlanIR 内部性与可读性边界（ADR-005 §7）

### 为什么 IR 不能直接执行？

ExecutionPlanIR 是 Supply Chain Layer 的内部构建产物。如果允许直接执行 IR，就绕过了 SkillRelease 包装层——没有 Dependency Lock、没有 Source Map、没有 Behavioral Assets。这意味着：

- 无法做兼容性检查（没有 RuntimeABI 版本）
- 无法做依赖校验（没有 Dependency Lock）
- 无法做 Source 回溯（没有 Source Map）
- 无法做 Release Gate（没有 SkillRelease Candidate 可评估）

### 可读性边界

ExecutionPlanIR 允许人工查看（read），但禁止任何形式的写入（write）：

| 场景 | 是否允许 | 原因 |
|------|----------|------|
| 通过 Source Map 回溯 IR 节点到 Blueprint 源位置 | ✅ 允许 | 调试与审计需要 |
| 通过 Registry 按 digest 拉 IR bytes 用于离线分析 | ✅ 允许 | 拉取不等于装载执行 |
| 在 Evaluation 中作为评估对象子结构 | ✅ 允许 | 评估不修改 IR |
| 人工编辑 IR bytes（包括"等价改写"） | ❌ 禁止 | 任何 IR 修改 = 新 BuildRun |
| 直接执行 IR（不通过 SkillRelease） | ❌ 禁止 | 绕过了包装层 |
| 直接部署 IR（不通过 DeploymentRevision） | ❌ 禁止 | 绕过了闭包校验 |
| 把 IR 作为 wire 对外暴露 | ❌ 禁止 | IR 不进 SkillRelease wire API |
| 把 IR 作为 ApplicationContract 字段 | ❌ 禁止 | 业务层不引用 IR |

### IR 字段级 schema 归属

IR 字段级 schema（节点类型、边类型、调度约束、IR 版本号策略）归 AS §22 Q-01 与未来 ADR-007。本 ADR 只定义可读性边界。

---

# 第三部分：当前代码如何实现？

## 3.1 BlueprintCandidate（草案阶段）

代码位置：`apps/backend/langchat/blueprint/candidate.py`

```python
@dataclass(frozen=True)
class BlueprintCandidate:
    candidate_id: str
    tenant_id: str
    workspace_id: str
    blueprint_id: str
    application_contract_version_digest: str  # ← 绑定 Contract
    content_digest: str                       # ← 内容寻址
    effect_policy: str                         # ← 策略声明
    lineage_parent_ids: tuple[str, ...]        # ← 谱系追溯
    state: str = "draft"                       # ← 生命周期
```

**生命周期状态转换**：`Draft → In Review → Promoted | Rejected`（终态不可逆）

```python
_VALID_TRANSITIONS = {
    "draft": frozenset({"in_review"}),
    "in_review": frozenset({"promoted", "rejected"}),
    "promoted": frozenset(),  # terminal
    "rejected": frozenset(),  # terminal
}
```

Candidate 的 `digest` 计算基于 canonical JSON（sorted keys, compact separators, UTF-8）。

## 3.2 Admission Validation

代码位置：`apps/backend/langchat/blueprint/admission.py`

```python
def admit(candidate: BlueprintCandidate) -> AdmissionDecision:
    # (1) 结构完整性 — 检查 7 个必填字段非空
    for field_name in _REQUIRED_FIELDS:
        value = getattr(candidate, field_name)
        if not value:
            reasons.append(f"missing or empty required field: {field_name}")

    # (2) 引用合法性 — ContractVersion digest 格式校验
    if not _is_well_formed_digest(candidate.application_contract_version_digest):
        reasons.append("application_contract_version_digest is not well-formed")

    # (3) Policy floor — effect_policy 在 {read_only, conditional_write} 内
    if candidate.effect_policy not in _ALLOWED_EFFECT_POLICIES:
        reasons.append(f"effect_policy={candidate.effect_policy!r} not allowed")
    
    # ⚠️ 不评估业务正确性！(ADR-005 D-2)
    return AdmissionDecision(allowed=not reasons, reasons=tuple(reasons))
```

`AdmissionDecision` 有一个有趣的约束：`allowed=True` 时 MUST NOT 携带 `reasons`。

## 3.3 BlueprintVersion（不可变源制品）

代码位置：`apps/backend/langchat/blueprint/version.py`

```python
@dataclass(frozen=True)
class BlueprintVersion:
    blueprint_id: str
    version: str
    tenant_id: str
    workspace_id: str
    application_contract_version_digest: str
    originating_candidate_id: str   # ← 谱系指针（必须非空！）
    content_digest: str
    state: str = "active"           # ← 创建即 Active，没有 Draft
```

**生命周期**：`Active → Deprecated → Retired`（无 Draft 态）

关键校验：
- `application_contract_version_digest` 必须是格式正确的 digest（`sha256:` 或 `sha512:` 前缀）
- `originating_candidate_id` 必须非空——"没有匿名版本"
- `transition()` 方法严格限制状态转换方向

## 3.4 Build / BuildRun（确定性编译）

代码位置：`apps/backend/langchat/supply_chain/build.py`

### Build（输入身份）

```python
@dataclass(frozen=True)
class Build:
    build_id: str
    blueprint_version_digest: str
    compiler_version: str  # EPOCH.MAJOR.MINOR
    deterministic_params: Mapping[str, object]
    dependency_lock: Mapping[str, str]
    target_compat_key: CompatCellKey
```

`input_digest` 属性计算 SHA-256 over canonical JSON，**排除了 `build_id`**。

`__post_init__` 中：如果 `blueprint_version_digest` 为空，抛出 `InvalidBuildInputError`，错误信息明确提到 WorkflowSpec 不可作为 Build 输入。

### WorkflowSpec 拦截器

```python
def validate_build_input(value: object) -> None:
    value_type = type(value)
    module_name = getattr(value_type, "__module__", "") or ""
    if module_name.startswith("langchat.workflow."):
        raise InvalidBuildInputError(
            code="workflowspec-not-supported",
            message="Build input must be a BlueprintVersion from langchat.blueprint..."
        )
```

这段代码通过检查输入对象的类模块路径来识别 WorkflowSpec——是 ADR-005 HC-2 的代码级实现。

### BuildRun（一次执行）

```python
@dataclass(frozen=True)
class BuildRun:
    build_run_id: str
    build: Build
    state: BuildRunState  # "running" | "succeeded" | "failed"
    started_at: str
    completed_at: str | None = None
    execution_plan_ir: ExecutionPlanIR | None = None
    source_map: SourceMap | None = None
    provenance: ProvenanceManifest | None = None
    error: str | None = None
```

校验逻辑：
- `succeeded` 状态 MUST 填充 IR + SourceMap + Provenance，MUST NOT 携带 error
- `failed` 状态 MUST 填充 error，MUST NOT 填充 outputs

## 3.5 10 阶段流水线

代码位置：`apps/backend/langchat/supply_chain/stages.py` + `pipeline.py`

```python
STAGE_ORDER = (
    "parse", "validate", "normalize", "resolve", "policy_check",
    "plan", "lower", "optimize", "package", "provenance"
)
```

`run_pipeline()` 函数：
1. 检查 `operation_context.operation_kind == "build"`
2. 创建 `StageContext`
3. 按 STAGE_ORDER 依次执行每个阶段函数
4. 每个阶段产出 `StageResult`（含 accumulated output + Provenance entry）
5. 最终从 `ctx.accumulated` 提取 ExecutionPlanIR 和 SourceMap
6. 组装 ProvenanceManifest 并返回 terminal BuildRun

**当前实现状态**（WP-03）：
- Parse/Normalize/Resolve/Plan/Lower/Optimize/Provenance 阶段是 pass-through stub（只标记完成 + 记录 Provenance）
- Validate 阶段执行 Compatibility Matrix 三点检查（有实际逻辑）
- Package 阶段组装 ExecutionPlanIR 和 SourceMap（有实际逻辑）

## 3.6 ExecutionPlanIR

代码位置：`apps/backend/langchat/supply_chain/execution_plan_ir.py`

```python
IR_VENDOR_MEDIA_TYPE = "application/vnd.langchat.execution-plan-ir.v1+json"
IR_SCHEMA_VERSION = "v1"

@dataclass(frozen=True)
class IRNode:
    node_id: str
    node_type: str
    payload_digest: str       # SHA-256 over canonical JSON of node's semantic content
    source_position: str      # e.g. "blueprint.md:L42:C7"

@dataclass(frozen=True)
class ExecutionPlanIR:
    ir_schema_version: str    # 固定 "v1"
    nodes: tuple[IRNode, ...] # 不可变 tuple
```

`digest` 只取决于 `(ir_schema_version, nodes)`。`canonical_json` 属性产出的 JSON 排除了所有 transient 字段。

---

# 第四部分：差距分析

## 详细对照

| 维度 | 当前态（WP-03） | 目标态（ADR-005 + AS） | Gap |
|------|-----------------|----------------------|-----|
| BlueprintCandidate | 数据类已定义，支持基本字段校验 | 支持 External Authoring Client 导入，完整 Admission 规则集 | 🟡 中 |
| Admission Validation | 3 项检查（结构、引用、Policy） | 5 项检查（+ Self-Reference、digest 可计算）+ 自动化工具 | 🟡 中 |
| Source Review | **未实现** | 三类 Reviewer + RBAC 映射 | 🔴 高 |
| BlueprintVersion | 数据类完整，生命周期完整 | 与目标态一致 | 🟢 低 |
| Build 输入身份 | 数据类完整，input_digest 排除 build_id | 与目标态一致 | 🟢 低 |
| WorkflowSpec 拦截 | `validate_build_input` 已实现 | 保持现状 | 🟢 低 |
| 10 阶段流水线 | 框架完整，**大多为 pass-through stub** | 各阶段真实编译逻辑 | 🔴 高 |
| Compiler 版本治理 | 硬编码 1.0.0 | EPOCH.MAJOR.MINOR 注册体系 | 🔴 高 |
| ExecutionPlanIR | 数据类完整，digest 正确 | 字段级 schema 归 ADR-007 | 🟡 中 |
| Source Map | 基础结构已定义 | 完整 IR→Blueprint 位置映射 | 🟡 中 |
| Provenance | ProvenanceManifest 已定义 | SLSA-style 完整证据链 | 🟡 中 |

**最大 Gap**：
1. Source Review 流程未实现——当前只有 Admission Validation，没有人工评审环节
2. 10 阶段真实编译逻辑——当前大多是 pass-through stub
3. Compiler 版本治理——当前硬编码为 1.0.0，无注册体系

---

# 第五部分：今天多理解了什么

**以前以为：** Blueprint 就是一份配置文件，Runtime 直接读取执行。

**现在知道：**

1. Blueprint 是**制品**（artifact），不是配置——它有版本、digest、生命周期
2. Blueprint 和 ExecutionPlanIR 之间隔着 10 阶段确定性 Compiler——不是简单翻译
3. Compiler 的存在不是多余：它保证了**同一输入永远产出同一输出**
4. ExecutionPlanIR 是**内部不可编辑**的——不存在"手动 patch IR"的合法路径
5. Build 阶段**不做价值判断**（不评估 Release、不调 LLM、不签发）——职责严格分离
6. `build_run_id` 被排除在 hashed bytes 之外——两次不同构建（不同 ID）只要输入相同就产出相同 IR digest
7. Candidate 不存在原地修改路径——每次修改都是新对象，保留了完整谱系
8. Source Review 不评业务正确性——只看结构、引用、合规

---

# 第六部分：重新设计时是否仍这样做

**会。而且理由比昨天更充分。**

原因：

1. **确定性 Build 是信任的基础。** 如果 Blueprint 可以直接运行，每次执行结果取决于解释器的偶然行为，无法审计、无法复现。Compiler 的存在确保了同一设计图永远产出同一施工计划。

2. **Compiler 版本治理让工具链可演进。** Compiler 升级不会偷偷改变已发布 Release 的行为。同版本号字节级确定。如果允许"同版本号偷改实现"，就等于在确定性链条上开了一个不可审计的后门。

3. **ExecutionPlanIR 不可编辑是不可谈判的。** 一旦允许"IR hotfix"，整个确定性链条就断了——谁改的？什么时候改的？为什么改的？不可追溯。所有修改必须通过新 BuildRun 走完整路径。

4. **Build 禁区（不调 LLM、不评估 Release）是关注点分离的典范。** 编译就是编译，评估就是评估。混在一起就两边都做不好。如果 Build 调 LLM 来优化 prompt，那么同一份 Blueprint 在不同 LLM 版本下会产出不同 IR——确定性就破了。

5. **Candidate 不存在原地修改路径。** 每次修改都是新对象——保留了完整谱系，不会"丢了原来长什么样"。这一规则与版本控制系统的"commit 不可变"哲学一脉相承。

---

# 第七部分：每日工程日志

| 类型 | 内容 |
|------|------|
| **新增** | 理解了制品链完整链路：Candidate → Admission → Source Review → BlueprintVersion → Build → Compiler 10 阶段 → ExecutionPlanIR → SkillRelease |
| **新增** | 理解了 Compiler 10 个阶段及其确定性约束 |
| **新增** | 理解了 ExecutionPlanIR 的可读性边界：允许查看，禁止任何写入 |
| **修改** | 以前认为 Blueprint 是配置文件；现在知道 Blueprint 是制品 |
| **确认** | `Build.input_digest` 排除 `build_id`——确定性 |
| **确认** | WorkflowSpec 拦截器是 HC-2 的代码级实现 |
| **遗留** | 当前 10 阶段流水线大多为 pass-through stub |
| **遗留** | BlueprintCandidate 不支持从 External Authoring Client 导入 |
| **技术债** | Source Review 流程未实现 |
| **技术债** | Compiler 各阶段版本号硬编码为 1.0.0 |
| **下一步** | 明天学习 Runtime：执行计划怎么跑起来的？ |

---

# 课堂练习

## 练习一：给 MallSenseAI 的“商场客流日报”能力划分制品边界

假设业务方要交付“读取昨日客流、生成日报、推送运营负责人”的能力。请分别写出：

1. 哪些内容属于 `ApplicationContractVersion`（例如输入日期、输出日报、读写副作用与审批要求）。
2. 哪些内容属于 `BlueprintCandidate`，并说明它为何不能直接进入 Runtime。
3. 若发现“推送消息”会产生外部副作用，应该由 Admission、Source Review、Build、ReleaseEvaluation 中的哪一层确认，为什么？

**自检标准：** 契约描述“做什么”和治理约束；Candidate 描述待评审的设计；Build 只做确定性转换，不承诺业务效果；效果与发布风险不能被塞进 Build。

## 练习二：判断一次修改应从哪里重走

请给下列变更选择正确路径，并说明是否能直接修改 IR：

| 变更 | 正确路径 |
|------|----------|
| 将日报字段从“昨日客流”改成“昨日客流和同比” | 新 Candidate → 评审 → 新 BlueprintVersion → 新 BuildRun |
| 修复 Compiler 的 Normalize 规则 | 新 Compiler 版本 → 新 BuildRun → 新 Release Gate |
| 线上发现某个 IR 节点参数错误 | 回到源制品产新 Candidate；禁止直接修改 IR |

---

# 课后测试

1. 判断题：`BlueprintVersion` 可以由 Runtime 直接执行。答案：**错误**；它必须经 Compiler 产出 IR，再由 SkillRelease 与 DeploymentRevision 的受治理链路进入 Runtime。
2. 判断题：同一完整 Build 输入身份产生的 `ExecutionPlanIR` digest 应相同。答案：**正确**；`build_run_id`、时间戳和操作者只记录在 detached Provenance，不参与哈希。
3. 单选题：以下哪个环节负责业务效果与回归验证？
   - A. Admission Validation
   - B. Build
   - C. ReleaseEvaluation
   - D. IR 手工修补

   答案：**C**。Admission 审结构、引用和策略下限；Build 做确定性编译；IR 不允许手工修补。
4. 简答题：为什么 `WorkflowSpec` 不能作为 v2 Build 输入？

   参考答案：ADR-005 §3.2 HC-2 与 §8 的目标态要求它从制品链退役。Build 的 canonical 输入是已经晋升且不可变的 `BlueprintVersion`，否则无法保证唯一来源、版本谱系与确定性。

---

# 术语表

| # | 英文术语 | 音标 | 中文释义 |
|---|----------|------|----------|
| 1 | **Blueprint** | /ˈbluːprɪnt/ | 设计制品——人可读的、声明式的 canonical 源制品 |
| 2 | **BlueprintCandidate** | /ˈbluːprɪnt ˈkændɪdət/ | 蓝图候选——作者提交的草案 |
| 3 | **BlueprintVersion** | /ˈbluːprɪnt ˈvɜːrʒn/ | 蓝图版本——不可变、内容寻址的 canonical 源制品 |
| 4 | **Compiler** | /kəmˈpaɪlər/ | 编译器——把 BlueprintVersion 确定性编译为 ExecutionPlanIR |
| 5 | **ExecutionPlanIR** | /ˌeksɪˈkjuːʃn plæn aɪˈɑːr/ | 执行计划中间表示——Compiler 产出的内部不可编辑表示 |
| 6 | **BuildRun** | /bɪld rʌn/ | 构建运行——Build 的一次具体执行 |
| 7 | **Deterministic Build** | /dɪˌtɜːrmɪˈnɪstɪk bɪld/ | 确定性构建——同一完整输入身份永远产出相同 digest |
| 8 | **Provenance** | /ˈprɒvənəns/ | 溯源证据——记录构建全链路的 detached attestation |
| 9 | **Source Map** | /sɔːrs mæp/ | 源映射——把 IR 节点映射回 BlueprintVersion 源位置 |
| 10 | **Immutable** | /ɪˈmjuːtəbl/ | 不可变——对象创建后内容不可修改 |

---

# 真实参考

| 来源 | 路径/章节 |
|------|-----------|
| ADR-005 D-2 | §5 BlueprintCandidate 评审流程 |
| ADR-005 D-3 | §6 Build/BuildRun Compiler 版本治理 |
| ADR-005 D-4 | §7 ExecutionPlanIR 内部性与可读性边界 |
| ADR-005 §9 | 单一制品链权威边界总图 |
| Artifact Spec §7.2 | Build 阶段定义 |
| Domain Model §7.2 SC-02 | BlueprintCandidate |
| Domain Model §7.3 SC-03 | BlueprintVersion |
| Domain Model §7.4 SC-04/SC-05 | Build/BuildRun |
| Domain Model §7.5 SC-06 | ExecutionPlanIR |
| 代码 | `apps/backend/langchat/blueprint/candidate.py` |
| 代码 | `apps/backend/langchat/blueprint/version.py` |
| 代码 | `apps/backend/langchat/blueprint/admission.py` |
| 代码 | `apps/backend/langchat/supply_chain/build.py` |
| 代码 | `apps/backend/langchat/supply_chain/execution_plan_ir.py` |
| 代码 | `apps/backend/langchat/supply_chain/stages.py` |
| 代码 | `apps/backend/langchat/supply_chain/pipeline.py` |
