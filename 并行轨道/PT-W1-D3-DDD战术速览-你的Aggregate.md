# PT-W1 Day3：DDD 战术速览 + 你的 Aggregate

📅 日期：2026-07-29（周二）
并行轨道：Business Semantic Architecture（PT-W1: DDD → Semantic Model）
今日主题：**Entity / Value Object / Aggregate 在 MI 里长什么样？**

---

## 核心问题

> Entity、Value Object、Aggregate 这些 DDD 战术概念，我在 MI Domain Model 里已经做了，只是没用这些名字？

**答案是：你不仅做了，而且做得相当规范。** 今天是把"你已经做的事"用 DDD 战术语言重新标注一遍。

---

## 1. DDD 战术设计三件套（60秒版）

### ① Entity（实体）

> 有唯一身份标识（Identity），身份不随属性变化而改变。

关键特征：
- 有 ID —— 即使所有属性都变了，它还是它
- 有生命周期 —— 会创建、修改、销毁
- 可变状态 —— 字段可以被修改

**MI 例子**：`Contract`（合同）。合同编号不变，但条款、状态、金额都可能变更。

### ② Value Object（值对象）

> 没有身份标识，完全由属性值决定相等性。不可变（Immutable）。

关键特征：
- 无 ID —— 两个值对象属性相同就是"相等"
- 不可变 —— 创建后不修改，要改就创建新的
- 通常用于描述实体的属性

**MI 例子**：`PhysicalAttributes`（物理属性：面积、工程条件）。两间铺位如果面积和条件完全相同，这些值对象就是"相等"的。

### ③ Aggregate（聚合）

> 一组紧密关联的 Entity 和 Value Object 的集合，作为一个一致性边界统一操作。

关键概念：
- **Aggregate Root（聚合根）**：唯一的外部入口。外部只能引用 Root，不能直接引用内部对象
- **Invariant（不变量）**：聚合内部必须始终保持一致的业务规则
- **事务边界**：一次操作只修改一个 Aggregate，保证一致性

**MI 例子**：`Asset Foundation` 聚合：
- Root：`Resource Unit`（铺位/单元）
- 内部：`PhysicalAttributes`、`ResourceType`、`AssetOperationalStatus`
- 不变量：编码全局唯一不可变、层级关系不可循环

---

## 2. 用 MI Domain Model §3 做对照标注

你的 Domain Model §3 Object Ownership Matrix 里，每个 Context 都明确列出了：

| Domain Model 里的叫法 | DDD 战术术语 | 你的例子 |
|---------------------|------------|---------|
| 聚合根 | Aggregate Root | Resource Unit、Contract、Bill/AR |
| 值对象 | Value Object | ResourceType、ClauseType、FeeItem |
| 不变量 | Invariant | "一个铺位同一时间只有一个 Active Occupancy" |
| 不负责 | 不属于本聚合的职责（聚合边界声明） | ❌ 算费执行（归 Billing） |

**你已经在用 DDD 战术语言了。** §3 的结构 = Aggregate Root + Value Object + Invariant + 边界声明。

---

## 3. 深度检验：五个 P0 聚合

### ① Asset Foundation 聚合

```
聚合根：Resource Unit（铺位/单元）
内部实体：Project → Building → Floor → Zone（层级实体）
值对象：ResourceType（三族分类）
       PhysicalAttributes（面积/工程条件）
       AssetOperationalStatus（Active/Inactive/Under Renovation/Blocked）

不变量：
  1. 编码全局唯一不可变
  2. 层级关系不可循环
  3. Asset 不拥有商业可用性（D-001 A）—— Reserved/Contracted 不在此聚合
```

**DDD 评分**：✅ 聚合根清晰，不变量严格

**Ontology 视角缺口**：Asset Operational Status 有四个值（Active/Inactive/Under Renovation/Blocked），但没有声明状态之间的合法迁移路径。Agent 无法推断"Blocked 能否直接变 Active"。

---

### ② Lease / Occupancy 聚合

```
聚合根：Occupancy（占用记录）
值对象：OccupancyPeriod（交付日 → 退场日）
       AvailabilityAssessment（组合判断结果）
       VacancyRate（出租率口径）

不变量：
  1. 一个 Resource Unit 同一时间只有一个 Active Occupancy
  2. occupancy-effect：合同审批→铺位使用中；终止/作废→空置
  3. 出租率 ≠ 占用率

领域规则（Domain Rule）：
  AvailableForLeasing =
      Asset.operational_status == Active
      AND Occupancy.current == None
      AND Restriction.exists == False
```

**DDD 评分**：✅ 这是你最关键的聚合，不变量 1 是核心业务规则

**Ontology 视角洞察**：`AvailabilityAssessment` 是一个**领域规则的结果**，不是字段（D-001 Amendment A 明确了这一点）。这对 AI Agent 极其重要 —— Agent 不能"写入"可用性状态，只能通过查规则推断。这是 Ontology 的 Rule 维度，不是 Entity 属性。

---

### ③ Contract Lifecycle 聚合

```
聚合根：Contract（合同）
内部实体：Contract Clause（11 类条款）、Contract Template
值对象：ClauseType（固定/面积/提成/保底取高/滞纳金/免租/保证金...）
       RentMethod（12 种计租矩阵 = 4 租金类型 × 3 扣点类型）
       SettlementCycle（自然月/合同月/固定日）
       ChangeType（9 类变更）

不变量：
  1. 条款定义归此 Context，算费执行归 Billing
  2. 合同审批通过 → 触发跨域 effect（铺位状态、Billing 应收、Merchant 待进场）
  3. 合同状态五态封闭：未生效/使用中/已终止/已结束/已作废
```

**DDD 评分**：✅ 聚合内高内聚（合同+条款+模板）

**关键发现**：不变量 2 描述的是**跨聚合的 effect**。Contract 聚合自己不知道这些 effect 的具体实现，只负责"声明触发"。这正是 effect-registry 的价值 —— 把跨聚合的因果关系显式化。

---

### ④ Billing & AR 聚合

```
聚合根：Bill / AR（账单/应收）
内部实体：Charge Definition、Billing Rule
值对象：FeeItem（费项）
       SettlementConfig（结算配置矩阵 6 组）
       ArStatus（未生效/已生效/已核销/部分核销）
       AgingReport（账龄分析）

不变量：
  1. 消费 Contract Clause 执行算费，不自定义条款
  2. 已终止合同零账单
  3. 保底/提成"取高"周期模式待定稿

三层模型：
  Contract Clause（定义"怎么算"）
    → Charge Definition（定义"算什么费项"）
      → Billing Rule（执行算费生成 Bill）
```

**DDD 评分**：✅ Charge Definition 三层模型防止了 Billing 吞合同逻辑

**Ontology 视角洞察**：三层模型 `Clause → Charge Definition → Billing Rule` 本质上是一个**语义编译链**。这不是偶然 —— 它正是 Ontology Compiler 的雏形（W3 会深入展开）。

---

### ⑤ Merchant 聚合

```
聚合根：Merchant（商户主体）
内部实体：Merchant Application（申请单）
值对象：LegalIdentity（身份证/统一社会信用代码）
       QualificationDocs（资质证照）
       BankInfo（银行资料）
       InvoiceTitle（开票信息）
       Contact（联系方式）
       BrandAuthorization（品牌授权关系）
       OperatingStatus（正常/监管/禁止）
       MerchantLifecycleStage（待核验 → 经营中 → 已退出）

不变量：
  1. 名称 + LegalIdentity 唯一
  2. Merchant 是 Identity Reference 主体，跨域只引用不复制
  3. 只有有效授权的品牌才能进入条件报批/合同
```

**DDD 评分**：✅ Identity Reference 原则清晰（ADR-002/006）

**Ontology 视角洞察**：不变量 2 是 Ontology 的 Identity 维度的核心 —— "商户身份"在全域是一个引用令牌，不是复制的记录。AI Agent 理解"商户"时，知道所有 Context 里的 Merchant 引用指向同一个实体。

---

## 4. Aggregate 的边界 = AI Agent 的认知边界

这是今天最重要的认知。

### 传统视角：Aggregate 是事务一致性边界
> 一次操作只修改一个 Aggregate，保证数据一致性。

### Ontology 视角：Aggregate 是 AI Agent 的推理边界
> Agent 在一个 Aggregate 内部可以安全推理（因为不变量保证了语义一致性）。跨 Aggregate 推理需要通过显式声明的 effect 关系。

**具体例子**：

| 推理场景 | 在一个聚合内 | 跨聚合 |
|---------|------------|--------|
| "这个铺位面积多少？" | ✅ Asset Foundation 聚合内 | 不需要跨 |
| "这个铺位能出租吗？" | ❌ 需要 Lease/Occupancy 的规则 | 跨 Asset + Lease 聚合 |
| "合同终止后影响什么？" | ❌ 需要 effect-registry | 跨 Contract + Lease + Billing 聚合 |

**结论**：你的 Aggregate 边界 = AI Agent 安全推理的范围。effect-registry = 跨边界推理的"桥梁说明"。

---

## 5. 你的 effect-registry 从 Aggregate 视角看

effect-registry v1.0 冻结了 5 类 effect，从 Aggregate 间因果关系看：

| Effect 类型 | 触发方（上游聚合） | 被影响方（下游聚合） | 语义 |
|------------|------------------|-------------------|------|
| occupancy-effect | Contract 聚合 | Asset + Lease 聚合 | 合同生命周期 → 资源占用状态变更 |
| state-transition-effect | 任意聚合 | 任意聚合 | 对象状态传播（通用型） |
| financial-effect | Contract 聚合 | Billing 聚合 | 合同事件 → 账单/应收生成 |
| lead-conversion-effect | Leasing Pipeline 聚合 | Leasing Pipeline 内部 | 招商阶段转化 |
| maintenance-effect | Operations 聚合 | Work Order 聚合 | 巡检异常 → 工单生成 |

**关键发现**：`occupancy-effect` 和 `financial-effect` 是你目前最重要的跨聚合因果关系。它们让 AI Agent 能回答"合同审批后会发生什么"——不需要读代码，读 effect-registry 就够了。

---

## 6. 战术设计 20%：够用就好

| DDD 战术概念 | 你需要掌握的程度 | MI 对照 |
|-------------|---------------|---------|
| Entity / Value Object | ✅ 知道区别 | §3 已标注 |
| Aggregate Root | ✅ 知道是唯一入口 | §3 聚合根列 |
| Invariant | ✅ 知道是聚合内规则 | §3 不变量列 |
| Factory / Repository | ⏭️ 不用深入 | 代码层的事 |
| Domain Service | ⏭️ 不用深入 | 代码层的事 |
| Domain Event | ✅ 后面 W2-D3 会深入 | effect-registry |

**80/20 原则**：战略设计（Bounded Context + Context Map + Aggregate 边界）才是 AI Agent 最需要的。战术模式（Factory/Repository/Service）是代码实现细节，对 Ontology 层不关键。

---

## 7. 今天的关键认知

| # | 认知 | 对 AI Agent 的意义 |
|---|------|-------------------|
| 1 | **你已经做了规范的 Aggregate 设计** | DDD 战术语言只是重新标注 |
| 2 | **不变量 = Agent 推理的安全边界** | Agent 在聚合内推理不会违反业务规则 |
| 3 | **Aggregate 边界 = Agent 认知边界** | 跨聚合推理需要 effect-registry |
| 4 | **Charge Definition 三层模型 = 语义编译雏形** | W3 Ontology Compiler 会展开 |
| 5 | **AvailabilityAssessment 是规则不是字段** | Agent 不能写入可用性，只能推断 |

---

## 8. 连接思考（主线 ↔ 并行）

没有主线内容的日子，纯并行轨道聚焦。

**今日内部连接**：D1（认识 Domain Model）→ D2（验证 Bounded Context）→ D3（深入 Aggregate）。三天形成完整的 DDD 战略 → 战术视角：
- D1/D2：**怎么切边界**（战略）
- D3：**边界内部怎么组织**（战术）
- 两者共同构成 **AI Agent 的认知地图 + 推理规则**

---

## 9. 练习（5分钟）

> 看看你的 Occupancy 聚合。`AvailableForLeasing` 是一个组合判断（Asset.Active ∧ no Occupancy ∧ no Restriction）。
>
> 如果 AI Agent 要回答"A101 能不能出租？"，它需要分别查 Asset Foundation 聚合（物理状态）和 Lease/Occupancy 聚合（占用状态），然后组合判断。
>
> **思考**：这个"组合判断"逻辑应该放在哪里？
> - A. 写在 Agent 的 prompt 里？
> - B. 声明在 Ontology 的 Rule 层？
> - C. 编码在某个聚合的方法里？
>
> 提示：Agent 不可靠的地方，就是你需要显式声明的地方。

---

## 10. 本周进度

| Day | 主题 | 状态 |
|-----|------|------|
| D1 | 你已经做了 Domain Model | ✅ 完成 |
| D2 | DDD 战略设计 — 你已经做了 | ✅ 完成 |
| **D3** | **DDD 战术速览 + 你的 Aggregate** | **📍 今天** |
| D4 | 为什么 Domain Model 不够（核心课） | ⬜ 明天 |
| D5 | Ontology 能补充什么 | ⬜ |
| D6 | Ontology vs Knowledge Model vs RAG | ⬜ |
| D7 | ⚡ 输出 MI CRE Semantic Gap Analysis v0.1 | ⬜ |

---

## 11. 明日预告

**D4：为什么 Domain Model 不够（核心课）**

> AI 读你的 Domain Model 能读懂吗？

明天是本周最重要的一课 —— 从"你已经做得很好"转向"但这些还不够"。我们将用 ADR-006 四类关系做案例，看 AI Agent 读你的 Domain Model 时会遇到什么困难，以及为什么需要 Ontology 层来补充。
