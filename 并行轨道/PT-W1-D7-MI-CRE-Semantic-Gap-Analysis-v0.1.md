# PT-W1 Day 7：MI CRE Semantic Gap Analysis v0.1

> **日期**：2026-08-02（周六）
> **周主题**：DDD → Semantic Model
> **今日定位**：⚡ Week 1 输出日——已有资产 vs 缺失语义的全景图

---

## 为什么需要这份 Gap Analysis

过去六天，我们做了一件事：**用 Ontology 视角重新审视你已有的 Domain Model 资产**。

结论很清晰——**你不缺 Ontology 的雏形，你缺的是一个统一语义层，把散落在六七份文件里的语义构件串成一个 AI 可推理的整体。**

这份 Gap Analysis 就是那张导航图：它告诉你已经站在哪里，还需要补什么，以及后续三周每周补哪一块。

---

## 一、已有资产全景

你手里已经有了这些：

| # | 资产 | 位置 | Ontology 对应 |
|---|---|---|---|
| 1 | **MI Domain Model v1.0**（17 个 Bounded Context） | `docs/lanlnk/out/prd/商管系统/output/domain-model/` | DDD 战略设计：Context 划分 + Object Ownership + Aggregate |
| 2 | **business-ontology.yaml**（11 模块 / ~50 子功能 / 上百场景 / 数百术语） | `docs/lanlnk/config/ontology/business-ontology.yaml` | 初级 Ontology：模块→能力→场景→术语 |
| 3 | **ADR-006 四类对象关系**（Identity Reference / Structural Composition / Hierarchical Containment / Lifecycle Transition Effect） | CRE BCM 目录 | Ontology Relationship Model 治理框架 |
| 4 | **effect-registry.yaml**（5 类冻结 Effect） | CRE BCM 目录 | Ontology Event Model 注册中心 |
| 5 | **CRE BCM 14 域 + 6 个 ADR published** | CRE BCM 目录 | Business Rule + Capability 声明 |
| 6 | **capability-traceability-matrix** | `mi/docs/` | Capability → 代码模块追溯 |
| 7 | **MI 代码仓库**（307 表 + Go 模块化单体） | `/root/mi` | Domain Model 代码实现（事实来源） |
| 8 | **LangChat ADR-001~008** | `docs/lanlnk/out/prd/langchat/output/review/` | AI 平台架构（Capability / Skill / Agent） |

**这不是"从零开始建 Ontology"，这是"把已有资产升级为统一 Semantic Model"。**

---

## 二、Ontology 七维度 Gap Analysis

### 维度总览

| Ontology 维度 | 定义 | 已有资产 | 成熟度 | 关键缺口 | W2-W4 补建计划 |
|---|---|---|---|---|---|
| **Entity** | 世界里有什么东西？ | business-ontology.yaml terms + Object Ownership Matrix | ★★★☆☆ | 缺业务定义（只有术语名，没有"是什么"） | W2 D1 |
| **Identity** | 它如何被唯一识别？ | 表 ID + 编码规则（楼宇编码+楼层编码+流水号） | ★★☆☆☆ | 缺业务身份层级（项目→楼宇→楼层→铺位的 Ontology 路径） | W2 D1 |
| **Relationship** | 事物如何连接？ | ADR-006 四类关系（已覆盖 7 处跨域关系） | ★★★★☆ | 缺语义动词命名（occupies / signs / governs） | W2 D2 |
| **State / Event** | 业务如何变化？ | effect-registry 5 类 Effect + 散落的状态字段 | ★★★☆☆ | 缺完整状态机 + Event 声明格式统一 | W2 D3 |
| **Rule** | 为什么这样变化？ | CRE BCM 域文件（部分显式、部分隐式） | ★★☆☆☆ | 规则未显式化——藏在代码 if-else 里，AI 不可推理 | W2 D4 |
| **Capability** | 可以做什么？ | capabilities 列表 + BCM + traceability matrix | ★★★☆☆ | 缺 Capability → Agent Skill 映射 | W2 D5 |
| **Policy** | 什么条件下允许做？ | 审批流代码（合同审批/减免审批） | ★☆☆☆☆ | 几乎空白——缺 AI 执行约束声明 | W2 D6 |

---

### 逐维度详解

## 维度 1：Entity（★★★☆☆）

### 已有

`business-ontology.yaml` 已列出数百个业务术语：铺位、楼宇、楼层、合同、商户、品牌、账单、保证金、工单、广告位……MI Domain Model §3 Object Ownership Matrix 定义了几十个核心对象及其归属 Context。

### 缺什么

**术语名 ≠ Entity 定义。** "铺位"这个词后面没有写：它是什么？它的业务边界是什么？它和"单元""广告位"的根本区别是什么？

| 现在的表达 | Ontology 需要的表达 |
|---|---|
| `shop` 表，terms 列表里写"铺位" | **铺位** = 可独立租赁的最小商业空间单元，具有唯一编码和计租面积，是租赁关系的最小承载客体 |
| `contract` 表，terms 列表里写"合同" | **合同** = 商管公司与商户之间确立租赁权利义务关系的法律文书，关联铺位、租金方案、租期 |

### AI 受什么影响

> ❌ AI 看到 `shop` 表知道是一条数据库记录
> ❌ AI 看到 terms 列里有"铺位"知道是一个业务词汇
> ✅ AI 需要："铺位 = 可独立租赁的最小商业空间单元"——才能理解"这个铺位能不能拆分"

---

## 维度 2：Identity（★★☆☆☆）

### 已有

- 表主键：`shop.id = 12345`
- 编码规则：铺位编码 = 楼宇编码 + 楼层编码 + 流水号（如 B1-F2-015）

### 缺什么

**技术编码 ≠ 业务身份。** Ontology 需要的是层级化的业务身份路径：

```
技术身份：shop.id = 12345（数据库主键）
编码身份：B1-F2-015（铺位编码）

业务身份（Ontology 需要）：
  万象城（项目）
    └── A 栋（楼宇）
         └── L2（楼层）
              └── L2-015（铺位）← 业务身份锚点
```

### AI 受什么影响

当用户问"A 栋二楼那个奶茶店旁边的是哪个铺位"，AI 需要通过层级关系定位 Entity，而不是要求用户先提供数据库 ID。

---

## 维度 3：Relationship（★★★★☆）

### 已有

**ADR-006 是你最强的 Ontology 资产。** 四类对象关系覆盖了静态结构和动态影响：

| 关系类别 | 定义 | 已验证案例 |
|---|---|---|
| Identity Reference | 类型化字段引用另一个对象的身份 | 合同↔商户 |
| Structural Composition | 对象是另一个对象的组成部件 | 资源↔仪表/设备 |
| Hierarchical Containment | 树状组织包含关系 | 项目→楼宇→楼层→资源 |
| Lifecycle Transition Effect | 对象生命周期迁移导致另一类型对象状态变化 | 合同生效→铺位占用 |

经过 6 个域的压力测试验证（财务 POC + 合同 + 租赁 + 招商 + 运营 + 商户），覆盖交易链、资源拓扑、CRM 转化、状态维护、主体生命周期五种业务模式。

### 缺什么

**关系分类 ✅ 有了，但关系缺少语义动词命名。** ADR-006 定义了关系的**类别**（四类），但每对关系缺少一个**业务动词**：

| 现在的表达 | Ontology 需要的表达 |
|---|---|
| 合同.shop_id = FK 引用（Identity Reference 类） | Lease **occupies** Space |
| 合同.tenant_id = FK 引用（Identity Reference 类） | Lease **is-signed-by** Tenant |
| 铺位.building_id = FK 引用（Hierarchical Containment 类） | Space **is-located-in** Building |
| 合同生效 → effect（Lifecycle Transition Effect 类） | Lease.activated **triggers** → Space: status=occupied |

> **FK 告诉 AI "两个表有连接"，语义动词告诉 AI "它们是什么关系"。**

---

## 维度 4：State / Event（★★★☆☆）

### 已有

**effect-registry.yaml 已经冻结 5 类 Effect**，这是一个扎实的 Event Model 雏形：

| effect_type | 语义 | 注册域 |
|---|---|---|
| state-transition-effect | 对象状态传播 | 通用 |
| occupancy-effect | 资源占用变化 | 租赁 |
| financial-effect | 财务影响 | 财务 |
| lead-conversion-effect | 招商转化链 | 招商 |
| maintenance-effect | 维护流程影响 | 运营 |

### 缺什么

**Effect 注册了，但每个核心实体的完整状态机散落各处。**

现在的状态分布在三四个地方：

```
铺位状态：空置、已租、锁定、已退出  ← business-ontology.yaml 场景描述
合同状态：草稿、已签、生效、到期、终止  ← 散落在代码 if-else 里
账单状态：待出账、已出账、已收款、已核销  ← 散落在字段枚举里
```

AI 需要的是每个核心实体的**完整状态机 + 迁移条件 + 触发 Event**：

```
Lease Lifecycle:
  Draft → Signed → Active → Expiring → Expired → Terminated
  
  每个迁移点：
    Signed → Active:
      event: lease.activated
      effects:
        - occupancy-effect → Space: status = occupied
        - financial-effect → BillingPlan: generate receivables
    
    Active → Expiring:
      event: lease.entering_expiry_window
      trigger: current_date >= lease.end_date - 30d
    
    Expired → Terminated:
      event: lease.terminated
      effects:
        - occupancy-effect → Space: status = available_for_release
        - financial-effect → SecurityDeposit: trigger refund flow
```

---

## 维度 5：Rule（★★☆☆☆）

### 已有

CRE BCM 14 个域文件里有部分业务规则显式声明（如 ADR-006 的迁移规则、各域 §8 的压力测试规则）。

### 缺什么

**大部分业务规则仍然藏在代码的 if-else 里，AI 看不见。**

```
现在的规则分布：
  ❌ 代码 if-else：if (lease.status == 'expired' && space.inspection != 'done') { ... }
  ❌ 业务人员的脑子里：("退租铺位必须先验收"——没写在任何文件里）
  ✅ BCM 域文件（少数显式声明，但格式不统一）

Ontology 需要的格式：
  Rule: "存在未完成退租流程的 Space 不可出租"
  Condition: Space.Lease.status ∈ {Terminating, Terminated} 
              AND Space.inspection != Completed
  Effect: Space.available_for_lease = false
  Source: 03-租赁管理.md §8.2.5
```

> **规则藏在代码里 = AI 瞎了。规则声明在 Ontology 里 = AI 能推理。**

---

## 维度 6：Capability（★★★☆☆）

### 已有

- `business-ontology.yaml` 每个子功能下有 capabilities 列表
- CRE BCM 14 个域有 capability 行声明
- `capability-traceability-matrix.md` 追溯 Capability → MI 代码模块

### 缺什么

**Capability 声明了，但缺少到 Agent Skill 的映射。** 当前的追溯链是：

```
Capability → MI 代码模块 ✅（已有）
Capability → Agent Skill ❌（缺）
Capability → 执行权限/前置条件 ❌（缺）
```

Ontology 需要补建：

```
Capability: 铺位建档
  Executable by: 招商运营数字员工
  Required Role: 招商经理
  Precondition: 楼层已建档 AND 用户有 create_shop 权限
  Skill: shop-create-v1
  Effect: Space.created → 触发租控图更新
```

---

## 维度 7：Policy（★☆☆☆☆）

### 已有

MI 代码里有审批流实现（合同审批、减免审批），但这些是**流程实现**，不是**Policy 声明**。

### 缺什么

**几乎空白。** Policy 是"即使知道怎么做，没有授权也不能做"的声明层：

```
Policy: 合同减免审批
  Rule: 租金减免 > 10% 需区域总审批
  Rule: 租金减免 > 20% 需集团总部审批
  Enforced by: LangChat ApplicationContract.effect_policy
  Audit: 记录审批链 + 决策依据
```

> 这一层是从**代码里的审批流**升级到**AI 可执行的约束声明**。Agent 需要知道"我能做什么"的边界在哪。

---

## 三、Ontology 层级图

```
企业现实业务世界
（万象城的日常运营：招租、签约、收租、退租、维修……）
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Ontology / Semantic Model                        │
│ 描述：有什么、什么关系、什么约束                    │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Entity   │ │Identity  │ │ Relationship     │ │
│  │ 铺位/合同 │ │项目→楼宇 │ │ occupies/signs   │ │
│  │ 商户/账单 │ │→楼层→铺位│ │ governs/triggers │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ State/   │ │ Rule     │ │ Capability       │ │
│  │ Event    │ │ 退租验收 │ │ 铺位建档/合同签订 │ │
│  │ 状态机   │ │ 不可出租 │ │ 账单生成/收款核销 │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐                                    │
│  │ Policy   │ ← 最薄弱的层                       │
│  │ 审批权限 │                                    │
│  └──────────┘                                    │
└─────────────────────────────────────────────────┘
    │                              │
    ▼                              ▼
┌──────────────┐          ┌──────────────┐
│ Domain Model │          │Knowledge Model│
│ 怎么软件实现  │          │ 什么知识需要  │
│              │          │ 被检索        │
│ MI 代码       │          │ LangChat RAG │
│ 307 表       │          │ 企业知识库    │
└──────────────┘          └──────────────┘
    │                              │
    ▼                              ▼
┌──────────────────────────────────────────────┐
│ Code / RAG Implementation                     │
│ Go 模块化单体 + 向量检索 + Function Calling    │
└──────────────────────────────────────────────┘
```

---

## 四、一周认知回顾

| Day | 主题 | 核心发现 |
|---|---|---|
| D1 | 你已经做了 Domain Model | 17 个 Bounded Context = DDD 战略设计的实践。P0 的 9 个 Full Model = Core Domain |
| D2 | Bounded Context 验证 | 你的 Context 划分基于业务域（招商/合同/租赁/财务…），符合 DDD 战略设计原则 |
| D3 | Entity / Aggregate | Object Ownership Matrix 里的对象就是 Entity，Aggregate 根已经识别（如 Lease 聚合了 Space/Tenant/Billing） |
| D4 | 为什么 Domain Model 不够 | **核心课**——AI 读 Domain Model 只看到表结构，看不到语义。Identity Reference 是技术 FK，不是业务关系 |
| D5 | Ontology 能补充什么 | 六维度 Gap Analysis：Relationship 最强（ADR-006），Policy 最弱（几乎空白） |
| D6 | Ontology vs Knowledge vs RAG | 三层分离——Ontology = 结构语义，Knowledge = 内容资产，RAG = 检索机制。三者协作不可互相替代 |

---

## 五、关键设计判断的变化

```
以前：MI Domain Model v1.0 是一份技术架构文档
现在：MI Domain Model v1.0 是 Ontology 的第一层——Entity + Ownership，
      但缺少 Identity 层级、语义关系命名、显式规则

以前：business-ontology.yaml 是一份业务术语表和功能清单
现在：business-ontology.yaml 是一个初级 Ontology，
      骨架已对（模块→能力→场景），但需要补七层语义

以前：effect-registry 是一个技术配置文件
现在：effect-registry 是 Ontology Event Model 的注册中心，
      5 类 effect 已覆盖核心业务模式

以前：ADR-006 四类关系是架构文档
现在：ADR-006 是 Ontology Relationship Model 的治理框架，
      是你最强的 Ontology 资产（经过 6 域压力测试验证）

以前：CRE BCM 14 域是业务能力清单
现在：CRE BCM 14 域是 Capability Model 的声明层，
      但缺少 Capability → Agent Skill 的映射

以前：审批流是 MI 代码里的流程实现
现在：审批流需要升级为 Policy Model——AI 可读的执行约束声明
```

---

## 六、后续三周的补建路线

这份 Gap Analysis 直接映射到 W2-W4 的工作：

```
Week 2（8/3-8/9）：Business Ontology Extraction
  从已有材料中逐维度抽取语义，输出 MI CRE Ontology Graph v0.1
  
  D1: Entity + Identity 抽取   ← 补维度 1、2 的缺口
  D2: Relationship 抽取         ← 补维度 3 的语义动词命名
  D3: Lifecycle + Event 抽取    ← 补维度 4 的完整状态机
  D4: Rule 抽取                 ← 补维度 5 的显式化
  D5: Capability 抽取           ← 补维度 6 的 Skill 映射
  D6: Policy 抽取 + Compiler 初探 ← 补维度 7 + 引入 Ontology Compiler
  D7: 组装 Ontology Graph v0.1

Week 3（8/10-8/16）：Ontology → Agent Architecture
  理解 Ontology 在 AI Agent 架构中的角色
  重点：Ontology Compiler（语义→能力的编译链路）
  输出：LangChat × Ontology × Compiler 集成方案

Week 4（8/17-8/23）：Semantic Model + Digital Employee Validation
  升级为完整 Semantic Model v0.1
  通过数字员工场景验证（"A101 铺位为什么不能出租？"）
  输出：毕业作品 + 验证报告
```

---

## 七、练习（10 分钟）

这是 Week 1 的毕业练习。

打开这份 Gap Analysis 表，挑**一个 Core Domain 实体**（建议选"铺位"或"合同"），完成以下填空：

```
实体名称：______

1. Entity 定义
   它是什么？（一句话业务定义，不是技术描述）
   _______________________________________________

2. Identity
   它的业务身份路径是什么？
   项目 → 楼宇 → 楼层 → ______

3. Relationship
   它和其他实体之间的关系动词：
   - 和______的关系：______（如 occupies）
   - 和______的关系：______（如 is-signed-by）

4. State / Event
   它的状态有哪些？画出状态迁移图：
   ______ → ______ → ______ → ______

5. Rule
   一条业务规则（现在藏在代码里的）：
   "当______时，______"

6. Capability
   它关联的能力有哪些？哪个 Agent 可以执行？
   Capability: ______ → Skill: ______

7. Policy
   执行这个能力需要什么授权？
   _______________________________________________
```

**不需要完美。写下来本身就是 Ontology 建模的第一步。**

---

## 八、Week 1 总结

> **你不是一个 Ontology 新手。你是一个已经做出 Domain Model + BCM + ADR-006 的架构师，现在要用 Ontology 视角把这些资产升级为统一 Semantic Model。**

Week 1 的核心收获：

1. **你的 17 个 Bounded Context 就是 DDD 战略设计**——不是巧合，是实践
2. **ADR-006 四类关系是你最强的 Ontology 资产**——经过 6 域验证的关系治理框架
3. **effect-registry 5 类 Effect 是 Event Model 的雏形**——已冻结、已注册
4. **最大的缺口在 Policy 层（★☆☆☆☆）和 Rule 层（★★☆☆☆）**——规则藏在代码里，AI 看不见
5. **Ontology / Knowledge / RAG 三层分离**——结构语义、内容资产、检索机制各司其职

Week 2 开始，我们将从"诊断"转向"施工"——从已有材料中逐维度抽取语义，组装 MI CRE Ontology Graph v0.1。
