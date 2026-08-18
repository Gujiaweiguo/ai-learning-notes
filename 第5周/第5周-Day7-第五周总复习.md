# 第5周 Day7：第五周总复习——推理能力全景回顾

> **导语**：这一周我们没有学一个孤立技巧，而是搭建了一套从“会答”到“会想、会查、会验证”的能力体系。今天把 CoT、ToT、R1、评测、Prompt 实验和 Agent 放在同一张地图上：知道它们分别解决什么问题，也知道什么时候不该用它们。

## 学习进度

```
W1 Transformer 基础 ✅ → W2 深入架构 ✅ → W3 训练全景 ✅ → W4 RAG 检索 ✅ → W5 推理 🔵进行中
```

## 为什么需要全景回顾

知识点单独看都容易：CoT 是一步步想，ToT 是多分支，R1 是推理模型。但真实系统不按教材章节运行。用户问一个复杂问题时，可能先要 RAG 找到资料，再用 CoT 计算，再调用工具验证，最后由 Agent 决定是否需要人工确认。

全景回顾的价值，是把“名词记忆”变成“技术选型能力”。就像会开车不只要记住方向盘、刹车和油门，还要知道什么路况该减速、什么时候该看后视镜。

## 核心原理详解

### 1. 从 W1 到 W5 的能力链

- **W1 Transformer 基础**：模型通过注意力机制理解序列中词与词的关系。
- **W2 Transformer 深入**：多头注意力、残差连接、归一化让深层网络稳定学习。
- **W3 训练全景**：预训练提供通识能力，SFT 教会任务格式，偏好/强化学习优化行为。
- **W4 RAG 检索**：遇到训练时没有或会变化的信息，先从可信知识库取证。
- **W5 推理能力**：把问题拆开、比较路径、检查中间结论，把知识和证据组织成答案。

这条链路说明：推理不是替代知识或检索。没有事实证据的推理可能很漂亮却是错的；没有推理的检索可能拿到资料却不会应用。

### 2. 本周技术地图

| 技术 | 核心问题 | 类比 | 适用场景 | 主要代价 |
|---|---|---|---|---|
| CoT | 如何避免跳步 | 草稿纸 | 数学、规则、多步骤分析 | 输出变长 |
| ToT | 如何避免一条路走错 | 导航多路线 | 规划、搜索、开放难题 | 分支计算多 |
| Self-consistency | 如何交叉验证 | 多人对账 | 高价值判断 | 多次采样 |
| DeepSeek R1 式推理 | 如何把深思考训练进模型 | 慢思考系统 | 数学、代码、复杂推理 | 延迟与 Token 高 |
| RAG | 如何获得新事实 | 查档案 | 企业知识、实时政策 | 依赖检索质量 |
| Agent | 如何把推理变行动 | 项目经理 + 工具箱 | 多工具工作流 | 权限和安全复杂 |

### 3. 技术选择决策树

先问四个问题：

1. **答案是否依赖最新或私有事实？** 是，则优先 RAG/数据库/工具，不要只让模型记忆回答。
2. **任务是否需要两步以上推导？** 是，则给 CoT 结构或使用推理模型。
3. **是否存在多种可行方案？** 是，则用 ToT、候选采样或情景分析比较路径。
4. **结果是否会触发外部动作或高风险影响？** 是，则让 Agent 做证据核验、权限检查和人工确认。

一个简化原则：**越接近外部真实世界，越要用工具和验证；越接近主观表达，越要用清晰任务定义和人工品控。**

### 4. 推理可靠性的四层防线

第一层是 Prompt：明确输入、目标、边界和格式。第二层是推理：把复杂问题拆成可检查步骤。第三层是证据：用检索、数据库、计算器验证事实。第四层是治理：权限、审计、人工在环和回归测试。

只靠其中一层都不够。比如 CoT 可以让计算过程可见，却无法证明引用的库存数字是真实的；RAG 可以给出处，却不保证模型正确理解了规则；Agent 能调用 API，却可能因权限错误造成外部副作用。

## 代码实战

### 1. 中文字体配置与全景图

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 统一中文字体设置，确保图表可读
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

weeks = ["W1\n基础", "W2\n架构", "W3\n训练", "W4\nRAG", "W5\n推理"]
values = [2, 4, 6, 8, 10]  # 仅用于绘制演进位置，不代表真实评分

plt.figure(figsize=(11, 4))
plt.plot(weeks, values, marker="o", linewidth=3, color="#4c9f9a")
for week, value in zip(weeks, values):
    plt.text(week, value + 0.35, week.replace("\n", " "), ha="center")
plt.title("W1-W5：从模型基础到推理能力")
plt.ylabel("能力链位置（教学示意）")
plt.grid(alpha=0.25)
plt.tight_layout()
plt.show()
```

### 2. 用规则实现一个技术路由器

```python
def choose_reasoning_strategy(needs_fresh_facts: bool,
                              step_count: int,
                              has_multiple_plans: bool,
                              is_high_risk: bool) -> list[str]:
    """根据任务特征返回建议技术组合，而非只选一个模型。"""
    plan = []

    # 新鲜或私有事实先检索，这是避免幻觉的基础
    if needs_fresh_facts:
        plan.append("RAG/数据库查询")

    # 多步任务需要可审阅的分解过程
    if step_count >= 2:
        plan.append("CoT 或推理模型")

    # 有多种方案时再增加分支搜索，避免不必要开销
    if has_multiple_plans:
        plan.append("ToT/候选方案比较")

    # 高风险任务必须加入工具验证和人工确认
    if is_high_risk:
        plan.append("工具验证 + 人工确认")

    return plan or ["Zero-shot 直接回答"]

print(choose_reasoning_strategy(True, 4, True, True))
print(choose_reasoning_strategy(False, 1, False, False))
```

逐行理解：这个函数没有假装“智能”，而是把决策依据显式写成参数。生产系统可由分类模型或 LLM 提取这些参数，但最终策略应可审计、可测试。

### 3. 端到端的可验证推理示例

```python
def analyze_restock(stock: int, daily_sales: int, lead_days: int) -> dict:
    """用可解释公式给出补货风险，而非仅给一句建议。"""
    # 计算到货前预计消耗的数量
    demand_during_lead = daily_sales * lead_days
    # 安全库存以两天销量为例；真实业务需按波动率计算
    safety_stock = daily_sales * 2
    # 当库存不足以覆盖提前期需求加安全库存时，提示补货
    reorder_needed = stock < demand_during_lead + safety_stock

    return {
        "stock": stock,
        "lead_day_demand": demand_during_lead,
        "safety_stock": safety_stock,
        "reorder_needed": reorder_needed,
        "reason": "库存低于提前期需求加安全库存" if reorder_needed else "库存暂可覆盖需求",
    }

print(analyze_restock(stock=95, daily_sales=18, lead_days=4))
```

这段代码体现了本周思路：先取事实（库存、销量、交期），再做透明计算，最后输出结论和原因。若 Agent 要真的创建采购单，仍必须经过供应商、预算和人工审批工具。

## 可视化：技术的准确率与成本权衡

```python
methods = ["零样本", "CoT", "ToT", "R1式推理", "RAG+Agent"]
accuracy = [62, 82, 87, 90, 92]     # 教学模拟，不是通用榜单
cost = [1, 2, 4, 5, 4]              # 相对成本

fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(methods, accuracy, marker="o", color="#d96d73", label="准确率")
ax1.set_ylabel("准确率（示意）", color="#d96d73")
ax1.set_ylim(0, 100)
ax1.grid(alpha=0.25)

ax2 = ax1.twinx()
ax2.bar(methods, cost, alpha=0.35, color="#4c9f9a", label="相对成本")
ax2.set_ylabel("相对成本", color="#4c9f9a")
plt.title("推理技术的效果与成本不是单调关系")
plt.tight_layout()
plt.show()
```

图不是为了宣称某技术一定胜出，而是提醒：复杂方案的收益要和成本、延迟、可维护性一起评估。RAG+Agent 可能比纯推理更可靠，是因为它补上了事实来源；但它也多了检索失败、权限控制、工具超时等工程问题。

## 业务关联：LangChat / Agent

一个可落地的 LangChat 工作流可以这样拆：

1. 用户问“这周柠檬茶要不要补货”。
2. Agent 识别这是库存决策，高风险但可读。
3. 调库存、近 7 天销量、供应商交期工具。
4. 用 CoT/公式计算提前期需求与安全库存。
5. 输出证据、计算、建议和不确定因素。
6. 用户或店长确认后，才调用采购单创建工具。

这个流程的关键不是模型说得像专家，而是每一步都有数据来源、业务规则和可撤回的控制点。

## 常见误区

1. **把 RAG 当成推理**：RAG 找资料，推理负责使用资料，两者都需要。
2. **把长回答当成深思考**：长度不是质量，关键是中间结论能否验证。
3. **把 ToT 用在每个任务**：分支搜索昂贵，简单任务应直接解决。
4. **模型选型只看榜单**：还要用真实脱敏业务集测试格式、延迟和安全。
5. **Agent 能调用工具就可以自动执行**：写操作必须有最小权限、审计与人工确认。

## 课堂练习

1. 给“客户投诉饮品变味”设计一条 Agent 推理链：哪些信息该检索，哪些工具该调用，在哪一步转人工？
2. 把“本月利润下降”拆成至少五个可验证的子问题。
3. 对“是否降价”分别设计 CoT、ToT 和反事实分析的提示结构，比较它们的差异。

## 课后测试

**1. RAG 最主要解决什么？** A. 获取外部/最新事实 B. 代替计算器 C. 删除权限 D. 生成图片

**2. ToT 最适合什么问题？** A. 单步事实题 B. 多路径规划问题 C. 固定翻译 D. 无输入任务

**3. 高风险 Agent 动作前最需要什么？** A. 更长回答 B. 工具证据、权限检查和人工确认 C. 更高温度 D. 更多表情

**4. CoT 的主要价值？** A. 随机性 B. 将多步推导显式化 C. 取代知识库 D. 减少所有 Token

**5. 简答**：请解释“检索正确但推理错误”与“推理正确但事实过期”各是什么情况，怎样分别防范？

## 术语表

| 英文 | 音标 | 中文 |
|---|---|---|
| Chain-of-Thought | /tʃeɪn əv θɔːt/ | 思维链 |
| Tree-of-Thought | /triː əv θɔːt/ | 思维树 |
| Reasoning Model | /ˈriːzənɪŋ ˈmɒdl/ | 推理模型 |
| GRPO | /dʒiː ɑːr piː əʊ/ | 群组相对策略优化 |
| Benchmark | /ˈbentʃmɑːk/ | 基准测试 |
| Prompt Engineering | /prɒmpt ˌendʒɪˈnɪərɪŋ/ | 提示工程 |
| Retrieval-Augmented Generation | /rɪˈtriːvəl ɔːɡˈmentɪd ˌdʒenəˈreɪʃən/ | 检索增强生成 |
| Agent | /ˈeɪdʒənt/ | 智能体 |
| Tool Calling | /tuːl ˈkɔːlɪŋ/ | 工具调用 |
| Verification | /ˌverɪfɪˈkeɪʃən/ | 验证 |
| Human-in-the-loop | /ˈhjuːmən ɪn ðə luːp/ | 人工在环 |

## 参考资源

- Wei et al., *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*
- Yao et al., *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*
- DeepSeek-AI, *DeepSeek-R1 Technical Report*
- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*
- 建议：完成本周后，选一个真实但脱敏的业务问题，写出“证据—推理—验证—行动”的完整流程图。

## 补充：一页纸复盘法

复盘一个 AI 回答时，可以用一页纸按四栏记录。第一栏写**事实**：用户给了什么、工具查到了什么、哪些数据有时间戳；第二栏写**推理**：模型依据哪些规则得出中间结论；第三栏写**验证**：哪些计算被计算器复核、哪些来源可点击追溯；第四栏写**行动**：只是建议，还是已经执行了外部操作，谁确认的。

这四栏能很快暴露问题位置。若事实错，应修检索或数据接口；若事实对但结论错，应修 Prompt、规则或推理模型；若结论对但动作错，应修权限、确认和工作流。不要把所有错误都归结为“模型幻觉”，否则团队无法找到真正的工程改进点。

### 综合练习：设计你的推理工作流

选择“为门店制定周末促销方案”作为任务，至少写出：

- 输入事实：近四周销量、每个品类毛利、库存、竞品价格、活动预算。
- 证据工具：销售数据库、库存系统、价格表、活动规则库。
- 推理结构：先计算各品类利润与库存压力，再用反事实比较满减、折扣、赠品三个方案。
- 验证机制：预算不能超限，折后价格不能低于规定毛利线，关键数字由计算器复核。
- 行动边界：Agent 只提交方案草稿；发布优惠券和改价必须由授权人员确认。

如果能把这五项写清楚，你已经不只是“会用 Prompt”，而是在设计一个可控的推理系统。