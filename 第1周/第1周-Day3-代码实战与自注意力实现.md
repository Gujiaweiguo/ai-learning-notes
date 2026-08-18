# 📚 第1周-Day3：代码实战与自注意力实现

> **理论听懂了不算本事，代码能跑通才是真的会。** 前两天我们学了 Self-Attention 和 Multi-Head Attention 的原理。今天，我们要用纯 NumPy 把它们一行一行地实现出来。没有框架，没有黑盒，每一个数字怎么来的，你都要清楚。

## 📅 学习进度

```
W1 ██████████████░░░░░░░░░░░░░░░░░░░░░░  ← 你在这里（Day 3）
W2 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
...
W13 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

**当前位置：W1 Day 3/7（实战日）**

---

## 一、为什么需要"手动实现"？

### 🤔 不是有 PyTorch 吗，为什么要手写？

你可能会问：`nn.MultiheadAttention` 一行代码就能搞定的事，为什么要用 NumPy 手写？

**答案很简单**：

1. **理解 > 使用**：会用 API 是工程师，理解原理是架构师。你想成为哪种？
2. **Debug 能力**：当模型输出不正常时，如果你不知道 Q/K/V 怎么算的，你根本不知道哪里出了问题
3. **面试必备**：任何 AI 相关的面试，"手写 Self-Attention"都是经典题目
4. **定制化需求**：做企业 AI 时，你可能需要修改注意力机制（比如 Longformer 的稀疏注意力），不懂原理根本改不了

**打个比方**：你可以用计算器算 1+1，但如果你不知道加法的含义，你永远不知道什么时候该用加法。

### 🎯 今天的目标

用纯 NumPy（不依赖任何深度学习框架）实现：
1. Self-Attention 完整流程
2. 手动验证矩阵计算 = 逐元素计算
3. 多头注意力
4. 注意力权重可视化

---

## 二、核心原理回顾（代码视角）

在写代码之前，让我们用代码注释的方式快速回顾整个流程：

```python
# ========== Self-Attention 完整流程 ==========

# 输入：一个句子的词向量矩阵 X
# X shape: (句子长度, 模型维度)，比如 (4, 8) 表示 4 个词，每个 8 维

# 第1步：线性变换，生成 Q, K, V
# Q = X @ W_q  → 每个词"想找什么"
# K = X @ W_k  → 每个词"能提供什么"  
# V = X @ W_v  → 每个词"的实际内容"

# 第2步：计算注意力分数
# scores = Q @ K.T  → 任意两个词的相关度

# 第3步：缩放
# scaled = scores / sqrt(d_k)  → 防止分数过大

# 第4步：Softmax 归一化
# weights = softmax(scaled)  → 变成概率，每行和=1

# 第5步：加权求和
# output = weights @ V  → 每个词的新表示
```

**整个流程的 shape 变化**：

```
X:      (seq_len, d_model)
Q,K,V:  (seq_len, d_k)        — 经过 W_q/W_k/W_v 变换
scores: (seq_len, seq_len)    — Q @ K^T 的结果
weights:(seq_len, seq_len)    — softmax 后
output: (seq_len, d_k)        — weights @ V 的结果
```

---

## 三、代码实战：逐步实现

### 3.1 Step 1：准备输入矩阵

```python
import numpy as np

np.random.seed(42)  # 固定随机种子，保证结果可复现

# 模拟句子 "我 爱 AI 学习"，4个词
seq_len = 4    # 句子长度
d_model = 8   # 模型维度（每个词的向量维度）

# 初始化输入矩阵 X，shape = (4, 8)
X = np.random.randn(seq_len, d_model)

print(f"输入矩阵 X 的 shape: {X.shape}")
print(f"X 的值（前2行）:\n{np.round(X[:2], 3)}")
print(f"\n解读：{seq_len}个词，每个词{d_model}维向量")
```

**这一步在做什么？**

X 就是词向量矩阵。在实际应用中，X 是通过 Embedding 层把每个词（token）转成向量得到的。这里我们直接用随机数模拟。

### 3.2 Step 2：生成 Q, K, V

```python
# Q/K/V 的维度 d_k（可以和 d_model 不同）
d_k = 4

# 生成权重矩阵，shape = (d_model, d_k) = (8, 4)
# 这些矩阵是模型在训练中学习出来的参数
W_q = np.random.randn(d_model, d_k)
W_k = np.random.randn(d_model, d_k)
W_v = np.random.randn(d_model, d_k)

# 矩阵乘法得到 Q, K, V
Q = X @ W_q   # (4, 8) @ (8, 4) = (4, 4)
K = X @ W_k   # (4, 4)
V = X @ W_v   # (4, 4)

print(f"Q shape: {Q.shape}")  # (4, 4)
print(f"K shape: {K.shape}")  # (4, 4)
print(f"V shape: {V.shape}")  # (4, 4)
print("\nQ 的值:")
print(np.round(Q, 3))
```

**为什么要做矩阵乘法？**

X @ W_q 的含义是：用 W_q 对每个词向量做"线性变换"。这个变换让向量从"原始词嵌入"空间转到"查询"空间。不同的 W 矩阵提取出词向量中不同方面的信息。

### 3.3 Step 3：计算注意力分数

```python
# Q × K^T 得到注意力分数矩阵
# Q shape: (4, 4)
# K.T shape: (4, 4)
# scores shape: (4, 4) —— 每个元素是两个词的 Q-K 点积

scores = Q @ K.T

print("原始注意力分数:")
print(np.round(scores, 3))
print("\n解读：scores[i][j] 表示第i个词对第j个词的关注度（未归一化）")
```

**如何理解分数矩阵？**

`scores[0][1]` 表示第0个词（"我"）的 Q 和第1个词（"爱"）的 K 的点积。如果分数为正且大，说明"我"的查询和"爱"的键很匹配。

### 3.4 Step 4：缩放 + Softmax

```python
def softmax(x):
    """
    数值稳定的 softmax 函数。
    为什么要减去最大值？防止 exp() 溢出！
    比如 e^1000 在 Python 中是 inf（无穷大），减去最大值后变成 e^0 = 1。
    """
    x_shifted = x - x.max(axis=1, keepdims=True)
    exp_x = np.exp(x_shifted)
    return exp_x / exp_x.sum(axis=1, keepdims=True)

# 缩放：除以 sqrt(d_k)
scaled_scores = scores / np.sqrt(d_k)

# Softmax 归一化
attn_weights = softmax(scaled_scores)

print("注意力权重（softmax后）:")
print(np.round(attn_weights, 3))

# 验证：每行求和应该等于 1
row_sums = attn_weights.sum(axis=1)
print(f"\n每行求和: {np.round(row_sums, 5)}")
print("✅ 应该每行都等于 1.0")
```

**为什么要缩放？**

如果 d_k = 64，那么 Q·K^T 的方差大约是 64（因为每个维度贡献一个独立项）。方差 64 意味着标准差 8——数值波动很大。除以 √64 = 8 后，方差变成 1，数值稳定了。

**打个比方**：考试从 100 分制缩到 10 分制。排名不变，但分数看起来更"紧凑"。

### 3.5 Step 5：加权求和

```python
# 用注意力权重对 V 做加权平均
output = attn_weights @ V

print("最终输出:")
print(f"shape: {output.shape}")
print(np.round(output, 3))
print("\n✅ 每个词的输出 = 所有词的 V 向量的加权平均")
print("   权重 = 注意力分数（softmax后的）")
```

### 3.6 Step 6：验证——手动 vs 矩阵

这是最重要的一步！验证矩阵运算的结果和手动逐元素计算的结果一致：

```python
# 手动计算第0个词的输出
word0_weights = attn_weights[0]   # 第0个词对所有词的注意力权重
word0_output = word0_weights @ V  # 手动加权求和

print("手动计算第0词输出:", np.round(word0_output, 4))
print("矩阵计算第0词输出:", np.round(output[0], 4))
print("是否一致:", np.allclose(word0_output, output[0]))
print("\n✅ 如果一致，说明你的实现是正确的！")
```

**如果结果不一致怎么办？** 检查 softmax 是否对正确的维度做了归一化（应该对 axis=1，即每行归一化）。

### 3.7 注意力权重热力图打印

```python
# 打印一个漂亮的文本热力图
words = ["我", "爱", "AI", "学习"]

print("\n注意力权重热力图:")
print("         " + "  ".join(f"{w:^6}" for w in words))
for i, w in enumerate(words):
    row = "  ".join(f"{attn_weights[i][j]:.3f}" for j in range(seq_len))
    print(f"{w:^6}  {row}")

print("\n解读：每行表示一个词对其他所有词的关注度")
print("数值越高 = 关注越多")
```

---

## 四、可视化理解

### 4.1 注意力权重热力图（matplotlib 版）

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt

# 中文字体配置（必须配置，否则中文显示为方框）
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

words = ["我", "爱", "AI", "学习"]

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(attn_weights, cmap='Blues')

ax.set_xticks(range(len(words)))
ax.set_yticks(range(len(words)))
ax.set_xticklabels(words, fontsize=14)
ax.set_yticklabels(words, fontsize=14)
ax.set_xlabel('被关注的词 (Key)', fontsize=12)
ax.set_ylabel('发起关注的词 (Query)', fontsize=12)
ax.set_title('Self-Attention 权重热力图\n（颜色越深=注意力越高）', fontsize=14)

# 每个格子写上数值
for i in range(len(words)):
    for j in range(len(words)):
        ax.text(j, i, f'{attn_weights[i][j]:.3f}',
                ha='center', va='center', fontsize=12,
                color='white' if attn_weights[i][j] > 0.4 else 'black')

plt.colorbar(im, label='注意力权重')
plt.tight_layout()
plt.savefig('self_attention_heatmap.png', dpi=150)
plt.show()
print("图表已保存为 self_attention_heatmap.png")
```

### 4.2 Self-Attention 流程图

```python
# 用文字+箭头画一个流程图
print("""
Self-Attention 计算流程：
═══════════════════════════════════════════

  输入 X (seq_len, d_model)
    │
    ├──→ X @ W_q ──→ Q (查询)
    ├──→ X @ W_k ──→ K (键)
    └──→ X @ W_v ──→ V (值)
                        │
            ┌───────────┘
            ▼
    scores = Q @ K.T         # 计算注意力分数
            │
            ▼
    scaled = scores / √d_k   # 缩放
            │
            ▼
    weights = softmax(scaled) # 归一化（每行和=1）
            │
            ▼
    output = weights @ V      # 加权求和
            │
            ▼
    最终输出 (seq_len, d_k)

═══════════════════════════════════════════
""")
```

---

## 五、业务关联

### 🏪 从代码到产品的距离

你可能会想：这段 NumPy 代码和实际的 AI 产品有什么关系？

**1. 理解 Tokenizer 的输出**

当你用 LangChat 发送一条消息时，第一步就是把文字变成 token id，再变成词向量。今天我们写的代码从 X（词向量）开始，但你需要知道 X 从哪里来：

```
用户文字 → Tokenizer → token ids → Embedding 查表 → X (我们今天的起点)
```

**2. 理解模型的"思考过程"**

当你问 Agent "帮我分析一下这个月的销售数据"时，模型内部就是今天写的这套 Q/K/V 运算。理解了这套运算，你就知道：
- 模型不是"理解"了你的话，而是通过矩阵运算找到了相关的信息
- 模型的输出质量取决于注意力权重分配得好不好
- 如果 Prompt 写得不清楚，模型的注意力可能分散到不相关的地方

**3. 企业 AI 性能优化**

理解了 Self-Attention 的计算量（O(n²)），你就知道：
- 为什么长文本需要更多 GPU 内存
- 为什么大模型有"上下文窗口"限制（比如 4K、32K、128K）
- 为什么 Agent 处理大量文档时会变慢

**4. 糖水店 AI 助手的 Debug 场景**

假设你的 AI 客服回答"你们有什么甜的"时，总是推荐咸的。如果你理解注意力机制，你会：
- 检查是不是 prompt 中的关键词位置不对（位置编码问题）
- 检查是不是上下文太多干扰了注意力（长文本稀释问题）
- 调整 prompt 结构让关键信息更突出

**Jason 的实际场景**：在 LangChat 中，当用户对话历史很长时，模型可能"忘记"前面说过的话。本质上是注意力被稀释了——每个词的注意力分散到太多 token 上。理解这个原理后，Jason 可以设计更好的对话管理策略（如摘要、关键信息高亮）。

---

## 六、常见误区

### ❌ 误区1："softmax 后的权重一定有一个很接近 1"

**纠正**：不一定！如果所有词的相关度差不多，softmax 输出会接近均匀分布。只有当某个词特别相关时，才会出现接近 1 的权重。实际中，大部分权重在 0.1-0.5 之间。

### ❌ 误区2："Q、K、V 必须维度相同"

**纠正**：Q 和 K 的维度必须相同（因为要做点积），但 V 的维度可以不同。不过在原始论文和大部分实现中，为了简单，Q、K、V 用相同维度。

### ❌ 误区3："注意力权重就是模型的'解释'"

**纠正**：注意力权重确实能提供一些可解释性，但它不完全等于"模型在看什么"。有时模型把高注意力放在某个词上，但最终决策其实依赖于其他词。把注意力权重当作 100% 准确的解释是危险的。

---

## 🧪 课堂练习（5分钟）

**题目1**：把 `np.random.seed(42)` 改成 `np.random.seed(0)`，重新运行所有代码。注意力权重变了还是没变？为什么？

**题目2**：如果把 `d_k` 从 4 改成 1（即 Q/K/V 只有一列），注意力权重矩阵会变成什么样？

**题目3**：`softmax` 函数中，如果不减去最大值（去掉 `x_shifted` 那行），当输入 `[1000, 1001, 1002]` 时会发生什么？

---

## 📝 课后测试（15分钟）

**第1题（代码题）**：修改上面的代码，让 `seq_len=6, d_model=16, d_k=8`，重新计算注意力。观察注意力权重矩阵的大小变化。

**第2题（计算题）**：给定：
```
Q = [[1, 0], [0, 1]]
K = [[1, 1], [1, 0]]
V = [[2, 3], [4, 5]]
```
手动计算 `softmax(QK^T / √2) × V` 的结果（可使用计算器）。

**第3题（简答）**：代码中 `attn_weights @ V` 这一步用到了什么数学运算？为什么矩阵乘法能实现"加权求和"？

**第4题（简答）**：如果句子长度从 4 变成 100，注意力分数矩阵从多大变成多大？计算量增加多少倍？

**第5题（思考）**：为什么我们说"手动计算第0个词的输出"和"矩阵计算第0个词的输出"应该一致？这说明矩阵运算的什么性质？

---

## 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| Matrix Multiplication | [ˈmeɪtrɪks ˌmʌltɪplɪˈkeɪʃən] | 矩阵乘法，@ 运算符 |
| Transpose | [trænˈspoʊz] | 转置，行列互换，用 .T 表示 |
| Numerical Stability | [njuːˈmɛrɪkəl stəˈbɪlɪti] | 数值稳定性，防止计算溢出 |
| Random Seed | [ˈrændəm siːd] | 随机种子，固定后保证结果可复现 |
| Weighted Average | [ˈweɪtɪd ˈævərɪdʒ] | 加权平均，按权重做平均 |
| Verification | [ˌvɛrɪfɪˈkeɪʃən] | 验证，确认计算结果正确 |
| Shape | [ʃeɪp] | 矩阵/张量的维度大小 |
| Overflow | [ˈoʊvərfloʊ] | 溢出，数值超出表示范围 |

---

## 📎 参考资源

### 💻 代码学习
- **The Annotated Transformer**（Harvard NLP，用 PyTorch 逐行实现 Transformer）
  - http://nlp.seas.harvard.edu/2018/04/03/attention.html
- **PyTorch 官方教程：Multi-Head Attention**
  - https://pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html

### 📖 延伸阅读
- **NumPy 矩阵运算教程**（理解 @ 运算符）
  - https://numpy.org/doc/stable/user/basics.matmul.html
- **Softmax 函数详解**（为什么减最大值）
  - https://zhuanlan.zhihu.com/p/105722023

### 🎬 视频推荐
- **李沐 - 用代码实现 Attention**（动手实现系列）
  - https://www.bilibili.com/video/BV1pu411o7BE/
- **Andrej Karpathy - Let's build GPT from scratch**
  - https://www.youtube.com/watch?v=kCc8FmEb1nY

### 📁 相关 Notebook
- `第1周/第1周-Day3-代码实战-填空式.ipynb` —— 对应的代码练习

---

## 📋 附：完整代码汇总

```python
"""
Self-Attention 完整实现（纯 NumPy）
==================================
可以用这段代码验证你对 Self-Attention 的理解。
"""
import numpy as np

np.random.seed(42)

# 配置
seq_len, d_model, d_k = 4, 8, 4

# 输入
X = np.random.randn(seq_len, d_model)

# 权重矩阵（训练出来的，这里用随机值）
W_q = np.random.randn(d_model, d_k)
W_k = np.random.randn(d_model, d_k)
W_v = np.random.randn(d_model, d_k)

# Q/K/V 变换
Q = X @ W_q
K = X @ W_k
V = X @ W_v

# 注意力计算
scores = Q @ K.T / np.sqrt(d_k)

def softmax(x):
    x = x - x.max(axis=1, keepdims=True)
    return np.exp(x) / np.exp(x).sum(axis=1, keepdims=True)

attn_weights = softmax(scores)
output = attn_weights @ V

# 输出结果
words = ["我", "爱", "AI", "学习"]
print("注意力权重热力图:")
print("         " + "  ".join(f"{w:^6}" for w in words))
for i, w in enumerate(words):
    row = "  ".join(f"{attn_weights[i][j]:.3f}" for j in range(seq_len))
    print(f"{w:^6}  {row}")

print(f"\n输出 shape: {output.shape}")
print(f"✅ Self-Attention 实现完成！")
```

---

> 💡 **进度：W1 Day 3/7 | ⚡实战日 | 下一篇：Day 4 - 第一周总复习**
