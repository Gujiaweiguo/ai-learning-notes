# W17-D2 · 五族 Citing 逐族立案（22 表债务清算 cited 0→22）× G-05 v0.2 expect 定界签名

> 开发期 · Week 17「边界治理落地周」（2026-09-22 周二，W16-D7 定轨第 3 项 + 第 5 项）
> Today's Question：**五族全部裁决「入域登记」，一个「显式不入域」都没有——这是真裁决还是橡皮图章？**
>
> 📌 计划来源说明：w14-plus 无 W17 逐日条目（仅粗粒度方向），按解析规则回落 learning-plan.md 周节奏表（周二 = 推进当日对象）+ W16-D7 Review §7 定轨表第 3 项（五族 22 表逐族 citing change，验收线「五 change 落盘，canonical 门 cited 数 0→N」）与第 5 项（G-07 v0.2 expect 定界签名）；W17-D1 明日连接指定今日启动 leasing-progress → indicator-target → … 逐族立案。第 4 次建议 Jason 在 w14-plus 补 W17 一行指向（W15-D7/W16-D7/W17-D1 已提）。
> 配套实验：`第17周-Day2-五族Citing逐族立案×22表债清算×G05Expect定界签名.ipynb`

---

## 0. 今日开发目标

① 五族 22 表逐族核（迁移 DDL/spec/包/ontology 挂点/Context 先例五路证据）→ 逐族裁决入域 or 显式不入域；② 每族一个 citing change 落盘 `changes/citing-*`（g0x What-5 首批执行对象）；③ canonical 门双基线复验（w39 透镜 cited 0→22 + w40 执勤 ±0）+ w40 基线头部账本追加清算记录；④ G-05 v0.2：expect 子串 → 定界签名（治 W16-D2 实锤的「扩名不改名」0% 检出盲区），15 锚复跑必须全绿 + 突变证据更新。

## 1. 完成事实①：五族逐族核与裁决总表（今日主交付）

22 表五路证据全部核毕（四迁移 DDL 直读 + openspec specs 4 份 + 包结构 4 个 + ontology 挂点 + W14-D5 Context 先例），**五族全部裁决「入域登记」，零「显式不入域」**：

| 族 | 表数 | 迁移 | Context 裁决 | 裁决要点（被排除的替代项） |
|---|---|---|---|---|
| leasing-progress（stage 4 + progress 5） | 9 | 000234 | **03 Leasing Pipeline** | 全新业务面（任务驱动+事件消费+审计留痕）；本体挂点招商管理.招商计划；**V1/V2 表零触碰——本族是 V3 执行面，不是 V2 改造** |
| unit_leasing | 3 | 000234 | **03 Leasing Pipeline** | 铺位×节点跟踪容器（实例层）。unit 锚定但归 03 不归 01：**进度是过程不是资产属性**（01 的先例=unit_pricing_versions 价格属性） |
| indicator-target | 3 | 000233 | **17 BI & Analytics** | 目标值层是指标语义的**目标侧**，非新指标域；核证：target_indicators 种子与 analytics_metrics（17 锚表）**同码对齐**（lea_signed_area_period），caliber_note 直引 leasing-achievement-rate-caliber spec。年度载体 asset_annual_indicators 的 D5 启发式归属（06）不动——存量重裁决不是本案范围 |
| leasing-policy | 3 | 000227 | **03 Leasing Pipeline** | 政策=招商条件报批的事实层（壳/版本/生命周期）；本体 aliases 直接含「租赁政策/租决」；content_hash 提交不可变 + workflow 挂接是 W18 Policy 显式化的第一批完整样本 |
| unit-pricing | 4 | 000227+000229 | **01 Asset Foundation** | **跟随存量锚 unit_pricing_versions（D5 归属）保持族内一致**：4 表全部服务于 versions 的批量生成与授权校验；跨域引用（leasing_policy_versions 为定价来源）登记在 relationship 不改归属。本体双挂点如实登记：资源定价（资源管理）+ 一铺一价（招商管理） |

**Today's Question 的回答**：

> 裁决的牙齿不在结果分布，在**依据链里被显式排除的替代项**。今天每个「入域」都踩死了一个反面：unit-pricing 归 01 不是 03（族内一致 > 语义直觉）；indicator-target 归 17 不是 06（同码对齐证据 > D5 启发式噪声）；leasing-progress 不碰 V1/V2（三代并列，不是改造）。五族全入域的真实原因是**上游纪律好**——W39 digest 已预判，这 22 表全部带 spec、带验收链、带零数据纪律，没有一张实验残留表。换句话说：**门的 RED 判决本身就是筛子**，昨天 BROKEN 的 44 条判决里没有一条值得「显式不入域」豁免。裁决会不会变橡皮图章，要看未来出现边缘表（实验 schema、临时看板）时「不入域」选项是否真的敢用——今天的全入域是裁决与上游质量的一致，不是裁决缺席。真正的验证：**每个 Context 数字都有出处，每条关系都有 FK/设计条款背书**（详见五个 change 的 What 段）。

## 2. 完成事实②：五 change 落盘 + 双基线复验 + 账本闭环

**五案落盘**（`changes/` 非 `_drafts`，open change 即生效）：
`citing-leasing-progress`（9表）/ `citing-unit-leasing`（3表）/ `citing-indicator-target`（3表）/ `citing-leasing-policy`（3表）/ `citing-unit-pricing`（4表）——每案含 Why（五路证据）/ What（Context 归属+表语义+关系+术语）/ 边界声明 / Impact / 证据行号。**模型 yaml 一行未动**：snapshot 是结果，change 是过程（v0.2 组装时合并 Entity/Relationship/术语三层）。

**canonical 门双基线复验**（实跑）：

| 透镜 | 基线 | 判决 | 关键数 |
|---|---|---|---|
| 债务清算度量 | w39（477） | **GREEN** | added 22 / **cited 22** / leaked 0 / broken 0（昨日 digest 取证时刻 cited 0 / leaked 22 / broken 44） |
| 执勤基线 | w40（499） | **GREEN** | ±0（表宇宙稳定） |

每表判决均带出生证明（如 `leasing_stage_templates ← pg:000234@L53`、`target_indicators ← pg:000233@L36`）。**实验①复算暴露的口径细节**：严格词边界口径下，g0x What-5 族表括注「unit-pricing（含 price_authority_constraints）」本身已构成一次 citing——09-21 收盘口径实为 cited 1/21 而非 0/22（digest 记录的 cited 0 是取证时刻值，先于 g0x 落盘）。门的裁决只认文本不认意图：**族名括注也是 citing**，这正是「落在 changes/ 才算」条款的字面执行，也反证了五案显式登记的必要性——碰巧被括注≠被裁决。**w40 基线头部账本式追加清算记录**（不重写历史行）：carrying-debt 清零（22/22），待周日 digest 复核归档。**g0x 提案验收线第 5 条达标**（4/5→**5/5**），What-5 五族裁决表由「待裁决」更新为终态，Open Question 2 关闭——W18 Rule 显式化输入范围随之确定。

## 3. 完成事实③：G-05 v0.2 expect 定界签名（含一次首版翻车）

**升级动机**（W16-D2 实验遗留）：锚点三元组 `(file, line, expect)` 的 expect 是子串匹配，「扩名不改名」（`StatusDraft` → `StatusDraftLegacy`）对子串不可见——0% 检出，纯盲区。

**首版翻车（今日最大的坑）**：v0.2 首版照搬 Identity 门的两侧全边界（`(?<!\w)pat(?!\w)`），15 锚复跑 **7 个假 BROKEN**——全部是 expect 以 `(` 结尾的函数签名（`func ValidateTransition(`、`func (r *Repository) CreateTx(`…）：右缘边界把**后随实参**（`from`、`ctx`）误判成扩名。逐锚取证（7/7 在登记行号上原样存在）后修正：**边界只加在 pattern 边缘本身是词字符的一侧**——`StatusDraft` 右缘是词字符→加界（防后缀扩名）；`func Foo(` 右缘是 `(`→不加界（`(` 后跟实参是合法命中）。修正后 **15/15 GREEN**，且 Identity 门语义不受影响（其锚点全是纯标识符，两种边界等价，26/26 复跑绿）。

**突变证据更新**（定轨第 5 项验收线，四场景对照旧子串）：

| 场景 | 旧子串 | v0.2 定界 | 判读 |
|---|---|---|---|
| 未篡改 | OK | OK | 零误伤 |
| 扩名（后缀 Legacy） | **OK（假绿）** | **BROKEN** | 盲区闭合 |
| 扩名（前缀 X） | **OK（假绿）** | **BROKEN** | 盲区闭合 |
| 改名 | BROKEN | BROKEN | 原有能力保持 |

W16-D2 tamper 矩阵的「扩名 0% 检出」断言就此翻案：**0% → 100%**。教训固化：**升级验证器的第一跑必须先对存量全绿，才有资格谈新增检测力**——不引入假阳性不是性能指标，是入场资格（与 W16-D2「误报率低到没人想关掉它」同一条定律的另一半）。

## 4. ipynb 实验要点（与 md 差异化，verify 全绿）

① **债务透镜实验**：importlib 直载 canonical_drift_ci，read_citing/word_rx 复算「仅 g01/g0x 在册」vs「五 citing 落盘后」的判决翻转——并复算出昨日收盘真实口径 cited 1（g0x 族表括注 price_authority_constraints 的词边界命中，digest 的 0 是取证时刻值），断言 cited_after==22 且 leaked==0；② **五族×迁移归因矩阵**：四份 .up.sql 直读 CREATE TABLE 正则提取，与双基线 diff 的 22 表全量对账（断言并集相等）；③ **Context 重分布图**（NotoSansCJK）：03 Leasing 40→55 / 17 BI 70→73 / 01 Asset 36→40；④ **定界签名 tamper 矩阵**：temp repo 注入六场景（含 `(` 右缘合法命中防假阳性回归——首版翻车教训固化为断言），旧子串 vs 新定界对照，2/2 盲区闭合 + 零误伤断言。

## 5. 明日连接（W17-D3）

定轨剩余项启动：**第 6 项 MCP 工具描述 change（提案 draft）**——后置条件「基线稳定」昨日已满足、今日 cited 22/22 后表宇宙语义层就绪，ontology → capability/MCP tool 描述生成的第一份 AI 侧 change 可以开写（w14-plus W16+ 方向 2 的落地入口）；g0x 受理观察窗持续开启（下周一首查）；W18 Rule/Policy 显式化输入范围今日锁定（leasing-policy 版本不可变链 + unit-pricing 授权约束链是前两批语料）。

## 6. 理解变化（保留学习期传统）

- **以前以为**：「入域登记」= 把表名写进语义模型 yaml。**现在知道**：登记的载体是 change（过程留痕），yaml 只是 snapshot（结果）——先改 yaml 是把结果当地过程，半年后没人说得清哪张表是哪天谁的裁决；先落 change，门的 cited 判决才有可复核的依据链。这也解释了为什么 G-07 门设计成「yaml 有痕迹只能降级 DRIFTED，不能豁免泄漏」。
- **以前以为**：词边界匹配是「更严格」的匹配，严格=更安全。**现在知道**：边界加在哪一侧比加不加更重要——两侧全边界在 7 个合法锚点上制造假 BROKEN，边缘条件定界（只在词字符边缘加界）才是「防扩名」的精确表达。**验证器升级的顺序律：先证明零误伤，再证明新增检出**。
- **以前以为**：22 表全入域说明「显式不入域」是摆设条款。**现在知道**：条款的价值在威慑与容量，不在使用频率——正因为「不裁决即违规」悬在头上，上游 55 commits 的波次里没有一张表是随手建的（全部带 spec/验收链/零数据纪律）。**好的治理条款像好的安全带：系着的时候感觉不到它，但没有它的事故都不会进统计**。
