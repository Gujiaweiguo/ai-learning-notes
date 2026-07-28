# 🧱 LangChat 心智模型 | Week9-Day3
## 📌 当前主题：Deployment / DeploymentRevision — 为什么 Deployment 独立于 Release？

---

━━━ 1. 今日核心问题 ━━━

### 为什么 Deployment 独立于 Release？

**为什么不是：SkillRelease 一旦发布（Published），就直接跑起来？**

这个问题击中了 LangChat 架构里一个极其重要的分离：**制品（Artifact）和部署（Deployment）是两个生命周期。**

在传统 ERP 世界里，这就像问："为什么程序编译完了（.exe），不直接在生产服务器上跑？" —— 因为编译产物是通用的、可移植的，而生产运行需要绑定具体环境配置、数据库连接、权限策略、灰度策略。

LangChat 把这件事讲得更严格：**SkillRelease 是 Supply Chain 的产物（digest-pinned、不可变、跨环境可移植），DeploymentRevision 是 Runtime 的执行闭包（digest-pin 了 SkillRelease + 环境绑定 + 依赖快照 + 兼容矩阵）。两者 MUST NOT 互为别名。**

---

━━━ 2. 人话解释 ━━━

**用 Jason 26 年 ERP 经验讲：**

回想你在 MI 做 ERP 部署的场景。SAP 的一个 Enhancement Package 发布了（相当于 SkillRelease Published），但你不能直接让客户用它。你需要：

1. **确认这个包跟你当前的 SAP Basis 版本兼容**（→ Compatibility Matrix）
2. **在客户环境绑定具体的客户端编号、公司代码、工厂代码**（→ environment / scope）
3. **配置连接到客户的 Oracle 数据库**（→ binding_manifest_digest，不是明文 secret）
4. **决定是全量切换还是灰度**（→ TrafficPolicy）
5. **生成一个"这次上线的快照"**，出了问题能回滚到上一个快照（→ DeploymentRevision）

这个过程就是 **materialization（物化）**：把一个通用的制品，变成一个特定环境里的可执行实例。

LangChat 的 DeploymentRevision 更进一步：它不只是"配置一下"，而是把 **所有影响执行结果的内容** 都 digest-pin 到一个闭包里。这样 Runtime 执行时，不存在任何模糊地带——不存在"latest"、不存在"当前版本"、不存在运行时去查 Catalog 的情况。

**一句话：Release 回答"这是什么"，Deployment 回答"在哪儿、怎么跑、跑哪个版本"。**

---

━━━ 3. LangChat 架构位置 ━━━

在 v2 四层架构中，Deployment 和 DeploymentRevision 位于 **Runtime Layer**：

```
Business Domain Layer
  DigitalEmployeeDefinition ──引用──→ ApplicationContractVersion
                                           │
Supply Chain Layer                          │
  BlueprintCandidate → BlueprintVersion     │
    → Build/BuildRun → ExecutionPlanIR      │
    → SkillRelease v2 (OCI制品)             │
    → ReleaseChannel → PromotionEvent       │
                                           │
Runtime Layer  ◄───────────── 今天的焦点 ───┘
  Deployment (聚合生命周期)
    └─ DeploymentRevision (完整运行时闭包, 16字段)
       ↑
  TrafficPolicy (指向具体 Revision, cohort路由)
       │
  FrozenExecutionContext (不可变执行上下文)
       │
  RuntimeABI → Execution → Session → State/Memory

Operations Layer
  Registry (按主题权威) / Catalog Projection (只读)
```

**关键位置感**：DeploymentRevision 是 Supply Chain 和 Runtime 之间的 **唯一桥梁**。Supply Chain 产出 SkillRelease（通用制品），物化操作把 SkillRelease + 环境绑定 + 全部依赖变成 DeploymentRevision（特定执行闭包）。Runtime 只认 DeploymentRevision，不认 SkillRelease。

---

━━━ 4. ADR 依据 ━━━

### 4.1 Domain Model §8.1 RT-01 / RT-02（冻结决策）

**Deployment（RT-01）**：
- **定义**：部署聚合，承载一个 DigitalEmployeeDefinition 在某 scope 内的部署生命周期
- **职责**：持有 DeploymentRevision 序列，关联 DigitalEmployeeDefinition（语义锚点）
- **不承担**：不持有制品内容，不路由流量，不充当 ReleaseChannel
- **生命周期**：`Draft → Active → Suspended → Retired`

**DeploymentRevision（RT-02）**：
- **定义**：完整运行时闭包，digest-pin 一切影响执行结果的内容，**唯一可被流量路由的对象**
- **16字段闭包**：skill_release_digest、application_contract_version、runtime_abi_version、runtime_profile、manifest_schema_version、execution_plan_ir_schema_version、frozen_context_schema_version、required_artifact_media_types、knowledge_snapshot_digests、capability_release_digests、policy_bundle_digest、prompt_artifacts、model_artifacts、runtime_artifacts、environment、binding_manifest_digest
- **不可变量**：完整闭包（缺失任一项不合法）、不可修改（变更必须生成新 Revision）、唯一可路由性（只有非 evaluation_only 的生产 Revision 可被 TrafficPolicy 路由）

### 4.2 Artifact & Execution Spec §11（物化过程）

- 部署操作可接收 Channel 名作为输入，但必须在入口处 **一次性解析** 为精确 SkillRelease digest，之后 Channel 名不再进入后续流程
- `source_channel` 仅作 provenance 记录，不进入 runtime closure 的 digest 计算
- Materialization 必须验证目标 SkillRelease 处于 Published/Active 资格，且具备通过的 ReleaseEvaluation、Approval 和有效 Signature

### 4.3 ADR-007（平台架构链）

DeploymentRevision 属于段 2（Capability Runtime）内部对象。段 1 的 External Clients 通过 ApplicationContract 解析到 Deployment，再经 TrafficPolicy 选定具体 Revision，最终在 Runtime 内执行。

### 4.4 跨对象不变量（Domain Model §10.4）

- **不变量 2（闭包完整性）**：DeploymentRevision 必须 digest-pin §8.1 RT-02 定义的全部内容
- **不变量 3（流量精确性）**：TrafficPolicy 的所有路由目标必须是具体 DeploymentRevision ID + digest
- **不变量 4（Channel 与流量解耦）**：ReleaseChannel 移动不改变 TrafficPolicy 或已 Serving 的 DeploymentRevision
- **不变量 8（回滚前向性）**：回滚是前向操作——从历史 digest 闭包物化新 Revision，不改变历史对象状态

---

━━━ 5. 代码验证 ━━━

### 5.1 DeploymentRevision dataclass（核心结构）

文件：`/root/langchat/apps/backend/langchat/runtime/deployment_revision.py`

```python
CLOSURE_FIELDS = (
    "skill_release_digest",
    "application_contract_version",
    "runtime_abi_version",
    "runtime_profile",
    "manifest_schema_version",
    "execution_plan_ir_schema_version",
    "frozen_context_schema_version",
    "required_artifact_media_types",
    "knowledge_snapshot_digests",
    "capability_release_digests",
    "policy_bundle_digest",
    "prompt_artifacts",
    "model_artifacts",
    "runtime_artifacts",
    "environment",
    "binding_manifest_digest",   # ← 16个字段，精确匹配 AS §11.2
)

@dataclass(frozen=True)          # ← 不可变
class DeploymentRevision:
    revision_id: str
    skill_release_digest: str
    # ... 16个闭包字段
    evaluation_only: bool = True  # ← 默认隔离，生产部署显式设为 False
    source_channel: str = ""      # ← provenance only, 不进 digest

    @property
    def deployment_revision_digest(self) -> str:
        # SHA-256 over canonical JSON of 16 fields
        # source_channel 和 evaluation_only 被排除
```

**代码事实确认**：
- ✅ 16字段闭包与 AS §11.2 逐项匹配
- ✅ `frozen=True` dataclass 保证 Python 层面不可变
- ✅ `source_channel` 和 `evaluation_only` 不参与 digest 计算（AS §11.3）
- ✅ `config_hash` 是 `binding_manifest_digest` 的兼容别名

### 5.2 Deployment aggregate（生命周期聚合）

文件：`/root/langchat/apps/backend/langchat/runtime/deployment.py`

```python
@dataclass
class Deployment:
    deployment_id: str
    tenant_id: str
    workspace_id: str
    digital_employee_id: str
    references: set[str] = field(default_factory=set)  # Revision IDs

    def add_reference(self, revision: DeploymentRevision) -> None:
        if revision.evaluation_only:
            raise EvaluationOnlyReferenceError(...)  # ← 生产 Deployment 拒绝隔离 Revision
        self.references.add(revision.revision_id)
```

**代码事实确认**：
- ✅ Deployment 是生命周期聚合，只持有 Revision 引用（不是内容）
- ✅ `add_reference` 在引用点拒绝 evaluation-only Revision（安全门）
- ✅ Deployment 与 DigitalEmployeeDefinition 通过 `digital_employee_id` 关联

### 5.3 持久化模型（Append-Only）

文件：`/root/langchat/apps/backend/langchat/server/db/models/deployment_revision_model.py`

```python
class DeploymentRevisionModel(Base):
    __tablename__ = "v2_deployment_revision"
    revision_id = Column(String(64), unique=True, nullable=False)
    deployment_revision_digest = Column(String(80), unique=True)
    closure_json = Column(Text, nullable=False)  # ← 完整16字段闭包
    is_active = Column(Boolean, default=True)     # ← 回滚通过切换 is_active
```

**代码事实确认**：
- ✅ Append-only：新 Revision = 新行，不修改旧行
- ✅ 回滚通过标记 `is_active` 实现，不删除历史记录（前向语义）
- ✅ `closure_json` 是单行可重建内存 dataclass 的唯一真相源

---

━━━ 6. 商业地产映射 ━━━

### LangChat Deployment/DeploymentRevision → MI CRE 场景

| LangChat 概念 | MI CRE 场景映射 | 类比解释 |
|---|---|---|
| **SkillRelease** | MI 标准合同查询数字员工 v2.3（已签名发布包） | 通用能力包，可以在任何客户的 LangChat 上部署 |
| **Deployment** | 客户 A 的购物中心使用的"合同查询数字员工" | 特定客户环境里的部署实例，有自己的生命周期 |
| **DeploymentRevision** | 今天在客户 A 的 production 环境上线的具体快照 | 绑定了客户 A 的 ERP API 端点、租户权限、知识库快照、灰度策略 |
| **binding_manifest** | 客户 A 的 SAP IP、端口、API Key 版本、租户编号 | 环境绑定信息（不含明文 secret） |
| **TrafficPolicy** | 80% 流量到旧版本，20% 流量到新版本 | 购物中心运营团队先让 2 个商户试用新版本 |
| **回滚（前向）** | 发现 bug → 物化历史闭包为新 Revision → 新 TrafficPolicy 全量切回 | 不是"还原数据库"，而是"上线一个新版本（恰好与旧版本内容相同）" |
| **evaluation_only** | 在隔离环境测试合同查询新版本 | 评估 Revision 不能被生产 Deployment 引用 |

**关键洞察**：在 ERP 世界里，"升级"和"部署"经常混在一起——装了包就等于上了线。LangChat 强制把它们拆成两个独立步骤，因为：
1. 同一个 SkillRelease 可以在不同客户环境部署成不同的 DeploymentRevision
2. 同一个 Deployment 可以有多个 Revision（灰度共存）
3. 回滚不碰 Supply Chain，只在 Runtime 层操作

---

━━━ 7. 与传统方案比较 ━━━

### 为什么 Deployment 独立于 Release？三种方案对比

| 维度 | 方案A：Release 直接跑（传统） | 方案B：Release + 配置文件（CI/CD 常见） | 方案C：LangChat 的 DeploymentRevision 闭包 |
|---|---|---|---|
| **部署表示** | Release tag = 部署版本 | Release + 环境变量/configmap | 独立 DeploymentRevision 对象，16字段闭包 |
| **环境绑定** | 写死在 Release 里 | 运行时注入环境变量 | digest-pin 到闭包的 binding_manifest_digest |
| **依赖锁定** | 不锁定（用 latest） | 部分锁定（Docker image tag） | 完全锁定（所有依赖精确 digest，不允许 range/latest） |
| **兼容矩阵** | 不检查 | 手动检查或 CI 脚本 | 闭包内含 RuntimeABI + schema 版本元组 |
| **回滚** | 切回旧 tag（但配置可能已变） | 重新部署旧版本（依赖可能已漂移） | 物化新 Revision（闭包完整，确定性回滚） |
| **灰度** | 困难（只有一个版本在线） | 需要额外工具（如 Argo Rollouts） | 原生支持（多个 Revision 通过 TrafficPolicy 共存） |
| **审计** | 只有部署日志 | CI/CD pipeline 记录 | 每个 Revision 是不可变审计对象，Provenance 可追溯 |
| **可移植性** | 差（环境写死） | 中（配置外置但依赖不锁定） | 高（制品可移植，闭包精确） |

**为什么选方案C？**

核心原因：**AI 应用的执行结果不确定性远超传统软件。** 传统软件只要版本对，行为就确定。AI 应用还受 prompt、模型版本、知识库快照、策略叠加影响。如果 DeploymentRevision 不把这些全部锁死，就无法做到"同一个闭包 → 同一个执行结果"，也就无法做可靠的灰度对比和回滚。

---

━━━ 8. 架构师思考题 ━━━

### 思考题（CTO 级）

**场景**：你是 LangChat 平台的架构师。客户 A（大型商业地产集团，20 个购物中心）使用你的平台运行"合同查询数字员工"。现在客户提出一个需求：

> "我希望在总部数据中心运行 v2.3（新功能），同时在 3 个新开业的购物中心试运行 v2.4-beta（AI 推荐条款功能），其他 17 个购物中心继续用 v2.3。如果 v2.4-beta 效果不好，一键回滚到 v2.3。"

**请思考**：
1. 这个场景需要几个 SkillRelease？几个 Deployment？几个 DeploymentRevision？几个 TrafficPolicy？
2. "一键回滚"在 LangChat 架构里具体是什么操作序列？
3. 如果 v2.4-beta 引入了一个新的 Capability（条款推荐），这个 Capability 的 CapabilityRelease 需要在什么时机被 digest-pin 到 DeploymentRevision？
4. 客户说"试运行"——这意味着什么？是 evaluation_only 还是生产灰度？两者的区别是什么？

> 提示：关注 DeploymentRevision 闭包的 environment 字段和 TrafficPolicy 的 cohort 路由能力。

---

━━━ 9. 我的理解变化 ━━━

**以前以为**：Deployment 就是把代码部署到服务器上，是一个运维动作，不是架构对象。Release 和 Deployment 是"发布"这一个动作的前后两步。

**现在知道**：

1. **DeploymentRevision 是 Runtime 层最重要的架构对象**，不是运维概念。它是一个不可变的、内容寻址的完整执行闭包。它的16个字段锁死了"这次执行用了什么、跑了什么、在什么环境下跑的"。

2. **Release 和 Deployment 的分离不是流程偏好，是架构刚性约束**。SkillRelease 是通用制品（跨环境可移植），DeploymentRevision 是特定实例（绑定到具体环境）。合并它们意味着：每次环境变更都要重新走 Supply Chain（构建、评估、签名），这是不可接受的。

3. **回滚不是"还原"，而是"前進到一个与历史内容相同的新版本"**。这保证了审计链不断裂——你不修改历史，只创造新的决策记录。在 AI 应用里，这特别重要：因为知识库快照、策略叠加都可能已经变化，即使 SkillRelease digest 相同，物化出的新 Revision 也可能与历史不同。

4. **evaluation_only 是一个安全护栏**，不是调试工具。它阻止评估期的 Revision 被生产流量触达，从架构层面防止"测试版本意外服务真实用户"的事故。

---

━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题

**Week9-Day4：ReleaseChannel / TrafficPolicy — 为什么需要灰度？不能一次全量？**

今天学了 DeploymentRevision 是"完整运行时闭包"，明天学 TrafficPolicy 如何控制多个 Revision 之间的流量分配。关键问题：为什么不直接把 TrafficPolicy 做成 Deployment 的属性？为什么 TrafficPolicy 必须独立演进？

### Semantic Layer 定位

```
Ontology（本体论）
  └─ Domain Model（域模型）
       ├─ Deployment ──────── 今天的焦点：部署生命周期聚合
       │    └─ DeploymentRevision ── 完整运行时闭包（16字段）
       │
       ├─ ReleaseChannel ──── 昨天学过：晋升指针（Supply Chain）
       │
       ├─ TrafficPolicy ───── 明天学习：流量路由策略（Runtime）
       │
       └─ FrozenExecutionContext ── 后天学习：不可变执行上下文
```

**DeploymentRevision 是链上的"锚点"**：它把 Supply Chain 的一切产出（SkillRelease + CapabilityRelease + KnowledgeSnapshot + PolicyBundle）和 Runtime 的环境绑定（binding_manifest）冻结成一个不可变快照。没有 DeploymentRevision，Supply Chain 的制品就无法进入 Runtime 执行——它是两个世界之间唯一的合法通道。

---

*📅 2026-07-29（周三）| Week9-Day3 | Deployment / DeploymentRevision*
