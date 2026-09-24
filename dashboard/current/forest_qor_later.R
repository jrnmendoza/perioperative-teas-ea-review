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

# Start logging
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
  
  # Prepare plotting bounds
  # all plotted intervals
  ci_lbs <- c(res$yi - 1.96*sqrt(res$vi), res$ci.lb)
  ci_ubs <- c(res$yi + 1.96*sqrt(res$vi), res$ci.ub)
  min_val <- min(ci_lbs)
  max_val <- max(ci_ubs)
  
  # Compute alim with pretty()
  pticks <- pretty(c(min_val, max_val))
  alim_val <- c(min(pticks), max(pticks))
  
  # Layout setup: xlim leaves space on left and right
  # left space for study name and 4 arm columns. right for MD [CI]
  span <- alim_val[2] - alim_val[1]
  xlim_val <- c(alim_val[1] - span * 1.5, alim_val[2] + span * 0.6)
  
  # Position of 4 columns in the left space (between xlim[1] and alim[1])
  left_w <- alim_val[1] - xlim_val[1]
  # space out the columns: TEAS n, TEAS mean(SD), Sham n, Sham mean(SD)
  ilab_pos <- c(
    xlim_val[1] + left_w * 0.35,
    xlim_val[1] + left_w * 0.55,
    xlim_val[1] + left_w * 0.75,
    xlim_val[1] + left_w * 0.95
  )
  
  svg_path <- sprintf("forest_%s.svg", model_id)
  svg(svg_path, width=12, height=4.5 + k*0.35)
  par(mar=c(5, 1, 3, 1))
  
  slab_vals <- df$study
  ilab_vals <- cbind(df$n_i, sprintf("%.1f (%.1f)", df$mean_i, df$sd_i), df$n_c, sprintf("%.1f (%.1f)", df$mean_c, df$sd_c))
  
  if (k > 1) {
    # No prediction interval, use short mlab
    forest(res, slab=slab_vals, ilab=ilab_vals, ilab.xpos=ilab_pos, ilab.pos=2,
           xlab=m$unit, xlim=xlim_val, alim=alim_val, refline=0,
           top=3, addfit=TRUE, mlab="RE model (REML, safeguarded HK)")
           
    # I2 and tau2 underneath the diamond
    text(xlim_val[1], -1.5, sprintf("I^2 = %.1f%%, tau^2 = %.2f", res$I2, res$tau2), pos=4, cex=0.85)
  } else {
    forest(res, slab=slab_vals, ilab=ilab_vals, ilab.xpos=ilab_pos, ilab.pos=2,
           xlab=m$unit, xlim=xlim_val, alim=alim_val, refline=0,
           top=3, addfit=FALSE)
    text(xlim_val[1], 0, "Single study, not pooled", pos=4, cex=0.85)
  }
  
  # Headers
  # The first study is at y=1, header one row above (y = k+1)
  # But forest internally sets ylim slightly higher. Let's just use text() at k+1.5 or so
  text(xlim_val[1], k + 1.5, "Study", pos=4, font=2)
  text(ilab_pos[1], k + 1.5, "TEAS n", pos=2, font=2)
  text(ilab_pos[2], k + 1.5, "TEAS mean (SD)", pos=2, font=2)
  text(ilab_pos[3], k + 1.5, "Sham n", pos=2, font=2)
  text(ilab_pos[4], k + 1.5, "Sham mean (SD)", pos=2, font=2)
  text(xlim_val[2], k + 1.5, "MD [95% CI]", pos=2, font=2)
  
  # Title
  title(m$label, line=1.5, cex.main=1.1)
  
  # Positive MD favours TEAS
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
