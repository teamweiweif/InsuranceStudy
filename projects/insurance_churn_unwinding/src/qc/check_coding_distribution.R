# Part 2: Check coding consistency and distributions
# For variables that exist across multiple years, check if coding is consistent

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

source_project("src", "features", "harmonize_variables.R")
source_project("src", "features", "derive_features.R")

OUTPUT_DIR <- project_path("outputs", "harmonization_report")

YEARS <- 1996:2023

cat("\n")
cat(paste(rep("=", 80), collapse=""), "\n")
cat("Part 2: Coding Consistency and Distribution Checks\n")
cat(paste(rep("=", 80), collapse=""), "\n\n")

# ============================================================================
# Step 5: Check coding consistency for key variables
# ============================================================================

cat("Step 5: Checking coding consistency...\n\n")

# Key variables to check coding
KEY_VARS_TO_CHECK <- c(
  "SEX", "INSCOV", "UNINS", "PRVEV", "MCREV", "MCDEV",
  "DLAYCA42", "AFRDCA42", "HAVEUS42",
  "POVCAT", "REGION", "EMPST42"
)

coding_report <- list()

for (var in KEY_VARS_TO_CHECK) {
  cat(sprintf("  Checking %s...\n", var))

  var_coding <- data.table(
    year = integer(),
    n_obs = integer(),
    n_valid = integer(),
    unique_values = character(),
    min_val = numeric(),
    max_val = numeric(),
    mean_val = numeric(),
    na_count = integer()
  )

  for (yr in YEARS) {
    tryCatch({
      dt <- harmonize_fyc(yr)

      if (!(var %in% names(dt))) next

      x <- dt[[var]]
      valid_x <- x[!is.na(x) & x >= 0]  # Exclude negative (missing codes)

      if (length(valid_x) == 0) next

      unique_vals <- sort(unique(valid_x))
      unique_str <- if (length(unique_vals) <= 10) {
        paste(unique_vals, collapse=",")
      } else {
        sprintf("%d unique values", length(unique_vals))
      }

      var_coding <- rbind(var_coding, data.table(
        year = yr,
        n_obs = nrow(dt),
        n_valid = length(valid_x),
        unique_values = unique_str,
        min_val = min(valid_x, na.rm=TRUE),
        max_val = max(valid_x, na.rm=TRUE),
        mean_val = mean(valid_x, na.rm=TRUE),
        na_count = sum(is.na(x) | x < 0)
      ))

    }, error = function(e) {
      # Skip year if error
    })
  }

  if (nrow(var_coding) > 0) {
    coding_report[[var]] <- var_coding

    # Check if coding is consistent
    unique_codings <- unique(var_coding$unique_values)

    if (length(unique_codings) == 1) {
      cat(sprintf("    ✓ Consistent coding across %d years\n",
                  nrow(var_coding)))
    } else {
      cat(sprintf("    ✗ INCONSISTENT coding across years!\n"))
      cat(sprintf("      Found %d different coding schemes:\n",
                  length(unique_codings)))
      for (uc in unique_codings) {
        years_with_coding <- var_coding[unique_values == uc]$year
        cat(sprintf("        %s: years %s\n",
                    uc, paste(years_with_coding, collapse=",")))
      }
    }

    # Save detailed report
    fwrite(var_coding,
           file.path(OUTPUT_DIR, sprintf("coding_%s.csv", var)))
  } else {
    cat(sprintf("    ! No data found\n"))
  }
}

cat("\n")

# ============================================================================
# Step 6: Distribution checks for continuous variables
# ============================================================================

cat("Step 6: Distribution checks for continuous variables...\n\n")

CONTINUOUS_VARS <- c("TOTSLF", "TOTEXP", "RXSLF", "OBTOTV", "ERTOT")

dist_report <- list()

for (var in CONTINUOUS_VARS) {
  cat(sprintf("  Checking %s...\n", var))

  var_dist <- data.table(
    year = integer(),
    n_valid = integer(),
    mean = numeric(),
    median = numeric(),
    sd = numeric(),
    p25 = numeric(),
    p75 = numeric(),
    p95 = numeric(),
    max = numeric(),
    zeros_pct = numeric()
  )

  for (yr in YEARS) {
    tryCatch({
      dt <- harmonize_fyc(yr)

      if (!(var %in% names(dt))) next

      x <- dt[[var]]
      valid_x <- x[!is.na(x) & x >= 0]

      if (length(valid_x) == 0) next

      var_dist <- rbind(var_dist, data.table(
        year = yr,
        n_valid = length(valid_x),
        mean = mean(valid_x),
        median = median(valid_x),
        sd = sd(valid_x),
        p25 = quantile(valid_x, 0.25),
        p75 = quantile(valid_x, 0.75),
        p95 = quantile(valid_x, 0.95),
        max = max(valid_x),
        zeros_pct = 100 * mean(valid_x == 0)
      ))

    }, error = function(e) {
      # Skip
    })
  }

  if (nrow(var_dist) > 0) {
    dist_report[[var]] <- var_dist

    # Check for outliers or trend breaks
    mean_trend <- var_dist$mean
    if (length(mean_trend) > 5) {
      # Check if mean changes dramatically
      mean_change <- diff(mean_trend) / mean_trend[-length(mean_trend)]
      big_jumps <- which(abs(mean_change) > 0.5)  # >50% change

      if (length(big_jumps) > 0) {
        cat(sprintf("    ⚠ Large jumps in mean detected:\n"))
        for (j in big_jumps) {
          cat(sprintf("      %d→%d: %.0f → %.0f (%.0f%% change)\n",
                      var_dist$year[j], var_dist$year[j+1],
                      var_dist$mean[j], var_dist$mean[j+1],
                      100 * mean_change[j]))
        }
      } else {
        cat(sprintf("    ✓ Stable distribution across %d years\n",
                    nrow(var_dist)))
      }
    }

    fwrite(var_dist,
           file.path(OUTPUT_DIR, sprintf("distribution_%s.csv", var)))
  }
}

cat("\n")

# ============================================================================
# Step 7: Generate summary report
# ============================================================================

cat("Step 7: Generating summary report...\n\n")

sink(file.path(OUTPUT_DIR, "HARMONIZATION_SUMMARY.txt"))

cat("MEPS FYC Multi-Year Variable Harmonization Report\n")
cat(paste(rep("=", 80), collapse=""), "\n")
cat(sprintf("Generated: %s\n", Sys.time()))
cat(sprintf("Years covered: %d-%d (%d years)\n\n",
            min(YEARS), max(YEARS), length(YEARS)))

cat("SUMMARY OF FINDINGS\n")
cat(paste(rep("-", 80), collapse=""), "\n\n")

cat("1. VARIABLE AVAILABILITY\n")
cat("   See: variable_availability.csv\n")
cat("   See: availability_summary.csv\n\n")

cat("2. CODING CONSISTENCY\n")
for (var in names(coding_report)) {
  cr <- coding_report[[var]]
  unique_codings <- unique(cr$unique_values)
  if (length(unique_codings) == 1) {
    cat(sprintf("   ✓ %s: Consistent\n", var))
  } else {
    cat(sprintf("   ✗ %s: INCONSISTENT (%d schemes)\n",
                var, length(unique_codings)))
  }
}
cat("\n")

cat("3. DISTRIBUTION STABILITY\n")
for (var in names(dist_report)) {
  dr <- dist_report[[var]]
  cat(sprintf("   %s: mean range [%.0f, %.0f]\n",
              var, min(dr$mean), max(dr$mean)))
}
cat("\n")

cat("RECOMMENDATIONS FOR POOLED ANALYSIS\n")
cat(paste(rep("-", 80), collapse=""), "\n\n")

cat("1. Variables safe to pool (consistent coding + stable distribution):\n")
cat("   - Check individual variable reports\n\n")

cat("2. Variables needing recoding:\n")
cat("   - Check coding_*.csv files for inconsistencies\n\n")

cat("3. Variables needing inflation adjustment:\n")
cat("   - All spending variables (TOTSLF, TOTEXP, RXSLF, etc.)\n")
cat("   - Use CPI-U medical care component\n\n")

cat("4. Variables with limited availability:\n")
cat("   - Check availability_summary.csv for <80% coverage\n")
cat("   - Consider dropping or using only subset of years\n\n")

sink()

cat("✓ Summary report saved to:\n")
cat(sprintf("  %s/HARMONIZATION_SUMMARY.txt\n", OUTPUT_DIR))
cat("\n")
cat(paste(rep("=", 80), collapse=""), "\n")
cat("Harmonization check complete!\n")
cat(paste(rep("=", 80), collapse=""), "\n")
