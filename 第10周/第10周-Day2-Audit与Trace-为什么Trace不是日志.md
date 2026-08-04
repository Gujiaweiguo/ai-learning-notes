# 🧱 LangChat 心智模型 | Week10-Day2
## 📌 Audit & Trace：为什么 Trace 不是日志？

> 2026-08-04 周二 | Governance 周第2天
> 今日角色：Chief Architect Mentor

---

━━━ 1. 今日核心问题 ━━━

**为什么 Trace 不是日志（Log）？**

这个问题乍看很奇怪——开发写了这么多年日志，`logger.info()`、`console.log()`、`print()`，不都是在"记录发生了什么"吗？

但当你站在企业 AI 平台的视角，问题就不同了：

- **日志**是给**开发者排障**用的——"这段代码跑过了，没报错"
- **Trace**是给**系统理解**用的——"这次执行从哪开始、经过哪些节点、每一步花了多久、输入输出是什么、谁调用了谁"

一句话：**日志回答"发生了什么"，Trace 回答"为什么这样发生"。**

更深一层：**日志是线性的文本流，Trace 是结构化的因果树。**

Jason 你做 ERP 26 年，一定遇到过这种场景：用户说"系统慢了"，你翻日志翻到眼花，因为日志是按时间线铺开的，你不知道哪个 log 行属于哪个请求。Trace 解决的就是这个问题——它用 trace_id + span_id + parent_span_id 构建一棵**执行树**，任何一个慢节点都能精确定位。

---

━━━ 2. 人话解释 ━━━

**用 ERP 经验讲：Trace 就是"工单追溯链"。**

在 ERP 里，一张采购订单从请购→审批→下单→收货→入库→付款，每一步都有单据号、操作人、时间戳。如果出了问题，你可以沿单据号追回去。

LangChat 的 Trace 就是 AI 执行的"工单追溯链"：

```
用户问："退款政策是什么？"
│
├─ channel_dispatch span（微信消息进来）
│  ├─ rag_retrieval span（去知识库搜）
│  │  └─ rag_rerank span（重排序）
│  ├─ llm span（调大模型生成回答）
│  └─ adapter.send_reply span（回复用户）
│
trace_id = 整个请求的唯一追溯号
```

**日志写的是什么？** "2026-08-04 08:30:15 INFO dispatch.py:142 RAG search completed in 340ms"

**Trace 写的是什么？** 一棵树，你不仅能看到"RAG 搜了 340ms"，还能看到它在整个请求链路中的位置、它搜了什么、返回了什么、父节点是谁、子节点是谁。

**Audit 又是什么？** Audit 是"谁在什么时候对什么资源做了什么操作，结果如何"——它是**合规证据**，不是排障工具。Trace 是**系统可观测性**，Audit 是**治理证据链**。

---

━━━ 3. LangChat 架构位置 ━━━

在 ADR-007 三段式架构链中：

```
External Clients ───► Capability Runtime ───► Enterprise Systems
                            │
                     ┌──────┴───────┐
                     │ Observability │ ← Trace 在这里
                     │   子系统       │
                     └──────┬───────┘
                            │
                     ┌──────┴───────┐
                     │    Audit      │ ← Audit 在这里
                     │   (横切治理)   │
                     └──────────────┘
```

Trace 属于 **Operations Layer**（v2 Charter §5 四层架构的第四层）。它横切所有执行路径：
- Workflow Runtime 每次执行 → 发射 span 树
- Channel Dispatch 每次消息 → 发射 span 树
- SPA Chat 每次对话 → 发射 span 树
- RAG Retrieval 每次检索 → 发射子 span

Audit 属于 **Governance 横切平面**（v2 Charter §7）。它记录的是治理决策：
- SkillRelease 被调用了 → 审计六维上下文
- 用户登录/创建/删除 → 审计操作者与结果
- 配置变更 → 审计变更摘要

---

━━━ 4. ADR 依据 ━━━

### v2 Architecture Charter §5 Operations Layer

> Operations Layer 核心职责：提供部署操作、可观测性、审计与治理控制面。

### v2 Architecture Charter §6.1 FrozenExecutionContext

> FrozenExecutionContext 承载 Trace 与审计上下文（request_id、trace_id、租户、工作空间）。

这意味着：**每次执行都必须有一个 trace_id，它是 FrozenExecutionContext 的一部分**。不是可选的。

### OpenSpec: execution-trace

关键要求：
1. **Span 树数据模型**：`ExecutionSpan` 含 `{trace_id, span_id, parent_span_id, kind, name, started_at, ended_at, status, error, attributes}`
2. **SpanKind 枚举**：`workflow_run`, `workflow_node`, `rag_retrieval`, `rag_rerank`, `llm`, `channel_dispatch`, `adapter`, `kb_search`, `mcp_tool`, `capability_invoke`
3. **异步安全传播**：基于 `contextvars`，支持 `asyncio.create_task` 和 `asyncio.to_thread`
4. **全量输入输出存 side table**：`trace_payload` 存完整内容，span 行只存 256 字符预览
5. **run 级关联**：`WorkflowExecution.trace_id` 和 `channel_message_log.trace_id` 反向指向 span 树

### OpenSpec: skill-release-audit

关键要求：
1. **每次 SkillRelease 调用都必须产生审计记录**——包括成功(200)、拒绝(403)、待审批(202)、失败
2. **审计记录包含六维上下文**：client_id, actor_id, tenant_id, workspace_id, effective_scope, delegation_chain, skill_id, effect_policy, decision_result
3. **审计写入是 best-effort**：写失败不影响业务响应

---

━━━ 5. 代码验证 ━━━

### 5.1 Trace 数据模型（`observability/span.py`）

```python
class SpanKind(str, Enum):
    WORKFLOW_RUN = "workflow_run"
    WORKFLOW_NODE = "workflow_node"
    RAG_RETRIEVAL = "rag_retrieval"
    RAG_RERANK = "rag_rerank"
    LLM = "llm"
    CHANNEL_DISPATCH = "channel_dispatch"
    KB_SEARCH = "kb_search"
    MCP_TOOL = "mcp_tool"
    CAPABILITY_INVOKE = "capability_invoke"

@dataclass
class ExecutionSpan:
    trace_id: str           # 整棵树共享
    span_id: str            # 本节点唯一
    parent_span_id: str | None  # 父节点 → 构成树
    kind: SpanKind          # 节点类型
    name: str               # 人可读名称
    started_at: datetime
    ended_at: datetime | None
    status: SpanStatus      # ok / error / timeout
    attributes: dict        # 变量数据（tokens, scores, model name）
```

**关键发现**：`SpanKind` 有 10 种，覆盖了 LangChat 所有执行路径类型。这不是偶然——每种 SpanKind 对应一个发射点。

### 5.2 Span 持久化（`execution_span_model.py`）

```python
class ExecutionSpan(Base):
    __tablename__ = "execution_span"
    # 热列（可查询）
    trace_id = Column(String(36), index=True)
    span_id = Column(String(36), unique=True, index=True)
    parent_span_id = Column(String(36))
    kind = Column(String(40))
    status = Column(String(20))
    duration_ms = Column(Integer)
    attributes = Column(JSON)  # 变量字段
    preview = Column(Text)     # 256 字符预览
    
    __table_args__ = (
        Index("ix_execution_span_tenant_created", "tenant_id", "created_at"),
        Index("ix_execution_span_run", "run_kind", "run_id"),
        Index("ix_execution_span_kind_status", "kind", "status"),
    )
```

**关键发现**：三个复合索引精准覆盖了三种查询场景：
- `(tenant_id, created_at)` → 按租户按时间查
- `(run_kind, run_id)` → 按 execution 反查 span 树
- `(kind, status)` → "找出所有失败的 LLM 调用"

### 5.3 Audit 数据模型（`audit_model.py`）

```python
class AuditEventModel(Base):
    __tablename__ = "audit_event"
    actor_user_id = Column(Integer, index=True)
    actor_tenant_id = Column(Integer, index=True)
    action = Column(String(120), index=True)     # "skill_release:invoke"
    resource_type = Column(String(80))            # "skill_release"
    resource_id = Column(String(120))             # skill_id
    result = Column(String(20), index=True)       # succeeded/denied/pending_approval
    request_metadata_json = Column(Text)          # 六维上下文 JSON
    change_summary = Column(Text)
```

**关键发现**：Audit 和 Trace 是**完全不同的数据模型**：
- Trace 是**树结构**（parent_span_id 构成父子关系）
- Audit 是**扁平事件流**（每条独立，不构成树）
- Trace 存完整输入输出；Audit 只存治理决策摘要

### 5.4 SkillRelease 审计写入（`skill_release/audit.py`）

```python
def log_skill_release_invocation(db, six_dim_ctx, *, skill_id, 
                                   effect_policy, decision_result, ...):
    metadata = {
        "client_id": six_dim_ctx.client_id,
        "actor_id": six_dim_ctx.actor_id,
        "tenant_id": six_dim_ctx.tenant_id,
        "workspace_id": six_dim_ctx.workspace_id,
        "effective_scope": list(effective_scope),
        "delegation_chain": [...],
        "skill_id": skill_id,
        "decision_result": decision_result,  # succeeded/denied/pending_approval/failed
    }
    try:
        write_audit_event(db, ...)
    except Exception:
        logger.warning("skill_release audit write failed (best-effort)")
```

**关键发现**：审计写入用 try/except 包裹，失败只 warning 不阻断业务。这是"治理不阻断业务"的设计原则——审计是后置证据，不是前置门控（前置门控是 Permission/Policy 做的）。

---

━━━ 6. 商业地产映射 ━━━

| LangChat 概念 | MI CRE（商业地产）场景 | 说明 |
|---|---|---|
| **ExecutionSpan 树** | 购物中心巡检工单追溯链 | 从发现问题→派单→处理→验收→关闭，每步都有工单号和操作人 |
| **trace_id** | 工单总编号 | 一个工单从创建到关闭，所有操作共享同一编号 |
| **span_id + parent_span_id** | 工序关系 | "处理→维修→更换零件"是父子关系，不是平行日志行 |
| **SpanKind** | 工单类型枚举 | 巡检/维修/清洁/安保各有类别，方便分类统计 |
| **trace_payload** | 工单附件 | 完整的现场照片、处理记录，不是一行摘要 |
| **AuditEventModel** | 合规审计台账 | "谁授权了这笔维修费"、"谁审批了这个合同变更" |
| **best-effort 审计** | 财务记账不阻断业务 | 单据传票写失败不能阻止业务流程继续走 |
| **retention（30天）** | 监控录像保留周期 | 视频存7天自动覆盖；Trace 30天，语音7天，各有保留期 |

**MI CRE 具体场景**：
- 租户通过微信问"我的合同什么时候到期？" → Channel Dispatch 接收 → RAG 检索 → LLM 生成回答 → 全程被 Trace 覆盖
- 如果回答有误，你可以用 trace_id 找到：RAG 返回了什么、LLM 输入是什么、哪一步出了问题
- 如果租户投诉"系统泄露了我的合同信息"，Audit 记录可以证明：哪个 client_id 在什么时间用哪个 skill_id 访问了什么数据

---

━━━ 7. 与传统方案比较 ━━━

### Trace vs 传统日志

| 维度 | 传统日志（logger.info） | LangChat Trace（ExecutionSpan） |
|---|---|---|
| **结构** | 线性文本行 | 结构化树（parent-child） |
| **关联** | 靠 request_id 手动串联 | 自动通过 contextvars 传播 |
| **内容** | 开发决定写什么 | 执行路径自动覆盖（kind/status/duration/IO） |
| **查询** | grep / ELK 全文搜索 | SQL 查 span 树，按 kind/status/tenant 过滤 |
| **输入输出** | 通常不记录（太长） | trace_payload 存完整内容，span 只存预览 |
| **异步安全** | 需要手动管 context | contextvars 自动传播 |
| **适用场景** | 开发排障 | 系统理解 + 性能分析 + 回溯审计 |

### Audit vs Trace

| 维度 | Audit（审计） | Trace（追踪） |
|---|---|---|
| **目的** | 合规证据 | 系统可观测性 |
| **结构** | 扁平事件流 | 树结构 |
| **内容** | 谁对什么做了什么，结果如何 | 执行经过哪些节点，每步输入输出 |
| **消费者** | 审计员、合规官、安全团队 | 开发者、运维、架构师 |
| **保留期** | 长期（法规要求） | 30天（成本控制） |
| **失败策略** | best-effort（不阻断业务） | best-effort（emitter batch flush） |

### 为什么不把 Audit 和 Trace 合并？

因为它们回答不同的问题：
- Audit 回答：**"谁授权了？是否合规？"**
- Trace 回答：**"系统怎么执行的？哪里慢了？"**

合并会让审计员在一堆性能 span 里找合规证据，也会让开发在一堆审计事件里找性能瓶颈。**关注点分离是架构的核心原则。**

---

━━━ 8. 架构师思考题 ━━━

**问题：如果你的 AI 平台同时接入 5 个客户系统（SAP/Oracle/用友/金蝶/MI ERP），每次 SkillRelease 调用都跨越 3-4 个系统，你怎么设计 Trace 的跨系统传播？**

提示思考方向：
1. trace_id 怎么跨 HTTP 边界传播？（W3C Trace Context？自定义 Header？）
2. 如果 SAP 那边不给你 span 数据怎么办？（只有"出去"和"回来"两个时间戳）
3. Audit 和 Trace 在跨系统场景下，各自最需要记什么？
4. 如果一次执行跨 3 个租户（多租户 SaaS 场景），tenant_id 在 span 上怎么传递？

> 这不是考试题，是真实会遇到的架构决策。OpenTelemetry 的解决方案是 `traceparent` Header，但企业 AI 平台比微服务更复杂，因为有 LLM 调用这种"黑盒延迟"。

---

━━━ 9. 我的理解变化 ━━━

**以前以为**：日志和 Trace 差不多，都是"记录发生了什么"，写好 logger.info 就够了。

**现在知道**：
1. 日志是**开发工具**，Trace 是**架构设施**——Trace 不是"更好的日志"，而是**完全不同的数据结构**
2. Trace 的核心价值不是"记录"，而是**关联**——通过 parent-child 关系构建因果链
3. Trace 和 Audit 是**两个不同的东西**——Trace 服务于系统理解，Audit 服务于治理合规
4. Trace 的**异步安全传播**是硬核工程问题——`contextvars` + `asyncio.to_thread` + mutable holder 这种组合不是炫技，是真实需要的
5. `trace_payload` side table 的设计（热列 + 全量分离）是经典的**存储分层**——列表页只查热列，详情页才 join payload
6. 审计写入是 **best-effort**——这和 ERP 里"财务凭证写失败不阻断出库"的设计哲学完全一致

**最重要的认知变化**：Trace 不是运维工具，而是**架构的一部分**。它从设计阶段就要考虑——等系统跑起来再加 Trace，就像大楼建好了再加消防管道一样痛苦。

---

━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题：Approval（人审）—— 为什么 AI 不能全自动发布？

今天是 Trace（怎么知道发生了什么），明天是 Approval（怎么控制不该自动发生的事）。

- Trace 是**事后可观测**
- Approval 是**事前控制**
- 两者构成 Governance 的"前门 + 后窗"

### Semantic Layer 位置

```
Ontology（存在什么）
  └─ Domain Model（对象关系）
       └─ Capability（能做什么）
            └─ Skill（怎么调）
                 └─ SkillRelease（部署形态）
                      │
                      ├── 执行时 → Trace（ExecutionSpan 树）← 今天
                      ├── 调用时 → Audit（六维审计记录）← 今天
                      └── 敏感操作时 → Approval（人审门控）← 明天
```

Trace 和 Audit 都在 **Operations Layer**，横切所有执行路径。它们是 Governance 面板的"眼睛"——没有它们，你不知道系统在做什么；但只有眼睛还不够，你还需要"手"（Approval）来阻止不该做的事。

---

*📝 Week 10 Day 2 | 2026-08-04*
*Focus: Trace ≠ Log, Audit ≠ Trace, 两者都是 Governance 基础设施*
