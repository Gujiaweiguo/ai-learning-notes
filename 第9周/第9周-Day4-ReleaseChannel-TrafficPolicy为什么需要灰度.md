# 🧱 LangChat 心智模型 | Week9-Day4

**📌 当前主题：ReleaseChannel / TrafficPolicy — 为什么需要灰度？不能一次全量？**

**日期**：2026-07-30（周四）
**链路位置**：Supply Chain 末端 → Runtime 始端（制品晋升与流量路由的交界）

---

## ━━━ 1. 今日核心问题 ━━━

### 为什么需要灰度？不能一次全量？

Jason 做了 26 年 ERP。你一定遇到过这种场景：一个财务模块升级，周一早上全量推上线，结果某个边缘税率计算逻辑在新版本里出错了，全公司当天没法做账。

你当时一定想过：**"如果能先让 5% 的人用新版本，确认没问题再全推就好了。"**

这就是灰度发布（Canary Release）的本质——**不是技术炫技，而是风险控制的工程纪律。**

LangChat 的回答更进一层：灰度不是部署工具的附属功能，而是**架构层面两个独立对象**——`ReleaseChannel`（晋升指针）和 `TrafficPolicy`（流量策略）——各司其职，确保灰度可控、可审计、可回滚。

---

## ━━━ 2. 人话解释 ━━━

用 ERP 经验讲：

**传统 ERP 的"发布"**：开发 → 测试 → 上线。上线就是全量替换。出了问题？回滚到昨天的备份。这个过程里，"哪个版本在生产"、"谁批的"、"流量怎么切"全混在一个动作里。

**LangChat 的"发布"拆成三个独立动作**：

| 动作 | 对象 | 做什么 | ERP 类比 |
|---|---|---|---|
| 晋升（Promotion）| ReleaseChannel | 把 scope 内的指针指向新版本 digest | "标记 v2.1 为当前正式版本" |
| 物化（Materialization）| DeploymentRevision | 把 SkillRelease digest + 环境 = 完整运行时闭包 | "在生产环境安装 v2.1" |
| 切流（Traffic Routing）| TrafficPolicy | 决定多少流量到新版本、多少到旧版本 | "先让 5% 的用户用 v2.1" |

三个动作独立。你可以晋升了但还没部署（ReleaseChannel 指向新 digest，但 TrafficPolicy 还指向旧 Revision）。你也可以部署了但只给 1% 流量（DeploymentRevision 已物化，TrafficPolicy 做 99/1 分流）。

**这就是灰度存在的理由：把"哪个版本是正式版"和"生产实际在跑哪个版本"解耦。**

---

## ━━━ 3. LangChat 架构位置 ━━━

在 ADR-007 的三段式架构链中：

```
External Clients → Capability Runtime → Enterprise Systems
                        ↑
                   段 2 内部：
                   
  Supply Chain                    Runtime
  ──────────────                  ──────────────
  BlueprintVersion                Deployment
       ↓                               ↓
  SkillRelease (制品)          DeploymentRevision (闭包)
       ↓                               ↑
  ReleaseChannel ──→ (部署操作) ──→ TrafficPolicy
  (晋升指针)         一次性解析       (流量策略)
       ↓
  PromotionEvent
  (审计事件)
```

关键位置：
- **ReleaseChannel** 属 Supply Chain 层（严格归属，Domain Model §3 硬约束）
- **TrafficPolicy** 属 Runtime 层
- 两者之间是**部署操作**——它读取 Channel 指针，解析为 digest，物化 DeploymentRevision，然后 TrafficPolicy 决定流量怎么走

---

## ━━━ 4. ADR 依据 ━━━

### Domain Model SC-14 ReleaseChannel（§7.10）

核心不变量：
1. **单点性**：`(scope, channel_name)` 在任一时刻只指向一个精确 SkillRelease digest（或空）
2. **晋升受审计**：每次移动必产出 `PromotionEvent`
3. **不影响服务流量**：Channel 移动不直接改变 TrafficPolicy 或 DeploymentRevision 的活跃性

显式禁止：
- ❌ 不在运行时请求路径中
- ❌ 不指向 DeploymentRevision
- ❌ 不路由流量
- ❌ Channel 移动不改变已 Serving 的 Deployment 或 TrafficPolicy

### Domain Model RT-03 TrafficPolicy（§8.2）

核心不变量：
1. **精确引用**：所有路由目标必须是具体 DeploymentRevision ID + digest
2. **确定性 cohort 路由**：相同稳定分流键永远划入同一 cohort
3. **版本演进**：变更必生成新版本，不原地修改

显式禁止：
- ❌ 不读 Catalog
- ❌ 不读 ReleaseChannel 作为路由依据
- ❌ 不路由到 "latest"
- ❌ 不路由到 mutable name

### Artifact & Execution Spec §10 — ReleaseChannel 契约

> Promotion MUST NOT 自动修改 TrafficPolicy 或 Deployment.
> Promotion MUST NOT 自动物化 DeploymentRevision.

### Artifact & Execution Spec §12 — TrafficPolicy 契约

> Cohort 划分 MUST 确定性：相同稳定分流键（如 tenant、workspace、actor、session）永远划入同一 cohort.

### 跨对象不变量（Domain Model §10.4）

- **§10.4-4 Channel 与流量解耦**：ReleaseChannel 移动不改变 TrafficPolicy 或已 Serving 的 DeploymentRevision
- **§10.4-11 ReleaseChannel 归属固定**：严格属 Supply Chain，不得在运行时请求路径中引用

---

## ━━━ 5. 代码验证 ━━━

### ReleaseChannel 实现

```python
# langchat/supply_chain/release_channel.py
@dataclass(frozen=True)
class ChannelScope:
    # (tenant, workspace, environment, channel_name) = 唯一定位
    
class ReleaseChannel:
    def promote(self, scope: ChannelScope, digest: str, operator, promoted_at):
        # 单点映射：scope 内只能指向一个 digest
        # 产出 PromotionEvent 审计记录
        
    def get(self, scope: ChannelScope) -> str:
        # 返回当前 digest 或空字符串
        
    def unpin(self, scope, operator, unpinned_at):
        # 清除指针，也产出审计事件
```

### 单元测试验证（test_release_channel_single_point.py）

```python
def test_repin_replaces_digest():
    """Single-point: promoting again replaces the previous digest."""
    ch.promote(_scope(), "sha256:" + "a" * 64, ...)
    ch.promote(_scope(), "sha256:" + "b" * 64, ...)
    assert ch.get(_scope()) == "sha256:" + "b" * 64  # 只保留最新的

def test_different_scopes_are_independent():
    """Two scopes with the same channel_name are independent."""
    ch.promote(_scope("prod"), digest_a, ...)
    ch.promote(_scope("shadow"), digest_b, ...)
    assert ch.get(_scope("prod")) == digest_a    # 互不干扰
    assert ch.get(_scope("shadow")) == digest_b
```

### TrafficPolicy 实现

```python
# langchat/runtime/traffic_policy.py
@dataclass(frozen=True)
class TrafficPolicy:
    policy_id: str
    revision_id: str          # 必须是具体 revision ID
    revision_digest: str      # 必须是精确 digest
    percentage: int           # 0-100 流量百分比
```

### 单元测试验证（test_traffic_policy_only_points_to_revisions.py）

```python
def test_latest_rejected():
    with pytest.raises(ValueError, match="forbidden_reference"):
        TrafficPolicy("tp-1", "latest", "sha256:" + "a" * 64, 100)
        # "latest" 被拒绝！

def test_channel_name_rejected():
    with pytest.raises(ValueError, match="forbidden_reference"):
        TrafficPolicy("tp-1", "production", "sha256:" + "a" * 64, 100)
        # Channel 名被拒绝！

def test_concrete_revision_accepted():
    tp = TrafficPolicy("tp-1", "rev-42", "sha256:" + "a" * 64, 100)
    assert tp.revision_id == "rev-42"  # 只接受具体 revision
```

### 关键发现

代码忠实实现了 ADR 设计：
1. ReleaseChannel 是纯控制面指针，不碰流量
2. TrafficPolicy 在构造时就拒绝一切非精确引用（latest、channel 名、非法 digest）
3. 部署管道（pipeline.py）严格遵循 Channel→Digest→Revision→Register 四步分离

---

## ━━━ 6. 商业地产映射 ━━━

LangChat → MI CRE（商业地产运营）场景：

| LangChat 概念 | MI CRE 场景对应 | 解释 |
|---|---|---|
| ReleaseChannel | "合同审核机器人版本标记" | 标记"当前正式版合同审核机器人是 v2.1"，但实际生产可能还在跑 v2.0 |
| PromotionEvent | "版本变更审批单" | 每次移动 Channel 都留痕：谁批的、什么时候、从哪个版本到哪个版本 |
| DeploymentRevision | "实际部署的机器人实例" | v2.1 机器人 + MI ERP 接口 + 知识库快照 = 一个完整的运行实例 |
| TrafficPolicy | "租户分流规则" | 先让 3 个租户用新版合同审核，其他 47 个租户继续用旧版 |
| Cohort Hash | "租户级粘性路由" | 租户 A 今天用新版，明天还是用新版，不会随机跳来跳去 |

**场景举例**：MI 购物中心有 50 个租户。新版合同审核 SkillRelease 增加了自动条款比对能力。

- **全量上线（错误做法）**：50 个租户同时切换 → 如果条款比对逻辑在某些边缘 case 出错 → 50 个租户的合同审核全部受影响
- **灰度上线（正确做法）**：先让 3 个租户用（TrafficPolicy 6%），观察一周 → 没问题 → 扩大到 10 个租户（20%）→ 再扩大到全部

**Channel 在这里的作用**：运营总监把"正式版"指针指向 v2.1（ReleaseChannel promotion），但技术总监决定让只有 3 个租户实际使用（TrafficPolicy cohort）。版本标记与实际流量完全解耦。

---

## ━━━ 7. 与传统方案比较 ━━━

### 方案对比：灰度发布的三种做法

| 维度 | 传统 ERP（直接替换）| DevOps 工具（蓝绿部署）| LangChat（Channel + TrafficPolicy）|
|---|---|---|---|
| 版本标记与流量 | 混在一起 | 部分分离 | 完全分离（两个独立对象）|
| 灰度粒度 | 无 | 按服务器/实例 | 按租户/用户/session（cohort hash）|
| 回滚方式 | 恢复备份 | 切回旧实例 | 新建 TrafficPolicy 版本（前向操作）|
| 审计追踪 | 日志 | 部署记录 | PromotionEvent + TrafficPolicy 版本链 |
| 版本精确性 | "v2.1" | image tag | content-addressed digest |
| 运行时安全 | 依赖人工纪律 | 依赖 CI/CD 流水线 | 架构层强制（拒绝 latest、拒绝 mutable name）|

### 为什么不把 Channel 和 TrafficPolicy 合并？

| 合并的问题 | 后果 |
|---|---|
| "标记正式版"= 切流量 | 你不能只标记版本而不影响生产 |
| 流量策略变更需要审批 | 每次版本标记都要走审批流程 |
| 无法做 shadow deployment | Channel 指向新版但没人用——这个状态没有意义 |
| 职责模糊 | 谁负责"标记"？谁负责"切流"？出错时谁背锅？ |

**分离后**：ReleaseChannel 是 Supply Chain 的事（版本管理团队）。TrafficPolicy 是 Runtime 的事（运维/SRE 团队）。各自独立审计，各自独立演进。

---

## ━━━ 8. 架构师思考题 ━━━

### CTO 级问题

**场景**：MI 集团有 3 个业态（购物中心、写字楼、酒店），每个业态有独立的租户群体。合同审核机器人发布了 v3.0，新增了按业态差异化的条款审核逻辑。

**问题**：
1. 你会设计几个 ReleaseChannel？Channel scope 怎么定义？
2. 三个业态的灰度策略应该相同还是不同？
3. 如果写字楼的 v3.0 出了问题需要回滚，购物中心和酒店受不受影响？
4. 回滚时，ReleaseChannel 指针要动吗？TrafficPolicy 怎么变？

**参考思路**（不是标准答案，是思考方向）：
- Channel scope 可能是 `(tenant_group, industry, environment, channel_name)`
- 不同业态的风险承受力不同 → 灰度比例可以不同
- 如果 Channel 按业态分 → 回滚一个业态不影响其他
- 回滚 = 新建 TrafficPolicy 版本指向旧 Revision → Channel 不一定要动

---

## ━━━ 9. 我的理解变化 ━━━

**以前以为**：灰度发布就是部署工具的一个功能——在 CI/CD 流水线里配个百分比就行了。

**现在知道**：LangChat 把灰度拆成了**两个独立架构对象**：
- ReleaseChannel 是"版本标记"（Supply Chain 的事）
- TrafficPolicy 是"流量切分"（Runtime 的事）

两者在架构上完全解耦，在跨对象不变量中被显式约束（§10.4-4 和 §10.4-11）。

**更深一层的认知**：灰度的核心不是"能不能按比例切流量"，而是**"版本标记与实际运行状态的解耦程度"**。传统方案的问题是：标记了正式版 = 全量上线，没有中间态。LangChat 的设计让你可以标记了正式版但只给 1% 流量——这个"标记但不全量"的中间态，才是灰度发布的工程价值。

---

## ━━━ 10. 明日连接 + Semantic Layer ━━━

### 明日主题

**Day 5（周五）：DigitalEmployeeDefinition — 为什么数字员工不拥有 Runtime？**

这是 Week 9 最后一个对象。前面四天看了 Release/Deployment 的制品和流量侧，明天看"产品语义锚点"——数字员工的定义本身。

### Semantic Layer 位置

```
Ontology（存在什么）
  └─ Domain Model（对象边界）
       ├─ ReleaseChannel = "哪个版本是正式版"（Supply Chain 指针）
       ├─ TrafficPolicy = "生产实际跑哪个版本"（Runtime 流量策略）
       └─ DigitalEmployeeDefinition = "这个 AI 应用是什么"（Business Domain 语义锚）

Capability → SkillRelease → DeploymentRevision → TrafficPolicy → Execution
  ↑                                                           ↑
  Supply Chain                                    Runtime（受 TrafficPolicy 控制）
```

今天的知识在链上的位置：**Supply Chain 末端（ReleaseChannel）与 Runtime 始端（TrafficPolicy）的交界**。理解这个交界，就理解了"从制品到运行"的完整路径。

---

*📝 Week 9 Day 4 · 灰度不是功能，是架构纪律*
