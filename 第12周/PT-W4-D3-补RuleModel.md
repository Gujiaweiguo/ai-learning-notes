# PT-W4-D3 · 补 Rule Model：从表格散文到 AI 可推理的规则声明

> 日期：2026-08-19（PT-W4 Day 3）｜毕业作品《MI CRE Enterprise Semantic Model v0.1》第三层
>
> 真实材料：MI Domain Model v1.0 Lease/Occupancy 域"领域规则 + 不变量"（D-001 Amendment A）+ CRE BCM 02-合同管理 §3.7/3.8（CRE-CON-024/026/027）+ 03-租赁管理 §3.4/3.6（CRE-LEA-007/008/010/011）业务规则列

---

## 一、毕业作品进度

```
D1 ✅ Ontology Model（Entity + Identity + Relationship）
D2 ✅ Lifecycle + Event Model（状态机 + 迁移声明）
D3 📍 Rule Model（今天）
D4    Capability + Policy Model
D5    Agent Mapping
D6-D7 组装 + Digital Employee Validation
```

昨天 D2 把**守卫（Guard）**显式化进了迁移声明——"终止前置条件是 Inspection 完成"。但守卫只是规则家族里的一个物种。今天把整族规则补齐：**这是验证场景 L3（规则判断）的直接依赖**。没有 Rule Model，Agent 能"看懂"A101 的状态（L2），但不能判断"**能不能**"（L3）。

---

## 二、现状盘点：你的规则现在住在哪里

| 藏身处 | 格式 | 实例 | AI 能用吗 |
|---|---|---|---|
| Domain Model 领域规则块 | 伪代码公式 | `AvailableForLeasing = Active ∧ no Occupancy ∧ no Restriction` | ✅ 最接近可推理，但只有零星几条 |
| Domain Model 不变量清单 | 编号散文 | "一个 Resource Unit 同一时间只有一个 Active Occupancy" | ⚠️ 有 ID 有语义，无谓词结构 |
| BCM 能力矩阵"业务规则"列 | 长散文 | CRE-LEA-011："费用未清算不许退场；首期欠缴不许进场（万达）、未挂表不许开业（中旅）……" | ❌ 一段话混了 5 条规则 + 客户变体 + 成熟度备注 |
| MI 代码 if-else | Go 代码 | `ErrInvalidTransition` 原子失败 | ❌ AI 能读到，但无法当业务依据引用 |

**关键观察**：你的规则不缺治理（BCM 每行都有 ID 和 evidence），缺的是**统一声明格式**——同一个"规则"概念，四种载体四种写法，AI 无法把"费用未清算不许退场"应用到"合同 #1234 清算未完成"这个实例上，因为这句话没有结构化谓词，也没有链接到 D1/D2 已建好的概念。

还有一条早已埋下的伏笔——**D-001 Amendment A**："铺位可出租"不是 Asset 字段，是 Domain Rule（组合判断）。这条架构决策本质上是 Rule Model 的第一课：**什么应该是存储的状态，什么应该是推导的结论**。你三个月前就已经在做 Rule Model 的分类学判断了，只是没叫它这个名字。

---

## 三、核心概念：规则的四个物种

按"**判定主体 + 违反后果**"分类（这是今天的方法论核心）：

| 物种 | 回答什么 | 违反后果 | MI 真实实例 |
|---|---|---|---|
| **Invariant 不变量** | 什么必须**永远**为真 | 系统级错误（不可能的事发生了 = 有 bug） | 一个 RU 同一时间只有一个 Active Occupancy |
| **Guard 守卫** | **这次**迁移/操作允许吗 | 操作被拒绝，状态不变（`ErrInvalidTransition`） | 费用未清算不许退场；作废前置无有效账单/销售/预存 |
| **Derivation 推导规则** | 这个结论由哪些事实**算出** | 不适用（它是计算，不是判断） | AvailableForLeasing = Active ∧ no Occupancy ∧ no Restriction |
| **Variant 变体规则** | **这家客户**适用哪一版 | 基础规则被替换/追加 | 首期欠缴不许进场（万达版）vs 未挂表不许开业（中旅版） |

三个关键辨析：

**1. Derivation vs 状态字段。** "可出租"要不要落库？D-001 A 已裁决：不落。它是三个事实的函数，落库 = 制造第四个可能不一致的事实来源。对 AI 的意义：推导规则让 Agent **永远从事实重新计算**，而不是信任可能过期的快照——这与 LLM 的"重算优于缓存"天然同构。

**2. Guard vs Invariant。** Guard 是**入口检查**（拒绝这次操作，世界不变），Invariant 是**出口断言**（如果违反，说明写路径有 bug，世界已坏）。MI 的"混合状态批量 Reserve/Release 写入前以 ErrInvalidTransition 原子失败"是标准 Guard 语义；"一个 RU 只有一个 Active Occupancy"如果被违反，不是拒绝操作能解决的，是数据已脏。

**3. Rule vs Policy（明天 D4 的分界线）。** Rule 说"业务上什么**合法**"（费用未清算不许退场），Policy 说"谁有权决定、走什么审批路径"。注意 CRE-CON-024 里两者同时出现："合同终止**无需审批**、终止**申请**需审批"——前半句是 Policy 裁决（免审批路径），后半句的审批流本身是 Policy 体系。今天只做 Rule，明天补 Policy。

---

## 四、AI 可推理格式的三要素

一条散文规则变成 AI 可推理，需要补三样东西：

```
1. 结构化谓词   条件 = 原子谓词的合取，每个谓词引用 Ontology 概念
                 （Contract.inspection_status == completed），不是自然语言
2. 概念引用     谓词里的每个名词都能在 D1 Entity / D2 Lifecycle 里找到定义
                 —— 规则是 Ontology 的公民，不是代码的注释
3. 证据链接     evidence 指回 BCM 行 ID / PRD 行号
                 —— Agent 回答"依据"时引用业务条文，而不是"代码这么写的"
```

**Rule Card 示范**（把 CRE-LEA-011 散文升级）：

```
Rule ID:      CRE-R-014
Species:      Guard
Scope:        Lease Termination（挂载点：D2 迁移声明 Active→Terminated）
Statement:    退场登记前，合同清算必须完成
Predicates:   Contract.settlement_status == completed
On Violation: 拒绝退场登记（保持 Contract=Terminating, Space=Occupied）
Evidence:     CRE-LEA-011 业务规则列
Variant:      base
```

对照原文："费用未清算不许退场"——人读没问题；AI 读不出**谓词作用的对象是谁、违反时世界保持什么状态、依据哪条业务条文**。

---

## 五、升级动作：A101 验证场景的规则清单

从四个来源抽取、拆分、分类（这就是毕业作品 Rule Model 章节的雏形——今天示范 A101 场景所需的最小集）：

| Rule ID | 物种 | 规则声明 | 证据来源 |
|---|---|---|---|
| CRE-R-001 | Invariant | 一个 RU 同一时间只有一个 Active Occupancy | Domain Model Lease/Occupancy 不变量 1 |
| CRE-R-002 | Derivation | AvailableForLeasing = Asset.Active ∧ no Occupancy ∧ no Restriction | Domain Model 领域规则（D-001 A） |
| CRE-R-003 | Guard | 存在未完成退租流程的 Space 不可新签约；终止守卫 = Inspection 完成 ∧ 清算完成 | D2 迁移声明 3 + CRE-LEA-011 |
| CRE-R-008 | Guard | 预定到期自动释放；预定生效后其他人不可选 | CRE-LEA-008 |
| CRE-R-010 | Guard | 作废仅适用"已签未进场" ∧ 无有效账单/销售/预存 | CRE-CON-026 |
| CRE-R-011 | Guard | 账款未开票的合同不可结束 | CRE-CON-027 |
| CRE-R-020 | Variant | 进场守卫：万达版 = 首期欠缴不许进场；中旅版 = 未挂表不许开业 | CRE-LEA-011 |

两个结构要点：

1. **CRE-R-003 直接继承 D2 的守卫**。Lifecycle 迁移声明与 Rule 清单不是两套体系——**Guard 是规则在迁移上的挂载点**，迁移声明引用 Rule ID，规则声明标注 Scope 指回迁移。两层互相引用，不重复定义。
2. **Variant 不是独立规则，是规则的客户维度**。CRE-R-020 的 base/万达/中旅三版共享同一个 Rule ID，部署时按租户选择。这就是"客户经验差异"从 BCM 散文里被解放出来变成**配置**的过程。

---

## 六、Agent 视角：L3 规则判断预演

> 验证问题："A101 铺位为什么不能出租？"

| 升级前（散文规则） | 升级后（Rule Card 驱动） |
|---|---|
| AI 读 CRE-LEA-011 那段长散文，靠 LLM 语感猜"可能因为退租没完成"——不可靠、不可解释、不可引用 | 沿 D1 关系定位 Contract → D2 状态机定位 **Terminating** → 评估 CRE-R-002：Active ✓ / no Occupancy ✗ → 推导 **False** → 引用失败分支 CRE-R-003（守卫未满足：Inspection 未完成）→ 输出依据与建议 |

Agent 的最终回答（D7 验证目标）：

```
原因：该空间存在未完成退租流程
依据：Rule CRE-R-003（Guard，evidence: D2 迁移声明 + CRE-LEA-011）
当前状态：Contract=Terminating，Inspection 未完成，清算进行中
建议动作：创建 Inspection Task；完成后触发 ContractTerminated → occupancy-effect → A101 释放
```

注意最后一句——建议动作的"完成后会怎样"引用的是 **D2 的 Event/Effect**，"为什么不能"引用的是**今天的 Rule**，"它是谁、连着谁"引用的是 **D1 的 Relationship**。三层各答一问，这就是 Semantic Model 分层的意义：**每一层只回答一个问题，合起来回答完整业务问题**。

---

## 七、架构师视角

- **以前**：规则 = BCM 表格散文 + Domain Model 零星伪代码 + 代码 if-else + 客户差异混在备注里。人可读，AI 不可推理；同一规则四种载体，改一处漏三处。
- **现在**：规则 = **Rule Card**（ID + 物种 + 谓词 + 挂载点 + 证据 + 变体）。四物种决定执行位置：**Invariant 进写路径断言、Guard 进迁移入口、Derivation 进查询/推理层、Variant 进租户配置**。不是把规则从代码里搬出来，而是给规则一个 **Ontology 身份**——让每条规则像 effect_type 一样可注册、可冻结、可追溯（你已经用 registry 治理过 Effect，今天只是把同一品味应用到 Rule）。

---

## 八、练习（5 分钟）

两道题，都在考"物种边界感"：

1. CRE-LEA-008 有一条"**预定到期自动释放**"。它是四个物种里的哪个？（陷阱提示：它没有条件判断、不拒绝任何操作——想想它是不是根本不归 Rule Model 管，而应该回到 D2 的 Event/Lifecycle 声明？如果是，Guard 和时间触发型迁移的分界线画在哪？）
2. 把"混合状态批量 Reserve/Release 在写入前以 `ErrInvalidTransition` 原子失败并保持原状态"分类，并解释：为什么它是 Guard 而不是 Invariant？（用"违反时世界处于什么状态"来判断。）

---

*配套实验：`PT-W4-D3-补RuleModel.ipynb` —— 用 60 行 Python 实现四物种 Rule Card 引擎，跑通 A101 场景的 L3 规则判断 + 万达/中旅变体切换。*
