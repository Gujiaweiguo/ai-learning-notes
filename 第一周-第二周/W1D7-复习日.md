# W1 Day 7 — 复习日（Transformer深入理解）

> 🔄 复习 Day 1-5 核心概念 + 补漏练习

## 复习要点

| Day | 主题 | 核心内容 |
|-----|------|----------|
| Day 1 | 自注意力机制 | Q/K/V 矩阵，Attention(Q,K,V) = softmax(QK^T/√d_k)V |
| Day 2 | Multi-Head Attention + 位置编码 | 多头并行捕捉不同语义关系；正弦/学习式位置编码 |
| Day 3 | FFN + LayerNorm + 残差连接 | Transformer的"肌肉"和"骨骼" |
| Day 4 | Tokenizer + 词嵌入 | BPE/SentencePiece分词，Embedding将token映射为向量 |
| Day 5 | 整体架构对比 | GPT（解码器only）vs BERT（编码器only）的设计取舍 |

## 知识脉络

文本 → Tokenizer分词 → Embedding嵌入 + 位置编码 → 多头自注意力（并行捕捉关系）→ FFN（非线性变换）→ 残差 + LayerNorm（稳定训练）→ 堆叠N层 → GPT自回归生成 / BERT双向理解

## 核心公式

- Attention(Q,K,V) = softmax(QK^T / √d_k) · V
- Multi-Head = Concat(head_1, ..., head_h) · W^O

## 查漏补缺测试

1. 自注意力中为什么要除以 √d_k？
2. 位置编码为什么要加到Embedding上？
3. BERT和GPT最核心的区别是什么？
4. 残差连接解决了什么问题？
5. BPE算法的核心思路是什么？

## 知识卡片

- **自注意力** = 每个词主动"看"其他所有词，决定关注谁
- **多头** = 多个"视角"并行观察（语法、语义、指代...）
- **残差** = 信息高速公路，梯度不会在中途消失
- **BPE** = 用高频词组替代低频字符，平衡词表大小

## 下周预告：W2 大模型训练全景

- Day 1: 预训练（数据、规模与涌现能力）
- Day 2: SFT 监督微调
- Day 3: RLHF 人类反馈强化学习
- Day 4: DPO 与其他对齐方法
- Day 5: 训练全流程串联
- 周六实战：用unsloth做QLoRA微调demo
