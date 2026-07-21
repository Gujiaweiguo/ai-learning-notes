# 第6周 Day 7：第六周总复习

> **导语**：六天急行军，从 Agent 概念到框架设计到代码实战，信息量巨大。今天是"串联日"——把所有知识点连成线、织成网，帮你形成完整的 Agent 知识体系。配有综合测试、实战案例分析和实战项目建议。学完这一天，你应该能够独立向别人解释"什么是 Agent、怎么开发 Agent、Agent 用在哪里"。

---

## 📊 学习进度

```
█████████████████████████████████████░░░░░░░░░░░░░░░ 56%
第1周 ✅  Python基础
第2周 ✅  AI与大模型基础
第3周 ✅  RAG检索增强生成
第4周 ✅  向量数据库与Embedding
第5周 ✅  大模型微调与部署
第6周 ✅  Agent与工具使用 ← 本周完成！🎉
第7周 ⏳  待开启
```

---

## 一、本周知识全景图

### 1.1 六天学了什么？一张图概括

```
第6周学习路线
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Day 1 🧠 Agent 基本架构
  └→ 三大核心：LLM（大脑）+ Tools（工具箱）+ Memory（记忆）
  └→ ReAct 框架：Reason → Action → Observation 循环

Day 2 🔧 Function Calling 详解
  └→ 工具定义三要素：name + description + parameters
  └→ 调用决策流程：意图识别 → 工具选择 → 参数提取
  └→ tool_choice：auto / none / required

Day 3 🔄 ReAct 模式与多 Agent 协作
  └→ ReAct 循环：边想边做，逐步逼近答案
  └→ 多 Agent 模式：流水线 / 中央调度 / 对话式
  └→ 设计决策：Agent 数量、通信方式、冲突处理

Day 4 📊 推理评测与 Prompt 工程
  └→ 三大基准：MMLU（知识）/ GSM8K（数学）/ HumanEval（代码）
  └→ 四大策略：零样本 / 少样本 / CoT / 自洽性
  └→ RTF 框架：Role + Task + Format

Day 5 🏗️ Agent 开发实战与框架设计
  └→ 核心三要素：LLM + 工具库 + 执行引擎
  └→ 状态管理：内存 → 文件 → 数据库 → 向量库
  └→ 错误处理：指数退避重试 + 降级 + 兜底
  └→ 可观测性：日志 + 追踪 + 指标
  └→ 框架对比：LangChain / OpenAI SDK / AutoGen / CrewAI / 自研

Day 6 💻 搭建 Function Calling Agent
  └→ 完整代码实战：5个工具 + Agent核心 + 多轮对话
  └→ 教学版 → 生产版的改造路径
  └→ 运行数据可视化与统计分析
```

### 1.2 核心概念关系图

```
                    ┌──────────┐
                    │   User   │ 用户提出需求
                    └────┬─────┘
                         ↓
                    ┌──────────┐
                    │   Agent  │ 智能体
                    │   Core   │ ──── 包含什么？
                    └────┬─────┘
              ┌──────────┼──────────┐
              ↓          ↓          ↓
         ┌────────┐ ┌────────┐ ┌────────┐
         │  LLM   │ │ Tools  │ │ Memory │
         │ (大脑) │ │(工具箱)│ │(记忆)  │
         └───┬────┘ └───┬────┘ └────────┘
             │          │
     ┌───────┴──────┐   │ 工具怎么调用？
     │              │   │
  ┌──┴──┐     ┌────┴───┴───┐
  │ReAct│     │ Function   │
  │模式 │     │ Calling    │
  └─────┘     └────────────┘
  边想边做     工具定义+决策+执行

  Agent 怎么评测？
  ┌─────────────────────────────┐
  │ MMLU / GSM8K / HumanEval   │ ← 三大评测基准
  │ Zero/Few-shot / CoT / SC   │ ← 四大 Prompt 策略
  └─────────────────────────────┘

  生产级需要什么？
  ┌─────────────────────────────┐
  │ 状态管理 + 错误处理 + 可观测 │
  │ 框架选择：LangChain/自研等  │
  └─────────────────────────────┘
```

---

## 二、核心知识点回顾

### 2.1 Agent 三大核心组件

**记忆方法——"大脑手套记忆法"**：
- 🧠 **LLM（大脑）**：思考、决策、推理——决定"做什么"
- 🔧 **Tools（手套/工具）**：执行操作——"动手做"
- 💾 **Memory（笔记本）**：记录历史——"记住经验"

**一句话记忆**：大脑指挥、工具干活、记忆帮忙。

### 2.2 ReAct 循环

**记忆方法——"TAO 循环"**：
- **T**hought（思考）：分析情况，决定下一步
- **A**ction（行动）：执行操作
- **O**bservation（观察）：评估结果，决定是否继续

**关键点**：不是一条路走到黑，而是每一步都评估，可以随时调整方向。

### 2.3 Function Calling 三要素

工具定义 = **N**ame（名称）+ **D**escription（描述）+ **P**arameters（参数）

**记忆方法——"NDP 法则"**：
- **N**ame：动宾结构，如 `query_order`（查订单）
- **D**escription：最重要！LLM 靠这个决定用不用这个工具
- **P**arameters：类型 + 是否必填 + 描述

**关键点**：Description 写得好，Agent 选择准确率就高。

### 2.4 Prompt 四大策略

| 策略 | 核心思想 | 适用场景 | 一句话记忆 |
|------|---------|---------|-----------|
| 零样本 | 直接问 | 简单常识题 | "直接开口" |
| 少样本 | 给示例 | 格式化输出 | "先示范一遍" |
| 思维链CoT | 分步推理 | 数学/逻辑题 | "一步步算给我看" |
| 自洽性 | 多次投票 | 有标准答案的题 | "多算几次取多数" |

**效果排序**（推理类任务）：自洽性 > CoT > 少样本 > 零样本

### 2.5 状态管理策略

```
短期记忆 → Python dict/list（内存，重启丢失）
中期记忆 → Redis（快速读写，TTL 自动过期）
长期记忆 → PostgreSQL + 向量库（持久化，可检索）
```

**记忆方法——"短中长法则"**：对话用内存、用户用缓存、知识用数据库。

### 2.6 错误处理策略

```
网络超时 → 指数退避重试（1s→2s→4s）
参数错误 → 不重试，反馈给 LLM 修正
服务不可用 → 降级到备选方案
全部失败 → 人工兜底
```

**关键原则**：参数错误不重试（因为同样的输入会得到同样的错误），其他暂时性错误才重试。

---

## 三、综合测试（20分钟）

### 选择题（每题2分，共20分）

**1. Agent 的三大核心组件是什么？**
A. 前端 + 后端 + 数据库
B. LLM + Tools + Memory
C. 训练 + 推理 + 部署
D. 输入 + 处理 + 输出

**2. ReAct 模式中，一个完整循环的顺序是？**
A. Observation → Thought → Action
B. Action → Observation → Thought
C. Thought → Action → Observation
D. Thought → Observation → Action

**3. Function Calling 工具定义中，最影响 LLM 工具选择准确率的要素是？**
A. 工具名称
B. 工具描述（description）
C. 参数类型
D. 返回值格式

**4. 一个学生做数学题时先写"第一步... 第二步... 第三步..."，这对应什么 Prompt 策略？**
A. 零样本
B. 少样本
C. 思维链（CoT）
D. 自洽性

**5. GSM8K 基准测试主要评测大模型的什么能力？**
A. 代码生成能力
B. 知识广度
C. 数学推理能力
D. 创意写作能力

**6. 多 Agent 系统中，"中央调度"模式的核心角色是？**
A. 主 Agent（Orchestrator）
B. 数据库
C. 前端界面
D. 消息队列

**7. 以下哪种错误类型不适合自动重试？**
A. 网络超时
B. 服务暂时不可用
C. 参数格式错误
D. 限流（429）

**8. 生产级 Agent 的可观测性三支柱是？**
A. 日志 + 追踪 + 指标
B. 代码 + 测试 + 文档
C. CPU + 内存 + 磁盘
D. 速度 + 质量 + 成本

**9. RTF 框架中，"R" 代表什么？**
A. Response
B. Reasoning
C. Role
D. Routing

**10. 以下关于 CoT 的说法，正确的是？**
A. CoT 对所有任务都有正面效果
B. CoT 只对多步推理任务有明显提升
C. CoT 会显著降低响应速度
D. CoT 只适用于数学题

### 简答题（每题5分，共20分）

**Q1**：请用自己的话解释 Agent 和传统 LLM 聊天机器人的核心区别。（至少说出3点）

**Q2**：设计一个糖水店智能客服 Agent 的工具集。列出至少4个工具，写出名称和描述。

**Q3**：解释"指数退避重试"的原理，并说明为什么参数错误不应该用这种策略。

**Q4**：如果让你为一个电商平台设计多 Agent 系统，你会设几个 Agent？各负责什么？它们怎么协作？

---

## 四、实战案例分析

### 案例：糖水店全链路智能系统

**业务需求**：Jason 的糖水店需要一个 AI 系统，覆盖从客户咨询到订单完成的全流程。

**系统设计**：

```
客户消息
    ↓
┌──────────────────────────────────┐
│        主 Agent（编排器）          │
│  分析意图 → 分配子任务 → 汇总     │
└───────┬──────────┬──────────┬────┘
        ↓          ↓          ↓
   ┌─────────┐┌─────────┐┌─────────┐
   │客服Agent││库存Agent││数据Agent│
   │         ││         ││         │
   │知识查询  ││查库存    ││查销售    │
   │FAQ回答   ││下采购单  ││算利润    │
   │投诉处理  ││供应商管理││生成报表  │
   └─────────┘└─────────┘└─────────┘
```

**涉及的本周知识点**：

| 知识点 | 在案例中的应用 |
|--------|--------------|
| Agent 三大组件 | LLM做决策、Tools连接业务系统、Memory记住客户偏好 |
| Function Calling | 客服Agent调用FAQ查询、库存Agent调用库存API |
| ReAct 模式 | 处理复杂投诉时，先查询订单→分析问题→给出方案 |
| 多Agent协作 | 客服+库存+数据三个Agent分工协作 |
| Prompt 工程 | 用CoT处理复杂的退款金额计算 |
| 状态管理 | Redis存当前对话，PostgreSQL存客户历史 |
| 错误处理 | 库存API超时时降级到缓存数据 |

---

## 五、代码复习要点

### 5.1 最小 Agent 代码结构

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


class MiniAgent:
    """最小 Agent：理解了这段代码，就理解了 Agent 的本质"""
    
    def __init__(self):
        self.tools = {}        # 工具注册表
        self.history = []      # 记忆
    
    def register_tool(self, name, func, description):
        """注册工具"""
        self.tools[name] = {"func": func, "desc": description}
    
    def think_act_observe(self, user_input):
        """ReAct 循环"""
        # Think: 决策（实际用 LLM）
        tool_name = self._decide(user_input)
        
        if tool_name is None:
            return "直接回答"  # 不需要工具
        
        # Act: 执行
        result = self.tools[tool_name]["func"]()
        
        # Observe: 评估
        response = f"根据工具结果：{result}"
        
        # 记忆
        self.history.append({"input": user_input, "response": response})
        
        return response
    
    def _decide(self, text):
        """工具选择决策（教学版用规则，生产版用LLM）"""
        for name, tool in self.tools.items():
            if any(w in text for w in tool["desc"].split("/")):
                return name
        return None


# 运行
agent = MiniAgent()
agent.register_tool("weather", lambda: "晴天25°C", "天气/温度")
agent.register_tool("calc", lambda: "42", "计算/等于/多少")

print(agent.think_act_observe("今天天气怎么样？"))
print(agent.think_act_observe("3乘以14等于多少？"))
```

### 5.2 可视化复习

```python
# 本周知识掌握度自评雷达图
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

topics = ['Agent概念\n(Day1)', 'Function\nCalling\n(Day2)', 'ReAct+\n多Agent\n(Day3)',
          '推理评测+\nPrompt\n(Day4)', '框架设计\n(Day5)', '代码实战\n(Day6)']
# 自评分数（满分100），请根据自己的理解程度调整
scores = [85, 80, 75, 80, 70, 75]

N = len(topics)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]
values = scores + scores[:1]

ax.plot(angles, values, 'o-', linewidth=2, color='#FF6B6B', markersize=8)
ax.fill(angles, values, alpha=0.15, color='#FF6B6B')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(topics, fontsize=12)
ax.set_ylim(0, 100)
ax.set_title('第六周知识掌握度自评', fontsize=16, fontweight='bold', y=1.08)
ax.grid(True, alpha=0.3)

# 标注分数
for angle, score in zip(angles[:-1], scores):
    ax.text(angle, score + 5, f'{score}', ha='center', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第6周/ima/day7_self_assessment.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 自评雷达图已保存。分数低于70的板块建议回看对应Day的内容。")
```

---

## 六、常见误区总汇

本周六个误区最容易踩，务必牢记：

| # | 误区 | 真相 |
|---|------|------|
| 1 | "Agent = ChatGPT + 插件" | Agent 是完整的决策-执行-记忆系统 |
| 2 | "工具描述随便写" | Description 是 LLM 选择工具的唯一依据 |
| 3 | "Agent 越多越好" | 3-5个专业 Agent 通常优于 10+ 个 |
| 4 | "CoT 万能" | CoT 只对推理类任务有明显提升 |
| 5 | "参数错误也重试" | 同输入→同错误，应反馈给 LLM 修正 |
| 6 | "日志以后再加" | 可观测性必须在架构阶段考虑 |

---

## 七、下一步学习建议

### 7.1 如果你想深入 Agent 开发

1. **实战项目**：选一个真实业务场景，从零搭建一个 Agent（推荐：智能客服、数据分析助手、自动化工作流）
2. **学习框架**：深入一个框架（LangChain 或 LangGraph），不要浅尝辄止
3. **阅读论文**：ReAct 论文、Toolformer、Reflexion 等经典 Agent 论文

### 7.2 如果你想在企业中落地 Agent

1. **从小开始**：先做一个单工具的简单 Agent（如FAQ查询），验证可行性
2. **重视工程**：Agent 的核心不是 AI，而是工程——错误处理、状态管理、性能优化
3. **关注成本**：每次 LLM 调用都花钱，做好缓存和短路优化

### 7.3 如果你想准备面试

Agent 相关高频面试题：
- 解释 ReAct 模式的工作原理
- Function Calling 的完整流程
- 如何设计多 Agent 系统
- CoT 为什么能提升推理准确率
- 生产级 Agent 需要考虑哪些问题
- LangChain vs 自研框架的取舍

---

## 八、术语表（本周汇总）

| 英文术语 | 音标 | 中文释义 |
|----------|------|----------|
| Agent | /ˈeɪdʒənt/ | 智能体，自主感知、决策、执行的 AI |
| LLM | /el el em/ | 大语言模型 |
| Function Calling | /ˈfʌŋkʃən ˈkɔːlɪŋ/ | 函数调用 |
| ReAct | /riˈækt/ | 推理+行动循环模式 |
| Thought | /θɔːt/ | 思考步骤 |
| Action | /ˈækʃən/ | 行动步骤 |
| Observation | /ˌɒbzəˈveɪʃən/ | 观察步骤 |
| Tool Use | /tuːl juːz/ | 工具使用 |
| Memory | /ˈmeməri/ | 记忆能力 |
| Multi-Agent | /ˈmʌlti ˈeɪdʒənt/ | 多智能体系统 |
| Orchestration | /ˌɔːkɪˈstreɪʃən/ | 编排协调 |
| MMLU | /em em el juː/ | 多任务理解基准 |
| GSM8K | /dʒi es em eɪt keɪ/ | 数学推理基准 |
| Zero-shot | /ˈzɪərəʊ ʃɒt/ | 零样本 |
| Few-shot | /fjuː ʃɒt/ | 少样本 |
| Chain-of-Thought | /tʃeɪn əv θɔːt/ | 思维链 |
| Self-consistency | /self kənˈsɪstənsi/ | 自洽性 |
| Prompt Engineering | /prɒmpt ˌendʒɪˈnɪərɪŋ/ | 提示工程 |
| Exponential Backoff | /ˌekspəˈnenʃəl ˈbækɒf/ | 指数退避重试 |
| Observability | /əbˌzɜːvəˈbɪləti/ | 可观测性 |

---

## 九、参考资源汇总

### 📹 精选视频
1. 《从 LLM 到 Agent Skill》— 32分钟入门
   https://www.bilibili.com/video/BV1E7wtzaEdq
2. 《Function Calling 技术详解》— 13集系列
   https://www.bilibili.com/video/BV1SJm8YtETd/
3. 《ReAct Agent 智能体教程》— 10分钟速通
   https://www.bilibili.com/video/BV1QmNX6UEWN/
4. 《Prompt Engineering — 吴恩达》— 1.5小时系统课
   https://www.bilibili.com/video/BV1H14y1j7eR/

### 📖 必读论文与文档
1. ReAct 论文：https://arxiv.org/abs/2210.03629
2. LangChain 官方文档：https://docs.langchain.com
3. OpenAI Function Calling 指南：https://developers.openai.com/api/docs/guides/function-calling
4. Lilian Weng Agent 综述：https://lilianweng.github.io/posts/2023-06-23-agent/

### 💻 代码资源
1. LangChain 仓库：https://github.com/langchain-ai/langchain
2. Awesome AI Agents：https://github.com/e2b-dev/awesome-ai-agents
3. Learn Prompting：https://learnprompting.org/

---

## 十、本周总结

**一周一句话**：

> Agent = LLM + Tools + Memory + ReAct。让 AI 从"只会说"变成"能做事"。

**知识层次**：
```
概念层（Day 1）：Agent 是什么？为什么需要？
    ↓
机制层（Day 2-3）：Function Calling 怎么调？ReAct 怎么转？
    ↓
优化层（Day 4）：怎么评测？怎么用 Prompt 提升效果？
    ↓
工程层（Day 5-6）：怎么搭框架？怎么处理错误？怎么写代码？
    ↓
整合层（Day 7）：串联所有知识，形成完整能力体系
```

**自我检查清单**：
- [ ] 我能用自己的话解释 Agent 是什么
- [ ] 我能说出 Agent 的三大核心组件
- [ ] 我能画出 ReAct 的循环流程图
- [ ] 我能写出一个基本的工具定义（JSON Schema）
- [ ] 我能说出 Function Calling 的三个步骤
- [ ] 我理解零样本、少样本、CoT、自洽性的区别
- [ ] 我能说出至少三种状态管理策略
- [ ] 我知道指数退避重试的原理
- [ ] 我能说出至少两个主流 Agent 框架
- [ ] 我能跑通 Day 6 的代码并理解每一行

全部 ✅ → 恭喜，你已经具备了 Agent 开发的基础能力！
有 ❌ → 回看对应 Day 的教材，重点复习。

---

> 🎓 **下周预告**：第7周我们将进入新的主题。Agent 是工具，学会用工具之后，下一步就是解决真实业务问题。无论是 LangChat 企业 AI 平台、糖水店智能系统，还是其他业务场景，把 AI 能力转化为业务价值，才是最终目标。继续加油！💪
