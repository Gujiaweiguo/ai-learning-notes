# PT-W3-D3：Ontology 如何约束 Agent 认知 — Bounded Context = Agent 认知边界

> 📅 Week 3 - Day 3 | 2026-08-12 周三
>
> **并行轨道：Business Semantic Architecture**
>
> **今日主题：Bounded Context 作为 Agent 的认知围栏**

---

## 一句话开篇

> **如果 Agent 什么都能看、什么都能做，它就什么都做不好。Bounded Context 就是给 Agent 画一道认知围栏——你在哪个 Context，你就只理解这个 Context 的语义。**

昨天讲了 Ontology Compiler：把业务语义编译成 Agent 可消费的能力组合。今天要回答一个更深层的问题：

**编译出来的能力，应该在什么范围内被理解和执行？**

答案藏在你已经做的东西里：**MI Domain Model 的 17 个 Bounded Context + Context Map**。

---

## 二、为什么 Agent 需要认知边界？

### 先看一个反例

假设你有一个"全能管家 Agent"，它能同时处理招商、合同、账单、收款、发票、凭证——全部 17 个 Context。

问它一个问题：

> "A101 铺位的租金算出来了吗？"

一个没有认知边界的 Agent 会怎么想？

```
嗯，A101 是铺位……铺位在 Asset Foundation 里……
租金要查合同条款……合同在 Contract Lifecycle 里……
算费在 Billing & AR 里……
收款了吗？在 Collection 里……
开发票了吗？在 Tax Invoice 里……
凭证推了吗？在 Accounting Bridge 里……
等等，A101 的 Occupancy 状态是什么？在 Lease/Occupancy 里……
营业额采集了吗？在 Operations 里……
```

**这恰恰是今天 LLM-based Agent 的典型困境**：它试图同时持有所有上下文，结果注意力被稀释，关键推理链条被淹没在信息噪音里。

### Ontology 视角的解法

```
不是给 Agent 整个企业，
而是给它一个"工位"。

工位 = Bounded Context + 该 Context 内的 Entity / Rule / Lifecycle / Capability

Agent 在自己的工位上干活，
需要跨 Context 协作时，
走 Context Map 定义的"协作通道"。
```

这就是 **Bounded Context = Agent 认知边界** 的含义。

---

## 三、用你的 MI Domain Model 重新理解

### 3.1 你的 17 个 Context = 17 个"Agent 工位"

读 MI Domain Model §2 Context Coverage Matrix：

| # | Context | Agent 认知范围 | Agent 不需要懂的 |
|---|---|---|---|
| 01 Asset Foundation | 空间身份、层级、物理状态 | ❌ 租赁、计费、商户信用 |
| 02 Merchant | 商户身份、资质、经营状态 | ❌ 空间物理信息、算费规则 |
| 03 Leasing Pipeline | 线索→商机→报价→意向→条件报批 | ❌ 合同条款细节、账单执行 |
| 04 Contract Lifecycle | 合同、条款、模板、变更、终止 | ❌ 算费执行、收款核销 |
| 05 Lease/Occupancy | 占用生命周期、可用性判断 | ❌ 合同条款定义、资金流 |
| 06 Billing & AR | 计费、应收、账单 | ❌ 条款定义、收款执行 |
| 07 Collection & Settlement | 收款、核销、保证金/预存款资金流 | ❌ 发票、凭证 |
| 08 Tax Invoice | 发票生命周期、税控对接 | ❌ 凭证、收款执行 |
| 09 Accounting Bridge | 凭证生成、公司分流、外部对接 | ❌ 完整总账 |
| 10 Operations Management | 营业额采集、营运巡检、经营观察 | ❌ 计费执行、工单分派 |
| ... | ... | ... |

**每个 Context 的"不负责"清单，就是 Agent 的认知围栏。**

你的 Domain Model §5 里每个 Context 都有明确的"不负责"声明。以前你以为这是文档规范，**现在用 Ontology 视角看：这就是 Agent 的认知约束声明**。

### 3.2 Context Map = Agent 协作协议

读 MI Domain Model §4 Context Map。你已经定义了五种 Context 间关系类型：

| 关系类型 | MI Domain Model 案例 | Agent 协作含义 |
|---------|---------------------|---------------|
| **Upstream/Downstream** | Asset Foundation → Lease（空间身份供给） | 资产 Agent 向租赁 Agent 提供 Resource ID，不主动推送 |
| **Handoff**（业务交接） | Leasing → Contract（招商→签约） | 招商 Agent 完成条件报批后"交棒"，合同 Agent 接力 |
| **Shared Kernel**（共享内核） | Resource ID / Merchant ID / Effect Registry | 所有 Agent 共享的身份语言，像员工共用一套工号系统 |
| **Anti-Corruption Layer**（反腐层） | Accounting Bridge → 外部财务系统 | 凭证 Agent 对接外部系统时，不让外部模型"污染"内部语义 |
| **Customer/Supplier** | Contract → Billing（条款→算费） | 合同 Agent 是 Supplier，账单 Agent 是 Customer |

**关键洞察：你的 Context Map 本质上就是一张 Agent 协作拓扑图。**

---

## 四、核心概念：Bounded Context 作为语义容器

### 4.1 一个 Bounded Context 包含什么？

```
Bounded Context = 语义容器

├── Entity 定义（什么对象存在）
├── 不变量（什么规则永远成立）
├── Lifecycle / 状态机（对象如何演化）
├── Capability（这个 Context 能做什么）
├── Context Map 关系（与谁协作、怎么协作）
└── 不负责清单（不做什么——认知围栏）
```

以 **Contract Lifecycle** 为例：

```
Contract Lifecycle Bounded Context

├── Entity: Contract, Contract Clause, Contract Template
├── 不变量:
│   ├── 条款定义归此，算费执行归 Billing
│   ├── 合同审批→触发 Lease/Billing/Merchant（跨域 effect）
│   └── 状态五态封闭：未生效/使用中/已终止/已结束/已作废
├── Lifecycle: Draft → Approved → Active → Terminated/Expired/Voided
├── Capability: 创建合同 / 变更合同 / 终止合同 / 清算
├── Context Map:
│   ├── ← Handoff from Leasing Pipeline（条件报批→合同）
│   ├── → Handoff to Lease/Occupancy（合同生效→占用）
│   ├── → Upstream to Billing（条款→算费）
│   └── ← Upstream from Merchant（商户身份引用）
└── 不负责:
    ├── ❌ 算费执行（归 Billing）
    ├── ❌ 资金流（归 Collection）
    └── ❌ 商户身份真值（归 Merchant）
```

### 4.2 对 Agent 来说这意味着什么？

一个"合同管理 Agent"（或 Digital Employee）只需要理解 Contract Lifecycle Context 的语义。它：

- ✅ **能做**：创建合同、审批合同、变更合同、终止合同
- ✅ **知道**：合同有哪些状态、什么条件触发什么迁移
- ✅ **知道**：合同审批通过后要通知 Lease 和 Billing（effect）
- ❌ **不需要懂**：账单怎么算（那是 Billing Agent 的事）
- ❌ **不需要懂**：铺位物理信息（那是 Asset Agent 的事）
- ❌ **不能做**：直接修改商户信用（那是 Merchant Agent 的事）

---

## 五、商业事实唯一来源 = Agent 不能造谣

### D-014 原则的 Agent 语义

读 MI Domain Model D-014：

> **任何业务事实只能有一个 Owner Context。其他 Context 只能引用或消费，不能复制或产生第二真值。**

| 业务事实 | 唯一 Owner | Agent 含义 |
|---------|-----------|-----------|
| 营业额采集证据 | Operations | 账单 Agent 可以消费它计费，但不能自己"发明"一个营业额数字 |
| 合同条款 | Contract Lifecycle | 账单 Agent 消费条款执行算费，但不能自己定义"租金应该是多少" |
| 商户身份 | Merchant | 所有 Agent 只能引用 Merchant ID，不能在自己的 Context 里存一份商户副本 |
| 空间资源身份 | Asset Foundation | 合同 Agent 引用 Resource ID，不能自己定义铺位 |

**用 Agent 的话来说：每个 Agent 只能在自己的管辖范围内"说话"（产生业务事实），跨范围只能"引用"别人的话。**

这就是 D-014 的 Agent 约束语义：**防止 Agent 造谣**。

如果一个 Agent 同时持有合同和商户信息，它可能会"推断"出商户的某种新属性并存下来——这就是第二真值的产生。Bounded Context 边界 + D-014 约束联合确保：**Agent 在自己的边界内是权威，跨边界只是消费者**。

---

## 六、Handoff 关系 = Agent 交接协议

你的 Domain Model §4.5 定义了一种特殊关系：

> **Handoff** = 上游 Context 完成一个业务阶段后，将业务对象连同上下文移交给下游 Context 继续推进。上游不再拥有该对象的后续生命周期。

### Agent 视角

```
招商 Agent（Leasing Pipeline）
  │
  │ "条件报批已通过，这是审批结果"
  │
  ▼  Handoff
合同 Agent（Contract Lifecycle）
  │
  │ "合同已审批，这是合同信息"
  │
  ▼  Handoff
占用 Agent（Lease/Occupancy）
  │
  │ "铺位状态更新为 Occupied"
  │
  ▼  Upstream/Downstream
账单 Agent（Billing & AR）
```

**Handoff 不是 API 调用，是所有权转移。** 交接之后，上游 Agent 不再管这个对象。这跟人之间的岗位交接完全一样：招商经理谈完客户、签完意向，后面是合同专员的事。

### 对 Digital Employee 设计的影响

如果你要设计一个"招商运营数字员工"，它不需要从线索一路管到收款。它管的是：

```
招商运营 Digital Employee
  ├── 管辖 Context: Leasing Pipeline + Lease/Occupancy
  ├── 能做: 线索管理 / 报价 / 意向跟进 / 占用状态查询
  ├── 协作: Handoff → Contract Agent（条件报批交接）
  └── 不做: 合同审批 / 算费 / 收款 / 凭证
```

**Bounded Context 边界直接定义了 Digital Employee 的职责边界。**

---

## 七、反腐层（ACL）= Agent 的免疫系统

MI Domain Model §4.4：

> MI 对接外部财务系统（EAS/用友/SAP）时，Accounting Bridge 作为 ACL，不泄露外部财务模型到 MI 内部。
> MI 对接税控系统（航信/百旺/票通）时，Tax Invoice 作为 ACL。

### Agent 视角

外部系统是"异世界"——有自己的语言、规则、数据格式。如果 Agent 直接对接外部系统，它的认知模型会被污染。

```
外部财务系统（EAS）
  │ 用的是：总账科目、核算维度、凭证模板
  │
  ▼  Anti-Corruption Layer
Accounting Bridge Agent
  │ 翻译成：Accounting Entry、CompanySplit、EntrySource
  │
  ▼  内部语义
其他 MI Agent
```

**ACL Agent 的职责**：做翻译官，不让外部语义渗透到内部。就像公司财务部对接税务局的人——财务部翻译官把税务语言转成公司内部语言，不让税务规则直接渗透到业务部门。

---

## 八、Ontology 约束的三个层次

把今天的内容拉到全景：

```
Agent 认知约束（三层围栏）

第一层：Bounded Context 边界
  "你属于哪个工位，你就只看那个工位的东西"
  → 定义 Agent 的认知范围

第二层：D-014 商业事实唯一来源
  "别人的事实你只能引用，不能复制或篡改"
  → 定义 Agent 的数据主权

第三层：Context Map 协作关系
  "需要协作时走规定通道，不能翻墙"
  → 定义 Agent 的协作协议
```

**三层围栏合在一起 = Agent 的行为宪法。**

没有第一层，Agent 信息过载。
没有第二层，Agent 数据混乱（多真值冲突）。
没有第三层，Agent 协作失控（谁知道该找谁？）。

---

## 九、与主线的连接思考

| 主线（Code Reality） | 并行轨道（Ontology 约束 Agent 认知） |
|---------------------|-------------------------------------|
| MI 代码是 307 表 + Go 模块化单体 | Bounded Context 边界在代码中怎么体现？模块边界 = Context 边界？ |
| Connector 现状盘点 | Connector 就是 ACL 的代码实现——它在做翻译 |
| Gap Matrix（理想 vs 现实） | 理想：Context 边界清晰；现实：跨模块直接查表 |

**连接思考**：你的代码现实 Gap，很大程度上就是"Bounded Context 边界在代码层未严格执行"的 Gap。模块化单体是物理近似，但语义边界可能已经模糊——比如 Billing 直接读 Contract 的字段，而不是通过 Context Map 定义的 Upstream/Downstream 接口。

---

## 十、架构师视角

**以前**：17 个 Context 是领域建模的组织工具，帮我划分模块边界。

**现在**：17 个 Context 是 Agent 的认知围栏。未来设计 Digital Employee 时，**第一步不是想"这个 Agent 能做什么"，而是想"这个 Agent 属于哪些 Context"**。

Context 边界定了，Agent 的能力范围、协作对象、数据权限就全定了。这跟人类组织的岗位设计原理完全一致——先定岗位归属哪个部门，再定岗位职责。

---

## 十一、练习（5 分钟）

拿出你的 MI Domain Model §4 Context Map，回答：

1. **如果你的每个 Bounded Context 是一个独立 Agent，哪些 Context Map 关系会变成 Agent-to-Agent 的消息协议？**
2. **Leasing Pipeline → Contract 的 Handoff 关系，如果用 Agent 语言描述，"交棒"时传递的数据载荷是什么？**（提示：看 Domain Model §3 里 Leasing Pipeline 的对象和 Contract 的对象，谁是通过 Handoff 进入 Contract 的？）
3. **Operations Management 拥有 Revenue Evidence（D-014）。如果 Billing Agent 需要营业额数据来算提成租金，它怎么获取？直接查表？还是通过某种语义协议？**

> 思考这些问题的目的：**让你的 Context Map 从"文档里的架构图"变成"Agent 运行时的协作协议"。**

---

## 本日小结

| Ontology 概念 | MI Domain Model 对应 | Agent 含义 |
|--------------|---------------------|-----------|
| Bounded Context | 17 个 Context | Agent 认知围栏 |
| Context Map | §4 五种关系类型 | Agent 协作拓扑 |
| 商业事实唯一来源（D-014） | §0 D-014 裁定 | Agent 不造谣约束 |
| Handoff | §4.5 业务交接 | Agent 所有权转移协议 |
| Anti-Corruption Layer | §4.4 外部系统对接 | Agent 免疫翻译层 |
| 不负责清单 | §5 每 Context 末尾 | Agent 能力排除清单 |

**一句话总结**：

> **Bounded Context 不是"代码怎么分模块"，而是"Agent 该知道什么、不该知道什么"。你的 Domain Model §2 + §4 + §5 + D-014，合在一起就是一张 Agent 认知宪法。**
