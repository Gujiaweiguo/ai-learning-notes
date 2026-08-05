# 🧱 LangChat 心智模型 | Week10-Day4

📅 2026-08-06（周四）
📌 Fail-closed vs Fail-open + Approval（人审）

---

## ━━━ 1. 今日核心问题 ━━━

**为什么不 fallback？**

更精确地问：LangChat 在哪些地方选择"宁可不工作也不降级安全"，在哪些地方选择"降级但保留风险标记"？这条线画在哪里，为什么？

传统 ERP 系统的设计哲学是"尽量不崩"——连接失败就重试，权限不够就找管理员覆盖。LangChat 反过来：安全检查不过就 raise，Prompt hash 不匹配就拒绝执行，v2 路径未实现就返回 503。为什么？

---

## ━━━ 2. 人话解释 ━━━

Jason，你在 ERP 行业 26 年，一定遇到过这种场景：

财务模块连接不上数据库，系统选择"用上次缓存的数据继续跑"，结果月底结账数字全错。这就是 **fail-open**——出问题时系统继续工作，但工作在一个不安全的状态上。

LangChat 选择 **fail-closed**，用你熟悉的 ERP 术语说就是：

> **权限检查不通过 = 单据挂起，不是"先放行后补审"**
> **数据完整性校验失败 = 拒绝过账，不是"先记账后核对"**

但 LangChat 不傻——它不是所有地方都 fail-closed。关键洞察是 **分层**：

| 层次 | 失败策略 | ERP 类比 |
|---|---|---|
| 安全边界（认证/授权/hash/审批） | **Fail-closed：拒绝执行** | 没审批的单据不能过账 |
| 执行路径（LLM/KB/工作流） | **优雅降级：返回兜底结果 + 风险标记** | 暂存单 + 标记"需人工复核" |
| 兜底结果中的敏感输入 | **风险保留：human_review_required=True** | 系统算不了，但标记"这个客户可能有问题" |

用一句话讲：**安全问题绝不妥协，执行问题优雅降级，但风险信息不丢失。**

---

## ━━━ 3. LangChat 架构位置 ━━━

在四层架构中，fail-closed 不是某一个模块的功能，而是 **横切所有层的约束**（和 Governance 一样）：

```
Business Domain Layer
  └─ ApplicationContract 声明 human_review_gate: required
       ↓ fail-closed: 不声明就不发布

Supply Chain Layer
  └─ Release Gate approval attestation
       ↓ fail-closed: 不审批就不能晋升
  └─ DeploymentRevision register → approve 两阶段
       ↓ fail-closed: ApprovedDeploymentRevision 类型边界

Runtime Layer
  └─ FrozenExecutionContext 不可变
       ↓ fail-closed: 策略只能遵从或收紧，不能放宽
  └─ Prompt hash 验证
       ↓ fail-closed: hash 不匹配 → raise PromptHashMismatch
  └─ v2 FEC 快照验证
       ↓ fail-closed: 缺快照 → raise MissingSnapshotError
  └─ Capability Gateway scope 校验
       ↓ fail-closed: scope 违规 → raise GatewayError

Operations Layer
  └─ HITL Gate (conditional_write)
       ↓ fail-closed: 未审批的 side effect = 0
  └─ Channel 适配器凭证校验
       ↓ fail-closed: 空 token → verify_request 返回 False
```

---

## ━━━ 4. ADR 依据 ━━━

### 4.1 Charter §6.1 — FrozenExecutionContext 宪法原则

> "Runtime 不得放宽 FrozenExecutionContext 中的策略。"

这不是建议，是宪法（AI Native Principles）。意味着：Runtime 拿到的策略是冻结好的，只能执行或报错，不能"灵活处理"。

### 4.2 Charter §7 — Governance 横切

> "控制面下达，执行面只能遵从或收紧，不得放宽。"

这句话定义了 fail-closed 的方向：收紧 ✅，放宽 ❌。

### 4.3 ADR-LC-011 — DeploymentRevision Approval Gate

两个关键设计：

1. **两阶段生命周期**：`register`（pending, is_active=False）→ `approve`（approved, is_active=True）
   - register 之后 revision **不在运行时注册表里**
   - approve 之后需要 **rolling restart** 才生效（不热加载）

2. **类型级边界**：`ApprovedDeploymentRevision`（frozen dataclass）
   - `register_revision()` 只接受 `ApprovedDeploymentRevision`，传 bare `DeploymentRevision` 抛 `TypeError`
   - 生产代码路径必须显式构造 wrapper（编码了 DB 验证后的审批状态）

3. **从 DB 行派生 approval**：不信任请求参数 `auto_approve`，从 DB 行实际状态读取
   - 防止"重新注册时 auto_approve=True 绕过审批"

### 4.4 Prompt Runtime errors.py — 防存在性探测

> "所有跨租户/跨工作空间的匹配失败，都坍缩为对外不可区分的 `PromptNotFound`"

这是 fail-closed 的信息安全维度：不仅拒绝执行，还**不告诉你为什么拒绝**（防止信息泄漏）。

---

## ━━━ 5. 代码验证 ━━━

### 5.1 Canonical Runtime 的"分层降级"策略

`canonical_entry.py` 的 `execute()` 函数是最佳示例：

```python
# v2 路径 — 硬拒绝（fail-closed）
def _execute_v2(...):
    raise V2ExecutionUnavailableError(
        "v2 runtime execution is unavailable: immutable FEC v2 snapshots "
        "are not yet materialized..."
    )
    # ↑ 不用 placeholder 数据假装能跑

# v1 路径 — 执行失败时优雅降级
def _execute_v1(...):
    try:
        return _run_workflow(...)
    except Exception:
        return _fallback_result(
            ...,
            reason="workflow_error",
            sensitive_keywords=binding.sensitive_keywords,
        )
        # ↑ 返回兜底结果，但保留敏感关键词检测
```

`_fallback_result()` 的精妙设计：

```python
def _fallback_result(...):
    is_sensitive = bool(sensitive_keywords) and any(
        kw in message.lower() for kw in sensitive_keywords
    )
    # 如果输入涉及敏感关键词，即使系统失败了，也标记 human_review_required=True
    return ExecutionResult(
        output={
            "summary": "Sensitive inquiry — human review required." if is_sensitive else ...,
            "human_review_required": is_sensitive,  # ← 风险保留
            "risk_flags": ["sensitive_topic"] if is_sensitive else [],
        }
    )
```

**关键理解：execute() MUST NEVER raise to the caller。** 但这不是 fail-open！这是 API 契约设计——Execution 失败不是异常，是结果。风险通过 `human_review_required` 和 `risk_flags` 保留。

### 5.2 Prompt Runtime — 纯 fail-closed

`resolver.py` 的 `resolve_prompt_template_version()`：

```
explicit_version is None → raise PromptRetiredWithoutExplicitVersion
  ↓ (进入 DB 查询)
template/version 不存在 → raise PromptNotFound
  ↓ (查到了)
content_hash != expected_hash → raise PromptHashMismatch
  ↓ (匹配)
返回 frozen ResolvedPromptTemplateVersion
```

**没有 fallback 路径。** 唯一的出路是成功或异常。

### 5.3 Capability Gateway — fail-closed scope 执行

`lnkchatbi.py` adapter 注释：

```python
# All failure paths fail closed — no fallback to arbitrary SQL
# or unscoped queries.
```

Scope 违规、认证失败、超时 → 全部 raise `GatewayError`。

### 5.4 HITL HumanApprovalNode — 默认不自动批准

`spec.py` 的 `HumanApprovalNode`：

```python
timeout_seconds: int = 86400          # 24 小时
auto_approve_on_timeout: bool = False  # ← 默认 False！
```

超时**不会**自动批准。超时 = 保持 pending = 需要人工处理。

### 5.5 Multi-Approver HITL — 三种审批策略

`canonical_review_vote_repository.py` 的 `_evaluate_threshold()`：

| 策略 | 批准条件 | 拒绝条件 |
|---|---|---|
| `single` | 1 票批准 | 1 票拒绝 |
| `majority` | >50% 批准 | 无法达到批准阈值 |
| `unanimous` | 全票批准 | 1 票拒绝即否决 |

关键设计：**unanimous 模式下 1 票 reject 立即否决**（不是等所有人投完）。这是 fail-closed 在投票策略上的体现——宁可多等，不可错放。

---

## ━━━ 6. 商业地产映射 ━━━

LangChat → MI CRE（商业地产）场景：

| LangChat 概念 | MI CRE 场景 | Fail-closed 含义 |
|---|---|---|
| DeploymentRevision Approval | 数字员工技能上线审批 | 合同审核技能上线前必须法务审批 |
| HumanApprovalNode | conditional_write 技能执行暂停 | 租金调整建议必须人工确认后才写入 ERP |
| auto_approve_on_timeout=False | 超时未审批 | 超时 = 挂起，不是"默认通过" |
| Prompt hash mismatch | Prompt 被篡改 | 拒绝执行，不用"可能是对的"继续跑 |
| Capability scope 校验 | 数字员工只能查授权范围的数据 | 跨商场数据访问 = GatewayError |
| _fallback_result + sensitive_flag | 系统故障但识别到敏感关键词 | 租金变更/解约关键词 → 标记需人工复核 |

**MI 场景的具体例子：**

数字员工"租金对账助手"执行时 LLM 服务挂了：
- ❌ Fail-open 做法：用上次结果回答 → 可能给出过时数字 → 租户投诉
- ❌ 直接报错做法：用户看到 500 错误 → 不知道怎么办
- ✅ LangChat 做法：返回兜底结果"系统暂时无法完成对账"，但如果输入包含"退款/解约/减免"等敏感词，`human_review_required=True`，自动进入人工队列

---

## ━━━ 7. 与传统方案比较 ━━━

### 7.1 Plugin 系统的 fail-open 问题

传统 Plugin 系统（如 Dify、FastGPT）的设计：
- Plugin 加载失败 → 跳过，继续执行
- 工具调用超时 → 返回空结果
- 权限校验失败 → 降级为只读模式

问题：用户**不知道**系统降级了。AI 用不完整的数据生成回答，用户以为是完整的。

LangChat 的做法：
- Capability scope 违规 → **GatewayError，不返回任何数据**
- Prompt 被修改 → **hash 校验失败，拒绝执行**
- 技能未审批 → **不在注册表里，不会被路由到**

### 7.2 传统 ERP 审批 vs LangChat HITL

| 维度 | 传统 ERP | LangChat |
|---|---|---|
| 审批位置 | 业务流程中（可有可无） | 类型系统 + 运行时双重强制 |
| 可跳过？ | 管理员可配置跳过 | `ApprovedDeploymentRevision` 类型不可绕过 |
| 审批粒度 | 按单据类型 | 按制品（Release）+ 按执行（HITL Gate）+ 按部署（Revision） |
| 超时处理 | 通常自动通过或转交上级 | 默认保持 pending（`auto_approve_on_timeout=False`） |
| 多人审批 | 通常一人或串签 | single/majority/unanimous 策略可配 |
| 防重放 | 单据号唯一约束 | atomic SELECT FOR UPDATE + token 消费 |

### 7.3 为什么不 fallback？

核心论点：**AI 系统的 fallback 比 crash 更危险。**

传统系统 fallback 到缓存数据，用户知道"这是旧数据"。AI 系统 fallback 到不完整上下文，AI 会**自信地生成错误回答**，用户分不清"完整分析"和"降级分析"。所以 LangChat 选择：

- 安全边界 → 绝不 fallback（raise）
- 执行路径 → fallback 但**标记**（human_review_required + risk_flags）

---

## ━━━ 8. 架构师思考题 ━━━

**CTO 级问题（不是考试题）：**

假设 MI 部署了 LangChat，接入了 SAP（ERP）、Salesforce（CRM）、自建 BI 三个系统的 Capability。某天 Salesforce 的 Connector 网络超时：

1. 数字员工正在执行"租户画像分析"，需要同时读 SAP 的合同数据和 Salesforce 的互动数据。应该 fail-closed（全部拒绝）还是部分降级？
2. 如果选择降级，用户（商场运营经理）怎么知道"这次分析缺了 CRM 数据"？
3. 如果数字员工在 `effect_policy=conditional_write` 模式下运行，fallback 结果应该自动触发人审吗？
4. 你作为架构师，会把"Connector 超时阈值"和"fail-closed vs fallback"的决策权放在哪里？平台层固定、租户配置、还是按技能声明？

> 提示：思考这个问题时，记住 `_fallback_result` 的设计——它不只是"降级"，而是"降级 + 风险标记"。

---

## ━━━ 9. 我的理解变化 ━━━

**以前以为：** Fail-closed 就是"出错就报错"，fail-open 就是"出错就跳过"。很简单。

**现在知道：** Fail-closed 不是一种策略，是 **一整套分层设计哲学**，包含四个层次：

1. **安全边界层**（认证/授权/hash/scope）= 绝对 fail-closed，raise 异常
2. **制品治理层**（审批/类型边界/状态机）= 结构性 fail-closed，不可绕过
3. **执行层**（LLM/KB/工作流）= 优雅降级，返回兜底结果
4. **风险保留层**（兜底结果中的敏感检测）= 即使降级也不丢失风险信号

以前以为 `execute() MUST NEVER raise` 是 fail-open。现在知道这是 **API 契约设计**——执行失败是结果不是异常。真正的 fail-open 是"权限校验失败就跳过权限校验"，而 LangChat 从来不做这种事。

另一个认知转变：以前觉得 `auto_approve_on_timeout=False` 是默认配置，改成 True 就行。现在知道 **默认值就是架构决策**——24 小时超时不自动批准，意味着系统宁可"卡住"也不"默认放行"。在传统 ERP 里，审批超时自动转交或自动通过是常见的；在 AI 平台里，这是不可接受的，因为 AI 生成的建议可能看起来合理但实际有害。

---

## ━━━ 10. 明日连接 + Semantic Layer ━━━

**明日主题：** Realization Rollback + FrozenExecutionContext — 编译产物回滚机制 + 身份委托传递

今天理解了 fail-closed 的分层设计，明天看一个具体场景：**当 fail-closed 触发后（比如审批被拒绝、hash 不匹配），系统怎么回滚到之前的安全状态？** FrozenExecutionContext 在回滚时怎么处理？身份委托链（D1 profile）在回滚后还有效吗？

**Semantic Layer 位置：**

```
Ontology → Domain Model → Capability → Skill
                              ↑
                         今天的位置
                         
Fail-closed 是 Capability 和 Skill 执行时的安全保障机制。
它不生产新的 Domain对象，但它约束了现有对象的行为边界：
  - SkillRelease 的 effect_policy 决定了 fail-closed 的层次
  - DeploymentRevision 的 approval_state 决定了 fail-closed 的部署边界
  - FrozenExecutionContext 的不可变性决定了 fail-closed 的运行时边界
```

---
