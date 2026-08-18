# 第6周 Day 4：Agent 推理能力评测与 Prompt 工程

> **导语**：Agent 好不好，不能"感觉不错"，得拿数据说话。今天我们学习两件事：怎么评测大模型的推理能力（MMLU、GSM8K 是什么），以及怎么用 Prompt 技巧让模型"变聪明"（零样本、少样本、思维链、自洽性检查）。这些不仅是开发 Agent 的必备知识，也是 AI 面试的高频考点。

---

## 📊 学习进度

```
██████████████████████████████████░░░░░░░░░░░░░░░░░░ 53%
第1周 ✅  Python基础
第2周 ✅  AI与大模型基础
第3周 ✅  RAG检索增强生成
第4周 ✅  向量数据库与Embedding
第5周 ✅  大模型微调与部署
第6周 🔄  Agent与工具使用（Day 4/7）← 今天
```

---

## 一、为什么需要评测和 Prompt 工程？

### 1.1 一个常见的困境

你在 LangChat 平台上给企业搭了一个智能客服 Agent，老板问："这个 Agent 到底行不行？比之前的版本好多少？"

你怎么回答？"感觉不错"？——老板不会接受。

你需要**量化指标**来回答这个问题。这就是评测的意义。

同时，同样一个 Agent，换一种 Prompt（提示词）写法，效果可能差 30%。所以不仅要会评测，还要会通过 Prompt 工程来提升效果。

### 1.2 评测和 Prompt 的关系

**评测是"体检"**：用标准化的测试题，检查模型各方面的能力。
**Prompt 工程是"营养处方"**：根据体检结果，调整给模型的"输入"，让它发挥更好。

```
评测（知道模型强弱） → Prompt工程（针对弱项优化） → 再评测（验证效果提升）
```

### 1.3 生活类比

把大模型想象成一个学生：
- **MMLU** = 综合素质考试（考57门科目）
- **GSM8K** = 数学考试（考小学应用题）
- **HumanEval** = 编程考试（考函数实现）
- **Prompt 工程** = 教这个学生更好的做题方法

你不能只看一次考试成绩就说"这个学生行/不行"，要看多个维度。也不能怪学生笨——也许是你出题的方式（Prompt）不够好。

---

## 二、核心原理详解

### 2.1 三大评测基准

**基准一：MMLU（Massive Multitask Language Understanding）**

- **考什么**：知识广度，涵盖 57 个学科（法律、医学、计算机、历史、数学……）
- **题型**：选择题（A/B/C/D）
- **题量**：约 14,000 道
- **意义**：测试模型的"通识水平"。就像高考考语文、数学、英语、理综/文综

**为什么重要？** 因为企业 AI 需要处理跨领域的问题。糖水店的 Agent 可能被问到食品安全法规、营养学知识、消费者权益保护法……MMLU 分数高的模型，在跨领域问答中更可靠。

**基准二：GSM8K（Grade School Math 8K）**

- **考什么**：数学推理能力
- **题型**：小学数学应用题（别小看小学题，很多大模型在这里翻车）
- **题量**：约 8,500 道
- **特点**：需要多步推理，不是一步就能得出答案

**示例**：
```
题目：小明有25个苹果，给了小红1/5，又卖了剩下的50%，最后还剩多少个？
需要推理：
  1. 给了小红：25 × 1/5 = 5个
  2. 剩下：25 - 5 = 20个
  3. 卖了：20 × 50% = 10个
  4. 最后剩：20 - 10 = 10个
```

**为什么重要？** Agent 经常需要做计算和推理。比如"打完折后多少钱"、"这个月的利润率是多少"。GSM8K 分数高的模型，在多步推理任务中更准确。

**基准三：HumanEval**

- **考什么**：代码生成能力
- **题型**：给定函数签名和文档，补全函数实现
- **评分**：通过率（生成的代码能否通过单元测试）

**为什么重要？** 如果你的 Agent 需要生成代码（比如数据分析 Agent 自动生成 Python 脚本），HumanEval 分数高的模型更可靠。

### 2.2 Prompt 工程四大策略

**策略一：零样本（Zero-shot）**

直接提问，不给任何示例。
```
Prompt: "法国首都是哪里？"
回答: "巴黎。"  ← 可能答对，也可能答错
```

**适用场景**：简单事实问题、常识问题。
**缺点**：对复杂任务效果不稳定。

**策略二：少样本（Few-shot）**

先给几个示例，再提问。
```
Prompt:
  Q: 中国首都是？ A: 北京。
  Q: 日本首都是？ A: 东京。
  Q: 美国首都是？ A: 华盛顿。
  Q: 法国首都是？ A: ?
回答: "巴黎。"  ← 有示例参考，准确率更高
```

**适用场景**：特定格式输出、分类任务、翻译。
**关键点**：示例要有代表性，通常 2-5 个就够。

**策略三：思维链（Chain-of-Thought, CoT）**

要求模型展示推理过程，而不是直接给答案。

```
不用 CoT（可能算错）：
  Q: 一个糖水店每天卖出200杯，每杯利润3元，一个月利润多少？
  A: 18000元。  ← 可能直接算错

用 CoT（准确率高）：
  Q: 一个糖水店每天卖出200杯，每杯利润3元，一个月利润多少？请一步步计算。
  A: 
    Step 1: 每天利润 = 200杯 × 3元/杯 = 600元
    Step 2: 一个月（30天）= 600 × 30 = 18000元
    答案：18000元
```

**为什么 CoT 有效？**
- 让模型"慢下来"，分步推理减少跳步错误
- 中间步骤可见，便于发现和纠正错误
- 数学证明：对于多步推理任务，CoT 能提升 15-30% 的准确率

**策略四：自洽性（Self-consistency）**

对同一个问题生成多次推理路径，选出现频率最高的答案。

```
问题：25 × 20% = ?

  路径1: 25 × 0.2 = 5    ✅
  路径2: 25 × 0.2 = 5    ✅
  路径3: 25 × 0.2 = 5    ✅
  路径4: 25 × 0.2 = 4    ❌（模型偶尔出错）
  路径5: 25 × 0.2 = 5    ✅

  最终答案: 5（5次中出现4次，置信度80%）
```

**适用场景**：有明确答案的推理题（数学、逻辑）。
**不适用**：开放性问题（没有"对错"的创意题）。

### 2.3 RTF 框架——Prompt 设计黄金法则

**R - Role（角色）**：告诉模型它是谁
```
"你是一位有20年经验的糖水店运营专家..."
```

**T - Task（任务）**：明确要做什么
```
"...请分析以下销售数据，找出销量下滑的三个主要原因..."
```

**F - Format（格式）**：规定输出格式
```
"...请按以下格式输出：
1. 问题概述
2. 数据分析（附数字）
3. 原因分析（排名前三）
4. 改进建议（每条附预期效果）"
```

**RTF 框架的核心价值**：消除模糊性。模型最怕的不是难题，而是"你到底想要什么"不清晰。

---

## 三、代码实战

### 3.1 Prompt 策略效果对比实验

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np
import random
from collections import Counter

# matplotlib 中文字体配置
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False


# ===== 实验一：自洽性检查演示 =====
def self_consistency_demo(problem: str, correct_answer: int, 
                          accuracy: float = 0.7, num_samples: int = 8):
    """
    演示自洽性检查的完整流程
    在真实场景中，每条路径是一次 LLM API 调用（温度参数调高，增加多样性）
    """
    print(f"📝 问题：{problem}")
    print(f"🔬 对 {num_samples} 条推理路径进行采样...\n")
    
    answers = []
    for i in range(num_samples):
        # 模拟模型推理：accuracy 概率答对，其余随机错
        if random.random() < accuracy:
            answer = correct_answer
            status = "✅"
        else:
            answer = random.choice([correct_answer - 2, correct_answer - 1, 
                                    correct_answer + 1, correct_answer + 2])
            status = "❌"
        answers.append(answer)
        print(f"  路径 {i+1}: 推理中... → 答案 = {answer} {status}")
    
    # 统计：少数服从多数
    counter = Counter(answers)
    final_answer, count = counter.most_common(1)[0]
    confidence = count / num_samples * 100
    
    print(f"\n📊 答案分布：{dict(counter)}")
    print(f"🎯 最终答案：{final_answer}（出现 {count} 次，置信度 {confidence:.0f}%）")
    print(f"{'✅ 正确！' if final_answer == correct_answer else '❌ 错误'}")
    return final_answer

# 运行自洽性检查
print("=" * 60)
print("🧪 自洽性检查实验")
print("=" * 60)
self_consistency_demo("小明有25个苹果，卖掉了20%，还剩多少个？", correct_answer=20)


# ===== 实验二：Prompt 策略对比 =====
def compare_prompt_strategies():
    """对比四种 Prompt 策略在不同任务上的表现"""
    
    strategies = ['零样本\n(直接问)', '少样本\n(给示例)', '思维链\n(分步推理)', '自洽性\n(多次投票)']
    
    # 模拟数据（基于真实研究报告的趋势）
    math_accuracy = [45, 62, 78, 88]       # 数学推理：CoT和自洽性优势明显
    logic_accuracy = [40, 55, 72, 82]      # 逻辑推理：类似趋势
    fact_accuracy = [72, 75, 73, 74]       # 事实问答：差异不大，甚至CoT可能略降
    
    x = np.arange(len(strategies))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - width, math_accuracy, width, label='数学推理', color='#FF6B6B', alpha=0.85)
    bars2 = ax.bar(x, logic_accuracy, width, label='逻辑推理', color='#4ECDC4', alpha=0.85)
    bars3 = ax.bar(x + width, fact_accuracy, width, label='事实问答', color='#45B7D1', alpha=0.85)
    
    # 数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('准确率 (%)', fontsize=13)
    ax.set_title('不同 Prompt 策略在各类任务上的准确率对比', fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(strategies, fontsize=11)
    ax.legend(fontsize=12, loc='upper left')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    # 添加洞察标注
    ax.annotate('CoT 提升 33%', xy=(2, 78), xytext=(2.3, 95),
               fontsize=10, color='#FF6B6B', fontweight='bold',
               arrowprops=dict(arrowstyle='->', color='#FF6B6B'))
    ax.annotate('事实问答\n提升不大', xy=(3, 74), xytext=(3.5, 60),
               fontsize=9, color='#45B7D1',
               arrowprops=dict(arrowstyle='->', color='#45B7D1'))
    
    plt.tight_layout()
    plt.savefig('/root/learning-notebooks/第6周/ima/day4_prompt_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 Prompt 策略对比图已保存")

compare_prompt_strategies()
```

### 3.2 大模型能力雷达图

```python
# 评测维度对比：不同级别模型的能力画像
categories = ['知识理解\n(MMLU)', '数学推理\n(GSM8K)', '代码生成\n(HumanEval)', 
              '逻辑分析', '创意生成', '安全性']

N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# 模拟三个级别模型的评测数据
models = [
    ("顶级模型\n(GPT-4级)", [92, 88, 85, 82, 88, 90], '#FF6B6B'),
    ("开源模型\n(Qwen/DeepSeek)", [85, 80, 78, 75, 80, 85], '#4ECDC4'),
    ("小模型\n(7B级别)", [70, 55, 60, 62, 72, 78], '#45B7D1'),
]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

for name, scores, color in models:
    values = scores + scores[:1]
    ax.plot(angles, values, 'o-', linewidth=2, label=name, color=color, markersize=6)
    ax.fill(angles, values, alpha=0.1, color=color)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12)
ax.set_ylim(0, 100)
ax.set_title('大模型推理能力评测雷达图', fontsize=16, fontweight='bold', y=1.08)
ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第6周/ima/day4_model_radar.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 模型能力雷达图已保存")
```

### 3.3 代码要点

| 代码段 | 教学要点 |
|--------|---------|
| `self_consistency_demo()` | 模拟多次推理 → 投票 → 选最一致答案 |
| `compare_prompt_strategies()` | 可视化展示不同 Prompt 策略的效果差异 |
| `accuracy` 参数 | 模型单次准确率，越高自洽性效果越好 |
| 雷达图 | 多维度评测模型，不能只看一个指标 |

---

## 四、业务关联

### 4.1 Prompt 工程在 LangChat 中的应用

**应用一：Agent 系统提示词设计**

```python
# LangChat 中一个优秀的 Agent 系统 Prompt（RTF 框架）
SYSTEM_PROMPT = """
【角色】你是一位专业的糖水店智能客服助手，熟悉店内所有产品、价格、促销活动。

【任务】根据用户的问题，提供准确、友好、专业的回答。
- 如果用户问产品信息，请查询产品数据库
- 如果用户问价格，请精确到每杯/每份
- 如果用户问营业时间，请告知周一至周日 10:00-22:00

【格式】回答格式要求：
1. 先直接回答用户问题
2. 如有相关推荐，附在回答后面
3. 保持回复在100字以内，简洁有力

【约束】
- 不知道的信息不要编造（说"我帮您确认一下"）
- 不要讨论竞品
- 遇到投诉先道歉再解决
"""
```

**应用二：评测 Agent 效果**

在 LangChat 平台中，可以通过以下方式评测 Agent：
- 准备 100 个常见用户问题作为测试集
- 用不同 Prompt 策略运行 Agent，记录回答
- 人工评分或自动评分（与标准答案对比）
- 对比不同策略的准确率、响应时间、用户满意度

### 4.2 CoT 在企业 AI 中的实际价值

| 场景 | 不用 CoT | 用 CoT |
|------|---------|--------|
| 利润计算 | 直接给数字（经常错） | 分步计算（准确率高） |
| 故障诊断 | 直接猜原因（可能乱猜） | 逐步排除可能原因 |
| 投诉处理 | 直接给方案（可能不合适） | 先分析问题再给方案 |
| 数据分析 | 直接给结论（不可靠） | 先描述数据再分析原因 |

---

## 五、常见误区

### ❌ 误区一："CoT 万能，什么问题都该用"
**真相**：CoT 对多步推理任务（数学、逻辑）效果显著，但对简单事实问答几乎没有帮助，甚至可能降低准确率（模型"想多了"反而答错）。用不用 CoT，取决于任务复杂度。

### ❌ 误区二："少样本示例越多越好"
**真相**：研究表明，2-5 个高质量示例的效果通常最优。示例太多会：消耗 token、增加延迟、可能引入噪声。关键不是数量，而是示例的代表性和多样性。

### ❌ 误区三："自洽性检查就是问多次取平均"
**真相**：自洽性是"取众数"（最一致的答案），不是"取平均"。对于"法国首都"这种问题，答案只能是一个确定值。取平均只适用于数值型连续结果。

### ❌ 误区四："MMLU 分数高就一定好用"
**真相**：MMLU 测的是通识知识，不代表你的业务场景表现好。一个 MMLU 85 分的模型，在特定垂直领域可能不如一个经过领域微调的 70 分模型。一定要在自己的业务数据上做评测。

---

## 六、课堂练习（5分钟）

**练习一**：判断用什么 Prompt 策略

1. "什么是人工智能？" → ____ 策略
2. "帮我计算上周利润率（需要多个数据步骤）" → ____ 策略
3. "把这段话翻译成英文" → ____ 策略
4. "25的17%加上38的23%是多少？" → ____ 策略

**练习二**：用 RTF 框架写一个 Prompt

场景：让 Agent 帮糖水店写一条朋友圈营销文案。

**练习三**：思考题

自洽性检查的成本是什么？（提示：每条路径都是一次 API 调用）

---

## 七、课后测试（10分钟）

**1. MMLU 基准主要评测大模型的什么能力？**
A. 数学推理能力
B. 代码生成能力
C. 知识理解和综合应用能力（57个学科）
D. 创意写作能力

**2. 以下哪种 Prompt 技术最适合复杂的多步推理问题？**
A. 零样本直接提问
B. Chain-of-Thought（思维链）
C. 简单指令
D. 只给答案选项

**3. RTF 框架的三个字母分别代表什么？**
A. Role - Task - Format
B. Reasoning - Training - Format
C. Response - Task - Feedback
D. Role - Technology - Function

**4. 自洽性检查的核心原理是？**
A. 让模型回答更快
B. 多次采样推理路径，选出现频率最高的答案
C. 减少模型计算量
D. 增加回答字数

**5. 关于少样本示例数量，以下哪个说法正确？**
A. 越多越好
B. 2-5个高质量示例通常最优
C. 只能用1个
D. 不超过20个

---

## 八、术语表

| 英文术语 | 音标 | 中文释义 |
|----------|------|----------|
| MMLU | /em em el juː/ | 大规模多任务语言理解基准 |
| GSM8K | /dʒi es em eɪt keɪ/ | 小学数学8000题评测基准 |
| HumanEval | /ˈhjuːmən ɪˈvæljueɪt/ | 代码生成能力评测基准 |
| Zero-shot | /ˈzɪərəʊ ʃɒt/ | 零样本，不给示例直接提问 |
| Few-shot | /fjuː ʃɒt/ | 少样本，给几个示例再提问 |
| Chain-of-Thought | /tʃeɪn əv θɔːt/ | 思维链，要求展示推理过程 |
| Self-consistency | /self kənˈsɪstənsi/ | 自洽性，多次采样取最一致结果 |
| Prompt Engineering | /prɒmpt ˌendʒɪˈnɪərɪŋ/ | 提示工程，优化输入提升输出质量 |
| Ground Truth | /ɡraʊnd truːθ/ | 真实答案/标准答案 |
| Hallucination | /həˌluːsɪˈneɪʃən/ | 幻觉，模型生成的不实信息 |
| Benchmark | /ˈbentʃmɑːk/ | 基准测试 |
| Inference | /ˈɪnfərəns/ | 推理，模型生成输出的过程 |

---

## 九、参考资源

### 📹 视频推荐
1. **《ChatGPT Prompt Engineering for Developers》— 吴恩达**（约1.5小时）
   https://www.bilibili.com/video/BV1H14y1j7eR/

2. **《Let's build GPT: from scratch》— Andrej Karpathy**（约2小时）
   https://www.youtube.com/watch?v=kCc8FmEb1nY

### 📖 延伸阅读
1. **OpenAI Prompt Engineering 官方指南**
   https://developers.openai.com/api/docs/guides/prompt-engineering

2. **Learn Prompting — 全面 Prompt 教程**（支持中文）
   https://learnprompting.org/

---

> 📅 **明天预告**：Day 5 我们将进入 **Agent 开发实战与框架设计**——主流 Agent 框架怎么选？LangChain、OpenAI Agents SDK、自研框架各有什么优劣？从架构设计到状态管理到错误处理，全是工程师必备干货！
