# 第5周 Day2：Tree-of-Thought 与图推理

> **导语**：昨天我们学了思维链（CoT），它让 AI 像走直线一样一步步推理。但现实世界的问题往往不是直线型的——你有多种思路，每种思路可能走到一半发现行不通，需要回头换一条路。这就是今天的主角：**Tree-of-Thought（思维树，ToT）**。它让 AI 像下棋一样，同时考虑多条路径，遇到死胡同就回溯，最终找到最优解。我们还会学习图推理，用节点和边来表示复杂的关系网络。

---

## 📊 学习进度

```
■■■■■■■■■■■■■■■■■■■■■■□□□□□□□□□□□□□□□□□□□□□□□□□□
W1 ✅  W2 ✅  W3 ✅  W4 ✅  W5 🔵 进行中（Day2/7）  W6-W12 待解锁
```

---

## 🌳 为什么需要 Tree-of-Thought？

### CoT 的局限性

思维链（CoT）是一条**线性**的推理路径：A → B → C → D → 答案。问题在于，如果 C 这一步走错了，后面全盘皆错——没有回头路。

打个比方：你去一个陌生的地方导航，CoT 就像只给你规划了一条路线。如果中间修路了，你就卡死了。

### 现实问题的"多路径"特征

很多问题天然有多条解题思路：

**例子**：一道数学题"一个水池，甲管 6 小时注满，乙管 12 小时注满，两管同时开几小时注满？"

- 思路 A：算每根管子的注水速度，然后相加 → 1/6 + 1/12 = 1/4 → 4 小时
- 思路 B：设总量为 1，列方程 → 1/(1/6 + 1/12) = 4 小时
- 思路 C：举例验证 → 12 小时内甲管注 2 池，乙管注 1 池，共 3 池 → 每池 4 小时

三条路都通向同一个答案。但有些问题可能只有一条路是对的，其他路是死胡同。**ToT 的价值在于同时探索多条路径，淘汰走不通的，保留走得通的。**

### 一个生动的类比

| 推理方法 | 生活类比 | 特点 |
|---------|---------|------|
| 直接回答 | 蒙答案 | 快但不可靠 |
| CoT（思维链） | 走一条路到终点 | 有方向但走错就完了 |
| ToT（思维树） | 导航软件规划多条路线 | 并行探索，选最优 |
| 图推理 | 地铁线路图找换乘 | 网络化关系推理 |

---

## 🧠 核心原理详解

### 1. Tree-of-Thought 的四个步骤

ToT 把推理过程拆成四个阶段：

#### 步骤一：分解（Decompose）
把大问题拆成一系列小决策点。就像走迷宫，每个岔路口就是一个决策点。

#### 步骤二：生成候选（Generate）
在每个决策点，让模型生成多个可能的"下一步思考"。比如面对一个数学题，可以同时尝试"代数方法""几何方法""枚举方法"。

#### 步骤三：评估（Evaluate）
给每条候选路径打分——这条路走得通吗？逻辑有没有漏洞？前景如何？分数低的路径会被"剪枝"。

#### 步骤四：搜索（Search）
在所有可能的推理路径中搜索最优解。常用搜索策略包括：
- **广度优先搜索（BFS）**：先把同一层的所有可能性都试一遍，再深入
- **深度优先搜索（DFS）**：先沿一条路走到底，不行再回溯
- **蒙特卡洛树搜索（MCTS）**：AlphaGo 同款算法，用随机模拟评估路径

### 2. 剪枝（Pruning）：砍掉没希望的分支

想象你在考试时，面前有 10 种解法。聪明的学生不会每种都从头算到尾——他们会快速扫一眼，排除明显不靠谱的，只深入尝试最有希望的 2-3 种。

ToT 的剪枝策略也是同理：
- 如果某条路径的评估分数低于阈值 → 直接砍掉
- 如果某条路径出现了逻辑矛盾 → 直接砍掉
- 这样可以把计算资源集中在最有希望的路径上

### 3. 自洽性（Self-Consistency）

当多条路径最终得出相同答案时，这个答案的可靠度就大大提高。就像你问了 5 个朋友同一道数学题，3 个都说答案是 42，那 42 大概率是对的。

### 4. 图推理（Graph Reasoning）

图推理是把问题建模为**图结构**（节点 + 边），然后通过图上的搜索算法来求解。

**什么情况下用图推理？**
- 问题中存在明确的关系网络（如社交关系、交通网络）
- 需要找最短路径或最优路径
- 实体之间存在复杂的多对多关系

**经典算法：Dijkstra 最短路径**
- 从起点出发，逐步扩展到所有可达节点
- 每次选择距离最短的未处理节点
- 最终得到起点到终点的最短路径

---

## 💻 代码实战

### 1. 环境准备

```python
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx  # 用于绘制网络图
from typing import List, Dict, Tuple, Any
import heapq           # 用于优先队列（Dijkstra 算法）

# 中文字体配置——照例先跑这段
from matplotlib import font_manager

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

print("✅ 环境准备就绪，字体：", font_name)
```

### 2. 绘制思维树示意图

```python
def draw_tree_of_thought():
    """
    用 NetworkX 画一棵思维树：
    根节点是"问题"，分出3条思路，每条思路得出一个中间结论，
    最后汇聚到"最优解"。
    """
    G = nx.DiGraph()  # 有向图

    # 添加节点
    nodes = ['问题', '思路A\n(代数法)', '思路B\n(几何法)', '思路C\n(枚举法)',
             '结论A', '结论B', '结论C', '最优解']
    G.add_nodes_from(nodes)

    # 添加边——表示推理流向
    edges = [
        ('问题', '思路A\n(代数法)'),
        ('问题', '思路B\n(几何法)'),
        ('问题', '思路C\n(枚举法)'),
        ('思路A\n(代数法)', '结论A'),
        ('思路B\n(几何法)', '结论B'),
        ('思路C\n(枚举法)', '结论C'),
        ('结论A', '最优解'),
        ('结论B', '最优解'),
        ('结论C', '最优解'),
    ]
    G.add_edges_from(edges)

    # 设置布局——树形分层布局
    pos = {
        '问题': (0, 4),
        '思路A\n(代数法)': (-3, 3),
        '思路B\n(几何法)': (0, 3),
        '思路C\n(枚举法)': (3, 3),
        '结论A': (-3, 2),
        '结论B': (0, 2),
        '结论C': (3, 2),
        '最优解': (0, 1),
    }

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=2500, font_size=9, font_family=font_name,
            arrows=True, arrowsize=20, edge_color='gray',
            edgecolors='black', linewidths=1.5)

    plt.title('Tree-of-Thought 思维树示意图', fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig('tot_tree.png', dpi=150, bbox_inches='tight')
    plt.show()

draw_tree_of_thought()
```

### 3. 实现一个思维树推理引擎

```python
class TreeOfThought:
    """
    一个简易的思维树推理框架：
    1. 定义问题
    2. 添加多条推理分支
    3. 检查自洽性
    4. 输出最佳答案
    """

    def __init__(self, problem: str):
        self.problem = problem
        self.branches = []          # 存储所有推理分支
        self.final_answer = None

    def add_branch(self, method: str, reasoning: str, answer: Any):
        """
        添加一条推理分支
        - method: 使用的解法名称
        - reasoning: 推理过程
        - answer: 该分支得出的答案
        """
        branch = {
            'method': method,
            'reasoning': reasoning,
            'answer': answer,
            'is_consistent': True  # 初始标记为一致
        }
        self.branches.append(branch)

    def check_consistency(self) -> float:
        """
        检查所有分支的自洽性：
        - 如果多个分支得出相同答案，一致性高
        - 如果各分支答案不同，一致性低
        返回一致性比例（0-1）
        """
        if len(self.branches) < 2:
            return 1.0

        # 统计各答案的出现次数
        answers = [b['answer'] for b in self.branches]
        answer_counts = {}
        for a in answers:
            answer_counts[a] = answer_counts.get(a, 0) + 1

        # 最常见的答案
        most_common = max(answer_counts.values())
        consistency = most_common / len(answers)

        # 标记不一致的分支
        best_answer = max(answer_counts, key=answer_counts.get)
        for b in self.branches:
            b['is_consistent'] = (b['answer'] == best_answer)

        return consistency

    def solve(self) -> dict:
        """求解并返回最佳答案"""
        consistency = self.check_consistency()
        consistent_branches = [b for b in self.branches if b['is_consistent']]

        # 选择第一个一致分支的答案作为最终答案
        self.final_answer = consistent_branches[0]['answer']

        return {
            'answer': self.final_answer,
            'consistency': consistency,
            'consistent_branches': len(consistent_branches),
            'total_branches': len(self.branches)
        }


# ====== 实战：用思维树解决数学题 ======
print("=" * 60)
print("🧮 思维树实战：计算 √25")
print("=" * 60)

tot = TreeOfThought("25 的平方根是多少？")

# 分支 A：试错法
tot.add_branch(
    method="试错法",
    reasoning="尝试几个数：4×4=16，5×5=25，找到了！",
    answer=5
)

# 分支 B：因数分解
tot.add_branch(
    method="因数分解",
    reasoning="25 = 5 × 5，所以 √25 = 5",
    answer=5
)

# 分支 C：近似估算
tot.add_branch(
    method="近似估算",
    reasoning="√25 在 4 和 6 之间，更接近 5",
    answer=5
)

result = tot.solve()
print(f"\n📊 结果：答案 = {result['answer']}")
print(f"📊 自洽性：{result['consistency']:.0%}")
print(f"📊 一致分支：{result['consistent_branches']}/{result['total_branches']}")
```

### 4. 图推理：最短路径搜索

```python
def draw_graph_reasoning():
    """
    用图推理解决路径规划问题：
    构建一个 5 节点的交通网络，找从起点 A 到终点 E 的最短路径
    """
    G = nx.Graph()

    # 5 个节点
    nodes = ['起点A', '节点B', '节点C', '节点D', '终点E']
    G.add_nodes_from(nodes)

    # 边（带权重 = 距离）
    edges = [
        ('起点A', '节点B', 3),   # A → B 距离 3
        ('起点A', '节点C', 1),   # A → C 距离 1
        ('节点B', '节点D', 2),   # B → D 距离 2
        ('节点C', '节点D', 4),   # C → D 距离 4
        ('节点D', '终点E', 2),   # D → E 距离 2
    ]
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    # 画图
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))

    nx.draw(G, pos, with_labels=True, node_color='lightgreen',
            node_size=2000, font_size=11, font_family=font_name,
            edge_color='gray', width=2)

    # 在边上标注权重
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=12)

    plt.title('图推理：交通网络最短路径', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('graph_reasoning.png', dpi=150, bbox_inches='tight')
    plt.show()

    return G

graph = draw_graph_reasoning()


def find_shortest_path(graph, start, end):
    """
    使用 Dijkstra 算法寻找最短路径：
    1. 从起点开始，距离为 0
    2. 每次选距离最短的未处理节点
    3. 更新该节点邻居的距离
    4. 重复直到到达终点
    """
    # 初始化所有节点的距离为无穷大
    distances = {node: float('infinity') for node in graph.nodes()}
    distances[start] = 0

    # 优先队列：(距离, 节点)
    priority_queue = [(0, start)]
    # 记录前驱节点（用于回溯路径）
    previous = {start: None}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # 到达终点
        if current_node == end:
            # 回溯路径
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = previous[node]
            path.reverse()
            return current_distance, path

        # 如果当前距离比已知距离大，跳过
        if current_distance > distances[current_node]:
            continue

        # 检查所有邻居
        for neighbor in graph.neighbors(current_node):
            edge_weight = graph[current_node][neighbor]['weight']
            new_distance = current_distance + edge_weight

            # 如果找到更短的路径
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return float('infinity'), []

# 运行最短路径搜索
distance, path = find_shortest_path(graph, '起点A', '终点E')
print(f"\n🛣️ 最短路径：{' → '.join(path)}")
print(f"📏 总距离：{distance}")
```

### 5. CoT vs ToT 效果对比可视化

```python
def compare_cot_vs_tot():
    """
    用可视化对比 CoT 和 ToT 在不同复杂度任务上的表现：
    - 简单任务：两者差不多
    - 中等任务：ToT 略好
    - 复杂任务：ToT 优势明显
    """
    task_complexity = ['简单任务', '中等任务', '复杂任务', '极复杂任务']
    cot_scores = [85, 72, 55, 38]   # CoT 准确率
    tot_scores = [87, 80, 75, 68]   # ToT 准确率

    x = np.arange(len(task_complexity))
    width = 0.3

    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, cot_scores, width, label='CoT（思维链）',
                   color='#FF6B6B', alpha=0.85)
    bars2 = ax.bar(x + width/2, tot_scores, width, label='ToT（思维树）',
                   color='#4ECDC4', alpha=0.85)

    ax.set_xlabel('任务复杂度', fontsize=13)
    ax.set_ylabel('准确率 (%)', fontsize=13)
    ax.set_title('CoT vs ToT：不同复杂度任务的效果对比', fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(task_complexity, fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{int(height)}%', ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('cot_vs_tot.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 关键发现：任务越复杂，ToT 的优势越明显！")

compare_cot_vs_tot()
```

### 6. 实战：商品定价策略（ToT 经典应用）

```python
def pricing_strategy_analysis():
    """
    用思维树方法分析最优定价策略：
    问题——成本价 100 元，定价 80~150 元之间，
    价格越高销量越低，目标是利润最大化。
    """
    def sales_volume(price):
        """模拟销量函数：价格越高，销量越低"""
        return max(0, 200 - 2 * price)

    def profit(price, cost=100):
        """利润 = (售价 - 成本) × 销量"""
        return (price - cost) * sales_volume(price)

    # 三条思维树分支：三种定价策略
    strategies = [
        {'name': '策略A: 成本加成法', 'price': 120, 'reasoning': '成本100元 + 加价20%'},
        {'name': '策略B: 市场导向法', 'price': 135, 'reasoning': '参考竞品价格，取中位'},
        {'name': '策略C: 利润最大化', 'price': 125, 'reasoning': '穷举试算找利润最大点'},
    ]

    print("🏪 定价策略思维树分析")
    print("=" * 50)
    for s in strategies:
        vol = sales_volume(s['price'])
        p = profit(s['price'])
        print(f"\n{s['name']}")
        print(f"  定价: ¥{s['price']}")
        print(f"  预计销量: {vol} 件")
        print(f"  预计利润: ¥{p:,.0f}")
        print(f"  推理: {s['reasoning']}")

    # 穷举找最优价格
    best_price = max(range(80, 151), key=lambda p: profit(p))
    print(f"\n🏆 最优定价：¥{best_price}")
    print(f"🏆 最大利润：¥{profit(best_price):,.0f}")
    print(f"🏆 最优销量：{sales_volume(best_price)} 件")

pricing_strategy_analysis()
```

---

## 🏪 业务关联：LangChat / Agent 场景

### 1. 多步骤决策 Agent

在 Agent 框架中，ToT 可以用来做多步骤决策。比如用户说"帮我策划一次促销活动"，Agent 可以：
- 分支 A：满减方案 → 计算成本 → 评估效果
- 分支 B：折扣方案 → 计算成本 → 评估效果
- 分支 C：赠品方案 → 计算成本 → 评估效果
- 自洽性检查：选 ROI 最高的方案

### 2. 客服路由

用户问了一个复杂问题，Agent 需要判断该路由到哪个处理流程。ToT 可以并行评估多种路由可能，选择最合适的。

### 3. 知识图谱推理

图推理在知识图谱上的应用天然适配 RAG 系统。从用户问题出发，在知识图谱上搜索相关实体和关系路径，找到最相关的答案。

---

## ⚠️ 常见误区

### 误区1："ToT 一定比 CoT 好"
**事实**：ToT 需要更多的计算资源（多次生成 + 评估 + 搜索）。对于简单问题，CoT 就够了，用 ToT 是杀鸡用牛刀。

### 误区2："分支越多越好"
**事实**：分支太多会导致组合爆炸。通常 3-5 条分支就够用了，配合剪枝策略可以有效控制计算量。

### 误区3："ToT 就是多次运行 CoT"
**事实**：ToT 的关键不在于"多运行几次"，而在于**结构化地探索**不同推理方向，并在中间步骤进行评估和剪枝。

### 误区4："图推理只适用于社交网络"
**事实**：任何包含关系网络的问题都可以用图推理——知识图谱、交通路线、依赖关系、组织架构等。

---

## ✏️ 课堂练习（5分钟）

**练习1**：请用思维树方法分析以下问题，至少写出 3 条推理分支：

> "一家咖啡店想要提高月营业额，有哪些可能的策略？哪一种投入产出比最高？"

**练习2**：给定以下交通网络，用 Dijkstra 算法手动计算从 A 到 D 的最短路径：
- A → B：5，A → C：2
- B → D：1，C → B：1，C → D：7

---

## 📝 课后测试（15分钟）

**❶ Tree-of-Thought 相比 Chain-of-Thought 的核心优势是什么？**
A. 生成速度更快
B. 可以并行探索多条推理路径
C. 使用的 Token 更少
D. 不需要 Prompt 设计

**❷ 在 ToT 中，"剪枝"的作用是什么？**
A. 让推理树更好看
B. 淘汰低分路径，节省计算资源
C. 增加推理分支
D. 替代搜索引擎

**❸ Dijkstra 算法用于解决什么问题？**
A. 文本分类
B. 图中最短路径搜索
C. 模型训练
D. 图像识别

**❹ 以下哪种搜索策略是"先探索完同一层再深入"？**
A. 深度优先（DFS）
B. 广度优先（BFS）
C. 线性搜索
D. 二分搜索

**❺ 简答题：自洽性检查是如何提高推理可靠性的？请举例说明。**

---

## 📖 术语表

| 英文术语 | 音标 | 中文释义 |
|---------|------|---------|
| Tree-of-Thought (ToT) | /triː əv θɔːt/ | 思维树，CoT 升级版，分支探索多条推理路径 |
| Graph Reasoning | /ɡrɑːf ˈriːzənɪŋ/ | 图推理，用图结构表示推理关系 |
| Backtracking | /ˈbækˌtrækɪŋ/ | 回溯，走到死胡同退回来换条路 |
| Branching | /ˈbrɑːntʃɪŋ/ | 分支，从一个点分出多条路径探索 |
| Heuristic Search | /hjʊˈrɪstɪk sɜːtʃ/ | 启发式搜索，用经验法则快速缩小范围 |
| Breadth-First Search (BFS) | /bredθ fɜːst/ | 广度优先，先探索同一层再深入 |
| Depth-First Search (DFS) | /depθ fɜːst/ | 深度优先，沿一条路走到底再回溯 |
| Pruning | /ˈpruːnɪŋ/ | 剪枝，去掉没希望的分支节省算力 |
| State Space | /steɪt speɪs/ | 状态空间，所有可能状态的集合 |
| Lookahead | /ˈlʊkəhed/ | 前瞻，预测未来几步再决定当前走法 |
| Self-Consistency | /self kənˈsɪstənsi/ | 自洽性，多路径验证答案一致性 |
| Dijkstra's Algorithm | /ˈdaɪkstrəz ˈælɡərɪðəm/ | 戴克斯特拉算法，经典最短路径算法 |
| Monte Carlo Tree Search | /ˈmɒnti ˈkɑːləʊ triː sɜːtʃ/ | 蒙特卡洛树搜索，AlphaGo 同款 |

---

## 🔗 参考资源

- 📄 **原始论文**：[Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)
- 📄 **自洽性论文**：[Self-Consistency Improves Chain of Thought Reasoning](https://arxiv.org/abs/2203.11171)
- 🎬 **推荐视频**：B站搜索"Tree of Thoughts 论文精读"
- 📚 **算法可视化**：[Visualgo](https://visualgo.net/) ——