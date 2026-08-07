# 🧱 LangChat 心智模型 | Week10-Day6
## 📌 Governance 覆盖图 + 最大 Gap 清单（周六实战交付）

> **日期**：2026-08-08（周六）
> **角色**：Chief Architect Mentor — 实战交付日
> **交付物**：LangChat Governance 覆盖图 + PII & Compliance 现状 + 最大治理 Gap 排序

---

━━━ 1. 今日核心问题 ━━━

### 为什么 Governance 不是模块，而是横切所有模块的约束？

传统 ERP 思维：治理 = 权限模块，放在系统的一个角落。
LangChat 事实：治理 = 空气，每一层都呼吸它。

**如果去掉 Governance，LangChat 还能跑吗？** 能跑，但它是裸奔的 LLM。
**如果 Governance 只在一个模块里？** 那就像一栋楼只有大门有锁，每个房间都敞开。

今天的问题不是"Governance 在哪里"，而是 **"Governance 覆盖了哪些层，又漏了哪些层"**。

---

━━━ 2. 人话解释 ━━━

Jason，你在 MI 管 ERP 的时候，治理是这样的：

| ERP 治理 | LangChat 治理 | 本质 |
|---|---|---|
| 用户登录认证（AD/LDAP） | JWT + API Key + Ed25519 签名 | 身份认证 |
| 角色权限矩阵（RBAC） | 六维权限 + Scope + Permission | 授权 |
| 操作日志（Audit Trail） | AuditEvent + ExecutionSpan + Trace | 审计追踪 |
| 审批流（OA 流程） | Dual-Gate + Human Review Gate | 人工审批 |
| 数据脱敏（身份证、银行账号） | PII Redaction（Regex 策略） | 数据保护 |
| 数据保留策略（归档/销毁） | Trace Retention + Voice Retention | 生命周期 |
| 合规检查（SOX/等保） | Fail-closed + Evidence + Custody | 合规证据链 |

MI 的 ERP 治理是"模块化"的——每个子系统自己管自己。
LangChat 的治理是"横切式"的——**从 External Client 进来到 Enterprise System 出去，每一步都有治理检查点**。

---

━━━ 3. LangChat 架构位置 ━━━

用 ADR-007 的三段架构链，标注每一段的治理覆盖：

```
┌─────────────────────────┐    ┌──────────────────────────┐    ┌─────────────────────────┐
│    External Clients     │──▶│   Capability Runtime      │──▶│   Enterprise Systems    │
│     (L4 接入层)          │    │    (L2/L3 平台核)         │    │    (客户既有系统)       │
└──────────┬──────────────┘    └────────────┬─────────────┘    └──────────┬──────────────┘
           │                                │                             │
     ╔═════╧═════╗                ╔═════════╧════════╗           ╔═══════╧═════╗
     ║ 治理检查点 ║                ║   治理检查点      ║           ║  治理检查点  ║
     ╚═══════════╝                ╚══════════════════╝           ╚═════════════╝
     ① JWT 认证                   ④ 六维权限(SixDim)              ⑧ Tool Use 签名
     ② API Key + Scope            ⑤ PolicyBundle (effect/review)  ⑨ Webhook 回调验证
     ③ Rate Limiter               ⑥ Dual-Gate 授权算法
                                   ⑦ PII Redaction + Trace
```

**关键洞察**：治理检查点不是独立的"治理模块"，而是嵌入在每一层的入口处。

---

━━━ 4. ADR 依据 ━━━

### ADR-001 §2.1 平台定位
> "面向中大型企业，默认多租户、多工作区、JWT + API Key + **六维权限治理**"

治理是平台定位的四支柱之一，不是可选附加。

### ADR-007 §2.1 三段架构链
治理横跨三段：
- 段1（External Clients）：认证、限流
- 段2（Capability Runtime）：授权、审批、脱敏、追踪
- 段3（Enterprise Systems）：Tool Use 签名、Webhook 验证

### ADR-003 §2.2 正交约束
Capability ID 禁止行业词 → Governance 是平台级横切，不是行业级定制。

---

━━━ 5. 代码验证 ━━━

### 5.1 已有治理机制（代码事实）

| # | 治理维度 | 代码位置 | 状态 | 关键结构 |
|---|---|---|---|---|
| ① | **身份认证** | `server/auth/middleware.py` + `jwt_utils.py` | ✅ 完整 | JWT 解析 + API Key 验证 + Ed25519 签名 |
| ② | **六维权限** | `server/auth/six_dim_context.py` + `permissions.py` | ✅ 完整 | `SixDimExecutionContext` (frozen dataclass)：client_id, tenant_id, workspace_id, actor_id, actor_type, delegation_chain |
| ③ | **权限矩阵** | `server/auth/permissions.py` | ✅ 完整 | 23 个 Permission 常量 + 4 个角色 (platform_admin, tenant_admin, member, legacy_admin) → `ROLE_PERMISSIONS` 映射 |
| ④ | **API Scope** | `server/auth/scopes.py` | ✅ 完整 | 5 个 Scope (chat, knowledge_base, file_upload, admin, read_only) + 每 scope 限流配置 |
| ⑤ | **限流** | `server/auth/rate_limiter.py` | ✅ 完整 | `SlidingWindowRateLimiter`（Redis 滑动窗口）+ 默认速率配置 |
| ⑥ | **审计日志** | `server/auth/audit.py` + `db/models/audit_model.py` | ✅ 完整 | `emit_audit_event()` → `AuditEventModel` 表，记录 actor/action/resource/result/metadata |
| ⑦ | **执行追踪** | `observability/span.py` + `trace_read.py` | ✅ 完整 | 11 种 SpanKind（workflow_run, rag_retrieval, llm, capability_invoke, prompt_resolution 等）→ `ExecutionSpan` 数据结构 |
| ⑧ | **PII 脱敏** | `observability/pii_redaction.py` | ⚠️ 默认关闭 | `NoopRedactionStrategy`（默认）→ `RegexRedactionStrategy`（8 种 PII 模式：EMAIL/IP/PHONE/ID_CARD/BANK_CARD/URL_CRED），需手动启用 `PII_REDACTION_ENABLED` |
| ⑨ | **数据保留** | `observability/retention.py` | ✅ 基础完成 | Trace Payload + Voice 按天清理，`prune_old_traces()` + `count_old_traces()` |
| ⑩ | **PolicyBundle** | `supply_chain/policy_bundle.py` | ✅ 完整 | `effect_policy` (read_only / conditional_write) + `review_gate_policy` (none / conditional / mandatory) → Pydantic frozen model + 交叉验证 |
| ⑪ | **Dual-Gate 授权** | `skill_release/authorization/algorithm.py` | ✅ 完整 | Step 0-8 组合算法：classify → boundary → gate_reasons → create/get → frozen_replay → action_invocation，三种结果（Authorized / PendingHumanReview / TerminalReject） |
| ⑫ | **Read-Only Guard** | `skill_release/canonical/read_only_guard.py` | ✅ 完整 | P0 阶段所有 SkillRelease 必须 `effect_policy=read_only`，否则 `ReadOnlyViolationError` |
| ⑬ | **Prompt Custody** | `prompt_runtime/resolver.py` | ✅ 完整 | custody → evidence（hash 比对）→ verify（fail-closed），`ResolvedPromptTemplateVersion` (frozen Pydantic) |
| ⑭ | **FrozenExecutionContext** | `runtime/frozen_execution_context.py` | ✅ 完整 | v2: 三个 policy snapshot (floor + overlay + bindings) + 13+ pinned digests，immutable |
| ⑮ | **Realization Rollback** | `compiler/realize.py` | ✅ 完整 | Savepoint 隔离 → 失败时 ROLLBACK TO SAVEPOINT → 记录失败 + 审计 |

### 5.2 治理缺失/Gap（代码事实）

| # | 缺失维度 | 现状 | 风险 |
|---|---|---|---|
| ❌1 | **PII 默认关闭** | `NoopRedactionStrategy` 是默认值 | 生产环境如果忘记开启，用户敏感数据裸奔到 Trace |
| ❌2 | **Enterprise Systems 侧无签名** | Tool Use 调用外部系统缺少出站签名验证 | 无法证明"这个调用是 LangChat 发的"，企业系统侧无法验证来源 |
| ❌3 | **Webhook 回调验证不完整** | `server/webhook/emitter.py` 存在，但缺少接收方签名验证标准 | 回调可能被伪造 |
| ❌4 | **无数据分类分级** | 所有 Trace Payload 平等对待，没有按敏感度分级 | 高敏感数据（PII）和低敏感数据（性能指标）混在一起，保留策略一刀切 |
| ❌5 | **无合规报告生成器** | 审计事件被记录但没有自动化的合规报告 | 等保/SOX 审计时需要手工查询 |
| ❌6 | **跨租户隔离测试覆盖不足** | 有 `test_cross_workspace_isolation_security.py`，但边界 case 不全 | 多租户场景下的数据泄漏风险 |
| ❌7 | **Governance Health 指标缺失** | 没有"治理健康度"仪表盘 | 无法一眼看出治理是否正常工作 |

---

━━━ 6. Governance 覆盖图（核心交付物）━━━

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LangChat Governance Coverage Map                         │
│                    ────────────────────────────────                         │
│                                                                             │
│     Build Time                    Deploy Time              Runtime          │
│  ┌──────────────┐            ┌──────────────┐        ┌──────────────┐      │
│  │ Compiler     │            │ Supply Chain │        │ Runtime      │      │
│  │              │            │              │        │              │      │
│  │ ✅ Prompt    │───────────▶│ ✅ Policy    │───────▶│ ✅ SixDim    │      │
│  │   Custody    │            │   Bundle     │        │   Context    │      │
│  │   (hash→     │            │   (effect +  │        │   (6 fields  │      │
│  │    evidence) │            │    review)   │        │    frozen)   │      │
│  │              │            │              │        │              │      │
│  │ ✅ Realize   │───────────▶│ ✅ Release   │───────▶│ ✅ Dual-Gate │      │
│  │   Rollback   │            │   Gate       │        │   Authorize  │      │
│  │   (savepoint)│            │   (3-point)  │        │   (Step 0-8) │      │
│  │              │            │              │        │              │      │
│  │ ✅ Execution │            │ ✅ Compat    │        │ ✅ ReadOnly  │      │
│  │   Plan       │            │   Matrix     │        │   Guard      │      │
│  │   (frozen)   │            │              │        │              │      │
│  └──────┬───────┘            └──────┬───────┘        └──────┬───────┘      │
│         │                           │                       │              │
│         └───────────┬───────────────┴───────────────────────┘              │
│                     │                                                       │
│              ╔══════╧══════╗                                                │
│              ║  横切层      ║                                                │
│              ║             ║                                                │
│              ║ ✅ Audit    ║  (全覆盖：Build/Deploy/Runtime 都有审计)       │
│              ║ ✅ Trace    ║  (11 种 Span，全覆盖 Runtime 全链路)           │
│              ║ ✅ FEC      ║  (FrozenExecutionContext，3 个 policy snapshot)│
│              ║ ⚠️ PII     ║  (代码完整，但默认关闭！)                        │
│              ║ ⚠️ Retain  ║  (基础完成，缺分级保留)                          │
│              ║ ❌ Compliance║  (无自动化合规报告)                             │
│              ║ ❌ Outbound ║  (出站签名缺失)                                  │
│              ║   Sign      ║                                                  │
│              ╚═════════════╝                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

图例：  ✅ 已覆盖    ⚠️ 部分覆盖/默认关闭    ❌ 缺失
```

---

━━━ 7. 与传统方案比较 ━━━

### 治理架构对比

| 维度 | 传统 ERP 治理 | LangChat 治理 | 差异本质 |
|---|---|---|---|
| **认证** | 集中式（AD/LDAP 统一） | 分布式（JWT + API Key + Ed25519 签名） | LangChat 需要支持机器身份（Service Agent） |
| **授权** | 静态 RBAC | 动态六维 + PolicyBundle + Dual-Gate | LangChat 的授权在运行时实时计算，不是预先配置 |
| **审计** | 操作日志（事后查询） | ExecutionSpan（实时流式 + OpenTelemetry 导出） | LangChat 的审计是"执行过程"级别的，不只是"操作结果" |
| **审批** | 固定 OA 流程 | Adaptive（gate_reasons → conditional/mandatory） | LangChat 的审批根据操作风险等级动态决定 |
| **数据保护** | 数据库加密 + 字段脱敏 | PII Redaction（可插拔策略） | LangChat 的脱敏在 Trace 层，不是数据库层 |
| **合规证据** | 人工准备报告 | Custody → Evidence → Verify（自动证据链） | LangChat 的合规证据是代码自动生成的，不可篡改 |

**为什么差异这么大？** 因为 AI 应用有一个传统 ERP 没有的挑战：**LLM 的行为不确定**。
传统 ERP 的规则是确定的，治理只需管"谁能做什么"。
LangChat 还要管"AI 做了什么、为什么做、做对了吗"——这就是 Trace + Evidence 存在的原因。

---

━━━ 8. 架构师思考题 ━━━

### 如果你是 LangChat 的 Virtual CTO，PII 默认关闭这件事你会怎么处理？

**思考框架**：

1. **选项 A：改为默认开启** — 安全优先
   - 代价：可能误杀非 PII 数据（正则匹配精度不够），影响调试体验
   - 适合：面向等保/SOX 合规要求强的客户

2. **选项 B：保持默认关闭，但启动时强制配置** — 折中
   - `langchat init` 时必须选择 PII 策略（类似数据库初始化必须设密码）
   - 代价：增加部署复杂度

3. **选项 C：按租户/工作区配置** — 灵活
   - 不同租户有不同的合规要求（银行 vs 内部测试）
   - 代价：配置管理复杂

**Jason 的 ERP 经验映射**：MI 的 ERP 上线时，数据脱敏是强制的还是可选的？
如果 MI 的合同管理模块允许"不脱敏"，审计会怎么说？

> 💡 这不是技术选择题，是 **商业定位选择题**。
> 如果 LangChat 定位为"企业 AI 应用平台"（ADR-001），那 PII 保护不应该是 opt-in。

---

━━━ 9. 我的理解变化 ━━━

**以前以为**：Governance 是一个模块，和 Knowledge Base、Workflow 并列。

**现在知道**：Governance 是三个时间轴上的横切约束：

```
Build Time  →  Prompt Custody + Realization Rollback + Execution Plan (frozen)
                ↓
Deploy Time →  PolicyBundle + Release Gate + Compatibility Matrix
                ↓
Runtime     →  SixDim + Dual-Gate + ReadOnly Guard + Audit + Trace + PII + Retention
```

**以前以为**：LangChat 的治理和传统 ERP 差不多，就是权限 + 审计。

**现在知道**：LangChat 的治理多了一个维度——**AI 行为可追溯性**。
传统 ERP 不需要证明"系统为什么做了 X"（规则是人写的，系统只是执行）。
LangChat 必须证明"AI 为什么做了 X"（LLM 的决策路径是不确定的，必须用 Custody → Evidence → Verify 链路固化）。

**以前以为**：PII 脱敏是个配置项，打开就好了。

**现在知道**：PII 脱敏是一个完整的策略体系——`RedactionStrategy` Protocol → `NoopRedactionStrategy`（默认）→ `RegexRedactionStrategy`（内置 8 种模式）→ 自定义策略（entry point 插件）——但**默认关闭**是一个架构决策风险。

---

━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日预告

**Week10-Day7（周日）🔄 Virtual CTO Review**

> 如果只能修一个治理问题，先修哪个？

将进行：
1. 本周理解进度评分（1-10）
2. 五维评分（Architecture Quality / Code Health / ADR Consistency / Technical Debt / Developer Experience）
3. ADR Health Check（7 个 ADR 是否过时/需拆分/需冻结）
4. **最大治理 Gap 的优先级判定**：PII 默认关闭 vs 出站签名缺失 vs 合规报告缺失

### Semantic Layer 定位

```
Ontology → Domain Model → Capability → Skill
                              │
                    ┌─────────┴──────────┐
                    │  Governance 横切层  │
                    │                    │
                    │  Build:  Custody    │
                    │  Deploy: PolicyBundle│
                    │  Runtime: Dual-Gate │
                    │                    │
                    │  ← 今天的位置       │
                    └────────────────────┘
```

本周 Day1-Day5 学了 5 个治理关注点（Permission, Audit/Trace, Prompt Resolution, Fail-closed/Approval, Rollback/FEC），
今天的覆盖图把它们**拼成了一张完整的地形图**。
明天 Virtual CTO Review 会站在这张图上，决定"先修哪里"。

---

📝 **今日交付物清单**
- [x] Governance Coverage Map（三段架构 × 三时间轴 × 15 个检查点）
- [x] PII & Compliance 现状评估
- [x] 7 个治理 Gap 识别 + 风险评级
- [x] 与传统 ERP 治理对比
- [x] 架构师决策练习：PII 默认策略选择
