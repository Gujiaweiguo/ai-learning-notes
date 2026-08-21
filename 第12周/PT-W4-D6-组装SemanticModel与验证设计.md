# PT-W4-D6 · 组装 Semantic Model v0.1：从六层堆叠到层间接线，再到可判分的验证设计

> 日期：2026-08-22（PT-W4 Day 6）｜毕业作品《MI CRE Enterprise Semantic Model v0.1》第六步：组装 + 验证设计
>
> 真实材料：MI Domain Model v1.0（§2 17 Context / §3 Object Ownership / §6 状态机）+ effect-registry.yaml（5 类冻结）+ ADR-006（四类关系）+ CRE BCM README（§5.4 双轴 / §7 AI 层级）+ MI `docs/capability-traceability-matrix.md`（accepted/excluded 词表）+ LangChat ADR-003（skill descriptor 字段）

---

## 一、毕业作品进度

```
D1 ✅ Ontology Model（Entity + Identity + Relationship，语义动词命名）
D2 ✅ Lifecycle + Event Model（状态机 + 迁移声明 + Guard 挂载）
D3 ✅ Rule Model（四物种 Rule Card：Invariant / Guard / Derivation / Variant）
D4 ✅ Capability + Policy + Skill Mapping（执行三角：能力/授权/技能）
D5 ✅ Agent Mapping（数字员工 = 组合层，五字段 Agent Card）
D6 📍 组装 + 验证设计 —— 今天
D7    Digital Employee Validation（跑验证、出报告）
```

五天里你每层都做对了。今天要回答一个更尖锐的问题：**六层各自都对，拼在一起就对吗？** 组装不是把六份文档订成一册——是**接线**：层与层之间的每一根引用线都要真实存在、不悬空。接完线才有资格谈验证：**一个模型"可验证"的前提，是它的推理链上任何一跳都不会断链。**

---

## 二、组装 ≠ 堆叠：层间接线图

六层模型的层级关系不是"从上到下的清单"，是一张**引用网**：

```
Agent Mapping（D5）── 谁来消费：Context×姿态 ⊆ 17 Context；能力依赖 ⊆ Capability Map
      │
      ▼ 引用
Policy（D4③）────── 谁有权执行：审批路径① / AI 执行② / 委托边界③
      │
      ▼ 授权
Capability（D4）──── 动词+对象+边界；delegation ≠ excluded；依赖 ──► Rule
      │                                              │
      ▼ 触发                                         ▼ 谓词引用
Rule（D3）── Guard 挂载 ──► Lifecycle（D2）迁移 ──► Ontology（D1）概念
                                │
                                ▼ effects ∈ effect-registry 5 类冻结
```

每一根箭头都是一个**可以悬空的引用**。悬空引用对人是"文档不一致"，对 AI 是**断链**：Agent 推理到"引用 CRE-R-003"，而 CRE-R-003 的谓词写的是 `Space.reservation_status`——D1 的 Space 根本没这个属性——推理当场失败，而且失败得**无声**（LLM 会用语感编一个继续往下走）。

### 六条装配规则（每条都可机器检查）

| # | 装配规则 | 检查什么 | 悬空后果 |
|---|---------|---------|---------|
| W1 | Rule 谓词里的每个名词（`Entity.属性`）必须在 D1 Entity 定义中存在 | 符号解析 | Agent 查不到谓词作用的对象 |
| W2 | Guard 的挂载点必须是 D2 声明过的迁移（from→to 真实存在） | 挂载点存在性 | 守卫守着一扇不存在的门 |
| W3 | 迁移声明的 effects 必须 ∈ effect-registry 冻结的 5 类 | 类型封闭 | Event 流无法被下游消费 |
| W4 | Skill 的 capability_dependencies 每个 capability 必须在 Capability Map 中存在且 status ≠ excluded | 依赖可解析 | Agent 调用不存在的执行锚点 |
| W5 | Agent Card 认知边界 ⊆ 17 Context；技能依赖的能力必须落在认知边界内 | 边界包含性 | 员工"看不见却在做" |
| W6 | Variant 规则必须声明 base 版本；base 本身必须是完整 Rule Card | 变体锚定 | 客户配置漂移、无回归基准 |

**这六条就是你已经发明过的东西的语义版**：MI capability-traceability-matrix 的五列追溯链（legacy→spec→anchor→verification→status）保证"能力不断链"；W1-W6 保证"**语义**不断链"。组装 = 给语义模型做一次**符号解析（symbol resolution）**——这正是 W3 讲的 Ontology Compiler 的前端：编译器拿到源码第一件事不是生成代码，是把每个名字绑定到定义。六层模型组装的那一天，编译才可能开始。

---

## 三、Semantic Model v0.1 骨架（毕业作品目录）

每层 = 已有资产 + 本周升级动作 + 对下层的引用：

| 层 | 已有资产（真实文件） | 本周升级（D1-D5） | 层间引用 |
|---|---|---|---|
| Ontology | Domain Model §3 Object Ownership + ADR-006 四类关系 | 业务定义 / 身份路径 / 动词化关系（occupies 等） | 被所有上层引用（叶子） |
| Lifecycle + Event | §6 状态机 + effect-registry.yaml | 统一迁移声明：from→to / guard / emits / effects | guard→Rule ID；effects→registry |
| Rule | 领域规则块 + BCM 业务规则列 | 四物种 Rule Card（谓词结构化） | 谓词→Entity.属性；Guard→迁移 |
| Capability + Policy | BCM 能力行 + MI 追溯矩阵 + LangChat descriptor | Capability Card + 三层 Policy + Skill Mapping | 依赖→Capability；授权→Policy |
| Agent Mapping | BCM README §7 AI 层级 + §5.4 双轴 | 五字段 Agent Card（岗位锚点×边界×技能×授权×状态） | 边界→Context；技能→Skill |

一个重要的**减法判断**：组装时你会发现有些东西**不该进** Semantic Model——比如 MI 的表结构细节、LangChat 的 runtime 参数。判据还是那一条：**这个东西帮助 AI 理解企业业务吗？** 表结构帮助的是"怎么实现"（Domain Model 层的事，W1 就分过家）。Semantic Model v0.1 收敛在六层，不多不少。

---

## 四、验证设计：让模型"能够失败"的测试才叫验证

今天的主交付是**验证设计**（D7 才跑）。设计验证比跑验证难，因为最大的陷阱是：**验证场景设计得让模型不可能失败。**

陷阱长这样：只造一个 A101 夹具（被退租流程卡住的铺位），跑一遍，Agent 答对了"不能出租"→ 宣布验证通过。问题在哪？一个只会背"铺位通常不能租"的 LLM 也能通过这个测试——**单夹具、单方向、无对照的验证等于没验**。

### 4.1 三组分对照夹具（fixture）

| 夹具 | 世界状态 | 预期结论 | 考验什么 |
|---|---|---|---|
| **反例 A101** | Space=Active，存在 Terminating 租约，Inspection 未完成 | 不可租；依据 CRE-R-003 守卫未满足 | 业务链推理 + 规则失败分支解释 |
| **正例 A102** | Space=Active，无 Occupancy，无 Restriction | **可租**；依据 CRE-R-002 推导为 True | 模型不是"永远说不租"——正例是防止退化模型的对照 |
| **边界例 A103** | Space 被预定（Reserved），预定到期日 8/20 已过（今天 8/22） | 可租；依据 CRE-R-008 预定到期自动释放（Event 驱动，非查询驱动） | 时间性：结论依赖"到期事件已发生"，不是字段快照 |

**正反对照才能证明模型有判别力。** A103 是精心设计的杀手锏：如果模型的 `AvailableForLeasing` 是落库的字段（D-001 Amendment A 明确反对的做法），预定到期后没人刷字段，A103 永远显示"不可租"——这个夹具专杀"快照式实现"，逼模型走"从事实重算"的 Derivation 路径。

### 4.2 判定梯：每级的可观察输出 + 通过判据 + 失败模式

验证标准不是"答案对"，是**推理轨迹（trace）对**。答案可以是语感撞对的，轨迹撞不了——每一跳都必须携带 evidence ID。

| 级别 | 可观察输出 | 通过判据 | 典型失败模式 |
|---|---|---|---|
| L1 语义理解 | 身份路径解析结果 | 输出 `Project→Building→Floor→A101` 完整路径，而非匹配 status 字段串 | 只回"A101 状态是 Occupied"——用字段代替身份 |
| L2 业务链推理 | 关系遍历 + 状态定位 | 沿 occupies 找到关联 Lease，读出状态机节点 Terminating | 读 status 字符串而非状态机节点，说不出还差哪步迁移 |
| L3 规则判断 | 推导过程 + 失败分支 | CRE-R-002 求值为 False，**并指出**是哪条 Guard（CRE-R-003）的哪个谓词不满足 | 只说"不符合条件"，引用不出 Rule ID |
| L4 Policy 判断 | 审批路径裁决 | 创建 Inspection 免审批（②层 conditional）；引用具体 Policy 条目 | 把免审批动作也送去审批——或反之，越过 human_review_gate |
| L5 动作建议 | 建议动作 + 执行姿态 | 建议 ops.inspection.create，conditional_write，human_review_gate=true | 建议的动作不在运营 DE 认知边界内（W5 违规） |

注意每级的失败模式都预先写出来了——**验证设计必须包含"如果模型错了会是什么样"**，否则跑的时候你认不出失败。这和写单元测试先写断言是同一个纪律。

### 4.3 判分表（rubric）

| 级别 | 权重 | 必达/加分 | 判分对象 |
|---|---|---|---|
| L1 | 10% | ✅ 必达 | 轨迹：身份路径 |
| L2 | 20% | ✅ 必达 | 轨迹：关系跳 + 状态机节点 |
| L3 | 25% | ✅ 必达 | 轨迹：Rule ID + 失败分支 |
| L4 | 15% | ⚠️ 加分 | 轨迹：Policy 条目引用 |
| L5 | 30% | ⭐ 超额 | 轨迹：capability ID + 姿态 + 人审标志 |

L5 权重最高但它只是超额——因为 L1-L3 是"Agent 理解企业"的地板（本轨道四周的核心命题），L5 是天花板。**地板不达标，天花板再漂亮也不算数字员工。**

---

## 五、Agent 视角：为什么验证对象是轨迹不是答案

这是今天最重要的一条认知。LLM 时代"答案正确"的含金量暴跌——同一个正确答案，可能来自六层语义模型的推理，也可能来自训练语料里"商场铺位退租期间不能出租"的语感记忆。**区分二者的唯一办法是看轨迹**：推理链上每一跳是否携带 evidence（Rule ID / 迁移 ID / capability ID），是否落在某个数字员工的认知边界内（D5）。

这直接呼应 W3 的 Ontology Compiler：**trace 就是语义模型"编译"出的中间表示（IR）**。D7 验证报告的主体不是问答记录，是三条 trace（A101/A102/A103）+ 判分表。一个模型的可信度，最终沉淀在"它的每一步都能被引用回业务条文"这件事上——这正是四周前 W1-D4 那个发现的终局答案：AI 读 Domain Model 时语义是隐式的；四周后，语义显式到**每一跳都可审计**。

---

## 六、连接思考（与主线 W12 Vision Intelligence）

主线今天交付 Vision 五层图 + 场景矩阵：判断"一个场景落在技术栈哪一层、ROI 多少"。并行轨道今天交付六层接线 + 验证设计：判断"一个问题落在语义栈哪一层、判据是什么"。两个交付物同构，而且互补：主线场景矩阵里每个场景的"语义成本"列（D5 提出），今天有了具体的度量方式——**场景需要多少条悬空引用被补上，才能让 L1-L5 判定梯跑通**。悬空引用数 = 语义债的计量单位。两张表对着看，Vision Intelligence 才既算得清收益、又付得起语义成本。

---

## 七、架构师视角

- **以前**：模型文档写完就算交付——读者是谁、能不能读懂、读懂了能不能验证，无人负责。验收 = 领导签字。
- **现在**：模型组装完才是**编译的开始**——六条装配规则是符号解析（W1-W6 全绿才有资格进验证），三组对照夹具是测试套件，判定梯是 CI 流水线，trace 是被测产物。"能被验证的语义模型"和"能被测试的代码"完全同构：**没有夹具的模型等于没有测试的代码，没有失败模式的验证等于永远通过的测试。**

## 八、练习（5 分钟）

1. 装配规则只有六条吗？试着提出第 7 条并反驳自己。候选：*「Skill 声明 human_review_gate=true，但其能力的 Policy③ delegation=True（完全可委托），两者矛盾，应在该层裁决」*——这真是装配规则（层间引用），还是同层内的 Policy 一致性问题？它该在哪一层、由哪个字段裁决？
2. A103 夹具里，如果 Agent 最终答"可租"（答案正确），但轨迹里没有引用 CRE-R-008 的释放事件、只说"预定已经过期了"——L2 应该判过还是判挂？如果把 L2 判过，这个验证体系还杀得住"快照式实现"吗？（提示：回到 4.1 的设计动机。）

---

*配套实验：`PT-W4-D6-组装SemanticModel与验证设计.ipynb` —— 六层语义模型 dataclass 实现 + 六条装配规则审计器（含故意植入的悬空引用拦截演示）+ 三组对照夹具 + L1→L5 轨迹推理引擎 + 判分表输出 + 层间引用图与判分热力图。*
