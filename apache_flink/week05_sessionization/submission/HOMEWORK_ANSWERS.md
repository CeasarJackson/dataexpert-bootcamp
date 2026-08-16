# DataExpert Boot Camp — Apache Flink Sessionization Homework

## Author

Ceasar Jackson

## Assignment Requirements

The assignment requires a Flink job that:

1. Sessionizes incoming web events by IP address and host.
2. Uses a five-minute inactivity gap.
3. Determines the average number of web events in a session.
4. Compares the requested hosts:
   - zachwilson.techcreator.io
   - zachwilson.tech
   - lulu.techcreator.io

## Implementation

The submitted implementation uses Apache Flink's PyFlink Table API.

Session key:

    (ip, host)

Session gap:

    5 minutes

The implementation uses the Flink 1.16-compatible Session window API:

    Session.with_gap(lit(SESSION_GAP_MINUTES).minutes)
        .on(col("event_timestamp"))

The configured constant is:

    SESSION_GAP_MINUTES: int = 5

The source table defines event time and a 15-second watermark.

The session aggregation produces:

- ip
- host
- session_start
- session_end
- event_count

The session grouping is performed by both ip and host.

## Multi-Sink Execution

The completed-session output and host-summary output consume the same
sessionized streaming pipeline.

Both sink INSERT statements are added to one Flink StatementSet and
submitted as one coordinated streaming job.

The final implementation contains:

- one create_statement_set() call
- two add_insert_sql() calls
- one statement_set.execute() call
- one table_result.wait() call

This prevents the two unbounded INSERT statements from being submitted
as unrelated streaming jobs.

## Course Runtime Validation

The implementation was validated using the course-compatible runtime:

- Apache Flink 1.16.2
- PyFlink 1.16.2
- Python 3.7.9

The final module successfully imported under Python 3.7.9.

The Flink 1.16.2 planner successfully accepted the session-window
implementation.

The validated physical plan included:

    SessionGroupWindow('w, event_timestamp, 300000)

and:

    Exchange(distribution=[hash[ip, host]])

The value 300000 milliseconds is five minutes.

This provides runtime evidence that Flink planned a five-minute
session window keyed by ip and host.

## Historical Offline Validation

An offline validation was also performed against the historical
events.csv dataset in the course materials.

Important limitation:

The historical CSV does not contain the live Kafka ip field.
For offline validation only, device_id was used as an identity
surrogate.

The actual submitted Flink job still sessionizes by the assignment's
required key:

    ip + host

Offline validation processed:

- 412,320 source rows
- 6,993 rows for the three requested target hosts
- 0 malformed timestamp rows
- 0 blank identity rows

## Results

| Host | Sessions | Total Events | Avg Events / Session | Min | Max |
|---|---:|---:|---:|---:|---:|
| zachwilson.techcreator.io | 2,521 | 4,339 | 1.721142 | 1 | 51 |
| zachwilson.tech | 1 | 2 | 2.000000 | 2 | 2 |
| lulu.techcreator.io | 1,503 | 2,652 | 1.764471 | 1 | 97 |

## Interpretation

For the historical validation dataset:

- zachwilson.techcreator.io averaged approximately 1.7211 web events
  per session.
- lulu.techcreator.io averaged approximately 1.7645 web events per
  session.
- zachwilson.tech produced one qualifying historical session containing
  two events, for an average of 2.0 events per session.

The zachwilson.tech result has only one session in this particular
offline dataset, so it should not be treated as a robust comparative
estimate.

Among the two hosts with substantial session counts,
lulu.techcreator.io had the higher average events per session.

## Assignment Compliance Summary

The submitted solution satisfies the requested requirements:

- Sessionizes web events by IP address and host.
- Uses a five-minute inactivity gap.
- Calculates event count per session.
- Calculates average events per session.
- Includes all three requested hosts.
- Uses Apache Flink session-window semantics rather than a tumbling
  window.
- Is compatible with the course's Flink 1.16.2 / Python 3.7.9 runtime.
- Uses coordinated StatementSet execution for both streaming sinks.
- Includes historical validation evidence for spot checking.

## Post-Grade Remediation

The submission was hardened after grader feedback to address the missing
operational and SQL deliverables and to strengthen runtime correctness.

### Added SQL Deliverables

The resubmission includes:

- `create_sessionization_tables.sql`
- `avgsessionevents.sql`

`create_sessionization_tables.sql` creates the physical PostgreSQL tables
required by the Flink JDBC sinks.

The host-summary table defines:

    host TEXT PRIMARY KEY

This supports the upsert semantics required by the continuously updating
host-level aggregation.

`avgsessionevents.sql` answers both required analytical questions:

1. Overall Tech Creator average:

       host LIKE '%.techcreator.io'

2. Comparison of:

   - zachwilson.techcreator.io
   - zachwilson.tech
   - lulu.techcreator.io

### Added Makefile Workflow

The resubmission includes these reproducible targets:

    make postgres-init
    make sessionization_job
    make session-metrics

The intended execution order is:

    make postgres-init
    make sessionization_job
    make session-metrics

### JDBC Upsert Hardening

The Flink host-summary connector table now declares:

    PRIMARY KEY (host) NOT ENFORCED

The physical PostgreSQL table defines a real primary key on `host`.

This allows the JDBC connector to process update/changelog records from the
unbounded host aggregation using upsert semantics.

### UTC Event-Time Hardening

Kafka event timestamps contain a trailing `Z`, indicating UTC.

The Flink Table API local timezone is now explicitly pinned to UTC:

    table.local-time-zone = UTC

This prevents JVM-local timezone settings from shifting session event-time
interpretation.

### Configurable Runtime Settings

The following runtime settings are now configurable through environment
variables:

- `FLINK_WATERMARK_SECONDS`
- `FLINK_CHECKPOINT_INTERVAL_MS`
- `KAFKA_STARTUP_MODE`

Defaults remain compatible with the original live pipeline:

- watermark: 15 seconds
- checkpoint interval: 10000 milliseconds
- Kafka startup: latest-offset

For QA/backfill validation, `KAFKA_STARTUP_MODE=earliest-offset` is also
supported.

### PostgreSQL Integration Validation

The remediation SQL was executed against an isolated PostgreSQL 15
container.

Validated behavior included:

- physical DDL execution
- idempotent DDL rerun
- physical host-summary primary key
- overall Tech Creator metric
- all three requested host metrics
- primary-key upsert behavior

A deterministic fixture produced:

- overall Tech Creator average: 4.0000
- zachwilson.techcreator.io: 3.0000
- zachwilson.tech: 8.0000
- lulu.techcreator.io: 6.0000

These values are test-fixture validation results only and are not intended
to replace the historical/offline homework results documented earlier.

## Required Runtime Environment

The Flink runtime requires the course Kafka and PostgreSQL settings,
including:

- `KAFKA_URL`
- `KAFKA_TOPIC`
- `KAFKA_GROUP`
- `KAFKA_WEB_TRAFFIC_KEY`
- `KAFKA_WEB_TRAFFIC_SECRET`
- `POSTGRES_URL`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

Optional runtime-tuning settings are:

- `FLINK_WATERMARK_SECONDS`
- `FLINK_CHECKPOINT_INTERVAL_MS`
- `KAFKA_STARTUP_MODE`

No live credentials are included in the submission.
