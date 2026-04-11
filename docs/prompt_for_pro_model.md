# Prompt for Pro Reasoning Model

> 将此prompt连同 `project_briefing_for_reasoning.md` 一起提供给你的高推理模型。

---

## Context

I am a health economics researcher working on a US insurance empirical project using MEPS (Medical Expenditure Panel Survey) public data spanning 1996-2023 (28 years). I want to publish a paper in an SCI Q3-Q4 health economics or health services research journal.

## What I Have Done

I've completed a **pooled 2002-2017 Medicare@65 Fuzzy RDD analysis** combined with **Generalized Random Forest (GRF) instrumental forest for heterogeneous treatment effects** and **policy trees for targeted allocation**. Key findings:

- Medicare significantly reduces out-of-pocket spending by ~$289 (p<0.001) and catastrophic OOP (>5% of income) by 6.1pp (p<0.001)
- Effects on access barriers and utilization are largely insignificant
- Post-ACA effects are larger than pre-ACA
- HTE shows education and chronic disease count are the most important moderators (not income)
- Policy targeting can improve allocation efficiency by 15-20% over uniform

See the attached `project_briefing_for_reasoning.md` for complete data, methods, results, limitations, and variable details.

## What I Need You to Think About

Please provide deep, structured analysis on these interrelated questions:

### 1. Theoretical Framework (最重要)
- What theoretical framework best explains my empirical pattern (strong financial protection effect, weak access/utilization effect)? 
- How should I theoretically motivate the HTE findings (education > income in importance)?
- Can you propose a coherent mechanism chain that is consistent with my results and defensible to reviewers?
- How does this connect to existing literature (Oregon Health Insurance Experiment, Card et al. Medicare@65 papers, Finkelstein & colleagues)?

### 2. Innovation and Contribution
- Given that Medicare@65 RDD is a very well-studied design, what is my realistic incremental contribution?
- Among these potential innovation angles, which is most viable for Q3-Q4 journals?
  - (a) Causal ML (GRF + policy trees) as a systematic HTE tool in RDD
  - (b) 20+ year time-span analysis showing how effects evolve across policy regimes
  - (c) "Precision public health" targeting — who benefits most from Medicare financial protection
  - (d) Broad mechanism testing across many outcomes with proper multiple testing correction
  - (e) Some combination of the above
- Are there specific journals where this type of contribution would be most welcome?

### 3. Methodological Concerns
- My covariate balance tests show imbalance at the cutoff for POVCAT and EMPST42. How serious is this? What should I do?
- I haven't done inflation adjustment on spending. For pooled multi-year analysis, is CPI-U or CPI-Medical more appropriate? What base year?
- HTE was only estimated for TOTSLF (other outcomes had too many missing cases). How do I handle this?
- The narrow bandwidth (BW=30) yields insignificant results while the main (BW=60) and wide (BW=90) are significant. How should I present this?
- Should I use CCT data-driven bandwidth selection instead of manual bandwidth?
- Is 15 outcomes × 3 eras = 45 tests a multiple testing problem? How should I address it?

### 4. Year Selection and Data Scope
- Currently using 2002-2017. Should I extend to 2018-2019 (pre-COVID) or even 2020-2023 (with COVID)?
- Can I add 1996-2001 if some variables (especially EDUCYR) may be missing?
- Should I split by more policy periods (pre-Part D 2006, post-Part D, pre-ACA, post-ACA)?
- COVID-19 (2020-2021) is a major confounder. How do other researchers handle this in MEPS-based studies?

### 5. Variable Harmonization Risks
- What are the most common harmonization pitfalls in multi-year MEPS analyses?
- Which of my 15 outcome variables are most likely to have measurement inconsistency across years?
- The access variables (DLAYCA42, AFRDCA42) have specific response coding — is this stable across 2002-2017?
- Should I do formal measurement equivalence tests, or is documentation review sufficient?

### 6. Broader Testing Strategy
- Should I expand to test additional outcomes (medical bill stress, preventive care, dental access, mental health)?
- Should I add more HTE dimensions (immigration status, language, job changes)?
- Is there value in a "mechanism map" showing which pathways are active vs inactive?
- How do I balance breadth of testing with multiple comparison concerns and story coherence?

### 7. Alternative Research Designs Worth Pursuing
- Is the Age-26 ACA dependent coverage RDD worth pursuing as a companion analysis or separate paper?
- What about insurance churn analysis using MEPS panel (2-year) structure?
- Are there other identification strategies I'm missing that work with public MEPS FYC data?

### 8. Publication Strategy
- Given my results and realistic contribution, which journals should I target?
- What would be the strongest 1-paragraph "pitch" for this paper?
- What are the top 3 reviewer objections I should preempt?
- Should I aim for one comprehensive paper or split into multiple focused papers?

## How to Structure Your Response

Please organize your response hierarchically:
1. **Executive Summary** (your top-line assessment and recommendation in <500 words)
2. **Theoretical Framework Proposal** (detailed, with literature connections)
3. **Innovation Strategy** (rank the options, explain why)
4. **Methodological Recommendations** (specific, actionable, prioritized)
5. **Data and Scope Decisions** (year selection, variable choices)
6. **Publication Roadmap** (journals, timeline, presentation strategy)
7. **Risk Assessment** (what could go wrong, how to mitigate)

Be direct and critical. I need honest assessment of what's publishable and what's not, not encouragement. If an approach won't work, tell me why and suggest alternatives.
