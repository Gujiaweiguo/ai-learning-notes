# 📚 第2周-Day7：第二周总复习

> **经过 6 天的高强度学习，你已经从"大概知道 Transformer 是什么"升级到了"能拆解、能优化、能微调大模型"的实操级别！今天是复习日，我们把所有知识点串联起来，形成一张完整的技术图谱，并通过测试检验你的掌握程度。**

## 📅 学习进度

```
W1 ████████████████████ ✓ 已完成（Transformer 基础架构）
W2 ████████████████████ ← 进行中（Day 7/7：本周复习）
W3 ░░░░░░░░░░░░░░░░░░░░ 预训练与数据工程 ← 下周目标
W4 ░░░░░░░░░░░░░░░░░░░░ 微调与对齐
...
W13 ░░░░░░░░░░░░░░░░░░░░ 综合项目
```

---

## 一、为什么需要第二周总复习？

第二周的信息密度很高：既有 Transformer 内部结构，又有分词、位置编码、推理部署和 QLoRA 微调。它们不是七个孤立的知识点，而是一条从“文本输入”到“模型输出”、再到“企业部署”的完整链路。

如果不做串联，常见状态是“每个词都认识，但一问整体怎么工作就说不清”。例如，知道 KV Cache 能提速，却不清楚它为什么只适用于 GPT 式自回归生成；知道 LoRA 能省显存，却不清楚它与 4-bit 量化如何配合。

**打个比方**：这一周像学习开一家智能糖水店。你已经分别认识了后厨设备（FFN、LayerNorm、残差）、菜单编码系统（Tokenizer、Embedding）、前台服务方式（GPT/BERT）、店内导航（位置编码）、加速出餐设备（KV Cache、Flash Attention、GQA）和定制配方的方法（QLoRA）。总复习就是把这些设备接成一条真正能营业的流水线。

---

## 二、核心原理详解

### 2.1 第二周知识全景图

#### Day 1：FFN、LayerNorm 与残差连接

Transformer Block 的三大核心组件：

| 组件 | 作用 | 关键公式 | 类比 |
|------|------|---------|------|
| **FFN** | 对每个 token 独立做非线性变换 | $\text{FFN}(x) = W_2 \cdot \text{GELU}(W_1 \cdot x)$ | 后厨厨师深度加工 |
| **LayerNorm** | 稳定数值分布 | $y = \gamma \cdot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta$ | 品控质检员 |
| **残差连接** | 解决梯度消失 | $\text{out} = F(x) + x$ | 直达电梯 |

关键决策：**Pre-Norm vs Post-Norm** → 现代大模型都用 Pre-Norm

**打个比方**：注意力层像前台把顾客需求汇总，FFN 像后厨把原料加工成菜品，LayerNorm 像出餐前的品控，残差连接像信息和梯度的直达电梯。四者组合，模型才能堆得深、训得稳。

#### Day 2：Tokenizer 与词嵌入

从文字到数字的两步翻译：

```
文本 → Tokenizer → Token IDs → Embedding → 高维向量
```

| 概念 | 关键点 | 代表 |
|------|--------|------|
| BPE | 字符级开始，频率合并 | GPT 系列 |
| SentencePiece | 多语言友好 | LLaMA, Qwen |
| 词嵌入 | ID → 向量，捕捉语义 | 训练学出来 |
| 上下文嵌入 | 向量随上下文动态变化 | BERT, GPT |

**打个比方**：Tokenizer 是把一张手写订单拆成标准菜品编码；Embedding 则是给每种菜建立“口味、原料、用途”等多维档案，所以红豆沙和绿豆沙会比红豆沙和打印机更接近。

#### Day 3：GPT vs BERT 架构对比

| 维度 | GPT | BERT |
|------|-----|------|
| 架构 | Decoder-only | Encoder-only |
| 注意力 | 单向（因果掩码） | 双向 |
| 预训练 | 预测下一个词 | 完型填空 (MLM) |
| 擅长 | 生成、对话 | 分类、理解 |
| 现代代表 | LLaMA, Qwen, GPT-4 | DeBERTa, RoBERTa |

**大模型时代为什么 Decoder-only 胜出**：Scaling Law 友好、Zero-shot 能力强、工程简洁

**打个比方**：BERT 像可以反复看全文再作答的阅读理解专家；GPT 像不能偷看后文、只能根据前文逐字讲故事的演讲者。前者擅长判断，后者擅长生成。

#### Day 4：位置编码

| 方案 | 编码类型 | 外推能力 | 代表模型 |
|------|---------|---------|---------|
| 正弦 | 绝对位置 | 理论可以，实际差 | 原版 Transformer |
| 可学习 | 绝对位置 | 无 | BERT, GPT-2 |
| **RoPE** | **相对位置** | **强** | **LLaMA, Qwen** |
| ALiBi | 相对位置 | 很强 | BLOOM |

**RoPE 的核心原理**：通过旋转矩阵编码位置，注意力分数只依赖相对距离

**打个比方**：位置编码像给排队的顾客发号码牌。RoPE 不只是记录“你是第 7 位”，而是通过旋转角度让模型自然感受到“你和前一位相距多远”。

#### Day 5：推理优化

| 技术 | 解决问题 | 核心思想 |
|------|---------|---------|
| **KV Cache** | 重复计算 K/V | 缓存历史结果 |
| **Flash Attention** | 中间矩阵太大 | 分块计算 |
| **GQA** | KV Cache 显存大 | 多个 Q 共享 KV |

效果：让大模型从"老爷车"变成"F1 赛车"

**打个比方**：KV Cache 是已读订单不再重复抄写；Flash Attention 是把常用食材放到手边分批处理；GQA 是多个点单窗口共享少量高效柜台。它们分别减少重复计算、内存搬运和缓存体积。

#### Day 6：QLoRA 微调

```
QLoRA = 4-bit 量化（压缩模型） + LoRA（低秩适配器）
```

- 显存：7B 模型从 112GB → 6-8GB
- 参数：LoRA 仅占原始权重的 1-3%
- 效果：接近全量微调（差距 <1%）

**打个比方**：全量微调是把整家店重装一遍，LoRA 是只加一份可替换的菜谱补丁，QLoRA 则先把原有装修压缩存档，再用小补丁完成定制，所以普通显卡也能负担。

---

### 2.2 从数据到推理的完整流程

### 一个完整的"大模型生成回答"的流程

```
用户输入: "糖水店的红豆沙怎么做？"
    │
    ├─1. Tokenizer 分词
    │   "糖水店的红豆沙怎么做？" → [糖, 水店, 的, 红豆, 沙, 怎么, 做, ？]
    │   → token IDs: [1234, 5678, 90, 234, 567, 890, 123, 45]
    │
    ├─2. Embedding 查表
    │   每个 ID → 4096 维向量
    │   + RoPE 位置编码（注入位置信息）
    │
    ├─3. Transformer Block × N 层
    │   每层包含:
    │   ├─ Pre-LayerNorm
    │   ├─ Multi-Head Attention (因果掩码 + GQA)
    │   │   ├─ Q × K^T → 注意力分数
    │   │   ├─ Flash Attention 加速计算
    │   │   └─ × V → 加权输出
    │   ├─ 残差连接
    │   ├─ Pre-LayerNorm
    │   ├─ FFN (升维 → GELU → 降维)
    │   └─ 残差连接
    │
    │   推理时：KV Cache 缓存历史 K/V
    │
    ├─4. 输出层 → 下一个 token 的概率分布
    │   → 选择概率最高的 token (或采样)
    │
    └─5. 回到步骤 1，继续生成下一个 token（自回归）
        直到遇到 <EOS> 或达到最大长度

最终输出: "红豆沙的做法是：先将红豆浸泡..."
```

### 每个组件的位置和作用

```
┌─────────────────────────────────────────────────────┐
│                   大模型推理管线                       │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Tokenizer│ Embedding│Transform │   ...    │ Output  │
│  (Day 2) │+(RoPE)   │  Block   │ ×N layers│ Layer   │
│          │ (Day 4)  │ (Day 1)  │          │         │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│  推理优化 (Day 5):                                    │
│  ├─ KV Cache: 缓存历史 K/V                            │
│  ├─ Flash Attention: 分块计算注意力                    │
│  └─ GQA: 减少 KV 头数                                 │
├──────────────────────────────────────────────────────┤
│  微调优化 (Day 6):                                    │
│  ├─ QLoRA: 4-bit量化 + LoRA 适配器                    │
│  └─ 领域定制化                                         │
├──────────────────────────────────────────────────────┤
│  架构选择 (Day 3):                                    │
│  ├─ 生成任务 → Decoder-only (GPT系)                    │
│  └─ 理解任务 → Encoder-only (BERT系)                   │
└──────────────────────────────────────────────────────┘
```

---

## 三、代码实战

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

# ==========================================
# 综合演示：从文本到生成（简化版）
# ==========================================

def complete_transformer_pipeline():
    """完整的 Transformer 推理流水线演示"""
    
    print("=" * 60)
    print("🏭 Transformer 推理流水线完整演示")
    print("=" * 60)
    
    # Step 1: 分词
    text = "红豆沙好喝"
    tokens = list(text)
    token_ids = [hash(t) % 10000 for t in tokens]
    print(f"\n📝 Step 1: 分词")
    print(f"  原文: {text}")
    print(f"  Tokens: {tokens}")
    print(f"  IDs: {token_ids}")
    
    # Step 2: Embedding
    d_model = 64
    np.random.seed(42)
    embedding_table = np.random.randn(10000, d_model) * 0.1
    embeddings = np.array([embedding_table[id] for id in token_ids])
    print(f"\n🔢 Step 2: 词嵌入")
    print(f"  Embedding 形状: {embeddings.shape}")
    
    # Step 3: RoPE 位置编码
    seq_len = len(tokens)
    pos = np.arange(seq_len).reshape(-1, 1)
    freqs = 1.0 / (10000 ** (np.arange(0, d_model, 2) / d_model))
    angles = pos * freqs
    pos_encoding = np.zeros((seq_len, d_model))
    pos_encoding[:, 0::2] = np.sin(angles)
    pos_encoding[:, 1::2] = np.cos(angles)
    
    input_embeddings = embeddings + pos_encoding
    print(f"\n📍 Step 3: RoPE 位置编码")
    print(f"  位置编码形状: {pos_encoding.shape}")
    print(f"  最终输入形状: {input_embeddings.shape}")
    
    # Step 4: 自注意力（简化版）
    Q = input_embeddings
    K = input_embeddings
    V = input_embeddings
    
    # 因果掩码
    mask = np.triu(np.ones((seq_len, seq_len)) * -np.inf, k=1)
    
    d_k = d_model
    scores = np.dot(Q, K.T) / np.sqrt(d_k) + mask
    attn = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    attn /= np.sum(attn, axis=-1, keepdims=True)
    attn_output = np.dot(attn, V)
    print(f"\n🧠 Step 4: 自注意力")
    print(f"  注意力权重:\n{np.round(attn, 3)}")
    
    # Step 5: FFN
    W1 = np.random.randn(d_model, d_model * 4) * 0.1
    W2 = np.random.randn(d_model * 4, d_model) * 0.1
    
    def gelu(x):
        return 0.5 * x * (1 + np.tanh(np.sqrt(2/np.pi) * (x + 0.044715 * x**3)))
    
    ffn_output = np.dot(gelu(np.dot(attn_output, W1)), W2)
    
    # 残差连接
    final_output = input_embeddings + ffn_output
    print(f"\n💪 Step 5: FFN + 残差连接")
    print(f"  输出形状: {final_output.shape}")
    
    # Step 6: 预测下一个 token
    output_logits = np.dot(final_output[-1], embedding_table.T)
    predicted_id = np.argmax(output_logits)
    print(f"\n🎯 Step 6: 预测下一个 token")
    print(f"  预测 ID: {predicted_id}")
    
    return final_output

result = complete_transformer_pipeline()
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

fig, ax = plt.subplots(1, 1, figsize=(18, 10))

# 绘制知识图谱
topics = [
    (1, 5, 'Day1: FFN+LN+残差', '#e74c3c', 
     'FFN: 升维→激活→降维\nLayerNorm: 数值稳定\n残差: 梯度直达'),
    (3, 5, 'Day2: Tokenizer+嵌入', '#e67e22',
     'BPE: 频率合并分词\nSentencePiece: 多语言\nEmbedding: 语义向量'),
    (5, 5, 'Day3: GPT vs BERT', '#f39c12',
     'GPT: 单向生成\nBERT: 双向理解\nDecoder-only 胜出'),
    (7, 5, 'Day4: 位置编码', '#2ecc71',
     '正弦: 经典方案\nRoPE: 旋转编码(主流)\nALiBi: 线性偏置'),
    (9, 5, 'Day5: 推理优化', '#3498db',
     'KV Cache: 空间换时间\nFlash Attn: 分块计算\nGQA: 共享KV头'),
    (11, 5, 'Day6: QLoRA微调', '#9b59b6',
     '4-bit量化: 压缩模型\nLoRA: 低秩适配器\n消费级GPU可训练'),
]

# 绘制主题节点
for x, y, label, color, desc in topics:
    circle = plt.Circle((x, y), 0.8, color=color, alpha=0.8)
    ax.add_patch(circle)
    ax.text(x, y, label.split(':')[0], ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    ax.text(x, y - 2.5, label, ha='center', fontsize=11, fontweight='bold', color=color)
    ax.text(x, y - 3.5, desc, ha='center', fontsize=8, color='#555',
            va='top', linespacing=1.4)

# 绘制连接线（时间线）
for i in range(len(topics) - 1):
    x1 = topics[i][0] + 0.8
    x2 = topics[i+1][0] - 0.8
    ax.annotate('', xy=(x2, 5), xytext=(x1, 5),
                arrowprops=dict(arrowstyle='->', color='gray', lw=2))

# 顶部标题
ax.text(6, 8, '第二周：Transformer 工程优化', ha='center', 
        fontsize=20, fontweight='bold', color='#2c3e50')
ax.text(6, 7.2, '从内部零件到推理优化的完整技术栈', ha='center',
        fontsize=12, color='#7f8c8d')

# 底部关联
ax.text(6, 0.5, '🔗 所有知识点 → 企业AI部署能力', ha='center',
        fontsize=14, fontweight='bold', color='#2c3e50',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', edgecolor='#bdc3c7'))

ax.set_xlim(-0.5, 12.5)
ax.set_ylim(-0.5, 9)
ax.set_aspect('equal')
ax.axis('off')
plt.title('W2 知识图谱', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('/tmp/week2_summary.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 第二周知识图谱已生成！")
```

---

## 五、业务关联

### LangChat、Agent 与企业 AI 的一条落地链路

1. **模型选择**：LangChat 的对话回复、内容生成和工具调用，需要 Decoder-only 的 GPT 系模型；意图识别、文本分类和检索向量生成，可以用更轻量的 BERT 系模型。**打个比方**：GPT 是能主动接待顾客的店员，BERT 是负责把订单归类、找资料的后台专员。

2. **长上下文与知识库**：RoPE、GQA 和 Flash Attention 决定企业 AI 能否稳定处理长合同、产品手册和多轮聊天历史。**打个比方**：RoPE 是编号清晰的长卷宗，GQA 是共用档案柜，Flash Attention 是把正在用的资料放在手边，避免来回跑仓库。

3. **并发和成本**：KV Cache 让生成阶段避免重复计算，但每位用户都占一份缓存。部署时要把“响应速度、并发人数、显存”一起测算，而不是只看模型参数。**打个比方**：每位到店顾客都有一张点单记录，记录能加快服务，却也占用柜台空间。

4. **领域定制**：QLoRA 让企业能以很低成本训练专属助手，例如糖水店助手理解菜单、库存和记账格式，而不需要重训整个基础模型。**打个比方**：在通用店员培训手册上加一页本店菜谱补丁，就能让店员说本店的专业话。

---

## 六、常见误区

### 误区 1：把所有优化都理解为“让计算更快”
**纠正**：KV Cache 主要消除重复计算；Flash Attention 主要减少内存读写；GQA 主要缩小 KV Cache。它们作用在不同瓶颈上，通常组合使用。

### 误区 2：认为长上下文只要改大 `max_seq_length` 就行
**纠正**：模型的训练长度、位置编码外推能力、KV Cache 显存和注意力实现都会限制实际可用长度。RoPE 长度扩展、GQA、Flash Attention 必须一起考虑。

### 误区 3：认为 QLoRA 是“无损压缩 + 万能微调”
**纠正**：量化与低秩适配通常效果很好，但仍依赖高质量数据、合适的 rank、学习率和评估集。领域知识缺失或训练数据冲突时，QLoRA 也不能自动修复。

---

## 🧪 课堂练习（5分钟）

1. 画出“用户输入 → Tokenizer → Embedding+RoPE → Transformer Block → 下一个 token”的流程图，并标注 KV Cache 出现的位置。

2. 一句话回答：为什么 GPT 要使用因果掩码，而 BERT 不需要？

3. 将以下优化对应到主要瓶颈：KV Cache、Flash Attention、GQA、QLoRA。

---

## 📝 课后测试（15分钟）

1. **概念题**：为什么残差连接能改善深层网络中的梯度传播？请说明公式中关键的“+1”路径。

2. **计算题**：一个 32 层、d_model=4096、32 个注意力头、float16 的 MHA 模型，在序列长度 4096 时，KV Cache 约需要多少显存？写出计算过程。

3. **对比题**：分别用一句话解释 RoPE、Flash Attention、GQA 的核心收益；它们解决的是同一个问题吗？

4. **设计题**：为糖水店智能客服设计“基础模型 + RAG + QLoRA 适配器”的方案，说明每一层各负责什么。

5. **代码题**：用 NumPy 实现一个 4×4 的 GPT 因果掩码，并验证未来位置的注意力权重为 0。

---

## 附：下周预告

### 第三周：预训练与数据工程

第二周我们学了 Transformer 的**工程优化**（怎么让模型跑得好、跑得快）。第三周将进入**预训练**（怎么从零训练一个大模型）：

- **Day 1-2**：预训练数据工程——数据收集、清洗、Tokenization
- **Day 3-4**：预训练策略——学习率调度、Batch Size、Scaling Law
- **Day 5**：分布式训练——数据并行、张量并行、流水线并行
- **Day 6-7**：代码实战 + 复习

**你需要提前准备**：
- 复习第二周的 Tokenizer 和 Embedding 知识
- 了解基本的 PyTorch 操作
- 准备好 GPU 环境（至少一张消费级显卡）

---

## 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| FFN | [fiːd ˈfɔːrwərd ˈnetwɜːrk] | 前馈神经网络，逐 token 做非线性加工 |
| LayerNorm | [ˈleɪər ˌnɔːrməlaɪˈzeɪʃən] | 层归一化，稳定每层数值分布 |
| Residual Connection | [rɪˈzɪdjuəl kəˈnekʃən] | 残差连接，为信息与梯度提供捷径 |
| BPE | [baɪt peər ɪnˈkoʊdɪŋ] | 字节对编码，按频率合并子词的分词算法 |
| SentencePiece | [ˈsentəns piːs] | 直接处理原始文本的多语言分词方法 |
| Causal Attention | [ˈkɔːzəl əˈtenʃən] | 因果注意力，只允许关注当前及之前 token |
| MLM | [mæskt ˈlæŋɡwɪdʒ ˈmɒdəlɪŋ] | 掩码语言模型，BERT 的完型填空式预训练任务 |
| RoPE | [ˈroʊtəri pəˈzɪʃən] | 旋转位置编码，以旋转方式注入相对位置信息 |
| ALiBi | [eɪ-laɪ-baɪ] | 注意力线性偏置，对远距离 token 加线性惩罚 |
| KV Cache | [keɪ-viː kæʃ] | 键值缓存，复用历史 token 的 Key 与 Value |
| Flash Attention | [flæʃ əˈtenʃən] | 通过分块减少内存读写的精确注意力算法 |
| GQA | [dʒiː-kjuː-eɪ] | 分组查询注意力，多个 Query 共享一组 KV |
| QLoRA | [kjuː-lɔːrə] | 4-bit 量化与 LoRA 结合的高效微调方法 |
| LoRA | [loʊ-rænk ˌædæpˈteɪʃən] | 用低秩矩阵表示权重变化的参数高效微调方法 |
| NF4 | [ˈnɔːrməl floʊt fɔːr] | 针对正态权重分布设计的 4-bit 量化格式 |

---

## 📎 参考资源

### 核心论文
- [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762)
- [BERT (2018)](https://arxiv.org/abs/1810.04805)
- [GPT-2 (2019)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [RoPE (2021)](https://arxiv.org/abs/2104.09864)
- [ALiBi (2021)](https://arxiv.org/abs/2108.12409)
- [FlashAttention (2022)](https://arxiv.org/abs/2205.14135)
- [GQA (2023)](https://arxiv.org/abs/2305.13245)
- [QLoRA (2023)](https://arxiv.org/abs/2305.14314)
- [LoRA (2021)](https://arxiv.org/abs/2106.09685)

### 实用工具
- [Unsloth](https://github.com/unslothai/unsloth) - 2x 更快的 QLoRA 训练
- [PEFT](https://github.com/huggingface/peft) - HuggingFace 微调框架
- [vLLM](https://github.com/vllm-project/vllm) - 高性能推理引擎
- [tiktoken](https://github.com/openai/tiktoken) - OpenAI 分词器

### 可视化教程
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [The Illustrated GPT-2](https://jalammar.github.io/illustrated-gpt2/)
- [The Illustrated BERT](https://jalammar.github.io/illustrated-bert/)
- [Andrej Karpathy: Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)

---

> 🎉 **恭喜完成第二周！** 你已经从 Transformer 的"外部观察者"变成了"内部工程师"。理解了 FFN/LayerNorm/残差、Tokenizer/Embedding、GPT/BERT 架构、RoPE 位置编码、KV Cache/Flash Attention/GQA 推理优化、QLoRA 微调——这些都是大模型工程师的核心知识储备。
> 
> **下周我们将进入预训练的世界——从零开始训练一个大模型需要什么？数据怎么准备？训练怎么加速？敬请期待！** 🚀
