# 🧱 LangChat 心智模型｜第8周-Day7：Virtual CTO 周度架构评审

> **🔄 Virtual CTO Review：这条链上哪里最薄弱？五维评分 + ADR Health Check + 下周建议**
>
> **日期**：2026-07-26（周日）
>
> **本周主题**：End-to-End Journey — 一条链走通（从用户意图到执行结果）
>
> **评审范围**：W8 D1-D6 全部学习产出 + ADR-001~008 + v2-strategy 文集 + 当前代码事实

---

## 目录

1. [本周理解进度](#1-本周理解进度)
2. [本周新增认知清单](#2-本周新增认知清单)
3. [是否符合 v2 Charter](#3-是否符合-v2-charter)
4. [ADR Health Check](#4-adr-health-check)
5. [五维评分](#5-五维评分)
6. [本周最大发现：链路断裂点](#6-本周最大发现链路断裂点)
7. [Gap Analysis 汇总](#7-gap-analysis-汇总)
8. [今天多理解了什么](#8-今天多理解了什么)
9. [重新设计时是否仍这样做](#9-重新设计时是否仍这样做)
10. [Daily Engineering Log](#10-daily-engineering-log)
11. [下周建议](#11-下周建议week-9-预告)
12. [术语表](#12-术语表)
13. [课堂练习与课后测试](#13-课堂练习与课后测试)
14. [真实参考](#14-真实参考)

---

## 1. 本周理解进度

### 1.1 评分：7.5 / 10

**不是 8 分的原因**：核心执行链路（站点 ①-⑧）已理解透彻，但 v2 目标态制品链（BlueprintVersion → ExecutionPlanIR → SkillRelease v2 → DeploymentRevision）只停留在"读过 ADR"层面，尚未在代码中验证目标态与当前态的差距。Connector 治理的 Gap 虽然识别了，但还没有深入到 MCP Connector 的具体实现细节。

**不是 6 分的原因**：六维身份、SkillRelease canonical invoke 链路、Read-Only 守卫递归扫描、七字段结构化输出、HITL 六态状态机——这些核心机制已经在代码层面验证，不是纸上谈兵。链路图已经画出，10 个站点、7 个治理检查点、覆盖 6 个治理维度的完整画面在脑子里是通的。

### 1.2 每日完成度

| Day | 主题 | 完成度 | 关键产出 |
|-----|------|--------|---------|
| D1 周一 | 用户意图：Agent Host → LangChat | ✅ 100% | LangChat 不是 Agent Host，是被动受治理的企业能力平台 |
| D2 周二 | ApplicationContract：传输无关的业务契约 | ✅ 95% | Contract 是业务治理一等对象，不是 API 文档 |
| D3 周三 | Blueprint → Compiler → ExecutionPlan | ✅ 90% | 10 阶段确定性 Compiler，当前大多为 pass-through stub |
| D4 周四 | Runtime 无状态执行 | ✅ 95% | 无状态手术室模型 + FrozenExecutionContext + 七字段 fallback |
| D5 周五 | Capability + Connector → Enterprise System | ✅ 85% | Capability 是治理描述符不执行，Connector 独立治理是最大 Gap |
| D6 周六 | 走完整条链（完整链路图） | ✅ 100% | 10 站点 7 检查点完整链路图 + 治理热力图 |
| D7 周日 | Virtual CTO Review | ⏳ 进行中 | 本文 |

### 1.3 时间投入

本周预计总投入约 8-10 小时（每天 60-90 分钟），符合学习计划设定的 60-90 分钟/天。

---

## 2. 本周新增认知清单

### 2.1 七大核心认知升级

以下是本周从"以前以为"到"现在知道"的认知转变清单：

| # | 以前以为 | 现在知道 | 来源 |
|---|---------|---------|------|
| 1 | LangChat 是 AI 运行时平台，负责编排所有系统 | LangChat 是**被动受治理的企业能力平台**，被 Agent Host 直接调用，不做编排 | D1 + ADR-001 |
| 2 | ApplicationContract 就是接口定义——输入输出写清楚就行 | Contract 是**业务治理一等对象**：传输无关、版本不可变、携带 effect_policy / required_scopes / human_review_gate | D2 + ADR-005 |
| 3 | Blueprint 是配置文件，Runtime 直接读取执行 | Blueprint 是**制品（artifact）**，隔着 10 阶段确定性 Compiler，ExecutionPlanIR 不可编辑 | D3 + ADR-005 HC-5/HC-6 |
| 4 | Runtime 就是"跑代码的引擎"，维护一些会话状态 | Runtime 是**无状态手术室**：FrozenExecutionContext 带入一切，execute() 永不抛异常，零 workflow import | D4 + Charter §6.1 |
| 5 | Capability 就是 Plugin 的换名——即插即用的执行模块 | Capability 是**治理描述符**，不含执行逻辑。E6 migration 后 `runtime_binding={}` 是铁证 | D5 + ADR-003 正交 facet |
| 6 | 各模块是并列的组件图 | 它们是一条**不可缩短的串行链路**：10 站点、7 检查点、6 维度覆盖 | D6 链路图 |
| 7 | WorkflowSpec 就是最终执行格式 | WorkflowSpec 是**当前态**实现，v2 目标态制品链要把它退役替换为 ExecutionPlanIR | Charter §3 第 5 项 + ADR-005 D-5 |

### 2.2 三个关键代码事实

| # | 代码事实 | 文件路径 | 意义 |
|---|---------|---------|------|
| 1 | `SixDimExecutionContext` 是 `frozen dataclass` | `server/auth/six_dim_context.py` | 六维身份不可变是租户隔离与审计的基础 |
| 2 | `enforce_read_only()` 递归 8 层深度扫描 `_WRITE_INDICATORS` | `skill_release/canonical/read_only_guard.py` | P0 阶段最后安全防线，枚举式检测是已知局限 |
| 3 | 七字段结构化输出 `_SEVEN_FIELD_OUTPUT_SCHEMA` | `skill_release/descriptor.py` | 所有 SkillRelease 执行结果的统一契约，不可降级 |

### 2.3 三个关键架构决策

| # | 决策 | 出处 | 为什么重要 |
|---|------|------|-----------|
| 1 | WorkflowSpec 不在 v2 目标态制品链中保留 | Charter §3 第 5 项 + HC-1 | 当前唯一执行格式将在未来被 ExecutionPlanIR 替代 |
| 2 | Capability 与 Industry 正交（不嵌套） | ADR-003 | 能力跨行业复用，行业是应用层标签 |
| 3 | 三段式架构链是唯一对外口径 | ADR-007 | 所有销售物料统一引用，段 1-段 3 不可合并 |

---

## 3. 是否符合 v2 Charter

### 3.1 Charter 八项 AI Native Principles 合规检查

| 原则 | 本周验证状态 | 证据 |
|------|------------|------|
| §6.1 FrozenExecutionContext | ✅ 已验证 | D4 代码验证：`FrozenExecutionContext` 是 frozen dataclass，所有状态通过它带入 |
| §6.2 Single Canonical Execution Path | ✅ 已验证 | D5/D6 链路验证：canonical invoke 是唯一执行入口，E6 migration 移除了旁路 |
| §6.3 ApplicationContract vs RuntimeABI 分离 | ⚠️ 目标态理解 | D2 理解了 Contract 是业务 API，但 RuntimeABI 的字段级 schema 只在 ADR-007 中读到，未在代码验证 |
| §6.4 Single Artifact Chain | 🔴 未验证 | 目标态制品链（BlueprintVersion → ExecutionPlanIR → SkillRelease v2）在代码中不存在，当前是 WorkflowSpec |
| §6.5 ReleaseChannel is Promotion-Only | ⚠️ ADR 阅读 | ADR-008 读了 scope 维度决策，但 ReleaseChannel 在代码中不存在 |
| §6.6 DeploymentRevision is Complete Runtime Closure | ⚠️ ADR 阅读 | DeploymentRevision 16 字段闭包 digest 在 ADR-008 中定稿，但代码中不存在 |
| §6.7 Catalog Never Source of Truth | ✅ 已验证 | D5 验证：`catalog.py` 只做投影查询，不执行、不是事实源 |
| §6.8 Deterministic Build | 🔴 未验证 | 10 阶段 Compiler 在代码中大多是 pass-through stub（D3 发现） |

### 3.2 Charter 合规总结

```
✅ 已验证：4/8（50%）
⚠️ ADR 阅读：3/8（37.5%）
🔴 未验证：2/8（12.5%）
```

**结论**：Week 8 聚焦"当前态执行链路"（符合计划），目标态制品链的理解停留在 ADR 层面。Week 9-11 需要逐步深入目标态对象在代码中的 Gap。

---

## 4. ADR Health Check

### 4.1 品牌层 ADR（ADR-001 ~ ADR-007 对外口径）

> 注：仓库内有两组 ADR 编号系统。`/root/langchat/docs/adr/` 下的 ADR-001~007 是品牌/产品定位层；`/root/langchat-docs/.../review/` 下的 ADR-001~008 是架构层。两者不冲突，覆盖范围不同。

#### 品牌层 ADR（`docs/adr/`）

| ADR | 标题 | 状态 | 是否过时 | 是否需拆分 | 是否需冻结 | 备注 |
|-----|------|------|---------|-----------|-----------|------|
| ADR-001 | LangChat 定位为「企业 AI 应用平台」 | accepted | ❌ 否 | ❌ 否 | ✅ 建议冻结 | 定位锚点，后续所有决策的根 |
| ADR-002 | 品牌层级 Lanlnk → LangChat → Capability → Application | accepted | ❌ 否 | ❌ 否 | ✅ 建议冻结 | 四级层级稳定，无变更需求 |
| ADR-003 | Capability × Industry 正交 facet 模型 | accepted | ❌ 否 | ❌ 否 | ✅ 建议冻结 | 7 个行业初始清单，可按需增补 |
| ADR-004 | MallSenseAI → LangChat AI Vision 重命名 | accepted | ❌ 否 | ❌ 否 | ✅ 已冻结 | 首个 L4 Application 命名模板 |
| ADR-005 | LangChat AI *X* 命名前缀规则 | accepted | ❌ 否 | ❌ 否 | ✅ 建议冻结 | 7 个形态词，可按 ADR 流程增补 |
| ADR-006 | 首页客户分层（决策者优先） | accepted | ❌ 否 | ❌ 否 | ✅ 建议冻结 | 信息架构约束，实施时需验收 |
| ADR-007 | 三段式架构链 | accepted | ❌ 否 | ❌ 否 | ✅ 建议冻结 | 对外口径锚点，非常稳定 |

**品牌层 ADR 总结**：7 个 ADR 全部状态为 accepted，无一过时。这些 ADR 解决的是"对外怎么说"的问题，与代码实现无关，稳定性极高。建议全部走冻结流程（如果尚未正式冻结）。

#### 架构层 ADR（`review/` 目录）

| ADR | 标题 | 状态 | 当前态验证 | 目标态理解 | Health |
|-----|------|------|----------|-----------|--------|
| ADR-001 | LangChat 直连 Agent Host 的企业能力平台定位 | 评审中（已确认方向） | ✅ G1-G18 通过 | ✅ | 🟢 健康 |
| ADR-002 | D1 统一委托 wire 级 profile | **文档事实**（G1-G7 全通过） | ✅ 代码已验证 | ✅ | 🟢 健康 |
| ADR-003 | SkillRelease API wire 级 profile | **文档事实**（G8-G10 全通过） | ✅ 代码已验证 | ✅ | 🟢 健康 |
| ADR-004 | Interaction Platform 架构 | **文档事实**（G11-G18 全通过） | ✅ 代码已验证 | ✅ | 🟢 健康 |
| ADR-005 | Blueprint / 制品链 / ApplicationContract | 评审中 | ⚠️ WorkflowSpec 当前态 | ✅ 目标态清晰 | 🟡 需关注：D-5 WorkflowSpec 退役路径 |
| ADR-006 | DigitalEmployeeDefinition / Deployment 聚合 | 评审中 | 🔴 目标态对象代码不存在 | ✅ | 🟡 需关注：P-06/P-07/P-14/P-15 闭合 |
| ADR-007 | RuntimeABI / CompatMatrix / FrozenExecutionContext wire | 评审中 | ⚠️ FrozenExecutionContext 已验证 | ✅ | 🟡 需关注：Q-01~Q-08 待落地验证 |
| ADR-008 | ReleaseChannel / DeploymentRevision / TrafficPolicy | 评审中 | 🔴 目标态对象代码不存在 | ✅ | 🟡 需关注：P-09~P-17 待落地验证 |

### 4.2 ADR Health Check 矩阵

```
                        当前态验证    目标态理解    落地风险
ADR-001 (定位)          ████████████  ████████████  ████░░░░░░░░  低风险
ADR-002 (D1 委托)       ████████████  ████████████  ████░░░░░░░░  低风险
ADR-003 (SR Wire)       ████████████  ████████████  ████░░░░░░░░  低风险
ADR-004 (交互架构)      ████████████  ████████████  ████░░░░░░░░  低风险
ADR-005 (制品链)        ████░░░░░░░░  ████████████  ████████░░░░  中风险 ← WorkflowSpec 退役
ADR-006 (DED/Deploy)    ░░░░░░░░░░░░  ████████████  ████████░░░░  中风险 ← 目标态对象未实现
ADR-007 (RuntimeABI)    ████████░░░░  ████████████  ██████░░░░░░  中风险 ← wire 字段待落地
ADR-008 (Release/Deploy) ░░░░░░░░░░░░ ████████████  ████████░░░░  中风险 ← 目标态对象未实现
```

### 4.3 关键发现

1. **ADR-001~004（当前态）健康度极高**：G1-G18 全部通过，代码与文档事实高度一致。这说明 LangChat 在 P0 阶段的工程执行质量很高。

2. **ADR-005~008（目标态）存在系统性落地风险**：四个 ADR 全部处于"评审中"状态，目标态对象（BlueprintVersion、ExecutionPlanIR、SkillRelease v2、DeploymentRevision、ReleaseChannel、TrafficPolicy）在代码中均不存在。这不是文档质量问题，而是工程节奏问题——目标态定义领先于实现。

3. **ADR-005 的 WorkflowSpec 退役路径是最大风险点**：当前唯一受治理的执行格式（WorkflowSpec v1/v2）在目标态被淘汰，但替代品（ExecutionPlanIR）尚未实现。过渡期的"两条路并行"如果管理不当，会导致治理断裂。

4. **ADR-005 HC-1（WorkflowSpec 不在 v2 制品链中保留）与代码事实存在表面冲突**：这不是 Bug，而是 Charter 明确的"目标态 vs 当前态"张力。ADR-005 §3.3 已显式桥接。但所有在 WorkflowSpec 上做新增功能的 PR 都应该标注"过渡期技术债"。

---

## 5. 五维评分

### 5.1 Architecture Quality（架构质量）：7.5 / 10

**评分理由**：

✅ **优势（+）**：
- 四层架构（Business Domain / Supply Chain / Runtime / Operations）职责边界清晰
- canonical 执行路径设计优雅：从 invoke 到七字段输出，链路不可缩短
- 六维身份 + FrozenExecutionContext 的安全模型在企业级 AI 平台中属于高水平设计
- Capability × Industry 正交模型避免了能力耦合行业
- 三段式架构链（ADR-007）对外口径锁定，避免信息架构混乱

⚠️ **不足（-）**：
- 目标态制品链（Blueprint → IR → SkillRelease v2 → DeploymentRevision）只有 ADR 定义，无代码实现
- Connector 治理是链路上最大的架构断裂点：MCP 嵌在 Workflow 内部，没有独立 effect_policy / scope / 版本管理
- `enforce_read_only()` 的枚举式 `_WRITE_INDICATORS` 检测无法覆盖所有写操作形式，是安全盲区
- WorkflowSpec 作为"当前唯一执行格式但目标态要退役"的过渡期状态，增加架构理解成本

### 5.2 Code Health（代码健康度）：7.0 / 10

✅ **优势（+）**：
- canonical 链路代码结构清晰：`router.py` → `execution_preparation.py` → `execution_service.py` → `execution_dispatch.py`
- frozen dataclass 广泛使用（SixDimExecutionContext、SkillReleaseDescriptor），不可变性好
- 回归测试覆盖核心路径：`test_canonical_*.py` 系列
- AGENTS.md 25KB+ 的架构指南极其详尽，新人 onboarding 有据可循

⚠️ **不足（-）**：
- 10 阶段 Compiler 大多为 pass-through stub，"看起来在做事实际上没做"
- RuntimeLoader 是 WP-05 stub，接受已实例化对象直接返回，无真实 OCI pull / 验签
- `add_message_to_db.__wrapped__()` 绕过 audit wrapper 是技术债（虽然 AGENTS.md 标注 intentional）
- Channel dispatch 的 DLQ + idempotency + config_cache 三套缓存机制增加理解成本

### 5.3 ADR Consistency（ADR 一致性）：8.0 / 10

✅ **优势（+）**：
- ADR-001~004 的 G1-G18 全部通过验证，文档事实与代码高度一致
- v2-strategy 文集（Charter + Domain Model + Artifact Spec）已于 2026-07-19 同批冻结
- ADR 之间引用关系清晰：每个 ADR 显式标注关联和取代关系
- 四态模型（文档事实 / 已确认方向 / 待决策 / 待验证）防止状态混乱

⚠️ **不足（-）**：
- 两组 ADR 编号系统（品牌层 `docs/adr/` 1~7 vs 架构层 `review/` 1~8）容易混淆
- ADR-005~008 全部"评审中"，长时间不正式通过会降低决策权威性
- Capability Execution Boundary ADR（`docs/architecture/`）状态为 proposed，与 ADR-003 正交模型有交叉但未显式关联

### 5.4 Technical Debt（技术债质量，分越高越好）：6.5 / 10

✅ **优势（+）**：
- 技术债大多被显式标注（AGENTS.md 中多处"legacy"、"intentional"、"compat path"）
- E6 migration 清理了 Capability 的执行能力，证明团队有主动还债的意识
- WorkflowSpec 退役路径在 ADR-005 中有显式规划，不是"假装看不见"

⚠️ **不足（-）**：
- WorkflowSpec → ExecutionPlanIR 的迁移是**系统性技术债**：当前所有 SkillRelease 的 workflow_binding 依赖 WorkflowSpec，迁移影响面巨大
- Connector 独立治理未启动：MCP 嵌在 Workflow 内是架构债，越晚拆成本越高
- 10 阶段 Compiler 的 stub 状态意味着"框架先行、逻辑后补"，但如果 stub 期间有人误以为 Compiler 在工作，可能导致错误的依赖假设
- `__wrapped__()` 绕过审计 wrapper 的 pattern 如果扩散，会削弱审计体系

### 5.5 Developer Experience（开发者体验）：7.0 / 10

✅ **优势（+）**：
- AGENTS.md 是见过的最详尽的架构指南之一，覆盖模块映射、数据流、注意事项
- `make lint` / `make test` 本地全链路验证，无 CI 依赖
- SkillRelease 注册机制清晰：定义 Descriptor → 注册 Executor → 自动接入 canonical 链路
- 七字段结构化输出让上游消费者有统一的解析契约

⚠️ **不足（-）**：
- 两组 ADR 编号系统增加新人认知负担
- 目标态对象在代码中不存在，开发者读 ADR 后容易产生"这个已经实现了"的错觉
- Channel dispatch 的调试需要理解 5 个模块的协作（dispatch / rag / context / dead_letter / idempotency）
- WorkflowSpec v1/v2 两个版本共存增加理解成本

### 5.6 五维评分雷达图汇总

| 维度 | 评分 | 趋势 | 说明 |
|------|------|------|------|
| Architecture Quality | 7.5/10 | — | 首次评分，作为基线 |
| Code Health | 7.0/10 | — | 首次评分，作为基线 |
| ADR Consistency | 8.0/10 | — | 首次评分，作为基线 |
| Technical Debt | 6.5/10 | — | 首次评分，作为基线（分越高质量越好） |
| Developer Experience | 7.0/10 | — | 首次评分，作为基线 |
| **综合** | **7.2/10** | — | Week 8 基线 |

---

## 6. 本周最大发现：链路断裂点

### 6.1 链路健康度全景

```
站点 ① Agent Host → LangChat     🟢 健康（代码实现完整）
站点 ② 六维身份解析              🟢 健康（frozen dataclass + 测试覆盖）
站点 ③ SkillRelease 资格检查     🟢 健康（eligibility + lifecycle 检查）
站点 ④ 幂等 + 限流               🟢 健康（双重保护机制完整）
站点 ⑤ HITL 审批门控             🟢 健康（六态状态机 + review_token）
站点 ⑥ 创建执行记录              🟢 健康（完整审计追踪）
站点 ⑦ Read-Only 守卫            🟡 关注（枚举式检测有盲区）
站点 ⑧ 分发执行                  🟢 健康（executor 注册 + dispatch）
站点 ⑨ SkillRelease Executor     🟢 健康（W09 实现完整）
站点 ⑩ Connector → 外部系统      🔴 断裂（MCP 嵌在 Workflow 内，无独立治理）
站点 ⑪ v2 制品链                 🔴 断裂（目标态对象代码不存在）
站点 ⑫ 七字段响应               🟢 健康（统一输出契约）
```

### 6.2 三个关键断裂点详解

#### 断裂点 1：Connector 治理缺失（🔴 高风险）

**现状**：MCP Connector 作为 Workflow 的工具节点存在，没有独立的 effect_policy、scope 管理和版本控制。

**风险**：
- Connector 调用不经独立 Capability Resolution
- `enforce_read_only()` 只检查 Workflow 级别的 `effect_policy`，不检查 Connector 级别
- `_WRITE_INDICATORS` 是枚举式检测（`http_request`/`db_write`/`tool_call`/`provider_conditional_write`），无法覆盖新的写操作形式

**影响**：如果 P0 阶段需要接入写操作 Connector（如 ERP 写入），当前架构无法安全支持。

**建议**：Week 10（Governance 周）深入分析 Connector 治理 Gap，提出 Connector 独立治理层设计建议。

#### 断裂点 2：v2 制品链完全未实现（🔴 高风险）

**现状**：BlueprintVersion、ExecutionPlanIR、SkillRelease v2（OCI manifest）、DeploymentRevision、ReleaseChannel、TrafficPolicy 这些目标态对象在代码中完全不存在。

**风险**：
- 当前 WorkflowSpec 是唯一执行格式，但它被标记为"v2 目标态中退役"
- 10 阶段 Compiler 大多为 stub，确定性构建链条未打通
- 制品链断裂意味着 deployment digest pinning、compatibility matrix check、OCI artifact 分发都无法实现

**影响**：LangChat v2 的核心价值（可审计的制品供应链）依赖这条链。如果延迟过久，当前态的 WorkflowSpec 会积累越来越多无法迁移的业务逻辑。

**建议**：Week 9（Domain Deep Dive）深入分析 WorkflowSpec → ExecutionPlanIR 迁移路径，评估首批迁移的 SkillRelease 候选。

#### 断裂点 3：Compiler stub 化（🟡 中风险）

**现状**：10 阶段 Compiler 流水线（WP-03）大多是 pass-through stub，只标记 "done" 并记录 Provenance entry，没有真实编译逻辑。

**风险**：
- 看起来结构完整的 10 阶段函数，实际不做编译工作
- 如果有人在 stub 期间基于"Compiler 已完成"假设做下游开发，会产生错误依赖
- 确定性构建的保证（"同一输入永远同一输出"）当前只停留在框架层面

**影响**：Compiler 是 BlueprintVersion → ExecutionPlanIR 的桥梁。如果 Compiler 不工作，整条 v2 制品链就无法打通。

**建议**：Week 11（Code Reality）详细扫描 10 个阶段各自的状态，列出哪些是 stub、哪些有真实逻辑。

---

## 7. Gap Analysis 汇总

### 7.1 本周 Gap 矩阵

| 对象/能力 | 目标态（ADR/v2-strategy） | 当前代码状态 | Gap 等级 | Gap 描述 |
|-----------|------------------------|------------|---------|---------|
| SixDimExecutionContext | frozen dataclass 六维 | ✅ 已实现 | 🟢 无 | 代码与 ADR 一致 |
| SkillRelease canonical invoke | 唯一执行入口 | ✅ 已实现 | 🟢 无 | E6 migration 后已清理旁路 |
| FrozenExecutionContext（运行时） | 不可变执行闭包 | ✅ 已实现 | 🟢 无 | P0 阶段已验证 |
| Read-Only Guard | 递归写操作检测 | ⚠️ 部分 | 🟡 小 | 枚举式检测有盲区 |
| HITL 六态状态机 | pending → approved/rejected | ✅ 已实现 | 🟢 无 | 含 review_token + 超时扫描 |
| 七字段结构化输出 | summary/details/refs/assumptions/review/actions/confidence | ✅ 已实现 | 🟢 无 | 统一输出契约 |
| Capability（元数据） | `/list` + `/describe` | ✅ 已实现 | 🟢 无 | E6 后 runtime_binding={} |
| Connector 独立治理 | 独立 effect_policy/scope/版本 | 🔴 未实现 | 🔴 大 | MCP 嵌在 Workflow 内 |
| BlueprintVersion | canonical 源制品 | 🔴 不存在 | 🔴 大 | 目标态对象 |
| ExecutionPlanIR | 确定性构建产物 | 🔴 不存在 | 🔴 大 | 目标态对象 |
| SkillRelease v2（OCI） | digest-pinned OCI artifact | 🔴 不存在 | 🔴 大 | 当前是 v1 canonical |
| DeploymentRevision | 16 字段闭包 digest | 🔴 不存在 | 🔴 大 | 目标态对象 |
| ReleaseChannel | scope 维度 + promotion-only | 🔴 不存在 | 🔴 大 | 目标态对象 |
| TrafficPolicy | cohort hash + 灰度路由 | 🔴 不存在 | 🔴 大 | 目标态对象 |
| Compiler 10 阶段 | 确定性编译 | ⚠️ stub | 🟡 中 | 框架存在，逻辑未填充 |
| RuntimeLoader | OCI pull + 验签 | ⚠️ stub | 🟡 中 | WP-05 pass-through |

### 7.2 Gap 分类统计

```
🟢 无 Gap（已对齐）：7 项 → 47%
🟡 小/中 Gap（部分实现/stub）：3 项 → 20%
🔴 大 Gap（完全不存在）：6 项 → 33%  ← 全部是 v2 目标态对象
```

**结论**：当前态执行链路（P0 阶段）的健康度很高（7/7 无 Gap），但 v2 目标态制品链的 Gap 是系统性的（6/6 完全未实现）。这不是"做了一半"的问题，而是"还没开始做 v2 制品链"的问题。

---

## 8. 今天多理解了什么

### 以前以为

以前以为"ADR 通过了就等于实现了"。看到 ADR-001~004 的 G1-G18 全部通过，就以为 LangChat 的架构已经完整落地了。

### 现在知道

现在知道**通过验证门（G1-G18）的只是"当前态"（ADR-001~004）**，而"目标态"（ADR-005~008）全部还在评审中。通过验证门意味着文档与代码一致——但文档描述的是 P0 阶段的当前事实，不是 v2 的目标。

v2 目标态的 6 个核心对象（BlueprintVersion、ExecutionPlanIR、SkillRelease v2、DeploymentRevision、ReleaseChannel、TrafficPolicy）在代码中完全不存在。这不是说代码写得不好，而是说 **v2 制品链的工程化还没开始**。

更深层地：ADR 的四态模型（文档事实 / 已确认方向 / 待决策 / 待验证）是一个极好的治理工具。它让"我们现在在哪"和"我们要去哪"可以同时存在于同一份文档体系中，而不互相矛盾。这个设计本身就值得学习。

### 对 ADR 价值的新认知

以前把 ADR 当成"决策记录文档"——记下来就行。

现在知道 ADR 是**治理工具**：
1. 它定义了"什么是当前事实 vs 什么是目标态"，防止混淆
2. 它通过 HC（Hard Constraint）建立不可放宽的前提
3. 它通过取代关系（supersedes / superseded-by）管理决策演进
4. 它通过验证门（G1-G18）确保文档与代码一致
5. 它通过状态模型防止"静默覆盖"——任何变更必须留下修订记录

---

## 9. 重新设计时是否仍这样做

### 如果从零设计 LangChat，本周发现的哪些设计会被保留？

| 设计决策 | 保留？ | 理由 |
|---------|--------|------|
| 六维身份作为第一步 | ✅ 绝对保留 | 没有身份就没有治理，没有治理就不是企业平台 |
| SkillRelease canonical invoke 唯一执行入口 | ✅ 绝对保留 | 单一执行路径是审计和安全的基石 |
| FrozenExecutionContext 不可变 | ✅ 绝对保留 | 审计基础，不可协商 |
| Read-Only Guard 作为最后防线 | ✅ 保留，但升级 | 保留递归扫描思路，但替换枚举式检测为更通用的策略 |
| 七字段结构化输出 | ✅ 绝对保留 | 统一输出契约，上游消费者有确定性 |
| HITL 六态状态机 | ✅ 绝对保留 | 人审是企业级 AI 的刚需 |
| Capability 不执行（只描述） | ✅ 绝对保留 | E6 migration 证明这是正确的 |
| WorkflowSpec 作为执行格式 | ❌ 不保留 | 如果从零开始，直接用 ExecutionPlanIR |
| Connector 嵌在 Workflow 内 | ❌ 不保留 | 从一开始就独立治理 |
| SkillReleaseDescriptor 承担三个角色 | ❌ 不保留 | P0 就引入 ContractVersion |

### 如果从零设计，会改变的三件事

1. **从一开始就建 v2 制品链**：Blueprint → Compiler → IR → SkillRelease v2 → DeploymentRevision。不走 WorkflowSpec 弯路。原因：后期从"没有制品链"迁移到"有制品链"的改造成本远大于一开始就建。

2. **Connector 独立治理层从 P0 开始**：每个 Connector 有自己的 effect_policy、scope、版本。不嵌在 Workflow 内。原因：Connector 是连接企业系统的核心通道，治理缺失等于安全链路有缺口。

3. **ApplicationContract 在 P0 就引入**：不让 SkillReleaseDescriptor 同时承担业务语义、设计描述、实现绑定三个角色。即使 P0 只有一个版本，也引入 ContractVersion 概念。原因：后期从"没有版本"迁移到"有版本"的改造成本远大于一开始就加一层。

---

## 10. Daily Engineering Log

### 新增
- Week 8 完整链路图（D6 产出）
- 五维评分基线（本文）
- ADR Health Check 矩阵（本文）
- Gap Analysis 汇总矩阵（本文）

### 确认
- ADR-001~004（当前态）G1-G18 验证全部通过，文档事实与代码高度一致
- 六维身份、canonical invoke、FrozenExecutionContext、七字段输出在代码层完整实现
- Capability 不执行的决策（E6 migration）是正确的
- 品牌层 ADR-001~007 全部 accepted，无一过时

### 遗留
- v2 制品链 6 个核心对象在代码中完全不存在（BlueprintVersion / ExecutionPlanIR / SkillRelease v2 / DeploymentRevision / ReleaseChannel / TrafficPolicy）
- Connector 独立治理未启动（MCP 嵌在 Workflow 内）
- Compiler 10 阶段大多为 pass-through stub
- RuntimeLoader 是 WP-05 stub（无真实 OCI pull / 验签）

### 技术债
- WorkflowSpec 作为"当前唯一执行格式但目标态要退役"的过渡期状态
- `enforce_read_only()` 枚举式检测无法覆盖所有写操作形式
- `add_message_to_db.__wrapped__()` 绕过 audit wrapper
- 两组 ADR 编号系统（品牌层 1~7 vs 架构层 1~8）增加认知负担

### 下一步
- Week 9 进入 Domain Deep Dive，逐个拆解核心对象
- 重点分析 WorkflowSpec → ExecutionPlanIR 演进路径
- 评估 Connector 独立治理层的设计方向

---

## 11. 下周建议（Week 9 预告）

### 11.1 Week 9 主题：Domain Deep Dive — 拆对象，理解为什么

Week 8 走通了整条链路。Week 9 回到每个对象，深入理解它为什么存在、边界在哪、替代方案是什么。

| Day | 对象 | Today's Question |
|-----|------|------------------|
| D1 | BlueprintVersion | 为什么 Blueprint 是制品不是配置？ |
| D2 | SkillRelease | 为什么 SkillRelease 是唯一可部署单元？ |
| D3 | Deployment / DeploymentRevision | 为什么 Deployment 独立于 Release？ |
| D4 | ReleaseChannel / TrafficPolicy | 为什么需要灰度？不能一次全量？ |
| D5 | DigitalEmployeeDefinition | 为什么数字员工不拥有 Runtime？ |
| D6 | Domain Model Diagram 实战 | 哪个对象最可能被合并？ |
| D7 | Virtual CTO: ADR Health Check | 8 个 ADR 有没有过时或需要拆分？ |

### 11.2 Week 9 重点关注

1. **WorkflowSpec → ExecutionPlanIR 演进路径**：D1 重点分析。WorkflowSpec 当前在代码中的依赖关系，迁移到 ExecutionPlanIR 的第一步应该做什么。

2. **SkillRelease v1 vs v2 的关系**：D2 重点分析。当前 canonical v1（`POST /v1/skill-releases/{skill_id}/invoke`）与目标态 v2（OCI digest-pinned artifact）的对应关系。

3. **DeploymentRevision 16 字段闭包 digest**：D3 重点分析。ADR-008 定稿的 16 字段列表，理解每个字段为什么必须进入闭包。

4. **Connector 治理方向预研**：为 Week 10（Governance）做铺垫。读取 MCP Connector 相关代码，评估独立治理的设计空间。

### 11.3 学习方法调整

- Week 8 是"跟着链路走"（线性推进），Week 9 是"拆对象"（深度挖掘）
- 每个对象做三件事：① 代码实现现状 ② 目标态定义 ③ Gap 分析
- 周六画 Domain Model Diagram（对象关系图），不只是文字描述

---

## 12. 术语表

| 英文 | 音标 | 中文 | 说明 |
------|------|------|------|
| Architecture Review | /ˈɑːrkɪtektʃər rɪˈvjuː/ | 架构评审 | 对系统架构进行系统性审查的过程 |
| ADR Health Check | /eɪ-diː-ɑːr hɛlθ tʃɛk/ | ADR 健康检查 | 检查架构决策记录是否过时、需拆分或需冻结 |
| Gap Analysis | /ɡæp əˈnæləsɪs/ | 差距分析 | 目标态与当前态之间的差异分析 |
| Technical Debt | /ˈteknɪkəl dɛt/ | 技术债 | 为短期利益做出的次优技术选择，未来需要偿还 |
| Virtual CTO | /ˈvɜːrtʃuəl siː-tiː-oʊ/ | 虚拟首席技术官 | 以 CTO 视角进行架构级别的审查和评估 |
| Pass-through Stub | /pæs-ˈθruː stʌb/ | 透传桩 | 只有接口框架没有真实逻辑的占位实现 |
| Frozen Dataclass | /ˈfroʊzən ˈdeɪtəklæs/ | 冻结数据类 | Python 中不可变的数据类（`@dataclass(frozen=True)`） |
| Compatibility Matrix | /kəmˌpætəˈbɪləti ˈmeɪtrɪks/ | 兼容性矩阵 | RuntimeABI 版本间的兼容性对照表 |
| Deterministic Build | /dɪˌtɜːrmɪˈnɪstɪk bɪld/ | 确定性构建 | 相同完整输入永远产出相同输出的构建过程 |
| OCI Artifact | /oʊ-siː-aɪ ˈɑːrtɪfækt/ | OCI 制品 | 符合 Open Container Initiative 标准的制品格式 |
| Cohort Hash | /ˈkoʊhɔːrt hæʃ/ | 分组哈希 | 用于灰度发布的确定性流量分桶算法 |
| Effect Policy | /ɪˈfɛkt ˈpɒləsi/ | 效果策略 | 声明操作是只读还是写操作的安全策略 |
| Canonical Execution Path | /kəˈnɒnɪkəl ˌeksɪˈkjuːʃən pæθ/ | 规范执行路径 | 平台唯一允许的执行路径，禁止旁路 |
| Provenance | /ˈprɒvənəns/ | 来源追溯 | 记录制品从创建到当前状态的完整链路 |

---

## 13. 课堂练习与课后测试

### 13.1 课堂练习

**练习 1：五维评分趋势预测**

基于本周的基线评分，预测 Week 9-11 的五维评分趋势。思考：
- 哪些维度会随着深入理解而上升？
- 哪些维度可能会因为发现更多 Gap 而下降？
- 到 Week 11 结束时，哪个维度的分数最重要？

**练习 2：ADR 优先级排序**

如果只能优先推进一个 ADR 的落地实现，你会选哪个？为什么？

参考答案方向：ADR-005（制品链）是所有 v2 目标态的基础，WorkflowSpec 退役路径必须最早启动。

**练习 3：技术债偿还路线图**

列出本周发现的所有技术债，按"影响面 × 紧迫度"排序，给出 3 个 Sprint 的偿还计划。

### 13.2 课后测试

**Q1**（单选）：以下哪个对象在代码中已经完整实现？
A. BlueprintVersion
B. ExecutionPlanIR
C. DeploymentRevision
D. SixDimExecutionContext

**Q2**（多选）：ADR Health Check 中，哪些 ADR 的状态是"文档事实"（已通过验证门）？
A. ADR-001
B. ADR-003
C. ADR-005
D. ADR-007

**Q3**（判断）：`enforce_read_only()` 的递归扫描可以覆盖所有可能的写操作形式。
A. 正确
B. 错误

**Q4**（简答）：为什么 Connector 嵌在 Workflow 内部是架构债？如果从零设计，Connector 的独立治理层应该包含哪些要素？

**Q5**（简答）：本周五维评分中 Technical Debt 得分最低（6.5/10），请列出影响这个分数的三个主要因素，并为每个因素给出一个改善建议。

---

## 14. 真实参考

### ADR 文档
| 文档 | 路径 |
|------|------|
| ADR-001（平台定位） | `/root/langchat/docs/adr/ADR-001-platform-positioning-enterprise-ai-application-platform.md` |
| ADR-003（正交 facet） | `/root/langchat/docs/adr/ADR-003-capability-industry-orthogonal-facet-model.md` |
| ADR-007（三段式架构链） | `/root/langchat/docs/adr/ADR-007-platform-architecture-chain-three-tiers.md` |
| 架构层 ADR INDEX | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/INDEX.md` |
| 架构层 ADR-005（制品链） | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-005-Blueprint-artifact-chain-and-ApplicationContract.md` |
| 架构层 ADR-006（DED/Deployment） | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-006-DigitalEmployeeDefinition-and-Deployment-aggregate.md` |
| 架构层 ADR-007（RuntimeABI） | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-007-RuntimeABI-CompatMatrix-FrozenExecutionContext-wire.md` |
| 架构层 ADR-008（Release/Deploy） | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-008-ReleaseChannel-DeploymentRevision-TrafficPolicy.md` |

### v2 战略文集
| 文档 | 路径 |
|------|------|
| Charter | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/v2-strategy/01-LangChat-v2-Architecture-Charter.md` |
| Domain Model | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/v2-strategy/02-LangChat-v2-Target-Domain-Model.md` |
| Artifact Spec | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/v2-strategy/03-LangChat-v2-Artifact-and-Execution-Specification.md` |

### 代码文件
| 模块 | 路径 |
|------|------|
| 六维身份 | `apps/backend/langchat/server/auth/six_dim_context.py` |
| Canonical Router | `apps/backend/langchat/skill_release/canonical/router.py` |
| 执行准备 | `apps/backend/langchat/skill_release/canonical/execution_preparation.py` |
| 执行分发 | `apps/backend/langchat/skill_release/canonical/execution_dispatch.py` |
| Read-Only 守卫 | `apps/backend/langchat/skill_release/canonical/read_only_guard.py` |
| 幂等重放 | `apps/backend/langchat/skill_release/canonical/execution_replay.py` |
| 速率限制 | `apps/backend/langchat/skill_release/canonical/canonical_rate_limit.py` |
| HITL 状态机 | `apps/backend/langchat/skill_release/canonical/state_machine.py` |

### Capability Execution Boundary ADR
| 文档 | 路径 |
|------|------|
| Capability Execution Boundary | `/root/langchat/docs/architecture/ADR-capability-execution-boundary.md` |

### 本周学习材料
| Day | 文件 |
|-----|------|
| D1-D5 | `/root/learning-notebooks/第8周/第8周-Day1~Day5*.md / .ipynb` |
| D6 链路图 | `/root/learning-notebooks/第8周/第8周-Day6-完整链路图.md` |
| Engineering Journal | `/root/learning-notebooks/engineering-journal.md` |