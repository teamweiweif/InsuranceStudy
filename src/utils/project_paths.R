# Shared helpers for resolving project-relative paths.

locate_project_root <- function(start = getwd()) {
  current <- normalizePath(start, winslash = "/", mustWork = FALSE)
  if (!dir.exists(current)) current <- dirname(current)

  repeat {
    has_markers <- file.exists(file.path(current, "src", "features", "harmonize_variables.R")) &&
      dir.exists(file.path(current, "data")) &&
      dir.exists(file.path(current, "outputs"))

    if (has_markers) return(current)

    parent <- dirname(current)
    if (identical(parent, current)) {
      stop("Could not locate project root from: ", start)
    }
    current <- parent
  }
}

set_project_root <- function(root = locate_project_root()) {
  root <- normalizePath(root, winslash = "/", mustWork = TRUE)
  options(usins.project_root = root)
  invisible(root)
}

project_root <- function() {
  root <- getOption("usins.project_root")
  if (is.null(root) || !nzchar(root) || !dir.exists(root)) {
    root <- set_project_root(locate_project_root())
  }
  root
}

project_path <- function(..., mustWork = FALSE) {
  path <- file.path(project_root(), ...)
  if (mustWork) {
    normalizePath(path, winslash = "/", mustWork = TRUE)
  } else {
    path
  }
}

ensure_dir <- function(path) {
  dir.create(path, recursive = TRUE, showWarnings = FALSE)
  invisible(path)
}

source_project <- function(...) {
  source(project_path(..., mustWork = TRUE))
}
