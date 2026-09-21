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

## 2026-07-30（Week9-Day4：ReleaseChannel / TrafficPolicy）

### 今天最大的认知
以前以为灰度发布是部署工具的功能——在 CI/CD 流水线里配个百分比就行了。现在知道 LangChat 把灰度拆成了两个独立架构对象：ReleaseChannel（Supply Chain 层的晋升指针）和 TrafficPolicy（Runtime 层的流量策略）。两者在架构上完全解耦：Channel 移动不改变流量，TrafficPolicy 不读 Channel。这个"标记正式版"≠"全量上线"的中间态，才是灰度发布的工程价值。传统 ERP 的"发布"把版本标记、部署、切流混在一个动作里，LangChat 拆成三个独立动作（晋升→物化→切流），各自独立审计。

### 今天最大的坑
发现 ReleaseChannel 被严格归在 Supply Chain 层，不在运行时请求路径中。一开始觉得奇怪——"正式版指针"难道不是运行时关心的吗？但理解后意识到：如果 Runtime 读 Channel，那 Channel 移动就会直接影响流量——这恰恰是设计要避免的。Channel 是"版本管理团队的事"，TrafficPolicy 是"运维团队的事"。代码验证了这一点：TrafficPolicy 在构造时就拒绝一切非精确引用（latest、channel 名、mutable name 全被 ValueError 拒绝）。

### 今天最大的决策
灰度的核心不是"能不能按比例切流量"，而是"版本标记与实际运行状态的解耦程度"。如果重新设计 MI 的合同审核机器人发布流程，会把"标记正式版"（ReleaseChannel）和"实际切流"（TrafficPolicy）分成两个审批流——版本管理委员会标记正式版，运维团队根据灰度策略逐步切流。出错时回滚只需新建 TrafficPolicy 版本指向旧 Revision，不需要动 Channel 指针。


## 2026-07-31（Week9-Day5：DigitalEmployeeDefinition）

### 今天最大的认知
以前以为数字员工就是一个"智能体"——定义它、启动它、它就开始干活。现在知道 DigitalEmployeeDefinition 只是"语义锚点"——一组引用的集合，指向真正干活的对象（SkillRelease → DeploymentRevision → Execution）。定义不拥有 Runtime，不持有 Deployment 状态，不构造 FrozenExecutionContext，不充当执行入口。当前代码的 `status=active` 同时承载了"定义已发布"和"部署在服役"双重语义——目标态要拆成 `DigitalEmployeeDefinition.Published` + `Deployment.Active` 两个独立状态。这和传统 ERP 里"员工主数据 ≠ 流程实例"是完全一致的道理。

### 今天最大的坑
当前代码的 `kill_switch` 直接放在 DigitalEmployeeModel 上，看似合理。但从目标态看，kill_switch 属于 Deployment 层——"停止运行"是运行时决策，不是定义层决策。定义可以 Deprecated（退役），不能被"停止运行"，因为定义本身不运行。另外 `bound_skill_id` 是 tag 引用而非 digest 引用，违反了"引用而非持有"原则——目标态要改成 digest/版本指针。

### 今天最大的决策
如果给 MI 的 10 个 mall 都部署"合同审核数字员工"，正确的做法是：1 个 DigitalEmployeeDefinition（共享身份声明）+ 10 个 Deployment（每个 mall 一个）。每个 Deployment 有独立的 KnowledgeSnapshot、PolicyBundle、DeploymentRevision。知识库更新一个 mall 不影响其他。这正是"定义不拥有 Runtime"的核心价值——多环境部署时定义保持稳定，运行独立演进。

---

## 2026-08-01（Week9-Day6：Domain Model Diagram 动手交付）

### 今天最大的认知
以前以为 Domain Model 就是 ER 图加类图——把数据表关系画清楚就够了。
现在知道 Domain Model 是**治理拓扑图**：不仅画数据关系，还要画生命周期（谁先出生谁先死）、不变量约束（合并后哪些不变量会破裂）、层归属（哪个对象在四层中的哪一层）、禁止职责（这个对象绝对不能做什么）。一张好的 Domain Model Diagram 能让你在 3 分钟内回答"这个对象放这里合不合适"。

### 今天最大的坑
代码验证发现 Runtime Layer 覆盖度只有 10%——Deployment、DeploymentRevision、TrafficPolicy、FrozenExecutionContext 四个核心对象在代码中完全不存在。当前代码的"数字员工"直接从 SkillRelease 跳到 Execution，中间没有部署闭包。这意味着所有 v2 治理（灰度、回滚、多环境、闭包 digest-pin）在当前代码中都没有基础设施支撑。Blueprint 层（SC-02/03）是代码最成熟的部分，但从 SkillRelease 之后几乎是断崖。

### 今天最大的决策
合并/拆分判定原则：**如果两个对象的演化节奏不同、生命周期不同、变更 Owner 不同，它们就不应该合并。** 用这个框架可以快速判断：Capability/CapabilityRelease 可短期合并（小团队），但 BlueprintVersion/ExecutionPlanIR 绝不可合并（违反 HC-3 单向制品链）。Definition/Deployment 绝不可合并（否则多环境部署变成不可能）。这条原则将作为后续架构评审的标尺。

---

## 2026-08-02（Week9-Day7：Virtual CTO Review — ADR Health Check）

### 今天最大的认知
以前以为"ADR 通过了就等于稳定了"——只要状态是 accepted，就可以放心引用。
现在知道 ADR 体系本身也有健康度问题：两套编号体系并存（品牌 ADR-00X vs 技术 ADR-LC-0XX vs v2 战略 ADR-00X）、v2-ADR-005/007/008 覆盖面过大需要拆分、v2-ADR-001~004 长期停留在"评审中"/"文档事实"状态阻碍下层推进。ADR Health Check 不只是看"有没有过时"，更要看"覆盖面是否合理"、"编号体系是否一致"、"实施状态是否可追踪"。

### 今天最大的坑
五维评分从 Week 8 的 7.2 降到 6.8。初看像是退步，实际上是"达克效应的正向穿越"——Week 8 看到的是链路全景（框架完整），Week 9 拆开每个对象后发现"框架完整但内容空洞"（Runtime Layer 覆盖度仅 10%）。评分下降不是架构变差了，是理解更深了。最大的坑是 v2-ADR-007（RuntimeABI + CompatMatrix + FEC wire）把三个独立技术决策合在一个 ADR 里，任一子主题修订都要整个 ADR 重评——这是治理设计的技术债。

### 今天最大的决策
提出三条 CTO 级建议：① 推进 v2-ADR-001~004 正式冻结（已通过 G1-G18 验证门，继续"评审中"不带来额外谨慎）；② 拆分 v2-ADR-007 为三个独立 ADR（RuntimeABI / CompatMatrix / FEC wire）；③ 在每个 ADR 中增加 implementation_status 字段（draft/partial/implemented/verified），让"ADR 定义了但代码不存在"这个最大风险可见化。

---

## 2026-08-03（Week10-Day1：Permission & Policy — 谁允许谁做什么）

### 今天最大的认知
以前以为权限就是 RBAC——定义角色、分配权限、代码里 if-hasPermission 检查。
现在知道在企业 AI 平台里，权限不是功能模块，而是**横切四层的治理制品链**：Policy（单条规则）→ PolicyBundle（不可变策略束，Pydantic frozen+strict）→ SkillRelease（打包）→ DeploymentRevision（digest-pin）→ FEC（冻结）→ Runtime 只读 → Dual-Gate 9步算法验证。三个维度同时生效：静态维度（角色权限映射表）、制品维度（conditional_write 必须配 review_gate 的跨字段不变量）、执行维度（Step 7 审批后用冻结快照重跑 Step 0-4）。传统 RBAC 的"检查"只是这条链的最后一环。

### 今天最大的坑
Dual-Gate 的 9步算法看起来极其复杂，但深入后发现它的核心洞察只有一个：**审批覆盖的是字节级快照**。Step 7 不只是"审批通过了就执行"，而是用冻结的 invocation_context_canonical_json 重跑 Step 0-4，对比 digest。这意味着如果审批者批准了 amount=5000，调用方在恢复时改成 amount=100（试图绕过 cannot max_amount=1000），系统会用冻结的 5000 做验证——篡改被拒绝。这个设计的复杂度是"AI 时代安全"的必要代价，不是过度设计。

### 今天最大的决策
Permission 不放 Runtime 里的根本原因不是"关注点分离"这种架构审美，而是**安全必要性**：LLM 可以通过 Prompt Injection 影响运行时行为，如果权限检查也在运行时，就被攻击面覆盖了。权限必须在外部冻结好，Runtime 只是一个无法篡改的执行者。这条原则对 MI 的启示是：合同审批数字员工的权限策略必须在部署前定义，不能"运行时根据情况灵活调整"——"灵活"在 AI 平台中等同于"可被攻击"。

---

## 2026-08-04（Week10-Day2：Audit & Trace）

### 今天最大的认知
以前以为 Trace 就是高级日志——把 `logger.info()` 换成 `span.record()`，本质没区别。
现在知道 Trace 和日志是两个物种。日志是叙述（面向人类阅读），Trace 是证据（面向系统查询）。日志没有结构，Trace 有严格的 Span Tree（trace_id / span_id / parent_span_id）。更关键的是：Trace 是 Governance 的基础设施——没有 Trace，Permission 效果无法验证、Approval 决策无法追溯、PII 泄漏无法定位。Trace 不是排障工具，是治理证据链。

### 今天最大的坑
LangChat 的 ExecutionSpan 有 10 种 SpanKind，覆盖所有执行路径（workflow_run / llm / rag_retrieval / channel_dispatch / capability_invoke / mcp_tool 等）。这不是日志级别（DEBUG/INFO/WARN），而是业务语义类型。坑在于：如果你用传统日志思维去理解 Trace，你会忽略 SpanKind 的语义价值——你不会想到可以 SQL 查询"所有租户 A 的失败 LLM 调用"，也不会想到可以按 kind 聚合分析"RAG 和 LLM 哪个更慢"。

### 今天最大的决策
LangChat 选择"OTel 形状 + 自实现"而不是直接用 OpenTelemetry SDK，这个决策的核心逻辑是：获得 OTel 的兼容形状（未来可以插入 OTel/Langfuse exporter），但不背负 OTel SDK 的重量级依赖。DbSpanEmitter 异步批量写入、CompositeEmitter 支持多写、contextvars 保证 async-safe 传播——这些都是自实现才能精确控制的。对 MI 的启示是：当数据量到 70 万 Span/天时，自实现的控制力（保留策略 CLI、租户隔离查询、预聚合）比依赖外部平台更重要。

---

## 2026-08-05（Week10-Day3：Approval — 人审）

### 今天最大的认知
以前以为人审就是一个审批按钮——AI 生成建议，人点"通过"，就这么简单。
现在知道 LangChat 的人审是一个**三层治理结构**：① 制品层（Release Gate 的 Approval attestation，digest-pin 到技能制品上，不审批不发布）；② 运行时层（HITL Gate，conditional_write 触发 `pending_human_review` 状态机强制暂停，6 步验证 + 4 写原子 CAS）；③ 部署层（DeploymentRevision 的 `ApprovedDeploymentRevision` 类型级边界）。三层各有各的强制机制：制品层用 Gate 序列 monotonic 约束、运行时层用六状态原子状态机、部署层用 frozen dataclass 类型系统。Approval 和 Signature 的分离是精妙设计——治理决定（人）和密码学证明（机器）分离验证。

### 今天最大的坑
`register_revision_from_envelope` 的设计让我踩了一个认知坑：它从 DB 行实际状态派生 approval，而不是从请求参数 `auto_approve` 派生。最初我以为 `auto_approve=True` 会自动批准——但它不会，因为 idempotent re-insert 返回已有的 pending 行，approval 从 DB 实际状态读取。这是防"重新注册时绕过审批"的安全设计。另一个坑：HITL 的 SameTransaction CAS 做了 4 个写操作（GateChallenge 锁 → Execution 锁 → token 消费 → event insert + CAS），全在一个事务里——两个并发审批会在 SELECT FOR UPDATE 上串行化，失败方收到 ChallengeAlreadyDecidedError。这比传统 ERP 的"审批后写日志"复杂得多，但这是 AI 时代的必要安全代价。

### 今天最大的决策
理解了"为什么 AI 不能全自动发布"的核心论点：不是不信任 AI 的能力，而是企业治理需要**可追溯的责任链**。传统 ERP 的审批可以被管理员配置跳过，但 LangChat 的审批由类型系统（ApprovedDeploymentRevision）+ 状态机（pending_human_review 不可跳过）+ Descriptor 验证器（conditional_write 强制 review_gate）三层强制执行。对 MI 的启示是：合同审批数字员工的技能发布、租金变更建议的执行，都必须经过人审——这不是降低效率，是建立企业信任边界。没有这个边界，AI 永远只能做 Demo，不能进生产。

---

## 2026-08-06（Week10-Day4：Fail-closed vs Fail-open + Approval）

### 今天最大的认知
以前以为 fail-closed 就是"出错就报错"，fail-open 就是"出错就跳过"，是个二元选择。
现在知道 LangChat 的 fail-closed 是**四层分层设计**：① 安全边界层（认证/授权/hash/scope）绝对 raise；② 制品治理层（审批/类型边界/状态机）结构性不可绕过；③ 执行层（LLM/KB/工作流）优雅降级返回兜底结果；④ 风险保留层（兜底结果中的敏感关键词检测）即使降级也不丢失风险信号。最精妙的设计是 `_fallback_result()`——`execute() MUST NEVER raise to the caller`，但这不是 fail-open，而是 API 契约：执行失败是结果不是异常，风险通过 `human_review_required` + `risk_flags` 保留。

### 今天最大的坑
`auto_approve_on_timeout=False` 看起来只是一个默认值，改 True 就行——但**默认值就是架构决策**。传统 ERP 审批超时自动转交或自动通过很常见；在 AI 平台里，这是不可接受的。AI 生成的建议可能看起来合理但实际有害，所以超时 = 保持 pending = 需要人工处理。另一个坑：`register_revision_from_envelope` 从 DB 行实际状态派生 approval，不信任请求参数 `auto_approve=True`——因为 idempotent re-insert 返回已有的 pending 行，approval 从 DB 实际读取。这是防"重新注册时绕过审批"的安全设计。

### 今天最大的决策
Fail-closed 在 MI 商业地产场景的具体映射：① 合同审核技能上线前必须法务审批（DeploymentRevision Approval Gate）；② 租金调整建议必须人工确认后才写入 ERP（HITL Gate + conditional_write）；③ 跨商场数据访问必须被拒绝（Capability scope 校验 → GatewayError）；④ LLM 挂了但输入含"退款/解约/减免"等敏感词 → 返回兜底结果但 `human_review_required=True`。MI 的架构原则应该是：**安全问题绝不妥协，执行问题优雅降级，但风险信息不丢失。**

---

## 2026-08-07（Week10-Day5：Realization Rollback + FrozenExecutionContext）

### 今天最大的认知
Realization Rollback 不是 DELETE，而是六种对象六种归档策略。Workflow → archived，Version → is_published=False，Binding → is_active=False，Assistant → archived，KB → 只解除关联不删数据，Prompt → 指针回退或模板退休。每一种策略都尊重对象的语义和历史可审计性。FrozenExecutionContext V2 不是一个简单的 immutable object——它是一个密码学容器，13 个 digest 把它跟 SkillRelease、DeploymentRevision、PolicyBundle 绑死，任何篡改都会导致 digest 不匹配。这不是代码层面的「君子协定」，而是数学层面的完整性保证。

### 今天最大的坑
`__wrapped__` 的使用。Realization Orchestrator 里 `create_workflow`、`create_version`、`publish_version` 都用了 `getattr(_create_workflow, "__wrapped__", _create_workflow)`——第一眼看像是绕过了什么安全机制。实际上是因为 `@with_session` 装饰器会自动 `db.commit()`，而在 savepoint 隔离模型中，任何中间 commit 都会打断事务完整性。所以必须用 `__wrapped__` 绕过装饰器的自动提交，保持所有 mutation 在同一个 savepoint 内。这是事务完整性的需要，不是安全绕过。另一个坑：Rollback 里 KB 的处理是「metadata flag」而非归档，因为 KB 里的文档可能已经被工作流使用过，硬归档会导致历史引用断裂。

### 今天最大的决策
MI CRE 场景中 Realization Rollback 的应用：当「租户续签数字员工」的 Prompt Template 引用了过期租金系数表时，Rollback 不是删除 v3 模板——而是指针回退到 v2，v3 行保留可查。修正后重新 Realize 生成 v4，attempt 递增。完整审计链零数据丢失。这比传统 ERP「删了重录」强太多。FrozenExecutionContext 对应到 MI 场景就是「合同审批身份快照」：审批人的权限范围、委托链、策略快照在审批过程中不可变——这直接对应企业内控对审批流程的合规要求。

---

## 2026-08-08（Week10-Day6：Governance 覆盖图 + Gap 分析）

### 今天最大的认知
以前以为 Governance 是一个模块，和 Knowledge Base、Workflow 并列。
现在知道 Governance 是三个时间轴上的横切约束：Build Time（Custody + Rollback + Plan）→ Deploy Time（PolicyBundle + Release Gate + Compat Matrix）→ Runtime（SixDim + Dual-Gate + ReadOnly + Audit + Trace + PII + Retention）。15 个治理检查点分布在 ADR-007 三段架构链的每一段。这不是"模块化治理"，是"空气化治理"——每一层都呼吸它，但你看不到它独立存在。

### 今天最大的坑
PII Redaction 默认关闭。代码写得很漂亮——`RedactionStrategy` Protocol → `NoopRedactionStrategy`（默认）→ `RegexRedactionStrategy`（8 种 PII 模式：EMAIL/IP/PHONE/ID_CARD/BANK_CARD/URL_CRED）→ entry point 插件扩展——但 `NoopRedactionStrategy` 是默认值！生产环境如果忘记开启 `PII_REDACTION_ENABLED`，用户敏感数据裸奔到 Trace Payload。这不是代码问题，是架构决策问题：定位为"企业 AI 应用平台"（ADR-001），PII 保护不应该是 opt-in。另外发现 Enterprise Systems 侧出站签名缺失——Tool Use 调用外部系统没有签名，企业系统侧无法验证来源，这在多租户场景下是安全隐患。

### 今天最大的决策
画出了完整的 Governance Coverage Map，识别了 7 个 Gap。最大的 Gap 优先级判定留给明天 Virtual CTO Review。初步判断：PII 默认关闭 > 出站签名缺失 > 合规报告缺失 > 数据分级保留 > 跨租户测试覆盖。核心原则：Governance 不是"有没有"的问题，是"默认开不开"的问题。安全机制默认关闭 = 没有安全机制。

---

## 2026-08-09（Week10-Day7：Virtual CTO Review — Governance 周总评）

### 今天最大的认知
以前以为 Governance Review 就是检查"有没有治理"——列出治理机制，确认存在就完了。
现在知道 Governance Review 要回答四个问题：① 治理覆盖了哪些层（Coverage Map）？② 每一层是默认开还是默认关（Default Policy）？③ 治理机制之间是否形成闭环（Custody→Evidence→Verify）？④ 如果只能修一个，先修哪个（Priority Matrix）？这四个问题的答案构成了一个完整的治理评估框架。本周的 Review 给出了明确答案：覆盖 8/15 个检查点、PII 默认关闭是最大风险、修复成本一行代码、优先级判定完成。

### 今天最大的坑
五维评分三周持平在 6.8（Week 9 = Week 10 = 6.8），初看像是"没有进步"。但深入分析发现：理解深度从 7.5 → 8.5（↑1.0），Charter 对齐度从 25% → 37.5%（+12.5%），新增 10 个认知增量。评分持平是因为"发现的好消息"（FEC 已落地、Dual-Gate 精密）和"发现的坏消息"（PII 默认关闭、出站签名缺失）相互抵消。这是达克效应正向穿越的第三阶段：不再盲目乐观也不盲目悲观，而是精确知道已有什么、缺什么。

### 今天最大的决策
PII Redaction 默认开启 — 优先级判定为 P0。判定依据四条：① 不对称风险（调试不便 << 数据泄漏+合规违规）；② 定位一致性（ADR-001 说"企业平台"，PII 不能 opt-in）；③ 修复成本极低（改一个默认值）；④ 行业先例（Azure/AWS/Google 全部默认开启）。修复行动方案四步已定：改默认值 → 启动日志 → 创建 ADR-LC-014 → 增加关闭审批流程。这不是"Week 11 的任务"，这是"今天的任务"。

---

## 2026-08-10（Week11-Day1：Capability Inventory — 能力清查）

### 今天最大的认知
以前以为 Capability Catalog 是 LangChat 的能力目录，列出了平台所有能力，SkillRelease 是能力的具体实现。
现在知道代码里有三套"能力注册体系"并行存在：① Capability Catalog（2 条，runtime_binding 全空，纯展示壳）；② SkillRelease Registry（10 条可执行 Skill，各有 executor_fn）；③ Capability Gateway（W01 MCP 独立体系）。三者互不引用，平行存在。Capability Catalog 的 2 个条目在 E6 迁移后变成了被掏空的元数据——OpenSpec 明确写 "runtime_binding SHALL be the empty object {}"。真正的执行入口是 SkillRelease 的 POST /v1/skill-releases/{skill_id}/invoke。Capability API 默认关闭（CAPABILITY_API_ENABLED = False），因为 Catalog 还没准备好面对外部。

### 今天最大的坑
W01-W09 的 Skill ID 看似遵守了 ADR-003 正交约束——没有行业词（ops.anomaly、customer.escalation、brand.research）。但 workflow_binding 里全是 mall-* 前缀，display_name 全是 "Mall Ops / Mall Customer / Mall Brand"。**Skill ID 遵守了正交约束的字母，但违反了精神。** 这些不是 Capability（跨行业原子能力），它们是 Application 级别的打包——9/10 个 Skill 是商业地产专属，只有 workflow.execute 一个是真正平台级的。ADR-003 说 Application = Capability 子集 × Industry 标签，但代码里这个矩阵没有被显式表达。

### 今天最大的决策
Week 11 的打开方式不是"继续学新东西"，而是"面对代码事实"。前三周建立了漂亮的心智模型——四层架构、25+ 个目标态对象、ADR 正交模型。今天开始把这些模型和代码对照，发现 Gap 不是"目标态对象没实现"（这在意料之中），而是"当前态有三套平行体系谁也不认谁"。Capability Catalog 不投影 SkillRelease，SkillRelease 不查 Catalog，Gateway 自成一套。这才是最危险的 Gap——不是缺什么，而是现有的东西彼此不连接。

---

## 2026-08-11（Week11-Day2：Gap Matrix — 目标态 vs 代码实现）

### 今天最大的认知
以前以为 Gap 分析是"列一个完成度百分比表"。
现在知道 Gap 分析的真正价值是识别**"语义 Gap"**——不是"有没有"的问题，而是"在那里但语义不对"的问题。最危险的 Gap 不是"对象不存在"，而是 DeploymentRevision 以为闭包完整实际不完整——没有 KnowledgeSnapshot 和 PolicyBundle 可引用，却按"digest-pinned 闭包"的语义运行。这给了一种虚假的安全感。整张 Matrix 打分下来，Supply Chain 是最薄弱的层（11个目标对象只有 2 个 ≥7分），而它恰恰是平台的"配置管理 + 变更管理"——ERP 里叫"工程变更管理"。

### 今天最大的坑
SkillRelease canonical execution 有 3710 行代码，初看以为这是 v2 制品链最厚的部分，应该没问题。但仔细看发现：那是 v1 canonical 执行路径（执行/审批/限流/重放/HITL 全套），**不是 v2 SkillRelease 作为 OCI 制品**。v2 的 OCI 打包（supply_chain/oci/）只有 manifest + publish 骨架（~400行），和 canonical execution 没有打通。同一个名字"SkillRelease"，在 v1 和 v2 指的是不同的东西。这种"术语重叠陷阱"比"完全空白"更危险——因为它让人误以为已经实现了。

### 今天最大的决策
如果给 3 个 Sprint 补 Gap，优先级排序：① 先修 KnowledgeSnapshot（部署闭包不完整 = 执行不可复现，最高运行时风险）；② 再修 RuntimeABI（Runtime 和制品之间无版本契约 = 升级必爆炸）；③ CapabilityRelease 可延后一个 Sprint（Capability 现在可用，版本化发布缺失的迁移成本可控）。判定依据：安全性 > 完整性 > 美观性。KnowledgeSnapshot 直接影响"上周三的数字员工回答了什么"——回答不了就是合规风险。


## 2026-08-13（Week11-Day4：Knowledge 现状）

### 今天最大的认知
以前以为 RAG 工程能力强 = Knowledge 治理没问题。现在知道这是两个完全不同的维度。当前 RAG 管道（Query Transform + Hybrid Search + Rerank + Citation + Evaluation + KB Improvement Queue）工程做得确实很好，但治理层完全空白：没有 KnowledgeCollection（逻辑集合）、没有 KnowledgeSnapshot（不可变快照）、没有 digest、没有被 DeploymentRevision 闭包锁定。知识库随时可改，数字员工行为不可预测——这在企业场景是合规风险。

### 今天最大的坑
当前 KnowledgeBaseModel 看起来很完整（tenant/workspace 隔离、跨工作空间挂载、Per-KB RAG 配置覆盖），容易让人以为"知识治理已经做了"。但这些是访问控制，不是知识治理。真正的治理要求：知识有版本、有不可变性、与部署闭包绑定、变更触发新部署。当前代码连版本号字段都没有。

### 今天最大的决策
Knowledge Gap 的优先级排第一（高于 RuntimeABI 和 CapabilityRelease），因为：部署闭包不完整 = 执行不可复现 = "上周三数字员工回答了什么"无法追溯。在商业地产场景，这等于合同审批引用的政策版本不可追溯。RAG 工程能力（检索质量优化）可以后续迭代，但知识版本化是不可妥协的治理底线。

---

## 2026-08-14（Week11-Day5：竞品对比 — Dify/LangGraph/OpenClaw/Claude Code）

### 今天最大的认知
以前以为 LangChat 和 Dify 是同一赛道的竞品，区别只是"企业级 vs 开源社区"。现在知道它们根本不在同一条赛道上。Dify 解决的是"AI 应用怎么快速搭建和运行"——核心价值是速度。LangChat 解决的是"AI 应用怎么在企业治理框架下确定性运行"——核心价值是确定性。Dify 说"配置即应用，改了就生效"。LangChat 说"制品即应用，改了要走完整链路"。这两句话背后是完全不同的架构哲学、完全不同的目标客户、完全不同的商业模型。这不是"更好的 Dify"，而是"Dify 范式的反面"。

### 今天最大的坑
竞品对比最大的陷阱是"功能列表比较"——列一张表，打勾打叉，最后得出"我们功能更多"的结论。这毫无意义。真正的对比维度是架构范式：制品链 vs 配置即应用、不可变闭包 vs 可变运行时、前置治理 vs 后置治理。LangGraph 不是竞品——它是可以被 LangChat 封装在 SkillRelease 里的编排能力。OpenClaw 不是竞品——它是调用 LangChat 的 Agent Host。Claude Code 不在企业 AI 应用平台赛道。把不是竞品的东西当竞品，会浪费精力防守不存在的战线。

### 今天最大的决策
LangChat 最独特的设计可以用一句话概括：把软件工程的最佳实践（制品链、确定性构建、不可变部署）引入 AI 应用治理。这不是功能创新，是范式创新。这决定了 LangChat 的竞品不是 Dify/LangGraph，而是"企业用传统方式自建 AI 应用"这个现状。真正的竞争不是功能对比表，是"有没有制品链治理"——这是企业 CIO 能理解的语言。

---

## 2026-08-15（Week11-Day6：⚡ 实战交付 — LangChat v2 实施路线图 v1.0）

### 今天最大的认知
以前以为实施路线图就是把 Gap Matrix 里的红色项按优先级排序、估工作量。现在知道路线图的第一行不是任何 Gap，而是术语清理——"SkillRelease" 在 v1/v2 指不同的东西，这种术语重叠陷阱会让所有后续工作沟通失真，两个工程师讨论的是不同的东西还以为在讨论同一个。其次，排序依据是"运行时爆炸概率×合规影响"，不是"代码量大小"——3710 行的 v1 canonical execution 是最大代码资产但不是最危险处，最危险的是 DeploymentRevision"以为闭包完整实际不完整"的虚假安全感。

### 今天最大的坑
差点把 Connector（Day 3 结论的最薄弱环节）排进前 3 个 Sprint。但仔细想：tools-call-external-provider-guard spec 已经挡住了不安全的外部调用路径，段 3 空白是"能力缺失"不是"运行时爆炸"；而 Outbound System Bridge 的 Phase-0 Gate 只关 2/10、设计还在 review-blocked，抢跑等于在没有地基的地方盖楼。**"最薄弱"和"最紧急"是两个维度**——路线图排的是紧急度+依赖链，不是薄弱度排名。

### 今天最大的决策
前 3 个 Sprint 排序定为：Sprint 0（1周）术语清理+基线冻结 → Sprint 1（2周）KnowledgeSnapshot 补全部署闭包 → Sprint 2（2周）RuntimeABI+OCI 打通 → Sprint 3（2周）CapabilityRelease+发布流；Connector 留 Sprint 4+ 并行推 OSB Phase-0 Gate 证据（8/22 deadline）。7 周后达到「最小可治理制品链」。元规则：验收标准必须用代码事实定义，不用文档说法定义——否则路线图变成又一份自我安慰文档（Target Domain Model §1.2 的警告同样适用于路线图自己）。

## 2026-08-16（Week11-Day7：最终 Virtual CTO Review — 4 周总复盘）

### 今天最大的认知
以前以为架构评审的评分下降是坏信号。现在知道 W8-W11 五维评分从 7.2 下探到 6.4，与理解深度从 7.0 升到 9.0 形成的"剪刀差"，恰恰是学习有效的证明——W8 是拿望远镜打分（看到框架完整），W11 是拿内窥镜打分（看到三套平行体系、术语陷阱、闭包空洞）。同一架系统，测得越准，分越实。就像 ERP 上线前的数据体检：第一轮盘点说库存准确率 95%，逐仓细盘后变成 88%——库存没变，盘点精度变了。Day 6 路线图 v1.0 的产出意味着测量阶段结束、行动阶段开始：从今天起，五维评分的下行压力应当被 Sprint 交付逐步对冲。

### 今天最大的坑
Review 建议积压。复盘四周的 ADR Health Check：W9 建议 6 条（v2-ADR 冻结、007 拆分、implementation_status 字段等），W10 建议 PII 默认开启（一行代码的 P0 修复），到今天代码复核 pii_redaction.py:172 默认值仍是 False——**建议必须有 owner 和 deadline，否则架构评审退化成"合规表演"**。四周边写边发现 Gap，但 Review 只产出了认知，没有产出变更。这是导师模式的结构性盲区：它能看，不能改。

### 今天最大的决策
宣布"架构导师模式"收官，切换"开发搭档模式"。学习线继续（W12-13 Vision Intelligence），开发线启动 Sprint 0（术语清理 + PII 默认值修复一起提交，让建议落地率从 0/6 变成 2/6）。同时把五维评分改造为工程仪表盘：Sprint 1 验收绑定 Code Health 回升至 6.5+，Sprint 2 绑定 Technical Debt 回升至 6.0+，Sprint 3 绑定 ADR Consistency 回升至 7.0+——评分不再只是认知记录。留给 Week 15 的判据：如果那时评分还在下行，说明路线图没有被执行，那才是真正的问题。

## 2026-08-17（Week12-Day1 · Vision Intelligence 全景）

### 今天最大的认知
MallSenseAI 不是 CV 项目：CV 只占价值链前 1/5（Detection），核心资产是检测之后的业务闭环（规则→告警→工单→通知）。代码验证证实 PRD 判断——当前是封闭系统，无任何 capability 暴露，无法被上层编排。

### 今天最大的坑
发现 MallSenseAI 对外已更名为 LangChat AI Vision（ADR-004），但仓库代码模块名未动（保护契约）。读文档和读代码会看到两个名字，必须知道这是同一个东西，且重命名只覆盖对外品牌。

### 今天最大的决策
Capability 粒度倾向：业务级（safety.alert.query/subscribe）为主 + 少量原子级（vision.detect）。待周六画五层图时结合制造业场景验证配置类能力（vision.rule.configure）是否必要。

## 2026-08-18（Week12-Day2 · MallSenseAI 仓库精读：截图 vs 视频流）

### 今天最大的认知
采样方式是业务时间尺度的函数，不是技术能力的函数。状态型场景（消防通道占用/地面脏污/堆物）物理变化以分钟计，截图采样就是终局不是妥协；事件型场景（跌倒/入侵）瞬间不可重现，必须视频流。判断标准是"业务对象变化多快"，不是"有没有 GPU"。CameraAdapter 接口本身就体现了截图世界观（capture_snapshot() -> bytes 单张 JPEG），且 adapter 抽象为未来 RTSP 留了无侵入的口子。

### 今天最大的坑
规则引擎自称 Stateless evaluator，但"停留超时"规则靠 cooldown_state 里的 active_since 跨快照累计停留时长——第一眼以为是名不副实，细看才懂这是"无状态核心 + 状态外置"模式：引擎本身不持有状态，状态放外部 store。这和 LangChat 无状态 Runtime + 外部状态是同一个架构模式，两个产品在两个领域独立收敛到同一答案。

### 今天最大的决策
用"老人跌倒 10 秒告警"需求做了三层压力测试（采样层 600 倍采样率、检测层无状态逐帧接口失效、规则层缺 Tracking 跨帧去重），确认事件型场景需要的是架构升级不是参数调整。倾向把"采样策略 per-camera 配置化"记入周六五层图的设计约束——混合模式（关键路视频流 + 其余截图）才是商业地产现实。

## 2026-08-19（Week12-Day3 · Detection 体系：为什么选 YOLO-World）

### 今天最大的认知
模型选型是约束求解，不是排行榜浏览。MallSenseAI 的 models/ 目录躺着三份权重 + 一个无模型检测器，四个检测器四种策略（COCO 闭集 / D-Fire 微调 / YOLO-World 零样本 / 基线对比）——检测体系是谱系不是单品，每个检测器对应一档"词表开放度 × 精度责任 × 算力预算 × 数据成本"的权衡。YOLO-World 入选的唯一性由三条硬约束推出：商场障碍物长尾词表不在 COCO 80 类（15 个默认类里 9 个 COCO 没有）→ 闭集出局；CPU-only 单帧预算 → GroundingDINO 出局；"暂不推广但维护"零标注预算 → 微调只配给火灾这种法律责任级场景。它的精度短板（min_confidence 只敢设 0.25）用管线四层兜底补：低阈值召回 → ROI 质心+面积比双闸门 → 规则引擎 → Cooldown。误报率是系统属性，不是模型属性。

### 今天最大的坑
细读 yolo_world.py 发现 classes 不是代码常量而是从 detector_configs 表读的运行时参数，ConfigWatcher 每 10 秒轮询热更新、多副本原子快照切换——第一反应是"这么重？"。细想才懂这是产品级必要设计：零样本检测的全部价值就在"检测什么"可运营配置化，如果改个词表要重启，开放词表就退化成了"换个地方硬编码"。顺带捡到一个产品级 bug 修复的教科书案例：文件头 monkey-patch ultralytics CLIP.encode_text 修 GPU 设备错位，AGENTS.md 第 127 条专门警告不要简化回去——长期运营资产和 demo 代码的区别就在这些注释里。

### 今天最大的决策
回答架构师思考题 1（共享充电宝检测）：先加文本类零样本试运行，用误报率数据驱动"何时转微调"——alarm_images 的 21 个目录 38MB 告警快照天然就是微调训练集的候选池，误报样本库 = 未来数据闭环的原材料。这个"零样本先上、数据回流、够痛再微调"的演进路径记入周六五层图备注，和 LangChat 侧"先 Capability 后 Governance"的节奏是同一个元策略：先让能力跑起来，用真实运行数据决定加码哪里。

## 2026-08-20（Week12-Day4 · Video Analytics 基线：从截图到视频流要改什么）

### 今天最大的认知
截图→视频流不是换采集协议，是执行范式转换：拉动模型（scheduler 到点才算 due、请求响应、处理释放）→ 推送模型（帧持续到达、消费者常驻、状态常驻）。五层耦合联动：采集（无状态 HTTP→RTSP 长连接会话）、处理（定时拉→帧队列推）、推理（0.35 次/秒→525 帧秒，1500 倍，CPU→GPU 必选）、状态（cooldown 外置→Track 常驻内存）、证据（JPEG→环形缓冲剪辑）。而 BaseDetector.detect(image_bytes) 契约一行不用改——改造全在检测器上游和下游，Day2 看到的 adapter 隔离在这里真正值钱。硬信号：config 里 alarm_interval_minutes=1（分钟）与 fire_smoke_check_interval_seconds=15（秒）并存，采样率压力已在参数层现形。

### 今天最大的坑
差点把"全流 25fps"当成视频化的默认答案。算完账才发现被忽略的中间态 B（RTSP 抽帧 1-2fps）才是架构上自然的下一站：保留检测契约、只重写采集层、21 次推理/秒 GPU 轻松扛住、且正好接住火灾 15 秒采样的业务压力。还有一层：OpenSpec 29 个 spec 里没有任何 video/stream/tracking 字样——视频流连规格层都还没进，是 roadmap 谈话不是 reality；而 AGENTS.md 里"password 存明文因为 HTTP/RTSP 都要用"和 legacy 里 update_base_image.py 的 4 种 RTSP URL 尝试，说明 RTSP 凭据和代码足迹早就预留，只是主链路从未启用——数据模型留了门，规格层没立户。

### 今天最大的决策
确立了演进谱系决策框架 A→B→C→D（截图加密→RTSP 抽帧→全流+GPU+Tracking→边缘盒子），每档按"改造量/帧率/事件覆盖/单路成本"定价。判断变量是场景 ROI 不是技术成熟度：跌倒检测防人身诉讼、客流统计支撑租金定价才配得上 C 档 10 万元级硬件；消防通道堆物留在 A 档零成本。竞争位锁定在 L3-L4（告警→工单→通知业务闭环）而非 L1-L2（海康大华盒子地盘）。明天 Day5 的 Business Scene Matrix 就用这条谱系当标尺，给每个商业场景标"需要站到哪一级"。

## 2026-08-21（Week12-Day5 · Business Scene Matrix：哪个商业场景 ROI 最高）

### 今天最大的认知
ROI 排序不按技术先进度也不按价值金额排，按"预算科目 × 资产复用度 × 信任成本"排。三种价值货币（风险规避=保费逻辑/人力替代=工资逻辑/收入增量=租金逻辑）落在两个预算科目（费用/资本）里——消防通道占用行边际成本≈0（21 路摄像头已沉没、5 个规则模板已跑通、新摄像头自动绑定默认规则）价值双算（合规风险+替代 252 次/天巡检），是当期 ROI 王；客流统计金额百万级但属资本预算且要 C 档硬件，是战略行不是当期行。误报率是经济学指标不是技术指标：它通过告警疲劳把三类价值同时翻负，而四层兜底+参数自主可调把它变成运营杠杆。最被低估的是 L5 自动巡检日报——复用已有告警数据资产，边际成本最低的收入型场景，Vision Agent 的最小可行形态。

### 今天最大的坑
差点把 Business Scene Matrix 当需求分析文档写。写完才发现它同时是三样东西：Capability 需求清单（哪行值得按 ADR-003 暴露）、预算答辩武器（费用 vs 资本科目）、路线图输入（档位列映射 Day4 的 A→D 谱系）。另外撞上产品定位与能力地图的张力：域知识.md 明确"不做客流统计"，但客流是五层模型 L3-L4 核心场景——这不是矛盾，是"商业定位（巡检告警产品）≠ 能力地图（Vision Intelligence 全谱）"，矩阵里必须区分 reality 行和 roadmap 行（OpenSpec 29 个 spec 无 video/stream/tracking 是硬判据）。

### 今天最大的决策
矩阵判定结论记入周六画图输入：①当期主打行=消防通道（已有资产复用叙事）；②战略行=客流（资本预算科目，二期答辩用）；③增量行=违停/占道/垃圾满溢（A 档零样本改词表即扩场景，把扩场景从硬件采购降级为配置变更——这是矩阵里最重要的架构经济学事实）；④优先验证行=L5 日报（等 Day6 评估读 DB 直连 vs 走 Capability 两条路线的成本）。架构师思考题 2 的结论倾向：火灾检测合同措辞必须卖"降低概率"不卖"消除风险"，漏报率不量化就不进第一期 SLA 承诺。

## 2026-08-22（W12-D6 周六交付：五层图 + Business Scene Matrix）

### 今天最大的认知
五层模型是 DAG（能力依赖的分类账），不是楼梯（升级路线）。代码级证据：workers/pipeline.py 五站链路（capture→detect→persist→rule→alert）中第 4 站（规则统计）不经过任何 L2 组件——状态型场景从 L1 直接记账到 L4'（工单闭环），跳 L2 是合法架构决策不是缺陷。据此修正了对 MallSenseAI 的定位：不是"低级 L1 系统"，是"窄而深"——L1 六格占四（含 P2 半格）、L3 退化统计两个（duration/area 是无跟踪的 Scene Understanding）、L4 闭环雏形、L2 有意为零（域知识"不做什么"三条 = 主动边界）。初级和专注在图上长得一样，区别在边界是画的还是没爬到的。

### 今天最大的坑
ipynb 实验 3 的行人计数模拟掉进自己挖的坑两次：① 一维世界（所有人同一条线）导致跟踪器身份根本歧义，贪心最近邻偷换轨迹、吞人计数；② 去掉距离闸门后新入场者挂到远处旧轨迹上，把已计数的 tid 复用造成假漏计。修复：2D 泳道世界 + 仅匹配上一帧更新过的轨迹 + 0.04 距离闸门，得到 43/40（~7% ID 切换误差——本身就是真实跟踪系统的教学点）。这个坑恰好演示了 md §9 的论断：L3 退化形态的边界来自 L2 缺失，无 ID 时慢行者被系统性高估（平均停留 80 帧 = 80× 过计数），静态误报（广告画假人）在 L1 下是随帧率线性放大的永久偏差。

### 今天最大的决策
① "MallSenseAI 在 L1 哪里"的正式答案定为格子间坐标而非单点：四格（封闭词表 yolo11n / 领域微调 D-Fire / 开放词表 YOLO-World / 基线比对 absdiff）+ 运行时路由（service.py:63 "prefer YOLO-World, fallback to Debris"——L1 内部已有容错拓扑）。② Business Scene Matrix 升级为层覆盖版（9 行 × 所需层/已有层/层缺口），三条硬结论进交付物：当期 ROI 行 = 层缺口 0 行；L2 是全部 B/C 档行的单点依赖层；L5 日报反而地基最全（L1+L3'+L4'），是最便宜的升层路径——Day5 判定④有了架构学依据。③ 技术债三件记入明日评分：DetectorType 枚举无 yolo_world/floor_cleanliness 位、AGENTS.md detectors 目录注释缺两个文件、Camera.password_hash 列名存明文。

## 2026-08-23（W12-D7 周日 · Virtual CTO：MallSenseAI 能力边界审视 + 五维评分）

### 今天最大的认知
横向对照发现平台本体（LangChat，W11 Code Health 6.0）的代码健康度低于挂在它下面的行业应用（MallSenseAI，7.5：510 后端测试 + 37 e2e + CI 三段流水线）。架构先进性和工程纪律是两个独立计分项——ADR 华丽救不了测试空白，测试纪律也不需要先进架构护航。集成时的信任边界要按 Code Health 画，不按 ADR 画。另一个定稿认知：边界判定三准则（状态型 vs 事件型 / 闭环可审计 / 人力替代 ROI）可以机械化地跑任何新场景，跑 L2 视频流的结论是"值得做但必须作为独立数据契约的新管线"——验证并定稿了 D4 结论。

### 今天最大的坑
ADR-004（MallSenseAI → LangChat AI Vision）声明的三项能力——客流/商品结构化分析、零售 POS/CRM 事件联动、通过 LangChat Channel 回传洞察——代码为零，29 个 OpenSpec spec 无任何支撑。加上 ADR-008（8/21，本周五）langchat→lnkchat 改名落地，MallSenseAI 对外名两周内换了两次（MallSenseAI→LangChat AI Vision→LnkChat AI Vision）。"行业能力包"目前只存在于 ADR 文本：两边各自完整（平台有治理体系、应用有闭环+测试），中间的桥（Capability 注册/Channel 集成）完全没画。

### 今天最大的决策
① MallSenseAI 首评 7.05（AQ 7.0 / CH 7.5 / ADR 6.0 / TD 7.0 / DX 7.5），明确记为"望远镜分数"并预测内窥镜区间 6.3-6.8，W13-D7 复评验证——把 W11 剪刀差方法论从 LangChat 移植到新对象。② 战略结论定稿：未来两季度主战场 = L1 换格子（YOLO-World 改词表扩场景）+ L4 补全（工单闭环指标化），不爬 L2；L2 等场景饱和 + 算力预算到位再作为独立管线启动。③ 术语切换三策略自 W13 生效：历史文档不追改、新笔记用 LnkChat（首现标注）、仓库/库/端口不动（ADR-004+008 双确认）。④ ADR-004 建议在 §1 三项纯规划承诺处标注"目标态"，防止销售/实施误读为现状态。

## 2026-08-25（W13-D2 Security Analytics：误报率为什么是核心挑战）

### 今天最大的认知
误报率在安全场景不是质量指标，是商业模式否决项。base rate 接近零（商场一年真火警 0~1 次）时，模型精度和有效告警质量是两个指标：99% 单帧精度对着每天数百次截图评估，年产误报仍是真报的几十倍——先验概率淹没精度，换更强模型（RT-DETR/大 backbone）救不了。真正的杠杆在模型之外的三层漏斗，且代码里已全部存在：①检测器层四道闸门（conf/label 白名单/area_ratio/ROI 中心点过滤，fire_smoke.py）；②规则引擎时间维度确认（min_stay_seconds 把"瞬时误检"和"持续事件"分开 + cooldown 治重复告警，engine.py 负键 first-seen/正键 last-alert）；③人审社会裁决（AlertStatus.false_positive 一等公民状态，pending→confirmed/false_positive/resolved）。六场景误报治理难度排序恰好等于 Tracking 依赖度排序——误报率是 L1→L2 升级的真实架构动机。

### 今天最大的坑
差点把"误报"当成单一概念处理。拆开才发现至少三种：瞬时误检（单帧噪声，min_stay 治）、持续误报（真有东西但不是违规，如过路搬运，duration/threshold 治）、重复告警（同一事件反复推，cooldown 治）。三种的治理手段完全不同，混在一起调阈值必然顾此失彼。另一个发现级细节：FireSmokeDetector 每个 detection 的 metadata 都带 supplemental: True——视频烟火是烟感的补充不是替代，"不做唯一真相源"本身就是误报治理（法律责任分摊），代码化石里藏着架构决策。

### 今天最大的决策
判定当前最大的 Gap 不是漏斗缺失而是闭环缺失：false_positive 人审标记被结构化留存（还有 Redis HSETNX 保证多 worker 竞争一致），但不回流——不调阈值、不进困难样本集、不驱动任何学习回路。人审在做分类，系统不在学习。修复优先级排序（记入周六 Radar 输入）：短期=阈值回流（用误报标记统计自动建议 confidence_threshold 调整，反馈周期最短）；中期=ROI×时段维度误报画像（蒸汽/夕照类误报有规律性时空分布）；长期=困难样本微调（数据量门槛高，最后做）。同时确认边界设计即治理：域知识"不做消防联动"把误报爆炸半径限制在"人跑一趟"，SLA 只能卖"降低概率"不能卖"消除风险"。

## 2026-08-26（W13-D3 Retail Analytics：视觉能力如何转化为 KPI）

### 今天最大的认知
零售场景的真正瓶颈不在检测在度量衡：像素→检测框→事件→指标→KPI→决策这条装配线上，检测框之后每一步都是测量问题。三个定量结论（notebook 仿真验证）：① 排队等待 W 按 Day1 谱系需要 ID 才能"测"，但 Little's Law `W = L/λ` 用两个无 ID 可测量（队长、POS 到达率）就能"算"——而且病态区反直觉地不在高峰在低峰（分母 λ̂ 趋零，除法放大误差，30 天仿真低流量窗口误差 std 高 1.4×），KPI 报表窗口必须按流量分级；② 检测噪声 vs 检测偏差是两种病：噪声按 1/√N 自动缩减（25 天仿真验证 √N×std 恒定），偏差是永远不掉的地板（−15% 遮挡 → 恒 −0.4 分），加密抽样治不了偏差，高峰段 2 小时人工清点一次校准就能拆掉地板（残差 −0.06 分）——钱优先花在校准；③ OSA 类比例 KPI 的检测混淆（8% 漏检+2% 误报）直接写进月度数字：45,000 次检查平均后抽样噪声塌缩到 ±0.0013，但 −1.3% 偏差纹丝不动，"不校准的报表越平滑越稳定地错"。

### 今天最大的坑
两次被自己的直觉骗，都被 notebook 数据打脸：先验认为"午高峰非稳态 → Little 估计偏差大"，实测恰恰相反（高峰样本密集最贴线，低峰除法病态）；第一版检测模型用 round+clip 模拟计数，结果在空场景引入 +0.5 分虚假系统偏差（clip 的 Jensen 效应），把噪声/偏差实验污染成三向纠缠，换成乘法零均值噪声模型才干净。教训记两条：KPI 类结论必须先跑仿真再写结论；"检测误差对称"是物理上不成立的理想化（真实检测错误以漏检为主，天然负偏）。

### 今天最大的决策
① 判定 Retail Analytics 是 MallSenseAI 打开封闭系统的首选切口：域知识设计决策 #2 封闭的理由是"安防秒级实时性不容编排中转"，反读即"分钟级容忍场景无理由封闭"——零售 KPI 恰好分钟/日级容忍，`retail.kpi.query` 应排在 `safety.alert.query` 之前成为第一个暴露的 capability（用旧 ADR 的边界条件论证新方向，零新增证据）。② 硬 Gap 定位：全仓库无 Metric/TimeSeries 领域对象（entities.py 全是事件型 Alert 状态机），"平均等待"在这套领域模型里无处安放——需要 MetricSample/KPIDefinition/CalibrationRecord 新对象，ADR 级决策不是加张表；检测层反而 60% 现成（yolo_world 换 prompt 即 person/empty shelf，OpenSpec 已有词表热配置场景）。③ 场景级质量策略应进 capability 元数据：安全误报=信任死刑（多层漏斗压制）、零售偏差=慢性毒（一次性校准+大数定律），同一套检测基础设施配不同质量工程——Day2 的"错误经济学分场景"升级为显式建模要求。

## 2026-08-27（W13-D4）Vision Agent vs LangChat Agent

### 今天最大的认知
"Agent"的自治有三种时钟——意图驱动（用户请求）、时间驱动（班次/跑批）、事件驱动（告警），时钟不改变物种。当前 MallSenseAI pipeline 是 automation 不是 agent（规则触发 vs 证据推理的分界）；Vision Agent 不是第三个物种，= L1-L4 感知系统 + LnkChat 数字员工的组合体。真正的结构差异在三件事：**时钟（谁触发）、证据（凭什么推理——LangChat Agent 推理结构化事实，Vision Agent 推理统计量，必须携带置信度说话）、失败模式（fail-closed 拒绝 vs 永不停机降级）**。

### 今天最大的坑
容易把 Vision Agent 想成"CV 领域的另一套 agent 框架"（perception-action loop 自治体），然后陷入选型思维。实际上框架问题平台层已经解决（SkillRelease + DigitalEmployee，ADR-LC-013 的 dispatch guard 代码已落地），剩下的是证据学问题：置信度传播、口径责任、日报公信力。域知识.md 的封闭系统边界在日报场景（分钟/日级容忍）再次失效——和 D3 一样的论证路径。

### 今天最大的决策
L5 推理层选址三案裁决：A 封闭系统内自建 LLM 调用（治理全缺）❌ / B 独立 Vision Agent 产品（双份 runtime 双份治理）❌ / **C 平台 Skill + 视觉 Capability**（MallSenseAI 到 L4 为止，推理住 LnkChat Skill 层）✅。核心理由：变化率分层——检测模型按周变、prompt 按天变，capability 接口把两种变化率切开。前置件：capability 注册表（P0）、日级调度触发源、证据 digest 对齐。

### 遗留 / 下一步
- D5（明天）：MallSenseAI 进入 LnkChat 的身份裁决（Connector / Capability 提供方 / Agent Host，今天思考题①即开场题）+ 集成路径
- 四个不存在的 gap 待 D5 排序：日级聚合层、指标口径层、LLM 推理层、capability 出口
- ADR Health Check 候选：域知识.md「不做客流统计」边界声明（D3 已登记，集成时必须重新裁决）

## 2026-08-28（W13-D5）Vision Capability Architecture：行业能力包 = 契约打包

### 今天最大的认知
"行业能力包"包的是元数据，不是代码。MallSenseAI 进 LnkChat = 三份纸：① Application 元数据（capabilities 子集 × industries 标签，ADR-004 已冻结为 LangChat AI Vision）；② Capability 描述符注册进段2 catalog（lnkchat.vision.*，行业词禁入 ID，ADR-003 正交 facet）；③ Connector 配置（Vision Runtime 留段3 当企业系统，代码/模型/凭证全不动）。MallSenseAI 同时持有三个身份（段1 产品 / 段2 能力提供方 / 段3 企业系统）且不冲突——因为段位不同。三段式链（ADR-007）的价值就是让多身份各就各位。Plugin 是"请人进自己家"（共享依赖与故障域），Capability 是"签互访协议"（独立部署独立发版）。

### 今天最大的坑
集成债全在平台侧，不在 MallSenseAI 侧。catalog.py 证据：① `_register_p0_capabilities()` 只有 2 个能力（knowledge.query/workflow.execute），无任何 vision.*；② registry 是 import 时静态注册的内存 dict——加能力=改平台代码发版，注册表是代码不是数据；③ `runtime_binding={}` 空 dict——capability→段3 路由未建模；④ Connector 子系统缺位（W11-D3 结论重申）；⑤ 词汇分裂：catalog 用 effects(read/write/destructive)，skill_release 用 effect_policy(read_only/conditional_write)，两套词表未对齐；⑥ ADR-004 的 application.yaml 示例还是 langchat.vision.* 前缀，没跟上 ADR-008 硬切换——文档示例与改名不同步。

### 今天最大的决策
effects 语义裁决悬而未决但已定位：lnkchat.vision.detect 触发抓拍+GPU 推理，不写业务数据但产生算力成本——"业务副作用"与"平台成本"是两个维度，catalog 只有一个字段，考虑拆 effects + cost_class（留作 D6 Inventory 的字段建议）。另确认能力粒度公式沿用 ADR-003 命名 `lnkchat.<domain>.<verb>`，domain 拆 vision/safety 两个域待明天裁决。

### 下一步
D6（周六）：Vision Capability Inventory——按今天架构图盘点段3 全部 API/detector/规则/dashboard，产出能力清单+技术雷达+演进路线图（前3 Sprint）。注册表数据化（DB-backed catalog + provider 自注册）应进路线图 P0。


## 2026-08-29（W13-D6）Vision Capability Inventory + Technology Radar + 演进路线图（周六交付）

### 今天最大的认知
盘点的主产品不是清单，是三个发现：① 最大 Gap 不在五层模型任何一层，在平台工程栏——"误报率度量"是零资产且全系统依赖的能力（15 项能力里唯一 ❌ 且被域知识.md 点名为推广卡点的）；② 技术雷达 Trial 环全空——不是没有值得试的技术，是评估→采纳之间的验证管道断了；③ 负资产栏决定路线图第一步（火灾漏报未量化+PIPL+LICENSE 三笔债），资产栏决定第三步（L1 满格+平台工程强，才有资格开 capability 接口）。清单是静态账本，盘点是动态裁决的输入。

### 今天最大的坑
差点掉进"ROI 驱动排序"：W12-D5 商业场景矩阵的冠军是客流（L2 Tracking），直觉上该排第一。但拆开看：客流在商业上是新开产品线（要重新卖、摄像头改造成本+付费意愿都是域知识.md 点名的落地难度），在技术上是架构换代（截图→视频流），在度量上依赖还没立起来的尺子。已部署商场的告警增值是口袋里的钱，新商业线是地平线上的钱——ERP 老兵的排序从来是对账→报表→开接口，不是哪块地值钱先扑哪块。

### 今天最大的决策
前3 Sprint 裁决：S1「立尺子」（PPV/漏报度量管线——关键洞察是 alert lifecycle 的 false_positive/confirmed 标签是运维免费打的 ground truth，量化不需要新采集只需要聚合）→ S2「出报表」（detection_events 日级聚合+指标口径层，同时是 S1 度量的持久化形态和 S3 契约的数据准备）→ S3「开接口」（第一个 capability=lnkchat.safety.alert.query@v1，选拉模式不破坏域知识.md 的秒级告警直发边界；平台侧同步做注册表数据化）。依赖链排序压过技术驱动和 ROI 驱动两种直觉。

### 遗留 / 下一步
- D7（明天）：最终 Virtual CTO Review——两周总复盘+五维评分+ADR Health Check+今天三件套送审
- ADR Health Check 重点：ADR-004 示例前缀未同步 ADR-008；域知识.md「不做客流统计」vs W12-D5 ROI 冠军的冲突裁决
- S1 度量口径的自证偏差（未打标告警系统性低估误报率）进 Sprint 1 任务设计

## 2026-08-30（W13-D7 周日 · 最终 Virtual CTO Review：两周总复盘 + 集成评估 —— 六周主线收官）

### 今天最大的认知
剪刀差规律完成跨对象定稿：LnkChat 四周 7.2→6.4（下探 0.8）、MallSenseAI 两周 7.05→6.8（下探 0.25），两个对象同构复现"理解深度上升 + 五维评分下探"，且复评分 6.8 精确命中 W12 首评时预测的 6.3-6.8 区间上沿。方法论结论：新对象首评必为望远镜分（排期用），+1 周内窥镜复评预期下探 0.2-0.5（还债用）——两种分数永不混用。下探幅度的对象差也有解释：MallSenseAI 的测试纪律（510+37+CI）托住了 Code Health 的底，所以它的内窥镜分（6.8）仍高于平台终值（6.4），"信任边界按 Code Health 画"经复评维持。

### 今天最大的坑
集成评估差点只做成"设计完成度打分"。补上量化维度后才发现真正有决策含金量的是木桶结构：集成通车 = max(视觉侧 S1+S2, 平台侧注册表+Connector)，两侧独立并行、互不阻塞——蒙特卡洛（3 万次）显示长尾几乎全由较慢一侧的悲观情形主导，且敏感度分析给出反直觉数字：帮快侧提速 20% 对通车日期几乎无效，帮慢侧收益数倍。另一个实锤：ADR-004 第 70 行 capability 示例仍是 langchat.vision.* 旧前缀（grep 验证），ADR-008 改名 9 天后尾巴未扫——低严重度高信号（OpenSpec change 没扫尾 ADR 附件）。

### 今天最大的决策
① 集成评估正式结论：战略成立、图纸（三份纸）完成、两岸未动工（设计成熟度 4/5 vs 实施成熟度 0.5/5）、通车窗口在 S3 之后；最大风险不是技术是节奏失配，W14 转入 lnkcre 开发期后视觉侧 S1 若无人认领，桥的图纸会过期（Trial 空环教训）——建议 W14 首周显式裁决：排期或挂起（挂起也要登记冻结日期）。② 悬案裁决：域知识.md「不做客流统计」是架构边界不是责任边界（与"不做消防联动"性质不同），L2 进 P2 路线图不进前3 Sprint；元教训：边界文档必须带类型标签（架构/责任/商业），否则三个月后分不清哪条能翻案。③ ADR-009（vision capability 注册）裁决暂不起草——等 S3 实施证据，先做后立 ADR 好过先立后违背（W11 六条 Review 建议 0 落地的教训）。④ 六周主线（W8-W13，42 天）正式收官：六问全答，三层地图（平台/行业/应用）画完，W14 起按 learning-plan-w14-plus.md 转入开发期，OpenClaw 从架构导师切换为开发搭档，保留周日 Review + 五维评分 + Daily 雷达三机制。

## 2026-09-01（W14-D2）两套语义结构的对账：business-ontology.yaml vs MI Domain Model vs openspec specs

### 今天最大的认知
"已经有 business-ontology.yaml 了，为什么还需要 Semantic Model"是个伪对立——正确答案是分层 SoT：ontology 是**词汇层**唯一权威（883 术语+别名+溯源场景，三源中独有），但它当不了语义层：①缺 Identity/Relationship/Lifecycle/Rule/Policy 五类构件，W1-W6 断链检查一条做不了；②capability 字段是贴纸不是锚点（102 标签中 23 个 L 占位、79 命名标签仅 33 个=42% 对得上 spec，反向 273 spec 仅 12% 被引用，platform-foundation 万能贴纸横跨 8 模块 33 子功能）；③半成品（场景层只填了资源管理 1 个模块 15 条，其余 11 模块 0 条）；④无治理头（文件第一行就是 modules:，无版本/状态/维护人——对比 BCM 的 ORE-1 和 Domain Model 的 D-001）。Semantic Model 不是第五份文档，是**对账层**：不新增权威，单向消费四源、接线跨源引用、产出机器可校验的一致性快照——D-001（BCM 权威+Crosswalk 显式映射 250 条）已裁决过一次同一模式，Semantic Model 是它的升维（两源对账→四源对账）。

### 今天最大的坑
三源对账差点做成"找不同"游戏——罗列名字差异没有决策含金量。真正有含金量的是**扇出结构**：资源管理 1 模块→2 Context（D-001 Amendment A 的物理/商业拆分在模块层完全隐形）、财务管理 1→4（财务链四拆）、运营管理↔客服 2→2（模块吞域）、反向 5 个 Context（Engineering/Customer/Parking 等）在模块层无入口——多对多是常态意味着**任何"模块名≈Context名"的假设都会翻车**，映射表不是文档装饰，是查询路由的必需品（ipynb 实验三：ontology 独答四个真实问题三个断链，fail-closed 显式失败 vs LLM 无声编造的对照）。

### 今天最大的决策
分层 SoT 定稿进 Semantic Model v0.1 宪章：术语/别名→business-ontology.yaml（须补治理头，列为 P0 缺口）；业务能力/行ID→CRE BCM（不可变锚点）；对象归属/边界/生命周期→MI Domain Model；规则/Effect→effect-registry.yaml（5 类冻结）；实现事实/验收→openspec specs+代码。产出第一张模块×BCM域×Context 手工映射 v0.1（12 模块全量），D3 程序化替代。另：W15 LnkChatBI 术语库只能吃术语层（场景层 15/102 填充率不可消费），消费范围预警已写入 md。

### 遗留 / 下一步
- D1（8/31 lnkcre 现状对齐）cron 未产出，未回填；关键事实（273 specs/R-wave/lease→cash MI-AC-001+）已并入今日对账，PT-W4 产出接入挪至 D3 实验输入
- 明日 D3（实验1）：business-ontology.yaml 源内体检——schema 校验/别名冲突/场景 source 分布/程序化模块×Context 映射表；Today's Question"语义资产如果机器不可校验，半年后会变成什么"——今天发现的无治理头就是开场证据
- 登记项：ontology 无 frontmatter 是 Semantic Model 宪章第一条的候选（"每个被消费的源必须有版本+变更流程"）

## 2026-09-02（W14-D3 实验1）business-ontology.yaml 机器体检：语义资产的熵——结构没烂，正在稀释

### 今天最大的认知
"语义资产半年后变成什么"的答案今天被量化成**烂法二分**：它不会写乱（schema 形状 102/102 规整、意外键 0），它会**安静地稀释**——三种熵无人观测下单调增长：完整性熵（role 7/102、场景 15/102 全冻在资源管理）、歧义熵（883 条目实为 792 唯一术语，91 条复用登记无消歧声明，「项目」跨 5 模块 ×16 处）、锚点熵（lnkcre specs 增长下反向覆盖 12%→模拟半年 9%，被对账侧在动、对账依据不动，稀释不需要任何人犯错）。数据字典的死刑从来不是被推翻，是被稀释死——今天 150 行 Python 就能给语义资产配 CI（schema 校验 + W1-W6 判分 + hash 基线体检），26 年前没有这个选项。

### 今天最大的坑
差点把体检做成"报告格式审计"。真正有含金量的是两处**分布不均**：①贴纸质量按模块天差地别（财务 12/12 全锚定 vs 移动端 1/15、数据决策 2/14、预算管理 1/8）——越近期扩张的模块贴纸越失真，锚点熵不是均匀腐蚀是定向腐蚀；②孤儿 Context（02 Party Core/12 Engineering/15 Customer/16 Parking）与 Gap Analysis 最重债务（三业态 Party 未建、normalizeStatus 无待核验态）**精确重合**——ontology 盲区=代码债务，同一份访谈覆盖缺口的两个投影，这条比任何覆盖率数字都有说服力。另一坑：熵增模拟的 +10 spec/月是假设，绝对值不可引用，只有方向结论（无校验→稀释）可进报告——已在 md 里显式标注。

### 今天最大的决策
① Semantic Model 宪章三条候选条款从证据直接导出：被消费源必须有 frontmatter；体检必须可复现（报告带 sha256 基线，重跑 diff=熵增量）；术语跨模块复用必须带消歧声明。已落 `w14d3-ontology-health-report.yaml`（D6 定稿包直接原料）。② PT-W4 六条装配规则对 ontology 判分 0/6 定性为**定位确认而非差评**：词汇层本不该有六构件，但 Semantic Model 必须有——"词汇认识对象、语义才认识事实"的机器判定版；D1 遗留的 PT-W4 接入以此兑现。③ 场景溯源四家分布（华侨城 12/锦和 8/明源 6/悦商 2）说明资源管理是"四家全收敛"模块，其余 11 模块访谈纪要存疑，登记 D6 缺口清单。

### 遗留 / 下一步
- 明日 D4：effect-registry.yaml 冻结 5 类 vs mi 代码事实（lease 状态机/condition-approval/amendment matrix）逐条对账；Today's Question"语义层声明的规则和代码里的 if-else，谁是 SoT"——今天 0/6 说明声明侧近空白，先量实现侧存量
- D5 交叉验证：用 canonical_tables 336 表增长验证熵增方向结论（替代 +10 spec/月假设）；D1 遗留 R-wave 跟读机制并入 D5 开发节奏环节
- 登记项：D6 组装时把「其余 11 模块场景层 0 条 + 溯源纪要存疑」写进缺口列表

## 2026-09-06（W14-D5 实验2，9/6 补录）Domain Model 覆盖率检查：过时、越界，还有第三种

### 今天最大的认知
计划问"Domain Model 过时了还是代码越界了"，472 张表实测后答案是**两者都有+第三种**：表层四个月 +40%（336→472，月增 98~152 张，D3 模拟的 +10 spec/月是乐观假设），同时增长正涌向跨切面桶——BI 70 张（14.8%，最大 Context，分析层吞了 sales_*/alert_*/report_* 事实）+ Platform/Shared 54 张（11.4%，workflow/打印/编码）合计 26.2%，四分之一 schema 领域不可归属。错位的真实方向不是某域越界，是**跨切面能力增速>领域能力增速**，领域 taxonomy 天生接不住。D3 的方向结论（无校验→稀释）拿到实数背书。

### 今天最大的坑
两个结构性陷阱差点漏掉：①**双迁移体系**——MySQL migrations 316 张是活跃子集、migrations-pg 472 张才是全量基线，canonical testdata 并集做裁判，PG-only 表（hazard/office_energy 族）已出现，同一 schema 双方言维护是表层版的 SoT 分叉，不治理就是下一个 D-001；②**稀疏区与盲区重合**——13 工单（3 张）/15 会员（2 张）的稀疏 Context 与 D3 发现的 ontology 四个孤儿 Context 精确重叠，访谈覆盖缺口在语义层和代码层是同一缺口的两个投影，这条比覆盖率数字更有说服力。

### 今天最大的决策
三层归类法（L1 迁移名 417 / L3 表名 34 / L2 包 grep 21，孤儿 18→0，12 灰区显式登记）沉淀为可复用资产：与 D3 的 150 行体检同构成"语义资产配 CI"的第二块——新表在 canonical diff 时必须携带 Context 归属，无归属挡板。覆盖率报告（w14d5-context-coverage-report.yaml）连同月度增长熵增基线直接喂 D6 定稿包，替代模拟假设。

### 遗留 / 下一步
- 补录背景：9/3-9/6 推送管线因旧日期算法静默跳过 D4-D7（已修复+提超时），D4-D6 本晚补齐
- D6 定稿包组装：六构件从 ontology+D3 体检+D5 覆盖率三源合成；「其余 11 模块场景层 0 条」「双迁移分叉」「灰区 12 条」全部进缺口列表
- D7 Virtual CTO Review：以补齐后的 W14 全量产物做五维评分


## 2026-09-06（W14-D4，9/6 补录）Rule 层对账：effect-registry 5 类 vs 代码事实

### 今天最大的认知
"规则在 registry 还是代码"的答案不是二选一，是**分层 + 第三形态**：存在性与意图在 effect-registry（service-effect 评审不注册的理由档案本身就是证据——代码侧 13 Context 仅 3 张表反向验证了它），执行事实在代码，而 amendmentmatrix 把 9 类矩阵做成**运行时可编辑表**——规则数据化，"if-else 在哪"越来越不在代码里。occupancy-effect 是对账标杆：语义（占用随租赁变更）与实现（Go 事务 CreateTx + ReserveRejectsActiveOccupancy 测试锚定）各司其职，语义层不管传输机制，边界划对了。

### 今天最大的坑
registry 与代码之间**没有机器锚点**：5 类 effect 不含任何 package/表引用，对账全靠人读——与 D3 发现的 ontology 无 frontmatter 完全同构，语义资产的三宗罪（无治理头、无锚点、无 CI）在规则层原样复现。financial-effect 落在 billing/collections/arrebalance 多包是多对多映射，人肉对账不可扩展。

### 今天最大的决策
D4 精简执行（对账表+3 例+缺口），四个缺口全部登记进 D6：①registry 无代码锚点 ②frozen 无 CI 强制（新增 effect 不走 ORE-1 零告警）③lead-conversion 断言未核 ④amendmentmatrix 运行时编辑无版本快照。

### 遗留 / 下一步
- D6 定稿包 Rule 构件以本对账为证据基座，四个缺口进已知缺口列表
- amendmentmatrix 变更是否被 lifecycle_audit 覆盖，W15 Policy 语义化日核


## 2026-09-06（W14-D6 实战日，9/6 补录）Semantic Model v0.1 定稿包：从文档到可消费资产

### 今天最大的认知
定稿包的核心决策是**索引不复制**：Semantic Model 做分层 SoT 的裁决层（什么在哪、谁说了算、哪里断了），不复制 business-ontology 内容——复制就是制造第二个需要同步的副本，D3 刚证明锚点稀释不需要任何人犯错。骨架选 Context 不选模块（多对多实证），缺口列表与六构件同等重要（负空间也是语义：service-effect 不注册的评审档案+代码反向验证是示范）。

### 今天最大的坑
组装顺序险些颠倒：D6 依赖 D5 实验报告（覆盖率/增长基线）和 D4 对账（Rule 构件证据基座），两个都被管线故障吃掉——先补实验再组装，定稿包里每个数字才有出处。教训登记：交付物依赖链（实验→报告→定稿包）在有静默跳过的管线里会整体断链，NO_REPLY 护栏+运行说明留痕就是为此修的。

### 今天最大的决策
v0.1 落盘 `semantic-model/` 双格式：六构件+证据指针（sha256_16/代码锚点）+10 条缺口（P0：ontology 无 frontmatter）+熵增基线+第一个消费方声明（W15-D3 术语层 only 预警）。

### 遗留 / 下一步
- D7 Virtual CTO Review：以补齐后的 W14 全量产物五维评分
- W15-D1（9/7 起）：LnkChatBI 精读，管线已修复（新日期算法+超时 1200s），明早 06:00 应正常推送


## 2026-09-06（W14-D7 周日 · Virtual CTO Review：Semantic Model v0.1 质检 + W15 裁决）

### 今天最大的认知
评审不读数字，评审**重算**数字——12 项机器检查直接跑在定稿包×D3×D5×ontology 真实文件上，11 过 1 失败，而那个失败项（C07 孤儿 Context 双源重合）是全场最有价值的产出：D3 报告叫 `02 Party Core`、定稿包叫 `02 Merchant`，**语义资产组装第一天就踩了自己 9/2 刚登记的 G-04（术语复用无消歧）**——消歧不能靠人记性有了实证。深挖还修正了 D5 journal 的过度概括句：盲区≠稀疏，四个孤儿 Context 里 12 Engineering（46 表）/16 Parking（30 表）是大块头（代码长大、语义没跟上的定向腐蚀），13 WorkOrder 反向稀疏（有入口、代码没长）——两种病两种药，比"精确重叠"的原句更有裁决含金量。

### 今天最大的坑
差点把质检做成"文档朗读 + 拍分数"。补上评分稳健性蒙特卡洛（3 万次权重扰动）后才看清：综合 6.4 在均值规则下 68% 区间 [6.1,6.8] 尚算稳健，但木桶规则恒锚 DX=5.5——**报分不报规则等于没报**（同一个资产 6.4 和 5.5 都是真的）。排期用木桶（最弱维度=第一个消费方的成败面），汇报用均值；DX 之所以最低，就是因为第一个消费方还没发生——W15 的全部意义是把这一分挣回来。

### 今天最大的决策
① Semantic Model v0.1 定稿**通过，带 4 项整改进 v0.1.1**（≤1 小时小修，排 W15-D3 前置）：场景层冻结升格机器可读 `scenario_layer_frozen: true`、Context 别名表（规范名以 D5 全名为准）、G-01 frontmatter 四行提案模板。② W15 落地方案 **GO**：双线不变（LnkChatBI 精读 + term-aliases 第一个消费方），附四条护栏——指纹锚（生成物带 sha256_16）、场景层冻结、名称规范、**Demo 前先测导入前基线**（没有基线的 Demo 是展示不是验证）。③ 五维评分 7.5/7.0/6.0/8.0/5.5 综合 6.4（望远镜分，排期用），预测 W15-D7 内窥镜复评 6.0±0.3——剪刀差规则延续到开发期对象。

### 遗留 / 下一步
- W15-D1（明早 9/7）：LnkChatBI 架构精读① NL→SQL 组装链路；Today's Question"为什么第一个消费方选问答而不是生成代码/自动审批"——今天质检已给一半答案（问答恰好只吃术语层这唯一完整可消费的面）
- v0.1.1 小修三件套登记为 W15-D3 实验前置步骤；effect-registry"冻结无 CI"（G-05）与 ontology frontmatter（G-01）合并为一个主仓 change 提案候选
- 挂账未动：LangChat ADR-004 示例前缀未跟 ADR-008 改名（W13 遗留，非本周对象）


## 2026-09-07（W15-D1 周一 · LnkChatBI 架构精读①：NL→SQL 组装链路）

### 今天最大的认知
NL→SQL 组装链路是一条**确定性与概率性分层共存**的流水线：九级流水（RAG 三件套 → M-Schema 选表 → XML 标签 prompt 组装 → 流式生成 → check_sql → 权限下推二次 LLM 调用 → AST 只读闸门 → 执行 → 图表）里，只读保证走 sqlglot AST 九类写操作黑名单（确定性），SSE 事件契约有 openspec 规格管着且可写成 7 条机器可校验不变量（实验①证实），但行权限是**概率性执行**——tables 来自 LLM JSON 自报、fallback 裸 SQL 路径 tables=None 直接整体跳过、改写后复验不含权限条件保留断言（实验②量化：join 表召回 0.93 时 J=3 单次缺口 16%，日查询 4 次即过 50%）。"为什么第一个消费方选问答"的完整答案四条：失败成本被 AST 锁零、只吃 v0.1 唯一完整的术语层、data_training 让消费即反哺、验收证据全落 record log 可机器复核。

### 今天最大的坑
差点把权限下推当成已解决的确定性机制写进验收口径。逐行核对 check_sql:1546（表自报）、get_row_permission_filters:46（空表返回 []）、check_save_sql:1622（复验无权限断言）三层代码后才确认：permissions 模板规则 #3"不要替换原过滤条件"只是 prompt 层约束，漏报/漏合并均静默。Demo 验收口径因此新增 L1' 护栏（改写后 SQL 文本含权限谓词断言），加固方向零新依赖（表提取改 sqlglot AST 遍历，实验③证明注册对账恒 100% 召回）。

### 今天最大的决策
L1-L5 判定梯正式翻译为 LnkChatBI 语境的机器可复核验收口径：L0 基线护栏（D7 裁决）+ L1 身份路径（POSITION_CODE 谓词 + 四级层级列）+ L2 join 链（CONT_NO→租约 + 状态引用）+ L3 降级口径（规则以术语 description 注入，模板原文"可能是计算公式或查询条件"= Rule 构件天然接口）为必达线，L4/L5 标 TODO；实验④判分器在 4 条种子数据轨迹上验证判分稳定（T3 反例"字段代替身份"被稳定识别）。种子无字面 A101：决策走 term-aliases 别名映射（A101→LOC_DEMO_*）而非补种，直接应用 D2"词汇层管命名漂移"结论。

### 遗留 / 下一步
- 权限概率性执行 Gap 与 G-05/G-01 合并为主仓 change 提案候选包；D6 Demo L1' 护栏实测
- 明日 D2：RAG 三件套精读 + MI context provider 集成线 + Semantic Model vs Text-to-SQL 分工边界；线索：术语 description 即 Rule 注入接口
- v0.1.1 三件套仍挂账 D3 前置；assistant 动态数据源（type=1）分支、pgvector 双路检索细节留 D2


## 2026-09-08（W15-D2 周二 · LnkChatBI 架构精读②：RAG 三件套 × 语义分工边界）

### 今天最大的认知
Today's Question「Semantic Model 和 Text-to-SQL 的分界线在哪」的答案不在功能清单上，在**错误归因与修复方式**上：错在词-物映射/关系/口径（语义）→ 治理修（SoT/锚点/CI，覆盖门控、零方差、重试无效）；错在语法/方言/join 写法（组装）→ 校准修（few-shot，概率下降、可重试）。LnkChatBI 三件套就是这条线的物证：术语库收编词-物归一、data_training 收编表达校准、custom_prompt **无检索**全量注入收编口径声明——三件套把确定性层铺满后，LLM 真正"自己说了算"的只剩 SQL 文本组装这一个窄条，而窄条恰好是 LLM 最强、规则最弱的。custom_prompt 的无检索设计今天读懂了：口径不能赌检索命中率，赌输了就是一次静默的错误回答。

### 今天最大的坑
差点把三件套当成同质的"RAG 检索"。逐行读完才发现三者的检索语义完全不同：术语是**单向**子串（sentence 包含 word）、示例是**双向**子串（短问句能命中长示例）、custom_prompt 根本不检索——方向差异是数据形态决定的（术语词短、示例 question 长），不是随意设计。另一个坑：术语归并是"命中任一别名拉全组"，意味着子别名设计就是归一语义单元的边界，写错一个别名整组污染 prompt。还有 to_xml_string 尾部把 XML 转义全部还原（escape_map 反转义）——description 含 `<>` 会直接破坏注入块结构，D3 生成必须过滤特殊字符。

### 今天最大的决策
① 分界线操作化为六构件 × 消费面矩阵：问数消费方的合同 = 术语层为主（Entity）+ Rule 走 description 注入（L3 接口），Relationship 是最大缺口但由 data_training 示例间接承载，v0.1 不欠。② D3 生成规格定稿：父行=规范词+description（定义+口径+Rule 条件），子行=别名（中文/英文/口语/**编码风格值 A101→LOC_DEMO_L101**——实验②证明这类任意编码映射两路检索都救不了，子串 miss 且表层余弦 0.33 不过 0.4 阈值，唯一出路是预喂子别名变确定性命中）；specific_ds=true 圈住 mallcre 数据源，不往 oid 级共享池倒项目私货。③ context provider 风险分类：sync 是 staleness 风险（旧值，可容忍），权限下推是 soundness 风险（越权，不可容忍）——AST 表提取加固仍最优先。

### 遗留 / 下一步
- 明日 D3 实验3：从 v0.1 六构件批量生成 term-aliases + SQL 示例校准集；**前置两件：v0.1.1 三件套小修（挂账两天了）+ 导入前基线测试（D7 护栏）**
- change 候选包再添一件：attribute_mapping 无校验静默跳过（SystemVariable 查不到只 warning）→ 与 G-01/G-05/权限概率性执行合并，四件同宗：语义漂移无机器告警
- to_xml_string 反转义面登记 D3 checklist：description 过滤 XML 特殊字符

## 2026-09-09（W15-D3 周三 · 实验3：Semantic Model → LnkChatBI term-aliases/SQL 示例生成与校准）

### 今天最大的认知
Today's Question「同一份 ontology，喂术语库和喂表结构注释差在哪」的另一半答案被量化了：**差的不是内容是通道能力，而且是四条可测的通道能力**——归并（844 唯一词→14 组语义单元，命中任一别名拉全组，A101 类编码映射 0/4→4/4 的来源）、口径注入（description 是 Rule 构件的 L3 注入口，"空置双口径/押金两粒度/POS 表无铺位需合同桥接"这类警示只有这条通道能命中即进 prompt）、作用域（specific_ds 闸挡住项目私货进 oid 共享池；表结构注释锁死单数据源，承载不了跨 ERP/BI 归并）、可追溯（术语库易失无版本，用指纹 manifest 对冲——消费不改变 SoT 地位，只改变消费物可追溯性，分层宪章第一次实战）。ERP-对象探针基线 0/4、生成后 4/4，BI-P0 8/10→9/10：第一个消费方闭环，而且是带基线的闭环。

### 今天最大的坑
两个，都值回票价。① 拍脑袋绑定被验证器当场抓住：初版给「销售明细」组绑 bipossaledtl.POSITIONCODE，三级验证 FAIL——POS 通道流水表根本没有铺位列（POSNO/FLOWNO/CONTRACT_CODE/BUSDATE），铺位维度必须经合同桥接；先在 starter pack 上校准验证器（11+18 全过）再裁决生成物，失败才可归因于生成物——这个顺序本身就是防自欺设计。② 口径复算翻出陈年差：报告 883/792/91 vs 复算 963/844/40，差异全部来自模块级 aliases（80 处）未入报告计数——同一个文件两种数法，治理头不声明计数口径，半年后没人说得清哪个是对的（G-01 教训+1：四行变五行）。

### 今天最大的决策
① v0.1.1 三件套原位 patch 落地（挂账两天收口）：R2 场景层冻结升格机器可读、R3 Context 别名表 14 条全解析、G-01 frontmatter 提案模板四键，ontology 指纹复验未漂移（bf550bc24de66813）——patch 不触碰 SoT。② 第一个真实消费物落盘 `semantic-model/consumers/lnkchatbi/` 四件（14 组术语/81 别名/11 条 SQL/merge 建议），全部带 sha256_16 指纹 + manifest；specific_ds/datasource_ids 标 SET_AT_IMPORT 不预填——宁缺勿错，防共享池污染。③ 消费率诚实数 6.0%（51/844）：demo 靶覆盖有限是靶子问题不是资产问题，机制由 A101 组闭环证明——报喜也报忧，D6 才有提升空间可测。

### 遗留 / 下一步
- 明日 D4：Policy 语义化（审批流→Policy Model 抽取规则，对照 BCM ADR-004 Binding Model 定义 AI 执行约束声明格式）；Today's Question"AI 需要知道谁审批，还是需要知道为什么找他审批"；今天的铺垫：description 注入口已验证能送口径警示，D4 检验它的上限
- D6 实战日待办：生成物导入 LnkChatBI 实测（mallcre 数据源）+ A101 依据链问答走 L1-L3 + 覆盖率复测；招商线索组缺失（BI-P0 唯一 MISS）登记 v0.2 候选第一顺位
- 验证器 v0 边界登记：裸列名未校验、大小写折叠近似；计数口径差（883 vs 963）并入 G-01 提案第五行
- 微信通道 9/8 起中断（NOTICE-2026-09-09 已留），等 owner 重配对；学习内容落盘链路不受影响

## 2026-09-10（W15-D4 周四 · Policy 语义化：审批流 → Policy Model 抽取规则 × AI 执行约束声明格式）

### 今天最大的认知
Today's Question「AI 需要知道谁审批，还是为什么找他审批」的答案被量化坐实：**"谁"塌缩"为什么"**。复刻 approvalmatrix resolveChain 扫描 56 份单据（7 金额×2 面积×2 租期×2 红旗），同一个终审级别 city 下压着 **4 条互斥理由路径**（金额越带升级/面积带跳级/谓词跳级/红旗下限强制），hq 级同样 4 条——只答"谁"的 AI 把政策理由压成标签必然丢因。更硬的证据是系统自己正丢着"为什么"：三处断链全部坐实——① StartInput.MinApprovalLevel 被 lease/conditionapproval/merchantstatus 多处认真赋值（SAL-021 红/管商户→city），workflow 包内 grep 零消费，红旗单据误路由率 11%（丢下限后 3/28 落回 project）；② workflowpolicy.ResolveRole 返回的映射角色被 `if _, err :=` 丢弃，门禁只验存在性不回填，审批人错配率 100%（策略映射 role 12 vs seed 硬编码 role_id=1）；③ authorization_policy 存了字符串、spec 声明 SHALL enforce、执法点为零。"谁审批"的表都在，"为什么"的字段都在，链没接完——**rationale 不是锦上添花，是当前实现的真实缺口**。

### 今天最大的坑
① YAML 流序列陷阱：`business_key: [a, b] + [c, d]` 在 YAML 里不是拼接是语法错误（流序列闭合后跟 `+` scalar），verify_ipynb 当场 FAIL 一次——修复后才全绿；draft 声明文件自己先被机器抓住格式错误，倒是意外验证了"机检先行"的流程价值。② Go resolveChain 有个容易漏看的细节：终端兜底优先选 hq 行时**只复查带+谓词闸，不复查 threshold_max**——复刻时忠实镜像了这个行为，否则 spec 场景回放会对不上。③ seed/spec 当天分叉的教训：condition-approval-workflow-policy spec 8/7 归档（"不内嵌角色 ID、两分支串行"），seed.go 8/8 写下四节点全 RoleID:1 + 多出 finance_review——W14-D4 发现的"语义声明与代码无机器锚点"在 policy 域原样复现，两份文件隔一天就分叉，人对人传递规格靠不住。

### 今天最大的决策
① 主交付物 **AI 执行约束声明格式 v0.1-draft** 落盘 `semantic-model/policy/`：五块结构（meta/schema 封闭词表/4 条约束实例/known_gaps），每条约束 = applies_to（声明式适用）+ rules（ai_may/ai_may_not/fail_mode）+ evidence（carrier/业务键/rationale_fields/版本绑定）+ explanation（trigger_questions+模板）；机检全过（封闭词表/证据四键/模板占位符⊆声明占位符/fail-open 仅限 act_with_approval）。R5 双消费方设计：同一份声明既能机检又能走 D3 验证的 description 通道进 prompt。② 抽取规则六条定稿（P1 策略是数据不是代码 / P2 升级链带迹遍历 / P3 声明式受限谓词 8-op / P4 fail-closed / P5 版本绑定 / P6 路由与商务计算分离），全部有 file:line 证据。③ 对照 ADR-004 三点校准+一条反哺：权限矩阵就是"声明式适用性"的生产实例；**O-4 反哺证据**——mi 的 auto_route_rule/ConditionJSON 就是 8-op+and/or 受限谓词集且生产在用，若 O-4 复审可直接采纳为受限 DSL 基线不必发明新 DSL；Policy Model 不是第五类 binding_type（O-9 已决策），是 ADR-004 §12.2 显式让渡给下游的领域。④ 三断链+seed 漂移登记为 lnkcre change 候选（与 G-01"语义漂移无机器告警"同宗），学习轨道不擅改主仓。

### 遗留 / 下一步
- 明日 D5：开发节奏定轨——W16+ backlog 按 Semantic Model 依赖排序（断链修复 > 策略载体版本化 GAP-P1 > 通道注入实测），定与主仓同步机制（每周 digest + R-wave 跟读）；Today's Question"学习期雷达机制，开发期保留什么砍掉什么"
- draft 未评审不得消费；D6 实战日：约束 explanation.template 占位符替换后随 term-aliases 一起走 LnkChatBI 注入实测
- GAP-P1（approval_authority_rules 行无版本快照，rationale 不可复现历史）与 W14-D4 缺口④（amendment 矩阵）同病，v0.2 统一裁决"策略载体版本化"
- 微信通道仍中断（NOTICE-2026-09-09），落盘链路不受影响

## 2026-09-11（W15-D5 周五 · 开发节奏定轨：W16+ backlog 依赖排序 × 主仓同步机制）

### 今天最大的认知
Today's Question「学习期雷达机制，开发期保留什么砍掉什么」的答案落成一条裁决标准：**不看机制有没有用，看它防不防开发期两类死法**——语义资产被主仓稀释（漂移）和 AI/资产越界（D4 三断链全是"声明无执法"）。防则保留、必要时改造形态，只服务心智模型建立则砍或降频。裁决结果：Daily Digest 雷达**保留功能砍掉仪式**——拆成 S1 周频深 digest + S2 日探针（秒级 fetch 只数 behind）+ S3 事件触发（>100 或新 wave 当天定向深读）+ S4 落后挡板（>300 暂停消费链开发先全量对齐）；Today's Question 和周日 CTO Review 原样保留（后者增"同步健康"检查项）；砍 10 段式模板与逐对象精读（精读从日程驱动变成事件响应，S3 就是它的合法形态）；新增 S5 openspec change 归档律 + S6 消费回执律。一句话：学习期雷达是望远镜（每天看新东西建星图），开发期雷达是烟雾报警器（平时秒级嗅探保持安静，阈值响了才灭火）。首次三仓 digest 的实证给这条标准供了弹药：lnkcre 落后 199（两周 211 commits、日分布 [12,27,17,17,15,13,2,7,11,26,19,13,18,14]、specs 273→306）、docs 落后 57、LnkChatBI 落后 14——"避免再落后 714"不是过虑，两周就积了近 200。

### 今天最大的坑
① 断言先行被自己的模拟打脸三次：初稿写"深读成本 1/6"（实测 24%≈1/4）、"孤儿峰值个位数"（实测 34，由月度到达高峰 152 决定）、"日探针把感知延迟压到 1 天"（探针压的是危险积压暴露时间，常规感知延迟仍由周节奏决定、最大 6 天）——全部按实测改写；教训与 D3"先校准验证器再裁决生成物"同宗：**结论必须从跑出来的数字里长出来，不是从直觉里写出来再找数字背书**。② builder 脚本的字符串转义两次咬人（YAML 流序列的远亲：Python 嵌套引号里写 Python），最终放弃 builder 内修补、直接对 ipynb JSON 打补丁——生成物的修正应该发生在离真相最近的那一层。

### 今天最大的决策
① **W16+ backlog 按 Semantic Model 依赖排序定稿四批**（排序原则：依赖排序≠价值排序；能启动⇔消费的构件已可信，能验收⇔反哺的缺口有度量）：W16 治理地基+消费面事实化（G-01 治理头 change / G-05 registry 锚点+frozen CI / chatbi 白名单 20 对象登记 Identity）→ W17 消费链扩展+挡板（G-07 citing 模式 / G-04 白名单域术语消歧 / MCP 工具描述 change）→ W18 规则显式化（lease→cash Rule / Policy 声明 0.1 / G-06 双迁移）→ W19 收口（策略载体版本化 / 三断链提案）。拓扑合法性由 ipynb 证明：11 节点 12 边 DAG 无环、批次零违边、最长链 3 节点（G05→POLICY→VERSION 与 CHATBI→G07→RULE 等）、最少 3 串行批 vs md 4 批=留一周缓冲。② **哪个 Context 先接入裁决：租赁域×analysis 消费面**——规则语料最厚（8 态+9 类矩阵+MI-AC 链+审批四载体全在此链）且消费方就绪（chatbi 白名单 20 对象 lease 相关过半，受限 fact_lease_* 恰好构成可见/不可见对照教学集）。③ **digest 首跑抓到两个 P0**：chatbi-governed-account-boundary 把第一个消费方的可见面从假设变成数据库事实（lnk_chatbi_ro 恰好持有 16 open 对象+3 gov 视图+1 函数，白名单外新对象默认不可见直到 citing OpenSpec action——G-07 挡板的现成范本，直接抄）；analysis wave 8 个新 spec 在放大 G-07。另登记分叉信号：docs 仓产品侧出现第二个 ontology.yaml，SoT 唯一性问题待 W16 digest 核查。

### 遗留 / 下一步
- 明日 D6 实战日：① term-aliases/SQL 示例导入 LnkChatBI（mallcre 种子）+ 白名单合规复查（11 条 SQL 必须落在 20 对象内）+ 覆盖率复测；② A101 依据链问答走 L1-L3；③ W16 开发 brief 定稿（今日四批→目标/范围/验收）；Today's Question"这个 Demo 距离生产环境还差几层，每层差的是什么"
- D6 前置：lnkcre 本地 pull 到 origin/main（199 commits）+ ontology 指纹复验
- W16 第一次正式 digest（周一）：重点核查第二个 ontology.yaml 是消费侧副本还是双 SoT 事故苗头
- backlog 是 v1 快照：指纹漂移或新 P0 出现时批次对调走周日 Review 裁决，不中途自改
- 微信通道仍中断（NOTICE-2026-09-09），落盘链路不受影响

## 2026-09-12（W15-D6 周六 · 实战日：双 Demo——导入验证 + A101 依据链 + W16 Brief）

### 今天最大的认知
Today's Question「这个 Demo 距离生产环境还差几层」的答案不是形容词是数字：**五层，每层都有当日实证**——①对象宇宙层：11 条 SQL 全落 mallcre demo 域（bi_*），与生产白名单（lnk_chatbi_ro · analysis 20 对象）**0 交集**、4 个映射缺口对象（bi_b_tenant/bisubject/bipreddeposit/fact_parking_daily）；②数据与编码层：A101→LOC_DEMO_L1xx 是 demo 种子映射规则、示例#2 值域口径与 DDL 数据字典不一致；③权限与护栏层：L1' 未测（权限下推概率性 gap 在案）；④组装确定性层：21 题电池里 6 题术语命中但示例 MISS（子串半径外=LLM 自由组装区）、V2 口语全 MISS；⑤治理与同步层：S6 回执今日闭环但 G-01 治理头未过 change。裁决框架沉淀：不看功能像不像，看**每层的失败模式在 demo 里是否已被消掉**——Demo 证明机制闭环（归并→注入→组装→执行→判定全程可机器复核），生产要求每层失败模式归零；0 交集恰恰说明 Demo 的价值不在"能上生产"，而在把差距从感觉变成可度量可排期的清单（五层里三层的修复动作压在 W16 批次上——这正是 D5 依赖排序的回声）。

### 今天最大的坑
① 对象宇宙扫描器两次漏视图：`create or replace view` 行尾 token 是 `as`，第一版正则不匹配、第二版取错列——修复后 #10/#11 才从 FAIL 回到 demo 域合法 11/11；教训同 D3"先校准验证器再裁决生成物"：**扫描器自己的正确性要先被已知对象证明**。② 值 tokenizer 第一版把裸数字留成字符串，`BDK*10000 + sid` 直接 TypeError——SQLite 无类型列会静默吞下类型错，直到算术才爆；数值/布尔/null 词元必须在装载边界统一转换。③ 差点把"0 行结果"笼统记为种子缺失：逐条归因后发现五种 0 行里藏着真发现（示例#2 值域口径错、#11 是 business_date=2024-12-17 时 90 天窗口内确实无到期合同）——0 行不是噪音，是未分类的证据。

### 今天最大的决策
① **第一个消费方闭环完成且带基线**：import-pack 物化为 starter-pack 同构格式（零适配成本）→ SQLite 镜像导入（结构对齐 Terminology 父子行/DataTraining）→ 幂等收敛 (0,0,0) 证明 → 覆盖率 A/B：术语 2→19、示例 2→13、端到端 11/11 合法执行、S 组守恒无回归；A101 依据链五步全真跑，L1-L3 PASS（L4/L5/L1' 显式 TODO 带理由），"别名映射而非补种"决策被完整验证。② **三个新发现全部登记而非当场消化**：验证器值域枚举缺失（change 候选包第五件，与 G-01/G-05/权限概率性/attribute_mapping 同宗）、通用词『项目』误触（P2/P3 命中≠可答，G-04 新形态素材）、示例覆盖半径 19→13 的差（示例库扩容优先于术语扩容）。③ **W16 brief 定稿**（semantic-model/w16-dev-brief.md）：四工作项（G-01 治理头 change / G-05 frozen CI / 白名单 20 对象登记 Identity + 示例#2 修正 / S1 首次正式 digest 核查第二个 ontology.yaml），范围红线与验收度量逐项落纸，主仓受理周期风险用"立案受理+对账报告"底线化解。

### 遗留 / 下一步
- 明日 D7 Virtual CTO Review（两周总复盘）：学习期→开发期切换评估、v0.1→v0.2 方向裁决（输入=五层差距+四批 backlog+今日三发现）、五维评分趋势 + 同步健康首查
- W16-③ 修订示例#2 回 D3 生成器（description 值域口径 + SQL 谓词改枚举），pack 不手改（S6 回执律）；重出后重跑今日验证链换新回执
- LnkChatBI 真库导入（PG + pgvector embedding + 真实 LLM 问答）为 W16 候选项——镜像已证 upsert 语义与幂等性，embedding 与 LLM 组装仍属未测层
- 微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-13（W15-D7 周日 · Virtual CTO Review：两周总复盘——切换评估 × v0.2 裁决 × 五维趋势）

### 今天最大的认知
评分口径本身成了今日最大发现：复算证明 W8-W13 发布分口径一致为均值（W11/W13 精确命中；W12 发布 7.05 vs 复算 7.00——0.05 手算误差，连"好周"的发布分都从未被机器复算过），唯独 W14 发布 6.4 不可复算（既非均值 6.8 也非木桶 5.5，权重未随分发布）——**评分也是语义资产，发布不带口径=漂移无告警**，与 D3 计数口径差（883 vs 963）同病同宗。由此固化评分纪律 v1.1 三条：发布必带口径 / 预测必条件于周期内已排期修改 / 趋势只在同口径内比较。W14 预测 6.0±0.3 落空的根因也被反事实分解定位（3 万次蒙特卡洛）：剔除周内修复后木桶口径恰好落回区间——**预测者自己排的班（v0.1.1 小修+消费闭环进 W15）推翻了自己按静止资产外推的预测**。

### 今天最大的坑
builder 脚本三重转义两次咬人（YAML 流序列远亲第三案）：f-string 嵌套三引号、annotate 换行转义层级、f 前缀与 .format 混用——三处全部被 verify_ipynb 执行面当场抓住，修三轮才全绿。教训与 D5 同宗（修正发生在离真相最近的层），且机检先行再次自证价值：错不在 ipynb 内容在生成层，没有执行验证就永远不知道。另外两个"坑"其实是礼物：W12 手算误差是复算时意外抓到的；ADR-004 挂账 grep 实锤 L70-73 仍 langchat.*（ADR-008 已裁定 lnkchat.*）——挂账第 3 周，低严重度高信号。

### 今天最大的决策
① **三裁决落定**：切换成立（消费方闭环 + 回执在盘 + 反哺候选≥5，三判据全中，且错误发现方式已从"读出来"变为"机器抓出来"）；v0.2=消费面生产化（白名单 Identity 锚点 / 示例半径 13→19 / 验证器三级含值域 / 消费率 6.0%→≥15% / G-01+G-05+宪章升格；Rule/Policy 不并包留 v0.3）；五维复评双轨发布——均值 6.9（↑0.1）/ 木桶 6.5（↑1.0），**五周来最弱维度首次上移，上移的正是 W14 点名的 DX**。② **同步健康首查全绿**：lnkcre 2 / docs 63 / LnkChatBI 14；SoT 在 origin/main 亦未漂移（docs 拉取零风险，周一随 S1 一并 pull）。③ **两个新登记**：产品级 ontology ×4 无治理头（内容互不相同非分叉，是"治理关系未声明"，并入 G-01 范围，周一 digest 裁决）；今日所有结论带证据指针落盘（配套 ipynb 9 cell 全绿 = 执行版）。

### 遗留 / 下一步
- W16-D1：S1 首次正式 digest（三仓 pull + 产品级 ontology 治理裁决 + R-wave 跟读）+ G-01 治理头 change 提案起草（范围扩入第五件同宗）
- W16 brief 维持四工作项 + Review 追加（产品级 ontology 治理关系声明并入 G-01；评分纪律 v1.1 即刻生效）
- 校准履历样本量 2（W13 命中上沿 / W15 MISS 偏高）——样本攒到 5 再评预测器本身
- 微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-14（W16-D1 周一 · S1 首次正式 Digest × 产品级 Ontology 家族治理裁决 × G-01 提案起草）

### 今天最大的认知
Today's Question「多一份 ontology 为什么是事故苗头」的答案固化为**双证据判定框架**：内容证据（管辖域重叠度）定性质，治理证据（关系声明）定风险——分界线不在内容相似度。五件真实文件量化坐实：SoT × 四件产品件模块 Jaccard = **0%**（既非消费副本、也非同域双 SoT，是**平行产品本体家族**）但反向引用双向 **0 处**（治理关系零声明）；legacy × live 模块集 **100% 同名**、指纹不同、子功能 18→26（拷贝演化无指纹链——拷贝就是分叉的前置态）；「数据源管理」已在 LnkChatBI × lnkreport **同名异义**（子功能交集 ∅）。结论：『内容不同』≠『分叉』也≠『无害』——平行家族不违反 SoT 唯一性条款（无同域竞争），却制造同样的事故面（选件无据 + 演化无链）。治理头的价值由此更准：不是"声明谁是老大"，是**把谁管什么/从哪来/谁维护从知情者脑中搬进机器可校验的文件头**——与 effect-registry 冻结声明、chatbi 白名单 citing action 是同一模式的三次实例化。

### 今天最大的坑
① ipynb gate-demo 图中文标题显式 `family="monospace"`，CJK 字形回落 DejaVu Mono 缺字——verify 第一次就 OK（代码全对）但图上有豆腐块：**执行验证只验代码不验渲染质量**，"verify 通过≠交付正确"；直接 patch ipynb JSON（修正发生在离真相最近的层）后重验全绿、警告归零。② 流程险情：w14-plus 无 W16 逐日条目，若按字面走规则④就 NO_REPLY 了——但计划链实际闭合（W15-D6 条目交付 w16-dev-brief → brief 工作项④明定"周一 D1 = S1 首次 digest + 核查第二个 ontology.yaml"，与 D7 复盘下一步一致）；已在 md 头部留「计划来源说明」，并建议 Jason 在 w14-plus 补一行指向 brief 使计划链显式闭合。

### 今天最大的决策
① **S1 首次正式 digest 落盘** `semantic-model/sync/digest-2026-W38.md`：lnkcre 15 commits（baseinfo 主数据纵深，spec 306→311）/ docs 63 commits（CAO 受治理自主进化章程 + R001 Controller Spike + tool routing = 工具级治理在产品侧成形）/ LnkChatBI 14 commits（**domain-semantic-pack-contract 归档**）。两个 P0 均不动 W16 批次：前者是 W17 ⑥ MCP 工具描述生成的需求侧证据；后者把 W16-③ 从"修订示例#2"升级为"修订+对齐契约"（S6 回执新增契约对照项）。挡板未触发（max behind 63 < 300）；SoT 指纹 `bf550bc24de66813` 复验未漂移。② **裁决+处置一体**：五件家族逐件裁决（digest §5 指纹表）；G-01 change 起草落盘 `semantic-model/changes/g01-ontology-governance-header/`（proposal + reconciliation，openspec 格式 draft）：SoT 五键治理头（version/status/maintainer/change_process + **counting_caliber 计数口径第五键**，883/963 教训固化）+ 四产品件最小治理块（authority_scope/custody/derives_from/relation_to_mi_sot）+ **registry.yaml 家族登记簿指纹链** + legacy 标 frozen；待主仓裁决三点（立案载体 lnkcre-openspec vs docs-evidence-chain / registry owner / 是否建 lnkcre 引用 spec）。③ 三仓全部 pull 对齐（ff-only），S2 日探针明日起每日执行，W39 digest 指纹基线 = 今日 registry 值（ipynb §6 已打印存档）。

### 遗留 / 下一步
- 明日 W16-D2：G-05 effect-registry 代码锚点 + frozen CI 红绿本地演示（消费 W14-D4 对账清单；今日 registry/指纹链是同一治理模式的 docs 侧兄弟件）
- G-01 提案待主仓立案受理（对账报告已成，brief 底线达标待立案）；w14-plus 建议补一行指向 w16-dev-brief
- 登记待查（P2）：trade/industry 字典表是否产生新 canonical 表/术语 → W16-③ Identity 登记时一并核
- 微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-15（W16-D2 周二 · G-05 Effect-Registry 代码锚点 × Frozen CI）

### 今天最大的认知
Today's Question「frozen 被违反时谁说不」的答案：**退出码**。`# Registry frozen v1.0` 昨天还是写给读者看的注释，今天被编码为 `frozen_effect_ci.py` 的两门（anchors 门治 W14-D4 缺口①无机器锚点、registry 门治缺口②无 CI 强制），8 场景红绿双向实测：篡改实现证据/新增第 6 类/伪造未立案 change 全部 exit 1，带已立案 change 才 exit 0——**门禁不消灭变化的权利，只给变化定价**（想改冻结项？先立案）。锚点设计的关键取舍：`(file, line, expect)` 三元组里行号只是首次观测值，三级判决把"证据消失"（BROKEN 红=违规）与"位置漂移"（DRIFTED 黄=维护）分开——蒙特卡洛（5 场景×400 次，真实文件）证明纯行号策略良性场景 100% 误报（狼来了→团队关告警的完整理由），包路径策略（现状）违规 0% 告警（静默腐烂），C 策略 0 误报+改名/删除 100% 抓获。**今日最重要实验发现：子串锚点对"扩名不改名"（StatusDraft→StatusDraftLegacy）盲**——新名包含旧子串，这是子串语义的固有代价不是 bug，已作为显式断言登记（`assert tamper_extend C==0`）；B 策略恰好此类全中但无法分辨哪次是对的——什么都报的策略总会蒙对几类。治理工具的第一性指标不是能抓到什么，是**误报率低到没人想关掉它**。

### 今天最大的坑
ipynb 构建脚本再踩 f-string 三重转义（W15-D7 同宗，第 N 次）：builder 的 f-string 与 notebook 内字典字面量 `{{}}` 混用导致两处 SyntaxError，被 verify 当场抓住；第一版模拟的"篡改"写法 `exp.replace(exp, exp+"Renamed")` 根本没破坏子串（新串仍包含 exp）——**模拟篡改先问自己：突变后的字符串还包含原锚吗**，修法是把篡改拆成"改名"（新名不含旧子串，C 抓获）与"扩名"（含，C 盲）两类分别断言，反而把盲区变成了显式登记的发现。另外 S4 演示 initially 红——`--change` 找不到 changes-dir（脚本默认 semantic-model/changes，演示建错位置），脚本行为正确、演示参数错：门禁第一次抓住的就是它自己的使用者。

### 今天最大的决策
① **G-05 落盘双工件**：`semantic-model/governance/g05-effect-anchors.yaml`（5 类×3 锚=15，声明/执行/档案三侧面，真实基线 15/15 OK @ 0392e107）+ `governance/ci/frozen_effect_ci.py`（两门，--json 机读输出）；brief 验收②「红绿可测本地演示」双向达成。锚点选 expect 子串而非整行精确匹配：对格式化重排（gofmt 对齐空格变化）免疫。② **S6 用 service-effect 做篡改素材**——它是 2026-07-29 经 PT-CS-06 评审被拒注册的类型，用它演示"不走 ORE-1 的注册"恰是该流程要防的事故，演示素材即语义。③ **G-05 锚点进 S1 周验基线**：digest 增锚点漂移项（15 锚 DRIFTED/BROKEN 计数），与 D1 registry 指纹链同窗复验；G-01 提案继续等主仓立案。S2 探针：lnkcre 9（baseinfo 波次尾段，拉齐锚定）/docs 3/chatbi 0，挡板未触发。

### 遗留 / 下一步
- 明日 W16-D3（brief ③）：chatbi 白名单 20 对象 Identity 登记 + 示例 #2 值域修订重出 pack + S6 回执换新；**须对齐 LnkChatBI domain-semantic-pack-contract（D1 digest P0）**；trade/industry 字典表新术语一并核
- G-05 v0.2 候选：expect 升级为定界签名（治扩名盲区）；锚点漂移项进 W39 digest
- G-01 提案待主仓立案受理；w14-plus 建议补一行指向 w16-dev-brief（D1 已提，待 Jason）
- 微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-16（W16-D3 周三 · ChatBI 白名单 Identity 登记 × 生成器 v0.1.2 值域修正 × Pack 契约化重出）

### 今天最大的认知
Today's Question「为什么修正必须回生成器源头」的答案：**pack 是投影，不是源**——直接改 pack = 在投影上打补丁 = 下次重生成补丁必丢，且没有机器证据能区分"手改的包"和"生成的包"，漂移从此无声开始。修正回源后三重保障：changelog（人可审计）+ 回归哨兵断言（`= 2` 必须在、`= '空置'` 必须不在）+ 全链指纹换新（漂移可检测）。**分层 SoT 宪章的消费面实例：改投影是漂移，改源是演进**。今日最强证据是 #8 的连带发现：正因为验证器建在了源，复验时揪出第二处同病——BILLMONTH 是 varchar(32)（种子 '6' 型月份串），裸数字谓词在 PG 类型报错、在 SQLite 静默恒 false；W15-D6 归因"种子无 12 月账单"只对表层，**即使有 12 月数据旧谓词也永远查不到**。同样 0 行语义完全不同：一个是坏了，一个是没数据——错误归因决定治理动作的值域版。

### 今天最大的坑
① 构建脚本嵌套引号第 N 次翻车（builder 外层定界符 vs cell 内 f-string/yaml 三引号/正则转义），verify 连环抓出 6→2→1 个失败 cell 才全绿——**每次都是 verify 抓的，这就是它存在的理由**；教训新增一条：含内层 `"""` 的 cell 外层一律 `'''`，正则转义在外层非 raw 字符串里必须加倍。② `plt.cm.get_cmap` 在当前 matplotlib 已移除，直接用 `plt.cm.RdYlGn`——老 API 肌肉记忆在环境升级后是雷。③ 手滑在 md 里写了一个"看起来像"的 spec 指纹占位，写完核对 identity yaml 实测值（80c720f39832e44d）后改回——**指纹没有"大概"，只有实测**。

### 今天最大的决策
① **Identity 登记走 G-05 同门设计**：20 对象（16 open + 3 gov 视图 + 1 函数）+ 6 负锚点（5 restricted + refresh_run——边界的一半是"不能看见什么"）全部 `(file, line, expect)` 锚定进 `governance/identity-analysis-anchors.yaml`；血缘事实显式化：9/20 有 demo 血缘（5 干净 + 1 缺口承接）、11/20 无血缘（即 W17 backlog 清单）、4 缺口对象登记不隐藏。**权限边界也是语义资产，且是最不该靠人读的那一种**。② **P2 待查裁决**：trade/industry 字典零新增 canonical（industry_dict_aliases/trade_definitions 8/28 前已在册）；真实增量 472→477 是工程条件库 5 张 + 门店变更台账 1 张——v0.1.1 的 table_total 过期，登记进 W39 digest 刷熵基线，不静默改计数。③ **契约对照不粉饰**：回执 contract_alignment 8 项 = 4 ALIGNED + 3 PARTIAL + 1 N/A，demo profile 未注册（先于框架存在）如实标注为生产 pack 接入项——PARTIAL 项就是 W17 backlog，契约对齐不是打勾练习。

### 数字速览
值域复验 11/11（9 PASS+2 N/A，0 FAIL，生成器自报与独立复算一致）｜#2 真跑 0 行→1 行（LOC_DEMO_L202）｜幂等全 0｜电池 2→19/2→13 守恒｜e2e 11/11｜A101 L1-L3 PASS（DDL 枚举口径随组注入）｜指纹换新 terminology 2deb9b63→8137b094 / sql_examples 9d3fbb38→0af3cb1f｜S1 检查单 2→5 项（G-05+Identity 锚点漂移进周验，基线 lnkcre 0392e107/docs c3d08d6/LnkChatBI c8927267）

### 遗留 / 下一步
- 明日 W16-D4：G-01 立案窗口跟进（docs behind 10 未消化，受理状态核查）+ 两套锚点（15+26）周验预演 + G-04 v0.2 别名素材定稿（V2"空着的铺"全 MISS 与『项目』误触今日电池再复现）
- 无血缘 11 对象（dim_date/dim_trade/mv_ops_daily 等）W17 生产绑定重生成时逐个补对象白皮书
- G-01 提案待主仓立案受理；w14-plus 建议补一行指向 w16-dev-brief（D1 已提，待 Jason）
- 微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-17（W16-D4 周四 · 两套锚点周验预演 × Identity 验证器补位 × G-01 证据链深化 × G-04 素材定稿）

### 今天最大的认知
Today's Question「验证器自己错了谁来红」的答案：**没有人——除非专门造一个会错的场景让它红给你看**。预演第一跑就抓到现行：负锚点 snap_lease_daily 注册在 L17（那里只有授权对象 gov_snap_lease_daily），朴素子串匹配 `"snap_lease_daily" in "gov_snap_lease_daily"` = True → **假 OK 绿了一整天**，锚的是错误证据（真实排除条款在 L23）。这相当于向关联方函证却把关联方回函当第三方确认——程序做了，证据错了。方法论沉淀：**门禁交付必须附带突变证据（改 X 必红、不改必绿、改无关不误伤）；没有突变证据的门禁只是绿色的装饰品**。brief ② 验收线从「红绿可测」升级为「红绿可测 + 突变留痕」（identity_anchor_ci.py selftest 成为可重放子命令）。

### 今天最大的坑
① edit 工具对 ipynb 的 JSON 转义敏感（外层找内层转义文本永远差 5 个反斜杠）——notebook 修补一律走 python json 读改写，不再硬 patch。② verify 抓出两个真 bug：G-05 门输出的「合计行」也含 BROKEN 字样把计数顶到 2（判决行以 [ 开头过滤）；claims JSON 键名 legacy-frozen-snapshot 与 notebook family 命名 legacy-frozen 不一致——键名映射第一次还搞反了方向（把 family 键映射去 JSON 侧），KeyError 教你重读自己的 diff。③ 负锚点双检设计差点做成"单检"：只查「排除条款还在」抓不住「对象被加进授权清单」（最危险的漂移方向）——授权区泄漏检查（restricted 对象出现在 SHALL hold 段落 → BROKEN）是今天最有价值的一行逻辑。

### 今天最大的决策
① **Identity 验证器补位而非复用 G-05 门**：匹配语义各自适配锚定对象——spec 文本是标识符世界（gov_x ⊃ x 子串碰撞 → 词边界正则），Go 代码锚是语句片段（无嵌套场景，子串够用）。强求"统一验证器"会把一方的正确语义变成另一方的误报源。② **修复走重锚不是改词**：负锚点 L17→L23 重锚 + 登记升 v0.1.1 留修订记录——改登记（源）而不是让验证器迁就错误登记（投影），与 D3「改投影是漂移，改源是演进」同一条宪章。③ **G-01 对账报告 evidence-chain 深化**：仿 docs 仓 40-delivery 范本把 E1-E5 一次性快照变成 C1-C5 可重放断言（复核命令/期望/实测/日期），受理状态如实核验=未受理（15 增量 commits 零 ontology/governance 主题），不粉饰不催办。④ **G-04 素材定稿宁缺毋滥**：『空着的铺』直录（两次电池全 MISS 实证），『空铺』『没租出去的』标 inferred:true 未验证不注入；『那个铺子』留痕拒收（指代不完整，消歧责任在对话层不在别名层）。

### 数字速览
S2 探针 lnkcre 0 / docs 10→15 / LnkChatBI 0（挡板未触发）｜G-05 门 15/15 OK GREEN（HEAD 0392e107 零漂移）｜Identity 门修复后 26/26 OK（20 正 + 6 负 + 授权区 L10-L18 零泄漏）｜selftest 5/5（M1/M2/M3 exit 1、M4 exit 0 黄不红、碰撞哨兵 PASS）｜G-05 突变恰 1 BROKEN exit 1｜G-01 证据链 C1-C5 全 PASS（五件指纹 docs +15 commits 零漂移；受理=未受理）｜格式问题 2 项当日清零（负锚点无验证器、子串碰撞假 OK）｜S1 检查单 rehearsal_2026_09_17 落盘（W39 digest 五项全部可执行）

### 遗留 / 下一步
- 明日 W16-D5：brief 验收对账预演（①-④ 验收线逐条自评 + 缺口清单）；W17 backlog 固化（G-07 新表挡板 citing-action 范本草稿——抄 Identity 三件套：正锚点+负锚点+泄漏检查）；周日 Review 材料包（五维评分 + 同步健康增查）
- G-01 立案窗口仍未开启，周日 Review 裁决是否挂起至 W17 与 G-07 并轨提案
- docs 6 个「备份」commit 语义待 W39 digest 定性（避免把备份线误读为治理线）
- Identity 门只锚 spec 文本；生产 PG 实际 GRANT 与 spec 一致性的机器对账 = W17+ 候选（需生产只读凭证）
- 微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-18（W16-D5 周五 · Brief 验收对账 × G-07 活事件与挡板范本 × 周日 Review 材料包）

### 今天最大的认知
Today's Question「验收线守『我做没做』，谁守『世界变没变』」的答案：**今天之前——没有人，这就是缺口本身**。四条验收线逐条复算三绿一黄（每条都运行时重放：SoT sha256 / git 增量主题扫描 / 两道门实跑 / pack 磁盘指纹 vs 回执对账），但当天最重要的发现不来自任何一条线：S2 探针背后多看了一眼 commit 内容，lnkcre 0→19 增量携带 **canonical 477→484（+7 孤儿表：leasing_policy 族 5 + unit_pricing 族 2，PG 迁移 000227/000229）**，语义层零登记、四线全盲。验收线是合同条款（静态/我方/时点），漂移是环境事件（动态/他方/持续），合同管不了环境——年审关账检查表再完美也不能替代银行对账单的日对。ERP 映射：**项目验收全优、三个月后账实不符**的系统，病根从来不是验收不严，是审计师走后例外报告没有同步上岗。方法论沉淀：**每次验收对账必须问「这些线之外，今天世界上发生了什么我的门看不见的事」——没有这个问题，验收就是在路灯下找钥匙**。绿色的合同和空白的雷达相互掩饰，比两边都红更危险。

### 今天最大的坑
① verify 第一跑 FAIL 在 §3 蒙特卡洛：延迟公式写成了「绝对检测日 − 期内随机偏移」，随检测日 d 增长（不是相对到达日的延迟），g.mean() 断言当场抓住——**模拟先行不变量检查：延迟必须与 d 无关且有界**；重写为「检测日−到达日+日内粒度」后过。② builder 首跑 NameError：cell 字符串里的 BASE 与 builder 命名空间是两层，静态字符串策略消灭了转义坑，代价是变量作用域也要分两层想。③ 双迁移目录实锤：MySQL 侧 migrations/000229=custom_form_types，PG 侧 migrations-pg/000229=unit_pricing_batch_model，**编号各自独立**——按单目录找新表必漏，G-07 实现必须并集扫描。

### 今天最大的决策
① **验收线全部活算复算**：三绿一黄里黄的那条（G-01）我方侧 100%（C1-C5 证据链重放全 PASS，5 分钟）、受理侧 0%——docs 受理机器活着（同窗 accept 了 PRD-LC-E1/F1/DV-LC-004），我们的件不在队列≠被拒；验收线设计必须区分「我方断言」与「他方事件」。② **G-07 草稿事故驱动起草**（governance/g07-newtable-guardrail-draft.md）：正/负/泄漏三检的集合版（新表∉登记∪citing→红；登记消失→红；新表零引用→红=今天事件形态）+ citing-action 定价模式（不禁止加表，给表定价：落地后一个探针周期内须立 change 引用，登记或显式不入域都算）+ S2 探针升级药方（从数 commit 到数表，`git show origin/main:canonical_tables.txt` 集合 diff 秒级无 pull）。③ **周日 Review 材料包落盘**（sync/w16-review-materials.md）：五维预填 7.0（带 W15 预测偏高的教训，先跑证据再对分）+ 三议题（G-01 挂起→W17 与 G-07 并轨双 change / G-07 提为 W17 首位 / D6 把 ipynb mini 门转正 canonical_drift_ci.py）。

### 数字速览
S2 探针 lnkcre 0→19（origin 51e9baf9）/ docs 15→22（备份×13+lnkchat受理×4+mi-cre×4+lnkreport×1，零 ontology 主题）/ chatbi 0｜canonical **477→484（+7 孤儿 / 0 死登记 / 7 泄漏）**，模型 yaml 自报 472——「三数一表」口径披露｜G-05 门 15/15 GREEN｜Identity 门 26/26 GREEN + selftest 全过｜C1-C5 重放全 PASS（SoT bf550bc24de66813 四度一致，五件指纹 5/5 零漂移）｜pack 磁盘指纹=回执（8137b094/0af3cb1f），值域 11/11 复现｜specs 311→314（白名单 spec 未触碰，W39 pull 后 26 锚预计零漂移）｜MC（λ=0.57 张/天标定，90 天×5000 次）：周 digest 均值 3.72 天/最坏 7.0 天/积压 p90 峰值 6 张；日表门 0.75 天/1.0 天/0 张；**P 只数 commit 的日探针曲线与 W 完全重合——速度是假象，看见的才作数**｜ipynb verify OK（5 code cells）

### 遗留 / 下一步
- 明日 W16-D6（周六动手日）：G-07 原型转正 `governance/ci/canonical_drift_ci.py`（三检 + fail-closed + --json + selftest 注入排练，+7 表做回放用例）+ G-01 并轨 change 骨架起草（等 D7 裁决立案）
- +7 孤儿表在案未判：W17 G-07 首个 citing change（至少 leasing_policy / unit_pricing 两族）；canonical 熵基线 477→484 待 W39 digest 刷新
- 周日 D7 Review：消费材料包（四线对账/五维预填/三议题/同步健康增查）
- docs 备份线累计 13 commits 语义定性 = W39 digest 议题；analysis 域第三消费方（LnkReport doc-grain 视图 3 个）另立清单不并入 chatbi 白名单 = W17+ 候选
- G-01 受理第 2 周未开窗（我方侧自足，裁决权主仓）；微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-19（W16-D6 周六 · G-07 集合门转正 × 活事件回放 × G-01 并轨骨架）

### 今天最大的认知
Today's Question「计数比对和集合判决都能发现 477→484，为什么必须是集合门」的答案：**计数门缺的不是灵敏度，是「对象」**。四个结构性盲区每个都无法靠调阈值补上：①无对象性——citing-action 是逐对象定价（每张表一张裁决），不知道哪 7 张就无从定价；②无方向性——等量换血（删1加1，477→477）计数门全盲（selftest M5 + ipynb §3 蒙特卡洛实证：swap 检出率计数门 0% vs 集合门 100%，全 k）；③无归因链——集合门每个 BROKEN 挂着 pg:000227@L18，报警里带着地址；④无负锚——计数对「谁消失了」同样失明（死登记=说谎的台账）。ERP 映射：**总账控制总额 vs 明细账+凭证链**——库存月盘点总量对上不敢签字（串户/错仓/以次充好都不改变总量），银行对账余额一致不是平（逐笔勾稽才抓对象级错配）；控制总额 necessary not sufficient，**不到对象的对账是假对账**。「S2 从数 commit 升级到数表」的说法还保守了——数表仍是计数，真正的升级是判决对象从标量变成集合（输出 results[] 逐表 verdict，不是 summary 计数）。

### 今天最大的坑
转正当天抓出四个 bug，全在「ipynb 原型没走过的路径」上：①`git grep -E` 是 POSIX ERE 不支持 `(?:`（rc=128 fatal）——修复=方言隔离：粗滤交 git（固定串 CREATE TABLE）、精判留 Python re；②正则交替未外层分组，`CREATE TABLE A|B|C` 实为 `(CTA)|(B)|(C)`，CREATE INDEX 行假阳性——靠「单表单 CREATE」的输出形态预期抓住；③`migrations` 是 `migrations-pg` 的**前缀**，side 判定把 PG 迁移标成 mysql——D4 词边界坑的目录版重演，教训泛化成规则：凡「名字包含名字」都要精确边界；④selftest 自己把 change 子目录当 --changes-dir 传（应为 changes 根），M2（唯一期望绿的突变）FAIL 暴露它——**selftest 不是门的配件，是门的第一用户**；fail-closed 哲学同样适用于测试本身。四个 bug 没有一个被「代码看起来对」防住，全部被运行时证据抓住——静态审查守不住动态世界，门如此，门的实现也如此。

### 今天最大的决策
① **G-07 原型转正为 canonical_drift_ci.py**（governance/ci/ 第三道门）：冻结基线 canonical-baseline-w39.txt（477 表，source_rev 0392e107，集合指纹 1a4c50e673ef32d2，排序哈希→行序不敏感；头部声明「快照非 SoT，升级须 digest 裁决」）；正/负/泄漏三检 + fail-closed + --json + selftest 六突变；活事件回放 7 positive BROKEN + 7 leak BROKEN（归因 pg:000227@L18/35/85/100/123 + pg:000229@L1/30 单行精确）→ **W17 验收线 1/2 提前达标**；--change 承认路径预演 GREEN（citing-action 生命周期完整走通：门不禁止加表，只要求裁决）。② **两个非显然设计**：泄漏检查不被语义模型 snapshot 文本豁免（yaml 是结果、changes/ 是过程——G-01 同款理由不在自己门里开倒车）；citing 扫描排除 `_drafts/`（草案无裁决效力）。③ **G-01×G-07 并轨骨架**落盘 changes/_drafts/（DRAFT 等 D7 议题 1 裁决）：Why 四条证据链（G-01 原三条 + 活事件第四条——次日 +10 commits 同波次扩案，案发家族仍在生长）+ What 六点 + W17 验收线现状表；材料包追加 D6 补充节。

### 数字速览
S2 探针 lnkcre 19→29（origin 94b83434，+10 commits：canonical 484 不变零新表，但 leasing_policy/unit_pricing 波次延续——孤儿案家族扩案中）/ docs 22→23（备份线第 14 commit）/ chatbi 0｜基线冻结 477 表（fp 1a4c50e673ef32d2，行序不敏感）｜活事件回放 RED：7 positive BROKEN + 7 leak BROKEN + 0 死登记 + 0 假阳性，归因双目录单行精确｜selftest 6/6 PASS（M1 孤儿红/M2 citing绿/M3 死登记红/M4 零误伤/M5 等量换血红/M6 fail-closed 红）｜--change 承认预演 GREEN（cited 7/7）｜MC（真实 477 表名×2000 次/格）：swap 检出率 计数门 0% vs 集合门 100%（k=1..8）；add/drop 双门 100%；reorder 双门 0%｜验证器 1→3（frozen/identity/canonical）｜转正日 bug 4 个全数运行时抓获｜ipynb verify OK（5 code cells）

## 2026-09-20（W16-D7 周日 · Virtual CTO Review：治理地基验收终审 × 477→499 活事件裁决 × 五维复算与 W17 定轨）

### 今天最大的认知
周日 Review 的最大发现不来自任何验收线，而来自门自己：**冻结的基线第二天就过期**——canonical 基线 477 冻结于 D6，今晨现实已是 499（两日再 +15：indicator-target ×3 @000233、leasing-progress ×10 + unit_leasing ×2 @000234）。G-07 门转正次日即执勤：44 BROKEN（22 孤儿 + 22 泄漏，cited 0）RED，归因 file:line 单行精确。门的价值由此更准一层：**不在基线永远对，在漂移从此有地址、升级从此是裁决而非猜测**（基线头部自 declare 升级须 digest 裁决——W39 周一执行 477→499，对齐源恰好是主仓自己的 testdata 清单）。同窗主仓出现 `canonical_set_test.go`（integration 门，testdata 清单=499）：主仓用「库↔清单」对照，语义层用「清单↔迁移源+裁决」对照——同一焦虑的两层执法，互补不竞争，且是 G-01「平行本体家族」教训的自我适用：若主仓升格为 spec，G-07 应对齐引用而非平行演化。

### 今天最大的坑
① **探针错仓**：首跑 S2 时 cd 顺序 fallback 命中 `/root/langchat-docs`——它同样含 lanlnk/ 目录树（连 business-ontology.yaml 都是同指纹副本 `bf550bc24de66813`），得假值 87；真仓 `/root/docs` = 24。假值险些进 Review 材料，自查 docs 主题与 W38 digest 对不上才发现。教训：S2 探针从未脚本化是人肉流程，W17-D1 落 `sync/probe.py` 钉死三仓绝对路径 + 表集合 diff。② **canonical 同名双文件**：`migrations/canonical_tables.txt`（3 表，con-005 局部）vs `testdata/canonical_tables.txt`（499 全量）——第一版集合 diff 全部 477 表显示「被删」假象；「名字包含名字」家族第三案（词边界→目录前缀→同名文件异目录）。③ ADR-004 挂账复查首跑查了 BCM 的 ADR-004（无 langchat 引用），挂账实际在 langchat/docs/adr——同名编号跨体系，检索必须带体系限定（今日终实锤：L70-73 仍 langchat.*，全目录残留 16 处，挂账第 4 周）。

### 今天最大的决策
① **五议题全落定**：G-01 并轨 W17（第 3 周未受理：docs 增量 24 commits 零 ontology 主题，但受理机器活着——同窗 accept 了 E1/F1/DV-LC-004，是队列优先级不是拒绝）；G-07 首位动作修正为「基线升级裁决 + 五族 22 表 citing」而非转正（转正 D6 已完成，今晨在执勤）；备份线（15/24=62.5%）W39 digest 定性立案；LnkReport 第三消费方另立清单不并入 chatbi 白名单（一主体一清单）；孤儿表归属裁决——主仓的债不算语义层 Code Health 扣分，语义层的债=登记滞后+基线升级欠裁决，计入 TD 论证。② **五维终值双轨**：均值 6.9（持平 W15）/ 木桶 6.0（回摆 0.5，DX 下调实锤：探针坑 + 消费面零新动作）；预填 7.0 vs 复算 6.9 命中（|Δ|=0.1，校准履历样本 3：命中上沿 / MISS 偏高 / 命中——「先跑证据再对分」程序化的兑现）。③ **W17 定轨六序**：D1 = W39 digest（pull + 基线升级 477→499 + 备份线定性 + 三门周验）+ G-01×G-07 并轨提案升格提交；五族 citing；S2 探针脚本化；G-07 v0.2 定界签名；MCP 工具描述 change 后置于基线稳定之后。

### 数字速览
四验收线：①部分（对账 C1-C5 全 PASS 五度指纹一致 / 受理第 3 周 0%）②超额（三门今晨实跑：G-05 15/15 GREEN @0392e107、Identity 26/26 GREEN + selftest、canonical selftest 6/6）③达成（pack 磁盘指纹=回执 8137b094/0af3cb1f 零漂移）④达成（digest W38 + 五件裁决）｜canonical 477→484→499（+22 五族 3+10+2+4+3；0 死登记）｜canonical 门 RED 44 BROKEN 执勤（cited 0）｜S2 lnkcre 29→47（0f66f152 +18）/ docs 23→24（备份第 15）/ chatbi 0｜SoT 五度一致 bf550bc24de66813｜ADR-004 挂账第 4 周（16 处 langchat.*）｜docs 增量主题 备份 15/mi-cre 4/lnkchat 4/lnkreport 1｜错仓假值 87 vs 真值 24｜五维 7.5/7.0/6.5/7.5/6.0 → 均值 6.9 / 木桶 6.0｜ipynb verify OK（5 code cells 一次全绿）

### 遗留 / 下一步
- W17-D1（周一）：W39 digest（三仓 pull + canonical 基线升级裁决 477→499 + 备份线定性 + 三门周验）+ G-01×G-07 并轨提案从 _drafts 升格提交 + `sync/probe.py` 探针脚本化（今日坑①直接修复）
- 五族 22 表逐族 citing change（W17 主菜）：indicator-target / leasing-progress / unit_leasing / leasing-policy / unit-pricing
- w14-plus 仍无 W17 逐日条目：第 2 次建议 Jason 补一行指向（W17 计划来源=本周 Review §7 + brief 展望锚点，md 头部已留计划来源说明）
- G-01 受理第 3 周未开窗（我方对账侧自足，裁决权主仓）；微信通道仍中断（NOTICE-2026-09-09 在案），落盘链路不受影响

## 2026-09-21（W17-D1 周一 · W39 Digest × Canonical 基线升级裁决 477→499 × G-01×G-07 并轨提案正式立案）

### 今天最大的认知
**基线不是墙，是账本**——今天第一次走完「取证 RED → 归因 → 裁决 → 重冻结记债 → 复验 GREEN」的完整基线升级程序。把 477 改成 499 只要一行 sed，那是扫进地毯下；合法性来自程序：先让门把 22 表全部判 BROKEN 留档（RED 是裁决的入场券，把「世界漂移」翻译成「语义层欠债」），再重冻结并在头部写下 carrying-debt: 22（cited 0/22）——升级之后债不但没消失，反而从「宇宙漂移」（无主）变成「cited 0/22」（有主、有期限、有验收线）。同步的真谛不是 diff=0，是**每一条 diff 都有判决**（G-07 与「同步一下表清单」的本质区别）。

### 今天最大的坑
无新坑——上周三坑中的两个今天修复闭环：①坑1（错仓假值 87）→ `sync/probe.py` 落地（三仓绝对路径钉死 + behind + 集合 diff + --json，实跑 OK：0/0/0、499=499），修复方式不是「下次小心」是把路径变成代码；②坑2（同名双文件）→ 脚本只认绝对路径与固定 baseline 文件，结构性免疫。唯一小摩擦：ipynb 实验3 首版模拟里事件3 的 citing 预期写错（new_99 未裁决仍在宇宙，单给 new_100 citing 判不全绿）——修正叙事后反而多出一个教学点：**citing 补齐只能治 leak，治不了死登记，两个方向各管各的**。

### 今天最大的决策
① **基线升级裁决执行**：477→499，对齐源=主仓 testdata 清单；w39 留档不动，冻结 w40（source_rev 470ba300，指纹 7995cb4839ddc5b1，头部完整裁决链 + carrying_debt: 22）；新基线复跑门 GREEN。五族归因闭环：000227×5（leasing-policy 3+unit-pricing 2）/ 000229×2（unit-pricing）/ 000233×3（indicator-target）/ 000234×12（leasing-progress 9+unit_leasing 3）——22 表全部有出生证明。② **G-01×G-07 并轨提案正式立案**（W16-D7 议题①执行）：changes/g0x-semantic-boundary-governance/proposal.md——原 G-01 案 Why 1-3/What 1-4 全量继承（原案标 SUPERSEDED 留档），第 4 证据链更新至 22 表（含今日 RED 实跑），五族裁决表嵌入第 5 条款作 citing 首批对象；验收线 5 条中 4 条今日达标。③ **docs 备份线定性**（议题③）：15/24=62.5% 增量是日频工作态快照（checksums 15/15 + pending-items 14/15，agent 共著，零语义零 SoT 触碰）→ 裁决「无害噪声」，digest 过滤规则固化（`备份` 主题归 P3 桶不逐条评级），不干预主仓习惯——定性本身比整改重要，未定性的线才污染判读。④ 三门周验全绿：G-05 15/15（首跑 2 DRIFTED=conditionapproval 纯行号位移 102→108/307→338，重锚后全绿——首个「上游业务演进触发锚点维护」真实样本）/ Identity 26/26 / canonical RED→裁决→GREEN。

### 数字速览
三仓对齐：lnkcre 55→0（HEAD 470ba300，09-16~20 波次：leasing-progress 全链+indicator-target 值层+unit-pricing rev3+R6 激活）/ docs 24→0（3738e98：备份 15+受理 9）/ chatbi 0｜spec 311→325｜canonical 477→499（+22 五族 3/9/3/3/4；cited 0/22=carrying_debt）｜门判决：升级前 RED（added 22/leaked 22/broken 44）→ w40 复验 GREEN（±0）｜SoT 指纹 bf550bc24de66813 六度一致（拉取前 origin 预验+拉取后本地复验）｜G-05 15/15（重锚 2）/ Identity 26/26｜probe.py 实跑 OK（behind 0/0/0，499=499，exit 0）｜g0x 验收线 4/5 达标（差第 5 条：五族 citing 0→22）｜ipynb verify OK（12 code cells，5 组断言，4 图）

### 遗留 / 下一步
- W17-D2+：五族 citing change 逐族立案（顺序：leasing-progress 12 表域预判最强 → indicator-target → unit_leasing → leasing-policy → unit-pricing），cited 0→22
- G-07 v0.2：expect 升级定界签名（治扩名盲区，W16-D2 遗留，定轨第 5 项）
- MCP 工具描述 change（定轨第 6 项）：后置条件「基线稳定」今日已满足，W17 内可排
- g0x 提案受理观察窗开启（下周一首查：docs 受理队列是否出现 ontology/governance 主题）
- w14-plus 仍无 W17 逐日条目：第 3 次建议补一行指向（计划来源链=W16-D7 §7 定轨，md 头部已留说明）

## 2026-09-22（W17-D2 周二 · 五族 Citing 逐族立案 × 22 表债清算 × G-05 v0.2 expect 定界签名）

### 今天最大的认知
**裁决的牙齿不在结果分布，在依据链里被显式排除的替代项**——五族 22 表全部「入域登记」，看起来像橡皮图章，但每个入域都踩死了一个反面：unit-pricing 归 01 不是 03（族内一致>语义直觉，跟随存量锚 unit_pricing_versions）、indicator-target 归 17 不是 06（analytics_metrics 同码对齐证据>D5 启发式噪声）、leasing-progress 不碰 V1/V2（三代并列不是改造）。全入域的真实原因是上游纪律好（22 表全带 spec/验收链/零数据纪律），门的 RED 判决本身就是筛子。另一个认知：**门的裁决只认文本不认意图**——实验①复算发现 g0x 族表括注「（含 price_authority_constraints）」已构成词边界 citing，昨日收盘真实口径是 cited 1/21 而非 0/22（digest 的 0 是取证时刻值）；碰巧被括注≠被裁决，这正是显式五案登记的必要性证明。

### 今天最大的坑
**G-05 v0.2 首版翻车**：照搬 Identity 门两侧全边界（`(?<!\w)pat(?!\w)`），15 锚复跑 7 个假 BROKEN——全是 expect 以 `(` 结尾的函数签名（`func ValidateTransition(` 等），右缘边界把后随实参（from/ctx）误判成扩名。逐锚取证（7/7 在登记行号原样存在）后修正为**边缘条件定界**：只在 pattern 边缘本身是词字符的一侧加界。教训固化：**验证器升级的顺序律——先证明零误伤（存量全绿），再证明新增检出**；词边界防的是标识符扩名，不是任意文本边缘。

### 今天最大的决策
① **五族全部裁决入域登记**（定轨第 3 项完成）：citing-leasing-progress 9 表→03 / citing-unit-leasing 3 表→03 / citing-indicator-target 3 表→17 / citing-leasing-policy 3 表→03 / citing-unit-pricing 4 表→01；每案五路证据（迁移 DDL 直读+spec+包+ontology 挂点+Context 先例），模型 yaml 一行未动（snapshot 是结果，change 是过程，v0.2 组装合并）。② **canonical 门双基线复验 GREEN**：w39 透镜 cited 22/22 leaked 0（昨日取证 cited 0/broken 44）；w40 执勤 ±0；w40 基线头部账本式追加清算记录（carrying-debt 22→0，不重写历史行）；**g0x 验收线 5/5 全达标**，What-5 裁决表转终态，OQ-2 关闭（W18 Rule 显式化输入范围锁定：leasing-policy 版本不可变链+unit-pricing 授权约束链）。③ **G-05 v0.2 定界签名落地**（定轨第 5 项完成）：边缘条件词界+首版翻车修正，15/15 GREEN，tamper 矩阵扩名检出 0%→100%（前/后缀双盲区闭合）+零误伤断言（含 `(` 右缘防回归）；Identity 门 26/26 复跑绿（纯标识符锚点两种边界等价）。

### 数字速览
五族 22 表：03 Leasing +15（40→55）/ 17 BI +3（70→73）/ 01 Asset +4（36→40）｜门判决：w39 透镜 cited 1→22/leaked 21→0 GREEN（digest 取证时刻 0/22/44）+ w40 ±0 GREEN｜G-05 v0.2：首版 7 假 BROKEN→修正后 15/15 GREEN｜扩名检出 0%→100%（旧子串对照 4 场景）｜changes/ 在册 7 个 open change（g01/g0x+citing×5）｜迁移归因 000227×5/000229×2/000233×3/000234×12 与五族 9/3/3/3/4 全对账｜ipynb verify OK（7 code cells，4 组断言，3 图）

### 遗留 / 下一步
- W17-D3：MCP 工具描述 change 提案 draft 启动（定轨第 6 项，后置条件全满足：基线稳定+cited 22/22）
- g0x 提案受理观察窗持续（下周一首查）；w14-plus 仍无 W17 逐日条目（第 4 次建议补一行指向）
- W18 预研输入已锁定：Rule/Policy 显式化前两批语料=leasing-policy 版本链+unit-pricing 授权链；LnkChatBI 术语库增量候选（五案术语条目）W18 评估
