# G-07 新表挡板 · 设计范本草稿（v0.1-draft）

> 起草：2026-09-18（W16-D5 brief 验收对账日）。状态：**draft——W17 执行**（w16-dev-brief §6 已排 W17；本稿把「抄 chatbi 白名单范本」落成具体设计）。
> 起因不是规划，是**活事件**：对账当天探针发现 lnkcre 0→19 增量携带 canonical_tables **477→484（+7 表）**，语义层零登记、四条验收线全部无感——G-07 要防的场景在起草当天真实开火。

## 0. 活事件档案（2026-09-18 S2 探针 + 取证）

| 事实 | 证据 |
|---|---|
| lnkcre behind 0→19（HEAD `0392e107` → origin `51e9baf9`） | `git fetch` + `rev-list --count` |
| canonical_tables.txt **477 → 484（+7）**，全部不在语义模型 v0.1 在册宇宙 | `git show origin/main:.../testdata/canonical_tables.txt` diff |
| +7 = leasing_policies / leasing_policy_versions / leasing_policy_lifecycle / price_authority_constraints / unit_pricing_batch_ops / unit_pricing_batches / unit_pricing_batch_lines | PG 迁移 000227（5 表）+ 000229（2 表）——**双迁移目录教训：MySQL 侧 `migrations/` 编号与 PG 侧 `migrations-pg/` 各自独立**（本地 MySQL 000229=custom_form_types，origin PG 000229=unit_pricing_batch_model），只盯一个目录必漏 |
| analysis 域新增 3 视图（v_billing_document / v_billing_document_line / v_lease_contract，供 LnkReport 消费） | PG 迁移 000231；与 chatbi 白名单 20 对象**零重叠**（grep 实测 0），但同在 analysis 域——**第三个消费方**模式成形 |
| role_permissions 80→81（+pricing.authority） | canonical_role_permissions.txt diff |
| openspec specs 311→314（+analysis-doc-grain-views / demo-seed-data-integrity / workflow-assignee-seed-coverage） | `git diff HEAD origin/main --name-only -- openspec/specs/` |
| 检测路径：**不是任何验收线**，是 S2 探针背后的人工 diff；S2 本身只数 behind（19），对「里面有没有表」完全失明 | 本次事件检测延迟 = 表落地（09-16/17）→ 发现（09-18）≈ 1-2 天，纯属对账日恰好多看了一眼 |

**结论**：四条 brief 验收线全绿的世界里，7 张孤儿表无声落地——验收线守「我的交付」，没人守「世界的漂移」。G-07 从 W17 功能项**提级为本周对账暴露的结构性缺口**。

## 1. 监视对象与来源

| 侧 | 来源 | 说明 |
|---|---|---|
| canonical 全量 | `lnkcre:backend/internal/platform/database/testdata/canonical_tables.txt` | 唯一全量清单（477→484 的事实源）；`migrations/canonical_tables.txt` 是每迁移 fixture（3 行），勿混 |
| 建表语句 | `migrations/` + `migrations-pg/` **双目录** | 表的出生证明；两目录编号独立，一律并集扫描 |
| 语义层登记宇宙 | `semantic-model/mi-cre-semantic-model-v0.1.yaml` entities + ontology SoT | 语义层「认识」的表 |
| citing 登记 | `semantic-model/changes/*/` openspec change | 新表的「准生证」——citing action 所在 |

## 2. 门设计：抄 Identity 三件套（正锚 + 负锚 + 泄漏检查）

与 `identity_anchor_ci.py` / `frozen_effect_ci.py` 同门：fail-closed、三级判决（OK/DRIFTED/BROKEN）、--strict、--json 机读输出、selftest 注入排练。差异：锚定对象从「文本行」变成「集合关系」，判决天然是集合运算而非正则：

| 检查 | 语义 | 判决 | 对应今天活事件 |
|---|---|---|---|
| **正锚（canonical ⊆ 已知宇宙）** | canonical 新表必须 ∈ 语义模型在册 ∪ 已 citing 它的 open change | 新表两者皆无 → **BROKEN（红）** | 7/7 全红——今天的真实判决 |
| **负锚（登记 ⊆ canonical）** | 语义层在册实体从 canonical 消失 = 死登记 | 消失 → BROKEN（登记腐烂方向） | 防语义层变成「说有却没有」的谎言层 |
| **泄漏检查（最危险方向）** | 同 Identity 授权区泄漏同构：新表落地却**没有任何 change 引用它**（哪怕语义模型还没登记） | canonical 增量 ∧ 引用数=0 → **BROKEN** | 今天事件正是此形态：主仓 change 有 5 个（leasing-policy rev2 等），但语义层侧零引用——引用关系要在**语义层的 changes/ 目录**立案 |

**citing-action 模式**（与 ORE-1、G-05 change 门同一哲学）：挡板不禁止新表——主仓加表是它的自由；挡板给新表**定价**：落地后 X 个探针周期内，语义层必须有一张 change 引用它（内容：实体登记 or 显式「不入域」裁决，两者都算 citing，不裁决才是违规）。变化留痕，不是禁止变化。

## 3. 检测节奏：S2 探针从「数 commit」升级为「数表」

今日事件的教训链：S2 探针 1-2 秒只数 behind（19），**看得见 commit 看不见表**——速度是假象。G-07 把表集合变成探针的直接对象：

```
S2 日探针（现）：fetch → rev-list --count → behind 数
S2+G-07（升级）：+ git show origin/main:canonical_tables.txt | 集合 diff → 新表名逐个判决（秒级，无 pull 需求）
```

S1 周验基线已有「S1-canonical 漂移」项（计数比对，477 基线）；G-07 把它从**周频提升到日频**、从**计数提升到逐表集合判决**。挡板阈值（behind>300）不变——G-07 不依赖 pull，先于 S4 挡板工作。

## 4. W17 验收线（可度量 + 突变留痕，沿用 brief §3 风格）

| # | 验收度量 | 达标线 |
|---|---|---|
| 1 | 对 2026-09-18 真实事件回放 | +7 表全部 BROKEN 判出，含来源迁移号与双目录归因 |
| 2 | 突变证据三向 | +假表→红；带 citing change→绿；无关行编辑→零误伤（selftest 子命令可重放） |
| 3 | 集成 S2 | 探针脚本一日一跑输出机读 JSON，本次事件类检测延迟 ≤1 个探针周期 |
| 4 | 首个 citing change 立案 | 对 +7 表（至少 leasing_policy/unit_pricing 两族）立语义层 change：登记 or 显式不入域裁决 |

## 5. 范围红线

- 不做表结构级（列/枚举）漂移——那是 G-05 effect 锚与 Identity 值域的地盘，G-07 只守**表集合边界**。
- 不自动改语义模型——citing change 立案与人审在 W17 流程里，门只负责红。
- 不动主仓——S5 归档律：一切对主仓的诉求走 openspec change。
