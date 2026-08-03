# 🧱 LangChat 心智模型 | Week10-Day2
# 📌 Audit & Trace：怎么知道发生了什么？

**日期**：2026-08-04（周二）
**本周主题**：Governance — 横切所有模块的约束
**今日核心**：为什么 Trace 不是日志？

---

## ━━━ 1. 今日核心问题 ━━━

### 为什么 Trace 不是日志？

你在 ERP 系统里查问题，第一件事是看日志。`tail -f`、`grep ERROR`，日志就是一切。

LangChat 说：**Trace 不是日志。日志是给人看的文本，Trace 是给系统查询的结构化执行证据。**

这个区别不是咬文嚼字。它决定了你能不能回答一个企业 AI 系统最致命的问题：*"这次 AI 回答，到底经过了哪些步骤、调了什么模型、检索了什么数据、花了多少 token、为什么出错？"*

用日志，你永远拼不出来。用 Trace，一条查询就能还原完整执行树。

---

## ━━━ 2. 人话解释 ━━━

Jason，你在 MI 管 ERP 时一定遇到过这个场景：

**传统排障（你熟悉的）**：
> 财务说"合同审批流程卡住了" → 你打开日志服务器 → grep 合同编号 → 找到 3 条日志记录 → 但中间调了什么服务、哪一步超时、谁触发的，全靠猜。

**为什么传统日志不够用？**
- 日志是线性文本流，不是结构化数据
- 日志分散在不同服务器、不同服务里
- 日志没有因果关系——你不知道哪条触发了哪条
- 日志没有统一 ID 把一次完整业务流串起来

**LangChat 的 Trace 怎么做？**
> 一次用户提问进来 → 系统生成唯一 `trace_id` → 从"收到请求"到"返回回答"，每一个步骤都是一个 **Span**（跨度），它们共享同一个 `trace_id`，通过 `parent_span_id` 形成树状结构。

```
trace_id: abc-123
├─ channel_dispatch (root, 1250ms)
│  ├─ adapter: wechat.verify (5ms)
│  ├─ idempotency: check (2ms)
│  ├─ context: resolve (15ms)
│  ├─ rag_retrieval (320ms)
│  │  └─ rag_rerank (80ms)
│  ├─ llm (850ms)
│  └─ adapter: wechat.send_reply (8ms)
```

这就是一棵 **Span Tree**。每个 Span 有：开始时间、结束时间、状态（ok/error）、耗时、自定义属性（token 数、模型名、检索分数）。整棵树存进数据库，可以查询、可以聚合、可以可视化。

**用 26 年 ERP 经验类比**：Trace 之于 AI 系统，就像**工单追踪**之于 ERP——工单上每一步都有时间戳、操作人、状态、结果。你不能靠日志查工单执行情况，你需要一个结构化的工单追踪表。Trace 就是 AI 系统的工单追踪。

---

## ━━━ 3. LangChat 架构位置 ━━━

在 Week 8 走过的完整链路图中，Trace 横跨**每一站**：

```
用户意图 → ApplicationContract → Blueprint → Compiler → ExecutionPlan
    → Runtime → Capability + Connector → Enterprise System
         ↑
     每一步都被 Trace 覆盖
```

具体位置：
- **入口层**：`channel_dispatch` Span 记录外部渠道（微信/飞书/钉钉）的完整处理
- **编排层**：`workflow_run` Span 记录整个工作流执行，`workflow_node` 记录每个节点
- **能力层**：`capability_invoke` Span 记录每次能力调用
- **模型层**：`llm` Span 记录每次 LLM 调用（模型名、token 数、耗时）
- **知识层**：`rag_retrieval` + `rag_rerank` + `kb_search` Span 记录 RAG 全链路
- **工具层**：`mcp_tool` Span 记录 MCP 工具调用

**关键洞察**：Trace 不是某个模块的功能，它是**横切所有模块的基础设施**。就像你在 ERP 里的审计日志——不是某个业务模块的附属功能，而是整个系统的合规骨架。

---

## ━━━ 4. ADR 依据 ━━━

### v2 Architecture Charter（01 文档）

Charter §审计与可观测性 层（第四层）明确：
> "Trace 与审计上下文（request_id、trace_id、租户、工作空间）跨层一致；Dev Console Timeline 只读。"

### v2 Artifact & Execution Specification（03 文档）§14

FrozenExecutionContext 必须承载 **Trace 与审计** 字段：
- `request_id` — 请求唯一标识
- `trace_id` — 本次执行的 Trace 根 ID
- `parent_trace_id` — 跨执行 Trace 关联
- `session_id`（可选）— 会话标识

§14.2 Audit Fields 进一步定义：
- `frozen_context_id` — 上下文唯一标识
- `frozen_at` — UTC 构造时间戳
- `constructed_by` — 构造主体
- `subject_closure_digest` — 制品闭包摘要
- `policy_floor_digest` — 策略包摘要
- `context_integrity_proof`（可选）— 完整性校验

**设计原则**：FrozenExecutionContext 冻结的不只是身份和策略，还包括 Trace 上下文。这意味着：**你可以在任何时候，通过 trace_id 回溯一次执行的完整证据链——谁触发的、用了什么策略、执行了什么、结果是什么。**

### Skill Release Audit Spec

每次 SkillRelease 调用产生六维审计记录：
`client_id` / `actor_id` / `tenant_id` / `workspace_id` / `effective_scope` / `delegation_chain`

决策结果四态：`denied` / `succeeded` / `pending_approval` / `failed`

---

## ━━━ 5. 代码验证 ━━━

### 核心数据结构：ExecutionSpan

```python
# /root/langchat/apps/backend/langchat/observability/span.py

class SpanKind(str, Enum):
    WORKFLOW_RUN = "workflow_run"
    WORKFLOW_NODE = "workflow_node"
    RAG_RETRIEVAL = "rag_retrieval"
    RAG_RERANK = "rag_rerank"
    LLM = "llm"
    CHANNEL_DISPATCH = "channel_dispatch"
    ADAPTER = "adapter"
    KB_SEARCH = "kb_search"
    MCP_TOOL = "mcp_tool"
    CAPABILITY_INVOKE = "capability_invoke"

class SpanStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class ExecutionSpan:
    trace_id: str          # 整棵树共享
    span_id: str           # 本节点唯一
    parent_span_id: str    # 树结构关键
    kind: SpanKind         # 什么类型的操作
    name: str              # 人类可读名称
    started_at: datetime
    ended_at: datetime | None
    status: SpanStatus
    error: str | None
    attributes: dict        # 变长属性（token数、模型名等）
    tenant_id: int | None   # 租户隔离
```

**关键发现**：SpanKind 有 10 种，覆盖了 LangChat 所有执行路径。这不是日志级别（DEBUG/INFO/WARN），这是**业务语义类型**。

### Span 发射器：不阻塞业务

```python
# /root/langchat/apps/backend/langchat/observability/emitter.py

class DbSpanEmitter:
    """Buffers closed spans and flushes them to execution_span/trace_payload
    via a daemon thread so the instrumented call is never blocked."""
```

设计要点：
- 批量缓冲（max_buffer=50），异步刷入数据库
- 业务线程**不等待** DB 写入完成
- 支持 `CompositeEmitter([DbSpanEmitter(), LangfuseExporter, OTelExporter])` — 双写/多写

### Context 传播：async-safe

```python
# /root/langchat/apps/backend/langchat/observability/context.py

_current_span: contextvars.ContextVar[ExecutionSpan | None]
```

用 `contextvars` 而不是线程局部变量。这意味着 `asyncio.create_task` 和 `asyncio.to_thread` 都能自动传播 parent span。并行分支的 Span 不会丢父节点。

### 审计事件：AuditEventModel

```python
# /root/langchat/apps/backend/langchat/server/db/models/audit_model.py

class AuditEventModel(Base):
    __tablename__ = "audit_event"
    actor_user_id     # 谁做的
    actor_tenant_id   # 哪个租户
    action            # 做了什么（如 "skill_release:invoke"）
    resource_type     # 操作对象类型
    resource_id       # 操作对象ID
    result            # 结果
    request_metadata_json  # 六维上下文
    change_summary    # 变更摘要
    created_at        # 什么时候
```

**Trace vs Audit 的分工**：
- **Trace（ExecutionSpan）**：记录**执行过程**——每一步做了什么、花多久、什么结果
- **Audit（AuditEventModel）**：记录**治理决策**——谁允许做什么、策略快照、委托链

两者通过 `trace_id` 关联，但服务于不同目的。

---

## ━━━ 6. 商业地产映射 ━━━

### LangChat Trace → MI CRE 场景

| LangChat 概念 | MI CRE 对应 | 场景说明 |
|---|---|---|
| `trace_id` | 工单编号 | 一次租户投诉处理的完整追踪 |
| `workflow_run` Span | 投诉处理流程 | 从受理到关闭的全流程 |
| `workflow_node` Span | 每个审批步骤 | 物业确认→维修派单->费用审核 |
| `llm` Span | AI 辅助决策 | AI 分析投诉内容并推荐处理方案 |
| `rag_retrieval` Span | 知识库检索 | 检索历史类似投诉处理案例 |
| `capability_invoke` Span | ERP 系统调用 | 调 MI ERP 查合同/查租户/建工单 |
| AuditEventModel | 审批审计日志 | 谁批了什么、用了什么权限 |

### 具体场景：租户投诉自动处理

```
trace_id: cre-2026-0804-001
├─ channel_dispatch: 微信物业助手收到投诉 (root)
│  ├─ adapter: wechat.verify
│  ├─ context: resolve → 租户=张三, 工作空间=A座
│  ├─ rag_retrieval: 检索"漏水"相关历史案例
│  │  └─ rag_rerank: 精排 Top 3
│  ├─ llm: AI 分析+生成处理建议
│  ├─ capability_invoke: 调 MI ERP 创建维修工单
│  │  └─ mcp_tool: erp.create_work_order
│  └─ adapter: wechat.send_reply → 回复张三

Audit: actor=物业AI, action="work_order:create",
       result=succeeded, delegation_chain=[物业经理→AI]
```

**为什么 MI CRE 需要 Trace 而不只是日志**：
商业地产合规要求"每次操作可追溯"。如果 AI 自动创建了一张维修工单，物业经理需要知道：AI 检索了什么案例？依据什么建议？调了 ERP 哪个接口？Token 花了多少？这些只有结构化 Trace 能回答。

---

## ━━━ 7. 与传统方案比较 ━━━

### 方案 A：传统日志（ERP 标准做法）

| 维度 | 传统日志 | LangChat Trace |
|---|---|---|
| 数据结构 | 非结构化文本 | 结构化 Span 树（trace_id + parent_span_id） |
| 因果关系 | 无（靠人工关联） | 有（parent_span_id 形成树） |
| 查询能力 | grep / 全文搜索 | SQL 精确查询（按 kind/status/tenant_id） |
| 性能影响 | 同步写文件，阻塞业务 | 异步批量写 DB，不阻塞业务 |
| 跨服务关联 | 无统一 ID | trace_id 全局唯一，跨执行关联 |
| Token/成本追踪 | 不存在 | llm Span 内置 usage 属性 |
| 合规就绪 | 差（日志格式不统一） | 好（六维审计 + 标准化 Span） |
| 保留策略 | 看运维心情 | 可配置 TRACE_RETENTION_DAYS |

### 方案 B：OpenTelemetry SDK

| 维度 | 直接用 OTel SDK | LangChat 自实现 Span |
|---|---|---|
| 依赖 | 重（OTel SDK + exporter 链） | 零外部依赖 |
| Span 形状 | OTel 标准 | OTel-compatible（adopted shape, not SDK） |
| 外部对接 | 原生支持 | 通过 CompositeEmitter 插入 OTel/Langfuse exporter |
| 控制 | 完全交给 OTel | 自己控制持久化、查询、保留 |
| **结论** | — | **LangChat 选择了"OTel 形状 + 自实现"——获得兼容性，不背依赖** |

### 为什么不直接用日志？

> 因为日志回答不了这个问题：*"这次 AI 回答为什么用了 3 秒、花了 500 token、检索结果质量如何？"*

Trace 可以：
```sql
SELECT kind, name, duration_ms, attributes->>'usage'
FROM execution_span
WHERE trace_id = 'abc-123'
ORDER BY started_at;
```

一行 SQL 还原完整执行树。

---

## ━━━ 8. 架构师思考题 ━━━

### 如果 MI 的 3 个购物中心同时接入 LangChat，每天产生 10 万次对话，Trace 数据怎么治理？

**约束条件**：
- 每次 Channel Dispatch 产生约 5-8 个 Span
- 每天 10 万次 × 7 Span = 70 万行/天 = 2100 万行/月
- trace_payload（完整输入输出）平均每行 2KB
- 合规要求保留 90 天（不是默认的 30 天）

**需要回答**：
1. 数据库能不能扛住？（PG 分区？TimescaleDB？冷热分离？）
2. 90 天保留策略下，查询性能怎么保证？（索引设计？预聚合？）
3. 如果审计需要 1 年但 Trace 只留 90 天，两者怎么解耦？
4. 跨购物中心的 Trace 隔离怎么做？（tenant_id 索引够吗？）
5. 什么时候该引入外部可观测性平台（Langfuse/Jaeger）而不是自建？

> 这不是假设题。当 LangChat 真正进入 MI 生产环境，这就是 CTO 要回答的问题。

---

## ━━━ 9. 我的理解变化 ━━━

**以前以为**：Trace 就是高级一点的日志。写代码时 `logger.info()` 换成 `span.record()` 就行了，本质上没区别。

**现在知道**：Trace 和日志是**两个物种**：
- 日志是**叙述**——"发生了什么事"，面向人类阅读
- Trace 是**证据**——"怎么发生的、花多久、结果如何"，面向系统查询
- 日志没有结构，Trace 有严格的 Span Tree 结构（trace_id / span_id / parent_span_id）
- 日志不阻塞业务是靠"可能丢"，Trace 不阻塞业务是靠"异步批量持久化"（DbSpanEmitter）
- 日志没有保留策略自动化，Trace 有 `langchat trace prune --days N` CLI + 后台自动清理

更深一层的认知：**Trace 是 Governance 的基础设施**。没有 Trace，Permission 的效果无法验证、Approval 的决策无法追溯、PII 泄漏无法定位。Trace 不是"排障工具"，是"治理证据链"。

---

## ━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题：Approval（人审）—— 为什么 AI 不能全自动发布？

今天看了 Trace 怎么记录"发生了什么"。明天看 Governance 最敏感的问题：**哪些操作必须人审？为什么 AI 不能全自动？**

- Trace 告诉你"AI 做了什么"
- Approval 决定"AI 能不能做"
- 两者合在一起才是完整的 **可审计 AI 系统**

### Semantic Layer 定位

```
Ontology → Domain Model → Capability → Skill
                            ↑
                        Trace 是 Capability/Skill 执行的
                        观测层，不改变业务语义，
                        但为 Governance 提供证据基础

今天知识在链上的位置：
  FrozenExecutionContext 的 Trace 字段
    → ExecutionSpan（运行时 Span Tree）
      → AuditEventModel（治理审计事件）
        → Dev Console Timeline（只读可视化）
```

Trace 在 Semantic Layer 中是**透明层**——它不参与业务决策，但所有业务决策都通过它变得透明可查。
