# 📚 第2周-Day1：FFN、LayerNorm 与残差连接

> **Transformer 工程优化周开始！本周我们从"大概知道 Transformer 是什么"走向"真正理解它的内部零件"。今天先拆解 Transformer Block 的三大核心组件：前馈神经网络（FFN）、层归一化（LayerNorm）和残差连接（Residual Connection）。搞懂它们，你才能真正理解为什么大模型能堆叠几十层还不崩。**

## 📅 学习进度

```
W1 ████████████████████ ✓ 已完成（Transformer 基础架构）
W2 ██████░░░░░░░░░░░░░░ ← 你在这里（Transformer 工程优化）
W3 ░░░░░░░░░░░░░░░░░░░░ 预训练与数据工程
W4 ░░░░░░░░░░░░░░░░░░░░ 微调与对齐
...
W13 ░░░░░░░░░░░░░░░░░░░░ 综合项目
```

---

## 一、为什么需要 FFN、LayerNorm 和残差连接？

上周我们学了自注意力机制——它让每个 token 都能"看到"其他所有 token。但光有注意力是不够的！

**打个比方**：假设你在开一家糖水店。

- **注意力机制**就像是"前台服务员"——负责收集所有顾客的需求，搞清楚谁跟谁是一桌的、谁先来谁后来。
- **FFN（前馈神经网络）**就像是"后厨厨师"——拿到前台整理好的订单后，对每道菜独立地进行深度加工。服务员只负责传递信息，真正把原材料变成美食的是厨师。
- **LayerNorm**就像是"品控质检员"——每一道菜出锅前，都要检查一下味道是否在正常范围内，太咸或太淡都不行。
- **残差连接**就像是"直达电梯"——即使某一层楼（某一层网络）的厨师出了问题，信息也能通过电梯无损传递到下一层，不会因为中间某一层失误导致整栋楼瘫痪。

**没有它们会怎样？**
- 没有 FFN：模型只能"找关系"，不能"做加工"，表达能力大打折扣
- 没有 LayerNorm：深层网络数值会越来越大或越来越小，最终爆炸或消失
- 没有残差连接：梯度无法有效回传，超过 10 层的网络几乎无法训练

---

## 二、核心原理详解

### 2.1 FFN（前馈神经网络）—— Transformer 的"深度思考"模块

#### 结构

FFN 是一个两层全连接网络，紧跟在每个注意力层后面：

```
输入 x (d_model=512)
    ↓
线性层1: x → 升维到 4×d_model = 2048
    ↓
激活函数: GELU 或 ReLU
    ↓
线性层2: 降维回 d_model = 512
    ↓
输出 (d_model=512)
```

#### 数学表达

$$\text{FFN}(x) = \text{Linear}_2(\text{GELU}(\text{Linear}_1(x)))$$

其中：
- $\text{Linear}_1$: $W_1 \in \mathbb{R}^{d_{model} \times 4d_{model}}$, $b_1 \in \mathbb{R}^{4d_{model}}$
- $\text{Linear}_2$: $W_2 \in \mathbb{R}^{4d_{model} \times d_{model}}$, $b_2 \in \mathbb{R}^{d_{model}}$

**大白话解释**：先把向量从 512 维"展开"到 2048 维（在更高维度的空间中思考），经过非线性激活函数，再"压缩"回 512 维。就像把一张纸放大看清楚细节，做标注后再缩回去。

#### 关键特性

1. **每个 token 独立处理**：FFN 对序列中的每个位置单独操作，不像注意力层那样让 token 之间交互
2. **升维→激活→降维**：在高维空间中捕捉非线性关系
3. **参数量占比最大**：Transformer 中约 2/3 的参数在 FFN 里

**打个比方**：注意力层是"开会讨论"，所有人交换信息；FFN 是"会后独立思考"，每个人根据收集到的信息独立做深度分析。

#### GELU vs ReLU

原始 Transformer 使用 ReLU：$\text{ReLU}(x) = \max(0, x)$

现代大模型多用 GELU：$\text{GELU}(x) = x \cdot \Phi(x)$（其中 $\Phi$ 是标准正态分布的累积分布函数）

GELU 比 ReLU 更平滑，在 0 附近不会突然"截断"，梯度流更好。**打个比方**：ReLU 是"一刀切"的门卫（负数一律不让进），GELU 是"温和的安检"（负数大概率不让进，但偶尔也放行一些接近 0 的）。

### 2.2 LayerNorm（层归一化）—— 数值的"血压调节器"

#### 为什么需要归一化？

深层网络中，每经过一层运算，数值的分布就会发生变化——可能越来越大（爆炸），也可能越来越小（消失）。就像你复印文件，每复印一次质量就下降一点，复印 50 次后可能完全看不清了。

#### 数学表达

对每个样本的每个位置（沿特征维度），计算：

$$\mu = \frac{1}{d} \sum_{i=1}^{d} x_i$$

$$\sigma^2 = \frac{1}{d} \sum_{i=1}^{d} (x_i - \mu)^2$$

$$\hat{x}_i = \frac{x_i - \mu}{\sqrt{\sigma^2 + \epsilon}}$$

$$y_i = \gamma \cdot \hat{x}_i + \beta$$

其中 $\gamma$ 和 $\beta$ 是可学习的缩放和偏移参数，$\epsilon$ 是防止除零的小常数。

**大白话**：先算出这一层所有特征的均值和方差，然后把它们标准化到均值为 0、方差为 1，最后用可学习的参数"重新调整"到合适的范围。

**打个比方**：就像血压计。人的血压太高或太低都不行，LayerNorm 就是把每层的输出"血压"调到正常范围，太高了压下来，太低了提上来。

#### Pre-Norm vs Post-Norm

这是 Transformer 中一个重要的设计选择：

| 方式 | 公式 | 特点 | 代表模型 |
|------|------|------|---------|
| **Post-Norm**（原始） | $x' = \text{LN}(x + \text{Sublayer}(x))$ | 先计算再归一化 | 原版 Transformer, BERT |
| **Pre-Norm**（现代） | $x' = x + \text{Sublayer}(\text{LN}(x))$ | 先归一化再计算 | GPT-2, LLaMA, Qwen |

**打个比方**：
- Post-Norm 是"先干活后体检"——可能干到一半身体就不行了
- Pre-Norm 是"先体检再干活"——保证每次开始工作时状态都是好的

现代大模型几乎都使用 Pre-Norm，因为它更容易训练深层网络。

### 2.3 残差连接（Residual Connection）—— 信息的"直达通道"

#### 核心公式

$$\text{output} = F(x) + x$$

就这么简单！把子层的输入 $x$ 直接加到子层的输出 $F(x)$ 上。

**大白话**：不管中间这一层学到了什么（甚至什么都没学到），原始信息都能无损地传递到下一层。

#### 为什么残差连接如此重要？

**问题**：深层网络的"梯度消失"问题

在反向传播时，梯度需要从输出层一路传回输入层。每经过一层，梯度可能被缩小（消失）或放大（爆炸）。层数越多，问题越严重。

**残差连接的解决方案**：提供一条"捷径"

$$\frac{\partial \text{loss}}{\partial x} = \frac{\partial \text{loss}}{\partial \text{output}} \cdot \left(\frac{\partial F(x)}{\partial x} + 1\right)$$

注意那个 "+1"！它意味着梯度至少有一条路径可以无损地回传。

**打个比方**：想象你建了一栋 100 层的大楼。
- 没有残差连接：每层楼的楼梯都很窄（梯度消失），住在 100 层的人下楼要花极其长的时间
- 有残差连接：除了楼梯，每层还装了一部直达电梯——不管中间楼层出了什么问题，信息都能快速传递

#### 在 Transformer 中的应用

每个 Transformer Block 有两个子层，每个子层都包了残差连接：

```
输入 x
  ├──→ LayerNorm → Multi-Head Attention → (+x) ← 残差连接1
  │
  ├──→ LayerNorm → FFN → (+上一层的输出) ← 残差连接2
  │
  └──→ 最终输出
```

---

## 三、代码实战

### 3.1 用 NumPy 实现 FFN

```python
import numpy as np

class FeedForwardNetwork:
    """简化版 FFN 实现"""
    
    def __init__(self, d_model=512, d_ff=2048):
        # 初始化权重
        self.W1 = np.random.randn(d_model, d_ff) * np.sqrt(2.0 / d_model)
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * np.sqrt(2.0 / d_ff)
        self.b2 = np.zeros(d_model)
    
    def gelu(self, x):
        """GELU 激活函数"""
        return 0.5 * x * (1 + np.tanh(
            np.sqrt(2 / np.pi) * (x + 0.044715 * x**3)
        ))
    
    def forward(self, x):
        """前向传播: 升维 → 激活 → 降维"""
        # x shape: (batch, seq_len, d_model)
        hidden = np.dot(x, self.W1) + self.b1   # 升维到 d_ff
        activated = self.gelu(hidden)            # 非线性激活
        output = np.dot(activated, self.W2) + self.b2  # 降维回 d_model
        return output

# 测试
ffn = FeedForwardNetwork(d_model=512, d_ff=2048)
x = np.random.randn(1, 10, 512)  # batch=1, seq_len=10, d_model=512
output = ffn.forward(x)
print(f"输入 shape: {x.shape}")    # (1, 10, 512)
print(f"输出 shape: {output.shape}")  # (1, 10, 512)
print(f"FFN 参数量: {ffn.W1.size + ffn.b1.size + ffn.W2.size + ffn.b2.size}")  # 约 2.1M
```

### 3.2 用 NumPy 实现 LayerNorm

```python
class LayerNorm:
    """简化版 LayerNorm 实现"""
    
    def __init__(self, d_model=512, eps=1e-6):
        self.gamma = np.ones(d_model)   # 可学习的缩放参数
        self.beta = np.zeros(d_model)   # 可学习的偏移参数
        self.eps = eps
    
    def forward(self, x):
        # x shape: (batch, seq_len, d_model)
        mean = np.mean(x, axis=-1, keepdims=True)     # 沿特征维度求均值
        var = np.var(x, axis=-1, keepdims=True)       # 沿特征维度求方差
        normalized = (x - mean) / np.sqrt(var + self.eps)  # 标准化
        return self.gamma * normalized + self.beta     # 仿射变换

# 测试
ln = LayerNorm(d_model=512)
x = np.random.randn(1, 10, 512) * 100  # 故意制造数值很大的输入
output = ln.forward(x)
print(f"归一化前 - 均值: {x[0,0,:].mean():.4f}, 标准差: {x[0,0,:].std():.4f}")
print(f"归一化后 - 均值: {output[0,0,:].mean():.4f}, 标准差: {output[0,0,:].std():.4f}")
```

### 3.3 完整的 Transformer Block

```python
class TransformerBlock:
    """完整的 Transformer Block（Pre-Norm 版本）"""
    
    def __init__(self, d_model=512, n_heads=8, d_ff=2048):
        self.ln1 = LayerNorm(d_model)
        self.ln2 = LayerNorm(d_model)
        self.ffn = FeedForwardNetwork(d_model, d_ff)
        # 注意力层省略，用占位函数代替
    
    def forward(self, x):
        # Pre-Norm + 残差连接
        # 子层1: 注意力（此处简化为恒等映射）
        attn_input = self.ln1.forward(x)
        attn_output = attn_input  # 实际中这里是多头注意力
        x = x + attn_output      # 残差连接1
        
        # 子层2: FFN
        ffn_input = self.ln2.forward(x)
        ffn_output = self.ffn.forward(ffn_input)
        x = x + ffn_output       # 残差连接2
        
        return x

# 测试
block = TransformerBlock()
x = np.random.randn(1, 10, 512)
output = block.forward(x)
print(f"Transformer Block - 输入: {x.shape}, 输出: {output.shape}")
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

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 图1: FFN 的升维-降维过程
d_model = 512
d_ff = 2048
stages = ['输入', '升维后\n(d_ff=2048)', 'GELU后', '降维后\n(d_model=512)']
sizes = [d_model, d_ff, d_ff, d_model]
colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
axes[0].bar(stages, sizes, color=colors)
axes[0].set_title('FFN: 升维 → 激活 → 降维', fontsize=14, fontweight='bold')
axes[0].set_ylabel('维度大小')
for i, v in enumerate(sizes):
    axes[0].text(i, v + 30, str(v), ha='center', fontweight='bold')

# 图2: LayerNorm 效果
np.random.seed(42)
before = np.random.randn(100) * 5 + 3  # 均值~3, 标准差~5
after = (before - before.mean()) / before.std()
axes[1].hist(before, bins=20, alpha=0.6, label='归一化前', color='#e74c3c')
axes[1].hist(after, bins=20, alpha=0.6, label='归一化后', color='#3498db')
axes[1].set_title('LayerNorm 效果对比', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].set_xlabel('数值')
axes[1].set_ylabel('频次')

# 图3: 残差连接的梯度流对比
layers = np.arange(1, 21)
without_residual = 0.85 ** layers  # 每层梯度衰减15%
with_residual = 0.98 ** layers      # 残差连接下衰减很慢
axes[2].plot(layers, without_residual, 'r-o', label='无残差连接', linewidth=2)
axes[2].plot(layers, with_residual, 'b-s', label='有残差连接', linewidth=2)
axes[2].set_title('梯度流动：残差连接的影响', fontsize=14, fontweight='bold')
axes[2].set_xlabel('层数')
axes[2].set_ylabel('相对梯度大小')
axes[2].legend()
axes[2].set_yscale('log')

plt.tight_layout()
plt.savefig('/tmp/transformer_components.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 可视化图表已生成！")
```

---

## 五、业务关联

### 与 LangChat / Agent / 企业AI 的关系

1. **模型选择与推理优化**：理解 FFN 的参数占比（约 2/3），你就知道为什么量化时 FFN 层的优化最关键。企业部署大模型时，FFN 的矩阵乘法是 GPU 算力消耗的大头。

2. **LayerNorm 的工程意义**：在 LangChat 中加载不同模型时，Pre-Norm 和 Post-Norm 模型的微调策略不同。Pre-Norm 模型（如 LLaMA、Qwen）通常可以用更大的学习率。

3. **残差连接与模型深度**：企业应用中需要根据任务复杂度选择模型深度。理解残差连接让你明白——为什么 70B 模型比 7B 模型效果好（更深 = 更多残差路径 = 更强的信息传递）。

4. **糖水店业务类比**：如果把 Transformer Block 想象成你糖水店的"标准操作流程"：
   - 注意力 = 前台接单（收集所有信息）
   - FFN = 后厨加工（深度处理每道菜）
   - LayerNorm = 品控检查（保证每道菜都在正常范围）
   - 残差连接 = 客户反馈直达店长（信息不丢失）

---

## 六、常见误区

### 误区 1: "FFN 和注意力层做的是类似的事"
**纠正**：完全不同！注意力层是 token 之间**交互信息**（你看看我，我看看你），FFN 是每个 token **独立地深度加工**自己的信息（关起门来仔细思考）。两者互补，缺一不可。

### 误区 2: "BatchNorm 和 LayerNorm 差不多"
**纠正**：差别很大！
- BatchNorm：沿 **batch 维度** 归一化（对不同样本的同一特征做统计）→ 需要足够的 batch size
- LayerNorm：沿 **特征维度** 归一化（对同一样本的所有特征做统计）→ 每个 token 独立计算，不受 batch size 影响

NLP 几乎只用 LayerNorm，因为序列长度可变，batch size 通常较小。

### 误区 3: "残差连接就是简单加法，没什么技术含量"
**纠正**：虽然公式简单（`output = F(x) + x`），但它解决的是深度学习的根本问题——梯度消失。没有残差连接，ResNet 和 Transformer 都不可能堆到几十上百层。2015 年 ResNet 论文的核心贡献就是这个"简单加法"。

---

## 🧪 课堂练习（5分钟）

1. **概念题**：一个 6 层的 Transformer Encoder（如 BERT-base），如果去掉所有残差连接，你预计训练时会出现什么问题？

2. **计算题**：如果 d_model=768，d_ff=3072（BERT-base 的配置），FFN 层有多少参数？

3. **选择题**：以下哪个模型使用的是 Pre-Norm？
   - A) 原版 Transformer (2017)
   - B) BERT (2018)
   - C) GPT-2 (2019)
   - D) 以上都不是

---

## 📝 课后测试（15分钟）

1. **简答题**：解释为什么 FFN 通常把维度扩展到 4 倍（d_ff = 4 × d_model），而不是 2 倍或 8 倍？从表达能力和计算成本的权衡角度分析。

2. **代码题**：修改本课的 LayerNorm 实现，添加一个 `dropout` 参数，使它在训练时随机丢弃一些维度（提示：在归一化之后、仿射变换之前加 dropout）。

3. **分析题**：给定一个 Pre-Norm 的 Transformer Block，画出数据流图，标注出梯度反向传播时的 4 条路径（2 个残差连接 × 2 个子层）。

4. **思考题**：现代大模型（如 LLaMA）在 FFN 中使用了 SwiGLU 激活函数代替 GELU，查阅资料解释 SwiGLU 的原理和优势。

5. **业务关联题**：如果你要用 LangChat 部署一个 13B 参数的模型做客服机器人，理解 FFN 的参数占比（约 2/3）对你的部署策略有什么启发？

---

## 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| Feed-Forward Network (FFN) | [fiːd ˈfɔːrwərd ˈnetwɜːrk] | 前馈神经网络，Transformer 中负责对每个 token 独立做非线性变换的模块 |
| Layer Normalization (LayerNorm) | [ˈleɪər ˌnɔːrməlaɪˈzeɪʃən] | 层归一化，沿特征维度标准化数值分布以稳定训练 |
| Residual Connection | [rɪˈzɪdjuəl kəˈnekʃən] | 残差连接，将子层输入直接加到输出上以解决梯度消失 |
| GELU | [dʒiː-iː-el-juː] | 高斯误差线性单元，一种平滑的激活函数 |
| Pre-Norm | [priː nɜːrm] | 先归一化再计算子层，现代大模型的主流选择 |
| Post-Norm | [poʊst nɜːrm] | 先计算子层再归一化，原始 Transformer 的设计 |
| Gradient Vanishing | [ˈɡreɪdiənt ˈvænɪʃɪŋ] | 梯度消失，深层网络中梯度逐层衰减导致无法训练 |
| SwiGLU | [swɪtʃ dʒiː-el-juː] | Swish-Gated Linear Unit，现代大模型常用的高性能激活函数 |

---

## 📎 参考资源

- 📄 [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762) - 原始 Transformer 论文
- 📄 [Deep Residual Learning (He et al., 2015)](https://arxiv.org/abs/1512.03385) - 残差连接的提出
- 📄 [Layer Normalization (Ba et al., 2016)](https://arxiv.org/abs/1607.06450) - LayerNorm 的详细分析
- 📄 [GLU Variants Improve Transformer (2020)](https://arxiv.org/abs/2002.05202) - SwiGLU 等 FFN 变体
- 🎥 [The Illustrated Transformer - Jay Alammar](https://jalammar.github.io/illustrated-transformer/) - 经典图解教程
- 🎥 [3Blue1Brown: But what is a neural network?](https://www.youtube.com/watch?v=aircAruvnKk) - 神经网络基础可视化

---

> 💡 **明日预告**：Day 2 我们将学习 Tokenizer 与词嵌入——文字是怎么变成数字的？BPE 分词算法的原理是什么？敬请期待！
