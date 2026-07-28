# PT-W1 Day1：你已经做了 Domain Model

📅 日期：2026-07-27（周日）
并行轨道：Business Semantic Architecture（PT-W1: DDD → Semantic Model）
今日主题：**用 Ontology 视角重新认识你已有的 Domain Model**

---

## 核心问题

> 我做的 17 个 Context 就是 DDD 吗？

**答案是：大部分是的。** 你在不知不觉中已经做了 DDD 战略设计的核心工作。

---

## 1. DDD 是什么（30秒版）

DDD（Domain-Driven Design）不是写代码的技术，是**理解业务然后建模**的方法论。

核心就一句话：
> **软件结构要反映业务结构，不是反过来。**

你做 MI 商管系统时，不是先想"数据库怎么设计"，而是先想"商业地产有哪些业务领域"——这就是 DDD。

---

## 2. 你已经做了什么

### MI Domain Model v1.0 — 17 个 Bounded Context

| # | Context | 优先级 | 说明 |
|---|---------|--------|------|
| 1 | Property Management | P0 | 物业资产管理 |
| 2 | Space Management | P0 | 铺位/空间管理 |
| 3 | Lease Management | P0 | 租赁管理 |
| 4 | Tenant Management | P0 | 租户管理 |
| 5 | Contract Management | P0 | 合同管理 |
| 6 | Billing Management | P0 | 账单管理 |
| 7 | Payment Management | P0 | 收款管理 |
| 8 | Finance Settlement | P0 | 财务结算 |
| 9 | Customer Management | P0 | 客户管理 |
| 10 | Sales/Mall Operations | P1 | 销售/商场运营 |
| 11 | Marketing/Promotion | P1 | 营销推广 |
| 12 | Property Service | P1 | 物业服务 |
| 13 | Asset Evaluation | P1 | 资产评估 |
| 14 | Energy Management | P1 | 能源管理 |
| 15 | Park Operations | P1 | 园区运营 |
| 16 | Report/Analytics | P1 | 报表分析 |
| 17 | System/Admin | P1 | 系统管理 |

### DDD 对照

| DDD 概念 | 你的对应物 | 符合度 |
|---------|----------|--------|
| **Domain** | 商业地产运营管理 | ✅ 完整 |
| **Bounded Context** | 17 个 Context | ✅ 你做了边界划分 |
| **Core Domain** | P0 的 9 个 Full Model | ✅ 你区分了核心和支撑 |
| **Supporting Domain** | P1 的 8 个 | ✅ |
| **Context Map** | 跨 Context 集成契约 | ⚠️ 有但不够显式 |
| **Ubiquitous Language** | 域知识.md + 术语表 | ⚠️ 部分有 |

**结论**：你的 DDD 战略设计完成度约 70-80%。

---

## 3. Ontology 视角：你的 Domain Model 缺什么

| Ontology 维度 | 你有吗 | 在哪里 | 缺什么 |
|--------------|--------|--------|--------|
| **Concept（概念）** | ✅ | 17 Context + 每个内的对象 | 缺业务定义（只有技术定义） |
| **Identity（身份）** | ⚠️ | 表 ID / 编码 | 缺业务身份层级（Building→Floor→Unit→Shop） |
| **Relationship（关系）** | ⚠️ | ADR-006 四类关系 | 缺语义命名（occupies/signs/governs） |
| **Lifecycle（生命周期）** | ⚠️ | status 字段 + effect-registry | 缺完整状态机 + Event 声明 |
| **Rule（规则）** | ⚠️ | 部分代码 + BCM 规则 | 未显式化（AI 不可推理） |
| **Capability（能力）** | ⚠️ | CRE BCM capability 行 | 缺 Skill 映射 |

**关键认知**：你做的是"软件工程师视角的 Domain Model"，缺的是"AI 可理解的语义层"。

---

## 4. 为什么 Domain Model 不等于 Ontology

打个比方：

- **Domain Model** = 建筑施工图（给工程师看的，关注怎么实现）
- **Ontology** = 建筑说明书（给使用者/AI 看的，关注这是什么、为什么存在、如何使用）

例子：`lease` 表

| 视角 | Domain Model 说 | Ontology 应该说 |
|------|-----------------|----------------|
| 字段 | `id, space_id, tenant_id, status, start_date, end_date` | Lease 是租户与空间之间的法律协议 |
| 关系 | `lease.space_id FK → space.id` | Lease **occupies** Space（占用关系）|
| 状态 | `status='active'` | Lease 处于生效期，意味着 Space 被占用，Billing 应该产生 |
| 规则 | `if lease.status=='terminated' then space.status='available'` | Lease 终止 → Space 释放（但需 inspection 完成才可用）|

**区别核心**：Domain Model 描述"数据怎么存"，Ontology 描述"业务世界怎么运作"。

---

## 5. 今天的关键认知

1. **你已经做了 DDD，只是没叫这个名字** — 17 个 Bounded Context 划分是真实的 DDD 战略设计
2. **Domain Model 是 Ontology 的基础，不是替代品** — 你需要的是在 Domain Model 之上加一个语义层
3. **从"软件视角"切换到"AI 视角"** — 以前是给程序员看的，现在是给 AI Agent 看的
4. **你的已有资产远超你以为的** — Domain Model + BCM + ADR-006 + effect-registry 合在一起就是 Ontology 雏形

---

## 6. 连接思考（主线 ↔ 并行）

主线今天拆 **BlueprintVersion**（制品不是配置），并行今天看 **Domain Model**（语义不是数据）。

共同认知：**不要把"设计制品"和"实现细节"混淆。**
- Blueprint 是设计制品，不是配置文件
- Domain Model 是语义描述，不是表结构
- Ontology 是业务世界模型，不是 UML 图

---

## 7. 明日预告

D2：**DDD 战略设计 — 你已经做了**
验证 17 个 Bounded Context 的边界划分是否合理。对照 DDD 战略设计原则，看哪些边界划对了、哪些需要调整。
