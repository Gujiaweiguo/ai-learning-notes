# 🧠🤖 AI 学习笔记

Jason 的大模型 + 脑科学学习之旅，每天自动生成 Jupyter Notebook。

## 每周节奏

| 日期 | 类型 | 内容 |
|------|------|------|
| 周一-周五 | 📚 新知识 + 🔄复习 | 每天学新内容，复习前一天 |
| 周六 | ⚡ 代码实战 | opencode 填空式动手练习 |
| 周日 | 🔄 复习日 | 本周全面回顾 + 查漏补缺 |

## 学习进度（按日历周编号）

- **第一周**（6/1-6/7，周一至周日）：Transformer 深入理解
  - Day1（6/4 周四）= 自注意力机制 ✅
  - Day2（6/5 周五）= Multi-Head Attention ✅
- **第二周**（6/8-6/14，周一至周日）：Transformer 深入理解（续）
  - Day1（6/8 周一）= FFN、LayerNorm 与残差连接
  - Day2（6/9 周二）= Tokenizer 与词嵌入
  - Day3（6/10 周三）= 整体架构回顾（GPT vs BERT）
  - Day4（6/11 周四）= ⚡代码实战（NumPy实现Self-Attention）
  - Day5（6/12 周五）= 🔄复习日
- **第三周**（6/15-6/21，周一至周日）：大模型训练全景
  - Day1 = 预训练：数据、规模与涌现能力
  - Day2 = SFT：监督微调
  - Day3 = RLHF：人类反馈强化学习
  - Day4 = DPO 与对齐方法对比
  - Day5 = 训练全流程串联 + 超参数调优

## 环境配置

### 1. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆项目 & 初始化环境

```bash
git clone git@github.com:Gujiaweiguo/ai-learning-notes.git
cd ai-learning-notes
uv init --python 3.11
uv add numpy matplotlib jupyter
```

> `uv init --python 3.11` 会自动下载对应版本的 Python，无需手动安装。

### 3. VS Code 打开项目

```bash
uv run code .
```

或者手动操作：
1. VS Code 打开项目目录
2. **Ctrl+Shift+P** → 输入 `Python: Select Interpreter` → 选择 `.venv` 里的 Python
3. 安装 VS Code 扩展：**Jupyter**（Microsoft 官方）
4. 打开 `.ipynb` 文件即可运行

> ⚠️ 关键：VS Code 必须选对 Python 解释器（uv 创建的 `.venv` 里的那个），否则 kernel 找不到依赖。

### 4. 依赖说明

当前核心依赖：
- `numpy` — 数值计算（Self-Attention 等代码实战）
- `matplotlib` — 可视化（位置编码热力图等）
- `jupyter` — 运行 Notebook

后续按需追加（不用提前装）：
- 第三周微调：`torch` `unsloth`
- 第四周 RAG：`sentence-transformers` `chromadb`
- 第六周 Agent：`openai` 等

## 目录结构

```
第一周-第二周/   - Transformer 深入理解
第三周/   - 大模型训练全景
第四周/   - RAG 与知识增强
第五周/   - 推理与思维链
第六周/   - Agent 与工具使用
第七周/   - 多模态、安全与前沿
第八周/   - 神经元基础
第九周/   - 大脑地图
第十周/   - 感知与记忆
第十一周/  - 注意力与决策
第十二周/  - 情绪与学习
第十三周/  - 脑科学与AI交汇
```

## 学习路线

- **第一周-第七周**：🤖 大模型（业务优先）
- **第八周-第十三周**：🧠 脑科学（个人爱好，带 AI 视角）

> 起始日期：2026-06-04（第一周 周四），每周一至周日为一周期
