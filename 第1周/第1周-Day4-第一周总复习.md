# 📚 第1周-Day4：第一周总复习

> **学完不复习 = 没学。** 这一周我们啃了 Transformer 最核心的部分——Self-Attention 和 Multi-Head Attention。今天是复习日，不是简单重复，而是把碎片化的知识"串成线"，补上你没注意到的盲点。好的复习不是"再看一遍"，而是"换一个角度看"。

## 📅 学习进度

```
W1 ████████████████████░░░░░░░░░░░░░░░░  ← 第一周即将完成！
W2 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
...
W13 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

**当前位置：W1 Day 4/7（复习日）—— 第一周即将收官！**

---

## 一、本周学了什么？一图看全

### 🧠 知识脉络图

```
第1周知识树：
═══════════════════════════════════════════════════════
                  
  ┌─ Day 1：Self-Attention 原理 ──────────────────────┐
  │   • Q/K/V 三个角色                               │
  │   • 点积 → 缩放 → Softmax → 加权求和              │
  │   • 公式：Attention(Q,K,V) = softmax(QK^T/√d_k)V │
  └───────────────────────────────────────────────────┘
                         │
                         ▼
  ┌─ Day 2：Multi-Head Attention + 位置编码 ──────────┐
  │   • 多头 = 多组 Q/K/V 并行计算                    │
  │   • 拼接 → 线性投影                               │
  │   • 位置编码 = sin/cos 固定编码                    │
  │   • 加到词向量上注入顺序信息                       │
  └───────────────────────────────────────────────────┘
                         │
                         ▼
  ┌─ Day 3：代码实战 ─────────────────────────────────┐
  │   • 纯 NumPy 实现 Self-Attention                  │
  │   • 手动验证 = 矩阵计算                            │
  │   • 注意力权重可视化                               │
  └───────────────────────────────────────────────────┘
                         │
                         ▼
  ┌─ Day 4：复习日（今天！）──────────────────────────┐
  │   • 知识串联                                      │
  │   • 查漏补缺                                      │
  │   • 巩固练习                                      │
  └───────────────────────────────────────────────────┘
```

### 📋 核心概念对照表

| 概念 | 一句话解释 | 生活类比 |
|------|-----------|---------|
| Self-Attention | 每个词同时"看"所有其他词 | 派对上同时扫视全场 |
| Q（Query） | "我想找什么信息？" | Google 搜索的关键词 |
| K（Key） | "我能提供什么信息？" | 网页的标题和标签 |
| V（Value） | "我的实际内容" | 网页的实际内容 |
| 点积 | 衡量两个向量的相似度 | 两个兴趣标签的匹配度 |
| 缩放（÷√d_k） | 防止分数过大 | 100分制转10分制 |
| Softmax | 把分数变成概率 | 分配100%的注意力预算 |
| Multi-Head | 多个视角并行观察 | 8个人从不同角度读同一篇文章 |
| 位置编码 | 给每个位置一个"指纹" | 电影院的座位号 |

---

## 二、核心原理回顾（深入版）

### 2.1 Self-Attention 的本质

**一句话**：每个词的输出 = 所有词 V 的加权平均，权重 = Q 和 K 的匹配度。

**详细步骤**：

```
Step 1: Q = X @ W_q,  K = X @ W_k,  V = X @ W_v
        └─ 每个词变成三个向量：查询、键、值

Step 2: scores = Q @ K^T  
        └─ 每对词算一个相关度分数

Step 3: scaled = scores / √d_k
        └─ 缩放，防止分数太大

Step 4: weights = softmax(scaled)
        └─ 变成概率（每行和=1）

Step 5: output = weights @ V
        └─ 用概率对 V 做加权平均
```

**为什么要这么算？** 因为语言理解需要"上下文"。"他"是什么意思？取决于"他"前面提到了谁。Self-Attention 让每个词都能获取整个句子的上下文信息。

### 2.2 Multi-Head Attention 的意义

**一句话**：把大维度拆成多个小维度，每个小维度独立做注意力，最后拼接。

**为什么有效？**

**打个比方**：你分析一家糖水店的经营状况：
- 头1（财务视角）：关注成本、利润、流水
- 头2（客户视角）：关注满意度、复购率
- 头3（运营视角）：关注库存、人员、效率
- 头4（市场视角）：关注竞品、天气、季节

任何单一视角都不够全面。多头 = 多视角 = 更全面的理解。

### 2.3 位置编码的必要性

**一句话**：Self-Attention 本身没有顺序概念，位置编码注入顺序信息。

**三种主流方案对比**：

| 方案 | 代表模型 | 特点 | 比喻 |
|------|---------|------|------|
| 正弦余弦（Sinusoidal） | 原始 Transformer | 固定不变，不可学习 | 固定座位号 |
| 可学习（Learned） | BERT, GPT-2 | 训练学习，有最大长度限制 | 可定制座位号 |
| 旋转编码（RoPE） | LLaMA, GLM | 通过旋转实现相对位置 | 每个人转一定角度 |

---

## 三、代码回顾：完整流程一气呵成

让我们用一句话"我 爱 AI"跑一遍完整的自注意力，这次带上详细注释：

```python
import numpy as np
from matplotlib import font_manager
import matplotlib.pyplot as plt

# ========== 中文字体配置 ==========
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ========== 准备数据 ==========
# 句子 "我 爱 AI" —— 3个词，每个词4维向量
X = np.array([
    [1.0, 0.0, 0.0, 0.0],   # "我"
    [0.0, 1.0, 0.0, 0.0],   # "爱"
    [0.0, 0.0, 1.0, 0.0],   # "AI"
])
d_model = 4

# ========== 生成 Q, K, V ==========
W_q = np.random.randn(d_model, d_model)
W_k = np.random.randn(d_model, d_model)
W_v = np.random.randn(d_model, d_model)

Q = X @ W_q
K = X @ W_k
V = X @ W_v

print(f"输入 shape: {X.shape}")
print(f"Q shape: {Q.shape}, K shape: {K.shape}, V shape: {V.shape}")

# ========== 注意力计算 ==========
def softmax(x):
    x_shifted = x - x.max(axis=-1, keepdims=True)
    exp_x = np.exp(x_shifted)
    return exp_x / exp_x.sum(axis=-1, keepdims=True)

scores = Q @ K.T                    # 注意力分数
scaled_scores = scores / np.sqrt(d_model)  # 缩放
attn_weights = softmax(scaled_scores)       # 归一化
output = attn_weights @ V                    # 加权求和

print("\n注意力权重矩阵（每行代表一个词对其他词的关注度）:")
print(np.round(attn_weights, 3))
print(f"\n最终输出 shape: {output.shape}")
print("输出:")
print(np.round(output, 3))
```

### 单头 vs 多头对比代码

```python
# ========== 单头 vs 多头对比 ==========
np.random.seed(42)
seq_len, d_model, num_heads = 3, 8, 2
d_k = d_model // num_heads  # 4

X = np.random.randn(seq_len, d_model)

# 生成 Q, K, V
W_q = np.random.randn(d_model, d_model)
W_k = np.random.randn(d_model, d_model)
W_v = np.random.randn(d_model, d_model)
Q = X @ W_q; K = X @ W_k; V = X @ W_v

# 单头注意力
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
import numpy as np
import math

max_len, d_model = 20, 16
pe = np.zeros((max_len, d_model))
pos = np.arange(max_len).reshape(-1, 1)
dim = np.arange(d_model).reshape(1, -1)
pe[:, 0::2] = np.sin(pos / 10000 ** (dim[:, 0::2] / d_model))
pe[:, 1::2] = np.cos(pos / 10000 ** (dim[:, 1::2] / d_model))

fig, ax = plt.subplots(figsize=(10, 4))
im = ax.imshow(pe.T, aspect='auto', cmap='coolwarm')
ax.set_xlabel('位置 (Position)')
ax.set_ylabel('维度 (Dimension)')
ax.set_title('正弦位置编码热力图')
plt.colorbar(im)
plt.tight_layout()
plt.savefig('review_pe_heatmap.png', dpi=150)
plt.show()

print("💡 每一行代表一个位置，每一列代表一个维度")
print("💡 每个位置的编码都是唯一的，模型借此区分词的顺序")
```

### 4.2 Self-Attention 计算流程图

```python
# 用代码画出 Q/K/V 的变换流程
fig, axes = plt.subplots(1, 5, figsize=(15, 4))
titles = ['输入 X', 'Q (查询)', 'K (键)', 'V (值)', '注意力权重']
data_list = [X, Q, K, V, attn_weights]

for ax, data, title in zip(axes, data_list, titles):
    im = ax.imshow(data, cmap='RdBu', aspect='auto')
    ax.set_title(title)
    plt.colorbar(im, ax=ax, fraction=0.046)

plt.suptitle('Self-Attention 数据流：X → Q/K/V → 注意力权重', fontsize=14)
plt.tight_layout()
plt.savefig('review_attention_flow.png', dpi=150)
plt.show()
print("图表已保存为 review_attention_flow.png")
```

---

## 五、业务关联

### 🏪 第一周知识在 LangChat/Agent 中的实际价值

**1. 理解 Tokenizer → Embedding → Attention 的完整链路**

当你在 LangChat 中发一条消息时，底层发生了什么：

```
你的消息 "帮我查库存"
    │
    ▼ (Tokenizer 分词)
[帮, 我, 查, 库, 存]  → token ids: [123, 45, 678, 901, 234]
    │
    ▼ (Embedding 查表)
X = 词向量矩阵  shape: (5, d_model)
    │
    ▼ (+ 位置编码)
X + PE  → 加上顺序信息
    │
    ▼ (Self-Attention — 今天学的！)
Q = X @ W_q → 每个词"想找什么"
K = X @ W_k → 每个词"能提供什么"
V = X @ W_v → 每个词"的实际内容"
    │
    ▼ (多头注意力 — Day 2 学的！)
8个头并行计算，拼接，投影
    │
    ▼ (更多层 Transformer Block)
... 重复多次 ...
    │
    ▼ (输出层)
预测下一个 token → 生成回复
```

**2. Agent 上下文窗口的本质**

你给 Agent 的上下文越长，注意力矩阵越大（n²增长）。这就是为什么：
- 4K 上下文 → 速度快但信息少
- 128K 上下文 → 信息多但更贵更慢
- 需要合理的对话管理策略

**3. Prompt Engineering 的注意力视角**

理解注意力机制后，写 prompt 时你应该：
- **重要信息放前面或后面**：中间位置容易"注意力稀释"（Lost in the Middle 现象）
- **重复关键信息**：相当于增加相关词的 Q-K 匹配机会
- **结构化 Prompt**：用 markdown/分隔符帮助模型区分不同部分

**4. 糖水店 AI 助手设计**

假设 Jason 做一个 AI 客服来处理糖水店订单：
- 用户说"来一碗不甜的红豆沙，少冰"
- 注意力机制让模型同时关注"不甜"（口味）、"红豆沙"（品名）、"少冰"（要求）
- 如果 Prompt 设计不好，模型可能"没注意到""不甜"，默认推荐标准甜度

---

## 六、查漏补缺（本周常见问题）

### ❓ 问题1：为什么注意力分数要除以 √d_k？

**答案**：当 d_k 较大时，Q·K^T 的结果数值也会很大。数值太大会导致 softmax 的梯度趋近于零（梯度消失），模型学不动。除以 √d_k 让方差回到合理范围。

**类比**：唱歌时声音太大（分数太大），麦克风（softmax）会失真。调低音量（缩放）让声音清晰可辨。

### ❓ 问题2：位置编码为什么要加到 Embedding 上？不能用别的方式吗？

**答案**：
- **加法**（原始 Transformer）：简单直接，位置信息和词信息融合
- **拼接**：会增加维度，破坏残差连接的维度匹配
- **相乘**：可能破坏词向量本身的信息
- **RoPE**（现代方案）：不直接加到输入上，而是在 Q/K 上做旋转

加法是最简单且有效的方式，虽然不是最优。

### ❓ 问题3：多头注意力比单头好在哪里？头数越多越好吗？

**答案**：
- **好处**：不同头可以关注不同模式（语法、语义、指代...），信息更丰富
- **不是越多越好**：头数增加 → 每头维度减少 → 单头表达能力下降
- **常见配置**：8-16 个头是甜蜜点

### ❓ 问题4：Q、K、V 三个矩阵如果完全相同会怎样？

**答案**：如果 W_q = W_k = W_v，那么 Q = K = V。注意力分数 = Q·Q^T（自相关矩阵）。这会让每个词最关注自己（对角线值最大），失去"去关注其他词"的意义。所以需要不同的 W 矩阵。

### ❓ 问题5：句子长度翻倍，计算量变成多少倍？

**答案**：**4倍！** 因为注意力分数矩阵是 (seq_len × seq_len)，长度翻倍 → 矩阵面积变成 4 倍。这就是 Self-Attention 的 O(n²) 复杂度问题，也是长文本处理的瓶颈。

---

## 七、🧩 查漏补缺测试

### 测试1：公式默写

请不看任何资料，写出以下公式：

1. Self-Attention 公式：Attention(Q,K,V) = __________________
2. 多头维度关系：d_model = __________________
3. 位置编码（偶数维）：PE(pos, 2i) = __________________

### 测试2：概念辨析

判断对错：
1. （ ）Self-Attention 是 RNN 的改进版本
2. （ ）每个注意力头的输出维度是 d_model
3. （ ）Softmax 后的注意力权重一定有一个接近 1
4. （ ）位置编码可以是固定不变的，也可以是可学习的
5. （ ）自注意力计算量和句子长度成正比

### 测试3：情景分析

你构建了一个 Agent，发现用户输入超过 2000 字时，模型经常"漏掉"前面的重要信息。基于本周学到的知识：
1. 这可能是什么原因？
2. 你会怎么优化？（至少提2个方案）

### 测试4：代码补全

以下代码缺少一行，请补全：

```python
import numpy as np

X = np.random.randn(5, 8)
W_q = np.random.randn(8, 4)
W_k = np.random.randn(8, 4)
W_v = np.random.randn(8, 4)
Q = X @ W_q
K = X @ W_k
V = X @ W_v

# TODO: 计算注意力分数（缩放后）
# scores = _____________________

attn = softmax(scores)
output = attn @ V
```

---

## 📐 核心公式速查卡

```
╔══════════════════════════════════════════════════════════════╗
║                    Week 1 公式速查卡                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Self-Attention：                                         ║
║     Attention(Q,K,V) = softmax(Q·K^T / √d_k) · V            ║
║                                                              ║
║  2. Multi-Head：                                              ║
║     head_i = Attention(Q·W_i^Q, K·W_i^K, V·W_i^V)           ║
║     MultiHead = Concat(head_1,...,head_h) · W^O              ║
║                                                              ║
║  3. 维度关系：                                                ║
║     d_model = num_heads × head_dim                           ║
║                                                              ║
║  4. 位置编码：                                                ║
║     PE(pos, 2i) = sin(pos / 10000^(2i/d_model))              ║
║     PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))            ║
║                                                              ║
║  5. 最终输入：                                                ║
║     X_final = Embedding(tokens) + PE                         ║
║                                                              ║
║  6. 复杂度：                                                  ║
║     Self-Attention = O(n² · d)  n=句子长度, d=模型维度       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 💡 知识卡片（一周总结）

| 知识点 | 核心内容 | 关键词 |
|--------|---------|--------|
| Self-Attention | 每个词主动"看"所有其他词 | Q/K/V, 点积, softmax |
| 缩放 | 除以 √d_k 防止分数过大 | 数值稳定性 |
| Softmax | 把分数变成概率 | 归一化, 每行和=1 |
| Multi-Head | 多个"视角"并行观察 | 拆分维度, 拼接, 投影 |
| 位置编码 | 给每个位置一个"身份证" | sin/cos, RoPE |
| Embedding | 把词转成向量 | 词嵌入, 查表 |

---

## 👀 下周预告：第2周（Transformer 深入理解·续）

第1周我们学了 Transformer 最核心的两个组件。第2周继续补完 Transformer 的其他关键部分：

- **Day 1**: FFN（前馈网络）、LayerNorm 与残差连接
  - 为什么需要残差连接？（防止梯度消失）
  - LayerNorm 在做什么？（让每层的输出分布稳定）

- **Day 2**: Tokenizer 与词嵌入
  - BPE/WordPiece 分词算法
  - 词嵌入是怎么训练出来的？

- **Day 3**: 整体架构回顾（GPT vs BERT）
  - Encoder-only vs Decoder-only vs Encoder-Decoder
  - 为什么 GPT 选择 Decoder-only？

**💡 建议**：在下周开始前，确保你能：
1. 不看资料默写 Self-Attention 公式
2. 用自己的话解释 Q/K/V 是什么
3. 说出多头注意力比单头好在哪
4. 知道位置编码为什么必要

---

## 📎 参考资源

### 📄 本周核心论文
- **Attention Is All You Need** (Vaswani et al., 2017)
  - https://arxiv.org/abs/1706.03762

### 🎬 视频清单（按优先级）
1. ⭐ 3Blue1Brown 注意力可视化：https://www.bilibili.com/video/BV1TZ421j7Ke/
2. 🎓 李沐论文精读：https://www.bilibili.com/video/BV1pu411o7BE/
3. 📺 15分钟注意力：https://www.bilibili.com/video/BV1pj42137ZY/

### 📖 必读文章
- ⭐ Jay Alammar 图解 Transformer：https://jalammar.github.io/illustrated-transformer/
- 📐 位置编码详解：https://kazemnejad.com/blog/transformer_architecture_positional_encoding/

### 💻 代码资源
- The Annotated Transformer：http://nlp.seas.harvard.edu/2018/04/03/attention.html
- Karpathy 从零实现 GPT：https://www.youtube.com/watch?v=kCc8FmEb1nY

### 📁 相关 Notebook
- `第1周/第1周-Day1-自注意力.ipynb`
- `第1周/第1周-Day2-多头注意力与位置编码.ipynb`
- `第1周/第1周-Day3-代码实战-填空式.ipynb`
- `第1周/第1周-Day4-复习日.ipynb`

---

## 🔑 本周全部术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| Self-Attention | [sɛlf əˈtɛnʃən] | 自注意力，让每个词看到所有其他词 |
| Multi-Head Attention | [ˌmʌlti hɛd əˈtɛnʃən] | 多头注意力，多个注意力并行 |
| Query (Q) | [ˈkwɪəri] | 查询向量 |
| Key (K) | [kiː] | 键向量 |
| Value (V) | [ˈvæljuː] | 值向量 |
| Dot Product | [dɒt ˈprɒdʌkt] | 点积运算 |
| Softmax | [ˈsɒftmæks] | 归一化函数 |
| Scaling | [ˈskeɪlɪŋ] | 缩放（÷√d_k） |
| Concatenation | [kənˌkætəˈneɪʃən] | 拼接 |
| Projection | [prəˈdʒɛkʃən] | 线性投影 |
| Positional Encoding | [pəˈzɪʃənəl ɪnˈkoʊdɪŋ] | 位置编码 |
| Sinusoidal | [ˌsaɪnəˈsɔɪdəl] | 正弦余弦的 |
| Embedding | [ɛmˈbɛdɪŋ] | 词嵌入 |
| head_dim | [hɛd dɪm] | 每头维度 |
| RoPE | [roʊp] | 旋转位置编码 |
| Tokenizer | [ˈtoʊkənaɪzər] | 分词器 |

---

> 💡 **进度：W1 Day 4/7 | 📖 复习日 | 第一周即将收官！下周见！**
