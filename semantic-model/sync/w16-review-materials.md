# W16 Virtual CTO Review · 材料包（D5 预备，2026-09-18）

> 用途：W16-D7（9/20 周日）Review 直接消费。评审对象 = w16-dev-brief 四工作项 + 本周机制运转。
> 口径：每条结论可复算——证据指针均为今日（09-18）新鲜复算，非转述。

## 1. 四条验收线对账（brief §3 逐条）

| # | 验收线（brief 原文口径） | 今日复算 | 判定 | 证据指针 |
|---|---|---|---|---|
| ① | change 立案受理 + 合入后指纹登记（底线：立案受理 + 对账报告） | 对账报告 ✓（evidence-chain C1-C5 今日重放**全 PASS**：SoT 指纹 `bf550bc24de66813` 三度+今日四度一致；五件家族指纹 5/5 零漂移；产品件反向引用 0；同名异义 1/3 并存）。立案受理 ✗：docs behind 15→22，增量 22 commits 主题=备份×13+lnkchat PRD 受理×4+mi-cre handoff 收口×4+lnkreport×1，**零 ontology/governance 主题**——但注意：docs 受理机器活着（PRD-LC-E1/F1-001、DV-LC-004 同窗口被 accept），我们的件不在队列里 ≠ 被拒 | **部分达成**（对账侧 100%，受理侧 0%，裁决权在主仓） | `changes/g01-ontology-governance-header/evidence/claims-2026-09-17.json` + 今日 docs origin log（46d9d6d） |
| ② | frozen CI 红绿可测（D4 升级为 +突变留痕） | G-05 门 15/15 OK GREEN（repo HEAD `0392e107`）；Identity 门 26/26 OK GREEN；selftest 4 突变+碰撞哨兵全 PASS——今日全部重跑 | **达成（超额）** | `governance/ci/frozen_effect_ci.py` / `identity_anchor_ci.py` 实跑记录（D5 md §2） |
| ③ | Identity analysis 域 20 对象 100% 登记；值域复验 11/11；pack 重出 + 回执更新 | 登记 20/20（16 open+3 gov+1 func，v0.1.1 含 D4 重锚修订）；生成器 v0.1.2 今日自检复现：术语 14 组/81 别名、示例 11 条、值域对账 **11/11（9 PASS+2 N/A，0 FAIL）**；回执指纹 `8137b094…`/`0af3cb1f…`、upsert 幂等全 0、电池 2→19/2→13、e2e 11/11、A101 L1-L3 PASS | **达成** | `governance/identity-analysis-anchors.yaml` + `consumers/lnkchatbi/import-pack/import-receipt.json` |
| ④ | digest 报告落盘 + 第二个 ontology.yaml 裁决 | `sync/digest-2026-W38.md` §5 五件全裁决：1 SoT 治理头缺失（G-01 主体）/ 3 产品级 live（非双 SoT，治理关系未声明）/ 1 冻结件未标记；今日复核第二 ontology.yaml 原位、指纹 `0a74edf9be475ecc` 未漂移 | **达成** | digest §5 + 今日 sha256 复算 |

**对账之外的发现（不属任何验收线，但属 Review 必看）**：canonical 477→484（+7 孤儿表）+ analysis 域 +3 视图（第三消费方 LnkReport 模式成形）+ role_permissions +1 ——详见 `governance/g07-newtable-guardrail-draft.md §0`。四线全绿的世界里结构性缺口开着：**验收线守交付，没人守漂移**。

## 2. 同步健康（D7 增查项，brief §4）

### 2.1 S2 探针趋势（behind 计数，日频）

| 日期 | lnkcre | docs | LnkChatBI | 备注 |
|---|---|---|---|---|
| D1 09-14 | 15（pull 清零→bd00eb6a） | 63（pull，SoT 零漂移确认后） | 14（pull） | W38 digest 三仓对齐 |
| D2 09-15 | 9 | 3 | 0 | baseinfo 波次尾段 |
| D3 09-16 | 0（=基线 `0392e107`） | 0（=基线 `c3d08d6`） | 0（=基线 `c8927267`） | 三仓基线日（s1-checklist w39_baseline） |
| D4 09-17 | 0 | 10→15 | 0 | docs 备份线累积 |
| **D5 09-18** | **0→19**（→origin `51e9baf9`） | **15→22**（→origin `46d9d6d`） | 0 | **lnkcre 单日 19 ≈ 均值 15.1/天上限区；携带 +7 表活事件（§2.3）** |

### 2.2 SoT 指纹 diff

- business-ontology.yaml：本地 `bf550bc24de66813` = 基线，四度一致；**前瞻**：W39 pull 前须 `git show origin/main:… | sha256` 复算（W15-D7 程序）。
- 白名单 spec（chatbi-governed-account-boundary）：origin 增量**未触碰**（diff 实测仅 3 个新 spec，全为新增文件）→ W39 pull 后 Identity 26 锚预计零漂移（仍须实跑）。

### 2.3 挡板与事件记录

- S4 挡板（behind>300）：**从未触发**（本周 max 63）。
- 事件：09-18 canonical +7 表（G-07 活事件，检测延迟 1-2 天，路径=人工 diff 而非任何门）——挡板对「commit 里装了什么」结构性失明，已在 G-07 草稿 §3 开药方（探针升级为表集合 diff）。

### 2.4 backlog 对调评估（建议 D7 裁决）

| 议题 | 选项 | D5 建议 |
|---|---|---|
| G-01 挂起 or 坚守 W17 | ① 挂起至 W17 与 G-07 并轨提案（D4 遗留）② 继续逐日探针跟进 | **①并轨**：docs 受理机器在处理其他队列，我方零杠杆；对账侧已 100% 自足，受理是主仓时间问题。并轨后 G-01+G-07 合成一份「治理头+新表挡板」语义层双 change，叙事完整 |
| G-07 提级 | W17 原计划 vs 提为 W17 首位 | **提为 W17 首位**：活事件给了回放素材与紧迫性；MCP 工具描述 change（W17 ⑥）依赖稳定的表宇宙，G-07 应先行 |
| W16-D6（周六）用途 | ① G-07 原型转正（canonical_drift_ci.py）② G-01 等待 ③ review 材料细化 | **①**：把 D5 ipynb 里的 mini 集合门转正为 ci 脚本 + selftest 突变证据，周六动手日传统与开发期合流 |

## 3. 五维评分预填建议（D7 复算后定稿）

| 维度 | W15 | W16 预填 | 预填理由（D7 须复核） |
|---|---|---|---|
| Architecture Quality | 7.0 | **7.5** | 两道锚点门 + 词边界/泄漏检查语义各自适配锚定对象（不强求统一验证器）；扣：表集合边界无门（G-07 活事件实证）——若 D7 认可「缺口已定位+范本已起草」可加回 |
| Code Health | 6.5 | **7.0** | 验证器从 1→3（frozen/identity/+D6 计划的 canonical 门），全部 fail-closed+机读输出+selftest；值域盲区修复且连带发现 #8；扣：仍是脚本非 CI，生产 GRANT 对账缺位 |
| ADR Consistency | 6.5 | **6.5** | 分层 SoT 宪章连续第二周实战（指纹链四度一致）；但 G-01 change 未过（第 2 周）——一致性「说」的部分在加强，「裁」的部分原地 |
| Technical Debt | 8.0 | **7.5** | 新债（+7 孤儿表、docs 备份线语义未定性、11 无血缘对象）全部登记不静默；债在长，登记速度本周略输于主仓产出速度 |
| Developer Experience | 6.5 | **6.5** | pack 契约对照如实标 PARTIAL、receipt 机读化；扣：本周消费面无新用户动作（Demo 已闭环，生产接入未动） |

预填均值 **7.0**（W15：6.9）——注意 W15 教训（预测偏高落空）：D7 复算时先跑证据再对分。

## 4. 议题清单（D7 逐项裁决）

1. G-01 挂起→W17 与 G-07 并轨？（§2.4 建议①）
2. G-07 提为 W17 首位 + D6 原型转正？（§2.4）
3. docs 备份线（累计 13 个「备份」commit）语义定性：W39 digest 议题立案？
4. analysis 域第三消费方（LnkReport doc-grain 视图）是否登记为 Identity 家族新成员（现白名单=chatbi 专属）？——建议：不并入 chatbi 白名单，另立 lnkreport 消费面清单（W17+ 候选）
5. 五维预填复核 + 木桶口径（Technical Debt 7.5 是否高估：孤儿表是不是该算 Code Health 扣分？）

## 5. D6 补充（2026-09-19 周六，供 D7 裁决时与 §2.4 对读）

- 议题 1/3 的裁决材料已补齐：`changes/_drafts/g01g07-merged-skeleton.md`（G-01×G-07 并轨提案骨架，含活事件第四条证据链与 W17 验收线现状——回放/突变两项已提前达标）。
- G-07 门已转正实跑：`governance/ci/canonical_drift_ci.py`（活事件回放 7+7 BROKEN 红、selftest 六突变全 PASS、--change 承认路径预演绿）；基线冻结 `canonical-baseline-w39.txt`（477 表，集合指纹 `1a4c50e673ef32d2`）。
- S2 探针 D6：lnkcre behind 19→29（origin 51e9baf9→94b83434，+10 commits 无新表但 leasing_policy/unit_pricing 波次延续——孤儿案家族仍在扩案）；docs 22→23（备份线第 14 commit）；LnkChatBI 0。
