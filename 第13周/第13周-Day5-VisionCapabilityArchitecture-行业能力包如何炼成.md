# 🧱 LangChat 心智模型 | Week13-Day5
# 📌 Vision Capability Architecture：MallSenseAI 如何成为 LnkChat 的行业能力包？—— 为什么是"契约打包"不是"代码打包"？

> 术语说明：LangChat 已按 ADR-008 更名为 LnkChat，本文按 W12-D7 决议使用新名（首现标注），历史引用保持原文。
> 现状声明：MallSenseAI 今天**没有一行代码跑在 LnkChat 平台里**，LnkChat 的 capability catalog 里**没有任何 vision 条目**。今天回答的不是"现状如何"，而是"能力包"这个词在架构上的准确含义——答案在昨天 Day4 留下的三份接口清单里：capability 注册表、日级触发源、证据 digest。今天把它们拼成一张完整的集成架构图。

━━━ 1. 今日核心问题 ━━━

**MallSenseAI 如何成为 LnkChat 的行业能力包？**

这个问题里藏着一个更锋利的子问题：**"能力包"包的到底是什么？** 直觉答案是"把 MallSenseAI 的检测代码打包塞进 LangChat"——像 Dify 装插件那样。W8-D5 已经否定过"Capability 是 Plugin"，但那是能力粒度层面；今天是**产品粒度**的同一道题：一个完整的行业系统（backend + workers + 前端 + 775 测试）怎么"进"平台？

昨天思考题①的裁决今天揭晓：MallSenseAI 在 LnkChat 架构里**同时持有三个身份**，而三个身份分属三段——这不是身份冲突，这是三段式架构链（ADR-007）本来就允许的结构。**能力包的本质是"契约打包"：代码一行不动，动的是三份"纸"。**

━━━ 2. 人话解释（用 26 年 ERP 经验讲）━━━

Jason，你 26 年 ERP 里见过太多次"系统集成"，今天的答案你在 2005 年就知道了：

**MallSenseAI 想进 LnkChat 生态，不是"搬进来住"，而是"挂靠+开票"。**

你在 ERP 时代做的最成功的一次集成是什么？不是把 POS 系统代码抄进 ERP，而是**给 POS 定了接口规范**（销售下载、库存上传、对账文件格式），然后 ERP 的"外部系统注册表"里多了一行：系统名=POS，协议=文件，方向=双向。POS 的代码、数据库、厂商、发版节奏全部不动。**ERP 没有"拥有"POS，ERP 拥有的是对 POS 的"契约"。**

行业能力包一模一样，只是从"一个系统挂靠"升级成"一个产品线挂靠"，要签三份纸：

**第一份纸：能力清单（Capability 描述符）。** 相当于供应商的《服务目录+SLA》。`lnkchat.vision.kpi.query@v1` 说清楚：输入什么、输出什么、读还是写、要什么权限、要不要人审。**关键规矩：目录页上不许出现行业词**（ADR-003 硬约束）——"零售客流查询"不行，只能写"视觉 KPI 查询"。为什么？你在 ERP 里见过"华南区版应收模块"吗？模块按功能命名，区域是客户属性。同一个应收模块卖给华南华北；同一个 vision 能力卖给零售制造。

**第二份纸：产品定义（Application 元数据）。** 相当于**招商手册上的产品包页**。客户（业主/区域总）买的从来不是"POS 接口"，是"智慧收银解决方案"。Application 元数据就是这个产品包页：本产品由哪几个能力组成（capabilities 子集）、面向哪些行业（industries 标签）、叫什么名字（LnkChat AI Vision，ADR-004 已冻结命名）。**行业词只出现在这里**——产品包当然可以说"面向购物中心"，能力目录不行。

**第三份纸：接入凭证（Connector 配置）。** 相当于给 POS 开的接口账号+地址。Vision Runtime（MallSenseAI backend/workers）留在第三段当"企业系统"，LnkChat 通过 service account 调它的 detection_events / dashboard API。摄像头凭证、模型文件、GPU worker 全都不进平台。

**为什么这套对你毫不陌生？因为这就是 ERP 生态的"认证合作伙伴"模式。** SAP 不收购每家做条码的厂商，但 SAP 有认证目录：能力描述符=认证清单，Application=合作伙伴解决方案包，Connector=RFC 目标配置。LnkChat 做的是同一件事，只是把"人签的合同"变成了"代码可校验的描述符"—— frozen pydantic 模型，字段不可变，改一个 schema 必须升版本。**合同条款不能偷改，只能重签**——这是把商业世界的契约道德编译进了类型系统。

━━━ 3. LangChat（LnkChat）架构位置 ━━━

今天画的是**整个 Week 13 的收官图**——五层模型怎么"躺进"三段架构链：

```
ADR-007 三段式架构链（纵切）          MallSenseAI 的三个身份
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────┐
│ 段1 External Clients (L4)        │ ← 身份① L4 Application
│   Agent Host / SPA / IM 渠道     │    "LnkChat AI Vision"
│   ┌───────────────────────┐     │    产品+Vue门户+数字督导
│   │ L5 Vision Agent        │     │    （SkillRelease+数字员工，
│   │ （推理层住平台）        │     │      推理不留在视觉侧）
│   └───────────┬───────────┘     │
└───────────────┼─────────────────┘
                │ 调用能力（带 scopes/审批）
┌───────────────▼─────────────────┐
│ 段2 Capability Runtime (L2/L3)   │ ← 身份② Capability 提供方
│   ┌───────────────────────┐     │    （描述符注册进 catalog）
│   │ L3 Catalog:            │     │    lnkchat.vision.* 描述符
│   │ lnkchat.vision.detect  │     │    行业无关、版本化、frozen
│   │ lnkchat.vision.kpi.q   │     │
│   │ lnkchat.safety.alert.s │     │
│   └───────────┬───────────┘     │
│      runtime_binding 指向下行    │
└───────────────┼─────────────────┘
                │ Connector（service account）
┌───────────────▼─────────────────┐
│ 段3 Enterprise Systems           │ ← 身份③ 被连接的企业系统
│   ┌───────────────────────┐     │    Vision Runtime 本体
│   │ L1-L4 感知+指标系统     │     │    （backend 17 routers
│   │ capture→detect→rule    │     │     + workers 流水线
│   │ →alert→dashboard       │     │     + detection_events 库）
│   └───────────────────────┘     │    系统 of record，代码不动
└─────────────────────────────────┘
```

三个身份的裁决（昨天思考题①的答案）：**第一位身份是 L4 Application**——因为客户买的是它（ADR-002 §2.2.4：Application 是收费单元）；第二身份是段2 的 capability 提供方（描述符是平台资产）；第三身份是段3 的企业系统（数据主权留在视觉侧）。**身份不冲突，因为段位不同。** 一个系统可以同时是"产品、能力来源、数据源"，就像一个供应商可以同时是"解决方案伙伴、认证能力提供方、接口对接方"。

━━━ 4. ADR / 战略文档依据 ━━━

**① ADR-004（MallSenseAI → LangChat AI Vision）：这就是"能力包"的出生证明。** ADR-004 冻结的不只是改名，而是第一份 Application 元数据模板：`application.yaml` 里 `capabilities: [langchat.vision.detect@v1, langchat.knowledge.query@v1, ...]` + `industries: [retail, manufacturing]`。两个决定今天读来尤其锋利：(a) **行业词从产品名里清除**，`Mall` 不许出现在名字里，行业属性下沉到 `industries` 字段——所以扩展到工厂安全不用再改名；(b) **industries 是数组不是单值**——一个 Application 天然可以落在正交矩阵的多个 cell。注意细节：示例里的 `langchat.vision.*` 是 ADR-008 之前的写法，硬切换后今天注册的等价物是 `lnkchat.vision.*`（**文档示例没跟着改名走，这本身就是个 Gap**，见 §5）。

**② ADR-003（Capability × Industry 正交 facet）：包的内部结构法。** §2.2.3 明文：`Application = Capability 子集 × Industry 标签`，两个独立字段。§2.2.5：矩阵允许空 cell（某能力不适用某行业就留空，不强行填充）。这条规则保证了"包"是**从能力清单里挑+贴行业标签**组装出来的，而不是为每个行业复制一份代码。Capability ID 命名硬约束 `^lnkchat\.<domain>\.<verb>$`，`retail`/`mall` 出现在 ID 里一律拒绝。

**③ ADR-002（四级品牌层级）：包的商业身份。** L3 Capability 不直接对客户收费（计费单位是 license/调用量），L4 Application 才是收费单元与价值载体。推论到今天：**"行业能力包"不是一个技术组件，是一个 SKU**。它对内由 capabilities 组合，对外客户只看到产品包的能力清单——这正是为什么打包打的是元数据而不是代码。

**④ ADR-007（三段式架构链）：身份裁决的坐标系。** 没有这张图，"MallSenseAI 是什么身份"会吵成一团；有了它，答案变成查表：产品在段1、描述符在段2、Runtime 在段3。**ADR 的价值不是告诉你做什么，是让争论变得没必要。**

**⑤ capability-runtime-contract spec：包的调用纪律。** 段2 → 段3 的每次调用都是 credential-bound：tenant/workspace/scopes/hop origin 全部绑定到持久化凭证；async 调用返回 202 + durable execution id；发起者不能自批准自己的审批。这些纪律昨天说过是 Vision Agent 的治理底座，今天换个角度看：**它就是 Connector 那张"第三份纸"的法律条文**——Vision Runtime 接受的每个请求都带完整身份链，谁调的、以谁的名义、批没批。

**⑥ capability-gateway TOMBSTONE（反面教材）。** W01 BI 网关 2026-08-19 退役，owner 收敛产品线到 R001 唯一资产。教训对今天的映射：**别急着为"接入"发明中间层**。MallSenseAI 集成不需要新建 gateway——catalog + skill release + connector 配置已经是足够的中介。想加层之前先问：这层消解了什么变化率差异？答不上来就是 W01。

━━━ 5. 代码验证（只看关键结构）━━━

**① 平台侧：catalog 长什么样、离 vision 有多远——`lnkchat/capability/catalog.py`：**

```python
class CapabilityDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)   # frozen：契约不可变
    capability_id: str          # 正则 ^[a-z0-9]+(\.[a-z0-9]+)*$
    capability_version: str     # 正则 ^v[0-9]+$
    lifecycle: Literal["draft", "published", "deprecated"]
    input_schema: dict; output_schema: dict
    execution_mode: list[Literal["sync", "async", "stream"]]
    effects: Literal["read", "write", "destructive"]         # ← 今天的关键裁决点
    required_scopes: list[str]
    approval_policy: Literal["none", "runtime_human_approval"]
    provider: str
    runtime_binding: dict                                      # ← capability→段3 的绑定

_IMMUTABLE_FIELDS = frozenset({"input_schema", "output_schema", ...})
# 同 id@version 重注册且字段不同 → 冲突拒绝；契约变更必须升版本
```

`_register_p0_capabilities()` 里注册的全部能力：**只有 2 个**——`lnkchat.knowledge.query@v1`、`lnkchat.workflow.execute@v1`，全部 `provider="lnkchat"`、`runtime_binding={}`。**三个 Gap 立现**：(a) 没有任何 `vision.*` 条目；(b) 注册发生在 **import 时静态注册**，registry 是内存 dict——MallSenseAI 无法"自注册"，加一个视觉能力要改平台代码发版（注册表是代码不是数据）；(c) `runtime_binding` 是空 dict——**capability 怎么路由到段3 的 Vision Runtime，这个绑定关系还没建模**。

**② 平台侧：对外只有元数据查询面——`lnkchat/capability/routes/`：** 只有 `POST /list_capabilities` 和 `/describe_capability` 两个端点，注释明说"业务执行走 skill release（E6 迁移）"。即能力包的**消费路径**是：Skill → 编译 → Runtime 按 binding 调 Connector → Vision Runtime。今天 catalog 只是"菜单"，"厨房"（binding+connector）还没盖。

**③ Skill 层的治理交叉校验——`lnkchat/skill_release/descriptor.py`：** `effect_policy="conditional_write"` 强制要求 `human_review_gate != "none"`（模型级 validator）。注意两边词汇的差异：catalog 用 `effects: read/write/destructive`，skill 用 `effect_policy: read_only/conditional_write`——**两套 effect 词表还没对齐**，这是集成时要裁决的第四个小 Gap（昨天 Day4 提过 vision 侧的 effects 裁决，今天在代码里找到了它的双胞胎）。

**④ 视觉侧：现成可包的 API 面——MallSenseAI `backend/app/api/`：** 17 routers ≈80 endpoints。与能力包直接相关的现成面：`detection_events`（list / by id / evidence 图片 / export CSV）、`dashboard`（stats / alert-trend / confidence-distribution / worker-status）、`alerts`（list / evidence / export / workflow 确认链）。**段3 的"接口原料"是齐的**，缺的是段2 的三份纸。

**⑤ 一个漂亮的隐喻藏在基础设施里：** MallSenseAI 的库 `mallsenseai` 和 LnkChat 的库 `lnkchat` **住在同一个 postgres16 容器里**（MallSenseAI AGENTS.md 明文）。物理同居、逻辑分居——两套独立的库、独立的凭证、独立的迁移。这正是整个集成架构的微缩模型：**共享机房，不共享账本。**

━━━ 6. 商业地产映射 ━━━

| LangChat/LnkChat 概念 | MI CRE（商业地产运营）对应物 |
|---|---|
| 行业能力包（Application） | **业态专线系统产品包**：客流统计系统、停车诱导系统——MI 中台不吞并它们，它们也不自建报表门户，按集团数据规范接入 |
| Capability 描述符 | 供应商《服务目录+SLA》：提供什么、读/写、响应模式、审批要求——**目录页禁止写"华南区专用"**（行业词不入 ID） |
| `industries` 标签 | 招商手册上的"适用业态"：同一套客流系统，购物中心标签是 retail，产业园区标签是 logistics——**系统不复制，标签多贴一张** |
| immutable + versioned 契约 | 合同条款变更必须重签：v1 接口加了字段就是 v2，存量客户按自己节奏升级（对应 ADR-008 ReleaseChannel 灰度） |
| Connector 配置 | 给专线系统开的接口账号：地址+凭证+方向。摄像头密码、模型权重绝不进 MI |
| L4 Application 是收费单元 | 业主采购的是"AI 视觉运营包"这个 SKU，不是 80 个 API |
| catalog 静态注册（现状 Gap） | 供应商目录要改 ERP 源码才能加一行——每次新签供应商都发一次版，荒谬但正是现状 |

**给 Jason 的一句话**：你在 MI 里做过的最正确的决定，就是没有把停车系统、客流系统、POS 的数据库并进 MI 库。今天 LnkChat 对 MallSenseAI 做的是同一个决定的 AI 版——**拥有契约，不拥有代码**。

━━━ 7. 与传统方案比较 ━━━

**MallSenseAI 怎么"进"平台？三个方案：**

| 方案 | 做法 | 为什么不行 |
|---|---|---|
| **A. 独立产品并列**（现状延续） | MallSenseAI 自带门户+告警+报表，LnkChat 只是"隔壁另一个系统" | 数据孤岛：视觉事实进不了数字员工的知识面；双份用户/权限/通知体系；无法进平台 license 计费；客户看到两个品牌两个报价单 |
| **B. 代码合并**（平台长出视觉模块） | 把 backend/workers 抄进 LnkChat 仓库，成为 `lnkchat/vision/` 包 | 违反 ADR-003 精神（平台核心装行业能力=为每个行业复制平台）；变化率焊死：检测模型周级迭代 vs 平台月级发版；故障域合并：GPU OOM / torch 依赖冲突打挂平台 API；775 个测试和平台测试互相拖累 CI |
| **C. 契约打包（ADR-004 事实选择）** | Runtime 留段3（代码不动）；描述符注册段2 catalog；Application 元数据打包段1；推理（L5）住平台 Skill 层 | 需要补齐今天列出的 5 个 Gap——但每个 Gap 都该补（注册表数据化、binding 建模、connector 落地本来就是平台欠的债） |

**Plugin（Dify 式）为什么连方案列表都进不了？** Plugin 是**代码级**扩展：插件进程跑在平台里，共享平台依赖与故障域。YOLO/torch 的 CUDA 依赖会污染平台 venv；一个插件内存泄漏拖垮整个平台。Capability 是**契约级**注册：Runtime 在段3 独立部署、独立发版、独立故障，平台只持有它的"服务目录页"。**Plugin 把别人请进自己家，Capability 和对方签互访协议**——企业级集成的全部区别就在这一句。

━━━ 8. 架构师思考题 ━━━

**① 粒度题**：段3 有 ~80 个 endpoint、3 类 detector、5 个规则模板。`lnkchat.vision.*` 该注册几个能力？候选光谱：一端是 `lnkchat.vision.query`（一个 god API 收编全部查询），另一端是按 endpoint 逐个注册（粒度爆炸）。裁决工具是什么——按"动词+读什么"切（detect/kpi.query/alert.summary 三个）？还是按"消费场景"切（日报要的数据包成一个、大屏要的包成一个）？**提示：回想 ADR-003 的命名公式 `lnkchat.<domain>.<verb>`——domain 是"视觉"还是"安全/运营"两个 domain，本身就是一个裁决。**

**② effects 语义题**：`lnkchat.vision.detect`（on-demand 触发抓拍+GPU 推理）的 effects 该标 `read` 还是 `write`？它不写业务数据，但消耗 GPU 算力、写检测缓存、可能被滥用刷爆推理队列。"对业务系统的副作用"和"对平台成本的产生"是两个维度，catalog 只有一个字段。**要不要拆成 `effects` + `cost_class` 两个字段？谁付钱——调用方租户还是 Application 供应商？**

**③ 双行业灰度题**：`lnkchat.vision.detect@v1` 同时服务 retail 和 manufacturing。制造业客户要"安全帽检测"导致 output_schema 必须加字段。改 v1（违反 immutable）还是发 v2（零售客户凭什么被迫升级）？ReleaseChannel/TrafficPolicy（W9-D4）挂在 Deployment 上——**capability 版本的灰度和 application 版本的灰度是同一层还是两层？三个维度（capability 版本 × application 版本 × 行业客户群）怎么摆才不会组合爆炸？**

━━━ 9. 我的理解变化 ━━━

**以前以为**："行业能力包"是把 MallSenseAI 的代码以模块/插件形式装进 LangChat——包 = 代码包，集成 = import。担心的问题是"怎么处理 torch 依赖冲突、怎么同步发版"。

**现在知道**：① 能力包 = **元数据包**。代码一行不动（Runtime 留段3），动的是三份纸：Application 元数据（capabilities × industries）、Capability 描述符（注册进段2 catalog）、Connector 配置（段3 接入凭证）。"打包"打的从来是契约，不是代码；② MallSenseAI 的三个身份（段1 产品 / 段2 能力提供方 / 段3 企业系统）**不冲突，因为段位不同**——以前觉得"一个系统三个身份"是架构混乱，现在明白三段式链的价值恰恰是让多身份各就各位、可同时成立；③ 真正的集成债不在 MallSenseAI 侧（它的 API 面是齐的），在平台侧：**catalog 静态注册（代码不是数据）、runtime_binding 空建模、connector 缺位**——这三件事不做，任何行业系统都"进不来"，MallSenseAI 只是第一个撞上这堵墙的。

━━━ 10. 明日连接 + Semantic Layer ━━━

**明天 D6（周六，动手交付）：Vision Capability Inventory + Vision Technology Radar + 演进路线图。** 今天 §8-① 留下的粒度光谱明天逐项盘点：把段3 的 80 endpoints × 3 detectors × 5 规则模板 × dashboard 全部过一遍，按今天确立的 `lnkchat.<domain>.<verb>` 公式产出能力清单（含 effects/scopes/approval 建议值），叠加 W12 的技术雷达，排出前 3 个 Sprint。**今天画的集成架构图就是明天 Inventory 的评分框架。**

**今天知识在 Semantic Layer 链上的位置**：

```
Ontology（商业地产运营本体：通道占用/烟火/排队是"运营事实"）
  → Domain Model（CapabilityDescriptor / Application 元数据 / DetectionEvent…
      —— 今天新增的两个"契约对象"就住在这层）
    → Capability（lnkchat.vision.detect / lnkchat.vision.kpi.query /
      lnkchat.safety.alert.summary ← 今天定义的候选，明天盘点）
      → Skill（视觉日报 / 督导对话，绑数字员工 = L5 推理层）
        → Application（LnkChat AI Vision = 能力包本体 = 收费 SKU）
```

Week 13 的五个工作日到此闭环：L1-L5 的纵向深度（Day1-4）+ 三段链的横向归属（今天）。**五层模型不再是悬空的金字塔，而是嵌进平台架构链的器官图**——明天开始盘点这个器官里实际有多少肌肉。
