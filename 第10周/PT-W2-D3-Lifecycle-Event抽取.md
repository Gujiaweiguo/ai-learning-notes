# PT-W2-D3：Lifecycle + Event 抽取

> 📅 Week 2 - Day 3（8/5）
>
> **并行轨道：Business Semantic Architecture（企业业务语义架构）**
>
> **本周目标**：从既有材料抽取 Ontology 语义构件，不另起炉灶。

---

## 今日主题：effect-registry.yaml 的 5 类冻结效应，能否构成 AI Agent 的推理骨架？

前两天抽取了 Entity/Identity 和 Relationship。今天进入第三个核心问题：**业务对象的状态如何变化，每次变化会波及什么？**

这是 AI Agent 最依赖的一层语义——它决定了 Agent 能否回答"A101 为什么不能出租"这类需要沿状态链推理的问题。

---

## 一、为什么 Lifecycle ≠ status 字段

在 MI 代码里，铺位有 `status` 字段（空置/已租/锁定/已退出），合同也有状态枚举。但这些数据库字段只记录**当前快照**，它们回答不了三个关键问题：

| 问题 | 数据库 status 字段能回答吗 | Lifecycle 模型需要补充什么 |
|------|---------------------------|-------------------------|
| 这个对象经历过哪些状态？按什么顺序？ | ❌ 只存当前值 | 状态机定义（State Machine）：状态节点 + 合法迁移路径 |
| 每次状态变化触发了什么业务后果？ | ❌ 无事件记录 | Event 声明：迁移发出什么事件、影响哪些目标类型 |
| 当前状态允许做什么、禁止做什么？ | ❌ 无约束声明 | 守卫条件（Guard）：迁移前置条件和不变量 |

**Ontology 视角的转变**：

```
以前：status 是一个字段值，代码 if-else 控制流转

现在：status 是 LifecycleVersion 的一个状态节点；
     迁移（Transition）是可声明的语义事实；
     每个 Transition 可以挂载 Effect 规则；
     Agent 可以读这些规则来推理，而不是逆向工程代码。
```

---

## 二、真实材料：effect-registry.yaml 的 5 类冻结效应

你的 `effect-registry.yaml` 已经把 5 类 Lifecycle Transition Effect 冻结为 v1.0。这不是理论练习——每一类都有域 ADR 或域矩阵证据支撑。

| effect_type | 语义 | 注册来源 | 典型场景 |
|---|---|---|---|
| `state-transition-effect` | 对象状态传播 | ADR-006 §4.2 初始注册 | 合同生效→铺位状态变更 |
| `occupancy-effect` | 资源占用变化 | ADR-006 §4.2 初始注册 | 合同/租赁生命周期导致资源占用状态变更 |
| `financial-effect` | 财务影响 | ADR-006 §4.2 初始注册 | 合同生命周期事件导致账单/应收生成 |
| `lead-conversion-effect` | 招商转化链推进 | 01 招商管理 §8.3 | 源阶段完成使下一类招商对象可创建或推进 |
| `maintenance-effect` | 维护/维修影响 | 05 运营管理 §8.3 | 工单状态迁移导致物料领用、费用归集 |

**架构判断**：这 5 类效应类型覆盖了五种业务模式——交易链、资源拓扑、CRM 转化、状态维护、主体生命周期。ADR-006 v5 已确认这是充分性边界——6 域验证（财务/合同/租赁/招商/运营/商户）没有出现需要第 6 类的域。

---

## 三、Lifecycle 抽取实战：以 Lease（租赁）为核心

结合 03 租赁管理域矩阵 §1.1 和 ADR-006 §4 的概念模型，我们来抽取一个完整的 Lifecycle。

### 3.1 资源状态机（七态 canonical）

03 租赁管理 §6 G1 确认了 baseline 七态为 canonical：

```
规划(planned)
  → 建立(created)
    → 可经营(available)
      → 预定(reserved)
        → 交付使用中(delivered/in-use)
      → 可经营(available)  [退定释放]
    → 暂停(suspended)
      → 可经营(available)  [恢复]
    → 退出(retired)
```

**关键迁移及其 Effect 声明**：

| 迁移（Transition） | 发出的 Effect 类型 | 目标对象类型 | 业务语义 |
|---|---|---|---|
| available → reserved | `occupancy-effect`（预定锁定） | Resource + Prospect | 招商锁定，其他人不可选；预定到期自动释放 |
| reserved → available | `occupancy-effect`（预定释放） | Resource | 解锁，恢复可经营 |
| available → delivered/in-use | `occupancy-effect`（合同占用） | Resource + Contract | 合同审批通过，铺位进入使用中 |
| delivered/in-use → available | `occupancy-effect`（退场释放） | Resource | 合同终止/退场完成，铺位空置 |
| any → suspended | `state-transition-effect` | Resource | 暂停经营（装修期锁定面积从出租率分母扣除） |
| any → retired | `state-transition-effect` | Resource | 退出经营（面积从出租率计算中移除） |

### 3.2 合同状态机（从 02 合同管理域抽取）

```
草稿(draft)
  → 已签(signed)
    → 生效(active)
      → 即将到期(expiring)
        → 已到期(expired)
          → 已终止(terminated)
    → 已作废(voided)
```

**关键迁移及其 Effect 声明**：

| 迁移 | 发出的 Effect 类型 | 目标对象类型 | 业务语义 |
|---|---|---|---|
| draft → signed | — | — | 签订动作本身不产生跨域影响 |
| signed → active | `occupancy-effect` + `financial-effect` | Resource + Bill/AR | 合同生效→铺位占用 + 账单生成 |
| active → expiring | — | — | 时间触发，Agent 可预警但不产生 effect |
| expiring → expired | `occupancy-effect` | Resource | 合同到期，铺位待释放（但需 inspection 完成才可用） |
| active/expired → terminated | `occupancy-effect` + `financial-effect` | Resource + Bill/AR | 终止→铺位释放 + 停止计费/清算 |
| signed → voided | `occupancy-effect` | Resource | 作废→释放预定/锁定 |

### 3.3 Event 声明：Agent 需要看到什么

ADR-006 §4.1 的概念模型告诉我们，每个 Transition 可以 emit（发出）BusinessEventType（遵循 ADR-002 §4 的四类来源词汇）：

| 事件来源分类 | 适用场景 | 真实例子 |
|---|---|---|
| `transition_emitted` | LifecycleVersion 内部迁移自然发出 | 合同 Signed→Active 发出 ContractActivated |
| `externally_observed` | 外部系统/域触发，本域观察 | 05 运营登记单触发资源状态推进 |
| `command_result` | 用户/Agent 命令执行的结果 | 招商执行预定命令→资源锁定 |
| `policy_derived` | 策略推导触发 | 预定到期 N 天未转正→自动释放 |

**Agent 的推理路径**（以"A101 为什么不能出租"为例）：

```
1. 查 Entity：定位 Resource A101
2. 查 Lifecycle：A101 当前状态 = delivered/in-use
3. 查 Relationship：A101 关联 Contract #2026-0888
4. 查 Contract Lifecycle：Contract 状态 = active
5. 查 Effect：signed→active 发出 occupancy-effect → Resource 被占用
6. 查 Rule：active 合同未终止前，资源不可重新出租
7. 输出结论：A101 被 Contract #2026-0888 占用，需先终止合同并完成退场
```

注意第 5 步——Agent 不是在读代码 if-else，而是在读一条**声明在 Transition 上的 Effect 规则**。这就是 Ontology 的价值。

---

## 四、Effect 声明的抽取模板

本周目标是抽取，不是设计。每发现一条 Lifecycle + Event，记录以下 7 项：

| 字段 | 示例：合同生效→铺位占用 |
|---|---|
| Source Concept | Contract |
| Source Lifecycle State | signed → active |
| Event Name | ContractActivated |
| Event Source Classification | `transition_emitted` |
| Effect Type | occupancy-effect |
| Target Object Type | Resource Unit |
| Evidence & Owner | 02 §8.2.5；03 §8.2.5；ADR-006 §8 |

**三条规则**（来自 ADR-006 §4.2）：

1. **不持有 `target_object_id`**：只声明类型级规则（"任一合同 Signed→Active 时，铺位类型变为 occupied"），不写具体实例 ID
2. **锚定到 Transition**：Effect 是迁移的属性，不是独立实体，没有自己的 ID 和生命周期
3. **effect_type 必须已注册**：只接受 effect-registry.yaml 中已冻结的 5 类，不接受随手新增

---

## 五、当前缺口诊断

对照 effect-registry.yaml 和域矩阵，Lifecycle + Event 层的缺口已经比较清晰：

| Ontology 维度 | 已有资产 | 缺口 | 对 Agent 的影响 |
|---|---|---|---|
| 状态机定义 | 资源七态 canonical（03 §6 G1）；合同状态枚举（02 §1.1） | 合同状态机尚未显式声明为 LifecycleVersion（含合法迁移路径 + 守卫条件） | Agent 无法判断"从 expired 能否直接回到 active" |
| 迁移→事件映射 | PRD §3.2 跨模块状态联动矩阵 L1932-1955 | 联动矩阵是产品视角的文档描述，不是 Ontology 可推理的规则声明 | Agent 需要读文档而非读模型 |
| Effect 类型覆盖 | 5 类冻结（effect-registry.yaml v1.0） | 类型覆盖充分（6 域验证），但每个 Transition 上具体挂了哪些 Effect 尚未系统化抽取 | Agent 知道"有哪几种效应"，但不知道"哪个迁移产生哪个效应" |
| 事件来源标注 | ADR-002 §4 四类来源词表 | 域矩阵中的事件尚未全部标注来源分类 | Agent 无法区分"迁移自然发出"vs"外部触发"vs"策略推导" |

**这些缺口正是 Week 4 要补的**——到时候会把今天抽取的结果升级为完整的 Event Model。

---

## 六、今天改变的设计判断

> **以前**：状态变化就是改 status 字段值，联动逻辑写在代码 if-else 里。
>
> **现在**：每个合法迁移及其后果是一份**声明式规则**。Effect 不指向具体实例，只声明类型级规则。Agent 可以读这些规则来推理"为什么不能出租"和"下一步该做什么"，而不需要逆向工程代码。

---

## 📝 练习（5 分钟）

选择"合同终止（active/expired → terminated）"这个迁移，写出 7 项抽取卡片。

然后回答：为什么 `occupancy-effect` 和 `financial-effect` 要分开声明，而不是合成一个 `termination-effect`？

**提示**：想想一个迁移可能影响多种目标对象类型——Agent 需要分别追踪"铺位状态变了"和"账单停止了"两条推理链。如果合成一个 effect，Agent 就丢失了这个区分能力。

---

> 明天进入 Rule 抽取：从 CRE BCM 域文件（01-06）的业务规则中，识别哪些已显式声明、哪些还埋在代码 if-else 里，以及 AI Agent 需要怎样的规则格式才能做推理。
