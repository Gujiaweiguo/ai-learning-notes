# PT-W1 Day2：DDD 战略设计 — 你已经做了

📅 日期：2026-07-28（周一）
并行轨道：Business Semantic Architecture（PT-W1: DDD → Semantic Model）
今日主题：**用 DDD 战略设计原则验证你的 Bounded Context 划分**

---

## 核心问题

> 我的 17 个 Bounded Context 划分对不对？

**答案是：大部分对了，但有几个值得重新审视。**

---

## 1. DDD 战略设计核心原则（60秒版）

DDD 战略设计关注三件事：

### ① Bounded Context 划分
> 每个 Context 应该有明确的业务边界，内部有一致的语义模型。

**检验标准**：一个概念在不同 Context 里可以有不同的含义。

例子：`Space`（空间）
- 在 Space Management 里：铺位的物理属性（面积、楼层、位置）
- 在 Lease Management 里：可租赁单元（租金、租期、状态）
- 在 Property Service 里：维护对象（设备、工单、巡检）

同一个 Space，三个 Context 关注的面不同。**如果它们共用一个 Space 模型，说明 Context 边界没划好。**

### ② Context Map（上下文映射）
> Context 之间如何协作？谁调用谁？翻译在哪里发生？

类型：
- **Shared Kernel**（共享内核）：两个 Context 共享一部分模型
- **Customer-Supplier**（客户-供应商）：下游依赖上游
- **Conformist**（遵奉者）：下游无条件遵从上游
- **Anti-Corruption Layer**（防腐层）：下游建翻译层隔离上游

### ③ Core Domain vs Supporting Domain
> 什么是你最核心的竞争力？什么是支撑性的？

---

## 2. 验证你的 17 个 Context

### P0（Core Domain）— 9 个 Full Model

| Context | 核心职责 | 验证 |
|---------|---------|------|
| Property Management | 资产树管理 | ✅ 独立的核心领域 |
| Space Management | 空间/铺位管理 | ✅ 独立 |
| Lease Management | 租赁全生命周期 | ✅ 核心 — 这是 CRE 最重要的业务 |
| Tenant Management | 租户档案 | ✅ 独立 |
| Contract Management | 合同管理 | ⚠️ 与 Lease 的边界？Contract 是法律文档管理，Lease 是业务执行 |
| Billing Management | 账单生成 | ✅ 独立 |
| Payment Management | 收款处理 | ✅ 独立 |
| Finance Settlement | 财务结算 | ✅ 独立 |
| Customer Management | 客户（潜在租户） | ⚠️ 与 Tenant 的边界？Customer 是营销视角，Tenant 是合同视角 |

### P1（Supporting Domain）— 8 个

| Context | 评估 |
|---------|------|
| Sales/Mall Operations | ✅ 支撑域 |
| Marketing/Promotion | ✅ 支撑域 |
| Property Service | ✅ 支撑域 |
| Asset Evaluation | ✅ 可考虑合并到 Finance？ |
| Energy Management | ✅ 独立但低频 |
| Park Operations | ⚠️ 与 Property Management 有重叠？ |
| Report/Analytics | ✅ 这是 Generic Domain（不是核心业务） |
| System/Admin | ✅ Generic Domain |

### 发现的问题

1. **Contract vs Lease 边界模糊**
   - Contract 管合同文档（条款、附件、用印）
   - Lease 管租赁业务（租期、租金、状态）
   - 划分合理，但需要 Context Map 声明它们的关系

2. **Customer vs Tenant 边界模糊**
   - Customer 是潜在租户（CRM 视角）
   - Tenant 是签约租户（合同视角）
   - 划分合理，但 Customer → Tenant 的转换流程需要明确

3. **Park Operations vs Property Management**
   - 如果是不同业态（园区 vs 商场），应该统一为 Property Management + 业态标签
   - 如果是不同业务（招商 vs 运营），应该独立

---

## 3. 你的 Context Map 现状

| 关系类型 | 示例 | 你的现状 |
|---------|------|---------|
| Customer-Supplier | Billing → Payment（账单驱动收款） | ✅ 隐式存在 |
| Shared Kernel | Lease 和 Contract 共享 Lease 概念 | ⚠️ 没有显式声明 |
| ACL | Payment 不应该直接依赖 Lease 内部状态 | ❌ 可能存在耦合 |

**关键 Gap**：你的 Context 之间的关系是隐式的（代码里调），不是显式的（Context Map 声明）。

---

## 4. Ontology 视角：Context Map 为什么重要

AI Agent 需要知道：
- "合同查询"应该查 Contract Context 还是 Lease Context？
- "客户分析"的 Customer 和签约的 Tenant 是同一个人吗？
- Billing 和 Payment 的关系是什么？

**如果 Context Map 是隐式的，AI 必须通过代码推理来理解这些关系——这不可靠。**

显式的 Context Map 就是给 AI 一张"业务地图"：
```
Lease Management → signs → Contract Management
Lease Management → occupies → Space Management
Billing Management → depends on → Lease Management
Payment Management → settles → Finance Settlement
Customer Management → converts to → Tenant Management
```

---

## 5. CRE BCM 14 域对照

你的 CRE Business Capability Matrix 有 14 个域，与 Domain Model 的 17 个 Context 对应：

| BCM 域 | Domain Model Context | 关系 |
|--------|---------------------|------|
| 招商管理 | Customer + Lease | 跨两个 Context |
| 合同管理 | Contract + Lease | 跨两个 Context |
| 财务管理 | Billing + Payment + Finance | 跨三个 Context |

**发现**：BCM 域是**业务视角**，Domain Model Context 是**软件视角**。它们不是一一对应，而是多对多关系。

这个映射关系本身就是 Ontology 的一部分。

---

## 6. 今天的关键认知

1. **你的 Context 划分 80% 是对的** — 问题是边界关系没有显式化
2. **Context Map 是 AI 理解业务的关键** — 隐式关系要变成显式声明
3. **Core Domain 不是固定的** — 随着业务发展，P1 可能变成 P0
4. **BCM 域 ≠ Domain Context** — 业务视角和软件视角是两个维度，需要 Ontology 桥接

---

## 7. 连接思考（主线 ↔ 并行）

主线今天拆 **SkillRelease**（唯一可部署单元），并行今天看 **Bounded Context**（业务边界划分）。

共同认知：**边界划分是架构设计的核心。**
- SkillRelease 划定了"对外暴露什么"的边界
- Bounded Context 划定了"业务领域在哪里结束"的边界
- 两者都遵循同一个原则：**边界内高内聚，边界间低耦合**

---

## 8. 练习（5分钟）

> 看看你的 MI Domain Model 里 Lease 和 Contract 两个 Context。它们的代码有没有互相直接 import？如果 Lease 直接读 Contract 的内部模型，说明边界有泄漏。该不该加一层翻译？

---

## 9. 明日预告

D3：**DDD 战术速览 + 你的 Aggregate**
Entity / Value Object / Aggregate 在 MI 里长什么样？你的 Aggregate 根是否正确？
