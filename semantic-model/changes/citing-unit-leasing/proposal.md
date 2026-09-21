# Citing Change: unit_leasing 族 3 表入域登记（铺位×节点进度实例 · 跟踪容器层）

> 立案：2026-09-22（W17-D2，W16-D7 定轨第 3 项 / g0x 提案 What-5 执行对象）。
> 状态：**registered**（canonical 门 w39 透镜 cited 0→3）。
> 裁决：**入域登记**。与 citing-leasing-progress 同迁移（000234）、同 Context，但业务角色不同（实例层 vs 执行层），按 g0x What-5 族划分独立立案。

## Why

- 来源迁移：`migrations-pg/000234_leasing_progress_phase1.up.sql`（12 表中 3 表属本族）。
- 业务角色：**铺位粒度的进度跟踪容器**——unit 锚定的计划/阶段实例与开业日期变更重算，是 leasing-progress 任务/事实层的挂靠骨架（任务按 unit 派生、完成事实落 stage 实例行）。
- spec/实现同 citing-leasing-progress（`leasing-progress-plan` spec D2/D9 条款；`backend/internal/leasingprogress/` derivation.go 驱动重算）。

## What（登记内容）

**Context 归属：03 Leasing Pipeline**（unit 锚定但业务对象是招商过程跟踪，非铺位静态属性；与 01 Asset Foundation 的分界=`unit_pricing_versions` 先例——价格属性归资产，进度实例归招商）。
本体挂点：招商管理.招商计划（terms：招商进度/节点/里程碑）。

表清单（3）与语义：

| 表 | 语义 |
|---|---|
| `unit_leasing_plans` | 每铺位跟踪容器（target_opening_date + template 引用；UNIQUE(unit_id,status) 每铺位至多一个 active 计划） |
| `unit_leasing_stages` | 铺位×节点实例（投影行：planned/actual/status/ref_doc + **模板快照冻结列**——生成时快照 stage_no/name/type/auto_event/lead_days/required，模板后续改版不回写实例，D1「实例冻结模板快照引用」） |
| `leasing_plan_recalc_batches` | 开业日期变更重算批次审计（before/after/recalculated_count/preserved_count，D9.3） |

关键关系：
- `unit_leasing_plans.unit_id` → `units`（01 Asset Foundation 锚表，跨 Context 引用）；
- `unit_leasing_stages.template_item_id` → `leasing_stage_template_items`（引用+快照双轨）；
- `leasing_stage_completion_facts.stage_id` → `unit_leasing_stages`（完成事实挂实例不挂模板）；
- `leasing_plan_recalc_batches.plan_id` → `unit_leasing_plans`（重算以计划为单位）。

术语条目：铺位招商计划、目标开业日期、阶段实例（快照冻结）、重算批次。

## 边界声明

- 「已覆盖 planned_date」判定 = `leasing_stage_plan_overrides` 行存在（D9.4），不在本族表上加覆盖标志列——实例层不做覆盖状态冗余。
- 零数据纪律同 000234（零行种子）。

## Impact

- canonical 门：w39 透镜 cited +3；模型快照合并留待 v0.2。
- 与 citing-leasing-progress 合计 +12 表落 03 Leasing Pipeline（40→52，+30%）。

## 证据

- 迁移：`migrations-pg/000234_leasing_progress_phase1.up.sql` L90-L194（unit_leasing_plans/stages/recalc_batches 三段）；
- spec：`openspec/specs/leasing-progress-plan/spec.md`（D2 实例/D9 倒排相关 Req）；digest `sync/digest-2026-W39.md` §2。
