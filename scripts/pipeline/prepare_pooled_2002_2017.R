# ==============================================================================
# Prepare pooled 2002-2017 dataset (run once, save for reuse)
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
  cat("Smoke test OK: prepare_pooled_2002_2017.R\n")
  cat(sprintf("Project root: %s\n", project_root()))
  quit(save = "no", status = 0)
}

library(data.table)
library(haven)
library(arrow)

source_project("src", "features", "harmonize_variables.R")
source_project("src", "features", "derive_features.R")

OUT_FILE <- project_path("data", "derived", "pooled_2002_2017.parquet")
ensure_dir(dirname(OUT_FILE))

cat("Building pooled 2002-2017 dataset...\n\n")

YEARS <- 2002:2017
RD_WINDOW <- 120

all_data <- list()
for (yr in YEARS) {
  cat(sprintf("  %d... ", yr))
  dt <- harmonize_fyc(yr)
  dt <- derive_features(dt)
  dt_rd <- dt[!is.na(age_months_c65) & abs(age_months_c65) <= RD_WINDOW]
  all_data[[as.character(yr)]] <- dt_rd
  cat(sprintf("%d obs\n", nrow(dt_rd)))
}

dt <- rbindlist(all_data, fill = TRUE)
dt[, post_aca := as.integer(YEAR >= 2014)]
dt[, era := fifelse(YEAR < 2014, "pre_aca", "post_aca")]

cat(sprintf("\nPooled: %s obs\n", format(nrow(dt), big.mark = ",")))

write_parquet(dt, OUT_FILE)
cat(sprintf("Saved to: %s\n", OUT_FILE))
cat(sprintf("File size: %.1f MB\n", file.info(OUT_FILE)$size / 1024^2))

cached_rds <- project_path("data", "derived", "pooled_2002_2017.rds")
saveRDS(dt, cached_rds)
cat(sprintf("Also saved as: %s\n", cached_rds))
