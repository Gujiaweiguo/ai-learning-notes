# 🧱 LangChat 心智模型 | Week9-Day2
## 📌 SkillRelease：为什么它是唯一可部署单元？

📅 2026-07-28 周二

---

━━━ 1. 今日核心问题 ━━━

**为什么 SkillRelease 是唯一可部署单元，而不是 Blueprint、Capability 或 Workflow？**

这个问题触及 LangChat 架构的一个根本选择：在制品链上，到底哪一环才是"可以被 Runtime 消费、可以被流量路由、可以被 Agent Host 调用"的最小单元？

答案不是 Blueprint（它不可执行），不是 Capability（它是依赖，不是入口），不是 Workflow（它是内部实现，目标态要退役）。答案是 SkillRelease——一个经过完整制品链锻造、通过 Release Gate、签名发布的 OCI 制品。

━━━ 2. 人话解释 ━━━

用 Jason 26 年 ERP 经验来讲：

想象你是一个 ERP 产品公司的研发总监。你的团队写了很多代码模块（= Capability），设计了很多业务流程蓝图（= Blueprint），还有各种工作流配置（= WorkflowSpec）。但你不会把源代码直接发给客户安装。

你需要做什么？

1. 把代码编译成可执行文件（= Build → ExecutionPlanIR）
2. 打包成安装包，包含所有依赖锁（= SkillRelease packaging）
3. 通过 QA 测试（= Release Gate: Evaluation + Approval）
4. 数字签名，防止篡改（= Signature）
5. 发布到客户可以下载的渠道（= ReleaseChannel publication）

**SkillRelease 就是那个"经过签名认证的安装包"**。客户（Agent Host）只能通过这个安装包使用你的产品。他们不需要、也不应该接触到你的源代码或蓝图。

这就是 ADR-001 §4.5 冻结的核心原则：**"SkillRelease 是 P0 唯一对外消费与发布单元"**。

━━━ 3. LangChat 架构位置 ━━━

在 LangChat 的制品链上：

```
External Authoring Client
    ↓
BlueprintCandidate → (Admission + Review) → BlueprintVersion
    ↓
BuildRun (确定性构建, Compiler版本 + 依赖锁)
    ↓
ExecutionPlanIR (内部中间表示, 不可直接执行)
    ↓
SkillRelease v2 (OCI 制品, 唯一可部署单元) ← ★ 今天的主角
    ↓                    ↑
    ├── Release Gate (Evaluation → Approval → Signature → Publication)
    ├── ReleaseChannel promotion (环境晋升: dev → staging → prod)
    └── Deployment materialization → DeploymentRevision (运行时闭包)
         ↓
         TrafficPolicy 路由 → Runtime 在 FrozenExecutionContext 内执行
```

SkillRelease 处在** Supply Chain Layer 和 Runtime Layer 的交界处**：
- 往上看，它是制品链的终点——所有 Blueprint、Build、IR 都汇聚到这里
- 往下看，它是 Runtime 的入口——DeploymentRevision 闭包就是 digest-pin SkillRelease 的完整运行时快照

━━━ 4. ADR 依据 ━━━

### ADR-001 §4.5（文档事实）

> SkillRelease 是 P0 唯一对外消费与发布单元。不暴露 Capability / Workflow API。

这意味着：
- Agent Host 只能看到 SkillRelease，不能看到 Capability / Workflow / Blueprint
- 任何对 Agent Host 的暴露都必须经过 SkillRelease 包装

### ADR-003 v1.2（文档事实，G8-G10 通过）

冻结了 SkillRelease API 的 HTTP wire profile，5 个端点：

| 端点 | 用途 |
|------|------|
| `GET /v1/skill-releases` | 发现：列出 caller 可见的 SkillRelease |
| `GET /v1/skill-releases/{skill_id}` | 描述：获取单个 SkillRelease 的 metadata + input_schema |
| `POST /v1/skill-releases/{skill_id}/invoke` | 调用：同步 200 或 HITL 202 |
| `GET /v1/skill-releases/{skill_id}/executions/{id}` | 查询执行状态 |
| `POST /v1/skill-releases/{skill_id}/executions/{id}/respond` | 人审响应 |

关键约束：
- **HC-4**: P0 只读（`effect_policy=read_only`）
- **HC-5**: SkillRelease 是唯一对外消费与发布单元
- 存在性保护：无权调用的 skill_id 返回 404 而非 403（避免存在性泄露）

### ADR-005 D-5（已确认方向）：WorkflowSpec 退役

WorkflowSpec 当前是 SkillRelease 底层的执行态实现（`workflow/schema.py`），但目标态中 WorkflowSpec 要退役：
- cutover：W01-W09 逐个迁移到 v2 制品链
- retire：WorkflowSpec 从 Runtime 路径移除

这进一步强化了 SkillRelease 作为唯一可部署单元的地位——退役后，Runtime 底层只有 SkillRelease v2 制品，不存在其他执行路径。

### ADR-006 D-1（已确认方向）：DigitalEmployeeDefinition 不取代 SkillRelease

> DigitalEmployeeDefinition 是产品语义锚点，SkillRelease 是 Supply Chain 制品。两者通过谱系关联，不互为别名。

DigitalEmployeeDefinition 是"数字员工的产品定义"（谁、做什么、在哪些环境可用），但它不持有内容字节、不签发授权、不构造执行上下文。真正被执行的还是 SkillRelease → DeploymentRevision。

━━━ 5. 代码验证 ━━━

### 5.1 Canonical Router（当前事实）

文件：`/root/langchat/apps/backend/langchat/skill_release/canonical/router.py`

```python
canonical_skill_release_router = APIRouter(
    prefix="/v1/skill-releases", tags=["canonical-skill-release"]
)

# 五个端点与 ADR-003 一一对应：
# - list_canonical_skill_releases  (GET /)
# - describe_canonical_skill_release (GET /{skill_id})
# - handle_canonical_invoke          (POST /{skill_id}/invoke)
# - handle_get_execution             (GET /{skill_id}/executions/{id})
# - handle_respond_approval          (POST /{skill_id}/executions/{id}/respond)
```

Router 的 `_public_descriptor()` 函数把内部 `SkillReleaseDescriptor` 转换为对外 `CanonicalSkillReleasePublicModel`——这个转换隐藏了内部实现细节，只暴露 metadata + schema。

### 5.2 SkillRelease Registry（注册表）

文件：`/root/langchat/apps/backend/langchat/skill_release/registry.py`

Registry 是 SkillRelease 的发现机制——Agent Host 通过它来"看到"有哪些 SkillRelease 可用。Registry 不是事实源（Catalog 永远不是事实源），它是按主题权威的索引。

### 5.3 Workflow Bindings（当前执行态）

文件：`/root/langchat/apps/backend/langchat/skill_release/bindings/w01.py` ~ `w09.py`

当前 W01-W09 各自有一个 binding 文件，把 SkillRelease 绑定到底层 WorkflowSpec 执行。这就是 cutover 后要替换的部分——目标态是 SkillRelease v2 制品直接驱动 Runtime，不需要 WorkflowSpec binding。

### 5.4 数据模型

```
skill_release_canonical_execution_model.py   → execution 记录（六态状态机）
skill_release_canonical_review_assignee_model.py → HITL reviewer 分配
skill_release_approval_model.py              → 发布审批
workflow_skill_release_binding_model.py      → Workflow↔SkillRelease 绑定（退役目标）
```

━━━ 6. 商业地产映射 ━━━

| LangChat 概念 | MI CRE 场景 | 类比解释 |
|--------------|------------|---------|
| SkillRelease | "合同查询数字员工"的发布包 | 经过 QA、签名、可部署的技能单元 |
| skill_id | `cre.lease.query.v1` | 稳定的对外标识，类似 MI 模块编号 |
| input_schema | `{space_code: "A101", query_type: "lease_status"}` | 调用接口规范 |
| output_schema（七字段） | summary + references + next_actions + risk_flags... | 结构化回答，不是自由文本 |
| effect_policy = read_only | 只查不改，不写回 MI | 当前阶段只做查询，不修改合同 |
| human_review_gate | 敏感问题（租金/违约金）需人工审核 | 类似 MI 合同审批流 |
| ReleaseChannel | dev → UAT → production | 和 MI 的环境晋升一样 |
| DeploymentRevision | 某次部署的完整快照 | 类似 MI 版本发布时的"安装包+配置"冻结 |
| DigitalEmployeeDefinition | "招商运营数字员工"产品定义 | 定义身份和范围，但不是安装包本身 |

━━━ 7. 与传统方案比较 ━━━

| 维度 | 传统 ERP / SaaS | LangChat SkillRelease |
|------|----------------|----------------------|
| 对外暴露 | API endpoint，前后端耦合 | SkillRelease wire API（5 个端点），隐藏内部实现 |
| 版本管理 | 代码分支 + 发布日志 | OCI 制品 digest + semver + 制品链谱系 |
| 依赖管理 | pom.xml / requirements.txt | 精确依赖锁（digest-pinned，不允许 latest） |
| 环境晋升 | 手动部署 + 配置修改 | ReleaseChannel promotion（不自动改流量） |
| 回滚 | 还原数据库 + 替换代码 | 前向回滚：物化新 DeploymentRevision（digest 精确匹配历史） |
| 人工审核 | 工单系统，脱离执行链 | HITL 内嵌：202 挂起 → review_token → respond → 恢复 |
| 知识管理 | 文档系统 + 数据库 | KnowledgeSnapshot（不可变快照，digest-pinned） |

**为什么选 SkillRelease 而不是直接暴露 API？**

传统方案的问题：API endpoint 暴露了内部实现，版本升级时客户端可能被" silent break"，依赖管理混乱（你不知道谁在用什么版本）。

SkillRelease 的设计：
1. **封装性**：Agent Host 只看到 skill_id + input_schema + output_schema，看不到内部 Workflow/IR
2. **不可变性**：每次发布是一个不可变制品，digest 精确标识
3. **谱系可溯**：SkillRelease → ExecutionPlanIR → BlueprintVersion → BlueprintCandidate，完整链路
4. **治理内嵌**：effect_policy / required_scopes / human_review_gate 不是外挂，是 SkillRelease 的字段

━━━ 8. 架构师思考题 ━━━

**如果 MI 有 3 个不同租户（甲方不同、数据隔离），同一个"合同查询"SkillRelease 怎么部署？**

提示思考方向：
- 是每个租户一个 skill_id，还是一个 skill_id + 多个 Deployment？
- KnowledgeSnapshot 是共享的还是每租户一份？
- TrafficPolicy 怎么路由？
- 如果租户 A 需要升版但租户 B 不想升，怎么管理？

这不是考试题，是你在设计 LangChat × MI 集成时真实会遇到的问题。

━━━ 9. 我的理解变化 ━━━

**以前以为**：SkillRelease 就是一个 API endpoint 的包装，类似把 REST API 文档化。

**现在知道**：SkillRelease 是一个完整的制品——它不只是"接口定义"，而是包含了：
- 确定性构建产物（ExecutionPlanIR）
- 精确依赖锁（KnowledgeSnapshot digest + Capability digest + PolicyBundle digest）
- Release Gate 证据（Evaluation + Approval + Signature）
- 不可变生命周期（published → deprecated，不原地修改）

更关键的认知：**SkillRelease 的"唯一性"不是技术约束，而是治理约束**。技术上你当然可以直接执行 WorkflowSpec；但治理上，只有经过完整制品链锻造的 SkillRelease 才能保证可审计、可复现、可回滚。这和 ERP 里"只有经过 QA 的版本才能上生产"是同一个道理，只是 LangChat 把这个原则做到了架构层。

━━━ 10. 明日连接 + Semantic Layer ━━━

**明日主题**：Deployment / DeploymentRevision——为什么 Deployment 独立于 Release？

SkillRelease 是"可部署的制品"，但"部署"本身是另一个动作、另一个聚合。Deployment 承载的是"这个制品在某个环境中实际运行的状态"。Release 是制品 lifecycle，Deployment 是运行 lifecycle——两者分离。

**Semantic Layer 位置**：

```
Ontology（企业业务世界）
    ↓
Domain Model（17 个 Bounded Context）
    ↓
Capability Model（CRE BCM 能力地图）
    ↓
Skill Model（LangChat SkillRelease）← 今天
    ↓
Deployment / Runtime ← 明天
```

SkillRelease 是"能力被封装为可执行制品"的环节。在 Semantic Layer 链上，它连接了 Capability（能做什么）和 Deployment（在哪里运行）。

---

## 📝 Engineering Log

### 今天最大的认知
SkillRelease 的"唯一可部署单元"地位不是技术决定，而是治理决定。它把制品链上的所有治理（确定性构建、依赖锁、评估、审批、签名）汇聚到一个不可变制品上，让 Runtime 只需要消费这一个入口。

### 今天最大的坑
WorkflowSpec binding（W01-W09）当前是 SkillRelease 的底层执行态，但目标态要退役。这意味着当前代码事实和目标态设计之间存在"过渡期认知 gap"——不能假设当前代码已经实现了目标态。

### 今天最大的决策
理解了 SkillRelease 和 DigitalEmployeeDefinition 的分离原则：定义是"谁"，SkillRelease 是"什么"。一个数字员工定义可以引用多个 SkillRelease（不同版本、不同能力），但每个 SkillRelease 是独立的不可变制品。

---

*📅 Week 9 - Day 2 | LangChat Mental Model | 2026-07-28*
