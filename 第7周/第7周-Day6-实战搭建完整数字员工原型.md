# ⚡ 实战日 | 第7周-Day6：搭建完整数字员工原型

> **Agent Runtime入门 → 从零搭建一个可运行的数字员工**
> 前五天我们学了：身份(SOUL.md) → 记忆(MEMORY.md) → 工作流 → 多Agent协作 → 质量评估
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

| Day | 主题 | 核心组件 | 一句话总结 |
|-----|------|----------|-----------|
| Day1 | 数字员工总览 | **SOUL.md** | 定义Agent的身份、规则、约束、输出格式 |
| Day2 | 记忆系统 | **MEMORY.md** | 三层记忆（短期/中期/长期），语义搜索持久化 |
| Day3 | 任务编排 | **Cron + 消息路由** | 工作流是图不是链，定时任务+跨平台推送 |
| Day4 | 多Agent协作 | **subagent + TaskFlow** | 主Agent分发任务，子Agent并行执行 |
| Day5 | 质量保障 | **护栏 + 监控** | 三层护栏(Prompt+工具+流程)，审计轨迹 |

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
- LangChat中每个Skill都有System Prompt约束行为
- Orchestrator通过SOUL.md判断请求路由到哪个能力域
- 商管系统的数字员工需要严格遵守权限边界

# 🧠 Step 2：设计 MEMORY.md 记忆系统

> 数字员工需要记住用户偏好、历史决策、业务上下文

## 三层记忆架构

| 层次 | 存储位置 | 容量 | 持久性 | 用途 |
|------|----------|------|--------|------|
| 短期 | 上下文窗口 | ~4K tokens | 单次对话 | 当前对话的临时信息 |
| 中期 | session历史 | ~32K tokens | 会话级 | 本轮对话的重要事实 |
| 长期 | MEMORY.md + memory/*.md | 无限 | 永久 | 用户偏好、历史决策 |

### 语义搜索原理
```
用户问 "上次那个餐饮招商的分析"
  → embedding(查询语句) → 向量
  → 在memory/*.md的embedding索引中搜索
  → 余弦相似度排序
  → 返回最相关的记忆片段
```

# 🔧 Step 3：工具注册表（Tool Registry）

> 数字员工通过工具与外部系统交互。工具注册表管理所有可用工具的元数据。

## 工具Schema设计

每个工具需要：
- **name**: 唯一标识
- **description**: 功能描述（给LLM看的）
- **parameters**: 输入参数Schema
- **returns**: 输出格式
- **permissions**: 调用权限要求

### 💡 对应MCP协议
- MCP Tool 就是结构化的工具定义
- LangChat的Skill最终通过MCP暴露为标准能力
- Orchestrator的capability路由基于工具注册表

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

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **isolated** | 子Agent获得干净上下文 | 独立任务（数据分析） |
| **fork** | 子Agent继承父Agent对话历史 | 需要上下文的连续任务 |

### 💡 OpenClaw的sessions_spawn
```python
# isolated模式（默认）
sessions_spawn(task="分析3F餐饮区域经营数据", context="isolated")

# fork模式（需要父对话上下文）
sessions_spawn(task="继续刚才的分析，深入租金差异", context="fork")
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

# 🔄 Step 6：TaskFlow — 可追踪的多步工作流

> 对于复杂任务（超过3步），用TaskFlow管理状态和等待

## TaskFlow vs 简单工具链

| 特性 | 简单工具链 | TaskFlow |
|------|-----------|----------|
| 步骤数 | 1-3步 | 4+步 |
| 状态管理 | 无 | 持久化 |
| 错误恢复 | 从头重来 | 从断点恢复 |
| 人工介入 | 不支持 | 支持人审节点 |
| 典型场景 | 查询商铺 | 月度经营报告生成 |

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

---

# ✏️ 课堂练习

## 练习1：扩展工具

在TOOL_REGISTRY中添加一个新工具 `query_foot_traffic`（查询客流量），
参数包含 `shop_id`、`date_range`、`granularity`（小时/天/月）。

<details>
<summary>💡 参考答案</summary>

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
</details>

## 练习2：设计客服数字员工

为一个购物中心设计一个「客服数字员工」，
写出它的 SOUL.md 四层结构（Identity/Rules/Constraints/Output）。

<details>
<summary>💡 思考方向</summary>

- Identity: 购物中心客服助手，面向顾客
- Rules: 常见问题优先KB查询，投诉转人工，导航给路线图
- Constraints: 不透露内部运营数据，不评论竞品
- Output: 简洁友好，带emoji，路线用文字+图片
</details>

---

# 📝 课后测试

**Q1**: 数字员工的 SOUL.md 四层结构是哪四层？

<details><summary>答案</summary>
Identity（身份）→ Rules（规则）→ Constraints（约束）→ Output Format（输出格式）
</details>

**Q2**: 子Agent的 `isolated` 和 `fork` 上下文模式有什么区别？

<details><summary>答案</summary>
- isolated: 子Agent获得干净上下文，适合独立任务（如数据查询）<br>
- fork: 继承父Agent的对话历史，适合需要上下文的连续任务（如报告生成）
</details>

**Q3**: TaskFlow比简单工具链多了什么能力？

<details><summary>答案</summary>
状态持久化、从断点恢复、支持人工审核节点、依赖管理
</details>

**Q4**: 为什么企业级数字员工必须有审计日志（Audit Trail）？

<details><summary>答案</summary>
因为Agent输出是概率性的（非确定性），必须记录「谁、何时、做了什么、结果如何」
以便追溯责任、排查异常、满足合规要求。
</details>

**Q5**: 在今天的架构中，OrchestratorAgent的三个核心职责是什么？

<details><summary>答案</summary>
1. 意图识别与路由  2. 子Agent编排与调度  3. 结果整合与审计记录
</details>

---

# 🔑 英文术语（10个）

| 术语 | 音标 | 释义 |
|------|------|------|
| **Orchestrator** | /ˈɔːkɪstreɪtər/ | 编排器，统一入口和路由 |
| **Subagent** | /sʌbˈeɪdʒənt/ | 子代理，被主Agent调度的专业Agent |
| **Audit Trail** | /ˈɔːdɪt treɪl/ | 审计轨迹，完整操作记录链 |
| **Context Mode** | /ˈkɒntekst moʊd/ | 上下文模式（isolated/fork） |
| **TaskFlow** | /tæsk floʊ/ | 任务流，多步骤可追踪工作流 |
| **Tool Registry** | /tuːl ˈredʒɪstri/ | 工具注册表，管理所有可用工具的元数据 |
| **Intent Classification** | /ɪnˈtent ˌklæsɪfɪˈkeɪʃən/ | 意图分类/识别 |
| **Human-in-the-Loop** | /ˈhjuːmən ðə luːp/ | 人工介入环节，如审核节点 |
| **Idempotency** | /ˌaɪdəmˈpoʊtənsi/ | 幂等性，重复调用不产生副作用 |
| **Fallback** | /ˈfɔːlbæk/ | 降级方案，主方案失败时的备用路径 |

---

# 🎬 推荐学习资源

## 📹 视频推荐

1. **B站：2025最新版大模型AI Agent入门到精通实战教程**
   - 链接：https://www.bilibili.com/video/BV1SqKHeUEm5/
   - 简介：99集完整教程，涵盖Agent+RAG+LangGraph，从入门到项目实战

2. **B站：2025必会的Agent课程（应用解读+项目实战）**
   - 链接：https://www.bilibili.com/video/BV1LhgSzrEgr/
   - 简介：20分钟搞懂AI Agent核心概念，72集系列覆盖应用场景和实战

## 📖 延伸阅读

1. **知乎：如何写好Agent的System Prompt?看这一篇就够了**
   - 链接：https://zhuanlan.zhihu.com/p/1990950758582088647
   - 简介：系统讲解System Prompt的结构化设计方法，含实战案例

2. **CSDN：AI Agent开发实战：30分钟搭建AI数字员工**
   - 链接：https://blog.csdn.net/weixin_43107715/article/details/157910358
   - 简介：基于LangChain+LLM快速搭建数字员工，涵盖感知-规划-执行-记忆四大模块

---

# 📊 今日总结

## ⚡ 实战成果

今天我们从零搭建了一个完整的商管数字员工原型，整合了本周Day1-5所有知识：

| 组件 | 来源 | 实现方式 |
|------|------|----------|
| SOUL.md | Day1 | 定义身份、规则、约束、输出格式 |
| MEMORY.md | Day2 | 用户偏好 + 决策记录 + 语义搜索模拟 |
| Tool Registry | Day3 | 商铺查询 + 租赁查询 + 通知发送 |
| SubAgent | Day4 | DataAgent + ReportAgent + AlertAgent |
| Audit Log | Day5 | 完整操作记录，支持追溯 |

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

---

## 📅 明天预告

> **Day 7（周日）：🔄 W7全面复习**
> 回顾Day1-6所有知识，做一套综合测试，查漏补缺！

加油 Jason！💪🚀
