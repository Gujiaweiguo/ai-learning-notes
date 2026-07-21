# 📚 第2周-Day2：Tokenizer 与词嵌入

> **昨天我们拆解了 Transformer Block 的内部零件（FFN、LayerNorm、残差连接）。今天我们要往前看——在数据进入 Transformer 之前，文字是怎么变成数字的？Tokenizer 负责"切词"，Embedding 负责"赋予含义"。这两个步骤看似简单，却直接决定了大模型能理解什么语言、支持什么长度、处理速度有多快。**

## 📅 学习进度

```
W1 ████████████████████ ✓ 已完成（Transformer 基础架构）
W2 ████████░░░░░░░░░░░░ ← 你在这里（Day 2/7）
W3 ░░░░░░░░░░░░░░░░░░░░ 预训练与数据工程
W4 ░░░░░░░░░░░░░░░░░░░░ 微调与对齐
...
W13 ░░░░░░░░░░░░░░░░░░░░ 综合项目
```

---

## 一、为什么需要 Tokenizer 和词嵌入？

### 问题：计算机不认识文字！

大模型本质上是一个超级计算器，它只能处理数字。但人类使用的是文字——中文、英文、代码、emoji……所以我们需要一个"翻译官"，把文字翻译成数字。

这个过程分为两步：
1. **Tokenizer（分词器）**：把连续的文本切成一个一个的小单元（token）
2. **Embedding（词嵌入）**：把每个 token 变成一个高维向量（数字组成的数组）

**打个比方**：假设你在开一家糖水店，每天要处理大量订单。

- **Tokenizer** 就像是"拆单员"——把一张写满字的订单拆成一道一道的菜品：
  - "两碗红豆沙和一杯凉茶" → ["两碗", "红豆沙", "和", "一杯", "凉茶"]
  
- **Embedding** 就像是"编码员"——给每道菜分配一个唯一的条形码，而且相似的菜编码也相似：
  - "红豆沙" → [0.8, 0.3, -0.2, ...]
  - "绿豆沙" → [0.7, 0.3, -0.1, ...]（跟红豆沙很像！）
  - "凉茶" → [-0.1, 0.9, 0.5, ...]（跟红豆沙差异大）

**没有它们会怎样？**
- 没有 Tokenizer：模型看到的只是一串连续的字符，不知道哪里是一个"词"的开始和结束
- 没有 Embedding：每个 token 只是一个 ID 编号（比如 "红豆沙" = 42），模型无法知道"红豆沙"和"绿豆沙"在语义上很接近

---

## 二、核心原理详解

### 2.1 Tokenizer——文本的"手术刀"

#### 分词的基本方法

| 方法 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| **字符级** | "hello" → ['h','e','l','l','o'] | 词表极小（几百） | 序列太长，语义信息弱 |
| **词级** | "I love coding" → ['I','love','coding'] | 语义完整 | 词表巨大（几十万），OOV 问题 |
| **子词级（Subword）** | "unhappiness" → ['un','happiness'] | 兼顾词表大小和语义 | 算法复杂 |

**现代大模型几乎都使用子词级分词（Subword Tokenization）**，因为它在词表大小和语义表达之间找到了最佳平衡。

#### BPE（Byte Pair Encoding）—— 最主流的分词算法

BPE 的核心思想很简单：**从字符开始，不断合并出现频率最高的字符对**。

训练过程（打个比方）：

想象你在学习一门新语言：
1. 一开始你只认识单个字母：a, b, c, d, e...
2. 你发现 't' 和 'h' 经常一起出现 → 学会了 "th"
3. 你发现 "th" 和 "e" 经常一起出现 → 学会了 "the"
4. 继续合并，直到达到设定的词表大小

**实际训练步骤**：

```
初始词汇表：所有单个字符 {a, b, c, ..., z, 中, 文, ...}

第1轮：统计所有相邻字符对，找到出现最多的对 (t,h) → 合并为 'th'
第2轮：统计所有相邻对（包含新合并的 'th'），找到最多的 → 继续合并
...
第N轮：直到词表大小达到目标（如 50000）
```

**代码示例**：

```python
# 简化版 BPE 训练
from collections import Counter

def bpe_train(corpus, vocab_size=1000):
    """BPE 训练算法简化版"""
    # 第一步：把所有词拆成字符
    word_freqs = Counter(corpus.split())
    splits = {word: list(word) for word in word_freqs}
    
    merges = []
    
    while len(set(char for split in splits.values() for char in split)) < vocab_size:
        # 统计所有相邻字符对
        pair_freqs = Counter()
        for word, freq in word_freqs.items():
            split = splits[word]
            for i in range(len(split) - 1):
                pair_freqs[(split[i], split[i+1])] += freq
        
        if not pair_freqs:
            break
        
        # 找到频率最高的对
        best_pair = pair_freqs.most_common(1)[0][0]
        merges.append(best_pair)
        
        # 合并所有词中的这对字符
        for word in splits:
            split = splits[word]
            i = 0
            while i < len(split) - 1:
                if (split[i], split[i+1]) == best_pair:
                    split[i] = split[i] + split[i+1]
                    del split[i+1]
                else:
                    i += 1
    
        return merges

# 演示
corpus = "low low low low low lower newer newest widest"
merges = bpe_train(corpus, vocab_size=20)
print(f"学到的合并规则: {merges}")
```

#### SentencePiece——多语言分词利器

BPE 的一个问题是：它需要预先分词（把句子拆成词），但中文、日文等语言没有空格分隔。

**SentencePiece** 解决了这个问题——它直接把整段文本当作字节流处理，不需要预分词。

代表模型和它们的 Tokenizer：
- GPT 系列：BPE（基于 tiktoken 库）
- LLaMA / Qwen：SentencePiece BPE
- ChatGLM：SentencePiece

#### 词表大小的影响

| 词表大小 | 代表 | 优点 | 缺点 |
|---------|------|------|------|
| ~30K | BERT, GPT-2 | 内存小，推理快 | 长文本 token 数多 |
| ~65K | LLaMA, Qwen | 中文效率高 | 内存占用大 |
| ~100K | Qwen2, DeepSeek | 多语言友好 | Embedding 层参数爆炸 |

**业务思考**：在 LangChat 中处理中文客服对话时，Qwen（词表 ~151K）比 LLaMA（词表 ~32K）的中文 token 效率高约 2-3 倍，意味着同样长度的对话，Qwen 消耗的 token 更少，推理更快。

### 2.2 Embedding（词嵌入）—— 给 token 赋予"灵魂"

#### 什么是词嵌入？

词嵌入就是把每个 token ID 映射到一个高维向量（通常是 768、4096 甚至更大的维度）。

```
"红豆沙" (token_id=1234)
    ↓
Embedding 查表
    ↓
[0.23, -0.45, 0.89, 0.12, ..., -0.33]  (768维向量)
```

**这个向量是怎么来的？** 它是训练学出来的！Embedding 层本质上是一个巨大的查找表（lookup table），形状是 `(vocab_size, d_model)`，每个 token ID 对应一行向量。

#### 为什么需要高维向量？

一维不够吗？用一个数字来表示 token 的含义？

**打个比方**：如果用一个数字来描述一个人，比如"身高"，那姚明和某个同样身高的陌生人就是"同一个人"了——显然不够。你需要多个维度：身高、体重、年龄、性格、职业……维度越多，区分越精细。

同理，768 维向量可以同时编码 token 的：
- 语法角色（主语/宾语/动词...）
- 语义类别（食物/动作/情感...）
- 情感极性（正面/负面/中性...）
- 时态信息（过去/现在/未来...）
- ……以及很多人类难以命名的抽象维度

#### 经典的词嵌入类比

```
King - Man + Woman ≈ Queen
```

这个著名的等式展示了 Embedding 空间的奇妙性质：向量运算可以对应语义关系！

```
中国 - 北京 + 日本 ≈ 东京
```

#### 词嵌入的进化历程

| 阶段 | 方法 | 特点 |
|------|------|------|
| 第一代 | One-Hot Encoding | 维度=词表大小，所有词正交，无法表达相似性 |
| 第二代 | Word2Vec / GloVe | 低维稠密向量（100-300维），静态嵌入 |
| 第三代 | Contextual Embedding（ELMo, BERT） | 动态嵌入——同一个词在不同语境下向量不同！ |

**动态嵌入的意义**：

"苹果"这个词在不同语境下含义不同：
- "我吃了一个**苹果**" → 水果
- "**苹果**发布了新手机" → 公司

在 BERT/GPT 等模型中，经过注意力层处理后，"苹果"的向量会根据上下文自动调整——这就是上下文感知的词嵌入。

### 2.3 从 Token 到模型输入的完整流程

```
原始文本: "糖水很好喝"
    ↓ Tokenizer
Tokens: ["糖", "水", "很", "好", "喝"]
    ↓ 转换为 ID
IDs: [1234, 5678, 90, 234, 567]
    ↓ Embedding 查表
Embeddings: [[0.2, -0.3, ...], [0.5, 0.1, ...], ...]
    ↓ + 位置编码（明天学！）
Final Input: Embeddings + Positional Encoding
    ↓
进入 Transformer
```

---

## 三、代码实战

### 3.1 用 Python 演示 BPE 分词

```python
from collections import Counter

class SimpleBPE:
    """简化版 BPE 分词器"""
    
    def __init__(self):
        self.merges = []  # 存储合并规则
        self.vocab = {}   # 存储最终词汇表
    
    def train(self, text, num_merges=50):
        """训练 BPE"""
        # 将文本拆成字符级
        words = text.split()
        word_splits = {w: list(w) for w in set(words)}
        word_freqs = Counter(words)
        
        for _ in range(num_merges):
            # 统计字符对频率
            pair_freqs = Counter()
            for word, freq in word_freqs.items():
                split = word_splits[word]
                for i in range(len(split) - 1):
                    pair_freqs[(split[i], split[i+1])] += freq
            
            if not pair_freqs:
                break
            
            # 合并频率最高的对
            best_pair, best_freq = pair_freqs.most_common(1)[0]
            self.merges.append(best_pair)
            
            # 更新所有词的分割
            for word in word_splits:
                split = word_splits[word]
                new_split = []
                i = 0
                while i < len(split):
                    if i < len(split) - 1 and (split[i], split[i+1]) == best_pair:
                        new_split.append(split[i] + split[i+1])
                        i += 2
                    else:
                        new_split.append(split[i])
                        i += 1
                word_splits[word] = new_split
        
        # 构建词汇表
        self.vocab = set()
        for split in word_splits.values():
            self.vocab.update(split)
        return self.vocab
    
    def tokenize(self, word):
        """使用训练好的规则分词"""
        split = list(word)
        for merge in self.merges:
            i = 0
            while i < len(split) - 1:
                if (split[i], split[i+1]) == merge:
                    split[i] = split[i] + split[i+1]
                    del split[i+1]
                else:
                    i += 1
        return split

# 演示
bpe = SimpleBPE()
corpus = "low low low lower newest newest newest wide wider"
vocab = bpe.train(corpus, num_merges=10)
print(f"词汇表: {vocab}")
print(f"合并规则: {bpe.merges}")
print(f"分词测试 'lowest': {bpe.tokenize('lowest')}")
```

### 3.2 词嵌入可视化

```python
import numpy as np

# 模拟词嵌入（实际中这些向量是训练学出来的）
word_embeddings = {
    "红豆": np.array([0.9, 0.8, -0.2, 0.3]),
    "绿豆": np.array([0.85, 0.75, -0.15, 0.25]),  # 跟红豆很像
    "凉茶": np.array([-0.1, 0.6, 0.9, -0.3]),     # 跟豆类差异大
    "糖水": np.array([0.7, 0.9, 0.1, 0.5]),        # 跟红豆有些像
    "咖啡": np.array([-0.3, 0.2, 0.8, -0.7]),      # 跟糖水差异大
}

def cosine_similarity(v1, v2):
    """计算余弦相似度"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# 计算所有词对之间的相似度
words = list(word_embeddings.keys())
print("词嵌入相似度矩阵：")
print(f"{'':8}", end="")
for w in words:
    print(f"{w:>8}", end="")
print()
for w1 in words:
    print(f"{w1:8}", end="")
    for w2 in words:
        sim = cosine_similarity(word_embeddings[w1], word_embeddings[w2])
        print(f"{sim:8.2f}", end="")
    print()
```

---

## 四、可视化理解

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 图1: 分词方法对比
methods = ['字符级\n(Char)', '词级\n(Word)', '子词级\n(BPE)']
seq_lengths = [20, 5, 8]  # 同一句话的分词数量
vocab_sizes = [200, 100000, 50000]
x = np.arange(len(methods))
width = 0.35
ax1 = axes[0]
bars1 = ax1.bar(x - width/2, seq_lengths, width, label='序列长度 (tokens)', color='#3498db')
ax1b = ax1.twinx()
bars2 = ax1b.bar(x + width/2, vocab_sizes, width, label='词表大小', color='#e74c3c')
ax1.set_xticks(x)
ax1.set_xticklabels(methods)
ax1.set_ylabel('序列长度', color='#3498db')
ax1b.set_ylabel('词表大小', color='#e74c3c')
ax1.set_title('三种分词方法对比', fontsize=14, fontweight='bold')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# 图2: 词嵌入空间可视化（2D投影）
np.random.seed(42)
words_zh = ['红豆', '绿豆', '凉茶', '糖水', '咖啡', '奶茶', '果汁', '可乐']
# 模拟 2D 坐标（实际是高维空间的投影）
coords = {
    '红豆':  (0.8, 0.7),
    '绿豆':  (0.7, 0.8),
    '糖水':  (0.6, 0.6),
    '凉茶':  (-0.1, 0.5),
    '奶茶':  (0.4, 0.3),
    '果汁':  (0.3, 0.5),
    '咖啡':  (-0.3, 0.1),
    '可乐':  (-0.4, -0.1),
}
colors = plt.cm.Set2(np.linspace(0, 1, len(words_zh)))
for i, (word, (x, y)) in enumerate(coords.items()):
    axes[1].scatter(x, y, s=200, c=[colors[i]], zorder=5, edgecolors='black')
    axes[1].annotate(word, (x, y), fontsize=12, fontweight='bold',
                     xytext=(10, 5), textcoords='offset points')
axes[1].set_xlim(-0.6, 1.0)
axes[1].set_ylim(-0.3, 1.0)
axes[1].set_title('词嵌入空间（2D 投影示意）', fontsize=14, fontweight='bold')
axes[1].set_xlabel('维度1')
axes[1].set_ylabel('维度2')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/tokenizer_embedding.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 可视化图表已生成！")
```

---

## 五、业务关联

### 与 LangChat / Agent / 企业 AI 的关系

1. **Token 计费与成本控制**：企业使用大模型 API 时按 token 数计费。理解 Tokenizer 让你能准确估算成本——同样是 1000 字中文，GPT-4 可能消耗 600 tokens，而 Qwen 可能只消耗 400 tokens。

2. **上下文长度计算**：LangChat 配置对话历史时，需要计算 token 数量确保不超过模型上下文窗口。不同 Tokenizer 的计算结果差异很大。

3. **多语言支持**：企业部署跨国 AI 客服时，选择 Tokenizer 对中文/日文/阿拉伯文支持好的模型至关重要。SentencePiece 在多语言场景中表现更优。

4. **Embedding 与 RAG**：企业知识库检索（RAG）依赖 Embedding 的质量。理解词嵌入让你更好地选择 Embedding 模型，优化检索准确率。

5. **糖水店场景**：如果你要训练一个糖水店记账助手，你需要：
   - 确保 Tokenizer 能正确分词"红豆沙"、"杨枝甘露"等专有名词
   - 通过微调让 Embedding 层学习这些领域术语的语义关系

---

## 六、常见误区

### 误区 1: "一个汉字就是一个 token"
**纠正**：不一定！在 GPT 系列中，一个汉字通常对应 1-2 个 token；在 Qwen 中，常见汉字通常是 1 个 token，但生僻字可能被拆成多个。Token 不等于字，也不等于词——它是子词级别的单元。

### 误区 2: "Embedding 层就是随机初始化的向量"
**纠正**：虽然初始化时是随机的，但在预训练过程中 Embedding 层会被不断调整，最终学到有意义的语义表示。而且，经过注意力层后，每个 token 的表示会根据上下文动态变化——这才是真正的"理解"。

### 误区 3: "词表越大越好"
**纠正**：不是！词表越大：
- Embedding 层参数越多（vocab_size × d_model）
- 每增加 1000 个词，7B 模型增加约 7M 参数
- 训练更慢，内存占用更大
需要在中文效率、多语言支持和模型大小之间做权衡。

---

## 🧪 课堂练习（5分钟）

1. **概念题**：用 BPE 对以下文本进行 3 轮合并训练："ab ab ab bc bc ab"。写出每轮合并的对和结果。

2. **思考题**：如果用 GPT-4 的 Tokenizer 处理"杨枝甘露很好喝"这句话，大概会产生多少个 token？为什么中文的 token 效率比英文低？

3. **选择题**：以下哪个说法是正确的？
   - A) Embedding 向量的维度越大，模型效果一定越好
   - B) One-Hot 编码可以表达词与词之间的相似性
   - C) BPE 从字符级开始，逐步合并频率最高的对
   - D) SentencePiece 需要预先用空格分词

---

## 📝 课后测试（15分钟）

1. **简答题**：解释 BPE 算法为什么能处理训练时没见过的词（OOV 问题）。

2. **计算题**：一个词表大小为 50000、d_model 为 4096 的模型，Embedding 层有多少参数？占 7B 模型总参数的百分之几？

3. **实践题**：使用 HuggingFace 的 `transformers` 库，分别用 GPT-2 和 Qwen2 的 Tokenizer 对同一句中文分词，比较 token 数量和分词结果。

4. **分析题**：为什么 Word2Vec 的词嵌入被称为"静态"的，而 BERT 的被称为"动态"的？用一个具体例子说明区别。

5. **设计题**：如果你要为一家糖水店设计一个垂直领域的 Tokenizer，你会怎么构建词表？需要包含哪些特殊 token？

---

## 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| Tokenization | [ˈtoʊkɪnaɪzeɪʃən] | 分词，将连续文本切分为离散 token 的过程 |
| Token | [ˈtoʊkɪn] | 文本的最小处理单元，可以是字、词或子词 |
| Vocabulary | [vəˈkæbjələri] | 词汇表，模型能识别的所有 token 的集合 |
| BPE (Byte Pair Encoding) | [baɪt peər ɪnˈkoʊdɪŋ] | 字节对编码，通过频率合并生成子词词表的主流算法 |
| SentencePiece | [ˈsentəns piːs] | 直接处理原始文本的多语言分词库 |
| Embedding | [ɪmˈbɛdɪŋ] | 词嵌入，将 token ID 映射为高维稠密向量的过程 |
| One-Hot Encoding | [wʌn hɒt ɪnˈkoʊdɪŋ] | 独热编码，每个词用一个仅含一个 1 的稀疏向量表示 |
| Cosine Similarity | [ˈkoʊsaɪn ˌsɪməˈlærəti] | 余弦相似度，衡量两个向量方向的相似程度 |
| OOV (Out-of-Vocabulary) | [aʊt əv vəˈkæbjələri] | 词表外词，训练时未见过的新词 |
| Contextual Embedding | [kənˈtɛkstʃuəl ɪmˈbɛdɪŋ] | 上下文感知的词嵌入，同一词在不同语境下向量不同 |

---

## 📎 参考资源

- 📄 [Neural Machine Translation of Rare Words with Subword Units (Sennrich et al., 2015)](https://arxiv.org/abs/1508.07909) - BPE 原始论文
- 📄 [SentencePiece: A simple and language independent subword tokenizer](https://arxiv.org/abs/1808.06226) - SentencePiece 论文
- 📄 [Efficient Estimation of Word Representations in Vector Space (Word2Vec)](https://arxiv.org/abs/1301.3781) - 经典词嵌入论文
- 🎥 [HuggingFace NLP Course - Tokenizers](https://huggingface.co/learn/nlp-course/chapter2/en) - 实战教程
- 🔧 [tiktoken (OpenAI)](https://github.com/openai/tiktoken) - GPT 系列快速分词器
- 🔧 [The Illustrated Word2Vector - Jay Alammar](https://jalammar.github.io/illustrated-word2vec/) - 图解词嵌入

---

> 💡 **明日预告**：Day 3 我们将从宏观视角对比 GPT 和 BERT 两大架构——同样是 Transformer，为什么 GPT 适合"写文章"，BERT 适合"做分类"？两者的底层设计有什么根本差异？
