# Churn / Unwinding Avoidable-Churn Memo

Last updated: `2026-04-11`

## 为什么要做这一轮

前一轮最大的疑问是：

- 原来的 outcome 太窄
- 原来的机制 proxy 也不够稳

具体来说，原先主盯的是：

- `medicaid_exit_to_uninsured_next`
- `renewal_form_rate / lag1`

这条线并不是完全没结果，但看起来总是“有一点点信号，但不够像主结果”。

所以这轮测试的核心思路变成了两步：

1. 把 outcome 改成更贴近 `avoidable churn` 的短期状态路径  
2. 不再只赌单个 raw proxy，而是测试更接近行政负担本质的 composite burden index

## 这轮实际做了什么

### 实验 1：重建短期 churn outcome layer

产物：

- [sipp_avoidable_churn_outcome_layer_2021_2023.parquet](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/sipp_avoidable_churn_outcome_layer_2021_2023.parquet)
- [sipp_avoidable_churn_outcome_audit.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.md)
- [build_sipp_avoidable_churn_outcome_layer.py](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/design_diagnostics/build_sipp_avoidable_churn_outcome_layer.py)

关键发现：

- `t+2` 支持是够的
- 但“掉保后 1-2 个月又回到 pure Medicaid”几乎没有样本量，不能当主 outcome
- 最可用的新 harmful outcome 是：
  - `persistent_uninsured_h2`
  - 也就是：本月 pure Medicaid，下一月 uninsured，再下一月仍 uninsured
- 最可用的 contrast outcome 是：
  - `broad_exit_resolved_insured_h2`
  - 也就是：本月 pure Medicaid，下一月离开 Medicaid，但到 `t+2` 又回到了 insured 状态

一句话：

- “literal return to Medicaid” 太稀疏
- “persistent uninsured after exit” 才是当前数据里真正能做的 avoidable-churn proxy

### 实验 2：用新 outcome 重跑 burden family / composite diagnostics

产物：

- [avoidable_churn_burden_diagnostics.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_burden_diagnostics.md)
- [avoidable_churn_burden_ranking.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_burden_ranking.csv)
- [avoidable_churn_burden_falsification_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_burden_falsification_summary.csv)
- [build_avoidable_churn_burden_diagnostics.py](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/design_diagnostics/build_avoidable_churn_burden_diagnostics.py)

这一轮比较了：

- 单指标：
  - `pending_rate`
  - `renewal_form_rate`
  - `procedural_term_share`
  - `ex_parte_renewal_rate`
- composite：
  - `backlog_automation_index`
  - `backlog_form_index`
  - `full_burden_index`

最重要的新结果是：

- 新的稳定 candidate 不再是 `renewal_form_rate / lag1`
- 现在更像样的 candidate 是：
  - `backlog_automation_index / same`

这个 composite 的直觉含义是：

- 州里 pending/backlog 越高
- 同时 ex parte 自动续保越弱
- 那么 administrative burden 越重

而它在结果上表现为：

- 在 `core_aug_oct_2023_h2` 里是正向、稳定的
- 在 `mature_jun_oct_2023_h2` 里仍然保持正向、稳定
- 对 harmful outcomes 是正向
- 对 resolved contrast outcome 是负向

对应分数：

- core score: `0.1242`
- mature score: `0.1105`

这比之前那种“只有某个 raw 指标在某个 timing 上勉强有点信号”要强得多。

### 实验 3：用 HPS 做轻量外部交叉验证

产物：

- [hps_avoidable_churn_crosscheck.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_avoidable_churn_crosscheck.md)
- [hps_avoidable_churn_crosscheck_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_avoidable_churn_crosscheck_summary.csv)
- [build_hps_avoidable_churn_crosscheck.py](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/design_diagnostics/build_hps_avoidable_churn_crosscheck.py)

外部检查对象是新 candidate：

- `backlog_automation_index / same`

HPS 上的方向现在比上一轮顺很多：

- `current_medicaid_rate`: 负向
- `uninsured_rate`: 正向
- `public_coverage_rate`: 负向

也就是说：

- 高 burden 州，在 HPS 上也更像是 Medicaid 覆盖更低、无保险更高

这仍然不是因果验证，但它至少说明：

- 新 candidate 并不是只在 SIPP 里“自说自话”

## 这一轮改变了什么判断

### 改变 1：项目不再只是“结果不好”

更准确地说，之前的问题更像：

- 问法太窄
- proxy 选得不够对

现在改成：

- `persistent uninsured after exit`
- `backlog + weak ex parte automation`

以后，信号就更像一个 coherent story 了。

### 改变 2：理论主轴也更清楚了

这轮结果更支持的不是：

- 狭义 `procedural friction`

而是：

- `administrative renewal burden`

而且在这个 umbrella 下，当前最像样的实证子通道是：

- `backlog pressure`
- `automation weakness`

所以，经验上更像是在说：

- 不是单纯“表格多”最关键
- 而是“系统积压 + 自动续保弱”，更容易对应持续性的 coverage harm

### 改变 3：这条线的机会变大了

这轮之前，我的判断更偏：

- 值得继续，但只是 `risk-first`

这轮之后，我的判断变成：

- 这条线不再只是“可做风险排序”
- 它开始有一个更清楚的 empirical core

但仍然要强调：

- 这不等于已经升级成发表级 causal design
- 也不等于现在就应该直接上 `DML`

## 当前最合理的战略评价

现在这条线最有希望的 paper 问法，已经不该写成：

- `procedural friction causes immediate uninsured exit`

更好的写法是：

- `administrative renewal burden and avoidable Medicaid churn during unwinding`

通俗说：

- 哪些州月度行政负担环境，更容易对应“持续性掉进无保险”
- 这个负担更像是 backlog 和 automation failure 的组合，而不只是单一程序性终止占比

## 现在最关键的结论

一句话版本：

- 这条线被“救活”了一点，而且是实质性的，不是 cosmetic 的

更严格一点说：

- 还不能说识别已经很强
- 但可以说：
  - 新 outcome 比旧 outcome 更像样
  - 新 composite 比旧 raw candidate 更稳
  - 轻量外部验证也开始顺了

这就是为什么本轮 `avoidable churn burden` 的 verdict 是：

- `PROMISING_H2_UPGRADE`

## 对下一步的含义

这轮之后，最值得继续的不是：

- 回去再死磕 `renewal_form_rate`
- 或者马上上 `DML`

而是：

1. 把 `backlog_automation_index` 当作当前主 candidate 继续压实  
2. 在 `persistent_uninsured_h2` 这个新 outcome 上重做 subgroup / heterogeneity / risk ranking  
3. 再决定它能不能继续升级到更强的 quasi-causal design

## 当前一句话总结

如果前一轮的总结是：

- “这条线还没死，但看起来什么都不够理想”

那么这一轮的总结就是：

- “真正可抓住的机会，可能不是程序性摩擦本身，而是 backlog 与自动续保不足共同构成的 administrative burden，它更能对应持续性的 uninsured churn。”
