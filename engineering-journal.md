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
