# MI CRE Enterprise Semantic Model v0.1（人读版）

> 组装：W14-D6（2026-09-06 补录）。机器可读版：`mi-cre-semantic-model-v0.1.yaml`（同目录）。
> 这不是又一份文档——它是**分层 SoT 的索引与裁决层**：不复制下游源，只声明"什么在哪、谁说了算、哪里断了"。

## 定位一句话

PT-W4 的 Semantic Model v0.1 草案是"文档"；本版把它升级为**机器可校验、可被消费的开发资产**：每个构件带证据指针（sha/路径/代码锚点），每个断言可重跑。

## 宪章（谁说了算）

| 层 | Source of Truth |
|---|---|
| 术语/别名 | business-ontology.yaml（sha `bf550bc24de66813`，须补治理头，G-01/P0） |
| 业务能力/行 ID | CRE BCM（不可变锚点） |
| 对象归属/边界/生命周期 | MI Domain Model 17 Context |
| 规则/Effect | effect-registry.yaml（5 类冻结） |
| 实现事实/验收 | openspec specs + 代码 |

## 六构件速览

1. **Entity**：骨架=17 Context+Platform（472 表实证分布，BI 14.8% 最大）；模块↔Context 多对多（财务管理 1→4，4 个 Context 无模块入口）——映射表是查询路由必需品。
2. **Identity**：物理锚=canonical_tables（472，双迁移并集裁判）；行锚=BCM 行 ID；术语层 883 条/792 唯一/91 复用待消歧。
3. **Relationship**：语义侧=模块×BCM×Context 映射；实现侧=三个事务耦合点（occupancy.CreateTx / amendment 应收重算 / ar_rebalance）+12 条灰区。
4. **Lifecycle**：lease 8 态（代码枚举为准）；condition-approval 带全生命周期审计；amendment 9 类矩阵已数据化（运行时可编辑）。
5. **Rule**：5 类冻结 effect 的实现映射；service-effect 不注册的决策档案；frozen 无 CI 是最大洞。
6. **Capability+Policy**：102 能力标签，role 7/102，场景 15/102 全冻在资源管理；policy 三载体（审批权矩阵/审批流策略/变更矩阵）。

## 已知缺口（10 条，全量见 YAML）

P0 一条：ontology 无治理 frontmatter。其余按 G-02~G-10：场景层断供、术语消歧、registry 无锚无 CI、双迁移分叉、新表无挡板、断言未核、矩阵无快照、语义超额承诺。

## 熵增基线（为什么现在就要消费它）

表增长 4 月 68 → 6 月 152 → 7 月 148 → 8 月 98；跨切面桶占比 26.2%。语义资产不是被推翻死的，是被稀释死的——**第一个消费方要赶在稀释前面**。

## 第一个消费方（W15 计划）

W15-D3：从术语层+Entity 锚点批量生成 LnkChatBI term-aliases/SQL 示例校准集。预警：只能吃术语层，场景层 15/102 不可消费。

## 验证方式

- 本文件全部数字可由 `w14d3-ontology-health-report.yaml`、`w14d5-context-coverage-report.yaml`、D4 对账 md 复算
- ontology 指纹带 sha256_16，重跑 diff = 熵增量（体检可复现原则）

## v0.1.1 patch 记录（2026-09-09，W15-D3 前置落地）

按 W14-D7 整改清单原位 patch，不重发版：R2 场景层冻结升格机器可读 `scenario_layer_frozen: true`；R3 Context 别名表 14 条（D3 短名→D5 全名，含 02 Party Core↔02 Merchant，规范名以 D5 全名为准）；G-01 ontology frontmatter 四行提案模板（待主仓 change 流程提交，语义资产侧先固化模板）。ontology 指纹复验仍为 `bf550bc24de66813`（patch 未触碰 SoT）。机器检查全过：版本 0.1.1 / 冻结字段 / 别名表全解析 / frontmatter 四键。
