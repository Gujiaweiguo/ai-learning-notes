# 🧱 LangChat 心智模型｜第9周-Day1：BlueprintVersion — 为什么 Blueprint 是制品不是配置？

> **📌 今日核心问题：为什么 Blueprint 不是配置文件，而是制品（Artifact）？**
>
> **日期**：2026-07-27（周一）
>
> **本周主题**：Domain Deep Dive — 拆对象，理解为什么存在、边界在哪
>
> **今日对象**：BlueprintVersion（Domain Model §7.3 SC-03，ADR-005 D-2）

---

## 目录

1. [往期回顾与业务关联](#1-往期回顾与业务关联)
2. [今日核心问题：为什么 Blueprint 是制品不是配置？](#2-今日核心问题为什么-blueprint-是制品不是配置)
3. [人话解释](#3-人话解释)
4. [LangChat 架构位置](#4-langchat-架构位置)
5. [ADR 依据：ADR-005 D-2 如何设计](#5-adr-依据adr-005-d-2-如何设计)
6. [代码验证](#6-代码验证)
7. [商业地产映射](#7-商业地产映射)
8. [与传统方案比较](#8-与传统方案比较)
9. [Gap Analysis](#9-gap-analysis)
10. [今天多理解了什么](#10-今天多理解了什么)
11. [重新设计时是否仍这样做](#11-重新设计时是否仍这样做)
12. [Daily Engineering Log](#12-daily-engineering-log)
13. [明日连接 + Semantic Layer](#13-明日连接--semantic-layer)
14. [术语表](#14-术语表)
15. [课堂练习与课后测试](#15-课堂练习与课后测试)
16. [真实参考](#16-真实参考)

---

## 1. 往期回顾与业务关联

### Week 8 回顾

Week 8 走通了 LangChat 完整链路的 10 个站点，从用户意图（Agent Host 接入）到执行结果（七字段结构化输出）。我们在 Day3 首次遇到 Blueprint，但当时是从"链路全景"视角快速扫过——知道它是制品链的起点，知道它经过 Compiler 变成 ExecutionPlanIR，但没有深入到对象本身。

Week 8 的 Virtual CTO Review 给出了五维评分基线（综合 7.2/10），其中 Technical Debt 最低（6.5/10），根本原因正是 BlueprintVersion 所在的 v2 制品链尚未落地。

### Week 9 定位

Week 9 不再走链路，而是**回到每个对象本身**。今天是第一个对象：BlueprintVersion。我们要回答的问题不是"它在链路中做什么"（Week 8 已回答），而是"**它为什么必须以这种形态存在**"。

### 与前面的关联

| 前面学过的 | 今天的深化 |
|---|---|
| W8-D2 ApplicationContract 是业务治理一等对象 | BlueprintVersion 引用精确的 ApplicationContractVersion digest |
| W8-D3 Blueprint 是制品不是配置 | 今天深入到 BlueprintVersion 的**不可变性、内容寻址、生命周期** |
| W8-D7 v2 制品链 6 个对象全部不存在于代码 | 今天验证：BlueprintVersion **已经存在于代码**（WP-02 已实现） |

---

## 2. 今日核心问题：为什么 Blueprint 是制品不是配置？

### 配置 vs 制品：一句话区分

**配置（Configuration）**：你随时可以改的东西。改了立即生效，不需要评审、不需要版本号、不需要 digest。

**制品（Artifact）**：你创建后不能改的东西。它有唯一身份标识（digest），有生命周期状态，有谱系（lineage），创建前必须经过评审。

### 为什么这个区别如此重要？

想象一个场景：你的数字员工"合同查询助手"今天回答了 500 个用户问题。明天有人修改了它的 Blueprint 配置文件——把 `effect_policy` 从 `read_only` 改成了 `conditional_write`。

如果是**配置模式**：修改立即生效，500 个用户的问题可能突然触发写操作。没有人审批过这个变更。没有回滚机制（因为你不知道之前的配置是什么）。没有审计追踪（因为配置文件没有版本）。

如果是**制品模式**：修改 = 创建新 BlueprintCandidate → 评审 → 升级为新 BlueprintVersion → Build → Release Gate → Deployment。每一步有审计。回滚 = 物化新 DeploymentRevision 指向旧 digest。变更影响可评估。

**LangChat 选择了制品模式。** 今天我们要理解这个选择的每一个维度。

---

## 3. 人话解释

### 用 Jason 26 年 ERP 经验讲

在传统 ERP 系统里，你见过的"配置"通常是：

- 销售订单的审批流配置——在 SPRO 里改几行，立即生效
- 报表参数配置——输入条件，点运行
- 权限角色配置——分配给用户，马上有权限

这些是**配置**，因为它们：
1. 没有内容寻址（没有 digest/hash）
2. 可以随时修改（没有评审门）
3. 没有谱系追踪（不知道从哪改过来的）
4. 修改后没有独立的版本号

**BlueprintVersion 不是配置，而是制品。** 类比：

| ERP 概念 | LangChat 概念 | 为什么类比 |
|---|---|---|
| 物料主数据（创建后不可改关键字段） | BlueprintVersion | 创建后有唯一编码，关键字段不可修改 |
| 工艺路线版本（有版本号和生效日期） | BlueprintVersion 的 version 字段 | 同一物料有多个工艺路线版本 |
| 变更管理（ECR/ECN） | BlueprintCandidate 评审流程 | 任何变更走正式评审，产生新版本 |
| 物料编码 = 内容标识 | BlueprintVersion 的 content_digest | 相同内容 = 相同编码 |

但 BlueprintVersion 比 ERP 物料主数据更严格：**它的不可变性是数学保证**（SHA-256 内容寻址），不是流程约定。

### 通俗类比

把 BlueprintVersion 想象成**已公证的合同文本**：

1. **起草阶段**（BlueprintCandidate）：你写了一份合同草案，可以反复修改。草案不是正式合同。
2. **公证阶段**（Admission + Source Review）：公证处检查合同格式（结构完整性）、引用的法律条款是否有效（引用合法性）、是否符合最低法律要求（Policy floor）。公证处**不评估**你的商业条件是否最优（业务正确性归 ReleaseEvaluation）。
3. **存档阶段**（BlueprintVersion）：公证完成后，合同被赋予唯一编号（digest），存入档案室（Registry）。从此不可修改。需要修改？走新一轮起草 → 公证 → 存档。

---

## 4. LangChat 架构位置

### 在制品链中的位置

```
External Authoring Client
      │
      ▼
BlueprintCandidate（DM §7.2 SC-02）        ← 草案，可修改
      │  Admission Validation（机器判定）
      ▼
Admitted Candidate
      │  Source Review（人工+规则评审）
      ▼
┌─────────────────────────────────┐
│  BlueprintVersion               │  ← ★ 今天在这里
│  （DM §7.3 SC-03）              │
│  - canonical 源制品              │
│  - 不可执行                      │
│  - 不可被人工编辑                 │
│  - 内容寻址（SHA-256 digest）    │
└─────────────────────────────────┘
      │  Build（确定性 10 阶段 Compiler）
      ▼
BuildRun → ExecutionPlanIR → SkillRelease v2 → DeploymentRevision → Runtime
```

### 在四层架构中的位置

BlueprintVersion 属于 **Supply Chain Layer**（制品链层），不是 Business Domain Layer，不是 Runtime Layer，不是 Operations Layer。

| 层 | 对象 | 与 BlueprintVersion 的关系 |
|---|---|---|
| Business Domain Layer | ApplicationContract, DigitalEmployeeDefinition | DED 引用 BlueprintVersion digest；ApplicationContract 被 BlueprintVersion 引用 |
| **Supply Chain Layer** | **BlueprintVersion**, Build, ExecutionPlanIR, SkillRelease | BlueprintVersion 是 canonical 源制品 |
| Runtime Layer | DeploymentRevision, RuntimeABI, FrozenExecutionContext | Runtime 不直接接触 BlueprintVersion，只接触 SkillRelease |
| Operations Layer | Registry, Catalog | BlueprintRegistry 是 per-topic 事实源 |

### 关键约束（HC-5）

> "BlueprintVersion 是 canonical 源制品，可审查、不可执行、不可被人工编辑"（Charter §6.4, Domain Model §7.3 SC-03）

注意三个"不"：
- **不可执行**：你不能 `BlueprintVersion.run()`
- **不可被人工编辑**：你不能 `version.content = "新内容"`
- **不可直接部署**：你不能把 BlueprintVersion 直接推到 Runtime

---

## 5. ADR 依据：ADR-005 D-2 如何设计

### ADR-005 D-2 关键决策

ADR-005 §5（D-2）定义了 BlueprintCandidate 到 BlueprintVersion 的完整评审流程。以下是核心决策：

#### 5.1 升级路径单向

```
Candidate 生命周期：
  Draft → In Review → Promoted（升级为 BlueprintVersion）
                    → Rejected（拒绝，保留为历史证据）

升级后：
  Candidate 进入只读历史态，不可复活
  BlueprintVersion 被创建，进入 Active 状态
```

**关键规则**：Candidate 不存在"Pend + Resubmit 同一对象"路径。任何修改都必须产新 Candidate。这确保了审计链的完整性。

#### 5.2 评审分两段

| 阶段 | 执行者 | 内容 | 失败行为 |
|---|---|---|---|
| Admission Validation | 机器 | 结构完整性 + 引用合法性 + Policy floor + Self-Reference 禁止 + digest 可计算 | 拒绝，不进入 In Review |
| Source Review | 人工+规则 | 结构评审（强制）+ 合规评审（强制）+ 业务评审（可选） | 拒绝，保留历史证据 |

**最关键的决策**：评审**只承担结构性、引用合法、Policy floor 合规判定，不承担业务正确性判定**。业务正确性归 ReleaseEvaluation。

为什么？因为评审门槛必须**可机械判定、可重复执行**。如果评审要判断"这个 prompt 能否答对问题"，就变成了主观判断，无法自动化，无法保证一致性。

#### 5.3 物化规则

Candidate 通过评审后物化为 BlueprintVersion：

1. Identity = `(blueprint_id, version)`，blueprint_id 在 `(tenant, workspace)` 内稳定，version 单调递增
2. Digest 按 AS §3.1 canonical serialization + hashing 规则计算
3. 必须保留指向原 Candidate 的指针（`originating_candidate_id`）
4. **创建后不可修改**——任何修改请求 = 新 Candidate → 重新走完整入口

### ADR-005 §9 制品链权威边界

ADR-005 §9 给出了完整的制品链总图，BlueprintVersion 位于第三个环节：

> BlueprintVersion（canonical 源制品；不可执行；不可被人工编辑）→ Build 物化 BuildRun → ...

链上每一环不可跳过、不可逆序（HC-3）。

---

## 6. 代码验证

### 6.1 BlueprintVersion 类定义

**文件**：`/root/langchat/apps/backend/langchat/blueprint/version.py`

```python
@dataclass(frozen=True)
class BlueprintVersion:
    """Immutable, content-addressed canonical source artifact (DM §7.3 SC-03)."""
    
    blueprint_id: str
    version: str
    tenant_id: str
    workspace_id: str
    application_contract_version_digest: str  # 引用 ApplicationContractVersion
    originating_candidate_id: str             # 谱系指针
    content_digest: str                       # 内容寻址
    state: str = "active"                     # 默认状态是 active（不是 draft！）
```

**关键代码事实**：

1. `@dataclass(frozen=True)` —— **冻结的数据类**。Python 层面保证不可变：任何赋值操作 `version.content_digest = "xxx"` 会抛出 `ImmutableObjectError`（FrozenInstanceError）。

2. `state: str = "active"` —— BlueprintVersion 创建后直接是 `active`，**没有 Draft 状态**。Draft 是 Candidate 的状态。Version 天生就是"已定稿"的。

3. `application_contract_version_digest` —— 必须是 well-formed digest（`sha256:xxx` 或 `sha512:xxx`），构造时就会校验。这确保了每个 BlueprintVersion 都锚定在一个精确的 ApplicationContractVersion 上。

4. `originating_candidate_id` —— **谱系指针**，指向产出这个 Version 的 Candidate。不允许"匿名 Version"。

### 6.2 内容寻址（Content Addressing）

```python
@property
def digest(self) -> str:
    """SHA-256 over canonical JSON of the version's full content."""
    payload = {
        "blueprint_id": self.blueprint_id,
        "version": self.version,
        "tenant_id": self.tenant_id,
        "workspace_id": self.workspace_id,
        "application_contract_version_digest": self.application_contract_version_digest,
        "originating_candidate_id": self.originating_candidate_id,
        "content_digest": self.content_digest,
        "state": self.state,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

**理解要点**：
- `sort_keys=True` —— JSON 序列化时按键名排序，确保相同内容永远产出相同字节序列
- `separators=(",", ":")` —— 紧凑模式，没有多余空格
- 任何一个字段变化 → digest 完全不同
- 这就是"内容寻址"：身份 = 内容的哈希

### 6.3 生命周期状态机

```python
_VALID_TRANSITIONS = {
    "active": frozenset({"deprecated"}),     # 只能前进
    "deprecated": frozenset({"retired"}),     # 只能前进
    "retired": frozenset(),                   # 终态，不可回退
}
```

```
active → deprecated → retired
  ↑                      │
  │    ❌ 不能反向         │
  └─── ✗ ────────────────┘
```

**关键设计**：状态转换是**前向唯一**（forward-only）。一个 `retired` 的 Version 永远不能回到 `active`。如果需要"恢复"某个已退役的 Version，必须创建新 Candidate → 新评审 → 新 Version。

### 6.4 BlueprintRegistry（注册表）

**文件**：`/root/langchat/apps/backend/langchat/blueprint/registry.py`

```python
_FORBIDDEN_EXECUTION_METHODS = frozenset({"execute", "invoke", "run", "dispatch"})

@dataclass
class BlueprintRegistry:
    """In-memory per-topic BlueprintVersion registry (DM §7.11 SC-16)."""
    
    _store: dict[tuple[str, str, str, str], BlueprintVersion]
    
    def register(self, version: BlueprintVersion) -> None: ...
    def get(self, tenant_id, workspace_id, blueprint_id, version) -> BlueprintVersion | None: ...
    def list_versions(self, tenant_id, workspace_id, blueprint_id) -> tuple[BlueprintVersion, ...]: ...
```

**关键代码事实**：

1. Registry 只有 `register`、`get`、`list_versions` 三个方法。**没有 execute/invoke/run/dispatch**。

2. Registry 在构造时通过 `__post_init__` 扫描自身成员，如果发现禁止的方法名，直接 `raise RuntimeError`。这是**防御性深度设计**（defence-in-depth）——即使未来有人加了执行方法，代码会在启动时崩溃。

3. **Per-topic** 意味着 `(tenant_id, workspace_id, blueprint_id)` 有独立的版本空间。不同 tenant 可以有相同 blueprint_id + version 的不同 Version。

### 6.5 Admission（准入检查）

**文件**：`/root/langchat/apps/backend/langchat/blueprint/admission.py`

```python
def admit(candidate: BlueprintCandidate) -> AdmissionDecision:
    """Validate candidate for structural, reference, and policy-floor compliance."""
    # (1) 结构完整性
    # (2) 引用合法性（ApplicationContractVersion digest 格式校验）
    # (3) Policy floor 合规（effect_policy ∈ {read_only, conditional_write}）
    # ⚠️ 不评估业务正确性！
```

`AdmissionDecision` 有一个不变量：`allowed=True` 时 `reasons` 必须为空。这通过 `__post_init__` 强制。

### 6.6 测试验证

**文件**：`/root/langchat/apps/backend/tests/unit_tests/test_blueprint_version_immutability.py`

已有测试覆盖：
- `test_version_is_content_addressed_identical_bytes_identical_digest` —— 相同内容 → 相同 digest
- `test_version_is_content_addressed_any_byte_change_changes_digest` —— 任何字节变化 → 不同 digest
- `test_version_is_immutable` —— 修改字段抛出 `ImmutableObjectError`
- `test_version_lifecycle_transitions_are_forward_only` —— 生命周期前向唯一
- `test_registry_is_not_execution_entrypoint` —— Registry 没有执行方法
- `test_registry_post_init_runtime_check_catches_future_execution_method` —— 子类加 execute 方法会崩溃

**文件**：`/root/langchat/apps/backend/tests/unit_tests/test_blueprint_candidate_admission.py`

已有测试覆盖：
- `test_admission_does_not_check_business_correctness` —— Admission 不检查业务正确性
- `test_admission_rejects_malformed_application_contract_reference` —— 畸形引用被拒
- `test_rejected_candidate_cannot_be_promoted` —— 被拒绝的 Candidate 不能升级

### 6.7 Build 拒绝 WorkflowSpec

**文件**：`/root/langchat/apps/backend/tests/unit_tests/test_build_rejects_workflow_spec.py`

```python
def test_workflow_spec_input_rejected() -> None:
    """WorkflowSpec-typed object as Build input raises InvalidBuildInputError."""
    # 模拟 WorkflowSpec 对象
    class WorkflowSpecSentinel: ...
    WorkflowSpecSentinel.__module__ = "langchat.workflow.schema"
    sentinel = WorkflowSpecSentinel()
    
    with pytest.raises(InvalidBuildInputError, match="workflowspec-not-supported"):
        validate_build_input(sentinel)
```

这条测试是**制品链边界的铁卫**——WorkflowSpec 永远不能进入 Build，只有 BlueprintVersion 可以。

---

## 7. 商业地产映射

### MI CRE 场景对应

| LangChat 概念 | MI CRE 场景 | 对应关系 |
|---|---|---|
| BlueprintCandidate | 合同查询助手的 AI 逻辑草案 | "我想让助手支持自然语言查合同到期"的 AI 行为描述 |
| ApplicationContractVersion | 合同查询的业务接口定义 | 输入：租户ID/时间段；输出：合同列表；effect=read_only |
| **BlueprintVersion** | **合同查询助手 AI 逻辑的已评审定稿版本** | **经 IT 评审通过的 AI 行为定义，有版本号 v1.2，不可修改** |
| Build | 把 AI 逻辑编译为可执行计划 | 把"查合同"的逻辑描述编译为 Runtime 可加载的 IR |
| SkillRelease | 合同查询助手的可部署包 | 包含 IR + Source Map + 依赖锁的可部署 OCI 制品 |

### 具体场景

**场景**：商场运营总监要求"合同查询助手新增到期提醒功能"。

**制品模式（LangChat）**：

```
1. 产品经理在 EAC 中编写新 BlueprintCandidate：
   "当用户查询合同时，如果合同在 90 天内到期，主动提醒"
   effect_policy = read_only
   引用 ApplicationContractVersion v1.2

2. Admission 机器检查：
   ✅ 结构完整
   ✅ ACV digest 格式正确
   ✅ effect_policy = read_only（符合 P0 约束）

3. Source Review 人工评审：
   结构评审员 ✅：引用了精确版本而非 "latest"
   合规评审员 ✅：effect_policy 不放宽
   业务评审员（建议）：prompt 可以更简洁——但不阻塞

4. 物化为 BlueprintVersion：
   blueprint_id = "contract-query-assistant"
   version = "v1.3"
   content_digest = sha256:abc123...
   originating_candidate_id = "cand-2026-07-27-001"
   state = active

5. 旧版本 v1.2 不受影响，继续在被已部署的 DeploymentRevision 引用
```

**如果用配置模式（传统做法）**：

```
1. 开发者修改 config.yaml：加一段"到期提醒"逻辑
2. 直接上线，没有评审
3. 线上 500 个用户突然开始收到提醒，有些用户不需要这个功能
4. 想回滚？不知道之前的配置是什么（没有版本）
5. 想审计？config.yaml 没有 changelog
6. 想知道谁改的？git log 有，但运营团队不看 git
```

---

## 8. 与传统方案比较

### 配置模式 vs 制品模式

| 维度 | 配置模式 | 制品模式（BlueprintVersion） |
|---|---|---|
| 修改方式 | 直接编辑文件/数据库 | 新 Candidate → 评审 → 新 Version |
| 版本追踪 | 依赖外部（git/数据库审计日志） | 内建于对象（version + digest） |
| 回滚 | 找到旧配置覆盖回去 | 物化新 DeploymentRevision 指向旧 digest |
| 评审 | 可选，依赖流程约定 | 强制，代码层面不可跳过 |
| 内容完整性 | 无法保证 | SHA-256 数学保证 |
| 谱系追踪 | 无 | originating_candidate_id 指向起源 |
| 可执行性 | 配置被直接加载执行 | Version 不可执行，必须经 Build → SkillRelease |
| 防御深度 | 无 | Frozen dataclass + Registry 无执行方法 + Build 拒绝错误输入 |

### Dify/LangChain 的做法

| 平台 | "AI 应用定义"是什么 | 与 BlueprintVersion 的区别 |
|---|---|---|
| Dify | YAML 配置文件（app.yaml） | 配置模式：可随时改，没有评审门，没有 digest，没有谱系 |
| LangChain | Python 代码（Chain/Agent 定义） | 代码模式：有 git 版本控制，但没有生命周期状态机，没有内容寻址 |
| n8n | JSON workflow 定义 | 配置模式：可随时改，有版本但不是内容寻址 |
| **LangChat** | **BlueprintVersion 制品** | **制品模式：不可变、内容寻址、有生命周期、有谱系、有评审门** |

### 为什么选制品模式？

**核心原因**：LangChat 面向**企业级生产环境**，不是个人玩具。

企业环境的硬需求：
1. **审计**：审计员要能追溯"谁在什么时候创建/修改了这个 AI 行为"
2. **回滚**：生产事故时必须能在 30 秒内回滚到上一版本
3. **合规**：某些行业（金融/医疗）的 AI 行为变更需要人工审批
4. **多版本共存**：灰度发布时 v1.2 和 v1.3 同时在跑
5. **供应链安全**：每个制品有密码学身份（digest），篡改即被发现

配置模式无法满足以上任何一个需求。

---

## 9. Gap Analysis

### 目标态 vs 代码现实

| 维度 | 目标态（ADR-005） | 代码现实 | Gap |
|---|---|---|---|
| BlueprintVersion 不可变性 | `@dataclass(frozen=True)` + transition 只能创建新对象 | ✅ 已实现 | 无 Gap |
| 内容寻址（digest） | SHA-256 over canonical JSON | ✅ 已实现 | 无 Gap |
| 生命周期 active→deprecated→retired | 前向唯一，无回退 | ✅ 已实现 | 无 Gap |
| 谱系指针（originating_candidate_id） | 每个 Version 必须指向起源 Candidate | ✅ 已实现 | 无 Gap |
| Admission 机器检查 | 结构+引用+Policy floor | ✅ 已实现（WP-02） | 无 Gap |
| Source Review 人工评审 | 结构+合规强制，业务可选 | 🔴 未实现 | 评审流程没有代码落地 |
| BlueprintRegistry per-topic | 每个 (tenant, workspace, blueprint_id) 独立 | ✅ 已实现 | 内存存储，需要持久化 |
| Registry 非执行入口 | 无 execute/invoke/run/dispatch | ✅ 已实现 | 防御深度测试已覆盖 |
| Build 只接受 BlueprintVersion | 拒绝 WorkflowSpec | ✅ 已实现 | 验证函数已存在 |
| Compiler 10 阶段 | Parse→Validate→...→Provenance | 🟡 已实现但为 stub | 10 个阶段大多是 pass-through |

### Gap 严重程度

| Gap | 严重程度 | 说明 |
|---|---|---|
| Source Review 无代码 | 🟡 中 | 评审流程是治理要求，但当前 WP-02 只实现了 Admission（机器部分），人工评审部分等待后续 WP |
| Registry 内存存储 | 🟡 中 | 当前是 `dict` 内存存储，生产需要持久化（数据库/对象存储） |
| Compiler 阶段为 stub | 🟡 中 | 10 阶段框架正确，但实际编译逻辑等待后续 WP 填充 |

**关键发现**：BlueprintVersion 的核心设计（不可变 + 内容寻址 + 生命周期 + 谱系 + Registry）**已经在代码中落地**，这是 v2 制品链中最成熟的部分。Gap 主要在周边流程（评审、持久化、编译逻辑），不在对象本身。

---

## 10. 今天多理解了什么

### 以前以为 → 现在知道

| 以前以为 | 现在知道 |
|---|---|
| BlueprintVersion 就是"有版本的 Blueprint" | BlueprintVersion 是**不可变制品**，它的不可变性不是流程约定而是**数学保证**（SHA-256 内容寻址 + frozen dataclass） |
| 评审就是"领导审批" | 评审是**两段式**：Admission（机器判定，不可人工覆盖）+ Source Review（人工+规则）。评审只管结构性/引用/Policy，**不管业务正确性** |
| 不可变就是"不能改" | 不可变是**多维度的**：Python 层（frozen dataclass）、逻辑层（无 setter）、身份层（digest 变了就不是同一个对象）、执行层（Registry 无执行方法） |
| Registry 就是一个存储 | Registry 是**非执行入口**——它通过 `__post_init__` 扫描自身方法名，发现 execute/invoke/run/dispatch 就崩溃。这是防御性深度设计 |
| "制品"和"配置"差不多 | 完全不同。制品有 digest（密码学身份）、有生命周期、有谱系、有评审门、有不可变性。配置只是"可改的参数" |
| Candidate 被拒绝后可以修改重提 | ❌ Candidate 是**终态的**——Rejected 和 Promoted 都是终态，不可回退。修改 = 创建**新** Candidate |
| Version 的 state 可以从 retired 回到 active | ❌ 生命周期是**前向唯一**的：active→deprecated→retired，不可逆。需要"恢复"= 新 Candidate → 新评审 → 新 Version |

---

## 11. 重新设计时是否仍这样做

### 会保留的设计

1. **`@dataclass(frozen=True)`** —— Python 语言层面的不可变性，是最简单有效的不可变保证。如果重设计，不变。

2. **SHA-256 内容寻址** —— 内容寻址是供应链安全的基础。如果重设计，不变。

3. **生命周期前向唯一（active→deprecated→retired）** —— 状态机的前向唯一是审计的基础。如果重设计，不变。

4. **Registry 无执行方法 + `__post_init__` 防御** —— 这种"自毁"式防御比任何文档约定都有效。如果重设计，不变。

5. **评审两段式 + 不检查业务正确性** —— 评审门槛可机械判定是关键设计。如果重设计，不变。

6. **originating_candidate_id 谱系指针** —— 每个 Version 都能追溯到起源 Candidate。如果重设计，不变。

### 可能调整的设计

1. **Candidate 终态不可回退** —— 可能考虑增加 "withdraw" 状态，允许作者主动撤回 In Review 的 Candidate（而不是等拒绝）。但不允许已决策（Promoted/Rejected）的回退。

2. **Registry 内存存储** —— 生产环境必须持久化。可能用 event-sourced 模式（每次 register 是一个事件，可重放到任意时间点）。

3. **Version 编号策略** —— 当前是自由字符串，可能改为语义化版本（MAJOR.MINOR.PATCH），与 ApplicationContractVersion 的版本策略对齐。

---

## 12. Daily Engineering Log

### 新增
- BlueprintVersion 类定义已验证（version.py）：frozen dataclass + SHA-256 digest + 前向唯一生命周期
- BlueprintCandidate 类定义已验证（candidate.py）：Draft→In Review→Promoted|Rejected 四态生命周期
- Admission 准入检查已验证（admission.py）：结构+引用+Policy floor 三项检查，不检查业务正确性
- BlueprintRegistry 已验证（registry.py）：per-topic 存储 + 禁止执行方法 + `__post_init__` 防御
- Build 输入验证已验证（build.py）：`validate_build_input()` 拒绝 WorkflowSpec 模块的对象
- 完整测试覆盖已验证：immutability / admission / build_rejects_workflow_spec 三组测试

### 修改
- 无

### 确认
- BlueprintVersion 是 v2 制品链中**代码实现最成熟**的对象——核心设计全部落地，测试覆盖完整
- `@dataclass(frozen=True)` + SHA-256 + 前向唯一生命周期 = 三重不可变性保证
- Registry 的"自毁式"防御（`__post_init__` 检测执行方法名）是企业级代码的典范

### 遗留
- Source Review 人工评审流程没有代码落地（当前只有 Admission 机器检查）
- Registry 是内存存储，没有持久化机制
- Compiler 10 阶段大多为 pass-through stub

### 技术债
- Source Review 代码缺失 → 当前 Candidate → Version 的升级路径只有机器检查，没有人工评审门
- Registry 持久化缺失 → 生产部署需要数据库/对象存储后端

### 下一步
- 明天（Day2）：SkillRelease —— 为什么它是唯一可部署单元？它和 BlueprintVersion 的关系是什么？

---

## 13. 明日连接 + Semantic Layer

### 明日预告

**Day 2：SkillRelease —— 为什么是唯一可部署单元？**

BlueprintVersion 是 canonical 源制品，但它不可执行、不可部署。那么什么才能部署？答案是 SkillRelease v2。明天我们理解：
- SkillRelease 包装了什么？（IR + Source Map + 依赖锁 + Behavioral Assets）
- 为什么 BlueprintVersion 不能直接部署？
- SkillRelease 的 Release Gate 有哪些门？
- canonical wire（ADR-003 v1.2）和 SkillRelease v2 的关系

### Semantic Layer 位置

```
Ontology（本体论：企业能力域）
    ↓
Domain Model（领域模型：35 个聚合对象）
    ↓
ApplicationContract（业务契约：API 语义）
    ↓
BlueprintCandidate → BlueprintVersion（★ 今天）   ← 源制品：定义 AI 行为
    ↓
Build → ExecutionPlanIR（确定性编译）
    ↓
SkillRelease（唯一可部署制品）
    ↓
DeploymentRevision（运行时闭包）
```

BlueprintVersion 在 Semantic Layer 上的位置是**源制品**——它是所有后续编译、打包、部署的输入源头。它的质量直接决定了整条链的质量。

---

## 14. 术语表

| 英文 | 音标 | 中文 | 说明 |
|---|---|---|---|
| Artifact | /ˈɑːrtɪfækt/ | 制品 | 创建后不可变的、有唯一身份标识的对象 |
| Blueprint | /ˈbluːprɪnt/ | 蓝图 | AI 行为的源描述，定义数字员工做什么、怎么做 |
| BlueprintVersion | /ˈbluːprɪnt ˈvɜːrʒən/ | 蓝图版本 | Blueprint 的不可变、内容寻址的 canonical 源制品 |
| BlueprintCandidate | /ˈbluːprɪnt ˈkændɪdət/ | 蓝图候选 | BlueprintVersion 的前身，可修改的提案 |
| Content Addressing | /ˈkɒntent əˈdresɪŋ/ | 内容寻址 | 用内容的哈希值作为对象唯一标识的技术 |
| Canonical | /kəˈnɒnɪk(ə)l/ | 规范的/标准的 | 权威的、唯一认可的表示形式 |
| Admission | /ədˈmɪʃ(ə)n/ | 准入 | Candidate 提交时的机器判定检查 |
| Source Review | /sɔːrs rɪˈvjuː/ | 源评审 | Candidate 的结构+合规人工评审 |
| Lineage | /ˈlɪniɪdʒ/ | 谱系 | 对象的来源追溯链 |
| Digest | /ˈdaɪdʒest/ | 摘要 | 内容的 SHA-256 哈希值，用作唯一标识 |
| Immutable | /ɪˈmjuːtəb(ə)l/ | 不可变的 | 创建后不可修改 |
| Forward-Only | /ˈfɔːrwərd ˈoʊnli/ | 前向唯一 | 状态只能向前推进，不可回退 |
| Per-topic | /pɜːr ˈtɒpɪk/ | 按主题 | 每个工作空间独立管理版本空间 |
| FrozenExecutionContext | /ˈfroʊzən ɪɡˈzekjuːʃən kɒntekst/ | 冻结执行上下文 | Runtime 执行时携带的不可变身份和委托信息 |
| OCI | /ˌoʊ siː ˈaɪ/ | 开放容器倡议 | Open Container Initiative，制品分发标准 |

---

## 15. 课堂练习与课后测试

### 课堂练习

**练习 1：制品 vs 配置判断题**

以下场景中，哪些应该用"制品模式"管理，哪些用"配置模式"即可？

| 场景 | 制品 or 配置？ | 理由 |
|---|---|---|
| 数字员工的 prompt 模板 | ? | ? |
| 数字员工的输出格式（JSON schema） | ? | ? |
| 数字员工连接的 API 端点 URL | ? | ? |
| 数字员工的回复语言（中文/英文） | ? | ? |
| 数字员工的 effect_policy（read_only/conditional_write） | ? | ? |

**参考答案**：

| 场景 | 答案 | 理由 |
|---|---|---|
| prompt 模板 | 制品 | 影响 AI 行为，需要审计和回滚 |
| JSON schema | 制品 | 影响接口契约，需要版本管理 |
| API URL | 配置 | 环境变量级别，不同环境不同值 |
| 回复语言 | 配置 | 用户偏好，不影响安全 |
| effect_policy | 制品 | 安全治理字段，必须不可变+有审计 |

**练习 2：状态机推演**

给定一个 BlueprintVersion 当前状态为 `deprecated`，以下哪些操作是合法的？

a) transition("active") —— 回到活跃
b) transition("retired") —— 退役
c) transition("deprecated") —— 保持不变
d) 修改 content_digest 字段
e) 创建新 Candidate 来替代它

**答案**：
- a) ❌ 非法。`_VALID_TRANSITIONS["deprecated"] = {"retired"}`，不包含 active
- b) ✅ 合法。deprecated → retired 是唯一合法前进路径
- c) ❌ 非法。不在合法转换集中（状态转换不允许"自转换"）
- d) ❌ 非法。`frozen=True`，赋值抛出 `ImmutableObjectError`
- e) ✅ 合法。创建新 Candidate → 评审 → 新 Version 是唯一更新路径

### 课后测试

**测试 1（单选）**：BlueprintVersion 创建后，以下哪个字段可以被修改？

A. state
B. content_digest
C. 都不能修改
D. blueprint_id

**答案**：C。BlueprintVersion 是 `@dataclass(frozen=True)`，所有字段不可修改。state 只能通过 `transition()` 方法创建新对象来改变。

---

**测试 2（单选）**：BlueprintRegistry 的 `__post_init__` 检查会阻止以下哪个方法？

A. register
B. get
C. list_versions
D. execute

**答案**：D。Registry 通过 `_FORBIDDEN_EXECUTION_METHODS = {"execute", "invoke", "run", "dispatch"}` 阻止任何执行方法。

---

**测试 3（多选）**：以下哪些是 BlueprintVersion 的设计约束？（选所有正确项）

A. 可以被人工编辑
B. 不可执行
C. 可以直接部署到 Runtime
D. 内容寻址（SHA-256 digest）
E. 必须指向起源 Candidate
F. 生命周期前向唯一

**答案**：B, D, E, F。A 错（不可变），C 错（不可直接部署，必须经 Build → SkillRelease）。

---

**测试 4（判断）**：BlueprintCandidate 被 Rejected 后，作者修改后可以用同一个 candidate_id 重新提交。

**答案**：错误。Rejected 是终态。修改后必须创建**新** Candidate（新 candidate_id）。旧 Rejected Candidate 保留为历史证据，不可复活。

---

**测试 5（简答）**：为什么 Admission 不检查业务正确性？如果 Admission 发现 Candidate 的 prompt 写得很差，应该怎么做？

**参考答案**：Admission 只负责结构、引用、Policy floor 的机器判定（ADR-005 D-2 §5.2.3）。业务正确性归 ReleaseEvaluation（Domain Model §7.12 SC-19）。如果 prompt 质量差：
1. Admission 会让它通过（结构没问题）
2. Source Review 的业务评审员可以提建议，但**不能阻塞** Promote
3. 真正的质量检查在 Release Gate 的 EvaluationSuite 中
4. 这样确保评审门槛可机械判定，不会因主观判断阻塞流程

---

## 16. 真实参考

| 参考 | 路径 | 用途 |
|---|---|---|
| ADR-005 D-2 BlueprintCandidate 评审流程 | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-005-Blueprint-artifact-chain-and-ApplicationContract.md` §5 | 评审两段式设计、物化规则、P-02 闭合 |
| ADR-005 §9 制品链权威边界 | 同上 §9 | 单一制品链总图 |
| Domain Model §7.3 SC-03 BlueprintVersion | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/v2-strategy/02-LangChat-v2-Target-Domain-Model.md` §7.3 | 目标态定义 |
| Charter §6.4 Single Artifact Chain | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/v2-strategy/01-LangChat-v2-Architecture-Charter.md` §6.4 | 制品链唯一性约束 |
| BlueprintVersion 代码 | `/root/langchat/apps/backend/langchat/blueprint/version.py` | 实际实现 |
| BlueprintCandidate 代码 | `/root/langchat/apps/backend/langchat/blueprint/candidate.py` | Candidate 实现 |
| Admission 代码 | `/root/langchat/apps/backend/langchat/blueprint/admission.py` | 准入检查实现 |
| Registry 代码 | `/root/langchat/apps/backend/langchat/blueprint/registry.py` | Registry 实现 |
| 不可变性测试 | `/root/langchat/apps/backend/tests/unit_tests/test_blueprint_version_immutability.py` | 测试覆盖 |
| Admission 测试 | `/root/langchat/apps/backend/tests/unit_tests/test_blueprint_candidate_admission.py` | 测试覆盖 |
| Build 拒绝 WorkflowSpec 测试 | `/root/langchat/apps/backend/tests/unit_tests/test_build_rejects_workflow_spec.py` | 制品链边界验证 |
