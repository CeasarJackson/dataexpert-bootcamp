# DataExpert Boot Camp - Week 5 Apache Flink Sessionization
## Final Grade A Record

- **Author:** Ceasar Jackson
- **Assignment:** Week 5 - Apache Flink Sessionization
- **Final grade:** **A**
- **Original graded commit:** `719b2db45c3498d1bd90adbbeed7a8d4b540b91d`
- **Accepted remediation commit:** `7cbae4888bce6907043f6589abc987de8ab92801`
- **Final-state tag:** `week05-flink-final-grade-a`
- **Remediation PR:** `#10`
- **Final grade date:** 2026-08-16

---

## Final Grader Assessment

**FINAL GRADE: A**

The grader confirmed that the Week 5 remediation met the core requirements
and specifically recognized the following strengths:

- Correct sessionization keyed by `(ip, host)`.
- Five-minute session windows.
- Proper event-time semantics and watermarking.
- Explicit UTC Table API timezone configuration.
- Clean PyFlink Table API structure.
- Coordinated multi-sink execution using `StatementSet`.
- Checkpointing.
- Append-only PostgreSQL session sink.
- Upsertable PostgreSQL host-summary sink with a primary key.
- Physical PostgreSQL DDL deliverable.
- Correct analytical SQL deliverables.
- Thorough documentation and validation evidence.
- Reproducible Makefile workflow documentation.

## Assignment Results

Using the offline validation results, the weighted overall Tech Creator
average was approximately:

`1.7373 events/session`

Host comparison:

| Host | Sessions | Average events/session |
|---|---:|---:|
| `zachwilson.techcreator.io` | 2,521 | 1.7211 |
| `zachwilson.tech` | 1 | 2.0000 |
| `lulu.techcreator.io` | 1,503 | 1.7645 |
| Overall `%.techcreator.io` | 4,024 | ~1.7373 |

## Grader Follow-Up Suggestions

The following were characterized as operational or future-polish
opportunities rather than grade-blocking defects:

- Consider `TO_TIMESTAMP_LTZ` after a future Flink upgrade.
- Consider `COUNT(1)` to communicate row-count intent.
- Document recommended watermark values for live versus backfill workloads.
- Normalize hostnames using `LOWER(host)`.
- Consider `sink.parallelism = 1` for the host-summary upsert sink.
- Add an index on `web_event_sessions(host, session_start)`.
- Optionally add defensive `event_count > 0` filtering.
- Add optional time-window filters for period-based analytics.
- Add smoke-check SQL for sink health and recent-session validation.
- Consider schema-registry support if Kafka schemas evolve.

## Makefile Grader-Ingestion Note

The grader reported that the grading system did not recognize the extensionless
`Makefile` artifact:

> The following files were not recognized (unknown format): Makefile (.makefile).

The validated submission ZIP did contain the Makefile. This was an artifact
ingestion limitation rather than a missing submission file.

For future grader-facing packages, consider including both:

- `Makefile`
- `Makefile.txt`

or reproducing the Makefile contents in a recognized Markdown/text document.

## Final Standing

- **Final grade:** A
- **Original graded state preserved:** Yes
- **Post-grade remediation preserved:** Yes
- **Accepted remediation commit tagged:** Yes
- **Submission package independently checksummed:** Yes
- **Final engineering status:** Complete
