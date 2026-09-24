.libPaths(c(Sys.getenv('ASTRA_R_LIBRARY'), .libPaths()))
library(jsonlite)
library(metafor)

inputs_file <- "../qor_inputs_later.csv"
models_file <- "../qor_models_later.json"

inputs <- read.csv(inputs_file, stringsAsFactors=FALSE)
models <- fromJSON(models_file, simplifyDataFrame=FALSE)

estimates_out <- data.frame()
comparison_out <- data.frame(
  model_id = character(),
  field = character(),
  canonical = numeric(),
  metafor = numeric(),
  abs_diff = numeric(),
  tolerance = numeric(),
  passed = logical(),
  stringsAsFactors = FALSE
)

sink("forest_qor_later_run.txt")
cat("--- RUN LOG ---\n")
print(R.version.string)
cat(sprintf("metafor version: %s\n", packageVersion('metafor')))
cat("---------------\n\n")

check_numeric <- function(model_id, field, canonical_val, metafor_val, tol) {
  if (is.null(canonical_val) || is.na(canonical_val)) {
    if (is.null(metafor_val) || is.na(metafor_val)) return()
  }
  abs_diff <- abs(canonical_val - metafor_val)
  passed <- abs_diff <= tol
  comparison_out <<- rbind(comparison_out, data.frame(
    model_id = model_id,
    field = field,
    canonical = canonical_val,
    metafor = metafor_val,
    abs_diff = abs_diff,
    tolerance = tol,
    passed = passed,
    stringsAsFactors = FALSE
  ))
  if (!passed) {
    cat(sprintf("FAIL: Model %s field %s failed: canonical %f, metafor %f, diff %f > tol %f\n", model_id, field, canonical_val, metafor_val, abs_diff, tol))
  }
}

for (i in 1:length(models)) {
  m <- models[[i]]
  model_id <- m$model_id
  ids <- unlist(m$result_ids)
  df <- inputs[match(ids, inputs$result_id), ]
  
  cat(sprintf("\n=== MODEL: %s ===\n", model_id))
  cat(sprintf("Result IDs: %s\n", paste(ids, collapse=", ")))
  cat(sprintf("Studies: %s\n", paste(df$study, collapse=", ")))
  
  if (any(is.na(df$result_id))) stop("Missing result_id for model ", model_id)
  expected_studies <- trimws(unlist(strsplit(m$studies, ";")))
  if (!all(expected_studies == df$study)) stop("Studies mismatch for model ", model_id)
  
  z <- escalc(measure='MD', m1i=df$mean_i, sd1i=df$sd_i, n1i=df$n_i, m2i=df$mean_c, sd2i=df$sd_c, n2i=df$n_c)
  if (any(abs(z$yi - df$yi) > 1e-10) || any(abs(z$vi - df$vi) > 1e-10)) stop("yi or vi mismatch in escalc for model ", model_id)
  
  k <- nrow(df)
  method_val <- if (k > 1) 'REML' else 'EE'
  test_val <- if (k > 1) 'adhoc' else 'z'
  
  res <- rma.uni(yi, vi, data=z, method=method_val, test=test_val, control=list(threshold=1e-10, maxiter=10000))
  print(res)
  
  check_numeric(model_id, 'effect', m$effect, res$beta[1], 1e-6)
  check_numeric(model_id, 'ci_low', m$ci_low, res$ci.lb, 1e-6)
  check_numeric(model_id, 'ci_high', m$ci_high, res$ci.ub, 1e-6)
  if (k > 1) {
    check_numeric(model_id, 'tau2', m$tau2, res$tau2, 1e-4)
    check_numeric(model_id, 'I2', m$I2, res$I2, 1e-4)
  }
  
  estimates_out <- rbind(estimates_out, data.frame(
    model_id = model_id,
    k = k,
    effect = res$beta[1],
    se = res$se,
    ci_low = res$ci.lb,
    ci_high = res$ci.ub,
    tau2 = if(k > 1) res$tau2 else NA,
    I2 = if(k > 1) res$I2 else NA,
    stringsAsFactors = FALSE
  ))
  
  svg_path <- sprintf("forest_%s.svg", model_id)
  svg(svg_path, width=12, height=4.5 + k*0.35)
  par(mar=c(6, 1, 3, 1))
  plot.new()  # opens the plot region so text widths can be measured

  ci_lbs <- c(res$yi - 1.96*sqrt(res$vi), res$ci.lb)
  ci_ubs <- c(res$yi + 1.96*sqrt(res$vi), res$ci.ub)
  pticks <- pretty(c(min(ci_lbs), max(ci_ubs), 0))  # always include the null (0) so refline=0 sits on the axis
  alim_val <- range(pticks)

  comp <- unique(df$comparator)
  if (length(comp) != 1) stop("Mixed comparators in ", model_id)
  ctrl <- switch(comp, "sham"="Sham", "usual care"="Usual care", stop("Unknown comparator '", comp, "' in ", model_id))
  hdr <- c("TEAS n", "TEAS mean (SD)", paste(ctrl, "n"), paste(ctrl, "mean (SD)"))
  c1_vals <- as.character(df$n_i)
  c2_vals <- sprintf("%.1f (%.1f)", df$mean_i, df$sd_i)
  c3_vals <- as.character(df$n_c)
  c4_vals <- sprintf("%.1f (%.1f)", df$mean_c, df$sd_c)
  annot_vals <- sprintf("%.2f [%.2f, %.2f]", c(res$yi, res$b), c(res$yi - 1.96*sqrt(res$vi), res$ci.lb), c(res$yi + 1.96*sqrt(res$vi), res$ci.ub))

  # Measure every width in INCHES (independent of user coordinates), then convert to
  # plot units once the inch width of the plot region (par("pin")) is known.
  cex_val <- 0.9
  win <- function(x, bold=FALSE) max(strwidth(x, units="inches", cex=cex_val, font=if (bold) 2 else 1))
  gap   <- win("MM")
  w_st  <- max(win(df$study), win("Study", TRUE), if (k > 1) win("RE model (REML, safeguarded HK)") else 0)
  w_col <- c(max(win(c1_vals), win(hdr[1], TRUE)),
             max(win(c2_vals), win(hdr[2], TRUE)),
             max(win(c3_vals), win(hdr[3], TRUE)),
             max(win(c4_vals), win(hdr[4], TRUE)))
  w_ann <- max(win(annot_vals), win("MD [95% CI]", TRUE))

  left_in  <- w_st + gap + sum(w_col) + 4*gap      # study label + four columns, each followed by a gap
  right_in <- gap + w_ann
  plot_in  <- par("pin")[1]
  axis_in  <- plot_in - left_in - right_in
  if (axis_in < 2) stop("Not enough width for the axis in ", model_id, ": ", round(axis_in, 2), " in")
  u <- diff(alim_val) / axis_in                    # plot units per inch

  xlim_val <- c(alim_val[1] - left_in*u, alim_val[2] + right_in*u)
  # Right edge of each column (values and headers are right-aligned with pos=2)
  x4 <- alim_val[1] - gap*u
  x3 <- x4 - (w_col[4] + gap)*u
  x2 <- x3 - (w_col[3] + gap)*u
  x1 <- x2 - (w_col[2] + gap)*u
  ilab_pos <- c(x1, x2, x3, x4)
  ilab_vals <- cbind(c1_vals, c2_vals, c3_vals, c4_vals)

  fp <- forest(res, slab=df$study, ilab=ilab_vals, ilab.xpos=ilab_pos, ilab.pos=2,
               xlab=m$unit, xlim=xlim_val, alim=alim_val, at=pticks, refline=0,
               top=3, addfit=(k > 1), header=FALSE, cex=cex_val,
               mlab=if (k > 1) "RE model (REML, safeguarded HK)" else NULL)
  
  y_head <- fp$ylim[2] - 1
  
  text(fp$textpos[1], y_head, "Study", pos=4, font=2, cex=fp$cex)
  text(ilab_pos[1], y_head, hdr[1], pos=2, font=2, cex=fp$cex)
  text(ilab_pos[2], y_head, hdr[2], pos=2, font=2, cex=fp$cex)
  text(ilab_pos[3], y_head, hdr[3], pos=2, font=2, cex=fp$cex)
  text(ilab_pos[4], y_head, hdr[4], pos=2, font=2, cex=fp$cex)
  text(fp$textpos[2], y_head, "MD [95% CI]", pos=2, font=2, cex=fp$cex)
  
  if (k > 1) {
    text(xlim_val[1], -1.5, sprintf("I\u00b2 = %.1f%%, \u03c4\u00b2 = %.2f", res$I2, res$tau2), pos=4, cex=fp$cex * 0.85)
  } else {
    mtext("Single study, not pooled", side=1, line=4.5, adj=0, cex=fp$cex * 0.85)
  }
  
  title(m$label, line=1.5, cex.main=1.1)
  mtext("Positive MD favours TEAS", side=1, line=4, cex=0.8, adj=1)
  
  dev.off()
}

write.csv(estimates_out, "metafor_estimates.csv", row.names=FALSE)
write.csv(comparison_out, "metafor_comparison_later.csv", row.names=FALSE)

cat("\n\n=== COMPARISON TABLE ===\n")
print(comparison_out)

if (all(comparison_out$passed)) {
  cat("\nALL COMPARISONS PASSED\n")
} else {
  cat("\nSOME COMPARISONS FAILED\n")
}

sink()

sink("R_session_forest_later.txt")
print(sessionInfo())
print(packageVersion('metafor'))
sink()

files_to_hash <- c("forest_qor_later.R", "metafor_estimates.csv", "metafor_comparison_later.csv", "R_session_forest_later.txt", "forest_qor_later_run.txt", unlist(lapply(models, function(m) sprintf("forest_%s.svg", m$model_id))))
manifest <- list(
  metafor_version = as.character(packageVersion('metafor')),
  R_version = R.version.string,
  files = lapply(files_to_hash, function(f) {
    list(file=f, sha256=digest::digest(file=f, algo="sha256"))
  })
)
write_json(manifest, "manifest.json", auto_unbox=TRUE, pretty=TRUE)
