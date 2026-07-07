# SIPP 與 CMS Medicaid Unwinding 論文的競品與缺口擷取

## 倉庫脈絡與判準

我把你的提案重疊判準，設成「以 SIPP 2021–2023 person-month transition 建 state-month cells，將 entity["organization","Centers for Medicare & Medicaid Services","US federal agency"] unwinding renewal-burden 指標對上 Medicaid exit to uninsured 與 persistent uninsured 類型結果，並往 subgroup / risk heterogeneity 延伸；若識別能站穩，才考慮 DML / causal ML」。你 repo 目前可見 memo 也明確把這支線界定為 **diagnostic state-month screen**，且 **not ready for DID / DML / causal ML**；timing stress 雖有改善，但作者自己仍說「diagnostic rather than causal」。fileciteturn6file0 fileciteturn7file0

因此我把「直接競品」定義為：已經很接近你的四個核心元件之任兩到三項者——
SIPP / 個體級 survey microdata、CMS unwinding renewal 資料、harmful churn / uninsurance transition 結果、以及 subgroup / targeting / ML。fileciteturn6file0 fileciteturn7file0

## 競品擷取總表

| 分類 | 來源 | 同行審查 | 精確研究問題 | 資料 / 樣本 | 結果變數 | 暴露 / 處置 | 識別策略 / ML | 主要結果 | 與你計畫重疊 | 若該文成立仍剩的缺口 |
|---|---|---:|---|---|---|---|---|---|---|---|
| 直接競品 | *Coverage and Access Changes During Medicaid Unwinding*，JAMA Health Forum，2024 citeturn18view0turn19view1 | 是 | 低收入者在 unwinding 初期如何掉保、轉往何種保險、以及可近性/負擔是否惡化？ citeturn18view0 | 四個南方州（Arkansas, Kentucky, Louisiana, Texas）19–64 歲、2022 收入低於 138% FPL 的 multimodal survey；亦問 child coverage。citeturn18view0turn19view3 | 自陳 Medicaid disenrollment、目前保險型態、coverage gap、因費用延遲照護等。citeturn3search3turn18view0 | unwinding 情境下曾否自 2020 年後持有 Medicaid；並看州別與個體特徵。citeturn18view0 | 重複橫斷 survey；logit / adjusted predicted probabilities；異質性看州別、年齡、就業、SNAP、SSI、rural 等。citeturn18view0 | 約 1/8 受訪 Medicaid 受益人 reported exit；其中約半數無保；掉保者較常因費用延遲照護。citeturn3search3turn18view0 | **高**：直接研究 unwinding 下個體 survey coverage loss、gap 與 access。 | 沒有 SIPP person-month；沒有 CMS renewal burden state-month exposure；不是 transition-based person-month outcome；不是全國。 |
| 直接競品 | *The effect of ending the pandemic-related mandate of continuous Medicaid coverage on health insurance coverage*，entity["organization","Federal Reserve Board","US central bank board"] FEDS working paper，2025（後續文獻索引顯示已進入 HSR 流程） citeturn15view0turn2search21 | 目前可直接驗證版本否 | 終止 continuous enrollment 後，州別首次 disenrollment timing 是否提高成年人無保險與家庭經濟壓力風險？ citeturn15view0 | CMS 州月 enrollment + Household Pulse Survey，成年人 <65，全國，約 2020/08–2024/03。citeturn15view0turn16view3 | Medicaid coverage、uninsured、private coverage、household expense hardship。citeturn15view0turn16view3 | 州別「首次實質 disenrollment 開始時間」。citeturn15view0 | TWFE + Wooldridge/JW-DID；異質性看年齡、教育、種族等。無 ML。citeturn15view0 | Medicaid enrollment 下降約 6–12%；整體未見顯著無保上升，但「some college, no BA」族群無保約升 1 個百分點。citeturn7view1turn15view0 | **高**：全國、州月 timing、survey coverage 結果、異質性。 | 不是 SIPP；不是 person-month transition；沒有直接用 CMS updated renewal burden / procedural metrics；沒有 harmful persistent uninsured outcome。 |
| 直接競品 | *US Coverage Changes During Medicaid Unwinding in 2023*，JAMA Health Forum，2025 citeturn22view0turn23view0 | 是 | unwinding 第一年的 coverage loss 在州與群體間如何變化？new applications 與 procedural termination rates 有何關係？ citeturn8search0turn22view0 | CMS enrollment + CMS redetermination outcomes + NHIS 2019–2023；0–64 歲低收入者 subgroup analysis。citeturn22view0turn23view4 | administrative 與 self-reported Medicaid enrollment、uninsured、cost-related delays、new applications。citeturn22view0turn23view3 | unwinding period；並以州 procedural termination rate 高低分層。citeturn22view0turn23view3 | descrip­tive admin comparisons + interrupted time series；異質性看 sex、race/ethnicity、pregnancy、age。無 ML。citeturn22view0turn23view4 | median termination 率 26.6%，但 net enrollment decline 中位數僅 13.9%；高 procedural termination 州 application rebound 更大；截至 2023 年底未見明顯整體無保上升。citeturn8search2turn23view3 | **高**：直接使用 CMS unwinding renewal / termination 資料且做異質性。 | 仍是州級/季度層；沒有個體 month-to-month 跳轉；無 SIPP；無 persistent uninsured churn 結果。 |
| 鄰近競品 | *Medicaid Unwinding Experiences in Dual-Eligible Older Adults*，JAMA Health Forum，2025 citeturn20view2turn21view0 | 是 | dual-eligible 老年人對 Medicaid redetermination 的認知、renewal 經驗與 access barrier 為何？ citeturn20view2turn21view2 | 全國 65+、≤100% FPL、community-dwelling older adults national survey。citeturn20view2 | unwinding awareness、renewal completion、coverage loss、cost-related access barriers。citeturn20view2 | 是否失去 Medicaid、是否再拿回。citeturn20view2 | 橫斷 survey；異質性看 race/ethnicity、insurance type；小樣本 exploratory。citeturn20view2turn21view3 | 49% 幾乎完全沒聽過 unwinding；5.5% lost and not regained；失去 Medicaid 者 care barriers 較高。citeturn20view2 | **中**：直接研究 unwinding、個體層、程序障礙與 coverage loss。 | 僅限 dual-eligible older adults；沒有 SIPP / CMS burden；不是 person-month transition；不是一般 Medicaid churn paper。 |
| 鄰近競品 | *Unwinding of Continuous Medicaid Coverage Among Pediatric Community Health Center Patients*，JAMA Network Open，2025 citeturn24view0turn25view0 | 是 | unwinding 期間，社區健康中心兒童病患從 Medicaid 掉到 uninsured 的規模與不平等為何？ citeturn24view0turn25view4 | 多州 entity["organization","OCHIN","US health network nonprofit"] network、450,146 pediatric patients。citeturn24view0turn25view1 | disenrollment from Medicaid to uninsured status。citeturn24view0turn25view0 | demographics、state variation、medical complexity。citeturn24view0turn25view1 | cohort；logit + time-to-event / hazard；異質性看年齡、性別、種族、語言、medical complexity。citeturn24view0turn25view1 | 8.7% 掉到 uninsured；AIAN、complex chronic、部分年齡/性別群體較高。citeturn24view0turn25view1 | **中**：個體級 harmful outcome、heterogeneity、真實服務接觸資料。 | 不是 survey；無法區分 administrative vs true ineligibility；沒有 SIPP；沒有 CMS state-month burden exposure。 |
| 鄰近競品 | *Loss of Medicaid Coverage During the Renewal Process*，JAMA Health Forum，2024 citeturn6search0turn6search2 | 是 | 誰會在年度 renewal deadline 掉出 Medicaid？之後多久回流？ citeturn6search0turn6search2 | Wisconsin administrative enrollment/claims，2016–2020，684,245 enrollment spells／586,044 人。citeturn6search0turn6search2 | month 12→13 掉保、提前掉保、gap duration。citeturn6search2 | enrollee characteristics、baseline income/eligibility/use-of-care。citeturn6search0turn6search2 | cohort + Kaplan-Meier + logistic regression；異質性看年齡、照護使用、種族等。無 ML。citeturn6search0turn6search2 | 20% 在 renewal deadline 掉保；其中 37% 六個月內回流。citeturn6search2 | **中**：非常接近「administrative burden / procedural loss / churn return」邏輯。 | 非 unwinding 時期；單州；不是 survey；沒有 CMS unwinding burden；沒有 persistent uninsured harmful outcome。 |
| 背景 / 動機 | entity["organization","KFF","health policy nonprofit"] *Survey of Medicaid Unwinding*，2024 citeturn13search0turn13search1 | 否 | 受益人對 unwinding 的認知、renewal 困難、程序問題、掉保後去向與負擔為何？ citeturn13search0turn14search3 | 1,227 位在 2023/01–03 曾有 Medicaid 的美國成年人，全國 survey。citeturn13search0 | awareness、renewal problems、disenrollment、current insurance、financial worries。citeturn13search0turn13search1 | unwinding 經驗與州 expansion status 等描述性切分。citeturn13search0turn14search3 | descriptive survey；無正式因果識別。citeturn13search0 | 19% 說自己曾在 unwinding 中掉保；其中 23% 仍 uninsured；58% 嘗試 renewal 者至少遇到一個問題。citeturn13search1turn14search3 | **中低**：非常有力的 procedural burden 動機材料。 | 非學術識別；沒有 month-level transitions；沒有 CMS burden linkage；無 author-stated full limitation section 可直接抽取。 |
| 資料先例 | *Evaluating State Options for Reducing Medicaid Churning*，Health Affairs，2015 citeturn30search0 | 是 | 哪些 eligibility-policy option 最能減少 Medicaid churning？ citeturn30search0 | SIPP 2004–2007 成年人 48-month panel；全國模擬。citeturn30search0 | transitions into/out of Medicaid、churning episodes、all-year coverage、caseload。citeturn4search1turn30search0 | 四種 simulated policy options。citeturn30search0 | longitudinal simulation model；無 ML。citeturn30search0 | 年底延長與 12-month continuous eligibility 最能減少 churn。citeturn30search0 | **中**：SIPP、monthly transition、Medicaid churn 核心 precedent。 | 是模擬政策，不是實際 unwinding；沒有 CMS renewal outcomes；沒有 harmful uninsured persistence。 |
| 資料先例 | *Health insurance regain after a spell of uninsurance*，Journal of Adolescent Health，2009 citeturn5search1turn5search7 | 是 | 年輕人在失去保險後，多久回到有保？不同 disability status 有何差異？ citeturn5search1 | SIPP 2001–2004；15–25 歲、基線有保險後失保者。citeturn5search1 | time to insurance regain、uninsurance spell duration。citeturn5search1 | disability severity。citeturn5search1 | Kaplan-Meier + discrete-time survival。無 ML。citeturn5search1 | 75% regained；non-severe disability 組回保較慢。citeturn5search1 | **中低**：spell persistence / persistent uninsurance 的實作範本。 | 不是 Medicaid unwinding；不是 Medicaid-specific exit；為 wave-based spell，而非你想做的更精細 month transition。 |
| 方法先例 | *Machine learning for detection of heterogeneous effects of Medicaid coverage on depression*，American Journal of Epidemiology，2024 citeturn27view0turn28view0 | 是 | 能否用 causal forest 找出 Medicaid 保障對 depression 的異質效果，並用於 targeting？ citeturn27view0turn28view4 | Oregon Health Insurance Experiment，隨機抽籤 Medicaid 擴張樣本。citeturn27view0 | positive depression screen、cost per depression case prevented。citeturn27view0 | Medicaid coverage，以 lottery 為 IV。citeturn27view0 | causal forest + cross-fitting + IV logic；明確 policy-targeting。citeturn27view0turn28view0 | high-benefit subgroup 的 depression reduction 遠大於 universal expansion，且每避免一例成本更低。citeturn27view0turn28view4 | **中**：若你未來走 causal ML，這是最像的 Medicaid targeting precedent。 | 不是 unwinding；結果是 depression 非 churn；識別仰賴 lottery，不是你現在的 observational design。 |
| 方法先例 | *Heterogeneity within the Oregon Health Insurance Experiment*，PLOS One，2024 citeturn11search0turn29view2 | 是 | causal / instrumental forests 能否在 OHIE 找到 insurance uptake 與 outcome heterogeneity？ citeturn29view2 | OHIE 約 12,229 人 in-person survey analytic sample。citeturn11search0turn29view0 | uptake、out-of-pocket spending、visits、drug use、ED/hospitalization 等。citeturn11search0turn29view2 | lottery selection / insurance coverage。citeturn11search0turn29view3 | causal forest + instrumental forest。citeturn11search0turn29view3 | uptake 異質性較明顯，但 outcome heterogeneity 整體偏弱。citeturn29view2turn29view3 | **中低**：告訴你在 Medicaid causally-identified 場景下，heterogeneity 也可能很弱、很吃 power。 | 不是 unwinding；不是 churn；作者自己也認為 subgroup power 不足。 |

## 逐源短註與精確缺口

### 最接近你提案的三篇

**McIntyre 2024, JAMA Health Forum**  
這篇最接近你想做的「個體級 coverage loss + harmful consequence」，但它沒有把 individual transition 跟 CMS 州月 administrative burden 接起來。作者自己承認限制是「*Our sample was limited to residents of 4 Southern states*」，所以它威脅的是你若只想寫「unwinding 讓人掉保、變無保、影響照護」這一層；它**沒有**佔掉「SIPP month-to-month transition + CMS burden linkage + persistent uninsured outcome」這個空位。citeturn19view2turn19view3

**Dasgupta and Solomon 2025 FEDS**  
這篇最接近你若走「全國 survey + state-month timing」路線。作者甚至寫到「*first to present an analysis using actual survey data*」來檢驗 CBO projection；但限制也很明確：HPS 低回應率，且作者說「*our analysis relies on self-reported survey data*」。所以它威脅的是「全國性、早期、州別 timing 對無保影響」問題；它**沒有**處理 person-month churn path，也沒有用 CMS updated renewal-burden 指標把 procedural load 與 harmful churn 直接對上。citeturn16view2turn16view3

**McIntyre et al. 2025, JAMA Health Forum**  
這篇是你在「CMS unwinding data empirically」面向上的最大直接對手，因為它直接用了 CMS redetermination / procedural termination 資料，並結合 NHIS 看 subgroup trends。作者的限制是「*Some terminations were still unresolved*」，而且 NHIS 只到 2023。換句話說，它已經吃掉「CMS administrative unwinding + demographic heterogeneity + application response」這塊，但**仍然沒有**個體的 Medicaid→uninsured next-month / persistent uninsured transition outcome，更沒有 SIPP person-month。citeturn23view0turn23view1turn23view4

### 鄰近但尚未正面覆蓋你核心設計的來源

**Tipirneni et al. 2025**  
貢獻聲明很直接：「*no research to date has focused on the unique experiences of dual-eligible older adults*」。這篇很適合當你寫 procedural burden 與 subgroup 章節時的比較組，但它的異質性分析受限於 state-level sample size，作者也說「*our findings may underestimate disenrollment*」。若把它當真，你的剩餘空間在於：把一般 Medicaid population 的 month transition 與 CMS state-month burden 連起來，而不是只描述一個高風險子群的 renewal experience。citeturn21view2turn21view1

**Bensken et al. 2025 pediatric**  
這篇把「harmful outcome」界定得很像你：直接看 Medicaid 掉到 uninsured。作者的限制也非常有用——「*precluded the ability to understand the reason for disenrollment*」。也就是說，它有真實個體級掉保到無保結果與不平等分析，但**無法**分辨 administrative vs eligibility，這正是你若接上 CMS renewal-burden 指標最可能補上的地方。citeturn25view0turn25view1

**Dague and Myerson 2024**  
這篇不是 unwinding paper，但它是 renewal-process paper 的硬核前身：單州行政資料、明確定義 renewal deadline loss、並量 gap duration。它的威脅不是主題，而是「人們會說 renewal loss / procedural loss 早有人做過」。你的回應應該是：那是 **pre-unwinding single-state administrative renewal study**；你做的是 **national unwinding-era SIPP person-month harmful churn linked to CMS state-month burden**。citeturn6search0turn6search2

**KFF Survey of Medicaid Unwinding**  
這篇不是學術識別，但對 procedural burden 敘事非常強：例如 58% renewal actors 遇到至少一個問題，19% 說自己曾掉保，23% 的 disenrolled 仍 uninsured。它會搶走你所有「動機式描述」的新聞性；所以你的 paper 不能主要停留在「很多人 renewal 很痛苦」這層，而要往 **transition mechanism + burden exposure + subgroup risk structure** 推。可惜我在可及頁面裡沒有找到明確作者限制段落，所以此處限制欄位只能保守標成「accessible summary 未明列」。citeturn13search1turn14search3

### SIPP 與 persistent uninsurance 的前置文獻

**Swartz et al. 2015**  
這篇最重要的價值，是它證明 SIPP 很早就被拿來做 Medicaid churn 的 longitudinal simulation，而且結果不是只有 point-in-time coverage，而是 transitions、all-year coverage、churning episodes。作者方法上明說模擬是以「*two different assumptions about monthly participation rates*」和 disruption rates 進行；所以它是 SIPP churn 文獻先例，但不是實際 unwinding 的觀察性實證，也沒有 harmful uninsured persistence。citeturn30search0

**Wang et al. 2009**  
這篇對你做 persistent uninsured 定義特別有用。作者明講「*we measure … during a wave … because of seam problems*」，這剛好提醒你：若你要在 SIPP 2021–2023 做真正的 person-month transition，必須在 paper 中主動處理 seam / reporting instability 的方法論說明。這篇是 spell-duration / survival 架構 precedent，不是 unwinding competitor。citeturn5search1

### causal ML 與 targeting 是否已被做掉

**Goto et al. 2024**  
這是最接近你未來若走 causal ML / policy learning 的 Medicaid precedent。作者的限制寫得很清楚：「*The causal forest can only detect heterogeneity across covariates included in the model*」，且 Oregon 外部效度有限。這代表：**方法上**，你可以合理引用 causal forest / targeting；**題材上**，它完全沒有碰 unwinding、coverage loss、administrative burden。citeturn28view0turn28view4

**Hattab et al. 2024**  
這篇的價值在於負面訊息：作者說研究「*underpowered to detect effects in subgroups*」，且結論是可能需要「*larger samples (e.g. administrative data)*」。這其實很像你 repo 目前的狀態：若識別與 sample support 還不夠，過早做 causal forest 會得到不穩定、難解釋的 heterogeneity。它是方法警告，不是主題競品。citeturn29view0turn29view1turn29view2

## 最實質的剩餘缺口

真正還沒被吃掉、而且與你 repo 目前方向最吻合的缺口，我判斷只剩三個，而且三個要**一起**成立才有紙的價值。第一，現有 unwinding 研究要嘛是個體 survey / EHR，但沒有 entity["organization","U.S. Census Bureau","US statistical agency"] SIPP 式的 person-month transition structure；要嘛是 CMS state-level renewal / termination 研究，但沒有個體 month-to-month 的 Medicaid→uninsured→persistent uninsured path。citeturn18view0turn15view0turn22view0turn24view0

第二，我沒有找到任何近似 paper 同時做了 **SIPP person-month transition outcomes + CMS updated renewal/procedural burden state-month exposure + harmful churn outcome**。最接近的組合是「McIntyre 2025 做 CMS state-level + NHIS」與「McIntyre 2024 / Bensken 2025 做個體 coverage loss」，但這兩類文獻仍是分開的。citeturn22view0turn23view3turn18view0turn24view0

第三，ML / targeting 面向目前只看到 Medicaid 的方法先例，還沒有我能確認的 **unwinding-specific causal ML / policy learning** paper。換言之，若你未來真要加 causal ML，最安全的寫法不是宣稱你在追隨既有 unwinding ML 文獻，而是說你借用 Medicaid causal-ML 的方法 precedent；題材本身仍屬空白，但 repo 自己也提醒現在尚未到可可信識別那一步。citeturn27view0turn29view0turn6file0turn7file0

## 開放問題與不完整處

有兩個地方我刻意保守。第一，*Loss of Medicaid Coverage During the Renewal Process* 我能穩定抽到 abstract / key points / methods 與結果，但 JAMA 站點之後對 full text 觸發 rate-limit，因此我沒有直接抓到作者完整的 limitation 段落；表中我因此把其限制寫成保守的設計邊界，而不是假裝有逐字限制引文。citeturn6search0turn20view0

第二，我沒有找到一篇我願意高信心標記為「已經完成 SIPP + CMS updated renewal outcomes + persistent uninsured harmful churn + credible causal ML」的論文。若你最後只能做到 descriptive / diagnostic，但能把這個四元組中的前三項真正做成一個連貫設計，仍然大概率有明確的 paper-level gap；反而若只做到一般性 survey coverage loss 或一般性 subgroup 描述，則會被上面的直接競品迅速覆蓋。citeturn18view0turn15view0turn22view0turn27view0turn29view0turn6file0turn7file0