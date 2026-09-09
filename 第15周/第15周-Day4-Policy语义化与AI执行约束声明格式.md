# W15-D4 · Policy 语义化：审批流 → Policy Model 抽取规则 × AI 执行约束声明格式

> 开发期 · Week 15「LnkChatBI 精读 × Semantic Model 第一个消费方」Day 4（2026-09-10 周四）
> Today's Question：**AI 需要知道"谁审批"，还是需要知道"为什么找他审批"？**
> 昨日 D3 铺垫：description 注入口已验证能把「口径警示」送进 prompt——今天检验它的上限：Policy 声明是否也能设计成同一条通道送得进去的东西。

---

## 0. 今日开发目标

① 盘点 lnkcre 审批策略的**四个载体**（workflow 引擎 / conditionapproval 策略接缝 / approvalmatrix 权限矩阵 / 节点级治理动作），落到 file:line 级代码事实；② 从代码事实抽取 **Policy Model 六条规则**（P1-P6）；③ 对照 **BCM ADR-004 Binding Model** 校准位置（含一条可反哺 O-4 的工程证据）；④ 定义 **AI 执行约束声明格式 v0.1-draft**（今天的主交付物，落盘 `semantic-model/policy/`，机器可校验）；⑤ 用 ipynb 量化回答 Today's Question（"谁"与"为什么"的信息论差距 + 三处断链）。

---

## 1. 完成事实①：审批策略四载体盘点（代码事实）

| 载体 | 代码锚（8/28 快照） | 策略语义 | "谁审批"从哪来 | "为什么找他"从哪来 |
|---|---|---|---|---|
| ① 工作流定义与引擎 | `workflow/model.go`：Definition（draft→validated→published→superseded→deactivated 生命周期）/ Node（NodeKind: single/countersign/gateway）/ Transition（ConditionJSON）/ AssignmentRule（**5 种分配策略**：fixed_user/fixed_role/department_leader/submitter_context/document_field） | 节点拓扑 + 分配策略 + 网关条件 | `ResolveAssigneesForNodes`（assignee_resolver.go）按节点第一条策略解析 | 定义版本 + 策略 ConfigJSON |
| ② 条件报批策略接缝 | `conditionapproval/service.go:233` SubmitForApproval；`workflowpolicy/policy.go`（branch_key `project_role`/`organization_role` → role_id） | 项目级角色键映射；**未映射 key 在 workflow.Start 之前失败**（不产生孤儿实例） | 映射表 role_id → 但见断链② | branch_key + 映射行 |
| ③ 审批权限矩阵 | `approvalmatrix/model.go` Rule（(role_id, document_type, approval_level) 唯一）；`service.go` resolveChain：**project→city→hq 有序遍历**，三道闸（金额带+面积/租期带、auto_route_rule 谓词、threshold_max），逐级跳过记入 `EscalatedFrom`，`amount<threshold_min` 记 `AutoPassEligible`，全不覆盖时终端兜底 hq | 金额/面积/租期带 + 受限谓词 + 三级升级 | rule.role_id | rule_id + 跳过迹（EscalatedFrom）——**"为什么"的机器雏形已存在** |
| ④ 节点级治理动作 | `timeout_service.go`（TimeoutAction 四值：reject/escalate_to_manager/auto_approve/none，幂等 timeoutKey）；`service.go` 会签（CountersignPolicy、and_gateway）、委托/转办/加签（MaxAdditionalSigners 上限） | 超时处置、会签完成度、中途调整 | 节点角色 | 节点 timeout 配置（publish 后 immutable） |

**规格对齐**：四个载体各有 openspec（workflow-approvals / condition-approval / condition-approval-workflow-policy / approval-authority-matrix），且 workflow-approvals spec 明确三条硬约束：实例创建即绑定义版本（后续发布不影响在途）、动作幂等（重放不产生重复副作用）、通知失败不回滚流程——这三条都是 Policy 声明格式要继承的语义。

## 2. 完成事实②：三处断链 + 一处漂移（"为什么"链的真实缺口）

盘点的最大收获不是四载体长什么样，而是**"谁审批"的表都在、"为什么找他"的字段都在、但链路没接完**：

1. **断链①（升级意图丢失）**：`workflow.StartInput.MinApprovalLevel`（model.go:323）被两处认真赋值——`lease/workflow_service.go:121`（MER-015/016 受控商户→city，SAL-021）和 `conditionapproval/service.go:276`（红旗报价 JudgmentFlags→city）——但 **workflow 包内零消费**（grep 全包仅剩声明行）。approvalmatrix 侧 `ResolveInput.MinLevel` 的跳级逻辑写了也测了（resolveChain minRank skip），生产调用方却无人传（handler 不解析 min_level）。策略决策做了，执行端没接。
2. **断链②（门禁不回填）**：`workflowpolicy.ResolveRole` 返回具体 role_id，`SubmitForApproval` 却 `if _, err :=` **丢弃返回值**——只验映射存在性，不回写节点分配。实际审批人来自 seed 定义节点，映射表改了 role，审批人不跟着变（见漂移④，是 role_id=1）。策略与执行两张皮。
3. **断链③（声明无执行）**：`authorization_policy` 字段（condition_approval_workflow_policy 表 + handler workflow_policy.go:39）存了字符串，spec 写"runtime SHALL enforce"，代码 grep 无任何执法点。
4. **漂移④（seed vs spec）**：condition-approval-workflow-policy spec（8/7 归档）要求"seed 不内嵌具体角色 ID、串行=提交→项目角色→组织角色→完成"；seed.go（8/8，晚一天）四个节点全部 `RoleID:1` + `fixed_role {"role_id":1}`，还多出一个 finance_review 节点且无完成迁移。**spec 与代码当天就分叉**——W14-D4 发现的"registry 与代码无机器锚点"在 policy 域再次复现。

这四处全部登记进了约束声明文件的 `known_gaps` / `evidence.known_gaps`（诚实声明优于装作没有）。

## 3. 完成事实③：Policy Model 抽取规则六条（P1-P6）

| # | 规则 | 代码证据 | 对 AI 约束格式的意义 |
|---|---|---|---|
| P1 | **策略是数据不是代码**：规则本体存在表里（authority 行、workflow_policy upsert、amendment 矩阵），if-else 越来越不在代码里 | approval_authority_rules CRUD；amendmentmatrix Get/Update | 约束声明引用 carrier+business_key，不引用 Go 函数 |
| P2 | **升级链是带迹的有序遍历**，不是点查询 | resolveChain 逐级 append EscalatedFrom | rationale_fields 把 escalated_from 列为一等公民 |
| P3 | **声明式受限谓词**：8 个比较符（>,>=,<,<=,==,!=,in,not_in）+ and/or 二元组合，字段解析失败返回 False（保守跳过）而不是报错 | condition_evaluator.go；approvalmatrix evalPredicate | R1：AI 约束的适用条件只能用这个谓词集，禁任意 DSL |
| P4 | **fail-closed**：未映射 key 在实例创建前失败；条件字段缺失→False 跳级（保守路由） | SubmitForApproval 门禁；EvaluateCondition 注释 | R2：AI 的 fail_mode 默认 closed，open 只能显式人定 |
| P5 | **版本绑定**：实例创建即绑 published 定义版本；超时配置 publish 后 immutable | workflow-approvals spec 三条硬约束；timeout spec | R3：解释必须锚提交时版本（策略表无版本=GAP-P1） |
| P6 | **路由与商务计算分离**：workflow 只路由审批，不算租金/折扣/政策金额 | condition-approval-workflow-policy spec 末条 Requirement | R4：AI 解释路由、不执行路由，auto_approve 只能是人定配置 |

## 4. 完成事实④：对照 BCM ADR-004 Binding Model 的三点校准 + 一条反哺

| 校准点 | ADR-004 说什么 | mi 代码事实 | 裁决 |
|---|---|---|---|
| 声明式适用性 | 五维封闭词表（scope / project type / business format / threshold / customer tier），显式排除表达式引擎 | mi 实证五维中三维有载体：scope↔project_id+datascope、threshold↔金额带+面积带+租期带+auto_route、customer tier↔role_id 侧；business format/project type 暂无载体 | 方向一致：**权限矩阵就是"声明式适用性"的财务域生产实例**。threshold 维在 mi 深化为三带+谓词，是深化不是越界 |
| O-4（受限 DSL）已 park | 五维足够（4 域确认），出现覆盖不了的场景才评审 | **auto_route_rule / ConditionJSON 就是 8-op+and/or 受限谓词集，生产在用**（approvalmatrix + workflow gateway 双处） | 反哺证据：若 O-4 复审，工程基线已存在——直接采纳 8-op 集为受限 DSL 基线，不必发明新 DSL。登记为 O-4 复审输入 |
| 工作流语义归属 | §12.2 明确"工作流语义（状态机、审批流、BPMN）不在本 ADR 范围；Binding 不是流程节点"；§12.3 运行时路由归下游 | 今天的 Policy Model（审批路由策略）正是 ADR-004 **显式让渡给下游**的领域 | 位置裁决：Policy Model **不是第五类 binding_type**（O-9 已决策 object↔object 不进 Binding），是 Semantic Model 的 Policy 构件，通过 evidence 业务键引用 BCM 的 Capability/Role，端点不引运行时 ID（ADR-004 §5 同构） |

一句话：**Binding 管"能力↔Skill 怎么编"，Policy Model 管"单据↔审批人怎么路由、AI 在哪止步"**——两个正交层，靠声明式词表和证据锚共享同一套治理语法。

## 5. 完成事实⑤：AI 执行约束声明格式 v0.1-draft（主交付物）

落盘 `semantic-model/policy/ai-execution-constraints-v0.1-draft.yaml`（draft-proposal，未经评审禁止消费）。结构五块：

```
meta（SoT 指纹：代码/spec/BCM 三源 + R1-R5 设计规则）
schema（封闭词表：4 类约束 / 5 个 ai_may / 9 个 ai_may_not / 2 种 fail_mode / 8 个谓词符 / 6 维适用性 / 4 个证据必填键）
constraints（四条实例，见下表）
每条 = applies_to（声明式适用条件）+ rules（ai_may/ai_may_not/fail_mode）
       + evidence（carrier/business_key/rationale_fields/version_binding/known_gaps）
       + explanation（trigger_questions + template + rationale_placeholders）
known_gaps（GAP-P1/P2/P3，升 0.1 前须裁决）
```

| 约束实例 | type | 一句话边界 |
|---|---|---|
| ① ca-approval-routing-explain-only | route_only | 条件报批流程 AI 只解释串行路由与失败原因，不得审批/跳支/改路由 |
| ② contract-authority-escalation-explain | route_only | 权限矩阵升级链 AI 可解释（锚 rule_id+跳过迹），禁止压制升级/改权限格 |
| ③ redflag-minlevel-escalation | route_only | 红旗/受控商户"应升级 city"是策略意图——**声明断链①存在，AI 必须说"应然而非已然"** |
| ④ node-timeout-autoapprove-boundary | act_with_approval | auto_approve 唯一合法来源是人定节点配置（唯一显式 fail-open） |

五条设计规则（R1-R5）：R1 声明式受限谓词（P3）；R2 fail-closed 默认（P4）；R3 证据锚用业务键+版本绑定（P5 + ADR-004 §5）；R4 AI 解释路由不执行路由（P6）；R5 双消费方——同一份声明既能被机器校验（ipynb §5 全过）又能走 D3 验证的 description 通道进 prompt（template 的占位符就是 rationale 字段）。

**与 v0.1 Semantic Model 的关系**：不改 v0.1.1 六构件与指纹（SoT 不动）；约束声明的 evidence.carrier 正好落在 v0.1 已登记的三个 policy_carriers（approval_authority_rules / condition_approval_workflow_policy / amendment_type_matrix）+ workflow 定义上——Policy 构件从"载体清单"升级为"带 AI 边界的声明格式"，升格进 v0.2 走评审。

## 6. Today's Question：AI 需要知道"谁审批"，还是"为什么找他审批"？

**答案：为什么。且今天的证据表明这不是偏好，是刚需——因为"谁"是派生事实，"为什么"才是策略本体；而系统自己恰恰在三处丢了"为什么"链（§2）。** ipynb 量化佐证（详见配套实验）：

1. **"谁"塌缩"为什么"**：同一批单据按金额/面积/红旗扫描，同一个终审级别（如 city）下存在 **4 种不同的 why 路径**（金额越带升级 / 面积带跳级 / 谓词跳级 / 红旗强制下限）——只答"谁"的信息量把 4 条政策理由压成 1 个标签，AI 答问时必然丢因。
2. **"谁"随配置漂移，"为什么"锚住证据**：扰动 workflowpolicy 映射（role 5→12），具体审批人变、级别与理由不变；扰动阈值，部分单据"谁"翻转——但"为什么"能精确解释**哪些翻、哪些不翻**（ipynb 输出翻转单据清单及各自命中/越带原因）。可解释性=配置变化的可预言性。
3. **断链的现实教训**：升级意图（MinApprovalLevel）、映射结果（ResolveRole）、授权策略（authorization_policy）三处都是"决策做了、rationale 没送达执行端/解释端"。AI 如果只知道"谁"，断链处它只会复读错误答案；知道"为什么"，它才能说"该到 city 级但系统未执行升级"——**约束③把这条写进了 AI 话术模板**。A101 问答场景同理：问"A101 这单为什么要总部审"，答案在 rule_id 的带与跳过迹里，不在审批人姓名里。

## 7. 遗留 / 风险

- **draft 未评审**：约束声明格式 v0.1-draft 待 Jason 评审 + 走 openspec change 才可升 0.1；当前禁止被任何生成物消费。
- **GAP-P1（策略行无版本）**：authority 规则行 is_active 软停用、无版本快照，rationale 不可复现历史——与 W14-D4 缺口④（amendment 矩阵）同病，v0.2 统一裁决"策略载体版本化"。
- **断链修复归主仓**：三处断链 + seed/spec 漂移是 lnkcre change 候选（与 G-01「语义漂移无机器告警」同宗：策略意图↔执行无对账），不在学习轨道内擅改。
- **prompt 注入未实测**：R5 的 description 通道注入是设计推断，D6 实战日随 term-aliases 一起验（template 占位符替换后送 LnkChatBI）。
- 微信通道 9/8 起中断（NOTICE-2026-09-09 已留），不影响落盘链路。

## 8. 明日连接（D5 · 开发节奏定轨）

W16+ backlog 按 Semantic Model 依赖排序（哪些 Rule 要先显式化、哪个 Context 先接入）+ 定与 lnkcre 主仓同步机制（每周 digest + R-wave 跟读）。Today's Question：**学习期的雷达机制，开发期保留什么、砍掉什么？** 今天的输入：Policy 构件的 known_gaps 三条就是 backlog 排序的现成素材（断链修复 > 版本化 > 通道注入）。

---

### 附：今日证据清单

| 证据 | 来源 |
|---|---|
| 四载体代码事实 | workflow/model.go（Node/AssignmentRule/5 策略）、assignee_resolver.go、conditionapproval/service.go:233-278、workflowpolicy/policy.go（Resolver fail-closed）、approvalmatrix/model.go+service.go（resolveChain/EscalatedFrom/MinLevel）、timeout_service.go（四值动作+幂等 key）、service.go（会签/加签上限） |
| 断链① | StartInput.MinApprovalLevel 声明于 workflow/model.go:323；赋值于 lease/workflow_service.go:121、conditionapproval/service.go:276；workflow 包内 grep 无消费 |
| 断链② | SubmitForApproval `if _, err := ResolveRole(...)` 丢弃返回值（conditionapproval/service.go:259-263） |
| 断链③ | authorization_policy 仅见表/handler/workflowpolicy 三处，无执法点 |
| 漂移④ | seed.go（8/8）role_id=1 硬编码 + finance_review 节点 vs spec（8/7 归档）"不内嵌角色 ID/两分支串行" |
| ADR-004 校准 | ADR-004 §4（binding_type 四值）、§9（五维声明式适用性+排除表达式引擎）、§10（O-4 已 park/O-9 已决策 v8）、§12.2（工作流语义不做项）、§5（端点不引运行时 ID） |
| openspec 对齐 | workflow-approvals（版本绑定/幂等/通知不回滚/超时四值）、condition-approval-workflow-policy（无硬编码角色/运行时映射/assignee-preview nil-safe/不加第二引擎）、approval-authority-matrix（三级链/带与谓词/datascope 执法/409 唯一约束）、condition-approval（resolver seam 在 Start 之前） |
| 主交付物 | `semantic-model/policy/ai-execution-constraints-v0.1-draft.yaml`（meta/schema/4 约束实例/known_gaps，机器校验见 ipynb §5） |
| 量化实验 | 配套 ipynb：8 个 spec 场景回放、"谁塌缩为什么"（同级 4 路径）、配置/阈值扰动翻转解释、断链误路由率、约束文件机检全过、双图落盘 |

*配套实验：`第15周-Day4-Policy语义化与AI执行约束验证.ipynb` —— 受限谓词求值器复刻、审批链解析器复刻（回放 openspec 8 场景）、"谁 vs 为什么"量化、断链三处模拟、约束声明机检，全部代码 cell 执行通过 verify_ipynb。*
