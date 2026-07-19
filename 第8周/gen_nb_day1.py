#!/usr/bin/env python3
"""W8-Day1: Prompt工程进阶 - Notebook生成器"""
import json

cells = []

def add_md(text):
    lines = text.split('\n')
    source = [line + '\n' for line in lines[:-1]] + [lines[-1]]
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": source
    })

def add_code(code):
    lines = code.split('\n')
    source = [line + '\n' for line in lines[:-1]] + [lines[-1]]
    cells.append({
        "cell_type": "code",
        "metadata": {},
        "source": source,
        "execution_count": None,
        "outputs": []
    })

# ============ Cell 1: matplotlib中文字体配置 ============
add_code("""from matplotlib import font_manager
import matplotlib.pyplot as plt
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False
print(f"字体配置完成: {font_name}")""")

# ============ Cell 2: 标题与概述 ============
add_md("""# 🧠🤖 每日学习 | 第8周-Day1
# 📝 Prompt工程进阶

> **第8周主题：AI基础补强**
> Prompt工程实战、安全防御、结构化输出——为LangChat的Skill生成和Orchestrator的权限护栏打底

---

## 学习进度

```
W1-W6   AI基础与Agent入门（已完成）
W7      数字员工架构深化（已完成）
W8      AI基础补强（进行中）<-- 你在这里
W9-W18  待学
```

**进度条：38.9% (7/18周)**
`████████████████████████████████████░░░░░░░░░░░░░░░░░░`

## 今日学习目标

1. 理解 **System Prompt 设计模式**（角色-约束-输出模板-示例）
2. 掌握 **Few-Shot优化**策略：样本选择、顺序效应
3. 学会 **Structured Output**：JSON Schema约束、Function Calling输出控制
4. 业务关联：LangChat的Skill输出需要严格的Schema定义""")

# ============ Cell 3: 知识回顾 ============
add_md("""## 往期回顾（W7 数字员工架构）

| 日期 | 主题 | 核心要点 |
|------|------|----------|
| W7-D1 | 数字员工总览 | System Prompt + SOUL.md定义Agent人格 |
| W7-D2 | 记忆系统 | 三层记忆：短期/中期/长期，MEMORY.md持久化 |
| W7-D3 | 任务编排 | 工具编排、多工具链、Cron定时任务 |
| W7-D4 | 多Agent协作 | 主Agent + 子Agent，TaskFlow工作流 |
| W7-D5 | 质量保障 | 护栏设计：Prompt护栏-工具护栏-流程护栏 |

> 衔接思考：W7学的是Agent怎么"行动"，W8学的是怎么让模型"听话"地输出正确结果。没有可靠的Prompt工程，再好的Agent架构也会在"模型输出不稳定"上翻车！""")

# ============ Cell 4: System Prompt设计模式 ============
add_md("""## 今日新知识

### 一、System Prompt 设计模式

System Prompt 是大模型的"操作系统"——它定义了模型的角色、行为边界、输出格式和交互规则。

#### 1.1 四层架构模式

```
+---------------------------------------------+
|  Layer 1: 角色 (Role)                        |
|  "你是一个专业的商业地产数据分析助手"            |
+---------------------------------------------+
|  Layer 2: 约束 (Constraints)                 |
|  "不得泄露用户隐私，不得编造数据"               |
+---------------------------------------------+
|  Layer 3: 输出模板 (Output Template)          |
|  "输出JSON格式: {summary, data, suggestion}"  |
+---------------------------------------------+
|  Layer 4: 示例 (Examples)                    |
|  "例: 输入'本月客流' -> {summary:'...', ...}"  |
+---------------------------------------------+
```

#### 1.2 角色设定三要素

| 要素 | 说明 | 示例 |
|------|------|------|
| **身份** | 你是谁 | "你是LangChat的Skill编译器" |
| **专长** | 你擅长什么 | "擅长将自然语言需求转化为可执行的Skill Blueprint" |
| **行为边界** | 你不做什么 | "不执行未经审批的Skill发布" |

> 类比：就像给新员工发Offer时，要告诉他岗位名称（角色）、工作职责（专长）、公司红线（约束）。没有这些，新员工（模型）会"自由发挥"。""")

# ============ Cell 5: System Prompt代码示例 ============
add_code("""# System Prompt 设计模式示例：为LangChat Skill编译器设计System Prompt

system_prompt = \"\"\"# Role: LangChat Skill Compiler
你是LangChat平台的Skill编译器。你的职责是将自然语言需求转化为可执行的Skill Blueprint。

## Constraints
1. 不得编造不存在的工具或API
2. 所有输出必须为严格的JSON格式
3. 如遇到不明确的需求，输出 clarification_needed: true
4. Blueprint必须包含：inputs, outputs, steps, error_handling

## Output Format
{
  "blueprint_id": "string",
  "description": "string",
  "inputs": [{"name": "string", "type": "string", "required": true}],
  "outputs": [{"name": "string", "type": "string"}],
  "steps": [{"id": "int", "action": "string", "tool": "string"}],
  "error_handling": [{"error_type": "string", "action": "string"}],
  "clarification_needed": false
}

## Example
Input: "查询本月商铺租金收入并生成分析报告"
Output:
{
  "blueprint_id": "rent_analysis_001",
  "description": "查询租金收入并生成分析报告",
  "inputs": [{"name": "month", "type": "string", "required": true}],
  "outputs": [{"name": "report", "type": "markdown"}],
  "steps": [
    {"id": 1, "action": "query_rent_data", "tool": "shop.queryRent"},
    {"id": 2, "action": "analyze_data", "tool": "analysis.execute"},
    {"id": 3, "action": "generate_report", "tool": "report.generate"}
  ],
  "error_handling": [{"error_type": "no_data", "action": "return_empty_report"}],
  "clarification_needed": false
}
\"\"\"

print("System Prompt 设计完成")
print(f"Prompt长度: {len(system_prompt)} 字符")
print(f"包含角色定义: {'# Role' in system_prompt}")
print(f"包含约束规则: {'## Constraints' in system_prompt}")
print(f"包含输出格式: {'## Output Format' in system_prompt}")
print(f"包含示例: {'## Example' in system_prompt}")""")

# ============ Cell 6: Few-Shot优化 ============
add_md("""### 二、Few-Shot优化：样本选择策略

Few-Shot Prompting 是在Prompt中提供少量示例，让模型通过"模仿"来完成任务。

#### 2.1 Zero-shot vs One-shot vs Few-shot

```
Zero-shot:  "请分类这条评论的情感"         -> 模型靠猜，不稳定
One-shot:   "请分类... 示例: '好看' -> 正面"  -> 有一例参考
Few-shot:   "请分类... 示例1... 示例2... 示例3..."  -> 稳定输出
```

#### 2.2 样本选择四大策略

| 策略 | 原理 | 适用场景 |
|------|------|----------|
| **多样性采样** | 覆盖不同类型、长度、难度 | 通用分类任务 |
| **相似性采样** | 选取与输入最相似的样本 | 特定领域任务 |
| **困难负例** | 包含容易混淆的反例 | 边界清晰的分类 |
| **近期优先** | 最新的示例放最后 | 趋势性任务 |

> 关键洞察：示例的**顺序**会影响结果！把关键示例放在Prompt末尾（靠近用户输入），效果通常更好。这叫 **Recency Bias（近因偏差）**。

#### 2.3 Few-Shot的"甜蜜点"

- **2-5个示例**是性价比最高的区间
- 超过8个示例，边际收益急剧下降
- 示例质量 > 示例数量（1个高质量示例胜过10个低质量示例）""")

# ============ Cell 7: Few-Shot代码实战 ============
add_code("""# Few-Shot 样本选择策略实战
# 场景：为商管系统设计评论情感分类器

import random

# 模拟评论数据池
comment_pool = [
    {"text": "这家店服务超好，店员很热情！", "label": "正面", "category": "服务"},
    {"text": "商品质量差，再也不会来了", "label": "负面", "category": "质量"},
    {"text": "价格偏贵，但位置不错", "label": "中性", "category": "价格"},
    {"text": "环境很好，装修有品味", "label": "正面", "category": "环境"},
    {"text": "排队太久，体验很差", "label": "负面", "category": "服务"},
    {"text": "品牌挺多的，选择丰富", "label": "正面", "category": "品牌"},
    {"text": "停车不方便，绕了三圈", "label": "负面", "category": "设施"},
    {"text": "还行吧，没什么特别的", "label": "中性", "category": "综合"},
    {"text": "促销力度大，划算！", "label": "正面", "category": "价格"},
    {"text": "卫生间的卫生情况堪忧", "label": "负面", "category": "环境"},
]

# 策略1: 多样性采样 - 每个category选1个
def diverse_sampling(samples, n=3):
    \"\"\"确保覆盖不同类别\"\"\"
    by_category = {}
    for s in samples:
        by_category.setdefault(s['category'], []).append(s)
    result = []
    categories = list(by_category.keys())
    random.shuffle(categories)
    for cat in categories[:n]:
        result.append(random.choice(by_category[cat]))
    return result

# 策略2: 平衡采样 - 正面/负面/中性各选一个
def balanced_sampling(samples, n=3):
    by_label = {}
    for s in samples:
        by_label.setdefault(s['label'], []).append(s)
    result = []
    for label in ['正面', '负面', '中性']:
        candidates = by_label.get(label, [])
        if candidates:
            result.append(random.choice(candidates))
    return result

random.seed(42)  # 可复现
print("=" * 60)
print("Few-Shot 样本选择策略对比")
print("=" * 60)

print("\\n策略1: 多样性采样（覆盖不同类别）")
for s in diverse_sampling(comment_pool, 3):
    print(f"  [{s['label']}] {s['text']}  (类别: {s['category']})")

print("\\n策略2: 平衡采样（正/负/中各一）")
for s in balanced_sampling(comment_pool, 3):
    print(f"  [{s['label']}] {s['text']}  (类别: {s['category']})")

print("\\n业务关联：LangChat的Skill在处理用户评论分析时，")
print("   Few-Shot示例的选择直接影响分类准确率！")""")

# ============ Cell 8: Few-Shot可视化 ============
add_code("""import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 图1: 示例位置 vs 准确率
ax1 = axes[0]
positions = ['Pos 1\\n(开头)', 'Pos 2', 'Pos 3', 'Pos 4\\n(末尾)']
accuracy_random = [72, 75, 78, 85]
accuracy_classification = [68, 74, 80, 88]
x = range(len(positions))
width = 0.35
bars1 = ax1.bar([i - width/2 for i in x], accuracy_random, width, label='随机生成任务', color='#4ECDC4')
bars2 = ax1.bar([i + width/2 for i in x], accuracy_classification, width, label='分类任务', color='#FF6B6B')
ax1.set_xlabel('示例位置', fontsize=12)
ax1.set_ylabel('准确率 (%)', fontsize=12)
ax1.set_title('Few-Shot示例位置 vs 准确率\\n(末尾位置通常效果更好)', fontsize=13, fontweight='bold')
ax1.set_xticks(list(x))
ax1.set_xticklabels(positions)
ax1.legend()
ax1.set_ylim(60, 100)
for bar in bars1 + bars2:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{height}%', ha='center', va='bottom', fontsize=10)

# 图2: 示例数量 vs 准确率
ax2 = axes[1]
shot_counts = [0, 1, 2, 3, 5, 8, 10]
accuracy_by_count = [55, 72, 81, 86, 89, 91, 91.5]
ax2.plot(shot_counts, accuracy_by_count, 'o-', color='#9B59B6', linewidth=2, markersize=8)
ax2.fill_between(shot_counts, accuracy_by_count, alpha=0.1, color='#9B59B6')
ax2.axvspan(2, 5, alpha=0.15, color='green', label='甜蜜点 (2-5个)')
ax2.set_xlabel('Few-Shot 示例数量', fontsize=12)
ax2.set_ylabel('准确率 (%)', fontsize=12)
ax2.set_title('示例数量 vs 准确率\\n(2-5个示例性价比最高)', fontsize=13, fontweight='bold')
ax2.legend(fontsize=11)
ax2.set_ylim(50, 100)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('fewshot_analysis.png', dpi=100, bbox_inches='tight')
plt.show()
print("图表生成完成")""")

# ============ Cell 9: Structured Output ============
add_md("""### 三、Structured Output：让模型输出100%可控

在企业级AI平台中，模型输出的稳定性比"创意性"重要100倍。

#### 3.1 为什么需要结构化输出？

```
自由文本输出:
   模型: "本月租金总收入约为328万元，环比增长5.2%..."
   -> 下游系统无法解析，需要复杂的正则/NER

结构化输出:
   模型: {"total_rent": 3280000, "mom_growth": 0.052, "currency": "CNY"}
   -> 直接可以被JSON.parse()，下游系统零成本接入
```

#### 3.2 四大结构化输出技术

| 技术 | 原理 | 可靠性 | 适用场景 |
|------|------|--------|----------|
| **Prompt约束** | 在Prompt中要求输出JSON | 70-85% | 简单场景、快速原型 |
| **JSON Mode** | 模型层面强制输出合法JSON | 90-95% | 结构简单、固定Schema |
| **Function Calling** | 通过工具调用参数约束Schema | 95-99% | 企业级、复杂Schema |
| **Constrained Decoding** | 解码层强制JSON Schema | ~100% | 生产环境、零容错 |

> LangChat关联：Skill Compiler必须输出严格的Blueprint JSON Schema。使用Function Calling + Schema验证 + Retry机制三层保障，达到企业级99.9%的可靠性。""")

# ============ Cell 10: Structured Output代码实战 ============
add_code("""# Structured Output 实战：三层保障方案
import json
import re

# ========== 第一层：JSON Schema定义 ==========
skill_blueprint_schema = {
    "type": "object",
    "required": ["blueprint_id", "description", "inputs", "outputs", "steps"],
    "properties": {
        "blueprint_id": {
            "type": "string",
            "pattern": "^[a-z_]+_[0-9]+$",
            "description": "Blueprint ID"
        },
        "description": {"type": "string", "maxLength": 200},
        "inputs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type", "required"],
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": ["string", "number", "boolean", "array", "object"]},
                    "required": {"type": "boolean"}
                }
            }
        },
        "outputs": {"type": "array"},
        "steps": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "action"],
                "properties": {
                    "id": {"type": "integer", "minimum": 1},
                    "action": {"type": "string"},
                    "tool": {"type": "string"}
                }
            }
        }
    }
}

# ========== 第二层：验证函数 ==========
def validate_blueprint(blueprint):
    errors = []
    for field in skill_blueprint_schema['required']:
        if field not in blueprint:
            errors.append(f"缺少必需字段: {field}")
    bid = blueprint.get('blueprint_id', '')
    if not re.match(r'^[a-z_]+_[0-9]+$', bid):
        errors.append(f"blueprint_id格式错误: {bid}")
    if not blueprint.get('steps'):
        errors.append("steps不能为空")
    return errors

# ========== 第三层：测试 ==========
good_blueprint = {
    "blueprint_id": "rent_query_001",
    "description": "查询商铺租金收入",
    "inputs": [{"name": "shop_id", "type": "string", "required": True}],
    "outputs": [{"name": "rent_data", "type": "object"}],
    "steps": [{"id": 1, "action": "query", "tool": "shop.queryRent"}]
}

bad_blueprint = {
    "blueprint_id": "Invalid-ID!",
    "description": "测试",
    "inputs": [],
    "outputs": [],
    "steps": []
}

print("=" * 50)
print("验证测试")
print("=" * 50)

errors_good = validate_blueprint(good_blueprint)
errors_bad = validate_blueprint(bad_blueprint)

print(f"\\n合法Blueprint: {'通过' if not errors_good else '失败'}")
if errors_good:
    for e in errors_good: print(f"   - {e}")

print(f"\\n非法Blueprint: {'通过' if not errors_bad else '失败'}")
for e in errors_bad: print(f"   - {e}")

print("\\n这就是LangChat Validator的核心逻辑——")
print("   在Skill发布前，确保Blueprint 100%符合Schema规范！")""")

# ============ Cell 11: Function Calling ============
add_md("""### 四、Function Calling输出控制

Function Calling 是比JSON Mode更强的结构化输出方案。

#### 4.1 工作原理

```
1. 定义Tool Schema（JSON Schema格式）
     |
2. 用户提问 -> 模型决定是否需要调用Tool
     |
3. 模型生成Tool调用参数（自动符合Schema）
     |
4. 执行Tool -> 获取结果 -> 返回用户
```

#### 4.2 Function Calling vs JSON Mode

| 对比项 | JSON Mode | Function Calling |
|--------|-----------|------------------|
| **可靠性** | ~95% | ~99% |
| **Schema表达力** | 基础类型 | 复杂嵌套、枚举、正则 |
| **工具执行** | 不支持 | 内置支持 |
| **多工具选择** | 不支持 | 支持（模型自动选工具） |
| **适用场景** | 简单数据提取 | 企业级Tool调用 |

> Orchestrator关联：Orchestrator的capability路由就是基于Function Calling——用户说"查询本月租金"，模型自动选择 shop.queryRent 工具，生成参数 {"month": "2026-07"}。""")

# ============ Cell 12: Function Calling实战 ============
add_code("""# Function Calling 模拟实战
# 场景：Orchestrator路由用户请求到不同的Capability

tools = [
    {
        "name": "shop.queryRent",
        "description": "查询指定商铺的租金信息",
        "parameters": {
            "type": "object",
            "properties": {
                "shop_id": {"type": "string", "description": "商铺ID"},
                "month": {"type": "string", "description": "查询月份 YYYY-MM"}
            },
            "required": ["shop_id"]
        }
    },
    {
        "name": "member.queryPoints",
        "description": "查询会员积分余额",
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {"type": "string", "description": "会员ID"}
            },
            "required": ["member_id"]
        }
    },
    {
        "name": "analysis.generateReport",
        "description": "生成经营分析报告",
        "parameters": {
            "type": "object",
            "properties": {
                "report_type": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                "project_id": {"type": "string", "description": "项目ID"}
            },
            "required": ["report_type", "project_id"]
        }
    }
]

test_cases = [
    {"user_input": "帮我查一下A201商铺上个月的租金",
     "expected_tool": "shop.queryRent",
     "expected_params": {"shop_id": "A201", "month": "2026-06"}},
    {"user_input": "我的会员积分还有多少？",
     "expected_tool": "member.queryPoints",
     "expected_params": {"member_id": "需要追问"}},
    {"user_input": "生成本月经营月报",
     "expected_tool": "analysis.generateReport",
     "expected_params": {"report_type": "monthly", "project_id": "需要追问"}}
]

print("=" * 60)
print("Function Calling 模拟测试")
print("=" * 60)

for i, tc in enumerate(test_cases, 1):
    print(f"\\n测试 {i}: {tc['user_input']}")
    print(f"   -> 路由到: {tc['expected_tool']}")
    tool_def = next((t for t in tools if t['name'] == tc['expected_tool']), None)
    if tool_def:
        required = tool_def['parameters'].get('required', [])
        print(f"   -> 必需参数: {required}")
        for param in required:
            val = tc['expected_params'].get(param, '')
            if '追问' in str(val):
                print(f"   -> 需要追问: 请提供 {param}")

print("\\n" + "=" * 60)
print("这就是Orchestrator的核心能力——")
print("   通过Function Calling将自然语言路由到正确的Capability！")""")

# ============ Cell 13: 英文术语 ============
add_md("""## 英文术语（10个）

| # | 术语 | 音标 | 释义 |
|---|------|------|------|
| 1 | **System Prompt** | /ˈsɪstəm prɒmpt/ | 系统提示词，定义模型角色和行为规则 |
| 2 | **Few-Shot Prompting** | /fjuː ʃɒt ˈprɒmptɪŋ/ | 少样本提示，用少量示例引导模型 |
| 3 | **Structured Output** | /ˈstrʌktʃərd ˈaʊtpʊt/ | 结构化输出，JSON等固定格式输出 |
| 4 | **JSON Schema** | /ˈdʒeɪsən ˈskiːmə/ | JSON数据结构定义规范 |
| 5 | **Function Calling** | /ˈfʌŋkʃən ˈkɔːlɪŋ/ | 函数调用，模型自动选择并调用工具 |
| 6 | **Constrained Decoding** | /kənˈstreɪnd diːˈkoʊdɪŋ/ | 约束解码，生成时强制符合Schema |
| 7 | **Recency Bias** | /ˈriːsənsi ˈbaɪəs/ | 近因偏差，末尾信息影响更大 |
| 8 | **Zero-Shot** | /ˈzɪəroʊ ʃɒt/ | 零样本，不给示例直接让模型完成任务 |
| 9 | **Output Template** | /ˈaʊtpʊt ˈtɛmplət/ | 输出模板，预定义输出格式 |
| 10 | **Guardrail** | /ˈɡɑːrdreɪl/ | 护栏，限制模型行为的安全机制 |""")

# ============ Cell 14: 课堂练习 ============
add_md("""## 课堂练习

### 练习1：System Prompt诊断

以下System Prompt有什么问题？请找出至少3个改进点：

```
你是一个助手。帮我处理用户的问题。
能回答的尽量回答，不能回答的想办法回答。
```

### 练习2：选择Few-Shot策略

场景：你需要让模型判断商业地产评论是"投诉"、"建议"还是"咨询"。

思考：
1. 你会选择哪种Few-Shot策略？
2. 需要多少个示例？
3. 示例应该怎么排列？

> 把你的答案发给我，我来帮你批改！""")

# ============ Cell 15: 课后测试 ============
add_md("""## 课后测试

**1.** System Prompt的四层架构是哪四层？请按从上到下排列。

**2.** Few-Shot示例数量与效果的关系是什么？为什么超过8个示例边际收益急剧下降？

**3.** 以下哪种结构化输出技术可靠性最高？
- A. Prompt约束
- B. JSON Mode
- C. Function Calling
- D. Constrained Decoding

**4.** Recency Bias是什么意思？在Few-Shot中如何利用这个特性？

**5.** 业务思考题：如果LangChat的Skill Compiler生成的Blueprint有5%的概率格式错误，在1000次/天的调用量下，每天会有多少次失败？你会怎么解决？

> 答案明天揭晓！""")

# ============ Cell 16: 推荐资源 ============
add_md("""## 推荐学习资源

### 视频（B站）
1. [全网最详细的提示词工程教程，7天从入门到进阶实战](https://www.bilibili.com/video/BV1MpTq6BEGP/)
2. [2025讲的最好的提示词工程教程，全程干货](https://www.bilibili.com/video/BV19psRzpEPX/)

### 文章（知乎/CSDN）
1. [大语言模型结构化输出技术原理和实现 - 知乎](https://zhuanlan.zhihu.com/p/1966532664434599045)
2. [Few-shot prompt：通过少量样本提示提升大模型表现 - CSDN](https://blog.csdn.net/rengang66/article/details/156771399)

### 延伸阅读
- [LLM结构化输出：JSON Schema约束 vs Tool Calling - 知乎](https://zhuanlan.zhihu.com/p/2029564108513585085)
- [Prompt Engineering 完整学习指南 - 知乎](https://zhuanlan.zhihu.com/p/1993811969258587128)""")

# ============ Cell 17: 知识串联图 ============
add_md("""## 今日知识串联

```
              Prompt工程进阶
             /      |        \\
     System Prompt  Few-Shot   Structured Output
     四层架构       优化策略     三大技术
        |           |              |
   角色定义      样本选择        JSON Schema
   约束规则      顺序效应        Function Calling
   输出模板      数量甜蜜点      Constrained Decoding
   示例引导      (2-5个)        
        |           |              |
        +-----+-----+------+-------+
              |            |
     LangChat Skill      Orchestrator
     输出严格Schema       Capability路由
     Blueprint可控        Function Calling
```

> 明日预告：Prompt安全与护栏——如何防御Prompt Injection攻击！""")

# ============ Cell 18: 总结 ============
add_md("""## 今日总结

| 知识点 | 核心要点 | 业务关联 |
|--------|----------|----------|
| System Prompt设计 | 角色-约束-模板-示例 四层架构 | LangChat的Skill定义 |
| Few-Shot优化 | 2-5个高质量示例，末尾放最相似的 | 提升模型输出一致性 |
| Structured Output | Function Calling > JSON Mode > Prompt约束 | Skill Compiler输出保障 |
| Function Calling | 模型自动选工具+生成参数 | Orchestrator的路由核心 |

> 记住：在企业级AI平台中，**可控性 > 创造性**。让模型"听话"比让模型"聪明"更重要！""")

# ============ 生成Notebook ============
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

output_path = "/root/learning-notebooks/第8周/第8周-Day1-Prompt工程进阶.ipynb"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print(f"Notebook生成完成: {output_path}")
print(f"Cells数量: {len(cells)}")

# 验证
with open(output_path, 'r', encoding='utf-8') as f:
    json.load(f)
print("JSON验证通过!")
