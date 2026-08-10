# 🧱 LangChat 心智模型 | Week11-Day2

**📌 当前主题：Gap Matrix — 目标态对象 vs 代码实现，逐个打分**

**日期**：2026-08-11（周二）
**今日核心问题**：哪个 Gap 最危险？

---

## ━━━ 1. 今日核心问题 ━━━

### 为什么 Gap Matrix 不是"完成度报表"，而是"风险地图"？

昨天我们做了 Capability Inventory——列出了现有能力清单。今天换一个视角：**不是问"有什么"，而是问"目标态域模型里定义的 30+ 个对象，代码到底实现了多少？"**

这里的核心区别：
- **完成度报表** → 项目经理视角（进度 X%）
- **Gap Matrix** → 架构师视角（**哪个差距会导致系统不可演化？**）

一个对象"只有 dataclass 没有 DB 模型"不是最大的风险。最大的风险是：**一个对象在目标态被定义为"不可变"，在代码里却是 mutable 的——这种语义 Gap 会在运行时爆炸。**

---

## ━━━ 2. 人话解释 ━━━

Jason，想象你在做 ERP 升级评估。

你有一张"目标态业务流程图"（To-Be），还有当前系统的实际模块清单（As-Is）。你不会只列"应收模块完成了 80%"——你会做一张 Gap 分析表：

| 目标流程 | 当前系统 | Gap | 风险等级 |
|---|---|---|---|
| 多组织合并报表 | 单组织 | 缺组织维 | 🔴 阻塞 |
| 实时库存预警 | 定时批处理 | 无实时通道 | 🟡 可过渡 |
| 信用额度控制 | 手工审批 | 无自动化 | 🟡 可过渡 |

LangChat 今天做的事一模一样。目标态域模型（v2 Target Domain Model）定义了 30+ 个对象，代码里有的已经实现得很好，有的只是骨架，有的根本不存在。

但**最危险的不是不存在的，而是"看起来存在但语义不对"的**——就像 ERP 里"应收模块"看起来有，但它的"信用控制"逻辑完全不是目标态要求的那套。

---

## ━━━ 3. LangChat 架构位置 ━━━

```
ADR-007 三段式架构链：

External Clients → [Capability Runtime] → Enterprise Systems
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
  Business Domain   Supply Chain       Runtime
  (语义层)          (制品链)           (执行层)
    │                  │                  │
    ├─ DigitalEmployee  ├─ Blueprint       ├─ Deployment
    ├─ AppContract      ├─ Compiler        ├─ FrozenExecContext
    ├─ Capability       ├─ SkillRelease    ├─ TrafficPolicy
    └─ KnowledgeColl.   ├─ ReleaseChannel  └─ Execution
                        └─ Build/Run

 ←—— 今天给每个对象打分 ——→
```

---

## ━━━ 4. ADR 依据 ━━━

**核心约束来自三份文档：**

### ① v2 Target Domain Model §1.2 目标态未实施警告（强制）

> 下列对象在本文档中冻结的是**目标态语义边界**，不是当前实现：
> DigitalEmployeeDefinition、ApplicationContract、BlueprintCandidate/Version、ExecutionPlanIR、SkillRelease v2（OCI 制品）、Build/BuildRun、Capability/CapabilityRelease、KnowledgeCollection/KnowledgeSnapshot、Policy/PolicyBundle、Attestation/Provenance/Signature、Registry、ReleaseChannel/PromotionEvent、Deployment/DeploymentRevision、TrafficPolicy、FrozenExecutionContext、RuntimeABI、Execution/Session/State/Memory、EvaluationSuite/ReleaseEvaluation/DeploymentEvaluation。

> **把上述任一对象写成"已落地"都违反文档状态约定。**

### ② Charter §5 四层架构

四层职责边界 + 层间约束（上层不绕过下层、同对象不跨层）。

### ③ ADR-001 §2 "企业 AI 应用平台"

> 平台要提供完整的应用生命周期：建模 → 构建 → 发布 → 监控 → 评估 → 迭代。

**Gap 的本质**：哪些对象还撑不起这个生命周期。

---

## ━━━ 5. 代码验证 — Gap Matrix（核心交付物） ━━━

### 评分标准

| 分数 | 含义 | 特征 |
|---|---|---|
| 🟢 **9-10** | 生产级 | 有 DB 模型 + 有 API + 有测试 + 语义匹配目标态 |
| 🟢 **7-8** | 功能完整 | 有关键逻辑 + 有测试，缺生产化（DB持久化/性能/边界） |
| 🟡 **5-6** | 骨架级 | 有 dataclass/type 定义，有基本逻辑，无完整生命周期 |
| 🟡 **3-4** | 起步级 | 有文件结构，但只有 stub 或接口定义 |
| 🔴 **1-2** | 空白 | 目标态定义了，代码里找不到对应实现 |

---

### Business Domain Layer（业务语义层）

| 对象 | 代码位置 | 行数 | DB模型 | 评分 | Gap 说明 |
|---|---|---|---|---|---|
| **DigitalEmployeeDefinition** | `business_domain/digital_employee_definition.py` | 182 | ✅ `digital_employee_model.py` | 🟢 **7** | 语义完整（生命周期 draft→published→deprecated→retired），引用关系正确。但**无 API 端点**，SPA 无法管理 DE 定义。缺 published 前的自动校验。 |
| **ApplicationContract** | `business_domain/application_contract.py` | 160 | ❌ 无独立表 | 🟡 **6** | dataclass + transport-agnostic 校验完整。但**无持久化**——Version 创建后不可修改这个不变量靠 dataclass frozen 保证，不靠 DB。缺 API 暴露。 |
| **ApplicationContractVersion** | 同上 | (同文件) | ❌ | 🟡 **5** | 同上。内容寻址 digest 计算正确，但没有 Registry 登记。 |
| **Capability（语义定义）** | `capability/catalog.py` | 242 | ✅ `capability_model.py` | 🟢 **7** | Catalog 有注册和发现。但 Capability 与 CapabilityRelease **未分离**——代码里 Capability 直接带执行逻辑，目标态要求 Capability（语义）和 CapabilityRelease（制品）分开。 |
| **KnowledgeCollection** | `server/knowledge_base/` | ~大量 | ✅ 多表 | 🟢 **8** | 这是当前最成熟子系统之一。但 KnowledgeCollection（可变逻辑集合）与 KnowledgeSnapshot（不可变快照）**未分离**——代码只有可变的 KB，没有不可变快照概念。 |
| **Policy** | 散落在 auth/middleware + capability_gateway | — | 部分 | 🟡 **4** | 六维权限存在但散落。没有统一的 Policy 对象 + Policy DSL。PolicyBundle（不可变策略束）**不存在**。 |

**Business Domain 小结**：语义定义层骨架完整，但"可部署的 API 表面"几乎为零——DE 定义和 Contract 都没有暴露给用户。

---

### Supply Chain Layer（制品链层）

| 对象 | 代码位置 | 行数 | DB模型 | 评分 | Gap 说明 |
|---|---|---|---|---|---|
| **BlueprintCandidate** | `blueprint/candidate.py` | 143 | ✅ (workflow_authoring) | 🟡 **5** | 候选制品概念存在。但**来自 EAC（External Authoring Client）的产出路径不通**——EAC builder 存在但没接入正式 review 流程。 |
| **BlueprintVersion** | `blueprint/version.py` | 148 | ✅ (compile_manifest) | 🟡 **6** | 版本化 + digest 正确。admission.py 有评审逻辑（106行）。但**评审标准硬编码**，不接 Policy/Attestation。 |
| **ExecutionPlanIR** | `compiler/core.py` + `orchestrator.py` | 815 | ✅ `execution_plan_model.py` | 🟢 **7** | 确定性构建链存在。canonicalization + realize + snapshot 完整。但**Compiler 版本未进 Build 定义**——当前 Compiler 版本隐含在代码里。 |
| **SkillRelease v2（OCI 制品）** | `skill_release/canonical/` | 3710 | ✅ 多表 | 🟢 **8** | 这是最厚的模块（3710行）。canonical execution、approval、rate limit、HITL、replay 全有。**但这是 v1 canonical 执行路径的强化，不是 v2 OCI 制品**。OCI 打包（supply_chain/oci/）只有 manifest + publish 骨架（~400行），没和 canonical execution 打通。 |
| **Build / BuildRun** | `supply_chain/build.py` | 188 | ❌ | 🟡 **5** | 构建定义存在。但 **BuildRun（一次具体构建执行）无独立持久化**——构建状态不追溯。 |
| **CapabilityRelease** | ❌ | — | ❌ | 🔴 **2** | **不存在**。Capability 直接绑定执行逻辑，没有"不可变发布版本"概念。这与目标态"CapabilityRelease 是 Capability 的不可变发布版本"严重 Gap。 |
| **KnowledgeSnapshot** | ❌ | — | ❌ | 🔴 **2** | **不存在**。KB 是可变的，没有"知识集合在某一时刻的不可变快照"概念。部署时无法 digest-pin 知识。 |
| **PolicyBundle** | `supply_chain/policy_bundle_runtime.py` | ~存在 | ❌ | 🟡 **4** | 运行时 fallback 逻辑存在（194行）。但 PolicyBundle 作为**不可变发布制品**不存在——它是个运行时工具，不是 Supply Chain 制品。 |
| **ReleaseChannel** | `supply_chain/release_channel/__init__.py` | 140 | ✅ 部分 | 🟡 **6** | 概念存在，有 DB 持久化。但 **PromotionEvent（Channel 移动的审计事件）不存在**。Channel 移动不留痕。 |
| **Attestation / Provenance / Signature** | `supply_chain/provenance.py` | ~存在 | ❌ | 🟡 **4** | Provenance 有基本结构。但 **Attestation（detached envelope）和 Signature（密码学签名）不存在**——没有制品签名链。 |
| **Artifact（基础设施原语）** | `supply_chain/oci/manifest.py` | ~存在 | ❌ | 🟡 **5** | OCI manifest 骨架存在。但**统一的内容寻址 Registry 不存在**——各对象各自持久化，没有统一的 digest → content 查找。 |

**Supply Chain 小结**：管道形状对了，但"不可变 + 内容寻址 + 签名链"三根柱子缺两根半。**最危险 Gap：CapabilityRelease 和 KnowledgeSnapshot 完全空白**——部署闭包无法完整 digest-pin。

---

### Runtime Layer（执行层）

| 对象 | 代码位置 | 行数 | DB模型 | 评分 | Gap 说明 |
|---|---|---|---|---|---|
| **Deployment** | `runtime/deployment.py` | 48 | ✅ `deployment_assignment_model.py` | 🟡 **5** | 只有 48 行——极薄。生命周期存在但功能极少。缺 Deployment 与 ReleaseChannel 的联动。 |
| **DeploymentRevision** | `runtime/deployment_revision.py` | 132 | ✅ `deployment_revision_model.py` | 🟢 **7** | 闭包概念完整：digest-pinned + FrozenExecutionContext 绑定。但**闭包内不含 KnowledgeSnapshot 和 PolicyBundle**（因为前者不存在）。**这是最危险的语义 Gap**。 |
| **TrafficPolicy** | `runtime/traffic_policy.py` | 84 | ❌ | 🟡 **5** | 策略定义存在。但**无实际流量路由实现**——策略定义了，没有引擎执行它。 |
| **FrozenExecutionContext** | `runtime/frozen_execution_context.py` | 305 | ❌ | 🟢 **7** | 不可变 + 完整字段（身份/授权/digest/trace/时间戳）。**最成熟的 v2 对象之一**。但无持久化——每次运行时构造，不存储。 |
| **RuntimeABI** | ❌ | — | ❌ | 🔴 **2** | **不存在**。Runtime 与制品之间的接口契约没有显式定义。当前靠 Python import 硬绑定。 |
| **Execution** | `skill_release/canonical/execution_service.py` | 260 | ✅ `skill_release_canonical_execution_model.py` + `capability_model.py:CapabilityExecution` | 🟢 **7** | 执行记录完整。有 trace_id、parent_execution_id、hop_depth、idempotency。**但 Execution 状态机不够完整**——缺 `cancelled` 状态。 |
| **Session / State / Memory** | `conversation_model.py` | — | ✅ | 🟡 **4** | 会话存在但**不满足目标态语义**。Session 不应该授予执行权限（当前隐式授予）。State 和 Memory 没有独立对象——都在 conversation 里。 |

**Runtime 小结**：FrozenExecutionContext 和 DeploymentRevision 是亮点。但**闭包不完整**（缺 Knowledge/Policy）+ **RuntimeABI 缺失**意味着制品和 Runtime 之间没有版本安全边界。

---

### Operations Layer（运营治理层）

| 对象 | 代码位置 | 评分 | Gap 说明 |
|---|---|---|---|
| **Registry（统一登记）** | 散落在各模块自己的 registry | 🟡 **5** | 各模块各自登记（capability catalog、blueprint registry、skill release registry），没有统一的 Registry family。 |
| **Catalog Projection** | `capability/catalog.py` | 🟢 **6** | 只读投影概念在 capability 层存在。但**只覆盖 Capability，不覆盖 SkillRelease/Deployment**。 |
| **EvaluationSuite** | `eval/runner.py` + `eval/gates.py` | 🟢 **7** | 评估跑分逻辑完整（959行）。ReleaseEvaluation 和 DeploymentEvaluation 的分离**部分实现**——auto_trigger 连接了 release 和 eval，但 DeploymentEvaluation（线上评估）几乎空白。 |
| **Observability** | `observability/` (1429行) | 🟢 **8** | span/emitter/retention/PII redaction/OTel export/Langfuse export 完整。这是治理基础设施的亮点。 |

---

### 📊 Gap Matrix 总览

```
                    实现完整度
                    ◄──低──────────高►
Business Domain     ▪️▪️▪️▪️▫️▫️▫️     4/6 对象 ≥7分
Supply Chain        ▪️▪️▫️▫️▫️▫️▫️     2/11 对象 ≥7分  ← 最薄弱
Runtime             ▪️▪️▪️▫️▫️▫️▫️     3/7  对象 ≥7分
Operations          ▪️▪️▪️▫️▫️▫️▫️     2/4  对象 ≥7分
```

---

## ━━━ 6. 商业地产映射 ━━━

### Gap Matrix → MI CRE 场景映射

| LangChat Gap | MI CRE 对应风险 | 等价 ERP 经验 |
|---|---|---|
| **CapabilityRelease 不存在** | 合同查询数字员工"能力"没有版本控制——更新合同 API 后旧数字员工行为变 | ERP 里"报表模板"无版本，报表结果不可复现 |
| **KnowledgeSnapshot 不存在** | 知识库（租赁政策文档）在部署时无法冻结——数字员工可能用"更新后的政策"回答旧问题 | ERP 里 BOM 无快照，生产订单引用的 BOM 被改了 |
| **PolicyBundle 不存在** | 合同审批规则无法打包发布——散落在代码各处 | ERP 里审批流硬编码，不能配置 |
| **RuntimeABI 不存在** | 制品和运行时之间无版本契约——升级 Runtime 可能破坏在运行的数字员工 | ERP 升级时自定义报表和标准模块的兼容性问题 |
| **Deployment 极薄** | 数字员工的"部署"概念不清——不清楚哪个版本在运行 | ERP 里"模块上线"管理混乱 |

**核心洞察**：这些 Gap 在 ERP 世界里都似曾相识——它们是**"配置管理"缺位的表现**。LangChat 的 Supply Chain 层本质上就是在做 AI 应用程序的"配置管理 + 变更管理"。

---

## ━━━ 7. 与传统方案比较 ━━━

### Gap 应对策略对比

| 策略 | 描述 | 适用场景 | LangChat 可行性 |
|---|---|---|---|
| **A. 全部补齐再上线** | 先实现所有目标态对象 | 绿地项目 | ❌ 30+ 对象全实现需要数月 |
| **B. 按风险优先级补齐** | 先补 🔴 级 Gap（CapabilityRelease、KnowledgeSnapshot、RuntimeABI） | 有存量系统的演进 | ✅ **推荐** |
| **C. 保持现状 + 文档标注 Gap** | 在代码中标注"此处偏离目标态" | 团队小、技术债可控时 | ⚠️ 短期可以，长期危险 |
| **D. 降低目标态标准** | 从 Target Domain Model 降级 | 目标态过于理想化时 | ❌ Charter 已 Frozen |

**为什么选 B？**

因为 Gap 的危险性不均匀：
- CapabilityRelease 缺失 → **中风险**（Capability 现在可用，但没有版本化发布，未来迁移成本高）
- KnowledgeSnapshot 缺失 → **高风险**（部署闭包不完整 = 不可复现执行）
- RuntimeABI 缺失 → **高风险**（Runtime 和制品之间没有版本边界 = 升级必爆炸）

**先修 KnowledgeSnapshot + RuntimeABI，CapabilityRelease 可延后一个 Sprint。**

---

## ━━━ 8. 架构师思考题 ━━━

### 如果你是 LangChat 的 CTO，给你 3 个 Sprint（6周），你怎么排序补 Gap？

约束条件：
- 当前有客户在用 v1 canonical execution
- 不能破坏现有功能
- 团队 3 人
- 每个对象从骨架到可测需要约 1 Sprint

**思考框架提示**：
1. 先问"哪个 Gap 会在运行时爆炸？"（安全性 > 完整性 > 美观性）
2. 再问"哪个 Gap 阻塞了最多下游工作？"
3. 最后问"哪个 Gap 最容易补？"（快速赢也是赢）

### 进阶题

**DeploymentRevision 闭包现在不包含 KnowledgeSnapshot。如果客户问："我上周三的数字员工回答了什么？"——你能回答吗？**

（提示：不能。因为没有 KnowledgeSnapshot，不知道上周三用的是哪个版本的知识库。）

---

## ━━━ 9. 我的理解变化 ━━━

### 以前以为 → 现在知道

**以前以为**：Gap 分析就是"列一个完成度百分比表"。

**现在知道**：Gap 分析的真正价值是识别**"语义 Gap"**——不是"有没有"的问题，而是"在那里但语义不对"的问题。

具体认知刷新：

1. **以前以为**：SkillRelease canonical execution 有 3710 行代码，应该很完善了。
   **现在知道**：那是 v1 canonical 执行路径（强大的），但 v2 的 SkillRelease 作为 OCI 制品（不可变打包）只有骨架。**同一个名字，不同的东西**。

2. **以前以为**：FrozenExecutionContext 是最有价值的 v2 创新。
   **现在知道**：FrozenExecutionContext 确实成熟（305行，评分7），但**它的闭包不完整**——没有 KnowledgeSnapshot 和 PolicyBundle 可引用。就像 ERP 里有"生产订单"但订单上缺"BOM 版本"字段。

3. **以前以为**：最危险的 Gap 是"不存在的对象"。
   **现在知道**：最危险的 Gap 是 **"DeploymentRevision 以为闭包完整，实际不完整"**——因为它给了一种虚假的安全感。

4. **以前以为**：Supply Chain 是最复杂的层。
   **现在知道**：Supply Chain 是**最薄的层**（11个目标对象，只有 2 个 ≥7分）。这是整个平台的最大风险。

---

## ━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题

**Week11-Day3：Connector 现状 — REST/MCP/Channel 各自到什么程度？**

> Today's Question: Connector 是 LangChat 最弱的部分吗？

### Semantic Layer 定位

```
Ontology → Domain Model → Capability → Skill
                           ↑
                    今天在这里（Gap Matrix）

明天关注：
Capability → Connector → Enterprise Systems
              ↑
          连接能力层和外部系统的桥梁
```

### 本周路线回顾

| Day | 主题 | 状态 |
|---|---|---|
| D1 | Capability Inventory | ✅ 完成 |
| **D2** | **Gap Matrix** | **✅ 今天** |
| D3 | Connector 现状 | 明日 |
| D4 | Knowledge 现状 | 周四 |
| D5 | 竞品对比 | 周五 |
| D6 | ⚡ 实施路线图 v1.0 | 周六 |
| D7 | 🔄 最终 Virtual CTO Review | 周日 |

---

*📝 Day 2 Engineering Log 见 engineering-journal.md*
