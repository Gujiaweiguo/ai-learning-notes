# PT-W1 Day 4 · 为什么 Domain Model 不够（核心课）

> 📅 2026-07-30 周三 | Business Semantic Architecture 并行轨道
>
> **本周主题：DDD → Semantic Model**
>
> **今日核心问题：AI 读你的 Domain Model，能读懂吗？**

---

## 一、回顾：前三天我们确认了什么

| Day | 结论 |
|-----|------|
| D1 | 你的 17 个 Bounded Context 就是 DDD 战略设计的产物——只是没用这个词 |
| D2 | Context 边界划分基本合理，P0 的 9 个 Full Model = Core Domain |
| D3 | Object Ownership Matrix 里有 Aggregate 根的雏形，effect-registry 就是 Domain Event |

**三天的结论指向一个事实：你已经做了一份相当完整的 Domain Model。**

但今天是一道分水岭——

> **Domain Model 做得好，不等于 AI 能理解你的业务。**

---

## 二、今天的核心课：让 AI 读 ADR-006

### 2.1 你已经做了什么

打开你的 **ADR-006：对象关系与生命周期影响模型**。这份 ADR 非常精彩——它定义了四类对象关系：

| 类别 | 含义 | MI 例子 |
|------|------|---------|
| **Identity Reference（身份引用）** | 对象 A 通过字段引用对象 B 的身份 | 合同 → 引用 商户 ID |
| **Structural Composition（结构组成）** | 对象 A 是对象 B 的组成部件 | 铺位 → 包含 仪表/设备 |
| **Hierarchical Containment（层级包含）** | 树状组织包含关系 | 项目 → 楼宇 → 楼层 → 铺位 |
| **Lifecycle Transition Effect（生命周期迁移影响）** | 对象 A 的状态变化导致对象 B 的状态变化 | 合同生效 → 铺位变为 occupied |

还有 **effect-registry.yaml**，冻结了 5 类 effect_type：

```
state-transition-effect   — 对象状态传播
occupancy-effect          — 资源占用变化
financial-effect          — 财务影响
lead-conversion-effect    — 招商转化
maintenance-effect        — 维护影响
```

**这已经比 99% 的企业系统走得更远了。** 大多数 ERP 只有表结构和外键，连"关系是什么类型"都没显式声明。

### 2.2 但 AI 读到的是什么？

现在，假设一个 AI Agent（比如 LangChat 数字员工）阅读这份 ADR-006，它能看到：

✅ **"合同引用了商户"**（Identity Reference）——能看到外键
✅ **"铺位包含仪表"**（Structural Composition）——能看到组成关系
✅ **"项目包含楼宇包含楼层"**（Hierarchical Containment）——能看到层级树
✅ **"合同生效时，铺位会变 occupied"**（Lifecycle Transition Effect）——能看到 effect 规则

**但 AI 无法回答这些问题：**

❌ "合同终止后，铺位多久可以重新出租？"
❌ "铺位有未完成的退租流程时，新合同能签吗？"
❌ "商户有三笔以上逾期账单时，新合同需要谁审批？"
❌ "Lease 过期但 Inspection 未完成，这个铺位的真实可用状态是什么？"

### 2.3 为什么答不了？——语义的三层缺失

这就是今天最关键的认知。把 Domain Model 升级为 Semantic Model，需要补三层：

---

#### 缺失 1：语义命名（Semantic Naming）

你的 ADR-006 说"合同↔铺位"是 **Lifecycle Transition Effect** 关系。但这个关系**叫什么名字**？

- 技术命名：`contract → space : lifecycle-transition-effect`
- 语义命名应该是：`Contract **occupies** Space`（合同**占用**铺位）

没有动词级语义命名，AI 知道"有关系"，但不知道"什么关系"。它不能用自然语言推理：

> "因为合同 **occupies** 铺位，所以合同终止后铺位应该 **release**（释放）"

**Domain Model 有关系类型，但没有语义动词。**

---

#### 缺失 2：业务规则显式化（Explicit Business Rules）

你的 effect-registry 声明了：

```
当合同从 Signed → Active，
对 target_object_type: Space 产生 occupancy-effect
```

但**什么条件下生效？什么条件下不生效？** 例如：

- "合同生效，但如果铺位有**未完成退租流程**，不立即释放" → 这个条件在哪？
- "合同生效，但如果商户在**黑名单**中，先冻结" → 这个规则在哪？
- "合同终止后 **30 天内**完成 inspection 才能释放铺位" → 这个时间约束在哪？

这些业务规则在代码的 if-else 里、在审批流配置里、甚至在某些 Excel 里——**但不在 Domain Model 里，也不在 Ontology 声明里**。

**Domain Model 声明了"会发生什么"，但没有声明"在什么条件下会发生、不会发生"。**

> 对于 AI Agent 来说：没有显式规则 = 无法推理 = 只能调 API 碰运气。

---

#### 缺失 3：跨 ADR 的推理链（Cross-Domain Reasoning Chain）

一个真实问题：**"A101 铺位为什么不能出租？"**

AI 需要跨多个 ADR 推理：

```
1. 查 Identity Reference → A101 当前关联了哪些合同（合同↔铺位）
2. 查 Lifecycle → 当前合同处于什么状态（合同状态机）
3. 查 Lifecycle Transition Effect → 合同终止是否触发了 occupancy-effect
4. 查 Rule → 退租流程是否完成（业务规则）
5. 查 Policy → 是否需要特殊审批才能重新出租（执行策略）
6. 得出结论 → 不能出租，因为 Inspection 未完成
```

**这个推理链跨越了 ADR-006（关系）、effect-registry（事件）、BCM 域文件（规则）、审批流（策略）。**

你的 Domain Model 有每一块拼图，但**拼图之间的桥**（reasoning chain）是隐式的——它存在于你的脑子里（26 年经验），存在于代码的调用链里，但不存在于任何一份 AI 可以读取的文档里。

> **Domain Model 是一堆积木。Semantic Model 是积木之间的连接方式和推理规则。**

---

## 三、三轴分离原则的 Ontology 意义

ADR-006 §2 提出了一个深刻的架构原则——**三条独立语义轴**：

| 语义轴 | 回答什么 | 治理文件 |
|--------|---------|---------|
| **Skill Binding（D-3）** | AI 能力如何组合？ | ADR-004 |
| **Object Relationship（D-2）** | 企业实体如何连接？ | ADR-002 + ADR-006 前三类 |
| **Lifecycle Effect** | 业务状态如何演化？ | ADR-006 第四类 |

**从 Ontology 视角看，这三条轴对应了 AI 理解企业的三个认知层次：**

```
层次 1 — 静态拓扑：企业里有什么？它们怎么连接？
         （Identity Reference + Structural Composition + Hierarchical Containment）

层次 2 — 动态演化：业务怎么变化？变化如何传播？
         （Lifecycle Transition Effect）

层次 3 — 能力编排：AI 可以做什么？怎么组合能力完成任务？
         （Skill Binding）
```

**AI 理解企业，需要同时拥有这三个层次。** 你的 Domain Model 覆盖了层次 1 的大部分，在层次 2 迈出了第一步（effect-registry），层次 3 还在建设中（LangChat Capability）。

---

## 四、一个具体对比：Domain Model 视角 vs Semantic Model 视角

以 **"合同终止影响铺位"** 为例：

| 维度 | Domain Model 视角（你现在有的） | Semantic Model 视角（需要补的） |
|------|------|------|
| 关系类型 | Lifecycle Transition Effect | **terminates** 关系（语义动词） |
| 影响描述 | occupancy-effect | 合同终止 → 铺位状态从 occupied → pending_release |
| 触发条件 | 合同状态机：Active → Terminated | 合同终止 **且** 无未结算账单 **且** Inspection 已完成 |
| 时间约束 | 无 | 终止后 30 天内完成 Inspection，否则进入强制清理流程 |
| 关联规则 | 无 | 关联账单必须全部结清；关联减免必须审批完成 |
| AI 可推理？ | ❌ 只知道"有影响" | ✅ 能推理出"这个铺位当前不可出租" |

---

## 五、架构师视角

```
以前：Domain Model 做得好 = 架构完成了

现在：Domain Model 是地基，Semantic Model 是建筑。
      地基扎实不代表建筑完成。
      AI 需要的不只是"有什么"，还需要"意味着什么"和"在什么条件下如何变化"。
```

**三层缺失的优先级：**

1. **P0 — 语义命名**：给 ADR-006 的四类关系加上语义动词（occupies / releases / governs / generates...）。成本最低，收益最大。
2. **P1 — 业务规则显式化**：从代码和审批流中提取 Top 20 最关键的业务规则，写成声明式格式。
3. **P2 — 推理链**：设计 3-5 个典型场景的推理路径（如"铺位可租性判断"），作为 Semantic Model 的验证基准。

---

## 六、练习（5 分钟）

打开你的 ADR-006 §8 压力测试验证表，选其中一条关系：

> **合同↔账单：Lifecycle Transition Effect**

回答两个问题：

1. **语义命名**：合同和账单之间的 effect，用哪个动词描述最准确？是 `generates`（生成）、`triggers`（触发）、还是 `obligates`（产生义务）？——选一个，说出为什么。

2. **触发条件**：合同从什么状态迁移到什么状态时，会产生账单？这个 effect 有没有前置条件？（比如"合同金额 > 0"或"合同类型 = 正式合同"才生成账单？）

> 把你的答案写在笔记本里。Week 2 抽取 Ontology 时会用到。

---

## 七、本日小结

| 认知 | 内容 |
|------|------|
| Domain Model 的局限 | 描述了结构，但语义（含义）是隐式的 |
| 三层缺失 | ① 语义命名（动词） ② 业务规则显式化 ③ 跨域推理链 |
| ADR-006 的贡献 | 四类关系 + effect-registry 已经迈出了第一步 |
| 下一课（D5） | Ontology 能补充什么？对照 business-ontology.yaml 识别缺口 |

> **核心认知：你的 Domain Model 告诉 AI "有什么"。Semantic Model 要告诉 AI "意味着什么"。前者是清单，后者是理解。**

---

*📁 保存于 /root/learning-notebooks/并行轨道/PT-W1-D4-为什么Domain-Model不够.md*
