# DataExpert Boot Camp — Curriculum Traceability

## Purpose
This document maps the official DataExpert.io Community Edition curriculum to repository artifacts that demonstrate implementation, validation, grading, remediation, and technical capability.

> Academy module numbers and repository week numbers are not equivalent.

## Traceability Matrix

| Academy Module | Curriculum Area | Repository Evidence | Assessment / Evidence | Demonstrated Capabilities |
|---|---|---|---|---|
| 1 | Bootcamp Orientation | No dedicated implementation directory | Orientation only | Environment setup and onboarding |
| 2 | Dimensional Data Modeling | `dimensional_data_modeling/week01_actor_films/` | `week01-graded-a`; `grade_feedback/week01/` | Complex types, cumulative modeling, SCD concepts, historical state modeling |
| 3 | Fact Data Modeling | `fact_data_modeling/week02_devices_events/` | `week02-graded-a`, `week02-remediated-a`, `week02-remediated-final-a` | Fact grain, deduplication, cumulative activity, reduced facts |
| 4 | Apache Spark Fundamentals | `spark_fundamentals/week03_halo/` | `week03-graded-a`, `week03-remediated-final-a` | PySpark, broadcast joins, bucket joins, partitioning, testing |
| 5 | Applying Analytical Patterns | `analytical_patterns/week04_analytical_patterns/`; `homework/knucknuclear/` | `week04-graded-a`, `week04-remediated-a` | Growth accounting, grouping sets, windows, cardinality reduction |
| 6 | Flink and Kafka | `CeasarJackson_Week5_Apache_Flink_Sessionization.zip`; upstream Flink reference material | `week05-flink-post-grade-remediation` | Flink, Kafka, PostgreSQL, event time, watermarks, sessionization |
| 7 | Data Visualization and Impact | `data_visualization/tableau_homework/` | `week07-graded-b`; later remediation grade A | Tableau, KPI design, pre-aggregation, extracts, Tableau Public |
| 8 | Data Pipeline Maintenance | `data_pipeline_maintenance/week05_pipeline_maintenance/` | Graded-A archive and remediation evidence | Ownership, on-call, runbooks, failure analysis, reliability |
| 9 | KPIs and Experimentation | `kpis_and_experimentation/week09_kpis_experimentation/` | Submission, validation logs, checksum | Experiment design, leading/lagging KPIs, guardrails |
| 10 | Data Quality Patterns | Curriculum/reference coverage; no dedicated graded assignment directory evident | No assignment listed in supplied curriculum | MIDAS, spec building, WAP, quality checks, data trust |

## Numbering Caveat
Do not rename existing graded or validated directories solely to match academy numbering. Use this file as the canonical mapping layer.

## Recommended Uses
- Repository navigation
- Resume and LinkedIn evidence mapping
- Interview preparation
- Portfolio documentation
- Skill inventorying
- Assignment provenance
- Post-grade remediation tracking
