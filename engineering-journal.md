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
