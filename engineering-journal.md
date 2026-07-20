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
