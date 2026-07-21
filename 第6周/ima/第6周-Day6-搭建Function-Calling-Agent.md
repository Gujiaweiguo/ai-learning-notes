# 第6周 Day 6：搭建 Function Calling Agent

> **导语**：学了五天理论，今天"真刀真枪"写代码！我们从零开始搭建一个完整的 Function Calling Agent——定义工具、实现执行层、构建 Agent 核心、多轮对话测试。这不是"看一遍就过"的教程，而是可以反复对照练习的代码参考。每个模块都有详细注释，每一步都解释"为什么这样写"。

---

## 📊 学习进度

```
████████████████████████████████████░░░░░░░░░░░░░░░░ 55%
第1周 ✅  Python基础
第2周 ✅  AI与大模型基础
第3周 ✅  RAG检索增强生成
第4周 ✅  向量数据库与Embedding
第5周 ✅  大模型微调与部署
第6周 🔄  Agent与工具使用（Day 6/7）← 今天
```

---

## 一、今天要搭建什么？

### 1.1 目标 Agent 架构

```
用户输入
    ↓
┌─────────────────────────────────────┐
│          Agent Core                  │
│   (对话管理 + LLM决策循环)            │
└──────────┬──────────────────────────┘
           ↓ LLM 判断：需要工具吗？
      ┌────┴────┐
     是          否
      ↓           ↓
┌──────────┐   直接回答
│  Tool    │   返回用户
│ Registry │
└────┬─────┘
     ↓
  执行工具函数
     ↓
  获取结果
     ↓
  结果返回 LLM
     ↓
  生成最终回复
```

### 1.2 功能清单

今天搭建的 Agent 具备以下能力：
- ✅ 5个工具（天气、计算、知识库、股票、通知）
- ✅ 自动意图识别和工具选择
- ✅ 参数提取和验证
- ✅ 多轮对话（上下文感知）
- ✅ 工具调用日志和统计
- ✅ 可视化运行数据

### 1.3 生活类比

搭建一个 Agent 就像**开一家智能客服店**：
- **工具注册** = 在服务台上放好各种服务手册
- **Agent核心** = 店长，决定由谁处理客户需求
- **工具执行** = 具体员工执行操作
- **对话历史** = 客户档案，让服务更个性化
- **日志统计** = 运营报表，分析哪些服务最常用

---

## 二、核心原理回顾

### 2.1 Function Calling 的完整循环

昨天我们学了框架设计理论，今天落地到代码：

```
Step 1: 接收用户消息
Step 2: LLM 分析意图（需要工具吗？需要哪个？）
Step 3: LLM 提取参数（从自然语言中提取结构化数据）
Step 4: 执行工具（调用函数）
Step 5: 获取结果（工具返回数据）
Step 6: LLM 整合回复（把工具结果变成用户友好的语言）
Step 7: 返回用户（完成一轮交互）
```

### 2.2 教学版 vs 生产版

今天我们写的是**教学版**（用规则模拟 LLM 决策），但代码结构设计成可以无缝切换到生产版（接入真实 LLM API）。

```python
# 教学版（今天写的）
def decide_tool(self, user_message):
    if "天气" in user_message:
        return "get_weather", {"city": "北京"}

# 生产版（只需替换这一个方法）
def decide_tool(self, user_message):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}],
        tools=self.tools_schema
    )
    # 从 LLM 响应中解析工具名和参数
    return tool_name, arguments
```

---

## 三、代码实战（完整可运行）

### Step 1：环境配置

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np
import json
import re
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

# matplotlib 中文字体配置（必加！）
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False
print(f"✅ 环境就绪，使用字体: {font_name}")
```

### Step 2：工具定义

```python
# ===== 工具定义层 =====
# 每个工具包含两部分：
#   1. SCHEMA：给 LLM 看的"说明书"（名称、描述、参数定义）
#   2. FUNCTION：实际执行的 Python 函数

# --- 模拟数据 ---
WEATHER_DATA = {
    "北京": {"temp": 32, "humidity": 45, "condition": "晴", "wind": "北风3级"},
    "上海": {"temp": 28, "humidity": 75, "condition": "多云", "wind": "东南风2级"},
    "广州": {"temp": 35, "humidity": 80, "condition": "雷阵雨", "wind": "南风4级"},
    "深圳": {"temp": 33, "humidity": 78, "condition": "多云转晴", "wind": "西南风2级"},
    "杭州": {"temp": 30, "humidity": 65, "condition": "阴", "wind": "东风1级"},
}

KNOWLEDGE_BASE = {
    "退货": "退货流程：1.联系客服 2.提供订单号 3.等待审核（1-3工作日）4.安排退货",
    "会员": "会员权益：金卡会员享9折优惠、免费配送；银卡会员享95折优惠",
    "营业": "营业时间：周一至周五 9:00-21:00，周末 10:00-22:00",
    "支付": "支付方式：微信支付、支付宝、银行卡、现金。满1000元支持分期",
    "产品": "主打产品：红豆沙(12元)、杨枝甘露(18元)、双皮奶(15元)、绿豆沙(10元)",
}

STOCK_DATA = {
    "AAPL": {"name": "苹果", "price": 195.50, "change": 2.3},
    "TSLA": {"name": "特斯拉", "price": 267.80, "change": -5.1},
    "600519": {"name": "贵州茅台", "price": 1688.00, "change": 1.5},
}


# --- 工具函数 ---
def get_weather(city: str) -> str:
    """查询指定城市的当前天气信息"""
    if city in WEATHER_DATA:
        w = WEATHER_DATA[city]
        return f"{city}：{w['condition']}，温度{w['temp']}°C，湿度{w['humidity']}%，{w['wind']}"
    return f"暂无{city}的天气数据"

def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"

def search_knowledge(query: str) -> str:
    """搜索知识库"""
    for key, val in KNOWLEDGE_BASE.items():
        if key in query:
            return val
    return f"未找到关于'{query}'的信息"

def get_stock_price(symbol: str) -> str:
    """查询股票价格"""
    sym = symbol.upper()
    if sym in STOCK_DATA:
        s = STOCK_DATA[sym]
        trend = "↑" if s["change"] > 0 else "↓"
        return f"{s['name']}({sym})：${s['price']} {trend}{abs(s['change'])}%"
    return f"未找到股票代码 {symbol}"

def send_notification(phone: str, message: str) -> str:
    """发送短信通知"""
    return f"短信已发送至 {phone}，内容：{message[:30]}..."


# --- 工具 Schema（给 LLM 看的说明书）---
TOOLS_SCHEMA = [
    {
        "name": "get_weather",
        "description": "查询指定城市的当前天气信息，包括温度、湿度、天气状况和风力",
        "function": get_weather,
        "parameters": {"city": "str（城市名称，如'北京'）"}
    },
    {
        "name": "calculate",
        "description": "执行数学计算，支持加减乘除、幂运算、括号等",
        "function": calculate,
        "parameters": {"expression": "str（数学表达式）"}
    },
    {
        "name": "search_knowledge",
        "description": "搜索知识库，查找产品信息、政策文档、常见问题等",
        "function": search_knowledge,
        "parameters": {"query": "str（搜索关键词）"}
    },
    {
        "name": "get_stock_price",
        "description": "查询股票实时价格和涨跌信息",
        "function": get_stock_price,
        "parameters": {"symbol": "str（股票代码，如'AAPL'）"}
    },
    {
        "name": "send_notification",
        "description": "发送短信通知给指定手机号",
        "function": send_notification,
        "parameters": {"phone": "str（手机号）", "message": "str（通知内容）"}
    }
]

print(f"✅ 已注册 {len(TOOLS_SCHEMA)} 个工具")
for t in TOOLS_SCHEMA:
    print(f"   🔧 {t['name']}: {t['description'][:25]}...")
```

### Step 3：Agent 核心

```python
class FunctionCallingAgent:
    """完整的 Function Calling Agent 实现"""
    
    def __init__(self, tools: list):
        self.tools = {t["name"]: t for t in tools}
        self.history: List[Dict] = []        # 对话历史
        self.tool_call_count = 0             # 工具调用计数
        self.tool_usage = {}                 # 各工具使用次数
    
    def _decide_tool(self, user_message: str) -> Optional[tuple]:
        """
        模拟 LLM 的工具选择决策。
        实际项目中，替换为 LLM API 调用。
        
        返回：(tool_name, arguments_dict) 或 None（不需要工具）
        """
        msg = user_message
        
        # 规则1：天气相关
        if any(w in msg for w in ["天气", "温度", "下雨", "晴", "几度"]):
            city = "北京"  # 默认
            for c in WEATHER_DATA:
                if c in msg:
                    city = c
                    break
            return ("get_weather", {"city": city})
        
        # 规则2：计算相关
        if any(w in msg for w in ["计算", "等于", "加", "减", "乘", "除", "多少"]):
            # 提取数学表达式
            match = re.search(r'[\d\+\-\*/\.\(\)\s]+', msg)
            if match:
                expr = match.group().strip()
                if len(expr) > 1:
                    return ("calculate", {"expression": expr})
        
        # 规则3：知识查询
        if any(w in msg for w in ["退货", "会员", "营业", "支付", "产品", "怎么"]):
            return ("search_knowledge", {"query": msg})
        
        # 规则4：股票查询
        if any(w in msg for w in ["股票", "股价", "涨", "跌", "行情"]):
            # 提取股票代码
            for sym in STOCK_DATA:
                if sym.lower() in msg.lower() or STOCK_DATA[sym]["name"] in msg:
                    return ("get_stock_price", {"symbol": sym})
            match = re.search(r'[A-Za-z]{1,5}|\d{6}', msg)
            if match:
                return ("get_stock_price", {"symbol": match.group()})
        
        # 规则5：发送通知
        if any(w in msg for w in ["通知", "短信", "发消息"]):
            phone_match = re.search(r'\d{11}', msg)
            phone = phone_match.group() if phone_match else "13800138000"
            return ("send_notification", {"phone": phone, "message": msg})
        
        return None  # 不需要工具
    
    def chat(self, user_message: str, verbose: bool = True) -> str:
        """处理一条用户消息"""
        print(f"\n{'='*60}")
        print(f"👤 用户：{user_message}")
        
        # 记录用户消息
        self.history.append({"role": "user", "content": user_message})
        
        # Step 1: 决策（Reason）
        decision = self._decide_tool(user_message)
        
        if decision is None:
            # LLM 认为不需要工具，直接回答
            response = self._generate_direct_response(user_message)
            if verbose:
                print(f"🤖 Agent（直接回答，无工具调用）")
        else:
            tool_name, args = decision
            
            if verbose:
                print(f"🧠 决策：调用工具 {tool_name}")
                print(f"📝 参数：{json.dumps(args, ensure_ascii=False)}")
            
            # Step 2: 执行工具（Action）
            tool_fn = self.tools[tool_name]["function"]
            try:
                result = tool_fn(**args)
            except Exception as e:
                result = f"工具执行出错：{e}"
            
            if verbose:
                print(f"🔧 执行结果：{result}")
            
            # Step 3: 整合回复（Observe & Respond）
            response = self._format_response(tool_name, result, args)
            
            # 记录工具调用
            self.tool_call_count += 1
            self.tool_usage[tool_name] = self.tool_usage.get(tool_name, 0) + 1
            self.history.append({"role": "tool", "name": tool_name, 
                                "content": result, "args": args})
        
        # 记录 Agent 回复
        self.history.append({"role": "assistant", "content": response})
        
        if verbose:
            print(f"💬 回复：{response}")
        
        return response
    
    def _generate_direct_response(self, message: str) -> str:
        """直接回答（不使用工具）"""
        if "你好" in message or "你是谁" in message:
            return "你好！我是智能助手，可以帮你查天气、做计算、查知识库、看股票行情等。请问有什么可以帮您的？"
        return f"我收到了你的消息：「{message}」。让我想想怎么帮你..."
    
    def _format_response(self, tool_name: str, result: str, args: dict) -> str:
        """将工具返回结果格式化为用户友好的回复"""
        if tool_name == "get_weather":
            return f"🌤️ {result}"
        elif tool_name == "calculate":
            return f"🧮 {result}"
        elif tool_name == "search_knowledge":
            return f"📋 {result}"
        elif tool_name == "get_stock_price":
            return f"📈 {result}"
        elif tool_name == "send_notification":
            return f"📨 {result}"
        return result
    
    def stats(self):
        """打印运行统计"""
        print(f"\n{'='*60}")
        print(f"📊 Agent 运行统计")
        print(f"{'='*60}")
        print(f"总消息数：{len(self.history)}")
        print(f"工具调用次数：{self.tool_call_count}")
        print(f"工具使用分布：")
        for tool, count in sorted(self.tool_usage.items(), key=lambda x: -x[1]):
            bar = "█" * count
            print(f"  {tool:20s} {bar} ({count})")
```

### Step 4：单轮对话测试

```python
# 创建 Agent 实例
agent = FunctionCallingAgent(TOOLS_SCHEMA)

# 测试不同类型的请求
test_cases = [
    "北京今天天气怎么样？",                    # → get_weather
    "帮我算一下 (128 + 256) * 3 等于多少",     # → calculate
    "我想了解一下退货政策",                     # → search_knowledge
    "查一下苹果公司的股价",                     # → get_stock_price
    "你好，请问你是谁？",                      # → 直接回答
    "用短信通知客户13800138000，订单已发货",     # → send_notification
]

print("🧪 单轮对话测试")
print("=" * 60)

for msg in test_cases:
    agent.chat(msg)

agent.stats()
```

### Step 5：多轮对话测试

```python
# 多轮对话场景：Agent 需要记住上下文
print("\n\n🔄 多轮对话演示")
print("=" * 60)

conversation = [
    "广州今天天气怎么样？",                      # 查广州天气
    "那杭州呢？",                               # 上文提到查天气，这里省略了"天气"
    "帮我算一下，广州35度和杭州30度相差多少度",    # 基于前两轮结果做计算
    "好的，帮我发微信通知同事，广州天气比较好，建议去广州出差",
]

for msg in conversation:
    agent.chat(msg)

agent.stats()
```

### Step 6：可视化运行数据

```python
# Agent 运行数据可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：工具使用分布
tools_used = list(agent.tool_usage.keys())
usage_counts = list(agent.tool_usage.values())
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

if tools_used:
    wedges, texts, autotexts = axes[0].pie(
        usage_counts, labels=tools_used, colors=colors[:len(tools_used)],
        autopct='%1.0f%%', startangle=90,
        textprops={'fontsize': 11}
    )
    axes[0].set_title('工具调用分布', fontsize=14, fontweight='bold')
else:
    axes[0].text(0.5, 0.5, '暂无工具调用', ha='center', va='center', fontsize=14)
    axes[0].set_title('工具调用分布', fontsize=14)

# 右图：消息类型统计
msg_types = {'user': 0, 'assistant': 0, 'tool': 0}
for msg in agent.history:
    role = msg['role']
    msg_types[role] = msg_types.get(role, 0) + 1

axes[1].bar(msg_types.keys(), msg_types.values(), 
            color=['#42A5F5', '#66BB6A', '#FFA726'], alpha=0.85)
axes[1].set_ylabel('消息数量', fontsize=12)
axes[1].set_title('对话消息类型分布', fontsize=14, fontweight='bold')
for i, (k, v) in enumerate(msg_types.items()):
    axes[1].text(i, v + 0.3, str(v), ha='center', fontsize=14, fontweight='bold')
axes[1].set_ylim(0, max(msg_types.values()) * 1.3)

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第6周/ima/day6_agent_stats.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 Agent 运行数据图已保存")
```

---

## 四、从教学版到生产版

### 4.1 需要改什么？

| 模块 | 教学版 | 生产版 |
|------|--------|--------|
| 工具决策 | 关键词匹配 | LLM API（GPT/Qwen） |
| 参数提取 | 正则表达式 | LLM 自动提取 |
| 错误处理 | try-except | 指数退避重试 + 降级 |
| 状态管理 | 内存 list | Redis/PostgreSQL |
| 日志追踪 | print() | 结构化日志 + Tracing |
| 工具执行 | 同步调用 | 异步 + 超时控制 |

### 4.2 生产版伪代码

```python
# 生产版 Agent 核心伪代码
class ProductionAgent:
    
    async def chat(self, user_message: str) -> str:
        # 1. 记录对话（Redis）
        await self.redis.lpush(f"chat:{self.session_id}", user_message)
        
        # 2. 调用 LLM 做工具决策（带超时）
        try:
            llm_response = await asyncio.wait_for(
                self.llm.chat(user_message, tools=self.tools_schema),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            return "抱歉，处理超时，请稍后重试"
        
        # 3. 如果 LLM 决定调用工具
        if llm_response.tool_calls:
            tool_call = llm_response.tool_calls[0]
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # 4. 参数验证
            if not self._validate_params(tool_name, args):
                # 反馈给 LLM 让它修正
                return await self.chat(f"参数格式错误，请重新提取")
            
            # 5. 执行工具（带重试）
            result = await self.executor.execute(
                tool_name, args, 
                self.tools[tool_name]["function"],
                max_retries=3
            )
            
            # 6. 把结果送回 LLM 整合回复
            final_response = await self.llm.chat(
                f"工具{tool_name}的结果是：{result}，请用自然语言总结给用户"
            )
            return final_response
        
        # 7. 不需要工具，直接返回 LLM 回复
        return llm_response.content
```

---

## 五、业务关联

### 5.1 糖水店实战场景

**场景：多轮对话处理客户需求**

```
👤 用户：红豆沙还有吗？
🤖 Agent：[调用 check_inventory] 红豆沙当前库存充足（50份），欢迎下单！

👤 用户：那来两碗，多少钱？
🤖 Agent：[调用 calculate] 两碗红豆沙 = 12×2 = 24元。

👤 用户：好的，用微信支付
🤖 Agent：[调用 process_payment] 微信支付链接已发送，请扫码支付24元。

👤 用户：帮我发短信告诉朋友来吃糖水
🤖 Agent：[调用 send_notification] 短信已发送！
```

**Agent 的价值**：一次对话完成了库存查询、价格计算、支付处理、消息通知——用户不需要打开四个不同的系统。

### 5.2 LangChat 平台对接

在 LangChat 企业平台中，今天的代码对应：
- **工具定义** → LangChat 的 Tool Manager 模块
- **Agent核心** → LangChat 的 Agent Engine
- **对话历史** → LangChat 的 Session Manager
- **日志统计** → LangChat 的 Analytics 模块

---

## 六、常见误区

### ❌ 误区一："教学版够用了，直接上生产"
**真相**：教学版缺少错误处理、超时控制、并发管理、持久化存储。生产环境第一天就会出问题。

### ❌ 误区二："工具越多，Agent 越强"
**真相**：每多一个工具，LLM 的选择准确率就降低一些。精简工具集，保持每个工具的描述清晰明确，比堆工具数量重要得多。

### ❌ 误区三："LLM 提取的参数直接用就行"
**真相**：必须做参数验证！LLM 可能提取出 `{"city": "北京的天气"}`（把多余文字放进了参数）、`{"phone": "138001380000"}`（多了一位数）。参数验证是安全底线。

### ❌ 误区四："对话历史无限保留"
**真相**：对话历史会消耗 token（=花钱+变慢）。需要设置最大轮数或最大 token 数，超出后做摘要或截断。

---

## 七、课堂练习（5分钟）

**练习一**：添加一个新工具

为 Agent 添加一个 `get_time` 工具，能查询当前时间。需要：
1. 写工具函数
2. 写工具 Schema
3. 在 Agent 的 `_decide_tool` 中添加规则

**练习二**：处理参数缺失

当用户说"帮我查天气"但没说城市时，Agent 应该怎么处理？（提示：提示用户补充，或用默认值）

**练习三**：思考题

如果 Agent 连续调用了 3 次同一个工具都失败了，应该怎么处理？

---

## 八、课后测试（10分钟）

**1. Agent 架构中，Tool Registry 的作用是什么？**
A. 存储对话历史
B. 注册和管理所有可用工具
C. 调用 LLM API
D. 生成最终回复

**2. 在教学版 Agent 中，`_decide_tool` 方法模拟的是什么？**
A. 工具执行过程
B. LLM 的工具选择决策
C. 用户意图理解
D. 结果整合回复

**3. 多轮对话中，Agent 能理解"那杭州呢？"的上下文，靠的是什么？**
A. 工具定义
B. 对话历史（self.history）
C. LLM 的推理能力
D. 参数验证

**4. 生产版相比教学版，最关键的增加是什么？**
A. 更多的工具
B. 错误处理（重试、超时、降级）
C. 更好看的 UI
D. 更多的 Prompt

**5. 参数验证为什么重要？**
A. 让代码更长
B. 防止 LLM 提取的错误参数导致工具执行异常
C. 提高运行速度
D. 减少代码量

---

## 九、术语表

| 英文术语 | 音标 | 中文释义 |
|----------|------|----------|
| Tool Registry | /tuːl ˈredʒɪstri/ | 工具注册表，集中管理所有可用工具 |
| Agent Core | /ˈeɪdʒənt kɔː/ | Agent 核心，决策和编排中心 |
| Session | /ˈseʃən/ | 会话，一个用户的一次对话过程 |
| Parameter Validation | /pəˈræmɪtər ˌvælɪˈdeɪʃən/ | 参数验证，检查参数合法性 |
| Async/Await | /eɪˈsɪŋk əˈweɪt/ | 异步等待，非阻塞执行 |
| Throughput | /ˈθruːpʊt/ | 吞吐量，单位时间处理请求数 |
| Latency | /ˈleɪtənsi/ | 延迟，请求到响应的时间 |
| Rate Limit | /reɪt ˈlɪmɪt/ | 速率限制，防止过载 |

---

## 十、参考资源

### 📹 视频推荐
1. **《从零搭建 AI Agent 完整教程》**
   推荐搜索：build AI agent from scratch 2024

2. **《LangChain Agent 实战》**系列
   推荐搜索：langchain agent tutorial

### 📖 延伸阅读
1. **OpenAI Function Calling 官方指南**
   https://developers.openai.com/api/docs/guides/function-calling

2. **Building Effective AI Agents**（LangChain 官方博客）
   推荐搜索：building effective ai agents

---

> 📅 **明天预告**：Day 7 是第六周的**总复习日**！我们会把这一周学的所有内容串联起来——Agent 架构、Function Calling、ReAct 模式、推理评测、Prompt 工程、框架设计——形成一个完整的知识体系。配有综合测试和实战案例分析，帮你查漏补缺！
