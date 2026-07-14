import json, os
from textwrap import dedent

path = '/root/learning-notebooks/第7周/第7周-Day2-工具编排与自动化.ipynb'
os.makedirs(os.path.dirname(path), exist_ok=True)

cells = []

def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": dedent(text).strip() + "\n"})

def code(text):
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": dedent(text).strip() + "\n"})

md('''
# 第7周 Day2：工具编排与自动化

> 目标：把 W5 的 Function Calling 概念，升级成可持续运行的真实工具链。

## 学习进度条
- W1-W6：已完成
- W7 Day1 System Prompt：已完成
- W7 Day2 工具编排与自动化：正在学习
- W7 Day3 多 Agent 协作：明日

本周进度：`[███░░░░░░░] 33%`

## 今日路线
1. 从 Function Calling 到工具编排
2. Cron 定时任务
3. 跨平台消息路由
4. 工作流设计
5. 事件驱动架构
6. Webhook 与 API 集成
7. 综合案例、练习与测试
''')

md('''
## 往期回顾

### 回顾 W5：Function Calling
W5 的核心链路是：用户请求 → LLM 选工具 → 生成参数 → 执行工具 → 返回结果 → 回复用户。

它解决的是“**一次请求，如何调一个工具**”。

### 回顾 Day1：System Prompt
Day1 学的是“**Agent 应该怎么思考、怎么约束自己**”。

### 今天的升级点
今天要把两者拼起来：
- System Prompt 负责定义行为规则
- Function Calling 负责单次工具使用
- 工具编排负责把多个工具、多个触发器、多个输出通道连成完整链路

一句话：**昨天定义大脑，今天搭建神经系统。**
''')

code('''
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False
print("使用字体:", font_name)
''')

md('''
## 1. 从 Function Calling 到工具编排

### 单工具调用
`用户消息 → LLM → 工具 → 结果 → 回复`

### 编排后的真实链路
`触发器 → 路由 → LLM判断 → 工具A → 工具B → 格式化 → 多通道推送`

### 五个层次
1. 单工具：一次请求调一次工具
2. 顺序链：A 的输出给 B
3. 条件分支：根据中间判断走不同路径
4. 并行执行：多个工具同时跑
5. 事件循环：持续监听、持续响应

这就是从“函数调用”到“自动化系统”的跃迁。
''')

code('''
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")
levels = [
    ("L0 单工具", 5.2, "#E3F2FD"),
    ("L1 顺序链", 4.2, "#E8F5E9"),
    ("L2 条件分支", 3.2, "#FFF3E0"),
    ("L3 并行执行", 2.2, "#F3E5F5"),
    ("L4 事件循环", 1.2, "#FFEBEE"),
]
for i, (name, y, color) in enumerate(levels):
    w = 4.5 + i * 0.6
    x = 5 - w / 2
    ax.add_patch(FancyBboxPatch((x, y - 0.25), w, 0.5, boxstyle="round,pad=0.08", fc=color, ec="#666"))
    ax.text(5, y, name, ha="center", va="center", fontsize=12, fontweight="bold")
    if i < len(levels) - 1:
        ax.annotate("", xy=(5, y - 0.45), xytext=(5, y - 0.75), arrowprops=dict(arrowstyle="->", lw=1.5))
ax.set_title("工具编排复杂度层次")
plt.show()
''')

md('''
## 2. Cron：定时任务与周期工作

Cron 是最经典的调度器。它适合：
- 每天早上自动推送
- 每周生成周报
- 每隔 30 分钟检查一次状态
- 延迟提醒和周期提醒

### Cron 五段式
`分 时 日 月 周`

### 例子
- `0 8 * * *`：每天 8 点
- `*/30 * * * *`：每 30 分钟
- `0 18 * * 1-5`：工作日 18 点

在 Agent 世界里，Cron 不是“脚本小技巧”，而是**自动化的起点**。
''')

code('''
def explain_cron(expr):
    m, h, d, mo, w = expr.split()
    return {"表达式": expr, "分钟": m, "小时": h, "日期": d, "月份": mo, "星期": w}

examples = [
    ("0 8 * * *", "AI日报"),
    ("*/30 * * * *", "半小时同步"),
    ("0 18 * * 1-5", "工作日提醒"),
    ("0 9 * * 1", "周一周报"),
]
for expr, name in examples:
    print(name, explain_cron(expr))
''')

code('''
fig, ax = plt.subplots(figsize=(11, 4))
tasks = {
    "AI日报": [8],
    "状态同步": [0, 6, 12, 18],
    "邮件检查": [9, 12, 15, 18, 21],
    "下班提醒": [18],
}
colors = ["#1976D2", "#388E3C", "#F57C00", "#D32F2F"]
for i, (name, pts) in enumerate(tasks.items()):
    y = len(tasks) - i
    ax.hlines(y, 0, 23, color="#ddd")
    ax.scatter(pts, [y] * len(pts), s=120, color=colors[i], label=name)
    ax.text(-0.8, y, name, va="center")
ax.set_xlim(-1, 23.5)
ax.set_ylim(0.5, len(tasks) + 0.5)
ax.set_xticks(range(0, 24, 2))
ax.set_yticks([])
ax.set_title("24 小时定时任务分布")
ax.legend(loc="upper right")
plt.show()
''')

md('''
## 3. 跨平台消息路由

真实世界里，消息不会只来自一个地方。

常见入口：微信、Telegram、Signal、邮件、Webhook。
常见出口：原路返回、转发到别的平台、同时广播到多个平台。

### 四种路由策略
1. 来源回传：从哪里来，就回哪里去
2. 规则路由：按紧急程度和类型决定去哪里
3. 广播路由：多个通道同时发
4. 智能路由：让 LLM 辅助选择目标通道
''')

code('''
from dataclasses import dataclass

@dataclass
class Msg:
    text: str
    source: str
    level: str

class Router:
    def route(self, msg):
        if "告警" in msg.text or msg.level == "高":
            targets = ["微信", "Telegram", "Signal"]
            tools = ["analyzer", "notify"]
            intent = "告警处理"
        elif "提醒" in msg.text:
            targets = [msg.source]
            tools = ["scheduler", "notify"]
            intent = "设置提醒"
        elif "新闻" in msg.text:
            targets = [msg.source, "邮件"]
            tools = ["web_search", "summary_llm"]
            intent = "新闻摘要"
        else:
            targets = [msg.source]
            tools = ["llm_chat"]
            intent = "通用对话"
        return {"意图": intent, "目标": targets, "工具": tools}

router = Router()
for m in [
    Msg("今天的AI新闻", "微信", "中"),
    Msg("明天早上提醒我开会", "Telegram", "中"),
    Msg("服务器告警：CPU 95%", "Signal", "高"),
]:
    print(m, "->", router.route(m))
''')

code('''
platforms = ["微信", "Telegram", "Signal", "邮件"]
scenes = ["普通消息", "AI日报", "告警", "提醒"]
data = np.array([
    [40, 8, 4, 10],
    [25, 12, 3, 18],
    [20, 15, 10, 5],
    [18, 6, 2, 8],
])
fig, ax = plt.subplots(figsize=(8, 4.5))
im = ax.imshow(data, cmap="YlOrRd")
ax.set_xticks(range(len(platforms)), platforms)
ax.set_yticks(range(len(scenes)), scenes)
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        ax.text(j, i, int(data[i, j]), ha="center", va="center", fontsize=9)
ax.set_title("多通道路由热力图")
plt.colorbar(im, ax=ax)
plt.show()
''')

md('''
## 4. 工作流设计：触发 → 处理 → 回复

工作流就是一条完整的执行链。

### 常见模式
- 线性管道：搜索 → 提取 → 总结 → 推送
- 条件分支：高优先级走升级流程
- 并行汇聚：同时查多个来源后合并
- 事件循环：长期监听，持续响应

### 状态视角
- IDLE：等待触发
- RUNNING：正在处理
- WAITING：等待外部结果
- SUCCESS：成功
- FAILED：失败

好的工作流要能重试、能观测、能解释。
''')

code('''
import time

class Workflow:
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps
        self.state = "IDLE"
    def run(self):
        print("工作流:", self.name)
        self.state = "RUNNING"
        for step in self.steps:
            print("- 执行", step)
            time.sleep(0.05)
        self.state = "SUCCESS"
        print("最终状态:", self.state)

Workflow("每日AI摘要", ["搜索", "提取", "总结", "格式化", "推送"]).run()
''')

code('''
fig, axs = plt.subplots(2, 2, figsize=(10, 7))
axs = axs.ravel()
for ax, title in zip(axs, ["线性", "分支", "并行", "循环"]):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title(title)

for x, t in [(1.3, "入"), (3.3, "搜"), (5.3, "总"), (7.3, "推")]:
    axs[0].add_patch(FancyBboxPatch((x, 2.4), 1.0, 0.8, boxstyle="round,pad=0.05", fc="#E3F2FD"))
    axs[0].text(x + 0.5, 2.8, t, ha="center", va="center")
for x in [2.35, 4.35, 6.35]:
    axs[0].annotate("", xy=(x + 0.7, 2.8), xytext=(x, 2.8), arrowprops=dict(arrowstyle="->"))

axs[1].text(2, 3, "输入")
axs[1].text(5, 3, "判断")
axs[1].text(8, 4.3, "高")
axs[1].text(8, 1.7, "低")
axs[1].annotate("", xy=(4.2, 3), xytext=(2.6, 3), arrowprops=dict(arrowstyle="->"))
axs[1].annotate("", xy=(7.2, 4.1), xytext=(5.6, 3.1), arrowprops=dict(arrowstyle="->"))
axs[1].annotate("", xy=(7.2, 1.9), xytext=(5.6, 2.9), arrowprops=dict(arrowstyle="->"))

axs[2].text(1.5, 3, "输入")
axs[2].text(8.2, 3, "汇总")
for y, t in [(4.5, "A"), (3, "B"), (1.5, "C")]:
    axs[2].text(4.5, y, t)
    axs[2].annotate("", xy=(4.1, y), xytext=(2.2, 3), arrowprops=dict(arrowstyle="->"))
    axs[2].annotate("", xy=(7.5, 3), xytext=(4.9, y), arrowprops=dict(arrowstyle="->"))

pts = [(2, 4.5), (5, 4.5), (8, 4.5), (8, 1.5), (5, 1.5), (2, 1.5)]
labels = ["触发", "处理", "输出", "等待", "监听", "就绪"]
for (x, y), t in zip(pts, labels):
    axs[3].text(x, y, t)
for i in range(len(pts)):
    x1, y1 = pts[i]
    x2, y2 = pts[(i + 1) % len(pts)]
    axs[3].annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->"))
plt.tight_layout()
plt.show()
''')

md('''
## 5. 事件驱动架构

传统请求响应是“用户来一下，我答一下”。

事件驱动则是：
- 消息到达，触发处理
- Cron 到点，触发处理
- Webhook 到来，触发处理
- 设备状态变化，触发处理

### 事件流水线
事件接收 → 过滤 → 意图识别 → 工具执行 → 结果推送

### 队列策略
- FIFO：先进先出
- 优先级队列：告警优先
- 限流：防止系统过载
- 死信队列：失败事件单独存放
''')

code('''
from collections import deque

class EventBus:
    def __init__(self):
        self.q = deque()
    def emit(self, t, payload):
        self.q.append((t, payload))
        print("入队:", t, payload)
    def run(self):
        while self.q:\n            t, payload = self.q.popleft()\n            print("处理:", t, "->", payload)

bus = EventBus()
bus.emit("message", "微信：今天天气")
bus.emit("timer", "8点日报")
bus.emit("webhook", "GitHub PR opened")
bus.run()
''')

code('''
hours = np.arange(24)
msg = 5 + 18 * np.exp(-0.5 * ((hours - 10) / 3) ** 2)
alert = 1 + 6 * np.exp(-0.5 * ((hours - 14) / 2) ** 2)
hook = 2 + 4 * np.exp(-0.5 * ((hours - 16) / 3) ** 2)
cron = np.zeros(24)
cron[[8, 9, 18]] = [10, 7, 9]
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.stackplot(hours, msg, alert, hook, cron, labels=["消息", "告警", "Webhook", "Cron"], alpha=0.85)
ax.set_title("24 小时事件来源分布")
ax.set_xlabel("小时")
ax.set_ylabel("事件量")
ax.legend(loc="upper right")
plt.show()
''')

md('''
## 6. Webhook 与 API 集成

### Webhook 是什么
不是你去拉数据，而是别人把事件推给你。

### 典型场景
- GitHub：新 PR、新 Issue
- 支付系统：支付成功
- 监控系统：错误上报
- 电商系统：订单变更

### 处理过程
1. 收到 HTTP 请求
2. 验证签名
3. 解析事件类型
4. 进入工作流
5. 调用工具并推送结果

### 安全点
必须考虑：签名、HTTPS、限流、输入校验、最小权限。
''')

code('''
import hmac
import hashlib
import json

class Hook:
    def __init__(self, secret="demo-secret"):
        self.secret = secret.encode()
    def sign(self, body):
        raw = json.dumps(body, ensure_ascii=False).encode()
        return hmac.new(self.secret, raw, hashlib.sha256).hexdigest()
    def handle(self, body, signature):
        expect = self.sign(body)
        ok = hmac.compare_digest(expect, signature)
        print("签名通过:" if ok else "签名失败:", body["event"])
        if ok:
            print("进入工作流 -> 分析 -> 推送")

hook = Hook()
body = {"event": "pull_request", "repo": "demo", "title": "fix bug"}
sig = hook.sign(body)
hook.handle(body, sig)
''')

code('''
labels = ["GitHub", "支付", "监控", "电商"]
values = [30, 18, 22, 12]
fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.bar(labels, values, color=["#24292e", "#635BFF", "#F23D3E", "#96BF48"])
for i, v in enumerate(values):
    ax.text(i, v + 0.5, v, ha="center")
ax.set_title("Webhook 事件量示意")
ax.set_ylabel("次数")
plt.show()
''')

md('''
## 7. 综合案例：Jason 的每日 AI 新闻推送

### 目标
每天早上 8 点，把 AI 新闻摘要推送到 Jason 的微信，方便手机朗读收听。

### 完整链路
Cron 触发 → 搜索新闻 → 提取正文 → LLM 总结 → 机会提示 → 格式化 → 微信推送

### 与前几周的关系
- W4：可接知识检索与背景材料
- W5：每一步都可能是 Function Calling
- W6：Agent 在关键节点做判断
- Day1：System Prompt 控制风格、边界、步骤顺序

这是一个最典型的“**从概念到真实工具链**”案例。
''')

code('''
class DailyNewsWorkflow:
    def run(self):
        news = [
            "OpenAI 发布新模型，推理成本下降",
            "Google 更新多模态能力，强调原生工具使用",
            "端侧 AI 继续升温，设备部署成新热点",
        ]
        print("08:00 Cron 触发")
        print("1. 搜索新闻")
        print("2. 提取正文")
        print("3. LLM 总结")
        print("4. 输出内容：")
        for i, n in enumerate(news, 1):
            print(f"  {i}. {n}")
        print("5. 微信推送给 Jason")

DailyNewsWorkflow().run()
''')

md('''
## 练习题

### 练习 1
写出下面场景的 Cron：
- 每天 18:00 推送日报
- 每周一 09:00 发周报
- 每 15 分钟检查一次状态

### 练习 2
设计一个“会议提醒助手”工作流：
- 触发器是什么？
- 要调哪些工具？
- 失败后如何处理？

### 练习 3
设计一个多通道路由规则：
- 普通消息：原路返回
- 高优先级告警：微信 + Telegram + Signal
- 正式报告：邮件 + 微信
''')

md('''
## 课后测试

### 选择题
1. `0 */3 * * *` 表示什么？
A. 每 3 分钟  B. 每 3 小时  C. 每月 3 日  D. 每周 3 次

2. 下列哪一个最像事件驱动架构？
A. 用户手动刷新页面
B. 定时轮询日志文件
C. GitHub 发生事件后主动推送给 Agent
D. 手工复制结果给同事

3. “扇出-汇聚”模式最适合什么？
A. 单个工具调用
B. 多个独立任务并行
C. 必须人工审批
D. 只有一个出口

### 判断题
4. Cron 是事件源的一种。（ ）
5. Webhook 不需要签名校验。（ ）
6. 工具编排就是 Function Calling 的别名，没有新增内容。（ ）

### 简答题
7. 说明 System Prompt、Function Calling、工具编排三者的关系。
8. 说明消息到达 → Agent 响应 → 结果推送这条链路属于哪种架构，为什么。
''')

code('''
print("参考答案")
print("1. B：每 3 小时")
print("2. C：外部系统主动推送事件")
print("3. B：多个独立任务并行后再合并")
print("4. 对")
print("5. 错，必须校验")
print("6. 错，工具编排包含调度、路由、状态和事件机制")
print("7. System Prompt 定规则，Function Calling 负责单次调用，工具编排把多次调用串成系统。")
print("8. 属于事件驱动架构，因为系统由事件触发，再进入自动处理和推送。")

print("\n英文术语表")
terms = [
    ("工具编排", "Tool Orchestration"),
    ("定时任务", "Cron Job"),
    ("消息路由", "Message Routing"),
    ("工作流", "Workflow"),
    ("事件驱动", "Event-Driven"),
    ("事件总线", "Event Bus"),
    ("Webhook", "Webhook"),
    ("应用程序接口", "API"),
    ("幂等性", "Idempotency"),
    ("死信队列", "Dead Letter Queue"),
]
for cn, en in terms:
    print(f"- {cn}: {en}")
''')

md('''
## 小结

今天 Jason 应该掌握的是：
- 什么时候需要 Cron，而不是手动触发
- 什么时候需要路由，而不是单通道回复
- 什么时候需要事件驱动，而不是同步阻塞
- 什么时候需要完整工作流，而不是单次 Function Calling

如果说 W5 让你学会“调用工具”，那 Day2 的目标就是：**让工具自己排队、自己协作、自己持续工作。**
''')

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"}
    },
    "cells": cells
}

with open(path, 'w', encoding='utf-8') as f:\n    json.dump(nb, f, ensure_ascii=False, separators=(',', ':'))

print(path)
print('cells', len(cells), 'md', sum(c['cell_type']=='markdown' for c in cells), 'code', sum(c['cell_type']=='code' for c in cells), 'size', os.path.getsize(path))
