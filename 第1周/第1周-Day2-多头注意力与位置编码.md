# 📚 第1周-Day2：多头注意力与位置编码

> **昨天的知识还有温度，今天我们给它装上"多只眼睛"。** Self-Attention 让每个词看到了其他所有词，但只有一个"视角"。今天我们让模型拥有多个视角——多头注意力。同时，我们还要解决一个昨天悄悄忽略的问题：词的顺序。

## 📅 学习进度

```
W1 ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░  ← 你在这里（Day 2）
W2 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
...
W13 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

**当前位置：W1 Day 2/7**

---

## 一、为什么需要多头注意力和位置编码？

### 🤔 问题一：一个"头"够用吗？

昨天的 Self-Attention 只有一组 Q/K/V。这就像你只有一双眼睛——只能从一个角度看问题。

**现实中的类比**：

读一篇文章时，你其实同时在关注多个层面：
- **语法层**：主谓宾结构对不对？
- **语义层**：这句话是什么意思？
- **情感层**：这句话是正面还是负面？
- **指代层**："他"指的是谁？

如果只有一组 Q/K/V，模型只能学到一种注意力模式。但语言是复杂的，我们需要**多个"头"同时关注不同的模式**。

### 🤔 问题二：词的顺序怎么办？

这里有个昨天我们"悄悄忽略"的问题：**Self-Attention 本身不知道词的顺序！**

为什么？因为注意力的计算是对称的——它只看 Q 和 K 的匹配度，不看位置。换句话说：

- "我爱你" → 注意力计算出来的结果
- "你爱我" → 注意力计算出来的结果

**如果没有任何位置信息，这两句话对模型来说是"一样"的！**

这显然不行。中文里"我打你"和"你打我"意思完全相反（一个你是受害者，一个你是施暴者）。模型必须知道词的顺序。

### 💡 解决方案

| 问题 | 解决方案 | 比喻 |
|------|---------|------|
| 单一视角不够 | **多头注意力** | 一群人从不同角度同时看一篇文章 |
| 缺少顺序信息 | **位置编码** | 给每个位置发一张"身份证" |

---

## 二、核心原理详解

### 2.1 多头注意力（Multi-Head Attention）

#### 🎯 核心思想：把大维度拆成多个小维度

假设模型维度 d_model = 512，我们用 8 个头。每个头的维度 = 512 / 8 = 64。

**打个比方**：你有一个 512 平方米的仓库（d_model），把它分成 8 个 64 平方米的小房间（head），每个房间关注不同类型的货物。

#### 📐 计算过程

```
第1步：生成完整的 Q, K, V（和昨天一样）
    Q = X × W_q   shape: (seq_len, d_model)

第2步：按头切分
    Q_head_1 = Q[:, 0:64]      # 第1个头只看前64维
    Q_head_2 = Q[:, 64:128]    # 第2个头看接下来的64维
    ...
    Q_head_8 = Q[:, 448:512]   # 第8个头看最后64维

第3步：每个头独立计算 Self-Attention
    head_1 = Attention(Q_1, K_1, V_1)  # 各算各的
    head_2 = Attention(Q_2, K_2, V_2)
    ...
    head_8 = Attention(Q_8, K_8, V_8)

第4步：拼接所有头的输出
    multi_output = Concat(head_1, head_2, ..., head_8)
    # 拼接后维度恢复为 d_model

第5步：最后过一次线性投影
    final_output = multi_output × W_O
    # W_O 是模型学习的投影矩阵
```

#### 🌍 每个头学到了什么？

研究表明，不同的头确实学到了不同的模式：

- 有的头关注**相邻词**（比如"非常"关注后面的"好"）
- 有的头关注**句法关系**（比如动词关注它的宾语）
- 有的头关注**指代消解**（比如"他"关注前面的人名）
- 有的头关注**全局信息**（关注句号或关键标点）

**打个比方**：就像公司里不同岗位的人——销售关注客户需求、财务关注成本、技术关注架构。多头并行工作，最后汇总各自的信息。

#### 📐 维度关系公式

```
d_model = num_heads × head_dim
```

常见配置：
- GPT-2 小模型：d_model=768, 12头, 每头64维
- GPT-3：d_model=12288, 96头, 每头128维
- BERT-Base：d_model=768, 12头, 每头64维

### 2.2 位置编码（Positional Encoding）

#### 🎯 核心思想：给每个位置一个独特的"指纹"

位置编码是一组固定的向量，每个位置（第1个词、第2个词...）都有一个独特的向量。把这个向量**加到**词向量上，模型就能区分位置了。

**打个比方**：你去电影院看电影，每个人（词）有自己的座位号（位置编码）。虽然两个人长得一样（相同词向量），但座位号不同，所以系统能区分"第3排的人"和"第5排的人"。

#### 📐 正弦余弦编码公式

原始 Transformer 用的是固定的正弦/余弦编码：

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

其中：
- `pos` = 词在句子中的位置（0, 1, 2, ...）
- `i` = 维度索引（0, 1, 2, ..., d_model/2-1）
- `d_model` = 模型维度

**这个公式在做什么？**

不同维度用不同频率的正弦/余弦波。低维用高频（变化快），高维用低频（变化慢）。

**打个比方**：就像时钟——秒针转得快（高频），分针中等，时针转得慢（低频）。每个时刻，三根针的组合都是唯一的。同理，每个位置的编码向量也是唯一的。

#### 🔑 为什么用 sin/cos 而不是直接用位置数字？

1. **数值稳定性**：直接用 1, 2, 3... 当位置数字，句子长了数字就很大，和词向量不在一个量级
2. **相对位置**：sin/cos 有个美妙的数学性质——位置 pos+k 的编码可以通过位置 pos 的编码做线性变换得到，模型容易学到相对关系
3. **泛化能力**：可以处理训练时没见过的更长序列

#### 📐 最终输入

```
最终输入 = 词向量 + 位置编码
X_final = X + PE[0:seq_len]
```

注意是**加法**，不是拼接！因为维度相同（都是 d_model），直接逐元素相加。

---

## 三、代码实战

### 3.1 多头注意力实现

```python
import numpy as np
import math

np.random.seed(42)

# ========== 配置 ==========
seq_len = 4        # 句子长度：4个词
d_model = 8        # 模型维度
num_heads = 2      # 头数
head_dim = d_model // num_heads  # 每头维度 = 4

print(f"模型维度: {d_model}, 头数: {num_heads}, 每头维度: {head_dim}")
print(f"验证: {num_heads} × {head_dim} = {num_heads * head_dim}")

# ========== 准备输入 ==========
X = np.random.randn(seq_len, d_model)  # 4个词，每个8维

# ========== 生成 Q, K, V ==========
W_q = np.random.randn(d_model, d_model)
W_k = np.random.randn(d_model, d_model)
W_v = np.random.randn(d_model, d_model)

Q = X @ W_q   # (4, 8)
K = X @ W_k   # (4, 8)
V = X @ W_v   # (4, 8)

# ========== 按头切分 ==========
# reshape 为 (seq_len, num_heads, head_dim)
Q_heads = Q.reshape(seq_len, num_heads, head_dim)
K_heads = K.reshape(seq_len, num_heads, head_dim)
V_heads = V.reshape(seq_len, num_heads, head_dim)

print(f"\n切分后 Q shape: {Q_heads.shape}")
print("每个头独立计算注意力 ↓")

# ========== 每个头独立计算 ==========
def softmax(x):
    """数值稳定的 softmax"""
    x_shifted = x - x.max(axis=-1, keepdims=True)
    exp_x = np.exp(x_shifted)
    return exp_x / exp_x.sum(axis=-1, keepdims=True)

outputs = []
for h in range(num_heads):
    # 取第 h 个头的数据
    q = Q_heads[:, h, :]   # (seq_len, head_dim)
    k = K_heads[:, h, :]
    v = V_heads[:, h, :]

    # 计算注意力（和昨天的公式一样）
    scores = q @ k.T / math.sqrt(head_dim)  # 缩放
    weights = softmax(scores)
    out = weights @ v
    outputs.append(out)

    print(f"\n--- 头 {h} ---")
    print(f"注意力权重:\n{np.round(weights, 3)}")

# ========== 拼接所有头 ==========
multi_out = np.concatenate(outputs, axis=-1)  # (seq_len, d_model)
print(f"\n拼接后 shape: {multi_out.shape}")

# ========== 最终线性投影 ==========
W_O = np.random.randn(d_model, d_model)
final_output = multi_out @ W_O
print(f"最终输出 shape: {final_output.shape}")
print("多个头的输出拼接 → 再过一次线性投影 → 最终输出")
```

### 3.2 位置编码实现

```python
# ========== 正弦余弦位置编码 ==========
max_len = 20       # 最大句子长度
d_model = 8        # 维度（要和词向量维度一致）

pos = np.arange(max_len).reshape(-1, 1)          # 位置：0,1,2,...,19
dim = np.arange(d_model).reshape(1, -1)           # 维度：0,1,...,7

PE = np.zeros((max_len, d_model))
# 偶数维用 sin
PE[:, 0::2] = np.sin(pos / (10000 ** (dim[:, 0::2] / d_model)))
# 奇数维用 cos
PE[:, 1::2] = np.cos(pos / (10000 ** (dim[:, 1::2] / d_model)))

print("位置编码矩阵 (前5个位置):")
print(np.round(PE[:5], 3))

# ========== 把位置编码加到词向量上 ==========
# 假设 X 是词向量 (seq_len, d_model)
seq_len = 4
X = np.random.randn(seq_len, d_model)
X_encoded = X + PE[0:seq_len]  # 逐元素相加！

print(f"\n原始词向量 [0]: {np.round(X[0], 3)}")
print(f"位置编码   [0]: {np.round(PE[0], 3)}")
print(f"加位置后   [0]: {np.round(X_encoded[0], 3)}")
print("\n✅ 每个位置都有独特的编码向量")
print("加到词向量上：X_encoded = X + PE[0:seq_len]")
```

### 3.3 单头 vs 多头对比

```python
# 对比单头和多头的注意力权重差异

np.random.seed(42)
seq_len, d_model, num_heads = 3, 8, 2
d_k = d_model // num_heads

X = np.random.randn(seq_len, d_model)

# 单头注意力
W_q = np.random.randn(d_model, d_model)
W_k = np.random.randn(d_model, d_model)
W_v = np.random.randn(d_model, d_model)
Q = X @ W_q; K = X @ W_k; V = X @ W_v

scores = (Q @ K.T) / np.sqrt(d_model)
single_attn = softmax(scores)

# 多头注意力
Q_heads = np.hsplit(Q, num_heads)
K_heads = np.hsplit(K, num_heads)
V_heads = np.hsplit(V, num_heads)

print("单头注意力权重:")
print(np.round(single_attn, 3))

for i in range(num_heads):
    s = (Q_heads[i] @ K_heads[i].T) / np.sqrt(d_k)
    a = softmax(s)
    print(f"\n多头 - 头{i+1}注意力权重:")
    print(np.round(a, 3))

print("\n💡 两个头关注的角度不同！拼接后信息更丰富")
```

---

## 四、可视化理解

### 4.1 位置编码热力图

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

# 计算位置编码
max_len, d_model = 20, 16
PE = np.zeros((max_len, d_model))
pos = np.arange(max_len).reshape(-1, 1)
dim = np.arange(d_model).reshape(1, -1)
PE[:, 0::2] = np.sin(pos / (10000 ** (dim[:, 0::2] / d_model)))
PE[:, 1::2] = np.cos(pos / (10000 ** (dim[:, 1::2] / d_model)))

# 画热力图
fig, ax = plt.subplots(figsize=(10, 4))
im = ax.imshow(PE[:10], cmap='RdBu', aspect='auto')
ax.set_xlabel('维度', fontsize=12)
ax.set_ylabel('位置', fontsize=12)
ax.set_title('正弦位置编码热力图', fontsize=14)
plt.colorbar(im, label='编码值')
plt.tight_layout()
plt.savefig('positional_encoding.png', dpi=150)
plt.show()
print("图表已保存为 positional_encoding.png")
```

**如何看这个图**：
- 每一行代表一个位置（词的位置）
- 每一列代表一个维度
- 颜色深浅代表编码值的大小
- 可以看到低维度（左侧）变化快（高频），高维度（右侧）变化慢（低频）

### 4.2 多头注意力对比图

```python
# 可视化两个头的注意力差异
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 模拟两个头的注意力权重
head1_weights = np.array([
    [0.7, 0.2, 0.1],
    [0.1, 0.8, 0.1],
    [0.15, 0.15, 0.7],
])
head2_weights = np.array([
    [0.1, 0.3, 0.6],
    [0.4, 0.1, 0.5],
    [0.2, 0.5, 0.3],
])

words = ["小明", "喜欢", "AI"]

for idx, (weights, title) in enumerate([
    (head1_weights, "头1：关注语法结构"),
    (head2_weights, "头2：关注语义关系"),
]):
    ax = axes[idx]
    im = ax.imshow(weights, cmap='YlOrRd')
    ax.set_xticks(range(len(words)))
    ax.set_yticks(range(len(words)))
    ax.set_xticklabels(words, fontsize=12)
    ax.set_yticklabels(words, fontsize=12)
    ax.set_title(title, fontsize=13)
    for i in range(len(words)):
        for j in range(len(words)):
            ax.text(j, i, f'{weights[i][j]:.2f}',
                    ha='center', va='center', fontsize=12,
                    color='white' if weights[i][j] > 0.5 else 'black')

plt.suptitle('多头注意力：不同头关注不同模式', fontsize=14)
plt.tight_layout()
plt.savefig('multi_head_attention.png', dpi=150)
plt.show()
```

---

## 五、业务关联

### 🏪 多头注意力在 LangChat/Agent 中的实际意义

**1. Agent 的多维度理解**

当用户对 Agent 说"帮我查一下库存，顺便提醒我下午3点开会"：
- 头1可能关注**动作**（查库存、提醒）
- 头2可能关注**时间**（下午3点）
- 头3可能关注**对象**（库存、开会）
- 多个头的输出拼接，模型就能完整理解这个复合指令

**2. 企业知识库的精准搜索**

做企业搜索时，用户可能输入"去年的财务报表在哪"。多头注意力让模型同时关注：
- 语义维度："财务报表" → 找财务文档
- 时间维度："去年" → 过滤时间范围
- 意图维度："在哪" → 这是在找文件位置

**3. 糖水店 AI 客服的案例**

当顾客问"你们有什么不甜的"，多头注意力让模型：
- 头1关注"不甜" → 低糖产品
- 头2关注隐含意图 → 健康饮食需求
- 头3关注推荐场景 → 适合推荐无糖茶饮

**Jason 的实际场景**：在设计 LangChat 的对话引擎时，多头注意力确保模型不会"只看一个角度"。比如处理用户投诉时，既要理解投诉内容，也要感知情绪强度，还要关联历史对话——这些都需要不同的"头"来处理。

---

## 六、常见误区

### ❌ 误区1："头越多越好"

**纠正**：不是！头数增加，每个头的维度就减少（因为 d_model = num_heads × head_dim）。维度太少，每个头的表达能力下降。研究表明，8-16 个头是大多数场景的甜蜜点。GPT-3 用了 96 个头，但那是因为它的 d_model=12288，每个头仍有 128 维。

### ❌ 误区2："位置编码必须是 sin/cos"

**纠正**：原始论文用的是 sin/cos，但后来的模型有不同做法：
- BERT 用的是**可学习的位置编码**（像词向量一样训练出来）
- GPT 系列用的是**旋转位置编码（RoPE）**——现在最主流的方案
- ALBERT 用的是**相对位置编码**

### ❌ 误区3："位置编码和词向量是独立的"

**纠正**：位置编码直接加到词向量上后，后续所有计算（Q/K/V 变换、注意力计算）都在用这个"加了位置信息的向量"。所以位置信息会渗透到整个网络中。

---

## 🧪 课堂练习（5分钟）

**题目1**：如果 d_model=512，用 8 个头，每个头的维度是多少？

**题目2**：位置编码为什么用加法而不是拼接？如果拼接，维度会变成多少？

**题目3**：假设你构建一个多轮对话 Agent，为什么多头注意力比单头更适合理解上下文？

---

## 📝 课后测试（15分钟）

**第1题（选择）**：多头注意力中，不同头的计算是：
- A) 串行执行，一个算完再算下一个
- B) 并行执行，各自独立
- C) 共享 Q/K/V，只改变计算方式
- D) 先算完所有头的权重，再统一 softmax

**第2题（填空）**：d_model = num_heads × ______。

**第3题（简答）**：位置编码的 sin/cos 公式中，为什么低维度用高频率、高维度用低频率？

**第4题（简答）**：如果你的 Agent 处理长文本（比如 10000 字），自注意力的计算量是 O(n²)。这意味着什么？有什么问题？

**第5题（思考）**：假设你把所有头的输出做平均而不是拼接，效果会怎样？为什么？

---

## 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| Multi-Head Attention | [ˌmʌlti hɛd əˈtɛnʃən] | 多头注意力，多个注意力并行计算 |
| Concatenation | [kənˌkætəˈneɪʃən] | 拼接，把多个头的输出连在一起 |
| Projection | [prəˈdʒɛkʃən] | 投影，拼接后再做一次线性变换 |
| Positional Encoding | [pəˈzɪʃənəl ɪnˈkoʊdɪŋ] | 位置编码，给每个位置一个独特向量 |
| Sinusoidal | [ˌsaɪnəˈsɔɪdəl] | 正弦余弦的，指用 sin/cos 做编码 |
| head_dim | [hɛd dɪm] | 每个头的维度 = d_model / num_heads |
| RoPE | [roʊp] | 旋转位置编码，目前主流的位置编码方案 |
| Embedding | [ɛmˈbɛdɪŋ] | 词嵌入，把词转成向量表示 |

---

## 📎 参考资源

### 📄 论文
- **Attention Is All You Need** (Vaswani et al., 2017)
  - https://arxiv.org/abs/1706.03762
  - 多头注意力和位置编码的原始定义都在这里

### 🎬 推荐视频
- ⭐ **3Blue1Brown - 直观解释注意力机制**（后半段图解多头注意力）
  - https://www.bilibili.com/video/BV1TZ421j7Ke/
- 📺 **15分钟认识注意力·多头注意力**（B站）
  - https://www.bilibili.com/video/BV17x8jzvEm6/
- 🎓 **李沐 - Transformer 论文精读**
  - https://www.bilibili.com/video/BV1pu411o7BE/

### 📖 延伸阅读
- ⭐ **Jay Alammar - The Illustrated Transformer**
  - https://jalammar.github.io/illustrated-transformer/
- 📐 **Transformer Positional Encoding 详解**（公式拆解 + 可视化）
  - https://kazemnejad.com/blog/transformer_architecture_positional_encoding/

### 💻 代码
- **The Annotated Transformer**（Harvard NLP，MultiHeadAttention 逐行注释）
  - http://nlp.seas.harvard.edu/2018/04/03/attention.html

### 📁 相关 Notebook
- `第1周/第1周-Day2-多头注意力与位置编码.ipynb` —— 对应的代码练习

---

> 💡 **进度：W1 Day 2/7 | 🤖 大模型基础 | 下一篇：Day 3 - 代码实战与自注意力实现**
