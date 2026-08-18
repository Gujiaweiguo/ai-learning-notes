# 第4周 Day4：GraphRAG 与知识图谱增强

> **导语**：传统 RAG 像一个只会"按页码查书"的图书管理员——你问他"椰子和奶茶什么关系"，他只会找同时提到两者的段落。但如果知识是这样的链路：椰子→榨汁→椰汁→加奶茶底→奶茶，每一步在不同文档里，传统 RAG 就断了链。GraphRAG 的思路是：先把知识织成一张"关系网"（知识图谱），然后在网中顺着线找答案。今天我们从零理解 GraphRAG。

---

## 📊 学习进度

```
██████████████████░░  Day 4/7  GraphRAG与知识图谱增强
```

| 维度 | 今日目标 |
|------|---------|
| 概念 | 理解知识图谱的三要素：实体、关系、属性 |
| 原理 | 掌握 GraphRAG 的"建图→检索→生成"三步流程 |
| 对比 | 分清传统 RAG 和 GraphRAG 各自的优劣 |
| 实战 | 用 NetworkX 构建糖水店知识图谱 |

---

## 🤔 为什么需要 GraphRAG？

### 传统 RAG 的关系盲区

假设你有一份产品手册，里面有这些信息分散在不同章节：

- 椰汁是从椰子榨取的
- 椰果是椰汁发酵制成的
- 奶茶的配料包括椰果
- 椰浆是椰汁浓缩的

用户问："椰子和奶茶之间有什么间接关系？"

传统 RAG 检索到的是零散段落，它无法"顺着链条推导"出：椰子→椰汁→椰果→奶茶。

> 💡 **类比**：传统 RAG 像查字典——你查一个词得到一段解释，但这个词和其他词的关系你得自己猜。GraphRAG 像查维基百科——不仅有解释，还有超链接，可以从一个词条跳到相关词条，形成完整的知识网络。

### 知识图谱要解决的核心问题

| 问题 | 传统 RAG 的表现 | GraphRAG 的表现 |
|------|----------------|----------------|
| "红豆沙的原料是什么" | ✅ 能找到直接描述 | ✅ 能找到，且能展示完整链路 |
| "椰子和奶茶有什么关系" | ❌ 找不到直接描述两者关系的文档 | ✅ 通过多跳推理找到路径 |
| "我们店所有含椰子成分的产品" | ⚠️ 可能遗漏间接含椰子的产品 | ✅ 沿图谱遍历即可找全 |
| "红豆沙和芝麻糊哪个更甜" | ✅ 简单对比可以 | ⚠️ 杀鸡用牛刀 |

---

## 🧠 核心原理详解

### 一、知识图谱三要素

知识图谱（Knowledge Graph）由三样东西组成：

#### 1. 实体（Entity / Node）
世界上的一个"东西"。可以是物体、概念、事件。

```
实体示例：椰子、椰汁、奶茶、红豆沙、美华糖水店
```

#### 2. 关系（Relation / Edge）
实体之间的联系，有方向性。

```
关系示例：(椰子) --[榨汁]→ (椰汁)
         (椰汁) --[原料]→ (奶茶)
```

#### 3. 属性（Property / Attribute）
实体或关系的特征描述。

```
属性示例：椰子.产地=海南，椰汁.糖分=5%，奶茶.价格=12元
```

> 🎯 **一句话总结**：知识图谱就是"谁（实体）和谁（实体）之间有什么关系（关系），各自有什么特征（属性）"。

### 二、GraphRAG 工作流程

GraphRAG 分三个阶段：

#### Phase 1：知识图谱构建（离线）

```
原始文档 → 实体抽取 → 关系抽取 → 构建图谱
```

**实体抽取**：从文本中识别出名词性实体。比如从"椰汁是用椰子榨汁制成的"中抽取"椰汁"和"椰子"。

**关系抽取**：判断实体之间的关系类型。上面的句子中关系是"原料"。

```python
import networkx as nx

def build_knowledge_graph(triples):
    """
    从(头实体, 关系, 尾实体)三元组列表构建知识图谱
    
    参数:
        triples: [(head, relation, tail), ...] 列表
    
    返回:
        networkx 图对象
    """
    G = nx.DiGraph()  # 有向图
    
    for head, relation, tail in triples:
        G.add_node(head)
        G.add_node(tail)
        G.add_edge(head, tail, relation=relation)
    
    return G

# 糖水店知识三元组
triples = [
    ("椰子", "榨汁", "椰汁"),
    ("椰汁", "原料", "奶茶"),
    ("椰汁", "浓缩", "椰浆"),
    ("椰汁", "发酵", "椰果"),
    ("椰果", "配料", "奶茶"),
    ("椰浆", "调味", "糖水"),
    ("红豆", "熬煮", "红豆沙"),
    ("红豆沙", "类型", "糖水"),
    ("西米", "配料", "糖水"),
    ("芋圆", "配料", "糖水"),
    ("奶茶", "类型", "冷饮"),
    ("糖水", "类型", "冷饮"),
    ("糖水", "类型", "热饮"),
]

G = build_knowledge_graph(triples)
print(f"实体数量: {G.number_of_nodes()}")  # 12
print(f"关系数量: {G.number_of_edges()}")  # 13
```

#### Phase 2：图谱检索（在线）

当用户提问时，GraphRAG 不是直接搜文本，而是：

1. **从问题中提取关键词/实体**
2. **在图谱中定位对应节点**
3. **沿边遍历，找到相关子图（多跳邻居）**
4. **把子图信息转换为文本上下文**

```python
def graph_rag_search(query, graph, max_hops=2):
    """
    GraphRAG 检索：从实体出发做多跳遍历
    
    参数:
        query: 用户查询
        graph: 知识图谱
        max_hops: 最大跳数
    
    返回:
        相关子图的实体和关系
    """
    # Step 1: 简化的实体识别（实际用NER模型）
    all_entities = set(graph.nodes())
    query_entities = [e for e in all_entities if e in query]
    
    if not query_entities:
        # 如果没匹配到，尝试模糊匹配
        query_entities = [e for e in all_entities 
                         if any(word in query for word in e)]
    
    print(f"识别到的实体: {query_entities}")
    
    # Step 2: 多跳遍历找相关子图
    related_nodes = set()
    related_edges = []
    
    for entity in query_entities:
        for hop in range(1, max_hops + 1):
            # 获取 hop 跳内的所有邻居
            neighbors = nx.single_source_shortest_path_length(
                graph.to_undirected(), entity, cutoff=hop
            )
            for neighbor, dist in neighbors.items():
                related_nodes.add(neighbor)
    
    # Step 3: 提取相关边
    related_subgraph = graph.subgraph(related_nodes)
    
    return related_subgraph
```

**检索示例**：

```python
query = "椰子和奶茶有什么关系？"
subgraph = graph_rag_search(query, G, max_hops=3)

print("\n相关实体:", list(subgraph.nodes()))
print("\n相关关系:")
for u, v, data in subgraph.edges(data=True):
    print(f"  {u} --[{data['relation']}]--> {v}")
```

**输出**：
```
相关实体: ['椰子', '椰汁', '椰果', '椰浆', '奶茶']

相关关系:
  椰子 --[榨汁]--> 椰汁
  椰汁 --[原料]--> 奶茶
  椰汁 --[发酵]--> 椰果
  椰果 --[配料]--> 奶茶
```

#### Phase 3：增强生成

把子图信息转换为自然语言上下文，送入 LLM：

```python
def subgraph_to_context(subgraph):
    """将子图转换为可读的文本上下文"""
    lines = []
    for u, v, data in subgraph.edges(data=True):
        lines.append(f"{u}的{data['relation']}是{v}")
    return "；".join(lines) + "。"

context = subgraph_to_context(subgraph)
prompt = f"""根据以下知识图谱信息回答问题：

知识：{context}

问题：{query}
"""
```

LLM 拿到这段上下文，就能生成："椰子通过榨汁得到椰汁，椰汁是奶茶的原料；同时椰汁发酵得到椰果，椰果也是奶茶的配料。所以椰子和奶茶有两条间接关系链。"

---

### 三、GraphRAG vs 传统 RAG 深度对比

| 维度 | 传统 RAG | GraphRAG |
|------|---------|----------|
| 数据结构 | 文本块 | 图结构（节点+边） |
| 检索方式 | 向量相似度 Top-K | 图遍历（BFS/DFS）+ 语义匹配 |
| 关系推理 | 弱（只靠文本描述） | 强（多跳遍历） |
| 全局视图 | 无（只见局部文本） | 有（可看到实体网络全貌） |
| 建图成本 | 低（切割即可） | 高（需要实体/关系抽取） |
| 维护难度 | 低（更新文档即可） | 高（需重新抽取/更新图谱） |
| 适用场景 | 简单问答、事实查询 | 复杂推理、关系分析、溯源 |

**选型建议**：
- 先用传统 RAG 跑通，当发现"关系类问题答不好"时再引入 GraphRAG
- GraphRAG 不是替代传统 RAG，而是**补充**——两者协同效果最好

---

## 📊 可视化：糖水店知识图谱

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import networkx as nx

# 中文字体配置
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

plt.figure(figsize=(12, 8))

# 使用 spring 布局让相关节点自然聚集
pos = nx.spring_layout(G.to_undirected(), k=1.5, iterations=50)

# 根据节点连接数设定大小
node_sizes = [300 + G.degree(node) * 200 for node in G.nodes()]
node_colors = ['#ff6b6b' if G.degree(n) > 3 else '#4ecdc4' for n in G.nodes()]

# 绘制节点
nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                      node_size=node_sizes, alpha=0.8)

# 绘制边（有方向用箭头）
nx.draw_networkx_edges(G, pos, edge_color='gray', 
                      width=1.5, alpha=0.6, 
                      arrows=True, arrowsize=15,
                      connectionstyle='arc3,rad=0.1')

# 绘制标签
nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

# 绘制关系标签
edge_labels = nx.get_edge_attributes(G, 'relation')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

plt.title("🥥 糖水店知识图谱", fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.savefig('day4_knowledge_graph.png', dpi=150)
plt.show()
```

**观察要点**：
- 大节点（红色）是"枢纽实体"——连接数多，比如"椰汁"、"糖水"
- 箭头方向表示关系的方向性——"椰子→榨汁→椰汁"
- 通过边的标签可以理解每条关系的语义

---

## 🍧 业务关联：糖水店经营分析

### 场景 1：原材料溯源

```
问题："奶茶里都有哪些原料？分别从什么来的？"
```

GraphRAG 沿图谱遍历：奶茶→(原料)→椰汁→(来源)→椰子，奶茶→(配料)→椰果→(来源)→椰汁→(来源)→椰子。一步到位给出完整溯源链。

### 场景 2：产品推荐

```
问题："顾客喜欢椰子味的，推荐什么？"
```

GraphRAG 从"椰子"出发，找到所有含有椰子衍生品的商品路径：椰汁→奶茶、椰浆→糖水、椰果→奶茶。

### 场景 3：过敏原排查

```
问题："哪个产品不含豆类？"
```

GraphRAG 可以做"反向遍历"：找到所有不含"红豆""绿豆"等豆类实体的产品路径。这在食品安全场景极其重要。

---

## ⚠️ 常见误区

### 误区 1："GraphRAG 会取代传统 RAG"
❌ GraphRAG 擅长关系推理，但简单事实查询它反而不如传统 RAG 高效。两者是互补关系，最佳实践是"传统 RAG + GraphRAG"双路并行检索。

### 误区 2："有了 LLM 就不需要知识图谱了"
❌ LLM 的知识在参数里是"黑盒"的，无法保证准确。知识图谱是显式的、可审计的、可编辑的。在企业场景（医疗、法律、金融）中，知识图谱的可信度远超 LLM 的参数记忆。

### 误区 3："知识图谱构建是一次性的"
❌ 业务在变化，产品在更新，关系在演变。知识图谱需要持续维护——定期重新抽取实体和关系，更新图谱结构。

### 误区 4："图越大越好"
❌ 图谱太大意味着更多噪音和不相关路径，检索效率也会下降。好的图谱应该是"精而准"，不是"大而全"。

---

## 📝 课堂练习

**练习 1**：为以下文本提取三元组（实体-关系-实体）：
> "芒果布丁使用新鲜芒果制作，是冷饮类甜品。杨枝甘露也使用芒果，还配有西米和西柚。"

**练习 2**：给定一个知识图谱，用户问"我们店所有和椰子有关的产品"，请描述 GraphRAG 的检索过程（从哪个节点出发、遍历哪些边、返回哪些节点）。

**练习 3**：思考题——如果你的糖水店有 500 个产品、3000 种原料关系，你会选择传统 RAG 还是 GraphRAG？还是两者结合？为什么？

---

## ✅ 课后测试

1. 知识图谱的三要素是 ______、______ 和 ______。

2. GraphRAG 相比传统 RAG 的核心优势是 ______。

3. 判断题：GraphRAG 完全可以替代传统 RAG。（  ）

4. GraphRAG 检索时使用的方法是 ______（填"向量相似度"或"图遍历"）。

5. 简答题：为什么说"知识图谱更适合需要可解释性的场景"？

---

## 📖 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| Knowledge Graph | /ˈnɒlɪdʒ ɡrɑːf/ | 知识图谱 | 实体-关系-属性构成的图结构知识库 |
| Entity | /ˈɛntɪti/ | 实体 | 图谱中的节点，表示一个事物 |
| Relation | /rɪˈleɪʃən/ | 关系 | 实体之间的有向连接 |
| Triple | /ˈtrɪpəl/ | 三元组 | (头实体, 关系, 尾实体)的基本知识单元 |
| GraphRAG | /ɡrɑːf ræɡ/ | 图谱增强检索 | 利用知识图谱增强RAG的技术 |
| Multi-hop Reasoning | /ˈmʌlti hɒp ˈriːzənɪŋ/ | 多跳推理 | 沿图谱边做多步推导 |
| Entity Extraction | /ˈɛntɪti ɪkˈstrækʃən/ | 实体抽取 | 从文本中识别命名实体 |
| Relation Extraction | /rɪˈleɪʃən ɪkˈstrækʃən/ | 关系抽取 | 从文本中识别实体间关系 |
| Subgraph | /ˈsʌbɡrɑːf/ | 子图 | 大图中截取的部分图 |
| NetworkX | /ˈnɛtwɜːrk ɛks/ | NetworkX | Python图分析库 |

---

## 🔗 参考资源

- 📄 [GraphRAG 论文（Microsoft, 2024）](https://arxiv.org/abs/2404.16130)
- 📦 [Microsoft GraphRAG 开源项目](https://github.com/microsoft/graphrag)
- 📚 [Neo4j GraphRAG 入门指南](https://neo4j.com/blog/graphrag-manifesto/)
- 🎥 [知识图谱入门视频（李文哲）](https://www.youtube.com/watch?v=R8MyLRBmJ7c)
- 📦 [NetworkX 中文文档](https://networkx.org/documentation/stable/)

---

> 🚀 **明天预告**：Day 5 聚焦 RAG 实战架构设计——从分块策略优化、缓存机制到性能调优，学习如何搭建生产级 RAG 系统！
