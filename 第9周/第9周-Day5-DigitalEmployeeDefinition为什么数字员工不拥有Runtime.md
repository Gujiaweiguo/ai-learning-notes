# 🧱 LangChat 心智模型 | Week9-Day5
## 📌 DigitalEmployeeDefinition：为什么数字员工不拥有 Runtime？

---

━━━ 1. 今日核心问题 ━━━

**为什么 DigitalEmployeeDefinition 不拥有 Runtime？**

换个问法：如果数字员工是"员工"，为什么它不能"自己跑"？

这是 Week 9 最反直觉的问题。在当前代码里，`DigitalEmployeeModel` 有 `bound_skill_id`、有 `kill_switch`、有 `status=active`——看起来它就是在"运行"。但 ADR-006 和 Domain Model §6.1 明确规定：**DigitalEmployeeDefinition 不拥有 Runtime，不持有 Deployment 状态，不构造 FrozenExecutionContext，不充当执行入口**。

为什么？

---

━━━ 2. 人话解释 ━━━

用 Jason 26 年 ERP 经验来讲。

在传统 ERP 里，"员工"是一个主数据对象——张三是采购员，李四是审批人。系统不会因为"张三"存在就自动运行采购流程。流程运行需要：工单（what）、权限（who can do）、环境（which system）。

LangChat 的数字员工也一样。**"数字员工"是身份，不是引擎。**

想象 MI 集团有一个"合同审核数字员工"叫小明。小明是谁？
- 小明的**定义**（DigitalEmployeeDefinition）：名字、职责、关联的契约、谱系记录 → 像 HR 档案
- 小明的**能力**（SkillRelease）：具体执行的技能包 → 像岗位技能认证
- 小明的**部署**（Deployment/Revision）：在某环境实际运行 → 像被派到具体项目
- 小明的**运行时**（Runtime + FrozenExecutionContext）：每次执行 → 像每次具体干活

HR 档案不等于员工本人。你不能拿着档案就开始干活——你需要被分配到项目、获得系统权限、打开电脑才能工作。

**DigitalEmployeeDefinition 就是 HR 档案。它只持有引用（digest/版本指针），不持有内容字节，不持有运行状态。**

---

━━━ 3. LangChat 架构位置 ━━━

在四层架构中，DigitalEmployeeDefinition 是 **Business Domain Layer** 的对象：

```
Business Domain Layer
  └── DigitalEmployeeDefinition（语义锚点）
        ├── 引用 ApplicationContractVersion（业务契约）
        ├── 引用 BlueprintVersion（谱系锚点）
        └── 声明发布策略 scope

Supply Chain Layer
  └── Blueprint → Build → ExecutionPlanIR → SkillRelease（制品链）

Runtime Layer
  └── Deployment → DeploymentRevision → FrozenExecutionContext → Execution
        ├── Session（交互上下文）
        ├── State（状态对象）
        └── Memory（记忆对象）

Operations Layer
  └── Registry / Catalog Projection / Governance
```

DigitalEmployeeDefinition 在最上层（Business Domain），Runtime 在第三层。**跨越两层**——定义层不触碰运行层。

---

━━━ 4. ADR 依据 ━━━

### ADR-006 D-1（§4.1）：DigitalEmployeeDefinition 是引用语义锚点，不是聚合根

关键决策：

**身份**：`(tenant, workspace, digital_employee_id, definition_version)`，definition_version 单调递增。

**引用而非持有**：
- MUST 引用一份 ApplicationContractVersion digest
- MUST 引用一份活跃 BlueprintVersion digest 作为谱系锚点
- MUST 显式声明发布策略 scope
- MUST NOT 持有 Blueprint 内容字节、Knowledge 内容字节、Policy 内容字节、Deployment 状态或 Runtime 对象

**生命周期**：`Draft → Published → Deprecated → Retired`

注意：**没有 Activated 状态**。激活是 Deployment 聚合的职责（`Draft → Active → Suspended → Retired`），不是定义的职责。定义只能说"已发布可被部署"，是否实际承载流量由 Deployment 裁决。

### ADR-006 §7 明确不做（20 条中的前 7 条直接相关）：

1. DigitalEmployeeDefinition **不拥有 Runtime**
2. DigitalEmployeeDefinition **不持有 Deployment 状态**
3. DigitalEmployeeDefinition **不持有任何 artifact 内容**
4. DigitalEmployeeDefinition **不签发授权**
5. DigitalEmployeeDefinition **不构造 FrozenExecutionContext**
6. DigitalEmployeeDefinition **不充当执行入口**
7. DigitalEmployeeDefinition **不聚合子内容为巨型聚合根**

### Domain Model §10.4-12（系统级不变量）

> DigitalEmployeeDefinition 非聚合根：只持有引用，不持有子内容。

### Domain Model §6.1 BD-01 禁止职责

> 不拥有 Runtime；不持有 Deployment 状态；不持有任何 artifact 的内容（只持有 digest 或版本引用）；不签发授权；不构造 FrozenExecutionContext；不充当执行入口；不聚合子内容为一个巨型聚合根。

---

━━━ 5. 代码验证 ━━━

### 当前代码事实：`DigitalEmployeeModel`（digital_employee_model.py）

```python
class DigitalEmployeeModel(Base):
    __tablename__ = "digital_employee"

    id = Column(Integer, primary_key=True)
    name = Column(String(200))              # 业务名
    tenant_id = Column(Integer)              # 租户
    workspace_id = Column(Integer)           # 工作空间
    owner_id = Column(Integer)               # 负责人
    status = Column(String(20))              # active/inactive/retired
    business_context_json = Column(Text)     # 商业上下文
    allowed_capabilities_json = Column(Text) # 能力清单
    bound_skill_id = Column(String(200))     # 绑定的 SkillRelease
    bound_assistant_id = Column(Integer)     # 绑定的 Assistant
    kill_switch = Column(Boolean)            # 紧急停止
```

### 关键结构分析

**当前代码做了什么**：
- 创建了一个"数字员工"表，承载 name、tenant、capabilities、bound_skill
- 有 kill_switch（紧急停止开关）
- 有 status 三态：active / inactive / retired
- 通过 bound_skill_id 关联到 SkillRelease
- 通过 bound_assistant_id 关联到 AssistantResource

**当前代码与目标态的 Gap**：

| 目标态要求 | 当前代码 | Gap |
|---|---|---|
| definition_version 单调递增 | 无版本字段 | ❌ 没有 definition_version |
| 引用 ApplicationContractVersion digest | 无 | ❌ 不存在 |
| 引用 BlueprintVersion digest | 无 | ❌ 不存在 |
| 声明发布策略 scope | 无 | ❌ 不存在 |
| 生命周期 Draft→Published→Deprecated→Retired | active/inactive/retired | ⚠️ 三态 vs 四态，语义混合 |
| 只持有引用不持有内容 | bound_skill_id 是 tag 引用 | ⚠️ 用 skill_id 而非 digest |
| 不拥有 Runtime | kill_switch 直接控制执行 | ⚠️ kill_switch 跨越了定义层和运行层 |
| 不签发授权 | allowed_capabilities_json | ⚠️ 能力清单混合了声明与授权 |

**最关键的 Gap**：当前 `status=active` 同时承载了"定义已发布"和"部署在服役"双重语义。ADR-006 §4.1 明确指出：激活是 Deployment 的职责。目标态要拆分为 `DigitalEmployeeDefinition.Published`（定义层）+ `Deployment.Active`（运行层）两个独立状态。

---

━━━ 6. 商业地产映射 ━━━

### LangChat → MI CRE 场景

| LangChat 概念 | MI CRE 场景 | 说明 |
|---|---|---|
| DigitalEmployeeDefinition | "合同审核数字员工" HR 档案 | 定义身份、职责、归属部门 |
| ApplicationContractVersion | 合同审核岗位 SOP | 输入什么、输出什么、需要什么权限 |
| BlueprintVersion | 审核流程设计文档 | 经评审的规范文件 |
| SkillRelease | 审核技能包（含模型+知识+策略） | 具体可执行的技能制品 |
| Deployment | 派驻到某 mall 的审核岗 | 在某环境实际部署 |
| DeploymentRevision | 某次部署的完整快照 | 锁死了所有依赖版本 |
| FrozenExecutionContext | 每次审核任务的工作令 | 身份、权限、知识版本全部冻结 |
| Execution | 一次具体的合同审核 | 一次运行实例 |
| Session | 一个租户的持续审核上下文 | 跨多次审核的对话 |
| State | 当前审核任务的中间状态 | 草稿、待审、已审 |
| Memory | 该数字员工的历史经验记忆 | 跨任务的长期记忆 |

**MI 场景举例**：

你定义了一个" MI 集团合同审核数字员工"，它：
- **定义层**：名字叫"小合"，属于法务部，绑定合同审核 SOP → DigitalEmployeeDefinition
- **制品层**：包含合同条款识别模型、法规知识库快照、审核策略束 → SkillRelease
- **部署层**：部署到上海 mall 和北京 mall 两个环境 → 两个 Deployment
- **运行层**：每次审核一份合同时，冻结当前知识版本和策略 → FrozenExecutionContext + Execution

"小合"的定义（HR 档案）不因为你暂停了北京 mall 的部署而改变。北京停了，上海还在跑。**定义和运行是分离的**。

---

━━━ 7. 与传统方案比较 ━━━

### 方案对比：数字员工应该拥有 Runtime 吗？

| 维度 | 方案A：定义拥有 Runtime（传统思路） | 方案B：定义不拥有 Runtime（LangChat v2） |
|---|---|---|
| **多环境部署** | 定义只有一份，Runtime 状态混在定义里。同时部署到上海+北京时状态冲突 | 定义是引用锚点，每个环境有独立 Deployment 和 Revision |
| **灰度发布** | 不可能。定义指向唯一的"当前版本"，无法按比例切流 | Deployment 有多个 Revision，TrafficPolicy 按 cohort 路由 |
| **回滚** | 修改定义状态回到旧版本。历史被篡改 | 前向回滚：物化新 Revision + 新 TrafficPolicy 版本 |
| **审计** | 定义变更和运行变更混在一起，责任不清 | 定义层变更（产品决策）和运行层变更（运维决策）各自独立审计 |
| **知识更新** | 定义直接指向知识库，改知识 = 改定义 | KnowledgeSnapshot 独立版本化，通过 DeploymentRevision 闭包 digest-pin |
| **权限分离** | 定义同时管身份和执行权限 | 定义只声明 scope；授权由控制面下达；运行时在 FrozenExecutionContext 内执行 |

**为什么选方案B？**

因为 AI 应用的执行结果受 prompt、模型版本、知识库快照、策略叠加影响——不像传统软件"代码固定，结果固定"。如果定义拥有 Runtime，任何依赖变更都会导致"定义"本身改变，版本爆炸，审计链断裂。

把定义和运行分离，定义保持稳定（"我是谁"），运行独立演进（"我今天用了什么版本的模型和知识"），才是正确的治理方式。

---

━━━ 8. 架构师思考题 ━━━

**场景**：MI 集团有 10 个 mall，每个 mall 都需要"合同审核数字员工"。这 10 个数字员工：

- 使用相同的合同审核 SOP（ApplicationContract）
- 使用相同的审核流程设计（BlueprintVersion）
- 但每个 mall 的法规知识库不同（上海 vs 北京的法规差异）
- 每个 mall 的策略不同（上海允许自动审批 50 万以下，北京要求全量人审）

**问题**：
1. 这需要几个 DigitalEmployeeDefinition？几个 Deployment？
2. 如果上海 mall 的知识库更新了，会影响北京 mall 的数字员工吗？
3. 如果集团决定统一审核流程（改 Blueprint），10 个 Deployment 如何同步？
4. kill_switch 在这个场景下应该属于谁？定义层还是 Deployment 层？

**提示**：答案藏在"引用 vs 持有"和"定义层 vs 运行层"的分离原则中。

---

━━━ 9. 我的理解变化 ━━━

**以前以为**：数字员工就是一个"智能体"——定义它、启动它、它就开始干活。kill_switch 就是关闭它。

**现在知道**：数字员工是一组架构对象的协作——
- DigitalEmployeeDefinition 是**身份声明**（HR 档案）
- SkillRelease 是**能力制品**（技能认证）
- Deployment/Revision 是**部署实例**（外派到具体项目）
- FrozenExecutionContext 是**每次工作的许可令**（工作令）
- Execution 是**一次具体工作**（干活）

"数字员工"这个词太容易让人以为它是一个"东西"、一个"实体"、一个"运行中的程序"。但它实际上是一个**语义聚合**——一组引用的集合，指向真正干活的对象。

**最反直觉的认知转变**：当前代码的 `kill_switch` 字段直接放在 DigitalEmployeeModel 上，看起来很合理。但从目标态看，kill_switch 应该在 **Deployment 层**——因为"停止运行"是运行时决策，不是定义层决策。定义可以被 Deprecated（退役），但不能被"停止运行"，因为定义本身不运行。

---

━━━ 10. 明日连接 + Semantic Layer ━━━

### 明天（周六）：⚡ 画 Domain Model Diagram

明天是动手日。目标：画出 Week 9 所有对象的关系图——
- 对象生命周期（从 Draft 到 Retired）
- 对象间的引用关系（谁引用谁、谁拥有谁）
- 依赖方向（Supply Chain → Runtime 单向流动）

回答关键问题：**哪个对象最可能被合并？哪个最可能被拆分？**

### Semantic Layer 定位

今天的知识在 Ontology → Domain Model → Capability → Skill 链上的位置：

```
Ontology（什么是数字员工）
  └── Domain Model §6.1 BD-01（DigitalEmployeeDefinition 的八要素规约）
       └── ADR-006 D-1（引用语义锚点的可执行边界）
            └── Code: DigitalEmployeeModel（当前实现，与目标态有 Gap）
                 └── Tomorrow: 画出来，让所有对象关系可视化
```

DigitalEmployeeDefinition 是整条链的**起点**——它定义了"我们要构建什么"。但起点不等于终点。从定义到执行，要经过 Supply Chain（制品化）和 Runtime（实例化）两个完整阶段。每一步都有独立的治理、独立的审计、独立的状态机。

**这正是 LangChat 最独特的设计哲学：把传统"一个对象搞定一切"的模式，拆成"多层对象各司其职"的治理链。**
