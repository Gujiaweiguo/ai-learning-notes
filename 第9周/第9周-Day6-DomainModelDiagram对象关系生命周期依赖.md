# 🧱 LangChat 心智模型 | Week9-Day6

## ⚡ 动手交付：Domain Model Diagram — 对象关系、生命周期、依赖

> **📌 今日核心问题：哪个对象最可能被合并？哪个最可能被拆分？**
>
> **日期**：2026-08-01（周六）
>
> **本周主题**：Domain Deep Dive — 拆对象，理解为什么存在、边界在哪
>
> **今日交付物**：一张完整的 Domain Model 关系图 + 生命周期图 + 合并/拆分分析

---

## 目录

1. [今日核心问题](#1-今日核心问题)
2. [人话解释](#2-人话解释)
3. [LangChat 架构位置](#3-langchat-架构位置)
4. [ADR 依据](#4-adr-依据)
5. [代码验证](#5-代码验证)
6. [商业地产映射](#6-商业地产映射)
7. [与传统方案比较](#7-与传统方案比较)
8. [架构师思考题](#8-架构师思考题)
9. [我的理解变化](#9-我的理解变化)
10. [明日连接](#10-明日连接--semantic-layer)

---

## 1. 今日核心问题

### 哪个对象最可能被合并？哪个最可能被拆分？

这是架构师的核心判断力。不是"对象越多越好"，也不是"对象越少越好"。而是：

> **每个对象必须能回答一个问题——"如果把它合并到另一个对象里，会失去什么？如果拆不出来，会造成什么耦合？"**

Week 9 我们逐个拆了 5 个对象（BlueprintVersion、SkillRelease、Deployment/Revision、ReleaseChannel/TrafficPolicy、DigitalEmployeeDefinition）。今天把它们放在一起，看整体拓扑。

---

## 2. 人话解释

用 Jason 26 年 ERP 经验来讲。

你做 MI 的 17 个 Bounded Context 的时候，一定纠结过：**"客户主数据和租户主数据能不能合并？"** "合同上下文和租赁上下文边界到底在哪？"

Domain Model Diagram 就是你当年画 Context Map 的升级版——不仅画"谁跟谁有关系"，还要画：

- **引用方向**（谁引用谁，单向还是双向）
- **生命周期**（谁先出生，谁先死，谁依赖谁的存活）
- **不变量约束**（合并后哪些不变量会破裂）

一张好的 Domain Model Diagram 能让你在 3 分钟内回答任何"这个对象放这里合不合适"的问题。

---

## 3. LangChat 架构位置

### 3.1 四层架构全图

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        LangChat v2 四层架构                                ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  ┌─── Business Domain Layer ──────────────────────────────────────┐     ║
║  │                                                               │     ║
║  │  ┌──────────────────────┐    ┌──────────────────────────┐     │     ║
║  │  │ DigitalEmployee       │    │ ApplicationContract       │     │     ║
║  │  │ Definition (BD-01)    │───▶│ / ContractVersion         │     │     ║
║  │  │ "数字员工 HR 档案"     │ 引用│ (BD-02 / BD-03)          │     │     ║
║  │  └──────┬───────────────┘    │ "业务接口契约"             │     │     ║
║  │         │                    └──────────────────────────┘     │     ║
║  │         │ 引用(BlueprintVersion digest)                         │     ║
║  │         │                    ┌──────────────────────────┐     │     ║
║  │         │                    │ Capability (SC-07)        │     │     ║
║  │         │                    │ "原子能力定义"             │     │     ║
║  │         │                    └─────────────┬────────────┘     │     ║
║  │         │                                  │ 发布              │     ║
║  │         │                    ┌─────────────▼────────────┐     │     ║
║  │         │                    │ KnowledgeCollection       │     │     ║
║  │         │                    │ (SC-09) "知识集合(可变)"   │     │     ║
║  │         │                    └─────────────┬────────────┘     │     ║
║  │         │                                  │ 快照              │     ║
║  │         │                    ┌─────────────▼────────────┐     │     ║
║  │         │                    │ Policy (SC-11)            │     │     ║
║  │         │                    │ "单条治理策略"             │     │     ║
║  │         │                    └──────────────────────────┘     │     ║
║  └─────────┼───────────────────────────────────────────────────┘     ║
║            │                                                           ║
║  ┌─────────▼─── Supply Chain Layer ────────────────────────────┐     ║
║  │                                                             │     ║
║  │  ┌────────────────┐    评审    ┌──────────────────┐        │     ║
║  │  │ Blueprint       │ ────────▶ │ BlueprintVersion  │        │     ║
║  │  │ Candidate       │  升级     │ (SC-03)           │        │     ║
║  │  │ (SC-02)         │           │ "canonical 源制品"│        │     ║
║  │  │ "草案"          │  ←拒绝    │  不可变+digest    │        │     ║
║  │  └────────────────┘           └────────┬─────────┘        │     ║
║  │                                         │ Build输入          │     ║
║  │  ┌──────────────────────────────────────▼──────────────┐   │     ║
║  │  │  Build/BuildRun (SC-04/05)                           │   │     ║
║  │  │  "确定性编译：Blueprint → ExecutionPlanIR"            │   │     ║
║  │  └──────────────────────────────┬──────────────────────┘   │     ║
║  │                                 │ 产出                       │     ║
║  │  ┌──────────────────────────────▼──────────────────────┐   │     ║
║  │  │  ExecutionPlanIR (SC-06)                             │   │     ║
║  │  │  "内部中间表示，不可编辑"                              │   │     ║
║  │  └──────────────────────────────┬──────────────────────┘   │     ║
║  │                                 │ 打包+依赖锁                 │     ║
║  │  ┌──────────────────────────────▼──────────────────────┐   │     ║
║  │  │  SkillRelease v2 (SC-13)                             │   │     ║
║  │  │  "唯一可部署 OCI 制品"                                │   │     ║
║  │  │  含: IR + CapabilityRelease + KnowledgeSnapshot      │   │     ║
║  │  │      + PolicyBundle + prompt/model artifacts          │   │     ║
║  │  └──────┬───────────────────────────────────┬───────────┘   │     ║
║  │         │                                   │               │     ║
║  │  ┌──────▼──────────┐              ┌────────▼────────────┐   │     ║
║  │  │ ReleaseChannel   │              │ CapabilityRelease    │   │     ║
║  │  │ (SC-14)          │              │ (SC-08)              │   │     ║
║  │  │ "晋升指针"        │              │ "能力不可变版本"      │   │     ║
║  │  └──────┬──────────┘              └─────────────────────┘   │     ║
║  │         │ 产出 PromotionEvent (SC-15)                        │     ║
║  │         │                                                   │     ║
║  │  ┌──────▼──────────────────────────────────────────────┐    │     ║
║  │  │  KnowledgeSnapshot (SC-10) / PolicyBundle (SC-12)    │    │     ║
║  │  │  "不可变知识快照" / "不可变策略束"                      │    │     ║
║  │  └─────────────────────────────────────────────────────┘    │     ║
║  │                                                             │     ║
║  │  ┌──────────────────────────────────────────────────────┐    │     ║
║  │  │  ReleaseEvaluation (SC-19) ← EvaluationSuite (SC-18) │    │     ║
║  │  │  "制品级评估"                                          │    │     ║
║  │  └─────────────────────────────────────────────────────┘    │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║            │                                                           ║
║  ┌─────────▼─── Runtime Layer ────────────────────────────────┐     ║
║  │                                                             │     ║
║  │  ┌────────────────────┐                                     │     ║
║  │  │ Deployment (RT-01)  │──── 持有 ────┐                     │     ║
║  │  │ "部署聚合生命周期"   │              │                     │     ║
║  │  └────────────────────┘              │                     │     ║
║  │                                       ▼                     │     ║
║  │  ┌──────────────────────────────────────────────────┐      │     ║
║  │  │  DeploymentRevision (RT-02)                       │      │     ║
║  │  │  "完整运行时闭包 = digest-pin 一切"                 │      │     ║
║  │  │                                                   │      │     ║
║  │  │  闭包内容:                                         │      │     ║
║  │  │  ├── SkillRelease digest                          │      │     ║
║  │  │  ├── ApplicationContractVersion digest            │      │     ║
║  │  │  ├── KnowledgeSnapshot digest                     │      │     ║
║  │  │  ├── CapabilityRelease digest                     │      │     ║
║  │  │  ├── PolicyBundle digest                          │      │     ║
║  │  │  ├── Compatibility Matrix                         │      │     ║
║  │  │  ├── binding_manifest_digest                      │      │     ║
║  │  │  └── environment/scope                            │      │     ║
║  │  └──────────────────────┬───────────────────────────┘      │     ║
║  │                          │ 路由                              │     ║
║  │  ┌──────────────────────▼───────────────────────────┐      │     ║
║  │  │  TrafficPolicy                                    │      │     ║
║  │  │  (RT-03) "流量策略 → 指向具体 Revision"            │      │     ║
║  │  └──────────────────────┬───────────────────────────┘      │     ║
║  │                          │ 执行                              │     ║
║  │  ┌──────────────────────▼───────────────────────────┐      │     ║
║  │  │  FrozenExecutionContext (RT-04)                   │      │     ║
║  │  │  "不可变执行上下文：身份+授权+策略+digest+trace"     │      │     ║
║  │  └──────────────────────┬───────────────────────────┘      │     ║
║  │                          │                                   │     ║
║  │  ┌──────────────────────▼───────────────────────────┐      │     ║
║  │  │  RuntimeABI → Execution → Session/State/Memory    │      │     ║
║  │  │  (RT-05~09) "运行时执行实例"                        │      │     ║
║  │  └──────────────────────────────────────────────────┘      │     ║
║  │                                                             │     ║
║  │  ┌──────────────────────────────────────────────────┐      │     ║
║  │  │  DeploymentEvaluation (RT-06)                     │      │     ║
║  │  │  "部署级评估（对比 ReleaseEvaluation）"              │      │     ║
║  │  └──────────────────────────────────────────────────┘      │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                                                                      ║
║  ┌──── Operations Layer ─────────────────────────────────────┐      ║
║  │                                                           │      ║
║  │  Registry (SC-16)    Catalog Projection (SC-17)           │      ║
║  │  "按主题事实源"        "只读投影，不是事实源"                 │      ║
║  │                                                           │      ║
║  │  Governance 横切: Attestation / Provenance / Signature    │      ║
║  └───────────────────────────────────────────────────────────┘      ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 3.2 制品链流向（单向，不可逆）

```
External Authoring Client
        │
        ▼
BlueprintCandidate ──(评审)──▶ BlueprintVersion
        │  草案，可改                    │  canonical，不可变
        │                                │
        │                                ▼
        │                    Build/BuildRun ──(确定性编译)
        │                                │
        │                                ▼
        │                    ExecutionPlanIR
        │                    (内部中间表示)
        │                                │
        │                                ▼
        │                    SkillRelease v2 ──(Release Gate)
        │                    ★ 唯一可部署制品    │
        │                                │     │ 评估
        │                                │     ▼
        │                                │  ReleaseEvaluation
        │                                │
        │                    ┌───────────┘
        │                    │
        │                    ▼  (晋升)
        │              ReleaseChannel ──▶ PromotionEvent
        │                    │
        │                    ▼  (物化)
        │              DeploymentRevision ◄── 闭包digest-pin
        │                    │
        │                    ▼  (路由)
        │              TrafficPolicy
        │                    │
        │                    ▼  (执行)
        │              FrozenExecutionContext
        │                    │
        │                    ▼
        └────────────▶ Execution（运行时执行）
```

**关键约束**：箭头方向严格单向。任何反向操作（如从 Execution 修改 Blueprint）都被禁止。

---

## 4. ADR 依据

### 4.1 四层归属硬约束（Charter §5 + Domain Model §3）

| 对象 | 层归属 | 能否跨层？ | 理由 |
|---|---|---|---|
| DigitalEmployeeDefinition | Business Domain | ❌ | 只持有引用，不持有内容 |
| ApplicationContract | Business Domain | ❌ | 传输无关的业务契约 |
| BlueprintVersion | Supply Chain | ❌ | canonical 源制品 |
| SkillRelease | Supply Chain | ❌ | 唯一可部署制品 |
| DeploymentRevision | Runtime | ❌ | 运行时闭包 |
| TrafficPolicy | Runtime | ❌ | 只指向 Revision |
| ReleaseChannel | **Supply Chain（严格）** | ❌ | 不在运行时路径 |
| Registry | 按主题归属 | 每实例只归一层 | 不跨层 |

### 4.2 对象分离的硬约束

| 两个对象 | 能否合并？ | ADR 依据 |
|---|---|---|
| SkillRelease ↔ DeploymentRevision | ❌ 绝不可 | Charter §6.4: "同一对象不跨层归属" |
| ReleaseChannel ↔ TrafficPolicy | ❌ 绝不可 | Channel 属 Supply Chain，TrafficPolicy 属 Runtime |
| BlueprintVersion ↔ ExecutionPlanIR | ❌ 绝不可 | 源制品 ≠ 中间表示 |
| DigitalEmployeeDefinition ↔ Deployment | ❌ 绝不可 | 定义层 ≠ 运行层 |
| ReleaseEvaluation ↔ DeploymentEvaluation | ❌ 不可 | Domain Model §10.3: 评估对象不同 |
| Capability ↔ CapabilityRelease | ⚠️ 有条件可合并 | 但会失去发布版本化 |
| KnowledgeCollection ↔ KnowledgeSnapshot | ⚠️ 有条件可合并 | 但会失去快照不可变性 |
| Policy ↔ PolicyBundle | ⚠️ 有条件可合并 | 但会失去打包发布能力 |

### 4.3 合并与拆分的判定原则（从 ADR-003 提炼）

ADR-003 的正交 facet 模型给出了一个通用判定框架：

> **如果两个对象的演化节奏不同、生命周期不同、变更 Owner 不同，它们就不应该合并。**

用这个框架检验：

| 对象对 | 演化节奏 | 生命周期 | 变更 Owner | 合并？ |
|---|---|---|---|---|
| Capability / CapabilityRelease | Capability 慢(语义)，Release 快(版本) | Capability: Draft→Retired, Release: 创建即冻结 | Cap: 平台团队, Release: 发布管道 | ⚠️ 可合并（如果团队小） |
| Collection / Snapshot | Collection 可变(频繁更新)，Snapshot 不可变(创建即冻结) | 完全不同 | Col: 业务团队, Snap: 构建管道 | ⚠️ 可合并（代价是丢失不可变性） |
| Policy / PolicyBundle | Policy 单条演化，Bundle 批量打包 | 完全不同 | Policy: 合规团队, Bundle: 发布管道 | ⚠️ 可合并（代价是丢失批量管理） |

---

## 5. 代码验证

### 5.1 当前代码中的对象实现

```
代码文件 → Domain Model 对象映射

/root/langchat/apps/backend/langchat/
├── blueprint/
│   ├── candidate.py          → BlueprintCandidate (SC-02)  ✅ 已实现
│   ├── version.py            → BlueprintVersion (SC-03)    ✅ 已实现
│   ├── admission.py          → Admission 评审               ✅ 已实现
│   └── registry.py           → BlueprintRegistry (SC-16)   ✅ 已实现
├── release/
│   ├── builder.py            → Build/BuildRun (SC-04/05)   🟡 部分(stub)
│   └── pipeline.py           → Release Pipeline            🟡 部分
├── skill_release/
│   ├── descriptor.py         → SkillRelease Descriptor     🟡 v1非v2
│   ├── registry.py           → SkillRelease Registry       ✅ v1版
│   ├── canonical/            → canonical wire (ADR-003)    ✅ 已实现
│   │   ├── invoke.py
│   │   ├── execution_service.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── gate/                 → Release Gate                🟡 部分
│   ├── authorization/        → 授权步骤(Step0-8)           ✅ 已实现
│   ├── bindings/             → W01-W09 能力绑定             ✅ 已实现
│   └── executors/            → 各能力执行器                 ✅ 已实现
├── (无 deployment/ 目录)      → Deployment (RT-01)          ❌ 不存在
├── (无 deployment_revision/)  → DeploymentRevision (RT-02)  ❌ 不存在
├── (无 traffic_policy/)       → TrafficPolicy (RT-03)       ❌ 不存在
├── (无 frozen_execution/)     → FrozenExecutionContext      ❌ 不存在
└── observability/             → Observability 横切          ✅ 已实现
```

### 5.2 关键结构验证

**已实现对象**（Blueprint 层）：

```python
# version.py
@dataclass(frozen=True)
class BlueprintVersion:  # SC-03 ✅
    blueprint_id: str
    version: str
    content_digest: str  # SHA-256
    state: str = "active"
    # 生命周期: active → deprecated → retired（前向唯一）

# candidate.py
@dataclass
class BlueprintCandidate:  # SC-02 ✅
    candidate_id: str
    # 生命周期: Draft → In Review → Promoted | Rejected
```

**v1 对象**（SkillRelease v1，非目标态 v2）：

```python
# descriptor.py — 当前是 v1 tag-based，不是 v2 OCI 制品
class SkillReleaseDescriptor:  # SC-13 v1 🟡
    skill_id: str
    version_tag: str  # 不是 content-addressed digest
    # 缺少: ExecutionPlanIR、依赖锁、OCI manifest
```

**缺失对象**（Runtime 层全部缺失）：

```python
# ❌ Deployment (RT-01) — 不存在
# ❌ DeploymentRevision (RT-02) — 不存在
# ❌ TrafficPolicy (RT-03) — 不存在
# ❌ FrozenExecutionContext (RT-04) — 不存在
# ❌ ReleaseChannel (SC-14) — 不存在
# ❌ ReleaseEvaluation (SC-19) — 不存在
```

### 5.3 代码 vs 目标态覆盖度

```
覆盖度统计：

Business Domain Layer:  ████░░░░░░  40%
  ✅ DigitalEmployeeModel (v1版，需升级)
  ✅ ApplicationContract (散落在代码中)
  ❌ ApplicationContractVersion (不存在)
  ✅ Capability (bindings/ 体系)
  ✅ KnowledgeCollection (server/knowledge_base/)
  ❌ Policy (散落在各处，无统一模型)

Supply Chain Layer:     ██████░░░░  60%
  ✅ BlueprintCandidate + Admission + Review
  ✅ BlueprintVersion (最成熟)
  🟡 Build/BuildRun (stub)
  🟡 ExecutionPlanIR (概念存在)
  🟡 SkillRelease (v1非v2)
  ❌ CapabilityRelease (不存在)
  ❌ KnowledgeSnapshot (不存在)
  ❌ PolicyBundle (不存在)
  ❌ ReleaseChannel (不存在)
  ❌ ReleaseEvaluation (不存在)

Runtime Layer:           █░░░░░░░░░  10%
  ❌ Deployment (不存在)
  ❌ DeploymentRevision (不存在)
  ❌ TrafficPolicy (不存在)
  ❌ FrozenExecutionContext (不存在)
  🟡 RuntimeABI (散落在 canonical/ 中)
  ✅ Execution/Session (v1版，直接跑)

Operations Layer:       ███░░░░░░░  30%
  ✅ BlueprintRegistry
  ✅ SkillReleaseRegistry
  ✅ Observability (span/trace/emitter)
  ❌ Catalog Projection (不存在)
  🟡 Attestation/Provenance (概念散落)
```

---

## 6. 商业地产映射

### MI CRE 场景：10 个 Mall 的合同审核数字员工

```
                    MI 集团数字员工体系

┌─────────────────────────────────────────────────────┐
│  定义层（DigitalEmployeeDefinition）                  │
│                                                     │
│  "合同审核数字员工 - 小合"                              │
│  definition_version: v1.0                           │
│  引用: ApplicationContractVersion "lease.query@v2"   │
│  引用: BlueprintVersion "contract-review@v1.3"       │
│  scope: [shanghai-mall, beijing-mall, ...10个]      │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 上海 Mall    │ │ 北京 Mall    │ │ 广州 Mall    │
│ Deployment-A │ │ Deployment-B │ │ Deployment-C │
│              │ │              │ │              │
│ Revision-r1  │ │ Revision-r1  │ │ Revision-r2  │
│ (v1.3+沪法规模)│ │ (v1.3+京法规模)│ │ (v1.3+粤法规模)│
│              │ │              │ │              │
│ TrafficPolicy│ │ TrafficPolicy│ │ TrafficPolicy│
│ 100%→r1     │ │ 100%→r1     │ │ 100%→r2     │
│              │ │              │ │              │
│ kill_switch  │ │ kill_switch  │ │ kill_switch  │
│ = false      │ │ = true(暂停) │ │ = false      │
└─────────────┘ └─────────────┘ └─────────────┘
```

**关键观察**：同一个 DigitalEmployeeDefinition 衍生出 10 个独立 Deployment。每个 Deployment 有自己的 Revision（不同的知识快照）、自己的 TrafficPolicy（不同的灰度策略）、自己的 kill_switch（独立的紧急停止）。

**如果合并 Definition 和 Deployment**（错误做法）：
- 10 个 Mall 变成 1 个，无法独立管理
- 上海暂停 = 全部暂停
- 广州更新知识库 = 全部变更
- 无法独立灰度

**这正是定义层与运行层必须分离的业务理由。**

---

## 7. 与传统方案比较

### 传统单体 vs LangChat 多对象治理链

| 维度 | 传统 ERP 单体 | Dify/LangChain | LangChat v2 |
|---|---|---|---|
| 对象数量 | 少（一张配置表搞定） | 中（App + Model + Prompt） | 多（35+ 聚合对象） |
| 关系复杂度 | 低（扁平 CRUD） | 中（App 引用 Model） | 高（四层引用链） |
| 版本管理 | 靠 git/数据库审计 | 靠 git | 靠 digest + 版本内建 |
| 回滚能力 | 覆盖旧文件 | git revert | 前向回滚（新 Revision 指旧 digest） |
| 多环境部署 | 多套配置文件 | 多个 App 实例 | Deployment + scope 独立管理 |
| 灰度发布 | 不支持 | 不原生支持 | TrafficPolicy 内建 |
| 审计追踪 | 散落在日志 | 靠 git log | PromotionEvent + Attestation |
| 学习曲线 | 低 | 中 | 高（但一次学会终身受用） |

### 为什么 LangChat 选了最复杂的路？

**因为 LangChat 面向的是企业级生产环境，不是个人工具。**

- 个人工具可以牺牲治理换易用性（Dify 模式）
- 企业工具必须牺牲易用性换治理（LangChat 模式）
- 35 个对象看起来多，但每个对象只做一件事。传统单体看起来简单，但每个对象的职责被塞进了一张表

### Dify 的对象模型 vs LangChat 的对象模型

```
Dify（≈ 5 个对象）:
  App → Model Config → Prompt Template → Dataset → Workflow

LangChat（35+ 个对象，按四层组织）:
  Business Domain:  DED + ACV + Capability + Collection + Policy
  Supply Chain:     Candidate → Version → Build → IR → SkillRelease
                   + Channel + Evaluation + Registry + Catalog
  Runtime:          Deployment → Revision → TrafficPolicy
                   → FrozenExecContext → RuntimeABI → Execution
  Operations:       Governance + Observability + Audit
```

Dify 的 5 个对象 = LangChat 的 35 个对象的"压缩版"。但压缩的代价是：Dify 的 App 同时承担了定义、制品、部署三重角色，无法独立演化。

---

## 8. 架构师思考题

### 思考题：合并/拆分推演

**场景 A：如果团队只有 3 个人，是否应该合并对象？**

| 候选合并 | 理由 | 风险 | 建议 |
|---|---|---|---|
| Capability + CapabilityRelease | 小团队不需要独立的发布版本 | 失去版本化，能力变更无法追踪 | ⚠️ 可合并（短期），但留拆分接口 |
| KnowledgeCollection + KnowledgeSnapshot | 小团队的知识库更新不频繁 | 失去快照不可变性 | ❌ 不建议（知识更新时运行时必须有快照） |
| Policy + PolicyBundle | 小团队策略不多 | 失去批量管理 | ⚠️ 可合并（短期） |
| Deployment + DeploymentRevision | 简化部署流程 | 失去多 Revision 共存能力 | ❌ 不建议（灰度需要多 Revision） |
| BlueprintVersion + ExecutionPlanIR | 减少中间环节 | 失去确定性构建保证 | ❌ 绝不建议（违反 HC-3） |

**场景 B：如果 LangChat 未来要支持"多模型供应商"（OpenAI/Claude/Gemini），哪些对象需要拆分？**

提示：答案藏在 SkillRelease 的依赖锁里。当前 SkillRelease digest-pin 了 model provider，如果要多模型，要么 SkillRelease 拆分为 "逻辑制品 + 模型绑定"，要么 DeploymentRevision 增加模型维度。

**场景 C：如果未来出现"Serverless 数字员工"（按需启动，不持续运行），Deployment 对象还需要吗？**

提示：Deployment 的生命周期是 Draft→Active→Suspended→Retired。Serverless 场景下，"Active" 的定义可能改变——不再是"持续运行"，而是"可被触发"。DeploymentRevision 作为闭包仍然需要，但 Deployment 的生命周期语义可能需要演化。

---

## 9. 我的理解变化

### 以前以为 → 现在知道

| 以前以为 | 现在知道 |
|---|---|
| Domain Model 就是 ER 图 + 类图 | Domain Model 是**治理拓扑图**——不仅画数据关系，还画生命周期、不变量、层归属、禁止职责 |
| 对象越多 = 越复杂 = 越不好 | 对象多≠复杂。每个对象只做一件事，边界清晰，反而**降低了整体认知复杂度**。35 个对象各司其职，比 5 个对象什么都塞要好 |
| 合并对象 = 简化系统 | 合并对象 = **增加耦合**。短期看似简化，长期变成巨石。关键是判断"演化节奏是否一致" |
| Build 和 BuildRun 是冗余的 | Build = 构建定义（可复用），BuildRun = 一次执行（有具体环境、时间、Operator）。分离使得"同一份定义跑多次"成为可能，CI/CD 基础 |
| ReleaseChannel 和 TrafficPolicy 做的是同一件事 | 完全不同！Channel = "哪个版本是正式版"（Supply Chain 决策），TrafficPolicy = "生产实际在跑哪个版本"（Runtime 决策）。解耦使得"晋升了但还没全量"成为可能 |
| Diagram 就是文档 | Diagram 是**架构决策的推演工具**。画图的过程就是验证"这个对象能不能独立存在"的过程 |

### Week 9 整体认知收获

经过 Day1-Day5 的逐个对象拆解 + Day6 的整体关系图，我现在能回答：

1. **BlueprintVersion 为什么是制品不是配置？** → 不可变性 + 内容寻址 + 评审门 = 审计/回滚/合规的基础
2. **SkillRelease 为什么是唯一可部署单元？** → 它是 Supply Chain 的终点，Runtime 的入口，唯一跨层桥梁
3. **Deployment 为什么独立于 Release？** → 制品（通用、可移植）vs 部署（绑定环境、有状态）是两个生命周期
4. **为什么需要灰度？** → 风险控制：ReleaseChannel（晋升）和 TrafficPolicy（切流）解耦
5. **数字员工为什么不拥有 Runtime？** → 定义层只持有引用，运行层独立管理执行。多环境、多版本、独立灰度

---

## 10. 明日连接 + Semantic Layer

### 明天（周日）：🔄 Virtual CTO Review

明天是 Week 9 的 Virtual CTO Review：
- 本周理解进度评分（1-10）
- 五维评分（Architecture Quality / Code Health / ADR Consistency / Technical Debt / Developer Experience）
- **ADR Health Check**：8 个 ADR 有没有过时或需要拆分的？
- 下周建议

### Semantic Layer 定位

今天画的 Domain Model Diagram 在 Ontology → Domain Model → Capability → Skill 链上的位置：

```
Ontology（本体论：什么是企业 AI 应用）
    ↓
Domain Model（★ 今天：35 个对象的拓扑关系图）
    ↓
    ├── 理解了四层归属（Business / Supply Chain / Runtime / Operations）
    ├── 理解了单向制品链（Candidate → Version → Build → IR → SkillRelease → Revision）
    ├── 理解了层间硬约束（SkillRelease ≠ DeploymentRevision）
    └── 理解了合并/拆分判定（演化节奏 + 生命周期 + Owner 一致性）
    ↓
Capability（下周：Governance 横切关注点）
    ↓
Skill（最终：可治理的企业 AI 能力）
```

### Week 9 交付物清单

| 交付物 | 状态 | 路径 |
|---|---|---|
| BlueprintVersion 深度分析 | ✅ | 第9周-Day1 |
| SkillRelease 深度分析 | ✅ | 第9周-Day2 |
| Deployment/Revision 深度分析 | ✅ | 第9周-Day3 |
| ReleaseChannel/TrafficPolicy 深度分析 | ✅ | 第9周-Day4 |
| DigitalEmployeeDefinition 深度分析 | ✅ | 第9周-Day5 |
| **Domain Model Diagram（本文件）** | ✅ | **第9周-Day6** |
| Virtual CTO Review + ADR Health Check | 📅 明天 | 第9周-Day7 |

---

### 附录：对象完整清单（35 个）

| 编号 | 对象 | 层 | 一句话 |
|---|---|---|---|
| BD-01 | DigitalEmployeeDefinition | Business | 数字员工语义锚点 |
| BD-02 | ApplicationContract | Business | 业务 API 契约 |
| BD-03 | ApplicationContractVersion | Business | 契约不可变版本 |
| SC-01 | Artifact | Supply Chain | 不可变制品基类 |
| SC-02 | BlueprintCandidate | Supply Chain | 候选源制品（草案） |
| SC-03 | BlueprintVersion | Supply Chain | canonical 源制品 |
| SC-04 | Build | Supply Chain | 构建定义 |
| SC-05 | BuildRun | Supply Chain | 一次构建执行 |
| SC-06 | ExecutionPlanIR | Supply Chain | 内部中间表示 |
| SC-07 | Capability | Business/跨层 | 原子能力定义 |
| SC-08 | CapabilityRelease | Supply Chain | 能力不可变版本 |
| SC-09 | KnowledgeCollection | Business | 知识逻辑集合（可变） |
| SC-10 | KnowledgeSnapshot | Supply Chain | 知识不可变快照 |
| SC-11 | Policy | Business/跨层 | 单条治理策略 |
| SC-12 | PolicyBundle | Supply Chain | 不可变策略束 |
| SC-13 | SkillRelease v2 | Supply Chain | 唯一可部署 OCI 制品 |
| SC-14 | ReleaseChannel | Supply Chain | 晋升指针 |
| SC-15 | PromotionEvent | Supply Chain | 晋升审计事件 |
| SC-16 | Registry | Operations/SC | 按主题事实源 |
| SC-17 | Catalog Projection | Operations | 只读投影 |
| SC-18 | EvaluationSuite | Supply Chain | 评估套件定义 |
| SC-19 | ReleaseEvaluation | Supply Chain | 制品级评估 |
| RT-01 | Deployment | Runtime | 部署聚合生命周期 |
| RT-02 | DeploymentRevision | Runtime | 完整运行时闭包 |
| RT-03 | TrafficPolicy | Runtime | 流量策略 |
| RT-04 | FrozenExecutionContext | Runtime | 不可变执行上下文 |
| RT-05 | RuntimeABI | Runtime | Runtime-制品接口契约 |
| RT-06 | Execution | Runtime | 一次执行实例 |
| RT-07 | Session | Runtime | 持续交互上下文 |
| RT-08 | State | Runtime | 受治理状态对象 |
| RT-09 | Memory | Runtime | 受治理记忆对象 |
| RT-10 | DeploymentEvaluation | Runtime/Ops | 部署级评估 |
| GX-01 | Attestation | Governance | 已签发声明 |
| GX-02 | Provenance | Governance | 构建链路证据 |
| GX-03 | Signature | Governance | 密码学签名 |
