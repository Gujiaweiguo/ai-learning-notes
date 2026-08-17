# 🧱 LangChat 心智模型 | Week12-Day2 · MallSenseAI 仓库精读

**日期**：2026-08-18（周二）
**主题**：Pipeline / Detectors / Rules / Alerts / Workers 全链路精读
**Today's Question**：为什么当前是定时截图而不是视频流？

---

## 1. 今日核心问题

**为什么 MallSenseAI 是定时截图（snapshot polling），而不是视频流（video stream）？**

答案的分水岭不在技术，在业务对象的时间尺度：

- **状态型场景**（消防通道占用、地面脏污、装修垃圾堆积）：物理世界变化以分钟/小时计 → 采样（截图）足够
- **事件型场景**（跌倒、入侵、打架）：瞬间发生、不可重现 → 必须连续观测（视频流 + Tracking）

当前 MallSenseAI 管的三个场景全部是状态型。**截图不是妥协，是匹配。**

## 2. 人话解释（26 年 ERP 视角）

这就像**周期盘点 vs 实时流水账**。

库存管理里，你不需要每一秒都知道货架上还有几箱货——每天盘一次、每周盘一次就够。但收银流水必须逐笔实时，漏一笔就是钱。

商场消防通道堆货 = 库存状态问题。保安每 2 小时巡场拍一张照片、对照标准、超标开单，这套流程管了二十年，有效。MallSenseAI 做的就是把这个保安装进代码：**定时到点（scheduler）→ 每个点位拍照（executor/capture）→ 对照标准（detectors）→ 超标开单（alerts→work_orders）**。

而视频流方案 = 监控中心 7×24 盯屏。为"通道有没有被堵"这个问题上视频流，等于为了盘点库存给每箱货装 RFID——技术上可行，商业上荒谬。

## 3. LangChat 架构位置

```
workers/ 子系统 = 整个平台的发动机
scheduler.py ─→ executor.py ─→ detectors/ ─→ pipeline._persist ─→ rules/engine ─→ alerts/ ─→ notifications/
  定时到点        拍照(隔离失败)   L1 图像理解     审计落库            状态规则         告警生命周期     wecom/sms/email
```

- 五层模型中：detectors 在 **L1（Image Understanding）**，规则引擎在 **L3（Scene Understanding）的雏形**
- 在 LangChat 蓝图里：这是未来**行业能力包（Industry Capability Pack）的原料车间**——产出的结构化 `detection_events` / `alerts` 就是未来 `safety.alert.query` 类 Capability 的数据底座（W12-D1 结论：当前封闭，无 capability 暴露）

## 4. ADR 依据

- **ADR-004**：MallSenseAI → LangChat AI Vision。行业词 `Mall` 从产品名剥离，下沉到 Application 元数据的 `industries` 字段。重命名只覆盖对外品牌，代码模块名不动（保护契约）——读代码和读文档看到两个名字是同一个东西
- **ADR-003**（Capability × Industry 正交）：当前这个"原料车间"未来要以 Capability 形式被 LangChat 编排，所以它内部怎么实现（截图还是流）是它自己的事——**采样方式是实现细节，结构化事件输出才是契约**

## 5. 代码验证（关键结构）

| 文件 | 关键事实 |
|---|---|
| `backend/app/camera/adapter.py` | `CameraAdapter` ABC 只有一个采集方法：`capture_snapshot() -> bytes`（单张 JPEG）。大华 HTTP 快照协议 + `mock://` 测试摄像头。**接口本身就是"截图世界观"** |
| `workers/scheduler.py` | `InspectionScheduler`：每摄像头独立间隔（默认 `ALARM_INTERVAL_MINUTES=5` 分钟），指数退避 30→60→120→300s，并发上限 10，优雅停机 |
| `backend/app/detectors/base.py` | `BaseDetector.detect(image_bytes: bytes, roi_polygons, ...)` —— 无状态、图进图出 |
| `backend/app/rules/engine.py` | 自称 `Stateless evaluator`，但"停留超时"靠 `cooldown_state` 里的 `active_since` **跨快照累计停留时长** —— 状态外置模式（引擎无状态，状态放外部 store） |
| `workers/pipeline.py` | 全链编排：load context → detect → `_persist_detections()`（审计落库 detection_events）→ 规则评估（含 suppression 检查）→ 告警 |
| 生产配置 | `CUDA_VISIBLE_DEVICES` 空 = **CPU 推理**。21 路摄像头 × 5 分钟一张，CPU 扛得住；25fps 视频流 CPU 必死 |

## 6. 商业地产映射（MI CRE）

| MallSenseAI 概念 | MI 商管场景 |
|---|---|
| 定时截图巡检 | 保安定时巡场打卡拍照（每点位一张，留档） |
| detection_events 审计表 | 巡场记录本（每张照片可追溯） |
| Alert + 证据图 | 整改通知单 + 现场照片（法务凭证链） |
| 告警→工单自动创建 | 保安发现 → 物业工单系统开单 |
| suppression（静音） | 装修期报备：该区域已知会，暂不开单 |
| 视频流方案 | 监控中心 7×24 盯屏（成本 100 倍，只对事件型场景必要） |

## 7. 与传统方案比较

| 维度 | 传统安防（海康/大华智能盒子） | MallSenseAI 截图模式 |
|---|---|---|
| 采集 | RTSP 视频流持续拉取 | HTTP 定时快照 |
| 推理 | GPU（每路都要算力） | CPU（分时复用） |
| 目标 | 事件（越界/徘徊/跌倒） | 状态（占用/脏污/堆物） |
| 单路成本 | 高 | 低一个数量级 |
| 证据 | 录像片段（存储贵） | 单张证据图（KB 级） |
| 失败恢复 | 断流重连复杂 | 下个周期自然重试（backoff） |

**留的口子**：`CameraAdapter` 是抽象类，未来 RTSP/FFmpeg 抽帧 adapter 可以无侵入接入——采集方式被隔离在 adapter 层，不污染下游。

## 8. 架构师思考题

业主提出新需求：**"商场里老人跌倒，10 秒内必须告警。"**

当前架构哪三层先崩？
1. **采样层**：5 分钟间隔 → 需 ≥2fps，采样率提 600 倍，scheduler/executor 的并发模型还成立吗？
2. **检测层**：`BaseDetector.detect(image_bytes)` 无状态逐帧 → 跌倒判定需要 Pose 或时序信息，接口要不要重定义？
3. **规则层**：`cooldown_state` 按"连续出现"累计 → 跌倒是"出现即触发"，且需要跨帧去重（同一人躺 10 分钟 ≠ 600 条告警），Tracking 在哪一层引入？

进一步：如果 50 路摄像头都要 2fps，GPU 预算多少？哪些路保持截图模式、哪些升级流模式——**采样策略要不要变成 per-camera 配置？** 这就是 L2（Video Understanding）逼进 L1 的真实压力测试。

## 9. 我的理解变化

**以前以为**：截图是视频流的"穷亲戚"，是没上 GPU 之前的过渡方案，终局一定是视频流。

**现在知道**：采样方式是**业务时间尺度的函数**。状态型场景，截图就是终局不是妥协；事件型场景，截图根本不成立。判断标准不是技术能力，是"这个业务对象变化多快"。另外发现一个惊喜：`Stateless 规则引擎 + cooldown_state 状态外置` 和 LangChat 的 `无状态 Runtime + 外部状态` 是**同一个架构模式**——无状态核心 + 外置状态，两个产品在两个领域独立收敛到同一答案，这就是模式的通用性。

## 10. 明日连接 + Semantic Layer

**明日（Day3）**：Detection 体系——YOLO / YOLO-World / RT-DETR / SAM / GroundingDINO 各自的取舍，为什么 MallSenseAI 选 YOLO-World 做零样本检测。

**Semantic Layer 位置**：今天的 capture→detect 产出原始 Detection（像素坐标 + 类别 + 置信度），位于 `Ontology → Domain Model → Capability → Skill` 链的**最底层原料端**。规则引擎把 Detection 提升为业务语义（"消防通道被堵超过 10 分钟"），这正是未来 Domain Model 的 `DetectionEvent → BusinessEvent` 语义跃迁——Vision 侧的 Semantic Layer 还很薄，只有规则模板这一层，没有真正的 Ontology。
