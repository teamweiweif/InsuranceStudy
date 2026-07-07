# Master script: Run all harmonization checks
# This generates a consistency report across MEPS FYC years 1996-2023.

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

OUTPUT_DIR <- project_path("outputs", "harmonization_report")
ensure_dir(OUTPUT_DIR)

log_file <- file.path(
  OUTPUT_DIR,
  sprintf("harmonization_log_%s.txt", format(Sys.time(), "%Y%m%d_%H%M%S"))
)

if (identical(Sys.getenv("USINS_SMOKE_TEST"), "1")) {
  cat("Smoke test OK: run_harmonization_checks.R\n")
  cat(sprintf("Project root: %s\n", project_root()))
  cat(sprintf("Output directory: %s\n", OUTPUT_DIR))
  quit(save = "no", status = 0)
}

log_msg <- function(msg) {
  cat(msg)
  cat(msg, file = log_file, append = TRUE)
}

log_msg("MEPS FYC Multi-Year Harmonization Check\n")
log_msg(sprintf("Started: %s\n", Sys.time()))
log_msg(paste(rep("=", 80), collapse = ""))
log_msg("\n\n")

log_msg("This will check:\n")
log_msg("  1. Variable name availability across years\n")
log_msg("  2. Fuzzy matching for year-suffixed variables\n")
log_msg("  3. Coding consistency (e.g., 1/2 vs 0/1)\n")
log_msg("  4. Distribution stability over time\n")
log_msg("  5. Recommendations for pooled analysis\n\n")
log_msg("Estimated time: 5-10 minutes\n\n")
log_msg("Starting checks...\n\n")

initial_sink <- sink.number()
sink(log_file, append = TRUE, split = TRUE)
on.exit({
  while (sink.number() > initial_sink) sink()
}, add = TRUE)

tryCatch({
  cat("Running Part 1: Variable availability...\n")
  cat(paste(rep("-", 80), collapse = ""), "\n")
  source_project("src", "qc", "check_variable_harmonization.R")

  cat("\n\n")
  cat("Running Part 2: Coding and distribution checks...\n")
  cat(paste(rep("-", 80), collapse = ""), "\n")
  source_project("src", "qc", "check_coding_distribution.R")

  cat("\n\n")
  cat(paste(rep("=", 80), collapse = ""), "\n")
  cat("ALL CHECKS COMPLETE\n")
  cat(paste(rep("=", 80), collapse = ""), "\n\n")

  cat(sprintf("Completed: %s\n\n", Sys.time()))
  cat("Output files saved to:\n")
  cat(sprintf("  %s\n\n", OUTPUT_DIR))

  cat("Key files:\n")
  cat("  - HARMONIZATION_SUMMARY.txt (read this first)\n")
  cat("  - variable_availability.csv\n")
  cat("  - availability_summary.csv\n")
  cat("  - coding_*.csv\n")
  cat("  - distribution_*.csv\n")
  cat(sprintf("  - %s (this run log)\n\n", basename(log_file)))

  cat("Next steps:\n")
  cat("  1. Review HARMONIZATION_SUMMARY.txt\n")
  cat("  2. Identify variables safe to pool\n")
  cat("  3. Update harmonization logic if needed\n")
  cat("  4. Add inflation adjustment for spending variables\n")
  cat("  5. Re-run the pooled analysis\n")
}, error = function(e) {
  cat("\n\nERROR occurred:\n")
  cat(sprintf("  %s\n", e$message))
  cat("  Traceback:\n")
  print(traceback())
})

cat(sprintf("\nComplete log saved to:\n  %s\n", log_file))
