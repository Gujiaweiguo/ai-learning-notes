# 第6周 Day 1：LLM Agent 基本架构

> **导语**：如果你之前学的大模型只是一个"只会说话的嘴巴"，那么 Agent 就是给它装上了"大脑""双手"和"记忆"。从今天开始，我们进入 AI 最激动人心的领域——让大模型真正"做事"。

---

## 📊 学习进度

```
████████████████████████████████░░░░░░░░░░░░░░░░░░░░ 50%
第1周 ✅  Python基础
第2周 ✅  AI与大模型基础
第3周 ✅  RAG检索增强生成
第4周 ✅  向量数据库与Embedding
第5周 ✅  大模型微调与部署
第6周 🔄  Agent与工具使用 ← 今天
```

---

## 一、为什么我们需要 Agent？

### 1.1 传统 LLM 的天花板

想象一下：你问大模型"今天北京天气怎么样？"，它会怎么说？它可能会说"我无法获取实时天气数据"。这就好比你雇了一个知识渊博的顾问，但他被关在一个没有窗户、没有手机的房间里——再聪明也没用。

传统大模型的三大局限：
- **知识截止**：训练数据有截止日期，不知道今天发生了什么
- **无法执行**：不能帮你发邮件、查数据库、操作文件
- **无状态记忆**：每次对话都是"金鱼记忆"，不能积累经验

### 1.2 Agent 打破了什么限制？

Agent（智能体）= LLM + 工具 + 记忆 + 自主决策

用一个生活类比来理解：

| 类比 | 传统LLM | LLM Agent |
|------|---------|-----------|
| 角色 | 闭门造车的教授 | 带着工具箱的工程师 |
| 能力 | 只能口头回答 | 能查资料、用工具、动手做 |
| 记忆 | 金鱼记忆（7秒） | 有笔记本，能记住经验 |
| 自主性 | 问什么答什么 | 能自己拆解任务、分步执行 |

**一句话总结**：Agent 就是给大模型装上了"手脚"和"记忆"，让它从一个只会聊天的系统，变成一个能解决实际问题的智能助手。

### 1.3 真实业务痛点驱动

以 LangChat 企业 AI 平台为例：
- 客户问"我的订单到哪了？"——LLM 答不了，但 Agent 可以调用物流 API
- 用户问"这个月销售额多少？"——LLM 不知道，但 Agent 可以查数据库
- 管理者说"帮我给VIP客户群发优惠信息"——LLM 做不到，但 Agent 可以调用消息推送工具

---

## 二、核心原理详解

### 2.1 Agent 的三大核心组件

Agent 不是一个单一的东西，而是三个组件协同工作的系统：

**🧠 组件一：LLM（大脑）**

LLM 是 Agent 的决策中枢。它负责：
- **理解意图**：用户说"外面冷吗"，LLM 要理解为"查询当前天气温度"
- **制定计划**：把"帮我订一张明天去上海的机票"拆解为多个步骤
- **选择工具**：根据任务需求，从工具箱中选合适的工具
- **生成回复**：整合工具返回的结果，生成人类可读的回复

**🔧 组件二：Tools（工具箱）**

工具是 Agent 与外部世界交互的接口。常见工具类型：
- **信息获取类**：天气API、股票API、搜索引擎、数据库查询
- **执行操作类**：发邮件、发短信、创建日历事件、文件操作
- **计算处理类**：数学计算、数据分析、文本翻译、图片生成
- **业务系统类**：CRM操作、ERP查询、订单管理、库存检查

**💾 组件三：Memory（记忆）**

记忆让 Agent 具备持续学习和上下文感知能力：
- **短期记忆**：当前对话的上下文（最近几轮对话）
- **长期记忆**：用户偏好、历史交互、学到的经验教训
- **工作记忆**：当前任务的中间状态和中间结果

### 2.2 工作流程：ReAct 框架

ReAct = Reasoning（推理） + Acting（行动）

这是 Agent 最经典的工作模式，简单说就是"想一步、做一步、看结果、再想下一步"。

**生活类比——做一道菜**：
1. **思考(Reason)**：我要做番茄炒蛋 → 需要番茄、鸡蛋、油
2. **行动(Action)**：打开冰箱查看 → 发现有番茄但没鸡蛋
3. **观察(Observe)**：鸡蛋缺货，需要买
4. **思考(Reason)**：去楼下超市买鸡蛋
5. **行动(Action)**：出门买鸡蛋
6. **观察(Observe)**：买到了，回家
7. **思考(Reason)**：现在可以开始做了
8. ……循环直到菜做好

ReAct 的核心价值：**不是一条路走到黑，而是根据每一步的结果灵活调整**。

### 2.3 Agent vs 传统编程——本质区别

```python
# 传统编程：写死所有规则
def handle_order(order_type):
    if order_type == "退款":
        return process_refund()
    elif order_type == "换货":
        return process_exchange()
    else:
        return "未知操作"  # ← 遇到新情况就傻眼

# Agent 编程：动态决策
def agent_handle(user_message):
    # LLM 自己分析意图、选择工具、执行操作
    intent = llm.analyze(user_message)
    tool = llm.select_tool(intent, available_tools)
    result = tool.execute()
    response = llm.summarize(result)
    return response  # ← 能处理没见过的情况
```

**核心区别**：传统编程是"穷举所有可能"，Agent 编程是"让 AI 自己判断该怎么做"。

---

## 三、代码实战

### 3.1 搭建一个最小 Agent

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np

# matplotlib 中文字体配置（必加！）
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False


# ===== 第一步：定义工具 =====
# Agent 的工具本质上就是 Python 函数，加上一段描述
# 这段描述是给 LLM 看的，让它知道什么时候该用这个工具

def check_weather(city: str) -> str:
    """查询指定城市的天气信息"""
    # 实际项目中这里调用天气 API
    weather_db = {"北京": "晴天 25°C", "上海": "多云 28°C", "广州": "雷阵雨 30°C"}
    return weather_db.get(city, f"暂无{city}的天气数据")


def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expression)  # 教学用，生产环境不要用 eval
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


# ===== 第二步：工具注册表 =====
# 把工具的"说明书"告诉 Agent
# 就像新员工入职，先给他一本工具使用手册

TOOL_REGISTRY = {
    "check_weather": {
        "function": check_weather,                          # 实际函数
        "description": "查询城市天气，输入城市名称",          # 给 LLM 的描述
        "parameters": {"city": "string"}                    # 参数说明
    },
    "calculate": {
        "function": calculate,
        "description": "数学计算，输入表达式如 '2+3*4'",
        "parameters": {"expression": "string"}
    }
}


# ===== 第三步：Agent 核心 =====
class SimpleAgent:
    """最小可用的 Agent 实现"""
    
    def __init__(self, tools: dict):
        self.tools = tools       # 注册工具
        self.history = []        # 对话历史（记忆组件）
    
    def _decide_tool(self, user_input: str):
        """模拟 LLM 的工具选择决策"""
        # 实际项目中，这里会调用 LLM API
        # 我们用关键词匹配来模拟这个决策过程
        if "天气" in user_input:
            # 提取城市名（简化版）
            for city in ["北京", "上海", "广州"]:
                if city in user_input:
                    return "check_weather", {"city": city}
            return "check_weather", {"city": "北京"}  # 默认
        elif any(w in user_input for w in ["计算", "等于", "多少", "+", "-"]):
            import re
            match = re.search(r'[\d\+\-\*/\.\(\)\s]+', user_input)
            if match:
                return "calculate", {"expression": match.group().strip()}
        return None, None  # 不需要工具
    
    def chat(self, user_input: str) -> str:
        """Agent 的对话入口"""
        print(f"\n👤 用户：{user_input}")
        
        # 第一步：决策（Reason）
        tool_name, args = self._decide_tool(user_input)
        
        if tool_name:
            # 第二步：执行（Action）
            tool_fn = self.tools[tool_name]["function"]
            result = tool_fn(**args)
            print(f"🔧 工具调用：{tool_name}({args}) → {result}")
            
            # 第三步：整合回复（Observe & Respond）
            response = f"根据查询结果：{result}"
        else:
            response = f"我收到了你的消息：{user_input}（当前没有匹配的工具）"
        
        print(f"🤖 Agent：{response}")
        
        # 记录到历史（Memory）
        self.history.append({"user": user_input, "agent": response})
        return response


# ===== 第四步：运行 Agent =====
agent = SimpleAgent(TOOL_REGISTRY)
agent.chat("北京今天天气怎么样？")
agent.chat("帮我计算 128 * 45 等于多少")
agent.chat("你好，你是谁？")
```

### 3.2 代码逐行解析

| 代码行 | 作用 | 为什么这样写 |
|--------|------|-------------|
| `TOOL_REGISTRY` | 工具注册表 | 统一管理所有工具，方便扩展 |
| `_decide_tool()` | 工具选择 | 模拟 LLM 的决策过程，实际用 API |
| `self.history` | 对话记忆 | 让 Agent 有上下文感知能力 |
| `tool_fn(**args)` | 动态调用 | 根据工具名动态执行对应函数 |

---

## 四、可视化分析

```python
# Agent 能力对比图：传统AI vs LLM Agent
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 传统 AI 能力雷达
categories = ['回答问题', '文本生成', '翻译', '摘要', '任务规划', '工具调用']
traditional_scores = [85, 80, 75, 70, 20, 10]
agent_scores = [90, 85, 80, 75, 80, 90]

x = np.arange(len(categories))
width = 0.35

bars1 = axes[0].bar(x - width/2, traditional_scores, width, 
                     label='传统AI', color='#FF9999', alpha=0.8)
bars2 = axes[0].bar(x + width/2, agent_scores, width, 
                     label='LLM Agent', color='#66B2FF', alpha=0.8)

axes[0].set_ylabel('能力评分', fontsize=12)
axes[0].set_title('传统AI vs LLM Agent 能力对比', fontsize=14, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(categories, rotation=45, ha='right')
axes[0].legend()
axes[0].set_ylim(0, 100)
axes[0].grid(axis='y', alpha=0.3)

# Agent 三大组件重要性
components = ['LLM（大脑）\n决策推理', 'Tools（工具箱）\n执行能力', 'Memory（记忆）\n上下文感知']
importance = [40, 35, 25]
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
wedges, texts, autotexts = axes[1].pie(importance, labels=components, colors=colors,
                                         autopct='%1.1f%%', startangle=90,
                                         textprops={'fontsize': 11})
axes[1].set_title('Agent 三大核心组件', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第6周/ima/day1_agent_overview.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 图表已保存")
```

---

## 五、业务关联：LangChat / 企业 AI

### 5.1 糖水店 Agent 应用场景

Jason 经营糖水店，Agent 能帮什么忙？

**场景一：智能客服**
- 顾客问"红豆沙还有吗？" → Agent 调用库存查询工具 → 返回实时库存
- 顾客问"你们几点关门？" → Agent 查询营业时间 → 直接回答
- 顾客问"帮我下单一碗杨枝甘露" → Agent 调用下单系统 → 确认订单

**场景二：运营辅助**
- "这个月卖了多少碗绿豆沙？" → Agent 查销售数据库 → 生成报表
- "红豆快没了，帮我联系供应商" → Agent 调用采购系统 → 发送订单

**场景三：多Agent协作**
- 接单Agent → 库存Agent → 厨房Agent → 配送Agent，全链路自动化

### 5.2 企业 AI Agent 的价值

| 指标 | 传统方式 | Agent 方式 | 提升 |
|------|---------|-----------|------|
| 客服响应时间 | 3-5分钟 | 10秒内 | 95%↓ |
| 订单处理效率 | 人工逐条 | 批量自动 | 10x↑ |
| 7×24小时服务 | 需要倒班 | 天然支持 | 100% |
| 知识积累速度 | 靠老师傅 | 自动学习 | 不可比 |

---

## 六、常见误区

### ❌ 误区一："Agent 就是 ChatGPT 加个插件"
**真相**：Agent 是一个完整系统，包含决策、执行、记忆、反馈的闭环。插件只是工具的一种形式，Agent 的核心在于"自主决策"——它决定什么时候用工具、用哪个工具、怎么用。

### ❌ 误区二："Agent 什么都能做"
**真相**：Agent 的能力受限于工具集和 LLM 的推理能力。没有定义好的工具，Agent 就是个"无米之炊"。而且 LLM 会"幻觉"，可能做出错误决策。生产环境必须有错误处理和人工兜底。

### ❌ 误区三："Agent 不需要编程，对话就行了"
**真相**：虽然 Agent 的交互方式是对话，但背后需要大量工程工作：工具开发、API 集成、状态管理、错误处理、性能优化、安全防护。Agent 开发是 20% 的 AI + 80% 的工程。

### ❌ 误区四："ReAct 是唯一的 Agent 模式"
**真相**：ReAct 只是最经典的模式之一。还有 Plan-and-Execute（先规划再执行）、Tree of Thoughts（树形思维）、Reflection（反思模式）等多种框架，各有适用场景。

---

## 七、课堂练习（5分钟）

**练习一**：识别 Agent 组件

场景：一个智能客服 Agent，能根据用户问题查询订单状态、推荐产品、处理退款。

请回答：这个场景中——
- LLM（大脑）负责什么？ → ____
- Tools（工具）有哪些？ → ____
- Memory（记忆）需要记住什么？ → ____

**练习二**：设计 ReAct 流程

任务："帮我查一下明天上海的天气，如果下雨就提醒我带伞"

请写出完整的 ReAct 循环（思考→行动→观察→...）。

---

## 八、课后测试（10分钟）

**1. Agent 的三大核心组件是什么？**
A. 前端 + 后端 + 数据库
B. LLM + Tools + Memory
C. 输入 + 处理 + 输出
D. 训练 + 推理 + 部署

**2. ReAct 框架的正确顺序是？**
A. Action → Reason → Observe
B. Observe → Reason → Action
C. Reason → Action → Observe
D. Reason → Observe → Action

**3. 以下哪个不是 Agent 相比传统 LLM 的优势？**
A. 能调用外部工具
B. 能获取实时信息
C. 训练成本更低
D. 具备记忆能力

**4. 在糖水店场景中，"查询库存"属于 Agent 的哪个组件？**
A. LLM（大脑）
B. Tools（工具箱）
C. Memory（记忆）
D. 以上都不是

**5. 传统编程和 Agent 编程的核心区别是？**
A. 编程语言不同
B. Agent 用 GPU，传统编程用 CPU
C. 传统编程写死规则，Agent 动态决策
D. Agent 不需要写代码

---

## 九、术语表

| 英文术语 | 音标 | 中文释义 |
|----------|------|----------|
| Agent | /ˈeɪdʒənt/ | 智能体，能自主感知、决策、执行的 AI 系统 |
| Autonomy | /ɔːˈtɒnəmi/ | 自主性，自己决定做什么的能力 |
| Perception | /pəˈsepʃən/ | 感知，Agent 获取外界信息的能力 |
| Reasoning | /ˈriːzənɪŋ/ | 推理，分析问题并制定方案 |
| Action Space | /ˈækʃən speɪs/ | 动作空间，Agent 可以选择的所有操作 |
| Tool Use | /tuːl juːz/ | 工具使用，调用外部工具完成任务 |
| Memory | /ˈmeməri/ | 记忆，Agent 保存历史信息的能力 |
| Planning | /ˈplænɪŋ/ | 规划，制定多步骤行动方案 |
| ReAct | /riˈækt/ | 推理+行动，边想边做的 Agent 模式 |
| Observation | /ˌɒbzəˈveɪʃən/ | 观察，获取工具执行后的反馈 |
| Environment | /ɪnˈvaɪrənmənt/ | 环境，Agent 所处的操作空间 |
| Policy | /ˈpɒləsi/ | 策略，什么状态下做什么的规则 |

---

## 十、参考资源

### 📹 视频推荐
1. **《从 LLM 到 Agent Skill，一期视频带你打通底层逻辑！》**（32分钟，138万播放）
   https://www.bilibili.com/video/BV1E7wtzaEdq

2. **《LLM大模型入门：AI Agent 核心知识点》**（约25小时系列，23万播放）
   https://www.bilibili.com/video/BV11nSjB2ErQ

### 📖 论文与文档
1. **ReAct: Synergizing Reasoning and Acting in Language Models**（Yao et al., 2022）
   https://arxiv.org/abs/2210.03629

2. **LangChain 官方文档 — Agent 概览**
   https://docs.langchain.com/oss/python/langchain/overview

### 💻 代码实践
1. **LangChain 官方仓库**（含 Agent 模块源码与示例）
   https://github.com/langchain-ai/langchain

2. **LLM Powered Autonomous Agents — Lilian Weng**（Agent 领域必读综述）
   https://lilianweng.github.io/posts/2023-06-23-agent/

---

> 📅 **明天预告**：Day 2 我们将深入 **Function Calling 详解**，学习 Agent 到底是怎么"打电话"给外部工具的——工具定义的三要素、LLM 的调用决策逻辑、参数提取机制，全是干货！
