# 🧱 LangChat 心智模型｜第8周-Day3：Blueprint → Compiler → ExecutionPlanIR

> **链路第三步：意图怎么变成可执行的？**
>
> **日期**：2026-07-22（周三）
>
> **今日核心问题：为什么 Blueprint（蓝图制品）不能直接运行？**

---

## 目录

1. [往期回顾与业务关联](#1-往期回顾与业务关联)
2. [为什么需要 Compiler（编译器）？](#2-为什么需要-compiler编译器)
3. [ADR/架构如何设计](#3-adr架构如何设计)
4. [当前代码如何实现](#4-当前代码如何实现)
5. [差距分析](#5-差距分析)
6. [今天多理解了什么](#6-今天多理解了什么)
7. [重新设计时是否仍这样做](#7-重新设计时是否仍这样做)
8. [每日工程日志](#8-每日工程日志)
9. [术语表](#9-术语表)
10. [课堂练习与课后测试](#10-课堂练习与课后测试)
11. [真实参考](#11-真实参考)

---

## 1. 往期回顾与业务关联

### W8 链路前两天

| Day | 主题 | 核心要点 | 与今天的关系 |
|-----|------|----------|--------------|
| Day1 | 用户意图 | Agent Host 直接调用 LangChat，不是 Orchestrator 编排 | Agent Host 的请求需要被翻译成可执行计划 |
| Day2 | ApplicationContract | 传输无关的业务契约，定义"做什么" | Contract 是 Blueprint 的输入约束，不是 Blueprint 本身 |

### 昨天的延续

昨天学到 ApplicationContract 是"做什么"的业务契约。今天进入下一个核心问题：

**有了契约之后，"怎么做"的执行逻辑从哪里来？谁来把设计意图翻译成机器可执行的表示？**

答案就是制品链的核心三环：**Blueprint → Compiler → ExecutionPlanIR**。

---

## 2. 为什么需要 Compiler（编译器）？

### 生活类比：建筑设计图 vs 施工计划

想象你在盖一栋楼：

| 角色 | 建筑行业 | LangChat |
|------|----------|----------|
| 设计草图 | 建筑师的手绘概念图 | BlueprintCandidate |
| 审核通过的设计图 | 盖章的施工蓝图 | BlueprintVersion |
| 施工组织计划 | 分阶段施工方案 | ExecutionPlanIR |
| 盖好的楼 | 交付的可入住建筑 | SkillRelease v2 |

**你能拿设计图直接盖楼吗？不能。** 设计图说"这里要有一面墙"，但施工计划还需要决定：先浇混凝土还是先砌砖？哪个工序可以并行？哪些材料要提前采购？

同理，Blueprint 是人可读的、声明式的、描述"要做什么"的制品；ExecutionPlanIR 是机器可执行的、过程式的、描述"怎么做"的内部表示。中间的转换过程就是 Compiler。

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

## 3. ADR/架构如何设计

### 3.1 D-2：BlueprintCandidate 评审流程（ADR-005 §5）

Candidate → BlueprintVersion 的两段式入口：

#### 第一段：Admission Validation（机器判定）

| 检查项 | 判定规则 | 失败行为 |
|--------|----------|----------|
| 结构完整性 | canonical bytes 能被解析为合法 schema | 拒绝，不进入评审 |
| 引用合法性 | ApplicationContractVersion digest 存在且有引用权 | 拒绝 |
| Policy floor 合规 | effect_policy 不放宽最低约束 | 拒绝 |
| Self-Reference 禁止 | bytes 不包含自身 digest | 拒绝 |
| 内容寻址可计算 | 能产出稳定 digest | 拒绝 |

Admission 是机器判定，**不允许人工覆盖**。

#### 第二段：Source Review（人工 + 规则组合）

| Reviewer 类 | 职责 | 强制性 |
|-------------|------|--------|
| 结构评审（Structural Reviewer） | 复核 Admission 未覆盖的结构风险 | 强制 |
| 合规评审（Compliance Reviewer） | 复核 Policy、scope、人审门配置 | 强制 |
| 业务评审（Business Reviewer） | 提供业务建议 | 可选，不阻塞 |

**关键决策：评审只看结构/引用/合规，不评业务正确性。** 业务正确性归 ReleaseEvaluation（Domain Model §7.12 SC-19）。这是一个重要的关注点分离——评审门槛可机械判定、可重复执行，不会因业务主观判断阻塞 Candidate 升级。

Candidate 不存在"Pend + Resubmit 同一对象"路径。任何修改都必须产新 Candidate。

### 3.2 D-3：Build / BuildRun Compiler 版本治理（ADR-005 §6）

#### Compiler 的 10 个阶段（Artifact Spec §7.2）

```text
BlueprintVersion bytes
    ↓
 1. Parse        — 解析为 AST
 2. Validate     — 结构校验 + Compatibility Matrix 三点检查
 3. Normalize    — 规范化 AST
 4. Resolve      — 解析依赖为精确 digest（不接受 range/latest）
 5. Policy Check — Policy floor 合规
 6. Plan         — 确定性调度计划（不调 LLM！）
 7. Lower        — 降低为 IR 中间形式
 8. Optimize     — 确定性优化
 9. Package      — 组装 ExecutionPlanIR + SourceMap
10. Provenance   — 组装构建证据
    ↓
ExecutionPlanIR + SourceMap + ProvenanceManifest
```

每个阶段都是纯函数：相同输入永远产出相同中间结果与最终 digest。

#### Compiler 版本号：EPOCH.MAJOR.MINOR

| 递增类型 | 含义 | 示例 |
|----------|------|------|
| EPOCH | 阶段大重构（阶段重排、IR schema 不兼容） | 1.0.0 → 2.0.0 |
| MAJOR | 单阶段不兼容变更 | 1.0.0 → 1.1.0 |
| MINOR | bug 修复，行为不变 | 1.0.0 → 1.0.1 |

**同一版本号的 Compiler 实现字节级确定。** "同版本号偷改实现"是关键风险。

#### Build 的铁律（HC-7）

- Build **MUST NOT** 进行 Release 评估
- Build **MUST NOT** 调用 LLM 进行 Planning / Authoring / IR 重写
- Build **MUST NOT** 以 WorkflowSpec 为输入（HC-2）
- Build **MUST NOT** 进行 Production signing
- Build **MUST NOT** 进行 ReleaseChannel promotion

一句话：**Build 只负责确定性编译，不做价值判断。**

#### Build 输入身份完整性（HC-12）

Build 必须显式声明全部影响产出的输入：

```
BlueprintVersion digest
  + Compiler EPOCH.MAJOR.MINOR
  + 确定性构建参数集
  + 精确依赖锁（每条依赖是精确 digest，不允许 tag/range/latest）
  + PolicyBundle digest
```

`build_run_id`、构建时间戳、构建机器标识、Operator 身份只进入 detached Provenance，**不进入 hashed bytes**。

### 3.3 D-4：ExecutionPlanIR 内部性与可读性边界（ADR-005 §7）

| 决策项 | 定稿 |
|--------|------|
| IR 内部性 | Supply Chain Layer 内部构建产物，不对外暴露 |
| IR 不可执行性 | 必须经 SkillRelease 包装才能进入 Runtime |
| IR 不可直接部署性 | 部署对象是 DeploymentRevision |
| IR 不可人工编辑性 | 任何 IR 修改 = 新 BuildRun = 新 IR digest |
| IR 确定性 | 同一完整 Build 输入身份 → 同一 IR digest |

#### 可读性边界

| 场景 | 是否允许 |
|------|----------|
| 通过 Source Map 回溯 IR 节点到 Blueprint 源位置 | ✅ 允许 |
| 通过 Registry 按 digest 拉 IR bytes 用于离线分析 | ✅ 允许 |
| 在 Evaluation 中作为评估对象子结构 | ✅ 允许 |
| 人工编辑 IR bytes | ❌ 禁止 |
| 直接执行 IR（不通过 SkillRelease） | ❌ 禁止 |
| 直接部署 IR（不通过 DeploymentRevision） | ❌ 禁止 |
| 把 IR 作为 wire 对外暴露 | ❌ 禁止 |

---

## 4. 当前代码如何实现

### 4.1 BlueprintCandidate（草案阶段）

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

生命周期：`Draft → In Review → Promoted | Rejected`（终态不可逆）

### 4.2 Admission Validation

代码位置：`apps/backend/langchat/blueprint/admission.py`

```python
def admit(candidate: BlueprintCandidate) -> AdmissionDecision:
    # (1) 结构完整性 — 检查必填字段非空
    # (2) 引用合法性 — ContractVersion digest 格式校验（sha256:/sha512: 前缀）
    # (3) Policy floor — effect_policy 在 {read_only, conditional_write} 集合内
    # ⚠️ 不评估业务正确性！(ADR-005 D-2)
    # ⚠️ Admission 是机器判定，不覆盖
```

### 4.3 BlueprintVersion（不可变源制品）

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

生命周期：`Active → Deprecated → Retired`（无 Draft 态）

关键规则：BlueprintVersion 创建后不可修改。任何修改请求生成新 Candidate，重新走完整入口。

`digest` 属性计算 SHA-256 over canonical JSON（sorted keys, compact separators）。

### 4.4 Build / BuildRun（确定性编译）

代码位置：`apps/backend/langchat/supply_chain/build.py`

```python
@dataclass(frozen=True)
class Build:
    build_id: str
    blueprint_version_digest: str     # ← 必须 BlueprintVersion
    compiler_version: str             # ← EPOCH.MAJOR.MINOR
    deterministic_params: Mapping[str, object]
    dependency_lock: Mapping[str, str]  # ← 精确 digest
    target_compat_key: CompatCellKey   # ← 兼容性矩阵维度
```

`input_digest` 计算排除了 `build_id`——两个不同 build_id 但相同输入身份的 Build 产出相同 input_digest。这就是确定性。

#### WorkflowSpec 拦截器（HC-2 的代码级实现）

```python
def validate_build_input(value: object) -> None:
    """拒绝 WorkflowSpec 类型的输入"""
    value_type = type(value)
    module_name = getattr(value_type, "__module__", "") or ""
    if module_name.startswith("langchat.workflow."):
        raise InvalidBuildInputError(
            code="workflowspec-not-supported",
            message="Build input must be a BlueprintVersion..."
        )
```

这段代码在 Build 入口**显式拒绝** WorkflowSpec——是 ADR-005 HC-2（WorkflowSpec MUST NOT 作为 Build 输入）的代码级实现。

### 4.5 10 阶段流水线

代码位置：`apps/backend/langchat/supply_chain/pipeline.py` + `stages.py`

`run_pipeline()` 函数按固定顺序执行 10 个阶段：

```python
STAGE_ORDER = (
    "parse", "validate", "normalize", "resolve", "policy_check",
    "plan", "lower", "optimize", "package", "provenance"
)
```

每个阶段是纯函数 `(StageContext) -> StageResult`。阶段版本固定为 `1.0.0`（WP-03 阶段）。

`Validate` 阶段额外执行 Compatibility Matrix 三点检查（Artifact Spec §15.4）。

`Package` 阶段组装 `ExecutionPlanIR` 和 `SourceMap`，这是编译的最终产物。

### 4.6 ExecutionPlanIR（不可编辑内部表示）

代码位置：`apps/backend/langchat/supply_chain/execution_plan_ir.py`

```python
IR_VENDOR_MEDIA_TYPE = "application/vnd.langchat.execution-plan-ir.v1+json"
IR_SCHEMA_VERSION = "v1"

@dataclass(frozen=True)
class IRNode:
    node_id: str
    node_type: str
    payload_digest: str       # ← 语义内容的 SHA-256
    source_position: str      # ← 回溯到 Blueprint 源位置

@dataclass(frozen=True)
class ExecutionPlanIR:
    ir_schema_version: str    # ← 固定 "v1"
    nodes: tuple[IRNode, ...] # ← 不可变 tuple
```

`digest` 只取决于 `(ir_schema_version, nodes)`——时间戳、build_run_id、Operator 身份全部排除在 hashed bytes 之外。

---

## 5. 差距分析

| 维度 | 当前态（WP-03） | 目标态（ADR-005 + AS） | Gap 评级 |
|------|-----------------|----------------------|----------|
| BlueprintCandidate | 数据类已定义，支持基本字段校验 | 支持 External Authoring Client 导入，完整 Admission 规则集 | 🟡 中 |
| Admission Validation | 3 项检查（结构、引用、Policy） | 5 项检查（+ Self-Reference、digest 可计算）+ 自动化工具 | 🟡 中 |
| Source Review | 未实现 | 三类 Reviewer（结构/合规/业务），RBAC 映射 | 🔴 高 |
| BlueprintVersion | 数据类已定义，生命周期完整 | 完整生命周期管理，多版本共存 | 🟢 低 |
| Build 输入身份 | 数据类已定义，input_digest 排除 build_id | 与目标态一致 | 🟢 低 |
| WorkflowSpec 拦截 | `validate_build_input` 已实现 | 保持现状 | 🟢 低 |
| 10 阶段流水线 | 框架完整，大多为 pass-through stub | 各阶段真实编译逻辑 | 🔴 高 |
| Compiler 版本治理 | 硬编码 1.0.0 | EPOCH.MAJOR.MINOR 注册体系 | 🔴 高 |
| ExecutionPlanIR | 数据类完整，digest 计算正确 | 字段级 schema 归 ADR-007 | 🟡 中 |
| Source Map | 基础结构已定义 | 完整 IR 节点到 Blueprint 位置映射 | 🟡 中 |
| Provenance | ProvenanceManifest 已定义 | SLSA-style 完整证据链 | 🟡 中 |

**最大 Gap**：Source Review 流程和 10 阶段真实编译逻辑。

---

## 6. 今天多理解了什么

**以前以为：** Blueprint 就是一份配置文件，Runtime 直接读取执行。

**现在知道：**

1. Blueprint 是**制品**（artifact），不是配置——它有版本、digest、生命周期
2. Blueprint 和 ExecutionPlanIR 之间隔着 10 阶段确定性 Compiler——不是简单翻译
3. Compiler 的存在不是多余：它保证了**同一输入永远产出同一输出**
4. ExecutionPlanIR 是**内部不可编辑**的——不存在"手动 patch IR"的合法路径
5. Build 阶段**不做价值判断**（不评估 Release、不调 LLM、不签发）——职责严格分离
6. `build_run_id` 被排除在 hashed bytes 之外——两次不同构建（不同 ID）只要输入相同就产出相同 IR digest

---

## 7. 重新设计时是否仍这样做

**会。而且理由比昨天更充分。**

原因：

1. **确定性 Build 是信任的基础。** 如果 Blueprint 可以直接运行，每次执行结果取决于解释器的偶然行为，无法审计、无法复现。
2. **Compiler 版本治理让工具链可演进。** Compiler 升级不会偷偷改变已发布 Release 的行为。同版本号字节级确定。
3. **ExecutionPlanIR 不可编辑是不可谈判的。** 一旦允许"IR hotfix"，整个确定性链条就断了——谁改的？什么时候改的？为什么改的？不可追溯。
4. **Build 禁区（不调 LLM、不评估 Release）是关注点分离的典范。** 编译就是编译，评估就是评估。混在一起就两边都做不好。
5. **Candidate 不存在原地修改路径。** 每次修改都是新对象——保留了完整谱系，不会"丢了原来长什么样"。

---

## 8. 每日工程日志

| 类型 | 内容 |
|------|------|
| **新增** | 理解了制品链的完整链路：Candidate → Admission → Source Review → BlueprintVersion → Build → Compiler 10 阶段 → ExecutionPlanIR → SkillRelease |
| **新增** | 理解了 Compiler 的 10 个阶段（Parse → Validate → Normalize → Resolve → Policy Check → Plan → Lower → Optimize → Package → Provenance）及其确定性约束 |
| **新增** | 理解了 ExecutionPlanIR 的可读性边界：允许查看（Source Map 回溯、Registry 拉取、Evaluation 引用），禁止任何写入 |
| **修改** | 以前认为 Blueprint 是配置文件；现在知道 Blueprint 是制品（artifact），有 digest、版本、生命周期 |
| **确认** | `Build.input_digest` 排除 `build_id`——不同 build_id 但相同输入身份产出相同 IR digest（确定性） |
| **确认** | WorkflowSpec 拦截器（`validate_build_input`）是 ADR-005 HC-2 的代码级实现 |
| **遗留** | 当前 10 阶段流水线大多为 pass-through stub（WP-03 阶段），无真实编译逻辑 |
| **遗留** | BlueprintCandidate 不支持从 External Authoring Client 导入（WorkflowSpec 导入器未实现） |
| **技术债** | Source Review 流程（结构评审 + 合规评审）未实现；当前只有 Admission Validation |
| **技术债** | Compiler 各阶段版本号硬编码为 1.0.0，无独立版本治理 |
| **下一步** | 明天学习 Runtime：执行计划怎么跑起来的？为什么 Runtime 不保存状态？ |

---

## 9. 术语表

| # | 英文术语 | 音标 | 中文释义 |
|---|----------|------|----------|
| 1 | **Blueprint** | /ˈbluːprɪnt/ | 设计制品——人可读的、声明式的、描述"要做什么"的 canonical 源制品 |
| 2 | **BlueprintCandidate** | /ˈbluːprɪnt ˈkændɪdət/ | 蓝图候选——作者提交的草案，经评审后升级为 BlueprintVersion |
| 3 | **BlueprintVersion** | /ˈbluːprɪnt ˈvɜːrʒn/ | 蓝图版本——不可变、内容寻址的 canonical 源制品 |
| 4 | **Compiler** | /kəmˈpaɪlər/ | 编译器——把 BlueprintVersion 确定性编译为 ExecutionPlanIR 的 10 阶段流水线 |
| 5 | **ExecutionPlanIR** | /ˌeksɪˈkjuːʃn plæn aɪˈɑːr/ | 执行计划中间表示——Compiler 产出的内部不可编辑表示 |
| 6 | **BuildRun** | /bɪld rʌn/ | 构建运行——Build 的一次具体执行，产出 IR + SourceMap + Provenance |
| 7 | **Deterministic Build** | /dɪˌtɜːrmɪˈnɪstɪk bɪld/ | 确定性构建——同一完整输入身份永远产出相同产出 digest |
| 8 | **Provenance** | /ˈprɒvənəns/ | 溯源证据——记录构建全链路的 detached attestation |
| 9 | **Source Map** | /sɔːrs mæp/ | 源映射——把 IR 节点映射回 BlueprintVersion 源位置 |
| 10 | **Immutable** | /ɪˈmjuːtəbl/ | 不可变——对象创建后内容不可修改，是制品链的核心约束 |

---

## 10. 课堂练习与课后测试

### 课堂练习

**练习1：判断对错**

1. BlueprintVersion 可以被人工修改后重新保存。 → ___
2. 同一 BlueprintVersion + 同一 Compiler 版本，产出相同 ExecutionPlanIR digest。 → ___
3. ExecutionPlanIR 可以被 Runtime 直接装载执行。 → ___
4. Build 阶段可以调用 LLM 来优化 prompt。 → ___
5. WorkflowSpec 可以作为 Build 的输入。 → ___

**练习2：排列制品链顺序**

请把以下对象按制品链正确顺序排列：

```
A. ExecutionPlanIR    B. BlueprintCandidate    C. DeploymentRevision
D. SkillRelease v2    E. BlueprintVersion      F. BuildRun
```

正确顺序：___ → ___ → ___ → ___ → ___ → ___

### 课后测试

**Q1:** 为什么 BlueprintVersion 不能直接运行？
- A) 因为它没有输入输出定义
- B) 因为它是人可读的声明式制品，需要经过 Compiler 确定性编译为 ExecutionPlanIR 才能执行
- C) 因为它的版本号不对
- D) 因为它没有 digest

**Q2:** Compiler 的 10 个阶段中，"Plan"阶段可以使用 LLM 来生成执行计划吗？
- A) 可以，LLM 能生成更好的计划
- B) 不可以，Build MUST NOT 调用 LLM 进行 Planning（AS §7.3）
- C) 可以，但只在特殊情况下
- D) 只在 Release Gate 阶段可以

**Q3:** Build 的 `input_digest` 包含以下哪个字段？
- A) build_id
- B) 构建时间戳
- C) compiler_version
- D) Operator 身份

---

## 11. 真实参考

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
