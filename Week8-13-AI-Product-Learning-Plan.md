# 🧠🤖 AI 产品学习路线｜第8周-第13周

> 前7周已经完成 AI 基础。第8周开始不是重学，而是把已有知识用到真实产品上：先看 LangChat 平台层，再看 MallSenseAI 视觉智能行业层，最后进入商管系统应用层。

## 📅 总体进度

```text
W1-W7   ████████████████████ ✅ AI 基础：Transformer、RAG、推理、Agent、数字员工
W8-W11  ███████████░░░░░░░░░ 🔥 LangChat 心智模型：理解产品的完整执行链
W12-W13 ░░░░░░░░░░░░░░░░░░░░ 👁 Vision Intelligence：MallSenseAI 能力地图
W14+    ░░░░░░░░░░░░░░░░░░░░ 🚀 商管系统与产品开发 Sprint
```

## 🏗 三层产品关系

```text
LangChat：企业 AI 应用平台（平台层）
    ↓ 提供 Agent Runtime / Workflow / MCP / Knowledge / Governance
MallSenseAI：视觉智能行业能力包（行业层）
    ↓ 提供检测、视频分析、客流、安全、零售、Vision Agent
商管系统：业务应用层
    ↓ 消费能力，形成招商、运营、物业和安全决策
```

---

# 🧱 第8周-第11周：LangChat 心智模型

## 学习目标

四周不追求把所有模块“看一遍”，而是先建立一张完整的产品地图。到第11周结束，要能讲清楚：

- LangChat 为什么不是 Dify，也不是 Agent Host？
- Blueprint 为什么不能直接运行？
- ExecutionPlan 为什么要独立存在？
- Runtime 为什么无状态？
- Capability 为什么不是 Plugin？
- Governance 为什么必须前移？

## 第8周：从用户到企业能力的一条完整链路

| Day | 今日主题 | 核心问题 |
|---|---|---|
| Day1 | 用户意图：谁在调用 LangChat？ | 为什么 LangChat 不是 Agent Host？ |
| Day2 | ApplicationContract：用户到底要什么？ | 为什么 Contract 不是 API 文档？ |
| Day3 | Blueprint → Compiler → ExecutionPlan | 为什么 Blueprint 不能直接运行？ |
| Day4 | Runtime：计划如何真正执行？ | 为什么 Runtime 不保存状态？ |
| Day5 | Capability + Connector → 企业系统 | 为什么 Capability 不是 Plugin？ |
| Day6 | ⚡ 画完整链路图：输入、输出、责任边界 | 为什么这条链不能短一步？ |
| Day7 | 🔄 Virtual CTO Review：找出最薄弱的一环 | — |

## 第9周：领域对象深挖

| Day | 对象 | 核心问题 |
|---|---|---|
| Day1 | BlueprintVersion | 为什么 Blueprint 是制品而不是配置？ |
| Day2 | SkillRelease | 为什么 SkillRelease 是可部署单元？ |
| Day3 | Deployment / DeploymentRevision | 为什么 Deployment 独立于 Release？ |
| Day4 | ReleaseChannel / TrafficPolicy | 为什么需要灰度发布？ |
| Day5 | DigitalEmployeeDefinition | 为什么数字员工不拥有 Runtime？ |
| Day6 | ⚡ Domain Model Diagram | 哪些对象可能合并或拆分？ |
| Day7 | 🔄 ADR Health Check | 现有 ADR 是否过时？ |

## 第10周：Governance 是横切约束，不是最后补丁

| Day | 主题 | 核心问题 |
|---|---|---|
| Day1 | Permission & Policy | 为什么权限不放在 Runtime 里？ |
| Day2 | Audit & Trace | 为什么 Trace 不等于日志？ |
| Day3 | Approval | 为什么 AI 不能自动发布全部内容？ |
| Day4 | PII & Compliance | 为什么治理不能最后做？ |
| Day5 | FrozenExecutionContext | 为什么上下文必须冻结？ |
| Day6 | ⚡ Governance 覆盖图 | 最大治理缺口在哪里？ |
| Day7 | 🔄 Virtual CTO Review | 如果只能修一个治理问题，先修哪个？ |

## 第11周：面对代码事实

| Day | 任务 | 核心问题 |
|---|---|---|
| Day1 | Capability Inventory：已有能力清单 | 哪些能力名不副实？ |
| Day2 | Gap Matrix：目标态与现状对照 | 哪个 Gap 最危险？ |
| Day3 | Connector 现状 | Connector 是最薄弱环节吗？ |
| Day4 | Knowledge 现状 | Knowledge 治理还缺什么？ |
| Day5 | 竞品对比：Dify / LangGraph / OpenClaw / Claude Code | LangChat 最独特的设计是什么？ |
| Day6 | ⚡ 输出 LangChat v2 实施路线图 | 前3个 Sprint 做什么？ |
| Day7 | 🔄 最终 CTO Review | 后续开发如何排优先级？ |

---

# 👁 第12周-第13周：Vision Intelligence 能力地图

> 统一叫“视觉智能”，而不是“计算机视觉”。因为真正的商业系统不止做检测，还要从视频理解到业务决策。

## 五层能力模型

```text
L1 图像理解：Detection / OCR / Segmentation
L2 视频理解：Tracking / MOT / Video Analytics
L3 场景理解：Counting / Heatmap / Crowd / Queue
L4 业务智能：客流 KPI / 安全事件 / 运营指标
L5 视觉 Agent：自动分析 / 推理 / 建议 / 日报
```

## 第12周：视觉智能全景与 MallSenseAI 现状

| Day | 主题 | 核心问题 |
|---|---|---|
| Day1 | Vision Intelligence 全景 | 为什么 MallSenseAI 不是 CV 项目？ |
| Day2 | MallSenseAI 仓库与巡检流水线 | 为什么当前先做定时截图？ |
| Day3 | Detection：YOLO / RT-DETR / SAM / GroundingDINO | 什么时候用哪个？ |
| Day4 | Video Analytics 基线 | 从截图升级视频流要改什么？ |
| Day5 | Business Scene Matrix | 哪个商业场景 ROI 最高？ |
| Day6 | ⚡ Vision 五层图 + 场景矩阵 | MallSenseAI 目前位于哪一层？ |
| Day7 | 🔄 Virtual CTO Review | 当前能力边界是否清晰？ |

## 第13周：能力蓝图与平台集成

| Day | 主题 | 核心问题 |
|---|---|---|
| Day1 | People Analytics：客流、停留、热区 | 客流为什么离不开 Tracking？ |
| Day2 | Security Analytics：入侵、越界、跌倒、烟火 | 为什么误报率是安全场景的核心？ |
| Day3 | Retail Analytics：排队、陈列、缺货 | 如何把视觉能力变成业务 KPI？ |
| Day4 | Vision Agent：从检测到建议 | Vision Agent 和 LangChat Agent 有何区别？ |
| Day5 | Vision Capability Architecture | MallSenseAI 如何成为 LangChat 行业能力包？ |
| Day6 | ⚡ Inventory + Technology Radar + Roadmap | 前3个 Sprint 做什么？ |
| Day7 | 🔄 最终 CTO Review | 如何设计集成边界？ |

## 📦 持续交付物

每一天都留下：

1. **今天多理解了什么**：以前以为 → 现在知道。
2. **一个核心问题**：为什么 X 不是 Y？
3. **Daily Engineering Log**：新增、修改、确认、遗留、技术债、下一步。
4. **Engineering Journal**：当天最大的认知、最大的坑、最大的决策。

每周日由 Virtual CTO 输出五维评分：架构质量、代码健康度、ADR 一致性、技术债、开发者体验。
