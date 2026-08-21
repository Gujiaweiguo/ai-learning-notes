# 🧱 Vision Intelligence 心智模型 | Week12-Day6

📌 **⚡ 动手交付：画 Vision Capability 五层图 + Business Scene Matrix —— MallSenseAI 现在站在 L1 的哪一部分？**

> 2026-08-22（周六）· Week 12 第六天
> Day5 的 Business Scene Matrix 是"自顶向下看钱"，今天把它落成**两张正式交付图**：能力维度的五层图（MallSenseAI 的精确坐标）+ 业务维度的场景矩阵（层的覆盖视图）。Day5 日志里"记入周六画图输入"的四条判定，今天全部落图。

---

## 1. 今日核心问题

**MallSenseAI 现在站在 L1 的哪一部分？**

表面答案："MallSenseAI 在 L1（Image Understanding），很初级。"——**错在两处**。

**第一处错：L1 不是一个点，是一个格子间。** "会做检测"和"会做检测"差别巨大：封闭词表检测（只能认训练时见过的类）、领域微调检测（D-Fire 只认烟火）、开放词表零样本检测（YOLO-World 运行时改文字就能认新物体）、图像比对（不是"认出是什么"而是"和干净基线差多少"）、OCR、分割、VLM 场景描述——全是 L1，互相不可替代。问"MallSenseAI 在 L1 哪里"，答案是**四个格子里的三个高价值格 + 一个土办法格**（见 §2 放大图）。

**第二处错：MallSenseAI 不止在 L1。** 停留时长（duration）和面积占比（area ratio）这两个规则参数，本质是**时间维度和空间维度的统计量**——那是 L3 Scene Understanding 的定义域。MallSenseAI 没有跟踪器，却用"帧级检测 + 告警状态机 + bbox 面积比"造出了 L3 统计的**退化形态**。再往上，告警→工单→resolved 的闭环和 Dashboard，是 L4 Business Intelligence 的雏形。所以精确坐标是：

```
L5  Vision Agent          ─ 空缺（0%）
L4  Business Intelligence ─ 雏形（告警工单闭环 + Dashboard，~20%）
L3  Scene Understanding   ─ 退化形态（占用面积/停留时长两个统计量，~15%）
L2  Video Understanding   ─ 空缺（0%，OpenSpec 29 个 spec 无 video/stream/tracking）
L1  Image Understanding   ─ 主阵地（4 个子能力格占了 3.5 个，~70%）
```

**为什么这个问题重要**：坐标定错，路线图就错。把 MallSenseAI 当"低级 L1 系统"，会得出"赶紧补 L2 视频流"的错误结论；看清它是"窄而深的 L1 + 踮脚够到 L3/L4"，才会得出 Day5 已验证的正确结论——**扩场景（L1 内换格子）比升层级（爬 L2）的 ROI 高一个数量级**。

---

## 2. 人话解释（用 26 年 ERP 经验讲）

Jason，你 1990s 末管 MRP II 项目时就见过一模一样的争论。

那时有人质疑："MRP II 只是计算器，真正的高级系统是 APS 高级排程。"听起来对，实际荒谬。MRP II 的价值不在"计算复杂度低"，在于它**把 BOM、工艺路线、库存三个对象咬合成了一个闭环**——订单→计划→领料→完工入库，每一步有凭证。APS 计算再高级，接不上这个闭环就是PPT。

MallSenseAI 是同一个故事。说"它只是 L1 检测"的人，等于说"MRP II 只是计算器"。它的价值不在检测模型多先进（YOLO 11n 就是最小的那种），在于**闭环**：定时采样→检测→规则→告警→工单→resolved，每步有凭证（DetectionEvent、Alert、WorkOrder 三张表就是会计凭证）。这个闭环让"人力替代"的价值可审计——Day5 算过，这是当期 ROI 的分子。

还有一个你熟悉的词今天有了新含义：**五层模型不是楼梯，是科目结构**。

你做过集团财务就知道：科目体系是"资产/负债/权益/成本/损益"的**分类框架**，不是"企业必须先做完资产核算才能做损益核算"的升级路线。五层模型同理：它是**能力依赖的分类账**（L3 客流 KPI 记账时必须引用 L2 Tracking 的凭证，L2 又引用 L1 Detection 的），不是"爬完 L1 才能上 L2"。**状态型场景的账可以 L1 直接记到 L4**（检测→工单），跳过 L2——就像损益表不需要等固定资产明细账建完才能出。传统 CV 团队按楼梯思维做项目（先检测、再跟踪、再分析），做了十年还在 L2；MallSenseAI 按科目思维做产品，第一年就把账记到了 L4。

---

## 3. LangChat 架构位置

```
LangChat（企业 AI 应用平台）
 │  Ontology → Domain Model → Capability → SkillRelease
 │                                        ▲
 │                     行业能力包（ADR-004：LangChat AI Vision）
 │                                        │
 ▼                                        │
MallSenseAI（视觉智能行业能力包）──────────┘
 │  ┌─ L1 检测器群（YOLO-World / D-Fire / 11n / 图像比对）
 │  ├─ L3' 规则统计（duration / area，退化形态）
 │  └─ L4' 工单闭环（Alert → WorkOrder → resolved）
 ▼
商管系统 / MI / CRM（业务应用层）
```

今天的两张图在 Semantic Layer 链上的位置：

- **五层图 = Capability 的"层地址系统"**。按 ADR-003（Capability × Industry 正交），每个 `vision.*` / `safety.*` Capability 都该标一个层地址（如 `safety.firecorridor.detect` = L1+L3'）。层地址决定了它的依赖（L3 能力必须声明对 L2 的依赖，或证明自己用退化形态绕过）。
- **Business Scene Matrix = Capability 的需求侧台账**。矩阵每一行（Day5 的 9 行）= 一个 Capability 候选；"行业适用性"列 = 正交模型的实证（消防通道多行业通用、客流仅商业地产）；"已有层 vs 所需层"的差 = Gap Matrix 的视觉版。
- 明年 MallSenseAI 集成进 LangChat 时，`safety.alert.query`（PRD §7.3 先行路径）暴露的就是 L4' 工单闭环那一格——**先卖闭环，不卖模型**。

---

## 4. ADR / 文档依据（读真实文档）

- **ADR-003（Capability × Industry 正交）**：五层图是"能力维"，行业是另一维——两维交叉处才是可复用单元。今天的 L1 放大图里"开放词表检测"格之所以值钱，正因为它对物业/园区/工地等行业是同一格（词表配置化），这是 Day5"扩场景=配置变更"结论的 ADR 根源。
- **ADR-004（更名 LangChat AI Vision）**：行业能力包定位 = 五层图不是 MallSenseAI 一家的路线图，是 LangChat 视觉能力的公共层地址系统。MallSenseAI 今天占的格子，就是未来 LangChat `vision.*` Capability 的首批实体。
- **域知识边界（差距分析.md §"不做什么"）**：不做客流统计（"不是客流分析系统"）、不做人脸识别（隐私）、不做消防联动（只告警+建工单）——**这是 L1 放大图上的三块"明示不占"格**。边界画得越明确，五层图上的坐标越可信：MallSenseAI 是"有边界的深"，不是"没爬高的浅"。
- **PRD §3.2/§6**：违停/占道经营/垃圾满溢列为 P2 扩展场景，全部落在 L1 开放词表格——路线图的下一步是**同层横向扩格**，印证 Day5 判定③。
- **OpenSpec 现实判据**：29 个 spec 无 video/stream/tracking 关键词（Day4 已验证）——L2 = 0% 的规格级证据，不是推断。
- **AGENTS.md 架构描述**："corridor obstruction detection platform"，`detectors/` 目录注释 "BaseDetector ABC, DebrisDetector (YOLO), FireSmokeDetector, DetectorRegistry"（实际还有 yolo_world.py / floor_cleanliness.py 未同步进注释——文档债，记入日志）。

---

## 5. 代码验证（只看关键结构）

| # | 代码事实 | 位置 | 五层图坐标证据 |
|---|---|---|---|
| 1 | `BaseDetector(abc.ABC)` + 4 个实现类 | `backend/app/detectors/{base,debris,fire_smoke,yolo_world,floor_cleanliness}.py` | **L1 四格的实体清单**：Debris(yolo11n 封闭词表)、FireSmoke(dfire-yolo11n 领域微调)、YOLOWorld(开放词表)、FloorCleanliness(absdiff 基线比对) |
| 2 | `DEFAULT_MODEL_PATH = "yolo11n.pt"` / `"dfire-yolo11n.pt"` | debris.py:58 / fire_smoke.py:15 | 封闭词表格与微调格的模型级区分 |
| 3 | "Obstruction: prefer YOLO-World, fallback to Debris" | `detectors/service.py:63` | **格子间的运行时路由**：同一场景（障碍物）优先走开放词表格，失败回退封闭词表格——L1 内部已有容错拓扑 |
| 4 | `FloorCleanlinessDetector`: "OpenCV absdiff + morphology + ROI masking, requires baseline_path" | floor_cleanliness.py docstring | 图像比对格的实现形态：不是分类模型，是**有监督参照物的时间差分** |
| 5 | `ObstructionRuleEngine (duration/area/forbidden-zone)` + `CooldownTracker` | `backend/app/rules/` | **L3 退化统计的实体**：duration=时间统计量、area=空间统计量——没有 tracker 却在做 Scene Understanding 的账 |
| 6 | 告警生命周期 `pending → confirmed(自动建工单) → resolved` + `suppressed` | alerts API / PRD §7.2 | **L4 雏形的闭环凭证**：工单是价值兑现的会计凭证（Day5） |
| 7 | `DetectionPipeline: capture→detect→persist→rule→alert` 五站 | `workers/pipeline.py` | 跨层链路的代码形态：L1(第2站)→L3'(第4站)→L4'(第5站)，**第 4 站不经过任何 L2 组件**——跳层直达的实证 |
| 8 | `DetectorType` 枚举仅 `image_compare / yolo / blue_box` 三值 | `models/entities.py:71` | 数据库层的类型系统落后于代码事实（yolo_world 无枚举位）——层地址系统还没进 schema，记入 Gap |

**结论**：五层图上的每个标记都能指到一个文件一个类。图不是画的，是从代码里长出来的。

---

## 6. 交付物一：Vision Capability 五层图

> 配套可执行版本见同目录 ipynb 实验 1/2（含层约束验证与覆盖率计算）。

### 6.1 全景五层图（MallSenseAI 坐标版）

```
════════════════════════════════════════════════════════════════════════════
                    Vision Capability 五层模型 · MallSenseAI 坐标图
        ✅ 已实现   🟡 退化形态(无L2支撑的模拟)   ⬜ 空缺   ◇ P2规划中
════════════════════════════════════════════════════════════════════════════

L5  Vision Agent            ⬜ 自动巡检报告  ⬜ 异常归因分析  ⬜ 运营建议
    (自动分析→推理→建议)     ⬜ 日报生成      ⬜ 跨摄像头事件关联
                             ── 空缺 0% ──（与 LangChat Agent 汇合点，W13-D4）

L4  Business Intelligence   🟡 告警工单闭环    🟡 Dashboard 统计
    (客流KPI/安全事件/运营)  ⬜ 客流 KPI       ⬜ 热区图         ⬜ 排队指标
                             ── 雏形 ~20% ──（闭环可审计 = 价值兑现凭证）

L3  Scene Understanding     🟡 占用面积统计    🟡 停留时长统计   ⬜ 密度估计
    (Counting/Heatmap/...)  ⬜ 热区            ⬜ 队列长度       ⬜ 轨迹聚类
                             ── 退化形态 ~15% ──（靠规则引擎+状态机，非跟踪）

L2  Video Understanding     ⬜ MOT/ByteTrack  ⬜ 轨迹管理       ⬜ 事件判定
    (Tracking/Video)        ⬜ ReID           ⬜ 跨摄关联       ⬜ 实时流推理
                             ── 空缺 0% ──（OpenSpec 29 spec 无 video/stream/tracking）

L1  Image Understanding     ✅ 封闭词表检测     ✅ 领域微调检测   ✅ 开放词表零样本
    (Detection/OCR/Seg)     ✅ 基线图像比对    ◇  违停/占道/满溢(P2,零样本扩)
                             ⬜ OCR            ⬜ 分割(SAM)      ⬜ VLM 场景描述
                             ── 主阵地 ~70% ──（4 个高价值格占了 3.5 个）
════════════════════════════════════════════════════════════════════════════
```

### 6.2 L1 放大图（今天的核心交付）

```
                    L1 · Image Understanding 格子间
 ┌──────────────────┬──────────────────┬──────────────────┐
 │  封闭词表检测     │  领域微调检测     │  开放词表零样本   │
 │  yolo11n.pt      │  dfire-yolo11n   │  YOLO-World      │
 │  COCO类:箱子/杂物 │  仅烟火类        │  运行时改词表     │
 │  ✅ debris.py    │  ✅ fire_smoke   │  ✅ yolo_world   │
 │  (回退位,见§5-3)  │                  │  (主路由位)       │
├──────────────────┼──────────────────┼──────────────────┤
 │  基线图像比对     │  OCR             │  分割/VLM        │
 │  absdiff+形态学   │  ⬜ (票据/车牌    │  ⬜ SAM/VLM      │
 │  ✅ floor_       │     场景暂无)     │  (场景理解入口,   │
 │     cleanliness  │                  │   W13 评估)      │
 └──────────────────┴──────────────────┴──────────────────┘
 → MallSenseAI 占 4/6 格（含半格：P2 场景已在开放词表格排期）
 → 未占 2 格（OCR/分割VLM）= 主动边界，非能力缺陷（§4 域知识）
```

### 6.3 关键架构论断：五层模型是 DAG，不是楼梯

```
楼梯思维(错)：L1 ──→ L2 ──→ L3 ──→ L4 ──→ L5   （必须逐级爬）

依赖DAG(对)：
  事件型：L1 ──→ L2(Tracking) ──→ L3(计数/轨迹) ──→ L4 ──→ L5
                        │                │
  状态型：L1 ──────────·────────·──→ L3'(退化统计) ──→ L4'(工单闭环)
          (帧级检测+状态机直接造出统计量，跳过 L2)
```

**状态型路径跳 L2 是合法的**（Day2 已证：状态变化以分钟计，采样足够）；**事件型路径跳 L2 是灾难**（跌倒瞬间发生不可重现，无跟踪必漏）。层间边是"凭证依赖"（L3 的账要引 L2 的轨迹凭证），不是"施工顺序"。

---

## 7. 交付物二：Business Scene Matrix（层覆盖版）

> Day5 的 9 行 ROI 矩阵升级：新增"所需层 / 已有层 / 层缺口"三列，成为 Gap Matrix 的视觉入口。
> 档位：A=截图零增量 B=RTSP抽帧 C=全流+Tracking D=边缘盒（Day4 谱系）

| MI 业务目标 | Vision Capability（层地址） | 档位 | 所需层 | MallSenseAI 已有 | 层缺口 | 状态 |
|---|---|---|---|---|---|---|
| 消防合规 | Detection(L1)+占用统计(L3') | A | L1,L3',L4' | **全覆盖** | 无 | ✅ 已部署 |
| 火灾早期 | 微调Detection(L1) | A | L1,L4' | L1✅ L4'✅ | 漏报率未量化 | ✅ 已部署 |
| 保洁监管 | 基线比对(L1) | A | L1,L4' | **全覆盖** | 无 | ✅ 已部署 |
| 违停/占道/满溢 | 开放词表(L1)+规则 | A | L1,L3' | L1✅(词表待配) | 运营调优 | ◇ P2 排期 |
| 跌倒检测 | Tracking(L2)+Pose(L1) | C | L1,L2,L4' | 仅 L1 | **L2 全缺** | ⬜ roadmap |
| 夜间入侵 | Tracking(L2)+轨迹判定 | B→C | L1,L2,L4' | 仅 L1 | **L2 全缺** | ⬜ roadmap |
| 租金定价/客流 | Tracking(L2)+计数(L3) | C | L1,L2,L3,L4 | 仅 L1 | **L2+L3 全缺** | ⬜ 战略行(资本预算) |
| 排队分析 | Tracking(L2)+队列(L3) | C | L1,L2,L3 | 仅 L1 | L2+L3 | ⬜ roadmap |
| 自动巡检报告 | 全层+Agent(L5) | A+B | L1..L4'+L5 | L1,L3',L4' | **L5 全缺** | ⬜ W13-D4 评估 |

**矩阵读法（三条硬结论）**：

1. **当期行（前3行）层缺口=0 或仅剩验证项**——已部署资产的复用叙事完整，这是 Day5 判定①的层视图。
2. **所有 B/C 档行的第一个缺口都是 L2**——L2 是事件型/分析型场景的**单点依赖层**。这就是为什么"L2 空缺"既是最大 Gap（阻断 5 行）又是最贵 Gap（GPU+重构，Day4 档位定价）。
3. **L5 行的层缺口反而是最小的**（已有 L1+L3'+L4' 三层地基）——自动日报这种 L5 场景不需要 L2/L3，**Agent 层可以直接建在状态型闭环上**。Day5 判定④"优先验证 L5 日报"的架构学依据：它是最便宜的升层路径。

---

## 8. 与传统方案比较

| 维度 | 传统 CV 项目制（海康/商汤定制） | 开源 CV 栈（自己搭 YOLO+ByteTrack） | **MallSenseAI** | LangChat 能力包（目标态） |
|---|---|---|---|---|
| 层模型 | 无层概念，按场景交付 | 有组件无产品化层 | **五层坐标 + 退化形态显式化** | 层地址进 Capability schema |
| 扩新场景 | 新项目/新合同/驻场 | 改代码重训 | **改词表=配置变更**（L1 开放词表格） | 改 Capability 声明 |
| 价值闭环 | 交付即结束（无工单闭环） | 无（裸算法） | **告警→工单→resolved 可审计** | 工单→企业系统 Connector |
| 楼梯思维 | 隐含（先检测再跟踪逐期卖） | 隐含（工程师本能） | **显式 DAG：状态型跳 L2 合法** | — |
| 弱点 | 贵、慢、不可复制 | 无产品化、无治理 | **L2=0、L1 仅有 4 格、无 Agent** | 未落地 |

**为什么不选"先补齐 L2 再谈产品"？** 因为传统厂商二十年就是这么干的——把楼梯思维做成了商业模式（逐期卖升级）。MallSenseAI 的机会恰恰是反着走：**先把 L1×L3'×L4' 的闭环复制到 N 个行业**（ADR-003 正交），L2 等 GPU 成本和场景需求同时成熟再上。

---

## 9. 架构师思考题

**题**：MI 明天提出需求："扶梯口人流密度热区图"（L3 场景），但预算只批了 A 档（无 GPU，现有截图服务器）。你的五层图上怎么走？

**约束拆解**（不要求唯一答案，要求层地址清晰）：

1. **诚实路线**：告诉 MI 这是 L2 依赖场景（密度估计要 Tracking），A 档做不了真热区——**不接**，保住"只告警可审计"的信任资产。
2. **退化路线**：能否造"L3 退化形态"？——用帧级人头检测（L1 开放词表，词表加 "person"）+ 每分钟采样 + 网格化计数，做**分钟级伪热区**（无个体轨迹，只有密度采样）。层地址：L1+L3'(密度版)。风险：拥挤场景遮挡严重，帧级人头检测漏检率高——退化形态的适用边界要在合同里写明。
3. **换场景路线**：同预算下推 MI 先做"扶梯口滞留物检测"（已有能力，A 档，风险规避型价值）——用矩阵证明 ROI 更高。

**追问**：路线 2 里"person"词表检测如果误报一个假人（广告画上的），L3' 统计会持续计入吗？——会，因为没有 L2 的轨迹去伪机制。**这题的考点：退化形态的能力边界来自下层依赖的缺失，架构师必须显式声明它，否则边界会以误报的形式在客户现场爆炸。**

---

## 10. 我的理解变化 + 明日连接

**以前以为**：五层模型是升级楼梯，MallSenseAI"只在 L1"意味着它是个初级系统，正确路线是赶紧补 L2 视频流往上爬。
**现在知道**：五层模型是**能力依赖的 DAG（分类账）**，不是施工顺序。MallSenseAI 的坐标是"窄而深"：L1 四格占 3.5、L3 退化统计 2 个、L4 闭环雏形、L2 有意为零（状态型场景的合法跳层）。**初级和专注在图上长得一样，区别在边界是主动画的（域知识"不做什么"）还是没爬到的**。Day5 的 ROI 结论今天有了几何解释：当期 ROI 最高的行恰好都是"层缺口=0"的行——**已部署资产所在的格子，就是价值所在的格子**。

**明日连接（Day 7 周日）**：🔄 Virtual CTO Review——MallSenseAI 能力边界审视 + 五维评分（Architecture / Code Health / ADR Consistency / Technical Debt / Developer Experience）。今天两张图是评分的底稿：L2=0% 和 DetectorType 枚举缺位会进 Technical Debt 项。

**Semantic Layer 位置**：五层图 = Capability 的层地址系统（Ontology 里的视觉域分类法）；Business Scene Matrix = Capability 需求台账（矩阵行 → `vision.*`/`safety.*` Capability 候选）；MallSenseAI 已占格 = 未来行业能力包的首批 Capability 实体（ADR-004）。

---

## 📝 Daily Engineering Log

**新增**：五层坐标图（8 个层状态判定）、L1 放大图（6 格占 4）、Business Scene Matrix 层覆盖版（9 行 × 所需层/已有层/层缺口三列）、"DAG 非楼梯"论断及代码证据（pipeline.py 五站中第 4 站无 L2 组件）。

**确认**：Day5 四条画图输入全部落图——①当期主打行=层缺口 0；②客流=资本预算战略行；③增量行=L1 同层扩格；④L5 日报=最便宜升层路径（地基三层已有）。

**修改**：对"MallSenseAI 在 L1"的定位从"点"改为"格子间坐标"；把 L3 判定从"空缺"（Day1 说法）修正为"退化形态 ~15%"（duration/area 是 L3 统计量的无跟踪实现）。

**遗留/技术债**：① `DetectorType` 枚举（image_compare/yolo/blue_box）无 yolo_world/floor_cleanliness 位——层地址系统未进 DB schema；② AGENTS.md detectors 目录注释缺 yolo_world.py、floor_cleanliness.py；③ `Camera.password_hash` 列名存明文（AGENTS.md 已自注）——三件记入明日 Technical Debt 评分。

**下一步**：明日 Virtual CTO Review 用今天两图作底稿；W13-D4 评估 Vision Agent（L5）建在 L4' 闭环上的最小路径；W13-D6 交付 Vision Capability Inventory + Technology Radar 时，把今天的层覆盖矩阵扩成正式 Inventory。

