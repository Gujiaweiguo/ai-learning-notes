# Citing Change: leasing-policy 族 3 表入域登记（招商政策事实 · 壳/版本/生命周期）

> 立案：2026-09-22（W17-D2，W16-D7 定轨第 3 项 / g0x 提案 What-5 执行对象）。
> 状态：**registered**（canonical 门 w39 透镜 cited 0→3）。
> 裁决：**入域登记**。09-18 活事件首发家族（W16 探针破案的 +7 之一），主仓侧已闭环归档，本案权利义务：语义侧补流程留痕。

## Why

- 来源迁移：`migrations-pg/000227_leasing_policy_unit_pricing.up.sql`（第 1 段：招商政策事实）。
- 主仓闭环：归档 change `2026-09-18-leasing-policy-unit-pricing-pages` + `unit-pricing-benchmark-enhancement`（rev3）；spec `openspec/specs/leasing-policy-management/spec.md`（8 Requirements）。
- 实现：`backend/internal/leasingpolicy/`（hash/hits/model/repository/seed/service）。
- 本体挂点：招商管理（aliases 直接含「租赁政策/租决」）——政策是招商条件报批的事实层。

## What（登记内容）

**Context 归属：03 Leasing Pipeline**（品牌/意向/条件报批的约束输入；与 quotations 等谈判对象同域）。
本体挂点：招商管理.招商报价/条件报批（capability 侧 `rent-decision-comparison` / `workflow-approvals`）。

表清单（3）与语义：

| 表 | 语义 |
|---|---|
| `leasing_policies` | 政策壳（稳定身份；policy_type∈{general 整体, business 业态, special 专项}；policy_code LPL-YYYY-NNNN 项目作用域 autocode） |
| `leasing_policy_versions` | 政策版本（draft 可编辑→**提交后业务字段不可变**；content_hash=提交时业务字段 canonical JSON SHA-256；适用范围 business_type/brand/area 区间；招商条件：租期上下限/递增率/管理费推广费标准/装改免租/运营免租/报价规则/底价 floor_price/目标价 target_price；workflow_instance_id 挂审批） |
| `leasing_policy_lifecycle` | 生命周期审计（action∈{submit,withdraw,approve,reject,void,copy}，append-only） |

状态机（登记进 lifecycle 构件）：version `draft → pending_approval → approved | void`（withdraw/reject 回退，copy 派生）。

关键关系：
- `unit_pricing_batch_lines.rent_price_policy` 等 11 组 *_policy 列 ← `leasing_policy_versions`（政策值作为定价行的基线参照，跨族→citing-unit-pricing）；
- `unit_pricing_versions.source_policy_version_id` → `leasing_policy_versions`；
- `workflow_instances`（Platform/Shared）经 workflow_instance_id 挂接——审批流不自建。

术语条目：招商政策（整体/业态/专项）、政策版本（不可变提交/content_hash）、租决（alias 登记）。

## 边界声明

- 「提交后不可变」由 content_hash 护航：hash 是提交时快照指纹，改业务字段即 hash 失配（hash.go 实现语义）。
- 版本表不回写壳表；生命周期只追加。

## Impact

- canonical 门：w39 透镜 cited +3；03 Leasing Pipeline 52→55。
- Policy 语义化（W15-D4 ai-execution-constraints 草案）获得第一个「版本不可变+审批挂接」的完整事实样本；W18 Rule 显式化的政策条件输入在此。

## 证据

- 迁移：`migrations-pg/000227_leasing_policy_unit_pricing.up.sql` L18-L48 + COMMENT（「招商政策壳（稳定身份；业务内容在版本表）」）；
- spec：`openspec/specs/leasing-policy-management/spec.md`（8 Req，首条即「Policy/PolicyVersion 事实与版本不可变」）；
- 包：`backend/internal/leasingpolicy/`（hash.go content_hash 实现）；digest `sync/digest-2026-W39.md` §2。
