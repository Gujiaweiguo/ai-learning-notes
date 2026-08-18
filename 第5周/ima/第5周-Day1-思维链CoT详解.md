# 第5周 Day1：思维链（Chain-of-Thought）详解

> **导语**：你有没有发现，当你让 AI 算一道稍微复杂的数学题时，它经常会"一本正经地胡说八道"？明明每一步看起来都对，最后答案却是错的。问题出在哪里？答案很简单——它跳步了。今天我们要学的**思维链（Chain-of-Thought, CoT）**，就是教 AI 像学生做应用题一样，把推导过程一步一步写出来，而不是直接报答案。这个看似简单的小技巧，却能让大模型的推理能力产生质的飞跃。

---

## 📊 学习进度

```
■■■■■■■■■■■■■■■■■■■■■□□□□□□□□□□□□□□□□□□□□□□□□□□□
W1 ✅  W2 ✅  W3 ✅  W4 ✅  W5 🔵 进行中  W6-W12 待解锁
```

- **当前进度**：第5周 / 共12周
- **本周主题**：推理与思维链
- **今日位置**：Day1 —— 从思维链的原理说起

---

## 🤔 为什么需要思维链？

### 一个生活中的场景

假设你去超市买水果：苹果 5 元一斤，香蕉 3 元一斤，你买了 3 斤苹果和 2 斤香蕉，又用了一张 5 元优惠券，最后要付多少钱？

你的思考过程大概是这样的：
1. 苹果花了 5×3=15 元
2. 香蕉花了 3×2=6 元
3. 小计 15+6=21 元
4. 减去优惠券 21-5=16 元
5. 答案：16 元

你看，你**自然而然地分步思考**了。这就是思维链——先展示推理过程，再得出结论。

### 大模型不写过程的后果

如果不让大模型写过程，它就只有一个"直觉"输出窗口。就像老师让你做一道 5 步的应用题，你却只能回答一个数字。错率自然高得离谱。

研究表明：
- 在 GSM8K（小学数学题）上，不做 CoT 的大模型准确率只有 45% 左右
- 加上 CoT 之后，准确率可以飙升到 73% 甚至 86%
- 越是复杂的多步推理，CoT 的提升幅度越大

### 为什么"展示过程"这么有效？

这要从大模型的**自回归生成机制**说起。大模型每次只能生成一个 Token，后面的 Token 依赖于前面的 Token。如果模型直接跳到答案，它就没有"思考空间"——答案前面的 Token 是空白的。但如果允许它先写推理步骤，这些步骤就会成为后续生成的**上下文**，帮助它"想清楚"再回答。

用一个类比：这就像考试时草稿纸不够用，你只能心算，出错概率肯定更高。思维链就是给大模型发了一张"草稿纸"。

---

## 🧠 核心原理详解

### 1. 什么是 Chain-of-Thought？

**定义**：思维链是一种提示技术，通过让大语言模型在给出最终答案之前，先生中间推理步骤，从而提升模型在复杂推理任务上的表现。

**论文出处**：Wei et al., 2022, *"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"*

说人话就是：**"先别急着回答，把过程写出来。"**

### 2. 两大核心类型

#### （1）Zero-shot CoT（零样本思维链）

最简单的版本，只需要在你的问题后面加一句"咒语"：

```
问题：一个班有30个学生，分成6组，每组几个人？

让我们一步步思考。
```

就加了一句"让我们一步步思考"，模型就会自动展开推理过程。这句"咒语"被称为 **CoT trigger prompt**。

**为什么有效？** 因为模型在海量训练数据中见过大量"先分析再总结"的文本模式。当你加一句"一步步思考"，就激活了这些模式，相当于按下了"推理模式"的开关。

#### （2）Few-shot CoT（少样本思维链）

给模型看几个带推理过程的例子，再让它回答新问题：

```
示例1：
问题：小明有10个苹果，吃了3个，还剩几个？
回答：第一步：知道开始有10个苹果
      第二步：知道吃了3个
      第三步：用10-3=7
      答案：还剩7个苹果

示例2：
问题：一支笔3元，买5支要多少钱？
回答：第一步：知道每支笔3元
      第二步：知道要买5支
      第三步：用3×5=15
      答案：需要15元

现在请回答：
问题：一个班有30个学生，分成6组，每组几个人？
```

模型看了两个"先分步再总结"的例子，就会照葫芦画瓢，也用这种方式回答。

### 3. 两种类型的对比

| 维度 | Zero-shot CoT | Few-shot CoT |
|------|--------------|--------------|
| **实现难度** | 极低，加一句话 | 中等，需要准备示例 |
| **效果** | 提升明显但有限 | 效果更好 |
| **适用场景** | 快速尝试 | 追求高准确率 |
| **对 Token 消耗** | 较少 | 较多（示例也要占 Token） |
| **灵活性** | 可用于任何任务 | 需要针对性设计示例 |

### 4. CoT 变体大家族

除了最基础的两种，CoT 还衍生出很多变体：

- **Auto-CoT**：让模型自己生成示例，省去人工编写
- **Active-CoT**：自动选择最有代表性的示例
- **Self-Consistency CoT**：多次生成推理链，投票选最一致的答案
- **Tree-of-Thought (ToT)**：不只是线性推理，而是分支探索（Day2 会讲）
- **Multimodal CoT**：图文结合的思维链

---

## 💻 代码实战：从零实现 CoT

### 1. 环境准备与中文字体配置

```python
# 标准科学计算 + 可视化库
import numpy as np
import matplotlib.pyplot as plt
import re

# matplotlib 中文字体配置——每次画图前都要跑这段
from matplotlib import font_manager

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示为方块的问题

print("✅ 字体配置完成，使用字体：", font_name)
```

**逐行解释**：
- `font_manager.fontManager.addfont(font_path)`：把 NotoCJK 字体注册到 matplotlib 的字体管理器
- `FontProperties(fname=font_path).get_name()`：获取该字体在系统中的注册名称
- `plt.rcParams["font.family"]`：设置全局默认字体
- `plt.rcParams["axes.unicode_minus"] = False`：防止负号 `-` 被渲染成乱码方块

### 2. 模拟 CoT vs 非 CoT 的回答对比

```python
def mock_model_response(question: str, use_cot: bool = False) -> str:
    """
    模拟大模型的两种回答模式：
    - use_cot=False：直接给答案（容易错）
    - use_cot=True：先写推理过程再给答案（更准确）
    """
    if use_cot:
        # 带思维链的回答——展示中间步骤
        if "算" in question or "多少" in question:
            steps = [
                "第一步：分析题目要求，提取关键数字",
                "第二步：确定运算顺序（先乘除后加减）",
                "第三步：逐步计算得出结果",
                "最终答案：正确答案来了！"
            ]
            return "\n".join(steps)
        else:
            return "分析问题 → 找关键信息 → 逻辑推理 → 答案"
    else:
        # 不带思维链——直接蹦答案
        return "答案：XX"

# 测试三个问题
questions = [
    "15 + 8 × 2 等于多少？",
    "小明有5个苹果，小红给了他3个，他又吃了2个，还剩几个？",
    "为什么天空是蓝色的？"
]

print("📚 思维链 vs 直接回答 对比实验：\n")
for i, q in enumerate(questions, 1):
    print(f"❓ 问题{i}: {q}")
    print(f"  💡 直接回答: {mock_model_response(q, use_cot=False)}")
    print(f"  🧠 思维链回答: {mock_model_response(q, use_cot=True)}")
    print()
```

### 3. Zero-shot CoT 与 Few-shot CoT 的 Prompt 构建

```python
def zero_shot_cot_prompt(question: str) -> str:
    """
    零样本思维链提示：
    只需要在问题后面加一句"让我们一步步思考"
    就能激活模型的推理模式
    """
    return f"让我们一步步思考这个问题：\n{question}\n请展示你的推理过程。"


def few_shot_cot_prompt(question: str, examples: list = None) -> str:
    """
    少样本思维链提示：
    先给2个带推理过程的示例，让模型"照葫芦画瓢"
    """
    if examples is None:
        # 默认示例——覆盖加减乘除四种基本运算
        examples = [
            {
                "question": "小明有10个苹果，吃了3个，还剩几个？",
                "answer": "第一步：知道开始有10个苹果\n"
                          "第二步：知道吃了3个\n"
                          "第三步：用10-3=7\n"
                          "答案：还剩7个苹果"
            },
            {
                "question": "一支笔3元，买5支要多少钱？",
                "answer": "第一步：知道每支笔3元\n"
                          "第二步：知道要买5支\n"
                          "第三步：用3×5=15\n"
                          "答案：需要15元"
            }
        ]
    
    # 拼装 Prompt：示例 + 新问题
    prompt = "以下是一些思考示例：\n\n"
    for ex in examples:
        prompt += f"问题：{ex['question']}\n回答：{ex['answer']}\n\n"
    prompt += f"现在请回答：\n{question}\n请展示你的推理过程。"
    return prompt

# 测试两种 Prompt
test_q = "一个班有30个学生，分成6组，每组几个人？"
print("=" * 50)
print("🔹 Zero-shot CoT:")
print(zero_shot_cot_prompt(test_q))
print("\n" + "=" * 50)
print("🔹 Few-shot CoT:")
print(few_shot_cot_prompt(test_q))
```

### 4. 推理质量评估器

```python
class SimpleCoT:
    """一个简易的思维链质量评估工具"""
    
    def __init__(self):
        # 匹配"第一步："这种模式
        self.steps_pattern = r'第[一二三四五六七八九十]+步[：:][^\n]+'
    
    def extract_reasoning(self, response: str) -> list:
        """从模型回答中提取推理步骤"""
        steps = re.findall(self.steps_pattern, response)
        return steps if steps else ["未找到明确的推理步骤"]
    
    def score_reasoning_quality(self, response: str, expected_answer) -> int:
        """
        对推理过程打分（0-100）：
        - 有多步推理 +30 分
        - 包含正确数字 +40 分  
        - 使用逻辑连接词 +30 分
        """
        if isinstance(expected_answer, (int, float)):
            expected_answer = [expected_answer]
        
        score = 0
        steps = self.extract_reasoning(response)
        
        # 检查推理步骤数量
        if len(steps) > 1:
            score += 30
        
        # 检查是否包含正确答案的数字
        if any(str(d) in response for d in expected_answer):
            score += 40
        
        # 检查逻辑连接词
        logic_words = ['首先', '然后', '最后', '因为', '所以', '因此']
        if any(w in response for w in logic_words):
            score += 30
        
        return min(score, 100)

# 测试评估器
cot = SimpleCoT()
sample = "第一步：计算总数30÷6\n第二步：所以每组5人\n答案：5人"
print(f"推理步骤: {cot.extract_reasoning(sample)}")
print(f"质量得分: {cot.score_reasoning_quality(sample, 5)}/100")
```

---

## 📊 可视化：CoT 到底有多大效果？

```python
def plot_cot_effectiveness():
    """
    用柱状图展示 CoT 在不同任务类型上的效果提升：
    - 数学推理：提升幅度最大（45% → 86%）
    - 逻辑推理：提升明显（38% → 78%）
    - 常识问答：提升一般（82% → 87%）
    - 简单事实：几乎无提升（95% → 97%）
    """
    tasks = ['数学推理', '逻辑推理', '常识问答', '简单事实']
    no_cot = [45, 38, 82, 95]       # 不使用 CoT
    zero_shot = [73, 62, 85, 96]    # Zero-shot CoT
    few_shot = [86, 78, 87, 97]     # Few-shot CoT

    x = np.arange(len(tasks))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(x - width, no_cot, width, label='无 CoT', color='#FF6B6B', alpha=0.85)
    ax.bar(x, zero_shot, width, label='Zero-shot CoT', color='#4ECDC4', alpha=0.85)
    ax.bar(x + width, few_shot, width, label='Few-shot CoT', color='#45B7D1', alpha=0.85)

    ax.set_xlabel('任务类型', fontsize=13)
    ax.set_ylabel('准确率 (%)', fontsize=13)
    ax.set_title('思维链对不同任务类型的效果提升', fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 105)

    # 在每根柱子上标注数值
    for i, (nc, zs, fs) in enumerate(zip(no_cot, zero_shot, few_shot)):
        ax.text(i - width, nc + 1, f'{nc}%', ha='center', fontsize=9)
        ax.text(i, zs + 1, f'{zs}%', ha='center', fontsize=9)
        ax.text(i + width, fs + 1, f'{fs}%', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('cot_effectiveness.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 图表已保存为 cot_effectiveness.png")

plot_cot_effectiveness()
```

**看图说话**：
- 数学推理从 45% 飙升到 86%，提升了 **41 个百分点**！
- 逻辑推理也有 40 个百分点的提升
- 但简单事实题几乎没变化——**CoT 不是万能药，它只在需要"推理"的任务上有效**

### CoT 变体的准确率与复杂度对比

```python
def plot_cot_variants():
    """
    不同 CoT 变体的准确率和实现复杂度对比：
    - 零样本 CoT：最简单，效果一般
    - 少样本 CoT：中等复杂度，效果不错
    - Auto-CoT：自动生成示例，省人工
    - Tree-of-Thought：最复杂但效果最好
    """
    variants = ['零样本CoT', '少样本CoT', 'Auto-CoT', 'Tree-of-Thought']
    accuracy = [70, 85, 88, 92]
    complexity = [1, 3, 4, 5]  # 1-5 分

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：准确率
    colors1 = ['#FFB6C1', '#98FB98', '#FFD700', '#FFA07A']
    bars1 = ax1.bar(variants, accuracy, color=colors1, alpha=0.85)
    ax1.set_title('不同 CoT 变体的准确率', fontsize=14, fontweight='bold')
    ax1.set_ylabel('准确率 (%)', fontsize=12)
    ax1.set_ylim(0, 100)
    for bar, v in zip(bars1, accuracy):
        ax1.text(bar.get_x() + bar.get_width()/2, v + 1, f'{v}%',
                 ha='center', fontsize=11)

    # 右图：复杂度
    bars2 = ax2.bar(variants, complexity, color=colors1, alpha=0.85)
    ax2.set_title('不同 CoT 变体的实现复杂度', fontsize=14, fontweight='bold')
    ax2.set_ylabel('复杂度 (1=最简单, 5=最复杂)', fontsize=12)
    ax2.set_ylim(0, 6)
    for bar, v in zip(bars2, complexity):
        ax2.text(bar.get_x() + bar.get_width()/2, v + 0.1, f'{v}',
                 ha='center', fontsize=11)

    plt.tight_layout()
    plt.savefig('cot_variants.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 图表已保存为 cot_variants.png")

plot_cot_variants()
```

---

## 🏪 业务关联：LangChat / Agent 场景

思维链在业务系统中怎么落地？以下是一些实际应用场景：

### 1. 客服机器人：多步问题分解

```
用户：我昨天下的单还没到，怎么办？

CoT 推理链：
第一步：识别用户问题 → 物流查询
第二步：提取订单信息 → 需要订单号
第三步：查询物流状态 → 调用物流 API
第四步：判断是否异常 → 超时未送达
第五步：给出解决方案 → 补发或退款
```

在 **LangChat** 中，你可以通过配置 CoT Prompt 模板，让客服机器人在处理复杂问题时自动走推理链，而不是直接蹦一个"请联系客服"。

### 2. 数据分析 Agent：多指标计算

```
用户：这个月的销售额比上个月增长了多少？

CoT 推理链：
第一步：查询本月销售额 → 调用数据库 API → 结果 150万
第二步：查询上月销售额 → 调用数据库 API → 结果 120万
第三步：计算增长率 → (150-120)/120 × 100% = 25%
第四步：组织回答 → 本月销售额比上月增长 25%
```

### 3. 决策支持系统

在 Agent 框架中，CoT 常常作为"大脑"负责推理，外部工具作为"手脚"负责执行。推理链决定了 Agent 要调用哪些工具、以什么顺序调用、如何整合结果。

---

## ⚠️ 常见误区

### 误区1："CoT 能让模型在所有任务上都变强"
**事实**：CoT 只对需要多步推理的任务有效。对于简单的事实检索（"中国首都是哪里？"）或文本生成（"写一首诗"），加不加 CoT 区别不大，反而浪费 Token。

### 误区2："示例越多越好"
**事实**：Few-shot CoT 的示例不需要太多，通常 2-5 个就够了。关键是示例的**质量**和**多样性**，而不是数量。太多示例会挤占上下文窗口，反而影响效果。

### 误区3："随便写'让我们一步步思考'就行了"
**事实**：这句 trigger prompt 对不同模型的效果不同。有些模型需要更明确的指令，比如"请先分析已知条件，再逐步推导，最后给出答案"。

### 误区4："CoT 的推理过程一定是正确的"
**事实**：CoT 展示的是模型"看起来在推理"，但中间步骤也可能出错。这被称为**"伪推理"现象**——模型可能先得出了答案，再编造一个看似合理的推理链。所以对于关键场景，需要配合**自洽性检查**。

### 误区5："只有大模型才能用 CoT"
**事实**：研究发现 CoT 对参数量有"涌现阈值"——通常在 60B 参数以上才显著有效。但小模型可以通过**蒸馏**（把大模型的推理链作为训练数据）来获得类似能力。

---

## ✏️ 课堂练习（5分钟）

**练习1**：请为以下问题写一段 Zero-shot CoT Prompt：

> "一个长方形游泳池，长50米，宽25米，深2米。如果每小时注水200立方米，需要多少小时才能注满？"

**练习2**：请为以下问题设计一个包含 2 个示例的 Few-shot CoT Prompt：

> "书店举行'买三送一'活动，一本书原价40元，小明买了8本，实际花了多少钱？"

**练习3**：思考题——如果你在做一个客服机器人，什么类型的用户问题适合用 CoT？什么类型不适合？

---

## 📝 课后测试（15分钟）

**❶ 思维链（CoT）的核心思想是什么？**
A. 让模型生成更多文字
B. 让模型在给出答案前先展示推理过程
C. 让模型使用更大的参数量
D. 让模型搜索互联网获取信息

**❷ 以下哪种是 Zero-shot CoT 的典型用法？**
A. 给模型 5 个例题再让它回答
B. 在问题后加"让我们一步步思考"
C. 让模型调用计算器工具
D. 让模型多次回答取众数

**❸ Few-shot CoT 相比 Zero-shot CoT 的主要优势是？**
A. 使用的 Token 更少
B. 不需要设计示例
C. 通过示例引导推理格式，效果通常更好
D. 可以用于任何模型

**❹ CoT 在哪类任务上效果提升最显著？**
A. 简单事实查询
B. 多步数学推理
C. 文本摘要
D. 情感分析

**❺ 简答题：为什么说"展示推理过程"能帮助大模型得到更准确的答案？（提示：从自回归生成机制角度思考）**

---

## 📖 术语表

| 英文术语 | 音标 | 中文释义 |
|---------|------|---------|
| Chain-of-Thought (CoT) | /tʃeɪn əv θɔːt/ | 思维链，让模型一步步推理不跳步 |
| Zero-shot CoT | /ˈzɪərəʊ ʃɒt/ | 零样本思维链，只加"请一步步思考"即可 |
| Few-shot CoT | /fjuː ʃɒt/ | 少样本思维链，先给带推理过程的例题 |
| Inference | /ˈɪnfərəns/ | 推理，从已知信息推导结论 |
| Decomposition | /ˌdiːkɒmpəˈzɪʃən/ | 分解，把复杂问题拆成简单小问题 |
| Demonstration | /ˌdemənˈstreɪʃən/ | 示范，给模型看的"例题" |
| Generalization | /ˌdʒenərəlaɪˈzeɪʃən/ | 泛化，学会一种方法解决类似新问题 |
| Hallucination | /həˌluːsɪˈneɪʃən/ | 幻觉，模型编造不存在的信息 |
| Intermediate Step | /ˌɪntəˈmiːdiət step/ | 中间步骤，推理过程中不直接跳到答案 |
| Scratchpad | /ˈskrætʃpæd/ | 草稿本，模型用来打草稿的输出空间 |
| Token | /ˈtəʊkən/ | 词元，模型处理文本的最小单位 |
| Autoregressive | /ˌɔːtəʊrɪˈɡresɪv/ | 自回归，根据已生成内容预测下一个 Token |
| Trigger Prompt | /ˈtrɪɡə prɒmpt/ | 触发提示，激活模型特定模式的提示语 |

---

## 🔗 参考资源

- 📄 **原始论文**：[Chain