# 🧱 LangChat 心智模型 | Week10-Day3
## 📌 Approval（人审）：为什么 AI 不能全自动发布？

---

━━━ 1. 今日核心问题 ━━━

### 为什么 AI 不能全自动发布？

更精确地问：**在一个企业 AI 平台里，"人审"（Human Approval / Human-in-the-Loop）应该放在哪里？是放成一个功能开关，还是放成一条不可绕过的治理链？**

这个问题之所以重要，是因为它直接决定了企业 AI 系统的信任边界。如果 AI 可以全自动发布技能、全自动执行写操作，那企业在审计时无法回答一个问题："谁批准了这个操作？"——不是 AI 自己，不是开发者，而是一个有权限、有责任的人类。

LangChat 的回答是：**人审不是一个开关，而是横跨制品链和运行时的治理约束。它在两个层面被强制执行：制品层（Release Gate 的 Approval 门控）和运行时层（HITL 审批门 + 状态机强制）。**

---

━━━ 2. 人话解释 ━━━

用 Jason 26 年 ERP 经验来讲：

在传统 ERP 里，审批流是这样的——采购订单提交 → 部门经理审批 → 财务总监审批 → 生效。审批是一个业务流程节点，串在工作流里。如果你有权限，你可以跳过某一级。审批是"流程配置"。

但在 AI 平台里，情况完全不同。AI 不像人类员工那样可预测——它可能因为 Prompt Injection 被诱导执行未授权操作，可能在幻觉中生成了一个看起来合理但实际错误的写操作。所以：

1. **制品层面**：一个 Skill（技能）从构建到发布，必须经过一道 Approval Gate——有人看了评估结果，签了字，这个技能才能上线。这不是"建议审核"，是"不审批就不能部署"的硬门控。就像 ERP 里的"凭证过账前必须有人复核签字"——只不过这里复核的是 AI 行为。

2. **运行时层面**：当一个 `conditional_write`（条件写）技能被调用时，执行会暂停在 `pending_human_review` 状态，等人类审批者用 review_token 来批准或拒绝。这就像 ERP 里的"大额付款需要双人复核"——只不过这里复核的是 AI 要做的写操作。

核心区别在于：传统 ERP 的审批是"流程节点"，可以被管理员配置跳过；LangChat 的审批是"治理约束"，由类型系统和状态机强制执行，不可配置跳过。

---

━━━ 3. LangChat 架构位置 ━━━

在 LangChat 的完整链路图上，Approval 出现在 **三个关键位置**：

```
用户意图 → ApplicationContract → Blueprint → Compiler → ExecutionPlan
                                                      ↓
                                              Runtime 执行
                                                      ↓
                                    ┌─────────────────┴──────────────────┐
                                    │                                    │
                              [执行时 HITL]                        [发布时 Gate]
                              pending_human_review              Release Gate §9
                              ↓ ↑                               ↓
                              GateChallenge                    Candidate → Evaluated
                              ↓ ↑                                    → Approved
                              ApprovalDecisionEvent                   → Signed
                              ↓ ↑                                    → Published
                              继续/拒绝                             DeploymentRevision
                                                                   ↓
                                                           [部署时审批]
                                                           approval_state='pending'
                                                           → 'approved'
                                                           → rolling restart
```

三道审批门：

| 门 | 位置 | 对象 | 强制机制 |
|---|---|---|---|
| **Release Gate** (制品层) | Supply Chain | SkillRelease Candidate | Gate 序列 monotonic，不通过不进入下一步 |
| **HITL Gate** (运行时层) | Runtime 执行 | CanonicalExecution | 六状态原子状态机，`pending_human_review` 不可跳过 |
| **DeploymentRevision Gate** (部署层) | Runtime 注册 | DeploymentRevision | 类型级边界：`ApprovedDeploymentRevision` 包装类 |

---

━━━ 4. ADR 依据 ━━━

### ADR-LC-011: DeploymentRevision Approval Gate

**核心决策**：引入两阶段审批生命周期：
1. **Register**：物化的 revision 写入 DB，`approval_state='pending'`，`is_active=False`，**不加载进内存注册表**
2. **Approve**：DB 行转为 `approval_state='approved''`，`is_active=True`，记录 `approved_by` + `approved_at`，需要 rolling restart 才能生效

**类型级边界**：内存注册表只存 `ApprovedDeploymentRevision`（frozen dataclass），不存裸 `DeploymentRevision`。传错类型直接 `TypeError`。这不是"约定"，是编译时检查。

**Pipeline 安全**：`register_revision_from_envelope` 从 DB 行实际状态派生 approval，不从请求参数 `auto_approve` 派生——防止"重新注册时自动批准"的绕过攻击。

### v2 Artifact Spec §9: Release Gate 序列

```
Candidate → Stored → Evaluated → Approved → Signed → Published
                                         ↑
                                    人审在这里
```

- Approval MUST 在 Evaluation 通过之后（先评估再审批）
- Detached Signature MUST 在 Approval 之后（先审批再签名）
- Publication 不重打包、不重算 digest（同一 digest 晋升到 Published namespace）
- **Approval 是治理决定，Signature 是密码学证明——两者分离**

### v2 Domain Model: SkillRelease 生命周期

`Candidate → Stored → Evaluated → Approved → Signed → Published → Active → Deprecated → Retired`

只有 Published/Active 具备生产部署资格。Candidate 不能被 TrafficPolicy 引用。

### Descriptor 级约束

`SkillReleaseDescriptor` 的 Pydantic 验证器强制：`effect_policy = "conditional_write"` 时，`human_review_gate` 必须为 `"conditional"` 或 `"required"`。这不是运行时检查，是模型验证——**技能定义时就锁定了必须人审**。

---

━━━ 5. 代码验证 ━━━

### ① 六状态原子状态机

```python
# state_machine.py
States: running, succeeded, failed, pending_human_review, rejected, expired

LEGAL_TRANSITIONS = {
    "pending_human_review": {"running", "rejected", "expired"},
    "running": {"succeeded", "failed", "pending_human_review", "rejected"},
}
# 所有终态（succeeded/failed/rejected/expired）无出边
# 任何非法转换 → 409 execution_state_conflict
```

关键：`pending_human_review` 是**一等公民状态**，不是"暂停标记"。进入此状态后，只有三种出路：approve→running，reject→rejected，timeout→expired。

### ② HITL 响应端点（RespondApproval）

```
POST /v1/skill-releases/{skill_id}/executions/{execution_id}/respond
```

严格验证顺序（6 步）：
1. Execution 存在 → 404
2. Status 必须是 `pending_human_review` → 409
3. `review_expires_at` 未过期 → 410
4. `review_token_hash` 匹配 → 401
5. Caller 是配置的 `review_assignee` → 403
6. 原子 CAS 更新 + 执行

### ③ Same-Transaction CAS（4 写原子）

```python
# same_transaction_cas.py
# 单 DB 事务内完成 4 个写操作：
1. SELECT FOR UPDATE GateChallenge; 验证 status=="pending"
2. SELECT FOR UPDATE CanonicalExecution; 验证 status=="pending_human_review"
3. 消费 review_token（hash 置空）
4. 签名 + INSERT ApprovalDecisionEvent
5. CAS GateChallenge pending → approved/rejected
6. CAS CanonicalExecution pending_human_review → running/rejected
```

两个并发 RespondApproval 会在 GateChallenge 的 `SELECT FOR UPDATE` 上串行化，失败方收到 `ChallengeAlreadyDecidedError`。

### ④ HITL 超时扫描器

独立 asyncio 后台任务，60 秒一轮：
- **Phase 1（SLA breach）**：升级到下一级审批人，或自动拒绝（`sla_timeout`）
- **Phase 2（Hard expiry）**：24h 安全网，强制过期

### ⑤ DeploymentRevision 审批

```python
# 类型级边界
class ApprovedDeploymentRevision:  # frozen dataclass
    revision: DeploymentRevision

def register_revision(rev: ApprovedDeploymentRevision):  # 只接受包装类型
    ...

# 生产代码路径必须显式构造包装类：
# register_revision_from_envelope → 验证 DB approval_state → ApprovedDeploymentRevision
# register_revision_unsafe → 仅供测试，MUST NOT 用于生产
```

---

━━━ 6. 商业地产映射 ━━━

| LangChat 概念 | MI CRE 场景 | 说明 |
|---|---|---|
| `human_review_gate: "required"` | 合同审批数字员工 | 租赁合同起草后必须由招商总监审批 |
| `effect_policy: "conditional_write"` | 租金调整技能 | 只能读取合同 → 条件写租金变更建议 → 人审后才执行 |
| `pending_human_review` 状态 | 合同变更等待审批 | 数字员工起草完变更单，停在等待状态 |
| `review_token` | 审批工单号 | 通过 token 找到待审批项，防篡改 |
| `ApprovalDecisionEvent` | 审批记录 | 谁批的、什么时候批的、批了什么——不可篡改 |
| SLA escalation | 超时升级 | 总监 4 小时不批 → 升级到 VP |
| DeploymentRevision approval | 技能版本上线审批 | 合同审批数字员工 v2 上线前需架构师审批 |
| Release Gate Approval attestation | 技能发布审批证书 | 正式的审批凭证，附在技能制品上 |

**MI 场景具体化**：

想象一个"租金调整建议"数字员工。它读取租户销售数据、合同条款、市场基准，生成租金调整建议——这是 `conditional_write`。它不能直接修改租金（那是 `read_only` 做不到的，也是 `conditional_write` 不被允许直接执行的）。它必须：

1. 生成建议草案（first_phase_output）
2. 停在 `pending_human_review`
3. 招商总监收到通知（通过 review_token）
4. 总监用 token 响应 approve/reject
5. 只有 approve 后，系统才执行实际租金变更

如果 24 小时没人批 → 自动过期，建议作废。如果总监 4 小时没响应 → 升级到 VP。

---

━━━ 7. 与传统方案比较 ━━━

### 比较 1：AI 全自动 vs. HITL（Human-in-the-Loop）

| 维度 | 全自动发布 | LangChat HITL |
|---|---|---|
| 速度 | 快 | 慢（多一道人审） |
| 安全 | 无法追溯责任 | 完整审计链 |
| 合规 | 不满足企业治理要求 | 满足"谁批准了什么"的审计要求 |
| Prompt Injection 风险 | 直接执行恶意操作 | 人审可以拦截异常行为 |
| 幻觉风险 | 错误写操作直接生效 | 人审可以发现不合理建议 |

### 比较 2：传统工作流审批 vs. LangChat Approval

| 维度 | 传统 ERP 审批 | LangChat Approval |
|---|---|---|
| 强制机制 | 流程配置（可跳过） | 状态机 + 类型系统（不可跳过） |
| 审批对象 | 业务数据（金额、订单） | AI 行为（技能执行、制品发布） |
| 并发控制 | 数据库锁 | SELECT FOR UPDATE + CAS + review_token |
| 超时处理 | 人工催办 | 自动升级 + 自动过期 |
| 证据 | 审批日志 | ApprovalDecisionEvent（签名、digest、不可篡改） |
| 可绕过 | 管理员可配置跳过 | `auto_approve` 仅限 dev/test，生产不可用 |

### 比较 3：Approval 放 Build vs. 放 Release Gate vs. 放 Runtime

| 放在哪 | 问题 |
|---|---|
| Build 阶段 | Build 不签发 approval。Build 只负责打包，不负责治理决策。（Spec §7） |
| Release Gate | ✅ 正确位置。Approval 是 Supply Chain governance 的决策 |
| Runtime | Runtime 只读 approval 状态，不做 approval 决策。Runtime 是执行者不是决策者 |

**LangChat 的选择**：Approval 在 Release Gate 做决策（制品级），在 Runtime 做执行级 HITL（运行时级）。两层独立，各管各的。

---

━━━ 8. 架构师思考题 ━━━

### 思考题 1（CTO 级）

如果 MI 的合同审批数字员工需要支持"三级审批"（招商经理 → 招商总监 → 财务VP），当前 LangChat 的 HITL 架构能否支持？需要改什么？

**提示**：看 SLA escalation 的 `escalate_or_reject` 逻辑——它目前是"升级到下一级或自动拒绝"。三级审批需要的是"逐级审批"而不是"升级"。这是一个 escalation chain vs. approval chain 的区别。

### 思考题 2

如果一个 SkillRelease 通过了 Release Gate 的 Approval（制品级审批），但在运行时触发了 HITL（运行时级审批），这两个审批的关系是什么？是同一个审批人在批吗？如果不是，出了问题谁负责？

**提示**：Release Gate 的 Approval 是"这个技能可以上线了"，审批主体是 Supply Chain governance。Runtime HITL 的审批是"这次具体执行可以继续"，审批人是 `review_assignee`。这是两个不同的治理决策，可能不是同一个人。

### 思考题 3

`ApprovedDeploymentRevision` 用类型系统（frozen dataclass）来强制审批。但 Python 的类型检查不是强制的（mypy 是可选的）。这个"类型级边界"在实际中有多少保护力？如果有人写出 `register_revision_unsafe()` 的调用，怎么防？

---

━━━ 9. 我的理解变化 ━━━

**以前以为**：人审就是一个审批按钮——AI 生成建议，人点"通过"，就这么简单。

**现在知道**：LangChat 的人审是一个**三层治理结构**：

1. **制品层**（Release Gate）：技能发布前，必须有人审批"这个技能可以上线"——产生 Approval attestation，作为制品的 detached referrer，digest-pin 到技能制品上。不审批 → 不发布 → 不可部署。

2. **运行时层**（HITL Gate）：技能执行中，`conditional_write` 操作触发 `pending_human_review` 状态暂停——不是"暂停按钮"，是**状态机的强制转换**。只有合法的 `respond` 调用（6 步验证）才能恢复执行。

3. **部署层**（DeploymentRevision approval）：物化的 revision 写入 DB 后默认 `pending`，必须显式 `approve` 才能 `is_active=True`。内存注册表用类型系统（`ApprovedDeploymentRevision`）做不可绕过的边界。

**更深的认知**：Approval 和 Signature 的分离是精妙的设计。Approval 是治理决定（人决定的），Signature 是密码学证明（机器验证的）。把两者混在一起就失去了"谁批准"和"是否被篡改"的独立验证能力。这就像 ERP 里"审批签字"和"印章验证"的区别——签字是授权意图，印章是防伪验证。

---

━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题：PII & Compliance —— 敏感数据怎么管？

今天学了 Approval（人审），明天进入 PII 治理。两者的连接点：

- Approval 解决的是"谁批准了操作"
- PII 治理解决的是"操作中涉及的敏感数据怎么处理"
- 两者都是 Governance 的横切关注点——不是某个模块的功能，而是贯穿所有模块的约束

### Semantic Layer 位置

```
Ontology（什么是"审批"）
    ↓
Domain Model（SkillRelease / GateChallenge / ApprovalDecisionEvent）
    ↓
Capability（approve_execution / register_revision / respond_approval）
    ↓
Skill（conditional_write 技能必须配 human_review_gate）
```

今天的知识在这条链上的位置：**Domain Model → Capability** 之间。Approval 不是一个独立的能力——它是一个横切约束，通过 Descriptor 验证器（制品定义时）、Release Gate（制品发布时）、状态机（运行时执行时）、类型系统（部署注册时）四个层面共同实现。

---

📌 **Engineering Journal 条目同步追加到 engineering-journal.md**
