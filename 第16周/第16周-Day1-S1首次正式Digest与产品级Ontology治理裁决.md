# W16-D1 · S1 首次正式 Digest × 产品级 Ontology 家族治理裁决 × G-01 提案起草

> 开发期 · Week 16「治理地基 + 消费面事实化」（2026-09-14 周一，W16 brief 工作项 ④ + W15-D7 复盘追加件）
> Today's Question：**「多一份 ontology」为什么不是冗余而是事故苗头——判定消费副本与双 SoT 的分界线是什么？**
>
> 📌 计划来源说明：learning-plan-w14-plus.md 无 W16 逐日条目（仅粗粒度方向），但其 W15-D6 条目明确定交付「W16 开发 brief」作为 W16 安排——本日按 `semantic-model/w16-dev-brief.md` 工作项 ④（"S1 首次正式 digest（周一 D1）+ 重点核查第二个 ontology.yaml"）执行；brief W16 范围 2026-09-14~09-20 与本周完全重合。建议 Jason 在 w14-plus 中补记一行指向该 brief，使计划链显式闭合。

---

## 0. 今日开发目标

① S1 首次正式 digest：三仓 fetch + pull + spec 增量 + wave 主题 + P0-P3 评级 → `semantic-model/sync/digest-2026-W38.md`；② **重点核查** docs 仓第二个 ontology.yaml（`30-products/lnkchat/ontology.yaml`）是消费侧副本还是双 SoT 事故苗头，并对"产品级 ontology ×4"（D7 登记）逐件裁决；③ G-01 治理头 change 提案起草（范围扩入第五件同宗：产品级 ontology 治理关系声明 + 计数口径）；④ ipynb 量化验证：五件 ontology 指纹/结构/重叠矩阵 + 同名异义 + 治理门模拟。

## 1. 完成事实①：S1 首次正式 digest（2026-09-12 → 09-14）

| 仓 | 拉取前 behind | pull 后 | 提交 | 关键发现 | 评级 |
|---|---|---|---|---|---|
| lnkcre | 15 | ✅ bd00eb6a | 15（9/12~9/13） | baseinfo 主数据纵深：品牌/渠道档案+**变更台账**+导入导出+业态字典 UI；spec 306→**311**（+4 新/2 改）；无 R6、无 analysis 触动 | P2 |
| docs | 63 | ✅ | 63（8/28~9/12） | **CAO 受治理自主进化章程生效 + R001 Controller Spike + tool routing/standalone tool invocation**（工具级治理在产品侧成形）+ langchat→lnkchat 六目录迁移；**SoT 指纹 `bf550bc24de66813` 复验未漂移** | **P0**（对 W17 ⑥） |
| LnkChatBI | 14 | ✅ | 14 | **governed datasource framework 归档，含 domain-semantic-pack-contract**——我们语义包的对接契约已定形 | **P0**（对 W16-③） |

两个 P0 都不动 W16 批次：前者是 W17 ⑥（MCP 工具描述 change）的需求侧证据正在落地——tool routing/autonomous controller 都要吃"工具与能力的机器可读描述"，正是 plan 方向②；后者把 W16-③ 的 pack 重出从"修订示例#2"升级为"修订 + **对齐 domain-semantic-pack-contract**"，S6 回执新增契约对照项。**结论：无批次对调，挡板未触发（max behind 63 < 300）。**详见 digest-2026-W38.md。

## 2. 完成事实②：产品级 ontology 家族治理裁决（主交付物）

**核查对象**：docs 仓全部 5 件 ontology（1 SoT + 4 非SoT），逐件解析+指纹+出身追溯：

| 文件 | 指纹 | 模块/子功能/cap | 裁决 |
|---|---|---|---|
| business-ontology.yaml（SoT） | `bf550bc24de66813` | 12/102/195 | 治理头缺失（G-01 主体） |
| 30-products/lnkchat/ontology.yaml | `0a74edf9be475ecc` | 8/26/41 | **产品级本体（live）**，非副本非双 SoT；治理关系未声明 |
| out/prd/LnkChatBI/output/ontology.yaml | `0240e95e2f9a84a1` | 8/12/13 | 产品级本体（live，源=域知识.md） |
| out/prd/lnkreport/output/ontology.yaml | `973f3b24a0e26d16` | 8/30/67 | 产品级本体（live，源=代码探查+45 specs） |
| 90-legacy/…/out-prd-langchat/…yaml | `e17ad8395baf8386` | 8/18/31 | lnkchat 本体冻结快照，**未标记 frozen** |

**Today's Question 的回答——判定框架**：

> 消费副本 vs 双 SoT 的分界线**不在内容相似度，在两条独立证据**：
> ① **内容证据（管辖域重叠度）定性质**：SoT × 四产品件模块集合 Jaccard = **0%**（ipynb §2 复算）——既不是 SoT 的副本（无派生内容），也不是同域竞争 SoT（管辖域不重叠：SoT 管 MI CRE 业务域，产品件管 AI 产品族域）。
> ② **治理证据（关系声明）定风险**：反向引用 grep 双向 **0 处**——派生关系、维护者、管辖边界全部零声明。
>
> 「内容互不相同」既不等于「分叉」（D7 已裁决非分叉），也**不等于「无害」**：苗头的具体路径有三条实证——**(a)** 五件同名 ontology.yaml 并存，消费方（我们的语义包生成、未来的工具描述生成）选件无机器依据；**(b)**「数据源管理」已在 LnkChatBI 与 lnkreport 两件中**同名异义**（内容不相交，ipynb §3）；**(c)** legacy 与 live 模块集 100% 同名但内容已演化（18→26 子功能），**复制演化无指纹链**——这个家族是靠拷贝生长的，拷贝就是分叉的前置态。

**裁决**：`30-products/lnkchat/ontology.yaml` = **平行产品本体家族的 live 件**。今天无害（0% 重叠），明天危险（零声明 + 拷贝式演化 + 同名异义已出现）。处置：并入 G-01，不另立案。

## 3. 完成事实③：G-01 change 提案起草（W16-① 启动）

落盘 `semantic-model/changes/g01-ontology-governance-header/`（proposal.md + reconciliation.md，openspec 格式、状态 draft 待立案）：

- **SoT 五键治理头**：version / status / maintainer / change_process + **counting_caliber（计数口径声明——883/963 双数教训固化为第五键）**；
- **四产品件最小治理块**：authority_scope / status（legacy→frozen）/ custody / derives_from / relation_to_mi_sot；
- **家族登记簿 registry.yaml**：五件指纹 + 管辖域 + 状态，作为 SoT 指纹链锚点（S1 digest 周验基线）；
- 对账报告 E1-E5 证据件齐备（0% 重叠、100% 同名演化、同名异义、双向零引用、SoT 两度指纹一致）；
- 待主仓裁决三点：立案载体（lnkcre openspec vs docs evidence-chain）、registry owner、是否在 lnkcre 建引用 spec。

验收对齐 brief：本周底线"立案受理 + 对账报告"——对账报告今日已成，提案待 Jason/主仓立案。

## 4. ipynb 实验要点（与 md 差异化，全绿通过 verify）

§1 五件结构指纹表 → §2 模块重叠矩阵热力图（0% / 100% / 6.7% 三处关键格子）→ §3「数据源管理」同名异义钻取 → §4 legacy→live 演化差集 → §5 **治理门模拟**：以真实 registry 为基线，模拟"拷贝产品件+加一个别名"的静默篡改——无门时零告警，有门（指纹校验）时当场抓获。图四张：`w16d1_structure_compare.png`、`w16d1_overlap_heatmap.png`、`w16d1_homonym.png`、`w16d1_gate_demo.png`。

## 5. 明日连接

- **W16-D2：G-05 effect-registry 代码锚点 + frozen CI**（brief 工作项 ②）——5 类冻结 effect 逐条加 file:line 锚点（消费 W14-D4 对账清单），本地演示"改 frozen effect 不带 change 即红"；今天的 registry/指纹链是同一治理模式的 docs 侧兄弟件。
- S2 日探针明日起每日开发前执行；G-01 提案等主仓立案窗口。
- 登记待查（P2）：trade/industry 字典表是否产生新 canonical 表/术语 → W16-③ Identity 登记时一并核。

## 6. 理解变化（保留学习期传统）

以前以为：SoT 唯一性问题的形态是"两份内容相同的文件打架"（副本/分叉二选一）。现在知道：**更常见的形态是"管辖域不重叠但关系零声明的平行家族"**——它不违反 SoT 唯一性条款（没有同域竞争），却制造了同样的事故面（选件无据 + 拷贝演化无链）。治理头的价值因此不是"声明谁是老大"，而是**把"谁管什么、从哪来、谁维护"从知情者脑中搬到机器可校验的文件头**——这和 BCM effect-registry 的冻结声明、chatbi 白名单的 citing action 是同一个模式的三次实例化。
