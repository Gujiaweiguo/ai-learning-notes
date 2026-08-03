# PT-W2-D2：Relationship 抽取

> 📅 Week 2 - Day 2（8/4）
>
> **并行轨道：Business Semantic Architecture（企业业务语义架构）**
>
> **本周目标**：从既有材料抽取 Ontology（本体）语义，而不是另起炉灶设计一套模型。

---

## 今日主题：ADR-006 的四类关系，能否让 AI Agent 读懂企业？

昨天抽取了 Entity（实体）和 Identity（业务身份）。今天处理第二个问题：这些业务对象究竟以什么方式相连？

不要把 `foreign key`（外键）当成业务关系。外键只能说“有一个引用”；语义关系必须说明“为什么连接、谁拥有真值、状态变化会带来什么后果”。这是 AI Agent 能否可靠跨域推理的分界线。

## 一、先确认已有的真实资产

对照 `ADR-006-Object-Relationship-and-Lifecycle-Effect.md` §2-§4：MI CRE 已经把三种不同问题拆开治理。

| 语义轴 | 它回答什么 | 已有治理位置 | Agent 获得什么能力 |
|---|---|---|---|
| Skill Binding（技能绑定） | AI 能力如何组合 | ADR-004 | 知道哪些 Skill 可以编排，不把它误读为业务对象关系 |
| Object Relationship（对象关系） | 企业对象如何相连 | ADR-002 / ADR-006 | 能沿着有业务含义的路径检索与解释 |
| Lifecycle Transition Effect（生命周期迁移影响） | 一个对象状态变化会影响什么 | ADR-006 | 能推导状态后果并提出下一步动作 |

**架构判断**：不能把这三类问题塞进同一张“关系表”。ADR-006 已明确否决无类型关系表；混合后，Agent 既可能把“合同关联铺位”误作可执行的 Skill，也无法区分静态事实与动态影响。

## 二、四类关系的抽取卡片

ADR-006 §3 定义的四类关系，正好是本周 Relationship 抽取的起点。

| 类别 | 业务问题 | MI CRE 真实例子 | 应补出的语义谓词 | 对 AI Agent 的价值 |
|---|---|---|---|---|
| Identity Reference（身份引用） | 谁指向谁的身份？ | 合同 → 商户 | `Contract is_signed_by Merchant`（合同由商户签署） | 回答“这份合同属于谁”，并回到 Merchant Context 获取主体真值 |
| Structural Composition（结构组成） | 谁由什么组成？ | 资源 → 仪表/设备 | `Resource contains Equipment`（资源包含设备） | 判断查询范围；问铺位状态时知道还需查看附属设备，而非把设备当独立租赁主体 |
| Hierarchical Containment（层级包含） | 谁处在哪个经营层级？ | 项目 → 楼宇 → 楼层 → 资源 | `Resource is_located_in Floor`（资源位于楼层） | 将“A101”还原为业务身份路径，支持按项目、楼层汇总和权限校验 |
| Lifecycle Transition Effect（生命周期迁移影响） | 什么状态变化会影响谁？ | 合同生效 → 铺位占用；合同 → 账单 | `Contract activation emits occupancy-effect / financial-effect`（合同生效产生占用/财务影响） | 回答“为什么不能出租/为什么有账单”，并把结论连接到可验证的业务事件 |

注意前三类是**静态拓扑**：描述企业世界已有的连接。第四类是**动态演化规则**：描述迁移发生时应产生的影响。它们不能合并。

## 三、以“合同—铺位”为例完成一次语义抽取

ADR-006 §8 将合同↔铺位归为 Lifecycle Transition Effect，而不是普通引用。这一判断很关键。

```text
Contract（合同）
  -- is_signed_by --> Merchant（商户）              [身份引用]
  -- applies_to --> Resource Unit / Space（铺位）   [业务关联，需以域证据明确谓词]
  -- Signed → Active --> occupancy-effect --> Resource Unit
  -- Signed → Active --> financial-effect --> Bill / AR（账单/应收）
```

此处要避免一个常见错误：把 `Contract.resource_id` 直接抽成“合同占用铺位”。它最多证明了对象引用；真正的“占用”是合同从 `Signed` 迁移到 `Active` 后，依据 `occupancy-effect` 产生的业务后果。

这也是为什么 `effect-registry.yaml` 将 `occupancy-effect` 和 `financial-effect` 作为已发布类型治理：effect type（影响类型）不是随手填写的标签，必须有域矩阵或域 ADR 证据，且经过跨域影响复核。

## 四、Relationship 抽取的最小工作模板

本周不设计数据库表。每发现一条对象关系，只记录以下六项，先形成可评审的语义事实：

| 字段 | 示例：合同生效影响铺位 |
|---|---|
| Source Concept（源概念） | Contract |
| Predicate（语义谓词） | activates_occupancy（激活占用） |
| Target Concept（目标概念） | Resource Unit |
| Relationship Category（关系类别） | Lifecycle Transition Effect |
| Trigger / Condition（触发条件） | Contract：Signed → Active |
| Evidence & Owner（证据与权威归属） | ADR-006 §4、§8；对象定义真值仍归 ADR-002 / 域模型 |

对于 Identity Reference、Structural Composition、Hierarchical Containment，同样填写 Source、Predicate、Target、Category、Evidence、Owner；但**不虚构生命周期触发条件**。对于 Lifecycle Transition Effect，则必须说明迁移与 effect type，且不要填具体 `target_object_id`（目标实例 ID）。ADR-006 §4.2 明确它是一条类型级规则，运行时再按业务身份解析实例。

## 五、今天的抽取检查

用 ADR-006 §8 的六条压力测试关系做第一轮检查：

| 关系 | 正确分类 | 需要继续补的内容 |
|---|---|---|
| 合同 ↔ 商户 | Identity Reference | 明确 `is_signed_by` 等业务谓词与身份真值来源 |
| 资源 ↔ 仪表/设备 | Structural Composition | 明确组成边界：哪些设备随资源管理，哪些独立维护 |
| 项目 → 楼宇 → 楼层 → 资源 | Hierarchical Containment | 明确层级路径与资源归属规则 |
| 合同生效 → 铺位占用 | occupancy-effect | 明确迁移、目标类型、占用状态的域证据 |
| 合同生效 → 账单生成 | financial-effect | 明确是“生成账单”还是“形成应收”的业务边界 |
| 合同/租赁变化 → 商户占用状态 | state-transition-effect | 明确由哪个生命周期版本负责声明 |

## 六、AI Agent 视角：它未来如何理解“A101 为什么不能出租？”

有了关系语义，Agent 的推理顺序不再是盲目联表：

1. 通过 Hierarchical Containment 定位 A101 的空间身份路径及其 Owner Context。
2. 通过相关 Contract / Occupancy 的 Identity Reference 找到可能关联的业务对象。
3. 检查 Contract 的 Lifecycle 迁移及声明的 `occupancy-effect`。
4. 区分“历史上关联过合同”与“当前 Active 合同造成占用”两个不同结论。
5. 引用 effect 的权威证据解释原因；若需改变状态，再转给受 Policy（策略）约束的 Capability（能力），而非擅自执行。

> **今天改变的设计判断**
>
> 以前：对象之间有外键或绑定，就可以称为“关系”。
>
> 现在：每条关系必须先判定它属于身份、结构、层级还是生命周期影响；只有附带业务谓词、权威归属和触发证据，AI Agent 才能据此进行可信解释。

## 📝 练习（5 分钟）

选择“合同生效 → 铺位占用”这条关系，写出六项抽取卡片：Source Concept、Predicate、Target Concept、Category、Trigger / Condition、Evidence & Owner。

然后回答：若合同仍是 `Signed` 而未迁移为 `Active`，Agent 能否仅凭 `Contract.resource_id` 断言“A101 已被占用”？为什么？

> 明天进入 Lifecycle + Event 抽取：把 `effect-registry.yaml` 的已注册影响类型，与 Lease / Contract 的完整状态机连接起来。
