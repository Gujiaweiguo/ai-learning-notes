# PT-W2-D1：Entity + Identity 抽取

> 📅 Week 2 - Day 1（8/3 周日）
>
> **并行轨道：Business Semantic Architecture**
>
> **本周目标**：从已有材料中抽取 Ontology 语义（不是"设计 Ontology"，而是"发现你已经有什么"）

---

## 今日主题：你的 Concept 清单全不全？业务身份是什么？

### 一、为什么要"抽取"Entity？

上一周（PT-W1）我们做了 **Gap Analysis**，发现 MI Domain Model 已经有完整的 Object Ownership Matrix——每个对象都有 Owner Context、Lifecycle Owner、Consumers。

但那是 **DDD 视角的对象清单**。

今天要做的，是切换到 **Ontology 视角**，回答两个问题：

| 问题 | DDD 回答 | Ontology 需要的回答 |
|------|---------|-------------------|
| 世界里有什么东西？ | Object Ownership Matrix 里有 30+ 个对象 | 这些对象在**业务世界**里是什么？ |
| 它如何被唯一识别？ | 表 `id` + 编码（如 `merchant_id`, `resource_code`） | 它的**业务身份**是什么？ |

> **核心区别**：DDD 说"这是 Lease 表，主键 lease_id"。Ontology 说"Lease 是一个商业占用关系，它的身份取决于 Space × Merchant × 时间段的组合"。

---

### 二、Entity 抽取：从 MI Object Ownership Matrix 到 Ontology Concept

#### 已有资产：MI Domain Model §3 Object Ownership Matrix

你的 Domain Model 已经列出了 P0（25 个）+ P1（20 个）对象。这是极好的基础。

**P0 核心对象清单（摘自 §3.1）：**

| Object | Owner Context | Ontology Concept 类型 |
|--------|--------------|---------------------|
| Project | Asset Foundation | **组织实体**（商业经营的最顶层容器） |
| Building / Floor / Zone | Asset Foundation | **空间实体**（层级） |
| Resource Unit（铺位/单元） | Asset Foundation | **空间实体**（可租赁的最小单元） |
| Merchant | Merchant | **主体实体**（B2B 商业参与者） |
| Lead / Opportunity / Quote / Intent Letter / Condition Approval | Leasing Pipeline | **流程实体**（招商管线状态流转） |
| Contract | Contract Lifecycle | **契约实体**（法律约束的商业协议） |
| Contract Clause | Contract Lifecycle | **契约构件**（条款 = 规则的载体） |
| Occupancy | Lease / Occupancy | **关系实体**（占用 = 空间 × 商户 × 时间） |
| Bill / AR | Billing & AR | **财务实体**（应收款） |
| Charge Definition | Billing & AR | **计费构件**（条款→算费的中介） |
| Payment | Collection & Settlement | **财务实体**（收款） |
| Invoice | Tax Invoice | **税务实体**（法定票据） |
| Accounting Entry | Accounting Bridge | **财务构件**（外部系统凭证） |

**P1 补充对象（摘自 §3.1a）：**

| Object | Owner Context | Ontology Concept 类型 |
|--------|--------------|---------------------|
| Revenue Evidence | Operations Management | **事实实体**（营业额采集证据） |
| Energy Reading | Engineering & Facility | **事实实体**（能源抄表读数） |
| Operation Task | Operations Management | **活动实体**（运营任务） |
| Service Ticket | Work Order Service | **活动实体**（工单） |
| Campaign | Marketing & Campaign | **活动实体**（营销活动） |
| Customer / Member | Customer / Member | **主体实体**（B2C 消费者） |
| Parking Order | Parking Management | **交易实体**（停车订单） |
| Business Metric | BI & Analytics | **度量实体**（只读指标） |

#### 关键发现：三种类型的 Concept

抽取后你会发现，你的对象不是扁平的"表"，而是有不同**本体类型**：

```
┌─────────────────────────────────────────────────┐
│           MI CRE Ontology Concept 分类            │
├─────────────────────────────────────────────────┤
│                                                   │
│  1. 实体（Entity）— 独立存在、有完整生命周期        │
│     · Resource Unit（铺位）                       │
│     · Merchant（商户）                            │
│     · Contract（合同）                            │
│     · Bill / AR（账单应收）                       │
│                                                   │
│  2. 关系实体（Relational Entity）— 连接两个实体    │
│     · Occupancy（占用 = Space × Merchant）        │
│     · Lease（租约 = Contract × Space × Merchant） │
│                                                   │
│  3. 事实构件（Fact Component）— 不可变的事实记录   │
│     · Revenue Evidence（营业额采集证据）           │
│     · Energy Reading（抄表读数）                   │
│     · Contract Clause（合同条款快照）              │
│                                                   │
│  4. 活动实体（Activity Entity）— 有开始和结束      │
│     · Operation Task（运营任务）                  │
│     · Service Ticket（服务工单）                   │
│     · Campaign（营销活动）                         │
│                                                   │
└─────────────────────────────────────────────────┘
```

> **为什么这个分类重要？** 因为 AI Agent 需要知道"这个概念是独立实体还是关系实体"，才能正确推理。比如 Occupancy 不是一个独立的东西——它必然同时关联一个 Space 和一个 Merchant，如果其中一方消失，Occupancy 就不应该存在。

---

### 三、Identity 抽取：从表 ID 到业务身份

#### DDD 视角的 Identity（你已经有的）

你的 Domain Model 用的是技术身份：

| 对象 | 技术身份 | 来源 |
|------|---------|------|
| Resource Unit | `resource_code`（全局唯一编码） | §3.1 不变量 |
| Merchant | `name + legal_identity`（名称+证件号） | §3.1 不变量 |
| Contract | `contract_id`（全局唯一） | §4.3 共享内核 |
| Bill / AR | `bill_id` | §6.5 状态机 |

#### Ontology 视角的 Identity（需要补充的）

Ontology 关心的不是主键，而是**业务身份层级**：

```
Project（项目）
  └── Building（楼栋）
       └── Floor（楼层）
            └── Zone（区域）
                 └── Resource Unit（铺位/单元）
                      └── Occupancy（占用关系）
```

**业务身份 = 这个对象在业务世界中被"谁认识谁"的方式。**

| 对象 | 技术身份 | 业务身份（Ontology 需要的） |
|------|---------|------------------------|
| Resource Unit | resource_code = "A101" | Project → Building → Floor → **A101**（空间路径身份） |
| Merchant | legal_identity = "9131..." | **统一社会信用代码** → 对应一个法人实体 |
| Contract | contract_id = "CT2026001" | Merchant + Resource Unit + **签约时间** → 一份特定合同 |
| Occupancy | occupancy_id | Resource Unit + **有效时间段** → 一个占用关系（同一铺位不同时间可有不同占用） |
| Revenue Evidence | evidence_id | Merchant + **采集日期** + 数据来源 → 一条营业额事实 |

> **关键洞察**：你的 Domain Model §3 已经定义了 `Space Hierarchy` 聚合（Project → Building → Floor → Zone → Resource Unit）。这在 DDD 里是层级聚合，在 Ontology 里就是**业务身份路径**。

---

### 四、对照真实材料：business-ontology.yaml 里的 Entity 覆盖度

你的 `business-ontology.yaml` 定义了 12 个模块（资源管理、招商管理、合同管理、财务管理、运营管理、物业管理、推广营销、系统管理、资产管理、移动端、数据决策、预算管理）。

**覆盖度分析：**

| business-ontology.yaml 模块 | Domain Model Context | Entity 数量 | 覆盖状态 |
|---------------------------|---------------------|------------|---------|
| 资源管理 | Asset Foundation (01) | 7 个 | ✅ 覆盖 |
| 招商管理 | Leasing Pipeline (03) | 5 个 | ✅ 覆盖 |
| 合同管理 | Contract Lifecycle (04) | 5 个 | ✅ 覆盖 |
| 财务管理 | Billing/Collection/Invoice/Accounting (06-09) | 12 个 | ✅ 覆盖 |
| 运营管理 | Operations (10) + Lease/Occupancy (05) | 6 个 | ⚠️ 部分 |
| 物业管理 | Property (11) + Engineering (12) + WorkOrder (13) | 8 个 | ⚠️ 部分 |
| 推广营销 | Marketing (14) + Customer (15) | 3 个 | ⚠️ P1 待补 |
| 系统管理 | — | — | ❌ 非 Ontology 范围 |
| 数据决策 | BI & Analytics (17) | 1 个 | ✅ 覆盖 |
| 预算管理 | — | 3 个 | ⚠️ 跨域 |

**发现**：`business-ontology.yaml` 是按**功能模块**组织的（软件视角），不是按 **Entity** 组织的（Ontology 视角）。这是一个重要差距——AI Agent 需要 Entity 清单，而不是功能模块清单。

---

### 五、D-014 商业事实唯一来源原则 = Ontology Identity 规则

你的 Domain Model 已经做了一个 Ontology 级别的决策——**D-014**：

> **任何业务事实只能有一个 Owner Context。其他 Context 只能引用或消费，不能复制或产生第二真值。**

这就是 Ontology 里的 **Identity Uniqueness Rule**（身份唯一性规则）。举例：

| 业务事实 | 唯一 Owner | AI Agent 的理解 |
|---------|-----------|---------------|
| 营业额采集证据 | Operations | Agent 知道"要查营业额，去 Operations 查，不要去 Billing 查" |
| 合同条款 | Contract | Agent 知道"条款真值在 Contract，Billing 只是消费者" |
| 空间资源身份 | Asset Foundation | Agent 知道"A101 的身份由 Asset 定义，其他域只引用" |

> **D-014 的 Ontology 含义**：AI Agent 在跨 Context 推理时，不会陷入"两个 Context 给出矛盾数据"的问题。每个 Entity 有且只有一个"真值主人"。

---

### 六、AI Agent 视角总结

```
如果 AI Agent 要理解"铺位 A101"，它需要知道：

1. Entity Type    → Resource Unit（空间实体）
2. Identity Path  → 某项目 → 某楼栋 → 某楼层 → A101
3. Owner Context  → Asset Foundation（身份唯一来源）
4. Fact Owner     → Asset Foundation 拥有物理状态
                    Lease/Occupancy 拥有占用状态
                    Billing 拥有计费状态
5. Type           → 商业空间族 / 停车配套族 / 多经点位族

→ 这 5 层信息 = Ontology 对 A101 的完整语义描述
→ Domain Model 只提供了第 1、3、4 层
→ Ontology 需要补：第 2 层（业务身份路径）+ 第 5 层（类型分类）
```

---

## 📝 练习（5 分钟）

拿起你的 Domain Model §3.1 Object Ownership Matrix，选择 **Lease / Occupancy** 这一行：

1. 它的技术身份是什么？
2. 它的业务身份应该怎么定义？（提示：它不是独立实体，而是关系实体——连接了谁和谁？）
3. 如果 AI Agent 问"铺位 A101 现在有没有被占用"，答案需要从哪个 Context 查？为什么不是 Asset Foundation？

> 明天我们抽取 **Relationship**——你 ADR-006 的四类关系，在 Ontology 视角下是否覆盖完整？
