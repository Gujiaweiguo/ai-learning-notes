# 第5周 Day5：高级推理技巧与 Agent 推理框架

> **导语**：会回答问题的模型像一本会说话的百科；会规划、查数据、调用工具、检查结果的模型才更像能办事的同事。今天把高级推理技巧放进 Agent 框架：自洽性负责交叉验证，元认知负责识别不确定性，反事实负责比较“如果……会怎样”，工具组合负责把想法变成可验证的行动。

## 学习进度

```
W1 基础 ✅  →  W2 架构 ✅  →  W3 训练 ✅  →  W4 RAG ✅  →  W5 推理 🔵进行中
```

## 为什么需要

现实任务不是一道孤立的数学题。比如“下周要不要给某饮品降价”：需要查询销量、计算毛利、看库存、估计竞品、比较不同方案，最后还要说明风险。若模型只凭一句直觉回答，它可能忽略成本或把不确定的预测说成事实。

高级推理的目标不是让模型输出更长，而是让每一步都可检查。生活中做重大决定会列方案、算账、找人复核、预演失败情形；Agent 也应该这样工作。

## 核心原理详解

### 1. 自洽性验证：多条路算同一个答案

自洽性（Self-consistency）让模型为同一问题生成多条独立推理路径，再按最终答案或证据一致性投票。它像会计对账：销售系统、支付系统和库存系统都指向同一个数字，可信度就高；三者不同，则不能急着报结果。

步骤是：生成候选 → 提取结论 → 聚合投票 → 对少数结论追溯原因。它适合数学、规则、结构化判断，不适合把“多数模型都这么说”误当成事实来源。

### 2. 元认知监控：知道自己不知道

元认知（Meta-cognition）是“对思考的思考”。一个成熟 Agent 应在执行前后问自己：信息够吗？假设是什么？结论能被工具验证吗？失败代价多大？

例如用户说“帮我算本月利润”，模型若只拿到销售额，应明确指出还缺采购成本、平台抽佣、退款和人工成本。把“无法判断”说清楚不是能力弱，而是可靠性的表现。

### 3. 反事实推理：比较如果不这样做

反事实（Counterfactual）不是预测未来的魔法，而是明确假设后的方案比较。例如“如果降价 10%，销量增加 20%，毛利会怎样？”它要求先写明假设，再计算结果，并说明假设可能失效的条件。

生活类比：买雨伞前不是断言“明天一定下雨”，而是比较“下雨且没伞”“下雨且带伞”“不下雨但带伞”的成本。业务分析也要区分事实、假设和推导。

### 4. 工具组合推理

Agent 的核心循环可以概括为：

```text
观察输入 → 规划子任务 → 选择工具 → 执行工具 → 校验结果 → 生成答复/继续行动
```

工具是 Agent 的手脚：数据库查事实，计算器做精确运算，检索系统找依据，代码解释器画图，工单系统创建任务。模型负责决定“用什么、何时用、结果是否足够”。

重要原则：工具结果是证据，模型文本是解释。涉及金额、库存、订单状态时，应优先引用工具返回的字段，而不是让模型凭语言记忆补全。

## 代码实战

### 1. 中文字体与依赖

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np

# 载入中文字体，避免图表标题乱码
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False
```

### 2. 一个可审计的自洽性选择器

```python
from collections import Counter


def select_consistent_answer(paths: list[dict]) -> dict:
    """按候选答案的出现次数投票，并保留审计信息。"""
    # paths 的每个元素包含 method、reasoning、answer 三个字段
    answers = [item["answer"] for item in paths]
    counts = Counter(answers)       # 统计每个结论出现次数
    winner, votes = counts.most_common(1)[0]  # 取票数最高的答案

    # 仅保留支持最终结论的路径，便于回查证据
    evidence = [p for p in paths if p["answer"] == winner]
    return {
        "answer": winner,
        "vote_ratio": votes / len(paths),
        "evidence": evidence,
        "needs_review": votes / len(paths) < 0.67,
    }

paths = [
    {"method": "逐项加总", "reasoning": "36 + 40 + 30", "answer": 106},
    {"method": "按品类表求和", "reasoning": "奶茶36、果汁40、咖啡30", "answer": 106},
    {"method": "心算", "reasoning": "可能漏算一项", "answer": 96},
]
print(select_consistent_answer(paths))
```

这里的 `needs_review` 很关键：投票不是万能裁判。若三条路径各不相同，或多数路径来自同一错误数据源，Agent 应调用计算器/数据库复核，或升级人工处理。

### 3. 反事实定价分析

```python
def counterfactual_price(base_price: float, base_units: int,
                         unit_cost: float, discount: float,
                         volume_change: float) -> dict:
    """在明确假设下，比较降价前后的收入和毛利。"""
    # 原始收入、原始毛利
    old_revenue = base_price * base_units
    old_profit = (base_price - unit_cost) * base_units

    # 假设：降价 discount，同时销量变化 volume_change
    new_price = base_price * (1 - discount)
    new_units = round(base_units * (1 + volume_change))
    new_revenue = new_price * new_units
    new_profit = (new_price - unit_cost) * new_units

    return {
        "old_profit": old_profit,
        "new_profit": new_profit,
        "profit_change": new_profit - old_profit,
        "assumption": f"降价{discount:.0%}，销量变化{volume_change:.0%}",
    }

result = counterfactual_price(20, 1000, 9, discount=0.10, volume_change=0.25)
print(result)
```

逐行要点：函数把假设显式作为参数；`old_profit` 和 `new_profit` 采用同一公式；结果必须带回 `assumption`，防止用户把情景结果误读为事实预测。

### 4. 极简 Agent 推理框架

```python
class StoreAgent:
    """示例：规划工具、保存证据、在不确定时停止自动化。"""

    def __init__(self):
        # 工具注册表：真实系统中这些函数可对应 API 或数据库查询
        self.tools = {
            "sales": self.query_sales,
            "inventory": self.query_inventory,
            "calculator": self.calculate,
        }

    def query_sales(self, period: str) -> dict:
        return {"period": period, "revenue": 12000, "units": 860}

    def query_inventory(self, sku: str) -> dict:
        return {"sku": sku, "stock": 95, "daily_sales": 18}

    def calculate(self, expression: str) -> dict:
        # 生产环境不要使用 eval；应使用受限计算器服务
        return {"expression": expression, "result": "由安全计算工具返回"}

    def plan(self, task: str) -> list[str]:
        # 这里用规则模拟规划；实际可由 LLM 输出受 JSON Schema 约束的计划
        if "补货" in task:
            return ["inventory", "sales"]
        return ["sales"]

    def run(self, task: str, **kwargs) -> dict:
        plan = self.plan(task)       # 第一步：得到工具计划
        evidence = {}                # 第二步：保存每次工具输出
        for tool_name in plan:
            tool = self.tools[tool_name]
            if tool_name == "inventory":
                evidence[tool_name] = tool(kwargs.get("sku", "默认SKU"))
            else:
                evidence[tool_name] = tool(kwargs.get("period", "本周"))

        # 第三步：不把证据丢掉，回答中可引用这些字段
        return {"task": task, "plan": plan, "evidence": evidence}

agent = StoreAgent()
print(agent.run("请判断是否需要补货", sku="柠檬茶", period="近7天"))
```

这个例子故意把“计划”和“证据”分开保存。真实 Agent 还应增加权限检查、超时、重试、日志、人工确认和工具输出校验。

## 可视化：推理路径评分

```python
methods = ["直接回答", "路径A", "路径B", "路径C"]
scores = [0.48, 0.86, 0.91, 0.62]  # 教学模拟的综合可靠度
colors = ["#e67e73", "#79b7d5", "#62b5a4", "#e3b55a"]

plt.figure(figsize=(9, 5))
bars = plt.bar(methods, scores, color=colors)
plt.title("不同推理路径的验证得分")
plt.ylabel("得分（0-1）")
plt.ylim(0, 1)
plt.grid(axis="y", alpha=0.25)
for bar, score in zip(bars, scores):
    plt.text(bar.get_x() + bar.get_width()/2, score + 0.02, f"{score:.2f}", ha="center")
plt.tight_layout()
plt.show()
```

分数只能作为调度信号，不能伪装成真实概率。若评分模型本身不可靠，就必须用规则、外部事实或人工复核校准它。

## 业务关联：LangChat / Agent

LangChat 的典型链路可以设计为：用户请求进入 → 意图与风险分级 → 推理模型生成计划 → Agent 调工具取得事实 → 验证器检查字段与规则 → 输出建议或发起人工审批。对“查库存”这类只读动作，自动化程度可以较高；对“退款”“改价”“发券”等外部写入，必须在真正执行前展示证据和确认信息。

对于经营决策，把反事实结果输出成“方案 A/B/C + 假设 + 预期收益 + 风险”。不要把单一预测包装成保证。这样管理者才能决定接受哪种风险，而不是被模型的语言流畅度误导。

## 常见误区

1. **多条路径一定更准确**：路径若共享同一错误前提，投票仍会错。
2. **置信度就是概率**：模型自报 90% 不等于真实 90%，需用历史数据校准。
3. **反事实等于预测**：反事实依赖假设，必须同时说明假设和适用范围。
4. **工具调用越多越智能**：无必要调用会增加成本、延迟和泄露面；按任务最小化工具集。
5. **Agent 可以自行执行一切操作**：高风险写操作应有权限、幂等、审计和人工确认。

## 课堂练习

1. 为“是否给草莓饮品降价 10%”列出三个反事实假设，并说明每个假设需要哪些数据验证。
2. 为库存补货 Agent 画出“查询—判断—建议—确认—执行”的流程，标记哪些节点不可自动执行。
3. 让三条独立路径计算同一个折扣题；如果答案为 96、106、106，系统应如何输出并说明原因？

## 课后测试

**1. 自洽性推理的主要目的？** A. 让回答更长 B. 多路径交叉验证 C. 去掉工具 D. 随机选择答案

**2. 元认知监控最重要的行为？** A. 永远自信 B. 识别信息缺口与不确定性 C. 忽略异常 D. 重复提问

**3. 反事实分析必须包含？** A. 绝对保证 B. 明确假设 C. 更多形容词 D. 随机数字

**4. Agent 工具输出应被当作？** A. 可审计证据 B. 不重要文本 C. 永远正确 D. 可直接丢弃

**5. 简答**：为什么“调用工具后再回答”通常比“模型直接猜”更可靠？请写出一个仍可能出错的环节。

## 术语表

| 英文 | 音标 | 中文 |
|---|---|---|
| Self-consistency | /self kənˈsɪstənsi/ | 自洽性验证 |
| Meta-cognition | /ˌmetə kɒɡˈnɪʃən/ | 元认知，对思考的思考 |
| Counterfactual | /ˌkaʊntəˈfæktʃuəl/ | 反事实推理 |
| Tool Use | /tuːl juːs/ | 工具调用 |
| Planning | /ˈplænɪŋ/ | 规划 |
| Reflection | /rɪˈflekʃən/ | 反思 |
| Evidence | /ˈevɪdəns/ | 证据 |
| Confidence Score | /ˈkɒnfɪdəns skɔː/ | 置信度得分 |
| Scenario Analysis | /sɪˈnɑːriəʊ əˈnæləsɪs/ | 情景分析 |
| Risk Assessment | /rɪsk əˈsesmənt/ | 风险评估 |
| Human-in-the-loop | /ˈhjuːmən ɪn ðə luːp/ | 人工在环 |

## 参考资源

- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*
- Wang et al., *Self-Consistency Improves Chain of Thought Reasoning*
- Pearl, *The Book of Why*（因果与反事实入门）
- LangChain Agent 文档与 OpenAI function calling 文档
- 上线前请为每个工具写清输入 Schema、权限范围、失败处理和审计字段。

## 补充：Agent 的失败处理清单

真正的生产 Agent 必须预先设计失败路径。工具超时时，不能假装查到了结果；工具返回空数据时，要区分“确实没有记录”和“查询条件错误”；模型计划不合法时，应拒绝执行而非猜测参数。一个实用的最小状态机可以是：`planned → executing → verified → awaiting_confirmation → completed`，任何异常都进入 `failed` 或 `needs_review`，并留下请求 ID、工具参数摘要和错误原因。

这套状态不仅方便排错，也能防止重复扣款、重复发券等幂等性事故。换句话说，推理负责提出下一步，工程约束负责确保下一步即使失败也可控、可追溯。