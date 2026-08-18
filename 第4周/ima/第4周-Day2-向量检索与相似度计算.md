# 第4周 Day2：向量检索与相似度计算

> **导语**：你有没有想过，为什么在淘宝搜索"红色连衣裙"，系统不会只找标题里带"红色连衣裙"的商品，而是还能推荐"玫红长裙"、"酒红礼裙"？背后的魔法就是**向量检索**——把文字变成数学向量，在几何空间里找到"意思最近"的内容。今天我们从 Embedding 原理到相似度计算，完整拆解 RAG 的"检索引擎"。

---

## 📊 学习进度

```
████████████░░░░░░░░  Day 2/7  向量检索与相似度计算
```

| 维度 | 今日目标 |
|------|---------|
| 概念 | 理解 Embedding 的本质——文本到向量的"语义翻译" |
| 数学 | 掌握余弦相似度、欧氏距离、点积三种度量 |
| 实战 | 用 Sentence-Transformers 编码真实中文文本 |
| 选型 | 了解不同 Embedding 模型的特点和选择策略 |

---

## 🤔 为什么需要 Embedding？

### 从"字面匹配"到"语义理解"

传统关键词搜索的逻辑很直接：文档里出现了搜索词就匹配。但这有致命问题：

| 用户搜索 | 关键词搜索的问题 |
|---------|----------------|
| "不辣的糖水" | 文档写的是"清甜降火"，匹配不上 |
| "便宜的手机" | 文档写的是"高性价比千元机"，匹配不上 |
| "减肥能喝的甜品" | 文档写的是"低卡路里健康甜品"，匹配不上 |

**根本原因**：同一个意思可以有很多种表达方式。人类能理解"清甜降火"和"不辣"的关系，但计算机怎么理解？

### Embedding 的灵感来源

Embedding 的灵感来自一个语言学的古老假说：**"上下文相似的词，语义也相似"**。

- 如果"苹果"经常和"吃"、"甜"、"水果"出现在一起
- 如果"橘子"也经常和"吃"、"甜"、"水果"出现在一起
- 那么计算机推断：苹果和橘子在语义上是"近亲"

Embedding 模型通过阅读海量文本，学会了把每段文字映射到一个高维空间中的点。语义越接近，空间中的点距离越近。

> 🎯 **生活类比**：想象一个巨大的超市。商品不是随机摆放，而是按"用途"排列的——洗涤用品区、零食区、生鲜区。Embedding 做的就是把每段文本"放"到正确的"语义超市"中的对应区域。

---

## 🧠 核心原理详解

### Embedding 是什么？（说人话版）

给一段文字生成一串数字（比如 384 个小数），这串数字就是这段文字的"语义身份证"。

```
"我喜欢喝红豆沙" → [0.23, -0.45, 0.89, 0.12, ..., 0.67]  # 共384个数
"红豆沙很好喝"   → [0.21, -0.43, 0.91, 0.10, ..., 0.65]  # 非常接近
"今天股票大跌"   → [-0.88, 0.33, -0.12, 0.95, ..., -0.44] # 完全不同
```

**关键特性**：
1. **固定维度**：不管输入多长，输出维度固定（384/768/1024维等）
2. **语义聚类**：同类话题的文本向量自然聚集
3. **支持运算**：可以做相似度计算、向量加减等数学操作

### 三种相似度计算方法

这是今天的核心。我们用"两个人的关系"来类比：

#### 1. 余弦相似度（Cosine Similarity）

**原理**：不看两个人的"绝对距离"，只看他们的"方向"是否一致。

```python
def cosine_sim(vec1, vec2):
    """
    计算余弦相似度
    
    数学公式: cos(θ) = (A·B) / (|A| × |B|)
    
    返回值范围: [-1, 1]
      1  = 完全同向（极度相似）
      0  = 垂直（无关）
     -1  = 完全反向（对立）
    """
    dot_product = np.dot(vec1, vec2)          # 点积：对应元素相乘再求和
    norm1 = np.linalg.norm(vec1)               # 向量的模长（长度）
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)
```

> 💡 **类比**：两个人从原点出发走，余弦相似度不看他们走了多远，只看他们走的方向是不是同一个。一个人走了 100 米、另一个人走了 10 米没关系，只要方向一样，相似度就是 1.0。

#### 2. 欧氏距离（Euclidean Distance）

**原理**：两点之间的"直线距离"。

```python
def euclidean_dist(vec1, vec2):
    """
    计算欧氏距离
    
    数学公式: d = √(Σ(Ai - Bi)²)
    
    返回值范围: [0, +∞)
      0  = 两个向量完全相同
     越大 = 越不相似
    """
    return np.linalg.norm(vec1 - vec2)
```

> 💡 **类比**：GPS 导航显示的"直线距离"。两个点在地图上的物理距离。

#### 3. 点积（Dot Product）

**原理**：向量对应元素相乘后求和。不考虑向量长度归一化。

```python
def dot_product(vec1, vec2):
    """
    计算点积
    
    数学公式: A·B = Σ(Ai × Bi)
    
    返回值范围: (-∞, +∞)，越大越相似
    """
    return np.dot(vec1, vec2)
```

> 💡 **类比**：两个人的"综合匹配度"。如果一个人在所有维度都很强、另一个人也很强，点积就会很大。

### 三种方法对比总结

| 方法 | 值域 | 越大/越小越相似 | 适用场景 | 计算成本 |
|------|------|----------------|---------|---------|
| 余弦相似度 | [-1, 1] | 越大越相似 | 文本语义匹配（首选） | 中 |
| 欧氏距离 | [0, ∞) | 越小越相似 | 数值型数据、图像检索 | 低 |
| 点积 | (-∞, ∞) | 越大越相似 | 已归一化的向量、推荐系统 | 最低 |

**实际 RAG 项目中最常用的是余弦相似度**，因为它不受向量长度影响，只看语义方向。

---

## 💻 代码实战：从零计算相似度

### Step 1：手动构造示例向量

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ⚠️ 中文字体配置（不配置中文会显示为方块）
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

# 用4维向量模拟 Embedding（真实场景是384+维）
vectors = {
    "机器学习": np.array([0.8, 0.6, 0.2, 0.1]),
    "深度学习": np.array([0.7, 0.5, 0.3, 0.2]),   # 和"机器学习"很近
    "猫咪":     np.array([0.2, 0.8, 0.1, 0.9]),
    "狗":       np.array([0.3, 0.7, 0.2, 0.8]),    # 和"猫咪"很近
    "苹果":     np.array([0.9, 0.1, 0.8, 0.2]),
    "手机":     np.array([0.1, 0.9, 0.3, 0.7])     # 和"苹果"不算近
}
```

### Step 2：计算所有文本两两之间的相似度

```python
texts = list(vectors.keys())
n = len(texts)

# 初始化相似度矩阵
cosine_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        # 余弦相似度 = 点积 / (模长A × 模长B)
        v1, v2 = vectors[texts[i]], vectors[texts[j]]
        cosine_matrix[i, j] = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print("余弦相似度矩阵：")
print(f"{'':10s}", end="")
for t in texts:
    print(f"{t:8s}", end="")
print()
for i, t in enumerate(texts):
    print(f"{t:10s}", end="")
    for j in range(n):
        print(f"{cosine_matrix[i,j]:.3f}  ", end="")
    print()
```

**预期输出**："机器学习"和"深度学习"的相似度会很高（>0.9），"猫咪"和"机器学习"的相似度会很低。

### Step 3：用真实模型编码中文文本

```python
from sentence_transformers import SentenceTransformer, util

# 加载多语言模型（首次运行自动下载约 400MB）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 测试文本——故意用不同表达方式说类似的话
sentences = [
    "机器学习是人工智能的重要分支",      # 技术陈述
    "深度学习属于机器学习的子集",        # 技术陈述
    "我喜欢喝糖水",                    # 日常话题
    "美华糖水店的芋圆很好吃",            # 糖水店相关
    "Python是一种编程语言",             # 技术话题
    "Java是另一种编程语言",             # 技术话题
    "我今天想喝奶茶",                  # 日常饮食
    "天气预报说明天会下雨"               # 无关话题
]

# 生成 Embedding
embeddings = model.encode(sentences)
print(f"Embedding 形状: {embeddings.shape}")  # (8, 384)

# 计算 8×8 的余弦相似度矩阵
sim_matrix = util.cos_sim(embeddings, embeddings)

# 找最相似的句子对
max_sim = 0
best_pair = None
for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        if sim_matrix[i][j] > max_sim:
            max_sim = sim_matrix[i][j]
            best_pair = (sentences[i], sentences[j])

print(f"最相似的句子对：'{best_pair[0]}' 和 '{best_pair[1]}'")
print(f"相似度: {max_sim:.4f}")
```

---

## 📊 可视化：向量空间中的语义聚类

```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# 模拟不同主题的二维向量分布
tech_vecs     = np.random.normal([2, 2],   [0.5, 0.5], (20, 2))  # 科技
medical_vecs  = np.random.normal([-2, 2],  [0.5, 0.5], (20, 2))  # 医疗
finance_vecs  = np.random.normal([2, -2],  [0.5, 0.5], (20, 2))  # 金融
education_vecs= np.random.normal([-2, -2], [0.5, 0.5], (20, 2))  # 教育

plt.figure(figsize=(10, 8))
plt.scatter(tech_vecs[:,0], tech_vecs[:,1], c='red', alpha=0.7, s=50, label='科技类')
plt.scatter(medical_vecs[:,0], medical_vecs[:,1], c='blue', alpha=0.7, s=50, label='医疗类')
plt.scatter(finance_vecs[:,0], finance_vecs[:,1], c='green', alpha=0.7, s=50, label='金融类')
plt.scatter(education_vecs[:,0], education_vecs[:,1], c='orange', alpha=0.7, s=50, label='教育类')

# 模拟查询向量
query = np.array([1.5, 1.8])
plt.scatter(query[0], query[1], c='black', s=120, marker='X', label='查询向量', zorder=5)

# 画检索范围圈
circle = plt.Circle(query, 0.8, fill=False, color='black', linestyle='--')
plt.gca().add_patch(circle)

plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
plt.title('向量空间中的语义聚类', fontsize=14, fontweight='bold')
plt.xlabel('语义维度 1')
plt.ylabel('语义维度 2')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

**观察要点**：
- 同主题文档在空间中自然聚成"一团"
- 查询向量落在"科技类"区域附近，圆圈内的红色点就是检索结果
- 这就是 RAG 检索的几何本质：**找空间中最近的点**

---

## 🍧 业务关联：糖水店智能搜索

### 场景：顾客搜索"解暑的甜品"

```python
# 产品知识库
products = [
    "红豆沙：传统粤式糖水，清热解暑，夏季首选",
    "芝麻糊：香浓滋补，秋冬暖身推荐",
    "杨枝甘露：芒果西米露，冰凉爽口，热带风情",
    "姜撞奶：暖胃驱寒，冬日必备",
    "绿豆沙：清热解毒，消暑利湿，经典夏日糖水",
    "双皮奶：顺滑细腻，奶香浓郁，老少皆宜"
]

# 向量化
product_embeddings = model.encode(products)

# 顾客查询
query = "天气热想喝点凉的"
query_embedding = model.encode([query])

# 计算相似度
similarities = util.cos_sim(query_embedding, product_embeddings)[0]

# 按相似度排序
ranked = sorted(enumerate(similarities), key=lambda x: x[1], reverse=True)

print(f"🔍 查询：'{query}'")
print("推荐结果：")
for rank, (idx, score) in enumerate(ranked[:3]):
    print(f"  {rank+1}. [{score:.3f}] {products[idx]}")
```

**预期结果**：绿豆沙、杨枝甘露、红豆沙会排在前面——虽然它们的描述里没有"天气热"这几个字，但语义上它们就是"解暑"的。

---

## ⚠️ 常见误区

### 误区 1："Embedding 维度越高越好"
❌ 维度高意味着精度好，但计算成本和存储成本也急速上升。384 维和 768 维在实际项目中差距可能不大，但 1536 维的延迟翻倍。要根据场景权衡。

### 误区 2："随便选一个 Embedding 模型就行"
❌ Embedding 模型有领域差异。在医疗、法律等专业领域，通用模型表现可能很差。一定要用你实际业务数据做测试。

### 误区 3："相似度高就意味着真的相关"
❌ Embedding 捕捉的是"语义相似度"，不等于"业务相关性"。比如"收入增长"和"成本增长"语义相似度很高（都在说财务增长），但业务含义完全不同。

### 误区 4："欧氏距离和余弦相似度效果一样"
❌ 当向量长度（模长）差异大时，两者结果差异显著。文本场景下一般首选余弦相似度，因为它对文本长度不敏感。

---

## 📝 课堂练习

**练习 1**：给定三个向量 A=[1,0], B=[0,1], C=[1,1]，手动计算 A 和 C 的余弦相似度。

**练习 2**：为什么在文本检索中，余弦相似度比欧氏距离更常用？请给出两个原因。

**练习 3**：用 Sentence-Transformers 编码以下三个句子，计算两两相似度：
- "糖水店今天搞活动"
- "甜品坊本日有促销"
- "银行利率调整"
观察前两句的相似度是否明显高于第三句，并思考原因。

---

## ✅ 课后测试

1. Embedding 的核心作用是把 ______ 转换成 ______。

2. 余弦相似度的值域是 ______，当两个向量完全相同时，值为 ______。

3. 判断题：欧氏距离越小，表示两个向量越不相似。（  ）

4. 在 RAG 系统中，检索阶段通常返回 ______（用英文术语）个最相关的文档片段。

5. 选择题：以下哪种情况会导致 Embedding 质量下降？（  ）
   A. 使用领域专用的 Embedding 模型
   B. 文本包含大量乱码和噪声
   C. 对文本进行预处理和清洗
   D. 增大 chunk_size

---

## 📖 术语表

| 英文 | 音标 | 中文 | 说明 |
|------|------|------|------|
| Embedding | /ɛmˈbɛdɪŋ/ | 向量嵌入 | 将文本映射为高维向量的技术 |
| Cosine Similarity | /ˈkoʊsaɪn ˌsɪmɪˈlærɪti/ | 余弦相似度 | 衡量向量方向一致性的指标 |
| Euclidean Distance | /juːˈklɪdiən ˈdɪstəns/ | 欧氏距离 | 向量间的直线距离 |
| Dot Product | /dɒt ˈprɒdʌkt/ | 点积/内积 | 向量对应元素乘积之和 |
| Vector Space | /ˈvɛktər speɪs/ | 向量空间 | 向量所在的数学空间 |
| Semantic Similarity | /sɪˈmæntɪk ˌsɪmɪˈlærɪti/ | 语义相似度 | 文本含义上的接近程度 |
| Sentence Transformer | /ˈsɛntəns trænsˈfɔːrmər/ | 句子变换器 | 生成句子级Embedding的模型 |
| Vector Dimension | /ˈvɛktər daɪˈmɛnʃən/ | 向量维度 | 向量的元素个数 |
| ANN (Approximate Nearest Neighbor) | /əˈprɒksɪmɪt ˈniːrɪst ˈneɪbər/ | 近似最近邻 | 高维空间中快速找最近向量的算法 |
| Norm | /nɔːrm/ | 模长/范数 | 向量的长度 |

---

## 🔗 参考资源

- 📦 [Sentence-Transformers 官方文档](https://www.sbert.net/)
- 📊 [MTEB 中文 Embedding 排行榜](https://github.com/FlagOpen/FlagEmbedding)
- 📄 [BERT 原始论文](https://arxiv.org/abs/1810.04805)
- 🎥 [3Blue1Brown: 线性代数本质（理解向量）](https://www.youtube.com/watch?v=fNk_zzaMoSs)
- 📚 [HuggingFace Embedding 模型选型指南](https://huggingface.co/blog/mteb)

---

> 🚀 **明天预告**：Day 3 进入高级 RAG 领域——混合检索（BM25+向量）、重排序（Cross-Encoder）、查询改写（HyDE），这些技术能把检索准确率从 70% 提到 90%+！
