# 🧱 LangChat 心智模型｜第8周-Day6：走完整条链

> **⚡ 动手交付：画一张完整链路图，标出每一步的输入输出**
>
> **日期**：2026-07-25（周六）
>
> **今日核心问题：为什么这条链不能短一步？**

---

## 目录

1. [往期回顾与业务关联](#1-往期回顾与业务关联)
2. [全景链路图：从用户意图到执行结果](#2-全景链路图从用户意图到执行结果)
3. [逐站解析：每一步的输入、输出、治理检查点](#3-逐站解析每一步的输入输出治理检查点)
4. [为什么这条链不能短一步？](#4-为什么这条链不能短一步)
5. [可运行的链路可视化](#5-可运行的链路可视化)
6. [Gap Analysis：链路上的断裂点](#6-gap-analysis链路上的断裂点)
7. [今天多理解了什么](#7-今天多理解了什么)
8. [重新设计时是否仍这样做](#8-重新设计时是否仍这样做)
9. [每日工程日志](#9-每日工程日志)
10. [术语表](#10-术语表)
11. [课堂练习与课后测试](#11-课堂练习与课后测试)
12. [真实参考](#12-真实参考)

---

## 1. 往期回顾与业务关联

### Week 8 前五天链路回顾

本周的任务是"跟着链路走"——从用户输入到执行结果，一天走一步。今天是第六天，我们要把五天的碎片拼成一张完整的图。

| Day | 链路站点 | 核心问题 | 关键产出 |
|-----|---------|----------|---------|
| Day1 | **Agent Host → LangChat** | 为什么 LangChat 不是 Agent Host？ | LangChat 是企业能力平台，被 Agent Host 直接调用，不做编排 |
| Day2 | **ApplicationContract** | 为什么 Contract 不是 API 文档？ | 传输无关的业务契约，携带 effect_policy / required_scopes / human_review_gate |
| Day3 | **Blueprint → Compiler → ExecutionPlan** | 为什么 Blueprint 不能直接运行？ | 确定性编译：10 阶段 Compiler，同一输入永远同一产出 |
| Day4 | **Runtime 无状态执行** | 为什么 Runtime 不保存状态？ | 所有状态通过 FrozenExecutionContext 带入，execute() 永不抛异常 |
| Day5 | **Capability + Connector** | 为什么 Capability 不是 Plugin？ | Capability 是治理描述符，SkillRelease 是唯一执行入口，Connector 是受治理集成资源 |

### 今天的目标

把这五站串成一条**完整的、可追踪的、不可缩短的**链路，并标出：
- 每一步的**输入**是什么
- 每一步的**输出**是什么
- 每一步的**治理检查点**是什么
- 如果去掉这一步会发生什么

---

## 2. 全景链路图：从用户意图到执行结果

### 2.1 链路全貌（ASCII 版）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LangChat 完整执行链路                              │
│                        （从 Agent Host 到业务结果）                           │
└─────────────────────────────────────────────────────────────────────────────┘

  ① Agent Host          ② Gateway           ③ SkillRelease
     用户意图        →    六维身份解析    →    发现 + 资格检查
     (OpenClaw等)        (six_dim_context)     (eligibility)
          │                   │                    │
          ▼                   ▼                    ▼
     输入：用户消息      输入：HTTP请求         输入：skill_id + scopes
     输出：HTTP请求      输出：六维上下文       输出：已验证的Descriptor
                                              + scope匹配结果

  ④ 幂等 & 限流         ⑤ HITL 审批          ⑥ 创建执行记录
     防重复 + 防刷      →   人审门控        →   (execution记录)
          │                   │                    │
          ▼                   ▼                    ▼
     输入：Idempotency   输入：review_assignee   输入：六维上下文
           -Key                是否存在               + Descriptor
     输出：放行/重放      输出：放行/202待审       输出：execution_id

  ⑦ Read-Only 守卫      ⑧ 分发执行           ⑨ SkillRelease Executor
     写操作检测       →   调度执行器       →   (如 W09 知识库问答)
          │                   │                    │
          ▼                   ▼                    ▼
     输入：Descriptor    输入：executor_fn       输入：用户query
           + binding           引用                  + 知识库
     输出：安全放行/      输出：调用 executor     输出：七字段结构化
           阻断 Violation                            回答

  ⑩ Workflow 执行       ⑪ Connector(目标态)   ⑫ 七字段响应
     内部执行表示     →   连接外部系统      →   结构化返回
          │                   │                    │
          ▼                   ▼                    ▼
     输入：workflow_id   输入：MCP/HTTP调用      输入：执行结果
           + 节点定义         (仅SR上下文内)        + trace_id
     输出：执行结果       输出：外部系统数据     输出：JSON响应
                                               → Agent Host
```

### 2.2 链路治理检查点一览

| 检查点 # | 名称 | 文件位置 | 检查内容 | 失败结果 |
|---------|------|---------|---------|---------|
| CP-1 | 六维身份解析 | `server/auth/six_dim_context.py` | client/actor/tenant/workspace/scope/delegation 六维 | 401 Unauthorized |
| CP-2 | SkillRelease 资格 | `canonical/eligibility.py` | scope 是否覆盖、生命周期是否 published | 403 Forbidden |
| CP-3 | 幂等重放 | `canonical/execution_replay.py` | Idempotency-Key 是否匹配历史 | 返回历史结果 |
| CP-4 | 速率限制 | `canonical/canonical_rate_limit.py` | RPM 是否超限（默认300） | 429 Too Many |
| CP-5 | HITL 审批人 | `canonical/execution_service.py` | human_review_gate + review_assignee 存在 | 500 Internal Error |
| CP-6 | Read-Only 守卫 | `canonical/read_only_guard.py` | effect_policy + 递归扫描写指标 | 500 Internal Error |
| CP-7 | 执行器存在性 | `canonical/execution_dispatch.py` | executor_fn 是否注册 | 执行失败 |

---

## 3. 逐站解析：每一步的输入、输出、治理检查点

### 站点 ① Agent Host → LangChat

**人话**：用户对 OpenClaw 说"帮我查一下报销流程"，OpenClaw 知道这个请求要找 LangChat。

**技术实现**：Agent Host 向 LangChat 发送 HTTP 请求：

```
POST /v1/skill-releases/{skill_id}/invoke
Host: langchat.example.com
Authorization: Bearer lc_service_agent_xxx
X-LC-Client-Id: openclaw-prod
X-LC-Actor-Id: user_12345
X-LC-Tenant-Id: 1
X-LC-Workspace-Id: 10
X-LC-Scope-Grants: skill_release:invoke
X-LC-Delegation-Chain: ...
X-LC-Idempotency-Key: uuid-xxx

{"input": {"query": "报销流程是什么？"}}
```

**输入**：用户的自然语言意图（"报销流程是什么？"）
**输出**：标准化的 HTTP 请求（携带六维身份上下文）

**关键代码**：路由定义在 `apps/backend/langchat/skill_release/canonical/router.py`

```python
@canonical_skill_release_router.post("/{skill_id}/invoke")
async def invoke_skill_release(
    skill_id: str,
    payload: CanonicalInvokeRequest,
    request: Request,
) -> JSONResponse | CanonicalInvokeResponseSync:
    context = get_six_dim_context(request)
    principal = CanonicalExecutionPrincipal.from_six_dim_context(context)
    ...
```

### 站点 ② 六维身份解析（Gateway 层）

**人话**：医院门口的预检分诊——先确认你是谁、从哪来、有没有挂号。

**技术实现**：`SixDimExecutionContext` 是一个 frozen dataclass（不可变），携带六个身份维度：

```python
# server/auth/six_dim_context.py
@dataclass(frozen=True)
class SixDimExecutionContext:
    client_id: str           # 哪个 Agent Host 在调用
    tenant_id: int           # 租户隔离边界
    workspace_id: int        # 租户内数据分组
    actor_id: str            # 实际发起者
    actor_type: str          # user / service_account
    key_scope_grants: tuple[str, ...]  # 授权 scope 列表
    delegation_chain: tuple[DelegationHop, ...]  # 委托链
    chain_depth: int         # 调用链深度
    credential_id: int       # 凭据 ID
    request_id: str          # 请求追踪 ID
```

**输入**：HTTP 请求头
**输出**：`SixDimExecutionContext` frozen 对象
**治理检查**：CP-1 六维身份完整

### 站点 ③ SkillRelease 发现 + 资格检查

**人话**：护士在系统里查你的号，确认你挂的是哪个科、有没有权限看这个科。

**技术实现**：`execution_preparation.py` → `prepare_canonical_execution()` 函数：

```python
# 步骤 1：找到 SkillRelease
descriptor = get_registry().get_latest(command.skill_id)

# 步骤 2：检查生命周期
if descriptor.lifecycle != "published":
    return unavailable

# 步骤 3：资格检查（scope + 可见性）
eligibility = canonical_eligibility(descriptor, principal.to_six_dim_context())
if not eligibility.is_eligible:
    if eligibility.denial_code == "scope_denied":
        return CanonicalExecutionFailure(403, ...)
```

**输入**：`skill_id` + `SixDimExecutionContext`
**输出**：`CanonicalPreparedExecution`（包含 Descriptor + 输入数据 + 哈希）
**治理检查**：CP-2 scope 是否匹配 + 生命周期是否 published

### 站点 ④ 幂等重放 + 速率限制

**人话**：
- 幂等：你按了两次"提交"按钮，系统只处理一次
- 限流：防止恶意刷接口

**技术实现**：

```python
# 幂等检查
idempotency_key = resolve_idempotency_key(
    command.header_idempotency_key,
    command.body_idempotency_key,
)
# 如果 header 和 body 都传了 Idempotency-Key 但值不同 → 400
# 如果匹配历史请求 → 返回历史结果

# 速率限制
rate_result = await check_canonical_rate_limit(rate_subject, command.skill_id)
if not rate_result.allowed:
    return CanonicalExecutionFailure(429, ...)
```

**输入**：Idempotency-Key + credential_id
**输出**：放行或重放历史结果
**治理检查**：CP-3 幂等 + CP-4 速率

### 站点 ⑤ HITL 审批门控

**人话**：如果这个技能需要人工审批（比如涉及敏感数据），先检查有没有配置审批人。

**技术实现**：

```python
if prepared.requires_review:
    assignee = get_review_assignee(
        session,
        skill_id=descriptor.skill_id,
        tenant_id=principal.tenant_id,
    )
    if assignee is None:
        return CanonicalExecutionFailure(500, "review_assignee not configured")
```

如果需要审批，执行进入 `pending_human_review` 状态，返回 202 + review_token：

```python
# 返回待审状态
return CanonicalExecutionPendingReview(
    execution_id=...,
    review_token=...,
    review_expires_at=...,  # 默认 86400 秒（24小时）
)
```

**输入**：`descriptor.human_review_gate` + `review_assignee` 配置
**输出**：放行进入执行 / 返回 202 待审
**治理检查**：CP-5 人审门控

### 站点 ⑥ 创建执行记录

**人话**：在病例本上写下"这位患者在 X 时间做了 Y 检查"，所有信息留痕。

**技术实现**：

```python
execution = create_execution(
    session,
    skill_id=descriptor.skill_id,
    skill_version=descriptor.version,
    tenant_id=principal.tenant_id,
    client_id=principal.client_id,
    actor_id=principal.actor_id,
    workspace_id=principal.workspace_id,
    effect_policy=descriptor.effect_policy,
    effective_scope=runtime_context.effective_scope,
    delegation_chain=[...],
    input_hash=prepared.input_hash,
    input_payload=prepared.input_data,
    trace_id=command.trace_id,
)
```

**输入**：六维上下文 + Descriptor + 输入数据
**输出**：`execution_id`（持久化执行记录）
**治理检查**：完整的审计追踪链

### 站点 ⑦ Read-Only 守卫

**人话**：进手术室前的最后安检——P0 阶段绝对不允许任何写操作。

**技术实现**：`read_only_guard.py`

```python
_WRITE_INDICATORS = frozenset({
    "http_request",      # HTTP 写请求
    "db_write",          # 数据库写
    "tool_call",         # 工具调用
    "provider_conditional_write",  # Provider 条件写
})

def enforce_read_only(descriptor: SkillReleaseDescriptor) -> None:
    # 检查 1：effect_policy 必须是 read_only
    if descriptor.effect_policy != "read_only":
        raise ReadOnlyViolationError(...)
    # 检查 2：递归扫描 workflow_binding 查找写指标
    _check_workflow_binding_writes(descriptor)
```

递归扫描的工作方式：深度优先遍历 `workflow_binding` 字典的每一个键和值（最多8层深度），发现任何键或字符串值匹配 `_WRITE_INDICATORS` 就阻断。

**输入**：`SkillReleaseDescriptor`
**输出**：安全放行 / `ReadOnlyViolationError`
**治理检查**：CP-6 P0 安全底线

### 站点 ⑧ 分发执行

**人话**：调度台根据技能 ID 找到对应的执行团队，把任务交过去。

**技术实现**：`execution_dispatch.py`

```python
async def dispatch_canonical_execution(
    principal: CanonicalExecutionPrincipal,
    command: CanonicalDispatchCommand,
) -> CanonicalDispatchOutcome:
    descriptor = command.descriptor
    executor = _get_executor(descriptor.skill_id, descriptor.version)
    if executor is None:
        return CanonicalDispatchFailed(error_code="no_executor", ...)

    # 在 OpenTelemetry span 内执行
    async with start_span_async(
        SpanKind.CAPABILITY_INVOKE,
        f"skill_release.invoke:{descriptor.skill_id}",
    ):
        result = await executor(principal, command)
```

**输入**：`CanonicalDispatchCommand`（Descriptor + 输入数据 + 六维上下文）
**输出**：`CanonicalDispatchSucceeded`（七字段结果）或 `CanonicalDispatchFailed`
**治理检查**：CP-7 执行器存在性 + OpenTelemetry 追踪

### 站点 ⑨ SkillRelease Executor（如 W09）

**人话**：执行团队实际干活——查知识库、生成回答。

**技术实现**：以 W09 为例，执行器函数注册在 `skill_release/bindings/w09.py`：

```python
_w09_descriptor = SkillReleaseDescriptor(
    skill_id="langchat.w09.internal.service",
    version="v1",
    lifecycle="published",
    required_scopes=["skill_release:invoke"],
    effect_policy="read_only",
    human_review_gate="conditional",  # 敏感咨询走人审
    workflow_binding={
        "workflow_id": "mall-internal-service",
        "schema_version": "v1"
    },
)

def _register():
    from ..executors.w09_executor import w09_invoke
    get_registry().register_skill(_w09_descriptor, w09_invoke)
```

执行器内部调用 Workflow 引擎执行知识库问答，最终产出**七字段结构化输出**。

### 站点 ⑩-⑫ Workflow → Connector → 七字段响应

**Workflow 执行**：内部执行表示（WorkflowSpec v1），当前是 LangChat 唯一受治理的执行格式。

**Connector（目标态）**：ADR-004 §8 要求 Connector 只在 SkillRelease execution context 内可用，当前 MCP Connector 嵌在 Workflow 内部是 Gap。

**七字段输出 Schema**（`descriptor.py` 中的 `_SEVEN_FIELD_OUTPUT_SCHEMA`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `summary` | string\|null | 摘要回答 |
| `details` | string\|null | 详细说明 |
| `references` | array | 引用来源（知识库文档等） |
| `assumptions` | array | AI 做了哪些假设 |
| `human_review_required` | boolean | 是否需要人工复核 |
| `next_actions` | array | 建议的下一步行动 |
| `confidence` | number | 置信度（0-1） |

---

## 4. 为什么这条链不能短一步？

这是今天的核心问题。我们逐一分析：如果去掉某一步会发生什么？

### 去掉 ① Agent Host 直连？

**不行。** 如果 LangChat 自己做 Agent Host，它就不再是"企业能力平台"，而变成了"另一个 AI 聊天产品"。Agent Host 和能力平台的分离是**关注点分离**的基础——Agent Host 管用户交互，LangChat 管能力治理。

> ADR-001 §4.1："LangChat 是企业能力平台，被 Agent Host 直接、受控地调用。"

### 去掉 ② 六维身份解析？

**不行。** 没有六维身份，就无法做租户隔离、scope 校验、委托链追踪。任何调用者都可以冒充其他租户、访问无权技能。

> ADR-001 §8：六维身份是"不可只信任请求体声明"的硬约束。

### 去掉 ③ SkillRelease 资格检查？

**不行。** 没有 eligibility 检查，任何已认证调用者都能调用任何技能——包括无权访问的租户专属技能、已废弃的旧版本。

### 去掉 ④ 幂等 + 限流？

**不行。**
- 没有幂等：网络重试导致重复执行，用户被扣两次款、知识库被重复写入
- 没有限流：一个恶意调用者可以在几秒内耗尽 LLM 推理配额

### 去掉 ⑤ HITL 审批？

**不行。** P0 阶段 W09 的 `human_review_gate="conditional"` 意味着敏感咨询（如薪资结构）必须有人工审批环节。没有这一步，AI 可能直接披露不该披露的信息。

### 去掉 ⑥ 执行记录？

**不行。** 没有执行记录 = 没有审计 = 没有合规。企业平台的核心要求是"可追踪"——出了问题必须能回查"谁在什么时间调用了什么技能，输入输出是什么"。

### 去掉 ⑦ Read-Only 守卫？

**绝对不行。** 这是 P0 阶段的安全底线。`enforce_read_only()` 是最后一道防线——即使前面所有检查都通过，如果 Workflow 中嵌入了写操作（如 `db_write` 节点），这里会阻断。

> P0 阶段所有 SkillRelease 的 `effect_policy` 必须为 `read_only`（ADR-001 §11.3）。

### 去掉 ⑧ 分发执行？

**不行。** 没有 dispatch 层，SkillRelease 和 Executor 的绑定就没有运行时验证。如果 Executor 未注册（代码部署遗漏），应该返回结构化错误而不是 500 崩溃。

### 结论：链不可缩短

每一步都有**独立的治理目的**——不是"为了流程完整"，而是为了解决一个具体的安全/治理/可靠性问题。去掉任何一步，都会在某个维度打开缺口。这就是为什么这条链**不能短一步**。

---

## 5. 可运行的链路可视化

> 下面的代码在 Jupyter Notebook 中可运行，生成 LangChat 完整执行链路的流程图和治理热力图。

### 5.1 链路流程图（Matplotlib）

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# 中文字体配置（每个 Notebook 第一格必须配置）
from matplotlib import font_manager
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

# 链路站点定义
stations = [
    ("① Agent Host\n用户意图", "#4CAF50"),
    ("② 六维身份\n身份解析", "#2196F3"),
    ("③ 资格检查\nScope+生命周期", "#2196F3"),
    ("④ 幂等+限流\n防重复+防刷", "#FF9800"),
    ("⑤ HITL 门控\n人审检查", "#FF9800"),
    ("⑥ 执行记录\n审计留痕", "#9C27B0"),
    ("⑦ 只读守卫\n写操作检测", "#F44336"),
    ("⑧ 分发执行\n调度Executor", "#4CAF50"),
    ("⑨ 技能执行\nWorkflow+知识库", "#4CAF50"),
    ("⑩ 七字段响应\n结构化返回", "#4CAF50"),
]

fig, ax = plt.subplots(figsize=(20, 6))
ax.set_xlim(-1, 21)
ax.set_ylim(-2, 4)
ax.axis('off')
ax.set_title('LangChat 完整执行链路：从用户意图到业务结果\n（每一步不可缩短）',
             fontsize=16, fontweight='bold', pad=20)

# 绘制站点
for i, (label, color) in enumerate(stations):
    x = i * 2.2
    # 站点方框
    rect = mpatches.FancyBboxPatch((x-0.8, 0.5), 1.6, 2.0,
                                     boxstyle="round,pad=0.1",
                                     facecolor=color, edgecolor='black',
                                     alpha=0.85, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x, 1.5, label, ha='center', va='center',
            fontsize=8, fontweight='bold', color='white')
    
    # 箭头（除最后一个）
    if i < len(stations) - 1:
        ax.annotate('', xy=(x+2.2-0.8, 1.5), xytext=(x+0.8, 1.5),
                    arrowprops=dict(arrowstyle='->', color='#333', lw=2))

# 标注治理检查点
checkpoints = [
    (1, "CP-1\n身份", "#2196F3"),
    (2, "CP-2\n资格", "#2196F3"),
    (3, "CP-3/4\n幂等+限流", "#FF9800"),
    (4, "CP-5\n人审", "#FF9800"),
    (5, "CP-6\n审计", "#9C27B0"),
    (6, "CP-7\n只读", "#F44336"),
]

for idx, label, color in checkpoints:
    x = idx * 2.2
    ax.text(x, -0.5, label, ha='center', va='top',
            fontsize=7, color=color, fontweight='bold')
    ax.annotate('', xy=(x, -0.1), xytext=(x, 0.4),
                arrowprops=dict(arrowstyle='->', color=color, lw=1, ls='--'))

# 图例
legend_elements = [
    mpatches.Patch(facecolor='#4CAF50', label='执行层（业务逻辑）'),
    mpatches.Patch(facecolor='#2196F3', label='认证与资格（治理）'),
    mpatches.Patch(facecolor='#FF9800', label='限流与人审（治理）'),
    mpatches.Patch(facecolor='#9C27B0', label='审计追踪（治理）'),
    mpatches.Patch(facecolor='#F44336', label='安全底线（治理）'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=9,
          ncol=5, bbox_to_anchor=(0, 1.15))

# 底部说明
ax.text(10, -1.5, '10个站点 · 7个治理检查点 · 0步可缩短',
        ha='center', fontsize=12, fontweight='bold', color='#333',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4', edgecolor='#FBC02D'))

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第8周/w8d6_chain_overview.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 链路流程图已生成")
```

### 5.2 治理检查点热力图

```python
# 治理检查点维度分析
import matplotlib.pyplot as plt
import numpy as np

dimensions = ['身份认证', '访问控制', '数据安全', '审计追踪', '可靠性', '性能保护']
checkpoints = ['CP-1\n六维身份', 'CP-2\n资格检查', 'CP-3\n幂等', 'CP-4\n限流',
               'CP-5\nHITL', 'CP-6\n只读守卫', 'CP-7\n执行器']

# 每个检查点在每个维度上的覆盖程度 (0=不覆盖, 1=部分覆盖, 2=完全覆盖)
coverage = np.array([
    [2, 1, 1, 2, 0, 0],  # CP-1 六维身份
    [0, 2, 1, 1, 0, 0],  # CP-2 资格检查
    [0, 0, 0, 1, 2, 0],  # CP-3 幂等
    [0, 0, 0, 0, 1, 2],  # CP-4 限流
    [0, 2, 2, 1, 0, 0],  # CP-5 HITL
    [0, 0, 2, 1, 1, 0],  # CP-6 只读守卫
    [0, 0, 0, 1, 2, 0],  # CP-7 执行器
])

fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(coverage, cmap='YlOrRd', aspect='auto', vmin=0, vmax=2)

ax.set_xticks(range(len(dimensions)))
ax.set_yticks(range(len(checkpoints)))
ax.set_xticklabels(dimensions, fontsize=10)
ax.set_yticklabels(checkpoints, fontsize=10)

# 在格子中写文字
labels = {0: '—', 1: '◐', 2: '●'}
for i in range(len(checkpoints)):
    for j in range(len(dimensions)):
        ax.text(j, i, labels[coverage[i, j]], ha='center', va='center',
                fontsize=14, fontweight='bold',
                color='white' if coverage[i,j] == 2 else '#333')

ax.set_title('LangChat 治理检查点 × 维度覆盖热力图\n（●=完全覆盖  ◐=部分覆盖  —=不覆盖）',
             fontsize=13, fontweight='bold', pad=15)
plt.colorbar(im, ax=ax, shrink=0.8, label='覆盖程度')

# 底部统计
total_checks = coverage.size
full_coverage = (coverage == 2).sum()
partial = (coverage == 1).sum()
ax.text(0.5, -0.12, f'完全覆盖: {full_coverage}/{total_checks}  |  部分覆盖: {partial}/{total_checks}  |  最大覆盖维度: 审计追踪',
        transform=ax.transAxes, ha='center', fontsize=10, style='italic')

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第8周/w8d6_governance_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 治理热力图已生成")
```

### 5.3 链路数据流图

```python
# 数据流：每一步的输入输出
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(18, 12))
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis('off')
ax.set_title('LangChat 链路数据流：每一步的输入与输出\n（从 HTTP 请求到七字段响应）',
             fontsize=14, fontweight='bold', pad=15)

# 数据流节点
flow_data = [
    (9, 11, "HTTP 请求\nPOST /v1/skill-releases/{id}/invoke\n+ 六维身份头", "#E8F5E9", "#4CAF50"),
    (9, 9.2, "SixDimExecutionContext (frozen)\nclient/actor/tenant/workspace/scope/delegation", "#E3F2FD", "#2196F3"),
    (9, 7.4, "CanonicalPreparedExecution\nDescriptor + input_data + input_hash", "#E3F2FD", "#2196F3"),
    (9, 5.6, "Execution Record\nexecution_id + 六维上下文 + effect_policy", "#F3E5F5", "#9C27B0"),
    (9, 3.8, "CanonicalDispatchCommand\nDescriptor + 输入数据 + runtime_context", "#FFF3E0", "#FF9800"),
    (9, 2.0, "七字段结构化输出\nsummary/details/references/assumptions/\nhuman_review_required/next_actions/confidence", "#E8F5E9", "#4CAF50"),
]

# 治理标注（左侧）
governance_labels = [
    (2, 9.2, "🔒 CP-1\n六维身份\n不可只信任\n请求体声明", "#2196F3"),
    (2, 7.4, "🔒 CP-2/3/4\n资格 + 幂等\n+ 限流", "#FF9800"),
    (2, 5.6, "🔒 CP-5/6\nHITL +\n只读守卫", "#F44336"),
    (2, 3.8, "🔒 CP-7\n执行器\n存在性校验", "#9C27B0"),
]

# 绘制数据流
for i, (x, y, text, bg, border) in enumerate(flow_data):
    rect = mpatches.FancyBboxPatch((x-3.5, y-0.6), 7, 1.2,
                                     boxstyle="round,pad=0.15",
                                     facecolor=bg, edgecolor=border, linewidth=2)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=7.5,
            fontweight='bold', color='#333')
    if i < len(flow_data) - 1:
        ax.annotate('', xy=(x, flow_data[i+1][1]+0.6), xytext=(x, y-0.6),
                    arrowprops=dict(arrowstyle='->', color='#666', lw=2.5))

# 绘制治理标注
for x, y, text, color in governance_labels:
    rect = mpatches.FancyBboxPatch((x-1.2, y-0.55), 2.4, 1.1,
                                     boxstyle="round,pad=0.1",
                                     facecolor='white', edgecolor=color,
                                     linewidth=1.5, linestyle='--')
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=7,
            fontweight='bold', color=color)
    # 虚线连接到数据流
    ax.annotate('', xy=(5.5, y), xytext=(x+1.2, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1, ls='--'))

# 右侧标注
right_labels = [
    (15.5, 11, "Agent Host\n发起", "#4CAF50"),
    (15.5, 9.2, "Gateway 层\n解析", "#2196F3"),
    (15.5, 7.4, "Preparation\n准备", "#2196F3"),
    (15.5, 5.6, "Audit\n记录", "#9C27B0"),
    (15.5, 3.8, "Dispatch\n调度", "#FF9800"),
    (15.5, 2.0, "Response\n返回", "#4CAF50"),
]
for x, y, text, color in right_labels:
    ax.text(x, y, text, ha='center', va='center', fontsize=8,
            fontweight='bold', color=color,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FAFAFA',
                      edgecolor=color, alpha=0.8))

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第8周/w8d6_data_flow.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 数据流图已生成")
```

---

## 6. Gap Analysis：链路上的断裂点

把完整链路画出来后，Gap 就无处藏身了。

### 6.1 链路完整性矩阵

| 链路站 | 目标态（ADR） | 当前代码现实 | 状态 | Gap 说明 |
|--------|-------------|-------------|------|---------|
| ① Agent Host 直连 | ADR-001 §4 | ✅ canonical router 可用 | 🟢 已对齐 | — |
| ② 六维身份 | ADR-002 D1 | ✅ `SixDimExecutionContext` | 🟢 已对齐 | wire profile D1 仍为待决策 |
| ③ SkillRelease 资格 | ADR-003 §13 | ✅ eligibility + scope | 🟢 已对齐 | — |
| ④ 幂等 + 限流 | ADR-003 §13 | ✅ 完整实现 | 🟢 已对齐 | — |
| ⑤ HITL 门控 | ADR-003 §13 | ✅ review_assignee + review_token | 🟢 已对齐 | — |
| ⑥ 执行记录 | ADR-004 §5 | ✅ create_execution | 🟢 已对齐 | — |
| ⑦ Read-Only 守卫 | ADR-001 §11.3 | ✅ enforce_read_only | 🟢 已对齐 | 枚举式检测有局限 |
| ⑧ 分发执行 | ADR-003 §13 | ✅ dispatch + OTel | 🟢 已对齐 | — |
| ⑨ Workflow 执行 | Domain Model §12 | ✅ WorkflowSpec v1 执行 | 🟡 过渡态 | 目标态为 ExecutionPlanIR（v2 制品链） |
| ⑩ Connector | ADR-004 §8 | ❌ MCP 嵌在 Workflow 内 | 🔴 最大 Gap | Connector 未独立治理 |
| — E3/E4 遗留路径 | ADR-004 §4.1.1 | ⚠️ SPA workflow / Public Chat | 🟡 待迁移 | P1 优先级 |
| — v2 制品链 | Charter §6.4 | ❌ 未实现 | 🔴 目标态 | Blueprint → Build → IR → SkillRelease v2 |

### 6.2 链路断裂风险排序

| 风险等级 | 断裂点 | 影响 | 缓解措施 |
|---------|--------|------|---------|
| **P0 危险** | Connector 未独立治理 | MCP 工具调用绕过 effect_policy 校验 | P0 通过 read_only_guard 兜底，但不完备 |
| **P1 高** | v2 制品链未实现 | WorkflowSpec 仍是唯一执行表示 | cutover 时 W09 首先迁移 |
| **P1 高** | E3/E4 遗留路径 | 旁路 canonical 执行，无统一审计 | 按迁移计划关闭 |
| **P2 中** | read_only_guard 枚举式检测 | 新型写操作可能绕过检查 | 增加 schema 级校验 |
| **P2 中** | D1 wire profile 未冻结 | 生产级 Agent Host 直连无法正式开放 | 冻结后可开放 |

---

## 7. 今天多理解了什么

### 以前以为 → 现在知道

| # | 以前以为 | 现在知道 |
|---|---------|---------|
| 1 | 各模块是独立的组件 | 它们是一条**不可缩短的链**——每一步有独立的治理目的，去掉任何一步都打开安全/审计/可靠性缺口 |
| 2 | 治理检查点散落在各处 | 画出来后发现有 **7 个检查点**，覆盖 **6 个治理维度**（身份/访问/数据安全/审计/可靠性/性能保护），审计追踪是覆盖最广的维度 |
| 3 | read_only_guard 只是个小守卫 | 它是 P0 阶段**最后的安全防线**——所有前置检查都通过后，它仍然可能阻断写操作。它的递归扫描设计（8层深度）体现了纵深防御原则 |
| 4 | 幂等和限流是"运维功能" | 它们是**链路治理**的一部分——幂等保证用户体验（不重复执行），限流保证平台安全（防刷），都属于 CP 级别检查点 |
| 5 | 当前代码已经"接近完整" | 画完链路图后看到：核心执行链路 🟢 对齐，但 Connector 治理 🔴 缺失，v2 制品链 🔴 未实现。链路的"后半段"还是目标态 |
| 6 | 链路图是"架构师才画的" | 画图过程本身就是**认知整理**过程——当你能画出完整链路并标出每一步的输入输出时，说明你真正理解了系统 |

---

## 8. 重新设计时是否仍这样做

### 问题：如果今天从零设计这条链路，有什么会更早做？

**会更早做的**：

1. **Connector 独立治理层**。当前 MCP 嵌在 Workflow 内是最大的架构债。如果从零开始，Connector 应该和 SkillRelease 同级注册，有自己的 effect_policy、scope、版本管理，而不是作为 Workflow 的子节点。

2. **v2 制品链从一开始就建**。WorkflowSpec 作为"过渡方案"最终需要退役，但当前 9 个工作流都绑定了它。如果从零开始，直接用 Blueprint → Compiler → ExecutionPlanIR 链路，不走 WorkflowSpec 弯路。

3. **ApplicationContract 在 P0 就引入**。当前 SkillReleaseDescriptor 同时承担"业务语义"+"设计描述"+"实现绑定"三个角色。如果在 P0 就有 Contract 层，后续演进不需要大规模重构。

**不会改变的**：

1. **六维身份作为第一步**。没有身份就没有治理，这一步不可延后。
2. **Read-Only 守卫作为最后防线**。纵深防御要求"即使前面都通过了，最后一道检查仍然存在"。
3. **七字段结构化输出**。给 Agent Host 提供可解析、可审计的标准输出格式。
4. **幂等 + 限流在准备阶段**。在真正执行之前做防重复和防刷，节省资源。

---

## 9. 每日工程日志

### 📅 2026-07-25（Week8-Day6）

#### 新增认知
- 完整链路有 **10 个站点**、**7 个治理检查点**、覆盖 **6 个治理维度**
- 链路中每一 步都有独立的治理目的，去掉任何一步都会打开具体的安全/审计/可靠性缺口
- 治理检查点不是"散落"的——它们有清晰的层次：身份认证 → 访问控制 → 流量保护 → 人审门控 → 审计追踪 → 安全底线 → 执行器校验
- `SixDimExecutionContext` 是贯穿全链路的数据结构——从 Gateway 解析到执行记录创建，六维上下文一路传递

#### 修改认知
- 之前认为各模块是"组件图"（并列关系）→ 现在知道是"链路图"（串行关系，不可跳过）
- 之前认为 read_only_guard 是"配置校验"→ 它是运行时**递归扫描**机制，深度8层，检查键名和字符串值

#### 确认
- 核心执行链路（① - ⑧）已完全对齐 ADR 目标态
- 幂等重放 + 速率限制 + HITL 审批 + 执行记录全部可工作
- OpenTelemetry span 追踪已嵌入 dispatch 阶段

#### 遗留
- Connector 独立治理是最大架构 Gap（P0 危险）
- v2 制品链（Blueprint → Build → IR → SkillRelease v2）完全未实现
- E3 SPA workflow / E4 Public Chat 遗留路径未迁移
- D1 unified delegation wire profile 未冻结

#### 技术债
- `read_only_guard.py` 的 `_WRITE_INDICATORS` 枚举式检测不完备
- WorkflowSpec 作为执行表示需要在 cutover 阶段逐步替换
- Connector 没有 independent lifecycle（版本、effect_policy、scope）

#### 下一步
- 明天（Day7）Virtual CTO Review：对整条链路做五维评分
- Week 9 进入 Domain Deep Dive，逐个理解对象为什么独立存在
- 关注 ADR-005（制品链）和 ADR-007（RuntimeABI）的工程推进

---

## 10. 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| **Canonical** | /kəˈnɒnɪkəl/ | 规范的 | 标准执行路径，区别于遗留路径 |
| **Checkpoint** | /ˈtʃekpɔɪnt/ | 检查点 | 链路上的治理校验节点 |
| **Eligibility** | /ˌelɪdʒəˈbɪləti/ | 资格 | Scope + 生命周期 + 可见性综合校验 |
| **Idempotency** | /ˌaɪdəmˈpɒtənsi/ | 幂等性 | 同一请求重复执行产生相同结果 |
| **Dispatch** | /dɪˈspætʃ/ | 分发 | 根据技能 ID 找到对应执行器并调用 |
| **HITL** | /eɪtʃ-tiː-el/ | 人工审核 | Human-In-The-Loop，关键操作需人工审批 |
| **Rate Limit** | /reɪt ˈlɪmɪt/ | 速率限制 | 防止单一调用者耗尽资源 |
| **Read-Only Guard** | /riːd-ˈəʊnli ɡɑːd/ | 只读守卫 | P0 阶段阻断所有写操作的运行时机制 |
| **SixDimExecutionContext** | — | 六维执行上下文 | 携带 client/actor/tenant/workspace/scope/delegation |
| **Seven-Field Output** | — | 七字段输出 | summary/details/references/assumptions/review_required/next_actions/confidence |
| **Chain Integrity** | /tʃeɪn ɪnˈteɡrəti/ | 链路完整性 | 链路上无断裂、无旁路、全链路可追踪 |
| **Depth Defense** | /depθ dɪˈfens/ | 纵深防御 | 多层安全检查，任一层不依赖其他层的正确性 |
| **Effect Policy** | /ɪˈfekt ˈpɒləsi/ | 效果策略 | read_only 或 conditional_write |
| **Review Assignee** | /rɪˈvjuː əˈsaɪniː/ | 审批指派人 | 为 HITL 技能配置的审批人 |
| **Delegation Chain** | /ˌdelɪˈɡeɪʃən tʃeɪn/ | 委托链 | actor 代表另一主体行动的授权链 |
| **Cutover** | /ˈkʌtoʊvər/ | 切换 | 从旧系统迁移到新系统的过程 |
| **Gap Analysis** | /ɡæp əˈnæləsɪs/ | 差距分析 | 目标态与代码现实之间的差距评估 |

---

## 11. 课堂练习与课后测试

### 课堂练习

**练习 1：画出你自己的链路图**

不看答案，凭记忆在纸上画出 LangChat 从 Agent Host 发起到返回七字段响应的完整链路。标注：
- 至少 8 个站点
- 至少 5 个治理检查点
- 每个站点的输入和输出

**练习 2：Gap 分析实战**

观察你画的链路图，找出：
- 哪些站点已经完全对齐 ADR 目标态？
- 哪些站点是过渡态？
- 哪些站点是最大 Gap？
- 如果你是 CTO，优先修哪个 Gap？

**练习 3：去掉一步的后果**

选择链路中的任意一个检查点，写一段 100 字的分析：如果去掉这个检查点，具体会出现什么安全问题？

### 课后测试

**Q1**：LangChat 完整执行链路中有多少个治理检查点（Checkpoint）？

A. 3 个
B. 5 个
C. 7 个
D. 10 个

**Q2**：`enforce_read_only()` 函数的递归扫描深度是多少？

A. 3 层
B. 5 层
C. 8 层
D. 无限制

**Q3**：以下哪个检查点覆盖了最多的治理维度？

A. CP-1 六维身份
B. CP-3 幂等
C. CP-6 只读守卫
D. CP-7 执行器存在性

**Q4**：当前链路上最大的 Gap 是什么？

A. 六维身份解析不完整
B. Connector 未独立治理
C. 幂等检查有 bug
D. 速率限制太严格

**Q5**：为什么说链路"不能短一步"？以下哪个不是原因？

A. 每一步有独立的治理目的
B. 去掉任何一步会打开具体的安全/审计/可靠性缺口
C. 步骤越多看起来越专业
D. 纵深防御要求多层独立检查

---

## 12. 真实参考

### ADR 文档

| 文档 | 关键章节 | 在链路中的位置 |
|------|---------|---------------|
| ADR-001 | §4 直连定位、§6 控制面/执行面、§8 六维身份 | ①②⑥⑦ |
| ADR-002 | D1 统一委托 wire profile | ②（wire profile 待决策） |
| ADR-003 | §13 SkillRelease API wire profile | ①③④⑤⑧ |
| ADR-004 | §4.1.1 遗留路径、§5 四逻辑Plane、§8 Connector | ⑩（Connector Gap） |
| ADR-005 | D-1~D-5 制品链 + WorkflowSpec 退役 | ⑨（目标态 v2 制品链） |
| ADR-007 | D-4 FrozenExecutionContext wire | ②（wire 表示） |

### 代码文件

| 文件 | 路径 | 链路位置 |
|------|------|---------|
| Canonical Router | `apps/backend/langchat/skill_release/canonical/router.py` | ① HTTP 入口 |
| 六维上下文 | `apps/backend/langchat/server/auth/six_dim_context.py` | ② 身份解析 |
| 执行准备 | `apps/backend/langchat/skill_release/canonical/execution_preparation.py` | ③④ 准备阶段 |
| 幂等重放 | `apps/backend/langchat/skill_release/canonical/execution_replay.py` | ④ 幂等检查 |
| 速率限制 | `apps/backend/langchat/skill_release/canonical/canonical_rate_limit.py` | ④ 限流 |
| 执行服务 | `apps/backend/langchat/skill_release/canonical/execution_service.py` | ⑤⑥ 编排 |
| 只读守卫 | `apps/backend/langchat/skill_release/canonical/read_only_guard.py` | ⑦ 安全底线 |
| 分发执行 | `apps/backend/langchat/skill_release/canonical/execution_dispatch.py` | ⑧ 调度 |
| W09 绑定 | `apps/backend/langchat/skill_release/bindings/w09.py` | ⑨ 执行器 |
| 描述符 | `apps/backend/langchat/skill_release/descriptor.py` | ⑨ 七字段 Schema |
| 执行契约 | `apps/backend/langchat/skill_release/canonical/execution_contracts.py` | 全链路数据结构 |
| ApplicationContract | `apps/backend/langchat/business_domain/application_contract.py` | 目标态 Contract |
