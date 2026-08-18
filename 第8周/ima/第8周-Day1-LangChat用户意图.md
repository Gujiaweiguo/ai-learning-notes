# 🎯 今日学习目标｜第8周-Day1：谁在调用 LangChat？

> **从 AI 基础学习 → 产品架构心智模型**
>
> 今天不学一个孤立概念，而是从一条真实请求出发：用户提出需求后，到底是谁理解需求？谁执行企业能力？为什么 LangChat 不应该又变成一个 Agent？

## 📅 学习进度

```text
W1  ████████████████████ ✅ Transformer 与大模型基础
W2  ████████████████████ ✅ Transformer 工程优化
W3  ████████████████████ ✅ 训练、SFT、RLHF、DPO
W4  ████████████████████ ✅ RAG 与知识增强
W5  ████████████████████ ✅ 推理与思维链
W6  ████████████████████ ✅ Agent 与工具使用
W7  ████████████████████ ✅ 数字员工架构深化
W8  ██░░░░░░░░░░░░░░░░░░ 🔥 LangChat 心智模型（Day1/7）
W9  ░░░░░░░░░░░░░░░░░░░░ 🧩 领域对象深挖
W10 ░░░░░░░░░░░░░░░░░░░░ 🛡 Governance 横切约束
W11 ░░░░░░░░░░░░░░░░░░░░ 💻 代码现实与实施路线图
W12 ░░░░░░░░░░░░░░░░░░░░ 👁 Vision Intelligence 全景
W13 ░░░░░░░░░░░░░░░░░░░░ 🚀 视觉智能能力蓝图
```

**进度：第8周 / 第13周｜今天开始把“学 AI”转为“理解并推进产品”。**

---

# 🔄 往期回顾：前7周为什么没有白学？

| 已学能力 | 现在在 LangChat 里的位置 |
|---|---|
| Transformer、Prompt、结构化输出 | Compiler、Contract、可控输出 |
| RAG、Embedding、知识图谱 | Knowledge 能力与企业知识治理 |
| 推理、CoT、ReAct | Agent Host 的意图理解与任务规划 |
| Function Calling、工具调用 | Capability 发现与 Connector 调用 |
| 多 Agent、任务编排 | 可替换的 Orchestrator 角色 |
| 数字员工、记忆、护栏 | Digital Employee、Governance、审批与审计 |

## 💡 今天与前面知识的关联

前面学 Agent 时，经常会把“理解用户、规划任务、调用工具、返回结果”全塞进一个 Agent 里。做 Demo 没问题；做企业产品会立刻出现责任混乱：权限谁管？版本谁管？发布谁管？审计谁管？

今天要建立的边界是：**Agent Host 负责理解和规划；LangChat 负责把企业能力变成可发现、可授权、可审计、可重复执行的产品能力。**

---

# 📚 Part 1：先走一遍真实链路

## 🎯 Today's Question

> **为什么 LangChat 不是 Agent Host？**

先看一条最小但完整的链路：

```text
用户：帮我查看本月商场运营异常，并给出处理建议
        ↓
Agent Host：理解用户意图，判断需要“运营异常检测”能力
        ↓  受控 HTTP / MCP 调用（带身份、租户、scope、委托链）
LangChat：发现并授权一个已发布的 SkillRelease
        ↓
Runtime / Workflow：执行受治理的内部工作流
        ↓
Provider：查询 MI、CRM、知识库或业务系统
        ↓
LangChat：返回带版本、Trace、结构化结果的能力输出
        ↓
Agent Host：组织给用户的最终回答或继续规划下一步
```

## 一句话分工

| 角色 | 它应该做什么 | 它不应该做什么 |
|---|---|---|
| Agent Host | 理解意图、拆解任务、跨系统规划、选择能力 | 管理企业能力发布、审批、版本与审计 |
| LangChat | 能力发现、授权、版本、人审、Trace、受治理执行 | 充当所有用户请求的第二个“大脑” |
| Provider | 执行业务系统查询，维护最终数据权限 | 替代平台层做统一能力治理 |

## 生活类比：前台、标准作业与业务部门

把企业想成一家大型医院：

- **Agent Host** 像导诊台：先听病人怎么描述问题，判断要去哪个科室、是否需要多个科室会诊。
- **LangChat** 像医院的标准作业与服务目录：规定“某项检查”是否可开、谁有权限开、版本是什么、是否需要审核、过程如何留痕。
- **Provider** 像检验科、影像科：真正掌握设备、数据和专业执行能力。

如果导诊台也去做 CT、检验和病历治理，会乱；如果服务目录又试图替病人判断所有病情，也会乱。清晰边界才能让系统扩展。

---

# 📚 Part 2：ADR-001 是怎么设计这条边界的？

ADR-001 的核心定位是：**LangChat 直连 Agent Host 的企业能力平台**。

## ADR-001 的四条关键决定

| 决定 | 含义 | 解决的问题 |
|---|---|---|
| LangChat 是 Enterprise Capability Platform | LangChat 的核心价值是受治理的企业能力 | 避免把平台做成又一个通用 Agent |
| Agent Host 直接调用 LangChat | 采用受控 HTTP/MCP，不强制经过编排层 | 减少虚构中间层和不必要跳转 |
| Orchestrator 是可替换角色 | 可以存在，但不是必经系统 | 允许不同 Agent Host 用不同规划方式 |
| 不把 Provider 权限收回 LangChat | 行/列级等业务数据权限仍归 Provider | 避免平台层越权、重复实现数据安全 |

## 为什么不保留“必经 Orchestrator”？

历史上有一个 `OrchestratorAgent` 的设想，但它没有真正投入生产。若仍把它写成所有调用的必经入口，后续 PRD、OpenSpec 和代码都会围绕一个不存在的中心展开。

这会带来三个问题：

1. **责任重复**：Agent Host 已经能理解意图和规划，Orchestrator 又做一次，谁是最终决策者？
2. **可用性风险**：每个请求多依赖一跳，中心组件故障就可能拖住全部能力。
3. **产品锁死**：不同企业已经有自己的 Agent、渠道机器人或工作流系统，不应被迫迁移到同一个编排器。

因此 ADR-001 不是说“不要编排”，而是说：**编排不应该成为 LangChat 的强制身份。**

---

# 📚 Part 3：现有代码已经做到哪里？

## 1. SkillRelease API：对外暴露的是“能力”，不是内部 Workflow

代码位置：`apps/backend/langchat/skill_release/routes.py`

这里提供了 SkillRelease 的发现、调用和审批相关入口。对 Agent Host 来说，应该看见的是一个已发布、可授权的 SkillRelease；它不需要知道内部到底绑定了哪个 Workflow、用的是哪家 Provider。

这就是产品封装：调用者面向稳定的“能力合同”，平台内部可以逐步替换实现。

## 2. 六维身份：直接调用不是裸调用

代码位置：`apps/backend/langchat/server/auth/six_dim_middleware.py`

每个请求要携带六个身份维度：

```text
client      哪个 Agent Host / 客户端在调用？
actor       谁真正发起了操作？
tenant      属于哪个租户？
workspace   落在哪个工作空间？
scope       被授权做哪些动作？
delegation  权限委托链是什么？
```

它对应的不是普通登录，而是企业场景里的“谁代表谁、在什么范围内、做什么事情”。例如同一个 Agent Host 可以代表不同用户，也可以在不同租户和工作空间工作；这些上下文不能只靠一个 user_id 粗暴解决。

## 3. SkillReleaseDescriptor：能力的可治理描述

代码位置：`apps/backend/langchat/skill_release/descriptor.py`

`SkillReleaseDescriptor` 是一个 frozen Pydantic 模型，核心字段包括：

| 字段 | 作用 |
|---|---|
| `skill_id` + `version` | 确定调用的是哪一个版本 |
| `lifecycle` | 管理草稿、发布、弃用状态 |
| `effect_policy` | 区分只读与可能产生副作用的操作 |
| `human_review_gate` | 决定是否需要人工审核 |
| `workflow_binding` | 连接当前内部实现 |
| `visibility` + `scopes` | 控制谁看得见、谁调用得了 |

这说明当前系统已经不是简单“把 Workflow API 暴露出去”，而是有了发布、权限和人审的初步治理壳。

## 4. 已有 SkillRelease 绑定

代码位置：`apps/backend/langchat/skill_release/bindings/`

目录中已有 W01-W09 的绑定文件。例如运营异常检测、内部制度问答等能力已经被包装成可调用的发布单元。它证明 LangChat 不是从零开始；当前任务是把已有的“Workflow 绑定”演进为 v2 定义的“制品执行链”。

---

# 📚 Part 4：目标态与代码现实之间的 Gap

## 已经具备的能力

```text
✅ SkillRelease 的发现与调用入口
✅ 六维身份验证
✅ 多个 Workflow-backed SkillRelease 绑定
✅ 审批相关流程
✅ Release 描述符中已有生命周期、作用策略、可见性与 scope
```

## v2 目标态仍缺失的能力

```text
❌ ApplicationContract：Agent Host 与 LangChat 的一等合同对象
❌ Blueprint → Compiler → ExecutionPlanIR：设计制品到执行制品的编译链
❌ OCI 制品、digest 与签名：可验证、可复现的发布包
❌ Deployment / DeploymentRevision：部署与部署修订管理
❌ ReleaseChannel / TrafficPolicy：灰度、金丝雀与流量控制
```

## Gap 的本质

当前的能力发布方式更接近：

```text
SkillRelease → 直接绑定 Workflow
```

v2 目标是：

```text
BlueprintVersion → Compiler → ExecutionPlanIR → 签名 SkillRelease 制品
                → DeploymentRevision → ReleaseChannel / TrafficPolicy → Runtime
```

前者能跑，但容易让调用语义和内部实现耦合；后者把设计、编译、发布、部署、流量和运行时拆开，才具备企业级可演进性。

---

# 📚 Part 5：今天的结论与架构判断

## 📘 今天多理解了什么？

**以前以为：** LangChat 是一个要编排所有 AI 系统的 Runtime。

**现在知道：** LangChat 是企业能力平台。它不抢 Agent Host 的意图理解与跨系统规划职责，而是把企业能力做成可发现、可授权、可审核、可追踪、可重复执行的 SkillRelease。

## ❓ Today's Question 的答案方向

LangChat 不能是 Agent Host，至少有三个原因：

1. **职责不同**：Agent Host 处理“用户想做什么”；LangChat 处理“企业允许、定义并治理哪些能力”。
2. **避免套娃**：如果 Agent Host 调用的还是另一个 Agent Host，会出现谁做最终规划、谁承担错误责任的问题。
3. **保持可替换性**：企业可以使用 OpenClaw、渠道 Agent、内部 Agent 或未来新的 Host；LangChat 不应绑死调用方。

## 🔮 反问：如果今天重新设计，还会这样分层吗？

我会保留 Agent Host 与 LangChat 的边界，但会更早把 `ApplicationContract` 和 `ExecutionPlanIR` 落地。

原因是：没有统一 Contract，Agent Host 很容易直接依赖 API 或 Workflow 细节；没有 ExecutionPlanIR，发布、部署、审核和追踪就难以围绕稳定制品展开。

---

# 🧪 课堂练习（5分钟）

1. 请用一句话分别描述 Agent Host、LangChat、Provider 的职责。
2. 为什么“Agent Host 直接调用 LangChat”不代表“不需要安全控制”？
3. 如果一个 Skill 会写入 CRM，`effect_policy` 和 `human_review_gate` 应该如何帮助治理？

## 📝 课后测试（15分钟）

1. 为什么把 Orchestrator 做成所有请求的必经入口会带来架构风险？请至少写出两点。
2. 六维身份中的 `client`、`actor` 和 `delegation` 分别解决什么问题？
3. 当前 `SkillRelease → Workflow` 绑定与 v2 制品链的主要差别是什么？
4. 设计题：如果 Agent Host 要调用“发布经营日报”能力，它应如何通过 LangChat 得到一个可追踪的结果？
5. 开放题：LangChat 哪些能力应该由平台层统一治理，哪些必须仍留在 Provider？为什么？

---

# 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|---|---|---|
| Agent Host | /ˈeɪdʒənt hoʊst/ | 接收用户请求、理解意图并规划任务的智能体宿主 |
| Enterprise Capability Platform | /ˈentərpraɪz ˌkeɪpəˈbɪləti ˈplætfɔːrm/ | 企业能力平台：将能力做成可治理、可复用、可调用的产品单元 |
| SkillRelease | /skɪl rɪˈliːs/ | 已发布、可被调用和治理的技能版本 |
| Delegation | /ˌdelɪˈɡeɪʃn/ | 委托链：谁代表谁、以何种权限执行 |
| Scope | /skoʊp/ | 授权范围：允许执行哪些动作 |
| ExecutionPlanIR | /ˌeksɪˈkjuːʃn plæn aɪr/ | 执行计划中间表示：编译后、运行前的稳定执行制品 |
| Trace | /treɪs/ | 链路追踪：一次请求经过哪些组件、产生什么结果 |
| Traffic Policy | /ˈtræfɪk ˈpɑːləsi/ | 流量策略：控制灰度、金丝雀、回滚等发布流量 |

## 📎 真实参考

- ADR-001：《LangChat 直连 Agent Host 的企业能力平台定位》
- `apps/backend/langchat/skill_release/routes.py`
- `apps/backend/langchat/server/auth/six_dim_middleware.py`
- `apps/backend/langchat/skill_release/descriptor.py`
- `apps/backend/langchat/skill_release/bindings/`
