```python
# W7 Day 6 - ⚡实战：搭建完整数字员工原型
# matplotlib 中文字体配置
from matplotlib import font_manager
import matplotlib.pyplot as plt
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False
print(f'中文字体配置完成: {font_name}')
```

# ⚡ 实战日 | 第7周-Day6：搭建完整数字员工原型

> **Agent Runtime入门 → 从零搭建一个可运行的数字员工**前五天我们学了：身份(SOUL.md) → 记忆(MEMORY.md) → 工作流 → 多Agent协作 → 质量评估
> 今天是把所有知识串起来，动手搭建一个完整的数字员工原型！

## 📅 学习进度

```
W1  ████████████████████ ✅ Transformer与大模型训练
W2  ████████████████████ ✅ 微调与RLHF
W3  ████████████████████ ✅ RAG与知识增强
W4  ████████████████████ ✅ 推理与思维链
W5  ████████████████████ ✅ Agent与工具使用
W6  ████████████████████ ✅ LLM Agent实战
W7  █████████████████░░░ 🔥 数字员工架构深化 (Day6/7)
W8  ░░░░░░░░░░░░░░░░░░░░ 📝 AI基础补强
W9  ░░░░░░░░░░░░░░░░░░░░ 🔌 MCP协议深入
W10 ░░░░░░░░░░░░░░░░░░░░ ⚙️ Agent Runtime进阶
W11 ░░░░░░░░░░░░░░░░░░░░ 🧠 AI Compiler
W12 ░░░░░░░░░░░░░░░░░░░░ 🏛 Capability Platform
W13 ░░░░░░░░░░░░░░░░░░░░ 📊 ChatBI
W14 ░░░░░░░░░░░░░░░░░░░░ 🔒 企业权限与安全
W15 ░░░░░░░░░░░░░░░░░░░░ 🎯 RL与优化
W16 ░░░░░░░░░░░░░░░░░░░░ 👁 商业地产视觉AI
W17 ░░░░░░░░░░░░░░░░░░░░ 🚀 前沿与部署
W18 ░░░░░░░░░░░░░░░░░░░░ 🧠 脑科学精华
```

**进度: 7/18 周 (38.9%) | Day 34/126**

# 🔄 往期回顾（W7 Day1-5 知识串联）

## 本周学过的五大模块

| **Day** | **主题**   | **核心组件**                | **一句话总结**               |
| ------- | -------- | ----------------------- | ----------------------- |
| Day1    | 数字员工总览   | **SOUL.md**             | 定义Agent的身份、规则、约束、输出格式   |
| Day2    | 记忆系统     | **MEMORY.md**           | 三层记忆（短期/中期/长期），语义搜索持久化  |
| Day3    | 任务编排     | **Cron + 消息路由**         | 工作流是图不是链，定时任务+跨平台推送     |
| Day4    | 多Agent协作 | **subagent + TaskFlow** | 主Agent分发任务，子Agent并行执行   |
| Day5    | 质量保障     | **护栏 + 监控**             | 三层护栏(Prompt+工具+流程)，审计轨迹 |

## 🎯 今天的任务

把上面5个模块整合成一个**可运行的数字员工原型**：

```
用户请求 → OrchestratorAgent（身份+路由）
              ├── SOUL.md（人格定义）
              ├── MEMORY.md（记忆持久化）
              ├── Tool Registry（工具注册表）
              │    ├── 查询商铺信息
              │    ├── 查询租赁状态
              │    └── 发送通知
              └── SubAgent池
                   ├── 数据分析Agent
                   └── 报告生成Agent
```

# 🏗️ Step 1：定义数字员工的 SOUL.md

> SOUL.md = 数字员工的灵魂文件，定义身份、行为边界和输出规范

## SOUL.md 四层结构回顾

```
Layer 1: Identity（身份）    → 你是谁？负责什么？
Layer 2: Rules（规则）       → 工作流程是什么？先做什么后做什么？
Layer 3: Constraints（约束） → 不能做什么？安全红线是什么？
Layer 4: Output（输出格式）  → 交付物长什么样？JSON/Markdown/模板？
```

### 💡 LangChat/Orchestrator关联

* LangChat中每个Skill都有System Prompt约束行为
* Orchestrator通过SOUL.md判断请求路由到哪个能力域
* 商管系统的数字员工需要严格遵守权限边界

```python
# Step 1: 定义商管数字员工的 SOUL.md
SOUL_MD = """# 商管数字员工 SOUL.md

## Identity（身份）
你是「商管智能助手」，服务于商业地产运营团队。
你的职责包括：商铺信息查询、租赁状态跟踪、经营数据分析、异常预警。

## Rules（工作规则）
1. 收到查询请求时，先验证用户权限（是否属于运营组）
2. 数据查询优先使用结构化API，知识查询使用RAG
3. 涉及合同/租金等敏感数据，必须输出完整审计日志
4. 无法确定时，转人工而不是猜测

## Constraints（约束）
- 禁止直接修改任何业务数据（只读 + 建议输出）
- 禁止泄露租户联系方式给非授权人员
- 超过权限范围的请求必须拒绝并上报

## Output Format（输出格式）
- 数据查询结果：结构化表格 + 摘要文字
- 分析报告：Markdown格式，含数据来源标注
- 预警通知：⚠️标识 + 紧急程度(低/中/高) + 建议操作
"""

print(SOUL_MD)
print(f"\n📊 SOUL.md 总字数: {len(SOUL_MD)}")
```

# 🧠 Step 2：设计 MEMORY.md 记忆系统

> 数字员工需要记住用户偏好、历史决策、业务上下文

## 三层记忆架构

| **层次** | **存储位置**                 | **容量**       | **持久性** | **用途**    |
| ------ | ------------------------ | ------------ | ------- | --------- |
| 短期     | 上下文窗口                    | \~4K tokens  | 单次对话    | 当前对话的临时信息 |
| 中期     | session历史                | \~32K tokens | 会话级     | 本轮对话的重要事实 |
| 长期     | MEMORY.md + memory/\*.md | 无限           | 永久      | 用户偏好、历史决策 |

### 语义搜索原理

```
用户问 "上次那个餐饮招商的分析"
  → embedding(查询语句) → 向量
  → 在memory/*.md的embedding索引中搜索
  → 余弦相似度排序
  → 返回最相关的记忆片段
```

```python
# Step 2: 设计记忆系统
MEMORY_MD = """# MEMORY.md - 商管数字员工记忆

## 用户偏好
- Jason（运营总监）：偏好数据驱动决策，喜欢图表而非纯文字
- Sarah（招商经理）：关注租赁转化率，偏好简洁摘要

## 重要决策记录
- 2026-06-15: 确认优先推广3F餐饮区域，目标品牌：海底捞、西贝
- 2026-06-28: B1层儿童区改造方案获批，预计Q3完成

## 业务上下文
- 当前项目：万达广场浦东店
- 总商铺数：285个，已出租：241个，空置率：15.4%
- 重点KPI：客流增长率、坪效、租金收缴率
"""

# 模拟语义搜索
import hashlib

def simple_embedding(text, dim=64):
    """简易hash-based embedding（教学用，真实场景用Transformer）"""
    words = text.replace('\n', ' ').split()
    vec = [0.0] * dim
    for w in words:
        h = int(hashlib.md5(w.encode()).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    # 归一化
    norm = sum(v*v for v in vec) ** 0.5
    if norm > 0:
        vec = [v/norm for v in vec]
    return vec

def cosine_sim(a, b):
    return sum(x*y for x, y in zip(a, b))

# 记忆片段库
memory_chunks = [
    "Jason偏好数据驱动决策，喜欢图表",
    "确认优先推广3F餐饮区域，目标品牌海底捞西贝",
    "B1层儿童区改造方案获批",
    "万达广场浦东店总商铺285个已出租241个",
    "重点KPI客流增长率坪效租金收缴率",
]

# 索引所有记忆
embeddings = {chunk: simple_embedding(chunk) for chunk in memory_chunks}

# 模拟查询
query = "餐饮招商分析"
query_vec = simple_embedding(query)

scores = [(chunk, cosine_sim(query_vec, vec)) for chunk, vec in embeddings.items()]
scores.sort(key=lambda x: -x[1])

print(f'🔍 查询: "{query}"')
print(f'\n📊 语义搜索结果（按相似度排序）:')
for i, (chunk, score) in enumerate(scores[:3], 1):
    print(f'  {i}. [{score:.4f}] {chunk}')
```

# 🔧 Step 3：工具注册表（Tool Registry）

> 数字员工通过工具与外部系统交互。工具注册表管理所有可用工具的元数据。

## 工具Schema设计

每个工具需要：

* **name**: 唯一标识
* **description**: 功能描述（给LLM看的）
* **parameters**: 输入参数Schema
* **returns**: 输出格式
* **permissions**: 调用权限要求

### 💡 对应MCP协议

* MCP Tool 就是结构化的工具定义
* LangChat的Skill最终通过MCP暴露为标准能力
* Orchestrator的capability路由基于工具注册表

```python
# Step 3: 定义工具注册表
import json

TOOL_REGISTRY = {
    "query_shop": {
        "description": "查询商铺信息（铺位号、面积、业态、租户）",
        "parameters": {
            "type": "object",
            "properties": {
                "shop_id": {"type": "string", "description": "商铺编号，如B1-001"},
                "floor": {"type": "string", "description": "楼层筛选，如3F"}
            }
        },
        "required": ["shop_id"],
        "permissions": ["read:shop"],
        "timeout_ms": 3000
    },
    "query_lease": {
        "description": "查询租赁状态（合同、租金、到期日）",
        "parameters": {
            "type": "object",
            "properties": {
                "shop_id": {"type": "string"},
                "status": {"type": "string", "enum": ["active", "expired", "pending"]}
            }
        },
        "required": ["shop_id"],
        "permissions": ["read:lease"],
        "timeout_ms": 5000
    },
    "send_notification": {
        "description": "发送通知消息（邮件/短信/微信）",
        "parameters": {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "enum": ["email", "sms", "wechat"]},
                "recipient": {"type": "string"},
                "message": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
            }
        },
        "required": ["channel", "recipient", "message"],
        "permissions": ["write:notification"],
        "timeout_ms": 2000
    }
}

# 模拟工具执行
MOCK_SHOP_DATA = {
    "3F-012": {"shop_id": "3F-012", "area": 280, "business": "餐饮", "tenant": "海底捞", "rent": 85000},
    "3F-015": {"shop_id": "3F-015", "area": 150, "business": "餐饮", "tenant": "空置", "rent": 0},
    "B1-008": {"shop_id": "B1-008", "area": 45, "business": "零售", "tenant": "名创优品", "rent": 12000},
}

def execute_tool(tool_name, params):
    """模拟工具执行"""
    if tool_name == "query_shop":
        shop_id = params.get("shop_id")
        if shop_id in MOCK_SHOP_DATA:
            return {"status": "success", "data": MOCK_SHOP_DATA[shop_id]}
        return {"status": "not_found", "data": None}
    elif tool_name == "query_lease":
        shop_id = params.get("shop_id")
        if shop_id == "3F-012":
            return {"status": "success", "data": {"contract": "L2024-0231", "monthly_rent": 85000, "expire": "2027-03-31"}}
        return {"status": "not_found", "data": None}
    elif tool_name == "send_notification":
        return {"status": "success", "message_id": f"MSG-{hash(params.get('message',''))%10000:04d}"}
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}

# 测试工具调用
print('🔧 工具注册表:')
for name, spec in TOOL_REGISTRY.items():
    print(f'  - {name}: {spec["description"]}')

print('\n🧪 测试工具调用:')
result = execute_tool("query_shop", {"shop_id": "3F-012"})
print(f'  query_shop(3F-012) → {json.dumps(result, ensure_ascii=False, indent=2)}')
```

# 🤖 Step 4：子Agent协作设计

> 主Agent（Orchestrator）负责路由，子Agent负责专业任务

## 子Agent类型

```
OrchestratorAgent（主控）
  ├── DataAgent（数据分析子Agent）
  │    └── 负责SQL查询、数据汇总、趋势分析
  ├── ReportAgent（报告生成子Agent）
  │    └── 负责将分析结果转为可读报告
  └── AlertAgent（预警子Agent）
       └── 负责异常检测和通知推送
```

## 上下文传递：isolated vs fork

| **模式**       | **说明**             | **适用场景**   |
| ------------ | ------------------ | ---------- |
| **isolated** | 子Agent获得干净上下文      | 独立任务（数据分析） |
| **fork**     | 子Agent继承父Agent对话历史 | 需要上下文的连续任务 |

### 💡 OpenClaw的sessions\_spawn

```python
# isolated模式（默认）
sessions_spawn(task="分析3F餐饮区域经营数据", context="isolated")

# fork模式（需要父对话上下文）
sessions_spawn(task="继续刚才的分析，深入租金差异", context="fork")
```

```python
# Step 4: 子Agent模拟实现
import time

class SubAgent:
    """子Agent基类"""
    def __init__(self, name, soul, tools, context_mode="isolated"):
        self.name = name
        self.soul = soul  # 子Agent的SOUL.md
        self.tools = tools  # 可用工具列表
        self.context_mode = context_mode
        self.results = []

    def run(self, task, parent_context=None):
        """执行任务"""
        print(f'  [{self.name}] 接收任务: {str(task)[:60]}')
        if self.context_mode == "fork" and parent_context:
            print(f'  [{self.name}] 继承父上下文 ({len(parent_context)} chars)')
        else:
            print(f'  [{self.name}] 使用隔离上下文 (isolated)')
        # 模拟执行
        time.sleep(0.1)
        result = self._execute(task)
        self.results.append(result)
        return result

    def _execute(self, task):
        raise NotImplementedError


class DataAgent(SubAgent):
    """数据分析子Agent"""
    def __init__(self):
        super().__init__(
            name="DataAgent",
            soul="你是数据分析专家，负责SQL查询和数据汇总",
            tools=["query_shop", "query_lease"],
            context_mode="isolated"
        )

    def _execute(self, task):
        shops = []
        for shop_id in ["3F-012", "3F-015"]:
            result = execute_tool("query_shop", {"shop_id": shop_id})
            if result["status"] == "success":
                shops.append(result["data"])
        total_area = sum(s["area"] for s in shops)
        total_rent = sum(s["rent"] for s in shops)
        occupied = sum(1 for s in shops if s["tenant"] != "空置")
        return {
            "agent": self.name,
            "analysis": {
                "total_shops": len(shops),
                "total_area": total_area,
                "total_monthly_rent": total_rent,
                "occupancy_rate": f"{occupied/len(shops)*100:.0f}%",
            }
        }


class ReportAgent(SubAgent):
    """报告生成子Agent"""
    def __init__(self):
        super().__init__(
            name="ReportAgent",
            soul="你是报告撰写专家，将数据转为可读的商业分析报告",
            tools=[],
            context_mode="fork"
        )

    def _execute(self, task):
        if isinstance(task, dict) and "analysis" in task:
            a = task["analysis"]
            report = f"""📊 3F餐饮区域经营分析报告
{'='*40}
总商铺数: {a['total_shops']}
总面积:   {a['total_area']}㎡
月租金:   ¥{a['total_monthly_rent']:,}
出租率:   {a['occupancy_rate']}
{'='*40}
💡 建议: 出租率偏低，建议加大招商力度。"""
            return {"agent": self.name, "report": report}
        return {"agent": self.name, "report": "数据不足，无法生成报告"}


class AlertAgent(SubAgent):
    """预警子Agent"""
    def __init__(self):
        super().__init__(
            name="AlertAgent",
            soul="你是预警监控专家，负责检测异常并推送通知",
            tools=["send_notification"],
            context_mode="isolated"
        )

    def _execute(self, task):
        if isinstance(task, dict) and "analysis" in task:
            rate_str = task["analysis"]["occupancy_rate"]
            rate = int(rate_str.replace('%', ''))
            if rate < 80:
                result = execute_tool("send_notification", {
                    "channel": "wechat",
                    "recipient": "Jason",
                    "message": f"⚠️ 3F餐饮区域出租率仅{rate_str}%，低于预警线80%",
                    "priority": "high"
                })
                return {"agent": self.name, "alert_sent": True, "result": result}
        return {"agent": self.name, "alert_sent": False}


print('🤖 子Agent注册完成:')
for cls in [DataAgent, ReportAgent, AlertAgent]:
    agent_tmp = cls()
    print(f'  ✅ {agent_tmp.name} | tools={agent_tmp.tools} | context={agent_tmp.context_mode}')
```

# 🎯 Step 5：OrchestratorAgent — 把一切串起来

> 主控Agent = SOUL.md + MEMORY.md + Tool Registry + SubAgent编排

## 执行流程

```
1. 用户请求进来
   "分析一下3F餐饮区域的经营状况"

2. OrchestratorAgent 解析意图
   → 意图: 数据分析 + 报告生成
   → 路由: DataAgent → ReportAgent → AlertAgent

3. 调用 DataAgent (isolated)
   → 查询商铺数据 → 返回结构化分析结果

4. 调用 ReportAgent (fork，继承DataAgent结果)
   → 将数据转为可读报告

5. 调用 AlertAgent (isolated)
   → 检查是否需要预警 → 如出租率<80%，发送通知

6. 整合所有结果，返回给用户
```

```python
# Step 5: OrchestratorAgent 完整实现

class OrchestratorAgent:
    """数字员工主控Agent"""

    def __init__(self, soul_md, memory_md, tool_registry):
        self.soul = soul_md
        self.memory = memory_md
        self.tools = tool_registry
        self.subagents = {}
        self.audit_log = []
        self.conversation_history = []

    def register_subagent(self, name, agent):
        self.subagents[name] = agent

    def _log(self, action, details):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details
        }
        self.audit_log.append(entry)
        print(f'  📝 [{entry["timestamp"]}] {action}')

    def _intent_classification(self, message):
        """简易意图识别"""
        if "分析" in message or "报告" in message:
            return "data_analysis"
        elif "查询" in message or "查" in message:
            return "query"
        elif "通知" in message or "提醒" in message:
            return "notification"
        return "unknown"

    def handle_request(self, user_message, user_id="Jason"):
        """处理用户请求"""
        print(f'\n{"="*60}')
        print(f'👤 用户({user_id}): {user_message}')
        print(f'{"="*60}')

        # 1. 记录到短期记忆
        self.conversation_history.append({"role": "user", "content": user_message})
        self._log("user_request", {"user": user_id, "message": user_message})

        # 2. 意图识别
        intent = self._intent_classification(user_message)
        print(f'\n🧠 意图识别: {intent}')

        # 3. 路由
        if intent == "data_analysis":
            return self._handle_analysis(user_message)
        elif intent == "query":
            return self._handle_query(user_message)
        else:
            response = "抱歉，我目前支持数据分析和信息查询。请试试：'分析3F餐饮区域经营状况'"
            self.conversation_history.append({"role": "assistant", "content": response})
            return response

    def _handle_analysis(self, message):
        """处理分析类请求 - 多Agent协作"""
        print(f'\n🔄 启动多Agent协作流水线...')

        # Step 1: DataAgent
        print(f'\n  Step 1: DataAgent 收集数据')
        data_agent = self.subagents.get("data")
        data_result = data_agent.run(message)
        self._log("subagent_complete", {"agent": "DataAgent"})

        # Step 2: ReportAgent (fork)
        print(f'\n  Step 2: ReportAgent 生成报告')
        report_agent = self.subagents.get("report")
        report_result = report_agent.run(data_result, parent_context=str(data_result))
        self._log("subagent_complete", {"agent": "ReportAgent"})

        # Step 3: AlertAgent
        print(f'\n  Step 3: AlertAgent 检查预警')
        alert_agent = self.subagents.get("alert")
        alert_result = alert_agent.run(data_result)
        self._log("subagent_complete", {"agent": "AlertAgent"})

        # 整合结果
        final_response = report_result.get("report", "无报告")
        if alert_result.get("alert_sent"):
            final_response += f"\n\n⚠️ 已通过微信推送预警通知给Jason"

        self.conversation_history.append({"role": "assistant", "content": final_response})
        return final_response

    def _handle_query(self, message):
        """处理查询类请求"""
        for shop_id in ["3F-012", "3F-015", "B1-008"]:
            if shop_id in message:
                result = execute_tool("query_shop", {"shop_id": shop_id})
                self._log("tool_call", {"tool": "query_shop", "shop_id": shop_id})
                if result["status"] == "success":
                    d = result["data"]
                    response = f"🏪 商铺 {shop_id}\n面积: {d['area']}㎡\n业态: {d['business']}\n租户: {d['tenant']}\n月租金: ¥{d['rent']:,}"
                    self.conversation_history.append({"role": "assistant", "content": response})
                    return response
        response = "请提供具体的商铺编号，如3F-012"
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def get_audit_log(self):
        return self.audit_log


# ========== 完整搭建数字员工 ==========
print('🚀 正在搭建商管数字员工...\n')

agent = OrchestratorAgent(
    soul_md=SOUL_MD,
    memory_md=MEMORY_MD,
    tool_registry=TOOL_REGISTRY
)
agent.register_subagent("data", DataAgent())
agent.register_subagent("report", ReportAgent())
agent.register_subagent("alert", AlertAgent())

print('✅ 商管数字员工搭建完成!')
print(f'   - SOUL.md: {len(SOUL_MD)} 字符')
print(f'   - MEMORY.md: {len(MEMORY_MD)} 字符')
print(f'   - Tools: {list(TOOL_REGISTRY.keys())}')
print(f'   - SubAgents: {list(agent.subagents.keys())}')
```

```python
# 🎬 实战演示：数字员工处理真实请求

# Demo 1: 分析请求
response1 = agent.handle_request("帮我分析3F餐饮区域的经营状况")
print(f'\n🤖 数字员工回答:\n{response1}')

print('\n' + '─'*60 + '\n')

# Demo 2: 查询请求
response2 = agent.handle_request("查询商铺3F-012的信息")
print(f'\n🤖 数字员工回答:\n{response2}')
```

```python
# 📋 查看审计日志
print('📋 审计日志（Audit Trail）')
print('='*60)
for i, log in enumerate(agent.get_audit_log(), 1):
    print(f'{i}. [{log["timestamp"]}] {log["action"]}')
    print(f'   详情: {json.dumps(log["details"], ensure_ascii=False)[:100]}')
    print()
print(f'总日志条数: {len(agent.get_audit_log())}')
print('💡 对应Day5学到的审计轨迹：谁、什么时候、做了什么、结果如何')
```

```python
# 📊 可视化：数字员工架构图
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('商管数字员工架构图', fontsize=18, fontweight='bold', pad=20)

c_user = '#4ECDC4'
c_orch = '#FF6B6B'
c_soul = '#95E1D3'
c_sub = '#FDA085'
c_tool = '#A8DADC'

# 用户
ax.add_patch(plt.Circle((2, 5), 0.8, color=c_user, ec='black', lw=2))
ax.text(2, 5, '👤\n用户', ha='center', va='center', fontsize=11, fontweight='bold')

# OrchestratorAgent
ax.add_patch(plt.Rectangle((5.5, 3.5), 3, 3, color=c_orch, alpha=0.8, ec='black', lw=2))
ax.text(7, 5, '🎯\nOrchestrator\nAgent', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# SOUL.md
ax.add_patch(plt.Rectangle((5.5, 7.5), 1.3, 1.2, color=c_soul, ec='black', lw=1.5))
ax.text(6.15, 8.1, 'SOUL.md', ha='center', va='center', fontsize=9, fontweight='bold')

# MEMORY.md
ax.add_patch(plt.Rectangle((7.2, 7.5), 1.3, 1.2, color=c_soul, ec='black', lw=1.5))
ax.text(7.85, 8.1, 'MEMORY.md', ha='center', va='center', fontsize=9, fontweight='bold')

# SubAgents
sub_positions = [(10.5, 7.5), (10.5, 5), (10.5, 2.5)]
sub_labels = ['📊 DataAgent\n(isolated)', '📝 ReportAgent\n(fork)', '⚠️ AlertAgent\n(isolated)']
for (x, y), label in zip(sub_positions, sub_labels):
    ax.add_patch(plt.Rectangle((x-0.6, y-0.6), 1.8, 1.2, color=c_sub, alpha=0.8, ec='black', lw=1.5))
    ax.text(x+0.3, y, label, ha='center', va='center', fontsize=8)

# Tools
tool_positions = [(10.5, 0.8), (12.5, 0.8)]
tool_labels = ['🔧 query_shop', '🔧 send_notify']
for (x, y), label in zip(tool_positions, tool_labels):
    ax.add_patch(plt.Rectangle((x-0.3, y-0.3), 1.8, 0.6, color=c_tool, ec='black', lw=1))
    ax.text(x+0.6, y, label, ha='center', va='center', fontsize=7)

# 箭头
ax.annotate('', xy=(5.5, 5), xytext=(2.8, 5), arrowprops=dict(arrowstyle='->', lw=2, color='black'))
ax.annotate('', xy=(7, 7.5), xytext=(7, 6.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(9.9, 7.5), xytext=(8.5, 5.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
ax.annotate('', xy=(9.9, 5), xytext=(8.5, 5), arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
ax.annotate('', xy=(9.9, 2.5), xytext=(8.5, 4.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

# 审计日志
ax.add_patch(plt.Rectangle((3, 0.5), 3, 1.5, color='#FFF3CD', ec='black', lw=1.5))
ax.text(4.5, 1.25, '📋 审计日志\nAudit Trail', ha='center', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('/root/learning-notebooks/第7周/agent_architecture_day6.png', dpi=150, bbox_inches='tight')
plt.show()
print('✅ 架构图已保存')
```

# 🔄 Step 6：TaskFlow — 可追踪的多步工作流

> 对于复杂任务（超过3步），用TaskFlow管理状态和等待

## TaskFlow vs 简单工具链

| **特性** | **简单工具链** | **TaskFlow** |
| ------ | --------- | ------------ |
| 步骤数    | 1-3步      | 4+步          |
| 状态管理   | 无         | 持久化          |
| 错误恢复   | 从头重来      | 从断点恢复        |
| 人工介入   | 不支持       | 支持人审节点       |
| 典型场景   | 查询商铺      | 月度经营报告生成     |

### 💡 OpenClaw TaskFlow

```python
# TaskFlow典型流程
task = TaskFlow()
task.step("collect_data")    # 收集数据
task.step("analyze")         # 分析趋势
task.wait("human_review")    # 等待人审
task.step("generate_report") # 生成报告
task.step("send_notification")# 推送通知
```

```python
# Step 6: TaskFlow模拟实现

class TaskFlow:
    """简化的TaskFlow实现"""
    def __init__(self, name):
        self.name = name
        self.steps = []
        self.results = {}
        self.status = "pending"

    def add_step(self, step_name, handler, depends_on=None, wait_for=None):
        self.steps.append({
            "name": step_name,
            "handler": handler,
            "depends_on": depends_on or [],
            "wait_for": wait_for or [],
            "status": "pending"
        })

    def run(self):
        print(f'\n🔄 TaskFlow: {self.name}')
        print(f'   步骤数: {len(self.steps)}')
        print(f'   状态: running\n')
        self.status = "running"

        for step in self.steps:
            # 检查依赖
            skip = False
            for dep in step["depends_on"]:
                if self.results.get(dep, {}).get("status") != "success":
                    print(f'  ⏭️ 跳过 {step["name"]}（依赖 {dep} 未完成）')
                    skip = True
                    break
            if skip:
                continue

            # 检查等待
            if step["wait_for"]:
                print(f'  ⏸️ {step["name"]} 等待人工审核...')
                input_result = {"approved": True, "reviewer": "Jason"}
                step["review"] = input_result
                print(f'     ✅ 审核通过（{input_result["reviewer"]}）')

            # 执行
            print(f'  ▶️ 执行: {step["name"]}')
            try:
                result = step["handler"](self.results)
                step["status"] = "success"
                self.results[step["name"]] = {"status": "success", "data": result}
                print(f'     ✅ 完成')
            except Exception as e:
                step["status"] = "failed"
                self.results[step["name"]] = {"status": "failed", "error": str(e)}
                print(f'     ❌ 失败: {e}')

        self.status = "completed"
        print(f'\n✅ TaskFlow完成!')
        return self.results


# 定义一个月度报告TaskFlow
def collect_data(prev):
    return {"shops": 285, "occupied": 241, "revenue": 2850000}

def analyze(prev):
    data = prev.get("collect_data", {}).get("data", {})
    occ_rate = data.get("occupied", 0) / data.get("shops", 1) * 100
    return {"occupancy_rate": f"{occ_rate:.1f}%", "revenue": data.get("revenue")}

def generate_report(prev):
    analysis = prev.get("analyze", {}).get("data", {})
    return f"月度经营报告: 出租率{analysis.get('occupancy_rate')}, 总收入¥{analysis.get('revenue'):,}"

def send_notification(prev):
    report = prev.get("generate_report", {}).get("data", "")
    return execute_tool("send_notification", {
        "channel": "wechat",
        "recipient": "Jason",
        "message": report[:80],
        "priority": "medium"
    })


# 构建并运行TaskFlow
tf = TaskFlow("月度经营报告生成")
tf.add_step("collect_data", collect_data)
tf.add_step("analyze", analyze, depends_on=["collect_data"])
tf.add_step("human_review", lambda prev: {"approved": True}, depends_on=["analyze"], wait_for=["human"])
tf.add_step("generate_report", generate_report, depends_on=["human_review"])
tf.add_step("send_notification", send_notification, depends_on=["generate_report"])

results = tf.run()

print(f'\n📊 最终报告:')
print(results.get("generate_report", {}).get("data", "无"))
```

***

# ✏️ 课堂练习

## 练习1：扩展工具

在TOOL\_REGISTRY中添加一个新工具 `query_foot_traffic`（查询客流量），

参数包含 `shop_id`、`date_range`、`granularity`（小时/天/月）。

\
\💡 参考答案\

```python
TOOL_REGISTRY["query_foot_traffic"] = {
    "description": "查询指定商铺的客流量数据",
    "parameters": {
        "type": "object",
        "properties": {
            "shop_id": {"type": "string", "description": "商铺编号"},
            "date_range": {"type": "string", "description": "日期范围"},
            "granularity": {"type": "string", "enum": ["hour", "day", "month"]}
        }
    },
    "required": ["shop_id", "date_range"],
    "permissions": ["read:traffic"],
    "timeout_ms": 5000
}
```

\

## 练习2：设计客服数字员工

为一个购物中心设计一个「客服数字员工」，

写出它的 SOUL.md 四层结构（Identity/Rules/Constraints/Output）。

\
\💡 思考方向\

* Identity: 购物中心客服助手，面向顾客
* Rules: 常见问题优先KB查询，投诉转人工，导航给路线图
* Constraints: 不透露内部运营数据，不评论竞品
* Output: 简洁友好，带emoji，路线用文字+图片

\

***

# 📝 课后测试

**Q1**: 数字员工的 SOUL.md 四层结构是哪四层？

\\答案\
Identity（身份）→ Rules（规则）→ Constraints（约束）→ Output Format（输出格式）
\

**Q2**: 子Agent的 `isolated` 和 `fork` 上下文模式有什么区别？

\\答案\
\- isolated: 子Agent获得干净上下文，适合独立任务（如数据查询）

\- fork: 继承父Agent的对话历史，适合需要上下文的连续任务（如报告生成）
\

**Q3**: TaskFlow比简单工具链多了什么能力？

\\答案\
状态持久化、从断点恢复、支持人工审核节点、依赖管理
\

**Q4**: 为什么企业级数字员工必须有审计日志（Audit Trail）？

\\答案\
因为Agent输出是概率性的（非确定性），必须记录「谁、何时、做了什么、结果如何」
以便追溯责任、排查异常、满足合规要求。
\

**Q5**: 在今天的架构中，OrchestratorAgent的三个核心职责是什么？

\\答案\
1\. 意图识别与路由  2. 子Agent编排与调度  3. 结果整合与审计记录
\

***

# 🔑 英文术语（10个）

| **术语**                    | **音标**                    | **释义**                |
| ------------------------- | ------------------------- | --------------------- |
| **Orchestrator**          | /ˈɔːkɪstreɪtər/           | 编排器，统一入口和路由           |
| **Subagent**              | /sʌbˈeɪdʒənt/             | 子代理，被主Agent调度的专业Agent |
| **Audit Trail**           | /ˈɔːdɪt treɪl/            | 审计轨迹，完整操作记录链          |
| **Context Mode**          | /ˈkɒntekst moʊd/          | 上下文模式（isolated/fork）  |
| **TaskFlow**              | /tæsk floʊ/               | 任务流，多步骤可追踪工作流         |
| **Tool Registry**         | /tuːl ˈredʒɪstri/         | 工具注册表，管理所有可用工具的元数据    |
| **Intent Classification** | /ɪnˈtent ˌklæsɪfɪˈkeɪʃən/ | 意图分类/识别               |
| **Human-in-the-Loop**     | /ˈhjuːmən ðə luːp/        | 人工介入环节，如审核节点          |
| **Idempotency**           | /ˌaɪdəmˈpoʊtənsi/         | 幂等性，重复调用不产生副作用        |
| **Fallback**              | /ˈfɔːlbæk/                | 降级方案，主方案失败时的备用路径      |

***

# 🎬 推荐学习资源

## 📹 视频推荐

1. **B站：2025最新版大模型AI Agent入门到精通实战教程**
   * 链接：[https://www.bilibili.com/video/BV1SqKHeUEm5/](https://www.bilibili.com/video/BV1SqKHeUEm5/)
   * 简介：99集完整教程，涵盖Agent+RAG+LangGraph，从入门到项目实战
2. **B站：2025必会的Agent课程（应用解读+项目实战）**
   * 链接：[https://www.bilibili.com/video/BV1LhgSzrEgr/](https://www.bilibili.com/video/BV1LhgSzrEgr/)
   * 简介：20分钟搞懂AI Agent核心概念，72集系列覆盖应用场景和实战

## 📖 延伸阅读

1. **知乎：如何写好Agent的System Prompt?看这一篇就够了**
   * 链接：[https://zhuanlan.zhihu.com/p/1990950758582088647](https://zhuanlan.zhihu.com/p/1990950758582088647)
   * 简介：系统讲解System Prompt的结构化设计方法，含实战案例
2. **CSDN：AI Agent开发实战：30分钟搭建AI数字员工**
   * 链接：[https://blog.csdn.net/weixin\_43107715/article/details/157910358](https://blog.csdn.net/weixin_43107715/article/details/157910358)
   * 简介：基于LangChain+LLM快速搭建数字员工，涵盖感知-规划-执行-记忆四大模块

***

# 📊 今日总结

## ⚡ 实战成果

今天我们从零搭建了一个完整的商管数字员工原型，整合了本周Day1-5所有知识：

| **组件**        | **来源** | **实现方式**                             |
| ------------- | ------ | ------------------------------------ |
| SOUL.md       | Day1   | 定义身份、规则、约束、输出格式                      |
| MEMORY.md     | Day2   | 用户偏好 + 决策记录 + 语义搜索模拟                 |
| Tool Registry | Day3   | 商铺查询 + 租赁查询 + 通知发送                   |
| SubAgent      | Day4   | DataAgent + ReportAgent + AlertAgent |
| Audit Log     | Day5   | 完整操作记录，支持追溯                          |

## 🎯 关键收获

1. **数字员工 = 身份 + 记忆 + 工具 + 协作 + 监控**
2. **Orchestrator是核心**：意图识别 → 路由 → 编排 → 整合
3. **isolated vs fork**：独立任务用isolated，需要上下文用fork
4. **TaskFlow解决复杂流程**：状态持久化 + 断点恢复 + 人工审核
5. **审计日志是底线**：Agent的每一步都要可追溯

## 🔮 与LangChat/OpenClaw的映射

```
本notebook的概念      →  LangChat/OpenClaw中的对应
──────────────────────────────────────────────
SOUL.md               →  OpenClaw的System Prompt + AGENTS.md
MEMORY.md             →  OpenClaw的memory/*.md + memory_search
Tool Registry         →  MCP Tool定义 + Capability Registry
SubAgent              →  sessions_spawn (isolated/fork)
TaskFlow              →  OpenClaw TaskFlow skill
Audit Log             →  Orchestrator的trace/audit/metrics
```

***

## 📅 明天预告

> **Day 7（周日）：🔄 W7全面复习**回顾Day1-6所有知识，做一套综合测试，查漏补缺！

加油 Jason！💪🚀
