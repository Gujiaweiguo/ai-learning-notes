# 第4周 Day7：第四周总复习

> **导语**：过去六天我们走过了 RAG 的完整旅程——从基本概念到向量检索、从混合检索到 GraphRAG、从架构设计到动手实战。今天是"收网日"，不学新技术，而是把 W3（大模型训练）和 W4（RAG与知识增强）的知识串联成一张清晰的网络。学完不是结束，能"连起来"才是真正的掌握。

---

## 📊 学习进度

```
██████████████████████  Day 7/7  第四周总复习 ✅
```

| 维度 | 今日目标 |
|------|---------|
| 梳理 | W4 全部知识点的结构化回顾 |
| 连接 | W3 训练 ↔ W4 RAG 的技术关联 |
| 自测 | 20 道综合测试题检验掌握程度 |
| 展望 | 从已有知识通向下一步的路径规划 |

---

## 📚 W4 知识全景图

```
              RAG 与知识增强（第四周）
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    Day 1-2         Day 3-4        Day 5-6
    基础理论         进阶技术        实战落地
        │              │              │
   ┌────┴────┐    ┌───┴───┐     ┌───┴───┐
   │         │    │       │     │       │
 RAG架构  向量检索 混合检索 GraphRAG 架构优化 完整系统
 四步流程  Embedding 重排序  知识图谱 分块策略  ChromaDB
 文档切割  相似度   查询改写 实体关系 上下文优化 评估测试
```

### Day 1：RAG 基本流程与架构

**核心三句话**：
1. RAG = 先检索后生成，让大模型"翻参考书"再回答
2. 四步流程：文档切割 → 向量化 → 检索 → 增强生成
3. 核心价值：知识实时更新、减少幻觉、支持私有数据

**必记概念**：Chunking、Embedding、Vector Database、Top-K 检索

### Day 2：向量检索与相似度计算

**核心三句话**：
1. Embedding 把文字变成数学向量，语义相近的文本在向量空间中距离更近
2. 三种相似度：余弦相似度（方向）、欧氏距离（直线距离）、点积（综合匹配）
3. 文本检索首选余弦相似度——对文本长度不敏感

**必记公式**：cos(θ) = A·B / (|A| × |B|)

### Day 3：高级 RAG——混合检索与重排序

**核心三句话**：
1. 混合检索 = BM25 关键词检索 + 向量语义检索，用 RRF 融合两路结果
2. 重排序 = Cross-Encoder 对初筛结果精排，精度提升 10-20%
3. 查询改写 = HyDE（假设文档）和 Multi-Query（多角度扩展）

**必记公式**：RRF score = Σ 1/(k + rank)

### Day 4：GraphRAG 与知识图谱增强

**核心三句话**：
1. 知识图谱 = 实体（节点）+ 关系（边）+ 属性
2. GraphRAG 通过图遍历做多跳推理，弥补传统 RAG 的关系推理短板
3. 不是替代而是补充——传统 RAG + GraphRAG 协同效果最佳

**必记三元组**：(头实体, 关系, 尾实体)

### Day 5：RAG 实战架构设计与优化

**核心三句话**：
1. 生产级 RAG 有 7 个阶段：预处理→改写→多路检索→融合→重排→上下文优化→生成
2. 最关键的优化：语义分块（地基）+ Prompt 约束（成本最低效果最好）
3. "Lost in the Middle"效应——LLM 对中间位置信息容易忽略

**必记指标**：召回率 > 0.9、精确率 > 0.8、去重率 > 0.7

### Day 6：RAG 系统实战

**核心三句话**：
1. 完整管道：文档→分块→向量化→ChromaDB→检索→Prompt→LLM
2. 评估方法：构建测试集，计算 Recall@K
3. 从 Demo 到生产需要全面升级：存储持久化、Embedding 升级、混合检索、监控告警

**必记工具**：Sentence-Transformers、ChromaDB、cross-encoder

---

## 🔗 W3 ↔ W4 知识串联

这两周的知识不是割裂的，它们像拼图一样严丝合缝：

### 技术关联图

```
W3：大模型训练                          W4：RAG与知识增强
┌────────────────┐                  ┌────────────────┐
│ Transformer架构 │──── 注意力机制 ──→│ 向量Embedding   │
│ (自注意力机制)  │    (语义表示基础)  │ (文本变向量)    │
└────────────────┘                  └────────────────┘
┌────────────────┐                  ┌────────────────┐
│ 预训练+SFT     │──── 模型能力 ────→│ RAG生成模块     │
│ (让模型会说话)  │    (语言理解生成)  │ (基于检索回答)  │
└────────────────┘                  └────────────────┘
┌────────────────┐                  ┌────────────────┐
│ RLHF/DPO       │──── 对齐优化 ────→│ Prompt约束     │
│ (让模型守规矩)  │    (规则遵循)     │ (让模型不幻觉)  │
└────────────────┘                  └────────────────┘
```

### 四个关键连接点

#### 1. 注意力机制 ↔ 检索系统

| 注意力机制 | RAG 检索 |
|-----------|---------|
| Q (Query)：当前位置"问"其他位置 | 用户查询向量 |
| K (Key)：被"问"位置的标签 | 文档向量 |
| V (Value)：被"问"位置的内容 | 文档内容 |
| Attention Weight：Q·K 相似度 | 余弦相似度 |
| Softmax：归一化注意力权重 | Top-K 筛选 |

> 💡 **洞察**：Transformer 的自注意力本身就是一种"内部检索"——在自身上下文中找相关信息。RAG 则是"外部检索"——在知识库中找相关信息。两者的数学本质惊人地相似！

#### 2. 模型训练 ↔ 检索优化

| 训练阶段 | RAG 对应 |
|---------|---------|
| 数据清洗影响训练效果 | 文档质量影响检索效果 |
| 超参数调优 (lr, batch_size) | RAG 参数调优 (chunk_size, top_k) |
| Loss 下降 = 模型在学 | 召回率上升 = 检索在改善 |
| 过拟合 = 死记硬背 | 知识库过时 = 回答过时 |

#### 3. RLHF 对齐 ↔ RAG 幻觉控制

- RLHF：用人类偏好数据训练模型"应该怎么回答"（行为约束）
- RAG：用真实文档约束模型"只能基于什么回答"（信息约束）
- **两者是互补的**：RLHF 管"态度"，RAG 管"事实"，共同减少幻觉

#### 4. 预训练知识 ↔ 外部知识

| 维度 | 预训练知识（参数中） | RAG 外部知识（数据库中） |
|------|-------------------|----------------------|
| 更新方式 | 重新训练/微调 | 更新文档即可 |
| 存储成本 | 高（模型参数） | 低（文档存储） |
| 检索精度 | 模糊（参数中的隐式表示） | 精确（原文级匹配） |
| 可追溯性 | 无法追溯 | 可标注引用来源 |
| 容量上限 | 受模型大小限制 | 理论上无限 |

---

## 📊 可视化：不同检索方法效果对比

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

methods = ['传统关键词', '向量检索', '混合检索', 'GraphRAG']
accuracies = [65, 78, 85, 82]
latencies = [120, 350, 420, 580]  # ms

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 准确率
colors = ['#a8e6cf', '#dcedc1', '#ffd3b6', '#ffaaa5']
bars1 = ax1.bar(methods, accuracies, color=colors)
ax1.set_ylabel('检索准确率 (%)')
ax1.set_title('不同RAG方法准确率对比', fontsize=13, fontweight='bold')
ax1.set_ylim(0, 100)
for bar, acc in zip(bars1, accuracies):
    ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
             f'{acc}%', ha='center', fontsize=12)

# 延迟
bars2 = ax2.bar(methods, latencies, color=colors)
ax2.set_ylabel('响应延迟 (ms)')
ax2.set_title('不同RAG方法响应延迟对比', fontsize=13, fontweight='bold')
ax2.set_ylim(0, 700)
for bar, lat in zip(bars2, latencies):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 10,
             f'{lat}ms', ha='center', fontsize=12)

plt.tight_layout()
plt.savefig('day7_method_comparison.png', dpi=150)
plt.show()
```

**观察要点**：
- 准确率和延迟往往是矛盾的——越准的方法通常越慢
- 混合检索是"甜点位"——准确率高达 85%，延迟只有 420ms
- GraphRAG 准确率略低于混合检索（它擅长的是关系推理而非通用检索）

---

## 📊 可视化：预训练损失曲线回顾

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

# 模拟完整的训练管道损失曲线
epochs = 50
pretrain_loss = 3.5 * np.exp(-np.linspace(0, 2.5, epochs)) + 0.5 + np.random.normal(0, 0.03, epochs)
sft_loss = 2.0 * np.exp(-np.linspace(0, 2, epochs//2)) + 0.8 + np.random.normal(0, 0.04, epochs//2)
rlhf_reward = np.linspace(0.2, 1.8, epochs//2) + np.random.normal(0, 0.05, epochs//2)

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# 预训练损失
axes[0].plot(range(1, epochs+1), pretrain_loss, 'b-', linewidth=2)
axes[0].set_xlabel('训练步数')
axes[0].set_ylabel('损失值')
axes[0].set_title('预训练 Loss', fontweight='bold')
axes[0].grid(True, alpha=0.3)

# SFT 损失
axes[1].plot(range(1, epochs//2+1), sft_loss, 'r-', linewidth=2)
axes[1].set_xlabel('训练步数')
axes[1].set_ylabel('损失值')
axes[1].set_title('SFT 指令微调 Loss', fontweight='bold')
axes[1].grid(True, alpha=0.3)

# RLHF 奖励
axes[2].plot(range(1, epochs//2+1), rlhf_reward, 'g-', linewidth=2)
axes[2].set_xlabel('训练步数')
axes[2].set_ylabel('奖励值')
axes[2].set_title('RLHF 奖励上升', fontweight='bold')
axes[2].grid(True, alpha=0.3)

plt.suptitle('大模型训练三阶段（W3 回顾）', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('day7_training_curves.png', dpi=150)
plt.show()
```

---

## ✅ 综合复习测试（20 题）

### 概念填空（1-5 题）

1. RAG 的四个步骤按顺序是 ______ → ______ → ______ → ______。

2. 余弦相似度的数学公式是 ______，取值范围是 ______。

3. GraphRAG 中知识图谱的三要素是 ______、______、______。

4. 混合检索融合两路结果常用的算法缩写是 ______。

5. Cross-Encoder 比 Bi-Encoder 精度高的原因是 ______。

### 选择题（6-10 题）

6. 以下哪个不是文档切割策略？（  ）
   A. 固定大小切割  B. 语义边界切割  C. 随机切割  D. 滑动窗口切割

7. "Lost in the Middle"问题指的是 LLM 对什么位置的信息容易忽略？（  ）
   A. 开头  B. 中间  C. 结尾  D. 所有位置

8. RLHF 训练流程的正确顺序是？（  ）
   A. PPO → 奖励模型 → SFT
   B. SFT → 奖励模型 → PPO
   C. 奖励模型 → SFT → PPO
   D. SFT → PPO → 奖励模型

9. 以下哪种情况最适合用 GraphRAG？（  ）
   A. 查询产品价格
   B. 查询"椰子和奶茶有什么关系"
   C. 查询最新促销活动
   D. 查询店铺地址

10. HyDE 的核心思路是？（  ）
    A. 生成多个查询变体
    B. 用假设的理想答案做检索
    C. 用知识图谱增强检索
    D. 用关键词精确匹配

### 判断题（11-15 题）

11. RAG 系统中，chunk_size 越大越好。（  ）

12. GraphRAG 可以完全替代传统 RAG。（  ）

13. DPO 不需要训练奖励模型。（  ）

14. ChromaDB 内存模式下重启程序数据不丢失。（  ）

15. 欧氏距离越小表示两个向量越相似。（  ）

### 简答题（16-20 题）

16. 用你自己的话解释 RAG 为什么能减少大模型的幻觉问题。

17. 对比 SFT（监督微调）和 RAG 在知识注入上的不同。

18. 如果要为糖水店设计一个智能问答系统，你会选择什么技术方案？简述架构。

19. 为什么说"注意力机制本质上是一种内部检索"？

20. 从 W1 到 W4，你学到的最重要的一个概念是什么？为什么？

---

## 📖 核心术语总表

| 英文 | 音标 | 中文 | 所属模块 |
|------|------|------|---------|
| Transformer | /trænsˈfɔːrmər/ | 变换器 | W1-W2 |
| Self-Attention | /sɛlf əˈtɛnʃən/ | 自注意力 | W1-W2 |
| Pre-training | /priː ˈtreɪnɪŋ/ | 预训练 | W3 |
| SFT (Supervised Fine-Tuning) | /ˈsuːpərvaɪzd faɪn ˈtjuːnɪŋ/ | 监督微调 | W3 |
| RLHF | /ɑːr ɛl eɪtʃ ɛf/ | 基于人类反馈的强化学习 | W3 |
| DPO | /diː piː oʊ/ | 直接偏好优化 | W3 |
| RAG | /ræɡ/ | 检索增强生成 | W4 |
| Embedding | /ɛmˈbɛdɪŋ/ | 向量嵌入 | W4 |
| Cosine Similarity | /ˈkoʊsaɪn ˌsɪmɪˈlærɪti/ | 余弦相似度 | W4 |
| BM25 | /biː ɛm twɛnti-faɪv/ | BM25算法 | W4 |
| RRF | /ɑːr ɑːr ɛf/ | 倒数排名融合 | W4 |
| Cross-Encoder | /krɒs ˈɛnkəʊdər/ | 交叉编码器 | W4 |
| HyDE | /haɪd iː/ | 假设文档嵌入 | W4 |
| Knowledge Graph | /ˈnɒlɪdʒ ɡrɑːf/ | 知识图谱 | W4 |
| GraphRAG | /ɡrɑːf ræɡ/ | 图谱增强检索 | W4 |
| Chunking | /ˈtʃʌŋkɪŋ/ | 文档分块 | W4 |
| ChromaDB | /kroʊmə diːbiː/ | 向量数据库 | W4 |
| Hallucination | /həˌluːsɪˈneɪʃən/ | 幻觉 | W3-W4 |
| Recall@K | /rɪˈkɔːl æt keɪ/ | K位召回率 | W4 |
| Prompt Engineering | /prɒmpt ˌɛndʒɪˈnɪərɪŋ/ | 提示词工程 | W3-W4 |

---

## 🔮 从 W4 到未来

学完 W4，你已经掌握了 RAG 的完整知识体系。以下是继续深入的方向：

| 方向 | 具体内容 | 推荐资源 |
|------|---------|---------|
| RAG 评估 | RAGAS 框架、自动评估指标 | docs.ragas.io |
| 多模态 RAG | 图文混合检索、视频理解 | CLIP、LLaVA |
| Agentic RAG | Agent 自主决定何时检索、检索什么 | LangGraph |
| 自适应 RAG | 根据问题难度动态调整检索策略 | Self-RAG 论文 |
| RAG 工程化 | 大规模部署、缓存、负载均衡 | vLLM + Milvus |

### 最值得做的三个项目

1. **个人知识库助手**：把你的笔记/文档做成 RAG 知识库，用 Qwen 本地部署
2. **客服问答 Bot**：为你的业务搭建多路检索 + 重排序的客服系统
3. **论文阅读助手**：上传论文 PDF，用 RAG 辅助阅读和提问

---

## 🔗 全周参考资源汇总

- 📚 [LangChain 官方文档](https://python.langchain.com/)
- 📚 [LlamaIndex 官方文档](https://docs.llamaindex.ai/)
- 📦 [Sentence-Transformers](https://www.sbert.net/)
- 📦 [ChromaDB](https://docs.trychroma.com/)
- 📄 [RAG 原始论文](https://arxiv.org/abs/2005.11401)
- 📄 [GraphRAG 论文](https://arxiv.org/abs/2404.16130)
- 📄 [HyDE 论文](https://arxiv.org/abs/2212.10496)
- 📄 [Lost in the Middle](https://arxiv.org/abs/2307.03172)
- 🎥 [Andrej Karpathy: State of GPT](https://www.youtube.com/watch?v=bZQun8Y4L2A)
- 🎥 [LangChain RAG From Scratch](https://www.youtube.com/watch?v=wd7TZ5wbKxI)

---

> 🎉 **恭喜完成第四周！** 你已经从 RAG 新手成长为能独立搭建和优化 RAG 系统的工程师。下一步，把这些知识用到一个真实项目中——"纸上得来终觉浅，绝知此事要躬行"。
