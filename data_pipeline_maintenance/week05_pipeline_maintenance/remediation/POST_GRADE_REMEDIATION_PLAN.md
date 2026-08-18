# Week 5 Data Pipeline Maintenance — Post-Grade Remediation Plan

**Student:** Ceasar Jackson
**Discord:** knucknuclear
**Original Grade:** B

## 1. Purpose

This remediation preserves the originally graded submission and creates a
separate hardened version that addresses the grader's operational-specificity
feedback.

The original graded deliverable remains unchanged:

`submission/data_pipeline_maintenance.md`

The remediated working deliverable is:

`remediation/data_pipeline_maintenance_hardened.md`

## 2. Grader Feedback Summary

The original submission was recognized as strong in:

- clarity and organization;
- coverage of all five pipelines;
- primary and secondary ownership;
- fair on-call rotation;
- holiday coverage;
- investor-facing runbooks;
- realistic failure scenarios;
- escalation and handoff expectations.

The principal gap versus the ideal rubric was insufficient operational
specificity, particularly missing explicit SLAs/SLOs and on-call procedures
inside each investor-facing runbook.

## 3. Remediation Objectives

The hardened submission will add the following.

### 3.1 Service levels

For each investor-facing pipeline, define:

- data freshness SLO;
- business-hours alert acknowledgment SLA;
- off-hours alert acknowledgment SLA;
- Sev1 resolution target;
- Sev2 resolution target;
- RPO;
- RTO.

### 3.2 Expertise-based ownership

Add an engineer skills and coverage matrix covering:

- analytics engineering;
- finance and reconciliation;
- customer identity and growth modeling;
- event and engagement pipelines;
- orchestration and infrastructure;
- observability and incident response.

Tie each primary and secondary ownership assignment to those strengths.

### 3.3 Run cadence and dependencies

For each investor-facing pipeline, document:

- run cadence;
- expected start time;
- expected completion time;
- orchestrator DAG or workflow identifier;
- critical upstream dependencies;
- downstream consumers;
- log location;
- dashboard location;
- rerun or backfill command.

### 3.4 Data-quality guardrails

Add concrete controls such as:

- row-count variance thresholds;
- null-key thresholds;
- duplicate-key thresholds;
- schema-contract checks;
- referential-integrity checks;
- source-to-target reconciliation tolerances;
- freshness thresholds.

State where checks execute, such as:

- dbt tests;
- Great Expectations;
- custom SQL validation;
- orchestration task checks;
- observability platform checks.

### 3.5 Reconciliation and reproducibility

For investor-facing metrics, document:

- reconciliation against source systems;
- variance tolerances;
- sign-off requirements;
- code/version pinning;
- semantic-layer versioning;
- configuration versioning;
- seeds and dictionaries;
- reporting-period freeze windows.

### 3.6 Incident severity model

Define:

- Sev1;
- Sev2;
- Sev3.

For each severity, specify:

- acknowledgment target;
- resolution target;
- stakeholder notification timing;
- communication cadence;
- required participants;
- escalation expectations.

### 3.7 On-call procedure specificity

Document:

- exact weekly shift start and end time;
- timezone;
- primary and secondary responsibilities;
- handoff storage location;
- owner-shadow coverage during sensitive reporting periods;
- rules for paging pipeline owners overnight or on weekends.

### 3.8 Change management

For investor-facing metrics, require:

- Data/Governance approval;
- Finance approval where applicable;
- changelog updates;
- semantic-layer versioning;
- validation evidence;
- release sign-off;
- reporting freeze windows.

### 3.9 Operational references

Add placeholders for:

- Airflow or orchestrator dashboard;
- data observability dashboard;
- lineage graph;
- secrets and credentials runbook;
- data dictionary;
- incident Slack channels;
- distribution lists;
- named stakeholder roles.

### 3.10 RACI

Add lightweight RACI guidance for:

- incidents;
- metric-definition changes;
- production changes;
- reporting sign-off.

## 4. Preservation Requirements

The remediation must not modify:

- `submission/data_pipeline_maintenance.md`
- `submission/CeasarJackson_Week5_Data_Pipeline_Maintenance.zip`
- `validation/results/submission_sha256.txt`
- original validation evidence

The baseline submission remains the immutable record of the graded B artifact.

## 5. Validation Requirements

The hardened submission must pass checks for:

- all five pipelines;
- all required assignment sections;
- SLA/SLO coverage;
- severity-model coverage;
- expertise-based ownership rationale;
- schedule and dependency details;
- concrete data-quality thresholds;
- reconciliation controls;
- change-management controls;
- incident communication procedures;
- no terminal or heredoc artifacts;
- no trailing whitespace;
- clean Git diff.

## 6. Deliverables

Expected remediation artifacts:

- `POST_GRADE_REMEDIATION_PLAN.md`
- `data_pipeline_maintenance_hardened.md`
- remediation validation script
- remediation validation results
- final remediation archive
- final remediation SHA-256 checksum
