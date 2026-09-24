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
    stop(sprintf("Model %s field %s failed: canonical %f, metafor %f, diff %f > tol %f", model_id, field, canonical_val, metafor_val, abs_diff, tol))
  }
}

for (i in 1:length(models)) {
  m <- models[[i]]
  model_id <- m$model_id
  
  ids <- unlist(m$result_ids)
  
  df <- inputs[match(ids, inputs$result_id), ]
  if (any(is.na(df$result_id))) {
    stop("Missing result_id for model ", model_id)
  }
  
  expected_studies <- trimws(unlist(strsplit(m$studies, ";")))
  if (!all(expected_studies == df$study)) {
    stop("Studies mismatch for model ", model_id)
  }
  
  z <- escalc(measure='MD', m1i=df$mean_i, sd1i=df$sd_i, n1i=df$n_i, m2i=df$mean_c, sd2i=df$sd_c, n2i=df$n_c)
  if (any(abs(z$yi - df$yi) > 1e-10) || any(abs(z$vi - df$vi) > 1e-10)) {
    stop("yi or vi mismatch in escalc for model ", model_id)
  }
  
  k <- nrow(df)
  method_val <- if (k > 1) 'REML' else 'EE'
  test_val <- if (k > 1) 'adhoc' else 'z'
  
  res <- rma.uni(yi, vi, data=z, method=method_val, test=test_val, control=list(threshold=1e-10, maxiter=10000))
  
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
  svg(svg_path, width=10, height=3 + k*0.3)
  
  slab_vals <- df$study
  ilab_vals <- cbind(df$n_i, sprintf("%.1f (%.1f)", df$mean_i, df$sd_i), df$n_c, sprintf("%.1f (%.1f)", df$mean_c, df$sd_c))
  
  forest(res, slab=slab_vals, ilab=ilab_vals, ilab.xpos=c(-10, -7.5, -4.5, -2),
         xlab=m$unit, header=c("Study", "MD [95% CI]"),
         addfit=(k>1), top=2)
  text(-10, k+1.5, "TEAS n", font=2)
  text(-7.5, k+1.5, "TEAS mean (SD)", font=2)
  text(-4.5, k+1.5, "Sham n", font=2)
  text(-2, k+1.5, "Sham mean (SD)", font=2)
  
  title(m$label, line=0.5)
  if (k == 1) {
    mtext("Single study, not pooled", side=1, line=3, cex=0.8, adj=0)
  }
  if (k > 1) {
    text(min(res$yi) - 5, -1, "REML, safeguarded Hartung–Knapp", pos=4, cex=0.8)
  }
  mtext("Positive MD favours TEAS", side=1, line=2, cex=0.8, adj=1)
  
  dev.off()
}

write.csv(estimates_out, "metafor_estimates.csv", row.names=FALSE)
write.csv(comparison_out, "metafor_comparison_later.csv", row.names=FALSE)

sink("R_session_forest_later.txt")
print(sessionInfo())
print(packageVersion('metafor'))
sink()

files_to_hash <- c("forest_qor_later.R", "metafor_estimates.csv", "metafor_comparison_later.csv", "R_session_forest_later.txt", unlist(lapply(models, function(m) sprintf("forest_%s.svg", m$model_id))))
manifest <- list(
  metafor_version = as.character(packageVersion('metafor')),
  R_version = R.version.string,
  files = lapply(files_to_hash, function(f) {
    list(file=f, sha256=digest::digest(file=f, algo="sha256"))
  })
)
write_json(manifest, "manifest.json", auto_unbox=TRUE, pretty=TRUE)
