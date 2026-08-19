# 🧱 Vision Intelligence 心智模型 | Week12-Day4

📌 **Video Analytics 基线：当前截图模式 vs 未来 RTSP/FFmpeg/GPU 推理 —— 从截图到视频流，架构要改什么？**

> 2026-08-20（周四）· MallSenseAI 仓库精读第四天
> Day2 回答了"为什么现在是截图"（状态型场景匹配采样）；今天回答反向问题：**当业务需要事件型场景（跌倒/入侵/客流）时，这套架构要动哪几层？**

---

## 1. 今日核心问题

**从截图到视频流，架构要改什么？**

表面答案：把 HTTP 快照换成 RTSP 拉流。**这是错的。**

真正的答案：截图模式的本质是**拉动模型（pull / 批处理）**——到点、请求、响应、处理、释放。视频流的本质是**推送模型（push / 流处理）**——持续到达、持续消费、状态常驻。这不是换一个采集协议，而是**执行范式的转换**，会牵动五个耦合层：

| # | 层 | 截图模式 | 视频流模式 | 转换性质 |
|---|---|---|---|---|
| 1 | 采集层 | 无状态 HTTP 请求/响应 | 有状态 RTSP 长连接 + FFmpeg 解码 + 断流重连 | 协议→会话 |
| 2 | 处理模型 | 定时拉（scheduler 到点才算 due） | 持续推（帧队列 + 每路消费者协程/线程） | 拉动→推送 |
| 3 | 推理层 | 单帧、分钟级频率、CPU 分时复用 | 连续帧、fps 级频率、GPU + 批处理 + 抽帧策略 | 数量级：1500× |
| 4 | 状态层 | 状态外置（cooldown_state 跨快照累计） | Track 常驻内存（ID + 轨迹 + 生命周期） | 外置→内置 |
| 5 | 证据层 | 单张 JPEG（KB） | 事件前后片段（环形缓冲区，MB 级） | 快照→剪辑 |

**一句话：改的不是"怎么拿图"，是"整个系统的时钟"。** 截图系统的时钟在 scheduler 手里（到点才动）；视频流系统的时钟在摄像头手里（帧到了就必须动）。

---

## 2. 人话解释（用 26 年 ERP 经验讲）

Jason，这件事你在 ERP 里干过一模一样的版本。

**截图模式 = 月结批处理。** 每月 1 号跑一次存货核算：取数、算账、出凭证、归档、释放资源。两次月结之间系统是"空"的。你现在可以把 MallSenseAI 的巡检链路逐字翻译：scheduler 是"调度日历"，executor 是"取数程序"，detectors 是"核算规则"，detection_events 是"凭证归档"，alerts 是"异常账龄报告"。**批处理的失败处理最优雅：这个月失败了，下个月重来**——这就是指数退避（30→60→120→300s）的本质，`next_run_at = now + backoff`，和"下月重跑"是同一个思想。

**视频流 = 实时过账。** 每一笔交易发生瞬间必须过账，系统永远不能"空"。你 26 年里一定见过把月结系统改实时总账的项目——改的从来不是核算规则（规则没变），而是：数据库锁策略、幂等设计、峰值吞吐、失败补偿、对账机制。**全在上游链路，不在业务逻辑本身。**

MallSenseAI 完全同理：**检测器（业务规则）一行都不用改**——`BaseDetector.detect(image_bytes, ...)` 图进图出，给它 JPEG 它就工作，不管这张图是 HTTP 快照来的还是 RTSP 第 1237 帧抽出来的。要改的全在检测器的上游和下游：

- **上游**：怎么拿图（无状态请求 → 长连接会话管理）
- **节奏**：谁来定时钟（scheduler 到点拉 → 帧到了推）
- **下游**：检测结果怎么变成业务事实（孤立框 → 连续轨迹）

还有一个 ERP 老江湖才会敏感的信号：**配置文件里已经出现了两种时间尺度**。`core/config.py` 里默认巡检间隔是 `alarm_interval_minutes = 1`（分钟级），但火灾检测预留了 `fire_smoke_check_interval_seconds = 15`（秒级）。因为火灾发展快，1 分钟采样可能错过最佳告警窗口——**团队已经在采样率谱系上滑动**。这在 ERP 里就像"月结改旬结"：业务压力先在参数上打补丁，参数撑不住的那天，就是架构改造立项的那天。

---

## 3. LangChat 架构位置（五层模型 + 产品栈）

```
L1  Image Understanding     ← MallSenseAI 现在全站在这：帧级 Detection ✅
L2  Video Understanding     ← ★ 今天的主题：Tracking / MOT —— 完全空缺
L3  Scene Understanding     ← 规则引擎雏形（ROI 命中 + 停留时长）
L4  Business Intelligence
L5  Vision Agent
```

**L2 是五层图上最大的空洞。** 而且它不是 L1 的"加强版"——L1 问"这一帧里有什么"，L2 问"这个目标从哪来、到哪去、待了多久"。问题变了，答案的结构就变了：L1 的输出是 `DetectionResult`（框+类别+置信度），L2 的输出必须是 `Track`（ID+轨迹+进入/离开事件）。

放进当前流水线看改造范围（Day2 精读过的链）：

```
scheduler.py → executor.py → [capture] → detectors → pipeline → rules → alerts
  时钟:改      会话:重写     采集:重写     不改↑       编排:改    输入:改   事件:扩
```

**放进 LangChat 产品栈**：关键判断是——这一切改造对 LangChat **不可见**。按 ADR-003（Capability × Industry 正交），MallSenseAI 作为行业能力包，对上暴露的是**结构化事件契约**（未来的 `safety.alert.query` / `people.flow.query` 类 Capability），内部用截图还是流是包的实现细节。**L2 改造是 MallSenseAI 的内部手术，不是 LangChat 的集成变更。**

---

## 4. ADR 依据（读真实文档）

本周主 ADR 仍是 langchat 的 ADR-003 / ADR-004（MallSenseAI 相关）：

- **ADR-003（Capability × Industry 正交）**：行业能力包内部怎么实现（采样还是流）不影响 Capability 契约。反过来说：**如果视频流改造把 RTSP 细节泄漏到事件契约里（比如事件 payload 要求消费方处理帧序号），就违反了这条 ADR**。改造的边界画在"结构化事件输出"处。
- **ADR-004（MallSenseAI → LangChat AI Vision）**：MallSenseAI 定位为行业能力包的原料车间。产出物（detection_events/alerts）是未来 Capability 的数据底座——**视频流改造必须保持这个产出物 schema 的稳定性**。

**更硬的证据是 OpenSpec 的"沉默"**：扫了 `/root/MallSenseAI/openspec/specs/` 全部 29 个 spec（advanced-detectors、alert-workflow、on-demand-detection、vision-model-artifact-management……），**没有任何一个涉及 video / stream / rtsp / tracking**。规格层完全没有视频流的位置——这证实：视频流今天处于 roadmap 谈话层，连 spec 都还没立。今天的 Gap 分析是给未来立 spec 时的输入。

**AGENTS.md 的两个伏笔**：
1. `Camera.password_hash stores plaintext (needed for HTTP/RTSP auth to cameras)` —— **RTSP 凭据已经预留存储但从未使用**。数据模型层给视频流留了门。
2. 生产配置 `CUDA_VISIBLE_DEVICES` 留空 = CPU 推理 —— 部署形态锚定在截图负载上。

**域知识证据（legacy/）**：老系统的 RTSP 只出现在 `update_base_image.py`（换基线图时用 cv2.VideoCapture 试 4 种 RTSP URL 格式），主巡检链路从来是 HTTP 快照。**迁移到新平台时有意保留了快照路线**——这是设计选择，不是技术遗留。

---

## 5. 代码验证（只看关键结构）

| 文件 | 关键事实 | 对视频流的含义 |
|---|---|---|
| `backend/app/camera/adapter.py` | `CameraAdapter` ABC 核心方法就一个：`capture_snapshot() -> bytes`（单张 JPEG）。Dahua 实现按 10 个快照路径逐一尝试，httpx DigestAuth | **"截图世界观"写进了类型系统**。接口粒度是"一次一张"，流式需要的是"连续供给"。新 RTSP adapter 不是实现这个接口，是**新增一个平行的接口族**（`open_stream() -> AsyncIterator[Frame]`） |
| `workers/scheduler.py` | `_tick()` 每秒扫一次：到点（`next_run_at <= now`）且不 running 的摄像头才算 due → `_run_due_batch` 有界并发（默认 10） | 纯拉动模型。视频流需要的是**每路一个常驻消费者任务**，scheduler 的"到点触发"心智整体作废 |
| `workers/executor.py` | `InspectionExecutor.execute()`：一次采集、失败隔离、返回 `InspectionResult`；`BatchExecutor` 有界扇出 | 采集是无状态短任务；RTSP 会话是有状态长任务，失败恢复从"下个周期重试"变成"watchdog 重连" |
| `backend/app/core/config.py` | `alarm_interval_minutes: int = 1`（分钟级默认）+ `fire_smoke_check_interval_seconds: int = 15`（火灾场景秒级预设） | 同一配置文件两种时间尺度 = 采样率压力已现 |
| `workers/pipeline.py` `_process()` | 一张图顺序过三个 detector（obstruction_world → debris 兜底；fire_smoke；floor_cleanliness）→ 证据落盘 → 三次 `_persist_detections` | 全链无帧间状态，天然无锁。流式化后这里要插入 **Tracker 节点**，且三个 detector 的帧要共享同一 Track 空间 |
| `backend/app/rules/engine.py` | 自称 Stateless evaluator，"停留超时"靠 `cooldown_state.active_since` 跨快照累计 | 状态外置在截图频率下够用；tracking 后"停留时长"改由 Track 的时间戳直接给出（`track.last_seen - track.first_seen`），规则引擎输入结构要变 |
| `openspec/specs/`（29 个） | 无 video/stream/tracking 相关 spec | 视频流未进规格层 |
| `legacy/update_base_image.py` | RTSP URL 四格式尝试（Streaming/Channels/101 等） | 唯一的 RTSP 足迹，一次性运维脚本，非主链路 |

**数量级验证**（改造必要性的硬账）：
- 当前：21 路 × 每分钟 1 张 ≈ **0.35 次推理/秒**，CPU 分时复用绰绰有余
- 全流：21 路 × 25fps = **525 帧秒**，≈1500 倍。yolo11n CPU 单帧 ~200ms → 需要 ~105 个 CPU 核；GPU 单帧 ~8ms → 需要 ~4.2 核满载，还不算解码
- 中间态（RTSP 抽帧 1fps）：21 次推理/秒，GPU 轻松，CPU 勉强——**这是架构上自然的下一站**

---

## 6. 商业地产映射（MI CRE）

| 截图模式概念 | MI 商管场景 | 视频流对应 | 场景性质 |
|---|---|---|---|
| 保安每 2 小时巡场拍照 | 消防通道占用、堆物、脏污 | 监控中心 7×24 盯屏 | 状态 vs 事件 |
| 火灾 15 秒采样预设 | 消防早期告警窗口 | 烟火视频确认（降低误报） | 快变状态，已在向流滑动 |
| —（截图做不到） | **跌倒检测**（扶梯口/老人） | 跌倒是 2-5 秒事件，1 分钟采样捕获率 <10%，必须流 + Pose | 事件型 |
| —（截图做不到） | **客流统计** | 计数需要 Tracking（同一人不重复计），必须流 + ByteTrack | 事件型 |
| —（截图做不到） | **越界/闯入**（夜间禁入区） | 轨迹判定，必须流 | 事件型 |
| 单张证据图 | 整改通知单附照片 | 事件前后 10 秒剪辑（法务证据链更强） | 证据升级 |

**成本映射（MI CRE 预算视角）**：
- 截图方案：一台无 GPU 服务器跑 21 路，硬件成本 ≈ 1 万元级
- 全流方案：解码 21×1080p（软解每路吃 30-50% 单核）+ GPU 推理 + 带宽（21×3Mbps ≈ 63Mbps 入口），硬件 ≈ 10 万元级
- **决策框架**：每个新增视频场景算一笔账——跌倒检测防一单人身伤害诉讼（商场保险费率），客流统计支撑招商租金定价。**场景 ROI 决定要不要上流，不是技术决定。**（明天 Day5 的 Business Scene Matrix 正是干这个）

---

## 7. 与传统方案比较

从截图到视频流不是二选一，是一条**演进谱系**，四个站位：

| 维度 | A. 截图加密（现状+调参） | B. RTSP 抽帧（1-2fps） | C. 全流+GPU+Tracking（25fps） | D. 边缘智能盒子 |
|---|---|---|---|---|
| 改造量 | 零（调 interval） | 采集层+adapter，推理/规则不动 | 五层全改 | 零改造，买硬件 |
| 帧率 | 0.017fps/路 | 1-2fps/路 | 15-25fps/路 | 盒内全帧率 |
| 算力 | CPU 现状 | CPU/GPU 轻量 | GPU 必备（~1500×） | 边缘 NPU |
| 事件覆盖 | 快变状态（≥30s） | 慢事件（≥10s）+计数粗估 | 全事件型（跌倒/轨迹） | 全事件型 |
| 时延 | 分钟级 | 秒级 | 亚秒 | 亚秒 |
| 失败恢复 | 下周期自然重试（优雅） | watchdog 重连 | 断流重连+丢帧补偿（复杂） | 盒子自治 |
| 单路增量成本 | ≈0 | 低（复用现有服务器） | 高（GPU+带宽） | 中（每路一盒，~2000元/路） |
| 证据 | JPEG | JPEG 序列 | 剪辑片段 | 盒内剪辑 |
| 适合场景 | 消防通道/堆物/脏污 | 火灾确认、区域计数 | 跌倒/越界/客流精算 | 已有海康/大华体系的项目 |

**为什么谱系上 B 是下一站**：
1. 火灾 15s 预设说明业务已在推采样率上行，B 直接接住这个压力
2. B 保留了 `BaseDetector.detect(image_bytes)` 契约——**检测器零改动**，改造收敛在 adapter 层（AGENTS.md 明说 adapter 是隔离层）
3. B 攒下的流管理经验（重连/背压/会话）是 C 的前置课程
4. C 只在"确有事件型场景 ROI"时立项——用 D 的对比价压价

**为什么传统安防（海康/大华盒子）抢不走这个市场**：盒子卖的是"单路智能"，MallSenseAI 卖的是"巡检→告警→工单→通知"的**业务闭环**（alert lifecycle: pending→confirmed→resolved + 工单自动创建）。盒子的告警要人盯屏处置，MallSenseAI 的告警进物业工单流程。**竞争位在 L3-L4，不在 L1-L2。**

---

## 8. 架构师思考题（CTO 级）

**题 1（容量规划）**：MI 预算只批 1 块 RTX 4060（8GB），21 路摄像头要上跌倒检测（Pose 模型，比 yolo11n 重 3 倍）。请给出：fps×路数的抽帧矩阵里哪个组合可行？解码放 GPU（NVDEC）还是 CPU？你的方案检测时延和漏报率各是多少？

**题 2（故障域隔离）**：视频流 worker 和截图巡检 worker 部署在同一进程还是分开？考虑：RTSP 断流重连风暴（交换机重启，21 路同时重连）会不会饿死 asyncio 事件循环、拖垮原本健康的截图巡检？如果分开，ConfigWatcher 双进程模型（现有设计）还能复用吗？

**题 3（契约稳定性）**：按 ADR-003，Capability 契约必须不感知实现。如果未来 LangChat 侧同时消费截图时代的 `detection_events` 和流时代的 `track_events`，事件 schema 怎么设计才不破坏已有消费者？（提示：新增事件类型 vs 扩展 payload 的取舍；想想 ERP 里"新增单据类型" vs "加字段"的老决策）

**题 4（中间态的纪律）**：B 方案（RTSP 抽帧 1fps）上线后，火灾场景会不会把 interval 调到 0.2 秒"顺手用流当快照"？抽帧频率配置要不要设上限？谁管这个上限——代码、配置校验、还是 ADR？

---

## 9. 我的理解变化

**以前以为**：截图→视频流就是把 `capture_snapshot()` 换成 `cv2.VideoCapture`，加一个 GPU，主要工作量在模型部署。

**现在知道**：
1. 检测器契约（图进图出）**一行不用改**——改造全在上游（会话/时钟）和下游（轨迹/证据），这是 Day2 看到的"adapter 隔离"真正值钱的地方
2. 真正的断层是**拉动→推送的执行范式**：scheduler 的"到点才算 due"心智整体作废，系统时钟从 scheduler 手里交到摄像头手里
3. 帧量是 **1500 倍**不是"快一点"——这个数量级决定了 CPU→GPU 不是优化项是必选项（或者用抽帧策略把 1500 压回 21）
4. **B 方案（RTSP 抽帧）是被忽略的关键中间态**——它保留检测契约、只改采集层，且正好接住火灾 15s 采样的业务压力。演进谱系 A→B→C 比一步到 C 稳健得多
5. 竞争位不在 L1/L2（海康大华的地盘）而在 L3/L4（告警→工单→通知的业务闭环）——所以"什么时候上视频流"的决策变量是场景 ROI，不是技术成熟度

**与 Day2 的呼应**：Day2 说"截图不是妥协，是匹配"；今天补全了后半句——**匹配是动态的**。配置文件里的 15 秒火灾预设，就是"匹配"开始松动的第一道裂缝。

---

## 10. 明日连接 + Capability 谱系位置

**明天 Day5：Business Scene Matrix** —— 业务目标→视觉场景→Vision Capability→系统模块的四列映射，回答"哪个商业场景 ROI 最高"。今天的演进谱系（A/B/C/D）就是明天给每个场景标"需要站到谱系哪一级"的标尺。客流统计（L2 Tracking）和消防通道（L1 截图）会落在谱系两端，ROI 计算方式完全不同。

**今天知识在 Capability 谱系上的位置**：

```
Ontology → Domain Model → Capability → Skill
                          ↑
              vision.detection（L1，已有实现）
              vision.tracking  （L2，今天论证的空缺——未来 Capability 的候选位）
```

L2 改造对 Capability 契约透明（ADR-003），但 **L2 会催生新 Capability 候选**（people.flow.query / fall.alert.query）——这是 W13-D5（MallSenseAI 如何成为 LangChat 行业能力包）要正式接线的地方。

**周六 Day6 预告**：画 Vision Capability 五层图 + Business Scene Matrix，把本周四天（全景/链路/Detection 谱系/演进谱系）拼成一张图。
