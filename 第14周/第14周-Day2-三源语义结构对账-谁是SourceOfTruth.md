# 🧱 W14-D2 · 两套语义结构的对账：business-ontology.yaml vs MI Domain Model vs openspec specs

> 开发期 · Week 14「语义资产工程化」Day 2（2026-09-01 周二）
> 昨日 D1（lnkcre 现状对齐）cron 未产出，关键对齐事实（273 specs、R-wave、lease→cash 验收链）已并入今日对账。

---

## 0. 今日开发目标

把 docs 仓里的三套语义结构做一次**名字级对账**，回答 Today's Question，并产出第一张「模块 × BCM 域 × Context」映射表（v0.1 手工版，D3 出程序化版本）：

```
① business-ontology.yaml   （config/ontology/，模块→能力→场景）
② MI Domain Model v1.0.x    （20-architecture/mi-cre/domain-model/，17 Bounded Context）
③ openspec specs            （/root/lnkcre/openspec/specs/，273 个能力规格目录）
（背景板：④ CRE BCM 14 域 250 行 Crosswalk——已存在的第五方对账先例）
```

---

## 1. Today's Question：已经有 business-ontology.yaml 了，为什么还需要 Enterprise Semantic Model？

**一句话答案：business-ontology.yaml 是词汇层（vocabulary），不是语义层（semantics）。它管"这个词叫什么"，不管"这个对象是谁的、状态怎么迁移、规则谁执行"。Semantic Model 不是第四份文档，是把四份现有资产的跨源引用接线、做成机器可校验的对账层。**

### 1.1 三源画像（今日实测数字）

| 维度 | business-ontology.yaml | CRE BCM | MI Domain Model | openspec specs |
|---|---|---|---|---|
| 切分逻辑 | **实施模块**（需求访谈视角） | **业务能力**（跨产品权威） | **限界上下文**（代码所有权） | **能力规格**（实现单元） |
| 数量 | 12 模块 / 102 子功能 | 14 域（13 域 active，07 会员 deferred） | 17 Context（9 P0 + 8 P1） | 273 spec 目录 |
| 独有资产 | **883 术语 + 别名 + 15 带溯源场景**（明源/华侨城/锦和/悦商） | **CRE-\* 行 ID 不可变锚点** + 受控词表 + AI 层级 | **Object Ownership + 状态机 + D-001/D-014/D-015 裁决** | 实现真值 + 验收口径 |
| 治理 | ❌ 无文件头（无版本/状态/维护人） | ✅ frontmatter + ORE-1 注册流程 + 冻结 v1.0 | ✅ frontmatter + D-001 冻结 + 边界声明 §2 | ✅ openspec change 流程 |
| 完成度 | **半成品**：场景层只填了资源管理 1 个模块（15 条），其余 11 模块 0 条 | published v0.3/v0.4 | P0 Full Model，P1 Boundary+Object | 持续增长（8/28 = 273） |

### 1.2 它当不了 Semantic Model 的四个硬理由（全部今日可量化）

**① 缺构件。** PT-W4 六构件 = Entity / Identity / Relationship / Lifecycle / Rule / Capability+Policy。ontology 只有「模块→子功能→术语/capability 贴纸」一层树。AI 推理需要的 W1-W6 断链检查（谓词可解析、Guard 挂载点存在、effects ∈ 冻结注册表……）它一条都做不了——它没有谓词、没有状态机、没有授权模型。

**② capability 字段是贴纸不是锚点。** 102 个 capability 标签里：23 个是 `L09/L10/L11` 式编号占位；79 个命名标签只有 **33 个（42%）** 能对上 openspec spec 目录名；反方向 273 个 spec 只有 **12%** 被 ontology 引用到。还有 12 个标签跨模块复用（如 `platform-foundation` 挂了 33 个子功能——它是个"万能贴纸"）。对比 BCM：行 ID 不可变 + Crosswalk 显式 250 条映射——那才叫锚点。

**③ 半成品。** 场景层是 ontology 的灵魂（带明源/华侨城/锦和/悦商四家需求溯源），但 102 个子功能只填了 15 个场景，全部集中在资源管理。它自己的使命还没完成。

**④ 无治理。** 文件第一行直接就是 `modules:`——没有版本、没有 status、没有维护人、没有变更流程。对比：BCM 有 ORE-1（effect 类型注册需域 ADR 证据 + 跨域影响评审）、Domain Model 有 D-001 消费边界声明。**无人治理 + 机器不可校验的语义文件，半年后就是另一份过期文档**（这正是明天 D3 的 Today's Question）。

### 1.3 正确关系：不是替代，是分工 + 接线（分层 Source of Truth）

```
分层 SoT 裁决（今天定稿，进 Semantic Model v0.1 宪章）：

  术语 / 别名 / 场景溯源   →  business-ontology.yaml（唯一权威，但必须补治理头）
  业务能力定义 / 行 ID     →  CRE BCM（不可变锚点，禁止改写）
  对象归属 / 边界 / 生命周期 →  MI Domain Model 17 Context（D-001 消费上游）
  实现事实 / 验收口径      →  openspec specs + 代码
  ─────────────────────────────────────────────
  Semantic Model          =  对账层：不新增权威，单向消费四源
                            （同 Crosswalk 原则），把跨源引用接线，
                            产出机器可校验的一致性快照 + 度量报告
```

这个模式不是新发明——D-001 已经裁决过一次（BCM 权威 + Domain Model 单向消费 + Crosswalk 显式映射，CRE-LEA-007 拆 007a/007b 都只在 MI 侧表达）。Semantic Model 是同一模式的升维：**把"两源对账"升级为"四源对账"，把 Crosswalk 的 250 行经验泛化成装配规则 W1-W6。**

### 1.4 ERP 人话（26 年对照）

这四样东西在传统 ERP 里分别叫：**业务术语表**（需求访谈纪要整理）、**集团业务功能架构图**、**系统设计说明书**、**模块开发说明书**。每家公司都有这四份 Word，从来对不上账，靠"老法师脑子"对账——老法师离职那天，对账能力就没了。

Semantic Model 做的事只有一件：**把老法师的对账能力外化成机器可执行的校验**。W15 的第一个消费方（LnkChatBI 术语库）会立刻检验这一点：883 术语喂进去能让 LLM 听懂"A101""多经点位"，但"A101 现在能不能出租"需要 Availability Rule（D-001 Amendment A：组合判断，不是字段）——**词汇认识对象，语义才认识事实**。

---

## 2. 完成事实：今日对账主表（v0.1 手工版）

### 2.1 模块 ↔ BCM 域 ↔ Context 映射（名字级）

| ontology 模块 | BCM 域 | MI Context | 对账发现 |
|---|---|---|---|
| 资源管理 | 03 空间管理（CRE-LEA） | **01 Asset Foundation + 05 Lease/Occupancy** | 1→2：物理状态 vs 商业可用性拆分（D-001 Amendment A） |
| 招商管理 | 01 招商管理（CRE-SAL） | 03 Leasing Pipeline | 名称三方一致 ✅ |
| 合同管理 | 02 协议管理（CRE-CON） | 04 Contract Lifecycle | **命名漂移**：合同→协议（Agreement Core 重构）→Contract |
| 财务管理 | 04 计费与财务（CRE-FIN） | **06/07/08/09 四个财务 Context** | 1→4：财务链被拆成 Billing/Collection/Invoice/Accounting |
| 运营管理 | 05 运营 + **08 客服（工单/投诉部分）** | 10 Operations + 13 Work Order | **模块吞域**：ontology 运营管理含工单/投诉单子功能 |
| 物业管理 | 10 物业管理（CRE-PRM） | 11 Property Management | 一致 ✅ |
| 推广营销 | 12 营销管理（CRE-MKT） | 14 Marketing & Campaign | 措辞漂移（推广营销 vs 营销） |
| 系统管理 | 14 企业管理（部分） | 无直接 Context（横切平台层） | 用户/权限/流程是平台能力，非业务域 |
| 资产管理（系统对接） | —（无对应域） | 外部集成 | BCM 不覆盖外部系统对接 |
| 移动端 | —（无对应域） | —（端不是域） | 渠道，非能力域 |
| 数据决策 | 13 数据分析（CRE-DAT） | 17 BI & Analytics | 措辞漂移 |
| 预算管理 | 04 财务（部分行） | spec `asset-budget-planning` | 跨域挂靠 |

**反向缺口**：BCM 07 会员（deferred）、08 客服主体、09 工程（CRE-ENG→Context 12）、11 停车（CRE-PKG→Context 16，ontology 只在资源管理下放了 `parking-space` 一个子功能）、Context 15 Customer/Member——在 ontology 模块层**没有对等入口**。

### 2.2 三个结构性结论

1. **三套切分逻辑都对，但视角不同**：ontology 按实施模块切（访谈产物）、BCM 按业务能力切（跨产品、业态无关——Party Core/Agreement Core 重构就是证据）、Domain Model 按代码所有权切。**多对多是常态**（资源管理 1→2、财务管理 1→4、运营管理 2→2），没有显式映射表就没有对账。
2. **命名漂移是系统性的**：同一对象三个名字（合同/协议/Contract），这正是 883 术语别名存在的理由，也正是"行 ID 锚点不变 + 词汇层管别名"设计的必要性——改名不丢锚点。
3. **Crosswalk 先例可复制**：BCM→Context 250 条已完成，今天补的 ontology→BCM/Context 是同一张网的最后一块缺板——D3/D5 把它程序化。

---

## 3. 遗留 / 风险

- **D1 缺产**：8/31 的「lnkcre 现状对齐」未产出（cron 缺席），已把 273 specs / R-wave / lease→cash（MI-AC-001+）事实并入今日；D1 的 PT-W4 产出接入动作挪到 D3 实验输入。
- ontology **无治理头**是 P0 级缺口：Semantic Model 宪章第一条应该是"为每个被消费的源要求 frontmatter + 变更流程"，否则对账基线会漂。
- 场景层 15/102 的填充率意味着：**需求溯源维度暂时不可消费**，W15 术语库只能吃术语层，不能吃场景层。

## 4. 明日连接（D3 · 实验 1）

**business-ontology.yaml 解析与校验**——今天证明了"它当不了 SoT 但必须被 SoT 消费"，明天给它做体检：YAML schema 结构校验、别名冲突检查、场景 source 分布、程序化输出模块×Context 映射表（替代今天的手工 v0.1）。Today's Question：**语义资产如果机器不可校验，半年后会变成什么？**（今天的"无治理头"发现就是明天的开场证据。）

---

### 附：今日证据清单

| 证据 | 来源 |
|---|---|
| 12 模块 / 102 子功能 / 883 术语 / 15 场景（全在资源管理）/ 102 capability 标签（23 L 占位）/ 33-42% 匹配率 / 12 跨模块复用标签 | `business-ontology.yaml` 实测（PyYAML 解析） |
| 17 Context / P0 对象归属总表 / D-001+A+B / 消费边界声明 | `MI-CRE-ERP-Domain-Model-v1.0.md` §2/§3/§0 |
| 250 条 Crosswalk / CRE-LEA-007a+b 拆分先例 | `MI-CRE-Capability-Context-Crosswalk-v1.0.md` |
| 14 域 / 07 deferred / 行 ID 前缀冻结 / ORE-1 | `00-Master-Matrix.md` + `effect-registry.yaml`（5 类冻结 2026-07-26） |
| 273 specs / 未覆盖前缀 TOP（analytics 16、park 9、workflow 8…） | `/root/lnkcre/openspec/specs/` 目录实测 |
| 六构件 + W1-W6 装配规则 | PT-W4-D6《组装SemanticModel与验证设计》 |
