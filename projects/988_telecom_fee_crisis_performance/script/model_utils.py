from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class FEModelResult:
    table: pd.DataFrame
    nobs: int
    n_clusters: int
    r2: float
    outcome: str
    model: str


def month_diff(later: pd.Timestamp, earlier: pd.Timestamp) -> int:
    return (later.year - earlier.year) * 12 + later.month - earlier.month


def add_constant_and_fe(df: pd.DataFrame, regressors: list[str], fe_cols: list[str]) -> tuple[pd.DataFrame, list[str]]:
    parts = [pd.Series(1.0, index=df.index, name="const")]
    names = ["const"]
    for col in regressors:
        parts.append(pd.to_numeric(df[col], errors="coerce").astype(float).rename(col))
        names.append(col)
    for fe in fe_cols:
        dummies = pd.get_dummies(df[fe].astype(str), prefix=fe, drop_first=True, dtype=float)
        parts.append(dummies)
        names.extend(dummies.columns.tolist())
    x = pd.concat(parts, axis=1)
    return x, names


def fit_fe_ols(
    df: pd.DataFrame,
    outcome: str,
    regressors: list[str],
    fe_cols: list[str],
    cluster_col: str,
    model_name: str,
) -> FEModelResult:
    cols = list(dict.fromkeys([outcome, cluster_col] + regressors + fe_cols))
    work = df[cols].copy()
    for col in [outcome] + regressors:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    work = work.dropna()
    if len(work) <= len(regressors) + 3:
        raise ValueError(f"Not enough observations for {model_name} on {outcome}.")

    x_df, names = add_constant_and_fe(work, regressors, fe_cols)
    y = work[outcome].to_numpy(float)
    x = x_df.to_numpy(float)
    xtx_inv = np.linalg.pinv(x.T @ x)
    beta = xtx_inv @ x.T @ y
    fitted = x @ beta
    resid = y - fitted
    tss = float(((y - y.mean()) ** 2).sum())
    rss = float((resid**2).sum())
    r2 = 1.0 - rss / tss if tss > 0 else np.nan

    clusters = work[cluster_col].astype(str).to_numpy()
    unique_clusters = np.unique(clusters)
    meat = np.zeros((x.shape[1], x.shape[1]))
    for cluster in unique_clusters:
        idx = clusters == cluster
        xg = x[idx, :]
        eg = resid[idx]
        score = xg.T @ eg
        meat += np.outer(score, score)
    n, k = x.shape
    g = len(unique_clusters)
    correction = 1.0
    if g > 1 and n > k:
        correction = (g / (g - 1)) * ((n - 1) / (n - k))
    vcov = correction * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.maximum(np.diag(vcov), 0.0))
    tvals = np.divide(beta, se, out=np.full_like(beta, np.nan, dtype=float), where=se > 0)
    dfree = max(g - 1, 1)
    pvals = 2 * (1 - stats.t.cdf(np.abs(tvals), df=dfree))

    table = pd.DataFrame(
        {
            "model": model_name,
            "outcome": outcome,
            "term": names,
            "estimate": beta,
            "std_error_cluster": se,
            "t_stat": tvals,
            "p_value": pvals,
            "nobs": n,
            "n_clusters": g,
            "r2": r2,
        }
    )
    return FEModelResult(table=table, nobs=n, n_clusters=g, r2=r2, outcome=outcome, model=model_name)


def event_name(event_time: int) -> str:
    if event_time < 0:
        return f"event_m{abs(event_time)}"
    return f"event_p{event_time}"


def state_block_bootstrap(
    df: pd.DataFrame,
    stat_func,
    n_boot: int = 200,
    seed: int = 988,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    states = np.array(sorted(df["state"].dropna().unique()))
    vals = []
    for _ in range(n_boot):
        draw = rng.choice(states, size=len(states), replace=True)
        pieces = []
        for idx, state in enumerate(draw):
            part = df[df["state"].eq(state)].copy()
            part["state"] = f"{state}__b{idx}"
            pieces.append(part)
        sample = pd.concat(pieces, ignore_index=True)
        try:
            vals.append(float(stat_func(sample)))
        except Exception:
            vals.append(np.nan)
    return np.array(vals, dtype=float)
