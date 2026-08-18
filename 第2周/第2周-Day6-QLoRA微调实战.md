# 📚 第2周-Day6：QLoRA 微调实战

> **前面四天我们学习了 Transformer 的内部结构和优化技术。今天进入实战环节——QLoRA 微调！这是目前最流行的大模型微调方案，让你能够在消费级 GPU（如 RTX 4060Ti）上微调几十亿参数的大模型。我们将以 Qwen2-0.5B 为例，打造一个糖水店记账助手。**

## 📅 学习进度

```
W1 ████████████████████ ✓ 已完成（Transformer 基础架构）
W2 ██████████████░░░░░░ ← 你在这里（Day 6/7）
W3 ░░░░░░░░░░░░░░░░░░░░ 预训练与数据工程
W4 ░░░░░░░░░░░░░░░░░░░░ 微调与对齐
...
W13 ░░░░░░░░░░░░░░░░░░░░ 综合项目
```

---

## 一、为什么需要 QLoRA？

### 问题：全量微调太贵了！

要微调一个 7B 模型：
- 模型参数：7B × 4 bytes（float32）= 28 GB
- 梯度：28 GB
- 优化器状态（Adam）：56 GB
- **总计：至少 112 GB 显存！**

这需要至少 2 张 A100（80GB），单张成本约 $20,000。

**而 QLoRA 只需要约 6-8 GB 显存**——一张 RTX 4060Ti 就够了！

**打个比方**：
- **全量微调**像"重新装修整栋大楼"——要移动每一面墙，成本极高
- **LoRA 微调**像"在大楼里加几块移动隔板"——不改原结构，只加小改动
- **QLoRA** 先把大楼"压缩"（量化），再加隔板——成本最低

### QLoRA = Quantization + LoRA

两个核心技术的组合：

1. **4-bit 量化**：把模型权重从 float32 压缩到 4 位整数，显存减少 87.5%
2. **LoRA**：冻结原模型，只训练一个很小的"适配器"（约 1-2% 的参数量）

---

## 二、核心原理详解

### 2.1 量化（Quantization）—— 压缩模型权重

#### 什么是量化？

把高精度的浮点数映射到低精度的整数：

```
float32: 0.12345678  → int4: 2  (范围 0-15)
float32: -0.87654321 → int4: -7 (范围 -8 到 7)
```

**打个比方**：就像把高清图片（4K）压缩成标清（480p）—— 占用空间大幅缩小，虽然细节损失了，但整体内容还能看清。

#### NF4（NormalFloat 4-bit）

QLoRA 使用特殊的 NF4 量化方式，不是均匀量化，而是根据权重的实际分布（正态分布）来设计量化区间——在权重密集的区域用更精细的量化。

```
均匀量化: |---|---|---|---|---|---|---|---|  (等间距)
NF4量化:  |-|--|---|----|----|---|--|-|        (在0附近更密集)
```

#### 量化对效果的影响

| 精度 | 每参数字节 | 7B 模型大小 | 效果损失 |
|------|-----------|------------|---------|
| float32 | 4 | 28 GB | 0%（基准） |
| float16 | 2 | 14 GB | <0.1% |
| int8 | 1 | 7 GB | ~0.5% |
| **NF4** | **0.5** | **3.5 GB** | **~1%** |

1% 的效果损失换来 87.5% 的显存节省——非常划算！

### 2.2 LoRA（Low-Rank Adaptation）—— 低秩适配器

#### 核心思想

不修改原始权重矩阵 $W$，而是加一个"补丁" $\Delta W$：

$$W' = W + \Delta W$$

但 $\Delta W$ 直接学习太大了（跟 $W$ 一样大），LoRA 的妙招是**把 $\Delta W$ 分解成两个小矩阵的乘积**：

$$\Delta W = A \times B$$

其中：
- $A \in \mathbb{R}^{d \times r}$（降维矩阵）
- $B \in \mathbb{R}^{r \times d}$（升维矩阵）
- $r$ 是秩（rank），通常取 8、16、32

**打个比方**：
- 原始权重 $W$ 是一本 1000 页的百科全书（$d \times d = 1024 \times 1024$）
- LoRA 适配器 $A \times B$ 像一份 16 页的"修订补丁"（$d \times r + r \times d = 1024 \times 16 + 16 \times 1024$）
- 最终效果 = 百科全书 + 修订补丁

#### 参数量对比

当 $d=4096, r=16$ 时：
- 原始权重 $W$：$4096 \times 4096 = 16,777,216$ 参数
- LoRA 适配器 $A + B$：$4096 \times 16 + 16 \times 4096 = 131,072$ 参数
- **LoRA 参数量仅为原始的 0.78%！**

#### LoRA 的三个关键参数

| 参数 | 含义 | 推荐值 | 影响 |
|------|------|--------|------|
| **r (rank)** | 适配器的秩 | 16 或 32 | r 越大，学习能力越强，但参数越多 |
| **alpha** | 缩放系数 | 2 × r | 控制 LoRA 贡献的权重 |
| **target_modules** | 加适配器的层 | q_proj, k_proj, v_proj, o_proj | 决定微调哪些层 |

#### 为什么 LoRA 有效？

研究表明，大模型微调时权重的变化量 $\Delta W$ 是"低秩"的——不需要完整的 $d \times d$ 自由度来表示微调所需的变化。用 $r=16$ 的低秩近似就足够了。

### 2.3 QLoRA = 4-bit 量化 + LoRA

QLoRA 的完整流程：

```
1. 加载预训练模型，权重用 NF4 量化存储（4-bit）
   模型大小: 7B × 0.5 bytes = 3.5 GB

2. 冻结所有 4-bit 权重（不更新）

3. 在注意力层的旁边添加 LoRA 适配器（float16 精度）
   适配器大小: 约 20-40 MB

4. 前向传播:
   x → 4-bit 解量化为 float16 → W·x + alpha/r × (B·A)·x

5. 反向传播:
   只计算 LoRA 适配器 A 和 B 的梯度
   原始 W 的梯度为零（冻结）

6. 训练完成后:
   可以将 LoRA 合并到原始权重中（可选）
```

**显存占用对比（7B 模型）**：
- 全量微调：~112 GB（需要多卡 A100）
- LoRA（float16）：~28 GB（需要 A100 40G）
- **QLoRA（4-bit）**：**~6-8 GB（RTX 4060Ti 即可！）**

---

## 三、代码实战

### 3.1 LoRA 参数效率分析

```python
def analyze_lora_params(d_model=4096, r_values=[4, 8, 16, 32, 64]):
    """分析不同 rank 下 LoRA 的参数效率"""
    original_params = d_model * d_model
    
    print(f"原始权重参数量: {original_params:,}")
    print(f"{'rank':<8} {'LoRA参数':<15} {'原始参数':<15} {'占比':<10} {'效果参考':<10}")
    print("-" * 60)
    
    for r in r_values:
        lora_params = 2 * d_model * r  # A: d×r, B: r×d
        ratio = lora_params / original_params * 100
        effect = {"4": "简单任务", "8": "一般任务", "16": "推荐", 
                  "32": "复杂任务", "64": "高精度"}[str(r)]
        print(f"r={r:<5} {lora_params:<15,} {original_params:<15,} {ratio:<10.2f}% {effect}")
    
    print(f"\n⭐ r=16 是最常用的平衡点：效果好，参数少")

analyze_lora_params()
```

### 3.2 完整 QLoRA 微调流程（伪代码）

```python
# ========================================
# QLoRA 微调完整流程
# ========================================

# Step 1: 安装依赖
# pip install unsloth  # 或 pip install peft transformers bitsandbytes

# Step 2: 加载模型（4-bit 量化）
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2-0.5B",
    max_seq_length=2048,
    load_in_4bit=True,      # ⭐ 4-bit 量化加载
    dtype=None,             # 自动选择精度
)
print(f"模型参数量: {model.num_parameters() / 1e9:.2f}B")
print(f"4-bit 量化后显存: ~300MB")

# Step 3: 配置 LoRA 适配器
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,                           # 秩（推荐 16 或 32）
    lora_alpha=32,                  # 缩放系数（通常 = 2 × r）
    target_modules=[                # 在哪些层加 LoRA
        "q_proj", "k_proj", 
        "v_proj", "o_proj",
    ],
    lora_dropout=0.05,              # LoRA 层的 dropout
    bias="none",                    # 不训练偏置
    task_type="CAUSAL_LM",          # 因果语言模型
)

model = model.get_peft_model(lora_config)

# Step 4: 准备训练数据
train_data = [
    {"instruction": "记录销售", "input": "卖了3碗红豆沙", 
     "output": "已记录：红豆沙 × 3碗"},
    {"instruction": "查询库存", "input": "红豆还有多少？", 
     "output": "当前红豆库存：15公斤"},
    # ... 更多数据
]

# Step 5: 训练
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./qwen2-sweetshop",
    num_train_epochs=3,              # 训练轮数
    per_device_train_batch_size=4,   # 每卡 batch size
    gradient_accumulation_steps=4,   # 梯度累积（等效 batch=16）
    learning_rate=2e-4,              # 学习率
    logging_steps=10,                # 每 10 步打印一次日志
    save_steps=100,                  # 每 100 步保存一次
    warmup_ratio=0.03,               # 预热比例
    lr_scheduler_type="cosine",      # 学习率调度器
    optim="adamw_8bit",              # 8-bit 优化器（进一步省内存）
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
)
trainer.train()

# Step 6: 保存 LoRA 适配器（只有几十 MB！）
model.save_pretrained("./qwen2-sweetshop-lora")
print(f"LoRA 适配器已保存（约 {sum(p.numel() for p in model.parameters() if p.requires_grad) / 1e6:.1f}M 参数）")

# Step 7: 推理测试
from unsloth import FastLanguageModel
FastLanguageModel.for_inference(model)

messages = [
    {"role": "system", "content": "你是一个糖水店记账助手"},
    {"role": "user", "content": "今天卖了多少碗绿豆沙？"},
]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt")
outputs = model.generate(inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 3.3 LoRA 矩阵分解的数学直觉

```python
import numpy as np

def demonstrate_lora_decomposition():
    """演示 LoRA 低秩分解的效果"""
    d = 512  # 原始维度
    r = 16   # 秩
    
    # 创建一个"低秩"的权重变化矩阵
    A = np.random.randn(d, r) * 0.1  # d×r
    B = np.random.randn(r, d) * 0.1  # r×d
    delta_W = A @ B                  # d×d，但本质秩只有 r
    
    original_size = d * d
    lora_size = d * r + r * d
    
    print(f"原始矩阵 ΔW 形状: ({d}, {d})")
    print(f"  参数量: {original_size:,}")
    print(f"LoRA 分解 (A×B): ({d}×{r}) + ({r}×{d})")
    print(f"  参数量: {lora_size:,}")
    print(f"  参数减少: {100*(1-lora_size/original_size):.1f}%")
    print(f"\n虽然参数少了 {(1-lora_size/original_size)*100:.1f}%，")
    print(f"但 A×B 仍然能表达很多种 ΔW 变化！")

demonstrate_lora_decomposition()
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

# 图1: 不同微调方式的显存对比
methods = ['全量微调\n(float32)', 'LoRA\n(float16)', 'QLoRA\n(NF4)']
memory_7b = [112, 28, 6]
colors = ['#e74c3c', '#f39c12', '#2ecc71']

bars = axes[0].bar(methods, memory_7b, color=colors, edgecolor='black')
axes[0].set_title('7B 模型微调显存对比', fontsize=13, fontweight='bold')
axes[0].set_ylabel('显存占用 (GB)')
for bar, mem in zip(bars, memory_7b):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{mem} GB', ha='center', fontweight='bold')
axes[0].axhline(y=16, color='red', linestyle='--', alpha=0.7, label='RTX 4060Ti (16GB)')
axes[0].legend()

# 图2: LoRA 参数量 vs rank
d = 4096
ranks = [1, 2, 4, 8, 16, 32, 64, 128]
lora_params = [2 * d * r for r in ranks]
original = d * d

axes[1].plot(ranks, [p/original*100 for p in lora_params], 'b-o', linewidth=2)
axes[1].set_title('LoRA 参数占比 vs Rank (d=4096)', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Rank (r)')
axes[1].set_ylabel('LoRA 参数 / 原始参数 (%)')
axes[1].axvline(x=16, color='red', linestyle='--', alpha=0.5, label='r=16 (推荐)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 图3: 量化精度对比
precisions = ['float32', 'float16', 'int8', 'NF4']
bits = [32, 16, 8, 4]
model_sizes = [28, 14, 7, 3.5]
quality = [100, 99.9, 99.5, 99]

ax3a = axes[2]
ax3b = ax3a.twinx()
bars = ax3a.bar(precisions, model_sizes, alpha=0.7, color=['#e74c3c', '#f39c12', '#3498db', '#2ecc71'])
line = ax3b.plot(precisions, quality, 'r-o', linewidth=2, markersize=8)
ax3a.set_title('量化精度对比（7B 模型）', fontsize=13, fontweight='bold')
ax3a.set_ylabel('模型大小 (GB)', color='gray')
ax3b.set_ylabel('效果保留 (%)', color='red')
ax3b.set_ylim(95, 101)

plt.tight_layout()
plt.savefig('/tmp/qlora_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 可视化图表已生成！")
```

---

## 五、业务关联

### 与 LangChat / Agent / 企业 AI 的关系

1. **企业定制化微调**：用 QLoRA 在通用大模型基础上注入领域知识（糖水店菜单、定价、话术等），无需昂贵的 GPU 集群。

2. **LoRA 适配器即插件**：一个基础模型 + 多个 LoRA 适配器 = 多种业务能力。切换成本只需几 MB 的文件。

3. **数据隐私**：QLoRA 可以在本地 GPU 上微调，不需要把数据上传到云服务——满足企业的数据合规要求。

4. **糖水店实战**：
   - 基础模型：Qwen2-0.5B（通用对话能力）
   - LoRA 适配器：糖水店专属知识（菜单、库存、记账格式）
   - 部署：RTX 4060Ti 单卡即可运行
   - 成本：电费 + 一次性训练时间（约 30 分钟）

5. **LangChat 集成**：LangChat 可以加载 LoRA 微调后的模型，实现企业专属的 AI 助手。

---

## 六、常见误区

### 误区 1: "量化后效果会差很多"
**纠正**：NF4 量化对效果的影响通常不到 1%。在大多数任务上，QLoRA 微调的效果接近全量微调。这是因为权重分布近似正态分布，NF4 量化在重要区域保留了足够的精度。

### 误区 2: "LoRA 只能微调注意力层"
**纠正**：虽然最常见的做法是对 q_proj、k_proj、v_proj、o_proj 加 LoRA，但你也可以对 FFN 层（gate_proj、up_proj、down_proj）加 LoRA。对更多层加 LoRA 通常能提升效果，但参数量也更多。

### 误区 3: "rank 越大效果越好"
**纠正**：不一定！研究表明，rank 从 8 提升到 16 通常有明显提升，但从 32 提升到 64 的收益就很小了。而且 rank 太大可能导致过拟合（特别是数据量少的时候）。r=16 是经过大量验证的最佳平衡点。

---

## 🧪 课堂练习（5分钟）

1. **计算题**：d_model=4096，r=16，对 4 个注意力投影层（q/k/v/o）加 LoRA，总共多少 LoRA 参数？占原始 4 层权重的百分之几？

2. **概念题**：为什么 QLoRA 的 4-bit 量化不影响反向传播？

3. **选择题**：QLoRA 微调中，以下哪些参数会被更新？
   - A) 原始模型权重 W
   - B) LoRA 矩阵 A 和 B
   - C) LayerNorm 的 gamma 和 beta
   - D) Embedding 层

---

## 📝 课后测试（15分钟）

1. **简答题**：解释 LoRA 的低秩分解原理。为什么 $\Delta W = A \times B$（其中 $A \in \mathbb{R}^{d \times r}$, $B \in \mathbb{R}^{r \times d}$）可以用远少于 $d \times d$ 的参数有效表示 $\Delta W$？

2. **计算题**：Qwen2-0.5B 模型用 NF4 量化加载后约 300MB。如果对 q_proj 和 v_proj（d_model=896）加 LoRA（r=8），LoRA 适配器有多少参数？

3. **实践题**：准备 10 条糖水店对话数据，使用 Unsloth 对 Qwen2-0.5B 做 QLoRA 微调。记录训练前后的效果差异。

4. **分析题**：QLoRA 训练时，前向传播需要先把 4-bit 权重"解量化"为 float16，这引入了额外的计算开销。为什么总的训练成本仍然远低于全量微调？

5. **设计题**：为你的企业设计一个 QLoRA 微调流水线：(1) 选择基础模型 (2) 准备训练数据 (3) 配置 LoRA 参数 (4) 训练和评估 (5) 部署方案。

---

## 🔑 今日术语

| 英文 | 音标 | 中文解释 |
|------|------|---------|
| QLoRA | [kjuː-lɔːrə] | 量化低秩适配，4-bit量化 + LoRA 的组合方案 |
| LoRA (Low-Rank Adaptation) | [loʊ-rænk ˌædæpˈteɪʃən] | 低秩适配，用小矩阵分解模拟大权重变化 |
| Quantization | [ˌkwɒntɪˈzeɪʃən] | 量化，将高精度浮点数映射到低精度整数 |
| NF4 (NormalFloat 4-bit) | [ˈnɔːrməl floʊt fɔːr] | 正态浮点 4 位量化，QLoRA 的量化方案 |
| Rank (r) | [ræŋk] | 秩，LoRA 适配器的核心超参数 |
| Adapter | [əˈdæptər] | 适配器，附加在冻结模型上的小型可训练模块 |
| Frozen Weights | [ˈfroʊzən weɪts] | 冻结权重，训练时不更新的原始模型参数 |
| Fine-tuning | [faɪn ˈtjuːnɪŋ] | 微调，在预训练模型基础上进行特定任务的训练 |
| Gradient Accumulation | [ˈɡreɪdiənt əˌkjuːmjʊˈleɪʃən] | 梯度累积，用小 batch 模拟大 batch 的技术 |
| Per-device Batch Size | [pɜːr dɪˈvaɪs bæʃ saɪz] | 单卡 batch size |

---

## 📎 参考资源

- 📄 [QLoRA: Efficient Finetuning of Quantized LLMs (2023)](https://arxiv.org/abs/2305.14314) - QLoRA 原论文
- 📄 [LoRA: Low-Rank Adaptation of Large Language Models (2021)](https://arxiv.org/abs/2106.09685) - LoRA 原论文
- 📄 [Intrinsic Dimensionality Explains LoRA Effectiveness](https://arxiv.org/abs/2307.03342) - 为什么 LoRA 有效
- 🔧 [Unsloth - 2x faster QLoRA training](https://github.com/unslothai/unsloth) - 加速训练框架
- 🔧 [PEFT - HuggingFace](https://github.com/huggingface/peft) - 官方 LoRA 实现
- 🔧 [bitsandbytes - 8-bit/4-bit quantization](https://github.com/bitsandbytes-foundation/bitsandbytes) - 量化库
- 🎥 [Sebastian Raschka: Practical Tips for LLM Fine-tuning](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms) - 微调实战指南

---

> 💡 **明日预告**：Day 7 是第二周的总结复习日！我们将把 Day1-Day6 的所有知识点串联起来，形成完整的 Transformer 工程优化技术图谱。
