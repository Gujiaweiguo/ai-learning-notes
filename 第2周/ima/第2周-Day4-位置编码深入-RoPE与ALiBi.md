# 📚 第2周-Day4：位置编码深入——RoPE 与 ALiBi

> **昨天我们对比了 GPT 和 BERT 两大架构。今天要解决一个 Transformer 的"先天缺陷"——位置感知。自注意力机制本身是位置无关的，它把输入看作"一组无序的 token"。但语言显然是有顺序的："狗咬人"和"人咬狗"意思完全不同。位置编码就是给模型注入"顺序感"的技术。**

## 📅 学习进度

```
W1 ████████████████████ ✓ 已完成（Transformer 基础架构）
W2 █████████░░░░░░░░░░░ ← 你在这里（Day 4/7）
W3 ░░░░░░░░░░░░░░░░░░░░ 预训练与数据工程
W4 ░░░░░░░░░░░░░░░░░░░░ 微调与对齐
...
W13 ░░░░░░░░░░░░░░░░░░░░ 综合项目
```

---

## 一、为什么需要位置编码？

### 自注意力的"先天缺陷"

自注意力机制计算的是每两个 token 之间的相似度，然后做加权求和。但这个过程完全忽略了 token 的**位置信息**。

**打个比方**：想象你是一位评委，看到以下"食材清单"：

```
方案A: 糖、水、红豆
方案B: 盐、水、红豆
```

自注意力只关心"这些食材之间有什么关系"，不关心它们的排列顺序。但实际上：
- "红豆沙配糖水" → 甜品 ✓
- "红豆沙配盐水" → 暗黑料理 ✗

顺序很重要！

更直接的例子：
- "我爱你" → 表白 ❤️
- "你爱我" → 也不错 😊
- "爱你我" → 有点奇怪 🤔

如果去掉位置编码，模型会把这三个句子理解为**完全相同**的输入——因为它们包含的词一样，只是顺序不同。

### 位置编码的解决方案

给每个位置一个独特的"标签"，加到词嵌入上：

```
Embedding("我") + PositionEncoding(1)
Embedding("爱") + PositionEncoding(2)
Embedding("你") + PositionEncoding(3)
```

这样模型就能区分"在位置1的我"和"在位置3的我"了。

---

## 二、核心原理详解

### 2.1 正弦位置编码（Sinusoidal）—— 原始方案

2017 年的原始 Transformer 使用 sin/cos 函数生成位置编码：

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

其中 $pos$ 是位置（0, 1, 2, ...），$i$ 是维度索引。

**大白话解释**：
- 偶数维度用 sin 函数，奇数维度用 cos 函数
- 不同维度使用不同的频率——低维度变化快（编码精细位置），高维度变化慢（编码大范围位置）

**打个比方**：就像一个多指针时钟：
- 秒针（高频维度）：快速旋转，精确区分相邻位置
- 分针（中频维度）：中速旋转，区分中等范围
- 时针（低频维度）：慢速旋转，区分大范围位置
- 三根针的组合可以唯一确定一个时刻（位置）

**优点**：无需训练，理论上可以外推到任意长度
**缺点**：实际中外推效果不好——训练时只见过 512 长度，推理时给 2048 就效果很差

### 2.2 可学习位置编码（Learned PE）—— BERT/GPT-2 方案

直接为每个位置创建一个可学习的向量：

```python
# 每个位置一个向量，随训练更新
self.position_embeddings = nn.Embedding(max_length, d_model)
# max_length=2048 意味着最多支持 2048 个位置
```

**优点**：简单、灵活，效果好
**缺点**：
- 最大长度固定——训练时 max_length=2048，推理时不能超过 2048
- 参数量增加——max_length × d_model 的额外参数
- 外推能力为零

### 2.3 RoPE（Rotary Position Embedding）—— 当前主流

RoPE 是目前最流行的位置编码方案，被 LLaMA、Qwen、ChatGLM、Mistral 等几乎所有主流大模型采用。

#### 核心思想

RoPE 不在输入上加位置信息，而是在**注意力计算时**通过旋转矩阵注入位置信息。

**打个比方**：想象一个二维平面上的向量，RoPE 把它按照位置角度旋转：
- 位置 0 的向量：不旋转
- 位置 1 的向量：旋转 1°
- 位置 2 的向量：旋转 2°
- ...
- 位置 N 的向量：旋转 N°

两个向量的点积（注意力分数）只取决于它们的**相对角度差**，而不是绝对角度。这就是 RoPE 的核心优势——**编码的是相对位置**。

#### 数学表达

对于位置 $m$ 的查询向量 $q$ 和位置 $n$ 的键向量 $k$：

$$q_m = R_m \cdot q$$
$$k_n = R_n \cdot k$$

其中 $R_m$ 和 $R_n$ 是旋转矩阵：

$$R_m = \begin{pmatrix} \cos m\theta_1 & -\sin m\theta_1 \\ \sin m\theta_1 & \cos m\theta_1 \\ & & \cos m\theta_2 & -\sin m\theta_2 \\ & & \sin m\theta_2 & \cos m\theta_2 \\ & & & & \ddots \end{pmatrix}$$

注意力分数：

$$q_m^T k_n = (R_m q)^T (R_n k) = q^T R_m^T R_n k = q^T R_{n-m} k$$

注意最后的结果 $R_{n-m}$ 只依赖于**相对位置** $(n-m)$！

#### 为什么 RoPE 成为主流？

1. **相对位置编码**：天然编码 token 之间的距离，更符合语言的本质
2. **外推能力强**：通过 NTK-Aware 等技巧，可以从 4K 扩展到 32K+ 甚至百万 tokens
3. **不增加参数**：旋转矩阵是固定的，不需要训练
4. **实现优雅**：只需要在注意力计算时加几行代码

### 2.4 ALiBi（Attention with Linear Biases）—— 极简方案

ALiBi 走了一条完全不同的路——不修改 Embedding，而是直接在注意力分数上加一个线性偏置。

#### 核心公式

$$\text{Attention}(q_i, k_j) = \text{softmax}\left(\frac{q_i \cdot k_j}{\sqrt{d_k}} - m \cdot |i - j|\right)$$

其中 $m$ 是一个与注意力头相关的斜率（负数），$|i - j|$ 是两个 token 的距离。

**大白话解释**：距离越远的两个 token，注意力分数被扣减得越多。就像"重力衰减"——离你越远的东西对你的影响越小。

**打个比方**：
- 正弦编码：给每个位置一个独特的"指纹"——复杂但精确
- 可学习编码：给每个位置一个"学号牌"——灵活但不能改
- RoPE：旋转每个位置的向量——优雅且可外推
- ALiBi：不管位置编码，只是在计算注意力时"惩罚距离远的"——简单粗暴

#### ALiBi 的优缺点

**优点**：
- 实现极其简单（几行代码）
- 外推能力极强（训练 1024 长度，推理 2048+ 仍然有效）
- 不增加任何参数

**缺点**：
- 效果通常略逊于 RoPE
- 强制假设"越远越不重要"——不总是对的（比如文档中相隔很远的呼应内容）
- 采用较少（BLOOM、MPT 等）

### 2.5 四种方案对比

| 方案 | 代表模型 | 编码类型 | 外推能力 | 参数量 | 复杂度 |
|------|---------|---------|---------|--------|--------|
| 正弦 | 原版 Transformer | 绝对位置 | 理论可以，实际差 | 0 | 中 |
| 可学习 | BERT, GPT-2 | 绝对位置 | 无 | max_len × d_model | 低 |
| **RoPE** | LLaMA, Qwen | 相对位置 | 强（配合扩展技巧） | 0 | 中高 |
| ALiBi | BLOOM, MPT | 相对位置 | 很强 | 0 | 低 |

---

## 三、代码实战

### 3.1 实现正弦位置编码

```python
import numpy as np

def sinusoidal_position_encoding(seq_len, d_model):
    """正弦位置编码实现"""
    pe = np.zeros((seq_len, d_model))
    position = np.arange(seq_len).reshape(-1, 1)
    
    # 计算频率
    div_term = np.exp(np.arange(0, d_model, 2) * 
                      -(np.log(10000.0) / d_model))
    
    pe[:, 0::2] = np.sin(position * div_term)  # 偶数维度用 sin
    pe[:, 1::2] = np.cos(position * div_term)  # 奇数维度用 cos
    
    return pe

# 生成 10 个位置、64 维的位置编码
pe = sinusoidal_position_encoding(seq_len=10, d_model=64)
print(f"位置编码形状: {pe.shape}")
print(f"位置 0 前8维: {np.round(pe[0, :8], 3)}")
print(f"位置 1 前8维: {np.round(pe[1, :8], 3)}")
print(f"位置 2 前8维: {np.round(pe[2, :8], 3)}")
```

### 3.2 实现 RoPE 旋转位置编码

```python
def rotary_position_embedding(seq_len, d_head):
    """RoPE 旋转位置编码实现"""
    # 计算频率
    theta = 1.0 / (10000 ** (np.arange(0, d_head, 2) / d_head))
    
    # 计算每个位置的角度
    positions = np.arange(seq_len)
    angles = np.outer(positions, theta)  # (seq_len, d_head/2)
    
    # 计算 cos 和 sin
    cos = np.cos(angles)
    sin = np.sin(angles)
    
    return cos, sin

def apply_rotary(x, cos, sin):
    """将 RoPE 应用到向量上"""
    # x shape: (seq_len, d_head)
    d_half = x.shape[-1] // 2
    
    x1 = x[..., :d_half]    # 前半部分
    x2 = x[..., d_half:]    # 后半部分
    
    # 旋转操作
    rotated = np.concatenate([
        x1 * cos - x2 * sin,
        x1 * sin + x2 * cos
    ], axis=-1)
    
    return rotated

# 演示
d_head = 64
seq_len = 10
cos, sin = rotary_position_embedding(seq_len, d_head)

x = np.random.randn(seq_len, d_head)
x_rotated = apply_rotary(x, cos, sin)

print(f"原始向量 shape: {x.shape}")
print(f"旋转后向量 shape: {x_rotated.shape}")
print(f"\nRoPE 的核心效果：两个位置的注意力分数只取决于它们的相对距离")
```

### 3.3 实现 ALiBi 偏置

```python
def alibi_attention_bias(seq_len, n_heads=8):
    """ALiBi 注意力偏置"""
    # 每个注意力头有不同的斜率
    # 通常使用几何序列: 2^(-8/n_heads) 的幂
    slopes = np.power(2, -(np.arange(1, n_heads+1) * 8 / n_heads))
    
    # 计算距离矩阵
    positions = np.arange(seq_len)
    distance = np.abs(positions.reshape(-1, 1) - positions.reshape(1, -1))
    
    # 每个头的偏置 = -slope * distance
    biases = -np.outer(slopes, distance.flatten()).reshape(n_heads, seq_len, seq_len)
    
    return biases

# 演示
biases = alibi_attention_bias(seq_len=8, n_heads=4)
print(f"ALiBi 偏置 shape: {biases.shape}")
print(f"\n第 1 个头的偏置矩阵:")
print(np.round(biases[0], 2))
print(f"\n第 4 个头的偏置矩阵:")
print(np.round(biases[3], 2))
print("\n注意：距离越远，偏置越负（注意力越弱）")
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

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 图1: 正弦位置编码热力图
d_model = 64
seq_len = 50
pe = np.zeros((seq_len, d_model))
position = np.arange(seq_len).reshape(-1, 1)
div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
pe[:, 0::2] = np.sin(position * div_term)
pe[:, 1::2] = np.cos(position * div_term)

im1 = axes[0, 0].imshow(pe.T, cmap='RdBu', aspect='auto', vmin=-1, vmax=1)
axes[0, 0].set_title('正弦位置编码（50位置 × 64维）', fontsize=13, fontweight='bold')
axes[0, 0].set_xlabel('位置')
axes[0, 0].set_ylabel('维度')
plt.colorbar(im1, ax=axes[0, 0])

# 图2: 不同维度的波形
dims_to_show = [0, 4, 16, 32]
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
positions = np.arange(50)
for i, (dim, color) in enumerate(zip(dims_to_show, colors)):
    axes[0, 1].plot(positions, pe[:, dim], color=color, linewidth=2, 
                    label=f'维度 {dim} (频率={1/(10000**(2*dim/d_model)):.4f})')
axes[0, 1].set_title('不同维度的位置编码波形', fontsize=13, fontweight='bold')
axes[0, 1].set_xlabel('位置')
axes[0, 1].set_ylabel('编码值')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 图3: ALiBi 偏置可视化
seq_len2 = 16
n_heads = 4
slopes = np.power(2, -(np.arange(1, n_heads+1) * 8 / n_heads))
positions2 = np.arange(seq_len2)
distance = np.abs(positions2.reshape(-1, 1) - positions2.reshape(1, -1))
alibi_bias = -slopes[0] * distance

im3 = axes[1, 0].imshow(alibi_bias, cmap='Blues_r', aspect='auto')
axes[1, 0].set_title(f'ALiBi 偏置（斜率={slopes[0]:.4f}）', fontsize=13, fontweight='bold')
axes[1, 0].set_xlabel('Key 位置')
axes[1, 0].set_ylabel('Query 位置')
plt.colorbar(im3, ax=axes[1, 0])
for i in range(seq_len2):
    for j in range(seq_len2):
        axes[1, 0].text(j, i, f'{alibi_bias[i,j]:.1f}', 
                        ha='center', va='center', fontsize=6, 
                        color='white' if abs(alibi_bias[i,j]) > 0.1 else 'black')

# 图4: RoPE 旋转示意
theta_vals = np.linspace(0, 2*np.pi, 100)
for i, (pos, color) in enumerate(zip([0, 1, 2, 3, 5], plt.cm.viridis(np.linspace(0, 1, 5)))):
    angle = pos * 0.5  # 简化角度
    vec = np.array([np.cos(angle), np.sin(angle)])
    axes[1, 1].arrow(0, 0, vec[0], vec[1], head_width=0.05, 
                     head_length=0.03, fc=color, ec=color, linewidth=2)
    axes[1, 1].text(vec[0]*1.15, vec[1]*1.15, f'pos={pos}', 
                    fontsize=10, color=color, fontweight='bold')

circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='gray', alpha=0.5)
axes[1, 1].add_patch(circle)
axes[1, 1].set_xlim(-1.5, 1.5)
axes[1, 1].set_ylim(-1.5, 1.5)
axes[1, 1].set_aspect('equal')
axes[1, 1].set_title('RoPE: 位置 = 旋转角度', fontsize=13, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].axhline(y=0, color='k', linewidth=0.5)
axes[1, 1].axvline(x=0, color='k', linewidth=0.5)

plt.tight_layout()
plt.savefig('/tmp/position_encoding.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 可视化图表已生成！")
```

---

## 五、业务关联

### 与 LangChat / Agent / 企业 AI 的关系

1. **长文本处理**：企业文档动辄上万字，模型能处理的上下文长度直接影响业务可行性。RoPE + 长文本扩展技术（如 YaRN）让 Qwen 等模型支持 128K+ tokens。

2. **对话历史管理**：LangChat 中多轮对话的历史越长越好，但受限于上下文窗口。理解 RoPE 的外推能力让你知道——为什么有些模型可以突然处理很长的历史，有些不行。

3. **知识库问答**：RAG 场景中需要把长文档切分成 chunk。位置编码方案影响 chunk 大小的选择——RoPE 模型通常可以用更大的 chunk。

4. **糖水店场景**：如果你的糖水店知识库有一份 5000 字的标准操作手册，用支持 RoPE 的 Qwen 模型（128K 上下文）可以一次性塞进去全部内容，无需复杂的分块检索。

---

## 六、常见误区

### 误区 1: "位置编码就是在 Embedding 上加一个数字"
**纠正**：不同方案的做法完全不同。正弦和可学习方案确实是在 Embedding 上加向量，但 RoPE 是在注意力计算时旋转向量，ALiBi 是在注意力分数上加偏置。后两者根本不碰 Embedding。

### 误区 2: "RoPE 可以无限外推"
**纠正**：原始 RoPE 的外推能力有限——训练时 4K，推理 8K 时效果就明显下降了。需要配合 NTK-Aware、YaRN 等扩展技巧才能实现真正的长上下文外推。

### 误区 3: "位置编码对所有 token 一视同仁"
**纠正**：不同的注意力头学习关注不同的位置模式。有些头关注近距离的 token，有些关注远距离的 token。ALiBi 通过不同斜率显式地实现了这一点，RoPE 则是隐式地由模型学习。

---

## 🧪 课堂练习（5分钟）

1. **概念题**：如果完全去掉位置编码，GPT 模型处理"猫追狗"和"狗追猫"时，输出会怎样？

2. **计算题**：正弦位置编码中，$d_{model}=512$，$pos=10$，$i=0$（第一个维度），计算 $PE_{(10, 0)}$ 的值。

3. **选择题**：以下哪个位置编码方案不需要额外的训练参数？
   - A) 可学习位置编码
   - B) RoPE
   - C) 两者都不需要
   - D) 两者都需要

---

## 📝 课后测试（15分钟）

1. **简答题**：解释为什么 RoPE 编码的是"相对位置"而不是"绝对位置"。从数学角度证明。

2. **对比题**：RoPE 和 ALiBi 各有什么优缺点？如果你要训练一个需要处理 100K 上下文的模型，会选择哪种？为什么？

3. **编程题**：实现一个函数，输入两个向量 $q$（位置 $m$）和 $k$（位置 $n$），使用 RoPE 计算它们的注意力分数。

4. **分析题**：为什么可学习位置编码的外推能力为零？从参数化的角度解释。

5. **业务题**：你的企业需要处理法律合同文档（平均 3 万字/份），当前使用的模型训练时上下文长度为 4K。你会选择什么方案来处理这些长文档？

---

## 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| Positional Encoding | [pəˈzɪʃənəl ɪnˈkoʊdɪŋ] | 位置编码，为 token 注入位置信息的技术 |
| Sinusoidal | [ˌsaɪnəˈsɔɪdəl] | 正弦的，指用 sin/cos 函数生成位置编码 |
| RoPE (Rotary Position Embedding) | [ˈroʊtəri pəˈzɪʃən ɪmˈbɛdɪŋ] | 旋转位置编码，通过旋转矩阵编码相对位置 |
| ALiBi | [eɪ-laɪ-baɪ] | 注意力线性偏置，直接在注意力分数上加距离惩罚 |
| Causal Mask | [ˈkɔːzəl mæsk] | 因果掩码，防止模型看到未来位置的信息 |
| Extrapolation | [ɪkˌstræpəˈleɪʃən] | 外推，模型处理比训练时更长的序列的能力 |
| NTK-Aware | [ɛn-tiː-keɪ əˈwɛr] | NTK 感知的 RoPE 扩展技巧，改善长文本外推 |
| Relative Position | [ˈrɛlətɪv pəˈzɪʃən] | 相对位置，两个 token 之间的距离 |

---

## 📎 参考资源

- 📄 [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762) - 正弦位置编码原始方案
- 📄 [RoFormer: Enhanced Transformer with Rotary Position Embedding (2021)](https://arxiv.org/abs/2104.09864) - RoPE 原论文
- 📄 [Train Short, Test Long: Attention with Linear Biases (ALiBi)](https://arxiv.org/abs/2108.12409) - ALiBi 论文
- 📄 [YaRN: Efficient Context Window Extension of LLMs](https://arxiv.org/abs/2309.00071) - RoPE 长文本扩展
- 📄 [NTK-Aware Scaled RoPE](https://www.reddit.com/r/LocalLLaMA/comments/14lz7j5/) - NTK-Aware 技巧
- 🎥 [Rotary Positional Embeddings - Eleuther AI](https://blog.eleuther.ai/rotary-embeddings/) - RoPE 通俗讲解

---

> 💡 **明日预告**：Day 5 我们将学习 Transformer 推理优化的三大核心技术——KV Cache、Flash Attention 和 GQA。它们让大模型从"老爷车"变成"F1 赛车"！
