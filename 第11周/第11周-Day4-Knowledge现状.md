# 🧱 LangChat 心智模型 | Week11-Day4

**📌 当前主题：Knowledge 现状 — 当前 RAG 实现 vs Knowledge Governance 目标**

**日期：2026-08-13（周四）**

---

## ━━━ 1. 今日核心问题 ━━━

### 为什么 Knowledge 治理不等于 RAG？

在传统 ERP 时代，"知识库"就是一个文档管理系统——上传文件、分类目录、搜索关键字。Jason 你做了 26 年 ERP，见过无数"知识管理"项目最终变成了"文档坟场"。

到了 AI 时代，RAG（Retrieval-Augmented Generation，检索增强生成）让"知识库"重新活了——不只是存文档，还能理解问题、检索相关段落、辅助 LLM 生成回答。

但 LangChat v2 的目标态告诉了我们一个不太舒服的事实：

> **当前 RAG 实现只是"能用"，离"可治理"还差很远。**

核心问题不是"RAG 效果好不好"——那是工程优化问题。核心问题是：

**Knowledge 在 LangChat v2 架构中是一等公民（KnowledgeCollection → KnowledgeSnapshot），但在当前代码中只是 Assistant 的一个 JSON 字段（`kb_names_json`）。**

这个差距意味着：知识内容目前没有版本、没有快照、没有 digest、没有不可变性约束、没有被 DeploymentRevision 闭包锁定。运行时消费的知识和生产者上传的知识之间，没有"冻结点"。

---

## ━━━ 2. 人话解释（用 Jason 26 年 ERP 经验讲）━━━

Jason，想象一下你在做 MI（Management Information）系统的合同模块。

**当前态**就像：租户上传了一份合同 PDF，系统直接把文件丢进文件夹，然后搜索的时候全量扫描。每次租户改了合同，旧版本直接被覆盖。你在 ERP 里绝不会这么做——ERP 有版本控制、审计日志、生效日期、作废标记。

但 LangChat 当前的 Knowledge 就是这样的：

| ERP 该有的 | LangChat Knowledge 当前有吗 |
|---|---|
| 文档版本控制 | ❌ 文件直接覆盖 |
| 生效快照（某时点的完整知识状态） | ❌ 没有快照概念 |
| 知识与业务应用的绑定关系 | ⚠️ 只是 Assistant 上的一个 JSON 数组 |
| 知识变更触发重新部署 | ❌ 修改知识不需要生成新版本 |
| 知识内容的不可变性保证 | ❌ 任何时候都能改 |

**目标态**（v2 Domain Model）要求的：

- `KnowledgeCollection`（逻辑集合，可变）→ `KnowledgeSnapshot`（不可变快照，内容寻址 digest）
- `KnowledgeSnapshot` 被 `DeploymentRevision` 闭包 digest-pin
- Runtime 只消费快照，不直接消费集合

这就好比：ERP 中"合同模板"（可编辑）和"已签订合同"（不可改）的关系。当前 LangChat 只有"合同模板"没有"已签订合同"。

---

## ━━━ 3. LangChat 架构位置 ━━━

在 10 站点完整链路图中，Knowledge 处于：

```
[Agent Host] → [ApplicationContract] → [Blueprint → ExecutionPlan] → [Runtime]
                                                                    ↓
                                              [KnowledgeSnapshot ← KnowledgeCollection]
                                                                    ↓
                                                    被 DeploymentRevision 闭包 digest-pin
```

Knowledge 的位置很特殊——它不是执行链路上的一环（不像 Capability/Connector 那样参与执行），但它是 **Runtime 闭包的必要组成部分**。没有 KnowledgeSnapshot，DeploymentRevision 的闭包就不完整。

**当前代码中的位置**：
- `Assistant.kb_names_json` — 一个 JSON 数组，记录关联的知识库名称
- `Assistant.rag_config_json` — RAG 配置（top_k、score_threshold、rerank 等）
- 运行时通过 `retrieve_rag_context()` 直接搜索知识库

这就是当前态和目标态的根本结构差异。

---

## ━━━ 4. ADR 依据 ━━━

### v2 Domain Model（02 文档）§7.7 明确定义：

**SC-09 `KnowledgeCollection`（Business Domain Layer）**
- 知识资源的逻辑集合，可变
- Identity: `(tenant, workspace, collection_id)`
- 职责：承载知识资源归属；演进产生新 KnowledgeSnapshot
- **红线：不直接被 Runtime 消费（Runtime 只消费快照）**

**SC-10 `KnowledgeSnapshot`（Supply Chain Layer）**
- 知识集合在某时刻的不可变快照
- Identity: 内容寻址 digest
- 职责：被 Runtime 消费的不可变知识视图；被 DeploymentRevision 闭包 digest-pin
- **红线：不可修改；不可被 Runtime 旁路**

### Charter §6.6 的宪法约束：

> 任何运行时变更（依赖升级、配置变更、Knowledge 更新）必须生成新 DeploymentRevision

这意味着：**知识变了 → 快照变了 → DeploymentRevision 闭包变了 → 新版本部署**。当前代码完全没有这条链路。

### 术语映射（§12.1）：

> 当前"知识库（Knowledge Base）"→ `KnowledgeCollection` + `KnowledgeSnapshot`
> **转化**：当前知识库混合了逻辑集合与运行时消费内容。v2 显式分离。

---

## ━━━ 5. 代码验证 ━━━

### 5.1 当前 RAG 管道（完整实现）

当前 RAG 能力其实不弱，工程做了很多优化：

```python
# channels/rag.py — 渠道 RAG 检索（共享给 SPA chat）
async def retrieve_rag_context(db, *, tenant_id, workspace_id, 
                                assistant_id, message, history, 
                                kb_names=None, rag_config=None):
    # 1. 加载 Assistant 的 kb_names_json 和 rag_config_json
    # 2. Query Transform: rewrite_with_context → transform_queries (multi_query/hyde)
    # 3. 每个 KB 独立搜索：search_docs(query, kb, top_k, score_threshold)
    # 4. 多 query 结果合并：merge_search_results (RRF Reciprocal Rank Fusion)
    # 5. Hybrid Search: _boost_keyword_matches (关键词 + 向量 RRF 融合)
    # 6. Rerank: get_Reranker().rerank(query, docs, top_n)
    # 7. 返回 context_text + citations（带 vector_distance, relevance_score, rrf_score）
```

**已有的 RAG 工程**：
| 能力 | 实现状态 |
|---|---|
| 向量检索（PGVector/Milvus/FAISS） | ✅ 完整 |
| Query Rewrite（上下文消解） | ✅ 默认开启 |
| Multi-Query / HyDE | ✅ 可配置 |
| Hybrid Search（向量+关键词 RRF 融合） | ✅ 实现 |
| Rerank | ✅ 实现（可配置 reranker） |
| Citation 持久化（rag_trace v2） | ✅ 实现 |
| RAG 评估（Precision/Recall/MRR/NDCG） | ✅ 实现 |
| KB Improvement Review Queue | ✅ 实现 |
| 知识隔离（tenant/workspace） | ✅ 实现 |
| 跨工作空间 KB 挂载 | ✅ 实现 |
| Per-KB RAG 配置覆盖 | ✅ 实现 |

### 5.2 关键结构：当前知识库模型

```python
# db/models/knowledge_base_model.py
class KnowledgeBaseModel(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True)
    kb_name = Column(String(50))
    kb_info = Column(String(200))  # 用于 Agent 的知识库简介
    vs_type = Column(String(50))   # 向量库类型
    embed_model = Column(String(50))
    file_count = Column(Integer, default=0)
    tenant_id = Column(Integer, ForeignKey("tenant.id"))
    workspace_id = Column(Integer, ForeignKey("workspace.id"))
    kb_metadata = Column(JSON, nullable=True)
    # 注意：没有版本字段、没有 digest 字段、没有快照关系
```

```python
# db/models/workspace_kb_binding_model.py — 跨工作空间挂载
class WorkspaceKBBindingModel(Base):
    __tablename__ = "workspace_knowledge_base"
    workspace_id = Column(Integer, ForeignKey("workspace.id"))
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"))
    granted_by = Column(Integer, ForeignKey("user.id"))
    rag_config_override_json = Column(Text, nullable=True)  # 挂载时可覆盖 RAG 配置
```

### 5.3 关键发现

当前 RAG 工程能力很强，但**治理结构完全缺失**：

```
已有（工程层）          缺失（治理层）
─────────────          ─────────────
向量检索 ✅              KnowledgeCollection（逻辑集合）❌
Query Transform ✅      KnowledgeSnapshot（不可变快照）❌
Rerank ✅                快照 digest ❌
Hybrid Search ✅         DeploymentRevision 闭包引用 ❌
RAG 评估 ✅              知识变更触发新部署 ❌
反馈队列 ✅              知识版本与制品谱系 ❌
```

---

## ━━━ 6. 商业地产映射（LangChat → MI CRE 场景）━━━

### MI CRE（商业地产管理）知识治理需求映射

| LangChat 目标态 | MI CRE 场景 | 当前态能用吗 |
|---|---|---|
| `KnowledgeCollection` | 「招商政策文档库」——可编辑、可增删文档 | ✅ 当前 KnowledgeBaseModel 勉强可用 |
| `KnowledgeSnapshot` | 「2026Q3 招商政策冻结版」——签合同时引用的版本 | ❌ 没有快照，无法冻结 |
| 被 DeploymentRevision pin | 「数字员工"招商助手 v2.1"绑定的知识版本」| ❌ 知识改了，数字员工行为就变了，无追溯 |
| 快照 digest | 合同审批时的"附件哈希值" | ❌ 无 digest |
| Runtime 只消费快照 | 数字员工只能用已冻结的知识版本回答 | ❌ 实时搜索，知识随时变 |

**商业地产风险场景**：

想象一个招商数字员工，租户问"免租期最长多久？"。如果知识库刚被改了（比如从90天改成了60天），数字员工的回答就会变。但在商业地产，已经签的合同适用的政策不应被追溯修改。

**这就是 KnowledgeSnapshot 存在的理由——和 ERP 的"生效日期"逻辑完全一致。**

---

## ━━━ 7. 与传统方案比较 ━━━

### 知识管理方案对比

| 维度 | 传统文档管理 | 当前 LangChat RAG | LangChat v2 目标态 |
|---|---|---|---|
| 知识表示 | 文件 + 目录 | 向量索引 + 文档 | KnowledgeCollection + KnowledgeSnapshot |
| 版本控制 | 文件版本号 | ❌ 无 | 内容寻址 digest |
| 不可变性 | ❌ | ❌ | ✅ 快照不可变 |
| 与部署绑定 | ❌ | ❌ | ✅ DeploymentRevision 闭包 |
| 变更影响 | 手动通知 | 实时生效，无感知 | 触发新 DeploymentRevision |
| 审计追溯 | 操作日志 | 无 | Attestation + Provenance |
| 知识评估 | 人工抽检 | RAG Evaluation Suite | ReleaseEvaluation + DeploymentEvaluation |

### 为什么不能直接用"文件版本号"？

因为 AI 时代的知识不只是文件——它是 **向量索引 + 文档 + 分块策略 + Embedding 模型 + Reranker** 的组合。同一个文件，用不同的 chunk size 或不同的 embedding 模型，检索效果完全不同。

所以 KnowledgeSnapshot 不只是"文档的快照"，而是"文档 + 索引 + 配置"的完整冻结。这比 ERP 的文档版本复杂得多。

---

## ━━━ 8. 架构师思考题 ━━━

**问题：如果 MI 有 50 个购物中心，每个中心的招商政策不同但格式相同，Knowledge 怎么设计？**

思考维度：

1. **一个 Collection 还是 50 个？**
   - 如果一个 Collection：知识量大，检索时需要 metadata 过滤（center_id），但管理简单
   - 如果 50 个 Collection：每个独立，但数字员工绑定多个 KB 时需要跨库检索
   - 当前 LangChat 支持多 KB 检索（`kb_names_json` 是数组），但 RRF 合并效果未验证

2. **共享政策 + 专属政策的层级关系？**
   - 集团统一政策（所有中心适用）+ 中心特色政策（仅该中心适用）
   - 需要 Workspace 级别的 KB 挂载（当前已支持 `WorkspaceKBBindingModel`）
   - 但 Per-KB RAG 配置覆盖（`rag_config_override_json`）能否满足层级优先级？

3. **政策更新时，已部署的数字员工怎么办？**
   - 当前态：知识改了立即生效，可能产生不一致回答
   - 目标态：需要新 KnowledgeSnapshot → 新 DeploymentRevision → 新 TrafficPolicy 版本
   - 过渡期怎么管理？

4. **知识质量退化怎么发现？**
   - 当前已有 RAG Evaluation Suite（Precision/Recall/MRR/NDCG）
   - 已有 KB Improvement Review Queue（负面反馈聚类 → AI 建议）
   - 但缺少 KnowledgeSnapshot 间的质量趋势对比

---

## ━━━ 9. 我的理解变化 ━━━

**以前以为**：RAG 就是"向量检索 + LLM 生成"，LangChat 的 RAG 管道已经很完整了（Query Transform + Hybrid Search + Rerank + Citation + Evaluation），知识这块应该没什么大问题。

**现在知道**：

1. **RAG 工程 ≠ Knowledge 治理**。当前 RAG 管道确实很强，但治理层完全缺失——没有版本、没有快照、没有不可变性、没有与部署闭包的绑定。

2. **最大的 Gap 不是"效果"，而是"可追溯性"**。当前知识库随时可改，数字员工行为不可预测——这在企业场景是不可接受的风险。

3. **KnowledgeSnapshot 是 KnowledgeCollection 到 Runtime 的唯一合法桥梁**。这个设计和 ERP 的"生效版本"逻辑完全一致——已发布的不能被追溯修改。

4. **当前已有的 KB Improvement Review Queue 和 RAG Evaluation 是很好的基础**。它们在目标态中对应 DeploymentEvaluation 的雏形——但需要绑定到快照版本才有意义。

---

## ━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题：Week11-Day5 — 竞品对比：Dify/LangGraph/OpenClaw/Claude Code 各自的链路

**Today's Question 预告**：LangChat 最独特的设计是什么？

### Semantic Layer 位置

```
Ontology → Domain Model → Capability → Skill
                              ↑
                    Knowledge 在这里被消费
                              ↑
         KnowledgeCollection → KnowledgeSnapshot（目标态）
                    ↓
         当前：KnowledgeBaseModel（实时可变，无版本）
```

Knowledge 在 Semantic Layer 上的位置：
- **不是** Capability（它不是执行依赖）
- **不是** Skill（它不是可部署单元）
- **是** Runtime 闭包的组成部分（被 DeploymentRevision digest-pin）
- **是** Supply Chain 的制品类型之一（KnowledgeSnapshot 是 Artifact 子类型）

### 本周进度

| Day | 主题 | 状态 |
|---|---|---|
| D1 周一 | Capability Inventory | ✅ |
| D2 周二 | Gap Matrix | ✅ |
| D3 周三 | Connector 现状 | ✅ |
| **D4 周四** | **Knowledge 现状** | **📍 今天** |
| D5 周五 | 竞品对比 | 明天 |
| D6 周六 | 实施路线图 v1.0 | 后天 |
| D7 周日 | 最终 Virtual CTO Review | 周日 |
