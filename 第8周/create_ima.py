#!/usr/bin/env python3
"""W8-Day1 IMA笔记创建"""
import json
import subprocess
import time
import sys

IMA_CLIENT_ID = open("/root/.config/ima/client_id").read().strip()
IMA_API_KEY = open("/root/.config/ima/api_key").read().strip()

content = r"""# 第8周-Day1-Prompt工程进阶

## 课程目标

今天是第8周的第1天，我们进入一个全新的主题：**AI基础补强**。本周的目标是为LangChat的Skill生成和Orchestrator的权限护栏打下坚实的Prompt工程基础。

在前面7周的学习中，我们已经掌握了Transformer、RAG、推理思维链、Agent架构、数字员工等核心技术。但从今天开始，我们要回头补强一个看似简单实则深奥的基础能力——**让大模型精确地做你想让它做的事**。

这听起来简单，但在企业级场景中，这是最核心的工程挑战。想象一下：LangChat的Skill Compiler每天要处理上千次"自然语言→Blueprint"的转换，如果Prompt设计不到位，5%的格式错误率就意味着每天50次失败——这在企业场景中是不可接受的。

---

## 一、System Prompt 设计模式

### 1.1 System Prompt是什么？

System Prompt是大模型的"操作系统"。它不是普通的对话开场白，而是定义了模型在整个会话中的角色、行为边界、输出格式和交互规则的**根本性指令**。

打个生活类比：System Prompt就像是给新员工的《员工手册》。一份好的员工手册要告诉新员工：
- 你的岗位是什么（角色）
- 你能做什么、不能做什么（约束）
- 你的工作产出应该长什么样（输出模板）
- 别人是怎么做的（示例）

如果你只写"你是一个助手，帮我处理问题"，就好比给新员工发了一张白纸说"看着办"——结果可想而知。

### 1.2 四层架构模式

经过大量工程实践，我总结出企业级System Prompt应该包含四个层次：

**Layer 1: 角色（Role）**——定义模型身份。关键三要素：身份（你是谁）、专长（你擅长什么）、行为边界（你不做什么）。例如："你是LangChat平台的Skill编译器，擅长将自然语言需求转化为可执行的Skill Blueprint，不执行未经审批的Skill发布。"

**Layer 2: 约束（Constraints）**——定义红线。例如："不得编造不存在的工具或API"、"所有输出必须为严格的JSON格式"、"遇到不明确的需求时，输出clarification_needed: true而不是猜测"。

**Layer 3: 输出模板（Output Template）**——定义输出格式。这一层非常关键：你不应该只说"输出JSON"，而应该给出完整的JSON Schema或模板，包括每个字段的类型、是否必需、取值范围。

**Layer 4: 示例（Examples）**——提供Few-Shot引导。给1-3个完整的"输入→输出"示例，让模型通过模仿来理解你到底要什么。

### 1.3 实际代码示例

让我们看一个完整的System Prompt设计——为LangChat Skill编译器设计的System Prompt：

角色定义："你是LangChat平台的Skill编译器"。约束包括：不得编造工具、必须输出JSON、不明确时请求澄清。输出模板定义了完整的Blueprint JSON结构：blueprint_id、description、inputs、outputs、steps、error_handling、clarification_needed。

最关键的是示例部分：我们给出了一个完整的"查询本月商铺租金收入并生成分析报告"的Blueprint示例。这个示例让模型知道：steps要按执行顺序排列、每个step要绑定具体的tool、error_handling要考虑"无数据"等边界情况。

### 1.4 业务关联思考

💡 对应LangChat：Skill的定义本质上就是一套System Prompt。角色=Skill的身份和职责，约束=安全边界和权限规则，模板=Blueprint Schema，示例=参考Skill。

💡 对应Orchestrator：Orchestrator的路由决策也依赖System Prompt来定义"什么请求路由到什么Capability"。

---

## 二、Few-Shot优化：样本选择策略

### 2.1 什么是Few-Shot？

Few-Shot Prompting是在Prompt中提供少量"输入→输出"示例，让模型通过"模仿"来完成新任务。

三种模式对比：
- **Zero-shot**：不给示例，直接让模型完成任务。模型靠"猜"，输出不稳定。
- **One-shot**：给1个示例。模型有了一个参考，但覆盖面不够。
- **Few-shot**：给2-5个示例。模型能识别模式，稳定输出。

生活类比：教小朋友认识水果。
- Zero-shot = "这是什么水果？"（不给参考，小朋友可能乱猜）
- One-shot = "这是苹果。那这个呢？"（有一个参考）
- Few-shot = "这是苹果，这是香蕉，这是橙子。那这个呢？"（有多个参考，小朋友能找出规律）

### 2.2 样本选择四大策略

**策略1：多样性采样**——确保示例覆盖不同类型、长度、难度。适用于通用分类任务。例如做情感分类时，评论数据应该包含服务、质量、价格、环境等不同维度的示例。

**策略2：相似性采样**——选取与当前输入最相似的样本作为示例。适用于特定领域任务。技术上可以通过embedding相似度来动态选择最相关的Few-Shot示例。

**策略3：困难负例**——在示例中包含容易混淆的边界案例。例如"价格偏贵，但位置不错"这种混合情感的评论，帮助模型学会处理"既有正面又有负面"的复杂情况。

**策略4：近期优先**——把最新的、与当前输入最相似的示例放在Prompt末尾。这里涉及一个重要发现——Recency Bias。

### 2.3 Recency Bias（近因偏差）

研究发现，示例在Prompt中的**位置**会显著影响效果。把关键示例放在Prompt末尾（靠近用户输入的位置），效果通常比放在开头好10-15%。

原因是大模型对最近看到的内容"记忆更深刻"（这和人类的近因效应类似）。所以Few-Shot排列的黄金法则是：**通用示例放前面，与当前输入最相似的示例放最后**。

### 2.4 数量的"甜蜜点"

多少个示例最好？研究表明：
- **2-5个示例**是性价比最高的区间
- 超过8个示例，边际收益急剧下降（准确率提升不到1%，但Token成本翻倍）
- **示例质量远比数量重要**：1个精心设计的示例胜过10个随意的示例

打比方：就像培训新员工，给他3个典型案例精讲，效果远好于丢给他20个案例让他自己看。

### 2.5 业务关联思考

💡 对应LangChat：Skill在处理用户意图分类时，Few-Shot示例的选择直接影响分类准确率。精心设计的3-5个示例，可能比增加一个微调模型效果更好，而且成本低100倍。

💡 对应商管系统：当用户说"这个月租金怎么样"，Few-Shot示例告诉模型应该调用shop.queryRent工具并生成{"month": "2026-07"}参数，而不是自由发挥。

---

## 三、Structured Output：让模型输出100%可控

### 3.1 为什么需要结构化输出？

在企业级AI平台中，模型输出的**稳定性比创意性重要100倍**。

自由文本输出的模型说"本月租金总收入约为328万元，环比增长5.2%"，下游系统无法直接解析——需要复杂的正则表达式或NER来提取信息。

结构化输出的模型直接返回 {"total_rent": 3280000, "mom_growth": 0.052, "currency": "CNY"}，下游系统一个JSON.parse()就搞定。

### 3.2 四大结构化输出技术

**青铜段位：Prompt约束**——在Prompt中要求"请输出JSON格式"。可靠性约70-85%，因为模型可能添加额外说明文字、忘记闭合括号、或混用中英文标点。适用于快速原型验证。

**白银段位：JSON Mode**——OpenAI等厂商提供的JSON Mode，在模型层面强制输出合法JSON。可靠性约90-95%。但JSON Mode只保证"是合法JSON"，不保证"符合你的Schema"。

**王者段位：Function Calling**——通过工具调用的参数定义来约束输出Schema。模型在生成参数时自动遵循Schema定义的类型、枚举值、必填字段。可靠性约95-99%。这是目前企业级应用的主流方案。

**神仙段位：Constrained Decoding（约束解码）**——在模型解码阶段就强制每一步生成符合JSON Schema。原理是：在每生成一个token时，检查"按照Schema，下一个合法的token是什么"，不合法的token直接被屏蔽。可靠性接近100%。

### 3.3 JSON Schema约束原理

JSON Schema是定义"JSON数据必须长什么样"的规范。它可以约束：
- **类型**：字段必须是string/number/array/object/boolean
- **必需字段**：哪些字段必须有
- **取值范围**：数字的最小最大值、字符串的正则模式、数组的长度限制
- **枚举值**：字段值只能是某几个选项之一
- **嵌套结构**：对象内嵌对象、数组内嵌对象等

Constrained Decoding的原理就像给模型装了一个"语法检查器"——不是生成完再检查，而是**在生成过程中就约束**。每生成一个token，都检查是否与Schema兼容，不兼容的token概率直接设为0。

### 3.4 Function Calling工作流程

Function Calling比JSON Mode更强的地方在于它不仅约束输出格式，还内置了"工具调用"的完整流程：

第一步：开发者定义Tool Schema（工具的名称、描述、参数schema）
第二步：用户提问，模型分析是否需要调用某个Tool
第三步：如果需要，模型生成Tool调用参数（自动符合Schema）
第四步：开发者代码执行Tool，获取结果
第五步：模型根据结果生成最终回答

### 3.5 三层保障方案

在LangChat的企业级场景中，单靠一种技术不够。我设计了"三层保障方案"：

第一层：JSON Schema定义——明确定义Blueprint的所有字段、类型、约束
第二层：验证函数——在代码层面验证模型输出是否符合Schema
第三层：Retry机制——如果验证失败，自动重试（通常最多3次），附带错误提示让模型修正

这三层叠加，可以将输出可靠性从95%提升到99.9%+。

### 3.6 业务关联思考

💡 对应LangChat：Skill Compiler必须输出严格的Blueprint JSON Schema。使用Function Calling + Schema验证 + Retry机制三层保障，达到企业级可靠性。

💡 对应Orchestrator：Orchestrator的capability路由就是基于Function Calling——用户说"查询本月租金"，模型自动选择shop.queryRent工具，生成参数{"month": "2026-07"}。

💡 成本思考：如果Skill Compiler有5%的格式错误率，每天1000次调用就有50次失败。假设每次失败需要人工处理（成本20元/次），每天损失1000元，每月3万元。投入精力做好Structured Output，每月省3万——这就是Prompt工程的ROI。

---

## 四、Function Calling vs JSON Mode 详细对比

| 对比项 | JSON Mode | Function Calling |
|--------|-----------|------------------|
| 可靠性 | ~95% | ~99% |
| Schema表达力 | 基础类型 | 复杂嵌套、枚举、正则 |
| 工具执行 | 不支持 | 内置支持 |
| 多工具选择 | 不支持 | 支持（模型自动选工具） |
| 参数验证 | 仅JSON合法性 | Schema级别验证 |
| 适用场景 | 简单数据提取 | 企业级Tool调用 |

关键区别：JSON Mode只保证"输出是合法JSON"，而Function Calling保证"输出符合你定义的具体Schema，并且模型知道什么时候该调用什么工具"。

---

## 五、英文术语表

1. **System Prompt** /ˈsɪstəm prɒmpt/ —— 系统提示词，定义模型角色和行为规则
2. **Few-Shot Prompting** /fjuː ʃɒt ˈprɒmptɪŋ/ —— 少样本提示，用少量示例引导模型
3. **Structured Output** /ˈstrʌktʃərd ˈaʊtpʊt/ —— 结构化输出，JSON等固定格式输出
4. **JSON Schema** /ˈdʒeɪsən ˈskiːmə/ —— JSON数据结构定义规范
5. **Function Calling** /ˈfʌŋkʃən ˈkɔːlɪŋ/ —— 函数调用，模型自动选择并调用工具
6. **Constrained Decoding** /kənˈstreɪnd diːˈkoʊdɪŋ/ —— 约束解码，生成时强制符合Schema
7. **Recency Bias** /ˈriːsənsi ˈbaɪəs/ —— 近因偏差，末尾信息影响更大
8. **Zero-Shot** /ˈzɪəroʊ ʃɒt/ —— 零样本，不给示例直接让模型完成任务
9. **Output Template** /ˈaʊtpʊt ˈtɛmplət/ —— 输出模板，预定义输出格式
10. **Guardrail** /ˈɡɑːrdreɪl/ —— 护栏，限制模型行为的安全机制

---

## 六、推荐学习资源

### 视频（B站）
1. [全网最详细的提示词工程教程，7天从入门到进阶实战](https://www.bilibili.com/video/BV1MpTq6BEGP/)
2. [2025最好的Prompt工程教程，全程干货](https://www.bilibili.com/video/BV19psRzpEPX/)

### 文章（知乎/CSDN）
1. [大语言模型结构化输出技术原理和实现 - 知乎](https://zhuanlan.zhihu.com/p/1966532664434599045)
2. [Few-shot prompt：通过少量样本提示提升大模型表现 - CSDN](https://blog.csdn.net/rengang66/article/details/156771399)
3. [LLM结构化输出：JSON Schema约束 vs Tool Calling - 知乎](https://zhuanlan.zhihu.com/p/2029564108513585085)
4. [Prompt Engineering 完整学习指南 - 知乎](https://zhuanlan.zhihu.com/p/1993811969258587128)

---

## 七、课后测试

**1.** System Prompt的四层架构是哪四层？请按从上到下排列。

**2.** Few-Shot示例数量与效果的关系是什么？为什么超过8个示例边际收益急剧下降？

**3.** 以下哪种结构化输出技术可靠性最高？
A. Prompt约束  B. JSON Mode  C. Function Calling  D. Constrained Decoding

**4.** Recency Bias是什么意思？在Few-Shot中如何利用这个特性？

**5.** 业务思考题：如果LangChat的Skill Compiler生成的Blueprint有5%的概率格式错误，在1000次/天的调用量下，每天会有多少次失败？你会怎么解决？

---

## 八、知识串联

今日知识在整体架构中的位置：

Prompt工程是企业级AI平台的**基石能力**。没有可靠的Prompt工程：
- Skill Compiler无法稳定生成Blueprint
- Orchestrator无法准确路由请求
- ChatBI无法生成正确SQL
- 所有上层能力都会"地基不稳"

明日预告：**Prompt安全与护栏**——如何防御Prompt Injection攻击！"""

body = json.dumps({
    "content_format": 1,
    "content": content
}, ensure_ascii=False)

print(f"Content length: {len(content)} bytes")
print(f"JSON body length: {len(body)} bytes")

# 创建笔记
result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://ima.qq.com/openapi/note/v1/import_doc",
    "-H", f"ima-openapi-clientid: {IMA_CLIENT_ID}",
    "-H", f"ima-openapi-apikey: {IMA_API_KEY}",
    "-H", "Content-Type: application/json",
    "-d", body
], capture_output=True, text=True)

print(f"Response: {result.stdout}")
resp = json.loads(result.stdout)
if resp.get("code") == 0:
    doc_id = resp["data"]["doc_id"]
    print(f"SUCCESS: doc_id={doc_id}")
else:
    print(f"FAILED: {resp}")
    sys.exit(1)
