# 🧱 LangChat 心智模型｜第8周-Day5：Capability 与 Connector

> **链路第五步：执行时怎么连到业务系统？**
>
> **日期**：2026-07-24（周五）
>
> **今日核心问题：为什么 Capability 不是 Plugin？**

---

## 目录

1. [往期回顾与业务关联](#1-往期回顾与业务关联)
2. [为什么需要 Capability？它解决了什么问题？](#2-为什么需要-capability它解决了什么问题)
3. [ADR/架构如何设计](#3-adr架构如何设计)
4. [当前代码如何实现](#4-当前代码如何实现)
5. [差距分析](#5-差距分析gap-analysis)
6. [今天多理解了什么](#6-今天多理解了什么)
7. [重新设计时是否仍这样做](#7-重新设计时是否仍这样做)
8. [每日工程日志](#8-每日工程日志)
9. [术语表](#9-术语表)
10. [课堂练习与课后测试](#10-课堂练习与课后测试)
11. [真实参考](#11-真实参考)

---

## 1. 往期回顾与业务关联

### W8 链路前四天

| Day | 主题 | 核心要点 | 与今天的关系 |
|-----|------|----------|--------------|
| Day1 | 用户意图 | Agent Host 直接调用 LangChat，LangChat 不是 Agent Host | Agent Host 发出的请求要执行的"能力"是什么？ |
| Day2 | ApplicationContract | 传输无关的业务契约，定义"做什么" | Contract 的实现需要调用底层"能力" |
| Day3 | Blueprint → Compiler → ExecutionPlan | 确定性编译，同一输入永远同一产出 | 编译产出的执行计划需要引用"能力清单" |
| Day4 | Runtime 无状态执行 | Runtime 是手术室，不保存病人档案 | Runtime 执行时需要调用外部系统——通过什么连？ |

### 昨天的延续

昨天学到 Runtime 是无状态的执行环境——它不保存会话状态、不记住用户偏好、不持有业务数据。今天进入下一个核心问题：

**Runtime 执行 SkillRelease 时，如果要查询外部知识库、调用 ERP 系统、触发 CRM 写操作——这些"连到企业系统"的能力从哪里来？谁来治理？怎么保证安全？**

答案的核心概念就是 **Capability** 和 **Connector**。而最反直觉的设计决策是：**Capability 不是 Plugin，Connector 不是 Gateway**。

---

## 2. 为什么需要 Capability？它解决了什么问题？

### 生活类比：医院里的"专科能力" vs "外包工"

想象一家大型医院：

- **外包工模式（Plugin 思路）**：医院把某科室整体外包给一个团队，团队自带设备、自定流程、自行管理。医院只知道"有人在干活"，但无法管控质量、无法审计、无法替换。
- **专科能力模式（Capability 思路）**：医院定义"心脏检查能力"的标准——包含哪些项目、需要什么资质、产出什么报告、哪些情况需要主任医师审核。具体由谁来做、用什么设备，都在医院治理框架内。

LangChat 选择了后者。

### Plugin 模式的问题（传统 AI 平台的常见做法）

在 Dify、Coze 等传统 AI 应用平台中，"插件"是常见的扩展机制：

```
用户 → AI Agent → Plugin（工具） → 外部系统
         ↑
    Plugin 直接执行
    Plugin 自己管安全
    Plugin 状态难追踪
```

Plugin 模式的问题：

| 问题 | 说明 |
|------|------|
| **治理黑洞** | Plugin 内部做什么，平台不可见、不可审。Plugin 成了"黑盒" |
| **安全绕过** | Plugin 拥有调用方的全部权限，没有独立的 effect 策略 |
| **版本失控** | Plugin 升级后行为变化，但没有版本号、没有生命周期管理 |
| **责任不清** | Plugin 出错时，是 Plugin 的问题还是平台的问题？ |
| **不可组合** | Plugin 之间没有统一的输入输出契约，无法被 SkillRelease 引用 |

### Capability 模式的核心区别

Capability 用三道防线解决上述问题：

```
第一道：Capability Descriptor（描述符）
  — "这个能力是什么？输入输出是什么？需要什么 scope？效果是什么？"
  — 冻结后不可变（immutable after published）

第二道：SkillRelease Binding（绑定）
  — "这个能力被哪个 SkillRelease 使用？在什么条件下使用？"
  — SkillRelease 是唯一可以执行的业务单元

第三道：Connector（连接器）
  — "具体怎么连到外部系统？"
  — 只在 SkillRelease 已授权执行上下文内可用
```

**一句话总结：Capability 定义"能做什么"的治理契约，SkillRelease 定义"用它做什么"的业务语义，Connector 定义"怎么连过去"的技术通道。三者分离，各司其职。**

---

## 3. ADR/架构如何设计

### 3.1 ADR-001：Capability 的定位（§7 分类法）

ADR-001 §7 明确定义了三层分类法：

| 概念 | 定位 | P0 角色 | ADR 状态 |
|------|------|---------|----------|
| **SkillRelease** | 面向 Agent Host 的对外消费与发布单元 | **P0 唯一对外消费与发布单元** | 已确认方向 |
| **Capability** | 受治理的可复用执行依赖与 Provider 契约 | 受治理的可复用执行依赖 | 已确认方向 |
| **Workflow** | 内部执行表示（WorkflowSpec v1/v2） | 内部执行表示，不对 Agent Host 暴露 | 已确认方向 |

关键约束（ADR-001 §7 要点）：

1. **对 Agent Host 暴露的稳定契约是 SkillRelease**，不是 Workflow。Workflow ID 不得充当对外契约。
2. **Capability 是 SkillRelease 与底层执行之间的受治理依赖**，P0 不将其作为 Agent Host 直连 API。
3. **Workflow 是内部实现细节**。未来格式替换不影响 SkillRelease 稳定性。
4. SkillRelease 和 Capability 的对外 wire 契约**当前未完全实现**。

> 💡 **为什么 Capability 不是 Plugin？**
>
> Plugin 是"即插即用"的——插上去就能跑。Capability 是"受治理契约"——先声明、再绑定、后执行。区别如同"U盘"（Plugin）vs"医院专科能力认证"（Capability）。

### 3.2 ADR-001 §6：控制面与执行面

Capability 的治理依赖控制面/执行面分离：

| 平面 | 职责 | Capability 相关 |
|------|------|----------------|
| 控制面 | 做出并记录策略决策 | Capability 注册、scope 审批、版本冻结、生命周期管理 |
| 执行面 | 执行期间落实已下达决策 | 在 SkillRelease 执行上下文中调用 Capability |
| 硬约束 | 执行面**不得放宽**控制面决策 | Connector 调用必须在已授权 execution context 内 |

### 3.3 ADR-003（docs/adr）：Capability × Industry 正交模型

ADR-003（docs 版）冻结了一个关键约束：**Capability 与行业正交**。

```
                    Industry（行业维度）
                    ┌────────┬────────┬────────┐
                    │ 零售   │ 金融   │ 制造   │
   ┌──────────────┼────────┼────────┼────────┤
C  │ knowledge.q  │  ✓     │  ✓     │  ✓     │  ← 能力跨行业复用
a  ├──────────────┼────────┼────────┼────────┤
p  │ workflow.ex  │  ✓     │  ✓     │  ✓     │
b  ├──────────────┼────────┼────────┼────────┤
i  │ vision.*     │  ✓     │  -     │  ✓     │  ← 部分行业不适用
l  └──────────────┴────────┴────────┴────────┘
t
y（能力维度）
```

硬约束（ADR-003 §2.2）：

1. **Capability ID 中禁止出现行业词**：`langchat.retail.*` 一律拒绝。
2. **Industry 标签不允许进入 Capability descriptor**。
3. Capability 清单 = `capability/catalog.py` 中的 `CapabilityRegistry` + `skill_release/registry.py`。
4. Industry 清单 = `docs/adr/industries.yaml`。

> **为什么正交？** 如果能力绑定行业，同一个"知识查询"能力在零售和金融就是两份代码。当能力升级时，要改 N 份。正交之后，能力只管"能不能做"，行业只管"在哪用"。

### 3.4 ADR-004 §8：Connector 的定位

ADR-004 §8 定义了 Connector 的架构位置：

> **Connector 是 Platform Governance Plane 登记、策略约束、版本管理、审计和部署边界共同治理的集成资源。Connector 的存在或被登记不等同于其拥有业务执行授权。**

Connector 的硬约束（ADR-004 §8.2）：

| 约束 | 说明 |
|------|------|
| **只在 SkillRelease execution context 内可用** | 脱离该上下文，Connector 不可调用 |
| **不可被 Channel/Gateway/Runtime 直接调用** | 这些组件不拥有业务执行授权 |
| **不可被 External Orchestrator 直接调用** | 编排器也必须走 SkillRelease |
| **P0 只允许 Class A、HTTP、单跳、read-only** | 最小化风险范围 |

ADR-004 §4.1.1 记录的遗留迁移路径：

| 遗留路径 | 入口 | 迁移目标 | 优先级 |
|----------|------|----------|--------|
| E3 SPA workflow | `/api/spa/chat/.../workflow` | 经 SkillRelease canonical invoke 执行 | P1 |
| E4 Public Chat | `/api/public/chat/{slug}` | 关闭或同 E3 | P1 |
| E6 Capability API invoke | `/api/capability/v1/invoke` | **已移除**，经 SkillRelease 执行 | 已完成 |

> **重要事实**：Capability API 的 `/invoke`、`/invoke_stream`、`/executions/*` 端点已在 E6 migration 中**完全移除**。当前 Capability API 只提供 `/list_capabilities` 和 `/describe_capability` 两个元数据查询端点。

### 3.5 Capability Resolution（ADR-004 §6.3）

ADR-004 §6.3 定义了"受治理的能力解析"：

> 平台可以提供受治理的 Capability Resolution 能力，用于解析 canonical SkillRelease 已声明的 Capability 依赖、版本、适用范围或路由信息。

关键限制：
- **不构成新的业务执行入口**
- **不代表授权事实**
- **不接受外部执行请求**
- **不直接访问 Connector、Provider 或客户业务系统**
- 解析结果仍必须通过 SkillRelease 执行流程生效

---

## 4. 当前代码如何实现

### 4.1 Capability 层：`capability/catalog.py`

文件路径：`apps/backend/langchat/capability/catalog.py`

这是 Capability 注册管理的核心。整个文件约 160 行，极其精简。

#### CapabilityDescriptor（能力描述符）

```python
# catalog.py 节选
class CapabilityDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)  # 冻结！
    
    capability_id: str          # 如 "langchat.knowledge.query"
    capability_version: str     # 如 "v1"
    lifecycle: Literal["draft", "published", "deprecated"]
    input_schema: dict          # JSON Schema 描述输入
    output_schema: dict         # 七字段输出 Schema
    execution_mode: list        # ["sync", "stream"] 等
    effects: Literal["read", "write", "destructive"]
    required_scopes: list       # 如 ["capability:knowledge:read"]
    approval_policy: Literal["none", "runtime_human_approval"]
    provider: str               # 如 "langchat"
    runtime_binding: dict       # E6 后统一为 {}
    deprecation_metadata: dict | None
```

**设计要点**：
- `frozen=True`：Pydantic 模型冻结，创建后不可修改字段
- `extra="forbid"`：禁止额外字段，防止隐式扩展
- `capability_id` 必须匹配 `^[a-z0-9]+(\.[a-z0-9]+)*$`——不允许行业词

#### CapabilityRegistry（能力注册表）

```python
class CapabilityRegistry:
    def register(self, descriptor: CapabilityDescriptor) -> None:
        # 注册新能力
    
    def list_all(self, scopes_filter=None) -> list[CapabilityDescriptor]:
        # 按 scope 过滤列出已发布能力
    
    def deprecate(self, capability_id, version, *, reason, ...) -> CapabilityDescriptor:
        # 废弃能力，记录后继者和日落日期
```

**不可变性保障**（`catalog.py` 关键逻辑）：

```python
# published 状态的能力，核心字段不可修改
if existing.lifecycle == "published":
    for field_name in _IMMUTABLE_FIELDS:
        if getattr(existing, field_name) != getattr(descriptor, field_name):
            raise ValueError(
                f"Cannot mutate {field_name} on published capability "
                f"{key[0]}@{key[1]}"
            )
```

这意味着：一旦 Capability 发布，其 `input_schema`、`output_schema`、`effects`、`required_scopes`、`approval_policy`、`provider`、`runtime_binding` 七个字段**永久不可修改**。要变更？只能废弃旧版本、发布新版本。

#### P0 预置能力（`_register_p0_capabilities()`）

```python
# 两个预置能力
# 1. 知识查询
_registry.register(CapabilityDescriptor(
    capability_id="langchat.knowledge.query",
    capability_version="v1",
    lifecycle="published",
    effects="read",
    required_scopes=["capability:knowledge:read"],
    approval_policy="none",
    provider="langchat",
    runtime_binding={},  # E6 后为空
))

# 2. 工作流执行
_registry.register(CapabilityDescriptor(
    capability_id="langchat.workflow.execute",
    capability_version="v1",
    lifecycle="published",
    effects="read",  # P0 强制 read_only
    required_scopes=["capability:workflow:execute"],
    approval_policy="runtime_human_approval",  # 有人审门控
    provider="langchat",
    runtime_binding={},
))
```

> ⚠️ **关键事实**：两个 Capability 的 `runtime_binding` 都是空对象 `{}`。这说明当前 Capability 层已经**完全剥离了执行逻辑**——它只是一个"治理描述符"，不再绑定任何运行时适配器。

### 4.2 Capability API 层：`capability/routes/__init__.py`

文件路径：`apps/backend/langchat/capability/routes/__init__.py`

当前只有两个端点：

| 端点 | 功能 |
|------|------|
| `POST /api/capability/v1/list_capabilities` | 按 scope 列出已发布能力 |
| `POST /api/capability/v1/describe_capability` | 查询单个能力详情 |

认证方式：`Authorization: Capability-Caller <token>`（HMAC 短期 token，最长 300 秒）

速率限制：默认 300 RPM per credential，60 秒滑动窗口

> **注意**：曾经存在的 `/invoke`、`/invoke_stream`、`/executions/*` 端点已**完全移除**。迁移指南在 `docs/api/capability-api.md` 中明确记录了迁移路径。

### 4.3 SkillRelease 层：`skill_release/`

SkillRelease 才是真正的"执行入口"。

#### SkillReleaseDescriptor（技能发布描述符）

文件路径：`apps/backend/langchat/skill_release/descriptor.py`

```python
class SkillReleaseDescriptor(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    skill_id: str               # 如 "langchat.w09.internal.service"
    version: str                # "v1"
    lifecycle: Literal["draft", "published", "deprecated"]
    required_scopes: list       # 如 ["skill_release:invoke"]
    effect_policy: Literal["read_only", "conditional_write"]
    human_review_gate: Literal["none", "conditional", "required"]
    workflow_binding: dict      # 绑定到哪个 Workflow
    display_name: str
    description: str
    input_schema: dict
    output_schema: dict         # 七字段输出
    visibility: Literal["platform", "tenant"]
    owner_tenant_id: int | None
```

**关键校验规则**（代码中的 model_validator）：

1. `required_scopes` 不允许包含 `"read_only"`——那是 `effect_policy`，不是 scope
2. `conditional_write` 必须搭配 `human_review_gate != "none"`——写操作必须有人审
3. `visibility="tenant"` 必须设置 `owner_tenant_id`——租户隔离

#### SkillRelease 绑定示例：W09（内部制度服务）

文件路径：`apps/backend/langchat/skill_release/bindings/w09.py`

```python
_W09_SKILL_ID = "langchat.w09.internal.service"

_w09_descriptor = SkillReleaseDescriptor(
    skill_id=_W09_SKILL_ID,
    version="v1",
    lifecycle="published",
    required_scopes=["skill_release:invoke"],
    effect_policy="read_only",      # P0 只读
    human_review_gate="conditional", # 敏感咨询走人审
    workflow_binding={
        "workflow_id": "mall-internal-service",
        "schema_version": "v1"
    },
    display_name="Mall Internal Service",
    description="内部员工服务：行政、财务、人事咨询",
)

def _register():
    from ..executors.w09_executor import w09_invoke
    get_registry().register_skill(_w09_descriptor, w09_invoke)
```

**关键观察**：SkillRelease 通过 `workflow_binding` 指向具体的 Workflow，通过 `effect_policy` 约束执行效果，通过 `human_review_gate` 控制人审。这是 Capability（治理描述）与执行（Workflow）之间的桥梁。

#### SkillReleaseRegistry（技能发布注册表）

文件路径：`apps/backend/langchat/skill_release/registry.py`

```python
class SkillReleaseRegistry:
    def register_skill(self, descriptor, executor_fn):
        """注册技能 + 绑定执行器"""
        
    def list_visible(self, caller_scope_grants, caller_tenant_id=None):
        """按 scope + 租户过滤可见技能"""
        
    def get_latest(self, skill_id):
        """获取最新版本（支持版本演进）"""
```

当前已注册的 W01-W09 + `workflow_execute` 共 10 个 SkillRelease。

### 4.4 Canonical Execution Service（受治理执行服务）

文件路径：`apps/backend/langchat/skill_release/canonical/execution_service.py`

执行流程（`CanonicalExecutionService.execute()`）：

```
1. prepare_canonical_execution(principal, command)
   → 校验身份、解析 descriptor、检查 idempotency
   
2. resolve_idempotency_replay(session, principal, prepared)
   → 幂等重放检查
   
3. 检查 HITL review_assignee
   → 如果需要人审但没配置审批人 → 直接失败
   
4. create_execution(session, ...)
   → 创建执行记录（含六维上下文）
   
5. enforce_read_only(descriptor)  ← 关键！
   → 如果 effect_policy != read_only → 阻断
   → 如果 workflow_binding 含 write 指标 → 阻断
   
6. dispatch_canonical_execution(principal, dispatch_command)
   → 实际执行
```

#### Read-Only 守卫：`canonical/read_only_guard.py`

文件路径：`apps/backend/langchat/skill_release/canonical/read_only_guard.py`

```python
_WRITE_INDICATORS = frozenset({
    "http_request",      # HTTP 写请求
    "db_write",          # 数据库写
    "tool_call",         # 工具调用
    "provider_conditional_write",  # Provider 条件写
})

def enforce_read_only(descriptor: SkillReleaseDescriptor):
    if descriptor.effect_policy != "read_only":
        raise ReadOnlyViolationError(...)
    _check_workflow_binding_writes(descriptor)  # 递归扫描 binding
```

这个守卫递归扫描 `workflow_binding` 的所有嵌套字段，发现任何写指标就阻断执行。这是 P0 阶段的安全底线。

### 4.5 MCP Connector 层

文件路径：`apps/backend/langchat/server/db/models/mcp_connection_model.py`

当前 LangChat 的"连接器"实现以 MCP（Model Context Protocol）为主：

```python
class MCPConnectionModel(Base):
    __tablename__ = "mcp_connection"
    
    id = Column(String(32), primary_key=True)
    server_name = Column(String(100))
    transport = Column(String(20))  # "stdio" 或 "sse"
    args = Column(JSON)             # 启动参数
    env = Column(JSON)             # 环境变量
    config = Column(JSON)          # 传输特定配置
    enabled = Column(Boolean)
    connection_status = Column(String(50))  # disconnected/connected/error
```

MCP Connector 支持两种传输方式：
- **stdio**：本地子进程，通过标准输入输出通信
- **sse**：远程服务，通过 Server-Sent Events 通信

MCP 管理面包括：
- `mcp_catalog`：平台 MCP 目录（预置可用工具）
- `workspace_mcp_binding`：跨工作空间共享 MCP
- `mcp_audit_log`：MCP 调用审计日志
- `MCPProfileModel`：MCP 全局配置（超时、工作目录、环境变量）

> **重要观察**：MCP Connector 当前是作为 Workflow 内部的工具调用节点存在的，**尚未完全对齐 ADR-004 §8 的"只在 SkillRelease execution context 内可用"约束**。这是当前的 Gap 之一。

### 4.6 完整链路：从 Capability 到企业系统

把所有部分串起来，当前代码中的完整链路：

```
Agent Host
    │ POST /v1/skill-releases/{skill_id}/invoke
    │ Authorization: Bearer <lc_ service_agent key>
    │ + 六维上下文 headers
    ▼
SkillRelease Canonical Execute（execution_service.py）
    │ 1. 准备阶段：校验身份、解析 descriptor
    │ 2. 幂等检查
    │ 3. HITL 检查
    │ 4. 创建执行记录
    │ 5. read_only 守卫
    │ 6. 分发执行 → 调用 executor_fn
    ▼
SkillRelease Executor（如 w09_invoke）
    │ 执行 Workflow（内部执行表示）
    │ Workflow 可能引用 MCP Connector
    ▼
MCP Connector（mcp_connection_model.py）
    │ stdio 或 sse 连接
    ▼
外部系统（知识库、ERP、CRM...）

Capability API（/api/capability/v1/）
    │ 独立于执行链路
    │ 只提供元数据查询
    └→ /list_capabilities：列出已注册能力
    └→ /describe_capability：查询单个能力
```

---

## 5. 差距分析（Gap Analysis）

### 5.1 目标态 vs 代码现实

| 维度 | ADR 目标态 | 当前代码现实 | Gap |
|------|-----------|-------------|-----|
| **Capability 执行** | 不直接执行，作为治理描述符 | ✅ `/invoke` 已移除，`runtime_binding={}` | 已对齐 |
| **Capability 发现** | 提供 metadata 查询 | ✅ `/list_capabilities` + `/describe_capability` | 已对齐 |
| **Capability × Industry 正交** | ID 禁止行业词 | ✅ `langchat.knowledge.query` / `langchat.workflow.execute` | 已对齐 |
| **SkillRelease 为唯一执行入口** | 所有执行经 canonical invoke | ⚠️ E3 SPA workflow / E4 Public Chat 遗留路径待迁移 | P1 待办 |
| **Connector 只在 SkillRelease 上下文内** | ADR-004 §8.2 硬约束 | ❌ MCP Connector 在 Workflow 内部，未独立治理 | **最大 Gap** |
| **Connector 审计** | 每次调用关联 execution context | ⚠️ 有 `mcp_audit_log` 但关联度不完整 | 改进中 |
| **P0 read-only 强制** | `effect_policy=read_only` | ✅ `enforce_read_only()` 运行时守卫 | 已对齐 |
| **Capability wire 契约** | 完整 spec 待定 | ❌ `/invoke` 已移除但替代路径 spec 未冻结 | 待决策 |
| **Provider 数据授权** | Provider 自治 | ❌ V1 待验证（ADR-001 §13 V1） | 待验证 |
| **六维上下文** | 全链路传递 | ✅ `CanonicalExecutionPrincipal` 携带六维 | 已对齐 |

### 5.2 最大 Gap：Connector 治理缺失

当前 MCP Connector 嵌在 Workflow 内部，意味着：

1. Connector 的调用不经过独立的 Capability Resolution
2. Connector 没有效果策略（effect_policy）独立校验
3. Connector 的版本管理依赖 Workflow 版本，没有独立生命周期
4. Connector 调用没有被 ADR-004 §8 描述的"Platform Governance Plane 登记"

**风险**：如果 Workflow 中嵌入了恶意 MCP 工具调用，`enforce_read_only` 只能检测 `_WRITE_INDICATORS` 中列出的关键词，无法覆盖所有可能的写操作形式。

**缓解措施**：P0 阶段通过 `effect_policy=read_only` + `read_only_guard.py` 的写指标扫描做基本防护，但长期需要独立的 Connector 治理层。

### 5.3 E6 迁移的完整性

E6 migration（关闭 Capability API 执行路径）已完成，代码事实：

- `capability/routes/__init__.py`：只剩 `/list_capabilities` 和 `/describe_capability`
- `capability/schemas.py`：`/invoke` 相关请求/响应 schema 已删除
- `capability/catalog.py`：`runtime_binding={}` 统一为空
- `capability-api.md`：有完整的迁移指南

迁移评估：✅ 完整、干净。

---

## 6. 今天多理解了什么

### 以前以为 → 现在知道

| # | 以前以为 | 现在知道 |
|---|---------|---------|
| 1 | Capability 就是 Plugin 的新名字 | Capability 是**治理描述符**，不包含执行逻辑。Plugin 是"即插即用的执行"，Capability 是"受治理的契约" |
| 2 | Capability 和 SkillRelease 是同一层 | 它们是三个不同层：Capability（治理描述）→ SkillRelease（业务执行单元）→ Workflow（内部实现） |
| 3 | Connector 就是 API Gateway | Connector 是"受治理集成资源"，只在 SkillRelease execution context 内可用。Gateway 是流量路由，Connector 是系统连接 |
| 4 | `/api/capability/v1/invoke` 还在 | 已在 E6 migration 中完全移除。Capability API 只剩元数据查询 |
| 5 | `runtime_binding` 指向具体执行器 | E6 后统一为 `{}`。执行逻辑全部转移到 SkillRelease 的 executor |
| 6 | read_only 只是个配置项 | 它是运行时守卫！`enforce_read_only()` 会递归扫描 workflow_binding 查找写指标 |
| 7 | 行业属性应该写在 Capability 里 | ADR-003 明确禁止。Capability 和 Industry 是正交维度 |
| 8 | P0 阶段已经有 Connector 治理 | 还没有。MCP Connector 当前嵌在 Workflow 内部，ADR-004 §8 描述的独立 Connector 治理层是目标态 |

---

## 7. 重新设计时是否仍这样做

### 问题：如果今天从零开始设计 LangChat，你还会把 Capability 和 SkillRelease 分开吗？

**回答：会，而且会更早分开。**

**理由 1：职责分离不可妥协。**

如果 Capability（描述"能做什么"）和 SkillRelease（描述"用它做什么"）合并，会出现：
- 同一个能力被 N 个 SkillRelease 引用时，要么 N 份重复描述，要么一个超级描述符承载所有场景
- 能力升级（如 knowledge.query 从 RAG 变为 hybrid search）导致所有 SkillRelease 被迫升级
- 治理粒度变粗——无法单独对"知识查询能力"做生命周期管理

**理由 2：Connector 独立治理应该更早做。**

当前代码中 MCP Connector 嵌在 Workflow 内部是最大的架构债。如果重新设计，应该：
- Connector 在 Platform Governance Plane 独立登记
- 每个 Connector 有自己的 effect_policy 和 scope
- SkillRelease 通过 Capability Resolution 引用 Connector（而不是直接嵌入 Workflow）
- Connector 调用链有独立审计（不仅仅是 `mcp_audit_log`）

**理由 3：E6 迁移证明了"Capability 不执行"是正确的。**

E6 migration 把 Capability API 的 `/invoke` 移除，说明"Capability 执行"本身就是一个错误设计。如果一开始就不给 Capability 执行能力，E6 迁移就不需要存在。

**不会改变的设计**：
- Capability × Industry 正交模型（ADR-003）
- Capability Descriptor 不可变（published 后核心字段冻结）
- read_only 守卫在运行时强制执行
- 六维上下文全链路传递

---

## 8. 每日工程日志

### 📅 2026-07-24

#### 新增认知
- Capability 不是执行层，是治理描述层。E6 migration 后 `runtime_binding={}` 是铁证
- ADR-004 §8 的 Connector 约束（只在 SkillRelease execution context 内可用）是目标态，当前 MCP Connector 嵌在 Workflow 内部是 Gap
- `enforce_read_only()` 的实现方式：递归扫描 `workflow_binding` 查找 `_WRITE_INDICATORS`，是运行时守卫不是配置校验
- SkillReleaseDescriptor 的三个 model_validator 约束：read_only 不是 scope、conditional_write 必须有人审、tenant visibility 必须有 owner

#### 修改认知
- 之前认为 Capability API 只是"受限"——实际是"完全移除了执行"，只剩元数据查询
- 之前认为 Connector = Gateway——实际 Connector 是"受治理集成资源"，Gateway 是"流量路由"
- 之前认为 `runtime_binding` 指向执行器——实际已统一为空对象

#### 确认
- Capability × Industry 正交模型已在代码中强制执行（ID 正则校验）
- P0 两个预置 Capability 的 effects 都是 `read`，approval_policy 分别是 `none` 和 `runtime_human_approval`
- Canonical Execution Service 的六步流程清晰可追踪

#### 遗留
- E3 SPA workflow / E4 Public Chat 遗留路径未迁移（P1 待办）
- Provider 数据授权证明（V1）未取得
- Capability / SkillRelease 完整 wire 契约未冻结

#### 技术债
- MCP Connector 未独立治理——当前作为 Workflow 内部节点存在
- `_WRITE_INDICATORS` 是枚举式检测，无法覆盖所有可能的写操作形式
- Connector 的版本管理和生命周期依赖 Workflow，缺乏独立性

#### 下一步
- 明天（Day6）画完整链路图：用户意图 → SkillRelease → Workflow → Capability → Connector → 企业系统
- 标出链路上每一步的输入输出和治理检查点
- 周日 Virtual CTO Review：评估链路完整度和最大风险点

---

## 9. 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| **Capability** | /ˌkeɪpəˈbɪləti/ | 能力 | 受治理的可复用执行依赖与 Provider 契约，描述"能做什么" |
| **CapabilityDescriptor** | /dɪˈskrɪptər/ | 能力描述符 | Capability 的 Pydantic 模型，frozen=True，published 后不可变 |
| **CapabilityRegistry** | /ˈredʒɪstri/ | 能力注册表 | 管理能力生命周期（draft→published→deprecated） |
| **Connector** | /kəˈnektər/ | 连接器 | 受治理集成资源，只在 SkillRelease execution context 内连接外部系统 |
| **SkillRelease** | /skɪl rɪˈliːs/ | 技能发布 | P0 唯一对外消费与发布单元，承载业务语义和执行绑定 |
| **SkillReleaseDescriptor** | — | 技能发布描述符 | 描述技能的 skill_id、effect_policy、human_review_gate 等 |
| **Plugin** | /ˈplʌɡɪn/ | 插件 | 传统 AI 平台的扩展模式，即插即用但治理薄弱。LangChat 明确不采用 |
| **Effect Policy** | /ɪˈfekt ˈpɒləsi/ | 效果策略 | `read_only` 或 `conditional_write`，约束 SkillRelease 执行效果 |
| **Human Review Gate** | /hjuːmən rɪˈvjuː ɡeɪt/ | 人审门控 | `none`/`conditional`/`required`，控制是否需要人工审批 |
| **Read-Only Guard** | /riːd ˈəʊnli ɡɑːd/ | 只读守卫 | 运行时递归扫描 workflow_binding 查找写指标的安全机制 |
| **Runtime Binding** | /ˈraɪntaɪm ˈbaɪndɪŋ/ | 运行时绑定 | Capability 中原指向执行适配器的字段，E6 后统一为 `{}` |
| **Orthogonal Facet** | /ɔːˈθɒɡənəl ˈfæsɪt/ | 正交维度 | Capability × Industry 两个独立维度，互不依赖 |
| **MCP** | /em-siː-piː/ | 模型上下文协议 | Model Context Protocol，LangChat 当前 Connector 的主要实现方式 |
| **Capability Resolution** | /ˌrezəˈluːʃən/ | 能力解析 | 解析 SkillRelease 已声明的 Capability 依赖，属治理辅助能力 |
| **Canonical** | /kəˈnɒnɪkəl/ | 规范的/标准的 | 指 SkillRelease 的标准执行路径，区别于遗留路径 |
| **Deprecation Metadata** | /ˌdeprəˈkeɪʃən/ | 废弃元数据 | 记录废弃原因、日落时间、后继能力 |
| **Idempotency** | /ˌaɪdəmˈpɒtənsi/ | 幂等性 | 同一请求重复执行产生相同结果，通过 Idempotency-Key 实现 |

---

## 10. 课堂练习与课后测试

### 课堂练习

**练习 1：Capability vs Plugin 对比分析**

请填写下表，对比 Capability 和 Plugin 在 6 个维度上的区别：

| 维度 | Plugin（传统模式） | Capability（LangChat 模式） |
|------|-------------------|---------------------------|
| 注册方式 | ? | ? |
| 版本管理 | ? | ? |
| 安全治理 | ? | ? |
| 执行权限 | ? | ? |
| 可组合性 | ? | ? |
| 审计追踪 | ? | ? |

**练习 2：追踪一次完整调用**

假设 Agent Host 要调用 `langchat.w09.internal.service` 查询"报销流程是什么"，请按顺序写出：

1. Agent Host 发出的 HTTP 请求（方法 + 路径 + 认证头）
2. CanonicalExecutionService 的六个步骤
3. read_only 守卫检查什么
4. 最终到达的 Workflow ID

**练习 3：识别违规**

以下 Capability ID 是否合规？如果不合规，违反了什么约束？

- a) `langchat.retail.knowledge.query`
- b) `langchat.vision.detect`
- c) `LangChat.Knowledge.Query`
- d) `langchat.finance.risk.assess`

### 课后测试

**Q1**：为什么 ADR-001 §7 说"对 Agent Host 暴露的稳定契约是 SkillRelease，不是 Workflow"？

A. 因为 Workflow 不稳定
B. 因为 Workflow 是内部实现细节，格式可能替换
C. 因为 SkillRelease 比 Workflow 更复杂
D. 因为 Workflow 没有 版本号

**Q2**：`enforce_read_only()` 函数检查以下哪些内容？（多选）

A. descriptor.effect_policy 是否为 "read_only"
B. workflow_binding 中是否包含 `http_request` 关键词
C. 调用者的 API Key 是否有效
D. workflow_binding 中是否包含 `db_write` 关键词

**Q3**：以下哪个描述了 Connector 与 SkillRelease 的正确关系？

A. Connector 可以独立于 SkillRelease 被调用
B. Connector 只在 SkillRelease 已授权 execution context 内可用
C. Connector 和 SkillRelease 是同一个东西
D. Connector 替代 SkillRelease 执行业务

**Q4**：E6 migration 的内容是什么？

A. 给 Capability API 添加了 `/invoke` 端点
B. 从 Capability API 移除了 `/invoke`、`/invoke_stream`、`/executions/*` 端点
C. 把 SkillRelease 合并进了 Capability
D. 给 Connector 添加了 MCP 支持

**Q5**：如果一个 SkillRelease 的 `effect_policy=conditional_write`，那么它的 `human_review_gate` 可以是哪些值？

A. "none"
B. "conditional"
C. "required"
D. B 和 C 都可以

---

## 11. 真实参考

### ADR 文档

| 文档 | 路径 | 关键章节 |
|------|------|----------|
| ADR-001 | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-001-LangChat-direct-to-agent-capability-platform.md` | §7 分类法、§6 控制面/执行面、§9 Provider 数据授权边界 |
| ADR-004 | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-004-interaction-platform-architecture.md` | §4.1 唯一执行入口、§4.1.1 遗留路径迁移、§8 Connector 边界 |
| ADR-003 (docs) | `/root/langchat/docs/adr/ADR-003-capability-industry-orthogonal-facet-model.md` | §2.2 正交硬约束、§2.3 Industry 清单 |

### 代码文件

| 文件 | 路径 | 关键内容 |
|------|------|----------|
| Capability 目录 | `apps/backend/langchat/capability/` | catalog.py, schemas.py, routes/__init__.py, errors.py |
| SkillRelease 目录 | `apps/backend/langchat/skill_release/` | registry.py, descriptor.py, bindings/, canonical/ |
| Read-Only 守卫 | `apps/backend/langchat/skill_release/canonical/read_only_guard.py` | `_WRITE_INDICATORS`, `enforce_read_only()` |
| 执行服务 | `apps/backend/langchat/skill_release/canonical/execution_service.py` | `CanonicalExecutionService.execute()` |
| MCP 模型 | `apps/backend/langchat/server/db/models/mcp_connection_model.py` | `MCPConnectionModel`, `MCPProfileModel` |
| Capability 中间件 | `apps/backend/langchat/server/auth/capability_middleware.py` | Token 验证 + 速率限制 |
| W09 绑定 | `apps/backend/langchat/skill_release/bindings/w09.py` | 内部制度服务 SkillRelease |

### 文档

| 文档 | 路径 |
|------|------|
| Capability API 文档 | `docs/api/capability-api.md` |
| Capability 路线图 | `docs/roadmaps/capability-roadmap.md` |
| SkillRelease 路线图 | `docs/roadmaps/skill-release-roadmap.md` |
