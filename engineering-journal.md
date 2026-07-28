# LangChat Engineering Journal

> 每天一条，记录设计史。4周28天的认知演变。

---

## 2026-07-20（Week8-Day1：用户意图）

### 今天最大的认知
以前以为 LangChat 是"AI 运行时平台"，要负责编排所有系统。
现在知道 LangChat 是企业能力平台，被 Agent Host 直接调用，不做编排，不拥有业务数据授权。

### 今天最大的坑
OrchestratorAgent 曾经被写成"必经入口"，但它从未投入使用。ADR-001 §12 显式取代了这个表述。如果继续保留这个虚构中间层，所有 PRD 和 OpenSpec 都会基于不存在的链路展开。

### 今天最大的决策
Agent Host 和 LangChat 是"直接调用"关系。Orchestrator 是可替换角色，不是指定系统。

---

## 2026-07-21（Week8-Day2：ApplicationContract）

### 今天最大的认知
以前以为 ApplicationContract 就是接口定义——写清楚输入输出就够了。
现在知道 Contract 是业务治理一等对象：传输无关、版本不可变、治理语义（effect_policy / required_scopes / human_review_gate）嵌入其中。Contract 和 Version 两层分离是多版本共存的基础。

### 今天最大的坑
当前 SkillReleaseDescriptor 同时承担了三个角色（业务语义 + 设计描述 + 实现绑定），在 P0 阶段是合理简化，但随着能力增长会成为演进瓶颈。拆分的触发点应该是：当第一个 conditional_write 能力出现时，混合模型就无法只靠 frozen=True 保证安全了。

### 今天最大的决策
如果重新设计，会在 P0 阶段就引入 ContractVersion 概念，即使只有一个版本。因为后期从"没有版本"迁移到"有版本"的改造成本远大于一开始就加一层。

---

## 2026-07-22（Week8-Day3：Blueprint → Compiler → ExecutionPlanIR）

### 今天最大的认知
以前以为 Blueprint 是一份配置文件，Runtime 直接读取执行。
现在知道 Blueprint 是制品（artifact），有版本、digest、生命周期。Blueprint 和 ExecutionPlanIR 之间隔着 10 阶段确定性 Compiler——不是简单翻译。Compiler 的存在不是多余：它保证了同一输入永远产出同一输出。ExecutionPlanIR 是内部不可编辑的——不存在"手动 patch IR"的合法路径。

### 今天最大的坑
发现当前 10 阶段流水线大多为 pass-through stub（WP-03 阶段），每个阶段只是标记 "done" 并记录 Provenance entry，没有真实编译逻辑。这意味着代码验证了框架结构正确性，但实际编译能力需要后续 WP 填充。代码骨架和实际能力之间存在认知陷阱——看到 10 个阶段函数就以为它们在"做事"。

### 今天最大的决策
ExecutionPlanIR 的不可编辑性是整个确定性链条的支点。一旦允许"IR hotfix"，信任基础就崩塌了——无法审计、无法复现、无法回溯。如果重新设计，这条规则会被设为不可协商的第一原则。

---

## 2026-07-23（Week8-Day4：Runtime 无状态执行）

### 今天最大的认知
以前以为 Runtime 就是"跑代码的引擎"——加载代码、执行、返回结果，中间维护一些会话状态、用户上下文。
现在知道 Runtime 是"手术室"不是"病房"——无状态、封闭、所有信息通过 FrozenExecutionContext 带进来，所有结果通过 ExecutionResult 带出去。execute() 永不抛异常，所有失败都返回 fallback 七字段结构化结果。Runtime 包零 workflow import——执行框架通过参数注入，是可替换的插件。

### 今天最大的坑
发现 RuntimeLoader 是 WP-05 stub——它接受已实例化的 DeploymentRevision 直接返回，没有真实的 OCI pull、layer 验证、Compatibility Matrix Load check。这意味着当前是"被投喂"模式，调用者负责实例化。理解 Runtime 的无状态设计不难，但容易忽略 stub 和真实实现之间的巨大 Gap——看起来代码结构完整，但核心装载和验签能力尚未填充。

### 今天最大的决策
如果重新设计，无状态 Runtime + FrozenExecutionContext 不可变性 + 封闭性（零 workflow import）会被设为三大不可协商原则。无状态是水平扩展的前提，FEC 不可变是审计的基础，封闭性是可替换性的前提。三者缺一，平台就退化为"有状态单体应用"。

---

## 2026-07-24（Week8-Day5：Capability 与 Connector）

### 今天最大的认知
以前以为 Capability 就是 Plugin 的新名字——"即插即用的执行模块"。
现在知道 Capability 是**治理描述符**，不包含任何执行逻辑。E6 migration 后 `runtime_binding={}` 是铁证：Capability API 的 `/invoke`、`/invoke_stream`、`/executions/*` 全部移除，只剩 `/list_capabilities` 和 `/describe_capability` 两个元数据查询端点。真正的执行入口是 SkillRelease 的 canonical invoke。三层分离极其清晰：Capability（描述能做什么）→ SkillRelease（定义用它做什么）→ Workflow（内部实现）。

### 今天最大的坑
发现 MCP Connector 当前嵌在 Workflow 内部，没有独立治理。ADR-004 §8 描述的"Connector 只在 SkillRelease execution context 内可用"是目标态，代码现实是 Connector 作为 Workflow 的工具节点存在，没有独立的 effect_policy 校验、没有独立的版本管理、没有在 Platform Governance Plane 独立登记。`enforce_read_only()` 的 `_WRITE_INDICATORS` 是枚举式检测（`http_request`/`db_write`/`tool_call`/`provider_conditional_write`），无法覆盖所有可能的写操作形式。这是当前最大的架构债。

### 今天最大的决策
如果重新设计，Connector 独立治理应该更早做。当前 MCP 嵌在 Workflow 内意味着：Connector 调用不经独立 Capability Resolution、没有独立 effect_policy、版本管理依赖 Workflow。正确做法是 Connector 在 Platform Governance Plane 独立登记，每个 Connector 有自己的 effect_policy 和 scope，SkillRelease 通过 Capability Resolution 引用 Connector。E6 migration 证明了"Capability 不执行"是正确的——如果一开始就不给 Capability 执行能力，E6 迁移就不需要存在。

---

## 2026-07-26（Week8-Day7：Virtual CTO Review）

### 今天最大的认知
以前以为"ADR 通过了就等于实现了"。看到 ADR-001~004 的 G1-G18 全部通过，就以为 LangChat 的架构已经完整落地了。现在知道通过验证门的只是"当前态"（ADR-001~004），而"目标态"（ADR-005~008）全部还在评审中。v2 目标态的 6 个核心对象（BlueprintVersion、ExecutionPlanIR、SkillRelease v2、DeploymentRevision、ReleaseChannel、TrafficPolicy）在代码中完全不存在。ADR 的四态模型（文档事实/已确认方向/待决策/待验证）是一个极好的治理工具，它让"我们现在在哪"和"我们要去哪"同时存在而不矛盾。

### 今天最大的坑
发现五维评分中 Technical Debt 得分最低（6.5/10），根本原因不是某个单独的技术债项，而是系统性的：WorkflowSpec 作为"当前唯一执行格式但目标态要退役"的过渡期状态，意味着所有在 WorkflowSpec 上做的新功能都是"未来要迁移的债务"。这不是一个能快速修复的问题，需要通过 v2 制品链的逐步落地来系统性解决。

### 今天最大的决策
Week 8 建立了五维评分基线（综合 7.2/10），这个基线将在 Week 9-11 持续追踪。如果到 Week 11 综合分仍在 7.2 以下，说明 v2 制品链落地没有实质进展，需要升级为 P0 风险。

---

## 2026-07-25（Week8-Day6：完整链路图）

### 今天最大的认知
以前以为各模块是并列的组件图——Capability、SkillRelease、Runtime、Connector 各管各的。
现在知道它们是一条**不可缩短的串行链路**——10 个站点、7 个治理检查点、覆盖 6 个治理维度（身份认证/访问控制/数据安全/审计追踪/可靠性/性能保护）。每一步有独立的治理目的，去掉任何一步都打开具体的安全/审计/可靠性缺口。画完链路图后，Gap 无处藏身：核心执行链路（①-⑧）已对齐，但 Connector 治理（🔴）和 v2 制品链（🔴）是最大断裂点。

### 今天最大的坑
发现 `enforce_read_only()` 的递归扫描设计比想象中更重要——它不是简单的配置校验，而是运行时递归 8 层深度的安全扫描，检查键名和字符串值是否匹配 `_WRITE_INDICATORS`。这是 P0 阶段最后的安全防线。同时发现 Connector 治理是链路上最大的 Gap：MCP Connector 嵌在 Workflow 内部，没有独立的 effect_policy、scope 和版本管理，`_WRITE_INDICATORS` 枚举式检测无法覆盖所有写操作形式。

### 今天最大的决策
如果从零设计这条链路，会更早做三件事：① Connector 独立治理层（不嵌在 Workflow 内）；② v2 制品链从 P0 开始建（不走 WorkflowSpec 弯路）；③ ApplicationContract 在 P0 就引入（不让 SkillReleaseDescriptor 承担三个角色）。不会改变的设计：六维身份作为第一步、Read-Only 守卫作为最后防线、七字段结构化输出、幂等+限流在准备阶段。

---

## 2026-07-27（Week9-Day1：BlueprintVersion）

### 今天最大的认知
以前以为 BlueprintVersion 就是"有版本的 Blueprint"——加了个版本号而已。
现在知道 BlueprintVersion 的不可变性不是流程约定，而是**数学保证**：`@dataclass(frozen=True)` 在 Python 语言层面冻结 + SHA-256 内容寻址在密码学层面保证 + Registry `__post_init__` 自毁式防御在执行层面拦截。三层中任何一层被绕过，其他层仍然有效（防御性深度）。这是企业级代码的典范。

### 今天最大的坑
发现 ADR-005 D-2 定义的 Source Review（人工评审）在代码中**完全不存在**。当前只有 Admission（机器检查），从 Candidate 到 Version 的升级路径缺少人工评审门。这意味着理论上任何通过机器检查的 Candidate 都能自动升级为 Version——治理缺口。不过考虑到当前是 WP-02 阶段（Blueprint 基础设施），Source Review 可能在后续 WP 中补充。

### 今天最大的决策
如果重新设计，会保留 BlueprintVersion 的所有核心设计：frozen=True、SHA-256 内容寻址、前向唯一生命周期、Registry 无执行方法 + 自毁防御、评审两段式 + 不检查业务正确性。唯一可能调整的是：增加 Candidate withdraw 状态（允许作者主动撤回 In Review 的 Candidate），以及 Registry 用 event-sourced 持久化模式。

## 2026-07-28（Week9-Day2：SkillRelease 唯一可部署单元 + DDD 战略设计验证）

### 今天最大的认知
SkillRelease 的"唯一可部署单元"地位不是技术决定，而是治理决定。它把制品链上的所有治理（确定性构建、依赖锁、评估、审批、签名）汇聚到一个不可变制品上。同时，从 DDD 战略设计视角看，MI 的 17 个 Bounded Context 划分经得起 DDD 原则检验——Core Domain（P0）/ Supporting Domain（P1）/ Generic Domain 的分层已经隐含在 Domain Model 中。

### 今天最大的坑
WorkflowSpec binding（W01-W09）当前是 SkillRelease 底层执行态，但目标态要退役。当前代码事实和目标态设计之间存在"过渡期认知 gap"。DDD 战略设计验证中发现：17 个 Context 有数据流边界但缺少显式的 Context Map（跨 Context 集成契约语义不够清晰）。

### 今天最大的决策
理解了 SkillRelease 和 DigitalEmployeeDefinition 的分离原则：定义是"谁"，SkillRelease 是"什么"。这与 DDD 中 Aggregate 边界划分是同一个思维模式——DigitalEmployeeDefinition 是引用语义锚点而非巨型聚合根，正如 DDD 中 Aggregate 应尽可能小。

## 2026-07-29（Week9-Day3：Deployment / DeploymentRevision）

### 今天最大的认知
以前以为 Deployment 就是"把 Release 部署到服务器上"，是一个运维动作，不是架构对象。Release 和 Deployment 是"发布"这一个动作的前后两步。
现在知道 DeploymentRevision 是 Runtime 层最重要的架构对象——它是一个不可变的、内容寻址的完整执行闭包，16 个字段锁死了"这次执行用了什么、跑了什么、在什么环境下跑的"。它是 Supply Chain 和 Runtime 之间唯一的合法通道。SkillRelease 是通用制品（跨环境可移植），DeploymentRevision 是特定实例（绑定到具体环境）。合并它们意味着每次环境变更都要重新走 Supply Chain（构建、评估、签名），这是不可接受的。

### 今天最大的坑
发现回滚语义是"前向操作"而不是"还原操作"——从历史 DeploymentRevision digest 闭包物化新 Revision，不改变历史对象状态。这与传统 ERP 的"还原数据库"完全不同。一开始觉得这很绕，但理解后意识到这是审计完整性的数学保证：你不修改历史，只创造新的决策记录。另一个坑是 source_channel 只作 provenance，不进 runtime closure digest——这意味着 Channel 名变化不改变 Revision 身份，但它记录了"这个 Revision 是从哪个 Channel 晋升来的"审计线索。

### 今天最大的决策
如果重新设计，会把 DeploymentRevision 的 16 字段闭包作为不可协商的第一约束。AI 应用的执行结果不确定性远超传统软件——受 prompt、模型版本、知识库快照、策略叠加影响。如果 DeploymentRevision 不把这些全部锁死，就无法做到"同一个闭包 → 同一个执行结果"，灰度对比和回滚就不可靠。evaluation_only 默认值为 True 是一个安全设计典范——默认隔离，生产部署需要显式打开。

