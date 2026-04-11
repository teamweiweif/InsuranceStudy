# Bootstrap all R packages used by the active pooled analysis workflow.

options(repos = c(CRAN = "https://cloud.r-project.org"))
options(timeout = 600)

required_packages <- c(
  "data.table", "arrow", "haven", "dplyr", "tidyr", "purrr",
  "rdrobust", "rddensity",
  "grf", "ranger", "xgboost", "glmnet",
  "policytree",
  "survey",
  "fixest", "sandwich", "lmtest",
  "ggplot2", "yaml"
)

mirrors <- c(
  "https://cloud.r-project.org",
  "https://cran.rstudio.com",
  "https://cran.r-project.org"
)

if (identical(Sys.getenv("USINS_SMOKE_TEST"), "1")) {
  cat("Smoke test OK: bootstrap_packages.R\n")
  quit(save = "no", status = 0)
}

install_with_retry <- function(pkg, mirrors, max_attempts = 3) {
  for (mirror in mirrors) {
    for (attempt in seq_len(max_attempts)) {
      cat(sprintf("Installing %s from %s (attempt %d/%d)...\n",
                  pkg, mirror, attempt, max_attempts))

      ok <- tryCatch({
        install.packages(pkg, repos = mirror, quiet = FALSE)
        requireNamespace(pkg, quietly = TRUE)
      }, error = function(e) {
        cat(sprintf("  Error: %s\n", e$message))
        FALSE
      }, warning = function(w) {
        cat(sprintf("  Warning: %s\n", w$message))
        FALSE
      })

      if (ok) {
        cat(sprintf("  Installed %s successfully\n", pkg))
        return(TRUE)
      }

      if (attempt < max_attempts) {
        Sys.sleep(5)
      }
    }
  }

  cat(sprintf("  Failed to install %s after retries\n", pkg))
  FALSE
}

cat("Bootstrapping packages for the US Insurance Project...\n\n")

for (pkg in required_packages) {
  if (requireNamespace(pkg, quietly = TRUE)) {
    cat(sprintf("✓ %-15s already installed (%s)\n",
                pkg, packageVersion(pkg)))
  } else {
    install_with_retry(pkg, mirrors)
  }
}

cat("\nVerification\n")
cat(paste(rep("=", 60), collapse = ""), "\n")

verify_ok <- 0L
for (pkg in required_packages) {
  if (requireNamespace(pkg, quietly = TRUE)) {
    cat(sprintf("✓ %-15s %s\n", pkg, packageVersion(pkg)))
    verify_ok <- verify_ok + 1L
  } else {
    cat(sprintf("✗ %-15s missing\n", pkg))
  }
}

cat(sprintf("\nReady packages: %d/%d\n", verify_ok, length(required_packages)))

if (requireNamespace("ranger", quietly = TRUE)) {
  cat("Testing ranger on iris... ")
  tryCatch({
    library(ranger)
    ranger(Species ~ ., data = iris, num.trees = 10)
    cat("OK\n")
  }, error = function(e) {
    cat(sprintf("ERROR: %s\n", e$message))
  })
}

if (requireNamespace("xgboost", quietly = TRUE)) {
  cat("Testing xgboost on iris... ")
  tryCatch({
    library(xgboost)
    X <- as.matrix(iris[, 1:4])
    y <- as.numeric(iris$Species) - 1
    xgboost(
      data = X, label = y, max_depth = 2, eta = 1, nthread = 2, nrounds = 2,
      objective = "multi:softmax", num_class = 3, verbose = 0
    )
    cat("OK\n")
  }, error = function(e) {
    cat(sprintf("ERROR: %s\n", e$message))
  })
}
