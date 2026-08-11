# 🧱 LangChat 心智模型 | Week11-Day3

**📌 当前主题：Connector 现状 — REST/MCP/Channel 各自到什么程度？**

**日期**：2026-08-12（周三）
**今日核心问题**：Connector 是 LangChat 最弱的部分吗？

---

## ━━━ 1. 今日核心问题 ━━━

### 为什么 LangChat 没有 "Connector" 这个模块？

在 v2 Target Domain Model 里，CapabilityRelease 与 Connector 边界协同（§7.8 SC-07），ADR-004 提到了 Connector 边界（§8），ADR-007 三段架构链的段 3 是 Enterprise Systems。但当你打开代码仓库搜索 "connector"——**找不到任何以 connector 命名的模块**。

真正的架构问题不是"Connector 做得好不好"，而是：**LangChat 的对外连接能力分散在三个互不相关的子系统里，它们甚至不知道彼此的存在。**

---

## ━━━ 2. 人话解释 ━━━

Jason，你在 ERP 行业 26 年，一定见过这种情况：

一个 ERP 系统要连外部——银行接口走"资金管理模块"、税务接口走"财务模块"、海关接口走"进出口模块"。每个模块都自己写了一套 HTTP 客户端、自己管重试、自己管超时。结果：

- 没有统一的连接配置管理
- 没有统一的监控面板
- 银行接口挂了，资金模块知道，CTO 不知道
- 三个模块重复写了三套 SSL 证书管理

LangChat 今天的情况一模一样。对外连接分散在三套系统里：

| 系统 | 它管什么 | 它不管什么 |
|---|---|---|
| **MCP Client**（mcp_kit） | Agent 调用 MCP 外部工具 | 不知道 Channel、不知道 Enterprise System |
| **Channel 子系统** | 微信/飞书/钉钉 **入站**消息 | 不是"连接企业系统"而是"接收用户消息" |
| **Outbound System Bridge** | 反向 mTLS 连客户私网 | **仅设计阶段，代码未实现** |

三者之间没有统一的 "Connector" 抽象。昨天说 Supply Chain 是最薄弱的层（11个对象只有2个≥7分）。今天看完 Connector 现状，结论更严重：**段3（Enterprise Systems）的连接能力，比段2（Supply Chain）更空白。**

---

## ━━━ 3. LangChat 架构位置 ━━━

```
ADR-007 三段式架构链：

 External Clients  ───►  Capability Runtime  ───►  Enterprise Systems
 (段1 接入层)               (段2 平台核心)             (段3 客户系统)
       │                         │                          │
       │                         │                          │
  Channel 子系统            MCP Client                ← 今天关注
  (微信/飞书/钉钉)          (工具调用出口)             这里最薄
  langchat-mcp-server       Platform Tools
  (MCP 对外暴露)            workflow runtime
```

**关键发现**：段 1（Channel + MCP Server）相对成熟，段 2（Platform Runtime）前面两周已经分析过。**段 3 是整条链最薄弱的一环**。

---

## ━━━ 4. ADR 依据 ━━━

### ① ADR-007 §2.1 三段定义

> 段 3 Enterprise Systems：客户既有业务系统。通过 Tool Use、SkillRelease W06/W07 类外部写操作、Webhook 子系统打通。

**代码现实**：Tool Use 存在（MCP Client + Platform Tools），Webhook 子系统存在（fire-and-forget 出站），但"打通"的程度差异极大。

### ② v2 Target Domain Model §7.8 SC-07 Capability

> Capability：受治理的可复用执行依赖或 Provider 契约描述。与 Connector 边界协同（继承 ADR-004 §8）。

**代码现实**：ADR-004 §8 的"Connector 边界"在代码中没有对应的模块。Capability Gateway 存在，但它面向的是 SkillRelease 调用，不是 Connector 接口。

### ③ Outbound System Bridge proposal

> LangChat 不持有客户私网 URL，也不能接受调用方指定任何 destination。客户 agent 主动建立 mTLS channel。

**代码现实**：设计文档非常严谨（反向 mTLS + 三层凭据 + scope claim wire protocol），但 **10 个 Phase-0 Gate 只关闭了 2 个**。状态仍是 `design-review-blocked`。Evidence deadline: 2026-08-22。

### ④ tools-call-external-provider-guard spec

> POST /tools/call SHALL reject external provider tools。External provider tools SHALL only be invocable through canonical SkillRelease。

**代码现实**：这是一个安全防护——直接工具调用端点拒绝外部 provider 工具。但这意味着**外部 provider 工具只能通过 SkillRelease 走 canonical execution path**。没有 canonical execution 的外部系统调用 = 被禁止。

---

## ━━━ 5. 代码验证 — 三个子系统的真实状态 ━━━

### ① MCP Client（mcp_kit）— Agent 的工具出口

**代码位置**：`langchain_langchat/agent_toolkits/mcp_kit/client.py`

**核心类**：`MultiServerMCPClient`

**支持的三种传输**：

| Transport | 用途 | 状态 | 证据 |
|---|---|---|---|
| `stdio` | 本地 MCP 进程（如 Claude Desktop 模式） | ✅ 可用 | `stdio_client(server_params)` |
| `sse` | Server-Sent Events 远程 MCP | ✅ 可用 | `sse_client(url, headers, timeout)` |
| `streamable_http` | FastMCP HTTP（lnkwebsite 等用） | ⚠️ **代码就绪，部署未就绪** | `streamablehttp_client(url, **kwargs)` |

**关键代码结构**：

```python
# 三种 transport 统一入口
async def connect_to_server(self, server_name, *, transport, **kwargs):
    if transport == "sse": ...
    elif transport == "stdio": ...
    elif transport == "streamable_http":
        # 新增：支持 httpx_client_factory（为 Phase 3 channel-backed transport 预留）
        if httpx_client_factory is not None:
            client_kwargs["httpx_client_factory"] = httpx_client_factory
```

**评分**：🟢 **6/10** — 传输层支持完整（三种），但：
- 无连接池管理（每次创建新 session）
- 无断线重连
- 无健康检查
- 无连接级权限隔离（所有 MCP server 的工具混在一起）
- `httpx_client_factory` 参数是 Outbound Bridge Phase 3 的预留口，但 Bridge 本身未实现

### ② Channel 子系统 — 入站消息处理

**代码位置**：`langchat/server/channels/`

**这不是"Connector"，是"入站适配器"**。Channel 子系统处理的是：
- 微信/飞书/钉钉用户发消息进来（Inbound）
- LangChat 回复消息出去（Outbound Reply）

**与 Enterprise System 的关系**：**零**。Channel 子系统不连接 ERP/CRM/OA，它连接的是 IM 平台。

| 模块 | 功能 | 成熟度 |
|---|---|---|
| `dispatch.py` | 入站消息 → RAG → LLM → 回复 | ✅ 生产级 |
| `adapters/` | 4 个平台适配器（微信/飞书/钉钉） | ✅ 生产级 |
| `dead_letter.py` | DLQ 重试 | ✅ 完整 |
| `crypto.py` | 平台加解密 | ✅ 完整 |

**评分**：🟢 **8/10** — 但与今天的主题无关。Channel 是段 1 的能力，不是段 3。

### ③ Outbound System Bridge — 连接客户私网

**代码位置**：设计文档 + 极少量骨架代码

**设计**：客户主动反向 mTLS → LangChat 按桥接绑定路由 → 客户 MCP middleware 验签消费

**Phase-0 Gate 状态（2026-08-12 快照）**：

| Gate | 描述 | 状态 |
|---|---|---|
| P0.0 | Loopback boundary 恢复 | ✅ Closed (2026-07-25) |
| P0.1 | Production egress / CA / cert lifecycle | ❌ Pending |
| P0.2 | Canonical provider audience URI | ❌ Pending |
| P0.3 | Dual-header middleware + replay store | ❌ Pending |
| P0.4 | Scope enforcement baseline (PR #6) | ❌ Pending |
| P0.5 | Fixed local target confirmation | ❌ Pending |
| P0.6 | FastMCP endpoint contract / fixture | ❌ Pending |
| P0.7 | Control-plane supersession | ❌ Pending |
| P0.8 | Canonical feedback reference URL | ❌ Pending |
| P0.9 | Phase-0 design review | ✅ Closed |
| **Deadline** | **2026-08-22T23:59:59Z** | ⏰ **10 天** |

**评分**：🔴 **2/10** — 设计非常严谨（三层独立凭据 + fail-closed + scope claim wire protocol），但 8/10 Phase-0 Gates 未关闭。如果 8/22 前证据不齐，自动冻结为 `externally-blocked`。

### ④ langchat-mcp-server — MCP 工具对外暴露

**代码位置**：`packages/langchat-mcp/`

这是 **LangChat 作为 MCP Server 向外部 AI 客户暴露工具** 的方向。46 个工具 / 11 个 toolset。

| 维度 | 状态 |
|---|---|
| 工具覆盖 | ✅ 46 个（模板/工作流/系统/知识库/助手/聊天/渠道/分析/KB高级/Trace） |
| 传输方式 | ✅ stdio + Streamable HTTP（`/api/v1/mcp`） |
| 认证授权 | ✅ API Key + scope-based + 审计日志 |
| Rate Limiting | ✅ 破坏性工具每租户限流 |
| CORS | ✅ Origin header 校验 |

**评分**：🟢 **8/10** — 这不是"Connector"，而是"Exposer"。方向相反。

### ⑤ Webhook 子系统 — Fire-and-forget 出站

**代码位置**：`langchat/server/webhook/`

**功能**：助手生命周期事件（assistant.created / assistant.updated 等）推送到外部 HTTP endpoint。

**安全**：HMAC-SHA256 签名 + SSRF IP pinning（`_PinningAsyncHTTPTransport`）。

**评分**：🟢 **7/10** — 成熟但范围极窄（只推事件，不是通用 Connector）。

---

### 📊 Connector 全景评分卡

```
连接方向          子系统              评分    能连什么
────────────────────────────────────────────────────
INBOUND           Channel 适配器      🟢 8    微信/飞书/钉钉消息
INBOUND           langchat-mcp-server 🟢 8    外部 AI 客户工具调用
OUTBOUND (工具)   MCP Client          🟡 6    MCP Server（stdio/sse/http）
OUTBOUND (事件)   Webhook             🟢 7    HTTP endpoint（事件推送）
OUTBOUND (系统)   Outbound Bridge     🔴 2    客户私网系统（仅设计）
────────────────────────────────────────────────────
统一定义层        Connector 抽象      🔴 0    不存在
```

**结论**：**LangChat 没有统一的 Connector 层。段 3 的连接能力分散在 5 个子系统里，每个各自管自己。**

---

## ━━━ 6. 商业地产映射 ━━━

### LangChat 连接能力 → MI CRE 场景

| LangChat 能力 | MI CRE 需求 | 现状 | 风险 |
|---|---|---|---|
| MCP Client（工具调用） | 调用 MI ERP 合同查询 API | ⚠️ 可连但无治理 | 无审计、无签名、MI 侧无法验证调用者 |
| Outbound Bridge | 连接客户私网 MI 系统 | 🔴 仅设计 | 无法连任何客户内网系统 |
| Webhook | 推送事件到 MI 系统 | ✅ 可用 | 但只有 assistant 生命周期事件，不是业务事件 |
| Channel | 微信用户咨询商场信息 | ✅ 可用 | 与 Enterprise System 无关 |

**具体场景：数字员工查询合同信息**

```
用户 → 微信 → LangChat Channel → Workflow Runtime → MCP Client → MI ERP API
                                                      ↑
                                                   这里是断点：
                                                   - 无 Connector 抽象
                                                   - 无 API 版本管理
                                                   - 无调用签名
                                                   - 无响应缓存
                                                   - 无断线重连
                                                   - MI 侧无法验证请求来源
```

**ERP 经验映射**：这就像 ERP 里没有"接口管理"模块——每个业务模块自己写 HTTP 客户端连外部系统。结果是：接口变更无管控、调用无监控、出了问题无法定位。

---

## ━━━ 7. 与传统方案比较 ━━━

### "连接企业系统"方案对比

| 方案 | 描述 | 代表 | LangChat 适合度 |
|---|---|---|---|
| **A. 通用 Connector 框架** | 定义 Connector 接口，每家企业系统一个 Connector 实现 | MuleSoft / Apache Camel | ⚠️ 过重，LangChat 是 AI 平台不是 ESB |
| **B. MCP-only** | 所有外部系统通过 MCP 暴露，LangChat 只做 MCP Client | Anthropic MCP 生态 | ✅ 长期方向，但当前 MCP 生态不成熟 |
| **C. Tool Use 直连** | 每个外部系统写成 Tool，Agent 直接调用 | LangChain / OpenAI Functions | ⚠️ 当前默认模式，但无治理 |
| **D. Reverse Bridge** | 客户主动反向注册 mTLS，LangChat 不直连 | Outbound System Bridge 设计 | ✅ 最安全的方案，但未实现 |
| **E. 混合：MCP + Bridge + Guard** | 工具调用走 MCP，私网系统走 Bridge，安全治理走 Guard | **LangChat 设计方向** | ✅ **正确路径**，但实施完成度最低 |

**为什么选 E（混合方案）？**

因为不同的连接场景需要不同的信任模型：

- **公开 API**（天气/搜索）→ MCP Client 直连，不需要 Bridge
- **客户 SaaS**（客户自有的 CRM SaaS）→ MCP Client + Provider Assertion 签名
- **客户私网**（MI 内网 ERP）→ 必须走 Reverse Bridge（客户主动 mTLS 出来）
- **LangChat 暴露给外部 AI**（Claude Desktop 调用 LangChat）→ langchat-mcp-server

**一个 Connector 抽象不可能覆盖四种信任模型。** 但当前的问题是：这四种模式之间**没有统一的服务发现、监控、配置管理**。

---

## ━━━ 8. 架构师思考题 ━━━

### 基础题

**如果 Outbound Bridge 在 8/22 前证据不齐被冻结，LangChat 怎么连客户私网系统？**

（提示：当前唯一的路径是 MCP Client 直连。但 MCP Client 没有 SSRF 防护、没有 Provider Assertion、没有 Bridge Channel。tools-call-external-provider-guard 阻止了非 canonical 路径的外部 provider 调用。如果 canonical execution 的外部 provider 工具需要连客户内网——**这条路走不通**。）

### 进阶题

**你是 LangChat CTO。团队提议：在段 2 增加一个 "Connector Service" 统一管理所有出站连接（MCP + Webhook + Bridge）。你要不要做？**

考虑因素：
1. 统一 Connector 是否违反 ADR-007 §2.2.6（不允许在链路上插入独立段）？
2. 如果 Connector 是段 2 内部模块而非独立段，它和 Capability Gateway 的职责边界在哪？
3. 如果不做统一 Connector，5 个子系统各自演进，3 年后会出现什么问题？
4. Dify / LangGraph 有没有 Connector 层？它们怎么解决这个问题？

### 挑战题

**Outbound System Bridge 设计了三层独立凭据：mTLS（通道）、Bearer（客户本地 MCP 认证）、Assertion（LangChat 委托授权）。为什么不用一层 mTLS + Bearer 搞定？多出 Assertion 层的价值是什么？**

（提示：如果 Bearer 足够，为什么 MI 的 ERP 要信任这个 Bearer 是"LangChat 委托的"而不是"某人偷了 Bearer 自己调用的"？Assertion 解决的是**委托证明**，不是身份证明。）

---

## ━━━ 9. 我的理解变化 ━━━

### 以前以为 → 现在知道

**1. 以前以为**：Connector 是 LangChat 的一个模块，和 Knowledge Base、Workflow 并列。
**现在知道**：**LangChat 没有 Connector 模块**。连接能力分散在 5 个子系统里：MCP Client（工具出口）、Channel（入站消息）、langchat-mcp-server（MCP 暴露）、Webhook（事件推送）、Outbound Bridge（客户私网，仅设计）。它们之间没有统一接口、统一配置、统一监控。

**2. 以前以为**：Outbound Bridge 是 Connector 的正式名字，即将实现。
**现在知道**：Outbound Bridge 只覆盖**客户私网**这一种场景。它不覆盖公开 API 调用、不覆盖 SaaS 集成、不覆盖事件推送。即使 Bridge 全部实现，LangChat 仍然没有统一的 Connector 层。而且 Bridge 的 10 个 Phase-0 Gate 只关了 2 个，8/22 deadline 前大概率被冻结。

**3. 以前以为**：MCP Client 三种传输都支持（stdio/sse/streamable_http），连接能力应该没问题。
**现在知道**：传输层确实可用，但**连接治理层完全空白**——无连接池、无断线重连、无健康检查、无连接级权限隔离。更关键的是：MCP Client 加载的工具直接注入 Agent，**Agent 调用这些工具时不受 Capability Gateway 管控**——这是一个治理 Gap。

**4. 以前以为**：昨天说 Supply Chain 是最薄弱的层（2/11 对象≥7分）。
**现在知道**：段 3（Enterprise Systems 连接）比段 2 更薄弱。Supply Chain 至少有对象定义和骨架代码，段 3 连"统一抽象"都不存在。**整条 ADR-007 架构链最弱的一环在段 2 → 段 3 的交界处**。

**5. 以前以为**："Connector 是 LangChat 最弱的部分吗？"——这个问题假设 Connector 存在但很弱。
**现在知道**：**Connector 不存在**。这才是最弱的形态——不是"有但差"，而是"没有却以为有"。

---

## ━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题

**Week11-Day4：Knowledge 现状 — 当前 RAG 实现 vs Knowledge Governance 目标**

> Today's Question: Knowledge 治理缺什么？

### Semantic Layer 定位

```
Ontology → Domain Model → Capability → Skill → Enterprise Systems
              ↑                                ↑
         昨天（Gap Matrix）              今天（Connector 现状）

明天关注：
    Capability → Knowledge → Runtime
                   ↑
              知识治理层
```

### 本周路线

| Day | 主题 | 状态 |
|---|---|---|
| D1 | Capability Inventory | ✅ 完成 |
| D2 | Gap Matrix | ✅ 完成 |
| **D3** | **Connector 现状** | **✅ 今天** |
| D4 | Knowledge 现状 | 明日 |
| D5 | 竞品对比 | 周五 |
| D6 | ⚡ 实施路线图 v1.0 | 周六 |
| D7 | 🔄 最终 Virtual CTO Review | 周日 |

---

*📝 Day 3 Engineering Log 见 engineering-journal.md*
