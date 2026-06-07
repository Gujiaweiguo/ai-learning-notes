# 🧠🤖 AI 学习笔记

Jason 的大模型 + 脑科学学习之旅，每天自动生成 Jupyter Notebook。

## 每周节奏

| 日期 | 类型 | 内容 |
|------|------|------|
| 周一-周五 | 📚 新知识 + 🔄复习 | 每天学新内容，复习前一天 |
| 周六 | ⚡ 代码实战 | Trae 填空式动手练习 |
| 周日 | 🔄 复习日 | 本周全面回顾 + 查漏补缺 |

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
- W2 微调：`torch` `unsloth`
- W3 RAG：`sentence-transformers` `chromadb`
- W5 Agent：`openai` 等

## 目录结构

```
W1/   - Transformer 深入理解
W2/   - 大模型训练全景
W3/   - RAG 与知识增强
W4/   - 推理与思维链
W5/   - Agent 与工具使用
W6/   - 多模态、安全与前沿
W7/   - 神经元基础
W8/   - 大脑地图
W9/   - 感知与记忆
W10/  - 注意力与决策
W11/  - 情绪与学习
W12/  - 脑科学与AI交汇
```

## 学习路线

- **W1-W6**：🤖 大模型（业务优先）
- **W7-W12**：🧠 脑科学（个人爱好，带 AI 视角）

> 起始日期：2026-06-04
