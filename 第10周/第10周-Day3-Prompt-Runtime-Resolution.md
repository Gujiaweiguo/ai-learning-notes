# 🧱 LangChat 心智模型 | Week10-Day3
## 📌 Prompt Runtime Resolution：为什么 Prompt 必须经过 custody→evidence→verify？

---

━━━ 1. 今日核心问题 ━━━

### 为什么 Prompt 不能直接从数据库取出来用？

更精确地问：**在一个企业 AI 平台里，当工作流执行到一个节点需要 prompt 时，为什么不能直接 `SELECT content FROM prompt_template WHERE name='refund'`？为什么要经过一条 custody → evidence → verify 的完整链路？**

这个问题之所以重要，是因为它直接关系到**生产级 Agent 平台的信任边界**。如果 prompt 可以被随意读取、没有版本锁定、没有完整性验证，那么：

- 运维修改了 prompt 内容 → 已经编译通过的工作流行为就悄悄变了
- 跨租户/跨工作区的 prompt 泄露 → 企业安全合规出问题
- 编译时的 prompt 和运行时的 prompt 不一致 → 审计无法回答"执行时用的是哪个版本"

LangChat 的回答是：**Prompt 是制品（artifact），不是配置（configuration）。** 它必须经过和代码一样的 custody（托管）→ evidence（证据）→ verify（验证）链路，才能在运行时被加载。

---

━━━ 2. 人话解释 ━━━

用 Jason 26 年 ERP 经验来讲：

传统系统里，prompt（或者模板、配置文案）就像一个数据库里的配置项——谁都能改，改了立即生效。就像 ERP 里的"打印模板"，运维直接在后台改了就行。

但 LangChat 把 prompt 当成**制品**来管理，就像 ERP 里的"凭证模板"——一旦审核通过、发布生效，就不能随意修改。要改？走变更流程，创建新版本，重新编译、重新发布。

关键区别在于一条**证据链**：

1. **Custody（托管）**：Prompt 内容存入 `PromptTemplateVersion` 表，不可变（immutable）。就像凭证过账后不能修改，只能红字冲销。
2. **Evidence（证据）**：编译器在编译工作流时，把 prompt 的 `content_hash`（SHA-256）记录到 `WorkflowVersion.resolved_prompt_evidence_json` 字段。就像审计报告里记录"本次审核基于凭证版本 X，哈希值 Y"。
3. **Verify（验证）**：运行时加载 prompt 时，用存储的 hash 和编译时记录的 hash 做比对。如果不一致 → **直接报错，拒绝执行**。就像出纳付款时核对审批单上的金额和实际凭证金额——不匹配就停止。

这就是 **fail-closed**（开关闭 = 报错）：不做 fallback，不尝试"找到最接近的版本"，不静默继续。hash 不匹配 = 执行中止。

---

━━━ 3. LangChat 架构位置 ━━━

在 LangChat 的完整链路图上，Prompt Runtime Resolution 位于 **Runtime 执行层和知识资源层之间**：

```
用户意图 → ApplicationContract → Blueprint → Compiler → ExecutionPlan
                                                      ↓
                                            WorkflowVersion（含 evidence_json）
                                                      ↓
                                    Runtime 执行每个 Node
                                                      ↓
                                    ┌─────────────────┴──────────────────┐
                                    │                                    │
                              [普通 Node]                         [引用 Prompt 的 Node]
                              inline prompt_template              ResourceReference(kind="prompt", version=3)
                                                                      ↓
                                                              ┌─ lookup_evidence_for_reference()
                                                              │   从 WorkflowVersion.resolved_prompt_evidence_json
                                                              │   取出编译时记录的 content_hash
                                                              │
                                                              ├─ resolve_prompt_template_version()
                                                              │   1. 加载 PromptTemplateVersion 行
                                                              │   2. hash 比对（fail-closed）
                                                              │   3. 返回 frozen ResolvedPromptTemplateVersion
                                                              │
                                                              └─ 替换 node 的 inline prompt_template
                                                                  → 传给 LLM
```

位置解读：Resolver 是 **Runtime 和 Prompt 存储之间的守卫**。没有它，Runtime 直接读数据库；有了它，Runtime 必须经过证据验证才能拿到 prompt 内容。

---

━━━ 4. 核心代码验证 ━━━

### 源码位置：`langchat/prompt_runtime/`

```
prompt_runtime/
├── __init__.py     # 公共 API 导出
├── resolver.py     # 核心解析器（~300行）
└── errors.py       # 类型化错误体系（~120行）
```

### 4.1 核心函数签名

```python
# resolver.py
def resolve_prompt_template_version(
    session: Session,
    *,
    tenant_id: int,
    workspace_id: int,
    ref: str,                    # 逻辑模板名
    explicit_version: int | None, # 必须提供，None → 报错
    expected_hash: str,          # 来自编译证据的 SHA-256
) -> ResolvedPromptTemplateVersion:
```

注意三个关键约束：
- `explicit_version` 是必需的——`None` 直接 raise `PromptRetiredWithoutExplicitVersion`，**不做任何 DB 查询**
- `expected_hash` 是必需的——调用者必须从编译证据中提供，**不能传 None**
- 返回值 `ResolvedPromptTemplateVersion` 是 `frozen=True` 的 Pydantic model——**不可修改**

### 4.2 Custody → Evidence → Verify 链路

```python
# Step 1: 入口检查（Custody Gate）
if explicit_version is None:
    raise PromptRetiredWithoutExplicitVersion(...)  # 拒绝，不查 DB

# Step 2: 精确 scope 查找（Custody Load）
template, version = _load_template_and_version(
    session, tenant_id=tenant_id, workspace_id=workspace_id,
    ref=ref, explicit_version=explicit_version,
)
# → 查不到 = PromptNotFound（统一错误，不泄露跨 scope 存在性）

# Step 3: Hash 验证（Evidence Verify）
actual_hash = str(version["content_hash"])
if actual_hash != expected_hash:
    raise PromptHashMismatch(...)  # fail-closed！

# Step 4: 返回 frozen 结果
return _build_resolved(template, version)
```

### 4.3 Evidence 查找函数

```python
def lookup_evidence_for_reference(
    workflow_version: WorkflowVersion,
    *, name: str, version: int,
) -> str:
    """从 WorkflowVersion.resolved_prompt_evidence_json 恢复编译时的 content_hash。"""
    # 解析 JSON 数组 → 找 kind="prompt" + name + version 匹配项
    # 找不到 → PromptEvidenceMissing
    # 找到多个 → PromptEvidenceMissing（数据损坏）
    # 找到唯一 → 返回 content_hash（64 位小写 hex）
```

### 4.4 错误类型体系

```python
PromptResolutionError              # 基类
├── PromptNotFound                 # 找不到（含跨 scope 统一）
├── PromptRetiredWithoutExplicitVersion  # 缺少版本号
├── PromptHashMismatch             # Hash 不匹配
├── PromptRuntimeResolutionDisabled     # Feature flag 关闭
└── PromptEvidenceMissing          # 编译证据缺失/损坏
```

⚠️ **没有 `PromptCrossWorkspace`**：跨租户/跨工作区的命中和自身 scope 的未找到，返回**字节级一致**的 `PromptNotFound`——防止存在性探测攻击（existence oracle）。

### 4.5 Span 可观测性

```python
# 每次 resolve 都会 emit 一个 PROMPT_RESOLUTION span
with start_span(SpanKind.PROMPT_RESOLUTION, ...) as span:
    # 始终有：tenant_id, workspace_id, ref_name, outcome
    # 成功才有：template_id, version_id, version_number, content_hash
    # 失败时 success-only 属性是 absent（不是 None）
    # → absent 本身就是失败信号，不泄露 template 是否解析成功
```

prompt 内容**默认不记录**到 span。只有 `TRACE_PROMPT_CONTENT_ENABLED=true` 时才记录，且截断到 4KB。

---

━━━ 5. Fail-closed 设计深度解读 ━━━

### 什么是 Fail-closed vs Fail-open？

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| **Fail-open** | 出错时继续运行，降级处理 | 消费级应用（用户体验优先） |
| **Fail-closed** | 出错时立即停止，拒绝执行 | 企业级/安全关键系统（安全优先） |

LangChat 在 Prompt Resolution 中选择了 **fail-closed**：

| 场景 | Fail-open 会怎样 | Fail-closed（LangChat 选择）|
|------|------------------|---------------------------|
| Hash 不匹配 | 用新内容继续执行，行为已偏移 | `PromptHashMismatch` → 执行中止 |
| Feature flag off | 跳过 prompt 节点，静默改变语义 | `PromptRuntimeResolutionDisabled` → 显式报错 |
| Evidence 缺失 | 尝试从其他地方找 hash | `PromptEvidenceMissing` → 拒绝执行 |
| 版本号缺失 | 用最新版本（隐式 latest） | `PromptRetiredWithoutExplicitVersion` → 拒绝 |

**为什么企业场景必须 fail-closed？**

1. **审计要求**："执行时用的是哪个版本的 prompt？"——必须能精确回答。Fail-open 下这个问题的答案是不确定的。
2. **安全姿态**：Prompt injection 攻击可能修改存储的 prompt 内容。Hash 验证是最后一道防线——存储被篡改 = hash 不匹配 = 执行停止。
3. **确定性**：同一个 `WorkflowVersion` 在任何时候执行，必须用同一个 prompt 内容。Fail-open 会引入时间维度的不可预测性。

### Feature Flag 的 fail-closed 设计

```python
# 默认 PROMPT_RUNTIME_RESOLUTION_ENABLED = false
# flag off 时遇到 prompt reference → 报错，不跳过
# 不允许 "skip and continue"，不允许 "fall through to legacy inline path"
```

这个设计意味着：**不开 flag 的工作流如果带了 prompt reference，会直接失败**。这比"静默忽略"安全得多——静默忽略等于改变了工作流的语义。

---

━━━ 6. 商业地产映射 ━━━

把 Prompt Runtime Resolution 映射到 MI CRE 场景：

| LangChat 概念 | MI CRE 场景对应 |
|---|---|
| `PromptTemplateVersion`（不可变） | 合同模板的已审核版本（法务签发的标准合同文本） |
| `content_hash` | 合同文本的哈希值（防止被篡改） |
| `resolved_prompt_evidence_json` | 审批记录里附带的"基于合同版本 X，哈希 Y" |
| `resolve_prompt_template_version()` | 合同管理系统在生成合同时，从模板库加载+验证 |
| `PromptHashMismatch` | 模板被篡改 → 拒绝生成 → 法务介入 |
| `PromptNotFound`（统一错误） | 合同模板不存在 → 不泄露是"你的部门没有"还是"别的部门有" |

**实际场景**：MI CRE 的招商数字员工需要生成租赁合同。它引用的合同模板必须经过法务审核（custody），编译时记录模板哈希（evidence），运行时验证模板完整性（verify）。如果有人在模板库里偷偷改了条款——hash 不匹配，数字员工立即拒绝生成合同。

---

━━━ 7. 与传统方案比较 ━━━

| 方面 | 传统配置中心 | LangChat Prompt Custody |
|------|-------------|------------------------|
| 存储 | 可变配置项 | 不可变版本行（trigger 阻止 UPDATE/DELETE） |
| 版本 | 有版本但运行时取 latest | 必须指定 explicit_version |
| 验证 | 无 hash 验证 | SHA-256 双向验证（编译时 + 运行时） |
| 失败模式 | Fail-open（配置缺失用默认值） | Fail-closed（任何异常 = 停止） |
| 跨租户安全 | 依赖应用层检查 | 数据库查询层面统一为 PromptNotFound |
| 审计 | 需要额外日志 | Span 自带完整 provenance |

**为什么选这个设计？** 因为 prompt 在 AI 系统中的角色 ≈ 代码在传统系统中的角色。你不会让运维直接修改生产代码然后立即生效——prompt 也一样。

---

━━━ 8. 架构师思考题 ━━━

**场景**：LangChat 接入了三个企业的 ERP 系统（MI、SAP、Oracle），每个企业有各自的 prompt 模板。现在需要支持"共享模板"——某些通用 prompt（如"分析销售数据"）可以跨企业复用。

**问题**：
1. 共享模板存在哪个 tenant/workspace 下？
2. evidence 链如何跨 scope 建立和验证？
3. 如果共享模板被更新，依赖它的工作流需要重新编译吗？
4. 如何防止"共享模板"变成跨租户数据泄露的通道？

**提示**：回到今天的核心原则——`PromptNotFound` 的统一错误设计不是为了不方便，而是为了安全。共享模板需要一条新的 trust path，不能绕过 scope 隔离。

---

━━━ 9. 我的理解变化 ━━━

- **以前以为**：Prompt 就是 LLM 的输入文本，存数据库里取出来用就行
- **现在知道**：Prompt 是**制品**，有完整的托管（custody）、版本（version）、证据（evidence）、验证（verify）链路。它的安全级别应该和代码一样——不可变、可审计、可复现

- **以前以为**：Feature flag 是用来"灰度上线"的
- **现在知道**：Feature flag 在这里的作用是**安全姿态选择**——flag off 不是"功能未上线"，而是"明确拒绝执行带 prompt reference 的工作流"，防止静默语义变更

- **以前以为**：跨租户错误应该尽量详细，方便排查
- **现在知道**：安全场景下，**信息越少越安全**。统一为 `PromptNotFound` 不是偷懒，是防止存在性探测攻击的刻意设计——和 HTTP 401 统一所有认证失败原因一样

---

━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题：Fail-closed vs Fail-open 模式 + Approval（人审）

今天看了 fail-closed 在 hash 验证中的应用。明天扩展到更广的层面：
- LangChat 在哪些其他地方也选择了 fail-closed？
- 人审（Human Approval）是 fail-closed 的延伸——哪些操作必须有人类签字？
- 如果整个平台都是 fail-closed，会不会导致系统过于脆弱？（答案：不会，因为 fail-closed 不等于 fail-frequently——严格的验证让正常路径更可靠）

### Semantic Layer 定位

```
Ontology     → Prompt 是 Artifact，不是 Configuration
   ↓
Domain Model → PromptTemplateVersion（不可变制品）+ WorkflowVersion（携带 evidence）
   ↓
Capability   → resolve_prompt_template_version()（custody → evidence → verify）
   ↓
Policy       → PROMPT_RUNTIME_RESOLUTION_ENABLED + hash 必须匹配 + scope 统一错误
   ↓
Skill        → 数字员工执行工作流时，prompt 经自动验证后才注入 LLM
```

---

### 📖 Engineering Journal 追加

```
## 2026-08-05 W10-D3
### 今天最大的认知
Prompt Runtime Resolution 不是"读 prompt"的技术细节——它是**把 prompt 当制品管理**的治理决策。custody→evidence→verify 三步链路本质上是在回答："你怎么保证执行时用的 prompt 和编译时审核通过的是同一个？"

### 今天最大的坑
errors.py 里没有 PromptCrossWorkspace——这不是遗漏，是**刻意的安全设计**。跨 scope 的存在性泄露（"这个 prompt 在别的 workspace 有"）本身就是信息泄露。所有 scope 不匹配统一为 PromptNotFound，字节级一致。

### 今天最大的决策
LangChat 选择 fail-closed 不是"保守"，是"正确的安全姿态"。在企业场景中，静默继续比显式失败危险得多——因为静默失败不会被注意到，而显式失败会触发修复。
```

### 📝 课后测试

1. `resolve_prompt_template_version()` 收到 `explicit_version=None` 时会发生什么？会查 DB 吗？
2. 编译时的 `content_hash` 存在哪里？运行时从哪里取？
3. 为什么 `PromptHashMismatch` 的外部消息是固定字符串而不是包含 hash 值？
4. `ResolvedPromptTemplateVersion` 的 `frozen=True` 解决了什么问题？
5. Feature flag off 时，工作流遇到 prompt reference 会怎样？能否跳过？

### 📚 英文术语（10个）

| 术语 | 含义 |
|------|------|
| Custody | 托管——不可变存储 + 生命周期管理 |
| Evidence | 证据——编译时记录的 hash，用于运行时验证 |
| Verify | 验证——运行时 hash 比对 |
| Fail-closed | 失败时关闭（拒绝执行） |
| Fail-open | 失败时开放（降级继续） |
| Existence Oracle | 存在性探测——通过错误差异推断资源是否存在 |
| Content Hash | 内容哈希——SHA-256，64 位小写 hex |
| Immutable | 不可变——创建后不可修改 |
| Provenance | 溯源——执行的完整证据链 |
| Feature Flag | 功能开关——控制新行为的安全启用 |

### ✅ 学习进度

```
W1-W7: AI 基础 ████████████████████ ✅
W8: End-to-End Journey ████████████████████ ✅
W9: Domain Deep Dive ████████████████████ ✅
W10: Governance ██████░░░░░░░░░░░░░░░░ 🔥 Day3/7
    D1 Permission & Policy ✅
    D2 Audit & Trace ✅
    D3 Prompt Runtime Resolution ✅ ← TODAY
    D4 Fail-closed + Approval
    D5 Realization Rollback + FrozenExecutionContext
    D6 Governance 覆盖图
    D7 Virtual CTO Review
W11: Code Reality ░░░░░░░░░░░░░░░░░░░░
W12-13: Vision Intelligence ░░░░░░░░░░░░░░░░░░░░
W14+: CRE ERP ░░░░░░░░░░░░░░░░░░░░

并行轨道 PT-W2: Business Ontology Extraction ████░░░░░░░░░░░░░░░░ Day3/7
```
