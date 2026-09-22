# Change Proposal: MCP 工具语义描述治理（t01 · 工具宇宙注册表 + Skills 引用门）— DRAFT

> 起草：2026-09-23（W17-D3，W16-D7 定轨第 6 项「MCP 工具描述 change（提案 draft）」启动）。
> 状态：**draft**（证据链已机器复核完毕；立案载体明确为 lnkcre openspec change——本案目标文件全部在 lnkcre 仓，不存在 g0x Open Question 1 的跨仓载体之问。升格 changes/ 立案待周日 Review 或 OQ-1 裁决）。
> 定位：w14-plus W16+ 方向 2「语义层接入 mi 真实栈：ontology → capability/MCP tool 描述的生成」的第一份 AI 侧 change；g0x What-6 Impact 段「MCP 工具描述生成获得表宇宙稳定性判定依据」的兑现。
> 后置条件核验（2026-09-23 实跑）：canonical 基线 w40（499 表，指纹 7995cb4839ddc5b1）与 origin/main **集合指纹一致**（sync/probe.py verdict OK，30 commits 零新表）+ 五族 cited 22/22（W17-D2 清算）——「基线稳定」满足。

## Why（为什么是工具描述、为什么是现在）

四条证据链，前三条今日实考取证：

1. **Skills 工具引用漂移（活事件，26 天无人发现）**：`backend/internal/mcp/skills/` 4 件技能包（2026-06-15 commit 1362c508 落地后零更新）中 2 件引用了**不存在或已改名**的工具，共 4 处，其中 3 处在 `required` 位置（技能按此编排无法执行）：
   | 技能包 | 引用 | 位置 | 事实 |
   |---|---|---|---|
   | mi-quotation.yaml | `generate_document` | **required** | 已移除（fbacc0f1 2026-08-28 write-path hardening "dead tools"） |
   | mi-quotation.yaml | `convert_quotation_to_contract` | optional | 从未注册（29 工具全集无此名） |
   | mi-service-triage.yaml | `create_service_request` | **required** | 已改名 → `create_spot_application`（D23 Decision 1） |
   | mi-service-triage.yaml | `query_tickets` | **required** | 已改名 → `query_spot_applications` |
   漂移窗口：2026-08-28（改名日）→ 今日 = **26 天**。同一次 hardening 提交里，`toolPermissions` 映射同步更新且有 `auth_mapping_test.go` 双向覆盖测试护栏（spec `mcp-tool-permission-mapping`：Registered MCP tools SHALL have a permission mapping entry）；**技能包引用零校验**——同一个工具面的两份声明性资产，一份有门，一份裸奔。
2. **工具描述是 AI 的唯一 UI，但它是无治理资产**：29 个工具的 description 全部是硬编码在 Go 源码的英文字符串（36–172 字符，中位 102），质量分布无标准——`approve` 带 High-risk/confirm_token 语义（172ch），`reject_draft` 一句话（36ch）；29 条中仅 1 条含中文（`create_spot_application` 的「点位申请」括注）。**中文产品的中文用户，数字员工读到的操作手册是英文的**，且与 SoT 术语（business-ontology.yaml 12 模块 / 102 子功能 / 195 capability / 80 条模块级 aliases）零对齐——描述里的「spot application」「draft」用户说「点位申请」「草稿合同」。
3. **表宇宙有门，工具宇宙没有**：G-07 已证明「集合 + 基线 + 引用承认」的治理模式可让漂移当天现形（499 表 universe，canonical_drift_ci.py 执勤）。工具宇宙（29 tools）没有清单、没有基线、没有引用校验——tools/list 每次现场拼装，改名的代价（skills 断链 26 天）已经付过一次。
4. **权限映射已证明的模式可以平移**：`toolPermissions` 29/29 全映射 + canonical catalog 对齐（canonical_functions.txt testdata）+ 双向覆盖测试——把「权限码 ↔ 工具名」的治理结构复制到「语义挂点 ↔ 工具名」，工程上零新概念。

## What Changes（改什么）

1. **工具注册表 `mcp-tool-registry.yaml`**（lnkcre 仓，29 条）：每工具声明 `name / module（ontology 挂点）/ capability / permission_code（对齐 toolPermissions）/ context（17 Context 归属）/ entities（触及核心表）/ risk_level（对接 confirm 语义）/ status`。v1 只做登记与校验，不做生成替换（OQ-2）。
2. **Skills 引用覆盖门**：skills yaml 引用的工具名必须 ∈ 注册表 ∪ RegisterTool 现场注册名（双向：注册表有而技能引用的孤儿也报）——照抄 `auth_mapping_test.go` 双向覆盖模式。**首个动作即修复 4 处漂移**（required 3 处必须修，optional 1 处裁决移除或登记）。
3. **描述双语化条款（v2，生成器在语义层）**：描述模板 = 中文意图句 + ontology 术语别名 + 风险等级 + 英文保留句；生成器从 registry + business-ontology.yaml 产出候选文案，**人工裁决后**替换 Go 硬编码（描述是声明性资产，生成不豁免裁决——与 G-07「yaml 是结果、changes/ 是过程」同一条原则）。
4. **描述漂移检测**：Go 源码 RegisterTool 的 description ↔ registry 声明 diff 报警（对照 G-07 模式：不禁止改描述，改了要有判决/同步）。

## Impact（影响面）

- lnkcre 仓：skills yaml ×2 修复、`mcp-tool-registry.yaml` 新增、覆盖测试 1 件、描述文案批量替换（v2）；**零运行时行为变化**——描述与 skills 声明均为声明性资产，不触碰 handler/权限/confirm 路径（write-path-hardening 全部条款不受影响）。
- 语义层侧：产出 registry 生成器（semantic-model/consumers/ 第二消费方，LnkChatBI term-aliases 之后的第 3 个）；registry 语义挂点对 G-05 锚点体系零依赖。
- 消费方：数字员工 skills 4 件恢复可用性（quotation/triage 两件现在是断链状态）；LnkChatBI 工具语义问答获得挂点。

## 验收线（可度量）

| # | 度量 | 达标线 |
|---|---|---|
| 1 | skills 漂移修复 | 4/4 陈旧引用清除 + 覆盖测试落盘 GREEN |
| 2 | registry 覆盖 | 29/29 工具登记；permission_code 对齐 toolPermissions 100%；module 挂点对齐 ontology 12 模块 |
| 3 | 改名演练 | 模拟 D23 式改名（temp repo 注入），覆盖门当次运行 RED 且归因到引用文件:行号（对照现状 26 天盲区） |
| 4 | 描述双语化（v2） | 29/29 描述含中文意图句 + ≥1 条 ontology 术语别名；风险等级与 confirm 语义一致（approve/reject/create_draft 等 High-risk 标注） |

## Open Questions

1. registry 归属：lnkcre 仓内（靠近执行面，主仓维护）vs 语义层维护导出（靠近 SoT，我方维护）。倾向前者：工具面演进权在主仓（26 天漂移的根因正是声明资产离执行面太远）；语义层只出生成器与校验规则。
2. v1 范围：只做登记+校验+修漂移（快、零争议），描述双语化生成放 v2（涉及 29 条文案的人工裁决量）。
3. `convert_quotation_to_contract` 的裁决：登记为「规划中未实现」还是从 mi-quotation 移除（业务上「报价转合同」是否仍是既定场景——ontology 合同管理模块有对应 capability，需要主仓表态）。

## 证据附录（2026-09-23 实跑，机器可复核）

- 工具提取：RegisterTool 调用扫描（tools.go 9 / extended_tools.go 10 / workflow_definition_tools.go 10）= 29 唯一名，与 toolPermissions 29 条一一对齐。
- skills 交叉验证脚本与漂移矩阵见 `第17周/第17周-Day3-*.ipynb` 实验②；描述画像见实验①。
- 漂移年龄：skills 最后更新 1362c508（2026-06-15）；改名/移除 fbacc0f1（2026-08-28）；今日 2026-09-23。
