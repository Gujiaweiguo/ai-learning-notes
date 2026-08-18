# 第6周 Day 3：ReAct 模式与多 Agent 协作

> **导语**：一个 Agent 再聪明，也只是"一个人在战斗"。真正的复杂任务需要一个团队。今天我们学习 Agent 领域两大核心话题：ReAct 模式（让 Agent 学会"边想边做"）和多 Agent 协作（让多个 Agent 组队解决问题）。这就像从一个"单打独斗的英雄"进化到一支"默契配合的战队"。

---

## 📊 学习进度

```
█████████████████████████████████░░░░░░░░░░░░░░░░░░░ 52%
第1周 ✅  Python基础
第2周 ✅  AI与大模型基础
第3周 ✅  RAG检索增强生成
第4周 ✅  向量数据库与Embedding
第5周 ✅  大模型微调与部署
第6周 🔄  Agent与工具使用（Day 3/7）← 今天
```

---

## 一、为什么需要 ReAct 和多 Agent？

### 1.1 单步 Agent 的局限

昨天我们学了 Function Calling，Agent 能调用工具了。但现实中的任务往往不是"一个问题用一个工具就能解决"的：

**复杂任务示例**："帮我分析一下上周销售数据，找出销量下滑的原因，然后给团队写一份报告发邮件"

这个任务包含：
1. 查询上周销售数据 → 需要数据库工具
2. 对比历史数据找趋势 → 需要计算工具
3. 分析可能原因 → 需要推理能力
4. 写分析报告 → 需要文本生成
5. 发送邮件 → 需要邮件工具

一个 Agent 需要 **5 步**才能完成，每一步都依赖前一步的结果。这就是 ReAct 模式要解决的问题。

### 1.2 单个 Agent 的瓶颈

当任务越来越复杂，一个 Agent 会遇到：
- **工具太多**：注册了 20 个工具，LLM 选择准确率下降
- **上下文太长**：多步对话积累太多信息，超出上下文窗口
- **专业度不够**：一个 Agent 很难同时擅长销售分析和文案写作
- **错误累积**：一步错，步步错

解决方案：**多 Agent 系统**——把一个大任务拆分成多个专业 Agent，各司其职。

### 1.3 生活类比

**ReAct 就像修理水管**：
1. 先看看哪里漏水（观察）
2. 想想可能是什么原因（思考）
3. 拿扳手拧一下（行动）
4. 看看还漏不漏（观察）
5. 如果还漏，换个思路（思考→行动→观察...循环）
6. 直到修好

**多 Agent 就像医院**：
- 挂号台 Agent（分诊）→ 检查科室 Agent（化验）→ 诊断医生 Agent（分析）→ 药房 Agent（开药）
- 每个 Agent 专注自己的领域，通过传递信息协作

---

## 二、核心原理详解

### 2.1 ReAct 模式深度剖析

ReAct = **Re**asoning + **Act**ing

**核心理念**：不要让 AI 一次性给出最终答案，而是让它"想一步、做一步、看结果"。

**三步循环详解**：

**Step 1：Thought（思考）**
Agent 分析当前状态，决定下一步该做什么。
```
Thought: 用户想知道上海明天是否适合户外活动。
         我需要先查天气，然后根据天气判断是否适合。
         → 决定：调用天气查询工具
```

**Step 2：Action（行动）**
Agent 执行上一步决定的操作。
```
Action: get_weather(city="上海", date="明天")
```

**Step 3：Observation（观察）**
Agent 获取工具返回的结果，作为下一步思考的输入。
```
Observation: 上海明天小雨，温度22°C，风力3级。
```

**继续循环**：
```
Thought: 小雨天不适合户外活动，但温度适中。
         我可以建议用户改去室内活动。
         → 决定：搜索室内活动推荐
Action: search_activities(type="室内", city="上海")
Observation: 上海室内活动推荐：博物馆、美术馆、购物中心...
Thought: 信息已足够，可以给用户最终回复了。
Final Answer: 上海明天有小雨，温度22°C，不太适合户外活动。
              但温度舒适，推荐去上海博物馆、中华艺术宫等室内场所...
```

### 2.2 ReAct 的关键优势

| 对比维度 | 直接回答（无 ReAct） | ReAct 模式 |
|---------|-------------------|-----------|
| 准确率 | 容易出错，特别涉及实时信息 | 逐步验证，准确率高 |
| 可解释性 | 黑盒，不知道怎么得出答案 | 透明，每步思考可见 |
| 错误恢复 | 一步错=全错 | 可在中间步骤发现并纠正 |
| 复杂任务 | 难以处理多步骤问题 | 天然支持多步骤 |

### 2.3 多 Agent 协作模式

**模式一：流水线协作（Pipeline）**

就像工厂流水线，每个 Agent 负责一道工序，上一步输出是下一步输入：

```
用户请求 → [需求分析Agent] → [方案设计Agent] → [执行Agent] → [审核Agent] → 最终结果
```

适用场景：流程明确的任务，如订单处理、内容审核、数据处理。

**模式二：中央调度（Orchestrator-Worker）**

一个"主 Agent"统筹全局，把子任务分给不同的专业 Agent：

```
                    ┌→ [搜索Agent] ─┐
用户请求 → [主Agent] ─┤→ [计算Agent] ─┤→ [主Agent] → 整合回复
                    └→ [分析Agent] ─┘
```

适用场景：任务需要多种专业能力，如综合分析、复杂决策。

**模式三：对话式协作（Conversation）**

多个 Agent 直接对话讨论，达成共识后输出：

```
[产品经理Agent] → [技术Agent] → [测试Agent] → [产品经理Agent] → ...
```

适用场景：创意性任务、方案评审、头脑风暴。

### 2.4 多 Agent 系统的关键设计决策

**决策一：Agent 数量**
- 太少（1-2个）：和多 Agent 没什么区别
- 太多（10+个）：协调成本高，通信开销大
- 建议：3-5个专业 Agent 为佳

**决策二：通信方式**
- 直接传递：A 的输出直接给 B（高效但耦合）
- 消息总线：通过中间媒介传递（解耦但复杂）
- 共享状态：所有 Agent 读写同一个状态空间（简单但可能冲突）

**决策三：冲突处理**
- 投票机制：多个 Agent 给出不同答案，少数服从多数
- 优先级：预先定义哪个 Agent 的结论优先级更高
- 仲裁者：设一个"裁判 Agent"来解决分歧

---

## 三、代码实战

### 3.1 实现一个完整的 ReAct Agent

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any

# matplotlib 中文字体配置
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False


class ReActAgent:
    """一个完整的 ReAct Agent 实现"""
    
    def __init__(self, name="智能助手"):
        self.name = name
        self.thoughts = []      # 思考历史
        self.actions = []       # 行动历史
        self.observations = []  # 观察历史
        self.max_steps = 5      # 最大循环次数（防止死循环）
    
    def think(self, question: str, available_tools: List[str]) -> Dict:
        """思考步骤：分析问题，决定下一步"""
        # 实际项目中，这里调用 LLM 生成 Thought
        # 教学版用规则模拟
        
        thought = {
            "step": len(self.thoughts) + 1,
            "analysis": f"分析问题：{question}",
            "decision": available_tools[0] if available_tools else "直接回答",
            "reasoning": f"根据问题内容，选择工具：{available_tools[0] if available_tools else '无需工具'}"
        }
        self.thoughts.append(thought)
        return thought
    
    def act(self, tool_name: str, tool_input: str) -> Dict:
        """行动步骤：执行工具调用"""
        action = {
            "step": len(self.actions) + 1,
            "tool": tool_name,
            "input": tool_input
        }
        self.actions.append(action)
        
        # 模拟工具执行
        if tool_name == "搜索":
            result = f"搜索'{tool_input}'完成，找到3条相关信息"
        elif tool_name == "计算":
            try:
                result = f"计算结果：{eval(tool_input)}"
            except:
                result = f"计算错误：无法执行 '{tool_input}'"
        elif tool_name == "数据库查询":
            result = f"查询'{tool_input}'完成，返回5条记录"
        else:
            result = f"工具 '{tool_name}' 执行完毕"
        
        return {"action": action, "result": result}
    
    def observe(self, action_result: Dict) -> Dict:
        """观察步骤：评估行动结果"""
        observation = {
            "step": len(self.observations) + 1,
            "result": action_result["result"],
            "assessment": "信息已获取，需要继续处理" if "完成" in action_result["result"] else "信息不足"
        }
        self.observations.append(observation)
        return observation
    
    def run(self, task: str, tools: List[str]) -> str:
        """运行完整的 ReAct 循环"""
        print(f"\n{'='*60}")
        print(f"🤖 {self.name} 开始处理任务：{task}")
        print(f"🔧 可用工具：{', '.join(tools)}")
        print(f"{'='*60}")
        
        for step in range(self.max_steps):
            print(f"\n--- 第 {step+1} 轮 ---")
            
            # Step 1: Think
            thought = self.think(task if step == 0 else f"根据观察继续：{self.observations[-1]['result']}", tools)
            print(f"💭 Thought（思考）：{thought['analysis']}")
            print(f"   决策：{thought['decision']}")
            
            if thought['decision'] == "直接回答":
                final = f"基于以上分析，最终答案已生成。"
                print(f"\n✅ 最终回复：{final}")
                return final
            
            # Step 2: Act
            tool = thought['decision']
            tool_input = task if step == 0 else "继续查询"
            action_result = self.act(tool, tool_input)
            print(f"🔧 Action（行动）：调用 {tool}('{tool_input}')")
            print(f"   结果：{action_result['result']}")
            
            # Step 3: Observe
            obs = self.observe(action_result)
            print(f"👁️ Observation（观察）：{obs['assessment']}")
        
        print(f"\n⚠️ 达到最大步数 {self.max_steps}，强制结束")
        return "任务处理超时"


# 运行 ReAct Agent
agent = ReActAgent("糖水店分析助手")
agent.run("分析上周红豆沙的销量下降原因", ["搜索", "数据库查询", "计算"])
```

### 3.2 多 Agent 协作系统

```python
class SpecializedAgent:
    """专业 Agent：负责特定领域"""
    
    def __init__(self, name: str, role: str, skills: List[str]):
        self.name = name
        self.role = role
        self.skills = skills
        self.tasks_completed = 0
    
    def can_handle(self, task: str) -> bool:
        """判断是否能处理这个任务"""
        return any(skill in task for skill in self.skills)
    
    def execute(self, task: str) -> str:
        """执行任务"""
        if self.can_handle(task):
            self.tasks_completed += 1
            return f"✅ {self.name}({self.role}) 完成任务：{task}"
        return f"❌ {self.name} 无法处理：{task}"


class MultiAgentOrchestrator:
    """多 Agent 编排器：中央调度模式"""
    
    def __init__(self, name: str = "Agent编排系统"):
        self.name = name
        self.agents: List[SpecializedAgent] = []
        self.task_log = []
    
    def add_agent(self, agent: SpecializedAgent):
        """注册 Agent"""
        self.agents.append(agent)
        print(f"🤖 已注册：{agent.name}（{agent.role}）技能：{agent.skills}")
    
    def process_request(self, user_request: str) -> str:
        """处理用户请求：拆分→分配→汇总"""
        print(f"\n{'='*60}")
        print(f"👤 用户请求：{user_request}")
        print(f"{'='*60}")
        
        # 第一步：分析请求，拆分任务
        sub_tasks = self._decompose_task(user_request)
        print(f"\n📋 任务拆分：{sub_tasks}")
        
        # 第二步：分配合适的 Agent
        results = []
        for task in sub_tasks:
            best_agent = self._find_best_agent(task)
            if best_agent:
                result = best_agent.execute(task)
                print(f"   → 分配给 {best_agent.name}")
                results.append(result)
            else:
                print(f"   ⚠️ 没有合适的 Agent 处理：{task}")
                results.append(f"⚠️ 无法处理：{task}")
        
        # 第三步：汇总结果
        summary = f"\n📊 处理完成，共 {len(results)} 个子任务：\n"
        for i, r in enumerate(results, 1):
            summary += f"   {i}. {r}\n"
        
        self.task_log.append({"request": user_request, "results": results})
        print(summary)
        return summary
    
    def _decompose_task(self, request: str) -> List[str]:
        """模拟任务拆分（实际由 LLM 完成）"""
        tasks = []
        if "分析" in request or "报告" in request:
            tasks.append("搜索相关信息")
            tasks.append("查询数据库数据")
            tasks.append("计算和分析数据")
            tasks.append("生成分析报告")
        elif "客服" in request or "咨询" in request:
            tasks.append("理解用户问题")
            tasks.append("搜索知识库")
        else:
            tasks.append(request)
        return tasks
    
    def _find_best_agent(self, task: str) -> SpecializedAgent:
        """找到最适合处理该任务的 Agent"""
        for agent in self.agents:
            if agent.can_handle(task):
                return agent
        return None


# 搭建糖水店多 Agent 系统
print("🏪 搭建糖水店多 Agent 系统\n")

system = MultiAgentOrchestrator("糖水店智能系统")
system.add_agent(SpecializedAgent("搜索员小搜", "信息检索", ["搜索", "查找", "了解"]))
system.add_agent(SpecializedAgent("数据员小数", "数据查询", ["数据库", "查询", "数据"]))
system.add_agent(SpecializedAgent("分析员小分", "数据分析", ["计算", "分析", "统计"]))
system.add_agent(SpecializedAgent("撰稿员小文", "内容生成", ["生成", "报告", "写"]))

system.process_request("分析上月销售数据，生成一份经营分析报告")
```

### 3.3 代码要点解析

| 组件 | 作用 | 关键设计 |
|------|------|---------|
| `ReActAgent.think()` | 推理决策 | 实际用 LLM，教学版用规则模拟 |
| `ReActAgent.act()` | 执行操作 | 调用工具函数 |
| `ReActAgent.observe()` | 评估结果 | 判断是否需要继续循环 |
| `max_steps` | 防死循环 | 生产环境必须设置上限 |
| `MultiAgentOrchestrator` | 多Agent编排 | 中央调度模式 |
| `_decompose_task()` | 任务拆分 | LLM 的核心能力之一 |
| `_find_best_agent()` | Agent匹配 | 按技能匹配任务 |

---

## 四、可视化分析

```python
# ReAct 循环 + 多 Agent 协作 双图可视化
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# 左图：ReAct 循环
ax1 = axes[0]
ax1.set_xlim(-1.5, 1.5)
ax1.set_ylim(-1.5, 1.5)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('ReAct 推理行动循环', fontsize=14, fontweight='bold')

# 三个节点
import matplotlib.patches as mpatches
steps = [
    ("Thought\n(思考)", 0, 1, '#FF6B6B'),
    ("Action\n(行动)", 0.87, -0.5, '#4ECDC4'),
    ("Observation\n(观察)", -0.87, -0.5, '#45B7D1')
]
for text, x, y, color in steps:
    circle = mpatches.Circle((x, y), 0.35, color=color, alpha=0.7)
    ax1.add_patch(circle)
    ax1.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold', color='white')

# 循环箭头
ax1.annotate('', xy=(0.6, -0.2), xytext=(0.3, 0.7),
            arrowprops=dict(arrowstyle='->', lw=2, color='#FF6B6B', connectionstyle='arc3,rad=-0.3'))
ax1.annotate('', xy=(-0.6, -0.2), xytext=(0.5, -0.7),
            arrowprops=dict(arrowstyle='->', lw=2, color='#4ECDC4', connectionstyle='arc3,rad=-0.3'))
ax1.annotate('', xy=(0.3, 0.7), xytext=(-0.5, -0.7),
            arrowprops=dict(arrowstyle='->', lw=2, color='#45B7D1', connectionstyle='arc3,rad=-0.3'))

# 右图：多 Agent 协作网络
ax2 = axes[1]
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')
ax2.set_title('多 Agent 协作网络', fontsize=14, fontweight='bold')

# 中心：编排器
center = mpatches.Circle((5, 5), 0.6, color='#FF6B6B', alpha=0.8)
ax2.add_patch(center)
ax2.text(5, 5, '主Agent\n(编排器)', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

# 四周：专业 Agent
agents = [
    ("搜索Agent", 2, 8, '#4ECDC4'),
    ("数据Agent", 8, 8, '#45B7D1'),
    ("分析Agent", 2, 2, '#96CEB4'),
    ("生成Agent", 8, 2, '#FFEAA7'),
]
for name, x, y, color in agents:
    circle = mpatches.Circle((x, y), 0.5, color=color, alpha=0.7)
    ax2.add_patch(circle)
    ax2.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold')
    # 连接线
    ax2.plot([5, x], [5, y], 'k--', alpha=0.3, linewidth=1)

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第6周/ima/day3_react_multiagent.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 ReAct 与多 Agent 协作图已保存")
```

---

## 五、业务关联

### 5.1 LangChat 企业场景中的多 Agent

**场景一：企业智能客服中心**
```
用户："我昨天下的单还没到，而且商品有损坏，想投诉"

→ [分诊Agent] 识别两个问题：物流延迟 + 商品损坏
  → [物流Agent] 调用物流API查询 → 回复配送状态
  → [售后Agent] 调用售后系统 → 发起退换货流程
→ [汇总Agent] 整合两个Agent的回复 → 给用户统一回复
```

**场景二：糖水店运营分析**
```
管理者："分析一下这个月的经营状况，给出优化建议"

→ [数据Agent] 查销售数据库 → 获取销售数据
→ [分析Agent] 计算同比环比 → 发现红豆沙销量下降15%
→ [搜索Agent] 搜索原因 → 发现附近新开了竞品店
→ [策略Agent] 生成建议 → 建议推出新品+促销活动
→ [汇总Agent] 写成报告 → 输出完整经营分析报告
```

### 5.2 ReAct 在 AI 开发中的实际价值

| 价值点 | 说明 |
|--------|------|
| 可调试性 | 每步都有 Thought 记录，出问题能追溯 |
| 可控性 | 可以在任意步骤插入人工审核 |
| 容错性 | 中间步骤出错可以重试或换策略 |
| 透明性 | 用户能看到 Agent 的推理过程 |

---

## 六、常见误区

### ❌ 误区一："ReAct 就是个 while 循环"
**真相**：ReAct 的精髓在于 LLM 自主决定"下一步做什么"。不是预定义的流程，而是根据每步的 Observation 动态调整。如果代码里写死了执行顺序，那只是传统编程，不是 ReAct。

### ❌ 误区二："Agent 越多越强大"
**真相**：每增加一个 Agent，就增加通信成本、协调成本和出错可能性。3-5 个专业 Agent 的效果通常优于 10+ 个。关键不是数量，而是分工是否合理。

### ❌ 误区三："多 Agent 一定能解决更复杂的问题"
**真相**：如果任务本身是线性的（A→B→C），单个 Agent 用 ReAct 就能搞定。多 Agent 适合需要多种专业能力或并行处理的场景。杀鸡不用牛刀。

### ❌ 误区四："ReAct 不会出错"
**真相**：ReAct 可能陷入死循环（反复调用同一工具）、偏离主题（被中间结果带偏）、过早终止（信息不足就给答案）。`max_steps` 和结果校验是必要的保护机制。

---

## 七、课堂练习（5分钟）

**练习一**：为以下任务设计 ReAct 流程

任务："帮我查一下北京和上海的天气，比较哪个城市更适合明天出行"

请写出完整的 Thought → Action → Observation 循环。

**练习二**：设计一个多 Agent 系统

场景：一个电商平台的智能客服中心，需要处理：售前咨询、订单查询、物流跟踪、售后退换、投诉处理。

请设计：需要几个 Agent？每个负责什么？它们怎么协作？

**练习三**：思考题

ReAct 模式的 `max_steps` 设成多少合适？太小和太大各有什么问题？

---

## 八、课后测试（10分钟）

**1. ReAct 模式的正确循环顺序是？**
A. Action → Thought → Observation
B. Observation → Thought → Action
C. Thought → Action → Observation
D. Thought → Observation → Action

**2. 以下哪个是多 Agent 系统的核心优势？**
A. 运行速度更快
B. 每个 Agent 可以专注于自己的专业领域
C. 不需要 LLM 了
D. 不需要写代码了

**3. 在中央调度模式中，主 Agent 的主要职责是什么？**
A. 执行所有具体任务
B. 拆分任务、分配给子 Agent、汇总结果
C. 只负责聊天
D. 只负责日志记录

**4. ReAct 模式中设置 max_steps 的主要目的是？**
A. 提高准确率
B. 减少内存使用
C. 防止死循环和无限执行
D. 让用户等更短时间

**5. 以下哪种场景最适合使用多 Agent 而非单个 Agent？**
A. 查询天气
B. 简单问答
C. 综合经营分析报告（涉及数据、分析、写作、审核）
D. 单次计算

---

## 九、术语表

| 英文术语 | 音标 | 中文释义 |
|----------|------|----------|
| ReAct | /riˈækt/ | 推理+行动，边想边做的 Agent 模式 |
| Thought | /θɔːt/ | 思考步骤，分析当前状态并决策 |
| Action | /ˈækʃən/ | 行动步骤，执行工具调用或操作 |
| Observation | /ˌɒbzəˈveɪʃən/ | 观察步骤，获取行动结果反馈 |
| Multi-Agent | /ˈmʌlti ˈeɪdʒənt/ | 多智能体系统 |
| Orchestration | /ˌɔːkɪˈstreɪʃən/ | 编排，协调多个 Agent 协作 |
| Delegation | /ˌdelɪˈɡeɪʃən/ | 委托，主 Agent 分配子任务给子 Agent |
| Pipeline | /ˈpaɪplaɪn/ | 流水线，Agent 串行处理 |
| Reflection | /rɪˈflekʃən/ | 反思，回顾执行过程评估效果 |
| Consensus | /kənˈsensəs/ | 共识，多 Agent 达成一致 |

---

## 十、参考资源

### 📹 视频推荐
1. **《ReAct Agent 智能体教程》**（10分钟快速入门）
   https://www.bilibili.com/video/BV1QmNX6UEWN/

2. **《ReAct：协同 Agent 推理与行动》**（论文逐行解读）
   https://www.bilibili.com/video/BV1qzNAerELM/

### 📖 论文与文档
1. **ReAct: Synergizing Reasoning and Acting in Language Models**（原始论文）
   https://react-lm.github.io/

2. **ReAct Agent 终极指南**（掘金实战教程）
   https://juejin.cn/post/7518707715129688064

---

> 📅 **明天预告**：Day 4 我们将学习 **Agent 推理能力评测与 Prompt 工程**——怎么衡量一个 Agent "聪不聪明"？怎么通过 Prompt 技巧让 Agent 更聪明？MMLU、GSM8K、思维链、自洽性检查……全是面试常考的硬核知识！
