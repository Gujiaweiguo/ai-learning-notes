#!/usr/bin/env python3
"""生成第8周 Day1《谁在调用 LangChat？》中文课程 Notebook。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Week8-Day1-LangChat-用户意图.md"
OUTPUT = ROOT / "第8周-Day1-LangChat用户意图.ipynb"

cells = []


def md(text: str) -> None:
    lines = text.split("\n")
    source = [line + "\n" for line in lines[:-1]] + [lines[-1]] if lines else []
    cells.append({"cell_type": "markdown", "metadata": {}, "source": source})


def code(text: str) -> None:
    lines = text.split("\n")
    source = [line + "\n" for line in lines[:-1]] + [lines[-1]] if lines else []
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source,
        }
    )


content = SOURCE.read_text(encoding="utf-8")
parts = [part.strip() for part in content.split("\n---\n") if part.strip()]

# 第7周沿用的约定：第一格始终配置中文字体。
code("""# 第8周 Day1：谁在调用 LangChat？
# matplotlib 中文字体配置
from matplotlib import font_manager
import matplotlib.pyplot as plt

font_path = \"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc\"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams[\"font.family\"] = font_name
plt.rcParams[\"axes.unicode_minus\"] = False
print(f\"中文字体配置完成：{font_name}\")""")

# 标题、进度和回顾。
md(parts[0])
md(parts[1])

md("""# 📚 Part 1：请求链路与职责边界

下面的图不是部署图，而是“责任图”。每一层只做自己该做的事：
- Agent Host 负责理解用户与规划任务；
- LangChat 负责发现、授权、发布、审计和执行企业能力；
- Provider 保留业务数据和最终数据权限。""")
code("""# LangChat 请求链路与职责边界可视化
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(15, 5))
ax.set_xlim(0, 15)
ax.set_ylim(0, 5)
ax.axis('off')

nodes = [
    (0.5, 2.1, '用户', '#E3F2FD'),
    (3.0, 2.1, 'Agent Host\\n理解意图 / 规划', '#FFF3E0'),
    (6.5, 2.1, 'LangChat\\n能力治理 / 受控执行', '#E8F5E9'),
    (10.0, 2.1, 'SkillRelease\\n版本 / 审批 / Trace', '#F3E5F5'),
    (13.0, 2.1, 'Provider\\n业务数据 / 最终授权', '#FCE4EC'),
]
for x, y, label, color in nodes:
    box = FancyBboxPatch((x, y), 1.7, 0.85, boxstyle='round,pad=0.12',
                         facecolor=color, edgecolor='#546E7A', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + 0.85, y + 0.425, label, ha='center', va='center', fontsize=11, fontweight='bold')

for start in [2.2, 4.7, 8.2, 11.7]:
    ax.annotate('', xy=(start + 0.68, 2.525), xytext=(start, 2.525),
                arrowprops=dict(arrowstyle='->', lw=1.8, color='#455A64'))

ax.text(5.55, 3.45, '受控 HTTP / MCP：client、actor、tenant、workspace、scope、delegation',
        ha='center', fontsize=11, color='#37474F')
ax.text(7.5, 0.85, '核心原则：不让 Agent Host 变成能力治理平台，也不让 LangChat 变成第二个 Agent Host',
        ha='center', fontsize=12, fontweight='bold', color='#1565C0')
plt.tight_layout()
plt.show()""")

# ADR、代码现状、Gap、结论、练习和术语。
for part in parts[2:]:
    md(part)
    if "现有代码已经做到哪里" in part:
        code("""# 六维身份上下文：理解“直接调用”为什么仍然受控
from dataclasses import dataclass

@dataclass(frozen=True)
class RequestIdentity:
    client: str       # 哪个 Agent Host / 客户端
    actor: str        # 谁真正发起请求
    tenant: str       # 哪个租户
    workspace: str    # 哪个工作空间
    scope: tuple[str, ...]       # 获得哪些动作权限
    delegation: tuple[str, ...]  # 权限委托链

request = RequestIdentity(
    client='openclaw',
    actor='user:jason',
    tenant='tenant:demo',
    workspace='workspace:mall',
    scope=('skill.invoke', 'report.read'),
    delegation=('user:jason', 'agent:openclaw'),
)

print('调用者：', request.client)
print('实际发起者：', request.actor)
print('允许动作：', ', '.join(request.scope))
print('委托链：', ' -> '.join(request.delegation))""")
    if "目标态与代码现实之间的 Gap" in part:
        code("""# 当前状态与 v2 目标态：用一个简单评分表查看 Gap
items = {
    'SkillRelease 调用入口': (1, 1),
    '六维身份验证': (1, 1),
    '审批相关流程': (1, 1),
    'ApplicationContract': (0, 1),
    'ExecutionPlanIR': (0, 1),
    'OCI digest / 签名': (0, 1),
    'Deployment / 流量策略': (0, 1),
}

for name, (current, target) in items.items():
    state = '✅ 已有基础' if current == target else '🔴 v2 Gap'
    print(f'{name:<28} {state}')

print('\\n结论：当前系统不是空白；核心工作是把“Workflow 绑定”演进为可发布、可部署、可验证的制品执行链。')""")

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"已生成：{OUTPUT}，共 {len(cells)} 个单元格")
