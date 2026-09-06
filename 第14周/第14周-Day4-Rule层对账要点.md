# 第14周-Day4 Lifecycle/Rule/Policy 层盘点——effect-registry 冻结 5 类 vs lnkcre 代码事实对账

> 补录说明：9/6 晚管线故障补填。本日按精简口径执行：对账表 + 逐类证据 + 缺口登记，非 10 段完整格式。

## Today's Question

语义层声明的规则（effect-registry.yaml）和代码里的 if-else，谁是 source of truth？

## 对账表（effect-registry v1.0 冻结 5 类 → 代码事实）

| Effect 类型（语义注册） | 代码证据（lnkcre） | 对账结论 |
|---|---|---|
| state-transition-effect | lease 8 态状态机（draft→pending_approval→active→…→closed，含 rejected/voided/pending_termination，`lease/model.go`）；condition-approval 带 lifecycle_audit 表 | ✅ 实现在，且状态迁移有审计轨迹 |
| occupancy-effect | 独立 occupancy 包：`CreateTx` 事务耦合、`ReserveRejectsActiveOccupancy` 集成测试（活跃占用拒绝再预留） | ✅ 语义=实现一致，测试锚定 |
| financial-effect | `amendment_receivable_impact.go`（变更→应收重算）+ arrebalance 引擎（trigger_events/rebalance_failures 表）+ billing 计费族 | ✅ 分布在 billing/collections/arrebalance 多包——**多对多映射** |
| lead-conversion-effect | opportunity/broker 包 + opportunity_status_history 表 | ⚠️ 表级证据在，转化链断言未逐条核（登记缺口） |
| maintenance-effect | repair_work_orders + material_* 全族（12 Context 46 表） | ✅ 表级证据充分 |
| ~~service-effect~~（评审未注册） | 13 Context 仅 3 表（service_requests/tenant_messages/status_history） | ✅ **代码反向验证了注册决策**：确无独立结果类语义 |

## 三个已核示例（谁依赖谁）

1. **状态机**：`Status = "draft"` 等 8 个字面量硬编码在 lease/model.go——代码是事实，registry 是契约；两边各自演化、无机器对账通道。
2. **占用联动**：occupancy 包用 Go 事务（CreateTx）保证一致性而非事件——effect-registry 声明的是"什么会变"，代码决定"怎么变"（同步事务 vs 异步事件），语义层不管传输机制，边界划对了。
3. **变更矩阵**：amendmentmatrix 包把 9 类矩阵做成**运行时可编辑表**（Get/Update by lease.AmendmentType）——规则本体在数据库不在代码，"if-else 在哪"这问题的答案是：越来越不在代码里。

## 结论：SoT 分层（接 D2 宪章）

- **规则的"存在性与意图"** → effect-registry（为什么有这 5 类、为何 service-effect 不注册——评审理由本身就就有档案价值）
- **规则的"执行事实"** → 代码 + 运行时表（amendmentmatrix 这类可编辑矩阵是第三形态：规则数据化）
- 两层之间**没有机器锚点**：registry 不含 package path/表名引用——与 D3 发现的 ontology 无 frontmatter 同构

## 缺口登记（进 D6）

1. registry 无机器可读代码锚点（package/table 引用），对账靠人读
2. "frozen" 无 CI 强制：新增 effect 不走 ORE-1 不会有任何告警（同 canonical 无归属挡板问题）
3. lead-conversion 链路断言未核（opportunity_status_history 有数据即可补）
4. amendmentmatrix 运行时可编辑 = 规则变更无版本快照（矩阵变更未入 audit，待核 condition_approval_lifecycle_audit 是否覆盖）
