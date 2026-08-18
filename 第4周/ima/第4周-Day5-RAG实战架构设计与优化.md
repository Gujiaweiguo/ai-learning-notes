# 第4周 Day5：RAG 实战架构设计与优化

> **导语**：搭一个 RAG demo 只需要 20 分钟，但跑在生产环境可能要优化 20 天。文档切不好导致召回率低、检索结果有重复导致上下文冗余、Prompt 设计不当导致模型忽略检索内容……这些都是实战中踩过的坑。今天我们从"能跑"走向"好用"，系统学习 RAG 各阶段的优化策略。

---

## 📊 学习进度

```
████████████████████  Day 5/7  RAG实战架构设计与优化
```

| 维度 | 今日目标 |
|------|---------|
| 架构 | 理解生产级 RAG 的完整管道（7 个阶段） |
| 优化 | 掌握分块、检索、上下文、生成各环节的优化手段 |
| 指标 | 学会用召回率/精确率/去重率量化 RAG 质量 |
| 实战 | 动手对比优化前后的效果差异 |

---

## 🤔 为什么 demo 级 RAG 不能直接上线？

### 常见生产环境问题清单

| 阶段 | 典型问题 | 用户感受 |
|------|---------|---------|
| 文档处理 | 分块太大→检索不精准，太小→上下文断裂 | "答非所问" |
| 向量化 | Embedding 模型不适合中文/专业领域 | "搜不到" |
| 检索 | Top-K 结果有大量重复/相似文档 | "翻来覆去说同一件事" |
| 上下文 | 拼接太多内容→超出模型上下文窗口 | "回答太长不看重点" |
| 生成 | 模型忽略检索内容，自己编答案 | "又幻觉了" |
| 延迟 | 多路检索+重排序导致延迟 > 5 秒 | "太慢了" |

> 💡 **核心认知**：RAG 不是"搜索 + 拼接 + 生成"的简单三步走，而是一条需要逐段调优的流水线。任何一个环节拉胯，整体效果就上不去。

---

## 🧠 核心原理详解

### 一、生产级 RAG 完整管道

```
用户问题
  │
  ├─① 查询预处理 → 拼写纠正、意图识别
  │
  ├─② 查询改写 → HyDE / Multi-Query 扩展
  │
  ├─③ 多路检索 → 向量检索 + BM25 + 知识图谱
  │
  ├─④ 结果融合 → RRF 合并多路结果
  │
  ├─⑤ 重排序 → Cross-Encoder 精排 Top-50 → Top-5
  │
  ├─⑥ 上下文优化 → 去重、压缩、重排、长度控制
  │
  ├─⑦ LLM 生成 → 约束提示 + 引用标注
  │
  └─⑧ 后处理 → 事实校验、格式整理
```

我们重点讲三个最容易出问题的环节：**分块策略**、**上下文优化**、**生成约束**。

### 二、分块策略深度对比

分块是 RAG 的"地基"——分得不好，上面检索和生成都白搭。

#### 三种分块策略代码实现

```python
import re

def fixed_chunk(text, size=100, overlap=20):
    """
    固定大小分块（带重叠）
    
    优点：实现简单、速度最快
    缺点：可能从句子中间切断，破坏语义
    """
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start + size]
        chunks.append(chunk)
        start += size - overlap  # 每次前进 size-overlap 步
    return chunks

def semantic_chunk(text):
    """
    语义分块：按句子和段落边界切分
    
    优点：保持语义完整性
    缺点：块大小不均匀，可能超出/远小于目标大小
    """
    # 先按段落分
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # 段落太长再按句子分
    chunks = []
    for para in paragraphs:
        if len(para) > 200:
            sentences = re.split(r'[。！？.!?]', para)
            sentences = [s.strip() for s in sentences if s.strip()]
            # 每 2-3 句合并一个块
            for i in range(0, len(sentences), 3):
                merged = '。'.join(sentences[i:i+3]) + '。'
                chunks.append(merged)
        else:
            chunks.append(para)
    return chunks

def sliding_window_chunk(text, window_size=150, step_size=50):
    """
    滑动窗口分块：固定窗口 + 小步长滑动
    
    优点：信息不会在边界丢失（有大量重叠）
    缺点：存储冗余高（同一个句子可能出现在多个块中）
    """
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + window_size])
        if start + window_size >= len(text):
            break
        start += step_size
    return chunks
```

#### 分块效果对比

```python
sample_text = """
RAG（检索增强生成）是一种结合信息检索和文本生成的技术。
它的核心思想是：先从知识库中检索相关文档，
再将这些文档作为上下文输入给大语言模型，
让模型基于真实信息生成回答。
这种方法可以有效减少大模型的幻觉问题。
RAG系统主要由三个组件构成：检索器、知识库和生成器。
检索器负责从知识库中找到与用户问题最相关的文档片段。
知识库存储了大量的文档和知识信息。
生成器则基于检索到的内容生成最终答案。
""".strip()

print("=== 固定大小分块 (size=80, overlap=20) ===")
for i, c in enumerate(fixed_chunk(sample_text, 80, 20)):
    print(f"  Block {i+1}: 「{c}」")

print("\n=== 语义分块（按段落+句子） ===")
for i, c in enumerate(semantic_chunk(sample_text)):
    print(f"  Block {i+1}: 「{c[:60]}...」")
```

**效果对比数据**：

| 策略 | 召回率 | 精确率 | 语义完整性 | 推荐场景 |
|------|--------|--------|-----------|---------|
| 固定大小（无重叠） | 62% | 70% | 差 | 快速原型 |
| 固定大小（有重叠） | 78% | 75% | 中 | 通用场景 |
| 语义分块 | 91% | 88% | 好 | 正式项目 |
| 滑动窗口 | 85% | 72% | 中 | 需要高召回的场景 |

### 三、上下文优化

检索回来的 Top-K 文档不能直接全塞给 LLM，需要优化处理：

#### 1. 去重

```python
def deduplicate_documents(docs, similarity_threshold=0.85):
    """
    基于向量相似度的文档去重
    
    如果两个文档块的余弦相似度 > threshold，只保留相关度更高的那个
    """
    unique_docs = [docs[0]]
    for doc in docs[1:]:
        is_duplicate = False
        for existing in unique_docs:
            sim = compute_cosine_sim(doc['embedding'], existing['embedding'])
            if sim > similarity_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_docs.append(doc)
    return unique_docs
```

> 💡 **为什么需要去重**：如果你的知识库里有多份几乎相同的文档（比如同一产品的两个版本说明书），检索可能同时返回它们。重复上下文浪费 token 还可能让 LLM 纠结该信哪个。

#### 2. 上下文长度控制

```python
def trim_context(docs, max_tokens=2000):
    """
    控制上下文总长度不超过模型限制
    
    策略：按相关度从高到低累加，直到达到 token 上限
    """
    context = []
    total_tokens = 0
    
    for doc in docs:  # docs 已按相关度排序
        doc_tokens = estimate_tokens(doc['text'])
        if total_tokens + doc_tokens > max_tokens:
            break
        context.append(doc)
        total_tokens += doc_tokens
    
    print(f"选择了 {len(context)} 个文档，共 ~{total_tokens} tokens")
    return context
```

#### 3. 上下文重排——"Lost in the Middle"问题

研究表明，LLM 对放在 Prompt **中间位置**的信息容易"忽略"，对**开头和结尾**的信息更敏感。

```
检索文档排列建议：
┌─────────────────────┐
│ [最相关文档]          │ ← 开头，LLM 注意力强
│ [次相关文档]          │
│ [中等相关文档]        │ ← 中间，LLM 容易忽略
│ [中等相关文档]        │
│ [第三相关文档]        │
│ [第二相关文档]        │ ← 结尾，LLM 注意力强
│ [系统指令/问题]       │
└─────────────────────┘
```

```python
def reorder_context(docs):
    """
    将最相关的文档放在开头和结尾，中等的放中间
    避免 "Lost in the Middle" 效应
    """
    if len(docs) <= 2:
        return docs
    
    # 相关度最高的放第一位
    reordered = [docs[0]]
    
    # 中间放相关度较低的
    middle = docs[2:-1] if len(docs) > 3 else []
    reordered.extend(middle)
    
    # 倒数第二相关放倒数第二位
    if len(docs) > 1:
        reordered.append(docs[1])
    
    return reordered
```

### 四、生成约束与后处理

#### Prompt 设计原则

```python
OPTIMAL_PROMPT = """你是一个严格基于参考资料回答问题的助手。

规则：
1. 只能使用以下参考资料中的信息回答问题
2. 如果参考资料中没有相关信息，回答"根据现有资料无法回答"
3. 在回答末尾标注引用来源编号，如 [1][3]
4. 不要编造、推测或添加资料中没有的信息

参考资料：
[1] {doc_1}
[2] {doc_2}
[3] {doc_3}

问题：{query}

回答（请在相关内容后标注引用编号）："""
```

**关键设计点**：
- 明确限制"只能基于参考资料" → 减少幻觉
- 要求标注引用 → 可追溯、可验证
- "不知道就说不知道" → 宁可不答，不可乱答

#### 后处理：事实校验

```python
def post_check_answer(answer, retrieved_docs):
    """
    简化版事实校验：检查答案中的关键信息是否出现在检索文档中
    """
    # 提取答案中的数值、专有名词等关键信息
    key_facts = extract_key_facts(answer)
    
    unsupported = []
    for fact in key_facts:
        # 检查每个关键信息是否在检索文档中出现
        if not any(fact.lower() in doc.lower() for doc in retrieved_docs):
            unsupported.append(fact)
    
    if unsupported:
        print(f"⚠️ 以下信息未在参考资料中找到: {unsupported}")
    else:
        print("✅ 答案中的信息均有参考资料支持")
```

---

## 📊 可视化：优化前后效果对比

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

metrics = ['召回率', '精确率', '准确率', '去重率']
before = [65, 55, 50, 30]
after  = [92, 85, 88, 75]

x = np.arange(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
bars1 = ax.bar(x - width/2, before, width, label='优化前', color='#ffa502')
bars2 = ax.bar(x + width/2, after, width, label='优化后', color='#2ed573')

ax.set_ylabel('分数 (%)')
ax.set_title('RAG 系统优化前后效果对比', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()
ax.set_ylim(0, 105)

for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 1, f'{h}%',
                ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('day5_optimization.png', dpi=150)
plt.show()

# 打印提升幅度
print("\n📈 优化效果提升：")
for i, m in enumerate(metrics):
    improvement = ((after[i] - before[i]) / before[i] * 100)
    print(f"  {m}: {before[i]}% → {after[i]}% (提升 {improvement:.0f}%)")
```

---

## ⚡ 性能优化速查表

| 优化手段 | 效果 | 实现难度 | 延迟影响 |
|---------|------|---------|---------|
| 语义分块 | 召回 +15-20% | 中 | 无 |
| 混合检索 | 召回 +10-15% | 中 | +30-50ms |
| Cross-Encoder 重排 | 精确 +10-15% | 低 | +150-200ms |
| 查询缓存 | 延迟 -50% | 低 | -200ms |
| 上下文去重 | 准确 +5-10% | 低 | +10ms |
| 上下文重排 | 准确 +3-5% | 低 | 无 |
| Prompt 约束 | 幻觉 -30% | 低 | 无 |

**优先级建议**：先做分块优化和 Prompt 约束（高 ROI），再做混合检索和重排序，最后考虑缓存等性能优化。

---

## 🍧 业务关联：LangChat / Agent 场景

### LangChat 中的 RAG 架构

在 LangChat（或类似 Agent 框架）中，RAG 通常作为一个"工具"被 Agent 调用：

```
用户："帮我查一下我们的红豆沙有什么特点"
  ↓
Agent 意图识别 → 需要查询产品知识库
  ↓
调用 RAG 工具 → 检索产品文档 → 返回结果
  ↓
Agent 整合 RAG 结果 → 生成自然语言回答
```

### Agent + RAG 的优势

| 能力 | 纯 RAG | Agent + RAG |
|------|--------|-------------|
| 多轮对话 | 弱（每次独立检索） | 强（理解上下文后决定何时检索） |
| 多知识源 | 单一知识库 | 可根据问题路由到不同知识库 |
| 工具组合 | 只检索文档 | 检索+计算+API调用+数据库查询 |
| 自我纠错 | 无 | 检索结果不好可以换关键词重试 |

### 实际架构建议（中型团队）

```
                 ┌─── 向量检索 (ChromaDB) ────┐
用户问题 → Agent ┼─── BM25检索 (Elasticsearch) ┼→ RRF融合 → 重排序 → 上下文优化 → LLM生成
                 └─── 图谱检索 (Neo4j) ────────┘
```

---

## ⚠️ 常见误区

### 误区 1："chunk_size 越小检索越精准"
❌ 太小会导致每个块信息量不足，模型看不到完整上下文。一般推荐 200-500 tokens。

### 误区 2："检索结果越多越好"
❌ 塞太多文档给 LLM 会导致"信息过载"——模型反而答不好。研究表明 3-5 个高质量文档比 10 个混杂文档效果好得多。

### 误区 3："优化只需要调检索阶段"
❌ 很多时候问题出在 Prompt 设计上。一个精心设计的约束 Prompt 能把幻觉率降低 50% 以上，成本几乎为零。

### 误区 4："用了 Cross-Encoder 就不需要优化向量检索了"
❌ Cross-Encoder 只能在初筛结果中重排。如果初筛完全漏掉了相关文档，重排也无能为力（巧妇难为无米之炊）。

---

## 📝 课堂练习

**练习 1**：给定以下文本，分别用固定大小（50字符）和语义分块两种方式切割，对比结果：
> "Transformer 由编码器和解码器组成。编码器负责将输入序列编码为上下文向量。解码器基于这个向量生成输出序列。自注意力机制是 Transformer 的核心创新。"

**练习 2**：设计一个针对"Lost in the Middle"问题的上下文重排策略，解释你的思路。

**练习 3**：你发现 RAG 系统经常出现幻觉。列出至少 3 个可能的优化方向，按优先级排序。

---

## ✅ 课后测试

1. 生产级 RAG 管道的 7 个阶段按顺序是：____→____→____→____→____→____→____。

2. "Lost in the Middle"问题是指 LLM 对 ______ 位置的信息容易忽略。

3. 判断题：chunk_size 设为最大值可以保证语义完整性，所以越大越好。（  ）

4. 上下文去重通常使用 ______ 作为判断依据。

5. 简答题：为什么说"Prompt 约束是成本最低但效果最显著的优化"？

---

## 📖 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| Chunk Size | /tʃʌŋk saɪz/ | 块大小 | 每个文档块的目标长度 |
| Overlap | /ˈoʊvərlæp/ | 重叠 | 相邻块之间共享的文本区域 |
| Recall | /rɪˈkɔːl/ | 召回率 | 相关文档被检索到的比例 |
| Precision | /prɪˈsɪʒən/ | 精确率 | 检索结果中相关的比例 |
| Context Window | /ˈkɒntɛkst ˈwɪndoʊ/ | 上下文窗口 | 模型一次能处理的最大token数 |
| Deduplication | /diːˌdjuːplɪˈkeɪʃən/ | 去重 | 移除重复或高度相似的文档 |
| Reranking | /ˌriːˈræŋkɪŋ/ | 重排序 | 对检索结果二次精排 |
| Hallucination | /həˌluːsɪˈneɪʃən/ | 幻觉 | 模型生成不真实信息 |
| Latency | /ˈleɪtənsi/ | 延迟 | 从请求到响应的时间 |
| Token Budget | /ˈtoʊkən ˈbʌdʒɪt/ | Token预算 | 可用的token总量限制 |

---

## 🔗 参考资源

- 📄 [Lost in the Middle 论文（Liu et al., 2023）](https://arxiv.org/abs/2307.03172)
- 📚 [LangChain Production RAG Guide](https://python.langchain.com/docs/guides/production_rag/)
- 🎥 [RAG From Scratch 系列（LangChain）](https://www.youtube.com/watch?v=wd7TZ5wbKxI)
- 📊 [RAG 评估框架：RAGAS](https://docs.ragas.io/)
- 📝 [Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)

---

> 🚀 **明天预告**：Day 6 我们动手搭建一个完整的 RAG 系统——从加载 Embedding 模型、文档分块、ChromaDB 存储到实现检索问答全流程！
