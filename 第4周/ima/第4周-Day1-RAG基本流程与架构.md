# 第4周 Day1：RAG基本流程与架构

> **导语**：你让一个聪明人回答问题，他可能博闻强识，但总有知识盲区。如果你在他回答之前，先递给他一本相关的参考书，让他"翻翻书再答"——这就是 RAG（Retrieval-Augmented Generation，检索增强生成）的核心思想。今天我们从零理解 RAG 的四步核心流程，搞清楚它为什么成为大模型落地的"标配"技术。

---

## 📊 学习进度

```
██████████░░░░░░░░░░  Day 1/7  RAG基本流程与架构
```

| 维度 | 今日目标 |
|------|---------|
| 概念 | 理解 RAG 的"先检索后生成"范式 |
| 架构 | 掌握文档处理→向量化→检索→生成四步流程 |
| 技术栈 | 了解 Embedding 模型、向量数据库、检索策略的选型 |
| 实战 | 用 Python 模拟完整的 RAG 管道 |

---

## 🤔 为什么需要 RAG？

### 大模型的"先天不足"

假设你开了一家糖水店，雇了一个北大毕业的店员。他记忆力惊人、口才极好，但你问他"今天的红豆沙用了哪批红豆"，他答不上来——因为他不知道你店里今天发生的事。

大语言模型就是这个"店员"：
- **训练数据有截止日期**：无法知道最新发生的事
- **不了解你的私有数据**：企业内部文档、个人笔记它都没见过
- **会"一本正经地胡说八道"**：也就是所谓的"幻觉"（Hallucination）
- **无法追溯信息来源**：你不知道它的回答依据是什么

### RAG 的解决思路

RAG 的逻辑特别朴素：**不要让模型"背"所有知识，而是在它回答之前，先帮它"查资料"**。

> 💡 **生活类比**：考试时开卷答题。模型本身提供"理解和表达能力"（语言能力），RAG 负责"递参考书"（知识供给）。你不需要把图书馆背下来，只需要知道怎么查、查到后怎么用。

### RAG vs 传统 LLM 对比

| 维度 | 纯 LLM | RAG 增强 |
|------|--------|----------|
| 知识时效性 | 训练截止日期后的事不知道 | 随时更新知识库即可 |
| 回答准确性 | 可能产生幻觉 | 基于检索到的真实文档 |
| 私有数据 | 完全不了解 | 企业内部知识轻松接入 |
| 可解释性 | "我就是这样生成的" | "根据以下文档……" |
| 维护成本 | 需要重新训练模型 | 只需更新知识库 |

---

## 🧠 核心原理详解：RAG 四步流程

RAG 的完整流程可以拆成四个阶段，我用"图书馆找资料"的类比来解释。

### Step 1：文档收集与切割（图书管理员分书）

**目标**：把原始文档变成可检索的"小卡片"。

为什么要切割？因为一篇 5000 字的文章，整体做向量表示会丢失细节信息。就像你查字典不会翻整本，而是按词条查。

```python
def chunk_documents(texts, chunk_size=512):
    """
    将大文档切割成小的可检索片段
    
    参数:
        texts: 原始文本列表
        chunk_size: 每个片段的最大字符数
    
    返回:
        chunks: 切割后的文档片段列表
    """
    chunks = []
    for text in texts:
        # 优先按段落（双换行）切割，保留语义完整性
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para) > chunk_size:
                # 超长段落递归切割
                for i in range(0, len(para), chunk_size):
                    chunks.append(para[i:i + chunk_size])
            else:
                chunks.append(para)
    return chunks
```

**三种切割策略对比**：

| 策略 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 固定大小切割 | 每 N 个字符切一刀 | 实现简单、速度最快 | 可能从句子中间切断 |
| 语义边界切割 | 按段落、句子边界切 | 保持语义完整 | 块大小不均匀 |
| 滑动窗口切割 | 块之间有重叠区域 | 避免边界信息丢失 | 存储冗余 |

> 🎯 **类比**：固定切割像用菜刀直接切蛋糕——一刀下去可能切到樱桃中间；语义切割像沿着樱桃之间的缝隙切——每块都完整好看。

### Step 2：向量化与存储（给每张卡片编号入柜）

**目标**：把文字变成 AI 能理解的数学向量，存到"向量数据库"里。

这是 RAG 最核心的一步。Embedding 模型能把一段文字"翻译"成一个高维向量（比如 384 维或 768 维的浮点数数组）。语义相近的文本，向量在空间中也更接近。

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# 加载多语言 Embedding 模型（支持中文）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 把文档片段转换成向量
documents = ["红豆沙是经典粤式糖水", "芒果布丁口感清爽", "芋圆Q弹有嚼劲"]
vectors = model.encode(documents)

print(f"向量形状: {vectors.shape}")  # (3, 384) — 3条文本，每条384维
print(f"每条文本被表示为 {vectors.shape[1]} 维向量")
```

**为什么需要向量化？**

想象一个二维坐标系：
- "红豆沙"和"绿豆沙"在这个空间里靠得很近（都是豆类甜品）
- "红豆沙"和"手机壳"在空间里距离很远（语义不相关）
- 当用户问"有什么豆类甜品"时，查询向量会落在"豆类甜品"区域，最近的几个点就是答案

实际使用的是 384~768 维空间，原理一样，只是维度更高、表达能力更强。

### Step 3：检索（从柜子里找到最相关的卡片）

**目标**：用户提问时，从向量数据库中找到最相关的 Top-K 个文档片段。

```python
from sklearn.metrics.pairwise import cosine_similarity

def search_documents(query, doc_vectors, doc_texts, top_k=3):
    """
    向量检索：找到与查询最相关的文档
    
    参数:
        query: 用户查询文本
        doc_vectors: 文档向量矩阵
        doc_texts: 文档原文列表
        top_k: 返回最相关的前K条
    """
    # 将查询转换为向量
    query_vec = model.encode([query])
    
    # 计算查询与所有文档的余弦相似度
    similarities = cosine_similarity(query_vec, doc_vectors)[0]
    
    # 按相似度降序排列，取前K个
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # 返回结果
    results = []
    for idx in top_indices:
        results.append({
            'text': doc_texts[idx],
            'score': float(similarities[idx])
        })
    return results
```

**余弦相似度**衡量的是两个向量"方向"的一致性，取值范围 [-1, 1]，越接近 1 表示越相似。它不关心向量长度，只关心方向——就像两个人可能在不同的跑道上跑步，但如果方向一致，就是"相似的"。

### Step 4：增强生成（拿着卡片回答问题）

**目标**：把检索到的文档片段拼到提示词（Prompt）中，让大模型基于这些材料生成回答。

```python
def rag_generate(query, retrieved_docs):
    """
    将检索结果拼接为增强提示词
    """
    # 拼接检索到的文档作为上下文
    context = "\n\n".join([f"[参考资料{i+1}] {doc['text']}" 
                           for i, doc in enumerate(retrieved_docs)])
    
    # 构建增强提示词
    prompt = f"""请根据以下参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明。

{context}

用户问题：{query}

请回答："""
    
    return prompt
```

> 💡 **关键点**：RAG 不是让模型"自由发挥"，而是给它画一条"只能基于参考资料回答"的框框。这大大减少了幻觉。

---

## 📊 可视化：RAG vs 传统 LLM 能力对比

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np

# 中文字体配置（必须配置否则中文显示为方块）
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

# 对比数据
categories = ['知识更新', '准确性', '幻觉控制', '私有数据', '推理能力']
rag_scores = [9, 8, 7, 10, 6]
llm_scores = [3, 5, 2, 1, 9]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(x - width/2, rag_scores, width, label='RAG', color='#ff6b6b')
ax.bar(x + width/2, llm_scores, width, label='传统LLM', color='#4ecdc4')

ax.set_ylabel('评分 (1-10)')
ax.set_title('RAG vs 传统LLM 能力对比')
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=30)
ax.legend()
ax.set_ylim(0, 11)

plt.tight_layout()
plt.savefig('day1_rag_vs_llm.png', dpi=150)
plt.show()
```

**观察要点**：RAG 在知识更新、准确性、私有数据方面大幅领先；但纯推理能力上，传统 LLM 更强（因为 RAG 的推理依赖检索质量）。这就是为什么实际系统往往两者结合使用。

---

## 🏗️ RAG 核心组件技术栈

一个完整的 RAG 系统由五层组成：

### 1. 文档处理层
- **加载器**：支持 PDF、Word、HTML、Markdown 等多种格式
- **切割器**：固定切割 / 语义切割 / 滑动窗口
- **清洗器**：去噪、标准化（去掉 HTML 标签、特殊字符等）

### 2. 向量化层
| 模型 | 语言 | 维度 | 特点 |
|------|------|------|------|
| text2vec-base | 中文 | 768 | 中文效果好 |
| bge-large-zh | 中文 | 1024 | 开源SOTA |
| paraphrase-multilingual | 多语言 | 384 | 轻量通用 |
| text-embedding-ada-002 | 多语言 | 1536 | OpenAI商业API |

### 3. 存储检索层
| 数据库 | 定位 | 适用场景 |
|--------|------|---------|
| FAISS | 轻量库 | 原型开发、本地实验 |
| ChromaDB | 轻量DB | 小型应用、开发测试 |
| Milvus | 企业级 | 大规模生产环境 |
| Pinecone | 云服务 | 免运维SaaS |
| PostgreSQL+pgvector | 扩展方案 | 已有PG架构的团队 |

### 4. 检索增强层
- 纯语义检索：基础方案
- 混合检索：BM25 + 向量（明天到 Day3 深入讲）
- 重排序（Reranking）：Cross-Encoder 精排

### 5. 生成输出层
- 开源模型：Qwen2、Llama3、ChatGLM3
- 商业API：GPT-4、Claude、Gemini
- 提示词工程：引导模型有效利用检索内容

---

## 🍧 业务关联：糖水店的 RAG 应用

### 场景 1：智能客服

顾客在微信问："你们有不辣的、适合小孩喝的糖水吗？"

**没有 RAG 的情况**：模型只能泛泛而谈"糖水一般都不辣……"

**有 RAG 的情况**：
1. 检索到店铺产品文档："红豆沙（温和滋补）、芝麻糊（香甜浓稠）适合儿童"
2. 检索到顾客评价："很多家长带孩子来都会点红豆沙"
3. 回答："推荐我们的招牌红豆沙，温和滋补、甜度适中，很多小朋友都喜欢。另外芝麻糊也是不错的选择。"

### 场景 2：经营问答

店主问："上个月哪款糖水卖得最好？为什么？"

RAG 系统从销售记录、顾客反馈、天气数据中检索相关信息，生成分析性回答。

### 技术选型建议（轻量方案）

```
文档存储 → 飞书文档 / Notion
向量数据库 → ChromaDB（本地部署，零配置）
Embedding → paraphrase-multilingual-MiniLM-L12-v2（384维，速度快）
LLM → Qwen2-7B（本地）或 API 调用
```

---

## ⚠️ 常见误区

### 误区 1："RAG 就是搜索引擎"
❌ 搜索引擎返回文档列表就结束了；RAG 还要把检索结果喂给大模型，生成自然语言回答。RAG = 搜索 + 生成。

### 误区 2："文档丢进去就能用"
❌ 文档质量决定 RAG 效果。如果文档格式混乱、内容过时、充满冗余信息，再好的模型也救不了。"Garbage In, Garbage Out"。

### 误区 3："RAG 可以完全替代微调"
❌ RAG 解决"知识注入"问题，微调解决"能力提升"问题。如果你的模型本身逻辑推理能力不足，给它再多参考资料也没用。两者往往配合使用。

### 误区 4："向量检索就是关键词搜索的高级版"
❌ 关键词搜索是"字面匹配"——搜"苹果"只会找包含"苹果"两个字的文档。向量检索是"语义匹配"——搜"苹果"可能找到"iPhone"相关文档，因为它们在语义空间中相近。

---

## 📝 课堂练习

**练习 1（概念理解）**：
用你自己的话解释 RAG 的四步流程，不超过 100 字。

**练习 2（切割策略选择）**：
以下场景分别适合哪种切割策略？
- A. 一本 300 页的技术手册（章节结构清晰）
- B. 客服聊天记录（每条消息独立）
- C. 产品规格说明书（表格+长段落混合）

**练习 3（架构设计）**：
为一家有 500 篇产品文档的公司设计 RAG 架构，列出你会选择的：
- Embedding 模型及原因
- 向量数据库及原因
- 切割策略及参数

---

## ✅ 课后测试

1. RAG 的四个核心步骤按顺序是：____ → ____ → ____ → ____

2. 以下哪个不是文档切割策略？（  ）
   A. 固定大小切割
   B. 语义边界切割
   C. 随机切割
   D. 滑动窗口切割

3. 判断题：RAG 系统中，Embedding 模型的选择不影响最终回答质量。（  ）

4. 余弦相似度的取值范围是 ______，越接近 ______ 表示越相似。

5. 简答题：为什么说"RAG 减少了大模型的幻觉问题"？

---

## 📖 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| Retrieval-Augmented Generation | /rɪˈtriːvəl ɔːɡˈmɛntɪd ˌdʒɛnəˈreɪʃən/ | 检索增强生成 | 先检索后生成的大模型增强范式 |
| Embedding | /ɛmˈbɛdɪŋ/ | 向量嵌入/向量化 | 将文本转换为数学向量的技术 |
| Vector Database | /ˈvɛktər ˈdeɪtəbeɪs/ | 向量数据库 | 专门存储和检索高维向量的数据库 |
| Chunking | /ˈtʃʌŋkɪŋ/ | 文档切割/分块 | 将长文档分割成可检索的小片段 |
| Cosine Similarity | /ˈkoʊsaɪn ˌsɪmɪˈlærɪti/ | 余弦相似度 | 衡量向量方向一致性的指标 |
| Hallucination | /həˌluːsɪˈneɪʃən/ | 幻觉 | 大模型生成不真实信息的现象 |
| Top-K | /tɒp keɪ/ | 前K个 | 检索结果中相关度最高的K条 |
| Semantic Search | /sɪˈmæntɪk sɜːrtʃ/ | 语义搜索 | 基于语义而非关键词的检索方式 |
| Prompt Engineering | /prɒmpt ˌɛndʒɪˈnɪərɪŋ/ | 提示词工程 | 设计优化模型输入提示的技术 |
| BM25 | /biː ɛm twɛnti-faɪv/ | BM25算法 | 经典的关键词检索排序算法 |

---

## 🔗 参考资源

- 📄 [RAG 原始论文（Lewis et al., 2020）](https://arxiv.org/abs/2005.11401)
- 📚 [LangChain RAG 教程](https://python.langchain.com/docs/use_cases/question_answering/)
- 🛠️ [ChromaDB 官方文档](https://docs.trychroma.com/)
- 📦 [Sentence-Transformers 模型库](https://www.sbert.net/)
- 🎥 [Andrej Karpathy: State of GPT（含RAG讨论）](https://www.youtube.com/watch?v=bZQun8Y4L2A)

---

> 🚀 **明天预告**：Day 2 我们深入向量检索的核心——Embedding 模型原理与相似度计算方法，动手计算真实文本之间的语义相似度！
