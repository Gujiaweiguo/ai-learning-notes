# PT-W1 Day 6：Ontology vs Knowledge Model vs RAG

> **日期**：2026-08-01（周五）
> **周主题**：DDD → Semantic Model
> **今日核心问题**：Ontology、Knowledge Model、RAG 三者在 LangChat + MI 里各自什么角色？它们如何配合让 AI 既"懂结构"又"能找资料"？

---

## 一句话区分三者

```
Ontology      → 描述"企业有什么"（结构化语义）
Knowledge     → 描述"什么知识需要被检索"（非结构化内容）
RAG           → 描述"如何检索并增强生成"（技术机制）
```

如果你觉得这三个概念有重叠，不是你理解力的问题——是行业里确实混着用。今天我们把三者放到你的 LangChat + MI 架构里，看它们各自占据什么位置。

---

## 一、三个比喻

### Ontology 是城市的"规划图"

规划图上标着：这是住宅区（Domain Module），那条是主干道（Relationship），这个地块的用途是商业（Capability Area），这栋楼的使用规则是"限高 60 米"（Rule）。

规划图**不关心**某栋楼里住着谁、办公桌上放着什么文件。它只定义**结构、关系和规则**。

### Knowledge Model 是城市的"图书馆目录"

图书馆里有租约模板、政策文件、操作手册、培训资料、合同条款。Knowledge Model 决定：哪些文档需要收录？怎么分类？哪些是权威来源？哪些已过期需要更新？

图书馆目录**不定义**城市的结构（那是规划图的事），但它告诉你**去哪里找信息**。

### RAG 是城市的"快递系统"

你说"我要 A101 铺位的租约模板"，RAG 就去图书馆找到对应的文档片段，送到你（LLM）面前。你基于这份真实文档来回答，而不是凭记忆猜测。

快递系统**不理解**城市规划（那是 Ontology），也**不拥有**图书馆的内容（那是 Knowledge）。它只负责**高效检索和投递**。

---

## 二、放到你的 LangChat + MI 架构里

对照你已经有的真实资产：

```
┌─────────────────────────────────────────────────────┐
│ Ontology 层（企业结构语义）                            │
│                                                       │
│ business-ontology.yaml  → 模块→能力→场景结构          │
│ ADR-006 四类关系         → Relationship 定义           │
│ effect-registry.yaml     → Event/Lifecycle 定义       │
│ MI Domain Model §3       → Entity + Ownership         │
│                                                       │
│ 回答：企业里有什么？它们什么关系？什么规则？            │
└─────────────────────────────────────────────────────┘
                        ↓ 指导
┌─────────────────────────────────────────────────────┐
│ Knowledge 层（企业知识内容）                           │
│                                                       │
│ LangChat AI Knowledge（企业 AI 知识库）               │
│   ← 制度文件、操作手册、合同模板、培训资料             │
│   ← 五阶段：Loading → Indexing → Storing →           │
│              Querying → Evaluation                    │
│                                                       │
│ 回答：哪些知识文档需要被 AI 检索？                      │
└─────────────────────────────────────────────────────┘
                        ↓ 检索
┌─────────────────────────────────────────────────────┐
│ RAG 层（检索增强生成机制）                              │
│                                                       │
│ LangChat RAG 引擎                                      │
│   ← 向量嵌入 + 混合搜索 + 重排序                       │
│   ← 把检索到的文档片段注入 LLM 上下文                   │
│                                                       │
│ 回答：怎么把正确的知识片段送到 AI 面前？                │
└─────────────────────────────────────────────────────┘
                        ↓ 增强
┌─────────────────────────────────────────────────────┐
│ Agent / Digital Employee（执行）                       │
│                                                       │
│ Agent 拿到 Ontology 的结构理解 + RAG 检索的知识        │
│   → 通过 SkillRelease 执行业务能力                    │
└─────────────────────────────────────────────────────┘
```

---

## 三、对照真实材料：LangChat ADR-001 怎么定位 RAG

你的 LangChat ADR-001 §4.1 明确写道：

> **LangChat 是企业能力平台（Enterprise Capability Platform）**。它承载知识、Skill、Workflow、人审、能力治理与子 Trace。

ADR-001 把 **RAG 列为四类一等公民能力之一**（RAG / Workflow / Agent / Tool Use）。这意味着：

- RAG 是**平台层核心构造块**，不是某个产品功能的附属
- LangChat AI Knowledge 以 RAG 为核心架构
- RAG 可以与 Workflow、Agent、Tool Use **组合使用**

你的网站内容（`what-is-rag.md`）里也写了 RAG 的定位：

> RAG 的核心价值是**可追溯性**——每个回答可以链接到源文档的具体位置。

但你自己在同一篇文档的"RAG ≠ 万能方案"一节也写明了边界：

> - **结构化数据查询**（如"上季度各区域平均客单价"）——需要 SQL 查询，不是向量检索
> - **实时数据**（如库存、定价、系统状态）——标准 RAG 从静态索引检索，需要配合 Function Calling

**这就是 Ontology 的价值所在——RAG 解决不了"结构化理解"问题，而 Ontology 恰好补位。**

---

## 四、三者各自做不到什么（边界意识）

| 层 | 能做到 | 做不到 | 需要谁补位 |
|---|---|---|---|
| Ontology | 描述实体、关系、规则、状态机 | 回答"我们的退租政策文档在哪？" | Knowledge Model |
| Knowledge | 存储和检索文档内容 | 判断"A101 铺位当前能不能出租" | Ontology（规则推理） |
| RAG | 高效检索文档片段并增强生成 | 知道两个实体的业务关系是什么 | Ontology（Relationship） |

### 一个具体场景看三者协作

**用户问数字员工**："A101 铺位为什么不能出租？"

```
第一步：Ontology 提供结构推理
  → Entity: Space A101（铺位）
  → Relationship: A101 关联 Lease #2023-085
  → Lifecycle: Lease #2023-085 状态 = Terminating
  → Rule: "存在未完成退租流程的 Space 不可出租"

  这一步不需要 RAG。这是 Ontology 的纯结构推理。

第二步：Knowledge + RAG 补充细节
  → RAG 检索到《退租管理操作手册》§3.2：
    "退租流程包括：合同终止 → 场地验收 → 费用结算 → 铺位释放"
  → RAG 检索到《2026 年招商政策》：
    "退租验收未完成的铺位不列入可招商清单"

  这一步不需要 Ontology。这是 Knowledge 的内容检索。

第三步：Agent 综合两者生成回答
  → "A101 铺位当前不能出租，因为：
      1. 关联合同 #2023-085 处于退租终止流程中（Ontology 推理）
      2. 根据退租操作手册，需完成场地验收后铺位才能释放（RAG 检索）
      3. 2026 招商政策明确：退租验收未完成的铺位不列入招商清单（RAG 检索）
      建议：发起场地验收 Task，完成后铺位自动释放进入可招商清单。"
```

**Ontology 提供"骨架"，Knowledge + RAG 提供"血肉"，Agent 组合成"完整的回答"。**

---

## 五、你的战略叙事链已经有了

你在企业 AI 知识库的文章里已经写了这条链：

```
企业知识 → Knowledge Base → Retrieval → Skill → Agent → Business Action
```

现在加上 Ontology 维度，完整的链是：

```
企业业务世界
    ↓ Ontology 描述（有什么、什么关系、什么规则）
企业语义模型
    ↓ +
企业知识库（Knowledge Base）
    ↓ RAG 检索增强
Agent 上下文（结构理解 + 知识内容）
    ↓ SkillRelease 执行
Business Action（业务动作）
```

**这条链就是你未来 AI Native Enterprise Software 的认知主干。**

---

## 六、Ontology 如何指导 Knowledge Model 的建设

这是很多人忽略的一点：**Ontology 应该指导 Knowledge Base 的组织方式。**

没有 Ontology 指导的 Knowledge Base：

```
一大堆文档 → 统一切片 → 向量入库 → 暴力检索
问题：检索到什么全靠运气，文档之间没有业务上下文关联
```

有 Ontology 指导的 Knowledge Base：

```
Ontology 定义了 14 个业务域
  → 文档按业务域归类，带业务元数据
  → 检索时可以按域过滤："只在合同管理域里搜"
  → 向量检索 + 业务上下文过滤 = 更精准

Ontology 定义了实体的生命周期
  → 文档可以标注"适用于哪个状态"
  → 例如《退租操作手册》标注：applies_to = Lease.status ∈ {Terminating, Terminated}
  → 检索时按当前状态过滤，不会把退租文档推给一个新签约场景
```

**这就是为什么 Ontology 是"语义操作系统"——它不只是描述世界，它还指导其他子系统如何组织。**

---

## 七、今天改变什么设计判断

```
以前：RAG 是 AI 知识库的核心技术
现在：RAG 是检索机制，它需要 Ontology 提供结构上下文，
      才能真正精准地服务企业场景

以前：Knowledge Base 是一堆文档的集合
现在：Knowledge Base 应该被 Ontology 指导组织——
      按业务域归类、按实体生命周期标注、按 Relationship 关联

以前：三者混在一起谈，觉得都是"AI 知识"的事
现在：三层分离——
      Ontology = 结构语义（你有什么）
      Knowledge = 内容资产（你知道什么）
      RAG = 检索机制（怎么找到）
      三者协作，不能互相替代
```

---

## 八、练习（5 分钟）

用你自己的 LangChat 架构回答以下问题：

1. 你的 LangChat AI Knowledge 当前有按 business-ontology.yaml 的 14 个业务域来组织知识库吗？
   - 如果有，效果如何？
   - 如果没有，你觉得按域归类会带来什么改进？

2. 当用户问"铺位的计租面积怎么算？"，这个回答应该来自：
   - Ontology（结构推理）？
   - Knowledge Base（文档检索）？
   - 还是 MI 数据库查询（Function Calling）？
   
   **思考：三者各自能提供什么？哪个最合适？**

3. 你的数字员工未来需要同时具备"结构理解"和"知识检索"能力。
   在你的架构里，这两个能力分别由哪个组件提供？

---

## 九、与明天 Day 7 的衔接

明天是 Week 1 的输出日：**《MI CRE Semantic Gap Analysis v0.1》**。

我们将汇总这一周的所有发现：

- Day 1：你已经做了 Domain Model（17 个 Context = DDD 战略设计）
- Day 2：Bounded Context 划分验证
- Day 3：Entity / Value Object / Aggregate 在 MI 里的样子
- Day 4：为什么 Domain Model 不够（AI 读不懂语义）
- Day 5：Ontology 六维度 Gap Analysis
- Day 6：Ontology vs Knowledge vs RAG 三层分离

这一周的认知汇聚成一张表：**已有资产 vs 缺失语义的全景图**。

这就是 Week 1 的毕业作品，也是后续三周的导航图。
