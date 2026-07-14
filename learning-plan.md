# 🏗 企业 AI 平台架构师学习计划（v8）

## 基本信息
- **对象**: Jason
- **学习目标**: 成为企业级 AI Platform 架构师，围绕 LangChat（Enterprise Capability Platform）和 OpenClaw（Orchestrator）建立完整知识体系，服务于商业地产 AI SaaS
- **每天时间**: 30分钟学习 + 实战练习另计
- **推送时间**: 每天 6:00（周一到周日每天推送）
- **资料语言**: 视频/图片英文也行，文字必须中文
- **交付形式**: 文字推送，用户用手机朗读功能听读
- **硬件**: RTX 4060Ti 16G
- **开发工具**: opencode（CLI AI编程助手）
- **总计划**: 21 周

## 核心定位

> 不是学习某一个 AI 框架，而是成长为企业级 AI Platform 架构师。
> 技术栈：OpenClaw（Orchestrator Agent）→ Orchestrator（统一入口/路由/权限/审计）→ LangChat（AI Compiler/Skill管线）→ LnkChatBI/商管/会员/物业

## 技术栈全景

```
用户 → OrchestratorAgent（入口/capability路由/system binding/权限/trace/audit/metrics）
         ├── LangChat（knowledge.query/workflow.execute/RAG/人审/Skill管线）
         │    └── AI Compiler：NL需求 → Blueprint → Validator → Simulator → Review → Publish → Runtime
         ├── LnkChatBI（data.query/Text-to-SQL/图表/数据分析）
         ├── 商管系统（项目/商铺/租赁/招商/收费/运营）
         ├── 会员系统（会员/积分/权益/营销/画像）
         └── 物业管理系统（工单/巡检/能耗/设备）
底层：OpenClaw / Hermes Agent / MCP
```

## 知识领域（11个Level）

```
Level 1  AI基础（LLM/Prompt/Embedding/Reasoning）
Level 2  MCP协议（Protocol/Tool/Auth/Session/Transport）
Level 3  Agent Runtime（Execution/Checkpoint/Memory/Planner/Event Bus）
Level 4  AI Compiler（Program Synthesis/DSL/Validator/Simulator/Composition）
Level 5  Capability Platform（Registry/Gateway/Skill Lifecycle/Observability）
Level 6  企业权限与安全（RBAC/ABAC/OAuth2/Delegation/AI Governance/PII）
Level 7  企业系统集成（REST/Webhook/EDA/Saga/多租户/事件溯源）
Level 8  数据与存储（PostgreSQL/PGVector/CQRS/Row-Level Security）
Level 9  AI运营（Trace/Cost/Token/Evaluation/Feedback/Testing/Canary）
Level 10 API设计（OpenAPI/MCP/Webhook/SSE/Streaming/Idempotency）
Level 11 AI产品设计（Capability/Skill/Blueprint/Publish/Multi-Tenant）
```

## 日程调整

按日历周编号，周一为每周起始：
- 第一周 = 6/1-6/7（Jason从6/4周四开始学习）

## 每周节奏（7天循环）

| 日期 | 类型 | 内容 |
|------|------|------|
| 周一 | 📚 新知识 | Day 1：当周第一个主题 |
| 周二 | 📚 新知识 + 🔄复习 | Day 2：新主题 + 复习 Day 1 |
| 周三 | 📚 新知识 + 🔄复习 | Day 3：新主题 + 复习 Day 2 |
| 周四 | 📚 新知识 + 🔄复习 | Day 4：新主题 + 复习 Day 3 |
| 周五 | 📚 新知识 + 🔄复习 | Day 5：新主题 + 复习 Day 4 |
| 周六 | ⚡ 代码实战 | opencode动手练习，基于本周知识点写代码 |
| 周日 | 🔄 复习日 | 本周 Day 1-5 全部回顾 + 查漏补缺 |

## 学习方法论：新学+复习+练习→代码→总复习

每天推送为一条完整文字消息：
- 📚 今日新知识
- 🔄 昨日复习（周二起）
- 🔑 英文术语（3-5个，来自当天内容）
- 🎬 推荐视频 + 📖 延伸阅读
- ✏️ 课堂练习 + 📝 课后测试
- 🔄 往期回顾

每天学习流程：
- 6:00 收到推送，朗读听知识点（30分钟）
- 先看「昨日复习」回忆昨天的内容（5分钟）
- 再学「今日新知识」（20分钟）
- 有空时做练习和测试，回复答案批改
- 周六动手写代码（有整块时间）
- 周日全面复习，查漏补缺

## 灵活机制
- 每周允许1天「请假」，当天只推往期复习题
- 连续3天未回复答案 → 自动降速
- 回复任意答案后 → 自动恢复正常

---

# 📅 学习路线总览

```
W1-W6   ✅ AI基础与Agent入门（已完成）
W7      🔥 数字员工架构深化（进行中）       → Level 3 Agent Runtime 入门
W8      📝 AI基础补强                      → Level 1 Prompt实战+安全
W9      🔌 MCP协议深入                     → Level 2 全链路
W10     ⚙️ Agent Runtime进阶               → Level 3 OpenClaw+Hermes对比
W11-12  🧠 AI Compiler                     → Level 4 核心技术壁垒
W13     🏛 Capability Platform             → Level 5 产品核心
W14     📊 ChatBI与数据分析Agent            → Level 5+11 业务核心
W15     🔒 企业权限与安全                   → Level 6 架构保障
W16-17  🎯 RL与优化                        → Level 9 Agent越用越聪明
W18     👁 商业地产视觉AI                   → Level 5+11 行业能力
W19     🚀 前沿与部署                       → 落地最后一公里
W20-21  🧠 脑科学精华                       → 个人兴趣
```

---

# ✅ 已完成阶段

## W1-W2：Transformer 与大模型训练 ✅
- W1：自注意力机制、Multi-Head Attention、位置编码
- W2：预训练、SFT、RLHF、DPO、QLoRA微调实战

## W3：RAG 与知识增强 ✅
- 向量检索、Embedding、高级RAG、混合检索、GraphRAG、RAG实战

## W4：推理与思维链 ✅
- Chain-of-Thought、Tree-of-Thought、DeepSeek R1、推理评测、Prompt工程

## W5：Agent 与工具使用 ✅
- LLM Agent架构、Function Calling、ReAct模式、Agent安全

## W6：LLM Agent 实战 ✅
- 搭建Function Calling Agent、Agent框架设计、实战代码

---

# W7：🔥 数字员工架构深化（进行中）

> Agent Runtime 入门。多Agent协作、长期记忆、任务编排——数字员工的核心骨架。
> Level 3 Agent Runtime 基础能力。

- Day 1（周一）: 数字员工总览 + Agent行为设计 ✅
  - 数字员工是什么：从聊天机器人到自主工作Agent
  - System Prompt + SOUL.md：定义Agent人格与行为规则
  - 输出格式控制（JSON/Markdown/模板）

- Day 2（周二）: 长期记忆与语义检索 ✅
  - 记忆三层结构：短期/中期/长期
  - MEMORY.md 与 memory/*.md 持久化策略
  - 语义搜索（memory_search）：embedding + 相似度匹配

- Day 3（周三）: 任务编排与工作流
  - 工具编排：单工具→多工具链→自动化工作流
  - 定时任务（Cron）、延迟提醒、周期工作
  - 跨平台消息路由（微信/Telegram/Signal）

- Day 4（周四）: 多Agent协作模式
  - 主Agent + 子Agent（subagent）编排
  - TaskFlow：多步骤可追踪工作流
  - 上下文传递：isolated vs fork

- Day 5（周五）: 评估体系与质量保障
  - Agent输出质量评估：准确性、一致性、安全性
  - 护栏设计：Prompt护栏 → 工具护栏 → 流程护栏
  - 监控与日志：审计轨迹、异常检测、人工介入

- Day 6（周六）: ⚡ 实战：搭建一个完整数字员工原型
  - 任务：SOUL.md + MEMORY.md + 工具链 + 子Agent协作

- Day 7（周日）: 🔄 复习 W7 关键概念

---

# W8：📝 AI基础补强

> Prompt工程实战、安全防御、结构化输出——为LangChat的Skill生成和Orchestrator的权限护栏打底。
> Level 1 AI基础补强 + Level 6 安全入门。

- Day 1（周一）: Prompt工程进阶
  - System Prompt 设计模式（角色→约束→输出模板→示例）
  - Few-Shot优化：样本选择策略、顺序效应
  - Structured Output：JSON Schema约束、Function Calling输出控制
  - 💡 对应：LangChat的Skill输出需要严格的Schema定义

- Day 2（周二）: Prompt安全与护栏
  - Prompt Injection：直接注入、间接注入、越狱攻击
  - 防御策略：输入过滤、输出过滤、权限隔离
  - Guardrail设计：Content Policy + Tool Policy + Output Policy 三层护栏
  - 💡 对应：Orchestrator和LangChat的安全防线

- Day 3（周三）: 模型输出可控性
  - Temperature/Top-P与输出质量的关系
  - 重复检测与多样化策略
  - JSON/Markdown输出的稳定性保障
  - Retry与Fallback策略（模型不可靠时的降级方案）
  - 💡 对应：Skill Compiler需要可靠的模型输出

- Day 4（周四）: 多模型协作基础
  - 大模型 vs 小模型：什么时候用哪个
  - 模型路由策略：按任务复杂度、按成本、按延迟
  - Fallback与降级：主模型不可用时的切换策略
  - 💡 对应：Orchestrator的多模型调度

- Day 5（周五）: Token优化与成本管理
  - Context Window管理：压缩、摘要、滑动窗口
  - Token预算与配额设计
  - 缓存策略：语义缓存、精确缓存
  - 成本估算与控制框架
  - 💡 对应：企业SaaS的成本控制

- Day 6（周六）: ⚡ 实战：设计一套完整的Prompt安全方案
  - 任务：为Orchestrator设计输入过滤+输出过滤+权限护栏
  - 验证：用常见攻击样本测试防御效果

- Day 7（周日）: 🔄 复习 W7-W8 + Prompt工程核心能力串联

---

# W9：🔌 MCP协议深入

> Model Context Protocol 全链路深入。LangChat的Skill对接外部系统的核心协议。
> Level 2 MCP协议 + Level 10 API设计。

- Day 1（周一）: MCP协议基础
  - MCP设计哲学：标准化AI与外部系统的交互
  - 三大原语：Tool（工具调用）、Resource（资源读取）、Prompt（模板管理）
  - Transport层：STDIO（本地进程） vs SSE（远程服务）
  - 💡 对应：LangChat的Skill最终通过MCP暴露为标准能力

- Day 2（周二）: MCP Tool深入
  - Tool Schema设计：输入/输出类型、必需/可选参数
  - Tool发现与注册：Capability Registry如何发现MCP Tool
  - Tool版本管理：向后兼容、Breaking Change
  - Tool执行模型：同步vs异步、超时、重试
  - 💡 对应：商管/会员系统的能力注册

- Day 3（周三）: MCP认证与会话
  - Auth机制：OAuth2 Bearer Token、API Key、签名认证
  - Session管理：有状态会话vs无状态
  - Sampling：模型请求工具执行权限的交互模式
  - 多租户场景下的MCP隔离
  - 💡 对应：Orchestrator的system binding与权限传递

- Day 4（周四）: MCP Resource与Prompt
  - Resource：静态资源vs动态资源、URI设计
  - Prompt：模板管理、变量注入、版本控制
  - MCP与RAG的结合：Resource作为知识源
  - MCP与Function Calling的关系
  - 💡 对应：LangChat知识查询的底层实现

- Day 5（周五）: MCP企业级实践
  - MCP Gateway设计：多MCP Server的统一入口
  - 限流、熔断、降级策略
  - MCP监控：调用统计、延迟追踪、错误率
  - MCP与OpenAPI的互补关系
  - 💡 对应：Orchestrator的capability路由架构

- Day 6（周六）: ⚡ 实战：实现一个MCP Server
  - 任务：为商管系统写一个MCP Server（商铺查询+租赁信息）
  - 验证：通过标准MCP Client调用并测试

- Day 7（周日）: 🔄 复习 W7-W9 + MCP协议核心能力

---

# W10：⚙️ Agent Runtime进阶

> OpenClaw与Hermes Agent架构对比，理解Agent运行时的核心机制。
> Level 3 Agent Runtime 核心。

- Day 1（周一）: OpenClaw架构剖析
  - 核心模块：Plugin/Skill/Session/Channel/MCP
  - 执行模型：Execution State、Checkpoint、Resume
  - 事件系统：Event Bus、订阅发布、执行回放
  - 💡 对应：Orchestrator的Agent执行引擎

- Day 2（周二）: Hermes Agent架构剖析
  - 核心模块：Provider/Node Registry/Planner/Reducer/Artifact
  - Memory模型：短期/长期/用户画像
  - Skill系统：Skill定义、加载、执行
  - 💡 对应：LangChat的Agent Runtime设计参考

- Day 3（周三）: OpenClaw vs Hermes对比
  - 设计哲学差异：CLI-first vs Web-first
  - Skill系统对比：OpenClaw Skill vs Hermes Skill
  - Channel机制对比：消息路由策略
  - Context管理对比：Fork/Isolated/Shared
  - 各自的优缺点与适用场景

- Day 4（周四）: Agent Runtime核心概念
  - Execution State：状态机、持久化、恢复
  - Planner：任务分解、依赖分析、并行执行
  - Reducer：结果聚合、冲突解决
  - Artifact：中间产物管理（文件、图表、报告）
  - 💡 对应：LangChat Runtime需要这些核心能力

- Day 5（周五）: 自研Agent设计思路
  - 核心模块清单：最小可用Agent需要什么
  - 技术选型考虑：语言、框架、部署
  - 与OpenClaw/Hermes的差异化方向
  - MVP设计：先做什么，后做什么
  - 💡 对应：Jason自研Agent的规划

- Day 6（周六）: ⚡ 实战：画出你的Agent Runtime架构图
  - 任务：设计自研Agent的核心模块与交互关系
  - 验证：与OpenClaw/Hermes对比，明确取舍

- Day 7（周日）: 🔄 复习 W7-W10 + Agent Runtime核心能力

---

# W11：🧠 AI Compiler基础

> 自然语言→可执行Skill的核心技术。LangChat最核心的技术壁垒。
> Level 4 AI Compiler 上半。

- Day 1（周一）: AI Compiler概念与动机
  - 什么是AI Compiler：从自然语言需求到可执行程序
  - 与传统编译器的类比：Lexer→Parser→IR→CodeGen→Optimize
  - LangChat的管线：NL → Blueprint → Validator → Simulator → Review → Publish → Runtime
  - 为什么Skill是第一公民，不是Workflow
  - 💡 对应：LangChat的核心产品定位

- Day 2（周二）: NL理解与意图解析
  - 自然语言需求的结构化提取
  - 意图识别与参数填充（Slot Filling）
  - 歧义消解与多轮对话中的需求澄清
  - 复杂需求的分解策略
  - 💡 对应：LangChat NL→Blueprint的第一步

- Day 3（周三）: Skill Blueprint设计
  - Blueprint Schema设计：输入/输出/步骤/依赖/错误处理
  - DSL（领域特定语言）设计原则
  - Skill的类型系统：数据类型、约束、验证规则
  - Blueprint示例：设计几个典型Skill的Blueprint
  - 💡 对应：LangChat的核心数据结构

- Day 4（周四）: 程序综合（Program Synthesis）
  - 从规约生成代码的基本原理
  - LLM作为Program Synthesizer的优势与局限
  - 代码生成vs程序合成：有什么区别
  - 技能组合（Composition）：多个Skill如何安全组合
  - 💡 对应：Blueprint生成的理论基础

- Day 5（周五）: Validator设计
  - 验证层级：语法验证→语义验证→安全验证→业务验证
  - 静态分析：Blueprint的结构正确性检查
  - 安全验证：权限检查、资源限制、敏感操作标记
  - 业务验证：与实际系统能力的匹配度检查
  - 💡 对应：LangChat Validator的核心逻辑

- Day 6（周六）: ⚡ 实战：设计一个Skill Blueprint Schema
  - 任务：为"查询某商场本月客流趋势"设计完整Blueprint
  - 验证：写出Validator的检查规则

- Day 7（周日）: 🔄 复习 W11 + AI Compiler核心概念

---

# W12：🧠 AI Compiler实战

> Simulator、Skill Composition、Inspector——AI Compiler的下半场。
> Level 4 AI Compiler 下半 + Level 11 AI产品设计。

- Day 1（周一）: Simulator设计
  - 沙箱执行环境：隔离、资源限制、状态管理
  - Dry Run模式：不真正执行，模拟结果
  - 状态回滚：执行失败时恢复到之前状态
  - 成本预估：执行前的Token/时间/费用估算
  - 💡 对应：LangChat Simulator的核心能力

- Day 2（周二）: Skill Composition与编排
  - 串行组合：Step1→Step2→Step3
  - 并行组合：同时执行多个Skill
  - 条件分支：根据结果选择不同Skill
  - 错误处理：重试、降级、人工介入
  - 💡 对应：复杂业务需求需要组合多个Skill

- Day 3（周三）: Review/Inspector设计
  - Inspector的可视化定位：检查、调试、微调
  - Blueprint Diff：版本对比、变更影响分析
  - 执行追踪：逐步查看Skill执行过程
  - 人审流程：AI生成→人审→批准→发布
  - 💡 对应：LangChat Inspector的产品核心

- Day 4（周四）: Publish与Runtime
  - Skill发布流程：Validate→Approve→Publish→Deploy
  - 版本管理：语义化版本、回滚策略
  - Runtime执行：Skill在运行时的调度与监控
  - 冷启动vs热启动：Skill加载策略
  - 💡 对应：LangChat Skill全生命周期

- Day 5（周五）: Skill生命周期与Observability
  - Skill健康度：成功率、延迟、错误率
  - 退化检测：Prompt变更后Skill行为是否退化
  - Canary发布：新Skill先对部分流量开放
  - A/B测试框架：Skill版本对比
  - 💡 对应：企业级Skill管理

- Day 6（周六）: ⚡ 实战：设计完整的AI Compiler管线
  - 任务：为"商管系统自动生成月度经营分析报告"设计端到端管线
  - 验证：画出NL→Blueprint→Validate→Simulate→Review→Publish→Runtime全流程

- Day 7（周日）: 🔄 复习 W11-W12 + AI Compiler全链路

---

# W13：🏛 Capability Platform

> 能力注册、网关、Skill全生命周期——企业级AI能力平台的核心。
> Level 5 Capability Platform + Level 9 AI运营。

- Day 1（周一）: Capability Registry设计
  - 能力注册模型：Capability元数据、版本、状态
  - 能力发现：按领域/按场景/按关键词搜索
  - 能力分类：数据查询/知识问答/工作流/分析/视觉
  - 能力依赖管理：A能力依赖B能力
  - 💡 对应：LangChat的核心能力注册中心

- Day 2（周二）: Capability Gateway
  - 统一入口：所有能力通过Gateway暴露
  - 路由策略：按意图→按能力类型→按成本
  - 限流与配额：每个用户/租户的调用上限
  - 缓存策略：相同查询的缓存与复用
  - 💡 对应：Orchestrator的capability路由

- Day 3（周三）: Skill作为Capability
  - Skill→Capability的映射关系
  - Skill Provider模型：谁提供的、谁维护的、谁来审批
  - Skill Release流程：开发→测试→审批→发布
  - 多租户Skill隔离：不同租户看到不同Skill集
  - 💡 对应：LangChat Skill的产品形态

- Day 4（周四）: 能力编排与组合
  - 单能力调用vs多能力编排
  - Pipeline模式：能力串联执行
  - Orchestrator模式的编排决策
  - 能力降级：A不可用时切到B
  - 💡 对应：Orchestrator的system binding

- Day 5（周五）: AI运营（Observability）
  - Trace/Span：能力调用的分布式追踪
  - Cost/Token：调用成本统计与预算控制
  - Evaluation：能力输出质量评估
  - Feedback Loop：用户反馈→能力优化
  - 💡 对应：LangChat运营必需

- Day 6（周六）: ⚡ 实战：设计Capability Platform架构
  - 任务：为LangChat设计完整的Capability Registry + Gateway方案
  - 验证：用商管/会员/ChatBI场景验证设计

- Day 7（周日）: 🔄 复习 W7-W13 阶段总结 + 主线能力串联

---

# W14：📊 ChatBI与数据分析Agent

> Text-to-SQL、ChatBI架构、数据洞察——直接服务于LnkChatBI。
> Level 5 Capability + Level 8 数据与存储。

- Day 1（周一）: Text-to-SQL 原理
  - 自然语言到SQL的转换流程
  - Schema Linking：理解表结构与字段含义
  - SQL生成的关键技术：意图识别→表选择→条件构建→排序聚合
  - 常见挑战：歧义消解、多表JOIN、复杂聚合
  - 💡 对应：LnkChatBI的核心技术

- Day 2（周二）: ChatBI 架构设计
  - ChatBI完整工作流：查询理解→SQL生成→执行→结果解读→可视化
  - 查询改写与意图分类（数据查询 vs 知识问答）
  - 结果解读：数字转洞察、自动生成文字分析
  - 图表生成：根据数据特征自动选择图表类型
  - 💡 对应：LnkChatBI产品架构

- Day 3（周三）: 查询结果分析与数据洞察
  - 数据分析Agent的核心能力：趋势、异常、对比、预测
  - 自动洞察生成：从SQL结果中提取业务价值
  - 追问与多轮交互：用户连续提问的场景处理
  - 💡 对应：LnkChatBI的analysis.execute

- Day 4（周四）: ChatBI作为Capability
  - ChatBI如何注册为LangChat的Capability
  - 与其他Capability的编排：数据查询→知识检索→报告生成
  - PGVector在ChatBI中的应用：语义搜索辅助Schema Linking
  - 💡 对应：LnkChatBI与LangChat的集成

- Day 5（周五）: ChatBI评估与产品化
  - ChatBI质量评估：SQL准确率、回答相关性、响应速度
  - 错误处理：SQL执行失败、空结果、超时的用户引导
  - 多数据源切换、角色权限、审计日志
  - 💡 对应：LnkChatBI的企业级能力

- Day 6（周六）: ⚡ 实战：优化一个ChatBI场景
  - 任务：选择一个实际业务查询场景，分析当前实现并优化
  - 输出：优化前后对比报告

- Day 7（周日）: 🔄 复习 W13-W14 + Capability Platform + ChatBI串联

---

# W15：🔒 企业权限与安全

> Delegation、AI Governance、PII脱敏——企业级安全体系。
> Level 6 企业权限与安全。

- Day 1（周一）: 企业身份认证
  - OAuth2/OIDC：授权码模式、客户端模式
  - JWT：Token设计、刷新、吊销
  - 多系统SSO：Orchestrator↔LangChat↔商管系统的统一认证
  - 💡 对应：Orchestrator的认证基础

- Day 2（周二）: 授权模型深化
  - RBAC回顾：角色、权限、资源
  - ABAC深入：基于属性的访问控制（用户属性、资源属性、环境属性）
  - Delegation（委派授权）：A授权B代表A执行操作
  - Scope设计：API调用粒度的权限控制
  - 💡 对应：Orchestrator权限体系的核心

- Day 3（周三）: 多租户架构
  - 数据隔离层级：Database per tenant / Schema per tenant / Row-level
  - 配置隔离：每个租户的模型、权限、Skill集合
  - 计费模型：按租户、按用户、按Token
  - 💡 对应：SaaS平台的多租户架构

- Day 4（周四）: AI Governance
  - AI输出安全：有害内容过滤、敏感信息检测
  - PII脱敏：识别并脱敏用户数据（手机号、身份证、银行卡）
  - Skill发布安全：AI生成→人审→发布，不能跳过审批
  - 合规基础：数据安全法、AI相关法规
  - 💡 对应：LangChat Skill管线的安全要求

- Day 5（周五）: 审计与监控
  - 审计日志：谁、什么时候、做了什么、结果如何
  - Trace：完整请求链路追踪
  - 异常检测：异常调用模式识别
  - Row-Level Security：PostgreSQL行级权限
  - 💡 对应：Orchestrator的trace/audit/metrics

- Day 6（周六）: ⚡ 实战：设计Orchestrator权限方案
  - 任务：为Orchestrator设计完整的认证+授权+审计方案
  - 验证：用多租户场景验证设计

- Day 7（周日）: 🔄 复习 W15 + 企业安全核心能力

---

# W16：🎯 RL与优化基础

> 让Agent"越用越聪明"——RL基础理论与偏好学习。
> Level 9 AI运营 + RL核心。

- Day 1（周一）: 强化学习基础
  - MDP、策略、价值函数、奖励信号
  - 经典RL vs 大模型时代的RL
  - 为什么RL对Agent优化重要

- Day 2（周二）: RLHF与RLAIF
  - RLHF全流程：奖励模型训练→PPO优化
  - RLAIF：用AI替代人类标注
  - 实际案例：ChatGPT如何用RLHF对齐

- Day 3（周三）: 偏好学习方法
  - DPO / IPO / KTO / ORPO 对比
  - 各方法的适用场景与优缺点
  - 偏好数据集的构造原则

- Day 4（周四）: Agent评估与反馈闭环
  - 评估指标：任务完成率、用户满意度、安全合规
  - 显式反馈：用户评分、点赞/点踩
  - 隐式反馈：使用时长、重试率、修改率
  - 反馈→改进的闭环流程

- Day 5（周五）: RL与ChatBI/LangChat的结合
  - 用RL优化ChatBI的查询质量
  - 用偏好学习优化Skill生成质量
  - 用在线学习让Agent从交互中持续改进
  - 💡 对应：LangChat Skill质量的持续优化

- Day 6（周六）: ⚡ 实战：构造偏好数据集
  - 任务：为ChatBI场景构造50条偏好对（chosen vs rejected）
  - 验证：分析数据质量对RL效果的影响

- Day 7（周日）: 🔄 复习 W15-W16 + 安全+RL核心

---

# W17：🎯 RL实战与优化

> DPO微调→策略优化→评估迭代——动手让模型变"聪明"。
> Level 9 RL实战。

- Day 1（周一）: DPO微调实战
  - DPO数学原理与代码实现
  - TRL库使用：数据格式、训练配置、超参数
  - 在4060Ti上跑DPO微调

- Day 2（周二）: Agent策略优化
  - 从固定Prompt到自适应策略
  - 工具选择优化：减少冗余调用
  - Prompt Version管理与A/B测试

- Day 3（周三）: 在线学习与持续改进
  - Agent从用户交互中学习
  - 安全约束下的在线更新
  - 模型路由的动态调整

- Day 4（周四）: Skill回归测试
  - Golden Set设计：固定评估集
  - 自动评分：改了Prompt后行为是否退化
  - 回归测试框架设计

- Day 5（周五）: W7-W17 阶段测验
  - 测验覆盖：Agent Runtime/MCP/AI Compiler/Capability Platform/ChatBI/权限/RL
  - 知识脉络梳理：从W7到W17的完整链路

- Day 6（周六）: ⚡ 实战：端到端优化
  - 任务：选一个实际Skill/查询场景，用RL方法优化质量
  - 验证：优化前后对比

- Day 7（周日）：🔄 复习 W7-W17 主线能力总串联

---

# W18：👁 商业地产视觉AI

> 精准客流、通道拥堵、异常检测、消防预警——视觉能力作为Capability。
> Level 5 Capability + Level 11 行业AI。

- Day 1（周一）: 视觉检测基础
  - YOLO原理快速过：图像→检测框→分类
  - 目标检测 vs 图像分类 vs 语义分割
  - 边缘部署考虑：模型大小、推理速度
  - 💡 对应：商业地产场景的视觉基础

- Day 2（周二）: 精准客流统计
  - 进出计数算法（线段计数法）
  - 区域热力图：客流密度可视化
  - 停留时长分析
  - 💡 对应：商管运营核心指标

- Day 3（周三）: 通道拥堵与异常检测
  - 人群密度估计
  - 拥堵预警：实时检测+阈值报警
  - 地面脏污检测、杂物占道检测
  - 区域入侵检测
  - 💡 对应：物业管理的AI能力

- Day 4（周四）: 消防安全检测
  - 烟雾识别、火焰识别
  - 联动报警机制
  - 误报率控制策略
  - 💡 对应：商业地产安全合规

- Day 5（周五）: 视觉能力接入Capability Platform
  - 视觉检测作为MCP Tool或Capability注册
  - 实时检测vs定时巡检的架构设计
  - 视觉结果与LangChat的集成
  - 💡 对应：视觉AI融入LangChat平台

- Day 6（周六）: ⚡ 实战：跑一个视觉检测场景
  - 任务：用YOLO跑客流计数或拥堵检测demo
  - 验证：模型准确率与推理速度

- Day 7（周日）: 🔄 复习 W18 + 视觉AI核心能力

---

# W19：🚀 前沿与部署

> AI趋势、量化部署、成本优化——落地最后一公里。
> Level 9 AI运营 + 部署。

- Day 1（周一）: AI for Business趋势
  - 2026年AI行业趋势与机会
  - 数字员工/Agent平台市场格局
  - 企业AI落地成熟度模型

- Day 2（周二）: 模型优化与量化部署
  - 蒸馏、量化（INT4/INT8）、剪枝
  - llama.cpp / vLLM / TensorRT-LLM 对比
  - 边缘部署：NVIDIA Jetson/4060Ti

- Day 3（周三）: 企业级部署架构
  - 容器化：Docker/K8s部署Agent服务
  - 监控：健康检查、灰度发布、蓝绿部署
  - 数据安全与合规
  - 多模型推理服务架构

- Day 4（周四）: 世界模型前沿
  - 世界模型概念：让AI理解"世界怎么运转"
  - Sora、Genie等案例
  - 与Agent/数字员工的潜在结合

- Day 5（周五）: 具身智能前沿
  - 从软件Agent到具身Agent
  - 服务机器人、SLAM、人机交互
  - 云端大脑+边缘执行：数字员工控制物理设备

- Day 6（周六）: ⚡ 实战：量化部署实验
  - 任务：用llama.cpp对7B模型做INT4量化
  - 验证：量化前后大小、速度、质量对比

- Day 7（周日）: 🎓 W7-W19 大模型路线总复习 + 结业回顾

---

# W20-21：🧠 脑科学精华（个人兴趣）

> 从原来6周压缩到2周精华版，保留AI关联度最高的内容。

### W20：神经科学基础精选
- Day 1（周一）: 神经元与信号传递
  - 生物神经元 vs 人工神经元
  - 动作电位 vs 前向传播
  - 突触可塑性 vs 模型微调
- Day 2（周二）: 大脑结构与功能分区
  - 四大脑叶与核心区域
  - 海马体（记忆） vs 上下文窗口
  - 前额叶（决策） vs Agent规划
- Day 3（周三）: 记忆与学习
  - 短期/长期/工作记忆
  - 遗忘曲线与间隔学习
  - 海马体如何"写入"新记忆
- Day 4（周四）: 注意力与决策
  - 大脑注意力网络 vs Transformer自注意力
  - 多巴胺奖赏系统 vs 强化学习
  - 决策偏差：为什么人不是纯理性的
- Day 5（周五）: 语言的大脑机制
  - 布洛卡区（产出） vs 韦尼克区（理解）
  - 语言模型 vs 大脑语言处理
- Day 6（周六）: ⚡ 实战：可视化大脑-AI对比
  - 任务：画一张生物大脑 vs AI模型的架构对比图
- Day 7（周日）: 🔄 复习 W20 脑科学×AI交叉点

### W21：脑科学与AI交汇
- Day 1（周一）: 脑启发AI
  - 从感知器到Transformer：哪些是脑启发
  - 注意力机制真的是"大脑注意力"吗
- Day 2（周二）: 意识、记忆与通用智能
  - 意识的神经相关物（NCC）
  - AGI需要"意识"吗
  - 记忆的本质：大脑vs大模型vs数字员工
- Day 3（周三）: 脑机接口与未来
  - Neuralink、BrainGate等前沿
  - BCI如何改变人机交互
- Day 4（周四）: 神经科学与Agent优化
  - 课程学习 vs 预训练策略
  - 神经可塑性 vs 持续学习
  - 情绪与决策 vs Agent人格设计
- Day 5（周五）: 脑科学与AI的未来展望
  - 类脑计算、神经形态芯片
  - 2026年后可能突破的方向
- Day 6（周六）: ⚡ 实战：脑科学×AI终极对比项目
  - 任务：交互式脚本展示生物大脑vs AI在"学习"上的异同
- Day 7（周日）: 🎓 21周总复习 + 结业回顾
  - 从Transformer到数字员工到ChatBI到脑科学：完整知识脉络
  - 企业AI平台架构师能力总结
