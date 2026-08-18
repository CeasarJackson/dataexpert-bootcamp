# Week 5 Data Pipeline Maintenance — A-Grade Remediation Result

**Student:** Ceasar Jackson
**Discord:** knucknuclear
**Original Grade:** B
**Remediated Grade:** A
**Status:** Remediation accepted

## Outcome

The Week 5 Data Pipeline Maintenance submission was remediated in response to
grader feedback and subsequently received a final grade of A.

The remediation retained the original graded B submission as an immutable
baseline and developed the hardened version separately.

## Major remediation areas completed

The hardened submission added or strengthened:

- a skills and coverage matrix tying ownership to domain expertise;
- explicit on-call shift timing;
- owner-shadow support during investor-reporting windows;
- an incident severity model with acknowledgment and mitigation targets;
- stakeholder communication expectations;
- portfolio-level schedule and dependency documentation;
- shared operational-reference placeholders;
- explicit SLO, SLA, RTO, and RPO targets for investor pipelines;
- concrete data-quality thresholds and guardrails;
- reconciliation and reproducibility controls;
- quick-triage and known-good checks;
- rerun and backfill procedures;
- pipeline-specific on-call escalation;
- RACI matrices;
- metric-definition change management;
- investor-reporting freeze windows;
- business-domain and governance stakeholder mappings.

## Final grader assessment

The remediated submission received:

**FINAL GRADE: A**

The grader specifically praised:

- structure and clarity;
- expertise-based ownership and redundancy;
- the fair on-call model;
- holiday coverage;
- comprehensive investor-facing runbooks;
- portfolio dependency visibility;
- incident management;
- SLO/SLA, RTO/RPO, data-quality, reconciliation, backfill, RACI, and
  change-freeze practices.

Remaining suggestions were operational polish rather than assignment deficiencies.

## README path clarification

The grader noted a possible path inconsistency.

Repository layout:

`submission/data_pipeline_maintenance.md`

Submission ZIP layout:

`data_pipeline_maintenance.md`

These are intentionally different contexts.

The repository README correctly identifies the repository-relative graded
deliverable as:

`submission/data_pipeline_maintenance.md`

The ZIP intentionally places the deliverable at the archive root so the grader
receives exactly:

- `data_pipeline_maintenance.md`
- `README.md`

No README correction was required.

## Artifact preservation

The repository preserves separate artifacts for:

- the original B-grade submission;
- the hardened remediation source;
- the exact A-grade submitted ZIP.

This maintains provenance and makes the remediation independently auditable.
