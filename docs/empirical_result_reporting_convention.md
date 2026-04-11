# Empirical Result Reporting Convention

Last updated: `2026-04-11`

## Purpose

This file records the preferred reporting structure for all future empirical updates in this project.

Use this format whenever presenting a result to the user, another agent, or in a memo.

## Required Structure

Every result summary should clearly state:

1. `Question`
   - What empirical question is being tested?

2. `Sample / Unit`
   - What is the sample?
   - What is the observation unit?
   - What years and window are used?

3. `Outcome`
   - What exactly is the outcome?
   - How is it operationalized in the data?
   - Why does it matter substantively?

4. `Treatment / Exposure`
   - What is the treatment, exposure, or policy variable?
   - Is it person-level, state-month, or something else?
   - What does a higher value mean in plain language?

5. `Purpose`
   - Why was this specification run?
   - What weakness or hypothesis is it meant to test?

6. `Numerical Result`
   - Report the key numeric result directly.
   - If there are multiple windows or alignments, say which one matters most.

7. `Interpretation`
   - Explain in plain language what the result means.
   - Explicitly separate what the result supports from what it does **not** support.

8. `Evaluation`
   - Is this encouraging, weak, mixed, or not usable?
   - Say this frankly.

9. `Caveat`
   - State the main threat, limitation, or unresolved issue.

## Default Tone

- Use econometrics logic, but write in plain language.
- Do not assume the user knows what a variable name means.
- Do not say “good signal” or “not ideal” without explaining:
  - relative to what
  - why
  - and what it implies for the next step

## Project-Specific Reminder

For this project in particular, future updates should always define:

- the exact `outcome`
- the exact `treatment / exposure`
- the exact `window`
- whether the result is:
  - descriptive
  - diagnostic
  - risk-prediction
  - quasi-causal

and should always say whether the result changes:

- the mechanism story
- the preferred paper question
- the feasibility of later `DML / causal ML`
