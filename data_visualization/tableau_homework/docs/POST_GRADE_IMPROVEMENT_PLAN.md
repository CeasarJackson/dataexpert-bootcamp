# Week 7 — Post-Grade Improvement Plan

**Course:** DataExpert Boot Camp
**Assignment:** Week 7 — Data Visualization / Tableau
**Author:** Ceasar Jackson
**Graded baseline:** `week07-graded-b`
**Final grade:** B
**Improvement branch:** `improve/week07-post-grade-hardening`

## Purpose

This document tracks post-grade improvements derived from the Week 7 grader feedback while preserving the exact graded submission at the `week07-graded-b` tag.

## Improvement Priorities

1. Executive dashboard KPI clarity and executive summary.
2. Trend context, date-range clarity, and comparison baselines.
3. Exploratory dashboard filters and normalized metrics.
4. Improved tooltips, distributions, and drill-through interactions.
5. Calculation and data-quality documentation.
6. Accessibility, formatting, and visual consistency.
7. Tableau Public publishing metadata and reviewer fallback artifacts.
8. Submission-package compatibility with the grading system.

## Grader Feedback Remediation Matrix

| Area | Grader Recommendation | Priority | Planned Action |
|---|---|---:|---|
| Executive | Concise 3–5 KPI header | High | Review existing six KPI cards and prioritize the most decision-relevant metrics. |
| Executive | Delta vs prior period | High | Add period-over-period context where supported by the available data. |
| Executive | Clear date range | High | Surface the active data period in dashboard context/title. |
| Executive | Primary trend | High | Preserve a dominant time-series view and improve its analytical context. |
| Executive | Executive summary | High | Add a concise takeaway/interpretation area. |
| Executive | Segment drivers | Medium | Evaluate available dimensions before adding segment views. |
| Exploratory | Player/playlist/map/medal/time filters | High | Add only filters supported by the prepared datasets. |
| Exploratory | Normalize comparisons | High | Add per-match/per-player normalized measures where valid. |
| Exploratory | Distribution views | Medium | Evaluate histogram/boxplot feasibility from available grain. |
| Exploratory | Drill-through interaction | Medium | Improve dashboard actions where they add analytical value. |
| Exploratory | Descriptive tooltips | High | Add definitions and analytical context to important marks. |
| Data | Document calculated fields | High | Document formulas, grain, assumptions, and interpretation. |
| Data | Validate totals across views | High | Add deterministic cross-view reconciliation checks. |
| Data | About/Data note | High | Document source, refresh/build information, and KPI definitions. |
| Accessibility | Colorblind-friendly palette | High | Review palette, contrast, and redundant visual encoding. |
| Accessibility | Readable typography | High | Review titles, labels, legends, and dashboard text sizing. |
| Publishing | Workbook description / Last Updated | Medium | Improve Tableau Public presentation metadata where supported. |
| Publishing | Mobile/tablet layouts | Low | Evaluate after desktop analytical design is stable. |
| Submission | Reviewer fallback artifacts | High | Provide PDF/screenshots in addition to Tableau Public URLs. |
| Submission | Unsupported TWBX grading format | High | Keep TWBX as source artifact but do not rely on it as the grader-readable deliverable. |

## Guardrails

- Do not modify the `week07-graded-b` baseline.
- All post-grade changes remain isolated to `improve/week07-post-grade-hardening`.
- Do not add metrics that cannot be derived correctly from the available data.
- Follow the verified capability boundaries documented in `POST_GRADE_CAPABILITY_AUDIT.md`; do not claim unsupported metrics.
- Preserve the existing working Tableau Public dashboards while improvements are developed and validated.
- Maintain deterministic workbook validation and package-integrity checks.

## Source Capability Audit

A formal source-data capability audit is documented in:

`docs/POST_GRADE_CAPABILITY_AUDIT.md`

The audit establishes the implementation boundary for the post-grade
hardening work.

Key conclusions:

- K/D, KDA, Win Rate, Player, Date, and Team Game are supported.
- Human-readable Map filtering is supported with 100% lookup coverage.
- Medals per Match is derivable.
- Prior-period comparisons are derivable from the daily series.
- Distribution analysis is supported from detailed source grains.
- Playlist and Game Variant are currently available only as IDs.
- Accuracy is unsupported because shots attempted/fired are unavailable.
- Region is unsupported.
- `match_duration` exists upstream but is null for all 24,025 matches.
- Medals per 10 Minutes and Average Match Length are therefore unsupported.

Post-grade implementation must remain inside these verified boundaries.
