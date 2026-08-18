# 第5周 Day6：推理 Prompt 实验

> **导语**：Prompt 工程不能只靠“感觉这句话更好”。今天我们像做小型科学实验一样，固定题目、控制变量、记录准确率、延迟和成本，比较零样本、少样本、思维链、自洽性四种策略。最终目标不是找一个万能 Prompt，而是建立一套能重复使用的实验方法。

## 学习进度

```
W1 基础 ✅  →  W2 架构 ✅  →  W3 训练 ✅  →  W4 RAG ✅  →  W5 推理 🔵进行中
```

## 为什么需要实验

同一句“请认真思考”在不同模型、不同温度、不同题型上，效果可能完全不同。若不记录实验条件，你今天觉得有效的技巧，明天换模型就可能失效。

生活类比：想调出一杯更好喝的咖啡，不能同时改咖啡豆、研磨度、水温和时间，然后说“这个版本更好”。你要一次只改一个变量。Prompt 实验也一样：固定测试集、模型版本和采样参数，只调整一项策略，才知道提升来自哪里。

## 核心原理详解

### 1. 四种策略

**Zero-shot**：没有示例，直接提出任务。成本低、延迟短，适合简单分类、提取、改写。

**Few-shot**：提供少量输入输出示例。模型会模仿示例的格式、领域语言和判断边界。示例应覆盖典型案例和容易错的边界案例，而不是只放最简单的正例。

**Chain-of-Thought（CoT）**：要求列出已知条件、运算过程和最终结论。它给模型一张“草稿纸”，适合多步数学、逻辑、规则判断。

**Self-consistency**：对同一问题采样多次独立推理，再选择最一致的结论。它通常更准确，但最慢、最贵；适合高价值决策，不适合每一句闲聊。

### 2. 实验的控制变量

一次实验至少固定：模型版本、系统提示、温度、最大输出 Token、测试集、评分规则和工具版本。一次只改 Prompt 策略或少数明确变量。

评价不应只看准确率。还要看：
- **格式合规率**：JSON 是否能解析、字段是否完整。
- **事实正确率**：是否引用了输入或工具证据。
- **延迟**：用户等待多久。
- **成本**：输入输出 Token 和工具调用。
- **稳定性**：相同输入重复运行时是否大幅波动。

### 3. 温度和采样的作用

温度低时，模型倾向选择最可能的词，结果更稳定；温度高时，结果更多样，但也更容易跑偏。做确定性数据抽取时可用低温；做自洽性时可适度增加多样性，再让投票机制筛选答案。

不要把“多次回答不同”简单归因于模型笨。很多时候是温度、上下文、工具返回时间或隐含随机种子不同造成的。

## 代码实战

### 1. 中文字体配置

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False
```

### 2. 生成四种 Prompt 模板

```python
def build_prompts(question: str) -> dict:
    """针对同一问题构建四种实验策略，方便公平比较。"""
    return {
        # 最简单基线：没有示范和推理要求
        "zero_shot": f"请直接回答：{question}",

        # 示例要与目标题型相似，且展示期望格式
        "few_shot": f"""示例：一支笔 3 元，买 5 支。
回答：3×5=15 元。

现在回答：{question}
请只给出计算和答案。""",

        # CoT 强调可检查的中间步骤，而不是无目的地变长
        "cot": f"""解决问题：{question}
请依次写出：已知条件、计算步骤、结果验证、最终答案。""",

        # 自洽性提示要求独立思路，最后明确投票规则
        "self_consistency": f"""问题：{question}
请用三种独立思路求解；分别给出答案；比较差异后选择最一致的答案。""",
    }

question = "甲管6小时注满水池，乙管12小时注满，同时打开需要几小时？"
for name, prompt in build_prompts(question).items():
    print(f"\n## {name}\n{prompt}")
```

### 3. 记录实验结果

```python
from dataclasses import dataclass
import time

@dataclass
class Trial:
    strategy: str
    answer: str
    correct: bool
    latency_seconds: float
    input_tokens: int
    output_tokens: int


def summarize_trials(trials: list[Trial]) -> dict:
    """按策略聚合准确率、平均延迟和平均 Token。"""
    summary = {}
    for name in {t.strategy for t in trials}:
        group = [t for t in trials if t.strategy == name]
        summary[name] = {
            "accuracy": sum(t.correct for t in group) / len(group),
            "avg_latency": sum(t.latency_seconds for t in group) / len(group),
            "avg_tokens": sum(t.input_tokens + t.output_tokens for t in group) / len(group),
        }
    return summary

# 教学模拟结果；真实系统应从 API 返回的 usage 和计时器采集
trials = [
    Trial("zero_shot", "4", True, 0.8, 35, 8),
    Trial("few_shot", "4小时", True, 1.1, 95, 20),
    Trial("cot", "1/6+1/12=1/4，故4小时", True, 2.2, 70, 75),
    Trial("self_consistency", "4小时", True, 4.0, 90, 230),
]
print(summarize_trials(trials))
```

重点不是这四个教学数字，而是记录方式：每个结果同时保留策略、原始回答、正确性、延迟和 Token。没有原始回答，后续很难诊断“为什么错”。

### 4. 一个简单但安全的评分函数

```python
import re


def normalize_number(text: str) -> str | None:
    """提取回答中的最后一个数字，适合非常简单的数值题演示。"""
    values = re.findall(r"\d+(?:\.\d+)?", text)
    return values[-1] if values else None


def score_math_answer(response: str, expected: str) -> bool:
    """比较标准化后的数字；生产环境需要按任务设计更严谨的验证器。"""
    return normalize_number(response) == expected

print(score_math_answer("计算得到 4 小时", "4"))
```

不要把这个函数直接用于金融或医疗。真实业务常包含单位、四舍五入、有效区间和多个正确表达，应使用领域验证器或人工标注。

## 可视化：准确率、延迟、成本三角

```python
import numpy as np

strategies = ["零样本", "少样本", "CoT", "自洽性"]
accuracy = [0.62, 0.76, 0.88, 0.91]
latency = [0.8, 1.1, 2.2, 4.0]
tokens = [43, 115, 145, 320]

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, values, title, ylabel in zip(
    axes,
    [accuracy, latency, tokens],
    ["准确率", "平均延迟", "平均 Token"],
    ["比例", "秒", "Token"],
):
    ax.bar(strategies, values, color=["#e76f73", "#6fb9b0", "#6c9ed4", "#e1b45d"])
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.show()
```

这张图提醒我们：没有“永远最佳”的策略。产品需要的是帕累托权衡：在可接受成本和延迟下，达到所需可靠度。

## 业务关联：LangChat / Agent

对 LangChat 的问答节点，可以按意图路由实验策略：知识库检索问答使用“检索证据 + 简短回答”；订单计算使用 CoT + 计算器验证；促销方案使用 ToT 或多候选方案；退款、删库等写操作不仅要推理，还要权限检查和人工确认。

Agent 的 Prompt 实验应有版本号。建议把 Prompt、模型、参数、测试集 hash 和实验结果写入同一条记录。这样出现回归时能回答：是哪次改动让格式合规率从 98% 降到 81%？而不是只能凭记忆回退。

## 常见误区

1. **一次成功就认为 Prompt 最优**：至少在固定测试集上重复多次。
2. **只看准确率**：忽略延迟、Token 和格式失败会让线上体验变差。
3. **示例放入真实敏感数据**：Few-shot 示例也会进入模型上下文，应脱敏。
4. **让模型自己评分自己**：可做辅助信号，关键任务仍需外部验证。
5. **把 CoT 原样展示给用户**：产品可展示简洁依据；内部详细推理和敏感信息应按安全策略处理。

## 课堂练习

1. 对“抽屉有3红2白球，不放回抽两次都为红的概率”各写一份 Zero-shot、Few-shot、CoT Prompt。
2. 设计一张实验记录表，至少包含 8 个字段。
3. 若自洽性准确率只比 CoT 高 1%，但延迟高 3 倍，你会在哪些业务中仍选择它？

## 课后测试

**1. Prompt 实验最重要的原则？** A. 一次改所有变量 B. 控制变量 C. Prompt 越长越好 D. 不记录结果

**2. Few-shot 的主要作用？** A. 让模型联网 B. 用示例约束格式和模式 C. 去掉输入 D. 代替测试

**3. CoT 更适合？** A. 多步推理 B. 单词翻译 C. 无输入任务 D. 所有任务

**4. 评估线上策略还应看？** A. 只看回答长度 B. 延迟、成本、格式合规率 C. 只看模型名字 D. 只看一次结果

**5. 简答**：为什么实验记录必须保存原始回答，而不只保存“对/错”？

## 术语表

| 英文 | 音标 | 中文 |
|---|---|---|
| Prompt Template | /prɒmpt ˈtempleɪt/ | 提示模板 |
| A/B Testing | /eɪ biː ˈtestɪŋ/ | A/B 测试 |
| Latency | /ˈleɪtənsi/ | 延迟 |
| Throughput | /ˈθruːpʊt/ | 吞吐量 |
| Accuracy | /ˈækjərəsi/ | 准确率 |
| Temperature | /ˈtemprətʃə/ | 采样温度 |
| Zero-shot | /ˈzɪərəʊ ʃɒt/ | 零样本 |
| Few-shot | /fjuː ʃɒt/ | 少样本 |
| Chain-of-Thought | /tʃeɪn əv θɔːt/ | 思维链 |
| Self-consistency | /self kənˈsɪstənsi/ | 自洽性 |
| Regression Test | /rɪˈɡreʃən test/ | 回归测试 |

## 参考资源

- Wei et al., *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*
- Wang et al., *Self-Consistency Improves Chain of Thought Reasoning*
- Prompt Engineering Guide：<https://www.promptingguide.ai/>
- Weights & Biases 实验跟踪文档
- 建议先建立 30～100 条脱敏的“黄金样本”，再开始任何 Prompt 优化。

## 补充：实验报告怎么写

一次能被团队复用的实验报告应包含五部分。第一部分写**假设**，例如“给出两个边界示例可提高退款意图识别准确率”；第二部分写**方法**，包括模型版本、温度、系统提示、测试样本数和评分器；第三部分列出**结果**，同时展示平均值和失败案例；第四部分解释**局限**，例如样本量太小、测试集只覆盖中文；第五部分给出**决策**，如“保留 Few-shot 模板，但仅用于退款路由”。

失败案例比成功平均值更有价值。把失败样本按原因分桶：误解条件、忽略单位、格式损坏、编造事实、工具使用错误、过度拒答。每次只优先修一个占比最高且风险最大的桶。这样 Prompt 工程会逐渐变成可维护的质量改进，而不是反复叠加“请更仔细”“请一定正确”这类无效句子。

### 示例：为实验结果导出 CSV

```python
import csv

# 每一行对应一次模型调用；生产环境可加入 request_id 和 prompt_version
rows = [
    {"case_id": "math_001", "strategy": "cot", "correct": True, "latency": 2.1},
    {"case_id": "math_002", "strategy": "cot", "correct": False, "latency": 2.4},
]

with open("prompt_trials.csv", "w", newline="", encoding="utf-8") as file:
    # fieldnames 固定列顺序，便于后续 DataFrame 分析
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)\n```

导出后可以按策略聚合，也可以人工阅读错误样本。注意将订单号、手机号、地址、支付信息等敏感字段在写入实验日志前脱敏；日志用于改进质量，不应成为隐私泄露的新入口。