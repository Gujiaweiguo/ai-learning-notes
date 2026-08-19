# PT-W4-D4 · 升级 Capability + Policy：从能力行散文到可授权的执行三角

> 日期：2026-08-20（PT-W4 Day 4）｜毕业作品《MI CRE Enterprise Semantic Model v0.1》第四层
>
> 真实材料：CRE BCM `README.md` §5.4 双轴规则 + §7 AI 层级、`02-合同管理.md` CRE-CON-018/021/024/025 审批规则、MI `docs/capability-traceability-matrix.md`（能力追溯矩阵）、LangChat ADR-003 验证证据里的 Skill descriptor 字段（`effect_policy` / `required_scopes` / `human_review_gate` / `capability_dependencies`）

---

## 一、毕业作品进度

```
D1 ✅ Ontology Model（Entity + Identity + Relationship）
D2 ✅ Lifecycle + Event Model（状态机 + 迁移声明）
D3 ✅ Rule Model（四物种 Rule Card）
D4 📍 Capability + Policy Model + Skill Mapping（今天）
D5    Agent Mapping（数字员工定义）
D6-D7 组装 + Digital Employee Validation
```

昨天 D3 结尾埋了分界线预告：**Rule 说"业务上什么合法"，Policy 说"谁有权决定、走什么路径"**。今天兑现它——并补上最后一块拼图：这些能力**能不能交给 AI 执行**。这是验证场景 L4（Policy 判断）和 L5（动作建议）的直接依赖：没有 Policy Model，Agent 建议"创建 Inspection Task"时说不清"这个动作谁批准"；没有 Skill Mapping，说不清"这个动作我能不能自己做"。

---

## 二、现状盘点：三套 Capability 体系各自为政

这是你资产里最隐蔽的缺口——**不是缺能力定义，而是同一件事有三份权威，互不引用**：

| 体系 | 回答什么 | 权威内容 | 格式 |
|---|---|---|---|
| **CRE BCM 能力行** | 业务**需要**什么能力 | CRE-CON-018"合同生成与签订"，含审批规则 + AI Skill 候选列 | 长散文行（有 ID、有证据链接） |
| **MI capability-traceability-matrix** | 产品**实现了**什么能力 | legacy 代码 → canonical OpenSpec → implementation anchor → verification anchor → status | 结构化表格（五列追溯链，accepted/spec-defined/excluded） |
| **LangChat SkillRelease** | Agent **可以执行**什么 | skill descriptor：`effect_policy`、`required_scopes`、`human_review_gate`、`capability_dependencies` | 机器可读 schema |

**关键观察**：MI 的追溯矩阵已经做到了 `accepted`（实现锚点 + 验证锚点 + 状态闭环），LangChat 已经把执行策略做成了 schema 字段，BCM 已经标了 Skill 候选——**但三份之间没有映射链**。"合同终止"（CRE-CON-024）在 MI 里对应 `backend/internal/lease/`，在 LangChat 里有没有对应 Skill？没有人能一口回答。**AI Agent 更不能**——它无法从 BCM 的"已核验"推出 MI 的"accepted"，也无法从"AI 变更影响测算（候选）"推出"哪个 Skill 依赖哪些 Capability"。

另一个被埋在备注里的金矿：**MI 矩阵的状态词表本身就是能力成熟度模型**——`excluded / spec-defined / implemented / accepted`。这就是 Capability Map 需要的 maturity 轴，你已经发明过了。

---

## 三、核心概念一：Capability Card——能力是"动词 + 对象 + 边界"

BCM 每行其实已经隐含三要素，只是散文没拆开。升级为结构化：

```
Capability ID:  CRE-C-024a
Verb + Object:  终止合同
Owned by:       02 合同管理
Boundary:       终止操作与触发清算归 02；解约生效期后应收抹除归 04；铺位变空置归 03
Consumes:       合同状态、应收余额（04）、铺位状态（03）
Produces:       ContractTerminated 事件 → occupancy-effect（ADR-006）→ 铺位释放
Maturity:       BCM=已核验 ↔ MI=accepted（lease-contract-management spec）
Skill 候选:     AI 变更影响测算（候选）
Evidence:       CRE-CON-024 + traceability-matrix "Lease contract lifecycle" 行
```

对照原文那句"合同终止是独立操作，终止后触发清算"——人能读懂，AI 读不出**动词作用在哪个对象、跨界时哪半归谁、产出什么事件**。注意 `Produces` 直接引用 D2 的 Event/Effect——**Capability 是 Rule 与 Event 的"动作接线板"**：它被 Rule 守卫（D3 的 Guard 挂在操作入口），触发 Event（D2 的迁移 + effect），这就是四层互相咬合的方式。

---

## 四、核心概念二：Policy 三层——同一词，三个决策面

D3 的分界线展开成完整分类。你的材料里"Policy"其实住着三个物种，**混淆它们是 AI 授权事故的头号来源**：

| 层 | 回答什么 | 真实材料实例 | 违反后果 |
|---|---|---|---|
| **① 审批路径 Policy**（业务决策面） | 这个操作**谁有权批准**、走哪条流 | CRE-CON-024："合同终止**无需审批**、终止**申请**需审批"；CRE-CON-021："变更类型决定审批路径"；CRE-CON-025："费用减免单（K2 审批）" | 流程不合规，单据无效 |
| **② AI 执行 Policy**（Agent 运行面） | 这个 Skill 对世界**只读还是可写**、需要什么 scope | LangChat descriptor：`effect_policy: read_only / conditional_write`、`required_scopes`、`human_review_gate` | Agent 被拒（`scope_denied`）或强制人审 |
| **③ 委托边界 Policy**（组织授权面） | 这个能力**允不允许委托给数字员工**、什么条件下 | README §7："数字员工是未来组合层，由 AI Skill 编排而成"；MI 矩阵"Membership = excluded" | 越权代执行 |

三个辨析：

**1. 审批 Policy 与 Rule 的分界（昨天的预告）。** "费用未清算不许退场"（CRE-R-003，Guard）判断**世界状态是否满足**——不满足则操作非法，谁批准都没用。"终止申请需审批"判断**社会授权是否完成**——状态全满足，但没有那个签字就是不能过。**Rule 的主语是世界，Policy 的主语是人/角色**。

**2. ②不是①的翻译，是①的延续。** LangChat 的 `conditional_write` 不是重新发明审批——它是把①的裁决结果**物化成 Agent 可执行的约束**。LangChat ADR-003 证据里那个细节就是证明：`conditional_write` 必须 `requires_review`（descriptor 校验器强制）。**写权限默认带人审门**——这就是①"需审批"在 Agent 运行时的化身。

**3. ③是②的前置闸门。** 一个能力可以技术上可执行（②通过）、业务上合法（Rule 通过），但组织上**不允许委托**（③拒绝）——MI 矩阵把 Membership 整域标 `excluded` 就是③的裁决：不是做不了，是不做。明天 D5 定义数字员工时，每个员工的"能力清单"必须先过③。

**Policy Card 格式**（把 CRE-CON-024 那句拆开）：

```
Policy ID:     CRE-P-024
Subject:       终止操作执行者（角色：招商/财务/营运）
Action:        Contract.Terminate
Decision:      申请阶段 → K2 审批流（CRE-P-024a）
               审批通过后执行终止 → 免审批（CRE-P-024b）
AI Execution:  effect_policy=conditional_write, human_review_gate=true
Delegation:    允许数字员工发起申请；终止执行须人审后放行
Evidence:      CRE-CON-024 + 海鼎合同手册 §终止申请 L552-568
```

注意一个精确处：**同一操作的两个阶段是两条 Policy**——"申请需审批"与"执行免审批"是一对，不是一句。BCM 散文里它们挤在一行，拆开后 Agent 才知道自己在哪个阶段、要不要等人。

---

## 五、核心概念三：Skill Mapping——三角对齐

现在把三套体系焊接成一条链，** BCM 的双轴规则是治理前提**（README §5.4：业务岗位轴 7 岗位 ≠ 岗位 Skill 覆盖轴 6 Skill，两轴不得合并）。在此之上建三角：

```
        BCM Capability Card（业务权威）
         /                    \
   capability_dependencies      evidence + anchors
        /                        \
LangChat SkillRelease  ←——————  MI Traceability（实现权威）
（AI 执行权威）                    legacy→spec→impl→verify→status
```

示范三行（A101 场景所需的最小集）：

| BCM Capability | MI 追溯锚点 | LangChat Skill 映射 | 执行 Policy |
|---|---|---|---|
| CRE-C-024a 终止合同 | lease-contract-management spec → `backend/internal/lease/`（accepted） | `contract.termination.impact`（候选）：`capability_dependencies=[CRE-C-024a, 029]` | read_only（影响测算） |
| 05 运营·创建巡检任务 | workflow-approvals spec → `backend/internal/workflow/`（accepted） | `ops.inspection.create`：`capability_dependencies=[CRE-OPS-*]` | conditional_write + human_review_gate |
| 04 财务·费用减免 | billing-and-invoicing spec → `backend/internal/billing/`（accepted） | `fin.relief.draft`：仅起草减免单 | conditional_write（仅草稿态） |

**关键机制**：LangChat descriptor 里的 `capability_dependencies` 字段就是为这条链预留的挂钩——每个 Skill 声明它依赖哪些业务能力，能力卡声明它的 Skill 候选与成熟度，MI 锚点声明实现事实。**三角任何一角变动，另两角可追溯**——这正是你用 effect-registry 治理 Effect、用 D3 Rule Card 治理 Rule 的同一品味，应用到"能力—执行"轴。

BCM 的状态后缀（候选 / 候选·产品已列）在三角里获得确切含义：**Skill 候选 ≠ Skill 事实**。"AI 变更影响测算（候选）"意味着三角的 LangChat 角还没立起来——README 那条红线的语义基础就在这里。

---

## 六、Agent 视角：L4 + L5 预演

> 验证问题："A101 铺位为什么不能出租？"——昨天 L3 回答了"为什么"，今天回答**"接下来怎么办、谁说了算"**。

Agent 的决策链（D7 完整版会跑通，今天先看走线）：

```
L3 结论：CRE-R-003 Guard 未满足（Inspection 未完成）
   ↓ 该怎么办？查 Capability Card：05 运营·创建巡检任务（Produces: InspectionTask）
L4 查 Policy ①：创建巡检任务 → 免审批（常规任务）
   ↓ 数字员工能做吗？查 Policy ②③
L4+ Skill 执行检查：ops.inspection.create = conditional_write
   → human_review_gate=true → 需要人确认后执行
L5 输出：建议创建 Inspection Task（本人可代办发起，执行需您确认）；
   完成后 → D2 Event: ContractTerminated → occupancy-effect → A101 释放
```

**升级前后对比**：升级前，Agent"建议创建巡检任务"是一句 LLM 语感生成的热心话——它不知道这个动作免不免审批、自己有没有权限、做完世界会怎样。升级后，每个建议动作都带三行依据：**合法性（Rule）、授权性（Policy）、后果（Event）**。这就是 L4/L5 与"聊天机器人"的分界线。

---

## 七、架构师视角

- **以前**：能力 = BCM 散文行（业务侧）+ MI 追溯矩阵（实现侧）+ LangChat schema（AI 侧），三权威平行宇宙；审批规则混在能力行备注里；"要不要让 AI 做"没有任何显式裁决处。
- **现在**：能力 = **Capability Card**（动词+对象+边界+Consumes/Produces+成熟度+三角锚点）；授权 = **三层 Policy**（审批路径 / AI 执行 / 委托边界），Skill descriptor 的 `effect_policy + required_scopes + human_review_gate` 不再是孤立 schema 字段，而是审批 Policy 在运行时的物化。**治理规则的落点**：Skill 上线前必须过三问——业务上候选转正了吗（BCM）？实现上 accepted 吗（MI）？执行上 read_only 还是 conditional_write（LangChat）？三问全绿才进数字员工的能力清单。

---

## 八、练习（5 分钟）

1. CRE-CON-021 说"变更类型决定可编辑字段范围、审批路径、是否产生收费差异"。这句话里其实混了 D3 和 D4 两个层的东西——哪半是 Rule（世界状态判断）、哪半是 Policy（授权路径）？"9 类变更类型"本身又该住在哪一层？（提示：想想"变更类型"是不是一个 Derivation 的输入。）
2. LangChat 校验器强制 `conditional_write → requires_review`。假设产品要给"财务数字员工"开一个**免人审**的减免单起草 Skill，按今天的三层 Policy，你会怎么设计才不破坏这条红线？（提示：②的 gate 挡的是"对世界的写"，起草草稿真的"写了世界"吗？草稿态和生效态在 D2 状态机上是不是两个状态？）

---

*配套实验：`PT-W4-D4-升级Capability与Policy.ipynb` —— 用 Python dataclass 实现 Capability Card + 三层 Policy Card + Skill descriptor，跑通 A101 场景的 L4 授权判断 + L5 动作建议全链（含 scope 检查与 human_review_gate 语义）。*
