#!/usr/bin/env python3
"""为 W6 Day2-Day7 和 W7 Day1-Day2 补充推荐学习资源 section"""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 每个notebook对应的推荐资源内容（在术语表之前插入）
RESOURCES = {
    "第6周/第6周-Day2-Function-Calling详解.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **Function Calling 技术详解**（13集系列，约3小时）
   https://www.bilibili.com/video/BV1SJm8YtETd/
   > 简介：从理论到实战的保姆级教程，覆盖单函数调用、多函数调度等核心场景

2. **Function Calling 30分钟全解**（30分钟）
   https://www.bilibili.com/video/BV1emMFzfE5A/
   > 简介：快速上手 OpenAI Function Calling，附带实战代码演示

### 📖 延伸阅读
1. **OpenAI Function Calling 官方指南**
   https://developers.openai.com/api/docs/guides/function-calling
   > 简介：官方最权威的 Function Calling 文档，含并行调用、结构化输出等高级用法

2. **大模型函数调用（Function Calling）完全指南**
   https://zhuanlan.zhihu.com/p/2004370775214424996
   > 简介：知乎深度解析文章，从背景原理到工程实践全面覆盖

""",

    "第6周/第6周-Day3-ReAct模式与多Agent协作.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **ReAct Agent 智能体教程**（10分钟）
   https://www.bilibili.com/video/BV1QmNX6UEWN/
   > 简介：10分钟完整梳理 ReAct 运行逻辑与落地实践，适合快速理解核心机制

2. **ReAct：协同 Agent 推理与行动**（一起啃书系列）
   https://www.bilibili.com/video/BV1qzNAerELM/
   > 简介：逐行解读 ReAct 论文与 LangChain 实现代码，适合想深入源码的同学

### 📖 延伸阅读
1. **ReAct: Synergizing Reasoning and Acting in Language Models（论文）**
   https://react-lm.github.io/
   > 简介：ReAct 范式原始论文，奠定了"推理+行动"交替执行的 Agent 基石

2. **ReAct Agent 终极指南**
   https://juejin.cn/post/7518707715129688064
   > 简介：掘金实战文章，涵盖 LangChain 实现、多工具调度、幻觉消除等进阶内容

""",

    "第6周/第6周-Day4-推理能力评测与Prompt工程.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **ChatGPT Prompt Engineering for Developers — 吴恩达**（约1.5小时）
   https://www.bilibili.com/video/BV1H14y1j7eR/
   > 简介：吴恩达与 OpenAI 联合出品的免费课程，系统讲解 Prompt Engineering 最佳实践

2. **Let's build GPT: from scratch — Andrej Karpathy**（约2小时）
   https://www.youtube.com/watch?v=kCc8FmEb1nY
   > 简介：前特斯拉 AI 总监从零实现 GPT，深入理解 Transformer 内部推理机制

### 📖 延伸阅读
1. **OpenAI Prompt Engineering 官方指南**
   https://developers.openai.com/api/docs/guides/prompt-engineering
   > 简介：六大策略提升模型输出质量，官方推荐的 Prompt 优化方法论

2. **Learn Prompting — 全面 Prompt 教程**
   https://learnprompting.org/
   > 简介：从入门到高级的 Prompt Engineering 免费教程，支持中文，社区持续更新

""",

    "第6周/第6周-Day5-Agent开发实战框架设计.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **AI Agentic Workflows with LangChain — 吴恩达**（约1小时）
   https://www.deeplearning.ai/short-courses/ai-agentic-workflows-with-langchain/
   > 简介：吴恩达讲解 Agentic Workflow 三种模式，对比传统 Chain 效率提升显著

2. **LLM Agent 实战教程**（30分钟）
   https://www.bilibili.com/video/BV1GJ411x7h7/
   > 简介：B站高人气 Agent 实战视频，从架构设计到代码实现全覆盖

### 📖 延伸阅读
1. **LLM Powered Autonomous Agents — Lilian Weng**
   https://lilianweng.github.io/posts/2023-06-23-agent/
   > 简介：OpenAI 研究员撰写的 Agent 领域综述博客，被广泛引用的经典参考

2. **Cognitive Architectures for Language Agents（论文）**
   https://arxiv.org/abs/2309.02427
   > 简介：系统对比 Agent 认知架构，涵盖记忆、推理、规划等核心模块设计

""",

    "第6周/第6周-Day6-搭建Function Calling Agent.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **Function Calling 技术详解**（13集系列）
   https://www.bilibili.com/video/BV1SJm8YtETd/
   > 简介：从单函数到多函数实战，手把手搭建完整的 Function Calling Agent

2. **OpenAI Function Calling 30分钟全解**（30分钟）
   https://www.bilibili.com/video/BV1emMFzfE5A/
   > 简介：快速上手教程，含完整可运行的代码示例

### 📖 延伸阅读
1. **OpenAI Cookbook — Function Calling 示例集**
   https://github.com/openai/openai-cookbook
   > 简介：官方维护的 OpenAI API 最佳实践仓库，含多个 Function Calling 实战案例

2. **LangChain Agents 文档**
   https://docs.langchain.com
   > 简介：LangChain 官方文档中 Agent 模块，涵盖 Tool Calling、ReAct 等模式

""",

    "第6周/第6周-Day7-Agent复习巩固.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **Building Agentic RAG with LlamaIndex — Jerry Liu**（约1小时）
   https://www.deeplearning.ai/courses/building-agentic-rag-with-llamaindex
   > 简介：LlamaIndex 联合创始人授课，展示 Agent 如何在 RAG 场景中自主推理与决策

2. **AI Agent 全景解读**（20分钟）
   https://www.bilibili.com/video/BV1QmNX6UEWN/
   > 简介：梳理 Agent 生态全貌，从 ReAct 到多 Agent 协作的演进脉络

### 📖 延伸阅读
1. **Awesome AI Agents — Agent 生态汇总**
   https://github.com/e2b-dev/awesome-ai-agents
   > 简介：收录数百个 AI Agent 项目和框架，是了解 Agent 生态的最佳入口

2. **LLM Powered Autonomous Agents — Lilian Weng**
   https://lilianweng.github.io/posts/2023-06-23-agent/
   > 简介：Agent 领域必读综述，系统总结 Agent 架构、规划、工具使用与反思机制

""",

    "第7周/第7周-Day1-数字员工总览与Agent行为设计.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **ChatGPT Prompt Engineering for Developers — 吴恩达**（约1.5小时）
   https://www.bilibili.com/video/BV1H14y1j7eR/
   > 简介：理解 System Prompt 如何塑造 AI 行为，是设计数字员工"性格"的基础

2. **Building Systems with the ChatGPT API — 吴恩达**（约2小时）
   https://www.deeplearning.ai/short-courses/building-systems-with-the-chatgpt-api/
   > 简介：多步推理与系统级 Prompt 设计，适合构建复杂的数字员工行为链

### 📖 延伸阅读
1. **Cognitive Architectures for Language Agents（论文）**
   https://arxiv.org/abs/2309.02427
   > 简介：从认知科学角度分析 Agent 行为架构，涵盖记忆、反思、规划模块设计

2. **Dify — 开源 AI Agent 应用开发平台**
   https://github.com/langgenius/dify
   > 简介：可视化的 Agent/Workflow 构建平台，适合快速搭建数字员工原型

""",

    "第7周/第7周-Day2-记忆系统与语义搜索.ipynb": """## 🎬 推荐学习资源

### 📹 视频推荐
1. **Building Agentic RAG with LlamaIndex — Jerry Liu**（约1小时）
   https://www.deeplearning.ai/courses/building-agentic-rag-with-llamaindex
   > 简介：深入讲解 RAG 中的向量检索、语义搜索和 Agent 自主决策机制

2. **LangChain RAG 从入门到实战**（40分钟）
   https://www.bilibili.com/video/BV1GJ411x7h7/
   > 简介：从文档加载到向量检索的完整 RAG 流水线搭建

### 📖 延伸阅读
1. **LangSmith Evaluation 文档**
   https://docs.langchain.com/langsmith/evaluation-concepts
   > 简介：如何量化评估 RAG 检索质量和 Agent 回答准确性，含评测框架设计

2. **Self-RAG: Learning to Retrieve, Generate, and Critique（论文）**
   https://arxiv.org/abs/2310.11511
   > 简介：Meta 提出的 Self-RAG 框架，让 LLM 自主判断何时检索、如何反思生成质量

""",
}


def process_notebook(filepath):
    """在术语表之前插入推荐学习资源 cell"""
    full_path = os.path.join(BASE, filepath)
    
    with open(full_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    resource_md = RESOURCES[filepath]
    
    # 找到"英文术语表"所在的 cell index
    target_idx = None
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "markdown":
            src = "".join(cell["source"])
            if "英文术语" in src:
                target_idx = i
                break
    
    if target_idx is None:
        print(f"  ⚠️  未找到'英文术语' cell，跳过 {filepath}")
        return False
    
    # 创建新的 markdown cell
    new_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in resource_md.rstrip("\n").split("\n")],
    }
    
    # 在术语表之前插入
    nb["cells"].insert(target_idx, new_cell)
    
    # 写回并验证
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    
    # 验证
    with open(full_path, "r", encoding="utf-8") as f:
        nb2 = json.load(f)
    
    # 检查插入是否成功
    check_src = "".join(nb2["cells"][target_idx].get("source", []))
    if "推荐学习资源" in check_src:
        print(f"  ✅ {filepath} — 插入到 cell {target_idx}（术语表之前）")
        return True
    else:
        print(f"  ❌ {filepath} — 验证失败")
        return False


if __name__ == "__main__":
    success_count = 0
    for filepath in RESOURCES:
        print(f"处理: {filepath}")
        if process_notebook(filepath):
            success_count += 1
    
    print(f"\n完成: {success_count}/{len(RESOURCES)} 个 notebook 处理成功")
