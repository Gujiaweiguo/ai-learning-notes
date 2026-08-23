# 🧱 LangChat 心智模型 | Week13-Day1
# 📌 People Analytics：客流/密度/停留/热区/轨迹 —— 客流统计为什么不是 Detection 而是 Tracking？

> 术语说明：LangChat 已按 ADR-008 更名为 LnkChat，本文按 W12-D7 决策使用新名（首现标注），历史引用保持原文。

━━━ 1. 今日核心问题 ━━━

**客流统计为什么不是 Detection 而是 Tracking？**

表面看，"数人头"是检测器最擅长的事——每帧框出人，加起来不就是客流吗？
今天的核心论断：**计数是事件，不是状态**。客流的本质是"穿越事件流的累积"（谁在什么时候跨过了入口线），不是"某帧画面里有几个人"。Detection 回答的是状态问题（这一帧里有谁），Tracking 回答的是事件问题（谁进来了、谁走了、待了多久）。状态快照堆不出事件流水。

━━━ 2. 人话解释（用 26 年 ERP 经验讲）━━━

Jason，这个你在 ERP 里见过一模一样的东西：

- **Detection = 库存快照**（stock snapshot）：每天盘一次库，知道当天账上有多少货。
- **Tracking = 出入库流水**（transaction log）：每一笔进货/出货都有单据号、时间戳、可追溯。

月底库存对，不代表流水对——因为没有单据号的库存变动就是"盘盈盘亏"，你不知道是丢了货还是数错了。客流同理：

- 摄像头每帧检测到"8 个人" = 一张快照；
- 快照之间没有单据号（track ID），就分不清"同一个人又待了一帧"还是"又来了一个人"。

**没有单据号的计数，本质上是盘盈盘亏，不是账。** 商管要的客流报表是账：进店人数、平均停留、进店率 = 这些全是流水派生指标，不是快照派生指标。

还有一层 ERP 直觉：快照是无状态的（每次盘点独立），流水是有状态的（单据要连号）。这就是为什么上周 D4 结论说 L2 必须是独立管线——有状态计算和无状态计算的部署契约根本不同，跟你们把 OLTP 和对账系统分开是同一个道理。

━━━ 3. LangChat（LnkChat）架构位置 ━━━

放在 Vision Capability 五层模型里看，今天的位置：

```
L1  Image Understanding     — Detection / OCR / Segmentation        ← MallSenseAI 现在站这里
L2  Video Understanding     — Tracking / MOT / Video Analytics      ← ★ 今天的主角
L3  Scene Understanding     — Counting / Heatmap / Crowd / Queue    ← People Analytics 的指标层
L4  Business Intelligence   — 客流 KPI / 安全事件 / 运营指标        ← People Analytics 的产出层
L5  Vision Agent            — 自动分析 / 推理 / 建议 / 日报
```

关键结构事实：**People Analytics 横跨 L2-L4，但不是均匀依赖 L2**。今天要建立的细分认知：五个经典指标（客流/密度/停留/热区/轨迹）对 Tracking 的依赖度是一条谱系，不是一刀切。这条谱系决定了"哪些指标可以在现有 L1 管线上退化实现（MallSenseAI 的 duration/area 统计已是先例），哪些指标必须等 L2 管线"。

在 LangChat 平台侧的位置：People Analytics 的产出（客流 KPI）是未来 `people.flow.report` / `footfall.query` 这类 Capability 的规格输入——能力地图最终要落成 Capability 契约，才能被数字员工消费。

━━━ 4. ADR / 战略文档依据 ━━━

**① 域知识.md「不做什么」第一条**：客流统计 / 访问者分析（不是客流分析系统）。
这是主动边界不是能力缺陷（W12-D6 已定稿此判定）。但注意边界的措辞精度：MallSenseAI 排除的是**产品定位**（不做客流分析系统），不是**能力依赖**——如果未来 LnkChat 平台的数字员工要消费客流 KPI，MallSenseAI 的摄像头资产就是数据源，届时按 ADR-004 的目标态路径走 Capability 暴露。

**② 域知识.md「不做什么」第二条**：人脸识别 / 身份追踪（隐私合规）。
这里藏着一个今天必须澄清的概念混淆：**tracking ≠ 身份追踪**。
- ByteTrack/BoT-SORT 的 tracklet ID 是**帧间几何关联**（"这个移动的 blob 是同一个东西"），完全匿名，生命周期只有几秒；
- 人脸/ReID 的身份识别是**实名跨摄像头关联**（"这是张三"），才踩 PIPL 红线。
把这两条线分开，"不做人脸识别"就**不必然**推出"不能做客流"。视频内的匿名 track ID 做客流统计，合规等级和检测框本身相同（都是"画面里有人"级别的事实）。当然，工程上要遵守无人脸脱敏现状的同等审慎——track ID 不得与任何实名数据 join。

**③ ADR-004 目标态**（W12-D7 已核实：三项能力代码为零）：客流/商品结构化分析、零售 POS/CRM 事件联动、Channel 回传洞察。今天的 People Analytics 指标谱系，就是给这三项目标态里"客流分析"画需求边界——它值多少钱、缺哪层、缺多大。

**④ OpenSpec 事实**：29 个 spec 无 video/stream/tracking 字样（W12-D5 硬判据），L2 缺失在规格层也成立。

━━━ 5. 代码验证（只看关键结构）━━━

三个代码事实，确认"当前系统没有 Tracking 的立足点"：

**事实一：`DetectorType` 枚举里没有人的位置**（`backend/app/models/entities.py:71`）：
```python
class DetectorType(str, enum.Enum):
    image_compare = "image_compare"
    yolo = "yolo"
    blue_box = "blue_box"
```
检测器类型空间里连 person 类别都没有（现有 YOLO 类检测的是障碍物/烟火），更没有 tracker 类型。Tracking 不是"加一个检测器"能解决的——它不在 `detectors/` 的插件位上。

**事实二：规则引擎的"时长"是 ROI 级，不是对象级**（`backend/app/rules/engine.py:52`）：
```python
class ObstructionRuleEngine:
    """Stateless evaluator for obstruction duration, area, and forbidden-zone rules."""
    # cooldown_state: 负键存 first-seen 时间戳（规则×ROI 维度）
```
`_evaluate_obstruction_duration` 的计时主体是 **rule_id × roi_id** 的 first-seen 到现在——即"这个区域被连续占用多久"，不是"这个人待了多久"。这就是 L3 退化统计的代码形态：无 ID 时，"人的停留时间"退化为"区域的占用时长"。单人单事件（走廊一个箱子）两者等价；连续人流（门口一直有人）时后者 ≈ 全天，完全失真。

**事实三：管线是逐帧无状态的**（`workers/pipeline.py` 模块 docstring）：
```
Detection pipeline — capture → detect → evaluate rules → create alerts
```
五站链路没有 track 站，每帧独立走完。跨帧状态只存在于 cooldown_tracker（告警去重的运营状态），不存在于感知层。**这与 LangChat "Runtime 无状态"的原则同构**——但 Tracking 恰恰是感知层的"有状态计算"，所以 L2 必须自带轨迹状态管理，作为独立数据契约的新管线（W12-D4 结论的代码层印证）。

━━━ 6. 商业地产映射（MI CRE 场景）━━━

五个 People Analytics 指标 → 商管的钱在哪里：

| 指标 | MI CRE 用途 | 商业价值形态 | 现状获取方式 |
|---|---|---|---|
| **客流（计数）** | 进店率、转化率（客流×POS）、租户业绩评估、租金定价模型 | 收入增量（租金逻辑） | 闸机/红外对射/WiFi 探针——侵入式或粗粒度 |
| **密度** | 高峰限流、聚集预警、空调/照明调度 | 风险规避+能耗优化 | 人工巡检 |
| **停留时间** | 租户吸引力指标、橱窗/陈列效果评估 | 收入增量（选址逻辑） | 几乎无法获取 |
| **热区** | 动线分析、铺位价值梯度、冷区招商调改 | 收入增量（租金逻辑） | 极少商场做 |
| **轨迹** | 主动线 vs 次动线验证、消防通道占用与客流的冲突分析 | 运营决策 | 无 |

LangChat（LnkChat）侧的映射链：
```
视觉 tracklet（匿名轨迹） → people.flow.report（Capability） → 客流数字员工（SkillRelease）
→ 日报/招商答辩材料（Channel 回传） → 招商/运营（数字员工使用者）
```
对应关系与既有心智模型完全同构：`Capability → lease.contract.query` 之于 MI ERP，就是 `people.flow.report` 之于视觉管线。**客户不为轨迹付费，客户为"铺位 B12 的周客流环比跌了 15%，建议降租续约或调改"付费**——L2 的数据要走到 L4 的 KPI 叙事才有商业形态。

沉没成本叙事（W12-D5 ROI 排序的延续）：21 路已部署摄像头是现成资产，视觉客流 = 零新增硬件的 KPI 生产。但要诚实：这属于资本预算科目的战略行（需 L2 管线 + C 档硬件），不是费用预算的当期行。

━━━ 7. 与传统方案比较 ━━━

**方案 A：红外对射/闸机（传统客流硬件）**
单点精确、成熟可靠；但只能数线不能看区，无停留/热区/轨迹，每店新增硬件成本，且闸机改变顾客动线体验。

**方案 B：Detection + 帧累积（无 ID 的"假客流"）**
零改造（现有 L1 管线直接加人检测类别），但有三个系统性偏差：
1. **慢行者过计数**：person-frames ÷ 帧率 ≠ 人数，停留越久计数越膨胀（W12-D6 实验已量化：平均停留 80 帧 = 80 倍过计数）；
2. **静态误报线性放大**：广告画上的假人、坐一下午的保安，每帧都被数；
3. **无方向性**：进和出分不开，净客流算不出。
它只在"密度/热区"这类**累积型指标**上近似可用（详见第 9 段的谱系）。

**方案 C：Tracking（ByteTrack/BoT-SORT + 检测器）**
检测框经卡尔曼滤波 + IoU/外观关联变成带 ID 的轨迹，五个指标全部可算，进出方向、停留、轨迹一次解决。代价：
1. 必须视频流/高帧率（截图模式 1 帧/5s 的间隔下，人已移动数米，IoU 关联失效——这就是 W12-D2 "为什么当前是定时截图"问题在 L2 的投影）；
2. 感知层引入有状态计算（轨迹缓冲区、ID 生命周期管理），部署契约与无状态检测完全不同；
3. ID 切换误差（W12-D6 实测 ~7%）直接转化为计数误差。

**选型结论**（延续 W12-D7 战略）：不因 People Analytics 的商业诱惑改变"不爬 L2"的主战线——L2 等场景饱和 + 算力预算到位后作为独立管线启动。但今天把"假客流"的偏差机制写清楚，是为了将来有销售拿方案 B 忽悠时，你能一句话拆穿：**没有单据号的库存不是账**。

━━━ 8. 架构师思考题 ━━━

商场中庭一个广角摄像头，运营同时提两个需求：
- **需求甲**：实时密度告警（区域内 >50 人触发限流广播）
- **需求乙**：月度客流报表（进/出人数、平均停留，进招商会）

问题：
1. 甲和乙分别最低需要五层模型的哪几层？为什么甲可以退化到 L1（帧级人数估计）而乙不能？（提示：甲问的是状态，乙问的是事件）
2. 如果只能给一个指标上 SLA 承诺，你选哪个？另一个用什么措辞写进合同？（回忆 W12-D5 的决策：火灾检测卖"降低概率"不卖"消除风险"）
3. 视觉 track ID 与 MI CRM 的会员 ID，在什么情况下会被业务方要求 join？你作为架构师拿什么挡？（域知识"无人脸脱敏"现状 + PIPL）

━━━ 9. 我的理解变化 ━━━

**以前以为**："不做人脸识别"意味着 MallSenseAI 做不了客流——合规一条线堵死。
**现在知道**：匿名 tracklet 与实名身份是两条合规线，帧间几何关联不踩 PIPL。堵死客流的是产品定位和 L2 缺失，不是隐私法。

**以前以为**：People Analytics 五个指标是一体的，要么全有要么全无，都等 L2。
**现在知道**：五个指标对 ID 的依赖度是一条谱系——
- 密度、热区：**累积型指标**，帧级检测叠加即可近似（误差来自静态误报，不来自无 ID 本身）；
- 客流（过线计数）、停留时间：**事件型/持续型指标**，必须有 ID 才能定义；
- 轨迹：ID 就是指标本身。
这条谱系解释了 MallSenseAI 的 duration/area 规则为什么"能用"（单人单事件的累积型场景），也划清了它在哪里失真（连续人流的事件型场景）。

**以前以为**：Tracking 只是 Detection 的"升级版"，同一根管线上加个模块。
**现在知道**：Tracking 是感知层从无状态到有状态的**范式切换**（快照→流水），数据契约、部署形态、误差模型全变——这和 LangChat 把 Runtime 设计成无状态、把状态外置是同一个架构决策的正反两面。

━━━ 10. 明日连接 + Semantic Layer 位置 ━━━

**明日（Day2）**：Security Analytics——入侵/越界/跌倒/烟火/危险区域/离岗，核心问题是"安全场景为什么误报率是核心挑战"。今天的谱系明天直接复用：越界（tripwire）是 line-crossing——和客流过线**同一个几何原语**，只是语义从"记一笔账"变成"拉一次警报"；而"区域内出现人"的入侵检测有 L1 退化形态。误报率如何通过谱系位置反推（累积型指标的静态误报怎么压），是明天的主菜。

**Semantic Layer 位置**：
```
Ontology → Domain Model → Capability → Skill
                        ↑
        people.flow.report / crowd.density.query（未来 Capability 规格）
        今天定义的"五指标 × ID 依赖度谱系"= 这两个 Capability 的需求边界
```
今天建立的是**能力地图→能力契约**之间最关键的中间层：不是"能检测什么"（L1 的语言），而是"能承诺什么指标、以什么精度、依赖哪层数据"（Capability 的语言）。这条翻译链练熟了，MallSenseAI 的任何新场景都能机械化地走一遍。

---
*生成于 2026-08-24 06:00 · W13-D1 · 信息源：MallSenseAI AGENTS.md / workers/pipeline.py / backend/app/rules/engine.py / backend/app/models/entities.py / 域知识.md / ADR-004 / ADR-008*
