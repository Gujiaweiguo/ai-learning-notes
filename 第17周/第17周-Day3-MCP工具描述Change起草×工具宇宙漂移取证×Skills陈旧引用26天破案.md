# W17-D3 · MCP 工具描述 Change 起草（t01）× 工具宇宙漂移取证 × Skills 陈旧引用 26 天破案

> 开发期 · Week 17「边界治理落地周」（2026-09-23 周三，W16-D7 定轨第 6 项 + w14-plus W16+ 方向 2 落地入口）
> Today's Question：**工具描述到底是给谁看的资产——给研发自己，还是给 AI 消费方？如果是后者，为什么它至今没有任何治理头？**
>
> 📌 计划来源说明：w14-plus 无 W17 逐日条目（仅粗粒度方向 2「ontology → capability/MCP tool 描述的生成……走 openspec 变更流程提交第一份 AI 侧 change」），按解析规则回落 learning-plan.md 周节奏表（周三 = 推进当日对象）+ W16-D7 Review §7 定轨表第 6 项（MCP 工具描述 change，后置条件「基线稳定」）+ W17-D2 明日连接（「后置条件全满足：基线稳定 + cited 22/22，第一份 AI 侧 change 可以开写」）。第 5 次建议 Jason 在 w14-plus 补 W17 一行指向（W15-D7/W16-D7/W17-D1/D2 已提）。
> 配套实验：`第17周-Day3-MCP工具描述Change起草×工具宇宙漂移取证×Skills陈旧引用26天破案.ipynb`
> 产出工件：`semantic-model/changes/_drafts/t01-mcp-tool-semantic-description-governance.md`（提案 DRAFT，证据链四条全部今日实考）

---

## 0. 今日开发目标

① 对 lnkcre MCP 工具体系完成首次语义侧全景取证（29 工具清单 + 描述画像 + 权限映射对齐核验）；② skills 技能包 × 注册工具交叉验证（w14-plus 方向 2 的第一问：语义层与工具面的接触点质量如何）；③ 后置条件核验（基线稳定：probe origin 集合指纹 = w40 基线）；④ t01 提案 draft 落盘（Why 四链 / What 四条 / 验收线四条 / OQ 三问），周日 Review 裁决升格立案。

## 1. 完成事实①：工具宇宙取证——29 工具画像与 26 天陈旧引用破案

**工具宇宙清单**（RegisterTool 调用扫描，tools.go 9 / extended_tools.go 10 / workflow_definition_tools.go 10 = 29 唯一名）：品牌/客户主数据 4、租赁链路 6（草稿三件套+报价+合同查询+铺位可租）、审批高风险对 2（approve/reject，confirm-token 语义）、工作流查询 2、应收/押金/报价单查询 3、点位申请对 2、workflow_definition 家族 10。**权限映射 29/29 一一对齐**（toolPermissions 与 canonical functions catalog 对齐，auth_mapping_test 双向覆盖）——主仓在「权限 ↔ 工具名」这一层治理是完备的。

**破案：skills 陈旧引用 26 天**。交叉验证（4 件技能包 × 29 注册工具）发现 **4 处漂移、2 件技能包断链、3 处在 required 位置**：

| 技能包 | 陈旧引用 | 位置 | 事实 |
|---|---|---|---|
| mi-quotation | `generate_document` | **required** | 已移除（fbacc0f1，2026-08-28，"dead tools"） |
| mi-quotation | `convert_quotation_to_contract` | optional | **从未注册**（29 工具全集无此名） |
| mi-service-triage | `create_service_request` | **required** | 已改名 → `create_spot_application`（D23 Decision 1） |
| mi-service-triage | `query_tickets` | **required** | 已改名 → `query_spot_applications` |

时间线考古：skills 落地 2026-06-15（1362c508）后**零更新**；改名/移除发生在 2026-08-28（fbacc0f1 write-path hardening）——**26 天无人发现**。mi-quotation 与 mi-service-triage 是教数字员工「报价转合同」「服务工单分诊」的课程，课程教的工具 3/4 不存在。

**Today's Question 的回答**：工具描述（和 skills 引用）是**给 AI 消费方看的声明性资产**——tools/list 的 description 是 LLM 选错或选对工具的唯一依据，skills 的 required/optional 是编排数字员工的课程表。正因为消费方是机器，它的腐烂**没有人疼**：人读的 API 文档烂了会有工单，机器读的描述烂了只有静默的失败（技能走不通 → 数字员工降级 → 没人知道为什么）。主仓并非没有治理意识——toolPermissions 那一层有 canonical catalog 对齐 + 双向覆盖测试，**同一份工具面，权限层有门、语义层裸奔**。这不是态度问题，是「谁的资产」没定清楚：权限是安全资产（有人负责），描述/技能引用是语义资产（无人认领）——t01 的第一主张就是把这份资产登记进注册表并装上门。

## 2. 完成事实②：t01 提案 draft 落盘（第一份 AI 侧 change）

`changes/_drafts/t01-mcp-tool-semantic-description-governance.md`，四条 Why 全部今日实考：

1. **Skills 漂移活事件**（上表，机器可复核：交叉验证脚本在 ipynb 实验②）；
2. **描述是无治理资产**：29 条全英文硬编码 Go 字符串（36–172ch，中位 102），仅 1/29 含中文——中文产品的 AI 操作手册是英文的，且与 SoT 术语（12 模块 / 102 子功能 / 195 capability / 80 模块级 aliases）零对齐（用户说「点位申请」，描述写 spot application）；
3. **表宇宙有门，工具宇宙没有**：G-07 已证明「集合+基线+引用承认」模式可让漂移当天现形；工具宇宙没有清单没有基线，改名的代价已经付过一次（26 天）；
4. **权限映射模式可平移**：toolPermissions 的「注册表 + catalog 对齐 + 双向覆盖测试」三件套照搬到「语义挂点 ↔ 工具名」，零新概念。

What 四条：① `mcp-tool-registry.yaml` 29 条登记（module/capability/permission_code/context/entities/risk_level）；② skills 引用覆盖门（照抄 auth_mapping_test 双向模式，**首个动作即修复 4 处漂移**）；③ 描述双语化 v2（生成器在语义层，人工裁决后替换——生成不豁免裁决）；④ 描述漂移检测（Go 源码 ↔ registry diff）。验收线 4 条全部可度量（漂移 4/4 修复、registry 29/29、改名演练当次 RED、双语 29/29）。OQ 三问：registry 归属（倾向 lnkcre 仓内——26 天漂移的根因正是声明资产离执行面太远）；v1 只校验不生成；`convert_quotation_to_contract` 登记还是移除（需主仓业务表态）。

**与 g0x 的关系**：g0x Impact 段预言「MCP 工具描述生成获得表宇宙稳定性的机器判定依据」——今日 probe 实跑核验后置条件成立（origin 499 = 基线指纹一致，30 commits 零新表），t01 是该预言的兑现件，不是新开的战线。

## 3. ipynb 实验要点（与 md 差异化，verify 全绿）

① **工具宇宙提取与画像**：Go 源码 RegisterTool 正则提取（断言 29），描述长度分布 + 中英标注可视化（断言仅 1 条含中文）；② **skills 交叉验证复现**：yaml 解析 × 注册工具集合，断言漂移恰好 4 处 / required 3 处，漂移矩阵图 + git 考古（06-15 → 08-28 → 09-23 时间线）；③ **术语对齐度量**：ontology 80 条模块 aliases × 29 条英文描述的直接对齐率（断言≈0，漂移的量化面），并渲染 2 个双语描述样例（registry 模板：中文意图 + aliases + 风险等级）对照现状英文；④ **覆盖门模拟**：temp 目录注入 D23 式改名事件，复刻 auth_mapping_test 的双向覆盖逻辑——无门 26 天盲区 vs 有门当次 RED 的检测延迟对比。

## 4. 明日连接（W17-D4）

t01 证据链已完成，明日转入 g0x 受理观察窗的周中巡检 + **W18 Rule/Policy 显式化预研开工**（D2 锁定的输入范围：leasing-policy 版本不可变链 + unit-pricing 授权约束链——从 mi 代码抽第一批 Rule 语料，为 W18 主菜备料）；t01 的 OQ-1（registry 归属）周日 Review 裁决后升格 changes/ 立案。另：probe 显示 LnkChatBI behind 0→18（首次出现主仓侧活动），纳入周一 W40 digest 议题；lnkcre behind 30 但表宇宙零漂移，R-wave 延续观察。

## 5. 理解变化（保留学习期传统）

- **以前以为**：MCP 工具描述是「文案」，写清楚就行，属于代码注释级别的卫生问题。**现在知道**：描述是 AI 消费方的**接口契约**——tools/list 是 LLM 的选型菜单，skills.required 是数字员工的课程表；契约腐烂没有编译错误、没有测试失败、没有工单，只有静默降级。机器消费的资产比人消费的资产**更需要**注册表和门，因为没有人会替机器抱怨。
- **以前以为**：语义层接入 mi 真实栈的第一步是「生成」——把 ontology 变成工具描述产出去。**现在知道**：第一步是「校验」——先证明存量工具面与语义资产的对齐关系（29/29 登记、4/4 漂移修复、改名演练 RED），才有资格谈生成（t01 OQ-2 把双语化放 v2 的理由）。这与 G-05 v0.2 的顺序律同构：**先零误伤，再新增检出**；也与基线升级程序同构：**先让漂移 RED 留档，再裁决重冻结**。
- **以前以为**：26 天没发现的漂移说明主仓纪律差。**现在知道**：恰恰相反——主仓在权限层（安全资产）的治理是完备的（canonical catalog + 双向覆盖测试 + spec 归档），漂移只发生在**无人认领的语义资产**上。治理的盲区不在技术，在所有权：谁的资产，谁装门。t01 的 OQ-1（registry 放 lnkcre 还是语义层）本质是在给这份资产找主人。
