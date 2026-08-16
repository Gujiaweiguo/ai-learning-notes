# PT-W4-D1 · 升级 Ontology Model：Entity + Identity + Relationship

> 日期：2026-08-17（PT-W4 Day 1）｜毕业作品《MI CRE Enterprise Semantic Model v0.1》第一层
>
> 真实材料：MI Domain Model v1.0 §3 Object Ownership Matrix + ADR-006 四类对象关系 + effect-registry.yaml

---

## 一、本周目标与今天的位置

W4 不是"从零创建"，而是**升级**：

```
已有：Domain Model v1.0（对象/归属/不变量）+ ADR-006（四类关系）+ effect-registry（5 类 effect）
缺的：语义命名（动词化关系）+ 业务身份（层级身份）+ 业务定义（一句话"这是什么"）
今天：把 Entity / Identity / Relationship 三层从"工程可用"升级为"AI 可读"。
```

---

## 二、Entity 升级：从表名到「带业务定义的 Concept」

看 §3.1 的两行：

| Object | 现有定义方式 | 问题 |
|---|---|---|
| Resource Unit（铺位） | Owner Context + 不变量（编码全局唯一） | AI 只知道"谁管它"，不知道"它在业务世界里**是什么**" |
| Occupancy | 不变量（一个铺位同一时间只有一个 Active Occupancy） | 不变量是约束，不是定义 |

**升级动作：每个 Concept 补一句业务定义。**

- Resource Unit：*商场中可被独立出租、计价与运营的最小空间单元。它不是一行记录，是"可出租能力"的载体。*
- Occupancy：*某个铺位在某段时间内被某份合同占住的事实。铺位"是否可租"由它决定，而不是由 status 字段决定。*
- Merchant：*与商场建立合同关系的经营主体（B2B），不是消费者（Customer 是 B2C）。*

为什么必须写这一句？因为未来 Agent 读到"A101 不能出租"时，第一步是**定位概念**——它需要知道该查 Occupancy 而不是查 Resource Unit 的状态字段。业务定义就是 Agent 的概念入口。

---

## 三、Identity 升级：从主键到「业务身份层级」

现状（§3.1 不变量）：
- Project：编码全局唯一不可变 ✅（已有业务身份意识）
- Merchant：名称 + 证件号唯一 ✅（这就是业务身份，不是 id）
- Resource Unit：只有"编码全局唯一" ❌ **缺层级身份**

**A101 的业务身份不是一个编码，而是一条路径：**

```
Project（项目）→ Building（楼宇）→ Floor（楼层）→ Resource Unit（A101）
```

这条路径本身就是 ADR-006 的 Hierarchical Containment（层级包含）关系。升级后：
- 人说"A101"，Agent 需解析成完整路径才能定位（多个项目可能有同名铺位）
- 出租率、动线分析（§3.1 Space Hierarchy 行）依赖的是**层级身份**，不是扁平编码
- 层级不可循环 —— 不变量挂在了身份上，而不是挂在校验代码里

**Identity 的 Ontology 判据：删掉主键，业务还能不能认出它？** 名称+证件号能认出 Merchant，路径能认出 A101——这才叫业务身份。

---

## 四、Relationship 升级：四类关系 × 语义动词命名

ADR-006 已冻结四类关系（这是你最强的资产，直接继承）：

| 类别 | 案例 | 治理归属 |
|---|---|---|
| Identity Reference | 合同↔商户 | D-2（ADR-002） |
| Structural Composition | 资源↔仪表/设备 | D-2 |
| Hierarchical Containment | 项目→楼宇→楼层→资源 | D-2 |
| Lifecycle Transition Effect | 合同生效→铺位占用；合同→账单生成 | ADR-006 |

**缺的是语义动词。** 现在写的是"合同↔商户"（名词对名词），AI 无法推理。升级为动词化语义命名：

| 关系（原写法） | 语义命名 | 类别 | effect_type |
|---|---|---|---|
| 合同↔商户 | Contract **signs-with** Merchant | Identity Reference | — |
| 合同↔铺位 | Contract **occupies** Resource Unit | Lifecycle Effect | occupancy-effect |
| 合同↔账单 | Contract **generates** Bill / AR | Lifecycle Effect | financial-effect |
| 招商链 | Lead 完成使 Opportunity **enables** 创建 | Lifecycle Effect | lead-conversion-effect |
| 项目→资源 | Project **contains** Building **contains** Floor **contains** Unit | Hierarchical | — |
| 资源↔仪表 | Resource Unit **equipped-with** Energy Meter | Structural | — |

关键：**动词不是注释，是可推理的关系类型。** "Lease 终止后影响什么"——AI 沿 `occupies` 反向查：Lease Terminated → occupancy-effect → Resource Unit 释放。一句话自动展开为推理链。这正是 PT-W1-D4 发现的缺口（跨 ADR 隐式推理），今天在 Relationship 层补上。

**命名治理提示**：动词词表应像 effect-registry 一样**注册制封闭**（ORE-1 同构），不接受随手新增——否则会退化为 ADR-001 §7.2 否决过的"通用无类型关系表"。

---

## 五、Agent 视角：升级前后对比

验证场景预演："A101 铺位为什么不能出租？"

| 步骤 | 升级前（Domain Model） | 升级后（Ontology Model） |
|---|---|---|
| 定位 | 查表 resource WHERE code='A101' | 解析业务身份路径 → Resource Unit |
| 关联 | 读 FK lease.space_id，语义靠猜 | 沿 `occupies` 关系找到 Active Occupancy / Lease |
| 判断 | if-else 代码 | 沿 `occupies` → occupancy-effect → "存在 Active Occupancy 则不可出租" |

**升级前 AI 需要"理解代码"；升级后 AI 只需要"遍历语义图"。**

---

## 六、架构师视角

- 以前：关系 = 外键 + 引用；身份 = 主键；定义 = 靠团队默契。
- 现在：关系 = 受治理的语义动词（四类封闭）；身份 = 层级路径 + 业务唯一键；定义 = 每个 Concept 一句业务定义。**这三样是 Semantic Model 的地基，后面 Rule/Policy/Capability 都挂在它上面。**

## 七、练习（5 分钟）

从 §3.1 任选两个对象对（建议：Contract ↔ Deposit、Campaign ↔ Member），回答：
1. 属于 ADR-006 四类关系中的哪一类？
2. 给它一个动词化语义命名。
3. 一句话说明：Agent 沿这条关系能推理出什么？

（提示：Deposit 的"条款归 Contract、资金流归 Collection"——§3.1 已写明归属，但关系类别需要你判断。）

---

*明日 D2：升级 Lifecycle + Event —— 基于 effect-registry 补完整状态机与 Event 声明。*
