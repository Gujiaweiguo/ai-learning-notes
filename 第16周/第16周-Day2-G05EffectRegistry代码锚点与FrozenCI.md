# W16-D2 · G-05 Effect-Registry 代码锚点 × Frozen CI：让"frozen"从注释变成退出码

> 开发期 · Week 16「治理地基 + 消费面事实化」（2026-09-15 周二，W16 brief 工作项 ②）
> Today's Question：**「Registry frozen v1.0」只是 effect-registry.yaml 里的一行注释——当它被违反时，谁会说"不"？**
>
> 📌 计划来源说明：w14-plus 无 W16 逐日条目，按其 W15-D6 交付的 `semantic-model/w16-dev-brief.md` 工作项 ②（"G-05 effect-registry 代码锚点 + frozen CI：5 类冻结 effect 逐条加 file:line 锚点；CI 规则：改 frozen effect 不带 change 即红，本地可演示"）执行；与 D1 明日连接一致。
>
> 配套实验：`第16周-Day2-G05EffectRegistry代码锚点与FrozenCI.ipynb`（8 cell 全绿，本文所有数字出自其中或同代码 CLI 实测）。

---

## 0. 今日开发目标

① S2 日探针（每日开发前）；② G-05 主菜：effect-registry 五类冻结 effect × 15 代码锚点登记（消费 W14-D4 对账清单）+ frozen CI 两门脚本本地红绿演示；③ 验收对齐 brief ②：改 frozen effect 不带 change → 红，带 change → 绿。

## 1. 完成事实①：S2 日探针与锚定基线

| 仓 | behind | 处置 |
|---|---|---|
| lnkcre | 9（baseinfo 主数据纵深延续：品牌落位对账/门店档案/变更台账/行业字典） | **拉齐**（锚点需当前 HEAD；wave 全程不触及五类 effect 的域）→ 锚定基线 `0392e107` |
| docs | 3 | 记录，周一 S1 digest 一并消化 |
| LnkChatBI | 0 | — |

挡板未触发（max 9 << 300）。lnkcre 的 9 提交仍是 D1 digest 标记的 baseinfo 波次尾段，spec 增量待 W39 digest 统一盘点——**探针只数数不做分析，这本身就是 S2 设计意图**（分析成本周一次，暴露时延 ≤1 天）。

## 2. 完成事实②：15 锚点登记（`semantic-model/governance/g05-effect-anchors.yaml`）

**锚点三元组设计**：`(file, line, expect)`——行号只是**首次观测值**，expect 是该行必须包含的子串。三级判决：

| 判决 | 条件 | 语义 |
|---|---|---|
| OK（绿） | expect 仍在登记行号上 | 证据在位 |
| DRIFTED（黄） | expect 在文件里但行号变了 | 上游插删行——**维护信号，不红** |
| BROKEN（红） | expect 在全文件找不到了 | 冻结 effect 的实现证据被改/删——**违规，须带 change** |

5 类 × 3 锚，每类覆盖三个侧面（单一侧面的证据会腐烂或说谎）：

| Effect | 声明侧 | 执行侧 | 档案侧 |
|---|---|---|---|
| state-transition | `lease/model.go:16`（8 态字面量首行） | `conditionapproval/repository.go:307` InsertLifecycleAudit | `conditionapproval/model.go:102` LifecycleAuditEntry |
| occupancy | `occupancy/state_machine.go:20` ValidateTransition | `occupancy/repository.go:26` CreateTx | `occupancy/integration_test.go:69` 活跃占用拒再预留 |
| financial | `lease/amendment_receivable_impact.go:10` ReceivableImpact | `billing/service.go:118` GenerateCharges | `arrebalance/model.go:17` 触发事件族（amendment/termination/renewal/void） |
| lead-conversion | `officelead/conversion.go:25` Convert（CD-04，幂等） | `opportunitydomain/funnel.go:253` funnelTransitions | `platform/db/models.go:4005` CRE-SAL-038 append-only 审计 |
| maintenance | `operations/repository.go:22` INSERT repair_work_orders | `material/billing_link.go:34` 工单→计费解耦契约 | `material/model.go:54` Material |

真实基线实测：**15/15 OK @ `0392e107`**（ipynb §2 子进程调用生产脚本）。附带收获：W14-D4 缺口③（lead-conversion 只有表级证据）今天补上符号级证据——`conversion.go:25` 的幂等转化函数 + CRE-SAL-038 审计表模型，锚点比当年对账更精确了一层。

## 3. 完成事实③：frozen CI 两门 + 8 场景红绿演示（`ci/frozen_effect_ci.py`）

两门各治 W14-D4 的一个缺口：**anchors 门**治缺口①（registry 无机器锚点，对账靠人读），**registry 门**治缺口②（frozen 无 CI 强制，新增 effect 不走 ORE-1 零告警）。registry 门语义：effect-registry.yaml 冻结清单任何增/删/改 → 必须带 `--change <id>` 且该 change 已立案（proposal.md 在盘）——**立案是逃逸口，不是注释**（S8 实测：伪造未立案 id 一样红）。

| # | 场景 | 门 | 实测 exit | 判决 |
|---|---|---|---|---|
| S1 | 真实基线 15 锚 | anchors | **0** | OK 15/15 |
| S2 | 上游插行×3 | anchors | **0** | DRIFTED 1（黄） |
| S3 | 篡改实现证据（CreateTx→CreateTxLegacy） | anchors | **1 红** | BROKEN |
| S4 | 篡改 + 已立案 change | anchors | **0** | BROKEN 被立案承认 |
| S5 | registry 无变更 | registry | **0** | no diff |
| S6 | 新增第 6 类 service-effect（未过 ORE-1） | registry | **1 红** | added 检出 |
| S7 | 新增 + 已立案 change | registry | **0** | 合法变更 |
| S8 | `--change g99-not-filed`（未立案） | registry | **1 红** | 逃逸口须真立案 |

**brief 验收②达成**：改 frozen effect 不带 change → 红（S3/S6/S8）；带 change → 绿（S4/S7）；本地双向演示完毕（ipynb §3 + 图 1 `w16d2_gate_matrix.png`）。S6 选 service-effect 做篡改素材是有意的——它正是 2026-07-29 经 PT-CS-06 评审**被拒绝注册**的类型，用它演示"不走评审的注册"恰是 ORE-1 要防的事故。

## 4. ipynb 要点：三策略锚点腐化模拟（§4，图 2 `w16d2_anchor_strategies.png`）

用两个真实锚点文件做 5 场景 × 400 次蒙特卡洛，回答"file:line 在 15 commits/天的仓库里能活多久"：

| 场景 | A 包路径（现状） | B 纯行号 | C 行号+内容（本设计） |
|---|---|---|---|
| 上游插行（良性） | 0% 告警 | **100% 误报**（狼来了） | 0% 红 + 100% 黄（正确识别为维护） |
| 下游插行（良性） | 0% | 0% | 0% |
| 改名（违规） | **0% 漏报**（静默腐烂） | 100% | **100% 抓获** |
| **扩名不改名（违规）** | 0% 漏报 | 100% | **0% 漏报——盲区** |
| 删除锚点行（违规） | 0% 漏报 | 100% | **100% 抓获** |

**今日最重要的实验发现**：`StatusDraft → StatusDraftLegacy` 这类"扩名不改名"对子串锚点**不可见**（新名包含旧子串）——这个盲区不是实现 bug，是子串语义的固有代价，已作为显式断言登记进 ipynb（`assert stats["tamper_extend"]["C"] == 0`）。B 策略恰好在这类场景全中，但代价是良性场景 100% 误报——**什么都报的策略总会蒙对几类，问题是你无法分辨它哪次是对的**。缓解组合：expect 升级为定界签名（v0.2 候选）+ registry 门 + 周期指纹复核（D1 模式）成网。

## 5. Today's Question 的回答

frozen 的执行者是谁？**昨天：没有执行者**——`# Registry frozen v1.0` 是写给未来的读者看的注释，违反它的方式有无数种（加一类、改语义、改证据），而没有一种会被当场拒绝。**今天：退出码**——`frozen_effect_ci.py` 把治理裁决编码为 0/1，CI 是唯一不会被"下次再改"稀释的沟通语言。更深一层：门禁没有消灭变化的权利，只是**给变化定价**——想改冻结项？可以，先立案（S4/S7 的绿色通道）；不想立案？那就红（S3/S6/S8）。这与 D1 的指纹链、chatbi 白名单 citing action 是同一模式在代码侧的实例化：**治理不防变化，治理让变化留下机器可核对的痕迹**。

## 6. 明日连接（W16-D3 · brief 工作项③）

chatbi 白名单 20 对象登记 Identity 构件 + D3 生成物修订（示例 #2 值域口径回生成器）并重出 pack，S6 回执换新（manifest+数字+指纹）。两个今日输入要带上：① D1 digest 的 P0——LnkChatBI **domain-semantic-pack-contract** 已归档，pack 重出须对齐该契约（回执新增契约对照项）；② P2 待查（trade/industry 字典表是否产生新 canonical 表/术语）在 Identity 登记时一并核。G-01 提案继续等主仓立案窗口；G-05 锚点从今日起进 S1 周验基线（digest 增锚点漂移项）。

## 7. 理解变化（保留学习期传统）

以前以为：CI 就是"跑测试的"——测试绿了 CI 就没别的事了。现在知道：CI 的本质是**把治理裁决编码为退出码**——测试只是裁决的一种来源，"改冻结项必须带 change"同样是裁决，且是测试框架不管的那一种（没有测试会在你往 registry 塞第六类 effect 时失败）。以前还以为：锚点 = 行号。现在知道：**锚点是 (file, line, expect) 三元组，行号只是首次观测值**——纯行号的 CI 会在第一次上游插行时狼来了，而被狼来了训练出的团队最终会关掉告警（策略 B 的 100% 误报就是关告警的完整理由）；把"证据消失"（违规）与"位置漂移"（维护）分开判级，门禁才能在 15 commits/天 的仓库里活过第一个月。治理工具的第一性指标不是"能抓到什么"，是**误报率低到没有人想关掉它**。
