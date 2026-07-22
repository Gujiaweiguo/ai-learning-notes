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
