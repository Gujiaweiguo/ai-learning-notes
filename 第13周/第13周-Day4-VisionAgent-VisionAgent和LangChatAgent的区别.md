# 🧱 LangChat 心智模型 | Week13-Day4
# 📌 Vision Agent：从"检测到一个人"到"自动分析→推理→建议→日报" —— Vision Agent 和 LangChat Agent 有什么区别？

> 术语说明：LangChat 已按 ADR-008 更名为 LnkChat，本文按 W12-D7 决议使用新名（首现标注），历史引用保持原文。
> 现状声明：MallSenseAI 当前代码里**没有 Vision Agent**——只有 capture→detect→rule→alert 的自动化流水线。今天是五层模型的最后一层 L5 的**蓝图推演**：从现有自动化出发，回答"加上什么才配叫 Agent"，以及它和 LnkChat 的数字员工是什么关系。这正是明天 D5（LangChat 集成路径）的前置思考。

━━━ 1. 今日核心问题 ━━━

**Vision Agent 和 LangChat Agent 有什么区别？**

W8-W11 建立的 LangChat Agent 心智模型是：Agent Host 发来意图（ApplicationContract）→ 编译成计划（ExecutionPlan）→ Runtime 无状态执行 → Capability 连企业系统 → 治理前移。核心动词是**"执行"**——替用户调 API、查数据、发工单。

五层模型里的 L5 Vision Agent 核心动词却是**"看和说"**：自动分析 → 推理 → 建议 → 日报。没有人给它下指令。这两者真的是同一类东西吗？

今天给出的答案：**是同一个物种（都是 LnkChat 意义上的数字员工），但在三个结构维度上截然不同——时钟（谁触发）、证据（凭什么推理）、失败模式（错了怎么办）**。而当前 MallSenseAI 流水线连"Agent"都还不是——它是自动化（automation），差的那一跳是"解读与建议"。把这三个维度想透，明天"MallSenseAI 如何成为行业能力包"的答案几乎是自动浮现的。

━━━ 2. 人话解释（用 26 年 ERP 经验讲）━━━

Jason，你 ERP 里天天见的两类人，就是这两种 Agent：

**LangChat Agent = 柜员/业务经办。** 人来窗口办事："帮我查这个租户的欠费。"意图是客户给的，柜员调系统、给结果、办结。**事务驱动**：没有请求就没有动作。错了怎么办？权限不够、数据冲突就**拒绝办理**（fail-closed）——宁可让客户重新排队，不能替他猜着办。

**Vision Agent = 夜间跑批对账 + 晨会差异报告。** 没有人在半夜两点给月结程序下指令。它按钟点自己起来，扫一遍原始凭证（像素/单据），按**口径**汇总（Day3 的 Metric Contract），早上八点给管理层一份差异清单和调整建议。**时间驱动**。你做了 26 年月结，深知跑批的难点从来不是"跑"，是两件事：**口径**（哪张单算本期）和**异常的解释**（这笔差异是错误还是业务正常波动）。视觉日报一模一样：难点不是检测（那是凭证扫描），是指标口径（昨天解决）+ 今天的推理可解释（这个数字异常意味着什么、建议做什么）。

三个 ERP 人秒懂的对照：

**① 时钟不同：请求-响应 vs 班次调度。** 柜员系统空闲是正常的；跑批系统到点不跑就是事故（P1）。Vision Agent 的"上班时间"是班次/日报周期——它的调度器（MallSenseAI 的 `InspectionScheduler` 就是雏形）扮演的是"闹钟"，对应到 LnkChat 侧就是"谁在每天 06:30 触发数字员工"——外部时钟，不是用户。

**② 证据不同：API 返回值可以信，自己的眼睛不能全信。** 柜员查余额，系统说多少就是多少（信任边界在系统外）。跑批对账不行——**凭证本身就是脏的**：漏录的单、重复的行、口径含混的科目。Vision Agent 更极端：它的"凭证"是 Day1-Day3 的检测流，自带 20% 偏差、误报率、系统性遮挡。所以 Vision Agent 推理时必须携带**证据的置信度**——"B1 昨日排队 11 分钟（95% CI [9, 14]）"和"B1 排队 11 分钟"是两句完全不同的话。LangChat Agent 的推理对象是结构化事实；Vision Agent 的推理对象是**统计量**。

**③ 失败模式不同：拒绝 vs 降级。** 柜员 fail-closed 拒办，客户重排队，损失一次体验。但巡场系统不能"停"——摄像头停了等于全盲，跑批停了月底没账。所以 Vision Agent 的正确姿势是 Day2 学过的**降级**：证据不足→标注不确定→转人工复核，观测永不停机。**Fail-closed 是事务系统的美德，降级是观测系统的美德。**

━━━ 3. LangChat（LnkChat）架构位置 ━━━

五层模型的塔尖，也是唯一"会说话"的一层：

```
L1  Image Understanding     — 检测框（凭证）                    ← 现有 detectors
L2  Video Understanding     — 时序证据                          ← Day1/Day2 讨论过
L3  Scene Understanding     — 场景状态（ROI 占用/队列形态）      ← 规则引擎部分同构
L4  Business Intelligence   — 指标/KPI（口径化）                 ← Day3，完全缺失
L5  Vision Agent            — 解读 KPI → 归因 → 建议 → 日报      ← 【今日】
```

放到 LnkChat 三层架构链（ADR-007）里，L5 不是一个平行的新东西，而是**一次身份映射**：

```
MallSenseAI（L1-L4，感知+指标系统）
   │  以 Capability 形式暴露数据（vision.kpi.query / safety.alert.summary）
   ▼
LnkChat 平台层（Capability → SkillRelease 编译 → Runtime 执行）
   │  Skill = "晨间运营日报生成"（LLM 推理层住在这里）
   ▼
数字员工（DigitalEmployeeModel，绑定该 Skill）
   │  每日 06:30 由外部时钟触发 dispatch（API / MCP）
   ▼
消费端：晨会大屏 / 企业微信日报 / 管理层追问对话
```

**塔尖的判断：Vision Agent 不是 MallSenseAI 内部要长出来的器官，而是 LnkChat 数字员工披上视觉外衣。** MallSenseAI 的职责到 L4 为止（提供带口径的证据），L5 的"推理"住进 LnkChat 的 Skill 层。谁触发（时钟）、凭什么推理（证据）、错了怎么办（治理）全部复用平台。这就是"行业能力包"的准确含义——**包里装的是能力和证据，不装 Agent 框架**。

━━━ 4. ADR / 战略文档依据 ━━━

**① v2 Domain Model：OrchestratorAgent 退役、数字员工是"产品语义聚合"。** 目标域模型明确 OrchestratorAgent 不在 v2 保留（"Orchestrator 是可替换角色"），`DigitalEmployeeDefinition` 表达"企业内承担某类工作的 AI 应用主体"。推论：**Vision Agent 如果要在企业里"承担某类工作"，它的企业身份就是数字员工**——不需要发明新身份。它的 Agent 性来自推理层（LLM），不来自感知层（摄像头）。

**② ADR-LC-013：数字员工不拥有 Runtime，且治理在 dispatch 时点收口。** 三条对 Vision Agent 直接适用：`bound_skill_id` 是 dispatch-time 约束（数字督导只能跑"日报生成"这个 Skill，403 mismatch）；`kill_switch` 传播到 canonical dispatch（一键停掉一个会发日报的员工，比停掉一个 pipeline 重要得多——它有话语权）；`allowed_capabilities` 延后强制。**注意最后这条的深意：能力注册表（稳定 capability ID）不存在之前，连"视觉督导能读哪些摄像头"都约束不了**——这是 D5 集成路径的 P0 前置件。

**③ ADR-003（Capability 行业正交）：视觉能力是行业 facet，不是新平台。** 按正交模型，`vision.kpi.query` 和 `lease.contract.query` 是同一抽象的两个实例——一个的 Connector 指向检测事件库，另一个指向 MI ERP。**平台不为视觉开特例**，这正是"Vision Agent ≠ 另一种 Agent"的架构表述。

**④ 域知识.md 设计决策 #2（封闭系统）再次成为边界裁决点。** 封闭的理由是秒级实时安防不能中转。但 L5 日报是分钟/日级容忍的——按 W13-D3 已经用过的推理：**凡是容忍分钟级延迟的场景，就没有理由封闭**。Vision Agent 是打开封闭系统的第二个切口（第一个是 D3 推演的 `retail.kpi.query`）。

**⑤ W10-D3 的 Prompt Runtime Resolution 直接管住 L5。** 日报是 LLM 生成的——即 prompt 产物。custody→evidence→verify 链路要求：日报里的每个数字必须能回溯到证据（哪个 KPI、什么口径、哪批检测事件）。**没有这条链，"AI 写的日报"在企业里没有公信力**——这和月结报告必须附试算平衡表是同一个道理。

━━━ 5. 代码验证（只看关键结构）━━━

**当前 pipeline 离 Vision Agent 差几跳？逐个看关键结构：**

**① 时钟已存在——`workers/scheduler.py`：**
```python
class InspectionScheduler:
    """Schedules periodic inspections with failure backoff and isolation."""
BACKOFF_SECONDS = (30.0, 60.0, 120.0, 300.0)
```
per-camera interval + 指数退避。这就是 Vision Agent 的"闹钟"原型——但它只触发**检测**，不触发**报告**。差的一跳：日级聚合调度（06:30 汇总昨日）不存在，也没有任何"到点调用外部系统"的出口（封闭系统）。

**② 主干是自动化，不是 Agent——`workers/pipeline.py`：**
```python
class DetectionPipeline:
    """Orchestrates: load context → run detectors → evaluate rules → create alerts."""
```
五个环节全是确定性代码：条件满足 → 告警。**没有任何一环在"解读"**——系统不知道"消防通道连续三天早高峰占用"意味着什么，只会第三次再响一次铃。这正是 automation 与 agent 的分界：**规则触发 vs 证据推理**。注意这不是贬义——Day2 学过，安防主链路要的就是确定性。推理层是**叠加**在旁边，不是替换。

**③ 人审闭环已在——alert lifecycle `pending → confirmed → resolved / false_positive`。** 这是 Vision Agent 最重要的现成资产：**信任闭环的雏形**。日报说"昨天 3 起通道占用"，管理层标其中 1 起 false_positive——这个反馈流将来就是推理层校准的原料（哪类场景它总说错）。LangChat 侧对应 ADR-LC-011 的 approval gate：**有话语权的输出，都要有人审通道**。

**④ LnkChat 侧的 dispatch 约束已就位——`skill_release/canonical/de_dispatch_guard.py`（ADR-LC-013 落地点）。** 数字员工身份（actor_type）进 dispatch，先查 bound_skill 匹配 + kill_switch 再放行。**Vision Agent 作为数字员工入职的那道门，代码已经写好了**——缺的是门这边没有 Skill（日报生成），门那边没有 Capability（vision.kpi.query）。

**Gap 小结（四个不存在）**：日级聚合层 ✗、指标口径层 ✗（Day3 结论）、LLM 推理层 ✗、capability 出口 ✗。存在的：时钟 ✚ 检测 ✚ 告警生命周期 ✚ 平台侧 dispatch 治理 ✚。

━━━ 6. 商业地产映射 ━━━

| LangChat/MallSenseAI 概念 | MI CRE 场景 |
|---|---|
| Vision Agent（数字督导） | 每个购物中心的"数字运营督导"：每日 06:30 出《昨日运营日报》 |
| L4 指标 + 口径 | 日报里的数字：客流峰值、排队时长、通道占用率、清洁达标率（口径=审计线索） |
| L1-L3 检测证据 | 日报附录的证据链：哪台摄像头、哪个时段、哪批检测事件 |
| bound_skill_id 约束 | 数字督导只会干"出日报"这一件事，不能顺手查财务（403） |
| kill_switch | 某项目日报出问题，总部一键停发该项目的数字督导，其他项目不受影响 |
| false_positive 反馈 | 物业经理晨会圈出"这条不对"→ 督导下周不再犯同类错（校准闭环） |
| LangChat Agent（对照） | 租户服务台数字员工：接租户问询、查合同、开工单——**等客上门** |

两个 Agent 组合的晨会场景：管理层看完日报追问——"为什么 B1 昨天排队 20 分钟？"数字督导给**事实与统计**（L4 层面归因：11:30-13:00 峰值，收银台开放数 3→2）；继续问"损失多少销售？"→ 这超出视觉证据范围，转给**租户服务/经营分析数字员工**调 POS 交叉归因。**各答各的证据范围内的问题——这本身就是治理**（Vision Agent 不越界推测 POS 数据）。

━━━ 7. 与传统方案比较 ━━━

L5 推理层放哪？三个方案：

| 方案 | 做法 | 问题 |
|---|---|---|
| A. 封闭系统内自建 | MallSenseAI pipeline 末尾直接调 LLM API 出日报 | 治理全缺：无 prompt custody（日报数字无法回溯验证）、无灰度（换 prompt=停机重发）、无 kill_switch、无审批；每次能力升级都是发版。域知识.md 自己的封闭理由（实时性）在日报场景根本不成立 |
| B. 独立 Vision Agent 产品 | 单独的 agent 框架/产品，自带 LLM 编排 | 双份 runtime、双份治理、双份数字员工体系；和租户服务数字员工无法统一管理（企业要的是"一个数字员工花名册"，不是 N 套 AI 产品） |
| **C. 平台 Skill + 视觉 Capability（推荐）** | MallSenseAI 到 L4 为止；推理做成 LnkChat SkillRelease；数字员工绑定该 Skill；数据经 capability（vision.kpi.query）暴露 | 需要 D5 解决集成件：capability 注册表、日级调度触发源、证据 digest 对齐（KPI snapshot 进 knowledge_snapshot_digest） |

**为什么选 C：** 治理复用是表因，深因是**变化率不同层**。检测模型/指标口径（MallSenseAI 侧）变化周期是周；prompt/推理策略（Skill 侧）变化周期是天。方案 A 把两种变化率焊死在一个发版单元里——正是 ERP 时代"报表改一行 SQL 要走财务系统发版"的老坑。方案 C 用 capability 接口把变化率切开，两边独立演进。

━━━ 8. 架构师思考题 ━━━

**① 身份题**：MallSenseAI 摄像头系统以什么身份进入 LnkChat——Connector 背后的 External System、Capability 提供方、还是 Agent Host？三者的平台契约分别是什么？（提示：它既是"被连接的企业系统"（数据在它库里），又是"能力提供方"（检测本身是能力），还自带时钟想触发 Skill。一个系统可以身兼数职吗？哪个身份是第一位的？）

**② 责任题**：日报里"B1 排队 20 分钟"实际是 15 分钟（Day3 型系统性偏差：遮挡漏检）。追责时——检测层（YOLO 漏检）、指标层（口径没做遮挡补偿）、推理层（LLM 没带不确定性地陈述）——错在哪层？**证据链要怎么设计，才能让审计在 10 分钟内定位到层**？（提示：Day3 的 Metric Contract + 今日的置信度传播，本质都是在给"数字"装配责任标签。）

**③ 治理题**：数字督导的日报有话语权（管理层据此排班）。按 ADR-LC-011 的 approval gate 思路——日报应该全量人审后发、抽样审、还是先全自动+事后反馈校准？三个方案的信任建立速度 vs 人力成本怎么权衡？什么阶段切换？

━━━ 9. 我的理解变化 ━━━

**以前以为**：Vision Agent 是 CV 领域的另一种 Agent 框架——有自己的一套 perception-action loop，和 LangChat Agent 是平行竞品，将来要做"MallSenseAI 的 Agent 框架"选型。

**现在知道**：① "Agent"的自治有三种时钟——意图驱动（用户请求）、时间驱动（班次/跑批）、事件驱动（告警触发），**时钟不改变物种**，都是"企业内承担某类工作的 AI 应用主体"（= 数字员工）；② 当前 MallSenseAI 是 automation（规则触发），agent 性只能来自推理层，而推理层不该自建——**Vision Agent = L1-L4 感知系统 + LnkChat 数字员工的组合体**，不是第三个物种；③ 真正的结构差异在时钟/证据/失败模式三件事上——尤其证据：**LangChat Agent 推理结构化事实，Vision Agent 推理统计量，后者必须携带置信度说话**，这决定了它的 prompt、它的报告格式、它的审批设计全都不同。框架是同一个，话术和证据学是两套。

━━━ 10. 明日连接 + Semantic Layer ━━━

**明天 D5：Vision Capability Architecture —— MallSenseAI 如何成为 LnkChat 的行业能力包？** 今天留下了全部接口：capability 注册表（P0 前置）、日级触发源、证据 digest 对齐、身份裁决（思考题①就是明天开场题）。

**今天知识在 Semantic Layer 链上的位置**：

```
Ontology（商业地产运营本体：客流/安全/排队/清洁 是"运营事实"）
  → Domain Model（数字员工=运营督导；DetectionEvent/Metric/KPI/Report 领域对象）
    → Capability（vision.kpi.query / safety.alert.summary ← 今天定义的两个候选）
      → Skill（晨间运营日报生成 = 推理层住所，绑定数字督导）
```

L5 的一天把五层模型封顶了：**本体层的"运营事实"，最终以一份可审计、可停发、可追责的日报形态，回到管理层手里**——这就是 Vision Intelligence 这条产品线的价值闭环。
