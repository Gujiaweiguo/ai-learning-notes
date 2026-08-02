# 🧱 LangChat 心智模型 | Week10-Day1
# 📌 Permission & Policy：谁允许谁做什么？

**日期**：2026-08-03（周一）
**本周主题**：Governance — 横切所有模块的约束
**今日核心**：为什么 Permission 不放 Runtime 里？

---

## ━━━ 1. 今日核心问题 ━━━

### 为什么 Permission 不放 Runtime 里？

你的 ERP 系统里，权限检查写在业务代码中间——点一个按钮，先查 `if user.hasPermission("contract:approve")`。天经地义，对吧？

LangChat 说：**Permission 检查不能在 Runtime 里做。** 权限策略是控制面的事，Runtime 只是执行面——它只能遵从策略，不能决定策略，更不能放宽策略。

这不是风格差异。这是**企业 AI 平台**和**传统业务系统**在架构理念上的根本分歧。

---

## ━━━ 2. 人话解释 ━━━

Jason，你在 MI 管过 ERP 升级。想想这个场景：

**传统做法（你熟悉的）**：
> 租赁经理想审批一份合同 → 登录 ERP → 系统在审批按钮的代码里查权限 → 有权限 → 放行。
>
> 权限规则在哪？散落在几十个 Controller、Service、存储过程里。换个角色定义，得改二十个地方。

**LangChat 做法**：
> 数字员工要执行 `lease.contract.approve` → 这份"权限规则"在它出生那天就冻结了（PolicyBundle）→ 执行时 Runtime 拿到的是一份不可修改的冰冻策略 → Runtime 照单执行，无权放宽。
>
> 权限规则在哪？在 Supply Chain 层打包进 SkillRelease，在 Runtime 层冻结进 FrozenExecutionContext。**不在业务代码里，不在运行时决策里。**

**为什么这样做？**

因为 AI 平台的执行环境比传统 ERP 危险得多。ERP 里人通过固定 UI 操作，AI 平台里 LLM 可以自由组合工具调用。如果权限检查放在 Runtime（LLM 可影响的层），一次 Prompt Injection 就可能绕过权限。

**权限必须在外面冻好，Runtime 只是一个听话的执行者。**

---

## ━━━ 3. LangChat 架构位置 ━━━

```
┌─────────────────────────────────────────────────────┐
│              Governance 横切平面                       │
│                                                       │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────┐ │
│  │ 身份与委托    │   │ 授权与策略     │   │ 审计与追踪  │ │
│  │ (Identity)  │   │ (Policy)     │   │ (Audit)   │ │
│  └──────┬──────┘   └──────┬───────┘   └─────┬─────┘ │
│         │                 │                  │       │
│         └─────────────────┼──────────────────┘       │
│                           │                           │
│                           ▼                           │
│              FrozenExecutionContext                    │
│         （冻结的身份 + 策略 + 制品 digest）              │
│                           │                           │
└───────────────────────────┼───────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │           Runtime Layer                       │
    │                                               │
    │   Runtime 只读策略 → 执行 → 审计               │
    │   不能修改策略，不能放宽策略                    │
    └───────────────────────────────────────────────┘
```

**Permission & Policy 在四层架构中的位置**：

| 层 | 角色 | 关键文件 |
|---|---|---|
| **Business Domain** | 定义 Policy（单条治理策略） | `Policy` 对象 |
| **Supply Chain** | 打包 PolicyBundle（不可变策略束） | `policy_bundle.py` |
| **Runtime** | 只读执行 — 从 FEC 中读策略，不修改 | `policy_bundle_runtime.py` |
| **Operations** | 控制面下达策略变更 | `dual-gate-authorization` spec |

**一句话**：Policy 从 Business Domain 定义 → Supply Chain 打包成 PolicyBundle → 冻结进 FEC → Runtime 只读执行。**策略的流动方向是单向的，从上到下，不可逆。**

---

## ━━━ 4. ADR 依据 ━━━

### Charter §7 Governance 横切（v2 战略文集 01）

> **授权与策略 | 四层 | 控制面下达，执行面只能遵从或收紧，不得放宽**

这是 Charter 级别的宪法约束。不是建议，是**宪法**。

### Charter §6.1 FrozenExecutionContext

FrozenExecutionContext 承载的内容包括：
- 身份与委托（继承 ADR-002 D1 profile）
- **授权与策略（`effect_policy`、调用链深度、scope）**
- 制品 digest 与版本
- Trace 与审计上下文

关键约束：**Frozen 后不可修改。Runtime 不得放宽 FEC 中的策略。**

### PolicyBundle 跨字段不变量（ADR-006 §4.4.6）

```python
# 宪法级约束：
effect_policy == "conditional_write"
    ⇒ review_gate_policy ∈ {"conditional", "mandatory"}

# 等价表述：不允许 (conditional_write, none) 组合
```

这意味着：**如果一个动作允许写操作，就必须有人审批。没有"可写但免审"的组合。** 这是代码级的硬约束，不是文档级的建议。

---

## ━━━ 5. 代码验证 ━━━

### 5.1 三层角色模型（`roles.py` + `permissions.py`）

```python
# roles.py — 三级角色
ROLE_PLATFORM_ADMIN = "platform_admin"  # 平台治理
ROLE_TENANT_ADMIN   = "tenant_admin"    # 租户治理
ROLE_MEMBER         = "member"          # 普通成员
ROLE_LEGACY_ADMIN   = "admin"           # 兼容映射 → platform_admin
```

```python
# permissions.py — 24个权限常量 + 角色权限映射
PERM_TENANT_MANAGE     # 管理租户
PERM_MODEL_GRANT       # 授予模型
PERM_WORKSPACE_MANAGE  # 管理工作空间
PERM_AUDIT_READ        # 读审计
# ... 共 24 个权限点

ROLE_PERMISSIONS = {
    "platform_admin": frozenset({全部 22 个权限}),
    "tenant_admin":   frozenset({16 个权限，不含 platform 级}),
    "member":         frozenset({7 个基础权限}),
}
```

**关键发现**：权限不是运行时动态计算的，是**静态映射表**。`platform_admin` 拥有的权限在代码里写得清清楚楚，没有一行是从数据库运行时查的。

### 5.2 PolicyBundle（`policy_bundle.py`）

```python
class PolicyBundle(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    effect_policy: EffectPolicy        # "read_only" | "conditional_write"
    review_gate_policy: ReviewGatePolicy  # "none" | "conditional" | "mandatory"

    @model_validator(mode="after")
    def _conditional_write_requires_review_gate(self) -> PolicyBundle:
        # 写操作必须有审批门 — 这是模型级硬约束
        if (self.effect_policy == "conditional_write"
            and self.review_gate_policy == "none"):
            raise ValueError(...)
        return self
```

**关键发现**：`frozen=True` + `extra="forbid"` + `strict=True` — Pydantic 模型在创建后不可修改、不接受多余字段、不做类型隐式转换。这是**代码级的不可变性保证**，不是文档约定。

### 5.3 运行时执行（`policy_bundle_runtime.py`）

```python
def enforce_policy_bundle_invariant(
    *, bundle: PolicyBundle, site: EnforcementSite, ...
) -> None:
    # 重新构造 PolicyBundle 做防御性验证
    PolicyBundle(**bundle.model_dump())  # 如果被篡改，这里会抛异常
    # 失败时：审计 + 抛异常。不自动修复，不覆盖，不默认填充。
```

**关键发现**：Runtime 不只是"读"策略，它**重新验证策略的完整性**。即使有人在 FEC 冻结后篡改了 PolicyBundle（理论上不可能），运行时也会通过重建模型捕获到。这是 defense-in-depth（纵深防御）。

### 5.4 Dual-Gate Authorization（`dual-gate-authorization` spec）

9 步算法的核心流程：

```
Step 0: FEC + action 分类（fail-closed）
Step 1: 已有授权重新验证（caller/delegation/workspace/scope）
Step 2: ResponsibilityBoundary cannot + whitelist 硬拒绝
Step 3: effect_policy 硬拒绝（write + read_only）
Step 4: 一次性计算 required_gate_reasons（escalation ∪ review_gate）
Step 5: 创建/获取 GateChallenge（幂等）
Step 6: Challenge 终态处理（pending/approved/rejected/expired）
Step 7: 冻结调用重放 + 签名验证（重跑 Step 0-4 用冻结上下文）
Step 8: CAS ActionInvocation ready→executing（只执行一次）
```

**关键发现**：Step 7 是最精妙的设计——审批通过后，不是直接执行，而是**用冻结的调用上下文重跑 Step 0-4**。这意味着即使审批者批准了 `amount=5000`，调用方在恢复时改成 `amount=100`，系统会用冻结的 `amount=5000` 做验证。**审批覆盖的是精确到字节级别的调用快照。**

---

## ━━━ 6. 商业地产映射 ━━━

| LangChat 概念 | MI CRE 场景 | 说明 |
|---|---|---|
| `platform_admin` | MI 集团 IT 总监 | 管所有 mall 的模型配置、全局策略 |
| `tenant_admin` | 单个 Mall 的运营经理 | 管自己 mall 的用户、知识库、API Key |
| `member` | Mall 前台客服 | 只能使用数字员工，不能管理 |
| `PolicyBundle(read_only)` | 查询类：租户名单查询 | 数字员工只能读，不能改 |
| `PolicyBundle(conditional_write, mandatory)` | 写入类：合同审批、租金调整 | 必须有人审才能执行 |
| `FrozenExecutionContext` | 每次合同审批的"审批单" | 冻结了谁审批、审批什么、什么版本的知识库 |
| Dual-Gate Step 7 | 审批后篡改合同金额 | 系统用冻结快照验证，篡改被拒绝 |
| `effect_policy: read_only` | 查询租户报表 | LLM 即使想写也写不了 |
| `review_gate: mandatory` | 租金调整超过 10% 必须商城总审批 | 不可跳过 |

**MI 场景**：假设 MI 的"合同审核数字员工"有 `contract.approve` 能力。

- 传统做法：ERP 在审批函数里查 `if user.role == "manager" and amount < 100000`
- LangChat 做法：PolicyBundle 定义 `effect_policy=conditional_write, review_gate=mandatory`，打包进 SkillRelease，冻结进 FEC。Runtime 执行到 `contract.approve` 时，从 FEC 读策略 → 发现有 review_gate → 创建 GateChallenge → 等人审 → 审批后用冻结上下文重验 → CAS 执行

**区别**：传统做法的权限可以被绕过（改代码、改数据库）。LangChat 的权限是**制品级保证**——策略被打包、被签名、被冻结，运行时无法绕过。

---

## ━━━ 7. 与传统方案比较 ━━━

| 维度 | 传统 ERP（RBAC in code） | LangChat（PolicyBundle in FEC） |
|---|---|---|
| **策略存储** | 散落在 Controller/Service/SP | 集中在 PolicyBundle 制品 |
| **策略变更** | 改代码、改配置、热更新 | 新建 PolicyBundle → 新 SkillRelease → 新 DeploymentRevision |
| **运行时权限** | 代码查数据库做判断 | 从冻结上下文只读 |
| **防篡改** | 靠代码规范 + DB 权限 | 靠 Pydantic frozen + digest-pin + 签名验证 |
| **审计** | 日志（可能被改） | 不可变审计事件（写入时即冻结） |
| **回滚** | 改回代码 | 部署旧 DeploymentRevision（策略完整恢复） |
| **多租户** | 每个租户写一套权限逻辑 | 同一套 PolicyBundle 模型，tenant scope 隔离 |
| **LLM 安全** | N/A（人不通过 LLM 操作） | Prompt Injection 无法影响冻结策略 |

**为什么选 LangChat 的方式？**

因为传统方式有三个致命问题在 AI 时代被放大：
1. **策略散落** → 改一个权限要改二十个地方，AI 组合调用时容易漏
2. **运行时可变** → 如果 LLM 能影响权限检查的上下文，就能提权
3. **不可审计** → 你不知道"那一刻"执行的是什么策略版本

LangChat 的答案：**策略是制品，不是代码。制品不可变，策略就不可篡改。**

---

## ━━━ 8. 架构师思考题 ━━━

**场景**：MI 集团要接入三个系统（SAP ERP、Oracle 财务、自研 CRM），每个系统的权限模型不同：
- SAP 用 role-based
- Oracle 用 responsibility-based
- CRM 用 ACL（Access Control List）

**问题**：
1. 在 LangChat 中，你设计几个 Capability？是一个 `erp.query` 还是三个 `sap.query` / `oracle.query` / `crm.query`？
2. PolicyBundle 的 `effect_policy` 怎么设？三个系统统一一个策略，还是每个系统一个？
3. 如果 SAP 的某些查询是只读的，但 Oracle 的同类查询需要审批（因为涉及财务数据），如何在 PolicyBundle 层表达？
4. 如果某个用户在 SAP 是 Manager 但在 Oracle 只是 Viewer，身份映射怎么做？这属于 Business Domain 层还是 Runtime 层？

**思考方向**：Capability 的粒度决定策略的精度。粒度太粗（一个 `erp.query` 管三个系统）→ 策略只能取最严格的；粒度太细（每个 API 一个 Capability）→ PolicyBundle 数量爆炸。架构师要在精确性和可维护性之间找平衡。

---

## ━━━ 9. 我的理解变化 ━━━

**以前以为**：权限就是 RBAC（Role-Based Access Control）——定义角色、分配权限、代码里做 `if user.hasPermission()`。

**现在知道**：在企业 AI 平台里，权限不是一个功能模块，而是**横切所有层的治理约束**。它有三个维度：

1. **静态维度**：角色权限映射（platform_admin / tenant_admin / member）— 这是传统的 RBAC
2. **制品维度**：PolicyBundle 是不可变制品，有构建时不变量（conditional_write 必须配 review_gate）
3. **执行维度**：Dual-Gate 9步算法 + 冻结重放验证 — 权限不是"检查一次就放行"，而是"审批后用冻结快照重新验证"

最关键的理解转变：**权限不是一个"检查"，是一个"制品链"。** 从 Policy 定义 → PolicyBundle 打包 → SkillRelease 包含 → DeploymentRevision digest-pin → FEC 冻结 → Runtime 只读 → Dual-Gate 验证。每一步都有不可变性保证。传统 RBAC 的"检查"只是这条链的最后一环。

---

## ━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题

**Audit & Trace：怎么知道发生了什么？**

为什么 Trace 不是日志？——日志是给人看的，Trace 是给系统看的。日志记录"发生了什么"，Trace 重建"为什么发生、在什么上下文发生、受什么策略约束"。

### Semantic Layer 定位

```
Ontology（存在论）
  └─ Domain Model（领域模型）
       └─ Capability（能力）← Policy 约束的对象
            └─ SkillRelease（技能发布）← PolicyBundle 打包在这里
                 └─ DeploymentRevision（部署闭包）← PolicyBundle 被 digest-pin
                      └─ FrozenExecutionContext（冻结上下文）← Policy 在此冻结
                           └─ Dual-Gate Authorization ← Policy 在此执行
```

今天的知识在这条链上的位置：**Policy → PolicyBundle → SkillRelease → DeploymentRevision → FEC → Dual-Gate**。

Policy 是 Business Domain 层的"单条规则"，PolicyBundle 是 Supply Chain 层的"不可变策略束"，Dual-Gate 是 Runtime 层的"执行时验证算法"。三层各管各的，不越界。
