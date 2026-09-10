// Outcome quarantine registry.
//
// An entry here means: this Meta Lab outcome contains at least one study record
// whose arm-level values have NOT been verified against the source publication,
// so its pooled estimate must not be presented as a normal verified result.
// renderMetaLab() shows a "pending verification" notice for any outcome listed.
//
// scripts/validate_dashboard.py (t_quarantine_registry_is_honest) asserts that
// every entry names a real, live Meta Lab outcome and carries a reason, so the
// registry cannot drift in either direction: an outcome cannot sit here after
// its records are verified, and cannot be listed without saying why.
//
// Add an outcome here the moment a record under it loses source backing.
// Remove it only when EVERY study record under it has been verified against the
// original publication.
//
// ── History ──────────────────────────────────────────────────────────────────
// 2026-09-10  Opened for intraop_opioid, flatus_time, rescue_analgesia and
//             opioid_48h during the placeholder-value incident: 15 arm-bearing
//             records held values matching no source and no lock.
// 2026-09-10  Closed. All 15 records were verified against their source PDFs and
//             regenerated from the lock; the two opioid_48h ambiguities were
//             resolved (Zhang 2023 recoverable via the documented median/IQR
//             transformation; Xie 2014 correctly outside the strict 48 h set).
//             See 99_audit/2026-09-10_placeholder_incident/.
window.OUTCOME_QUARANTINE = {};
