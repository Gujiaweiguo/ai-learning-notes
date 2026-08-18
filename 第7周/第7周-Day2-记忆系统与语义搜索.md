# 第7周-Day2：记忆系统与语义搜索

> 背景：Jason 已学完 W1-W6 大模型理论，W7 Day1 刚学完 System Prompt。
>
> 本周主线：**Prompt → 记忆 → 工具 → Skill → MCP**

## 今日目标

* 理解 Agent 记忆的三层结构
* 掌握 `MEMORY.md` 与 `memory/*.md` 的组织方式
* 理解语义搜索、embedding 与相似度匹配
* 用模拟代码串起跨会话记忆、用户画像与遗忘策略

## 往期回顾：W3 RAG 检索

RAG 的核心链路是：**切块 → embedding → 检索 → 拼接上下文 → 生成**。

今天的 Agent 记忆系统，本质上是在做同一件事，只是检索对象从“外部文档”换成了“历史对话、偏好和事件”。

| **W3 RAG** | **W7 记忆**                |
| ---------- | ------------------------ |
| 文档切块       | MEMORY.md / memory/\*.md |
| 向量化        | 向量化记忆条目                  |
| 语义检索       | 召回相关历史信息                 |
| 上下文拼接      | 注入当前会话                   |

```python
# matplotlib 中文字体配置（必须是第一段代码）
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np
import json

font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()

plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

print("使用字体:", font_name)

```

```python
# 学习进度条：W1-W6 完成，W7 进行中，共 15 周
weeks = [f"W{i}" for i in range(1, 16)]
status = ["done"] * 6 + ["doing"] + ["todo"] * 8
colors = {"done": "#4CAF50", "doing": "#FFB74D", "todo": "#E0E0E0"}

fig, ax = plt.subplots(figsize=(13, 2.4))
for idx, (week, st) in enumerate(zip(weeks, status)):
    ax.barh(0, 1, left=idx, height=0.62, color=colors[st], edgecolor="white")
    ax.text(idx + 0.5, 0, week, ha="center", va="center", fontsize=10, color="#222")

ax.set_xlim(0, 15)
ax.set_yticks([])
ax.set_xticks([])
ax.set_title("W1-W15 学习进度：W1-W6 已完成，W7 进行中", fontsize=14, pad=14)
ax.text(0, -0.9, "已完成 6/15 | 进行中 1/15 | 计划总周数 15", fontsize=11)
ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
plt.tight_layout()
plt.show()

```

## 1. Agent 记忆的三个层次

1. **短期记忆**：上下文窗口，最实时，但容量最小。
2. **中期记忆**：会话历史，承接同一轮会话里的重要事实。
3. **长期记忆**：外部存储，能跨会话持续保留。

关键点：不是所有信息都该写入长期记忆，真正要沉淀的是稳定偏好、长期事实和可复用结论。

```python
# Agent 记忆三层可视化
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

layers = [
    ("短期记忆上下文窗口", 7.6, "#E3F2FD", "#1565C0", "只保留当前对话片段"),
    ("中期记忆会话历史", 5.1, "#E8F5E9", "#2E7D32", "保留一段会话中的关键事实"),
    ("长期记忆外部存储", 2.6, "#FFF3E0", "#EF6C00", "写入 MEMORY.md / memory/*.md"),
]

for title, y, bg, fg, desc in layers:
    box = FancyBboxPatch((1.0, y - 0.7), 8.0, 1.2, boxstyle="round,pad=0.15", facecolor=bg, edgecolor=fg, linewidth=2)
    ax.add_patch(box)
    ax.text(1.4, y + 0.2, title, fontsize=14, fontweight="bold", color=fg, va="center")
    ax.text(1.4, y - 0.35, desc, fontsize=11, color="#333", va="center")

ax.annotate("", xy=(5, 6.1), xytext=(5, 6.9), arrowprops=dict(arrowstyle="->", lw=2, color="#666"))
ax.annotate("", xy=(5, 3.5), xytext=(5, 4.3), arrowprops=dict(arrowstyle="->", lw=2, color="#666"))
ax.text(5.3, 6.5, "向下沉淀", fontsize=10, color="#666")
ax.text(5.3, 3.9, "持久保存", fontsize=10, color="#666")
ax.text(5, 9.2, "记忆分层：越往下越稳定，越往上越实时", ha="center", fontsize=15, fontweight="bold")
plt.tight_layout()
plt.show()

```

## 2. `MEMORY.md`：持久化记忆文件格式

`MEMORY.md` 适合放“稳定、经常会用到、值得长期保留”的内容。

推荐结构：

* 用户偏好
* 项目事实
* 长期结论
* 重要约束

读写策略：先检索，再补写；先去重，再更新；先沉淀稳定事实，再过滤临时噪声。

```python
# MEMORY.md 文件模拟
memory_md = '''# Memory

## 用户偏好
- 回答优先中文
- 解释要短，先结论后展开
- 喜欢表格和清单

## 项目事实
- Jason 已学完 W1-W6 大模型理论
- W7 Day1 已学 System Prompt
- 本周主线：Prompt → 记忆 → 工具 → Skill → MCP

## 长期结论
- 适合沉淀稳定偏好，不适合塞入临时噪声
'''

def parse_sections(text):
    sections = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif line.startswith("- ") and current:
            sections[current].append(line[2:].strip())
    return sections

sections = parse_sections(memory_md)
print("解析到的章节:", list(sections))
for name, items in sections.items():
    print(f"[{name}]", " | ".join(items))

def append_memory(text, section, item):
    lines = text.splitlines()
    output = []
    inserted = False
    for idx, line in enumerate(lines):
        output.append(line)
        if line.strip() == f"## {section}":
            j = idx + 1
            while j < len(lines) and lines[j].startswith("- "):
                output.append(lines[j])
                j += 1
            output.append(f"- {item}")
            output.extend(lines[j:])
            inserted = True
            break
    return "\n".join(output) if inserted else text + f"\n- {item}"

updated = append_memory(memory_md, "用户偏好", "喜欢示例代码和图表")
print("\n更新后的 MEMORY.md 片段：\n")
print("\n".join(updated.splitlines()[:14]))
```

## 3. `memory/*.md`：分类记忆文件

当记忆越来越多时，单个 `MEMORY.md` 会变厚，于是可以拆成分类文件：

* `preferences.md`
* `facts.md`
* `projects.md`
* `decisions.md`

这样做的好处是：更容易检索、更容易更新、也更容易控制过期。

```python
# memory/*.md 分类组织
from collections import defaultdict

files = {
    "preferences.md": ["中文回答", "简洁", "表格"],
    "projects.md": ["W7 学习笔记", "Notebooks"],
    "facts.md": ["Jason 学完 W1-W6", "W7 Day1 System Prompt"],
    "decisions.md": ["先结论后展开", "重要信息写入长期记忆"],
}

topic_index = defaultdict(list)
for filename, tags in files.items():
    for tag in tags:
        topic_index[tag].append(filename)

print("目录式组织：")
for filename, tags in files.items():
    print(f"- {filename}: {', '.join(tags)}")

print("按主题反查：")
for tag in ["中文回答", "W7 Day1 System Prompt", "简洁"]:
    print(f"{tag} -> {topic_index[tag]}")

```

## 4. 语义搜索：embedding + 相似度匹配

语义搜索不是按字面完全匹配，而是把文本变成向量，再比较“意思有多像”。

核心步骤：

* 文本 → embedding
* 查询向量 ↔ 记忆向量
* 用 cosine similarity 排序

这就是 Agent 记忆能“找回旧对话”的底层方法。

```python
# 语义搜索：embedding + cosine similarity
import numpy as np

def embed(text):
    vocab = ["中文", "简洁", "表格", "System Prompt", "记忆", "RAG", "工具", "偏好"]
    vec = np.zeros(len(vocab), dtype=float)
    lowered = text.lower()
    for i, token in enumerate(vocab):
        if token.lower() in lowered:
            vec[i] = 1.0
    return vec

def cosine(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if denom == 0 else float(np.dot(a, b) / denom)

docs = [
    {"id": "m1", "text": "Jason 喜欢中文、简洁回答和表格"},
    {"id": "m2", "text": "W7 Day1 学过 System Prompt"},
    {"id": "m3", "text": "W3 学过 RAG 检索与 embedding"},
    {"id": "m4", "text": "记忆适合写入长期外部存储"},
]

query = "记住我更喜欢中文简洁回答"
q_vec = embed(query)

ranked = []
for doc in docs:
    score = cosine(q_vec, embed(doc["text"]))
    ranked.append((doc["id"], doc["text"], round(score, 3)))

ranked.sort(key=lambda x: x[-1], reverse=True)
print("查询:", query)
for item in ranked:
    print(item)

top = ranked[0]
print("最相关记忆:", top[1])

```

## 5. 跨会话记忆与用户画像

跨会话记忆的关键不是“存下来”，而是“下次还能找回来”。

用户画像会从多轮对话里慢慢积累，例如：

* 语言偏好
* 输出风格
* 信息密度
* 常见任务类型

画像越稳定，Agent 的个性化就越自然。

```python
# 跨会话记忆与用户画像积累
sessions = {
    "session-A": ["中文回答", "简洁", "喜欢表格"],
    "session-B": ["W3 RAG 理论", "embedding", "cosine similarity"],
    "session-C": ["W7 Day1 System Prompt", "希望 Notebook 结构清晰"],
}

profile = {"language": 0, "style": 0, "format": 0, "deepness": 0}

signals = {
    "中文": ("language", 1),
    "简洁": ("style", 1),
    "表格": ("format", 1),
    "结构清晰": ("deepness", 1),
}

for session, items in sessions.items():
    for item in items:
        for keyword, (slot, weight) in signals.items():
            if keyword in item:
                profile[slot] += weight

print("跨会话汇总:")
for k, v in profile.items():
    print(f"- {k}: {v}")

new_query = "这个用户回答风格偏好是什么"
memory_bank = [
    "用户喜欢中文回答",
    "用户喜欢简洁输出",
    "用户喜欢表格",
    "用户在 W7 Day1 学过 System Prompt",
]
print("新会话问题:", new_query)
print("可直接召回的历史信息:")
for item in memory_bank:
    print("-", item)

```

## 6. 记忆的更新与遗忘

记忆系统要同时解决两个问题：

1. 该记什么
2. 该忘什么

一般来说：

* 稳定偏好、长期事实、重复出现的任务模式，优先保留
* 临时状态、一次性细节、低价值噪声，尽快衰减

```python
# 记忆更新与遗忘：衰减与阈值
days = np.arange(0, 31)
importance = np.exp(-days / 10)
threshold = 0.25

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(days, importance, color="#1565C0", lw=2.5, label="记忆价值")
ax.axhline(threshold, color="#D32F2F", ls="--", lw=2, label="过期阈值")
ax.fill_between(days, importance, threshold, where=importance >= threshold, color="#90CAF9", alpha=0.3)

for day in [0, 7, 14, 21, 28]:
    ax.scatter(day, importance[day], color="#FF9800", zorder=3)
    ax.text(day, importance[day] + 0.04, f"D{day}", ha="center", fontsize=9)

ax.set_title("记忆价值随时间衰减（示意）")
ax.set_xlabel("天数")
ax.set_ylabel("保留价值")
ax.set_xlim(0, 30)
ax.set_ylim(0, 1.05)
ax.legend()
plt.tight_layout()
plt.show()

print("保留规则：高频、稳定、可复用的信息保留；临时噪声、一次性细节快速遗忘。")

```

## 7. 与 W3 RAG 的关系

RAG 的 embedding + 检索，直接启发了 Agent 记忆的语义搜索。

区别在于：

* RAG 面向“外部知识”
* 记忆系统面向“内部历史”

它们共享同一套检索思想，只是数据源不同。

```python
# 与 W3 RAG 检索理论的关联
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(12, 5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 6)
ax.axis("off")

boxes = [
    (0.6, 3.2, 2.6, 1.4, "W3 RAG文档切块 → embedding → 检索"),
    (4.2, 3.2, 3.0, 1.4, "共同核心向量表示 + 相似度匹配"),
    (8.2, 3.2, 3.0, 1.4, "W7 记忆系统MEMORY.md → 语义搜索 → 召回"),
]

for x, y, w, h, label in boxes:
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", facecolor="#E8F5E9", edgecolor="#2E7D32", linewidth=2)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=11)

ax.annotate("", xy=(4.1, 4.0), xytext=(3.2, 4.0), arrowprops=dict(arrowstyle="->", lw=2, color="#666"))
ax.annotate("", xy=(8.1, 4.0), xytext=(7.3, 4.0), arrowprops=dict(arrowstyle="->", lw=2, color="#666"))
ax.text(6, 2.1, "RAG 的检索范式，直接迁移到 Agent 记忆：只是数据源从文档变成历史对话与偏好。", ha="center", fontsize=12)
plt.tight_layout()
plt.show()

```

## 8. OpenClaw vs Hermes Agent 记忆系统对比

按题目描述整理：

* **OpenClaw**：`MEMORY.md` + `memory/*.md` + 语义搜索召回
* **Hermes**：Honcho 用户建模 + FTS5 + LLM 摘要

可以把它理解为：一个偏“显式持久记忆”，一个偏“建模 + 摘要 + 传统检索”的组合。

```python
# OpenClaw vs Hermes Agent 记忆系统对比（示意评分）
dimensions = ["持久化", "语义检索", "用户建模", "摘要压缩", "跨会话召回"]
openclaw = [5, 5, 4, 3, 5]
hermes = [4, 3, 5, 5, 4]

x = np.arange(len(dimensions))
width = 0.36

fig, ax = plt.subplots(figsize=(12, 5.5))
ax.bar(x - width/2, openclaw, width, label="OpenClaw", color="#1565C0")
ax.bar(x + width/2, hermes, width, label="Hermes", color="#EF6C00")

ax.set_xticks(x)
ax.set_xticklabels(dimensions)
ax.set_ylim(0, 6)
ax.set_ylabel("示意评分")
ax.set_title("OpenClaw vs Hermes Agent 记忆系统对比（按题目描述整理）")
ax.legend()

for i, v in enumerate(openclaw):
    ax.text(i - width/2, v + 0.08, str(v), ha="center", fontsize=9)
for i, v in enumerate(hermes):
    ax.text(i + width/2, v + 0.08, str(v), ha="center", fontsize=9)

plt.tight_layout()
plt.show()

print("Hermes 侧重点：Honcho 用户建模 + FTS5 + LLM 摘要。")
print("OpenClaw 侧重点：MEMORY.md + memory/*.md + 语义搜索召回。")

```

## 🎬 推荐学习资源

### 📹 视频推荐

1. **Building Agentic RAG with LlamaIndex — Jerry Liu**（约1小时）

[https://www.deeplearning.ai/courses/building-agentic-rag-with-llamaindex](https://www.deeplearning.ai/courses/building-agentic-rag-with-llamaindex)

> 简介：深入讲解 RAG 中的向量检索、语义搜索和 Agent 自主决策机制

2. **LangChain RAG 从入门到实战**（40分钟）

[https://www.bilibili.com/video/BV1GJ411x7h7/](https://www.bilibili.com/video/BV1GJ411x7h7/)

> 简介：从文档加载到向量检索的完整 RAG 流水线搭建

### 📖 延伸阅读

1. **LangSmith Evaluation 文档**[https://docs.langchain.com/langsmith/evaluation-concepts](https://docs.langchain.com/langsmith/evaluation-concepts)

> 简介：如何量化评估 RAG 检索质量和 Agent 回答准确性，含评测框架设计

2. **Self-RAG: Learning to Retrieve, Generate, and Critique（论文）**[https://arxiv.org/abs/2310.11511](https://arxiv.org/abs/2310.11511)

> 简介：Meta 提出的 Self-RAG 框架，让 LLM 自主判断何时检索、如何反思生成质量

## 英文术语表

| **术语**            | **解释**        |
| ----------------- | ------------- |
| Persistent Memory | 持久化记忆         |
| Semantic Search   | 语义搜索          |
| Embedding         | 向量表示          |
| Context Window    | 上下文窗口         |
| User Profile      | 用户画像          |
| FTS5              | SQLite 全文检索引擎 |
| RAG Retrieval     | RAG 检索        |
| Cross-session     | 跨会话           |
| Memory Decay      | 记忆衰减          |
| Vector Database   | 向量数据库         |

## 练习题

1. 说出 Agent 记忆的三层结构，并各举一个例子。
2. 为什么 `MEMORY.md` 里不适合写临时噪声？
3. 用一句话解释：语义搜索为什么比关键词匹配更适合做记忆召回？

## 课后测试

1. 单选：以下哪一项最接近长期记忆？
   * A. 当前一句话的上下文
   * B. 用户“喜欢中文简洁回答”
   * C. 临时的天气提醒
2. 简答：`MEMORY.md` 的核心作用是什么？
3. 简答：RAG 和 Agent 记忆在检索思想上有什么共同点？

## 小结

今天你已经把“会聊天的 Agent”推进到“会记住、会找回、会更新”的阶段。

下一步就是把记忆、工具和 Skill 串起来，让 Agent 不只是回答问题，而是能持续工作。
