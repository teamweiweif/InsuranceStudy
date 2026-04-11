# MEPS FYC Derived Features
# Computes: age_months, churn indicators, catastrophic OOP, chronic count, etc.
# Depends on: harmonize_variables.R

if (!exists("project_path", mode = "function")) {
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
}

library(data.table)

#' Derive all core features from harmonized FYC data
#' @param dt data.table from harmonize_fyc()
#' @return dt with additional derived columns
derive_features <- function(dt) {

  cat("Deriving features...\n")

  # --- Age in months ---
  # For RD: use round-42 reference end date if available, else 12/31/YEAR
  dt[, ref_month := fifelse(!is.na(ENDRFM42) & ENDRFM42 > 0, as.numeric(ENDRFM42), 12)]
  dt[, ref_year  := fifelse(!is.na(ENDRFY42) & ENDRFY42 > 0, as.numeric(ENDRFY42), as.numeric(YEAR))]
  dt[, age_months := as.integer((ref_year - DOBYY) * 12 + (ref_month - DOBMM))]
  # Clean: set impossible values to NA
  dt[age_months < 0 | age_months > 1500, age_months := NA_integer_]

  # RD assignment variables
  dt[, z_age65 := as.integer(age_months >= 780L)]  # 65 * 12
  dt[, z_age26 := as.integer(age_months >= 312L)]  # 26 * 12
  dt[, age_months_c65 := age_months - 780L]  # centered at 65
  dt[, age_months_c26 := age_months - 312L]  # centered at 26

  # --- Monthly insurance: churn metrics ---
  ins_cols <- paste0("INS_M", sprintf("%02d", 1:12))
  existing_ins <- intersect(ins_cols, names(dt))

  if (length(existing_ins) > 0) {
    # Months insured (count months with value == 1)
    dt[, months_insured := rowSums(.SD == 1, na.rm = TRUE), .SDcols = existing_ins]
    dt[, months_uninsured := rowSums(.SD == 2, na.rm = TRUE), .SDcols = existing_ins]

    # Number of switches (insured <-> uninsured transitions)
    dt[, num_switches := {
      n <- 0L
      for (i in 2:length(existing_ins)) {
        prev <- .SD[[i-1]]
        curr <- .SD[[i]]
        n <- n + as.integer(!is.na(prev) & !is.na(curr) & prev != curr)
      }
      n
    }, .SDcols = existing_ins]

    # High churn indicator
    dt[, t_high_churn := as.integer(num_switches >= 2L)]
  }

  # --- Medicare treatment indicators ---
  mcr_cols <- paste0("MCR_M", sprintf("%02d", 1:12))
  existing_mcr <- intersect(mcr_cols, names(dt))

  if (length(existing_mcr) > 0) {
    dt[, months_medicare := rowSums(.SD == 1, na.rm = TRUE), .SDcols = existing_mcr]
  }

  # Medicare treatment for RD
  dt[, t_medicare_any := as.integer(!is.na(MCREV) & MCREV == 1)]

  # --- Dependent-like ESI proxy (for age-26 RD) ---
  peg_cols <- paste0("PEG_M", sprintf("%02d", 1:12))
  hpe_cols <- paste0("HPE_M", sprintf("%02d", 1:12))

  if (all(c(peg_cols[1], hpe_cols[1]) %in% names(dt))) {
    # dep_esi = covered by ESI but NOT policyholder
    for (m in 1:12) {
      dep_col <- sprintf("DEP_ESI_M%02d", m)
      peg <- peg_cols[m]
      hpe <- hpe_cols[m]
      if (peg %in% names(dt) & hpe %in% names(dt)) {
        dt[, (dep_col) := as.integer(.SD[[1]] == 1 & .SD[[2]] != 1),
           .SDcols = c(peg, hpe)]
      }
    }
    dep_cols <- paste0("DEP_ESI_M", sprintf("%02d", 1:12))
    existing_dep <- intersect(dep_cols, names(dt))
    if (length(existing_dep) > 0) {
      dt[, months_dep_esi := rowSums(.SD, na.rm = TRUE), .SDcols = existing_dep]
      dt[, t_dep_esi_any := as.integer(months_dep_esi > 0)]
    }
  }

  # --- Catastrophic OOP ---
  # cat_oop10 = OOP > 10% of family income
  dt[, cat_oop10 := as.integer(TOTSLF > 0.10 * pmax(FAMINC, 1, na.rm = TRUE))]
  dt[is.na(TOTSLF) | is.na(FAMINC), cat_oop10 := NA_integer_]
  # Also 5% and 20% thresholds
  dt[, cat_oop05 := as.integer(TOTSLF > 0.05 * pmax(FAMINC, 1, na.rm = TRUE))]
  dt[is.na(TOTSLF) | is.na(FAMINC), cat_oop05 := NA_integer_]
  dt[, cat_oop20 := as.integer(TOTSLF > 0.20 * pmax(FAMINC, 1, na.rm = TRUE))]
  dt[is.na(TOTSLF) | is.na(FAMINC), cat_oop20 := NA_integer_]

  # --- Chronic condition count ---
  chronic_vars <- c("HIBPDX", "CHDDX", "STRKDX", "DIABDX", "ARTHDX", "CANCERDX")
  existing_chronic <- intersect(chronic_vars, names(dt))
  if (length(existing_chronic) > 0) {
    dt[, chronic_count := rowSums(.SD == 1, na.rm = TRUE), .SDcols = existing_chronic]
  }

  # --- FPL bins ---
  dt[, fpl_bin := fcase(
    POVCAT == 1, "Poor (<100%)",
    POVCAT == 2, "Near-poor (100-125%)",
    POVCAT == 3, "Low income (125-200%)",
    POVCAT == 4, "Middle income (200-400%)",
    POVCAT == 5, "High income (>400%)",
    default = NA_character_
  )]

  # --- Binary outcome recodes (MEPS uses 1=Yes, 2=No, negative=missing) ---
  binary_recode <- function(x) {
    fifelse(x == 1, 1L, fifelse(x == 2, 0L, NA_integer_))
  }

  binary_vars <- c("DLAYCA42", "AFRDCA42", "DLAYPM42", "AFRDPM42",
                    "PROBPY42", "PYUNBL42")
  for (v in intersect(binary_vars, names(dt))) {
    new_name <- paste0("y_", tolower(v))
    dt[, (new_name) := binary_recode(get(v))]
  }

  # HAVEUS42: 1=Yes, 2=No -> binary
  if ("HAVEUS42" %in% names(dt)) {
    dt[, y_haveus := binary_recode(HAVEUS42)]
  }

  # Log spending
  dt[, log_totslf := log1p(pmax(TOTSLF, 0, na.rm = TRUE))]
  dt[, log_totexp := log1p(pmax(TOTEXP, 0, na.rm = TRUE))]

  cat(sprintf("  -> %d total columns after feature derivation\n", ncol(dt)))
  return(dt)
}

# Test
if (sys.nframe() == 0) {
  if (!exists("harmonize_fyc", mode = "function")) {
    source_project("src", "features", "harmonize_variables.R")
  }
  dt <- harmonize_fyc(2021)
  dt <- derive_features(dt)

  cat("\nDerived feature summary:\n")
  cat(sprintf("  age_months: %d non-NA (range %d-%d)\n",
              sum(!is.na(dt$age_months)),
              min(dt$age_months, na.rm=TRUE),
              max(dt$age_months, na.rm=TRUE)))
  cat(sprintf("  z_age65: %d at/above 65\n", sum(dt$z_age65 == 1, na.rm=TRUE)))
  cat(sprintf("  months_insured mean: %.1f\n", mean(dt$months_insured, na.rm=TRUE)))
  cat(sprintf("  cat_oop10 rate: %.1f%%\n", 100*mean(dt$cat_oop10, na.rm=TRUE)))
  cat(sprintf("  chronic_count mean: %.2f\n", mean(dt$chronic_count, na.rm=TRUE)))
  cat(sprintf("  y_dlayca42 rate: %.1f%%\n", 100*mean(dt$y_dlayca42, na.rm=TRUE)))
}
