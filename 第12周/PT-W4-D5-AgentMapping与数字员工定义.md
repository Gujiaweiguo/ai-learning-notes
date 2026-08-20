# PT-W4-D5 · Agent Mapping：数字员工不是新角色，是语义模型的组合层

> 日期：2026-08-21（PT-W4 Day 5）｜毕业作品《MI CRE Enterprise Semantic Model v0.1》第五层：Agent Mapping
>
> 真实材料：CRE BCM `README.md` §7 AI 层级（AI 能力→AI Skill→数字员工，方向不可颠倒、不可跳层）+ §7.2 状态标注规则 + §5.4 双轴规则（7 业务岗位轴 vs 6 岗位 Skill 轴）、`04-财务管理.md` §AI 层级示例（财务数字员工＝规划）、MI `docs/capability-traceability-matrix.md`（Membership=excluded、`accepted` 词表）、MI Domain Model v1.0 §2（17 个 Bounded Context）

---

## 一、毕业作品进度

```
D1 ✅ Ontology Model（Entity + Identity + Relationship）
D2 ✅ Lifecycle + Event Model（状态机 + 迁移声明）
D3 ✅ Rule Model（四物种 Rule Card）
D4 ✅ Capability + Policy Model + Skill Mapping（执行三角）
D5 📍 Agent Mapping（数字员工定义）—— 今天
D6-D7 组装 Semantic Model v0.1 + Digital Employee Validation
```

昨天 D4 结尾留了一个钩子：Skill 上线要过三问（BCM 候选转正？MI accepted？LangChat 执行策略？），**三问全绿才进数字员工的能力清单**。今天就把这个"清单"本身定义出来。这是 D7 验证场景的最后一块地基：验证问题"A101 铺位为什么不能出租？"不是一个抽象 Agent 在回答，而是**某个有名字、有边界、有授权的数字员工**在回答。

---

## 二、核心转变：数字员工 = 组合层，不新增业务语义

你的 BCM README §7 早就把层级立好了，而且立得很准：

```
AI 能力（Capability，能力类型）→ AI Skill（岗位技能包）→ 数字员工（技能组合层）
```

三条铁律值得逐条读出声：

1. **方向不可颠倒、不可跳层**——不能先设计"财务数字员工"再倒推它需要什么能力；必须从能力类型出发，经 Skill 编排而成。
2. **数字员工是未来的组合层**（§7.1），"不是当前产品事实，除非产品文档正式定义并上线"。
3. **状态标注**（§7.2）：Skill 带（候选）/（候选·产品已列），数字员工带（规划）。**严禁把候选或规划写成已上线/已交付/已实现**。

用本轨道四周的语言翻译：**前四层（Ontology / Lifecycle / Rule / Capability+Policy）是世界的事实与约束；Agent Mapping 不发明任何新事实，只声明"谁来消费这些事实、在什么边界内、带着什么授权"。** 数字员工是 Semantic Model 的**消费面投影**——就像视图之于数据库。这一条是今天最重要的架构判断：如果你发现定义某个数字员工时需要"补一条只有它知道的业务规则"，说明那条规则漏在了前四层，该回 D3 补 Rule Card，而不是塞进员工定义里。

---

## 三、Agent Mapping Card：数字员工的身份公式

```
数字员工身份 = 岗位锚点 × 认知边界 × 技能组合 × 授权配置 × 状态诚实
```

五个字段逐个说清：

| 字段 | 是什么 | 真实材料依据 |
|---|---|---|
| **岗位锚点** | 挂在业务岗位轴（7 岗位）上，不是挂在 Skill 轴（6 Skill）上 | README §5.4 双轴规则：两轴不得合并；总经理/老板、IT/信息是横切角色，不投放专属 Skill |
| **认知边界** | Context 子集 + 每个	Context 的**读写姿态**（read_write / read_only） | Domain Model 17 Context；W3-D3"Bounded Context = Agent 认知边界"的落地 |
| **技能组合** | 一组 Skill，每个 Skill 声明 `capability_dependencies`（D4 三角） | LangChat skill descriptor + BCM A 列候选 Skill |
| **授权配置** | 每个能力过 D4 三层 Policy：审批路径① / AI 执行② / 委托边界③ | D4 Policy Card；MI 矩阵 `excluded` 词表 |
| **状态诚实** | Skill 全部（候选）→ 数字员工只能（规划） | README §7.2 状态标注规则 |

### 认知边界的读写姿态——最容易被忽略的字段

"招商数字员工能看到合同"和"招商数字员工能改合同"是两种完全不同的边界。认知边界不是一个 Context 名单，而是 **Context × 姿态**的矩阵。姿态不是随意标注的——它必须能追溯到业务归属：03 租赁的资源状态归运营管（域边界表：资源状态生命周期归 03），招商对它是**只读消费者**；01 招商漏斗归招商，运营对它只读。**读写姿态 = Domain Model 域边界在组织面上的投影**，这就是"每天绑定真实材料"在今天的形式。

### 委托边界③是硬闸门

MI 矩阵把 Membership / `Associator` 整个标为 `excluded`（"Do not migrate member cards, points…"）。这条记录在 Agent Mapping 层获得一个新语义：**excluded 能力不得进入任何数字员工的技能清单**。不是"技术做不了"，是"第一版明确不做"。任何一个数字员工定义若引用了 excluded 能力，校验就该直接失败——这是比"回答错问题"更早的失败，在定义阶段就拦住。

---

## 四、三张 Agent Mapping Card（真实证据版）

### 招商数字员工（规划）

```
ID:          DE-SAL-01
岗位锚点:     业务岗位轴「招商」（README §5.4）
认知边界:     01 招商管理 RW｜03 租赁管理 RO（资源可用性）｜02 合同管理 RO（意向转合同后）
技能组合:     招商研究 Skill（候选·产品已列，对应 01 域 A 列）
             每项 dependency: CRE-SAL-* 能力行 + MI masterdata spec（accepted）
授权配置:     全部 read_only（研究类）；跨 Context 写操作一律不委托
状态:         规划（Skill 均为候选）
```

### 运营数字员工（规划）——A101 验证场景的 owner

```
ID:          DE-OPS-01
岗位锚点:     业务岗位轴「营运」
认知边界:     05 运营管理 RW｜03 租赁管理 RW（进退场资源状态）｜06 商户管理 RO｜02 合同管理 RO（终止流程可见）
技能组合:     营运分析 Skill（候选·产品已列）
             ops.inspection.create（候选）: capability_dependencies=[CRE-OPS-巡检任务行]
授权配置:     巡检创建 = conditional_write + human_review_gate（LangChat ②层）
             资源状态变更（释放铺位）= 不委托（由 D2 Event 自动迁移，非 Agent 动作）
状态:         规划
```

### 财务数字员工（规划）

```
ID:          DE-FIN-01
岗位锚点:     业务岗位轴「财务」
认知边界:     04 财务管理 RW｜02 合同管理 RO（条款）｜03 租赁管理 RO（资源）｜05 运营 RO（营运数据）
技能组合:     AI 欠费分析（候选·产品已列）+ AI 账单助手（候选）+ AI 租费审核（候选）
             —— 04-财务管理.md §AI 层级示例的原文结构
授权配置:     减免单起草 = conditional_write（仅草稿态，D4 练习2 的答案）
             核销/收款执行 = 不委托（K 级审批①层 + 资金安全）
状态:         规划
```

注意财务这张卡几乎就是把 `04-财务管理.md` 的 AI 层级示例**翻译成结构化字段**——这正说明组合不是新设计，是把 BCM 已经推导出的组合关系落到 Agent Mapping 层。

---

## 五、跨员工协作：owner / subscriber，不是新语义

A101 问题横跨 03（资源状态）、02（终止流程）、05（巡检）三个域。三个数字员工谁回答？

**路由规则：问题的主实体 + 主状态决定 owner。** "A101 为什么不能出租"的主实体是 Space（03 域资产），主状态是"可租性"（03 域边界：进退场资源状态归 03）→ **运营 DE 是 owner**（对 03 有 RW），招商 DE 是 subscriber（对 03 只读，可订阅结论用于招商漏斗）。这条路由规则没有发明任何东西——它就是 D1 的 Relationship（Space 归属 03）+ Domain Model 域边界表的直接应用。**员工间协作协议 = 语义模型在组织面的投影**，这是今天第二重要的判断。

---

## 六、Agent 视角：A101 问题在数字员工身上的完整走线

```
问题："A101 铺位为什么不能出租？"
  ↓ 路由：主实体 Space → 03 → 运营 DE（RW）为 owner
L1 查 Entity（D1）    ：Space A101，身份 Building→Floor→Unit（D1 Identity）
L2 查 Lifecycle（D2） ：关联 Lease 处于 TerminatedPendingInspection
L3 查 Rule（D3）      ：CRE-R-003 Guard —— Inspection 未完成 → 不可租
L4 查 Policy（D4）    ：终止申请已过 K2 审批（①层合规）；创建巡检免审批
L5 查 Capability（D4）：ops.inspection.create = conditional_write
                       → 运营 DE 可发起，human_review_gate=true 需人确认
输出：原因 + 依据 + 当前状态 + 建议动作（人审后执行）
```

对照升级前：一个没有 Agent Mapping 的 LLM 也能"听起来像"回答这个问题，但它说不清**自己是谁、凭什么看这些数据、哪个动作自己有权发起**。五层模型 + 一张 Agent Card，把"热心的回答"变成"可审计的回答"。这就是 D7 验证要证明的东西。

---

## 七、连接思考（与主线 W12 Vision Intelligence）

主线本周在评估"哪些新场景值得做"（BusinessSceneMatrix / ROI）；并行轨道今天给出了评估器的另一半：**一个场景值不值得做，取决于它能不能落进某个数字员工的认知边界**——场景所需的 Context × Capability × Policy 越是被现有 Agent Card 覆盖，边际成本越低；需要新边界/新授权的场景，ROI 评估时必须把"语义模型增量"算进成本。主线算收益，并行轨道算语义成本，两张表对着看才是完整的 Vision Intelligence。

---

## 八、架构师视角

- **以前**：数字员工是 PPT 里的角色画像（"财务小助手：智能、贴心、7×24"）——没有边界、没有授权、没有状态诚实，也无法验证。
- **现在**：数字员工 = **Agent Mapping Card**（岗位锚点 × 认知边界[Context×姿态] × 技能组合[capability_dependencies] × 授权配置[三层 Policy] × 状态诚实[候选/规划]）。三条可执行校验：excluded 能力不得进清单（③硬闸门）；skill 依赖的 capability 必须落在认知边界内；Skill 全候选 → 员工只能是规划。**定义即约束，约束即可验证**——这是语义模型到组织部署之间的最后一跳，也是 D7 验证报告的骨架。

---

## 九、练习（5 分钟）

1. 按 §5.4 双轴规则，"客服分流 Skill"在 Skill 轴上有投放目标，但业务岗位轴 7 个岗位里没有"客服"。如果未来要定义一个"客服数字员工"，它的**岗位锚点**该挂哪里？挂错会违反哪条规则？（提示：横切角色不得投放专属 Skill；岗位轴修订权在 BCM 维护流程，不在 Agent Mapping 层。）
2. 运营 DE 对 03 是 RW，其中包含"释放铺位"。但 §四的卡里写"资源状态变更 = 不委托，由 D2 Event 自动迁移"。为什么同一个 Context 里的写操作要拆成两类？（提示：Agent 的写和世界的迁移是两回事——`ContractTerminated → occupancy-effect → 释放`这条链上，谁是主语？）

---

*配套实验：`PT-W4-D5-AgentMapping与数字员工定义.ipynb` —— 用 dataclass 实现 Agent Mapping Card + 委托边界校验器（含 Membership excluded 反例拦截）+ A101 问题路由（owner/subscriber 判定）+ 运营 DE 的 L1→L5 全链模拟 + 三员工认知边界热力图。*
