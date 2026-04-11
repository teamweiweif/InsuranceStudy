# ==============================================================================
# Medicare@65 Pooled RDD + Causal ML Analysis: 2002-2017
# ==============================================================================
# Full pipeline: RD → HTE (GRF) → Policy Targeting (policytree)
# Reuses existing harmonize_variables.R + derive_features.R
# ==============================================================================

bootstrap_project_root <- function(start = getwd()) {
  current <- normalizePath(start, winslash = "/", mustWork = FALSE)
  if (!dir.exists(current)) current <- dirname(current)

  repeat {
    candidate <- file.path(current, "src", "utils", "project_paths.R")
    if (file.exists(candidate)) return(current)

    parent <- dirname(current)
    if (identical(parent, current)) {
      stop("Could not locate project root from: ", start)
    }
    current <- parent
  }
}

PROJECT_ROOT <- bootstrap_project_root()
source(file.path(PROJECT_ROOT, "src", "utils", "project_paths.R"))
set_project_root(PROJECT_ROOT)

if (identical(Sys.getenv("USINS_SMOKE_TEST"), "1")) {
  cat("Smoke test OK: run_rdd_pooled_2002_2017.R\n")
  cat(sprintf("Project root: %s\n", project_root()))
  cat(sprintf("Output directory: %s\n",
              project_path("outputs", "rdd_pooled_2002_2017")))
  quit(save = "no", status = 0)
}

library(data.table)
library(haven)
library(rdrobust)
library(rddensity)
library(grf)
library(policytree)
library(ggplot2)

source_project("src", "features", "harmonize_variables.R")
source_project("src", "features", "derive_features.R")

# Output
OUT <- project_path("outputs", "rdd_pooled_2002_2017")
ensure_dir(OUT)
for (d in c("figures", "tables", "models", "logs")) {
  ensure_dir(file.path(OUT, d))
}

# Log file
LOG <- file.path(OUT, "logs", sprintf("run_%s.txt",
                                       format(Sys.time(), "%Y%m%d_%H%M%S")))
initial_sink <- sink.number()
sink(LOG, split = TRUE)
on.exit({
  while (sink.number() > initial_sink) sink()
}, add = TRUE)

cat(strrep("=", 80), "\n")
cat("Medicare@65 Pooled RDD + Causal ML (2002-2017)\n")
cat(sprintf("Started: %s\n", Sys.time()))
cat(strrep("=", 80), "\n\n")

# ==============================================================================
# STEP 1: Load pooled data (pre-prepared or build from scratch)
# ==============================================================================

cat("STEP 1: Loading 2002-2017 data...\n")

CACHED_RDS <- project_path("data", "derived", "pooled_2002_2017.rds")

if (file.exists(CACHED_RDS)) {
  cat("  Loading cached dataset...\n")
  dt <- readRDS(CACHED_RDS)
  cat(sprintf("  Loaded: %s obs\n", format(nrow(dt), big.mark = ",")))
} else {
  cat("  No cached data found. Building from scratch...\n")
  cat("  (Run scripts/pipeline/prepare_pooled_2002_2017.R first for faster loading)\n\n")

  YEARS <- 2002:2017
  RD_WINDOW <- 120

  all_data <- list()
  for (yr in YEARS) {
    tryCatch({
      d <- harmonize_fyc(yr)
      d <- derive_features(d)
      d_rd <- d[!is.na(age_months_c65) & abs(age_months_c65) <= RD_WINDOW]
      if (nrow(d_rd) > 0) {
        all_data[[as.character(yr)]] <- d_rd
        cat(sprintf("  %d: %d obs\n", yr, nrow(d_rd)))
      }
    }, error = function(e) {
      cat(sprintf("  %d: ERROR - %s\n", yr, e$message))
    })
  }

  dt <- rbindlist(all_data, fill = TRUE)
  dt[, post_aca := as.integer(YEAR >= 2014)]
  dt[, era := fifelse(YEAR < 2014, "pre_aca", "post_aca")]

  # Cache for next time
  ensure_dir(dirname(CACHED_RDS))
  saveRDS(dt, CACHED_RDS)
  cat(sprintf("  Cached to: %s\n", CACHED_RDS))
}

cat(sprintf("\nPooled: %s obs, Below 65: %d, At/above 65: %d\n",
            format(nrow(dt), big.mark = ","),
            sum(dt$z_age65 == 0, na.rm = TRUE),
            sum(dt$z_age65 == 1, na.rm = TRUE)))

# Ensure era columns exist
if (!"post_aca" %in% names(dt)) dt[, post_aca := as.integer(YEAR >= 2014)]
if (!"era" %in% names(dt)) dt[, era := fifelse(YEAR < 2014, "pre_aca", "post_aca")]

# ==============================================================================
# STEP 2: Define outcomes and covariates
# ==============================================================================

cat("\nSTEP 2: Defining variables...\n")

# --- Outcomes ---
OUTCOMES <- c(
  # Spending (continuous)
  "TOTSLF", "log_totslf", "TOTEXP",
  # Financial protection (binary)
  "cat_oop10", "cat_oop05",
  # Access (binary, harmonized old+new names)
  "y_dlayca42", "y_afrdca42", "y_dlaypm42", "y_afrdpm42",
  # Utilization (count)
  "OBTOTV", "ERTOT", "IPDIS", "RXTOT",
  # Usual source of care
  "y_haveus"
)

# Filter to outcomes that actually exist
OUTCOMES <- intersect(OUTCOMES, names(dt))
cat(sprintf("  Outcomes available: %d\n", length(OUTCOMES)))
for (o in OUTCOMES) {
  n_valid <- sum(!is.na(dt[[o]]))
  cat(sprintf("    %s: %d valid (%.0f%%)\n", o, n_valid,
              100 * n_valid / nrow(dt)))
}

# --- HTE Covariates ---
# Only use variables confirmed available in 2002-2017
X_VARS_CANDIDATES <- c(
  # Demographics (100% available)
  "SEX", "HISPANX", "MARRY", "REGION",
  # SES (100% available)
  "POVCAT",
  # Employment (96% available)
  "EMPST42",
  # Health status (96% available)
  "RTHLTH42", "MNHLTH42",
  # Education (75% - missing 1999-2004, 2013)
  "EDUCYR",
  # Chronic conditions (60% - available 2007-2017)
  "chronic_count",
  # Race (42% - available 2012-2017 only)
  "RACETHX",
  # Time
  "post_aca", "YEAR"
)

# Filter to what's actually in the data with >50% non-NA
X_VARS <- c()
for (v in X_VARS_CANDIDATES) {
  if (v %in% names(dt)) {
    pct_valid <- mean(!is.na(dt[[v]]))
    if (pct_valid > 0.5) {
      X_VARS <- c(X_VARS, v)
      cat(sprintf("  ✓ %s: %.0f%% valid\n", v, 100 * pct_valid))
    } else {
      cat(sprintf("  ✗ %s: %.0f%% valid (dropped)\n", v, 100 * pct_valid))
    }
  }
}
cat(sprintf("\n  Final HTE covariates: %d variables\n", length(X_VARS)))

# ==============================================================================
# STEP 3: Descriptive statistics
# ==============================================================================

cat("\nSTEP 3: Descriptive statistics...\n")

desc <- dt[, .(
  N = .N,
  pct_female = 100 * mean(SEX == 2, na.rm = TRUE),
  mean_age = mean(AGE, na.rm = TRUE),
  pct_poor = 100 * mean(POVCAT <= 2, na.rm = TRUE),
  mean_totslf = mean(TOTSLF, na.rm = TRUE),
  mean_totexp = mean(TOTEXP, na.rm = TRUE),
  pct_delay = 100 * mean(y_dlayca42, na.rm = TRUE),
  mean_office = mean(OBTOTV, na.rm = TRUE),
  pct_er = 100 * mean(ERTOT > 0, na.rm = TRUE),
  pct_medicare = 100 * mean(t_medicare_any, na.rm = TRUE)
), by = .(era, z_age65)]

print(desc)
fwrite(desc, file.path(OUT, "tables", "descriptive_stats.csv"))

# ==============================================================================
# STEP 4: First stage by era
# ==============================================================================

cat("\nSTEP 4: First stage...\n")

MANUAL_BW <- 60  # ±5 years

run_rd <- function(y, x, w = NULL, bw = MANUAL_BW, label = "") {
  valid <- !is.na(y) & !is.na(x)
  if (!is.null(w)) valid <- valid & !is.na(w)
  if (sum(valid) < 200) return(NULL)

  args <- list(
    y = y[valid], x = x[valid], c = 0,
    h = bw, p = 1, kernel = "triangular"
  )
  if (!is.null(w)) args$fuzzy <- w[valid]

  tryCatch(do.call(rdrobust, args), error = function(e) NULL)
}

# First stage: all, pre-ACA, post-ACA
for (period in c("all", "pre_aca", "post_aca")) {
  sub <- if (period == "all") dt else dt[era == period]
  fs <- run_rd(sub$t_medicare_any, sub$age_months_c65)
  if (!is.null(fs)) {
    cat(sprintf("  %s: FS=%.4f (SE=%.4f, p=%.4f), N=%d+%d\n",
                period, fs$coef[1], fs$se[1], fs$pv[1],
                fs$N_h[1], fs$N_h[2]))
  }
}

# First stage plot
png(file.path(OUT, "figures", "first_stage.png"), width = 900, height = 500)
rdplot(dt$t_medicare_any, dt$age_months_c65, c = 0,
       title = "First Stage: Medicare Take-up at 65 (Pooled 2002-2017)",
       x.label = "Age in months (centered at 65)",
       y.label = "Medicare coverage rate")
dev.off()

# ==============================================================================
# STEP 5: Main RD estimates (all outcomes)
# ==============================================================================

cat("\nSTEP 5: Main RD estimates...\n")

rd_results <- list()

for (outcome in OUTCOMES) {
  y <- dt[[outcome]]
  valid <- !is.na(y) & !is.na(dt$age_months_c65) & !is.na(dt$t_medicare_any)
  if (sum(valid) < 500) next

  cat(sprintf("  %s (n=%d)... ", outcome, sum(valid)))

  # Reduced form
  rf <- run_rd(y, dt$age_months_c65)
  # Fuzzy RD
  frd <- run_rd(y, dt$age_months_c65, w = dt$t_medicare_any)

  if (!is.null(rf) && !is.null(frd)) {
    rd_results[[outcome]] <- data.table(
      outcome = outcome, era = "all", n = sum(valid),
      rf_coef = rf$coef[1], rf_se = rf$se[1], rf_pval = rf$pv[1],
      frd_coef = frd$coef[1], frd_se = frd$se[1], frd_pval = frd$pv[1]
    )
    cat(sprintf("RF=%.4f (p=%.3f), FRD=%.4f (p=%.3f)\n",
                rf$coef[1], rf$pv[1], frd$coef[1], frd$pv[1]))

    # RD plot
    png(file.path(OUT, "figures", sprintf("rd_%s.png", outcome)),
        width = 900, height = 500)
    rdplot(y[valid], dt$age_months_c65[valid], c = 0,
           title = sprintf("%s at Age 65 (Pooled)", outcome),
           x.label = "Age in months (centered at 65)",
           y.label = outcome)
    dev.off()
  }
}

# By era
for (period in c("pre_aca", "post_aca")) {
  sub <- dt[era == period]
  cat(sprintf("\n  --- %s ---\n", period))

  for (outcome in OUTCOMES) {
    y <- sub[[outcome]]
    valid <- !is.na(y) & !is.na(sub$age_months_c65) & !is.na(sub$t_medicare_any)
    if (sum(valid) < 300) next

    frd <- run_rd(y, sub$age_months_c65, w = sub$t_medicare_any)
    if (!is.null(frd)) {
      rd_results[[paste(outcome, period, sep = "_")]] <- data.table(
        outcome = outcome, era = period, n = sum(valid),
        rf_coef = NA_real_, rf_se = NA_real_, rf_pval = NA_real_,
        frd_coef = frd$coef[1], frd_se = frd$se[1], frd_pval = frd$pv[1]
      )
      cat(sprintf("  %s: FRD=%.4f (p=%.3f)\n",
                  outcome, frd$coef[1], frd$pv[1]))
    }
  }
}

results_dt <- rbindlist(rd_results)
fwrite(results_dt, file.path(OUT, "tables", "rd_results.csv"))
cat(sprintf("\n  -> %d estimates saved\n", nrow(results_dt)))

# ==============================================================================
# STEP 6: Density test + Covariate balance
# ==============================================================================

cat("\nSTEP 6: Validity checks...\n")

# McCrary density test
dens <- rddensity(dt$age_months_c65, c = 0)
cat(sprintf("  Density test p-value: %.4f\n", dens$test$p_jk))

# Save density test to file (without disrupting main sink)
tryCatch({
  writeLines(capture.output(summary(dens)),
             file.path(OUT, "tables", "density_test.txt"))
}, error = function(e) {
  cat(sprintf("  Warning: could not save density test: %s\n", e$message))
})

# Covariate balance
balance_vars <- intersect(c("SEX", "HISPANX", "MARRY", "POVCAT",
                            "EMPST42", "REGION"), names(dt))
balance_results <- list()
for (v in balance_vars) {
  rd_bal <- run_rd(dt[[v]], dt$age_months_c65)
  if (!is.null(rd_bal)) {
    balance_results[[v]] <- data.table(
      variable = v, coef = rd_bal$coef[1],
      se = rd_bal$se[1], pval = rd_bal$pv[1]
    )
    cat(sprintf("  Balance %s: coef=%.4f (p=%.3f)\n",
                v, rd_bal$coef[1], rd_bal$pv[1]))
  }
}
fwrite(rbindlist(balance_results),
       file.path(OUT, "tables", "covariate_balance.csv"))

# ==============================================================================
# STEP 7: Robustness checks
# ==============================================================================

cat("\nSTEP 7: Robustness...\n")

rob_outcomes <- c("TOTSLF", "y_dlayca42", "OBTOTV", "cat_oop10")
rob_outcomes <- intersect(rob_outcomes, OUTCOMES)
rob_results <- list()

for (outcome in rob_outcomes) {
  y <- dt[[outcome]]

  # Main
  rd_main <- run_rd(y, dt$age_months_c65, w = dt$t_medicare_any, bw = 60)
  # Narrow BW
  rd_bw30 <- run_rd(y, dt$age_months_c65, w = dt$t_medicare_any, bw = 30)
  # Wide BW
  rd_bw90 <- run_rd(y, dt$age_months_c65, w = dt$t_medicare_any, bw = 90)
  # Donut (exclude ±2 months of 65)
  dt_donut <- dt[abs(age_months_c65) > 2]
  rd_donut <- run_rd(dt_donut[[outcome]], dt_donut$age_months_c65,
                     w = dt_donut$t_medicare_any, bw = 60)

  specs <- list(
    list("BW=60 (main)", rd_main),
    list("BW=30 (narrow)", rd_bw30),
    list("BW=90 (wide)", rd_bw90),
    list("Donut ±2mo", rd_donut)
  )

  for (s in specs) {
    if (!is.null(s[[2]])) {
      rob_results[[paste(outcome, s[[1]])]] <- data.table(
        outcome = outcome, spec = s[[1]],
        frd_coef = s[[2]]$coef[1], frd_se = s[[2]]$se[1],
        frd_pval = s[[2]]$pv[1]
      )
    }
  }
}

rob_dt <- rbindlist(rob_results)
fwrite(rob_dt, file.path(OUT, "tables", "robustness.csv"))
cat("  Robustness saved\n")

# ==============================================================================
# STEP 8: CAUSAL ML — GRF Instrumental Forest (pooled HTE)
# ==============================================================================

cat("\n")
cat(strrep("=", 80), "\n")
cat("STEP 8: CAUSAL ML — GRF Instrumental Forest\n")
cat(strrep("=", 80), "\n\n")

# Primary HTE outcome
PRIMARY_OUTCOME <- "TOTSLF"  # OOP spending (most policy-relevant)

# Build complete-case HTE dataset
hte_vars <- c("DUPERSID", "YEAR", "fpl_bin", "era",
              PRIMARY_OUTCOME, "t_medicare_any", "z_age65",
              "age_months_c65", "PERWT", X_VARS)
hte_vars <- intersect(hte_vars, names(dt))

dt_hte <- dt[, ..hte_vars]
dt_hte <- dt_hte[complete.cases(dt_hte)]

cat(sprintf("HTE sample (complete cases): %s obs\n",
            format(nrow(dt_hte), big.mark = ",")))

if (nrow(dt_hte) >= 1000) {

  # Build X matrix (exclude IDs, outcome, treatment, instrument)
  x_cols <- intersect(X_VARS, names(dt_hte))
  X <- as.matrix(dt_hte[, ..x_cols])
  Y <- dt_hte[[PRIMARY_OUTCOME]]
  W <- dt_hte$t_medicare_any
  Z <- dt_hte$z_age65

  # Random 70/30 train/test split (across all years)
  # post_aca is included as a covariate so GRF learns time heterogeneity
  set.seed(42)
  n_hte <- nrow(dt_hte)
  train_idx <- sample(n_hte, floor(0.7 * n_hte))
  test_idx <- setdiff(1:n_hte, train_idx)

  cat(sprintf("  Train (70%%): %d obs\n", length(train_idx)))
  cat(sprintf("  Test  (30%%): %d obs\n", length(test_idx)))

  # --- Train GRF Instrumental Forest ---
  cat("\n  Training instrumental forest (2000 trees)...\n")
  t0 <- Sys.time()

  iv_forest <- instrumental_forest(
    X = X[train_idx, ],
    Y = Y[train_idx],
    W = W[train_idx],
    Z = Z[train_idx],
    sample.weights = dt_hte$PERWT[train_idx],
    num.trees = 2000,
    honesty = TRUE,
    tune.parameters = "all"
  )

  t1 <- Sys.time()
  cat(sprintf("  Training time: %.1f minutes\n",
              as.numeric(difftime(t1, t0, units = "mins"))))

  # --- Predict CATE on test set ---
  cat("  Predicting CATE on test set...\n")
  cate_pred <- predict(iv_forest, X[test_idx, ], estimate.variance = TRUE)

  dt_test <- dt_hte[test_idx]
  dt_test[, cate_hat := cate_pred$predictions]
  dt_test[, cate_se := sqrt(cate_pred$variance.estimates)]

  cat(sprintf("  CATE mean: %.2f (sd: %.2f)\n",
              mean(dt_test$cate_hat), sd(dt_test$cate_hat)))
  cat(sprintf("  CATE range: [%.2f, %.2f]\n",
              min(dt_test$cate_hat), max(dt_test$cate_hat)))

  # --- Variable importance ---
  var_imp <- variable_importance(iv_forest)
  var_imp_df <- data.table(
    variable = x_cols,
    importance = as.numeric(var_imp)
  )[order(-importance)]

  cat("\n  Variable importance:\n")
  print(var_imp_df)
  fwrite(var_imp_df, file.path(OUT, "tables", "var_importance.csv"))

  # --- Best linear projection ---
  blp <- best_linear_projection(iv_forest, X[train_idx, ])
  writeLines(capture.output(print(blp)),
             file.path(OUT, "tables", "blp_summary.txt"))
  cat("  BLP summary saved\n")

  # --- CATE by subgroups ---
  cat("\n  CATE by subgroups:\n")

  # By poverty
  if ("POVCAT" %in% names(dt_test)) {
    cate_pov <- dt_test[, .(
      mean_cate = mean(cate_hat), se = sd(cate_hat) / sqrt(.N), n = .N
    ), by = POVCAT][order(POVCAT)]
    cat("  By POVCAT:\n")
    print(cate_pov)
    fwrite(cate_pov, file.path(OUT, "tables", "cate_by_povcat.csv"))
  }

  # By era
  cate_era <- dt_test[, .(
    mean_cate = mean(cate_hat), se = sd(cate_hat) / sqrt(.N), n = .N
  ), by = era]
  cat("  By era:\n")
  print(cate_era)

  # By health status
  if ("RTHLTH42" %in% names(dt_test)) {
    cate_health <- dt_test[, .(
      mean_cate = mean(cate_hat), se = sd(cate_hat) / sqrt(.N), n = .N
    ), by = .(poor_health = RTHLTH42 >= 4)]
    cat("  By health status:\n")
    print(cate_health)
    fwrite(cate_health, file.path(OUT, "tables", "cate_by_health.csv"))
  }

  # Save CATE predictions
  fwrite(dt_test[, .(DUPERSID, YEAR, cate_hat, cate_se)],
         file.path(OUT, "tables", "cate_predictions.csv"))

  # --- CATE distribution plot ---
  png(file.path(OUT, "figures", "cate_distribution.png"),
      width = 900, height = 500)
  hist(dt_test$cate_hat, breaks = 50, col = "steelblue", border = "white",
       main = sprintf("CATE Distribution: %s (Pooled 2002-2017)", PRIMARY_OUTCOME),
       xlab = "Estimated CATE (effect of Medicare on OOP spending)")
  abline(v = 0, col = "red", lwd = 2, lty = 2)
  abline(v = mean(dt_test$cate_hat), col = "darkgreen", lwd = 2)
  legend("topright", c("Zero", "Mean CATE"),
         col = c("red", "darkgreen"), lwd = 2, lty = c(2, 1))
  dev.off()

  # Save model
  saveRDS(iv_forest, file.path(OUT, "models", "iv_forest.rds"))
  cat("\n  -> GRF complete, model saved\n")

  # ============================================================================
  # STEP 9: POLICY TARGETING — Policy Tree
  # ============================================================================

  cat("\n")
  cat(strrep("=", 80), "\n")
  cat("STEP 9: POLICY TARGETING — Policy Tree\n")
  cat(strrep("=", 80), "\n\n")

  # Predict CATE on train set for policy learning
  cate_train <- predict(iv_forest, X[train_idx, ])$predictions

  # Policy covariates (interpretable subset)
  POLICY_VARS <- intersect(
    c("SEX", "POVCAT", "RTHLTH42", "REGION", "EMPST42",
      "chronic_count", "EDUCYR", "post_aca"),
    x_cols
  )
  X_policy_train <- X[train_idx, POLICY_VARS, drop = FALSE]

  # Gamma: higher = more benefit from Medicare
  # For OOP spending: negative CATE = Medicare reduces OOP = good
  Gamma <- -cate_train

  # Remove NAs
  valid_pol <- !is.na(Gamma)
  X_policy_train <- X_policy_train[valid_pol, , drop = FALSE]
  Gamma <- Gamma[valid_pol]

  cat(sprintf("  Policy training sample: %d obs\n", length(Gamma)))
  cat(sprintf("  Policy covariates: %s\n", paste(POLICY_VARS, collapse = ", ")))

  # --- Depth 2 tree (more stable) ---
  cat("\n  Fitting depth-2 policy tree...\n")
  tryCatch({
    ptree2 <- policy_tree(X_policy_train, cbind(Gamma, -Gamma), depth = 2)
    cat("  Policy tree (depth 2):\n")
    print(ptree2)

    # Evaluate on test set
    X_policy_test <- X[test_idx, POLICY_VARS, drop = FALSE]
    action2 <- predict(ptree2, X_policy_test)

    cate_test <- cate_pred$predictions
    targeted2 <- mean(cate_test[action2 == 1])
    uniform2 <- mean(cate_test)

    cat(sprintf("\n  Depth-2 results:\n"))
    cat(sprintf("    Targeted value: %.2f\n", targeted2))
    cat(sprintf("    Uniform value:  %.2f\n", uniform2))
    cat(sprintf("    Improvement:    %.2f\n", targeted2 - uniform2))
    cat(sprintf("    Treated share:  %.1f%%\n", 100 * mean(action2 == 1)))

    saveRDS(ptree2, file.path(OUT, "models", "policy_tree_d2.rds"))
  }, error = function(e) {
    cat(sprintf("  Depth-2 error: %s\n", e$message))
  })

  # --- Depth 3 tree (more granular) ---
  cat("\n  Fitting depth-3 policy tree...\n")
  tryCatch({
    ptree3 <- hybrid_policy_tree(X_policy_train, cbind(Gamma, -Gamma),
                                  depth = 3)
    cat("  Policy tree (depth 3, hybrid):\n")
    print(ptree3)

    action3 <- predict(ptree3, X_policy_test)
    targeted3 <- mean(cate_test[action3 == 1])

    cat(sprintf("\n  Depth-3 results:\n"))
    cat(sprintf("    Targeted value: %.2f\n", targeted3))
    cat(sprintf("    Improvement:    %.2f\n", targeted3 - uniform2))
    cat(sprintf("    Treated share:  %.1f%%\n", 100 * mean(action3 == 1)))

    saveRDS(ptree3, file.path(OUT, "models", "policy_tree_d3.rds"))
  }, error = function(e) {
    cat(sprintf("  Depth-3 error: %s\n", e$message))
  })

  # --- Policy value curve ---
  cat("\n  Computing policy value curve...\n")
  budget_levels <- seq(0.05, 0.50, by = 0.05)
  pv <- sapply(budget_levels, function(k) {
    threshold <- quantile(-cate_test, 1 - k)
    treated <- (-cate_test) >= threshold
    if (sum(treated) == 0) return(NA_real_)
    mean(cate_test[treated])
  })

  pv_dt <- data.table(
    budget_k = budget_levels,
    targeted_value = pv,
    uniform_value = uniform2
  )
  fwrite(pv_dt, file.path(OUT, "tables", "policy_value_curve.csv"))

  # Plot
  png(file.path(OUT, "figures", "policy_value_curve.png"),
      width = 900, height = 500)
  plot(budget_levels, pv, type = "b", col = "steelblue", lwd = 2, pch = 19,
       xlab = "Budget share (K)", ylab = "Policy value (avg CATE on OOP)",
       main = "Policy Value Curve: Medicare@65 Targeting")
  abline(h = uniform2, col = "red", lty = 2, lwd = 2)
  legend("bottomright", c("Targeted", "Uniform"),
         col = c("steelblue", "red"), lwd = 2, lty = c(1, 2))
  dev.off()

  cat("  -> Policy targeting complete\n")

  # ============================================================================
  # STEP 10: Run HTE for ALL outcomes (not just primary)
  # ============================================================================

  cat("\n")
  cat(strrep("=", 80), "\n")
  cat("STEP 10: HTE for all outcomes\n")
  cat(strrep("=", 80), "\n\n")

  hte_all_outcomes <- intersect(
    c("TOTSLF", "log_totslf", "cat_oop10",
      "y_dlayca42", "y_afrdca42",
      "OBTOTV", "ERTOT", "y_haveus"),
    OUTCOMES
  )

  hte_summary <- list()

  for (out_var in hte_all_outcomes) {
    cat(sprintf("  HTE for %s...\n", out_var))

    Y_out <- dt_hte[[out_var]]
    if (all(is.na(Y_out[train_idx]))) {
      cat("    Skipping (all NA)\n")
      next
    }

    tryCatch({
      # Train forest for this outcome
      iv_out <- instrumental_forest(
        X = X[train_idx, ], Y = Y_out[train_idx],
        W = W[train_idx], Z = Z[train_idx],
        sample.weights = dt_hte$PERWT[train_idx],
        num.trees = 1000, honesty = TRUE
      )

      # Predict on test
      cate_out <- predict(iv_out, X[test_idx, ])$predictions

      hte_summary[[out_var]] <- data.table(
        outcome = out_var,
        mean_cate = mean(cate_out),
        sd_cate = sd(cate_out),
        min_cate = min(cate_out),
        max_cate = max(cate_out),
        pct_negative = 100 * mean(cate_out < 0)
      )

      cat(sprintf("    Mean CATE: %.4f (sd: %.4f)\n",
                  mean(cate_out), sd(cate_out)))

    }, error = function(e) {
      cat(sprintf("    Error: %s\n", e$message))
    })
  }

  if (length(hte_summary) > 0) {
    hte_all_dt <- rbindlist(hte_summary)
    fwrite(hte_all_dt, file.path(OUT, "tables", "hte_all_outcomes.csv"))
    cat("\n  HTE summary across outcomes:\n")
    print(hte_all_dt)
  }

} else {
  cat("  [SKIP] Too few complete cases for HTE\n")
}

# ==============================================================================
# SUMMARY
# ==============================================================================

cat("\n")
cat(strrep("=", 80), "\n")
cat("ANALYSIS COMPLETE\n")
cat(strrep("=", 80), "\n\n")

cat(sprintf("Completed: %s\n", Sys.time()))
cat(sprintf("Output directory: %s\n\n", OUT))

cat("Output files:\n")
for (f in list.files(OUT, recursive = TRUE)) {
  cat(sprintf("  %s\n", f))
}

sink()

cat(sprintf("\n✓ Full log saved to: %s\n", LOG))
