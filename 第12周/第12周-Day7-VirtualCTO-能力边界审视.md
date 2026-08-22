# 🧱 Vision Intelligence 心智模型 | Week12-Day7
# 🔄 Virtual CTO Review：MallSenseAI 能力边界审视 + 五维评分

> **日期**：2026-08-23（周日）
> **今日角色**：Virtual CTO — Vision Intelligence 阶段（Week 12-13）第一次周评审
> **本周主题**：Vision Intelligence 全景 + MallSenseAI 现状
> **评审范围**：本周 7 天学习产出（Day1-Day6 + 本文）× MallSenseAI 代码事实复核 × ADR-008 冲击波（8/21 本周内发生）

---

## 目录

1. [本周理解进度](#1-本周理解进度)
2. [本周新增认知清单](#2-本周新增认知清单)
3. [定位一致性检查：是否符合 v2 Charter](#3-定位一致性检查)
4. [ADR Health Check：ADR-008 冲击波](#4-adr-health-check)
5. [MallSenseAI 能力边界审视（本周重点）](#5-mallsenseai-能力边界审视)
6. [五维评分（MallSenseAI 首评）](#6-五维评分)
7. [下周建议（Week 13）](#7-下周建议)

---

## 1. 本周理解进度

### 理解进度：8.0 / 10（Vision Intelligence 新阶段起步分）

| 天 | 任务 | 完成度 | 关键产出 |
|---|------|--------|---------|
| D1 | Vision Intelligence 全景 | ✅ 100% | 五层模型（L1-L5）确立；"为什么 MallSenseAI 不是 CV 项目"的定位答案 |
| D2 | 仓库精读：截图 vs 视频流 | ✅ 100% | "定时截图是状态型场景的正确架构，不是技术妥协"这一反直觉结论 |
| D3 | Detection 体系：YOLO-World 选型 | ✅ 100% | 封闭词表 / 领域微调 / 开放词表 / 图像比对四个 L1 子格子的不可替代性 |
| D4 | Video Analytics 基线 | ✅ 100% | 截图→视频流要改的是**数据契约**（DetectionEvent 语义），不只是推理 |
| D5 | Business Scene Matrix | ✅ 100% | ROI 排序：人力替代型自动巡检 > 客流分析 > 安全扩场景 |
| D6 | ⚡ 五层图 + 场景矩阵交付 | ✅ 100% | MallSenseAI 精确坐标："窄而深的 L1（~70%）+ 踮脚够到 L3'（15%）/ L4'（20%）" |
| D7 | 🔄 Virtual CTO Review | ⏳ 本文 | 能力边界审视 + 首次五维评分 |

**为什么是 8.0 而不是更高**：MallSenseAI 代码只精读了一轮（对比 LangChat 用了整整 4 周），`workers/` 的调度细节（失败退避、TTL 上下文缓存）和 `rules/engine.py` 的完整状态机只看了结构；视觉智能竞品生态（BriefCam、Spot AI、字节火山等）只扫描了定位，没有做 LangChat D5 那种逐链路对比。这两块是 Week 13 的"干中学"素材。

**为什么是 8.0 而不是更低**：因为本周完成了一次**坐标系切换**——从 LangChat 的"平台架构视角"切到"行业能力包视角"，而且切换当天（D1）就建立了五层模型这个稳定的分类框架，之后每一天都在往同一个框架里填格子，没有推倒重来。框架先行的学习效率远高于漫游式学习。

---

## 2. 本周新增认知清单

| # | 新认知 | 来源 | 类型 |
|---|--------|------|------|
| W12-01 | **五层模型是科目结构，不是楼梯**——L3 客流 KPI 记账必须引用 L2 Tracking 的凭证，但状态型场景的账可以 L1 直接记到 L4（检测→工单），跳过 L2。楼梯思维做项目十年还在 L2，科目思维做产品第一年记到 L4 | D1/D6 | 认知翻转 |
| W12-02 | **MallSenseAI 不是"低级 L1 系统"，是"窄而深的 L1 + 退化形态的 L3 + 雏形的 L4"**——坐标定错，路线图就错（会去急着补 L2 视频流） | D6 | 精确定位 |
| W12-03 | **定时截图对状态型场景是充分统计量**——通道占用/地面脏污/消防通道是"状态"（持续存在），30 秒采样必然命中；视频流只对"事件型场景"（跌倒、打架、抽烟）是必需品 | D2 | 反直觉结论 |
| W12-04 | **YOLO-World 零样本检测 = Capability 的运行时可配置性**——改提示文字就改检测能力，这是"规则引擎"级别的灵活性，不是"模型训练"级别的沉重 | D3 | 架构含义 |
| W12-05 | **截图→视频流的真正成本在数据契约**：DetectionEvent 从"状态快照"变"事件流"后，cooldown、告警去重、工单关联的语义全部重定义；GPU 只是账单问题，语义漂移才是架构问题 | D4 | Gap 发现 |
| W12-06 | **告警→工单→resolved 闭环是 MallSenseAI 真正的护城河**，检测模型反而是可替换商品（YOLO 11n 是最小的那种）。闭环让"人力替代"可审计，这是 ROI 分子 | D2/D5 | 价值判断 |
| W12-07 | **MallSenseAI 的 510 后端测试 + 37 e2e + 全链路 CI**——这是 LangChat 代码库里不存在的工程纪律，行业能力包的代码健康度反而高于平台本体 | D2 | 事实发现 |
| W12-08 | **ADR-008（8/21）：langchat → lnkchat 项目整体改名**，部分修订 ADR-002/004/005；品牌层级结构不变，产品名 LangChat → LnkChat。本周内发生的 P0 级品牌事件 | 本周扫描 | P0 事件 |

---

## 3. 定位一致性检查

### MallSenseAI 作为"行业能力包"的定位（ADR-004 原文口径）

ADR-004（2026-07-19，accepted）的核心决策：`MallSenseAI` 对外更名 `LangChat AI Vision`（经 ADR-008 现为 `LnkChat AI Vision`），行业属性（Mall）下沉到 Application 元数据的 `industries` 字段，**不重写底层代码模块名**。

本周逐条核对代码事实：

| ADR-004 的承诺 | 代码事实 | 判定 |
|---|---|---|
| 视觉识别能力组合 | `detectors/` 四检测器：YOLO 11n（杂物）/ D-Fire（烟火）/ YOLO-World（零样本）/ 图像比对（地面脏污）| ✅ 成立 |
| 客流/商品/行为结构化分析 | **不存在**。29 个 OpenSpec spec 无任何 people-analytics / tracking / retail 场景 | ⚠️ 文档超前于代码（这是 Week 13 D1-D3 的主题）|
| 与零售 POS/CRM 的事件联动 | **不存在**。告警只走 NotificationGroup（wecom/sms/email），无 ERP/POS 连接器 | ❌ 纯规划 |
| 通过 LangChat Channel 回传洞察 | **不存在**。MallSenseAI 有自己的 WebSocket + 通知体系，与平台 Channel 子系统零集成 | ❌ 纯规划（Week 13 D5 正面回答）|
| 不重写代码模块名 | 仓库仍名 `MallSenseAI`，数据库 `mallsenseai`，端口 5380 独立 | ✅ 严格遵守 |

**结论**：MallSenseAI 作为**独立产品**的事实基础扎实（闭环 + 测试纪律 + 模型热更新），但作为**平台行业能力包**的集成面为零。它现在是一颗"自带发动机的独立卫星"，还没接入"LnkChat 星系"的引力场。**这不是 MallSenseAI 的缺陷，而是平台侧 Connector/Capability 注册体系还没准备好的镜像**——LangChat 侧 W11-D3 已确认 Connector 是三套互不相识的子系统。两边各自完整，中间的桥还没画。

**v2 Charter 视角**：学习计划的产品关系图（LangChat 平台层 → MallSenseAI 行业层 → 商管应用层）在**战略层面**成立，在**代码层面**是目标态而非现状态。Week 13 的任务就是把这座桥设计出来。

---

## 4. ADR Health Check：ADR-008 冲击波

### 4.1 本周 P0 事件

**ADR-008：项目整体改名 langchat → lnkchat**（2026-08-21 accepted，即本周五）：

- **范围**：项目身份 / 打包 / CLI / 环境变量 / 对外契约 / 部署
- **Supersedes**：部分修订 ADR-002（品牌层级）、ADR-004（LangChat AI Vision → LnkChat AI Vision）、ADR-005（LnkChat AI X 前缀族）
- **不变量**：四级品牌层级结构不变；`MallSenseAI → LnkChat AI Vision` 的更名逻辑不变；"不重写代码模块名"原则不变
- **实施**：OpenSpec change `rename-langchat-to-lnkchat`

按学习计划的触发条件表，这属于 **P0: ADR 变化 → 立即学习**。本周 D5 当天已消化，今天正式入档。

### 4.2 全量 ADR 体检表

| ADR | 主题 | 状态 | 对 MallSenseAI 的影响 | 体检结论 |
|---|---|---|---|---|
| ADR-001 | 平台定位：企业 AI 应用平台 | accepted | 平台层定位的根基 | ✅ 健康 |
| ADR-002 | 四级品牌层级 | accepted（ADR-008 部分修订） | L4 Application 收费单元 | ✅ 健康（层级结构未动）|
| ADR-003 | Capability × Industry 正交模型 | accepted | 行业属性下沉 industries 字段的依据 | ✅ 健康（LangChat 侧的落地债不变，W11 已记录）|
| ADR-004 | MallSenseAI → AI Vision 更名 | accepted（ADR-008 部分修订） | **本周主角**：定位声明 + 更名范围 | ✅ 健康，但 §1 中"客流/POS 联动/Channel 回传"三承诺为纯规划，需在 ADR 或 roadmap 中标注"目标态"以免误导 |
| ADR-005 | LnkChat AI X 命名前缀 | accepted（ADR-008 部分修订） | MallSenseAI 对外名 = LnkChat AI Vision | ✅ 健康 |
| ADR-006 | 官网受众分层 | accepted | 无直接影响 | ✅ 健康（决策者优先原则）|
| ADR-007 | 平台架构链三层 | accepted | 能力包在三层中的位置依据 | ✅ 健康 |
| ADR-008 | langchat → lnkchat | **accepted（8/21 新增）** | 对外名再更替 | 🆕 需跟踪 OpenSpec change 的实施完成度 |
| ADR-LC-011 | DeploymentRevision 审批门 | accepted | 无直接影响 | ✅ 健康（W10 已审）|
| ADR-LC-013 | 数字员工运营聚合 | accepted | MallSenseAI 未来作为 Vision Agent 宿主的依据 | ✅ 健康（W13-D4 会用到）|

### 4.3 术语策略决定（本文生效）

1. **历史文档不追改**：v2-strategy、既有 ADR、OpenSpec 里的 `LangChat` 字样是历史事实，保留原文。
2. **新口径自 Week 13 起**：学习笔记新产出统一用 `LnkChat`（首次出现标注"原 LangChat，ADR-008 更名"）。
3. **MallSenseAI 对外名**：`LnkChat AI Vision`；仓库/数据库/端口不动（双 ADR 一致确认）。

---

## 5. MallSenseAI 能力边界审视（本周重点）

> Virtual CTO 的核心问题不是"能做什么"，是"**声明不做什么**"。边界清晰的系统才能长命；边界模糊的系统会在第一个大客户的需求面前解体。

### 5.1 三列边界表

| ✅ In-Scope（在界内，做得好）| ⚠️ Boundary（边界线上，扩张需换契约）| ❌ Out-of-Scope（界外，不该做）|
|---|---|---|
| 定时巡检型视觉检测（状态型场景）| 视频流推理（L2）：要改 DetectionEvent 数据契约 + cooldown 语义，不是"加个 FFmpeg" | 通用 CV 平台（什么都检测 = 什么都不精）|
| 告警→工单→resolved 闭环 | 客流统计（L3）：诚实路径是 ByteTrack/BoT-SORT，不是用 bbox 面积比硬算 | 模型训练平台（Model Management 是制品管理，不是训练）|
| 规则引擎（duration/area/禁入区）| 跨摄像头 ReID：需要特征库 + 隐私合规设计 | 平台层能力：Channel 通知路由、Capability 注册、治理审计——应由 LnkChat 提供 |
| 多检测器注册 + 热更新（ConfigWatcher 10s 轮询，原子换血不打断在飞检测）| VLM 场景理解（L5 前置）：算力与延迟预算需重新评估 | 自建通知渠道（已有 wecom/sms/email，接平台 Channel 即可，勿重复建设）|
| 证据链留存（detection_events 审计表 + 资产目录）| 多租户 SaaS化：当前单租户部署假设遍布代码 | |

### 5.2 边界判定准则（本周提炼，三条）

从 Day2-Day6 的分析中蒸馏出三条可复用的判定准则：

1. **状态型 vs 事件型**（D2）：问题是否存在超过一个采样周期？是 → 截图足够；否 → 需要事件流。这条准则直接决定"加场景"还是"换架构"。
2. **闭环可审计**（D6）：新能力能否接入 DetectionEvent → Alert → WorkOrder 的凭证链？能 → 扩张成本低；不能 → 它是另一个产品。
3. **人力替代 ROI**（D5）：新能力替代的是"人反复看"（高 ROI）还是"人偶尔看"（低 ROI）？前者优先。

**用这三条准则跑一遍 L2 视频流**：事件型（准则 1 说需要）✅；闭环可审计——事件流接入现有凭证链需要重定义 cooldown（准则 2 说成本高）⚠️；替代的是保安盯屏（准则 3 说 ROI 高）✅。**结论：L2 值得做，但必须作为独立数据契约的新管线，而不是在现有 snapshot 管线上打补丁**——这验证了 D4 的结论，也预告了 Week 13 路线图的拆分方式。

### 5.3 五层坐标复核（引用 D6 定稿）

```
L5  Vision Agent          ─ 空缺（0%）        ← W13-D4 设计对象
L4  Business Intelligence ─ 雏形（~20%）      告警工单闭环 + Dashboard
L3  Scene Understanding   ─ 退化形态（~15%）  duration/area 两个统计量
L2  Video Understanding   ─ 空缺（0%）        29 spec 无 video/stream/tracking
L1  Image Understanding   ─ 主阵地（~70%）    4 个子格子占 3.5 个
```

**边界审视后的战略结论**（与 D5/D6 一致，今天从 CTO 视角定稿）：

> MallSenseAI 未来 2 个季度的主战场是 **L1 内换格子**（用 YOLO-World 零样本 + 图像比对快速覆盖新状态型场景）和 **L4 补全**（工单闭环运营指标化），**不是**爬 L2。L2 视频流是独立管线投资，等 L1 场景矩阵饱和 + 算力预算到位再启动。

---

## 6. 五维评分

### 6.1 MallSenseAI 首次五维评分

| 维度 | 评分 | 理由 |
|---|---|---|
| **Architecture Quality** | **7.0** | 分层清晰：detectors / rules / alerts / workers 四模块解耦，BaseDetector ABC + DetectorRegistry + ConfigWatcher 热更新是同类项目少见的工程亮点；pipeline 单向流（capture→detect→persist→rule→alert）无环。扣分：`legacy/` 整目录共存（有边界但仍是双系统心智负担）、`shared/` 只有 2 个工具文件（跨切面层过薄）|
| **Code Health** | **7.5** | 510 后端测试 + 37 Playwright e2e + CI 三段流水线（pytest / vue-tsc+build / e2e）——**高于 LangChat 本体**。扣分：Camera.password_hash 明文存储（有注释说明是 RTSP 认证所需，但属已知安全债）、mock:// 相机逻辑混在生产捕获路径里（测试便利 vs 生产纯净的折中）|
| **ADR Consistency** | **6.0** | 正向：ADR-004"不重写代码模块名"被 100% 遵守（仓库/库名/端口未动）。负向：ADR-004 声明的客流分析/POS 联动/Channel 回传三项能力代码为零——**ADR 与代码的最大落差恰好全部压在"能力包集成"这一件事上**；且 MallSenseAI 自身无 ADR 体系（29 个 OpenSpec spec 承担了部分决策记录职能，但无 status/supersede 链）|
| **Technical Debt** | **7.0** | 债务清单**短且可见**：legacy/ 目录（有意的过渡债，边界清晰）、明文密码（已知已知）、无租户假设（已知已知）。相比 LangChat 的术语重叠债 + 三套平行注册体系债，MallSenseAI 的债务结构简单——因为它是单人节奏演进的新系统，还没积累组织级债 |
| **Developer Experience** | **7.5** | AGENTS.md 是范本级：端口冲突提醒、共享 postgres16 容器警告、mock:// 相机协议、一键种子脚本（21 摄像头 + 场景 + 规则）、首次建库命令——新人 30 分钟可跑通全链路。扣分：前后端双语言栈的本地依赖（Node 22 + Python 3.10）对纯后端开发者有门槛 |

```
MallSenseAI 首评综合：7.05 / 10
（Architecture 7.0 + Code Health 7.5 + ADR 6.0 + TechDebt 7.0 + DX 7.5）/ 5
```

### 6.2 与 LangChat 评分趋势的对照（关键：测量口径声明）

```
                      W8     W9     W10    W11     W12(新增行)
LangChat 综合          7.2    6.8    6.8    6.4     ──（本期未复评）
MallSenseAI 综合       ──     ──     ──     ──     7.05（首评）

LangChat 五维(W11)  vs  MallSenseAI 五维(W12首评)：
Architecture Quality   7.5   vs   7.0
Code Health            6.0   vs   7.5   ← 最大反差
ADR Consistency        6.5   vs   6.0
Technical Debt         5.5   vs   7.0
Developer Experience   6.5   vs   7.5
```

**两条必须写进记录的解读**：

**① Code Health 反差（7.5 vs 6.0）是本周最重要的横向发现。** 平台本体（LangChat）的代码健康度低于挂在它下面的行业应用（MallSenseAI）。原因不神秘：MallSenseAI 是单仓库闭环演进 + 测试先行；LangChat 经历了 v1→v2 战略重构，三套平行体系是转型期的活化石。**启示：架构先进性救不了工程纪律，工程纪律也不需要架构先进性护航——两者独立计分，缺一不可。** 对 Jason 的提醒：不要因为 LangChat 的 ADR 华丽就假设它的代码可靠，也不要因为 MallSenseAI "只是应用"就低估它的工程质量——集成时的信任边界要按 Code Health 画，不按 ADR 画。

**② 7.05 是望远镜分数，声明测量偏差。** W11 复盘已确立"剪刀差"原则：评分下行是测量精度提高。MallSenseAI 本周只精读一轮，相当于 W8 时对 LangChat 的 7.2。**按 LangChat 的下修规律（4 周下探 0.8），MallSenseAI 的"内窥镜分数"大概率在 6.3-6.8 区间**——最可能藏问题的位置：`rules/engine.py` 状态机细节、workers 并发路径、alert_workflow 的边界条件。Week 13 深入集成路径设计时顺带验证，不专门安排审计周。

### 6.3 五维评分趋势簿记

| 周 | 对象 | 综合 | 备注 |
|---|---|---|---|
| W8 | LangChat | 7.2 | 望远镜首评 |
| W9 | LangChat | 6.8 | 对象深潜后下修 |
| W10 | LangChat | 6.8 | 治理横切持平 |
| W11 | LangChat | 6.4 | 内窥镜精度 + 4 周收官 |
| **W12** | **MallSenseAI** | **7.05** | **望远镜首评（新对象），预计 W13 后下修至 6.3-6.8** |

---

## 7. 下周建议（Week 13）

### 7.1 Week 13 路线：能力蓝图 + LnkChat 集成路径

| Day | 主题 | 与本周的连接 |
|---|---|---|
| D1 周一 | People Analytics：客流/密度/停留/热区/轨迹 | 回答 §3 发现的"客流分析纯规划"缺口怎么补；为什么客流是 Tracking 不是 Detection |
| D2 周二 | Security Analytics：入侵/越界/跌倒/烟火/离岗 | 火烟火已有（D-Fire），扩到事件型场景时撞上 L2 边界（§5 准则 1 的试金石）|
| D3 周三 | Retail Analytics：排队/货架/缺货 | L1 换格子策略的主战场 |
| D4 周四 | Vision Agent：检测→分析→推理→建议→日报 | L5 从 0 开始设计；对照 ADR-LC-013 数字员工聚合 |
| D5 周五 | **Vision Capability Architecture：集成路径** | **本周最大 Gap（§3 的三张 ❌）的正面回答——能力包怎么装进平台** |
| D6 周六 | ⚡ 交付：Vision Capability Inventory + Technology Radar + 演进路线图 | 汇总本周 + 补齐雷达采用状态 |
| D7 周日 | 🔄 最终 Virtual CTO Review：2 周总复盘 + 集成评估 | MallSenseAI 二次评分（验证 6.3-6.8 预测）|

### 7.2 给 Jason 的三条 CTO 建议

1. **D5 是下周最重要的一天。** MallSenseAI×LnkChat 集成路径是两周学习里唯一"从看懂变成设计"的环节。建议那天给足 90 分钟上限，把 §3 的三张 ❌（客流/POS 联动/Channel 回传）逐一转为集成设计草图。
2. **术语切换从明天开始执行**（§4.3 三条策略），成本最低的时机是现在——Week 13 的新笔记还没写。
3. **警惕"首评乐观"传染到采购/合作决策。** 7.05 是望远镜分数。如果近期有基于 MallSenseAI 工程质量的决策（给客户 demo、接新场景），先按 6.5 的内窥镜预期留冗余。

---

## 附：Engineering Journal 条目（同步追加）

```markdown
## 2026-08-23（W12-D7 周日 · Virtual CTO：能力边界审视 + 五维评分）

### 今天最大的认知
平台本体（LangChat）的 Code Health（6.0）低于其行业应用（MallSenseAI 7.5）——
架构先进性和工程纪律是两个独立计分项。集成时的信任边界要按 Code Health 画，
不按 ADR 画。

### 今天最大的坑
ADR-004 声明的三项能力（客流分析/POS 联动/Channel 回传）代码为零——
"行业能力包"定位目前只存在于 ADR 文本里。两边各自完整，中间的桥还没画。

### 今天最大的决策
① MallSenseAI 未来两季度主战场 = L1 换格子 + L4 补全，不爬 L2（视频流是
   独立数据契约的新管线，等场景饱和再启动）。
② 术语自 W13 起切换 LnkChat 口径（ADR-008），历史文档不追改。
③ MallSenseAI 首评 7.05 记为望远镜分数，W13-D7 复评验证 6.3-6.8 预测。
```
