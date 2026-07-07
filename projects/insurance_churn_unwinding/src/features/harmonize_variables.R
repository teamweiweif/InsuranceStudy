# MEPS FYC Variable Harmonization
# Maps year-suffixed variables to canonical names across all years
# Usage: source this file, then call harmonize_fyc(year) to get clean data

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

library(haven)
library(data.table)

# Year-to-file-code mapping
FYC_FILE_CODES <- c(
  "1996"="h12", "1997"="h20", "1998"="h28", "1999"="h38",
  "2000"="h50", "2001"="h60", "2002"="h70", "2003"="h79",
  "2004"="h89", "2005"="h97", "2006"="h105", "2007"="h113",
  "2008"="h121", "2009"="h129", "2010"="h138", "2011"="h147",
  "2012"="h155", "2013"="h163", "2014"="h171", "2015"="h181",
  "2016"="h192", "2017"="h201", "2018"="h209", "2019"="h216",
  "2020"="h224", "2021"="h233", "2022"="h243", "2023"="h251"
)

# Two-digit year suffix
yy_suffix <- function(year) {
  sprintf("%02d", year %% 100)
}

# Month abbreviations used in MEPS variable names
MONTH_ABBR <- c("JA","FE","MA","AP","MY","JU","JL","AU","SE","OC","NO","DE")

#' Harmonize a single year of FYC data
#' @param year integer year (1996-2023)
#' @param data_dir path to the unified yearly FYC directory
#' @return data.table with canonical variable names + YEAR column
harmonize_fyc <- function(
    year,
    data_dir = project_path("data", "intermediate", "fyc_all_years")) {

  yy <- yy_suffix(year)

  # Read data
  dta_file <- file.path(data_dir, sprintf("fyc_%d.dta", year))
  if (!file.exists(dta_file)) stop(sprintf("File not found: %s", dta_file))

  dt <- as.data.table(read_dta(dta_file))
  orig_names <- toupper(names(dt))
  names(dt) <- orig_names

  cat(sprintf("Harmonizing %d (%s obs, %s vars)...\n",
              year, format(nrow(dt), big.mark=","), ncol(dt)))

  # Ensure YEAR column
  dt[, YEAR := year]

  # Helper: try to find a variable with year suffix, return NA column if missing
  get_var <- function(base, suffix = yy) {
    varname <- paste0(base, suffix)
    if (varname %in% names(dt)) return(dt[[varname]])
    # Try without suffix
    if (base %in% names(dt)) return(dt[[base]])
    return(rep(NA_real_, nrow(dt)))
  }

  # Build canonical dataset
  out <- data.table(
    # IDs
    DUPERSID = dt[["DUPERSID"]],
    PANEL    = if ("PANEL" %in% names(dt)) dt[["PANEL"]] else NA_integer_,
    YEAR     = year,

    # Survey design
    PERWT    = get_var("PERWT", paste0(yy, "F")),
    VARSTR   = if ("VARSTR" %in% names(dt)) dt[["VARSTR"]] else NA_real_,
    VARPSU   = if ("VARPSU" %in% names(dt)) dt[["VARPSU"]] else NA_real_,

    # Demographics
    AGE      = get_var("AGE", paste0(yy, "X")),
    SEX      = if ("SEX" %in% names(dt)) dt[["SEX"]] else NA_integer_,
    RACETHX  = if ("RACETHX" %in% names(dt)) dt[["RACETHX"]] else NA_integer_,
    HISPANX  = if ("HISPANX" %in% names(dt)) dt[["HISPANX"]] else NA_integer_,
    MARRY    = get_var("MARRY", paste0(yy, "X")),
    REGION   = get_var("REGION", yy),
    EDUCYR   = if ("EDUCYR" %in% names(dt)) dt[["EDUCYR"]] else NA_integer_,
    HIDEG    = if ("HIDEG" %in% names(dt)) dt[["HIDEG"]] else NA_integer_,

    # DOB (for age-in-months)
    DOBMM    = if ("DOBMM" %in% names(dt)) dt[["DOBMM"]] else NA_integer_,
    DOBYY    = if ("DOBYY" %in% names(dt)) dt[["DOBYY"]] else NA_integer_,

    # RD reference dates
    ENDRFM42 = if ("ENDRFM42" %in% names(dt)) dt[["ENDRFM42"]] else NA_integer_,
    ENDRFY42 = if ("ENDRFY42" %in% names(dt)) dt[["ENDRFY42"]] else NA_integer_,

    # Income / poverty
    FAMINC   = get_var("FAMINC", yy),
    TTLP     = get_var("TTLP", paste0(yy, "X")),
    POVCAT   = get_var("POVCAT", yy),
    POVLEV   = get_var("POVLEV", yy)
  )

  # Insurance summary
  out[, INSCOV   := get_var("INSCOV", yy)]
  out[, UNINS    := get_var("UNINS", yy)]
  out[, PRVEV    := get_var("PRVEV", yy)]
  out[, MCREV    := get_var("MCREV", yy)]
  out[, MCDEV    := get_var("MCDEV", yy)]
  out[, PRIV     := get_var("PRIV", yy)]
  out[, MCARE    := get_var("MCARE", paste0(yy, "X"))]
  out[, MCAID    := get_var("MCAID", paste0(yy, "X"))]

  # Medicare Advantage
  out[, MCRPHO   := get_var("MCRPHO", yy)]

  # Access / cost barriers
  # Variable names changed: pre-2015ish used MDDLAY42/MDUNAB42/PMDLAY42/PMUNAB42
  # Post-2015ish uses DLAYCA42/AFRDCA42/DLAYPM42/AFRDPM42
  pick_access <- function(new_name, old_name) {
    if (new_name %in% names(dt)) return(dt[[new_name]])
    if (old_name %in% names(dt)) return(dt[[old_name]])
    return(rep(NA_integer_, nrow(dt)))
  }
  out[, DLAYCA42 := pick_access("DLAYCA42", "MDDLAY42")]
  out[, AFRDCA42 := pick_access("AFRDCA42", "MDUNAB42")]
  out[, DLAYPM42 := pick_access("DLAYPM42", "PMDLAY42")]
  out[, AFRDPM42 := pick_access("AFRDPM42", "PMUNAB42")]
  out[, HAVEUS42 := if ("HAVEUS42" %in% names(dt)) dt[["HAVEUS42"]] else NA_integer_]

  # Spending
  out[, TOTEXP   := get_var("TOTEXP", yy)]
  out[, TOTSLF   := get_var("TOTSLF", yy)]
  out[, TOTMCR   := get_var("TOTMCR", yy)]
  out[, TOTMCD   := get_var("TOTMCD", yy)]
  out[, TOTPRV   := get_var("TOTPRV", yy)]
  out[, RXEXP    := get_var("RXEXP", yy)]
  out[, RXSLF    := get_var("RXSLF", yy)]

  # Utilization
  out[, OBTOTV   := get_var("OBTOTV", yy)]
  out[, ERTOT    := get_var("ERTOT", yy)]
  out[, IPDIS    := get_var("IPDIS", yy)]
  out[, RXTOT    := get_var("RXTOT", yy)]

  # Medical bill stress
  out[, PROBPY42 := if ("PROBPY42" %in% names(dt)) dt[["PROBPY42"]] else NA_integer_]
  out[, PYUNBL42 := if ("PYUNBL42" %in% names(dt)) dt[["PYUNBL42"]] else NA_integer_]

  # Health status
  out[, RTHLTH42 := if ("RTHLTH42" %in% names(dt)) dt[["RTHLTH42"]] else NA_integer_]
  out[, MNHLTH42 := if ("MNHLTH42" %in% names(dt)) dt[["MNHLTH42"]] else NA_integer_]

  # Chronic conditions
  out[, HIBPDX   := if ("HIBPDX" %in% names(dt)) dt[["HIBPDX"]] else NA_integer_]
  out[, CHDDX    := if ("CHDDX" %in% names(dt)) dt[["CHDDX"]] else NA_integer_]
  out[, STRKDX   := if ("STRKDX" %in% names(dt)) dt[["STRKDX"]] else NA_integer_]
  out[, DIABDX   := if ("DIABDX" %in% names(dt)) dt[["DIABDX"]] else NA_integer_]
  out[, ARTHDX   := if ("ARTHDX" %in% names(dt)) dt[["ARTHDX"]] else NA_integer_]
  out[, CANCERDX := if ("CANCERDX" %in% names(dt)) dt[["CANCERDX"]] else NA_integer_]

  # Monthly insurance indicators (for churn)
  for (m in 1:12) {
    ma <- MONTH_ABBR[m]
    # Any insurance monthly
    ins_var <- paste0("INS", ma, yy, "X")
    col_name <- sprintf("INS_M%02d", m)
    out[, (col_name) := if (ins_var %in% orig_names) dt[[ins_var]] else NA_integer_]

    # Medicare monthly
    mcr_var <- paste0("MCR", ma, yy)
    col_name_mcr <- sprintf("MCR_M%02d", m)
    out[, (col_name_mcr) := if (mcr_var %in% orig_names) dt[[mcr_var]] else NA_integer_]

    # Private monthly
    pri_var <- paste0("PRI", ma, yy)
    col_name_pri <- sprintf("PRI_M%02d", m)
    out[, (col_name_pri) := if (pri_var %in% orig_names) dt[[pri_var]] else NA_integer_]

    # Policyholder ESI monthly (for age-26 dependent proxy)
    hpe_var <- paste0("HPE", ma, yy)
    col_name_hpe <- sprintf("HPE_M%02d", m)
    out[, (col_name_hpe) := if (hpe_var %in% orig_names) dt[[hpe_var]] else NA_integer_]

    # Covered by ESI monthly
    peg_var <- paste0("PEG", ma, yy)
    col_name_peg <- sprintf("PEG_M%02d", m)
    out[, (col_name_peg) := if (peg_var %in% orig_names) dt[[peg_var]] else NA_integer_]
  }

  # Immigration / language (for HTE)
  out[, BORNUSA  := if ("BORNUSA" %in% names(dt)) dt[["BORNUSA"]] else NA_integer_]
  out[, HWELLSPK := if ("HWELLSPK" %in% names(dt)) dt[["HWELLSPK"]] else NA_integer_]

  # Employment
  out[, EMPST42  := if ("EMPST42" %in% names(dt)) dt[["EMPST42"]] else NA_integer_]

  cat(sprintf("  -> %d canonical variables\n", ncol(out)))
  return(out)
}

# Quick test function
test_harmonize <- function(year = 2021) {
  dt <- harmonize_fyc(year)
  cat(sprintf("\nTest results for %d:\n", year))
  cat(sprintf("  Rows: %s\n", format(nrow(dt), big.mark=",")))
  cat(sprintf("  Cols: %d\n", ncol(dt)))
  cat(sprintf("  Non-NA DOBMM: %d (%.1f%%)\n",
              sum(!is.na(dt$DOBMM)), 100*mean(!is.na(dt$DOBMM))))
  cat(sprintf("  Non-NA TOTSLF: %d (%.1f%%)\n",
              sum(!is.na(dt$TOTSLF)), 100*mean(!is.na(dt$TOTSLF))))
  cat(sprintf("  Non-NA DLAYCA42: %d (%.1f%%)\n",
              sum(!is.na(dt$DLAYCA42)), 100*mean(!is.na(dt$DLAYCA42))))
  cat(sprintf("  Non-NA PERWT: %d (%.1f%%)\n",
              sum(!is.na(dt$PERWT)), 100*mean(!is.na(dt$PERWT))))
  cat(sprintf("  Age range: %d - %d\n", min(dt$AGE, na.rm=TRUE), max(dt$AGE, na.rm=TRUE)))
  invisible(dt)
}

if (sys.nframe() == 0) {
  test_harmonize(2021)
}
