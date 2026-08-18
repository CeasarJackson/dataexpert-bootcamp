# Week 5 — Data Pipeline Maintenance

**Student:** Ceasar Jackson
**Discord:** knucknuclear

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
