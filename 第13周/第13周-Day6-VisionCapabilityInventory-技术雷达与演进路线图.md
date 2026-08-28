# 🧱 Vision Intelligence 心智模型 | Week13-Day6
# 📌 Vision Capability Inventory + Technology Radar + 演进路线图 —— 前3个 Sprint 做什么？排序原则是什么？

> 术语说明：LangChat 已按 ADR-008 更名为 LnkChat，本文按 W12-D7 决议使用新名（首现标注）。
> 现状声明：本文是 Week 12-13 的总交付物（Inventory + Radar + Roadmap 三件套）。所有"现状"栏均来自今天对 `/root/MallSenseAI` 代码的真实扫描，不是规划想象。

━━━ 1. 今日核心问题 ━━━

**前3个 Sprint 做什么？**

这个问题里藏着一个更根本的问题：**排序原则是什么？** 候选项一大堆——误报率优化、客流 Tracking（L2）、日级 KPI 聚合（L4）、capability 集成（Day5 的三份纸）、VLM 场景理解、人脸脱敏合规……每个都有理由做第一个。周六交付日不回答"做什么"清单，回答**"凭什么先做这个"的裁决逻辑**。

直觉排序是技术驱动的：哪个最酷做哪个（VLM Agent）、哪个缺补哪（L2 Tracking 是五层模型断层）。但今天的盘点会给出相反结论：**前3个 Sprint 里没有一个新检测能力**。因为 Inventory 盘出来的最大资产和最大负债，都指向同一件事——**系统已经在生成免费的监督标签（alert lifecycle），却没有人把尺子立起来**（火灾漏报率未量化、误报率未持续优化——两条写在域知识.md 里的已知风险）。

━━━ 2. 人话解释（用 26 年 ERP 经验讲）━━━

Jason，你 26 年 ERP 见过无数次"系统升级"，今天这份路线图就是你 2003 年就会做的排序：

**老系统要重新推广，第一步从来不是加新模块，是三件事按死顺序做：对账 → 报表 → 开接口。**

**第一步：对账（Sprint 1）。** 你的 ERP 接手一个烂尾项目要恢复推广，第一件事干什么？把库存对平、把应收对准。没人敢卖一个"账对不平"的系统。MallSenseAI 现在就是"账没对平"：告警发出去，客户问"误报率多少？"——答不出来；消防问"火灾漏报率多少？"——答不出来。**答不出来的数字，就是卖不出去的产品。** 而最讽刺的是：对账的原材料早就在账上了——每次告警的 `false_positive` / `confirmed` 标签就是运维人员免费打的 ground truth（Sprint 1 只需要把这笔"已记账"的数据变成报表）。

**第二步：报表（Sprint 2）。** 账平了，出经营报表。客户买的不是"告警事件列表"，是"本月 B1 消防通道告警 37 起、确认 29 起、误报 8 起、PPV 78%、比上月升 6 个点"。事件→KPI 的聚合层，就是你 ERP 时代的"日记账→科目余额表"。没有余额表，管理员每天翻流水账——现在 MallSenseAI 的 dashboard 就是流水账。

**第三步：开接口（Sprint 3）。** 报表有了，才谈生态。Day5 的三份纸（Application 元数据 + Capability 描述符 + Connector）这时候才落地——因为你得先有 `lnkchat.vision.kpi.query` 能查的东西（KPI 表是 Sprint 2 产物），才有东西可打包。

**为什么客流（L2）这个"ROI 最高"的场景反而不进前3个 Sprint？** 因为它在商业上是新开一条产品线（要重新卖），在技术上是架构换代（截图→视频流，W12-D4 的结论），在数据上依赖第一步的尺子（Tracking 的 PPV 怎么度量？用同一把尺）。**先卖好已有的，再造新的**——你从来不会在应收模块对账对不平的时候，同时启动新零售渠道系统。

━━━ 3. 架构位置（五层模型 × 三段架构坐标）━━━

今天盘点的对象覆盖全部坐标——这是 Week 13 第一次把 Inventory 按两个维度同时定位：

```
五层模型（能力纵轴）        三段架构链（ADR-007，集成横轴）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
L5 Vision Agent      ─→ 住段1（LnkChat Skill 层）        【无：前置件=capability】
L4 Business Intel    ─→ 数据住段3，查询经段2 capability    【雏形：事件流水有，聚合无】
L3 Scene Understand  ─→ 段3 视觉侧                        【无：依赖 L2】
L2 Video Understand  ─→ 段3 视觉侧                        【无：截图模式，无 Tracking】
L1 Image Understand  ─→ 段3 视觉侧                        【有：4 检测器全部产品化】
     平台工程底座     ─→ 段3（治理/模型管理/测试/规格）      【强：510 测试+29 规格+CI】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

两个坐标轴回答不同的问题：**五层轴回答"视觉能力到哪了"**（答案是：L1 满格、L2-L3 空白、L4 雏形、L5 无）；**三段轴回答"这些能力离被 LnkChat 消费还有多远"**（答案是：一段都没接——封闭系统，连第一个 capability 描述符都不存在）。今天的路线图必须在**两条轴上同时推进**，但推进顺序由第 2 节的商业逻辑决定：先在段3 内部把 L1 做实（对账+报表），再向段2 开门（接口）。

━━━ 4. ADR / 文档依据（读真实文档）━━━

**域知识.md（MallSenseAI PRD 侧，今天的第一依据）：**
- 「暂不推广但维护运行」+「误报率未持续优化是市场落地难度大的核心原因」→ Sprint 1 的商业理由
- 「火灾检测漏报率未量化（安全+法律责任风险）」「无人脸脱敏（PIPL 合规风险）」「无 LICENSE」→ Sprint 1 的风险清单
- 「封闭系统有意为之…未来 P1 评估是否暴露 `safety.alert.query`」→ Sprint 3 的能力选择直接引用这条（query 是拉不是推，不破坏秒级告警直发链路）
- 「不做什么：客流统计」→ L2 不进前3 Sprint 的边界声明依据（W13-D3 已登记需重新裁决，但裁决结论是"进路线图 P2，不进前3"）

**ADR-003（Capability × Industry 正交 facet）**：Sprint 3 注册第一个 vision capability 时，ID 必须行业无关（`lnkchat.safety.alert.query@v1`，不是 `mall.alert.query`）。Domain 拆分沿用 Day5 遗留裁决：vision（KPI 查询）与 safety（告警查询）两个域。

**ADR-004（LnkChat AI Vision 命名）**：Sprint 3 的 Application 元数据页沿用已冻结命名（注意 Day5 发现：示例文件还是 `langchat.vision.*` 旧前缀，未跟上 ADR-008，集成时同步修正）。

**ADR-007（三段式架构链）**：路线图三步与三段的对位——Sprint 1/2 全在段3 内部（Vision Runtime 自身债务），Sprint 3 才触碰段2（catalog）。**段内优化先于跨段集成**，因为跨段接口冻结的前提是段内输出稳定（KPI 口径都还没定，query 能力冻结什么？）。

**v2-strategy（LnkChat 平台侧）**：Day5 已确认 catalog.py 注册表是 import 时静态内存 dict、`runtime_binding={}` 空——「注册表数据化（DB-backed catalog + provider 自注册）」进 Sprint 3 的平台侧任务（这是集成债，债主在平台侧）。

━━━ 5. 代码验证（只看关键结构）━━━

Inventory 的"现状"栏今天逐条过了代码，关键证据：

**① 四检测器 = L1 全部家当**（`backend/app/detectors/integration.py`）：
```python
_DETECTOR_CLASSES.update({
    "debris":            DebrisDetector,        # YOLO 11n 障碍物
    "obstruction_world": YOLOWorldDetector,     # YOLO-World v8s+CLIP 零样本
    "fire_smoke":        FireSmokeDetector,     # 火灾烟雾
    "floor_cleanliness": FloorCleanlinessDetector,  # 基线图像对比
})
```
注册表按 `detector_type` 字符串分发，模型热重载经 `detector_configs` 表 + ConfigWatcher（10s 轮询）双进程收敛——**模型管理已产品化，这是 Inventory 平台工程栏的强项**。

**② 五模板规则包 = L1→L4 的规则化出口**（`backend/app/rules/standard_templates.py`）：通道拥堵-停留超时/面积超限/禁入区占用 + 火灾烟雾 + 地面脏污。幂等种子（skip existing，never overwrite）。**注意：停留超时/面积超限是"伪时序"——用截图间隔模拟持续存在，L2 缺失的代偿**（W13-D1 已论证）。

**③ alert lifecycle = 免费监督标签**（AGENTS.md 告警生命周期）：`pending → confirmed → resolved / false_positive`，工单在 confirm 时自动创建。**这行流程图就是 Sprint 1 的全部数据来源**——误报率量化不需要新采集，需要的是把 lifecycle 标签按 摄像头×规则×日 聚合（Sprint 2 的表结构顺带就把 Sprint 1 的报表做了）。

**④ 工程底座**：backend/tests 51 个测试文件（AGENTS.md 记 510 用例）+ 37 Playwright e2e + GitHub Actions 三段 CI（pytest + vue-tsc/build + e2e）；openspec/specs 29 项规格（检测/告警/规则/通知/部署全覆盖）。**单商场部署无多租户**（域知识.md）——Sprint 范围刻意不含多租户（单产品线策略，等集成后由 LnkChat 侧承担多租户）。

━━━ 6. 交付物一：Vision Capability Inventory ━━━

### 6.1 能力清单（五层 × 真实状态）

| # | 能力 | 层 | 现状 | 代码证据 | 路线图位置 |
|---|------|----|------|----------|-----------|
| 1 | 障碍物检测（YOLO 11n） | L1 | ✅ 产品化 | debris.py + 3 个通道拥堵模板 | 已有（S1 度量对象） |
| 2 | 零样本自定义检测（YOLO-World） | L1 | ✅ 产品化 | yolo_world.py（含 CLIP device patch） | 已有（S1 度量对象） |
| 3 | 火灾烟雾检测 | L1 | ⚠️ 产品化但漏报未量化 | fire_smoke.py + supplemental spec | **S1 专项** |
| 4 | 地面脏污检测（基线对比） | L1 | ✅ 产品化 | floor_cleanliness.py + 独立 spec | 已有 |
| 5 | OCR / 分割 | L1 | ❌ 无 | —（雷达 Assess：SAM2） | 不进前3 |
| 6 | 目标跟踪 Tracking | L2 | ❌ 无（截图模式） | scheduler.py 定时截图 | 不进前3（架构换代） |
| 7 | 场景统计（计数/热区/排队） | L3 | ❌ 无（依赖 L2） | — | P2（商业重启线） |
| 8 | 安全事件运营化 | L4 | 🟡 雏形：事件级流水有，聚合无 | alerts + work_orders + dashboard | **S2 聚合层** |
| 9 | 运营 KPI / 指标口径 | L4 | ❌ 无 | —（detection_events 无聚合） | **S2 口径层** |
| 10 | Vision Agent（推理/日报） | L5 | ❌ 无（裁决：推理住 LnkChat） | —（Day4/5 结论） | S3 之后 |
| 11 | Capability 出口 | 横切 | ❌ 无（封闭系统） | 域知识.md 边界声明 | **S3 第一个** |
| 12 | 模型管理（上传/热重载） | 平台 | ✅ 产品化 | models API + ConfigWatcher | 已有 |
| 13 | 告警治理（冷却/抑制/生命周期） | 平台 | ✅ 产品化 | CooldownTracker + suppressions | 已有 |
| 14 | 通知路由（企微/短信/邮件） | 平台 | ✅ 产品化 | NotificationGroup + severity 过滤 | 已有 |
| 15 | 误报率度量 | 平台 | ❌ **无（本 Inventory 最大 Gap）** | lifecycle 标签在、无人聚合 | **S1 核心** |

### 6.2 负资产栏（Inventory 必须盘负债）

| 负债 | 风险等级 | 处置 |
|------|---------|------|
| 火灾漏报率未量化 | 🔴 安全+法律 | S1 专项 |
| 误报率未量化 | 🔴 商业（推广卡点） | S1 核心 |
| 无人脸脱敏 | 🔴 PIPL 合规 | S1 方案 + S2 落地 |
| 无 LICENSE | 🟡 版权不明 | S1 行政项（半天） |
| 单人开发 bus factor | 🟡 组织 | S3 集成后由平台侧分担 |
| 无多租户 | 🟢 单产品线策略 | 刻意不做，集成后 LnkChat 承担 |

**Inventory 结论一句话：L1 是资产满格层，L4 是雏形层，"度量"是零资产且全系统依赖的负资产层——路线图第一步由此决定。**

━━━ 7. 交付物二：Vision Technology Radar ━━━

四环制（Adopt 采纳 / Trial 试用 / Assess 评估 / Hold 观望），状态以代码事实为准：

```
                    ADOPT（在产品里跑）
                 ┌─────────────────────┐
                 │ YOLO 11n（障碍物）    │
                 │ YOLO-World v8s+CLIP  │
                 │ 基线图像对比（脏污）   │
                 │ CPU-only 部署策略     │
                 └─────────────────────┘
              TRIAL（正在验证）★空环★
                 ┌─────────────────────┐
                 │    （无任何项目）      │ ← 今天最大的发现
                 └─────────────────────┘
              ASSESS（待评估）
                 ┌─────────────────────┐
                 │ RT-DETR（精度↑速度↓） │
                 │ SAM2（像素级分割，     │
                 │   可升级脏污检测）     │
                 │ GroundingDINO        │
                 │   （开放词表替代）     │
                 └─────────────────────┘
              HOLD（长期观望，等触发条件）
                 ┌─────────────────────┐
                 │ ByteTrack/BoT-SORT   │ ← 触发：视频流架构启动
                 │ ReID（跨摄像头）      │
                 │ Pose（跌倒/行为）     │
                 │ VLM（场景理解）       │
                 │ Vision Agent 框架    │
                 └─────────────────────┘
```

**雷达的三个读数：**

1. **Trial 环是空的。** 这不是"没有值得试的技术"，是**技术管道断了**——评估（Assess）和采纳（Adopt）之间没有正在进行的验证。Sprint 1 的度量管线本质上是给雷达装上 Trial 环：PPV 基线一立，RT-DETR/SAM2 任何升级都能用同一把尺子 A/B（Trial 环的工作方式）。
2. **Adopt 环全是推理侧轻技术 + 一条部署策略。** CPU-only PyTorch 省下的 1.8GB 镜像和 <500ms 单帧延迟，是"商场服务器无 GPU"这个约束逼出来的正确决策——雷达记的不只是模型，还有**被现实验证过的部署约束**。
3. **Hold 环的触发条件全是架构事件而非时间表。** ByteTrack 等"视频流架构启动"，VLM 等"capability 集成完成"（推理层在平台侧，W13-D4 裁决）。技术雷达的 Hold 环写着路线图的依赖关系。

━━━ 8. 交付物三：演进路线图（前3 Sprint）+ 与替代排序比较 ━━━

### 8.1 前3 Sprint（裁决结果）

**Sprint 1「立尺子」：度量与合规地基（段3 内部，纯还债）**
- PPV/误报度量管线：按 摄像头×规则×日 聚合 lifecycle 标签（confirmed / false_positive），输出误报率基线报告 = 恢复推广的 P0 依据（域知识.md 原话的兑现）
- 火灾烟雾漏报率专项：抽样评估（夜间/早期烟雾场景），量化给出置信区间而不是单点数
- 人脸脱敏方案定稿（blur 进检测管线，detector 框架现成）+ LICENSE 补齐
- 交付判据：能回答"系统整体 PPV 多少、火灾漏报率上限多少"两个数字，各带置信区间

**Sprint 2「出报表」：L4 日级聚合 + 指标口径层（段3 内部，L4 雏形→成型）**
- detection_events → 日级 KPI 表（告警数/确认数/误报数/PPV/MTTD/环比）
- 指标口径层：W13-D3 的口径结论固化（采样偏差声明、口径责任字段）——**KPI 表同时是 S1 度量管线的持久化形态**，两个 Sprint 是同一条数据流的"先手工跑通、再固化为表"
- 人脸脱敏落地进管线
- 交付判据：dashboard 从事件流水升级为运营 KPI 页；`lnkchat.vision.kpi.query@v1` 的返回结构草案定型（为 S3 冻结契约做数据准备）

**Sprint 3「开接口」：第一个 Capability 打包（跨段，兑现 Day5 三份纸）**
- 平台侧：catalog 注册表数据化（DB-backed + provider 自注册，Day5 遗留 P0 集成债）
- MallSenseAI 侧：暴露 `lnkchat.safety.alert.query@v1`（只读、拉模式、域知识.md P1 评估项——**拉不破坏秒级告警直发的实时性边界**）+ KPI 查询能力（数据来自 S2）
- Connector service account + 证据 digest 对齐（Day4 前置件）
- 交付判据：LnkChat 数字员工能回答"昨天 B1 消防通道告警几起、确认几起、误报几起"——**这句话验收的是三段链全程，不是单侧 API**

### 8.2 与替代排序比较（为什么不是另外两种排法）

| 排序策略 | 前3 Sprint 会是 | 为什么否决 |
|----------|----------------|-----------|
| **技术驱动**（补断层优先） | L2 Tracking → L3 场景统计 → L4 聚合 | 架构换代（截图→视频流）投入最大，但商业上等于是**新开产品线**；且没有 S1 的尺子，Tracking 的 PPV 无从度量——先造新车再发明速度表 |
| **价值驱动**（ROI 最高优先） | 客流产品线（W12-D5 ROI 冠军）→ KPI → 集成 | 客流 ROI 高但**门槛也高**（摄像头改造+物业付费意愿，域知识.md 原话）；已部署商场的告警增值是**口袋里的钱**，新商业线是**地平线上的钱** |
| **风险驱动（本路线图）** | 立尺子 → 出报表 → 开接口 | 每步是上一步的必要条件：没有尺子没法优化误报（S1），没有 KPI 表契约无物可冻结（S2→S3），没有接口 L5/L2 全是空中楼阁（S3 之后） |

**裁决逻辑一句话：技术驱动看能力地图的空洞，价值驱动看商业地图的高地，风险驱动看依赖链的根——前3 Sprint 必须从根开始，因为根上的两笔债（度量+合规）不还，后面所有投入都在沙地上。**

━━━ 9. 架构师思考题 ━━━

① **Sprint 1 的尺子有自证偏差吗？** false_positive 标签是运维人员打的——没被打标的告警（未处理/漏看）会系统性低估误报率。作为 CTO 你如何设计度量口径，让"PPV=78%"这句话经得起客户质询？（提示：分子分母的排除规则要进指标口径层，这正是 S2 的字段）

② **S3 暴露 `safety.alert.query` 后，告警数据有了两个消费方**（MallSenseAI 前端 + LnkChat 数字员工）。当两边看到的数字不一致时（比如聚合口径 vs 实时流水），谁是对的？这个问题的架构学名是什么？（提示：W13-D3 的"口径责任"，以及为什么 S2 要把口径声明做成数据而不是文档）

③ **如果 S1 度量跑出来火灾漏报率高到不可接受**（比如 >15%），路线图要不要变？（这不是操作题——考的是"度量结果驱动重排路线图"的机制：雷达四环里哪个环该动、S2/S3 是推迟还是照走）

━━━ 10. 我的理解变化 + 明日连接 ━━━

**以前以为**：能力盘点（Inventory）是列清单——把有的没的写下来打勾。**现在知道**：盘点的主产品不是清单，是**三个发现**——① 最大 Gap 藏在平台工程栏（度量，#15），不在五层模型的任何一层；② 雷达 Trial 空环暴露的是"技术管道断裂"这个组织事实，不是技术事实；③ 负资产栏决定路线图第一步，资产栏决定第三步。**清单是静态账本，盘点是动态裁决的输入。**

**以前以为**：路线图排序是"重要性排序"（谁重要谁先做）。**现在知道**：是**依赖链排序 + 风险贴现**——对账→报表→开接口这个 ERP 老兵的肌肉记忆，本质是"每一步为下一步生产必要条件"。客流 ROI 再高，也是第三步之后的事，因为它的度量、它的商业重启、它的架构换代，全都依赖根上的两笔债先还清。

**Semantic Layer 位置**：今天的三个交付物挂在 Ontology → Domain Model → Capability → Skill 链的**两端**——Inventory 盘的是 Domain Model 的视觉侧实态（段3），Roadmap 的 S3 是 Capability 链第一次真实闭合（描述符从纸面注册进 catalog）。`lnkchat.safety.alert.query@v1` 将是这条链上第一个**视觉域**节点。

**明日连接（Day 7 · 周日）**：🔄 最终 Virtual CTO Review——Week 12-13 两周总复盘 + MallSenseAI × LnkChat 集成评估。五维评分 + ADR Health Check（重点复查：ADR-004 示例前缀未同步 ADR-008、域知识.md「不做客流统计」边界声明与 W12-D5 ROI 结论的冲突裁决）+ 路线图签发（今天的三件套送审）。

━━━ 📝 Daily Engineering Log ━━━

- **新增**：Vision Capability Inventory（15 项能力×6 项负资产，全部经代码验证）；Technology Radar 四环版（发现 Trial 空环）；演进路线图前3 Sprint（立尺子→出报表→开接口）
- **确认**：alert lifecycle 标签 = 免费监督标签（AGENTS.md 流程图 + lifecycle 代码路径）；29 项 OpenSpec 规格；51 测试文件/510 用例
- **决策**：① 前3 Sprint 不含任何新检测能力（L2/L3 推迟，理由=依赖链排序）；② S3 能力选 `safety.alert.query`（拉模式不破坏实时性边界，引用域知识.md P1 评估条目）；③ 注册表数据化归平台侧 Sprint 3（集成债债主在平台）
- **遗留**：effects 语义裁决（Day5 悬置，catalog 只有单字段，拆 effects+cost_class 的提案未落 ADR）；S1 度量口径的自证偏差设计（今天思考题①，进 S1 任务）
- **技术债登记**：ADR-004 示例 `langchat.vision.*` 前缀未同步 ADR-008（D5 发现，S3 顺带修）
- **下一步**：D7 Virtual CTO Review（两周总复盘+路线图签发）
