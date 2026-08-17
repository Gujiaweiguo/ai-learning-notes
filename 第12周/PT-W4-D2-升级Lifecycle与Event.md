# PT-W4-D2 · 升级 Lifecycle + Event：从状态字段到可推理的状态机

> 日期：2026-08-18（PT-W4 Day 2）｜毕业作品《MI CRE Enterprise Semantic Model v0.1》第二层
>
> 真实材料：effect-registry.yaml（v1.0 冻结，5 类）+ ADR-006 §4 Lifecycle Transition Effect + MI Domain Model v1.0 §3 Lifecycle Owner / §6 状态机

---

## 一、毕业作品进度

```
D1 ✅ Ontology Model（Entity + Identity + Relationship，语义动词命名）
D2 📍 Lifecycle + Event Model（今天）
D3    Rule Model
D4    Capability + Policy Model
D5    Agent Mapping
D6-D7 组装 + Digital Employee Validation
```

昨天解决了"世界里有**什么**、怎么**连接**"（静态）。今天解决"世界怎么**演化**"（动态）——这是验证场景 L2（业务链推理）的直接依赖。

---

## 二、现状盘点：你已有的 Lifecycle 资产

| 资产 | 内容 | 层级 |
|---|---|---|
| Domain Model §3 | 每个核心对象的 **Lifecycle Owner** 列（Contract→Contract Lifecycle，Occupancy→Lease/Occupancy，Bill/AR→Billing & AR） | 归属层 ✅ |
| Domain Model §6 | 各对象状态机（AssetOperationalStatus：Active/Inactive/Under Renovation/Blocked；MerchantLifecycleStage：待核验→经营中→已退出） | 状态层 ✅ |
| effect-registry.yaml | 5 类冻结 effect_type（occupancy / financial / state-transition / lead-conversion / maintenance） | **类型层** ✅ |
| ADR-006 §4.1 | Transition → emits BusinessEventType → Effects 概念模型 | 机制层 ✅ |

**缺什么？缺"规则层"的完整声明。** effect-registry 注册的是类型（"存在 occupancy-effect 这种影响"），Domain Model 记的是归属（"Occupancy 的生命周期归 Lease/Occupancy 管"）——但**"哪个对象的哪次迁移、发出哪个 Event、携带哪些 Effect"这条链，散落在各域文件的 §8.3 里，没有统一声明格式**。AI 现在要拼装三个文件才能回答"A101 为什么不能出租"。

---

## 三、核心概念：State / Event / Effect 三层分离

这是今天的认知课。ADR-006 §2 的三轴分离原则（Skill Binding / 对象关系 / 生命周期影响）你已经熟了，今天在生命周期**内部**再做一次三分：

```
State（状态）      对象自身的演化阶段 —— "合同现在是 Active"
   ↓ 迁移发生
Event（事件）       不可变的事实声明 —— "ContractActivated 这件事发生了"
   ↓ 作为触发
Effect（影响）      对其他类型对象的状态影响 —— occupancy-effect → 铺位变使用中
```

| 层 | 回答什么 | 是什么 | 不是什么 |
|---|---|---|---|
| State | 它现在处于什么阶段 | 状态机的节点 | 不是 status 字段的枚举值 |
| Event | **什么事实已经发生**（过去式，不可变） | 迁移的命名声明 | 不是"调用了一个方法" |
| Effect | 这个事实让**别的对象**怎么了 | `{target_object_type, effect_type}` 规则 | 不是实例层链接（ADR-006：NO target_object_id） |

**为什么 AI 必须要 Event 这一层？** 因为 Agent 的推理单位是"事实"不是"状态"。状态是快照（查完就过期），Event 是因果链上的节点（可回溯、可解释）。数字员工回答"为什么"时，引用的永远是 Event："因为 8 月 10 日 ContractTerminationSubmitted 发生了"——而不是"因为 status='terminating'"。

**为什么 Effect 只声明 target_object_type 不声明 id？** 因为这是**声明式规则**（编译进 Ontology），不是实例数据。运行时由系统沿 D1 建立的关系（`occupies`）解析出具体是哪个 Resource Unit。规则层与实例层分离——这正是你 BCM ADR-001 编译器思想的又一次体现。

---

## 四、升级动作：Contract × Occupancy 完整声明示范

把 Domain Model §6.4 + effect-registry + 租赁域规则 §8.2.5 合并成**一张 AI 可读的声明表**：

```
对象：Contract（Owner: Contract Lifecycle）
状态机：Draft → Approved → Active → Expiring → Expired → Terminated
                                                      ↘ Voided（作废）

迁移声明：
1. Draft → Approved        守卫：审批通过
   Event: ContractApproved
   Effects: [{Resource Unit, occupancy-effect}]   ← 铺位进入"使用中"

2. Active → Expired        守卫：租期到期日到达
   Event: ContractExpired
   Effects: [{Bill/AR, financial-effect}]          ← 生成尾期账单

3. Active → Terminated     守卫：终止审批通过 ∧ 退租 Inspection 完成
   Event: ContractTerminated
   Effects: [{Resource Unit, occupancy-effect},   ← 铺位释放，面积回出租率分母
             {Bill/AR, financial-effect}]          ← 结算生成
```

对照原材料的三个升级点：

1. **守卫显式化**。Domain Model §05 写了 `AvailableForLeasing = Asset.Active ∧ no Occupancy ∧ no Restriction`，但"终止前置条件是 Inspection 完成"只在 BCM 域文件里。守卫（guard）必须进声明表，否则 Agent 知道"终止→释放"却不知道"什么时候允许终止"。
2. **Event 命名统一过去式**。ContractTerminated 而不是 terminate_contract——Event 是事实不是动作，命名即语义。
3. **Effect 挂到具体 Transition 而非对象**。effect-registry 只说"存在 occupancy-effect"，声明表说"是 **Active→Terminated 这一次迁移**发出的"。类型层（registry，冻结）+ 规则层（声明表，随域演进）双层治理，新增规则不打开 registry。

---

## 五、Agent 视角：A101 场景 L2 预演

> 验证问题："A101 铺位为什么不能出租？"

| 升级前（三层散落） | 升级后（声明表驱动） |
|---|---|
| 读 asset.status、读 lease.status、读 BCM 域文件 §8.3，人脑拼装 | 查 A101 → 沿 `occupies` 找到关联 Contract → 查其状态机位置：**Active→Terminated 迁移的守卫未满足**（Inspection 未完成） |
| 回答："代码里这么写的" | 回答："Contract 处于终止流程中，ContractTerminated 事件尚未发出，occupancy-effect 未触发，铺位仍被占用" |

**L1（定位）靠 D1 的 Relationship，L2（业务链推理）靠今天的 State/Event/Effect。** 没有 Event 层，Agent 的"为什么"永远只能引用代码；有了 Event 层，"为什么"引用的是业务事实。

---

## 六、架构师视角

- **以前**：生命周期 = status 字段 + 状态流转代码 + 散落在域文件里的 effect 证据。类型已治理（registry 冻结），但规则层无统一格式，AI 不可推理。
- **现在**：生命周期 = **状态机 + 迁移声明（守卫 + Event + Effects）**，类型层冻结在 registry、规则层声明在 Semantic Model、实例层运行时解析。三层各管各的——这和你 ADR-006 三轴分离是同一个设计品味：**宁要三个受治理的小模型，不要一个退化的通用大表**。

## 七、练习（5 分钟）

选 **Operation Task**（Domain Model §6.8，运营域），仿照第四节格式写出一条迁移声明：

1. 它的状态机里选一次关键迁移（提示：maintenance-effect 对应"工单状态迁移→物料领用/费用归集"）；
2. 给 Event 命名（过去式）；
3. 写出 Effects 列表——target_object_type 是谁？effect_type 用 registry 里哪一类？

（陷阱题：费用归集应该发 financial-effect 吗？看 registry 里 financial-effect 的 owner_domain 和 evidence 再回答。）

---

*明日 D3：补 Rule Model —— 从 BCM 域文件 + 代码抽取业务规则，显式化为 AI 可推理格式。*
