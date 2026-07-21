# 第4周 Day3：高级 RAG——混合检索与重排序

> **导语**：假设你在一个图书馆找"草莓甜品的做法"。图书管理员 A 按书名搜索（关键词检索），找到了《草莓蛋糕大全》但漏掉了《水果甜品手册》里专门讲草莓的一章。管理员 B 按内容相似度搜索（向量检索），找到了那一章但又混入了一些不太相关的内容。如果让 A 和 B 先各自搜，然后把两人的结果合并、排序，是不是更全面？这就是"混合检索"的核心思路。今天我们学习三大进阶技术，把 RAG 检索准确率从 70% 推到 90% 以上。

---

## 📊 学习进度

```
████████████████░░░░  Day 3/7  高级RAG：混合检索·重排序·查询改写
```

| 维度 | 今日目标 |
|------|---------|
| 混合检索 | 理解 BM25 + 向量检索的互补性及 RRF 融合算法 |
| 重排序 | 掌握 Cross-Encoder 精排的原理和流程 |
| 查询改写 | 学会 HyDE 和 Multi-Query 两种改写策略 |
| 实战 | 动手实现完整的混合检索管道 |

---

## 🤔 为什么基础 RAG 不够用？

### 基础向量检索的盲区

回顾 Day 2：我们把所有文档向量化，然后用余弦相似度检索。这在大多数情况下有效，但有几个典型翻车场景：

| 问题类型 | 例子 | 原因 |
|---------|------|------|
| 关键词遗漏 | 搜"iPhone 15"，向量检索可能返回"iPhone 14"的内容 | 语义太近，区分不开细微差异 |
| 专有名词丢失 | 搜"ISO 27001认证"，找不到含这个精确编号的文档 | 向量化后专有名词的精度被稀释 |
| 查询太模糊 | 搜"好喝的"，什么文档都有一定相似度，区分度差 | 缺乏关键词锚点 |
| 排序不准 | Top-1 可能不是最相关的，只是向量距离最近 | 余弦相似度并非完美排序指标 |

### 解决方案矩阵

| 问题 | 解决方案 | 今天学的内容 |
|------|---------|-------------|
| 关键词遗漏 / 专有名词 | 混合 BM25 关键词检索 | 混合检索 |
| Top-K 排序不准 | Cross-Encoder 重排序 | 重排序 |
| 查询太模糊 / 太短 | 查询改写扩展 | 查询改写 |

---

## 🧠 核心原理详解

### 一、混合检索（Hybrid Search）

#### 生活类比

> 你要找一本"做红烧肉的书"。方法一：问图书管理员（向量检索），他说"这本《中式烹饪》里应该有"。方法二：在书架索引里搜"红烧肉"三个字（关键词检索），找到了《家常菜大全》第 87 页。两个方法各有找到的内容，合并起来更完整。

#### BM25 关键词检索简介

BM25（Best Matching 25）是搜索引擎用了几十年的经典算法。它的核心逻辑：

- 文档中出现了搜索词 → 加分
- 搜索词在文档中出现频率越高 → 分数越高（但有上限）
- 文档越短，同样频率的匹配权重越高（短文档更精准）
- 搜索词越罕见（在全部文档中），匹配到时加分越多（IDF 权重）

#### RRF（Reciprocal Rank Fusion）融合算法

向量检索和 BM25 各自返回一个排序列表，怎么合并？RRF 的思路极其简洁：

```
RRF分数 = Σ  1 / (k + rank_i)
         各路检索
```

其中 `rank_i` 是文档在第 i 路检索中的排名，`k` 是平滑常数（通常取 60）。

**直觉理解**：一个文档如果在两路检索中都排名靠前，它的 RRF 分数就会很高。排名第一的得 1/61 ≈ 0.0164，排名第二的得 1/62 ≈ 0.0161。排名越靠前贡献越大，但不是赢者通吃。

```python
def reciprocal_rank_fusion(vector_ranking, keyword_ranking, k=60):
    """
    RRF 融合算法
    
    参数:
        vector_ranking: 向量检索返回的文档ID列表（按相关度降序）
        keyword_ranking: BM25检索返回的文档ID列表（按相关度降序）
        k: 平滑参数，默认60
    
    返回:
        融合后的排序结果 {doc_id: rrf_score}
    """
    fused = {}
    
    # 向量检索的排名贡献
    for rank, doc_id in enumerate(vector_ranking, 1):
        fused[doc_id] = fused.get(doc_id, 0) + 1 / (k + rank)
    
    # 关键词检索的排名贡献
    for rank, doc_id in enumerate(keyword_ranking, 1):
        fused[doc_id] = fused.get(doc_id, 0) + 1 / (k + rank)
    
    # 按融合分数降序排列
    return dict(sorted(fused.items(), key=lambda x: x[1], reverse=True))
```

**示例**：

```python
# 糖水店产品文档
documents = [
    "美华糖水店的草莓大福新鲜出炉",     # doc 0
    "今日特供：芒果布丁和红豆沙",       # doc 1
    "招牌红豆沙汤圆，用料十足",         # doc 2
    "季节限定：草莓系列甜品"            # doc 3
]

query = "草莓味的甜品"

# 向量检索排名（按语义相似度）
vector_ranking = [0, 3, 1, 2]  # doc0草莓大福 > doc3草莓系列 > doc1芒果 > doc2红豆

# BM25 关键词检索排名（按词频匹配）
keyword_ranking = [0, 3, 1, 2]  # doc0含"草莓" > doc3含"草莓" > doc1无 > doc2无

# RRF 融合
result = reciprocal_rank_fusion(vector_ranking, keyword_ranking)
print("混合检索结果：")
for doc_id, score in result.items():
    print(f"  doc{doc_id}: {documents[doc_id][:20]}... (RRF: {score:.4f})")
```

---

### 二、重排序（Reranking）

#### 为什么需要重排序？

向量检索用的是 **Bi-Encoder**（双编码器）：查询和文档分别独立编码，然后算相似度。速度快，但精度有天花板——因为查询和文档之间的交互信息完全丢失了。

重排序用的是 **Cross-Encoder**（交叉编码器）：把查询和文档拼接在一起 `[CLS] 查询 [SEP] 文档 [SEP]`，输入同一个模型，输出一个相似度分数。精度高得多，但速度慢（每对 query-doc 都要跑一次模型）。

> 💡 **类比**：Bi-Encoder 像看简历筛选——HR 快速扫一眼决定要不要；Cross-Encoder 像面试——花时间深入了解每个候选人。实际流程：先快速筛简历（初筛 50 份），再逐一面试（精排 50 → 取 Top 5）。

#### 两阶段检索流程

```
用户查询
  ↓
向量检索初筛 → Top-50（快，Bi-Encoder）
  ↓
Cross-Encoder 精排 → Top-5（慢，但准确）
  ↓
拼接到 Prompt → 送入 LLM 生成
```

```python
def rerank_with_cross_encoder(query, candidates, cross_encoder_model):
    """
    使用 Cross-Encoder 对初筛结果重排序
    
    参数:
        query: 用户查询
        candidates: 初筛返回的文档列表
        cross_encoder_model: 预加载的 Cross-Encoder 模型
    
    返回:
        重排序后的文档列表
    """
    # 构造 (query, doc) 对
    pairs = [[query, doc] for doc in candidates]
    
    # Cross-Encoder 一次性输出所有对的分数
    scores = cross_encoder_model.predict(pairs)
    
    # 按分数降序排列
    ranked_indices = np.argsort(scores)[::-1]
    
    return [candidates[i] for i in ranked_indices], sorted(scores, reverse=True)
```

#### 性能对比

| 方法 | 召回率 | 精确率 | 延迟 | 适用阶段 |
|------|--------|--------|------|---------|
| 纯向量检索 | ~75% | ~70% | 低（~50ms） | 初筛 |
| BM25 关键词 | ~65% | ~75% | 极低（~10ms） | 初筛 |
| 混合检索 | ~88% | ~80% | 低（~60ms） | 初筛 |
| Cross-Encoder 重排 | ~92% | ~92% | 中（~200ms） | 精排 |
| 混合检索 + 重排 | **~95%** | **~94%** | 中高（~260ms） | 最佳 |

---

### 三、查询改写（Query Rewriting）

#### 问题：用户的查询往往不完美

- 太短："糖水"（不知道具体想了解什么）
- 太模糊："有什么好喝的"（好喝的标准是什么？）
| 有错别字："红都沙"（应该是"红豆沙"）
| 口语化："那个甜甜的用豆子做的"（需要理解意图）

#### 方法 1：HyDE（Hypothetical Document Embeddings）

**思路**：先让 LLM 生成一个"假设的理想答案"，再用这个答案去检索。

```
原始查询："有没有适合夏天的糖水"
    ↓ LLM 生成假设文档
假设文档："夏天适合喝清凉解暑的糖水，比如绿豆沙、杨枝甘露、
         西米露等。这些糖水口感清爽，有消暑降温的效果。"
    ↓ 用假设文档做向量检索
检索到更精准的结果（因为假设文档的语义信息比原始查询丰富得多）
```

```python
def hyde_query_rewrite(query, llm_generate):
    """
    HyDE: 假设文档检索
    
    参数:
        query: 原始查询
        llm_generate: LLM生成函数
    
    返回:
        改写后的查询（假设文档）
    """
    prompt = f"""请为以下问题生成一段简短的理想答案（50-100字）：
    问题：{query}
    理想答案："""
    
    hypothetical_doc = llm_generate(prompt)
    return hypothetical_doc.strip()
```

> 🎯 **类比**：你想在二手市场找一把"舒服的椅子"。直接搜"舒服的椅子"结果太多太杂。如果你先描述"我想找一把人体工学椅，有腰部支撑，可调节高度，网布材质"，用这段描述去搜，结果精准得多。

#### 方法 2：Multi-Query（多查询扩展）

**思路**：从不同角度改写查询，分别检索，最后合并结果。

```python
def multi_query_expansion(query, llm_generate, num_variants=3):
    """
    多查询扩展：生成多个变体查询
    
    参数:
        query: 原始查询
        llm_generate: LLM生成函数
        num_variants: 生成的变体数量
    
    返回:
        扩展查询列表
    """
    prompt = f"""请将以下搜索查询从不同角度改写成 {num_variants} 个变体，
    每行一个，不要编号：
    原始查询：{query}
    改写："""
    
    result = llm_generate(prompt)
    variants = [q.strip() for q in result.strip().split('\n') if q.strip()]
    variants.append(query)  # 保留原始查询
    
    return list(set(variants))  # 去重
```

**示例**：
```
原始查询："草莓味的甜品"
变体 1："有哪些含草莓的甜点推荐"
变体 2："草莓系列的产品有哪些"  
变体 3："什么甜品用了新鲜草莓"
```

每个变体分别检索 Top-K，然后用 RRF 合并所有结果。

---

## 📊 可视化：不同检索策略效果对比

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np

# 中文字体配置
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

strategies = ['纯向量\n检索', '纯BM25\n关键词', '混合检索\n(Hybrid)', '混合+\n重排序']
recall = [75, 65, 88, 95]
precision = [70, 75, 80, 94]

x = np.arange(len(strategies))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
bars1 = ax.bar(x - width/2, recall, width, label='召回率', color='#4ECDC4')
bars2 = ax.bar(x + width/2, precision, width, label='精确率', color='#FF6B6B')

ax.set_ylabel('分数 (%)')
ax.set_title('不同检索策略效果对比', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(strategies)
ax.legend()
ax.set_ylim(0, 110)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}%', ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('day3_search_comparison.png', dpi=150)
plt.show()
```

---

## 🍧 业务关联：糖水店智能客服

### 完整管道演示

```python
# 顾客提问
query = "今天有没有草莓味的甜品"

# Step 1: Multi-Query 扩展
expanded = multi_query_expansion(query)
# → ["草莓味的甜品", "含草莓的甜点", "草莓系列产品", "新鲜草莓做的甜品"]

# Step 2: 对每个变体做混合检索
all_candidates = []
for q in expanded:
    vec_results = vector_search(q, top_k=10)    # 向量检索
    bm25_results = bm25_search(q, top_k=10)     # 关键词检索
    fused = reciprocal_rank_fusion(vec_results, bm25_results)
    all_candidates.append(fused)

# Step 3: 合并所有变体的结果（再次 RRF）
final_candidates = multi_rrf_fusion(all_candidates)

# Step 4: Cross-Encoder 重排序 Top-50 → Top-5
top_5 = rerank_with_cross_encoder(query, final_candidates[:50])

# Step 5: 送入 LLM 生成回答
answer = rag_generate(query, top_5)
```

**实际效果**：通过"查询改写 + 混合检索 + 重排序"三重优化，系统能精准找到"美华糖水店的草莓大福"和"季节限定草莓系列"，而不是泛泛推荐所有甜品。

---

## ⚠️ 常见误区

### 误区 1："加了重排序就一定更好"
❌ 如果你的文档库很小（< 100 篇），初筛就已经能覆盖大部分相关文档，重排序的收益很小，反而增加了延迟。重排序的价值在文档量大、初筛噪音多时才显著。

### 误区 2："Multi-Query 扩展越多越好"
❌ 每多一个查询变体就多一轮检索请求，延迟成倍增加。通常 3-5 个变体就够了。而且变体太多可能引入噪音。

### 误区 3："HyDE 总是有效"
❌ 如果 LLM 生成的假设文档方向偏差，反而会"带偏"检索。比如用户问"Python 异步编程的坑"，LLM 生成的假设文档全是基础概念，可能导致检索偏离"踩坑经验"类文档。

### 误区 4："BM25 过时了，不需要用"
❌ BM25 在精确匹配（产品编号、人名、术语）方面仍然碾压向量检索。混合检索的核心价值就是"向量管语义、BM25 管精确"。

---

## 📝 课堂练习

**练习 1**：给定以下两路检索结果，手动计算 RRF 分数（k=60）：
- 向量检索排名：[A, B, C, D]
- BM25 排名：[B, D, A, C]

**练习 2**：为以下查询设计 3 个 Multi-Query 变体：
- "糖水店哪个产品最受欢迎"

**练习 3**：判断以下场景应该用哪种检索策略（纯向量/纯BM25/混合/混合+重排）：
- A. 搜索产品编号 "SKU-12345"
- B. 搜索"适合老人吃的软糯甜品"
- C. 在 10 万篇论文中找和某个课题最相关的 5 篇

---

## ✅ 课后测试

1. RRF 的全称是 ______，它的核心思想是 ______。

2. Cross-Encoder 比 Bi-Encoder 精度更高的原因是 ______。

3. 判断题：HyDE 是先用 LLM 生成查询变体再检索。（  ）

4. 混合检索通常结合 ______ 检索和 ______ 检索。

5. 简答题：为什么说"两阶段检索（初筛+精排）比单阶段更高效"？

---

## 📖 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| Hybrid Search | /ˈhaɪbrɪd sɜːrtʃ/ | 混合检索 | 结合向量和关键词的检索方式 |
| BM25 | /biː ɛm twɛnti-faɪv/ | BM25算法 | 经典关键词检索排序算法 |
| RRF (Reciprocal Rank Fusion) | /ˈrɛsɪprəkəl ræŋk ˈfjuːʒən/ | 倒数排名融合 | 合并多路检索结果的算法 |
| Reranking | /ˌriːˈræŋkɪŋ/ | 重排序 | 对初筛结果二次精确排序 |
| Cross-Encoder | /krɒs ˈɛnkəʊdər/ | 交叉编码器 | 查询和文档联合编码的模型 |
| Bi-Encoder | /baɪ ˈɛnkəʊdər/ | 双编码器 | 查询和文档独立编码的模型 |
| HyDE | /haɪd iː/ | 假设文档嵌入 | 用假设答案做检索的改写策略 |
| Multi-Query | /ˈmʌlti ˈkwɪəri/ | 多查询扩展 | 生成多个查询变体的策略 |
| Recall | /rɪˈkɔːl/ | 召回率 | 相关文档被检索到的比例 |
| Precision | /prɪˈsɪʒən/ | 精确率 | 检索结果中相关的比例 |

---

## 🔗 参考资源

- 📄 [RRF 原始论文（Cormack et al., 2009）](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- 📦 [Cohere Rerank API 文档](https://docs.cohere.com/docs/reranking)
- 📝 [HyDE 论文（Gao et al., 2022）](https://arxiv.org/abs/2212.10496)
- 🎥 [LangChain Advanced RAG 教程](https://python.langchain.com/docs/modules/data_connection/retrievers/)
- 📊 [Cross-Encoder vs Bi-Encoder 对比](https://www.sbert.net/examples/applications/cross-encoder/README.html)

---

> 🚀 **明天预告**：Day 4 我们进入 GraphRAG 的世界——用知识图谱增强 RAG，让它能理解实体之间的复杂关系！"椰奶→椰汁→奶茶"这种链式关系，传统 RAG 搞不定，GraphRAG 可以。
