# 第5周 Day4：推理能力评测与 Prompt 工程

> **导语**：模型回答得流畅，不代表它真的可靠。要判断它是否会推理，需要一套标准考试；要让它在业务里稳定发挥，需要把问题说清楚。这两件事分别叫**评测**和 **Prompt 工程**。今天的目标不是背榜单，而是学会用可验证的方法判断模型能力，并把模糊需求翻译成模型能执行的指令。

## 学习进度

```
W1 基础 ✅  →  W2 架构 ✅  →  W3 训练 ✅  →  W4 RAG ✅  →  W5 推理 🔵进行中
```

## 为什么需要

想象招聘收银员。只问“你会算账吗”没有意义，应该给同一批订单、折扣和退款单，看谁能算对、算快、能解释。模型评测也是这样：给模型统一题目和规则，才可以比较能力。

同样，Prompt 不是“和 AI 聊天的花话术”。它更像给新同事派活：只说“分析销售”会得到泛泛建议；说明角色、数据、目标、边界和交付格式，才可能得到能执行的结论。评测回答“它能不能”，Prompt 工程回答“怎样让它稳定地做到”。

## 核心原理详解

### 1. 三类常见基准

**MMLU（Massive Multitask Language Understanding）**：覆盖 57 个学科的选择题，类似通识高考。它主要看知识广度：法律、医学、历史、计算机都能不能答。高分说明知识面广，却不能直接证明客服体验或业务决策一定好。

**GSM8K（Grade School Math 8K）**：小学应用题集合。题目不高深，却要求正确拆解条件、列式、按顺序计算。它像“买三送一、满减叠券”的账单，最能暴露模型是否会多步推理。CoT 对这个基准通常特别有效。

**HumanEval**：给函数签名和自然语言描述，让模型写代码，再运行单元测试。它像编程面试：不是说得对就算，而是代码必须跑通。常见指标是 `pass@1`（第一次生成就通过的比例）和 `pass@k`（尝试 k 次至少一次通过的比例）。

### 2. 评测不是分数竞赛

看榜单前要问四个问题：

1. **测的是什么**：MMLU 测知识，GSM8K 测算术推理，HumanEval 测可执行代码；不能互相替代。
2. **怎么测的**：Zero-shot 是裸考；Few-shot 会先给例题；CoT 还会要求分步推理。同一模型在不同设置下分数可差很多。
3. **题是否泄露**：测试题若进入训练数据，模型可能只是记忆答案。这叫数据污染（data contamination）。
4. **和业务是否相像**：你做售后机器人，就应另建订单查询、退款规则、情绪安抚、转人工等业务集，不能只看公开榜单。

生活类比：体检报告正常，不等于能跑马拉松；公开 Benchmark 好，也不等于能完成你的真实工作流。

### 3. RTF：最实用的 Prompt 骨架

RTF 指 **Role - Task - Format**：

- **Role（角色）**：模型应以什么专业视角工作。
- **Task（任务）**：输入、目标、约束和判断标准是什么。
- **Format（格式）**：输出是 JSON、表格、步骤还是一句结论。

例如：

```text
角色：你是零售经营分析师。
任务：根据给定日销售额、成本和库存，找出异常并给出两条可执行建议；
      不足以判断时明确说明缺什么数据。
格式：输出 JSON，字段为 summary、anomalies、actions、missing_data。
```

这比“帮我分析销售”强在：角色减少口吻漂移，任务定义成功标准，格式让程序可直接解析。

### 4. 从简单到复杂的策略

- **Zero-shot**：直接提问。适合事实查询、分类、短改写。
- **Few-shot**：给 2～5 个高质量例子。适合格式固定、领域术语多的任务。
- **CoT**：要求列出已知条件、计算和结论。适合数学、规则判断、排障。
- **Self-consistency**：采样多条独立推理链，按答案投票。适合高价值但允许慢一点的决策。

关键不是“用最复杂的”。简单问题用自洽性会浪费时间和 Token；高风险财务核对只用零样本又太冒险。

## 代码实战

### 1. 配置中文可视化环境

```python
from matplotlib import font_manager  # 管理系统字体
import matplotlib.pyplot as plt      # 绘图库

# 指定服务器已安装的 Noto CJK 中文字体文件
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
# 注册字体，避免中文标题显示为方块
font_manager.fontManager.addfont(font_path)
# 读取 matplotlib 认可的字体名称
font_name = font_manager.FontProperties(fname=font_path).get_name()
# 后续图表默认使用该中文字体
plt.rcParams["font.family"] = font_name
# 防止坐标轴负号显示异常
plt.rcParams["axes.unicode_minus"] = False
```

### 2. 写一个可复用的 RTF Prompt 生成器

```python
import json


def build_rtf_prompt(role: str, task: str, output_format: str) -> str:
    """把角色、任务、输出要求拼成结构化提示词。"""
    # 用 Markdown 标题隔开不同职责，模型更容易定位约束
    return f"""## 角色
{role}

## 任务
{task}

## 输出格式
{output_format}

## 质量要求
- 只依据输入信息推断，不要编造数据。
- 计算题先核对单位和中间结果。
- 信息不足时列出缺失项。"""

prompt = build_rtf_prompt(
    role="你是门店经营数据分析师。",
    task="分析本周销售额 [12000, 11800, 15100, 9900, 14300]，识别异常日期并说明可能原因。",
    output_format='返回 JSON：{"summary":"...", "anomalies":[], "actions":[]}'
)
print(prompt)
```

逐行看：函数参数让 Prompt 可配置；`f"""..."""` 保留清晰换行；质量要求防止模型在信息不足时“自信补全”。在 LangChat 中可把这段模板放到系统提示词，把用户数据作为变量填入。

### 3. 对模型回答做基础推理质量检查

```python
import re


def inspect_reasoning(response: str) -> dict:
    """用简单规则检查回答是否包含可审阅的推理痕迹。"""
    # 匹配“第一步”“第2步”等步骤标记
    steps = re.findall(r"第[一二三四五六七八九十0-9]+步", response)
    # 找出所有数字，粗略判断是否给出计算信息
    numbers = re.findall(r"-?\d+(?:\.\d+)?", response)
    # 逻辑词不是正确性的证明，但可作为人工复核的提醒
    logic_words = ["因为", "因此", "所以", "验证", "合计", "首先", "最后"]

    return {
        "step_count": len(steps),
        "number_count": len(numbers),
        "has_logic_link": any(word in response for word in logic_words),
        "needs_human_review": len(steps) == 0 or len(numbers) == 0,
    }

answer = "第一步：奶茶利润为 3×12=36 元。第二步：果汁利润为 5×8=40 元。最后合计为 76 元。"
print(json.dumps(inspect_reasoning(answer), ensure_ascii=False, indent=2))
```

注意：这个检查器只能检查“有没有过程”，不能证明过程正确。真正的准确率需要拿标准答案比对，或调用计算器、数据库等外部工具验证。

## 可视化：比较 Prompt 策略的代价

```python
import numpy as np
import matplotlib.pyplot as plt

# 以下数值是教学模拟数据；真实项目应替换为自己的评测结果
strategies = ["零样本", "少样本", "CoT", "自洽性"]
accuracy = [64, 76, 86, 91]       # 准确率百分比
latency = [0.8, 1.2, 2.6, 4.1]    # 平均响应秒数

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
# 左图衡量正确性
axes[0].bar(strategies, accuracy, color=["#ef767a", "#7ac7c4", "#7aa6d8", "#e6b85c"])
axes[0].set_title("不同 Prompt 策略的准确率")
axes[0].set_ylabel("准确率 (%)")
axes[0].set_ylim(0, 100)
# 右图衡量等待成本
axes[1].bar(strategies, latency, color=["#ef767a", "#7ac7c4", "#7aa6d8", "#e6b85c"])
axes[1].set_title("不同 Prompt 策略的平均延迟")
axes[1].set_ylabel("秒")

for ax in axes:
    ax.grid(axis="y", alpha=0.25)
plt.tight_layout()
plt.show()
```

图的结论很朴素：准确率和成本常常一起上涨。产品设计应按风险分层：聊天欢迎语追求快，合同审阅和财务汇总追求可验证。

## 业务关联：LangChat / Agent

在 LangChat 中，可以为不同节点设置不同 Prompt：意图分类节点用短 Prompt；订单核验节点要求引用订单字段；经营分析节点使用 RTF + CoT；高风险动作前要求 Agent 输出“证据、计算、置信度、是否需要人工确认”。

一个可靠的 Agent 还应把评测接入发布流程：收集真实脱敏案例，给每例标注期望答案和关键约束；每次改 Prompt 或换模型后重跑；只有准确率、格式合规率和转人工率都达标，才发布。这样 Prompt 优化不是凭感觉，而是有回归测试的工程行为。

## 常见误区

1. **榜单第一就一定适合业务**：公开题与真实业务不同，应建立私有评测集。
2. **Prompt 越长越好**：冗长指令会稀释重点；优先写清任务、边界和格式。
3. **有推理过程就一定正确**：模型也可能编造看似顺畅的步骤，关键结论仍要工具验证。
4. **Few-shot 的例子越多越好**：例子应覆盖典型边界；太多会挤占上下文。
5. **只测平均分**：还要看最差类别、格式失败率、延迟、成本和安全拒答。

## 课堂练习

1. 为“分析咖啡店近 7 天销量并给出补货建议”写一份 RTF Prompt，明确哪些数据不足时必须追问。
2. 把“帮我算总利润”改写成 CoT Prompt，要求列出每个品类、成本、折扣和最终校验。
3. 为客服场景各设计一条 Zero-shot 和 Few-shot 指令，比较它们的长度与预期效果。

## 课后测试

**1. MMLU 主要衡量什么？**
A. 图像识别  B. 多学科知识理解  C. 语音合成  D. 数据库速度

**2. GSM8K 的主要价值是？**
A. 测翻译  B. 测多步数学推理  C. 测图片生成  D. 测网页搜索

**3. RTF 中 T 表示？**
A. Token  B. Task  C. Test  D. Tree

**4. 何时适合自洽性推理？**
A. 每条欢迎语  B. 高价值且可容忍额外延迟的判断  C. 不需要答案的问题  D. 所有请求

**5. 简答**：为什么一个模型在 Few-shot 的分数可能高于 Zero-shot？怎样避免把这种提升误解成“模型本体一定更强”？

## 术语表

| 英文 | 音标 | 中文 |
|---|---|---|
| Benchmark | /ˈbentʃmɑːk/ | 基准测试、标准化考试 |
| MMLU | /em em el juː/ | 大规模多任务语言理解 |
| GSM8K | /dʒiː es em eɪt keɪ/ | 小学数学多步推理基准 |
| HumanEval | /ˈhjuːmən ɪˈvæl/ | 代码生成评测集 |
| Prompt Engineering | /prɒmpt ˌendʒɪˈnɪərɪŋ/ | 提示工程 |
| Role | /rəʊl/ | 角色 |
| Task | /tɑːsk/ | 任务 |
| Format | /ˈfɔːmæt/ | 输出格式 |
| Zero-shot | /ˈzɪərəʊ ʃɒt/ | 零样本 |
| Few-shot | /fjuː ʃɒt/ | 少样本 |
| Ground Truth | /ɡraʊnd truːθ/ | 标准答案 |
| Data Contamination | /ˈdeɪtə kənˌtæmɪˈneɪʃən/ | 数据污染 |
| Pass@k | /pɑːs æt keɪ/ | k 次中至少一次通过的指标 |

## 参考资源

- Hendrycks et al.，《Measuring Massive Multitask Language Understanding》
- Cobbe et al.，《Training Verifiers to Solve Math Word Problems》（GSM8K）
- Chen et al.，《Evaluating Large Language Models Trained on Code》（HumanEval）
- Prompt Engineering Guide：<https://www.promptingguide.ai/>
- 建议把本文代码中的模拟数据替换为自己的脱敏测试集，并记录模型版本、Prompt 版本、温度参数和评测日期。

## 补充：搭建一个最小业务评测集

公开基准是起点，业务评测集才是上线前的安全带。建议每个业务意图至少准备三类样本：正常样本、边界样本和对抗样本。以订单客服为例：正常样本是“订单什么时候到”；边界样本是订单号缺失、订单已取消、配送跨城市；对抗样本则包括用户要求绕过退款规则、输入错误订单号、把多个问题混在一条消息里。

每条样本至少保存：`input`、`expected_intent`、`required_facts`、`forbidden_claims`、`expected_format`。评测时不要只判断“回答像不像人”，而应分别计算：意图准确率、事实引用正确率、JSON 可解析率、幻觉率、平均延迟和单次成本。这样你会发现某个 Prompt 虽然总体更会说话，却可能在订单号缺失时胡编物流状态；这比平均分下降更值得修。

```python
# 一个最小评测样本的结构示例
case = {
    "input": "订单 DD1001 还没有收到，能查一下吗？",
    "expected_intent": "物流查询",
    "required_facts": ["DD1001"],
    "forbidden_claims": ["已签收", "具体配送时间"],
    "expected_format": "json"
}

# 实际项目中应由模型调用结果和标准字段逐项比较
# 不要仅依赖关键词；关键词适合作为冒烟测试，不适合作为最终判定
```

当模型的答案涉及退款、支付、医疗、法律、账号权限等高风险事项时，评测标准必须额外加入“是否拒绝越权”“是否要求人工确认”“是否保留证据来源”。这也是 Agent 设计中最重要的一条：模型可以负责推理和建议，但不可验证的结论不能自动变成外部动作。