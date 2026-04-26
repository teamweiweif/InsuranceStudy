# Churn / Unwinding 论文战略 Memo

Last updated: `2026-04-26`

## 这份 memo 是干什么的

这份文档不是技术日志，也不是代码说明。

它回答的是更实际的问题：

- 这条 `SIPP + CMS Medicaid unwinding` 线，现在到底走到哪一步了
- 目前结果意味着什么，不意味着什么
- 如果从“能不能形成一篇 paper”出发，应该怎么定位
- 这条线适不适合承载你想要的 `data-driven / ML / DML` 护城河

这份 memo 要和下面几份一起读：

- [churn_unwinding_round2_execution_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_execution_handoff.md)
- [churn_unwinding_round2_diagnostics_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_diagnostics_memo.md)
- [churn_unwinding_administrative_burden_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_administrative_burden_memo.md)

## 先用最直白的话讲：我这轮到底做了什么

我没有直接把这条线推进成 `DID`、`DDD`、`DML` 或者 `causal forest`。

原因很简单：

- 如果现在时间对齐、机制归因、风险排序都还没站稳
- 那么越早上复杂方法，越容易把不稳的东西包装得很像结果

所以这一轮我先做的是“体检”，不是“冲投稿结果”。

具体做了四件事：

1. 复现你之前第一轮 diagnostics，确认旧结果是可重复的  
2. 给 `SIPP person-month` 栈补了一层能做异质性和风险排序的 subgroup features  
3. 把不同 exposure family 和不同 timing 对齐方式系统跑了一遍  
4. 只有在 gate 通过以后，才做了一个很克制的 `risk prediction pilot`

另外还做了两个轻量外部检查：

- `HPS` 做 state-week 粗交叉验证
- `NHIS` 做公开数据可行性审计

## 目前最关键的发现，用通俗话解释

### 1. 这条线没有死，而且比之前更像一个“可以继续做”的项目

好消息是：

- 你现在不是只有一个粗糙 idea
- 这条线已经有了可重复的数据栈、诊断框架和初步风险信号

换句话说，它已经从“方向”变成了“研究原型”。

### 2. 但它还没有到“可以放心讲因果故事”的程度

这点非常重要。

目前最该避免的是：

- 因为手上已经有一堆表和模型，就误以为识别已经成立

现在的状态更像是：

- 可以说“这个设计开始有结构了”
- 不能说“这个设计已经够支撑发表级因果主张”

### 3. 你原本最想讲的机制，还没有被数据自动托起来

你原来更想讲的是：

- `procedural friction`
- 也就是很多人掉保，不一定是因为真的不再符合资格
- 而是因为续保材料、表格、电话、网站、时限、caseworker backlog 这些行政流程太难穿过去

这个故事从经验和政策上都很合理。

但这轮结果告诉我们：

- 它还不是当前数据里最自然、最稳定的领先信号

也就是说：

- 这个机制没有被否掉
- 但也不能现在就把它写成“已经被我们证明的主机制”

所以我把理论框架改成了更稳的总框架：

- `administrative renewal burden`

这个框架更大，能把下面几种东西都包进来：

- 程序性终止
- 续保工作量
- backlog / pending pressure
- ex parte 自动续保不足
- 必须人工交表的负担

### 4. 当前最“可继续”的 exposure，不是最猛的那个，而是相对最稳的那个

这点也很重要。

raw signal 最强的候选，往往是 `pending/backlog`，但它的问题是：

- 它很多时候最好看的结果来自 `lead1`

这很危险，因为它意味着：

- 你现在看到的关系，可能更多是在反映 timing 错位
- 而不是 treatment 和 outcome 的真正时间顺序

所以按当前 gate 规则，最后被选中的不是 raw strongest，而是：

- `manual_renewal_burden / renewal_form_rate / lag1`

这是什么意思？

- 不是说它一定最真实
- 而是说在“不要靠 lead 才有信号”这个前提下，它是当前最能继续往下做的候选

### 5. pre-period falsification 目前不明显致命

通俗说就是：

- 后来在 `2023` 看起来 exposure 更高的州
- 并不是在 `2021-2022` 就已经稳定地更差

这不能证明因果成立。

但至少说明：

- “这些州只是一直都比较糟，所以你看到的不是 unwinding”  
这个最简单反驳，目前没有被强烈支持。

### 6. 真正比州 tertile 更稳的，不是州，而是部分人群脆弱性分组

之前粗州排序的问题依旧存在：

- pre-period 的“高风险州”
- 到了 unwinding 年
- 并没有稳定保持高风险

但比这个好一点的是：

- `poverty band`
- `SNAP status`

这说明一件很关键的事：

- 如果以后要讲风险排序或优先干预
- 更应该从“谁更脆弱”出发
- 而不是从“哪个州本来更差”出发

### 7. 风险预测是有内容的，但还只是风险预测

这一轮我只做了一个非常克制的 pilot：

- 用 `2021-2022` 训练
- 用 `2023` 测试
- 预测下个月从 Medicaid 掉出，或者掉到 uninsured

结果是：

- 简单的 subgroup logistic，明显好于 naive state baseline

这说明：

- 当前这套 feature 确实能比“按州粗分高低风险”更好地区分风险

但这不等于：

- 已经能做 welfare-based targeting
- 已经能做 causal ML paper

它只说明：

- `risk ranking` 这件事开始有了基础

## 从论文角度，我现在的评价是什么

### 判断 1：它已经像 paper 的“中段”，但还不像 paper 的“最后成品”

什么意思？

你现在已经有：

- 题目背景
- 数据来源
- 一套可以重复的分析栈
- 初步机制框架
- 可继续发展的风险排序结果

但你还没有：

- 很硬的识别闭环
- 一个被数据自然抬起来的主机制
- 足够强的外部验证

所以这条线现在不是“不能发”，而是：

- 还没进入最终叙事定稿阶段

### 判断 2：它现在更像一篇“data-driven health policy / vulnerability / operational prioritization”文章

而不是一篇传统意义上的“硬识别 health econ causal paper”。

更准确地说，如果你现在就基于它写 paper，最稳的定位可能是：

- Medicaid unwinding 下的行政续保负担
- 哪些人更容易掉保
- 哪类州月度行政负担指标更贴近风险上升
- 简单、透明的风险排序能否优于粗州基线

这类 paper 的卖点会是：

- 公共数据可复制
- 指标构建清楚
- 强调 operational relevance
- ML 用于风险识别和优先级排序，而不是硬装成因果发现器

### 判断 3：如果你想要更强的“方法护城河”，现在还不能直接靠 DML 硬顶

这是关键判断。

你最重要的护城河是：

- `data-driven innovation`
- `DML / causal ML`

但前提是：

- treatment 定义要更稳
- timing 要更稳
- mechanism 至少不能处在“理论比数据更强”的状态

现在如果直接上 DML，会有两个风险：

1. 方法很先进，但识别基础没同步跟上  
2. 审稿人会觉得 ML 只是把不稳的 observational design 包装复杂化

所以当前最合理的态度不是反对 ML，而是：

- 先承认这轮最适合的是 `risk-oriented ML`
- 暂时不要把它写成 `causal ML contribution`

### 判断 4：这条线还值得继续，但下一步必须更克制、更战略化

我的评价不是“放弃它”。

相反，我觉得它值得继续，原因有三条：

1. 政策背景是真实且当前的  
2. 公共数据确实能支撑出一个独立研究栈  
3. 你已经开始有比粗 baseline 更好的风险信号

但继续的方法要变：

- 少一点“我要立刻证明一个大因果故事”
- 多一点“我先把最稳的可发表贡献钉住”

## 如果现在就问：这条线最适合发成什么样

我会给三个层级的答案。

### 层级 A：当前最稳的版本

题目定位：

- `administrative renewal burden and coverage-loss risk during Medicaid unwinding`

核心贡献：

- 用公共数据构造州-月份行政续保负担指标
- 证明某些 burden proxy 比别的 proxy 更值得继续追踪
- 证明人群脆弱性分组比粗州排序更能抓住风险
- 提供一个透明、克制的 risk prioritization 原型

优点：

- 现在最接近你已有结果
- 不需要过度宣称因果
- 最容易把目前的证据链讲顺

缺点：

- 期刊档次可能受限
- 需要把“公共政策 operational relevance”写得很清楚

### 层级 B：你可能想追求、但目前还没到的版本

题目定位：

- `causal effect of administrative burden on avoidable churn during unwinding`

这要求你后面必须再补：

- 更强 timing discipline
- 更像准实验的识别层
- 更可信的 external validation

这个版本不是不能去，但现在还没到。

### 层级 C：如果最终发现 timing/机制一直站不稳

那这条线最好的处理方式是：

- 把它保留成一个“风险识别与设计开发”分支
- 然后把你真正的 causal ML ambition 放到别的题上

比如：

- churn 之外的更强 policy shock
- 或者别的 insurance transition 场景

## 如果我是你，我现在会怎么写对这条线的内部定位

我会这样写：

- 这条线目前是项目里最成熟的公共数据新主线
- 它已经从 exploratory idea 进入 structured empirical prototype
- 当前最强可守的贡献不是因果效应识别，而是行政续保负担框架下的风险结构刻画与优先排序原型
- 是否能升级成更强的 causal / DML paper，取决于后续 timing 和 validation 能否显著增强

这段话的好处是：

- 不夸张
- 但也不贬低现在已有成果
- 对下一步怎么扩展非常清楚

## 现在最不该做的三件事

1. 现在就把 `procedural friction` 写成已经被证明的主机制  
2. 现在就把 `GO_RISK_ONLY` 误写成“可以直接上 causal targeting”  
3. 因为手头已经有 ML 结果，就跳过 timing 和 validation 的弱点

## 现在最该做的三件事

1. 把这条线的“当前可守贡献”写清楚  
2. 把 risk ranking 的结果讲成一个克制但明确的贡献  
3. 再决定是否要为它继续投入更强的识别扩展

## 一句话总结

这条 `Medicaid unwinding` 线现在最像的是：

- 一条已经有数据、结构和初步信号的 `data-driven policy paper` 主线

但它目前还不像：

- 一条已经准备好承载你全部 `causal ML / DML` 野心的成熟因果主线

所以我对它的战略评价是：

- 值得继续
- 值得写成 paper candidate
- 但当前最稳的定位是 `risk / burden / vulnerability / prioritization`
- 不是马上硬推成 `causal ML paper`

## Addendum: Avoidable-Churn Update

在这份 memo 写完之后，又补了一轮 `avoidable churn` 实验，见：

- [churn_unwinding_avoidable_churn_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_avoidable_churn_memo.md)

这个增量结果改变了一个重要判断：

- 之前更像是“这条线值得继续，但很多东西都还不够理想”
- 现在更像是“原来的问法不够对；换成 `persistent uninsured h2 + backlog_automation_index` 以后，这条线的 empirical core 明显更清楚了”

所以最新的战略位置应理解为：

- 仍然没有直接升级到 `DML / causal ML`
- 但已经从纯 `risk-first holding pattern`，往“有更明确 paper core 的 data-driven policy line”推进了一步

## Addendum: Round-4 Step 2 Subgroup-Stability Update

Round-4 Step 2 strengthens, but does not fundamentally change, the paper positioning.

New evidence:

- the upgraded harmful outcome layer was tested against subgroup ordering from pooled `2021-2022` into `2023`
- in the primary `core_aug_oct_2023` window, `foreign_born_group`, `household_child_group`, and `snap_group` were stable on both:
  - `persistent_uninsured_h2`
  - `broad_exit_persistent_uninsured_h2`
- relative to the older `medicaid_exit_to_uninsured_next` subgroup screen:
  - old stable family count: `2`
  - new stable family count: `3`
  - old mean Spearman: `-0.0286`
  - new mean Spearman: `0.2571`
- the explicit verdict is `SUBGROUP_STABILITY_ROUND2_SUPPORTS_RISK_RANKING`

Strategic implication:

- this makes the `risk / burden / vulnerability / prioritization` positioning more defensible
- it supports moving to a bounded `Risk-Ranking Round 2`
- it still does not support writing the paper as causal ML, DML, causal forest, DID, event-study, or causal targeting

## Addendum: Round-4 Step 3 Risk-Ranking Update

Round-4 Step 3 gives a mixed but useful risk-ranking result.

New evidence:

- the risk round trained on `2021-2022` and tested on `2023`
- the primary outcome was `persistent_uninsured_h2`
- the benchmark outcome was `medicaid_exit_to_uninsured_next`
- retained subgroup-family predictors were used without opening causal ML or targeting work

Primary outcome:

- AUC-leading model: `weighted_logistic`
  - AUC `0.5570`
  - PR AUC `0.0049`
  - top-decile capture `0.1057`
- top-decile-capture-leading model: `compact_boosting`
  - AUC `0.5389`
  - PR AUC `0.0046`
  - top-decile capture `0.1966`

Old-pilot comparison:

- on the benchmark outcome, weighted logistic beat the naive state baseline
- compared with the old risk pilot, the result is mixed:
  - AUC delta `-0.0850`
  - top-decile capture delta `0.0145`

Strategic implication:

- this supports a bounded `risk ranking / prioritization prototype` only with caveats
- it does not support probability-calibrated targeting language
- it does not support causal ML, DML, DID, event-study, causal forest, or causal targeting language
- the next useful document should be a paper-path decision memo, not another automatic escalation

## Addendum: Round-4 Step 4 Path Decision

Round-4 Step 4 closes the current diagnostic phase.

Final verdict:

- `PATH_A_NARROW_RISK_BURDEN_VULNERABILITY_PAPER_WITH_CAVEATS`

Selected path:

- `Path A: paper-first risk / burden / vulnerability line`

The selected path is narrowed to:

- public-data health policy
- administrative renewal burden
- avoidable harmful churn
- persistent uninsurance after Medicaid exit
- subgroup vulnerability
- bounded risk-ranking / prioritization prototype

The selected path is not:

- causal effect paper
- causal ML paper
- DML paper
- causal forest paper
- DID or event-study paper
- welfare targeting paper
- deployable outreach targeting model

Strategic implication:

- the current branch is strong enough to become the main paper candidate in a constrained form
- it should now move to a paper outline and results-to-table map
- it should not escalate to causal estimation or switch topics
