# 第4周 Day6：RAG 系统实战

> **导语**：前五天我们学了 RAG 的架构、检索原理、高级技术和优化策略，今天是"动手日"——从零搭建一个完整可运行的 RAG 系统。我们会用 Sentence-Transformers 做向量化、ChromaDB 做向量存储、实现检索+生成全流程，并做系统性的效果评估。完成后你就拥有了一个可以直接复用的 RAG 项目骨架。

---

## 📊 学习进度

```
██████████████████████  Day 6/7  RAG系统实战
```

| 维度 | 今日目标 |
|------|---------|
| 环境 | 安装并配置 Sentence-Transformers + ChromaDB |
| 构建 | 完成"加载→分块→向量化→存储→检索→生成"全流程 |
| 评估 | 用测试集量化检索召回率和准确率 |
| 复用 | 产出一套可移植的 RAG 代码模板 |

---

## 🤔 今天要解决什么问题？

我们模拟一个真实场景：**你有一批技术文档（关于 Transformer、RAG、向量数据库等），想搭建一个智能问答系统，用户提问后自动检索相关文档并生成回答。**

这个场景覆盖了 RAG 系统的所有核心环节，代码可以直接迁移到任何"文档问答"应用中。

---

## 🧠 系统架构总览

```
┌──────────────────────────────────────────────────────┐
│                   RAG 系统架构                        │
│                                                      │
│  ┌─────────┐   ┌──────────┐   ┌─────────┐          │
│  │ 原始文档 │──→│ 文档分块  │──→│ 向量编码 │          │
│  └─────────┘   └──────────┘   └────┬────┘          │
│                                    ↓                 │
│                              ┌──────────┐            │
│                              │ ChromaDB │            │
│                              └────┬─────┘            │
│                                   ↓                  │
│  ┌─────────┐   ┌──────────┐   ┌─────────┐          │
│  │ 用户问题 │──→│ 查询编码  │──→│ 向量检索 │          │
│  └─────────┘   └──────────┘   └────┬────┘          │
│                                    ↓                 │
│                            ┌──────────────┐          │
│                            │ 上下文构建    │          │
│                            └──────┬───────┘          │
│                                   ↓                  │
│                            ┌──────────────┐          │
│                            │ LLM 生成回答  │          │
│                            └──────────────┘          │
└──────────────────────────────────────────────────────┘
```

---

## 💻 Step 1：环境准备

```python
# 安装依赖（首次运行）
# !pip install sentence-transformers chromadb numpy

import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

print("✅ 依赖加载完成")
```

### 加载 Embedding 模型

```python
# 使用多语言轻量模型（384维，速度快，适合开发环境）
# 首次运行会自动下载约 470MB
model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
embed_model = SentenceTransformer(model_name)

# 快速测试：验证模型工作正常
test = embed_model.encode(["你好世界", "Hello World"])
print(f"Embedding 维度: {test.shape[1]}")  # 384

# 验证语义相似度
from numpy.linalg import norm
sim = np.dot(test[0], test[1]) / (norm(test[0]) * norm(test[1]))
print(f"'你好世界' 和 'Hello World' 的相似度: {sim:.4f}")  # 应该 > 0.7
```

---

## 💻 Step 2：准备文档数据

```python
# 模拟技术文档知识库
# 每篇文档是一个独立的"知识条目"
documents = {
    "doc1": """
    Transformer架构由Vaswani等人在2017年提出，彻底改变了自然语言处理领域。
    其核心是自注意力机制（Self-Attention），允许模型在处理序列数据时
    同时关注所有位置的信息，解决了传统RNN无法并行计算的问题。
    Transformer由编码器和解码器两部分组成，GPT使用了解码器结构，
    而BERT使用了编码器结构。多头注意力让模型从不同子空间关注信息。
    """,

    "doc2": """
    RAG（Retrieval-Augmented Generation）检索增强生成技术，
    由Lewis等人在2020年提出。它将信息检索与文本生成结合，
    先从知识库中检索相关文档片段，再将这些片段作为上下文
    输入给大语言模型，从而生成更准确、更有依据的回答。
    RAG能有效减少大模型的幻觉问题，是当前企业AI应用的核心技术。
    """,

    "doc3": """
    向量数据库是专门为高维向量检索设计的数据库系统。
    常用的向量数据库包括ChromaDB、Milvus、Pinecone、Weaviate等。
    它们支持高效的近似最近邻搜索（ANN），
    能在百万级向量中快速找到最相似的文档。
    常用的距离度量包括余弦相似度、欧氏距离和内积。
    """,

    "doc4": """
    Sentence-Transformers是HuggingFace开源的句子嵌入模型库。
    它可以将任意文本转换为固定维度的向量表示。
    常用的模型包括all-MiniLM-L6-v2和paraphrase模型系列。
    中文场景下推荐使用多语言模型或专门训练的中文模型。
    Embedding的质量直接影响RAG系统的检索效果。
    """,

    "doc5": """
    RLHF（基于人类反馈的强化学习）是让大模型对齐人类价值观的关键技术。
    训练过程分为三步：先进行SFT（监督微调），然后训练奖励模型，
    最后用PPO算法进行策略优化。DPO是RLHF的简化版本，
    直接用偏好数据优化模型，无需训练奖励模型。
    """
}

print(f"共加载 {len(documents)} 篇文档")
```

---

## 💻 Step 3：文档分块

```python
def chunk_text(text, chunk_size=150, overlap=30):
    """
    文档分块函数
    
    参数:
        text: 原始文本
        chunk_size: 每块字符数
        overlap: 相邻块的重叠字符数
    
    返回:
        文本块列表
    """
    text = text.strip()
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        if end >= len(text):
            break
        start = end - overlap  # 后退 overlap 步，确保重叠
    
    return chunks

# 对所有文档分块
all_chunks = []       # 存储所有文本块
chunk_sources = []    # 记录每块的来源文档

for doc_id, text in documents.items():
    chunks = chunk_text(text, chunk_size=150, overlap=30)
    all_chunks.extend(chunks)
    chunk_sources.extend([doc_id] * len(chunks))

print(f"总共生成 {len(all_chunks)} 个文档块")
print(f"\n前3个块预览：")
for i in range(min(3, len(all_chunks))):
    print(f"  [{chunk_sources[i]}] Block {i+1}: {all_chunks[i][:50]}...")
```

---

## 💻 Step 4：向量化并存入 ChromaDB

```python
# 初始化 ChromaDB（内存模式，重启后数据消失）
# 生产环境可用 persistent_client 持久化到磁盘
chroma_client = chromadb.Client()

# 创建集合（类似数据库中的"表"）
collection = chroma_client.get_or_create_collection(
    name="tech_docs",
    metadata={"description": "技术文档知识库"}
)

# 批量生成所有文本块的 Embedding
print("正在生成向量嵌入...")
embeddings = embed_model.encode(all_chunks, show_progress_bar=True)
print(f"向量形状: {embeddings.shape}")  # (N, 384)

# 准备 ID（每块的唯一标识）
chunk_ids = [f"{chunk_sources[i]}_chunk{j}" 
             for i, j in enumerate(range(len(all_chunks)))]

# 存入 ChromaDB
collection.add(
    ids=chunk_ids,
    documents=all_chunks,
    embeddings=embeddings.tolist()
)

print(f"✅ 成功存入 {len(all_chunks)} 个文档块到 ChromaDB")
```

---

## 💻 Step 5：实现检索函数

```python
def rag_retrieve(query, top_k=3):
    """
    RAG 检索函数
    
    参数:
        query: 用户查询字符串
        top_k: 返回最相关的前K个文档块
    
    返回:
        检索结果字典（包含文档、距离、ID）
    """
    # 将查询转换为向量
    query_embedding = embed_model.encode([query])
    
    # 在 ChromaDB 中做向量检索
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        include=["documents", "distances", "metadatas"]
    )
    
    return results

# 测试检索
query = "什么是Transformer架构？"
results = rag_retrieve(query, top_k=3)

print(f"🔍 查询: {query}")
print(f"\n检索结果：")
for i in range(len(results['ids'][0])):
    doc_id = results['ids'][0][i]
    distance = results['distances'][0][i]
    doc_text = results['documents'][0][i]
    # distance 越小越相似（ChromaDB 返回的是距离而非相似度）
    similarity = 1 - distance  
    print(f"\n  [{i+1}] {doc_id} | 相似度: {similarity:.4f}")
    print(f"      {doc_text[:80]}...")
```

---

## 💻 Step 6：完整 RAG 问答函数

```python
def rag_qa(question, top_k=3):
    """
    完整的 RAG 问答流程：检索 + 上下文构建 + Prompt 生成
    
    参数:
        question: 用户问题
        top_k: 检索的文档数
    
    返回:
        构建好的 Prompt（可直接送入 LLM）
    """
    # Step 1: 检索相关文档
    results = rag_retrieve(question, top_k=top_k)
    
    # Step 2: 构建上下文文本
    context_parts = []
    for i, doc in enumerate(results['documents'][0]):
        source = results['ids'][0][i]
        context_parts.append(f"[参考资料{i+1}] (来源: {source})\n{doc}")
    
    context = "\n\n".join(context_parts)
    
    # Step 3: 构建增强 Prompt
    prompt = f"""你是一个技术文档问答助手。请严格根据以下参考资料回答问题。

规则：
- 只使用参考资料中的信息
- 如果资料中没有相关信息，回答"根据现有资料无法回答此问题"
- 回答末尾标注引用的资料编号

{context}

问题：{question}

回答："""
    
    return prompt, results

# 测试多个问题
test_questions = [
    "什么是RAG技术？",
    "Transformer解决了什么问题？",
    "常用的向量数据库有哪些？",
    "什么是自注意力机制？",
    "RLHF的三个步骤是什么？"
]

print("=" * 60)
for q in test_questions:
    prompt, results = rag_qa(q, top_k=3)
    print(f"\n❓ 问题: {q}")
    print(f"📎 检索到 {len(results['ids'][0])} 个文档块:")
    for i, (doc_id, dist) in enumerate(zip(results['ids'][0], results['distances'][0])):
        sim = 1 - dist
        print(f"   {i+1}. {doc_id} (相似度: {sim:.3f})")
    print("-" * 40)
```

---

## 💻 Step 7：系统效果评估

```python
# 定义评估测试集：每个问题对应期望命中的文档ID
eval_set = [
    {'q': '什么是自注意力机制？',     'expected': ['doc1']},
    {'q': 'RLHF的训练步骤是什么？',   'expected': ['doc5']},
    {'q': '常用的向量数据库有哪些？',   'expected': ['doc3']},
    {'q': '如何提高Embedding质量？',  'expected': ['doc4']},
    {'q': 'RAG技术由谁提出？',       'expected': ['doc2']},
    {'q': 'DPO和PPO有什么区别？',     'expected': ['doc5']},
    {'q': 'Transformer的编码器和解码器', 'expected': ['doc1']},
    {'q': 'ChromaDB是什么？',        'expected': ['doc3']},
]

hits = 0
total = len(eval_set)

print("📊 RAG 系统检索质量评估")
print("=" * 60)

for item in eval_set:
    results = rag_retrieve(item['q'], top_k=3)
    # 提取检索到的文档来源ID
    retrieved_sources = [rid.split('_')[0] for rid in results['ids'][0]]
    # 检查期望文档是否在检索结果中
    hit = any(exp in retrieved_sources for exp in item['expected'])
    hits += int(hit)
    
    status = '✅' if hit else '❌'
    print(f"{status} Q: {item['q']}")
    print(f"   期望: {item['expected']} | 检索到: {retrieved_sources[:3]}")

recall = hits / total
print(f"\n🎯 召回率 (Recall@3): {hits}/{total} = {recall:.1%}")
```

---

## 📊 可视化：评估结果

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt

# 中文字体配置
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

# 每个问题的检索相似度得分（模拟数据）
questions = [item['q'][:12] + '...' for item in eval_set]
top1_sims = []
top3_sims = []

for item in eval_set:
    results = rag_retrieve(item['q'], top_k=3)
    dists = results['distances'][0]
    top1_sims.append(1 - dists[0])
    top3_sims.append(np.mean([1 - d for d in dists]))

x = np.arange(len(questions))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(x - width/2, top1_sims, width, label='Top-1 相似度', color='#4ECDC4')
ax.bar(x + width/2, top3_sims, width, label='Top-3 平均相似度', color='#FF6B6B')

ax.set_ylabel('余弦相似度')
ax.set_title('RAG 检索质量逐题分析', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(questions, rotation=30, ha='right')
ax.legend()
ax.set_ylim(0, 1.0)
ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='及格线')

plt.tight_layout()
plt.savefig('day6_eval_results.png', dpi=150)
plt.show()
```

---

## 🍧 业务关联：从 Demo 到生产

### 从技术文档 → 糖水店知识库

把上面的代码做简单替换，就能变成糖水店智能问答：

```python
# 替换文档内容
documents = {
    "menu": "美华糖水店菜单：红豆沙12元、芝麻糊10元、杨枝甘露15元...",
    "faq": "常见问题：营业时间9:00-22:00，支持外卖配送，满50元免配送费...",
    "recipes": "红豆沙配方：红豆200g、冰糖50g、陈皮少许，慢炖2小时...",
    "reviews": "顾客评价精选：红豆沙料足味正，杨枝甘露芒果味浓郁..."
}

# 替换 Embedding 模型（中文专用）
# model = SentenceTransformer('BAAI/bge-large-zh-v1.5')

# 替换 Prompt
prompt = f"""你是美华糖水店的客服助手。根据以下资料回答顾客问题。
保持友好专业的语气，回答简洁明了。

{context}

顾客问题：{question}
"""
```

### 生产环境架构升级清单

| 项目 | Demo 版本 | 生产版本 |
|------|----------|---------|
| 向量存储 | ChromaDB 内存模式 | Milvus / pgvector 持久化 |
| Embedding | MiniLM (384维) | bge-large-zh (1024维) |
| 检索 | 纯向量 | 混合检索 + Cross-Encoder 重排 |
| LLM | 直接 Prompt | API 调用 + 流式输出 |
| 监控 | 无 | 检索质量、延迟、用户反馈追踪 |
| 知识更新 | 手动改代码 | 后台管理界面 + 自动索引 |

---

## ⚠️ 常见误区

### 误区 1："demo 跑通了就可以上线"
❌ Demo 通常只有几篇文档，检索几乎不会出错。但文档量到 1000+ 篇时，各种边界问题就会暴露——同名实体、过时信息、格式不一致等。

### 误区 2："ChromaDB 够用了，不需要 Milvus"
❌ ChromaDB 适合开发和小规模应用（< 10万条）。超过这个量级，查询延迟会明显上升，而且缺乏分布式扩展能力。

### 误区 3："检索到了就等于答对了"
❌ 检索到正确文档不等于 LLM 能正确利用。有时候模型会"选择性忽略"某些上下文。需要端到端评估（从检索到最终回答），而不只看检索指标。

### 误区 4："只需要评估中文场景"
❌ 如果用户可能用中英混合提问（"Transformer怎么实现attention"），Embedding 模型需要同时支持中英文语义匹配。这也是推荐多语言模型的原因。

---

## 📝 课堂练习

**练习 1**：将本课的代码跑一遍，然后把 `chunk_size` 从 150 改为 100 和 300，分别观察召回率变化。

**练习 2**：在 Step 6 的 Prompt 中，去掉"规则"部分（不约束模型），换一个问文档中没有的问题，观察模型是否会"编造"答案。

**练习 3**：把 documents 字典的内容换成你自己感兴趣的主题（比如你熟悉的游戏攻略、电影信息），重新运行整个管道，测试检索效果。

---

## ✅ 课后测试

1. ChromaDB 的 `collection.query()` 方法返回的 `distances` 值，越 ______ 表示越相似。

2. 文档分块时设置 overlap 的作用是 ______。

3. 判断题：ChromaDB 内存模式下，程序重启后数据不丢失。（  ）

4. 在 RAG 评估中，Recall@K 表示 ______。

5. 简答题：如果要搭建一个支持 10 万篇文档的生产级 RAG，你需要对本课代码做哪些改造？

---

## 📖 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| ChromaDB | /kroʊmə diːbiː/ | Chroma数据库 | 轻量级开源向量数据库 |
| Collection | /kəˈlɛkʃən/ | 集合 | ChromaDB中存储向量数据的容器 |
| Persistent Client | /pərˈsɪstənt ˈklaɪənt/ | 持久化客户端 | 数据写入磁盘的数据库模式 |
| Recall@K | /rɪˈkɔːl æt keɪ/ | K位召回率 | 前K个结果中包含正确答案的比例 |
| Ingestion | /ɪnˈdʒɛstʃən/ | 数据摄入 | 将文档处理并存入向量库的过程 |
| Embedding Model | /ɛmˈbɛdɪŋ ˈmɒdəl/ | 嵌入模型 | 生成文本向量的模型 |
| Query Encoding | /ˈkwɪəri ɪnˈkoʊdɪŋ/ | 查询编码 | 将用户查询转换为向量 |
| Context Construction | /ˈkɒntɛkst kənˈstrʌkʃən/ | 上下文构建 | 拼接检索结果为LLM输入 |
| Evaluation Set | /ɪˌvæljuˈeɪʃən sɛt/ | 评估集 | 用于测试RAG效果的问题集合 |
| End-to-End | /ɛnd tuː ɛnd/ | 端到端 | 从输入到输出的完整流程 |

---

## 🔗 参考资源

- 📦 [Sentence-Transformers 文档](https://www.sbert.net/)
- 📦 [ChromaDB 官方教程](https://docs.trychroma.com/getting-started)
- 📚 [LangChain + ChromaDB 教程](https://python.langchain.com/docs/integrations/vectorstores/chroma)
- 🎥 [Building RAG from Scratch（视频）](https://www.youtube.com/watch?v=wd7TZ5wbKxI)
- 📊 [RAGAS: RAG 评估框架](https://docs.ragas.io/)

---

> 🔄 **明天预告**：Day 7 是第四周总复习——把 W3（大模型训练）和 W4（RAG与知识增强）的知识串联起来，做一次全面的"知识闭环"回顾！
