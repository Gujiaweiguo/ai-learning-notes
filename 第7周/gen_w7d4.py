#!/usr/bin/env python3
"""Generate W7 Day 4 notebook using a cell-list approach that avoids quote conflicts."""
import json

cells = []

def _make_source(text):
    """Convert string to ipynb source format (list of lines with \\n)."""
    lines = text.split('\n')
    result = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            result.append(line + '\n')
        else:
            result.append(line)
    return result

def add_md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _make_source(text)})

def add_code(text):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": _make_source(text)})

# ============================================================
# Cell 1: matplotlib config (code, must be first)
# ============================================================
c1 = (
    "# W7 Day 4 - 多Agent协作模式\n"
    "# matplotlib 中文字体配置\n"
    "from matplotlib import font_manager\n"
    "import matplotlib.pyplot as plt\n"
    '\n'
    'font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"\n'
    "font_manager.fontManager.addfont(font_path)\n"
    "font_name = font_manager.FontProperties(fname=font_path).get_name()\n"
    'plt.rcParams["font.family"] = font_name\n'
    'plt.rcParams["axes.unicode_minus"] = False\n'
    '\n'
    'print(f"字体配置完成: {font_name}")\n'
    'print("本notebook覆盖：主Agent+子Agent编排、TaskFlow工作流、上下文传递（isolated vs fork）")\n'
)
add_code(c1)

# ============================================================
# Cell 2: Learning objectives (markdown)
# ============================================================
add_md("""# 🎯 今日学习目标 | 第7周-Day4：多Agent协作模式

> **本周主题：数字员工架构深化**
> **今日主题：从单打独斗到团队协作——多Agent编排的核心模式**

## 📋 今天要掌握的核心概念

| # | 概念 | 关键点 |
|---|------|--------|
| 1 | 主Agent + 子Agent模式 | Orchestrator-Worker 架构 |
| 2 | 任务分发与结果聚合 | 分而治之策略 |
| 3 | TaskFlow工作流 | 多步骤可追踪的持久化任务 |
| 4 | 上下文传递：isolated vs fork | 子Agent的"记忆边界" |
| 5 | Agent间通信协议 | 消息格式、状态同步 |

## 🗺 在架构师路线中的位置

```
Level 3 Agent Runtime ← 你在这里
    ├── Agent行为设计（Day1）
    ├── 记忆与语义检索（Day2）
    ├── 任务编排与工作流（Day3）
    ├── 多Agent协作模式（Day4）← 今天
    └── 评估与质量保障（Day5）
```

💡 **业务关联**：Orchestrator本身就是主Agent，LangChat的各个Capability就是它的子Agent。理解多Agent协作 = 理解Orchestrator的核心运行机制。""")

# ============================================================
# Cell 3: Past review (markdown)
# ============================================================
add_md("""# 🔄 往期回顾（W1-W7已学内容速览）

## W1-W2：Transformer与大模型训练
- ✅ 自注意力机制、Multi-Head Attention、位置编码
- ✅ 预训练→SFT→RLHF→DPO→QLoRA微调全链路

## W3：RAG与知识增强
- ✅ 向量检索、Embedding、高级RAG（混合检索、GraphRAG）

## W4：推理与思维链
- ✅ CoT、ToT、DeepSeek R1推理、Prompt工程

## W5-W6：Agent与工具使用实战
- ✅ Function Calling、ReAct模式、Agent安全、框架设计

## W7（本周）
- ✅ Day1：数字员工总览、SOUL.md、输出格式控制
- ✅ Day2：记忆三层结构、MEMORY.md持久化、语义搜索
- ✅ Day3：工具编排（单→多→自动）、Cron定时任务、跨平台消息路由
- 📍 **Day4（今天）：多Agent协作模式**

## 🔗 昨日核心知识点（Day3复习）

| 知识点 | 一句话回顾 |
|--------|-----------|
| 工具编排层级 | 单工具→多工具链→自动化工作流，逐步升级 |
| Cron定时任务 | 周期性执行、延迟提醒、类似Unix crontab |
| 消息路由 | 微信/Telegram/Signal多平台统一处理 |
| 事件驱动 | Agent不仅被动应答，还能主动触发任务 |""")

# ============================================================
# Cell 4: Core concept 1 - Orchestrator-Worker (markdown)
# ============================================================
add_md("""# 📚 今日新知识 Part 1：主Agent + 子Agent编排模式

## 1.1 为什么需要多Agent协作？

想象一个公司只有一个员工——他既要接电话、又要写报告、又要做财务。
虽然全能，但效率极低，而且容易出错。

**多Agent协作就是给"数字员工公司"招更多的人：**

```
单Agent模式（一个人干所有事）：
用户 → Agent（什么都做）→ 结果

多Agent模式（团队协作）：
用户 → 主Agent（项目经理）
         ├── 子Agent A（数据分析专家）
         ├── 子Agent B（报告撰写专家）
         └── 子Agent C（图表生成专家）
         → 整合结果 → 返回用户
```

### 🔑 核心概念：Orchestrator-Worker 模式

| 角色 | 类比 | 职责 |
|------|------|------|
| **主Agent（Orchestrator）** | 项目经理 | 理解需求、分解任务、分发、整合结果 |
| **子Agent（Worker）** | 各领域专家 | 执行具体任务、返回专业结果 |
| **消息总线** | 公司内部邮件系统 | Agent间通信、状态同步 |

### 💡 对应到OpenClaw/LangChat

```
OpenClaw（OrchestratorAgent = 主Agent）
    ├── sessions_spawn → 子Agent A（搜索任务）
    ├── sessions_spawn → 子Agent B（代码生成）
    └── sessions_spawn → 子Agent C（数据分析）

主Agent负责：
  1. 理解用户意图
  2. 决定需要哪些子Agent
  3. 分发任务
  4. 等待结果
  5. 整合后返回用户
```""")

# ============================================================
# Cell 5: Orchestrator-Worker code demo
# ============================================================
c5 = (
    '# 主Agent + 子Agent 编排流程演示\n'
    'print("=" * 60)\n'
    'print("    主Agent + 子Agent 编排流程")\n'
    'print("=" * 60)\n'
    'print()\n'
    'print("用户请求：分析上月销售数据并生成报告")\n'
    'print("  -> 主Agent(Orchestrator) 理解意图、分解任务")\n'
    'print("  -> 分发到子Agent：")\n'
    'print("     A1: 数据查询  (ChatBI)")\n'
    'print("     A2: SQL生成   (Text-to-SQL)")\n'
    'print("     A3: 图表生成  (可视化)")\n'
    'print("     A4: 报告撰写  (LLM生成)")\n'
    'print("  -> 主Agent 收集结果、冲突解决、整合")\n'
    'print("  -> 用户收到完整分析报告")\n'
    'print()\n'
    '\n'
    '# 任务分解的核心逻辑\n'
    'task_decomposition = {\n'
    '    "user_request": "分析上月销售数据并生成报告",\n'
    '    "main_agent": "OrchestratorAgent",\n'
    '    "sub_tasks": [\n'
    '        {\n'
    '            "task_id": "T1",\n'
    '            "description": "查询上月销售数据",\n'
    '            "assigned_to": "DataQueryAgent",\n'
    '            "tools_needed": ["chatbi.execute", "postgres.query"],\n'
    '            "timeout": 30,\n'
    '            "depends_on": []\n'
    '        },\n'
    '        {\n'
    '            "task_id": "T2",\n'
    '            "description": "生成数据可视化图表",\n'
    '            "assigned_to": "ChartAgent",\n'
    '            "tools_needed": ["matplotlib.generate", "image.upload"],\n'
    '            "timeout": 60,\n'
    '            "depends_on": ["T1"]\n'
    '        },\n'
    '        {\n'
    '            "task_id": "T3",\n'
    '            "description": "撰写分析报告",\n'
    '            "assigned_to": "ReportAgent",\n'
    '            "tools_needed": ["llm.generate", "doc.write"],\n'
    '            "timeout": 120,\n'
    '            "depends_on": ["T1", "T2"]\n'
    '        }\n'
    '    ]\n'
    '}\n'
    '\n'
    'print("任务分解示例：")\n'
    'import pprint\n'
    'pprint.pprint(task_decomposition, sort_dicts=False, width=60)\n'
)
add_code(c5)

# ============================================================
# Cell 6: Agent communication (markdown)
# ============================================================
add_md("""## 1.2 Agent间通信机制

### 三种通信模式

```
模式1：管道式（Pipeline）—— 串行传递
Agent A → 结果 → Agent B → 结果 → Agent C → 最终结果
适合：数据处理流水线（查询→分析→报告）

模式2：广播式（Broadcast）—— 并行执行
    ┌→ Agent A → 结果 ┐
主Agent → Agent B → 结果 → 主Agent（聚合）→ 最终结果
    └→ Agent C → 结果 ┘
适合：独立子任务（同时搜索多个数据源）

模式3：对话式（Dialog）—— 协商协作
Agent A ⇄ Agent B（多轮交互，互相补充）
适合：需要反复讨论的复杂任务（代码Review、方案优化）
```

### 消息格式标准化

```json
{
  "from": "OrchestratorAgent",
  "to": "DataQueryAgent",
  "type": "task_assignment",
  "task_id": "T1",
  "content": "查询2026年6月商管系统销售额",
  "context": {"month": "2026-06", "system": "商管"},
  "deadline": 30,
  "reply_to": "session_abc123"
}
```

💡 **对应LangChat**：LangChat的Capability调用本质上就是Agent间通信。knowledge.query → 返回结果 → workflow.execute → 返回结果 → 组合输出。""")

# ============================================================
# Cell 7: TaskFlow concept (markdown)
# ============================================================
add_md("""# 📚 今日新知识 Part 2：TaskFlow 多步骤可追踪工作流

## 2.1 什么是TaskFlow？

如果说主Agent+子Agent是"分工"，那TaskFlow就是"项目管理"。

**TaskFlow = 多步骤、可追踪、可恢复的持久化任务系统**

### 普通任务 vs TaskFlow

| 特性 | 普通任务（sessions_spawn） | TaskFlow |
|------|---------------------------|----------|
| 持续时间 | 几秒到几分钟 | 几分钟到几天 |
| 状态持久化 | ❌ 进程结束就没了 | ✅ 持久化到数据库 |
| 可恢复 | ❌ 失败需重跑 | ✅ 从断点恢复 |
| 可追踪 | ❌ 只看到最终结果 | ✅ 每一步都有状态 |
| 等待外部事件 | ❌ 不支持 | ✅ 支持等待用户回复、API回调 |
| 子任务管理 | ❌ 不支持 | ✅ 支持父子任务层级 |

### TaskFlow 的生命周期

```
创建（create）→ 等待中（waiting）→ 就绪（ready）→ 执行中（running）
                                                         │
                              ┌──────────────────────────┤
                              │                          │
                        暂停（paused）              失败（failed）
                          │                          │
                          └→ 恢复（running）         └→ 重试（running）
                                                         │
                                                         ▼
                                                   完成（completed）✅
```

### 💡 业务场景：商管月度报告生成

```
TaskFlow: 商管7月经营月报
├── Step 1: 数据收集 [completed]
│   ├── 查询销售额 [done]
│   ├── 查询客流量 [done]
│   └── 查询出租率 [done]
├── Step 2: 数据分析 [completed]
├── Step 3: 报告生成 [running]
│   ├── 生成图表 [done]
│   ├── 撰写分析 [working...]
│   └── 人审确认 [pending]
└── Step 4: 分发 [pending]
```""")

# ============================================================
# Cell 8: TaskFlow code demo
# ============================================================
c8 = (
    '# TaskFlow 工作流管理（概念演示）\n'
    '\n'
    'class TaskFlow:\n'
    '    """简化的TaskFlow实现，展示核心概念"""\n'
    '    \n'
    '    def __init__(self, name, owner=None):\n'
    '        self.name = name\n'
    '        self.owner = owner\n'
    '        self.tasks = {}\n'
    '        self.status = "created"\n'
    '        self.context = {}\n'
    '    \n'
    '    def add_task(self, task_id, description, depends_on=None):\n'
    '        self.tasks[task_id] = {\n'
    '            "id": task_id,\n'
    '            "description": description,\n'
    '            "depends_on": depends_on or [],\n'
    '            "status": "waiting",\n'
    '            "result": None,\n'
    '        }\n'
    '        dep_info = f"  依赖: {depends_on}" if depends_on else ""\n'
    '        print(f"  [+] 添加任务 [{task_id}]: {description}{dep_info}")\n'
    '    \n'
    '    def execute_task(self, task_id, result):\n'
    '        task = self.tasks[task_id]\n'
    '        task["status"] = "running"\n'
    '        task["result"] = result\n'
    '        task["status"] = "completed"\n'
    '        self.context[task_id] = result\n'
    '        print(f"  [v] [{task_id}] done: {result[:60]}...")\n'
    '    \n'
    '    def get_progress(self):\n'
    '        total = len(self.tasks)\n'
    '        completed = sum(1 for t in self.tasks.values()\n'
    '                       if t["status"] == "completed")\n'
    '        pct = completed / total * 100 if total else 0\n'
    '        return f"{completed}/{total} ({pct:.0f}%)"\n'
    '\n'
    '\n'
    '# === 创建商管月报 TaskFlow ===\n'
    'print("=== 创建 TaskFlow: 商管7月经营月报 ===")\n'
    'print()\n'
    'tf = TaskFlow("商管7月经营月报", owner="OrchestratorAgent")\n'
    'tf.add_task("T1_data", "收集销售数据")\n'
    'tf.add_task("T2_analysis", "数据分析与洞察", depends_on=["T1_data"])\n'
    'tf.add_task("T3_chart", "生成可视化图表", depends_on=["T1_data"])\n'
    'tf.add_task("T4_report", "撰写分析报告", depends_on=["T2_analysis", "T3_chart"])\n'
    'tf.add_task("T5_review", "人审确认", depends_on=["T4_report"])\n'
    'tf.add_task("T6_distribute", "分发报告", depends_on=["T5_review"])\n'
    '\n'
    'print()\n'
    'print("=== 执行阶段 ===")\n'
    'tf.execute_task("T1_data", "7月总销售额: 1.2亿, 客流量: 85万, 出租率: 92%")\n'
    'tf.execute_task("T2_analysis", "环比增长15%, 同比增长8%, 峰值出现在周末")\n'
    'tf.execute_task("T3_chart", "生成5张图表: 趋势图/热力图/对比图等")\n'
    'tf.execute_task("T4_report", "经营月报初稿: 销售强劲增长, 建议关注工作日客流")\n'
    '\n'
    'print(f"\\n整体进度: {tf.get_progress()}")\n'
    'print(f"上下文数据keys: {list(tf.context.keys())}")\n'
    'print(f"\\n剩余任务等待人审和分发...")\n'
)
add_code(c8)

# ============================================================
# Cell 9: isolated vs fork (markdown)
# ============================================================
add_md("""# 📚 今日新知识 Part 3：上下文传递 —— isolated vs fork

## 3.1 子Agent的"记忆边界"问题

> **子Agent需要知道多少主Agent的上下文？**

| 模式 | 类比 | 子Agent知道多少 |
|------|------|----------------|
| **isolated** | "你只需要知道任务本身" | ❌ 不知道项目背景、之前的对话 |
| **fork** | "这是完整的项目背景" | ✅ 知道所有上下文，包括之前的讨论 |

### 什么时候用哪种模式？

| 场景 | 推荐模式 | 理由 |
|------|----------|------|
| 搜索任务 | isolated | 搜索不需要知道对话历史 |
| 代码生成（基于之前讨论） | fork | 需要理解之前的设计讨论 |
| 独立数据处理 | isolated | 只需要输入数据 |
| 代码Review | fork | 需要理解代码的设计意图 |
| 并行探索多个方案 | isolated | 各方案独立，避免相互干扰 |
| 继续之前的工作 | fork | 需要之前的工作成果 |

### 💡 对应OpenClaw

```python
# OpenClaw 中的 isolated 模式（默认）
sessions_spawn(
    task="查询商管系统7月销售额TOP10",
    # context 省略 = isolated，子Agent只知道任务本身
)

# OpenClaw 中的 fork 模式
sessions_spawn(
    task="基于上面的讨论，帮我完善这个架构方案",
    context="fork"  # 子Agent获得当前对话的完整上下文
)
```

### 💡 对应LangChat

在LangChat的Skill编排中：
- **独立Skill** → isolated（如 data.query 独立执行查询）
- **上下文Skill** → fork（如 report.generate 需要之前步骤的结果）
- 设计Skill管线时，大部分用isolated，只在必要时用fork""")

# ============================================================
# Cell 10: isolated vs fork code demo
# ============================================================
c10 = (
    '# isolated vs fork 上下文差异演示\n'
    'print("=" * 60)\n'
    'print("    isolated vs fork 上下文传递对比")\n'
    'print("=" * 60)\n'
    '\n'
    '# 模拟主Agent的上下文\n'
    'main_context = {\n'
    '    "messages": [\n'
    '        {"role": "user", "content": "帮我分析商管系统的运营情况"},\n'
    '        {"role": "assistant", "content": "好的，我先查看一下数据..."},\n'
    '        {"role": "user", "content": "重点关注出租率和客流"},\n'
    '        {"role": "assistant", "content": "收到。出租率目前92%，客流..."},\n'
    '        {"role": "user", "content": "帮我做个深度分析报告"},\n'
    '    ],\n'
    '    "tools_called": ["data.query", "chart.generate"],\n'
    '    "artifacts": ["销售趋势图.png", "出租率对比.xlsx"],\n'
    '    "token_count": 4500\n'
    '}\n'
    '\n'
    'print(f"\\n主Agent上下文:")\n'
    'print(f"  对话轮数: {len(main_context[\'messages\'])}")\n'
    'print(f"  工具调用: {main_context[\'tools_called\']}")\n'
    'print(f"  Token数: ~{main_context[\'token_count\']}")\n'
    '\n'
    'print(f"\\n{\'-\'*50}")\n'
    'print("isolated 模式：")\n'
    'isolated_context = {\n'
    '    "task": "生成7月经营月报",\n'
    '    "data_input": "总销售额1.2亿，出租率92%，客流85万"\n'
    '}\n'
    'print(f"  子Agent看到的: {list(isolated_context.keys())}")\n'
    'print(f"  Token消耗: ~低")\n'
    'print(f"  [+] 干净高效，不受无关信息干扰")\n'
    '\n'
    'print(f"\\n{\'-\'*50}")\n'
    'print("fork 模式：")\n'
    'print(f"  子Agent看到的: 完整主Agent上下文 + 新任务")\n'
    'print(f"  包含对话历史: {len(main_context[\'messages\'])} 轮")\n'
    'print(f"  Token消耗: ~高")\n'
    'print(f"  [+] 上下文完整，理解\'之前的分析\'是什么")\n'
    '\n'
    'print(f"\\n{\'=\'*50}")\n'
    'print("模式选择决策矩阵：")\n'
    'decisions = [\n'
    '    ("搜索/查询任务", "isolated", "不需要历史对话"),\n'
    '    ("基于讨论的深度分析", "fork", "需要理解之前的设计意图"),\n'
    '    ("并行多方案探索", "isolated", "避免方案间相互污染"),\n'
    '    ("Review/审计", "fork", "需要完整上下文判断"),\n'
    '    ("简单工具调用", "isolated", "输入输出明确"),\n'
    '    ("多轮协作延续", "fork", "需要之前的讨论成果"),\n'
    ']\n'
    'for scenario, mode, reason in decisions:\n'
    '    print(f"  {scenario:20s} -> {mode:10s} ({reason})")\n'
)
add_code(c10)

# ============================================================
# Cell 11: Architecture diagram (code)
# ============================================================
c11 = (
    '# 多Agent协作三大模式可视化\n'
    'import matplotlib.pyplot as plt\n'
    'import matplotlib.patches as mpatches\n'
    'import numpy as np\n'
    '\n'
    'fig, axes = plt.subplots(1, 3, figsize=(20, 7))\n'
    'fig.suptitle("多Agent协作三大模式", fontsize=18, fontweight="bold", y=0.98)\n'
    '\n'
    'colors = {"main": "#FF6B6B", "sub": "#4ECDC4", "user": "#45B7D1", "result": "#96CEB4", "bg": "#FFF5E6"}\n'
    '\n'
    '# 模式1: Pipeline\n'
    'ax = axes[0]\n'
    'ax.set_xlim(0, 10); ax.set_ylim(0, 10)\n'
    'ax.set_title("Pipeline 管道式\\n(串行流水线)", fontsize=13, fontweight="bold")\n'
    'ax.set_facecolor(colors["bg"])\n'
    'circle = plt.Circle((1, 5), 0.6, color=colors["user"], ec="black", lw=2)\n'
    'ax.add_patch(circle); ax.text(1, 5, "用户", ha="center", va="center", fontsize=9, fontweight="bold")\n'
    'for x, label in [(3.5, "Agent A\\n数据查询"), (5.5, "Agent B\\n数据分析"), (7.5, "Agent C\\n报告生成")]:\n'
    '    rect = mpatches.FancyBboxPatch((x-0.6, 4.3), 1.2, 1.4, boxstyle="round,pad=0.1", color=colors["sub"], ec="black", lw=1.5)\n'
    '    ax.add_patch(rect); ax.text(x, 5, label, ha="center", va="center", fontsize=7, fontweight="bold")\n'
    'for x1, x2 in [(1.6, 2.9), (4.1, 4.9), (6.1, 6.9)]:\n'
    '    ax.annotate("", xy=(x2, 5), xytext=(x1, 5), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))\n'
    'ax.annotate("", xy=(9, 5), xytext=(8.1, 5), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))\n'
    'ax.text(9.3, 5, "结果", ha="center", va="center", fontsize=9, color=colors["result"], fontweight="bold")\n'
    'ax.text(5, 2, "每步依赖上一步，串行执行", ha="center", fontsize=9, color="#666", style="italic")\n'
    '\n'
    '# 模式2: Broadcast\n'
    'ax = axes[1]\n'
    'ax.set_xlim(0, 10); ax.set_ylim(0, 10)\n'
    'ax.set_title("Broadcast 广播式\\n(并行执行)", fontsize=13, fontweight="bold")\n'
    'ax.set_facecolor(colors["bg"])\n'
    'circle = plt.Circle((1, 5), 0.6, color=colors["user"], ec="black", lw=2)\n'
    'ax.add_patch(circle); ax.text(1, 5, "用户", ha="center", va="center", fontsize=9, fontweight="bold")\n'
    'rect = mpatches.FancyBboxPatch((2.8, 4), 1.4, 2, boxstyle="round,pad=0.1", color=colors["main"], ec="black", lw=2)\n'
    'ax.add_patch(rect); ax.text(3.5, 5, "主Agent\\n(聚合)", ha="center", va="center", fontsize=8, fontweight="bold", color="white")\n'
    'for y, label in [(7.5, "子Agent A\\n搜索"), (5, "子Agent B\\n分析"), (2.5, "子Agent C\\n图表")]:\n'
    '    rect = mpatches.FancyBboxPatch((6, y-0.6), 1.4, 1.2, boxstyle="round,pad=0.1", color=colors["sub"], ec="black", lw=1.5)\n'
    '    ax.add_patch(rect); ax.text(6.7, y, label, ha="center", va="center", fontsize=7, fontweight="bold")\n'
    '    ax.annotate("", xy=(6, y), xytext=(4.2, 5), arrowprops=dict(arrowstyle="->", lw=1.5, color="#666"))\n'
    'ax.annotate("", xy=(2.8, 5), xytext=(1.6, 5), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))\n'
    'ax.annotate("", xy=(9, 5), xytext=(4.2, 5), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))\n'
    'ax.text(9.3, 5, "结果", ha="center", va="center", fontsize=9, color=colors["result"], fontweight="bold")\n'
    'ax.text(5, 0.8, "子任务并行，主Agent聚合", ha="center", fontsize=9, color="#666", style="italic")\n'
    '\n'
    '# 模式3: Dialog\n'
    'ax = axes[2]\n'
    'ax.set_xlim(0, 10); ax.set_ylim(0, 10)\n'
    'ax.set_title("Dialog 对话式\\n(协商协作)", fontsize=13, fontweight="bold")\n'
    'ax.set_facecolor(colors["bg"])\n'
    'circle = plt.Circle((1, 5), 0.6, color=colors["user"], ec="black", lw=2)\n'
    'ax.add_patch(circle); ax.text(1, 5, "用户", ha="center", va="center", fontsize=9, fontweight="bold")\n'
    'for x, y, label in [(4, 7, "Agent A\\n(架构师)"), (4, 3, "Agent B\\n(Reviewer)")]:\n'
    '    rect = mpatches.FancyBboxPatch((x-0.7, y-0.7), 1.4, 1.4, boxstyle="round,pad=0.1", color=colors["sub"], ec="black", lw=1.5)\n'
    '    ax.add_patch(rect); ax.text(x, y, label, ha="center", va="center", fontsize=7, fontweight="bold")\n'
    'ax.annotate("", xy=(3.3, 6.3), xytext=(1.6, 5), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))\n'
    'rect = mpatches.FancyBboxPatch((7, 4), 1.4, 2, boxstyle="round,pad=0.1", color=colors["result"], ec="black", lw=2)\n'
    'ax.add_patch(rect); ax.text(7.7, 5, "最终方案\\n(共识)", ha="center", va="center", fontsize=8, fontweight="bold")\n'
    'ax.annotate("", xy=(7, 5), xytext=(4.7, 5), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))\n'
    'ax.text(5, 0.8, "多轮协商，达成共识后输出", ha="center", fontsize=9, color="#666", style="italic")\n'
    '\n'
    'plt.tight_layout(rect=[0, 0, 1, 0.95])\n'
    'plt.savefig("/root/learning-notebooks/第7周/w7d4-agent-patterns.png", dpi=150, bbox_inches="tight")\n'
    'plt.show()\n'
    'print("图表已保存")\n'
)
add_code(c11)

# ============================================================
# Cell 12: English terminology (markdown)
# ============================================================
add_md("""# 🔑 英文术语表（10个核心术语）

| # | 英文术语 | 音标 | 中文释义 | 记忆技巧 |
|---|---------|------|---------|---------|
| 1 | **Orchestrator** | /ˈɔːrkɪstreɪtər/ | 编排器、主控Agent | 想象交响乐团指挥（orchestra） |
| 2 | **Sub-agent** | /sʌbˈeɪdʒənt/ | 子代理、子Agent | sub（下级）+ agent（代理） |
| 3 | **Task Decomposition** | /tæsk ˌdiːkɑːmpəˈzɪʃən/ | 任务分解 | de（分开）+ composition（组成） |
| 4 | **Aggregation** | /ˌæɡrɪˈɡeɪʃən/ | 聚合、汇总 | aggregate = 聚集在一起 |
| 5 | **Isolated Context** | /ˈaɪsəleɪtɪd ˈkɑːntekst/ | 隔离上下文 | isolate（隔离）→ 子Agent看不到主Agent历史 |
| 6 | **Fork Context** | /fɔːrk ˈkɑːntekst/ | 分叉上下文 | fork（叉子）→ 从主Agent分叉出完整副本 |
| 7 | **TaskFlow** | /tæsk floʊ/ | 任务流 | task（任务）+ flow（流动） |
| 8 | **Pipeline** | /ˈpaɪplaɪn/ | 管道、流水线 | pipe（管子）+ line（线） |
| 9 | **Broadcast** | /ˈbrɔːdkæst/ | 广播、并行分发 | broad（广泛）+ cast（投掷） |
| 10 | **Checkpoint** | /ˈtʃekpɔɪnt/ | 检查点、断点 | check（检查）+ point（点） |

## 📝 术语造句练习

> "The **Orchestrator** uses **Task Decomposition** to split a complex request into sub-tasks.
> It then **Broadcasts** them to **Sub-agents** running in **Isolated Context**.
> Results are collected through **Aggregation** into a **Pipeline**.
> Each step has a **Checkpoint** for recovery, and the whole process is tracked via **TaskFlow**.""")

# ============================================================
# Cell 13: Practice exercises (markdown)
# ============================================================
add_md("""# ✏️ 课堂练习

## 练习1：识别协作模式（选择题）

**场景**：用户要求"帮我查一下三个竞品商城的出租率，然后做个对比分析"

这种任务最适合哪种协作模式？
- A. Pipeline（管道式）
- B. Broadcast（广播式）
- C. Dialog（对话式）

---

## 练习2：选择上下文模式

| 场景 | isolated / fork |
|------|----------------|
| "翻译这段话为英文" | ? |
| "基于我们刚才讨论的架构，画个图" | ? |
| "搜索2026年AI行业报告" | ? |
| "检查我上面写的代码有没有bug" | ? |

---

## 练习3：设计TaskFlow（动手题）

为一个"自动生成商管周报"的需求设计TaskFlow：
1. 从商管系统获取本周数据
2. 与上周数据对比分析
3. 生成图表
4. 人审确认
5. 发送到企业管理群

请写出任务列表（含依赖关系），标注哪些可以并行。""")

# ============================================================
# Cell 14: Practice answers (code)
# ============================================================
c14 = (
    '# 练习参考答案\n'
    'print("=== 练习1答案 ===")\n'
    'print("答案: B. Broadcast (广播式)")\n'
    'print("原因: 三个竞品的查询相互独立，可以并行执行")\n'
    'print("      主Agent同时分发三个查询任务，各自完成后聚合结果")\n'
    'print()\n'
    'print("=== 练习2答案 ===")\n'
    'answers = [\n'
    '    ("翻译这段话为英文", "isolated", "只需要待翻译的文本"),\n'
    '    ("基于讨论画图", "fork", "需要理解之前讨论的架构内容"),\n'
    '    ("搜索行业报告", "isolated", "搜索不需要对话历史"),\n'
    '    ("检查上面的代码", "fork", "需要看到之前的代码和讨论"),\n'
    ']\n'
    'for scene, mode, reason in answers:\n'
    '    print(f"  {scene:20s} -> {mode:10s} ({reason})")\n'
    'print()\n'
    'print("=== 练习3参考设计 ===")\n'
    'print("  T1: 获取本周数据 [无依赖]")\n'
    'print("  T2: 获取上周数据 [无依赖]  <-- T1,T2可并行!")\n'
    'print("  T3: 对比分析 [依赖T1,T2]")\n'
    'print("  T4: 生成图表 [依赖T3]")\n'
    'print("  T5: 撰写周报 [依赖T3,T4] <-- fork模式")\n'
    'print("  T6: 人审确认 [依赖T5] <-- 暂停等待")\n'
    'print("  T7: 发送到企业群 [依赖T6]")\n'
)
add_code(c14)

# ============================================================
# Cell 15: After-class test (markdown)
# ============================================================
add_md("""# 📝 课后测试

## Q1（基础题）主Agent的核心职责是什么？
A. 执行所有具体任务
B. 理解需求、分解任务、分发、整合结果
C. 只负责接收用户消息
D. 监控其他Agent的工作状态

## Q2（基础题）以下哪个是 isolated 模式的优点？
A. 上下文完整
B. Token消耗大
C. 干净、安全、Token少
D. 子Agent能理解全部对话历史

## Q3（应用题）你需要设计一个Agent来处理"用户退款"请求，流程包括：
查询订单 → 验证退款条件 → 计算退款金额 → 执行退款 → 发送通知
这个流程最适合用哪种Agent协作模式？为什么？

## Q4（思考题）在LangChat的架构中，以下场景分别对应哪种上下文模式？
- knowledge.query 查询知识库 → ?
- 基于之前查询结果生成报告 → ?
- 并行查询3个不同知识源 → ?
- 对之前生成的报告做Review → ?

## Q5（开放题）如果TaskFlow执行到第4步失败了，系统如何恢复？

---
📌 **提交答案**：直接回复你的答案，AI助手会帮你批改！""")

# ============================================================
# Cell 16: Recommended resources (markdown)
# ============================================================
add_md("""# 🎬 推荐学习资源

## 📺 视频教程（国内平台）

### 1. 多智能体协作 Agent开发实战教程
- **平台**: B站（哔哩哔哩）
- **链接**: https://search.bilibili.com/all?keyword=多智能体协作+Agent+开发
- **搜索关键词**: "多Agent协作"、"Multi-Agent LLM"
- **内容**: 多智能体协作架构、任务分发、结果聚合
- **适合**: 理解Orchestrator-Worker模式的实际运行

### 2. LangChain/AutoGen多智能体实战
- **平台**: B站（哔哩哔哩）
- **链接**: https://search.bilibili.com/all?keyword=LangChain+AutoGen+多智能体
- **搜索关键词**: "AutoGen 多Agent"、"LangGraph Agent编排"
- **内容**: AutoGen框架的多Agent对话、LangGraph的状态图工作流
- **适合**: 对比理解OpenClaw的Agent编排设计

## 📖 延伸阅读（国内平台）

### 1. 深入理解多Agent系统架构设计
- **平台**: 知乎
- **链接**: https://www.zhihu.com/search?type=content&q=多Agent协作+LLM+架构设计
- **搜索关键词**: "多Agent协作 LLM"、"Agent编排架构"
- **内容**: 多Agent通信协议、任务分配策略、冲突解决机制

### 2. AutoGen/LangGraph多智能体框架对比与实践
- **平台**: CSDN / 掘金
- **链接**: https://so.csdn.net/so/search?q=多Agent+编排+LangGraph+AutoGen
- **搜索关键词**: "Agent编排 Python实战"
- **内容**: 主流多Agent框架对比、Python代码实战

> ⚠️ **提示**: 平台内容更新频繁，建议直接点击搜索链接，选择2024-2025年发布的最新内容。""")

# ============================================================
# Cell 17: Progress bar (code)
# ============================================================
c17 = (
    '# 学习进度条（18周总览）\n'
    'weeks = [\n'
    '    ("W1", "Transformer与大模型训练", "done"),\n'
    '    ("W2", "预训练/SFT/RLHF/DPO/QLoRA", "done"),\n'
    '    ("W3", "RAG与知识增强", "done"),\n'
    '    ("W4", "推理与思维链", "done"),\n'
    '    ("W5", "Agent与工具使用", "done"),\n'
    '    ("W6", "LLM Agent实战", "done"),\n'
    '    ("W7", "数字员工架构深化", "current"),\n'
    '    ("W8", "AI基础补强", "todo"),\n'
    '    ("W9", "MCP协议深入", "todo"),\n'
    '    ("W10", "Agent Runtime进阶", "todo"),\n'
    '    ("W11", "AI Compiler", "todo"),\n'
    '    ("W12", "Capability Platform", "todo"),\n'
    '    ("W13", "ChatBI与数据分析", "todo"),\n'
    '    ("W14", "企业权限与安全", "todo"),\n'
    '    ("W15", "RL与优化", "todo"),\n'
    '    ("W16", "商业地产视觉AI", "todo"),\n'
    '    ("W17", "前沿与部署", "todo"),\n'
    '    ("W18", "脑科学精华", "todo"),\n'
    ']\n'
    '\n'
    'print("=" * 60)\n'
    'print("  企业AI平台架构师学习路线（18周）")\n'
    'print("=" * 60)\n'
    'completed = 0\n'
    'for week, topic, status in weeks:\n'
    '    if status == "done":\n'
    '        icon = "[v]"\n'
    '        completed += 1\n'
    '    elif status == "current":\n'
    '        icon = ">>"\n'
    '    else:\n'
    '        icon = "[ ]"\n'
    '    print(f"  {week:4s} {icon} {topic}")\n'
    '\n'
    'total = len(weeks)\n'
    'pct = completed / total * 100\n'
    'print(f"\\n  总进度: {completed}/{total}周 ({pct:.0f}%)")\n'
    'print(f"  当前: 第7周 第4天（周四）")\n'
    'print(f"  Level: Level 3 Agent Runtime")\n'
    '\n'
    'bar_width = 40\n'
    'filled = int(bar_width * completed / total)\n'
    'bar = "=" * filled + ">" + "." * (bar_width - filled - 1)\n'
    'print(f"\\n  [{bar}]")\n'
    'print(f"  {pct:.0f}% 完成 | 你在这里 >")\n'
)
add_code(c17)

# ============================================================
# Cell 18: Knowledge chain (markdown)
# ============================================================
add_md("""# 🔗 知识串联：多Agent协作在架构中的位置

## 从单Agent到多Agent的演进

```
W5-W6：单Agent + Function Calling → "一个Agent用多个工具"
    ↓
W7 Day1-3：Agent行为 + 记忆 + 工具编排 → "数字员工有了人格和记忆"
    ↓
W7 Day4（今天）：多Agent协作 → "多个数字员工组成团队"
    ↓
W7 Day5（明天）：评估与质量保障 → "怎么确保团队输出质量？"
    ↓
W9：MCP协议 → "Agent之间用什么协议通信？"
    ↓
W10：Agent Runtime进阶 → "OpenClaw vs Hermes运行时设计"
```

## 💡 核心洞察：Orchestrator就是"超级主Agent"

```
OpenClaw = 终极Orchestrator（主Agent）
    ├── Session管理 = 对话上下文管理
    ├── Channel = 多平台消息入口
    ├── Skill = 可插拔的能力（相当于子Agent）
    ├── sessions_spawn = 创建子Agent
    ├── sessions_yield = 等待子Agent完成
    ├── Cron = 定时任务调度
    └── Memory = 持久化记忆
```

**OpenClaw的设计就是多Agent协作的最佳实践！**""")

# ============================================================
# Cell 19: Summary (markdown)
# ============================================================
add_md("""# 📝 今日总结

## 🎯 一句话总结
> **多Agent协作 = 主Agent（理解+分发+整合）+ 子Agent（专业执行）+ TaskFlow（可追踪工作流）+ 上下文管理（isolated/fork）**

## 🔑 今日5大收获

| # | 知识点 | 核心要点 |
|---|--------|---------|
| 1 | Orchestrator-Worker模式 | 主Agent管"what"，子Agent管"how" |
| 2 | 三种通信模式 | Pipeline（串行）、Broadcast（并行）、Dialog（协商） |
| 3 | TaskFlow工作流 | 持久化、可追踪、可恢复、支持人审节点 |
| 4 | isolated vs fork | isolated=干净高效，fork=上下文完整 |
| 5 | Agent间消息格式 | from/to/type/content/context标准化 |

## 🚀 明日预告：Day 5 - 评估体系与质量保障
- Agent输出质量怎么评估？
- 三层护栏设计：Prompt护栏 → 工具护栏 → 流程护栏
- 监控与日志：审计轨迹、异常检测、人工介入

## 💡 思考题（选做）
> 如果你要为LangChat设计一个多Agent协作场景，处理"用户问：帮我分析这个商场近半年的经营状况"，你会怎么设计Agent团队？""")

# ============================================================
# Build notebook
# ============================================================
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.0"},
        "title": "第7周-Day4-多Agent协作模式"
    },
    "cells": cells
}

output_path = "/root/learning-notebooks/第7周/第7周-Day4-多Agent协作模式.ipynb"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print(f"Notebook generated: {output_path}")
print(f"Total cells: {len(cells)}")
md_count = sum(1 for c in cells if c['cell_type'] == 'markdown')
code_count = sum(1 for c in cells if c['cell_type'] == 'code')
print(f"  markdown: {md_count}, code: {code_count}")

# Validate JSON
with open(output_path, 'r') as f:
    json.load(f)
print("JSON validation passed!")
