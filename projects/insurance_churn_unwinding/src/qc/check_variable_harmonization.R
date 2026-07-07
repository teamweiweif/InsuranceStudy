# MEPS FYC Multi-Year Variable Harmonization Report
# Systematic check of variable availability, naming, coding, and distribution
# across all years (1996-2023)

library(data.table)
library(haven)

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

OUTPUT_DIR <- project_path("outputs", "harmonization_report")
DATA_DIR <- project_path("data", "intermediate", "fyc_all_years")
ensure_dir(OUTPUT_DIR)

YEARS <- 1996:2023

cat("MEPS FYC Multi-Year Variable Harmonization Report\n")
cat(paste(rep("=", 80), collapse=""), "\n\n")

# ============================================================================
# Step 1: Scan all years for variable names (raw, before harmonization)
# ============================================================================

cat("Step 1: Scanning raw variable names across all years...\n")

raw_vars_by_year <- list()

for (yr in YEARS) {
  dta_file <- file.path(DATA_DIR, sprintf("fyc_%d.dta", yr))

  if (!file.exists(dta_file)) {
    cat(sprintf("  %d: MISSING\n", yr))
    next
  }

  tryCatch({
    dt <- as.data.table(read_dta(dta_file))
    all_vars <- toupper(names(dt))
    raw_vars_by_year[[as.character(yr)]] <- all_vars
    cat(sprintf("  %d: %d variables\n", yr, length(all_vars)))
  }, error = function(e) {
    cat(sprintf("  %d: ERROR - %s\n", yr, e$message))
  })
}

cat(sprintf("\nTotal years scanned: %d\n\n", length(raw_vars_by_year)))

# ============================================================================
# Step 2: Define target variables for pooled analysis
# ============================================================================

cat("Step 2: Defining target variables for pooled analysis...\n\n")

# Core variables needed for RD + HTE + Policy Learning
TARGET_VARS <- list(
  # IDs
  ids = c("DUPERSID", "PANEL"),

  # Survey design
  survey = c("PERWT", "VARSTR", "VARPSU"),

  # Age/DOB (for RD)
  age = c("DOBMM", "DOBYY", "AGE", "ENDRFM42", "ENDRFY42"),

  # Demographics (for HTE)
  demographics = c("SEX", "RACETHX", "HISPANX", "RACEV1X", "RACEV2X",
                   "MARRY", "EDUCYR", "HIDEG", "REGION",
                   "BORNUSA", "YRSINUS", "HWELLSPK"),

  # Income/poverty (for HTE)
  income = c("FAMINC", "TTLP", "POVCAT", "POVLEV"),

  # Employment
  employment = c("EMPST42", "EMPST31", "EMPST53"),

  # Insurance summary
  insurance_summary = c("INSCOV", "UNINS", "PRVEV", "MCREV", "MCDEV",
                        "PRIV", "MCARE", "MCAID", "MCRPHO"),

  # Monthly insurance (for churn)
  insurance_monthly = c("INS_M01", "INS_M12", "MCR_M01", "MCR_M12",
                        "PRI_M01", "PRI_M12"),

  # Access/cost barriers (PRIMARY OUTCOMES)
  access = c("DLAYCA42", "AFRDCA42", "DLAYPM42", "AFRDPM42",
             "MDDLAY42", "MDUNAB42", "PMDLAY42", "PMUNAB42",  # old names
             "HAVEUS42"),

  # Spending (PRIMARY OUTCOMES)
  spending = c("TOTEXP", "TOTSLF", "TOTMCR", "TOTMCD", "TOTPRV",
               "RXEXP", "RXSLF"),

  # Utilization
  utilization = c("OBTOTV", "ERTOT", "IPDIS", "RXTOT"),

  # Medical bill stress
  bill_stress = c("PROBPY42", "PYUNBL42", "CRFMPY42"),

  # Health status
  health = c("RTHLTH42", "MNHLTH42", "PCS42", "MCS42",
             "VPCS42", "VMCS42"),  # VR-12 versions

  # Chronic conditions
  chronic = c("HIBPDX", "CHDDX", "STRKDX", "DIABDX", "DIABDX_M18",
              "ARTHDX", "CANCERDX", "ASTHDX", "EMPHDX", "CHOLDX")
)

# Flatten to unique list
all_target_vars <- unique(unlist(TARGET_VARS))
cat(sprintf("Target variables defined: %d unique variables\n\n",
            length(all_target_vars)))

# ============================================================================
# Step 3: Fuzzy matching - find variable names across years
# ============================================================================

cat("Step 3: Fuzzy matching variable names across years...\n")
cat("(This may take a few minutes...)\n\n")

# For each target variable, find which years have it (exact or with suffix)
var_availability <- data.table(
  variable = character(),
  category = character(),
  year = integer(),
  raw_name = character(),
  match_type = character()
)

for (cat_name in names(TARGET_VARS)) {
  cat(sprintf("  Category: %s\n", cat_name))

  for (target_var in TARGET_VARS[[cat_name]]) {

    for (yr in names(raw_vars_by_year)) {
      raw_vars <- raw_vars_by_year[[yr]]

      # Try exact match
      if (target_var %in% raw_vars) {
        var_availability <- rbind(var_availability, data.table(
          variable = target_var,
          category = cat_name,
          year = as.integer(yr),
          raw_name = target_var,
          match_type = "exact"
        ))
        next
      }

      # Try with year suffix (e.g., TOTSLF22, TOTSLF08)
      yy <- sprintf("%02d", as.integer(yr) %% 100)
      suffixes <- c(yy, paste0(yy, "X"), paste0(yy, "F"))

      for (suf in suffixes) {
        pattern_var <- paste0(target_var, suf)
        if (pattern_var %in% raw_vars) {
          var_availability <- rbind(var_availability, data.table(
            variable = target_var,
            category = cat_name,
            year = as.integer(yr),
            raw_name = pattern_var,
            match_type = paste0("suffix_", suf)
          ))
          break
        }
      }
    }
  }
}

cat(sprintf("\nMatched %d variable-year combinations\n\n",
            nrow(var_availability)))

# Save availability matrix
fwrite(var_availability,
       file.path(OUTPUT_DIR, "variable_availability.csv"))

# ============================================================================
# Step 4: Availability summary by variable
# ============================================================================

cat("Step 4: Variable availability summary...\n\n")

avail_summary <- var_availability[, .(
  n_years = .N,
  years_available = paste(sort(unique(year)), collapse=","),
  pct_years = round(100 * .N / length(YEARS), 1)
), by = .(variable, category)]

avail_summary <- avail_summary[order(-n_years)]

# Print summary
cat("Variables available in ALL years (100%):\n")
print(avail_summary[pct_years == 100])

cat("\nVariables available in MOST years (>=80%):\n")
print(avail_summary[pct_years >= 80 & pct_years < 100])

cat("\nVariables with LIMITED availability (<80%):\n")
print(avail_summary[pct_years < 80])

fwrite(avail_summary,
       file.path(OUTPUT_DIR, "availability_summary.csv"))
