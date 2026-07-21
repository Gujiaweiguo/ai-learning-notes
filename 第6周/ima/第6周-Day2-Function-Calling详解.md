# 第6周 Day 2：Function Calling 详解

> **导语**：昨天我们认识了 Agent 的全貌——LLM（大脑）+ Tools（工具箱）+ Memory（记忆）。今天我们要打开"工具箱"，拆解 Agent 最核心的能力：Function Calling（函数调用）。如果说 Agent 是一个能干的助手，那 Function Calling 就是它"打电话给外界"的能力。

---

## 📊 学习进度

```
████████████████████████████████░░░░░░░░░░░░░░░░░░░░ 51%
第1周 ✅  Python基础
第2周 ✅  AI与大模型基础
第3周 ✅  RAG检索增强生成
第4周 ✅  向量数据库与Embedding
第5周 ✅  大模型微调与部署
第6周 🔄  Agent与工具使用（Day 2/7）← 今天
```

---

## 一、为什么需要 Function Calling？

### 1.1 一个真实的困境

假设你在用 LangChat 给企业搭智能客服，客户问了一个问题：

> "张三的订单 #20250721-003 现在到哪个环节了？"

如果没有 Function Calling，大模型会怎么回答？它可能会"编"一个答案——"您的订单正在配送中"。但这个信息是假的，模型根本没有查物流系统。

这就好比你问朋友"我的快递到哪了？"，朋友不看手机就瞎编一个答案。更糟糕的是，大模型编的答案听起来非常自信，用户可能真的信了。

**Function Calling 解决的核心问题：让大模型从"编答案"变成"查答案"。**

### 1.2 生活类比——"电话本"模型

把 Function Calling 想象成给 AI 配了一本"电话本"：

| 概念 | 类比 | 说明 |
|------|------|------|
| 工具定义 | 电话本里的联系人 | 每个联系人=一个可调用的功能 |
| 工具名称 | 联系人名字 | 如 `query_order`、`get_weather` |
| 工具描述 | 联系人职能说明 | "这个人能帮你查订单" |
| 参数定义 | 拨号需要的信息 | "查订单需要提供订单号" |
| 调用决策 | AI 决定要不要打电话 | "这个问题我答不了，得打电话问一下" |
| 返回结果 | 电话那头给的答复 | "订单已发货，预计明天送达" |

### 1.3 没有 Function Calling 的世界

```
用户：今天上海到北京的高铁还有票吗？
LLM：抱歉，我无法查询实时票务信息。（用户流失 💀）

用户：帮我算一下 35% 的复利，本金10000，5年
LLM：10000 × (1+0.35)^5 = 45069.19...（如果算对了还行，但经常算错 💀）

用户：我们店这个月红豆用量趋势怎么样？
LLM：我无法访问您的销售数据。（用户流失 💀）
```

有了 Function Calling，以上问题全部能解决。

---

## 二、核心原理详解

### 2.1 Function Calling 的三步工作流

**第一步：意图识别（Intent Recognition）**

LLM 接收到用户消息后，首先判断："这个问题我自己能答，还是需要借助外部工具？"

判断逻辑基于：
- **知识边界**：问题是否超出了训练数据范围？（实时信息一定超）
- **计算复杂度**：复杂计算交给计算器更准确
- **数据来源**：需要访问私有数据（数据库、API）

**第二步：工具选择（Tool Selection）**

如果需要工具，LLM 从可用的工具列表中选择最合适的一个。这个选择基于**工具描述（description）**——你写给 LLM 的"工具说明书"。

**第三步：参数提取（Parameter Extraction）**

选定工具后，LLM 从用户的自然语言中提取工具需要的参数。

```
用户："查一下北京明天的天气"
LLM 选定工具：get_weather
LLM 提取参数：{"city": "北京", "date": "2025-07-22"}
```

### 2.2 工具定义三要素（超重要！）

每个工具必须包含三个关键信息：

**要素一：工具名称（name）**
- 命名规范：动词+名词，小写下划线
- 好名字：`query_order_status`、`calculate_discount`
- 坏名字：`func1`、`handle_stuff`、`do_something`

**要素二：工具描述（description）**
- 这是最关键的部分！LLM 就是靠描述来决定用哪个工具的
- 必须说清楚：这个工具能做什么、什么时候该用、什么时候不该用
- 好描述："根据订单号查询订单的当前状态，包括已下单、制作中、配送中、已完成等状态"
- 坏描述："查询订单"（太模糊，LLM 不知道什么场景该用）

**要素三：参数定义（parameters）**
- 每个参数需要指定：类型（string/number/boolean...）、是否必填、描述
- 用 JSON Schema 格式定义

```python
# 一个标准的工具定义
{
    "name": "query_order_status",                    # ① 名称
    "description": "根据订单号查询订单的完整状态信息，"   # ② 描述
                   "包括当前环节、预计完成时间、配送进度。"
                   "适用于用户询问'我的订单怎么样了'等场景。",
    "parameters": {                                  # ③ 参数
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "订单编号，格式如 'ORD-20250721-001'"
            },
            "include_delivery": {
                "type": "boolean",
                "description": "是否包含配送轨迹详情，默认 false"
            }
        },
        "required": ["order_id"]                     # 必填参数
    }
}
```

### 2.3 LLM 的调用决策逻辑

LLM 决定"调不调工具、调哪个工具"的过程，本质是在做**语义匹配**：

```
用户输入 → 语义编码 → 与所有工具描述做匹配 → 选择匹配度最高的工具
```

**会触发工具调用的典型场景**：
- 需要实时数据（天气、股价、汇率、库存）
- 需要精确计算（数学、统计、财务）
- 需要访问私有数据（用户订单、企业数据库）
- 需要执行操作（发邮件、创建任务、调用API）

**不会触发工具调用的场景**：
- 常识问题（"北京是中国的首都吗？"）
- 创意生成（"帮我写一首关于夏天的诗"）
- 简单翻译（"把这句话翻成英文"）

### 2.4 tool_choice 参数

大多数 LLM API 提供了 `tool_choice` 参数来控制工具调用行为：

| 值 | 含义 | 使用场景 |
|----|------|---------|
| `auto` | LLM 自动决定 | 默认值，大部分场景用这个 |
| `none` | 禁止调用工具 | 只想纯对话，不调任何工具 |
| `required` | 强制调用工具 | 必须用工具，不允许直接回答 |
| 指定工具名 | 强制调用指定工具 | 明确知道该用哪个工具 |

---

## 三、代码实战

### 3.1 从零定义一组工具

```python
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np
import json

# matplotlib 中文字体配置
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False


# ===== 定义业务工具 =====
# 以糖水店为例，定义5个常用工具

# 工具1：查询天气
def get_weather(city: str) -> dict:
    """查询指定城市的当前天气"""
    weather_db = {
        "北京": {"temp": 32, "condition": "晴", "humidity": 45},
        "上海": {"temp": 28, "condition": "多云", "humidity": 75},
        "广州": {"temp": 35, "condition": "雷阵雨", "humidity": 80},
    }
    return weather_db.get(city, {"temp": None, "condition": "未知", "humidity": None})


# 工具2：计算器
def calculate(expression: str) -> float:
    """执行数学计算，支持四则运算"""
    return eval(expression)


# 工具3：查询库存
def check_inventory(item: str) -> dict:
    """查询糖水店某原料的库存"""
    inventory = {"红豆": 50, "绿豆": 40, "西米": 30, "椰奶": 20, "珍珠": 35}
    return {"item": item, "stock": inventory.get(item, 0), "unit": "kg"}


# 工具4：发送通知
def send_notification(phone: str, message: str) -> str:
    """发送短信通知给指定手机号"""
    return f"短信已发送至 {phone}：{message[:20]}..."


# 工具5：搜索知识库
def search_knowledge(query: str) -> str:
    """搜索糖水店知识库（FAQ、政策、产品信息）"""
    kb = {
        "退货": "退货需在购买后24小时内，凭小票办理",
        "营业": "营业时间：周一至周日 10:00-22:00",
        "会员": "会员充值500元送50元，享受9折优惠",
    }
    for key, val in kb.items():
        if key in query:
            return val
    return f"未找到关于'{query}'的信息"


# ===== 工具注册表 =====
# 这是给 LLM 看的"菜单"，包含每个工具的完整说明
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气信息，包括温度、天气状况和湿度。"
                           "当用户询问天气相关问题时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "中国城市名称，如'北京'、'上海'、'广州'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算。支持加减乘除、幂运算、括号等。"
                           "当用户需要精确计算时使用，避免LLM自己算错。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3 * 4' 或 '(100 + 200) / 3'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "查询糖水店某样原料或产品的当前库存量。"
                           "当用户询问'还有没有XX'、'库存多少'时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "原料或产品名称，如'红豆'、'椰奶'、'杨枝甘露'"
                    }
                },
                "required": ["item"]
            }
        }
    }
]

print(f"✅ 已注册 {len(TOOLS_SCHEMA)} 个工具")
for t in TOOLS_SCHEMA:
    print(f"   - {t['function']['name']}: {t['function']['description'][:30]}...")
```

### 3.2 模拟 LLM 的调用决策

```python
class ToolCallingSimulator:
    """模拟 LLM 的 Function Calling 决策过程"""
    
    def __init__(self, tools_schema, tool_functions):
        self.schema = tools_schema
        self.functions = tool_functions   # 工具名→函数 的映射
        self.call_history = []            # 记录所有调用
    
    def llm_decide(self, user_message: str):
        """
        模拟 LLM 的决策逻辑。
        实际项目中，这里会调用 GPT/Qwen/GLM API，
        传入 user_message + tools_schema，
        API 返回要调用的工具名和参数。
        """
        msg = user_message.lower()
        
        # 模拟语义匹配：关键词 → 工具
        if any(w in msg for w in ["天气", "温度", "下雨", "几度"]):
            # 提取城市
            for city in ["北京", "上海", "广州", "深圳", "杭州"]:
                if city in user_message:
                    return "get_weather", {"city": city}
            return "get_weather", {"city": "北京"}  # 默认
            
        elif any(w in msg for w in ["计算", "等于", "加", "减", "乘", "除", "多少"]):
            import re
            match = re.search(r'[\d\+\-\*/\.\(\)\s]+', user_message)
            if match:
                expr = match.group().strip()
                return "calculate", {"expression": expr}
                
        elif any(w in msg for w in ["库存", "还有", "剩下", "够不够"]):
            # 尝试提取物品名
            for item in ["红豆", "绿豆", "西米", "椰奶", "珍珠"]:
                if item in user_message:
                    return "check_inventory", {"item": item}
        
        return None, None  # LLM 判断不需要调用工具
    
    def execute(self, user_message: str) -> str:
        """完整的 Function Calling 流程"""
        print(f"\n{'='*60}")
        print(f"👤 用户：{user_message}")
        
        # Step 1: LLM 决策
        tool_name, args = self.llm_decide(user_message)
        
        if tool_name is None:
            # LLM 认为不需要工具，直接回答
            print(f"🤖 Agent：这个问题我可以直接回答（无需工具）")
            return "直接回答"
        
        print(f"🧠 LLM决策：需要调用工具 → {tool_name}")
        print(f"📝 提取参数：{json.dumps(args, ensure_ascii=False)}")
        
        # Step 2: 执行工具
        tool_fn = self.functions[tool_name]
        result = tool_fn(**args)
        print(f"🔧 工具执行：{tool_name} → {result}")
        
        # Step 3: 整合回复（实际由 LLM 完成）
        if isinstance(result, dict) and "temp" in result:
            response = f"天气信息：{result['condition']}，温度{result['temp']}°C"
        elif isinstance(result, (int, float)):
            response = f"计算结果是：{result}"
        elif isinstance(result, dict) and "stock" in result:
            response = f"{result['item']}当前库存：{result['stock']}{result['unit']}"
        else:
            response = str(result)
        
        print(f"✅ 最终回复：{response}")
        
        self.call_history.append({
            "user": user_message,
            "tool": tool_name,
            "args": args,
            "result": result
        })
        return response


# 运行测试
tool_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "check_inventory": check_inventory,
}

simulator = ToolCallingSimulator(TOOLS_SCHEMA, tool_map)
simulator.execute("北京今天天气怎么样？")
simulator.execute("帮我算一下 (128 + 256) * 3 等于多少")
simulator.execute("店里红豆还有多少库存？")
simulator.execute("你是谁？")  # 不需要工具

print(f"\n📊 共调用了 {len(simulator.call_history)} 次工具")
```

### 3.3 真实 API 调用示例（伪代码）

```python
# 真实项目中调用 OpenAI API 的标准写法
# （这里用伪代码展示，实际运行需要 API Key）

"""
from openai import OpenAI
client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "北京天气怎么样？"}],
    tools=TOOLS_SCHEMA,          # ← 传入工具定义
    tool_choice="auto",          # ← 让 LLM 自动决定
)

# 检查 LLM 是否决定调用工具
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    tool_name = tool_call.function.name         # "get_weather"
    arguments = json.loads(tool_call.function.arguments)  # {"city": "北京"}
    
    # 执行工具
    result = tool_map[tool_name](**arguments)
    
    # 把结果发回给 LLM，让它生成自然语言回复
    response2 = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "北京天气怎么样？"},
            response.choices[0].message,           # LLM 的工具调用
            {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}
        ]
    )
    print(response2.choices[0].message.content)  # "北京今天晴天，32°C..."
"""
```

---

## 四、可视化分析

```python
# Function Calling 完整流程可视化
fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_title('Function Calling 完整工作流程', fontsize=16, fontweight='bold', pad=20)

# 流程节点
nodes = [
    (1, 8, '👤 用户输入\n"北京天气"', '#E3F2FD', '#1565C0'),
    (4, 8, '🧠 意图识别\n需要实时数据', '#FFF9C4', '#F57F17'),
    (7, 8, '🔧 工具选择\n→ get_weather', '#C8E6C9', '#2E7D32'),
    (10, 8, '📝 参数提取\ncity="北京"', '#E1BEE7', '#7B1FA2'),
    (13, 8, '⚙️ 执行工具\n调用函数', '#FFCCBC', '#D84315'),
    (13, 4, '📋 获取结果\n{temp:32,晴}', '#B3E5FC', '#0277BD'),
    (10, 4, '🧠 结果整合\nLLM 组织语言', '#C8E6C9', '#2E7D32'),
    (7, 4, '💬 生成回复\n"北京今天32°C"', '#F8BBD0', '#C2185B'),
    (4, 4, '👤 返回用户', '#E3F2FD', '#1565C0'),
]

for x, y, text, bg, edge in nodes:
    from matplotlib.patches import FancyBboxPatch
    rect = FancyBboxPatch((x-1.2, y-0.7), 2.4, 1.4,
                           boxstyle="round,pad=0.15",
                           facecolor=bg, edgecolor=edge, linewidth=2)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')

# 箭头连接
arrows = [(2.2, 8, 2.8, 8), (5.2, 8, 5.8, 8), (8.2, 8, 8.8, 8), (11.2, 8, 11.8, 8),
          (13, 7.3, 13, 4.7), (11.8, 4, 11.2, 4), (8.8, 4, 8.2, 4), (5.8, 4, 5.2, 4)]
for x1, y1, x2, y2 in arrows:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=2, color='#666'))

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第6周/ima/day2_function_calling_flow.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 Function Calling 流程图已保存")
```

---

## 五、业务关联

### 5.1 LangChat 平台中的 Function Calling

LangChat 作为企业 AI 平台，Function Calling 是其核心能力之一：

**应用一：智能客服**
- 工具：`query_order`（查订单）、`check_inventory`（查库存）、`process_refund`（处理退款）
- 用户问"我的订单到哪了" → Agent 自动调用 `query_order`

**应用二：数据分析助手**
- 工具：`query_database`（查数据库）、`generate_chart`（生成图表）、`export_report`（导出报表）
- 用户说"看一下本月销售趋势" → Agent 自动查询 → 生成图表 → 导出报告

**应用三：办公自动化**
- 工具：`send_email`（发邮件）、`create_meeting`（建会议）、`update_crm`（更新CRM）
- 用户说"给王总发邮件说会议改到下午3点" → Agent 自动发邮件

### 5.2 工具定义的最佳实践

在 LangChat 等企业平台中定义工具，遵循以下原则：

1. **描述要详尽**：LLM 完全依赖描述来做选择，描述模糊=选错工具
2. **参数要有约束**：枚举值、格式说明、默认值
3. **错误信息要友好**：工具返回的错误信息会被 LLM 看到，帮助它调整策略
4. **工具粒度要适中**：太粗则不够灵活，太细则 LLM 难以选择

---

## 六、常见误区

### ❌ 误区一："工具描述随便写写就行"
**真相**：工具描述是 LLM 唯一的决策依据。描述写得差，LLM 就会选错工具或不选工具。好的描述要包含：功能说明、使用场景、参数含义、返回值格式。

### ❌ 误区二："Function Calling 就是调用 API"
**真相**：Function Calling 是一个完整的闭环——LLM 决策 → 提取参数 → 执行工具 → 结果反馈 → LLM 整合回复。API 调用只是"执行"那一步，前面的决策和后面的整合同样重要。

### ❌ 误区三："工具越多越好"
**真相**：工具太多会让 LLM "选择困难"，准确率反而下降。研究表明，超过 10-15 个工具后，选择准确率显著降低。解决方案：工具分组、级联选择、语义检索工具。

### ❌ 误区四："LLM 提取的参数一定对"
**真相**：LLM 经常提取错参数，比如把"后天"提取得不对、把手机号格式弄错。生产环境中必须做**参数验证**——类型检查、格式校验、范围限制。

---

## 七、课堂练习（5分钟）

**练习一**：为以下场景定义一个工具（写 JSON Schema）

场景：查询某个用户的消费记录。

要求：参数包括用户ID（必填）和时间范围（选填）。

**练习二**：判断以下用户输入是否需要工具调用

1. "帮我查一下北京天气" → ____（需要/不需要）
2. "什么是人工智能？" → ____
3. "给我算一下 15% 的小费，消费是238元" → ____
4. "你叫什么名字？" → ____

**练习三**：设计工具描述

为"发送短信"这个工具写一段好的 description 和差的 description，对比差异。

---

## 八、课后测试（10分钟）

**1. Function Calling 工作流程的正确顺序是？**
A. 执行工具 → 意图识别 → 参数提取 → 结果返回
B. 意图识别 → 工具选择 → 参数提取 → 执行工具
C. 参数提取 → 意图识别 → 执行工具 → 工具选择
D. 工具选择 → 执行工具 → 参数提取 → 意图识别

**2. 工具定义的三要素是什么？**
A. 名称 + 描述 + 参数
B. 名称 + 代码 + 测试
C. 输入 + 处理 + 输出
D. URL + 方法 + 头部

**3. LLM 做工具选择决策时，主要依赖什么信息？**
A. 工具的函数名
B. 工具的 description 描述
C. 工具的参数类型
D. 工具的返回值

**4. 以下哪种 tool_choice 设置表示"必须调用工具，不允许直接回答"？**
A. auto
B. none
C. required
D. any

**5. 关于工具数量，以下说法正确的是？**
A. 越多越好，功能越全面
B. 应该控制在合理范围，太多会降低选择准确率
C. 最多不能超过5个
D. 数量不影响性能

---

## 九、术语表

| 英文术语 | 音标 | 中文释义 |
|----------|------|----------|
| Function Calling | /ˈfʌŋkʃən ˈkɔːlɪŋ/ | 函数调用，让 LLM 调用外部工具的机制 |
| Tool Schema | /tuːl ˈskiːmə/ | 工具模式，描述工具结构的 JSON 定义 |
| Parameter Extraction | /pəˈræmɪtər ɪkˈstrækʃən/ | 参数提取，从自然语言中提取工具参数 |
| Tool Choice | /tuːl tʃɔɪs/ | 工具选择策略（auto/none/required） |
| JSON Schema | /ˈdʒeɪsɒn ˈskiːmə/ | JSON 模式，用 JSON 描述数据结构 |
| Intent Recognition | /ɪnˈtent ˌrekəɡˈnɪʃən/ | 意图识别，理解用户想要什么 |
| Endpoint | /ˈendpɔɪnt/ | 端点，API 的访问地址 |
| Payload | /ˈpeɪləʊd/ | 载荷，请求中携带的数据 |
| Callback | /ˈkɔːlbæk/ | 回调，工具执行完后通知结果 |
| OpenAPI | /ˌəʊpən ˈeɪpiːaɪ/ | 开放 API 标准规范 |

---

## 十、参考资源

### 📹 视频推荐
1. **《Function Calling 技术详解》**（13集系列，约3小时）
   https://www.bilibili.com/video/BV1SJm8YtETd/

2. **《Function Calling 30分钟全解》**（30分钟）
   https://www.bilibili.com/video/BV1emMFzfE5A/

### 📖 延伸阅读
1. **OpenAI Function Calling 官方指南**
   https://developers.openai.com/api/docs/guides/function-calling

2. **大模型函数调用完全指南**（知乎深度解析）
   https://zhuanlan.zhihu.com/p/2004370775214424996

---

> 📅 **明天预告**：Day 3 我们将学习 **ReAct 模式与多 Agent 协作**——当一个 Agent 不够用时，怎么让多个 Agent 组队干活？ReAct 循环到底是怎么"边想边做"的？精彩继续！
