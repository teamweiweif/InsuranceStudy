# US Insurance Project: 完整现状与未来方向思考文档

> 本文档为高推理模型准备的完整项目摘要，包含：当前数据与方法现状、已有结果、已知局限、待解决的理论机制问题、以及需要深入思考的未来方向。

---

## 一、项目概述

### 1.1 目标
利用 MEPS (Medical Expenditure Panel Survey) Full-Year Consolidated 公共数据 (1996-2023, 28年) 进行美国保险领域的健康经济学实证研究。结合 **因果推断 (Fuzzy RDD)** 和 **因果机器学习 (GRF + Policy Trees)**，产出一篇可发表于 SCI Q3-Q4 区的论文。

### 1.2 核心识别策略
**Medicare@65 Fuzzy Regression Discontinuity Design**：利用65岁 Medicare 资格断点，以年龄（月）为 running variable，估计 Medicare 覆盖对多种健康经济结局的因果效应，并通过 GRF 估计异质性处理效应 (HTE)，通过 policy trees 进行政策定向分配。

### 1.3 当前分析状态
- **已完成**：Pooled 2002-2017 分析，2026年4月2日产出
- **样本量**：92,804 观测（Pre-ACA 66,757; Post-ACA 26,047）
- **RD窗口**：±120个月（±10年围绕65岁）
- **主带宽**：60个月（±5年）

---

## 二、数据现状

### 2.1 数据来源与覆盖
| 项目 | 详情 |
|------|------|
| 数据源 | MEPS FYC 公共使用文件 |
| 年份范围 | 1996-2023 (28年, h12-h251) |
| 已使用年份 | 2002-2017 (16年pooled) |
| 未使用年份 | 1996-2001, 2018-2023 |
| 每年样本 | ~30,000-35,000 人 |
| 文件格式 | .dta (Stata) → R读取 |

### 2.2 变量协调 (Harmonization) 现状

已实现跨年变量名统一映射，将年份后缀变量（如 `TOTSLF22`, `TOTSLF21`）映射到 canonical name（如 `TOTSLF`）。**但存在以下已知/潜在问题**：

| 问题类别 | 具体情况 | 影响程度 |
|----------|----------|----------|
| **变量可用性随年份变化** | 教育 (EDUCYR) 在2004年前可能缺失; RACETHX 仅部分年份完整 | 中等 — 影响HTE协变量选择 |
| **编码一致性** | 不同年份的分类变量编码可能存在细微差异（如POVCAT编码、EMPST编码） | 待验证 — 已有QC检查但需更仔细审核 |
| **月度保险变量命名** | 月份缩写因年份不同（JA/FE/MA vs 01/02/03），已在harmonize中处理 | 已解决 |
| **支出变量通胀** | **当前未做通胀调整**，spending以名义美元衡量 | 高 — pooled多年数据中这是一个严重问题 |
| **权重变量** | PERWT跨年一致，但SAQ权重、DCS权重并非所有年份都可用 | 低 — 当前只用PERWT |
| **慢性病变量** | 部分慢性病指标（如CANCERDX）在早期年份可能不存在 | 中等 — 影响chronic_count构建 |
| **Access变量** | DLAYCA42, AFRDCA42等在大部分年份可用，但编码一致性需确认 | 待验证 |
| **Bill stress变量** | PROBPY42, PYUNBL42 未在当前分析中使用 | 潜在扩展 |

### 2.3 当前使用的变量清单

#### RD核心变量
- `age_months_c65`：以月为单位的年龄，centered at 65 (running variable)
- `z_age65`：处理指派 (1 if age ≥ 65)
- `t_medicare_any`：Medicare 覆盖 (first-stage endogenous variable, from MCREV)

#### 结局变量 (15个已测试)
| 类别 | 变量 | 描述 | 当前结果显著性 (pooled all) |
|------|------|------|--------------------------|
| **支出** | TOTSLF | 自付支出 | **FRD=-$289, p<0.001** |
| 支出 | log_totslf | 对数自付 | FRD=-0.20, p=0.027 |
| 支出 | TOTEXP | 总支出 | FRD=-$701, p=0.27 (NS) |
| **经济保护** | cat_oop05 | 灾难性OOP >5%收入 | **FRD=-0.061, p<0.001** |
| 经济保护 | cat_oop10 | 灾难性OOP >10%收入 | FRD=-0.010, p=0.39 (NS) |
| **就医可及** | y_afrdca42 | 因费用放弃就医 | FRD=-0.013, p=0.043 |
| 就医可及 | y_dlayca42 | 因费用延迟就医 | FRD=0.002, p=0.77 (NS) |
| 就医可及 | y_afrdpm42 | 因费用放弃处方药 | FRD=-0.009, p=0.16 (NS) |
| 就医可及 | y_dlaypm42 | 因费用延迟处方药 | FRD=0.002, p=0.85 (NS) |
| 就医可及 | y_haveus | 有常规就医来源 | FRD=0.021, p=0.096 |
| **利用** | OBTOTV | 门诊次数 | FRD=0.66, p=0.20 (NS) |
| 利用 | ERTOT | 急诊次数 | FRD=0.010, p=0.68 (NS) |
| 利用 | IPDIS | 住院次数 | FRD=0.007, p=0.72 (NS) |
| 利用 | RXTOT | 处方药次数 | FRD=-0.86, p=0.46 (NS) |

#### HTE协变量 (12个)
| 变量 | GRF重要性 | 描述 |
|------|-----------|------|
| EDUCYR | 16.5% | 教育年限 |
| chronic_count | 15.1% | 慢性病数量 (6种之和) |
| YEAR | 13.2% | 年份 |
| RTHLTH42 | 12.2% | 自评健康 |
| REGION | 8.3% | 地区 |
| MNHLTH42 | 8.1% | 心理健康 |
| MARRY | 7.5% | 婚姻状况 |
| POVCAT | 7.4% | 贫困分类 |
| EMPST42 | 7.3% | 就业状况 |
| SEX | 2.7% | 性别 |
| post_aca | 1.5% | ACA后期 |
| HISPANX | 0.2% | 西裔 |

### 2.4 公共FYC数据的已知限制
| 限制 | 影响 | 可能的解决方案 |
|------|------|----------------|
| **无州级地理编码** | 无法做州级Medicaid扩展DiD | 只能做全国层面pre/post ACA代理分析 |
| **无计划免赔额/保费** | 无法识别HDHP | 标记为"不可行" |
| **无MSA标识(部分年份)** | 无法控制城乡差异 | 只用REGION |
| **公共文件无法link其他文件** | 无法与Medical Conditions / Event文件关联 | 仅限FYC内变量 |

---

## 三、已有结果详述

### 3.1 First Stage
Medicare在65岁断点处覆盖率从~11%跳升至~97%，first stage非常强。Pre-ACA和Post-ACA均如此。

### 3.2 主要RD估计

**核心发现（Pooled 2002-2017）**：
- Medicare显著降低自付支出约$289 (p<0.001)
- Medicare显著降低灾难性OOP (>5%收入) 概率约6.1个百分点 (p<0.001)
- 对总支出、大部分利用指标、延迟就医指标效应不显著

**Pre-ACA vs Post-ACA对比**：
| 结局 | Pre-ACA FRD | Post-ACA FRD | 差异方向 |
|------|-------------|--------------|----------|
| TOTSLF | -$257 (p=0.002) | **-$375 (p=0.008)** | Post-ACA效应更大 |
| log_totslf | -0.11 (NS) | **-0.48 (p=0.009)** | Post-ACA显著 |
| cat_oop05 | -0.051 (p=0.015) | **-0.076 (p=0.002)** | Post-ACA效应更大 |
| ERTOT | 0.055 (p=0.046) | **-0.104 (p=0.041)** | **方向反转** |
| RXTOT | 0.76 (NS) | **-5.11 (p=0.031)** | **方向反转** |
| y_dlayca42 | -0.009 (NS) | **0.032 (p=0.050)** | Post-ACA延迟增加？ |

**注意**：Pre-ACA vs Post-ACA 的一些结果出现了方向反转（ERTOT, RXTOT），以及违反直觉的结果（Post-ACA延迟就医反而增加）。这些需要理论解释或视为噪声。

### 3.3 效度检验
- **McCrary密度检验**：无操纵证据（通过）
- **协变量平衡**：SEX (p=0.014), POVCAT (p=0.008), EMPST42 (p=0.040) 在断点处存在不平衡，其余变量平衡
- **稳健性**：BW=30(窄)时TOTSLF效应不显著(p=0.40)，BW=90(宽)和Donut均显著

### 3.4 异质性处理效应 (HTE)
- **仅TOTSLF完成了HTE分析**（其他结局因完整案例不足被跳过）
- CATE范围：[-$5,387, +$2,554]，均值 -$88.71
- 62.3%的个体CATE为负（受益于Medicare）
- **按贫困分组**：中等收入(POVCAT=4)受益最大(-$102.55)，高收入(POVCAT=5)受益最小(-$60.97)
- **按健康状况**：健康差者受益更大(-$123.71 vs -$71.79)

### 3.5 Policy Trees
- Depth-2树：基于EDUCYR和chronic_count分裂，覆盖~50%人群
- Depth-3树：覆盖~87%人群，增加RTHLTH42和EMPST42分裂
- 定向分配在5%预算时value为-$323（vs uniform -$83），效率提升显著

---

## 四、当前不足与待解决问题

### 4.1 理论机制缺失 (CRITICAL)
**当前问题**：分析是纯实证驱动的，缺乏清晰的理论框架来解释：
1. **为什么** Medicare 降低OOP但不影响总支出？（保险的成本转移 vs 利用效应）
2. **为什么** 异质性的维度是教育和慢性病而不是收入？
3. **为什么** Pre-ACA和Post-ACA效应存在差异？（ACA如何改变了Medicare@65的边际效应？）
4. HTE中 YEAR 的高重要性 (13.2%) 意味着什么？是时间趋势还是真实的政策环境变化？

**需要建立的理论链条**：
- Insurance → Financial protection → Access → Utilization → Health outcomes
- 但当前结果显示中间环节（access, utilization）大多不显著，这与标准理论预测不一致

### 4.2 创新性不足 (CRITICAL)
Medicare@65 RDD 是一个非常成熟的识别策略，已有大量文献：
- Card et al. (2008, 2009) — 开创性工作
- Barcellos & Jacobson (2015) — 健康行为
- Wallace & Song (2016) — 利用
- 等等大量后续研究

**需要思考**：本研究的创新点在哪里？可能的方向：
1. **方法创新**：GRF + Policy Trees 在 RDD 框架下的应用（Causal ML for HTE in RD）
2. **时间跨度创新**：28年数据 pooled 分析，跨越多个政策变革期
3. **政策定向创新**：从"平均效应"到"谁受益最多"的转变
4. **多结局广泛测试**：系统性测试多类结局的异质性模式
5. **Pre-ACA vs Post-ACA**：ACA如何改变了Medicare断点的边际效应

### 4.3 技术问题
| 问题 | 严重性 | 解决方案 |
|------|--------|----------|
| 未做通胀调整 | 高 | 需用CPI-Medical或CPI-U调整spending到某基准年 |
| HTE仅完成TOTSLF | 高 | 需为其他显著结局（cat_oop05, y_afrdca42）完成HTE |
| 协变量不平衡(POVCAT, EMPST) | 中 | 需加入协变量控制的RD或做敏感性分析 |
| 未用VARPSU聚类 | 中 | 需在rdrobust中加入cluster选项 |
| 窄带宽(BW=30)结果不显著 | 中 | 考虑CCT数据驱动带宽选择 |
| 部分年份变量缺失 | 中 | 需检查哪些年份-变量组合完整可用 |
| 仅用PERWT未用Survey Design | 低-中 | 可用survey包做完整设计 |
| 未做多重比较校正 | 中 | 15个结局需FDR/Bonferroni调整 |

### 4.4 年份选择问题
当前用 2002-2017，需要思考：
- **为什么是2002起？** — 可能是因为2002前教育变量不完整
- **为什么到2017？** — ACA后初始稳定期？还是数据当时只到这里？
- **要不要加入2018-2023？** — 可以扩大Post-ACA样本，但COVID-19 (2020-2021) 是一个严重的混淆因素
- **要不要分更细的时期？** — 如 pre-Medicare Part D (pre-2006), post-Part D, pre-ACA, post-ACA
- **1996-2001可以加入吗？** — 取决于关键变量的可用性

---

## 五、已探索但未深入的方向

### 5.1 Age-26 RDD (ACA Dependent Coverage)
在 `archive/legacy_analysis/rd26_dependent.R` 中有初步框架，但未完成分析。利用26岁ACA依赖人覆盖断点，识别失去父母保险对年轻成人的因果效应。

### 5.2 保险流失 (Insurance Churn)
已构建月度保险转换指标（months_insured, num_switches, high_churn），但未用于正式因果分析。可用panel FE或DML方法。

### 5.3 Medicare Advantage vs Traditional Medicare
MCRPHO变量可用于区分MA和传统Medicare，但因选择偏差只能用DML而非RD。

### 5.4 医疗账单压力 (Medical Bill Stress)
PROBPY42, PYUNBL42, CRFMPY42 等变量可作为额外结局，与CFPB政策动机对接。

### 5.5 灾难性OOP的更多阈值
已测试5%和10%，可扩展到20%，或使用连续OOP/income比率。

---

## 六、MEPS FYC 中尚未利用的重要变量

| 变量类别 | 具体变量 | 潜在用途 |
|----------|----------|----------|
| **SAQ健康评分** | VPCS42, VMCS42 (VR-12) | 健康结局（需SAQ权重） |
| **心理健康筛查** | K6SUM42, PHQ242 | 心理健康结局 |
| **预防保健** | ADFLST42, ADBPCK42, ADCLNS42 | 预防性服务利用 |
| **通常就医来源细节** | TMTKUS42, PHNREG42 | 就医便利性机制 |
| **交流质量** | TREATM42, DECIDE42 | 医患关系质量 |
| **牙科可及** | DLAYDN42, AFRDDN42 | 牙科覆盖差异 |
| **处方药细分** | RXEXP, RXSLF | 药品支出和自付 |
| **就业细节** | CHGJ3142, CHGJ4253 | 工作变动→保险变动 |
| **移民/语言** | BORNUSA, HWELLSPK | 注册摩擦机制 |
| **账单压力** | PROBPY42, PYUNBL42, CRFMPY42 | 经济压力结局 |
| **COVID相关** | COVIDTST, CVDLGACT | 2020+年份特殊变量 |

---

## 七、需要Pro模型深入思考的问题

### 7.1 理论框架构建
1. **保险的多维效应理论**：如何建立一个coherent的理论框架，解释Medicare为什么主要通过financial protection渠道（降低OOP）发挥作用，而对access和utilization影响有限？是否可以用moral hazard理论、consumption smoothing理论、或behavioral economics的loss aversion来解释？

2. **异质性的理论基础**：教育为什么是HTE最重要的维度？可能的解释：
   - 信息/健康素养假说：低教育者更难理解和利用Medicare福利
   - 收入-教育分离假说：教育捕捉了POVCAT未能捕捉的人力资本维度
   - 先前保险状况假说：教育水平与65岁前的保险覆盖质量相关

3. **Pre-ACA vs Post-ACA差异的理论解释**：
   - ACA扩展了<65岁人群的保险覆盖 → 65岁断点处的"保险增益"可能改变（比较对象不同了）
   - Post-ACA的Medicare@65效应更大是否因为：ACA人群此前有较差的保险 → 转入Medicare改善更大？
   - 还是因为Post-ACA期间医疗成本更高 → Medicare的保护效应更大？

### 7.2 创新角度
1. **哪种创新角度最有可能被Q3-Q4期刊接受？** 考虑：
   - 纯方法论创新（Causal Forest in RD）可能更适合方法学期刊
   - 政策创新（targeting / precision public health）可能更适合health policy/economics期刊
   - 时间维度创新（跨政策时期的效应演变）可能更适合保险/卫生经济学期刊

2. **是否应该改变核心识别策略？**
   - 当前：Fuzzy RD at 65 → 非常成熟，创新空间有限
   - 替代：多断点比较（65 vs 26）、跨时期政策变化的三重交互、或完全转向churn/DML方向？

3. **"广泛机制测试"的价值**：是否应该系统性地测试大量outcome × covariate组合，形成一个"机制图谱"？这在方法论上是否defensible（多重比较问题）？

### 7.3 具体操作可行性
1. **年份选择**：
   - 加入2018-2023是否可行？COVID的影响如何处理？
   - 是否应该做rolling/expanding window分析来展示效应的时间演变？
   - 1996-2001加入后变量完整性如何？

2. **变量协调深层问题**：
   - 哪些变量在跨年分析中最可能存在测量不一致？
   - 是否需要对每个变量做跨年coding consistency的正式测试？
   - 通胀调整应该用CPI-U还是CPI-Medical？基准年选哪一年？

3. **HTE扩展**：
   - 如何解决非TOTSLF结局的HTE完整案例不足问题？
   - 是否可以对binary outcomes用不同的GRF方法（如causal forest而非instrumental forest）？
   - 是否应该纳入更多协变量（如移民状态、语言、工作变动）到HTE？

4. **其他topic module的可行性**：
   - Age-26 RD 是否值得投入？First stage强度如何？
   - Insurance churn 模块用panel FE是否可行（MEPS只有2年panel）？
   - MA vs Traditional Medicare 在无instrument情况下能否发表？

### 7.4 方法论深入
1. **rdrobust vs 手动RD**：当前用rdrobust默认设置。是否应该：
   - 使用CCT最优带宽选择而非manual BW=60？
   - 加入协变量（covariates in RD）来解决balance问题？
   - 使用local quadratic (p=2) 作为robustness？

2. **GRF选择**：
   - 当前用instrumental_forest(2000 trees)。是否应该用causal_forest？
   - honesty splitting的train/test比例(70/30)是否合适？
   - 是否需要cross-fitting而不是simple split？

3. **Policy tree**：
   - 当前policy tree的welfare function是什么？是直接用CATE还是某种transformed score？
   - 是否应该加入公平性约束（按种族/收入的最低覆盖比例）？
   - Policy value curve只到50% budget — 是否应该展示完整曲线？

4. **Survey design**：
   - 当前部分规范未用VARPSU聚类。rdrobust是否支持survey design？
   - GRF/policy tree中如何正确使用survey weights？

---

## 八、我的初步看法和建议

### 8.1 关于理论框架
建议围绕 **"保险作为经济保护工具" (Insurance as Financial Protection)** 构建理论框架，而非传统的 "保险→access→utilization→health" 链条。原因：
1. 你的结果明确显示financial protection效应最强（TOTSLF, cat_oop05显著），而access和utilization效应弱
2. 这与近年来health economics文献的趋势一致（Finkelstein et al. Oregon Experiment也发现类似模式）
3. 可以对接CFPB的medical debt政策动机，增加政策相关性
4. HTE中教育和慢性病的重要性可以用"财务脆弱性"(financial vulnerability)概念统一解释

### 8.2 关于创新角度
最有前景的创新组合可能是：
1. **"Precision targeting of financial protection"** — 从平均效应到精准定向
2. **跨ACA时期比较** — 展示policy context如何调节Medicare的边际效应
3. **Causal ML in RD框架的规范化应用** — 将GRF+policy tree标准化为RD研究的补充工具

这三者结合可以形成一个coherent的贡献：**"谁从Medicare中获得最多经济保护，以及这种模式如何随政策环境变化？"**

### 8.3 关于具体执行优先级
1. **最优先**：通胀调整 + 完整survey design + 多重比较校正 — 这些是审稿人必问的
2. **高优先**：为cat_oop05和y_afrdca42完成HTE分析；加入协变量控制的RD
3. **中优先**：考虑加入2018-2019（避开COVID）；CCT带宽选择
4. **可选探索**：Medical bill stress变量作为额外结局；Age-26模块的初步first stage评估

### 8.4 关于发表策略
- **目标期刊类型**：Health Economics, Health Services Research, European Journal of Health Economics, Medical Care 等Q3-Q4
- **卖点应该是**：(1) 方法规范且前沿 (Causal ML in RD)；(2) 政策导向明确 (precision targeting)；(3) 时间跨度大 (20+年)；(4) 结果具有政策含义 (谁最需要帮助)
- **风险**：Medicare@65 RD 已被大量研究 → 必须清晰说明增量贡献

---

## 九、数据与代码结构快速参考

### 活跃代码入口
```
scripts/setup/bootstrap_packages.R          # 包安装
scripts/qc/run_harmonization_checks.R       # 变量协调QC
scripts/pipeline/prepare_pooled_2002_2017.R  # 数据准备
scripts/pipeline/run_rdd_pooled_2002_2017.R  # 主分析 (736行)
```

### 核心模块
```
src/features/harmonize_variables.R  # 变量映射 (238行)
src/features/derive_features.R      # 特征工程 (179行)
src/utils/project_paths.R           # 路径工具
```

### 输出目录
```
outputs/rdd_pooled_2002_2017/
  ├── figures/   (17 PNG)
  ├── tables/    (14 CSV + 2 TXT)
  ├── models/    (iv_forest.rds, policy_tree_d2.rds, policy_tree_d3.rds)
  └── logs/      (2 TXT)
```

### 数据路径
```
data/intermediate/fyc_all_years/fyc_YYYY.dta  # 28年原始数据
data/derived/pooled_2002_2017.parquet          # 已缓存分析数据集
data/derived/pooled_2002_2017.rds
```

---

## 十、附录：Deep Research Report 关键建议摘要

此前的deep research report (存于archive/research_notes/) 提出了5个paper-ready topic modules的完整规范，包括：

1. **Medicare@65** (当前已执行) — Fuzzy RD，15个结局
2. **ACA Age-26** — Fuzzy RD at 26, dependent-ESI proxy treatment
3. **Insurance Churn** — Panel FE / DML, monthly coverage transitions
4. **Medicare Advantage vs Traditional** — DML (selection-on-observables), sensitivity analysis
5. **Catastrophic OOP / Medical Debt** — DML, CFPB-anchored policy motivation

Report还建议了：
- Stage-gating pipeline (A: screen → B: causal core → C: HTE → D: robustness)
- Capability flags for FYC limitations
- Shared HTE/policy-learning module design
- Reproducible manifest system

**这些方向中，哪些值得进一步投入？资源有限的情况下如何排序？**
