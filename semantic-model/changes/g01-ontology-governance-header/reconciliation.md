# 对账报告：ontology 家族现状审计（G-01 proposal 证据件）

> 审计时间：2026-09-14（docs 仓已对齐 origin/main，2026-09-12 HEAD）
> 方法：PyYAML 结构化解析 + sha256_16 指纹 + 模块集合 Jaccard + git --follow 出身追溯；复算过程见 `第16周/第16周-Day1-*.ipynb` §1-§4。
> **2026-09-17 深化（W16-D4）**：新增 §6 机器可复核证据链（`evidence/claims-2026-09-17.json`，仿 docs 仓 40-delivery evidence 范本）——C1-C5 五断言今日全部复验 PASS；受理状态：**未受理**（docs behind 15，增量 commits 零 ontology/governance 主题，立案窗口未开启，挂起至周日 Review 裁决是否并轨 W17）。

## 1. 现状清单（5 件）

| # | 文件 | 指纹 | 模块 | 子功能 | capability | 顶层键 | 头部治理信息 |
|---|---|---|---|---|---|---|---|
| 1 | config/ontology/business-ontology.yaml | `bf550bc24de66813` | 12 | 102 | 195 | modules | **无**（零声明） |
| 2 | 30-products/lnkchat/ontology.yaml | `0a74edf9be475ecc` | 8 | 26 | 41 | scope_isolation / out_of_scope / channels / mcp_contract / modules | 注释级（Source/Scope/Coverage，人读有效、机器无效） |
| 3 | out/prd/LnkChatBI/output/ontology.yaml | `0240e95e2f9a84a1` | 8 | 12 | 13 | modules | 注释级（同上） |
| 4 | out/prd/lnkreport/output/ontology.yaml | `973f3b24a0e26d16` | 8 | 30 | 67 | modules | 注释级（同上） |
| 5 | 90-legacy/2026-07-31-pre-document-control-plane/out-prd-langchat/output/ontology.yaml | `e17ad8395baf8386` | 8 | 18 | 31 | modules | 注释级；**无 frozen 标记** |

## 2. 量化证据

| # | 证据 | 数字 | 含义 |
|---|---|---|---|
| E1 | SoT × 四产品件模块集合 Jaccard | 全部 **0%** | 产品件不是 SoT 副本、管辖域不重叠 → 非双 SoT |
| E2 | legacy × lnkchat-live 模块集合 Jaccard | **100%**（指纹不同，18→26 子功能 / 31→41 capability） | 复制演化无链：同族拷贝生长，历史件无标记 |
| E3 | 「数据源管理」同名模块 | LnkChatBI 与 lnkreport 各一，子功能/能力不相交 | 同名异义已发生：选件无机器依据 |
| E4 | 反向引用 grep | 产品件对 SoT 引用 **0 处**；SoT 对产品件登记 **0 处** | 治理关系双向零声明 |
| E5 | SoT 指纹复验（W15-D3 → 本次） | `bf550bc24de66813` 两度一致 | SoT 内容未漂移——治理头缺失是"未出事"，不是"已治理" |

## 3. 裁决（digest-2026-W38 §5 同文）

**性质**：平行产品本体家族（AI 产品族域），非消费副本、非双 SoT；风险 = 治理关系未声明 + 拷贝式演化 + 同名异义。
**判定框架**：内容证据（管辖域重叠度）定性质，治理证据（关系声明）定风险——「内容不同」既不等于「分叉」，也不等于「无害」。

## 4. 与 G-01 原始缺口对应

| G-01 原始表述 | 本提案覆盖 |
|---|---|
| ontology 无治理头 | 五键治理头（proposal §What-1） |
| 语义漂移无机器告警 | registry.yaml 指纹链 + S1 digest 周验（§What-3） |
| （W15-D6/D7 扩入）产品级 ontology 治理关系未声明 | 产品件最小治理块 + authority_scope（§What-2） |
| （W15-D3 教训）计数口径无声明 | counting_caliber 第五键（§What-1） |

## 5. 待立案裁决问题

1. 立案载体：lnkcre openspec change（S5 归档律现行载体）vs docs 仓自身 evidence-chain（docs(governance) 提交线）——目标文件全在 docs 仓，载体由主仓定夺。
2. registry.yaml 的 owner（mi-domain-owner 兼任 vs 家族各件 custody 自管）。
3. 合入后是否同步在 lnkcre 侧建引用 spec（ontology-governance）以纳入其 openspec 检查面。

## 6. 机器可复核证据链（2026-09-17 深化，W16-D4）

仿 docs 仓 `40-delivery/lnkchat/evidence` 范本：每断言一条结构化记录（复核命令 / 期望 / 实测 / 日期 / 验收线），工件 `evidence/claims-2026-09-17.json`，主仓受理时可直接复算：

| ID | 断言 | 复核结果 |
|---|---|---|
| C1 | SoT 指纹三度一致（W15-D3→W16-D1→今日） | `bf550bc24de66813` PASS |
| C2 | 五件家族指纹与 9/14 审计一致（docs +15 commits 零漂移） | 5/5 PASS |
| C3 | 产品件对 SoT 反向引用仍为 0 | 0 处 PASS |
| C4 | 近 15 增量 commits 无 G-01 受理记录（立案窗口未开启） | 0 处 PASS（状态=未受理） |
| C5 | 同名异义『数据源管理』两件并存（选件歧义未消） | 1 处 + 3 处 PASS |

**深化理由**：原报告的 E1-E5 是一次性审计快照（人读表格）；evidence-chain 把它们变成**可重放的断言集**——与同日完成的锚点周验预演同构：证据的价值不在「今天是对的」，在「任何人任何时候可复核且结果可比对」。受理后本节与 registry.yaml 指纹链合流，成为 S1 周验的 G-01 族检查项。
