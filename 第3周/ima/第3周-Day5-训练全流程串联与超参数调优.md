# 📚 第三周-Day5：训练全流程串联与超参数调优

> **一块石头从原石到宝石，要经过开采、切割、打磨、抛光、镶嵌五道工序。一个大模型从数据到上线，要经过七步。少一步，宝石就不亮；少一步，模型就不好用。今天我们把整条流水线串起来，加上超参数调优的"打磨"技巧。**

## 📅 学习进度

| 阶段 | 状态 |
|------|------|
| W1：Transformer 基础架构 | ✅ 已完成 |
| W2：Transformer 深入理解 | ✅ 已完成 |
| **W3：大模型训练全景** | 🔄 **进行中（Day 5/7）** |
| W4-W12 | ⏳ 待开始 |

---

## 一、为什么需要全流程视角？

### 1.1 从"单点学习"到"系统工程"

前四天我们分别学了预训练、SFT、RLHF、DPO。但真实的工业级训练不是一个个孤立环节——它是一条精密的流水线，每一步的输出是下一步的输入。

**生活类比：做饭**

```
🍽️ 做一顿年夜饭：

📦 食材采购 → 🔪 洗切准备 → 🔥 烹饪加工 → 🧂 调味 → 🍽️ 摆盘 → 😋 品尝 → 🏪 上桌

每一步都不可跳过：
  没洗的菜直接下锅 → 吃坏肚子（数据没清洗）
  火候不对 → 糊了或没熟（超参数没调好）
  没调味 → 不好吃（没有对齐训练）
  没摆盘 → 不好看（没有UI/部署优化）
```

### 1.2 工业级大模型训练 7 步走

```
📥 数据收集 → 🧹 数据清洗 → 🎯 预训练 → ✂️ SFT微调 → 🤝 对齐训练 → 📊 评估测试 → 🚀 部署上线
   Step1       Step2       Step3      Step4       Step5       Step6       Step7
```

| 步骤 | 输入 | 输出 | 关键指标 |
|------|------|------|---------|
| 数据收集 | 互联网、书籍、论文 | 原始文本库 | 数据量(TB) |
| 数据清洗 | 原始文本 | 高质量语料 | 质量、多样性 |
| 预训练 | 高质量语料 | 基础模型 | Loss、PPL |
| SFT | 指令数据 | 对话模型 | 指令遵循率 |
| 对齐 | 偏好数据 | 对齐模型 | 人类满意度 |
| 评估 | 测试集 | 评估报告 | 准确率、安全分 |
| 部署 | 对齐模型 | API服务 | 延迟、吞吐 |

---

## 二、核心原理详解

### 2.1 超参数：训练的"旋钮"

超参数是训练前手动设定的配置，**不参与梯度更新**，但决定了训练的效果。

**最核心的 5 个超参数：**

#### 🎯 学习率 (Learning Rate)
```
最重要！没有之一！

太大(>1e-3) → Loss震荡甚至NaN爆炸 💥
太小(<1e-6) → 训练太慢，一周跑不完 🐢
刚好(1e-5~5e-5) → 稳步下降 😊

口诀：宁可小一点稳稳的，不要贪大翻车
```

#### 📦 批次大小 (Batch Size)
```
太大(>128) → 显存爆 + 泛化变差
太小(<4)  → 梯度方向噪声大 + 训练不稳定
刚好(8~32) → 稳定 + 效果好

💡 黄金法则：Batch Size 加倍 → 学习率可线性增大
```

#### 🔄 训练轮数 (Epochs)
```
SFT: 通常 3-5 个 epoch
DPO: 通常 1-3 个 epoch
预训练: 不用 epoch，用 steps（百万级）

太多 → 过拟合（背答案）
太少 → 欠拟合（没学会）
```

#### 🌡️ 预热步数 (Warmup Steps)
```
训练初期学习率从0线性增长到目标值
通常 = 总步数的 3-10%

为什么需要warmup？
  初期模型参数还很"生"，大学习率会"毁掉"预训练权重
  慢慢加速，等模型适应了再全速前进
```

#### ⏰ 学习率调度 (LR Schedule)
```
Cosine Decay（最常用）：
  先warmup上去 → 再cosine曲线缓慢下降

为什么？
  前期需要大胆探索（学习率大）
  后期需要精细调整（学习率小）
  就像画画：先大笔触，再细描
```

### 2.2 调优策略：从暴力到智能

| 策略 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **网格搜索** | 穷举所有组合 | 不遗漏 | 组合爆炸 |
| **随机搜索** | 随机采样 | 高效 | 可能错过最优 |
| **贝叶斯优化** | 用历史结果预测 | 最省实验次数 | 实现复杂 |
| **人工经验** | 凭经验设值 | 最快 | 主观性强 |

**网格搜索的问题**：5个参数各试5个值 = 5^5 = 3125 次实验！每次跑12小时 = 4.3年 😱

**贝叶斯优化**：通常20-50次就能找到不错参数。工具：Optuna、Ray Tune、W&B Sweeps。

### 2.3 过拟合与早停法

**过拟合 = 模型"背答案"而不是"学方法"**

| 状态 | 训练集 Loss | 验证集 Loss | 比喻 |
|------|-----------|-----------|------|
| 欠拟合 | 高 | 高 | 考前没复习，啥也不会 |
| 刚好 | 低 | 低 | 复习到位，考试发挥正常 |
| 过拟合 | 很低 | 开始上升 | 把历年真题背了，题型一变就懵 |

**早停法 (Early Stopping)**：

```python
# 伪代码
patience = 3  # 容忍多少个epoch不改善
best_val_loss = float('inf')
wait = 0

for epoch in range(max_epochs):
    train_loss = train_one_epoch()
    val_loss = evaluate()
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        wait = 0
        save_best_model()
    else:
        wait += 1
        if wait >= patience:
            print(f"Early stopping at epoch {epoch}")
            break
```

### 2.4 生产环境部署考量

**模型大小选择：**

| 场景 | 推荐模型 | 显存(FP16) | 显存(INT4) |
|------|---------|-----------|-----------|
| 手机端 | 0.5-3B | 1-6GB | 0.4-2GB |
| 单卡(4060Ti) | 7-14B | 14-28GB | 4-8GB |
| 多卡服务器 | 32-72B | 64-144GB | 18-40GB |
| API服务 | 70B+ | 多卡并行 | - |

**推理加速技术：**
- **KV Cache**：缓存注意力的Key-Value，避免重复计算
- **Flash Attention**：减少内存访问，IO优化
- **量化**：FP16→INT8 速度翻倍，INT4 再快但有损
- **投机解码**：小模型先生成草稿，大模型快速验证

---

## 三、代码实战

### 3.1 学习率调度可视化

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

total_steps = 200
base_lr = 2e-5
warmup_steps = 20

# 1. 固定学习率
lr_constant = np.ones(total_steps) * base_lr

# 2. Warmup + Cosine Decay
lr_cosine = np.zeros(total_steps)
for i in range(total_steps):
    if i < warmup_steps:
        lr_cosine[i] = base_lr * (i + 1) / warmup_steps
    else:
        progress = (i - warmup_steps) / (total_steps - warmup_steps)
        lr_cosine[i] = base_lr * 0.5 * (1 + np.cos(np.pi * progress))

# 3. Warmup + Linear Decay
lr_linear = np.zeros(total_steps)
for i in range(total_steps):
    if i < warmup_steps:
        lr_linear[i] = base_lr * (i + 1) / warmup_steps
    else:
        progress = (i - warmup_steps) / (total_steps - warmup_steps)
        lr_linear[i] = base_lr * (1 - progress)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(range(total_steps), lr_constant, 'b-', linewidth=2, label='固定学习率')
ax.plot(range(total_steps), lr_cosine, 'r-', linewidth=2, label='Warmup + Cosine Decay')
ax.plot(range(total_steps), lr_linear, 'g-', linewidth=2, label='Warmup + Linear Decay')
ax.axvline(x=warmup_steps, color='gray', linestyle='--', alpha=0.5, label=f'Warmup结束(step={warmup_steps})')
ax.set_xlabel('训练步数', fontsize=13)
ax.set_ylabel('学习率', fontsize=13)
ax.set_title('学习率调度策略对比', fontsize=15)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
print("✅ Cosine Decay 是大模型微调的标配！")
```

### 3.2 过拟合检测模拟

```python
np.random.seed(42)
epochs = list(range(1, 81))

# 训练集Loss：持续下降
train_loss = [2.5 * np.exp(-e / 12) + 0.1 + 0.001 * e**1.5 * 0.01 for e in epochs]

# 验证集Loss：先降后升（过拟合）
val_loss = []
for e in epochs:
    if e <= 25:
        vl = 2.4 * np.exp(-e / 12) + 0.2
    else:
        vl = 2.4 * np.exp(-25 / 12) + 0.2 + 0.02 * (e - 25)**1.3 * 0.01
    vl += np.random.normal(0, 0.02)
    val_loss.append(max(0.1, vl))

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(epochs, train_loss, 'b-', linewidth=2, label='训练集 Loss')
ax.plot(epochs, val_loss, 'r-', linewidth=2, label='验证集 Loss')
ax.axvline(x=25, color='orange', linestyle='--', linewidth=2, label='最佳停止点 (Epoch 25)')
ax.axvspan(25, 80, alpha=0.1, color='red', label='过拟合区域')
ax.set_xlabel('Epoch', fontsize=13)
ax.set_ylabel('Loss', fontsize=13)
ax.set_title('过拟合检测：训练集在降，验证集开始升就该停！', fontsize=14)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### 3.3 不同学习率的影响

```python
np.random.seed(42)
epochs = 100

def simulate_training(lr, noise=0.05):
    losses = []
    loss = 3.0
    for i in range(epochs):
        gradient = 0.02 + 0.01 * np.sin(i / 10) + noise * np.random.randn()
        step = lr * gradient
        if lr > 0.1:
            step += 0.3 * np.sin(i * lr)
            if loss < 0.5 and lr > 0.15:
                step += np.random.normal(0, 0.5)
        loss -= step
        loss = max(0.01, loss)
        losses.append(loss)
    return losses

fig, ax = plt.subplots(figsize=(12, 6))

lrs = [(0.001, '太小（学不动）', 'gray'),
       (0.01, '适中（最佳）', 'green'),
       (0.05, '偏大（有震荡）', 'orange'),
       (0.2, '太大（爆炸）', 'red')]

for lr, label, color in lrs:
    losses = simulate_training(lr)
    ax.plot(range(epochs), losses, '-', color=color, linewidth=2,
            label=f'LR={lr} ({label})')

ax.set_xlabel('Epoch', fontsize=13)
ax.set_ylabel('Loss', fontsize=13)
ax.set_title('学习率对训练的影响：不贪大，不怯步', fontsize=15)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### 3.4 完整训练流程模拟

```python
# 模拟三阶段训练全流程
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 预训练
pretrain_epochs = range(200)
pretrain_loss = [4.0 * np.exp(-i/40) + 0.8 + 0.02 * np.random.randn() for i in pretrain_epochs]
axes[0].plot(pretrain_epochs, pretrain_loss, 'b-', linewidth=1.5, alpha=0.8)
axes[0].set_title('Step 3: 预训练 (200 epochs)', fontsize=13)
axes[0].set_ylabel('Loss')
axes[0].set_xlabel('Steps (×1000)')
axes[0].grid(True, alpha=0.3)

# SFT
sft_epochs = range(15)
sft_train = [2.5 * np.exp(-i/4) + 0.5 + 0.01 * np.random.randn() for i in sft_epochs]
sft_val = [2.3 * np.exp(-i/4) + 0.6 + 0.03 * np.random.randn() for i in sft_epochs]
axes[1].plot(sft_epochs, sft_train, 'b-o', linewidth=2, label='训练集')
axes[1].plot(sft_epochs, sft_val, 'r-s', linewidth=2, label='验证集')
axes[1].set_title('Step 4: SFT 微调 (15 epochs)', fontsize=13)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# DPO
dpo_epochs = range(5)
dpo_acc = [0.55, 0.68, 0.75, 0.79, 0.82]
axes[2].plot(dpo_epochs, dpo_acc, 'g-^', linewidth=2, markersize=10)
axes[2].set_title('Step 5: DPO 对齐 (5 epochs)', fontsize=13)
axes[2].set_ylabel('偏好准确率')
axes[2].set_xlabel('Epoch')
axes[2].set_ylim(0.5, 0.9)
axes[2].grid(True, alpha=0.3)

plt.suptitle('大模型三阶段训练全流程', fontsize=16)
plt.tight_layout()
plt.show()
print("✅ 预训练(大量步数) → SFT(少量epoch) → DPO(更少epoch) = 完整训练链路")
```

---

## 四、可视化理解

### 4.1 调优策略效率对比

```python
# 模拟三种调优策略的搜索过程
np.random.seed(42)

def objective(x, y):
    return (x - 0.3)**2 + (y - 0.7)**2 + 0.05 * np.sin(5*x) * np.cos(3*y)

xx, yy = np.meshgrid(np.linspace(0, 1, 100), np.linspace(0, 1, 100))
zz = objective(xx, yy)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 网格搜索
ax = axes[0]
ax.contourf(xx, yy, zz, levels=20, cmap='RdYlGn_r', alpha=0.6)
grid_x, grid_y = np.meshgrid(np.linspace(0.1, 0.9, 5), np.linspace(0.1, 0.9, 5))
ax.scatter(grid_x.ravel(), grid_y.ravel(), c='blue', s=30, zorder=5)
ax.set_title('网格搜索（25次实验）', fontsize=13)

# 随机搜索
ax = axes[1]
ax.contourf(xx, yy, zz, levels=20, cmap='RdYlGn_r', alpha=0.6)
rx, ry = np.random.rand(25), np.random.rand(25)
ax.scatter(rx, ry, c='blue', s=30, zorder=5)
ax.set_title('随机搜索（25次实验）', fontsize=13)

# 贝叶斯优化
ax = axes[2]
ax.contourf(xx, yy, zz, levels=20, cmap='RdYlGn_r', alpha=0.6)
opt_x = [0.5, 0.6, 0.4, 0.35, 0.3, 0.28, 0.31, 0.3, 0.3, 0.3]
opt_y = [0.5, 0.6, 0.65, 0.68, 0.72, 0.71, 0.69, 0.7, 0.7, 0.7]
ax.scatter(opt_x, opt_y, c=['blue']*3 + ['orange']*3 + ['red']*4, s=30, zorder=5)
ax.plot(opt_x, opt_y, 'k-', alpha=0.3)
ax.set_title('贝叶斯优化（10次就够了）', fontsize=13)

for ax in axes:
    ax.set_xlabel('参数1')
    ax.set_ylabel('参数2')

plt.suptitle('超参数搜索策略对比', fontsize=15)
plt.tight_layout()
plt.show()
```

### 4.2 生产环境模型选型图

```python
models = ['0.5B', '1.5B', '7B', '14B', '32B', '72B']
quality = [45, 62, 82, 89, 94, 97]
int4_mem = [0.4, 1, 4, 8, 18, 40]
speed = [180, 120, 55, 28, 12, 4]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 质量 vs 显存
ax = axes[0]
ax.bar(models, quality, color='skyblue', alpha=0.8, label='质量分数')
ax2 = ax.twinx()
ax2.plot(models, int4_mem, 'r-o', linewidth=2, label='INT4显存(GB)')
ax.set_ylabel('质量分数', fontsize=12)
ax2.set_ylabel('显存需求 (GB)', fontsize=12, color='red')
ax.set_title('模型大小 vs 质量 vs 显存', fontsize=14)
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

# 质量 vs 速度
ax = axes[1]
ax.bar(models, quality, color='lightgreen', alpha=0.8, label='质量分数')
ax2 = ax.twinx()
ax2.plot(models, speed, 'r-s', linewidth=2, label='推理速度(tok/s)')
ax.set_ylabel('质量分数', fontsize=12)
ax2.set_ylabel('推理速度 (tokens/sec)', fontsize=12, color='red')
ax.set_title('模型大小 vs 质量 vs 速度', fontsize=14)
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.show()
print("💡 选型核心权衡：质量、速度、成本——三者不可兼得！")
```

---

## 五、业务关联

### 5.1 糖水店 AI 助手全流程

```
Step 1: 📥 数据收集
  → 收集2年客服对话记录 + 菜单数据 + FAQ

Step 2: 🧹 数据清洗  
  → 去除无效对话、统一格式、标注指令-回答对

Step 3: 🎯 预训练（跳过——使用Qwen2-0.5B开源模型）

Step 4: ✂️ SFT 微调
  → 用500条精选指令数据做LoRA微调
  → 学习率2e-5，batch size=8，epoch=3

Step 5: 🤝 DPO 对齐（可选）
  → 收集客户反馈（好回答/差回答）
  → 用DPO优化回答质量

Step 6: 📊 评估测试
  → 用100道客服测试题验证准确率
  → 人工盲测对比微调前后

Step 7: 🚀 部署上线
  → QLoRA量化 + vLLM加速
  → 部署到LangChat系统
```

### 5.2 企业超参数调优清单

| 参数 | 预训练 | SFT | DPO |
|------|-------|-----|-----|
| 学习率 | 1e-4~3e-4 | 1e-5~5e-5 | 5e-7~5e-6 |
| Batch Size | 1024~4096 | 8~32 | 8~32 |
| Epochs | 不用epoch | 3~5 | 1~3 |
| Warmup | 2-5%总步数 | 3-10%总步数 | 固定100步 |
| LR Schedule | Cosine | Cosine | Linear |
| Weight Decay | 0.1 | 0.01~0.1 | 0.0~0.01 |
| Max Seq Len | 2048 | 2048 | 2048 |

---

## 六、常见误区

### ❌ 误区1："训练越久效果越好"
**事实**：训练太久会过拟合。早停法是必须的——监控验证集Loss，一旦开始上升就停止。

### ❌ 误区2："学习率越大学得越快"
**事实**：学习率太大会导致Loss爆炸（NaN），模型直接报废。微调时宁小勿大。

### ❌ 误区3："超参数可以用别人的默认值"
**事实**：不同模型、不同数据、不同任务的最优超参数不同。默认值只是起点，必须在自己的数据上调。

### ❌ 误区4："INT4 量化无损"
**事实**：INT4 量化在复杂任务（数学推理、代码生成）上有明显损失。对于简单对话还可以，精度要求高的场景建议用INT8或FP16。

### ❌ 误区5："7B 模型什么都能做"
**事实**：7B 模型在简单任务上表现不错，但复杂推理、多步规划、长文档理解等任务需要更大的模型。选模型要看任务难度。

---

## 🧪 课堂练习（5分钟）

**练习1**：你有以下训练日志，判断模型处于什么状态？
```
Epoch 1: Train Loss=2.1, Val Loss=2.3
Epoch 5: Train Loss=0.8, Val Loss=1.0
Epoch 10: Train Loss=0.3, Val Loss=0.9
Epoch 15: Train Loss=0.15, Val Loss=1.5
```

**练习2**：一张 4060Ti (16GB)，想跑 14B 模型推理，该怎么做？（提示：14B FP16需要多少GB？）

**练习3**：网格搜索5个参数各试5个值 = 多少次实验？为什么贝叶斯优化更高效？

---

## 📝 课后测试（15分钟）

**❶** 微调大模型时推荐的学习率是？
- A. 0.1~1.0
- B. 1e-5~5e-5
- C. 1e-10~1e-8
- D. 10~100

**❷** 早停法监控的指标是？
- A. 训练集Loss
- B. 验证集Loss
- C. 测试集Loss
- D. 训练准确率

**❸** 调优效率最高的策略是？
- A. 网格搜索
- B. 随机搜索
- C. 贝叶斯优化
- D. 全部手试

**❹** 7B 模型 INT4 量化大约需要多少显存？
- A. 0.5GB
- B. 4GB
- C. 14GB
- D. 28GB

**❺** 简答题：列出大模型从数据到部署的7步流程。

---

## 🔑 今日术语

| 英文 | 音标 | 中文 |
|------|------|------|
| Hyperparameter | /ˌhaɪpərˈpærəˌmɪtər/ | 超参数 |
| Learning Rate | /ˈlɜːrnɪŋ reɪt/ | 学习率 |
| Batch Size | /bætʃ saɪz/ | 批次大小 |
| Early Stopping | /ˈɜːrli ˈstɒpɪŋ/ | 早停法 |
| Overfitting | /ˌoʊvərˈfɪtɪŋ/ | 过拟合 |
| Cosine Decay | /ˈkoʊsaɪn dɪˈkeɪ/ | 余弦衰减 |
| Warmup | /ˈwɔːrmˌʌp/ | 预热 |
| Quantization | /ˌkwɒntɪˈzeɪʃən/ | 量化 |

---

## 📎 参考资源

### 工具推荐
1. 🔧 **Optuna** - 贝叶斯超参数优化框架
2. 🔧 **Weights & Biases** - 训练可视化 + Sweep 调参
3. 🔧 **HuggingFace Trainer** - 封装好的训练循环

### 视频推荐
1. 📺 **10分钟学会深度学习调参**（B站）
   - https://www.bilibili.com/video/BV1isCvBNEff/
2. 📺 **大模型微调超参数设置指南**（图文教程）
   - https://blog.csdn.net/l35633/article/details/147566394

### 明日预告
理论学完了，明天**代码实战**——用 HuggingFace TRL 对 Qwen2-0.5B 做完整的 SFT 微调，走通数据→训练→评估的全流程！⚡
