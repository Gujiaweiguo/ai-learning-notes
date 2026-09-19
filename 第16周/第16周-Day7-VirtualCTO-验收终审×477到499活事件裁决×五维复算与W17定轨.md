# W16-D7 · 🔄 Virtual CTO Review：治理地基验收终审 × 477→499 活事件裁决 × 五维复算与 W17 定轨

> 开发期 · Week 16 收官（2026-09-20 周日）
> 评审对象：w16-dev-brief 四工作项 + S1-S6 机制全周运转 + D5 材料包（`semantic-model/sync/w16-review-materials.md`）五议题
> 评审方式：同 W14/W15-D7——结论每条可复算，本文所有数字为今晨 06:00 后新鲜实跑，非转述；配套 ipynb 即执行版
> 配套实验：`第16周-Day7-VirtualCTO-验收终审×477到499活事件裁决×五维复算与W17定轨.ipynb`

> **计划来源说明**：w14-plus 无 W16 逐日条目；按解析规则回落 learning-plan.md 每周节奏表（周日 = Virtual CTO Review + 五维评分 + ADR Health Check），叠加 w14-plus「开发期保留机制」表（周日 Review 是开发期唯一质量闸门）与 W15-D6 brief §4「周日 Review 增查同步健康」。第 2 次建议 Jason 在 w14-plus 补 W17 逐日条目或一行指向（见 §7）。

---

## 0. 裁决速览（TL;DR）

| 裁决项 | 结论 |
|---|---|
| W16 四验收线 | **三达成 + 一部分达成**（①G-01 对账侧 100%/受理侧第 3 周未开窗——裁决权在主仓；②超额：三门全绿 + 突变留痕；③③④ 全达成，今日终审复算在案） |
| 活事件终报 | canonical **477→484→499**（D6 后两日再 +15，五族 22 表）；G-07 门转正**次日即执勤**：44 BROKEN（22 孤儿 + 22 泄漏）RED，归因 file:line 单行精确 |
| 主仓平行呼应 | lnkcre 出现 `canonical_set_test.go`（integration 门，testdata 清单=499）——主仓自己也开始做集合对照；G-07 基线升级从此有权威对齐源 |
| 五议题 | 全部落定：G-01 并轨 W17 / G-07 首位动作修正为「基线升级+五族 citing」/ 备份线 W39 定性 / LnkReport 另立清单 / 五维复算 6.9（见 §4） |
| 五维终值 | 均值口径 **6.9**（持平 W15）/ 木桶口径 **6.0**（回摆 0.5，DX 下调有实锤）；预填 7.0 vs 复算 6.9 **命中**（校准履历样本 3） |
| ADR Health | BCM ADR-001~006 published 冻结健康；LangChat ADR-004 挂账**第 4 周**（L70-73 仍 langchat.*，全目录残留 16 处）——继续登记不动手 |
| 同步健康 | lnkcre 29→47 / docs 23→24 / chatbi 0；挡板未触发（max 47 < 300）；SoT 指纹 **五度一致** `bf550bc24de66813`；**探针踩坑自曝**：首跑错仓得假值 87（真值 24），S2 脚本化提前到 W17-D1 |

---

## 1. 四条验收线终审（brief §3 逐条，D5 对账 + D6/D7 增量事实）

| # | 验收线 | 终审判定 | 终审证据（今日实跑/复算） |
|---|---|---|---|
| ① | G-01 change 立案受理 + 指纹登记（底线：立案受理 + 对账报告） | **部分达成**（对账 100%，受理 0%，第 3 周） | 对账侧：C1-C5 证据链 D4 重放全 PASS，SoT 指纹今日**五度一致**（`bf550bc24de66813`，本地=origin/main）。受理侧：docs 增量 24 commits 主题分类 = 备份×15 + mi-cre 收口×4 + lnkchat 受理×4 + lnkreport×1，**零 ontology/governance 主题**；受理机器活着（同窗 accept 了 PRD-LC-E1-001/F1-001/DV-LC-004）——我们的件不在队列 ≠ 被拒，是队列优先级问题 |
| ② | frozen CI 红绿可测 + 突变留痕（D4 升级线） | **达成（超额）** | 三门今晨全部实跑：G-05 anchors **15/15 OK GREEN**（@0392e107 零漂移）；Identity verify **26/26 OK GREEN** + selftest GREEN（碰撞哨兵 PASS）；canonical selftest **6/6 PASS**。突变留痕已固化 selftest 子命令，可重放 |
| ③ | Identity 20 对象 100% 登记 + 值域 11/11 + pack 重出回执 | **达成** | 登记 20/20（v0.1.1 含 D4 重锚）；今晨复算 pack 磁盘指纹 = 回执指纹：terminology `8137b094a09c5e02` / sql_examples `0af3cb1f524cb908`（D3 回执原值，零漂移）；回执内含幂等 (0,0,0)、电池 2→19/2→13、e2e 11/11、A101 L1-L3 PASS |
| ④ | digest 落盘 + 第二个 ontology.yaml 裁决 | **达成** | `sync/digest-2026-W38.md` §5 五件全裁决；SoT 未漂移（今日前瞻复算 origin/main 同指纹） |

**终审结论**：brief 目标「从可消费推进到可治理」——**治理的三件套（登记/门禁/回执）本周全部从清单变成机器可执行**，唯一未闭环是主仓侧受理（非我方可控，对账自足）。四线之外的最大事实仍是 D5 的发现：**验收线守交付，门守漂移**——而漂移本周没有停（§2）。

---

## 2. 活事件终报：canonical 477 → 484 → 499（五族 22 表）

### 2.1 时间线与家族构成（全部今日实测，ipynb §2 复算）

| 时点 | 表数 | 增量 | 家族 |
|---|---|---|---|
| 09-16 D3（基线冻结，0392e107） | 477 | — | — |
| 09-18 D5（活事件首报） | 484 | +7 | leasing_policy 族 + unit_pricing 族（迁移 000227/000229） |
| 09-19 D6 | 484 | +0 | 波次延续但无新表 |
| **09-20 D7（今日，origin 0f66f152）** | **499** | **+15** | **indicator-target ×3（000233）+ leasing-progress ×10（000234）+ unit_leasing ×2（000234）** |

22 张新表（按名前缀分五族；file:line 归因以门输出为准）：`indicator_monthly_target_history / indicator_monthly_targets / target_indicators`（indicator-target）；`leasing_progress_{tasks,settings,setting_audits,task_adjustments,event_consumptions} / leasing_stage_{templates,template_items,completion_facts,plan_overrides} / leasing_plan_recalc_batches`（leasing-progress）；`unit_leasing_plans / unit_leasing_stages`；`leasing_policies / leasing_policy_versions / leasing_policy_lifecycle / price_authority_constraints`（leasing-policy）；`unit_pricing_batches / unit_pricing_batch_lines / unit_pricing_batch_ops`（unit-pricing）。

### 2.2 G-07 门执勤证据（转正次日即上岗）

`canonical_drift_ci.py verify` 今晨实跑（现实源 = lnkcre@origin/main）：

```
baseline: 477 表, 集合指纹 1a4c50e673ef32d2（行序不敏感）
reality : 499 表, 集合指纹 7994cb4839ddc5b1
added 22 / removed 0 / cited 0 / leaked 22 → BROKEN 44 → RED
```

归因单行精确（例：`pg:000233_indicator_target_value_layer.up.sql@L36`、`pg:000234_leasing_progress_phase1.up.sql@L90/L105`）。**RED 不是门的失败，是门在咬真骨头**：44 BROKEN 每条带地址，22 张表逐张可裁决——对比 D5 靠人工 diff commit 内容才发现，检测成本从「读 19 个 commit」降到「一条命令」。

### 2.3 主仓平行呼应：canonical_set_test.go

本周增量中出现 `backend/internal/platform/database/canonical_set_test.go`（integration build tag）：读 `testdata/canonical_tables.txt`（**499 条**，主仓清单已跟上现实）对照实际库做集合校验。三层解读：

1. **同一焦虑的两层执法**：主仓门对照「库 ↔ 清单」（需要活 DB，integration）；G-07 门对照「清单 ↔ 迁移源 + 语义层裁决」（无 DB，秒级，且多一维 citing 判决）。互补不重复——主仓清单恰好成为 **G-07 基线升级的权威对齐源**（477→499 不是我们数出来的，是主仓清单确认的）。
2. **同名双文件陷阱（本周第三案）**：`migrations/canonical_tables.txt`（仅 3 表，con-005 局部集）与 `testdata/canonical_tables.txt`（499 全量）同名不同义——D4 词边界、D6 目录前缀之后，「名字包含名字」家族的文件版。本周踩到两次（见 §6 坑）。
3. **G-07 的 W17 基线升级有了合法程序**：基线头部自declare「快照非 SoT，升级须 digest 裁决」——W39 digest（周一 D1）执行 477→499 升级，对齐源即主仓 testdata 清单。

### 2.4 裁决

- **22 表逐族 citing change 列为 W17 主菜**（五族五个裁决：入域登记 or 显式不入域，落在 changes/ 才算 citing——门的设计初衷）。
- **不追赶式刷基线**：基线升级必须走 digest 裁决（W39），不在活事件压力下静默改基线——静默改基线 = 把门的牙齿拔了。

---

## 3. 议题裁决（材料包 §4 五项，逐项落定）

| # | 议题 | 裁决 | 理由（今日证据加权） |
|---|---|---|---|
| 1 | G-01 挂起 or 坚守 W17 | **并轨 W17（G-01×G-07 合并提案）** | 第 3 周未受理 + 对账侧 100% 自足 + 活事件 7→22 使并轨叙事更重：治理头与新表挡板本来就是「谁管什么/变化怎么留痕」一件事的两面。D6 骨架 `changes/_drafts/g01g07-merged-skeleton.md` 于 W17-D1 升格正式提案提交 |
| 2 | G-07 提为 W17 首位 | **修正：首位动作 = 「基线升级裁决 + 五族 citing」而非转正** | 材料包建议时门尚未转正；D6 已转正且今晨在执勤（44 BROKEN）。W17 首位变成消化事件而非建门——G-07 转正这件事本身提前完成 |
| 3 | docs 备份线语义定性 | **W39 digest 立案议题** | 本周备份 15/24 = 62.5% 的 docs 增量（09-15 起每日一备）；定性问题（备份线 vs 治理线）影响 behind 数的解读口径，属 digest 职责，不周日抢答 |
| 4 | LnkReport 第三消费方（doc-grain 视图×3） | **另立 lnkreport 消费面清单，不并入 chatbi 白名单** | 白名单锚定 lnk_chatbi_ro 单一消费主体；并入会稀释「一主体一清单」的 Identity 语义。W17+ 候选维持 |
| 5 | 五维预填复核（孤儿表是否算 Code Health 扣分） | **孤儿表是主仓的债，不算语义层 Code Health 扣分**；语义层的债 = 登记滞后 + 基线升级欠裁决 → 计入 Technical Debt 论证 | 见 §4 |

---

## 4. 五维复算（先跑证据再对分；口径与纪律 v1.1：发布必带口径）

| 维度 | W15 | W16 预填 | **W16 终值** | 终值理由（今日证据） |
|---|---|---|---|---|
| Architecture Quality | 7.0 | 7.5 | **7.5** | 三门同哲学成体系（fail-closed/三级判决/--change 承认/--json）；主仓 canonical_set_test.go 平行呼应证明判断方向；扣：22 表裁决流程未闭环（但全部被门盯住带归因） |
| Code Health | 6.5 | 7.0 | **7.0** | 验证器 1→3 全带 selftest；值域修复带连带发现；扣：canonical 门默认现实源是 origin/main 而非本地 HEAD——语义正确但文档未言明（今晨才看清）；仍非 CI（本地脚本）；生产 GRANT 对账缺位 |
| ADR Consistency | 6.5 | 6.5 | **6.5** | 分层 SoT 五度指纹一致；G-01 第 3 周未受理——「说」在加强「裁」原地（裁决权在主仓，我方无违约）；ADR-004 挂账第 4 周继续登记 |
| Technical Debt | 8.0 | 7.5 | **7.5** | 新债（22 孤儿 / 备份线未定性 / 11 无血缘对象）全部登记不静默，可见性 100%；但主仓产出速度（+15 表/2 天）> 登记消化速度（citing 待 W17）——债在加速长，靠门保持可见 |
| Developer Experience | 6.5 | 6.5 | **6.0 ↓** | 下调实锤两条：① S2 探针从未脚本化，今晨人肉 cd 踩错仓得出假值 87（真值 24），差点进材料——探针体验是 DX 的一部分；② 消费面本周零新用户动作（生产 pack 接入未动，PARTIAL×3 挂起）。维持项：三门 CLI+--json+selftest、receipt 机读 |

- **均值口径：(7.5+7.0+6.5+7.5+6.0)/5 = 6.9**（W15 6.9，持平）
- **木桶口径：6.0**（W15 6.5，回摆 0.5——最弱维度 DX 本周实锤恶化，五周来首次单维下调）
- **校准履历样本 3**：W13 命中上沿 / W15 MISS 偏高 / **W16 命中**（预填 7.0，复算 6.9，|Δ|=0.1 ≤ 0.3）——预填质量改善归因于「先跑证据再对分」程序化（W15 教训的机制化兑现）。样本仍不足 5，预测器本身不评。

**本周理解进度：8/10。** 「治理链从清单到门禁」的跃迁完成且被活事件检验；扣分项：基线会过期这件事是活事件教的而非设计预见——冻结的基线第二天就过期（477 冻结于 D6，D7 现实 499），**门的价值不在基线永远对，在漂移从此有地址、升级从此是裁决而非猜测**。

**本周新增认知清单**（7 条，全周沉淀）：
1. 验收线守交付，门守漂移——合同条款管不了环境事件（D5）
2. 集合门 vs 计数门四盲区：无对象性/无方向性/无归因链/无负锚（D6）
3. 门禁交付必须附带突变证据，否则是绿色的装饰品（D4）
4. 改投影是漂移，改源是演进（D3）
5. 双证据判定：内容证据定性质，治理证据定风险（D1）
6. 子串锚点对扩名盲/词边界规则/目录前缀边界——「名字包含名字」三案家族（D2/D4/D6）
7. 冻结不是终态是起跑线，基线升级须裁决程序（D7 今日）

**Charter 对齐**：分层 SoT（五度指纹一致）/ S6 回执律（pack=回执零漂移）/ fail-closed（三门 + 探针挡板）全部符合；唯一张力是 G-01 受理周期（主仓侧，非违约）。

---

## 5. ADR Health Check（周日固定项）

| 对象 | 状态 | 今日证据 |
|---|---|---|
| BCM ADR-001~006（cre-business-capability-matrix） | **健康（published 冻结）** | 全部止于 903d07c 冻结 commit，无后续变更；effect-registry 五类冻结与 G-05 锚点对账 15/15 |
| LangChat ADR-004（rename-mallsenseai） | **挂账第 4 周** | grep 实锤 L70-73 仍 `langchat.vision.detect@v1` 等四条命名串（ADR-008 已裁定 lnkchat.*）；全 ADR 目录残留 `langchat.*`（非 lnkchat）**16 处**。处置：继续登记不动手——ADR 是冻结件，改名须走 ADR 修订流程，且 langchat 主仓不在 S1 探针范围（开发期口径） |
| 拆分/新增需求 | 无 | 六件 BCM ADR 职责边界清晰，无过时信号 |

新观察（非 ADR 体系，登记备查）：主仓 `canonical_set_test.go` 是主仓侧对「表宇宙治理」的架构表态——若主仓后续将其升格为 spec/ADR，G-07 应对齐引用而非平行演化（避免我们自己制造「平行家族」——G-01 教训的自我适用）。

---

## 6. 同步健康终查（brief §4 增查项）

### 6.1 S2 探针终值（今晨 06:00 后）

| 仓 | D5 | D6 | **D7** | 备注 |
|---|---|---|---|---|
| lnkcre | 19 | 29 | **47**（origin 0f66f152） | +18：leasing-progress Change A phase-1（000234）、indicator-target（000233）、unit-pricing rev3、E2 文档生成入口、openspec 归档若干 |
| docs | 22 | 23 | **24**（本地 HEAD 保持 c3d08d6） | +1 = 备份线第 15 commit；SoT 指纹 origin/main = 本地 = `bf550bc24de66813` **五度一致** |
| LnkChatBI | 0 | 0 | **0** | 静默 |

挡板（>300）未触发，本周 max 47。W39 digest（周一）随基线升级裁决一并三仓 pull 对齐。

### 6.2 今日坑自曝（三条，全部运行时证据）

1. **探针错仓**：首跑探针时 cd 顺序 fallback 命中 `/root/langchat-docs`——它同样含 `lanlnk/` 目录树（连 business-ontology.yaml 都是同指纹副本），得假值 **87**；真仓 `/root/docs` = **24**。假值险些进入本 Review 材料。教训：**S2 探针从未脚本化是人肉流程，必须钉死绝对路径**——W17-D1 落 `sync/probe.py`（三仓固定路径 + 表集合 diff，即 G-07 草稿 §3 药方提前实施）。
2. **canonical 同名双文件**：`migrations/canonical_tables.txt`（3 表）vs `testdata/canonical_tables.txt`（499 全量）——第一版集合 diff 全部 477 表显示「被删」假象。「名字包含名字」家族第三案（词边界 → 目录前缀 → 同名文件异目录）。
3. **ADR 检索错体系**：ADR-004 挂账复查首跑查了 BCM 的 ADR-004（Binding Model，无 langchat 引用），挂账实际在 langchat/docs/adr 的 ADR-004——同名编号跨体系，检索必须带体系限定。

---

## 7. W17 定轨（下周建议，D1 起执行）

| 序 | 动作 | 验收线 |
|---|---|---|
| 1 | **W39 digest（D1 周一）**：三仓 pull 对齐 + **canonical 基线升级裁决 477→499**（对齐源=主仓 testdata 清单）+ 备份线定性 + 三门周验（G-05 15 锚 / Identity 26 锚 / canonical 新基线重跑） | digest 落盘 + 基线升级记录在案 |
| 2 | **G-01×G-07 并轨提案升格提交**：从 `_drafts/` 升格正式 change（含活事件第四条证据链更新至 22 表） | 提交落盘 + 等受理（对账侧自足） |
| 3 | **五族 22 表逐族 citing change**：indicator-target / leasing-progress / unit_leasing / leasing-policy / unit-pricing，逐族裁决入域 or 显式不入域 | 五 change 落盘，canonical 门 cited 数 0→N |
| 4 | **S2 探针脚本化**：`sync/probe.py` 钉死三仓绝对路径 + 表集合 diff（§6.2 坑 1 的直接修复） | 每日一条命令出全量探针值 |
| 5 | G-07 v0.2：expect 升级定界签名（治扩名盲区，D2 遗留） | 突变证据更新 |
| 6 | MCP 工具描述 change（brief W17 ⑥）：**后置于基线升级裁决之后**（依赖表宇宙稳定） | 提案 draft |

范围红线（维持）：Rule/Policy 显式化仍 W18；生产 GRANT 对账 W17+ 候选；LnkReport 消费面清单另立不动 chatbi 白名单。

---

*本文所有今日数字可由配套 ipynb 复算；三门命令、集合 diff、docs 主题分类、五维趋势均有对应 cell。评审人：Virtual CTO（OpenClaw）；材料：D5 材料包 + D6 补充节 + 今晨实跑证据。*
