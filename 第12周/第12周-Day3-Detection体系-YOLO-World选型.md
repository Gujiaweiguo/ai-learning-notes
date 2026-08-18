# 🧱 Vision Intelligence 心智模型 | Week12-Day3

📌 **Detection 体系：YOLO / RT-DETR / SAM / GroundingDINO，什么时候用哪个 —— 为什么 MallSenseAI 选择了 YOLO-World？**

> 2026-08-19（周三）· MallSenseAI 仓库精读第三天
> 前两天建立了全景（Day1）和截图式流水线（Day2），今天下探到流水线里唯一"AI"的那一环：**detect**。

---

## 1. 今日核心问题

**为什么 MallSenseAI 选择了 YOLO-World？**

但真正的架构问题不是"为什么选它"，而是——**为什么 MallSenseAI 同时跑着 4 个检测器，而且 4 个的策略完全不同？**

看 `/root/MallSenseAI/models/` 目录的真实文件：

| 文件 | 检测器 | 策略 |
|---|---|---|
| `yolo11n.pt` | DebrisDetector | **闭集词表**（COCO 80 类里筛出杂物相关类） |
| `yolov8s-world.pt` | YOLOWorldDetector | **开放词表**（CLIP 文本编码器，运行时 `set_classes()`） |
| `dfire-yolo11n.pt` | FireSmokeDetector | **专用微调**（D-Fire 数据集，只学 fire/smoke 两类） |
| （无模型文件） | FloorCleanlinessDetector | **无模型**（基线图对比，纯 OpenCV） |

一个问题四个答案。检测体系不是"选一个最好的模型"，而是**一张谱系**：每类业务需求落在谱系的不同位置。

---

## 2. 人话解释（用 26 年 ERP 经验讲）

Jason，这不就是报表体系的老问题吗？

一个 ERP 项目上线，报表需求大概也分四类：

1. **标准报表**：科目余额表、总账——出厂自带，标准模型（COCO 80 类）就是这种，"出厂标准功能清单"，瓶子、背包、雨伞它认识，因为全世界都教过它。
2. **行业定制报表**：商业地产的租金分摊——必须定制开发，但开发一次到处用。D-Fire 模型就是"消防行业版"：别人拿几万张火灾烟雾图训练好了，你直接用，精度还比你自拍数据高。
3. **配置化自助报表**：业务人员自己拖维度、改口径——**YOLO-World 就是视觉界的低代码平台**。想检测什么，改一段文本清单（"shopping cart, stroller, wheelchair"），不用找供应商、不用发版、不用训练。物业说"最近共享单车老堵消防通道"，把 `bicycle`（本来就有）改成/加上 `shared bike`，10 秒后生效。
4. **对账脚本**：两系统余额核对——确定性规则能解决的，绝不上 ML。地面脏污检测就是拿当前截图和"打扫干净时的基线图"做像素差，简单、可解释、零模型成本。

**YOLO-World 的本质：把"检测什么"从开发域搬到了运营域。**

传统检测模型，类别烧死在权重里（就像硬编码的报表），改一个字段要重新训练发版。YOLO-World 用 CLIP 文本编码器，类别变成运行时参数——这在 ERP 里叫**科目表配置化**、**单据类型自定义**，你 26 年前就在做这件事，只是当时对象是借贷科目，现在是英文单词。

还有一层 ERP 老江湖才懂的账：**MallSenseAI 的产品状态是"暂不推广但维护运行"**（域知识.md 设计决策第 1 条）。这个状态下，为每个商场收集标注数据、微调专用模型？预算为零。零样本 = 零数据成本，这是唯一选得起的方案。

---

## 3. LangChat 架构位置（五层模型 + 产品栈）

```
L1  Image Understanding  ← ★ 今天在这：Detection 是 L1 的核心
L2  Video Understanding     （Tracking / MOT —— 明天）
L3  Scene Understanding
L4  Business Intelligence
L5  Vision Agent
```

放进巡检流水线（Day2 精读过的那条链）：

```
scheduler → executor(capture) → 【detect ★】 → persist → rule → alert → EventBus → 通知
```

**detect 是整条链上唯一"AI"的环节**，前后都是工程。但注意它的占比错觉：代码里 detectors/ 只占一个包，可是产品成败（误报率——域知识.md 明说这是"市场落地难度大"的核心原因）几乎全压在这一环。

产品栈位置：

```
LangChat（平台层）
 └─ MallSenseAI / 未来 LangChat AI Vision（行业能力包，ADR-004）
     └─ 检测器谱系 ← ★ 今天：这批检测器就是未来 vision.* Capability 的实现内核
```

---

## 4. ADR 依据（真实文件）

本周虽以 MallSenseAI 为主，但两份 LangChat ADR 直接框住了检测体系的战略位置：

**ADR-003（Capability × Industry 正交 facet 模型）**：产品矩阵里明确画了 `vision.*` 这一行 Capability，且标注"仅适用于部分行业"。正交模型要求能力与行业解耦——**检测器谱系正是这个要求的实现基础**：基线检测器（debris/world/fire）是通用能力，行业语义（什么算障碍、什么算脏）下沉到配置（ROI、classes、阈值），不是硬编码。`yolo_world.py` 里 classes 从 `config` 读而不是写死，就是 Capability 正交思想在代码层的投影。

**ADR-004（MallSenseAI → LangChat AI Vision 重命名）**：明确该产品是 LangChat 平台第一个官方 L4 Application，行业词 `Mall` 从产品名中拿掉、下沉到元数据。含义：**这套检测器未来要服务商场以外的场景**（园区、仓库、医院），届时"检测什么"必须可配置——又一次指向开放词表路线。

**域知识.md 设计决策**（MallSenseAI 自己的"准 ADR"）：
- 第 3 条：CPU-only PyTorch，商场服务器通常无 GPU，YOLO 11n 单帧 <500ms 可接受——**这条硬约束直接排除了重型开放词表方案**（见第 7 段）。
- 术语表把 YOLO-World 定义为"零样本开放词表检测（CLIP 文本编码器 + YOLO，可自定义检测目标）"——自定义检测目标是产品特性，不是技术细节。

---

## 5. 代码验证（只看关键结构）

**契约层** `backend/app/detectors/base.py`——所有检测器实现同一个 ABC：

```python
class BaseDetector(abc.ABC):
    async def detect(self, image_bytes, roi_polygons, config) -> list[DetectionResult]: ...

@dataclass(frozen=True)
class DetectionResult:
    polygon: list[Point]      # 归一化 [0,1] 坐标，与分辨率无关
    confidence: float
    label: str
    metadata: dict            # area_ratio / class_id / detector 名
```

统一契约 = 检测器可插拔，模型选型被封装在实现内部，上游 pipeline 完全无感。这是第 7 段"谱系并存"在代码上成立的前提。

**YOLO-World 三个关键结构** `yolo_world.py`：

1. 默认词表 `DEFAULT_WORLD_CLASSES`——15 个类里数一数：shopping cart、stroller、wheelchair、traffic cone、cleaning cart、ladder、barrier、trash bag、cardboard box……**COCO 80 类里一个都没有**（只有 backpack/suitcase/handbag/umbrella/bicycle/motorcycle 6 个重叠）。这就是"词表错配"的铁证：商场障碍物的世界和 COCO 的世界不是同一个世界。

2. 运行时换词表：
```python
classes = config.get("classes") or config.get("debris_classes") or DEFAULT_WORLD_CLASSES
model.set_classes(classes)   # CLIP 文本编码器在线重嵌入，带 _classes_set 缓存
```
classes 来自 `detector_configs` 表（DB 是 source of truth，`.env` 只做首次引导），ConfigWatcher 每 10s 轮询、原子换入 registry——**改词表不重启，多副本 10 秒内收敛**（AGENTS.md 架构原则）。

3. 用管线弥补模型精度（零样本的代价显式写在阈值里）：
```python
min_confidence = 0.25        # 比火灾检测的 0.5 低一半 → 先放进来
# 然后两道几何闸门：
#   ① centroid 必须落在 ROI 多边形内（shapely contains）
#   ② bbox∩ROI 面积比 ≥ min_area_ratio (默认 0.005)
```
零样本精度不足 → 用"低置信度召回 + ROI 几何强过滤 + 规则引擎 + CooldownTracker"四层兜底。**模型弱，管线强**。

**微调对比组** `fire_smoke.py`：`confidence_threshold=0.5`（是 world 的 2 倍），所有检出强制 `critical` 级——高置信度阈值 × 专用模型，因为火灾误报是"狼来了"，漏报是法律责任（域知识.md 已知限制里专门列了"火灾检测漏报率未量化"）。

**彩蛋**：`yolo_world.py` 开头 monkey-patch 了 ultralytics 的 `CLIP.encode_text` 修 GPU 设备错位——一个产品级 bug 修复沉淀成了带完整注释的架构知识（AGENTS.md 第 127 条还专门警告"不要把它简化回去"）。这就是检测器作为**长期运营资产**而非 demo 代码的证据。

---

## 6. 商业地产映射（LangChat → MI CRE 场景）

**检测器谱系 = 物业巡检团队谱系**：

| MallSenseAI | MI CRE 对应 | 用人类比 |
|---|---|---|
| DebrisDetector（COCO 闭集） | 保洁主管日常巡场 | 只会认"标准问题清单"里的东西 |
| FireSmokeDetector（D-Fire 微调） | 持证消防专员 | 高薪专职，漏报要坐牢，标准最严 |
| YOLOWorldDetector（开放词表） | 零时巡检工按当日清单干活 | **清单（classes 配置）物业经理随时改**，人不用重新招 |
| FloorCleanliness（基线对比） | 交付验房拍照留底比对 | 拿着"合格样板间"照片对差异 |

**set_classes 的商业含义**：招商期要求检测"施工围挡材料堆积"（barrier/ladder），运营期改回"购物车滞留"（shopping cart）——**运营策略变化直接翻译成一条 DB 配置**，IT 不参与。这在 MI 语境里等于把"巡检 SOP"做成了可热更新的数据。

**对应 LangChat 概念链**：

```
BaseDetector.detect() 契约      ↔ Capability 的稳定接口
detector_configs 表（词表/阈值） ↔ Capability 的参数化配置
DetectionResult（label/conf/polygon）↔ Capability 返回的结构化结果
模型管理后台上传 .pt + 热切换    ↔ Connector / 模型接入管理 + 灰度思想（原子快照切换）
```

---

## 7. 与传统方案比较（选型矩阵）

把今天的四个候选 + 三个未选的放进同一张表（部署约束：**CPU-only、单帧预算 <1s、零标注数据、运营配置驱动**）：

| 方案 | 词表 | CPU 单帧* | 数据需求 | 换目标成本 | 判决 |
|---|---|---|---|---|---|
| YOLO 11n（COCO） | 闭集 80 类 | ~0.1-0.5s | 零 | 重新训练 | ✅ 用于 debris（捡 COCO 现成类）|
| D-Fire 微调 11n | 专用 2 类 | ~0.1-0.5s | 别人已标注 | 重新训练 | ✅ 用于火灾（精度/责任优先）|
| **YOLO-World v8s** | **开放** | ~0.5-2s | **零（零样本）** | **改文本，秒级** | ✅ 用于商场长尾障碍物 |
| 基线对比 | 无词表 | ~0.05s | 一张基线图 | 重拍基线 | ✅ 用于地面脏污 |
| RT-DETR | 闭集 | 更慢 | 标注数据 | 重新训练 | ❌ 更准但仍闭集——没解决核心问题 |
| GroundingDINO | 开放 | 秒级~十秒级 | 零 | 改文本 | ❌ CPU 上跑不动，实时性崩溃 |
| SAM/SAM2 | 无语义标签 | 慢 | 需 prompt | — | ❌ 它是分割器不是检测器，给 mask 不给"这是购物车" |

\* 数量级估计，取决于 CPU 型号与分辨率。

**决策链复盘**（CTO 视角）：
1. 商场障碍物是**长尾词表** → 闭集方案（11n 原生 / RT-DETR）出局，无论多准；
2. **CPU-only 硬约束** → 重型开放词表（GroundingDINO）出局——准确性买不起算力；
3. **零标注预算**（产品暂不推广）→ 微调路线只配给"法律责任级"场景（火灾），长尾场景不配；
4. 剩下唯一解：YOLO-World——单阶段检测器 + CLIP 文本嵌入，是 CPU 上唯一"开放词表 + 近实时"的交集。
5. 它的弱点（零样本精度不稳）用**管线四层兜底**（低阈值召回 → ROI 几何 → 规则引擎 → Cooldown）补，而不是换更重的模型。

**这就是架构师和算法工程师的区别**：算法工程师问"哪个模型 mAP 最高"，架构师问"哪个方案在算力/数据/运营预算的约束下，让整个系统的误报率最低"。**模型弱可以用管线补，管线弱神仙模型也救不了。**

---

## 8. 架构师思考题（CTO 级，不是考试）

1. **微调闭环**：某商场要求检测"共享充电宝柜旁散落的充电宝"。直接把 `power bank` 加进 classes 行不行？什么信号出现时你才决定"零样本不够，该微调了"？（提示：`alarm_images/` 那 21 个目录 38MB 的真实告警快照，除了当部署证据，还能当什么？）
2. **算力排程**：100 路摄像头 × 2 小时巡检一轮 × 每帧 3 个模型（debris+world+fire 串行还是并行？）。YOLO-World 在 CPU 上单帧可能 >1s，`executor` 的并发设计怎么定上界？如果加到第 4 个检测器，瓶颈在模型加载、推理还是截图 IO？
3. **能力上翻**：按 ADR-004，MallSenseAI 要变成 LangChat AI Vision。届时 `DetectionResult(label, confidence, polygon)` 要作为 `vision.*` Capability 的输出暴露给平台。这个契约够吗？缺什么？（想想：时间戳、camera_id、ROI 语义、归一化坐标的消费者假设……）
4. **词表治理**：classes 开放给物业运营配置后，有人写了中文"购物车"，有人写了 "shopping cart (red)"，有人把阈值调到 0.05。谁负责词表治理？需要什么样的 guardrail？（对比：LangChat 的 Governance 前移思想怎么搬过来？）

---

## 9. 我的理解变化

**以前以为**：检测系统的核心技术决策是"选哪个模型"——看 leaderboard，选 SOTA，精度至上。MallSenseAI "只用了 v8s 级别" 会让我觉得"技术不够先进"。

**现在知道**：
1. **选型是约束求解，不是排名浏览**。词表匹配度 × CPU 算力 × 数据成本 × 运营配置能力，四维约束下 YOLO-World 是唯一可行解，SOTA（GroundingDINO）反而是错的选择。
2. **检测体系是谱系不是单品**。4 个检测器 4 种策略并存，闭集/微调/零样本/无模型各守一档——就像报表体系里标准报表、行业版、自助报表、对账脚本并存，谁也替代不了谁。
3. **"检测什么"从权重变成数据，是一次小型的能力革命**。set_classes + detector_configs 热更新 = 检测能力的参数化，和 LangChat Capability 参数化是同一个思想在不同层的实例。
4. **误报率是系统属性，不是模型属性**。min_confidence、ROI 几何、规则引擎、Cooldown 四层过滤共同决定最终误报率——域知识.md 说"误报率是市场落地难度大的核心原因"，解药在管线，不全在模型。

---

## 10. 明日连接 + Semantic Layer

**明天（Day4）**：Video Analytics 基线——当前截图模式 vs 未来 RTSP/FFmpeg/GPU 推理。从截图到视频流，架构要改什么？（executor 变流式 consumer、帧采样策略、Tracking 引入、算力模型从"每 2 小时一帧"变成"每秒 25 帧"的三个数量级跳跃。）

**Semantic Layer 位置**：今天学的 Detection 处在视觉语义链的**最底端出口**——

```
像素（无语义） → Detection（label + confidence + polygon：最小语义单元） →
Tracking（同一物体跨帧同一 ID） → Scene（人数/密度/队列） → KPI（客流/安全事件） → 决策
```

`DetectionResult` 就是视觉世界的"原始凭证"——相当于 ERP 里的单据行。后面每一层（L2-L5）都拿它当事实源。明天会看到：没有 ID 的 Detection 帧堆积如山，有了 Tracking 才有"事件"——正如 ERP 里没有单据号的流水是垃圾数据，有单据号才可对账。

---

*今日信源：`/root/MallSenseAI/backend/app/detectors/`（base/debris/fire_smoke/yolo_world/integration.py）、`/root/MallSenseAI/models/`、`/root/MallSenseAI/AGENTS.md`（第 72-128 条）、`域知识.md`、ADR-003 / ADR-004。*
