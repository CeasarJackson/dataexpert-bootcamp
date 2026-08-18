# Week 5 — Data Pipeline Maintenance

**Student:** Ceasar Jackson
**Discord:** knucknuclear

---

## Contents

- [1. Overview](#1-overview)
- [2. Team](#2-team)
- [3. Pipeline Inventory and Ownership](#3-pipeline-inventory-and-ownership)
- [4. Fair On-Call Schedule](#4-fair-on-call-schedule)
- [5. Holiday and Time-Off Policy](#5-holiday-and-time-off-policy)
- [6. Investor Pipeline Runbooks](#6-investor-pipeline-runbooks)
  - [6.1 Aggregate Profit](#61-aggregate-profit-pipeline-runbook)
  - [6.2 Aggregate Growth](#62-aggregate-growth-pipeline-runbook)
  - [6.3 Aggregate Engagement](#63-aggregate-engagement-pipeline-runbook)
- [7. Potential Problems Across All Five Pipelines](#7-potential-problems-across-all-five-pipelines)
- [8. Experiment Pipeline Considerations](#8-experiment-pipeline-considerations)
- [9. Escalation Model](#9-escalation-model)
- [10. On-Call Handoff](#10-on-call-handoff)
- [11. Summary](#11-summary)

---

## 1. Overview

This document defines an operating model for a four-person data engineering team responsible for five production data pipelines supporting the following business areas:

- Profit
- Growth
- Engagement

The pipelines serve two different classes of consumers:

1. **Experimentation pipelines** — optimized for timely, granular metrics used by product and experimentation teams.
2. **Investor-reporting pipelines** — optimized for accuracy, reconciliation, reproducibility, and executive reporting.

Because investor-facing metrics have a higher business and reputational impact, those pipelines receive additional ownership redundancy and documented runbooks.

---

## 2. Team

The four data engineers are represented as:

| Engineer | Role in Rotation |
|---|---|
| Engineer A | Primary owner / on-call participant |
| Engineer B | Primary owner / on-call participant |
| Engineer C | Primary owner / on-call participant |
| Engineer D | Primary owner / on-call participant |

Every production pipeline has:

- one **primary owner**;
- one **secondary owner**;
- at least two engineers capable of investigating the pipeline;
- shared team responsibility while the assigned engineer is on call.

Ownership does **not** mean that only the primary owner may respond to incidents. Ownership identifies who is most familiar with the pipeline and who is responsible for keeping its documentation current.

### Skills and coverage matrix

Ownership is aligned to both business-domain knowledge and technical strengths so that assignments are not based only on fairness.

| Engineer | Primary Strengths | Business / Technical Coverage |
|---|---|---|
| Engineer A | Analytics engineering, product analytics, event pipelines | Engagement metrics, unit-level experimentation, semantic consistency, event-quality investigation |
| Engineer B | Finance data, reconciliation, accounting-oriented controls | Profit metrics, GL/subledger reconciliation, financial adjustments, reporting accuracy |
| Engineer C | Customer identity, growth modeling, lifecycle analytics | Growth metrics, customer/account identity, acquisition, activation, churn |
| Engineer D | Orchestration, infrastructure, performance, reliability | Scheduling, dependency management, backfills, platform failures, operational recovery |

The ownership model therefore reflects both expertise and redundancy:

- **Aggregate Profit** is primarily owned by Engineer B because of finance and reconciliation expertise, with Engineer D providing orchestration and reliability backup.
- **Aggregate Growth** is primarily owned by Engineer C because of customer-identity and growth-modeling expertise, with Engineer A providing analytics and semantic-layer backup.
- **Aggregate Engagement** is primarily owned by Engineer A because of event-pipeline and product-analytics expertise, with Engineer D providing infrastructure and operational backup.
- **Unit-Level Profit** pairs Engineer A's experimentation knowledge with Engineer C's analytical-modeling coverage.
- **Daily Growth** pairs Engineer D's operational reliability skills with Engineer B's control-oriented review discipline.

---

## 3. Pipeline Inventory and Ownership

| # | Business Area | Pipeline | Business Purpose | Primary Owner | Secondary Owner | Criticality |
|---:|---|---|---|---|---|---|
| 1 | Profit | Unit-Level Profit | Unit-level profit metrics used for experiments | Engineer A | Engineer C | High |
| 2 | Profit | Aggregate Profit | Aggregate profit metrics reported to investors | Engineer B | Engineer D | Critical |
| 3 | Growth | Aggregate Growth | Aggregate growth metrics reported to investors | Engineer C | Engineer A | Critical |
| 4 | Growth | Daily Growth | Daily growth metrics used for experiments | Engineer D | Engineer B | High |
| 5 | Engagement | Aggregate Engagement | Aggregate engagement metrics reported to investors | Engineer A | Engineer D | Critical |

### Ownership rationale

Ownership is deliberately distributed so that no engineer owns every high-impact pipeline.

Investor-reporting pipelines have primary/secondary combinations that spread institutional knowledge across the team:

- Aggregate Profit: Engineer B / Engineer D
- Aggregate Growth: Engineer C / Engineer A
- Aggregate Engagement: Engineer A / Engineer D

The experiment-oriented pipelines use complementary ownership:

- Unit-Level Profit: Engineer A / Engineer C
- Daily Growth: Engineer D / Engineer B

This arrangement ensures that every engineer participates in both primary and backup support while avoiding a single point of operational knowledge.

---

## 3.1 Portfolio Schedule and Dependency Matrix

The following matrix gives the on-call engineer a portfolio-level view of normal execution timing, critical dependencies, and primary operational references. Exact production URLs are environment-specific and should be maintained in the authoritative runbooks.

| Pipeline | Class | Normal Schedule / Target | Critical Upstream Dependencies | Primary Operational Reference |
|---|---|---|---|---|
| Unit-Level Profit | Experimentation | Daily; target ready before experiment-analysis window | Transaction-level revenue, cost allocation, experiment assignment, unit identifiers | `<UNIT_PROFIT_DAG_OR_JOB_URL>` |
| Aggregate Profit | Investor | Airflow 05:00 UTC; available by 08:00 UTC | Revenue/subledger, costs, approved adjustments, currency rates, business calendar | `<AIRFLOW_AGGREGATE_PROFIT_DAG_URL>` |
| Aggregate Growth | Investor | Airflow 05:30 UTC; available by 08:30 UTC | Customer/account master, lifecycle events, identity resolution, historical snapshots | `<AIRFLOW_AGGREGATE_GROWTH_DAG_URL>` |
| Daily Growth | Experimentation | Daily; target ready before product experimentation window | Registrations, customer/account records, experiment cohorts, daily snapshots | `<DAILY_GROWTH_DAG_OR_JOB_URL>` |
| Aggregate Engagement | Investor | Airflow 06:00 UTC; available by 09:00 UTC | Application/web events, sessions, authentication, identity mapping, event taxonomy | `<AIRFLOW_AGGREGATE_ENGAGEMENT_DAG_URL>` |

### Shared operational references

The following references should be maintained centrally so that on-call responders do not have to discover them during an incident:

- Airflow / orchestration dashboard: `<AIRFLOW_HOME_URL>`
- Data observability dashboard: `<DATA_OBSERVABILITY_HOME_URL>`
- Data-quality results: `<DATA_QUALITY_RESULTS_URL>`
- Data lineage graph: `<DATA_LINEAGE_HOME_URL>`
- Governed data dictionary: `<DATA_DICTIONARY_URL>`
- Secrets and credentials runbook: `<PLATFORM_ACCESS_RUNBOOK_URL>`
- Weekly on-call handoff document: `<ON_CALL_HANDOFF_DOCUMENT_URL>`
- Incident-management system / PagerDuty schedule: `<ON_CALL_SCHEDULE_URL>`
- Investor-data incident channel: `#data-investor-incidents`
- Data Engineering operations channel: `#data-engineering-ops`

### Operational ownership principle

The portfolio-level schedule does not replace the detailed investor runbooks. The primary on-call engineer owns initial detection and triage across all five pipelines, while pipeline owners provide domain expertise. Investor-facing workloads receive the stricter SLA, reconciliation, reproducibility, communication, and change-control requirements documented in Section 6.

---

## 4. Fair On-Call Schedule

The team uses a weekly rotating on-call schedule.

| Week | Primary On-Call | Secondary On-Call |
|---:|---|---|
| 1 | Engineer A | Engineer B |
| 2 | Engineer B | Engineer C |
| 3 | Engineer C | Engineer D |
| 4 | Engineer D | Engineer A |
| 5 | Engineer A | Engineer C |
| 6 | Engineer B | Engineer D |
| 7 | Engineer C | Engineer A |
| 8 | Engineer D | Engineer B |

After Week 8, the rotation repeats.

### Shift timing and operating expectations

Each weekly primary and secondary assignment runs from **Monday 09:00 UTC through the following Monday 09:00 UTC**.

The primary on-call engineer is the first operational responder for all five pipelines. The secondary on-call engineer:

- acknowledges the handoff at the start of the shift;
- confirms access to orchestration, monitoring, logs, lineage, and communication channels;
- becomes the acting primary if the scheduled primary is unavailable;
- assists with Sev1 incidents or incidents that affect an investor-reporting deadline.

During sensitive investor-reporting windows, the designated pipeline owner acts as an **owner shadow** in addition to the normal primary and secondary on-call engineers.

The on-call engineer may page a pipeline owner outside normal working hours when:

- a **Sev1** condition exists;
- a **Sev2** condition occurs within 48 hours of an investor-reporting deadline;
- specialized domain knowledge is required to prevent an investor-facing reporting delay or materially incorrect metric.

### Why this schedule is fair

The rotation provides:

- an equal number of primary on-call weeks;
- an equal number of secondary responsibilities over time;
- exposure to multiple teammates rather than using the same primary/secondary pair repeatedly;
- predictable handoffs;
- shared familiarity with all production pipelines.

The scheduled on-call engineer is responsible for the **entire pipeline portfolio**, not only pipelines for which that engineer is the designated owner.

If an incident requires deeper pipeline knowledge, the on-call engineer may escalate to the pipeline's primary owner and then secondary owner.

---

## 5. Holiday and Time-Off Policy

Holiday coverage must be planned so that the same engineer is not repeatedly assigned undesirable holiday periods.

### Holiday rules

1. Major holidays are identified before the quarterly on-call schedule is finalized.
2. Holiday primary assignments rotate from year to year.
3. Engineers should not receive the same major holiday assignment in consecutive years unless they volunteer.
4. Planned PTO takes precedence over the normal rotation when submitted before the schedule is finalized.
5. Voluntary swaps are permitted as long as both engineers agree and the schedule is updated.
6. A holiday assignment counts as a normal primary on-call week for workload-balancing purposes.
7. When practical, an engineer covering a major holiday receives reduced or avoided coverage during the following rotation.
8. The primary and secondary on-call engineers should not both be unavailable for the same period.

### Example holiday rotation

| Holiday | Year 1 | Year 2 | Year 3 | Year 4 |
|---|---|---|---|---|
| New Year's Day | Engineer A | Engineer B | Engineer C | Engineer D |
| Memorial Day | Engineer B | Engineer C | Engineer D | Engineer A |
| Independence Day | Engineer C | Engineer D | Engineer A | Engineer B |
| Labor Day | Engineer D | Engineer A | Engineer B | Engineer C |
| Thanksgiving | Engineer A | Engineer C | Engineer B | Engineer D |
| Christmas | Engineer B | Engineer D | Engineer C | Engineer A |

This prevents one engineer from consistently receiving the same holiday burden.

---

# 6. Investor Pipeline Runbooks

Runbooks are required for the three pipelines whose metrics are reported to investors:

1. Aggregate Profit
2. Aggregate Growth
3. Aggregate Engagement

The runbooks describe what should be checked when a pipeline does not behave as expected. Because this homework is an imagination exercise, the runbooks identify investigation areas and possible failure conditions rather than prescribing exact remediation procedures.

---

## 6.1 Aggregate Profit Pipeline Runbook

### Purpose

Produces aggregate profit metrics used in investor reporting.

### Ownership

- **Primary:** Engineer B
- **Secondary:** Engineer D

### Expected inputs

Possible upstream data includes:

- revenue transactions;
- refunds;
- discounts;
- cost-of-goods data;
- operating costs;
- accounting adjustments;
- currency conversion data;
- business-calendar data.

### Expected output

A reconciled aggregate profit dataset for the required investor-reporting period.

### Schedule, dependencies, and service objectives

The Aggregate Profit pipeline is treated as a critical investor-reporting workload with explicit operating targets.

| Control | Target |
|---|---|
| Normal daily schedule | Airflow DAG `aggregate_profit_investor_reporting` starts at 05:00 UTC daily |
| Normal completion target | Dataset available by 08:00 UTC |
| Month-end close target | Dataset available by 06:00 UTC after required Finance close inputs are available |
| Primary upstream dependencies | Revenue/subledger feed, cost feed, approved accounting adjustments, currency-rate reference data, business calendar |
| Orchestration | Airflow DAG `aggregate_profit_investor_reporting` |
| Transformation | dbt selector `tag:aggregate_profit_investor_reporting` |
| Monitoring | Airflow dashboard, data-observability dashboard, data-quality results, lineage graph |
| Logs | Airflow task logs plus warehouse/dbt execution logs |

Operational links should be maintained in the team runbook using environment-specific placeholders such as:

- Airflow: `<AIRFLOW_AGGREGATE_PROFIT_DAG_URL>`
- Observability: `<AGGREGATE_PROFIT_OBSERVABILITY_URL>`
- Lineage: `<AGGREGATE_PROFIT_LINEAGE_URL>`
- Data dictionary: `<AGGREGATE_PROFIT_DATA_DICTIONARY_URL>`
- Secrets / credentials runbook: `<PLATFORM_ACCESS_RUNBOOK_URL>`
- Incident channel: `#data-investor-incidents`
- Finance coordination channel: `#finance-data-reporting`

### SLA, RTO, and RPO targets

| Objective | Target |
|---|---|
| Data freshness SLO | Available by 08:00 UTC daily; month-end close target 06:00 UTC once required source systems close |
| Alert acknowledgment | 15 minutes during business hours; 30 minutes off-hours |
| Sev1 mitigation target | Within 2 hours during business hours; within 4 hours off-hours |
| Sev2 resolution target | Within 1 business day or an approved workaround |
| RTO | 4 hours for restoration of an investor-reporting-ready dataset |
| RPO | 24 hours maximum for reconstructable daily data; zero intentional loss of finalized investor-reporting periods |
| Backfill verification | Reprocessed periods must pass reconciliation and quality checks before release |

### Concrete data-quality guardrails

| Test | Guardrail |
|---|---|
| Primary-key uniqueness | No duplicate aggregate business keys for a reporting period |
| Required fields | No nulls in reporting period, revenue, recognized cost, profit, currency, or approved reporting dimensions |
| Row-count anomaly | Investigate changes greater than 20% versus the previous comparable period unless explained by a known business event |
| Revenue reconciliation | Aggregate revenue must reconcile to the approved revenue source/subledger within 0.5% or have a documented variance explanation |
| Cost reconciliation | Aggregate cost must reconcile to approved cost sources within 0.5% or have a documented variance explanation |
| Profit arithmetic | `profit = revenue - recognized_costs - approved_adjustments` must hold for every published aggregate |
| Currency coverage | 100% of non-base-currency records must have an approved exchange rate for the reporting date |
| Referential integrity | All reporting categories and account mappings must resolve to approved reference data |
| Reporting-period completeness | All expected partitions / business dates for the reporting period must be present |
| Schema contract | No unapproved breaking schema change may enter the investor-reporting dataset |

These controls may be implemented with dbt tests, Great Expectations, Monte Carlo or equivalent observability tooling, and targeted SQL reconciliation checks. The exact implementation should be linked from the operational locations above.

### Reconciliation and reproducibility

Before investor-facing publication:

1. reconcile total revenue to the approved revenue source or subledger;
2. reconcile recognized costs to the approved cost source;
3. verify material accounting adjustments against the Finance-approved adjustment list;
4. compare current-period profit to the prior comparable period and explain material variance;
5. retain the reconciliation result and sign-off evidence;
6. pin the deployed transformation code version / Git commit;
7. record the dbt package / semantic-layer version;
8. record reference-data versions, seeds, mappings, and currency-rate snapshots;
9. record the runtime environment / configuration used for the published result.

Any unexplained variance above the defined threshold blocks release until Finance and Data Engineering approve the exception.

### Quick triage and known-good checks

Initial triage should include:

1. Confirm Airflow DAG `aggregate_profit_investor_reporting` started.
2. Confirm all upstream tasks completed successfully.
3. Review the latest data-quality test results.
4. Compare record counts to the previous comparable period.
5. Reconcile total revenue and total cost to approved sources.
6. Review recent code, schema, mapping, or currency-rate changes.
7. Confirm the reporting-period partition is complete.
8. Compare profit margin and total profit to recent comparable periods and investigate unexplained material deviations.

Example validation queries should test uniqueness, nullability, reconciliation totals, partition completeness, and material period-over-period variance.

### Rerun and backfill procedure

For a failed or corrected reporting period:

1. identify the affected reporting date or range;
2. confirm upstream source corrections are complete;
3. record the incident or change ticket;
4. rerun the Airflow DAG for the affected logical date or approved backfill range;
5. execute the Aggregate Profit dbt selector and required tests;
6. rerun reconciliation against the approved Finance sources;
7. compare the corrected result to the previously produced result;
8. obtain Finance sign-off before republishing materially changed investor-facing numbers;
9. retain backfill parameters, code version, test evidence, and reconciliation evidence.

Backfills must be idempotent and must not double-count previously processed transactions.

### On-call procedure and escalation

When an Aggregate Profit alert pages:

1. the primary on-call engineer acknowledges within the applicable SLA;
2. verify Airflow run/task state and identify the first failed or delayed dependency;
3. inspect data-quality and reconciliation dashboards;
4. check task and warehouse logs;
5. classify the incident using the Sev1/Sev2/Sev3 model;
6. page Engineer B, the pipeline primary owner, for Sev1 or specialized Finance-domain issues;
7. involve Engineer D for orchestration, infrastructure, or recovery issues;
8. involve the Finance Controller role for reconciliation or accounting-definition issues;
9. involve Data Governance when semantic definitions, lineage, or approved mappings are in question;
10. notify Data Engineering leadership and Investor Relations / Corporate Communications when investor reporting may be delayed or materially incorrect.

### Incident and change RACI

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Initial incident triage | Primary on-call | Data Engineering lead | Secondary on-call, pipeline owners | Relevant stakeholders |
| Finance reconciliation | Engineer B / Finance analyst | Finance Controller | Data Governance | Data Engineering leadership |
| Platform recovery | Engineer D | Data Engineering lead | Platform/Infrastructure | Pipeline owners |
| Metric-definition change | Assigned engineer | Finance + Data Governance | Pipeline owners | Investor-reporting stakeholders |
| Investor-impacting communication | Incident commander | Data Engineering leadership | Finance, Investor Relations / Communications | Executive stakeholders |

### Change management and reporting freeze

Investor-facing metric logic is governed more strictly than experimentation logic.

- Metric-definition, mapping, semantic-layer, or material transformation changes require approval from Data Governance and Finance.
- Every approved change must reference a ticket, pull request, reviewer, deployment version, and effective reporting date.
- A changelog is maintained for investor-facing metric definitions and transformations.
- Semantic-layer definitions and reference mappings are versioned.
- A reporting freeze begins 48 hours before a scheduled investor-reporting deadline unless an emergency change is explicitly approved.
- During the freeze, only Sev1 corrective changes or approved reporting-critical fixes may be deployed.
- Pre-release validation requires successful automated tests, reconciliation, peer review, and Finance sign-off.
- Any post-publication correction requires impact analysis, documented approval, and a retained record of the original and corrected values.

### Operational checks

When investigating the pipeline, examine:

- whether the scheduled run started;
- whether the run completed;
- upstream source availability;
- row-count changes;
- duplicate records;
- missing partitions;
- schema changes;
- null values in important financial fields;
- unexpected negative or zero values;
- late-arriving transactions;
- currency conversion completeness;
- reporting-period boundaries;
- reconciliation against source totals;
- unexpected changes from prior reporting periods.

### Potential failure scenarios

The pipeline could be affected by:

- delayed revenue feeds;
- missing cost data;
- duplicate transactions;
- incorrectly processed refunds;
- currency conversion errors;
- stale exchange rates;
- missing accounting adjustments;
- upstream schema changes;
- incorrect joins;
- partial source loads;
- incorrect fiscal-period boundaries;
- timezone errors;
- backfills that double-count previously processed data;
- logic changes that alter historical calculations;
- orchestration failures;
- storage or warehouse availability problems;
- permissions or credential failures;
- corrupted source files;
- unexpected null values;
- unusually large or small financial values.

### Investor-reporting risks

Because this metric is externally reported, particular attention should be given to:

- reproducibility;
- reconciliation;
- calculation consistency;
- complete reporting periods;
- late corrections;
- unexplained material changes.

---

## 6.2 Aggregate Growth Pipeline Runbook

### Purpose

Produces aggregate growth metrics used in investor reporting.

### Ownership

- **Primary:** Engineer C
- **Secondary:** Engineer A

### Expected inputs

Possible upstream data includes:

- customer or account records;
- subscription events;
- user registrations;
- acquisition data;
- activation events;
- cancellations;
- churn events;
- historical population snapshots.

### Expected output

A validated aggregate growth dataset for investor reporting.

### Schedule, dependencies, and service objectives

The Aggregate Growth pipeline is a critical investor-reporting workload that converts customer and account lifecycle activity into governed growth metrics.

| Control | Target |
|---|---|
| Normal daily schedule | Airflow DAG `aggregate_growth_investor_reporting` starts at 05:30 UTC daily |
| Normal completion target | Dataset available by 08:30 UTC |
| Reporting-window target | Final reporting-period dataset available at least 24 hours before investor-package lock |
| Primary upstream dependencies | Customer/account master, registrations, acquisition, activation, subscription, cancellation, churn, identity-resolution outputs, historical snapshots |
| Orchestration | Airflow DAG `aggregate_growth_investor_reporting` |
| Transformation | dbt selector `tag:aggregate_growth_investor_reporting` |
| Monitoring | Airflow dashboard, observability dashboard, identity-quality dashboard, lineage graph |
| Logs | Airflow task logs plus warehouse/dbt execution logs |

Operational references should be maintained with environment-specific placeholders such as:

- Airflow: `<AIRFLOW_AGGREGATE_GROWTH_DAG_URL>`
- Observability: `<AGGREGATE_GROWTH_OBSERVABILITY_URL>`
- Identity quality: `<CUSTOMER_IDENTITY_QUALITY_URL>`
- Lineage: `<AGGREGATE_GROWTH_LINEAGE_URL>`
- Data dictionary: `<AGGREGATE_GROWTH_DATA_DICTIONARY_URL>`
- Secrets / credentials runbook: `<PLATFORM_ACCESS_RUNBOOK_URL>`
- Incident channel: `#data-investor-incidents`
- Growth coordination channel: `#growth-data-reporting`

### SLA, RTO, and RPO targets

| Objective | Target |
|---|---|
| Data freshness SLO | Available by 08:30 UTC daily |
| Reporting-window readiness | Final validated reporting-period result available at least 24 hours before investor-package lock |
| Alert acknowledgment | 15 minutes during business hours; 30 minutes off-hours |
| Sev1 mitigation target | Within 2 hours during business hours; within 4 hours off-hours |
| Sev2 resolution target | Within 1 business day or an approved workaround |
| RTO | 4 hours for restoration of an investor-reporting-ready dataset |
| RPO | 24 hours maximum for reconstructable daily lifecycle data; finalized reporting snapshots must remain reproducible |
| Backfill verification | Corrected periods must pass identity, reconciliation, and trend checks before release |

### Concrete data-quality guardrails

| Test | Guardrail |
|---|---|
| Entity uniqueness | No duplicate canonical customer/account identifier within the same governed population snapshot |
| Required identifiers | No null canonical entity ID for records included in published growth metrics |
| Referential integrity | Acquisition, activation, subscription, cancellation, and churn events must resolve to a governed customer/account identity where required |
| Population reconciliation | Ending population must reconcile to beginning population plus additions minus removals within defined business rules |
| Distinct-count anomaly | Investigate population changes greater than 15% versus the previous comparable period unless explained by an approved business event |
| Identity-resolution anomaly | Investigate sudden merge/split rates above 2% of the reporting population |
| Duplicate registration rate | Less than 0.5% unresolved duplicates in the investor-reporting population |
| Reporting-period completeness | 100% of expected daily snapshots or partitions must exist for the reporting period |
| Late-arriving events | Events arriving after the reporting cutoff must be quantified and evaluated before publication |
| Schema contract | No unapproved breaking schema changes in governed growth sources or output |

These controls may be implemented through dbt tests, Great Expectations, Monte Carlo or equivalent observability tooling, identity-resolution QA, and targeted SQL checks.

### Reconciliation and reproducibility

Before investor-facing publication:

1. reconcile beginning population to the prior approved reporting-period ending population;
2. reconcile new customers/accounts to governed acquisition or registration sources;
3. reconcile churn, cancellations, and removals to approved lifecycle sources;
4. validate identity merge/split effects and retain exception evidence;
5. verify beginning population plus additions minus removals equals ending population under approved business rules;
6. compare current growth rates to prior comparable periods and explain material deviations;
7. pin the deployed transformation code version / Git commit;
8. record semantic-layer definitions, identity rules, mappings, seeds, and reference-data versions;
9. retain the exact reporting cutoff timestamp and runtime configuration used to produce published numbers.

Unexplained reconciliation differences or material identity-definition changes block publication until reviewed by Growth leadership, Data Engineering, and Data Governance.

### Quick triage and known-good checks

Initial triage should include:

1. Confirm Airflow DAG `aggregate_growth_investor_reporting` started.
2. Confirm customer/account master and lifecycle sources completed.
3. Check identity-resolution job status and merge/split anomaly metrics.
4. Compare canonical entity counts with the prior comparable period.
5. Validate additions, removals, and ending population arithmetic.
6. Review missing partitions and late-arriving event counts.
7. Review recent metric-definition, identity-rule, schema, or source changes.
8. Compare growth percentage and net additions to recent known-good periods.

A large increase in growth without a corresponding acquisition or registration increase should be treated as suspicious until validated.

### Rerun and backfill procedure

For a failed or corrected reporting period:

1. identify the affected reporting period and exact lifecycle cutoff;
2. confirm upstream customer/account and identity-resolution corrections are complete;
3. record the incident or approved change ticket;
4. rerun the Airflow DAG for the approved logical date or backfill window;
5. execute the Aggregate Growth dbt selector and required tests;
6. rerun identity-quality and population reconciliation checks;
7. compare corrected growth metrics against the previously produced values;
8. obtain Growth business owner and Data Governance approval for materially changed published metrics;
9. retain backfill parameters, code version, identity-rule version, tests, reconciliation evidence, and sign-off.

Backfills must preserve historical reporting cutoffs and must not silently apply current identity rules to historical periods unless the restatement is explicitly approved.

### On-call procedure and escalation

When an Aggregate Growth alert pages:

1. the primary on-call engineer acknowledges within the applicable SLA;
2. verify Airflow DAG and task status;
3. identify the earliest delayed or failed upstream lifecycle dependency;
4. inspect identity-resolution and data-quality dashboards;
5. classify the incident using the Sev1/Sev2/Sev3 model;
6. page Engineer C for customer-identity, lifecycle, or growth-modeling issues;
7. involve Engineer A for analytics, semantic-layer, or metric-definition investigation;
8. involve the Growth Analytics / Growth PMO role for business-definition or reporting-impact questions;
9. involve Data Governance for identity rules, semantic definitions, lineage, or restatement questions;
10. notify Data Engineering leadership and Investor Relations / Corporate Communications for potential investor-reporting impact.

### Incident and change RACI

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Initial incident triage | Primary on-call | Data Engineering lead | Secondary on-call, pipeline owners | Relevant stakeholders |
| Identity reconciliation | Engineer C | Growth Analytics lead | Data Governance, Engineer A | Data Engineering leadership |
| Semantic / metric review | Engineer A | Growth business owner | Engineer C, Data Governance | Investor-reporting stakeholders |
| Platform recovery | Assigned on-call / platform engineer | Data Engineering lead | Pipeline owners | Growth stakeholders |
| Investor-impacting communication | Incident commander | Data Engineering leadership | Growth leadership, Investor Relations / Communications | Executive stakeholders |

### Change management and reporting freeze

- Customer, account, activation, churn, and growth definitions used for investor reporting are governed definitions.
- Identity-resolution rule changes require Data Governance approval and documented impact analysis.
- Material metric-definition changes require Growth business owner plus Data Governance approval.
- Every approved change references a ticket, pull request, reviewer, deployment version, and effective reporting date.
- Identity rules, mappings, semantic-layer definitions, seeds, and reference data are versioned.
- A reporting freeze begins 48 hours before the investor-reporting cutoff unless an emergency correction is explicitly approved.
- During the freeze, only Sev1 corrective work or approved reporting-critical changes may be deployed.
- Pre-release sign-off requires successful automated tests, population reconciliation, identity-quality review, peer review, and business-owner approval.
- Restatements must retain both original and corrected values plus the reason, approver, and effective date.

### Operational checks

When investigating the pipeline, examine:

- scheduled execution;
- upstream source freshness;
- record counts;
- distinct entity counts;
- duplicate users or accounts;
- missing date partitions;
- unexpected nulls;
- late-arriving records;
- changes to account or customer identifiers;
- changes to growth definitions;
- reporting-window boundaries;
- beginning-versus-ending population calculations;
- historical comparison trends;
- unexplained discontinuities.

### Potential failure scenarios

The pipeline could be affected by:

- delayed account events;
- duplicated registrations;
- deleted or merged accounts;
- churn events arriving late;
- inconsistent customer identifiers;
- historical records being rewritten;
- incorrect date filtering;
- timezone boundaries;
- incomplete partitions;
- schema changes;
- failed joins;
- changing business definitions;
- backfills;
- malformed source records;
- orchestration failures;
- warehouse outages;
- permission failures;
- accidental double counting;
- incomplete snapshot generation.

### Investor-reporting risks

Growth metrics can be materially distorted by relatively small definition changes. Particular attention should therefore be given to:

- metric-definition consistency;
- cohort boundaries;
- customer identity;
- beginning and ending populations;
- backfills;
- restatements;
- unexplained trend changes.

---

## 6.3 Aggregate Engagement Pipeline Runbook

### Purpose

Produces aggregate engagement metrics used in investor reporting.

### Ownership

- **Primary:** Engineer A
- **Secondary:** Engineer D

### Expected inputs

Possible upstream data includes:

- application events;
- website events;
- session events;
- user activity;
- device identifiers;
- authentication events;
- content interaction events.

### Expected output

Validated aggregate engagement metrics for the investor-reporting period.

### Schedule, dependencies, and service objectives

The Aggregate Engagement pipeline is a critical investor-reporting workload that converts application, web, session, authentication, and interaction events into governed engagement metrics.

| Control | Target |
|---|---|
| Normal daily schedule | Airflow DAG `aggregate_engagement_investor_reporting` starts at 06:00 UTC daily |
| Normal completion target | Dataset available by 09:00 UTC |
| Reporting-window target | Final validated reporting-period dataset available at least 24 hours before investor-package lock |
| Primary upstream dependencies | Application events, web events, sessions, authentication, user activity, device identity, content interactions, governed event dictionary |
| Orchestration | Airflow DAG `aggregate_engagement_investor_reporting` |
| Transformation | dbt selector `tag:aggregate_engagement_investor_reporting` |
| Monitoring | Airflow dashboard, event-observability dashboard, schema-quality dashboard, lineage graph |
| Logs | Airflow task logs, event-processing logs, warehouse/dbt execution logs |

Operational references should be maintained with environment-specific placeholders such as:

- Airflow: `<AIRFLOW_AGGREGATE_ENGAGEMENT_DAG_URL>`
- Observability: `<AGGREGATE_ENGAGEMENT_OBSERVABILITY_URL>`
- Event quality: `<ENGAGEMENT_EVENT_QUALITY_URL>`
- Lineage: `<AGGREGATE_ENGAGEMENT_LINEAGE_URL>`
- Data dictionary: `<ENGAGEMENT_DATA_DICTIONARY_URL>`
- Event taxonomy: `<EVENT_TAXONOMY_URL>`
- Secrets / credentials runbook: `<PLATFORM_ACCESS_RUNBOOK_URL>`
- Incident channel: `#data-investor-incidents`
- Engagement coordination channel: `#engagement-data-reporting`

### SLA, RTO, and RPO targets

| Objective | Target |
|---|---|
| Data freshness SLO | Available by 09:00 UTC daily |
| Reporting-window readiness | Final validated reporting-period result available at least 24 hours before investor-package lock |
| Alert acknowledgment | 15 minutes during business hours; 30 minutes off-hours |
| Sev1 mitigation target | Within 2 hours during business hours; within 4 hours off-hours |
| Sev2 resolution target | Within 1 business day or an approved workaround |
| RTO | 4 hours for restoration of an investor-reporting-ready dataset |
| RPO | 24 hours maximum for reconstructable daily engagement data; finalized reporting snapshots must remain reproducible |
| Backfill verification | Corrected periods must pass event-quality, completeness, deduplication, and trend checks before release |

### Concrete data-quality guardrails

| Test | Guardrail |
|---|---|
| Event uniqueness | Duplicate event rate below 0.5% after approved deduplication rules |
| Required fields | No null event timestamp, governed event name, user/session identifier where required, or reporting-period key |
| Event-volume anomaly | Investigate daily event-volume changes greater than 20% versus the previous comparable period unless explained by a known release or business event |
| Active-entity anomaly | Investigate changes greater than 15% in daily or monthly active entities versus comparable periods unless explained |
| Schema conformity | 100% of investor-reporting events must conform to the approved schema contract or approved compatibility rule |
| Event taxonomy | Published metrics may use only approved governed event names and definitions |
| Partition completeness | 100% of expected event-date partitions for the reporting period must be present |
| Late-arriving events | Late events beyond the reporting cutoff must be measured and assessed before publication |
| Session integrity | Session start/end and duration logic must satisfy approved business rules |
| Identity coverage | Required authenticated activity must resolve to governed identity mappings within the approved threshold |

These controls may be implemented with dbt tests, Great Expectations, Monte Carlo or equivalent observability tooling, event-schema contracts, and targeted SQL validation.

### Reconciliation and reproducibility

Before investor-facing publication:

1. reconcile total governed event volume against approved source ingestion totals;
2. verify active-user, active-account, and session calculations against the approved semantic definitions;
3. quantify duplicate suppression, malformed-event rejection, and late-arriving-event effects;
4. compare key engagement rates to prior comparable periods and explain material deviations;
5. confirm event-taxonomy and session-definition versions used for the reporting period;
6. pin the deployed transformation code version / Git commit;
7. record dbt package and semantic-layer versions;
8. record event schema, taxonomy, identity-mapping, and reference-data versions;
9. retain the reporting cutoff timestamp and runtime configuration used to produce published numbers.

Unexplained discrepancies in source-event reconciliation, event taxonomy, or active-entity calculations block publication until Engagement Analytics, Data Engineering, and Data Governance approve the result.

### Quick triage and known-good checks

Initial triage should include:

1. Confirm Airflow DAG `aggregate_engagement_investor_reporting` started.
2. Confirm event-ingestion and sessionization dependencies completed.
3. Review source-event freshness and backlog.
4. Compare event volume and distinct active entities with the prior comparable period.
5. Check duplicate, malformed-event, and null-rate dashboards.
6. Review missing partitions and late-arriving event counts.
7. Review recent application releases, event-schema changes, taxonomy changes, or identity-mapping changes.
8. Compare sessions per active user and engagement rate with recent known-good periods.

A material engagement increase without a corresponding rise in source event volume or active entities should be treated as suspicious until validated.

### Rerun and backfill procedure

For a failed or corrected reporting period:

1. identify the affected reporting period and event cutoff;
2. confirm source-event ingestion and any schema corrections are complete;
3. record the incident or approved change ticket;
4. rerun the Airflow DAG for the approved logical date or backfill window;
5. execute the Aggregate Engagement dbt selector and required tests;
6. rerun event-volume, deduplication, session-integrity, and active-entity checks;
7. compare corrected engagement metrics against previously produced values;
8. obtain Engagement Analytics and Data Governance approval for materially changed published metrics;
9. retain backfill parameters, code version, taxonomy version, schema version, tests, reconciliation evidence, and sign-off.

Backfills must use the historically appropriate event taxonomy, session logic, and identity rules unless an explicitly approved restatement requires otherwise.

### On-call procedure and escalation

When an Aggregate Engagement alert pages:

1. the primary on-call engineer acknowledges within the applicable SLA;
2. verify Airflow DAG and task status;
3. identify the earliest delayed or failed event-processing dependency;
4. inspect event-volume, schema-quality, and session-quality dashboards;
5. classify the incident using the Sev1/Sev2/Sev3 model;
6. page Engineer A for event-pipeline, analytics, or semantic issues;
7. involve Engineer D for orchestration, platform, backlog, or recovery issues;
8. involve the Engagement Analytics Lead for business-definition or interpretation issues;
9. involve Data Governance for event taxonomy, semantic definitions, identity rules, lineage, or restatement questions;
10. notify Data Engineering leadership and Investor Relations / Corporate Communications when investor reporting may be delayed or materially incorrect.

### Incident and change RACI

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Initial incident triage | Primary on-call | Data Engineering lead | Secondary on-call, pipeline owners | Relevant stakeholders |
| Event-quality investigation | Engineer A | Engagement Analytics lead | Data Governance, Engineer D | Data Engineering leadership |
| Platform / ingestion recovery | Engineer D | Data Engineering lead | Engineer A, Platform/Infrastructure | Engagement stakeholders |
| Event-taxonomy or metric-definition change | Assigned engineer | Engagement business owner + Data Governance | Pipeline owners | Investor-reporting stakeholders |
| Investor-impacting communication | Incident commander | Data Engineering leadership | Engagement leadership, Investor Relations / Communications | Executive stakeholders |

### Change management and reporting freeze

- Investor-reporting engagement metrics must use governed event and session definitions.
- Event-taxonomy, schema, identity, sessionization, and semantic-definition changes require documented impact analysis.
- Material metric-definition changes require Engagement business owner and Data Governance approval.
- Every approved change references a ticket, pull request, reviewer, deployment version, and effective reporting date.
- Event taxonomy, schema contracts, mappings, semantic definitions, seeds, and reference data are versioned.
- A reporting freeze begins 48 hours before the investor-reporting cutoff unless an emergency correction is explicitly approved.
- During the freeze, only Sev1 corrective work or approved reporting-critical changes may be deployed.
- Pre-release sign-off requires successful automated tests, source-event reconciliation, event-quality review, peer review, and business-owner approval.
- Restatements retain the original and corrected values, definition/version differences, approver, reason, and effective date.

### Operational checks

When investigating the pipeline, examine:

- event-source freshness;
- event volume;
- missing partitions;
- duplicate events;
- malformed events;
- schema changes;
- bot or test traffic;
- sessionization behavior;
- user identity resolution;
- device identity;
- timezone handling;
- event timestamps;
- late-arriving events;
- changes in instrumentation;
- filtering rules;
- aggregation completeness;
- trend changes compared with previous periods.

### Potential failure scenarios

The pipeline could be affected by:

- broken application instrumentation;
- events not being emitted;
- events emitted multiple times;
- delayed message ingestion;
- malformed JSON or payloads;
- renamed event types;
- application releases changing event schemas;
- timezone errors;
- incorrect session boundaries;
- bot traffic;
- internal employee traffic;
- test traffic entering production metrics;
- identity-resolution failures;
- deleted or missing user identifiers;
- event-processing backlog;
- data loss;
- orchestration failures;
- storage failures;
- incomplete partitions;
- late events;
- unexpected spikes caused by instrumentation rather than real user behavior.

### Investor-reporting risks

Engagement is particularly sensitive to instrumentation changes. Investigation should distinguish genuine behavioral changes from data-collection changes.

---

# 7. Potential Problems Across All Five Pipelines

Although each pipeline has domain-specific risks, many failure modes affect all five.

## Upstream data problems

Possible issues include:

- source system unavailable;
- source data delayed;
- incomplete extracts;
- malformed files;
- missing records;
- duplicate records;
- upstream schema changes;
- unexpected null values.

## Transformation problems

Possible issues include:

- incorrect joins;
- duplicate amplification;
- filter changes;
- calculation bugs;
- incorrect aggregation levels;
- accidental changes to business logic;
- bad assumptions about null values;
- incorrect incremental-processing logic.

## Scheduling and orchestration problems

Possible issues include:

- job not triggered;
- job triggered twice;
- dependency not completed;
- retries causing duplicate processing;
- incorrect dependency ordering;
- scheduler outage;
- incorrect environment configuration.

## Time-related problems

Possible issues include:

- timezone inconsistencies;
- daylight-saving changes;
- incorrect reporting windows;
- late-arriving data;
- incorrect partition dates;
- month-end or quarter-end boundary problems.

## Infrastructure problems

Possible issues include:

- database unavailable;
- compute capacity exhausted;
- warehouse unavailable;
- object storage unavailable;
- network failures;
- expired credentials;
- permission changes;
- disk or memory pressure.

## Data-quality problems

Possible issues include:

- unexpected volume changes;
- missing partitions;
- duplicate rows;
- null spikes;
- outliers;
- referential-integrity problems;
- historical data unexpectedly changing.

## Business-definition problems

Possible issues include:

- stakeholder changes metric definition;
- experiment logic differs from investor-reporting logic;
- naming conventions change;
- source-of-truth system changes;
- historical results become non-comparable.

---

# 8. Experiment Pipeline Considerations

The two experiment-oriented pipelines are:

- Unit-Level Profit
- Daily Growth

These pipelines may prioritize lower latency than the investor pipelines, but they still require dependable data.

## Unit-Level Profit

Potential problems include:

- incorrect allocation of costs to individual units;
- missing transaction-level data;
- duplicate units;
- incorrect experiment assignment;
- delayed cost information;
- inconsistent unit identifiers;
- late adjustments changing previously calculated profit.

## Daily Growth

Potential problems include:

- incomplete current-day data;
- late registration events;
- timezone boundaries;
- duplicated accounts;
- changed customer definitions;
- partial daily snapshots;
- experiment cohorts not aligning with production definitions.

---

# 9. Escalation Model

## Incident severity model

| Severity | Definition | Alert Acknowledgment | Target Resolution / Mitigation | Stakeholder Communication |
|---|---|---:|---:|---|
| **Sev1** | Investor-facing data unavailable, materially incorrect, or at risk of missing a reporting window | 15 minutes business hours; 30 minutes off-hours | Mitigate within 2 hours business hours / 4 hours off-hours | Initial update within 30 minutes; hourly updates until mitigated |
| **Sev2** | Material quality regression outside the immediate reporting window, failed critical dependency, or significant data delay without immediate investor impact | 30 minutes business hours; 60 minutes off-hours | Resolve or provide approved workaround within 1 business day | Initial update within 1 hour; update at major status changes |
| **Sev3** | Limited lag, minor defect, documentation issue, or non-critical degradation with a safe workaround | 4 business hours | Resolve within 3 business days or schedule into planned work | Update through normal engineering channels |

For Sev1 investor-impacting incidents, the communication loop should include:

- primary and secondary on-call engineers;
- pipeline primary and secondary owners;
- Head of Data / Data Engineering leadership;
- relevant business owner;
- Finance leadership for profit-related incidents;
- Data Governance for definition or lineage concerns;
- Corporate Communications or Investor Relations when external reporting could be affected.

A standard investor-impacting incident update should state:

1. affected pipeline and reporting period;
2. incident severity;
3. detected impact;
4. current mitigation status;
5. whether previously published numbers may be affected;
6. next update time;
7. incident owner.

## Escalation order

A simple operational escalation path is:

1. Primary on-call engineer
2. Secondary on-call engineer
3. Pipeline primary owner
4. Pipeline secondary owner
5. Relevant upstream/downstream system owner
6. Engineering leadership or business stakeholder when appropriate

Investor-reporting incidents should receive heightened visibility because incorrect external metrics carry greater business and reputational risk.

---

# 10. On-Call Handoff

The weekly handoff is recorded in the team's shared operational handoff document and retained with the pipeline operations documentation.

At each weekly rotation, the outgoing primary should communicate:

- currently failing or degraded pipelines;
- open incidents;
- recent backfills;
- known upstream delays;
- recent schema changes;
- recent releases;
- unusual data-quality observations;
- upcoming reporting deadlines;
- planned maintenance;
- upcoming holidays or PTO.

The incoming primary should confirm receipt of the handoff and access to required monitoring and documentation.

---

# 11. Summary

This operating model distributes the five pipelines across four engineers while ensuring every pipeline has both a primary and secondary owner.

The rotating on-call model gives each engineer an equal share of operational responsibility, and the holiday policy prevents undesirable dates from repeatedly falling on the same engineer.

The three investor-facing pipelines have dedicated runbooks because their metrics require especially strong attention to:

- completeness;
- consistency;
- reconciliation;
- reproducibility;
- reporting-period correctness;
- metric-definition stability.

The objective is not to assume that failures can be completely prevented. Instead, the team should ensure that ownership is clear, operational knowledge is shared, and likely failure modes are understood before incidents occur.
