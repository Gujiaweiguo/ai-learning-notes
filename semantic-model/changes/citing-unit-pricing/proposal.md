# Citing Change: unit-pricing 族 4 表入域登记（批量定价与三级价格授权 · 一铺一价族的批次化执行层）

> 立案：2026-09-22（W17-D2，W16-D7 定轨第 3 项 / g0x 提案 What-5 执行对象；09-18 活事件首发家族，主仓侧已闭环归档）。
> 状态：**registered**（canonical 门 w39 透镜 cited 0→4）。
> 裁决：**入域登记**。

## Why

- 来源迁移：`migrations-pg/000227_leasing_policy_unit_pricing.up.sql`（price_authority_constraints / unit_pricing_batch_ops）+ `000229_unit_pricing_batch_model.up.sql`（unit_pricing_batches / unit_pricing_batch_lines），并大规模扩展存量表 `unit_pricing_versions` / `unit_pricing_history` 列集。
- 主仓闭环：归档 change `2026-09-18-leasing-policy-unit-pricing-pages`（rev2 批量调价转正）+ `2026-09-18-unit-pricing-benchmark-enhancement`（rev3：结构化押金规则/派生摘要/相邻对比）；spec `openspec/specs/unit-pricing-management/spec.md`（17 Requirements，首条「批次单据模型（唯一改价事实）」）。
- 实现：`backend/internal/unitpricingbatch/`（comparison/deposit_rules…）。

## What（登记内容）

**Context 归属：01 Asset Foundation**——跟随存量锚 `unit_pricing_versions`（W14-D5 归属）保持族内一致：一铺一价是铺位资产的价格属性层，本族 4 表全部服务于 unit_pricing_versions 的批量生成与授权校验，不新增独立定价域。
本体挂点：资源管理侧「资源定价」term + 招商管理「一铺一价」term（双挂点如实登记：资产属性视角为主，招商消费视角为引用）。

表清单（4）与语义：

| 表 | 语义 |
|---|---|
| `price_authority_constraints` | 三级价格授权约束（scope_level∈{hq, project}；floor/ceiling；**解析取更严交集，集团约束不可被项目放宽**；hq 行 project_id 可空=全局） |
| `unit_pricing_batch_ops` | 批量设置台账（actor/authority_level/scope+payload JSONB/成败计数——操作级留痕，与业务批次分离） |
| `unit_pricing_batches` | 定价批次单据（UPB-YYYY-NNNN；draft→pending_approval→effective/rejected/void；content_hash；可溯源 source_policy_version_id） |
| `unit_pricing_batch_lines` | 批次行（batch×unit 唯一；**11 组「执行值 × _policy 政策基线」双列结构**——定价与政策参照并列可对账；价格单位五枚举） |

存量表扩展（非新表，随案登记）：`unit_pricing_versions` +batch_id/+四类价格列/+11 组 policy 列；`unit_pricing_history` 同步扩展捕获列（审计保真）。

关键关系：
- `unit_pricing_batch_lines.batch_id` → `unit_pricing_batches`；`.unit_id` → `units`（01 锚）；
- `unit_pricing_batches.source_policy_version_id` → `leasing_policy_versions`（03，政策作为定价来源，跨 Context 引用）；
- `unit_pricing_versions.batch_id` → 批次（生效后落版本）；`price_authority_constraints` 在提交校验时以更严交集约束 batch_lines 价格区间；
- 权限挂点：function 160 `pricing.authority`（admin approve 级）。

术语条目：一铺一价、定价批次（唯一改价事实）、价格授权（三级/更严交集）、政策基线列（*_policy）。

## 边界声明

- 「唯一改价事实」：改价只经批次单据走（spec 首条 Req）；`unit_pricing_batch_ops` 是操作台账不是业务单据——两层留痕不混。
- price_unit 000227 版枚举四值，000229 扩为五值（+sqm_week）并重建约束——迁移内自洽，登记以 000229 终态为准。

## Impact

- canonical 门：w39 透镜 cited +4；01 Asset Foundation 36→40。
- Policy→Pricing→Version 三段链（leasing_policy_versions → batches/lines → unit_pricing_versions）成为 W18 Rule/Policy 显式化的第二批语料（审批矩阵 + 授权约束都是 Policy Model 输入）。

## 证据

- 迁移：`migrations-pg/000227_leasing_policy_unit_pricing.up.sql` L100-L135 + `000229_unit_pricing_batch_model.up.sql` 全文（含 unit_pricing_versions/history 扩展段）；
- spec：`openspec/specs/unit-pricing-management/spec.md`（17 Req）+ `position-pricing-history` / `pricing-matrix`（存量族 spec）；
- 包：`backend/internal/unitpricingbatch/`；digest `sync/digest-2026-W39.md` §2。
