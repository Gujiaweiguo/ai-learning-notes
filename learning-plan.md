# AI 产品学习计划（Week 8-13）

## 总览

```
Week 1-7:   AI 基础（已完成）
Week 8-11:  LangChat 心智模型（4周）
Week 12-13: Vision Intelligence 能力地图（2周）
Week 14+:   商管系统 / 开发阶段
```

学习顺序 = 产品架构顺序：
```
LangChat（平台层）→ MallSenseAI（行业层）→ 商管系统（应用层）
```

---

# Part 1: LangChat Mental Model（Week 8-11）

## 目标

**Week 8-11（4周）建立 LangChat 完整心智模型。**

前7周（Week 1-7）是 AI 基础阶段。从 Week 8 开始，学习焦点从泛 AI 知识转向 LangChat 产品架构。这是延续，不是重来。

结束后能用自己的话讲清楚：
- LangChat 为什么不是 Dify？
- 为什么 ExecutionPlan 不是 Blueprint？
- 为什么 Runtime 无状态？
- 为什么 Capability 独立？
- 为什么 Governance 前移？
- 脑子里有一张完整的图，任何模块放进去都知道为什么存在

## 信息源

| 来源 | 路径 | 内容 |
|---|---|---|
| 代码仓库 | `/root/langchat` | 当前实现事实 |
| ADR | `/root/langchat-docs/lanlnk/out/prd/langchat/output/review/ADR-00*.md` | ADR-001~008 |
| v2战略文集 | `.../review/v2-strategy/` | Charter + Domain Model + Execution Spec（已冻结） |
| PRD | `.../langchat/output/产品PRD.md` 等 | 产品需求 |
| OpenSpec | `/root/langchat/openspec/specs/` | 100+ 能力规格 |
| AGENTS.md | `/root/langchat/AGENTS.md` | 代码架构指南 |

## 每日推送格式

```
🧱 LangChat 心智模型 | WeekX-DayY
📌 当前主题

🎯 Today's Question
   每天一个"为什么X不是Y"的核心问题

1. 为什么需要（10%）
2. ADR 怎么设计的（25%）— 扫描相关 ADR / v2-strategy / OpenSpec
3. 现有代码怎么实现的（25%）— 读 /root/langchat 对应模块
4. Gap Analysis（20%）— 目标态 vs 代码现实
5. 今日产出（20%）— 明确下一步 action

📘 今天多理解了什么？
   以前以为：XXX → 现在知道：XXX

🔮 如果今天重新设计 LangChat，你还会这样设计吗？为什么？
```

加上：
```
📝 Daily Engineering Log（结构化）
   新增 / 修改 / 删除 / 确认 / 遗留 / 技术债 / 下一步
```

## 每周节奏

| 日期 | 角色 | 内容 |
|---|---|---|
| 周一~周五 | Chief Architect Mentor | 推进当日链路/对象/关注点 |
| 周六 | Chief Architect Mentor | 实战：画图 / 写文档 / Gap Matrix |
| 周日 | Virtual CTO | Architecture Review + 五维评分 + ADR Health Check + Progress Report |

## 周日 Virtual CTO Review 模板

```
🔍 Weekly Architecture Review

1. 本周理解进度（1-10）
2. 本周新增认知清单
3. 是否符合 v2 Charter
4. ADR Health Check（是否过时/需拆分/需冻结）
5. 五维评分：
   - Architecture Quality (X/10)
   - Code Health (X/10)
   - ADR Consistency (X/10)
   - Technical Debt (X/10, 分越高质量越好)
   - Developer Experience (X/10)
6. 下周建议
```

## 永久文档

### Engineering Journal
每天追加到 `/root/learning-notebooks/engineering-journal.md`

```
## YYYY-MM-DD
### 今天最大的认知
### 今天最大的坑
### 今天最大的决策
```

---

## Week 8：End-to-End Journey（一条链走通）

> 不拆模块。从用户输入到执行结果，一天走一步。
> 7月20日-7月26日

| Day | 日期 | 跟着链路走 | Today's Question |
|---|---|---|---|
| D1 周一 | 7/20 | **用户意图**：谁在调用 LangChat？Agent Host 怎么连进来？ | 为什么 LangChat 不是 Agent Host？ |
| D2 周二 | 7/21 | **ApplicationContract**：用户要做什么？怎么描述？ | 为什么 Contract 不是 API 文档？ |
| D3 周三 | 7/22 | **Blueprint → Compiler → ExecutionPlan**：意图怎么变成可执行的？ | 为什么 Blueprint 不能直接运行？ |
| D4 周四 | 7/23 | **Runtime**：执行计划怎么跑起来的？ | 为什么 Runtime 不保存状态？ |
| D5 周五 | 7/24 | **Capability + Connector → Enterprise System**：执行时怎么连到业务系统？ | 为什么 Capability 不是 Plugin？ |
| D6 周六 | 7/25 | ⚡ **走完整条链**：画一张完整链路图，标出每一步的输入输出 | 为什么这条链不能短一步？ |
| D7 周日 | 7/26 | 🔄 **Virtual CTO**：这条链上哪里最薄弱？五维评分 | — |

**Week 8 结束后：LangChat 完整链路在脑子里是通的。**

---

## Week 9：Domain Deep Dive（拆对象，理解为什么）

> 回到每个对象，理解它为什么存在、边界在哪、替代方案是什么。
> 7月27日-8月2日

| Day | 日期 | 对象 | Today's Question |
|---|---|---|---|
| D1 周一 | 7/27 | **BlueprintVersion** | 为什么 Blueprint 是制品不是配置？ |
| D2 周二 | 7/28 | **SkillRelease** | 为什么 SkillRelease 是唯一可部署单元？ |
| D3 周三 | 7/29 | **Deployment / DeploymentRevision** | 为什么 Deployment 独立于 Release？ |
| D4 周四 | 7/30 | **ReleaseChannel / TrafficPolicy** | 为什么需要灰度？不能一次全量？ |
| D5 周五 | 7/31 | **DigitalEmployeeDefinition** | 为什么数字员工不拥有 Runtime？ |
| D6 周六 | 8/1 | ⚡ **画 Domain Model Diagram**：对象关系、生命周期、依赖 | 哪个对象最可能被合并？哪个最可能被拆分？ |
| D7 周日 | 8/2 | 🔄 **Virtual CTO**：ADR Health Check — 8个 ADR 有没有过时或需要拆分的？ | — |

**Week 9 结束后：每个对象都能解释"为什么它必须独立存在"。**

---

## Week 10：Governance（横切关注点）

> 不按模块学，按关注点学。因为 Governance 横跨所有模块。
> 8月3日-8月9日

| Day | 日期 | 主题 | Today's Question |
|---|---|---|---|
| D1 周一 | 8/3 | **Permission & Policy**：谁允许谁做什么？ | 为什么 Permission 不放 Runtime 里？ |
| D2 周二 | 8/4 | **Audit & Trace**：怎么知道发生了什么？ | 为什么 Trace 不是日志？ |
| D3 周三 | 8/5 | **Approval（人审）**：哪些操作需要人审？ | 为什么 AI 不能全自动发布？ |
| D4 周四 | 8/6 | **PII & Compliance**：敏感数据怎么管？ | 为什么 Governance 不能最后做？ |
| D5 周五 | 8/7 | **FrozenExecutionContext**：身份和委托怎么传递？ | 为什么 Context 必须冻结？ |
| D6 周六 | 8/8 | ⚡ **画 Governance 覆盖图**：哪些模块已有治理，哪些没有 | 最大的治理 Gap 在哪？ |
| D7 周日 | 8/9 | 🔄 **Virtual CTO**：如果只能修一个治理问题，先修哪个？ | — |

**Week 10 结束后：理解 Governance 不是模块，而是横切所有模块的约束。**

---

## Week 11：Code Reality（面对代码事实）

> 前三周建立了心智模型。第四周面对现实：代码和模型差多远？
> 8月10日-8月16日

| Day | 日期 | 任务 | Today's Question |
|---|---|---|---|
| D1 周一 | 8/10 | **Capability Inventory**：扫描代码，列出所有现有能力 + 状态 | 哪些 Capability 名不副实？ |
| D2 周二 | 8/11 | **Gap Matrix**：目标态对象 vs 代码实现，逐个打分 | 哪个 Gap 最危险？ |
| D3 周三 | 8/12 | **Connector 现状**：REST/MCP/Channel 各自到什么程度？ | Connector 是 LangChat 最弱的部分吗？ |
| D4 周四 | 8/13 | **Knowledge 现状**：当前 RAG 实现 vs Knowledge Governance 目标 | Knowledge 治理缺什么？ |
| D5 周五 | 8/14 | **竞品对比**：Dify/LangGraph/OpenClaw/Claude Code 各自的链路 | LangChat 最独特的设计是什么？ |
| D6 周六 | 8/15 | ⚡ **输出：LangChat v2 实施路线图 v1.0** — 按 Sprint 拆分 | 前3个 Sprint 做什么？ |
| D7 周日 | 8/16 | 🔄 **最终 Virtual CTO Review**：4周总复盘 + 五维评分趋势 + 后续开发节奏 | — |

**Week 11 结束后：有一张"现状-目标"对照图 + 一份可执行的实施路线图。**

---

## 4周交付物

```
Week 8: LangChat 完整链路图
Week 9: Domain Model Diagram + ADR Health Check 报告
Week 10: Governance 覆盖图 + 最大 Gap 清单
Week 11: Capability Inventory + Gap Matrix + 实施路线图 v1.0

持续4周:
  📖 Engineering Journal（28天设计史）
  📝 Daily Engineering Log（每天代码事实）
  ❓ 28个核心 Question 及回答
  📊 五维评分趋势（每周日）
```

## Week 8-11 后

Week 8-11 是"建立心智模型"。之后进入开发阶段：
- 按路线图分 Sprint 推进
- 每周保持 Virtual CTO Review
- OpenClaw 从"架构导师"切换为"开发搭档"

---

# Part 2: Vision Intelligence 能力地图（Week 12-13）

## 定位

**建立 Vision Intelligence 认知地图，明确 MallSenseAI 作为 LangChat 行业能力包（Industry Capability Pack）的定位和演进路径。**

> 统一术语：Vision Intelligence（不叫 Computer Vision）
> 因为未来系统不会只有 Detection，还有 Tracking → Scene Understanding → Knowledge → Reasoning → Agent → Business Decision
> 后面都是 AI，不只是 CV

### 产品关系

```
LangChat（企业 AI 应用平台）
 │  Agent Runtime / Workflow / MCP / Knowledge / Governance
 │
 ▼
MallSenseAI（视觉智能行业能力包）
 │  Detection / Video Analytics / People Analytics
 │  Security Analytics / Retail Analytics / Vision Agent
 │
 ▼
商管系统 / MI / CRM（业务应用层）
```

- **LangChat** = 平台层（AI 应用平台）
- **MallSenseAI** = 行业层（视觉智能能力包）
- **商管系统** = 应用层（业务消费）

### Vision Capability 五层模型

```
L1  Image Understanding     — Detection / OCR / Segmentation
L2  Video Understanding     — Tracking / MOT / Video Analytics
L3  Scene Understanding     — Counting / Heatmap / Crowd / Queue
L4  Business Intelligence   — 客流 KPI / 安全事件 / 运营指标
L5  Vision Agent            — 自动分析 / 推理 / 建议 / 日报
```

每一层只依赖下一层。新增能力（ReID / Pose / Action / VLM）都知道放哪。

## 信息源

| 来源 | 路径 | 内容 |
|---|---|---|
| 代码仓库 | `/root/MallSenseAI` | 当前实现事实 |
| PRD | `/root/langchat-docs/lanlnk/out/prd/MallSenseAI/output/` | 产品需求 |
| 域知识 | `.../MallSenseAI/域知识.md` | 检测器/巡检流水线/设计决策 |
| AGENTS.md | `/root/MallSenseAI/AGENTS.md` | 代码架构指南（25KB） |
| OpenSpec | `/root/MallSenseAI/openspec/specs/` | 能力规格 |

---

## Week 12：Vision Intelligence 全景 + MallSenseAI 现状

> 8月17日-8月23日

| Day | 日期 | 任务 | Today's Question |
|---|---|---|---|
| D1 周一 | 8/17 | **Vision Intelligence 全景**：CV/VLM/Video Analytics 生态，五层模型总览 | 为什么 MallSenseAI 不是 CV 项目？ |
| D2 周二 | 8/18 | **MallSenseAI 仓库精读**：Pipeline/Detectors/Rules/Alerts/Workers 全链路 | 为什么当前是定时截图而不是视频流？ |
| D3 周三 | 8/19 | **Detection 体系**：YOLO/RT-DETR/SAM/GroundingDINO，什么时候用哪个 | 为什么 MallSenseAI 选择了 YOLO-World？ |
| D4 周四 | 8/20 | **Video Analytics 基线**：当前截图模式 vs 未来 RTSP/FFmpeg/GPU 推理 | 从截图到视频流，架构要改什么？ |
| D5 周五 | 8/21 | **Business Scene Matrix**：业务目标→场景→能力→系统 映射 | 哪个商业场景 ROI 最高？ |
| D6 周六 | 8/22 | ⚡ **画 Vision Capability 五层图 + Business Scene Matrix** | MallSenseAI 现在站在 L1 的哪一部分？ |
| D7 周日 | 8/23 | 🔄 **Virtual CTO**：MallSenseAI 能力边界审视 + 五维评分 | — |

**Week 12 结束后：Vision Intelligence 全景在脑子里，MallSenseAI 的位置清晰。**

---

## Week 13：能力蓝图 + LangChat 集成路径

> 8月24日-8月30日

| Day | 日期 | 任务 | Today's Question |
|---|---|---|---|
| D1 周一 | 8/24 | **People Analytics**：客流/密度/停留时间/热区/轨迹 | 客流统计为什么不是 Detection 而是 Tracking？ |
| D2 周二 | 8/25 | **Security Analytics**：入侵/越界/跌倒/烟火/危险区域/离岗 | 安全场景为什么误报率是核心挑战？ |
| D3 周三 | 8/26 | **Retail Analytics**：排队分析/货架陈列/缺货检测 | 零售场景的 Vision 能力如何转化为 KPI？ |
| D4 周四 | 8/27 | **Vision Agent**：从"检测到一个人"到"自动分析→推理→建议→日报" | Vision Agent 和 LangChat Agent 有什么区别？ |
| D5 周五 | 8/28 | **Vision Capability Architecture**：Vision Capability → Vision Runtime → Vision Agent → LangChat Integration | MallSenseAI 如何成为 LangChat 的行业能力包？ |
| D6 周六 | 8/29 | ⚡ **输出：Vision Capability Inventory + Vision Technology Radar + 演进路线图** | 前3个 Sprint 做什么？ |
| D7 周日 | 8/30 | 🔄 **最终 Virtual CTO Review**：2周总复盘 + MallSenseAI × LangChat 集成评估 | — |

**Week 13 结束后：有一张完整的视觉智能能力地图 + 技术雷达 + 演进路线。**

---

## Business Scene Matrix 模板

```
业务目标 → 视觉场景 → Vision Capability → 系统模块

提升招商   → 客流分析   → Counting/Tracking    → People Analytics
提高安全   → 消防通道   → Intrusion/Detection   → Security Analytics
提高运营   → 排队分析   → Queue Analysis       → Retail Analytics
降低成本   → 自动巡检   → Detection             → MallSenseAI 现有
```

## Vision Technology Radar 模板

| 技术 | 是否学习 | 是否采用 | 是否进入产品 | 备注 |
|---|---|---|---|---|
| YOLO（11n/v8s） | ✅ | ✅ | ✅ | 已用于障碍物/火灾检测 |
| YOLO-World | ✅ | ✅ | ✅ | 已用于零样本检测 |
| RT-DETR | ✅ | 待评估 | ❌ | 精度更高但推理更慢 |
| SAM2 | ✅ | 待评估 | ❌ | 分割能力 |
| GroundingDINO | ✅ | 规划 | ❌ | 开放词表检测替代 |
| ByteTrack | ✅ | 规划 | ❌ | 视频流 Tracking |
| BoT-SORT | ✅ | 规划 | ❌ | 多目标跟踪 |
| ReID | ✅ | 长期 | ❌ | 跨摄像头追踪 |
| Pose | ✅ | 长期 | ❌ | 跌倒/行为识别 |
| VLM | ✅ | 长期 | ❌ | 场景理解 |
| Vision Agent | ✅ | 长期 | ❌ | 自动分析+建议 |

> 每半年更新一次

---

## Week 12-13 交付物

```
1. Vision Capability 五层图（L1-L5）
2. Business Scene Matrix（业务目标→场景→能力→系统）
3. Vision Capability Inventory（能力清单 + 现状 + 规划）
4. Vision Technology Radar（技术评估 + 采用状态）
5. MallSenseAI × LangChat 集成路径
6. MallSenseAI 演进路线图

持续2周:
  📖 Engineering Journal（继续追加）
  ❓ 10个核心 Question 及回答
  📊 五维评分（每周日）
```
