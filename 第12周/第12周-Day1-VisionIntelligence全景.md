# 🧱 LangChat 心智模型 | Week12-Day1

## 📌 主题：Vision Intelligence 全景 — 为什么 MallSenseAI 不是 CV 项目？

日期：2026-08-17（周一）| 阶段：Week 12 开篇（Vision Intelligence 能力地图）

━━━ 1. 今日核心问题 ━━━

**为什么 MallSenseAI 不是 CV 项目？**

传统视角：MallSenseAI 用 YOLO 检测障碍物/火灾 → "这是个计算机视觉（CV）项目"。
架构视角：检测只是 L1（Image Understanding）的工具。产品的真正链路是：
**Detection → 规则判定 → 告警生命周期 → 工单闭环 → 通知触达 → 管理控制台**。
CV 只占这条价值链的前 1/5。如果它是 CV 项目，做完检测就结束了；但它的核心资产是「检测之后的业务闭环」——这正好是 ERP 人的直觉。

━━━ 2. 人话解释 ━━━

Jason 你 26 年做 ERP，见过太多"进销存项目"最后活成"报表项目"。
MallSenseAI 的道理一样：

- **CV 项目** = 交付一个"能识别的模型"（一次性交付，价值在算法精度）
- **MallSenseAI** = 交付一个"能运转的巡检业务"（持续运行，价值在闭环）

它更像你做过的 MES/安防巡检系统：摄像头是传感器，YOLO 是"质检员眼睛"，规则引擎是 SOP，告警→工单→通知是异常处理流程（很像 ERP 的审批流），管理控制台是运营驾驶舱。
**模型会过时，闭环不会。** 客户续费的原因从来不是"YOLO 精度 92%"，而是"消防通道被堵 10 分钟内有人去处理"。

━━━ 3. LangChat 架构位置 ━━━

在 LangChat 三层架构（ADR-007）中：

```
平台层  LangChat（企业 AI 应用平台）
行业层  MallSenseAI = LangChat AI Vision（视觉智能行业能力包，ADR-004）
应用层  商管系统 / MI / CRM（业务消费）
```

注意 ADR-004 已把 MallSenseAI 对外更名为 **LangChat AI Vision**：`Mall`（行业词）从产品名中移除，行业属性下沉到元数据 `industries: [retail, manufacturing]`。这印证了它不是"商场 CV 项目"，而是**可跨行业复制的视觉能力应用**（制造业产线安全是 P1 适配对象）。

━━━ 4. ADR 依据 ━━━

- **ADR-003（Capability × Industry 正交 facet）**：能力不带行业词（禁止 `langchat.retail.*`），行业是应用层标签。`vision.*` Capability 可跨零售/制造复用；MallSenseAI 的能力（如未来的 `langchat.vision.detect@v1`）+ `industries: [retail, manufacturing]` = 矩阵中的打包结果。
- **ADR-004（MallSenseAI → LangChat AI Vision）**：重命名只改对外品牌，不动代码模块名（保护既有契约）；Application 不锁定单一行业。
- **MallSenseAI PRD 导读**（关键事实）：产品已成熟（775+ 测试、40 e2e、真实 4 层商场部署），但**当前是封闭系统**——不与 LnkChatBI/OrchestratorAgent/langchat 互连，**无 capability 暴露**。这正是 Week 13 要解决的集成路径问题。

━━━ 5. 代码验证 ━━━

MallSenseAI 代码结构验证（只看关键结构）：

```python
# backend/app/detectors/base.py
class BaseDetector(abc.ABC):
    @property
    @abc.abstractmethod
    def is_enabled(self) -> bool: ...
    async def detect(self, image_bytes, roi_polygons, ...) -> ...
```

- 4 个检测器：DebrisDetector（YOLO 障碍物）/ FireSmokeDetector / YOLO-World（零样本）/ FloorCleanliness（图像对比）
- 完整流水线：`workers/pipeline.py`：capture → detect → persist（detection_events 审计）→ rule → alert
- 告警闭环：pending → confirmed → resolved / false_positive；确认后自动建工单
- 但：**没有任何 `capability` 目录或注册表**——代码证实了 PRD 的判断：封闭系统，能力未外露。

━━━ 6. 商业地产映射 ━━━

| MallSenseAI 概念 | MI CRE 场景 |
|---|---|
| 检测器（Detector） | 楼宇传感器/巡检员眼睛 |
| 规则引擎（5 模板包） | 物业 SOP（消防通道管理制度） |
| Alert → WorkOrder 闭环 | 工程部异常处理流程（报事-派单-销项） |
| 通知渠道（企微/短信/邮件） | 物业值班体系 |
| DetectionEvent 审计 | 商场运营台账（合规证据链） |

对 MI CRE 的启示：视觉巡检的价值不在"看见"，而在"看见之后的管理动作"。这和你做商业地产运营系统的核心逻辑完全一致。

━━━ 7. 与传统方案比较 ━━━

| 方案 | 交付物 | 价值形态 | 复购逻辑 |
|---|---|---|---|
| 传统 CV 项目 | 模型+Demo | 算法精度 | 项目制，一次性 |
| 安防集成商方案 | 摄像头+NVR | 硬件+录像 | 事后查证 |
| **MallSenseAI** | 平台+闭环 | 业务结果 | 订阅制，持续 |
| **LangChat AI Vision（目标态）** | Capability 包 | 可编排能力 | 平台生态位 |

关键差异：集成商方案是"事后取证"（出事查录像），MallSenseAI 是"事中拦截"（堵住 10 分钟内处理）。但当前缺最后一环——**能力没暴露成 Capability，无法被上层编排**。

━━━ 8. 架构师思考题 ━━━

如果 MallSenseAI 要成为 LangChat AI Vision（行业能力包），它应该暴露什么粒度的 Capability？

A. `vision.detect@v1`（传图返回检测结果）——太细，调用方要自己懂 CV
B. `safety.alert.query@v1`（查告警）+ `safety.alert.subscribe@v1`（订阅事件）——业务级
C. 整个 MallSenseAI 作为一个 Agent——太粗，无法被编排

我的倾向：B 为主 + 少量 A。PRD 的 P1 建议也是 `safety.alert.query` 方向。但你想想：如果制造业客户要"产线安全巡检"，B 够用吗？还是需要 `vision.rule.configure@v1` 这种配置类能力？（本周六画五层图时给出你的答案）

━━━ 9. 我的理解变化 ━━━

以前以为：MallSenseAI 是一个"AI 视觉检测项目"，核心资产是 YOLO 模型和检测精度。
现在知道：它的核心资产是**检测之后的业务闭环**（规则→告警→工单→通知），检测只是入口。而且它当前最大的架构事实是"封闭"——已成熟但无 capability 暴露。更名为 LangChat AI Vision 是平台化转型的第一步信号：从"商场项目"到"跨行业视觉能力应用"。

━━━ 10. 明日连接 + Semantic Layer ━━━

明日（Day2）：**MallSenseAI 仓库精读** — Pipeline/Detectors/Rules/Alerts/Workers 全链路，回答"为什么当前是定时截图而不是视频流？"

Semantic Layer 位置：今天是 Part 2 的开篇——从 LangChat 的 Ontology → Domain Model → Capability 链条，切换到 Vision Capability 五层模型（L1 Image Understanding → L5 Vision Agent）。MallSenseAI 当前站在 L1-L2 之间（定时截图=离散帧的 L1），未来走向 L4 Business Intelligence（运营 KPI）和 L5 Vision Agent（自动分析→建议→日报），后者才是与 LangChat Agent 体系汇合的地方。
