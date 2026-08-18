# 📚 第三周-Day7：第三周总复习

> **三周前，Transformer 还只是一堆 Q、K、V 的数学符号。今天，你已经理解了从预训练到 SFT、从 RLHF 到 DPO 的完整训练链路。这些知识串在一起，就是一部"大模型如何诞生"的完整史诗。今天的任务：回顾、串联、巩固。**

## 📅 学习进度

| 阶段 | 状态 |
|------|------|
| W1：Transformer 基础架构 | ✅ 已完成 |
| W2：Transformer 深入理解 | ✅ 已完成 |
| **W3：大模型训练全景** | ✅ **完成！** |
| W4-W12 | ⏳ 待开始 |

---

## 一、为什么需要第三周总复习？

三周的知识不是三摞互不相干的笔记，而是一台大模型从“读懂语言”到“能为企业服务”的完整机器。复习的目标不是再背一次术语，而是看清各组件之间的因果关系：Transformer 是发动机，推理优化是省油装置，训练与对齐则决定它最后是否会按人的需求工作。

生活类比：学会单个乐器，只是掌握了声音；能把鼓点、旋律和节奏合成一首歌，才算真正会演奏。W1-W3 的复习，就是把分散的知识点合成一条可落地的工程链路。

### 1.1 三周学习路线总览

```
🗺️ 大模型工程师学习路线

═══════ Week 1: Transformer 基础 ═══════
Day1  自注意力机制     → Q×K→softmax→×V
Day2  多头注意力       → 多角度并行关注
Day3  Transformer架构  → Encoder-Decoder
Day4  位置编码         → 让模型知道词的位置
Day5  GPT架构演进      → Decoder-Only的崛起

═══════ Week 2: Transformer 深入 ═══════
Day1  FFN+LayerNorm+残差 → 深层网络的关键组件
Day2  Tokenizer详解      → 文字→数字的魔法
Day3  KV Cache           → 推理加速第一课
Day4  Flash Attention    → IO优化革命
Day5  GQA+PagedAttention → 显存与效率的平衡

═══════ Week 3: 大模型训练全景 ═══════
Day1  预训练+Scaling Law  → 数据+规模=涌现
Day2  SFT监督微调         → 教模型"听指令做事"
Day3  RLHF人类反馈        → 让模型理解人类偏好
Day4  DPO+其他对齐方法    → 简化版对齐革命
Day5  全流程+超参调优     → 从数据到部署的7步
Day6  SFT实战             → Qwen2-0.5B微调
Day7  总复习（今天！）     → 串联所有知识
```

### 1.2 核心知识卡片（14张）

| # | 周次 | 知识点 | 一句话总结 |
|---|------|--------|-----------|
| 1 | W1 | 自注意力 | 每个词"查看"所有其他词，找到最重要的信息 |
| 2 | W1 | 多头注意力 | 多个"视角"并行关注，最后合并结果 |
| 3 | W1 | Transformer | Encoder理解输入，Decoder生成输出 |
| 4 | W1 | 位置编码 | 给每个位置一个独特"指纹"，RoPE最优 |
| 5 | W1 | GPT架构 | Decoder-Only + 自回归生成 |
| 6 | W2 | FFN+残差 | 非线性变换 + 梯度高速公路 |
| 7 | W2 | Tokenizer | BPE/WordPiece：文字到数字的桥梁 |
| 8 | W2 | KV Cache | 缓存历史信息，推理加速2-5倍 |
| 9 | W2 | Flash Attention | 减少IO，让计算不被内存拖后腿 |
| 10 | W3 | 预训练 | "读万卷书"→涌现能力 |
| 11 | W3 | SFT | "学社交礼仪"→遵循指令 |
| 12 | W3 | RLHF | "人类导师指导"→符合偏好 |
| 13 | W3 | DPO | "简化版RLHF"→工程友好 |
| 14 | W3 | 超参调优 | 学习率是灵魂，早停法是保险 |

---

## 二、核心原理详解

### 2.1 从 Tokenizer 到模型输出：完整数据流

```
用户输入: "糖水店有什么推荐？"
      ↓
1. Tokenizer 分词
   ["糖","水","店","有","什么","推荐","？"]
      ↓
2. 转换为 Token ID
   [1234, 5678, 9012, 3456, 7890, 2345, 6789]
      ↓
3. 词嵌入 (Embedding)
   每个ID → 768维向量 (或更高)
      ↓
4. 位置编码 (RoPE)
   给每个位置加上位置信息
      ↓
5. N层 Transformer Block
   每层包含:
   ├── 多头自注意力 (W1核心)
   ├── FFN前馈网络 (W2核心)
   ├── LayerNorm + 残差连接 (W2核心)
   └── KV Cache加速推理 (W2核心)
      ↓
6. 输出层 + Softmax
   计算下一个词的概率分布
      ↓
7. 采样生成
   下一个Token: "推荐" → "杨" → "枝" → "甘" → "露"
      ↓
最终输出: "推荐杨枝甘露，芒果+西柚+西米..."
```

### 2.2 大模型训练的"四级火箭"

```
🚀 大模型诞生记（类比火箭发射）

第1级火箭: 预训练 (Day1)
  ⛽ 燃料: TB级文本数据
  🎯 目标: 学会语言规律和世界知识
  📊 效果: 能续写文本，但不会对话
  💰 成本: $500万+

第2级火箭: SFT (Day2)
  ⛽ 燃料: 1万~10万条指令数据
  🎯 目标: 学会遵循指令进行对话
  📊 效果: 能回答问题了！但可能不够友好
  💰 成本: $5000+

第3级火箭: 对齐训练 RLHF/DPO (Day3-4)
  ⛽ 燃料: 人类偏好数据
  🎯 目标: 回答更有用、更安全、更符合期望
  📊 效果: 像一个懂礼仪的专业助手了！
  💰 成本: $1万~5万

第4级火箭: 超参调优+评估 (Day5)
  ⛽ 燃料: 验证集 + 测试集
  🎯 目标: 在质量和成本间找到最优平衡
  📊 效果: 可以部署到生产环境了！
  💰 成本: 持续投入

🚀 入轨: 部署上线
  模型服务化，接入产品，开始服务用户！
```

### 2.3 各阶段 Loss 函数对比

| 阶段 | Loss 函数 | 说人话 |
|------|---------|--------|
| 预训练 | Cross-Entropy | "我猜下一个词对不对" |
| SFT | Cross-Entropy（只在回答部分） | "我猜标准答案对不对" |
| RLHF | -Reward + β×KL | "我想拿高分又不跑偏" |
| DPO | -log(σ(β×Δlogπ)) | "好回答概率要比坏回答高" |

---

## 三、代码实战

下面用一个极简、可运行的 NumPy 例子，把“预训练预测下一个 token”与“SFT 只对回答部分计算损失”放在同一段代码中复习。它不是完整大模型，而是帮助理解训练目标的最小实验。

```python
import numpy as np

# 固定随机种子，保证每次运行结果一致。
np.random.seed(42)
# 三个位置的词表大小均设为5，模拟模型输出的未归一化分数（logits）。
logits = np.random.randn(3, 5)
# 每个位置的正确下一个 token 编号。
targets = np.array([1, 3, 0])
# mask=0 表示指令部分；mask=1 表示助手回答部分，需要计算 SFT Loss。
answer_mask = np.array([0, 1, 1])
# 稳定版 softmax：先减去最大值，避免 exp 溢出。
exp_logits = np.exp(logits - logits.max(axis=1, keepdims=True))
probabilities = exp_logits / exp_logits.sum(axis=1, keepdims=True)
# 取出正确 token 的预测概率，并加极小值避免 log(0)。
correct_probabilities = probabilities[np.arange(len(targets)), targets]
token_losses = -np.log(correct_probabilities + 1e-12)
# 预训练：所有位置都要预测下一个 token。
pretrain_loss = token_losses.mean()
# SFT：只让回答部分承担损失，模型不必学习复述用户指令。
sft_loss = (token_losses * answer_mask).sum() / answer_mask.sum()

print(f"预训练 Loss: {pretrain_loss:.4f}")
print(f"SFT 回答部分 Loss: {sft_loss:.4f}")
print("结论：同一个交叉熵公式，数据格式和 mask 决定了训练行为。")
```

## 🧪 课堂练习（5分钟）

1. 用一句话把 Tokenizer、Embedding、自注意力、Softmax 串成模型生成回答的流程。
2. 给“糖水店客服”设计一条 SFT 数据：写出用户问题、系统角色和理想回答。
3. 如果用户只给了“点赞/踩”记录，没有回答成对排序，你会优先尝试 DPO 还是 KTO？说明原因。

---

## 📝 课后测试（15分钟）

### 📝 选择题（每题3分）

**1. 在 Transformer 中，自注意力机制的核心作用是？**
- A. 减少模型参数量
- B. 捕捉序列中不同位置之间的依赖关系
- C. 替代循环神经网络
- D. 加速GPU计算

**2. RoPE 位置编码的主要优势是？**
- A. 绝对位置信息
- B. 相对位置信息，适合变长序列
- C. 位置无关性
- D. 不需要计算

**3. KV Cache 的作用是？**
- A. 存储模型权重
- B. 缓存注意力的K、V，避免重复计算
- C. 存储训练数据
- D. 压缩模型大小

**4. 预训练中"涌现能力"的特征是？**
- A. 随着参数增加，性能线性提升
- B. 模型规模超过临界点后突然出现新能力
- C. 只在训练数据量增大时出现
- D. 所有能力都是涌现出来的

**5. SFT 和预训练最大的区别是？**
- A. SFT使用GPU，预训练不用
- B. SFT用指令数据，预训练用纯文本
- C. SFT训练更快
- D. SFT不需要Loss函数

**6. RLHF 中奖励模型的作用是？**
- A. 直接生成回答
- B. 判断回答的好坏，给策略模型提供信号
- C. 加速推理
- D. 压缩模型

**7. DPO 相比 RLHF 的核心优势是？**
- A. 效果更好
- B. 不需要训练奖励模型和PPO，简化流程
- C. 需要的数据更少
- D. 模型更小

**8. 微调大模型时，推荐的学习率是？**
- A. 0.1~1.0
- B. 1e-5~5e-5
- C. 1e-10
- D. 随便设

### 📝 判断题（每题2分）

**9.** 大模型的涌现能力可以通过增加训练轮数在小模型上获得。（❌/✅）

**10.** LoRA 只训练模型 0.3% 的参数，但效果接近全参数微调。（❌/✅）

**11.** DPO 完全不需要参考模型。（❌/✅）

**12.** INT4 量化在所有任务上都没有精度损失。（❌/✅）

**13.** 早停法监控的是训练集 Loss。（❌/✅）

### 📝 简答题（每题5分）

**14.** 用一句话解释从"预训练"到"DPO"每一阶段模型获得了什么新能力。

**15.** 如果你是一家甜品店的老板，预算1万元做AI客服，你会怎么规划？（列出方案）

---

## 四、可视化理解

### 4.1 W1-W3 知识地图

```python
import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
from matplotlib import font_manager
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(16, 10))

# 三周的列
weeks = {
    'W1: Transformer基础': 1,
    'W2: 深入理解': 2,
    'W3: 训练全景': 3
}

# 知识点定义 (name, week, row, color)
points = [
    # W1
    ('自注意力\nQ,K,V', 1, 5, '#FF6B6B'),
    ('多头注意力\nMulti-Head', 1, 4, '#FF6B6B'),
    ('位置编码\nRoPE', 1, 3, '#FF8E72'),
    ('Transformer\n架构', 1, 2, '#FF8E72'),
    ('GPT Decoder\n架构', 1, 1, '#FFB347'),
    # W2
    ('FFN+LayerNorm\n+残差', 2, 5, '#4ECDC4'),
    ('Tokenizer\nBPE', 2, 4, '#4ECDC4'),
    ('KV Cache\n推理加速', 2, 3, '#45B7D1'),
    ('Flash\nAttention', 2, 2, '#45B7D1'),
    ('GQA+Paged\nAttention', 2, 1, '#96CEB4'),
    # W3
    ('预训练\nScaling Law', 3, 5, '#DDA0DD'),
    ('SFT\n监督微调', 3, 4, '#DDA0DD'),
    ('RLHF\n人类反馈', 3, 3, '#FF6B6B'),
    ('DPO\n偏好优化', 3, 2, '#FF8E72'),
    ('超参调优\n全流程', 3, 1, '#FFB347'),
]

# 绘制知识点
for name, week, row, color in points:
    x = week
    y = row
    circle = plt.Circle((x, y), 0.3, facecolor=color, edgecolor='black', 
                         linewidth=1.5, alpha=0.8)
    ax.add_patch(circle)
    ax.text(x, y, name, ha='center', va='center', fontsize=7.5, fontweight='bold')

# 画箭头连接（关键依赖关系）
connections = [
    (1, 5, 2, 5),   # 自注意力 → FFN
    (1, 4, 2, 4),   # 多头注意力 → Tokenizer
    (1, 3, 2, 3),   # 位置编码 → KV Cache
    (1, 2, 2, 2),   # Transformer → Flash Attn
    (2, 5, 3, 5),   # FFN → 预训练
    (2, 4, 3, 4),   # Tokenizer → SFT
    (2, 3, 3, 3),   # KV Cache → RLHF
    (3, 5, 3, 4),   # 预训练 → SFT
    (3, 4, 3, 3),   # SFT → RLHF
    (3, 3, 3, 2),   # RLHF → DPO
    (3, 2, 3, 1),   # DPO → 超参调优
]

for x1, y1, x2, y2 in connections:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5, alpha=0.5))

ax.set_xlim(0.3, 3.7)
ax.set_ylim(0.3, 5.7)
ax.set_aspect('equal')
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['W1: Transformer基础', 'W2: 深入理解', 'W3: 训练全景'], fontsize=13)
ax.set_yticks([])
ax.set_title('🗺️ W1-W3 知识全景地图', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()
```

### 4.2 训练流水线一图总览

```python
# 完整训练流程图
fig, ax = plt.subplots(figsize=(14, 7))

steps = [
    ('📥 数据收集', 0, '#FF6B6B'),
    ('🧹 数据清洗', 1, '#FF8E72'),
    ('🎯 预训练', 2, '#FFB347'),
    ('✂️ SFT微调', 3, '#96CEB4'),
    ('🤝 对齐训练', 4, '#4ECDC4'),
    ('📊 评估测试', 5, '#45B7D1'),
    ('🚀 部署上线', 6, '#DDA0DD'),
]

descriptions = [
    'TB级文本\n+企业数据',
    '去重+质量过滤\n+格式统一',
    '海量数据训练\n→基础模型',
    '指令数据微调\n→对话模型',
    'RLHF/DPO\n→对齐模型',
    '准确率+安全\n+人工测试',
    '量化+加速\n+服务化'
]

for i, (name, x, color) in enumerate(steps):
    # 矩形框
    ax.add_patch(plt.Rectangle((x*1.8, 3), 1.5, 1.5, facecolor=color, 
                                 edgecolor='black', linewidth=2, alpha=0.85))
    ax.text(x*1.8+0.75, 3.75, name, ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(x*1.8+0.75, 2.5, descriptions[i], ha='center', va='top', fontsize=9)
    
    # 箭头
    if i < len(steps)-1:
        ax.annotate('', xy=((x+1)*1.8, 3.75), xytext=(x*1.8+1.5, 3.75),
                    arrowprops=dict(arrowstyle='->', color='black', lw=2))

ax.set_xlim(-0.5, 13.5)
ax.set_ylim(1, 6)
ax.axis('off')
ax.set_title('大模型训练完整流水线：从数据到上线', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()
```

### 4.3 学习进度统计

```python
# 学习进度可视化
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 左图：周进度
weeks_labels = ['W1\nTransformer', 'W2\n深入理解', 'W3\n训练全景', 'W4\nRAG\n(下周)', 'W5-12\n待学']
progress = [100, 100, 100, 0, 0]
colors_p = ['#96CEB4', '#4ECDC4', '#FF6B6B', '#E0E0E0', '#E0E0E0']

bars = axes[0].bar(weeks_labels, progress, color=colors_p, edgecolor='black')
axes[0].set_ylabel('完成度 (%)', fontsize=12)
axes[0].set_title('📚 学习进度总览', fontsize=14)
axes[0].set_ylim(0, 115)
for bar, p in zip(bars, progress):
    axes[0].text(bar.get_x() + bar.get_width()/2, p+3,
                 f'{p}%' if p > 0 else '⏳', ha='center', fontsize=12)

# 右图：知识掌握度雷达图
categories = ['Transformer\n架构', '推理优化', '训练流程', '对齐方法', '实战能力']
mastery = [85, 75, 80, 78, 65]  # 自评分数

angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
mastery += mastery[:1]
angles += angles[:1]

ax_r = fig.add_subplot(122, polar=True)
ax_r.plot(angles, mastery, 'b-o', linewidth=2)
ax_r.fill(angles, mastery, alpha=0.2, color='blue')
ax_r.set_xticks(angles[:-1])
ax_r.set_xticklabels(categories, fontsize=11)
ax_r.set_title('🎯 知识掌握度自评', fontsize=14, pad=20)
ax_r.set_ylim(0, 100)

plt.tight_layout()
plt.show()
```

---

## 五、业务关联

### 5.1 LangChat、Agent 与企业 AI 的落地关系

| 能力层 | 在企业产品中的价值 | 典型例子 |
|------|----------------|---------|
| Transformer + Tokenizer | 让系统正确理解用户表达 | 识别“今天有无糖的吗”中的核心意图 |
| KV Cache + 量化 | 让服务响应快、成本可控 | LangChat 高并发客服会话 |
| SFT | 让回答遵循企业话术与格式 | 菜单咨询、售后流程、工单总结 |
| DPO / RLHF | 让回答更安全、友好、符合品牌调性 | 遇到投诉时先致歉再给解决方案 |
| RAG（下周） | 让模型查询最新业务知识 | 实时库存、最新活动、内部制度 |

对 LangChat 而言，W3 的训练技术决定“模型怎么说”；对 Agent 而言，SFT 和偏好对齐决定“任务怎么做才稳妥”；对企业 AI 而言，模型、知识库、工具调用和监控必须组合起来，才是可长期运营的服务。

### 5.2 脑科学与 AI 的交叉视角

| AI 技术 | 脑科学对应 | 启示 |
|---------|----------|------|
| 自注意力 | 大脑"选择性注意"机制 | 并行处理多信息源 |
| 残差连接 | 神经回路中的跳跃连接 | 深层结构需要信息捷径 |
| 预训练 | 儿童早期语言习得 | 大量暴露→自然习得 |
| SFT | 学校教育 | 结构化、目标导向的学习 |
| RLHF | 社会化过程 | 通过反馈学习"得体"行为 |
| 过拟合 | "死记硬背" | 理解原理 > 记住答案 |

### 5.3 学习方法论

```
🔥 高效学习的三个层级：

Level 1: 看懂（输入）
  → 读书、看视频、做笔记
  → 本周你已经完成了这一步 ✅

Level 2: 能做（输出）  
  → 写代码、跑实验、调试问题
  → Day6 实战课走出了这一步 ✅

Level 3: 能教（融会贯通）
  → 给别人讲解、写技术博客、做项目
  → 这是接下来要追求的目标 🚀

💡 费曼学习法：
  如果你能用最简单的话向一个新手解释清楚，
  说明你真正理解了。
```

---

## 六、常见误区

### 6.1 “懂 Transformer 就等于能训练大模型”

不等于。架构只是基础；数据质量、训练目标、对齐方法、评估和部署同样决定最终效果。就像理解发动机不等于能造一辆可安全上路的车。

### 6.2 “SFT、RLHF、DPO 都是在给模型补知识”

不准确。预训练主要学习广泛知识和语言规律；SFT 改变指令遵循方式；RLHF/DPO 优化回答偏好。企业最新知识更适合用 RAG，而不是反复微调。

### 6.3 “模型越大就一定越适合企业”

不一定。客服 FAQ、分类和格式化场景中，小模型加 SFT/RAG 往往更快、更便宜也更容易管控。模型选型应同时看任务难度、延迟、隐私和预算。

### 6.4 “只看训练 Loss 就能判断模型可上线”

不行。Loss 只说明模型对训练目标的拟合情况。上线前还要测事实准确性、拒答安全性、边界问题、响应时间和用户满意度。

### 6.5 下周预告

### 第四周：RAG 与知识增强

```
🎯 核心问题：如何让大模型"知道"企业内部的数据？

📚 你将学到：
  Day1: RAG 基本流程与架构
  Day2: 向量检索与 Embedding 技术
  Day3: 高级 RAG 优化策略
  Day4: GraphRAG 与知识图谱
  Day5: RAG 实战架构
  Day6: 本地搭建 RAG 系统
  Day7: 第四周复习

🔗 关键概念预习：
  • 什么是向量数据库？
  • 什么是相似度搜索？
  • Embedding 是什么？

💡 建议：
  本周学完训练全景，下周进入"知识增强"，
  就能理解完整的"训练+应用"大模型工程师技能树了！
```

---

## 📝 总复习答案

### 选择题答案
| 题号 | 答案 | 解析 |
|------|------|------|
| 1 | B | 自注意力捕捉序列中不同位置之间的依赖关系 |
| 2 | B | RoPE 优势是相对位置信息，适合变长序列 |
| 3 | B | KV Cache 缓存K-V对，避免重复计算 |
| 4 | B | 涌现是规模超过临界点后突然出现的能力 |
| 5 | B | SFT用指令数据，预训练用纯文本 |
| 6 | B | 奖励模型判断回答好坏，提供训练信号 |
| 7 | B | DPO不需要奖励模型和PPO，大大简化 |
| 8 | B | 微调学习率 1e-5~5e-5 |

### 判断题答案
| 题号 | 答案 | 解析 |
|------|------|------|
| 9 | ❌ | 涌现需要规模，不是训练轮数能解决的 |
| 10 | ✅ | LoRA 确实只训练~0.3%参数 |
| 11 | ❌ | DPO需要冻结的参考模型 |
| 12 | ❌ | INT4在复杂任务上有精度损失 |
| 13 | ❌ | 早停法监控验证集Loss |

---

## 🔑 第三周核心术语汇总

| 英文 | 音标 | 中文 | 出处 |
|------|------|------|------|
| Pre-training | /ˈpriːˌtreɪnɪŋ/ | 预训练 | Day1 |
| Scaling Law | /ˈskeɪlɪŋ lɔː/ | 规模定律 | Day1 |
| Emergent Ability | /ɪˈmɜːrdʒənt/ | 涌现能力 | Day1 |
| SFT | /ɛs ɛf tiː/ | 监督微调 | Day2 |
| LoRA | /ˈloʊrə/ | 低秩适配 | Day2 |
| RLHF | /ɑːr ɛl eɪtʃ æf/ | 人类反馈强化学习 | Day3 |
| Reward Model | /rɪˈwɔːrd ˈmɒdl/ | 奖励模型 | Day3 |
| PPO | /piː piː oʊ/ | 近端策略优化 | Day3 |
| DPO | /diː piː oʊ/ | 直接偏好优化 | Day4 |
| KTO | /keɪ tiː oʊ/ | 前景理论优化 | Day4 |
| GRPO | /dʒiː ɑːr piː oʊ/ | 群体相对策略优化 | Day4 |
| KL Divergence | /keɪ ɛl daɪˈvɜːrdʒəns/ | KL散度 | Day3 |
| Overfitting | /ˌoʊvərˈfɪtɪŋ/ | 过拟合 | Day5 |
| Early Stopping | /ˈɜːrli ˈstɒpɪŋ/ | 早停法 | Day5 |
| QLoRA | /kjuː ˈloʊrə/ | 量化低秩适配 | Day6 |

---

## 📎 参考资源

### 三周必读论文 Top 5
1. 📄 **Attention Is All You Need** (Transformer 原文, 2017)
2. 📄 **GPT-3: Language Models are Few-Shot Learners** (2020)
3. 📄 **LoRA: Low-Rank Adaptation** (2021)
4. 📄 **Training language models to follow instructions** (InstructGPT, 2022)
5. 📄 **DPO: Direct Preference Optimization** (2023)

### 综合学习资源
1. 📺 **3Blue1Brown: 神经网络系列**（可视化理解）
2. 📺 **李宏毅大模型课程**（系统讲解）
3. 📖 **HuggingFace 官方教程**（实战代码）
4. 📖 **The Illustrated Transformer**（图解Transformer经典）

### 学习统计
```
📊 三周学习统计：
  • 完成天数: 21天
  • 核心知识点: 14个
  • 代码练习: 6次
  • 总测试题: 35道
  • 学习进度: 3/12 周 (25%)

进度条: [██████░░░░░░░░░░░░░░] 25%
```

---

> 🎉 **恭喜完成第三周！** 你已经理解了大模型训练的完整链路——从预训练到SFT，从RLHF到DPO，从理论到实战。下周我们进入 RAG 的世界，学习如何让大模型"拥有"企业知识库！🚀
