# DataExpert Boot Camp - Week 5 Apache Flink Sessionization
## Grader Feedback Archive and Post-Grade Remediation Record

- **Author:** Ceasar Jackson
- **Assignment:** Week 5 - Apache Flink Sessionization
- **Recorded grade:** **B**
- **Original graded commit:** `719b2db45c3498d1bd90adbbeed7a8d4b540b91d`
- **Post-grade remediation branch:** `remediation/week05-post-grade-hardening`
- **Archive date:** 2026-08-16

> **Grade-status note:** The recorded grade remains **B** unless and until DataExpert.io Community Academy issues a regrade. The grader stated that addressing the identified gaps would make the submission "A-level"; that statement is preserved as grader feedback, not represented here as a revised grade.

---

# Original Grader Feedback

The following feedback is preserved from the grader response supplied by Ceasar Jackson.

**DataExpert.io Community Academy logo**

**FINAL GRADE: B**

Hi Ceasar — thanks for the thorough submission. You’ve clearly put care into the engineering of the Flink job, and your documentation shows you validated the core sessionization logic. Below is detailed feedback aligned to the rubric, plus a few concrete fixes/improvements to make your solution rock solid and fully compliant with the deliverables.

## What’s working well

Correct sessionization: You key by (ip, host) and use a 5-minute Session window, with event-time and a watermark. Good filtering of blank/null identities.

Clean structure: Clear separation of concerns (source, view, sinks, environment), and good use of StatementSet for multi-sink planning.

Sensible operational choices: Checkpointing enabled, modest parallelism, environment variables for secrets, and nice run-time prints.

Results and reasoning: You provided host-level averages and explained the offline validation limitations.

## Gaps against the assignment deliverables

### 1) Missing SQL script

The assignment asks for an SQL script to compute the metrics. Your job writes sessionized rows to Postgres (great), but you didn’t include a separate avgsessionevents.sql. Please add a simple script that:

Computes the overall Tech Creator average (e.g., all hosts ending with .techcreator.io).

Compares the three specified hosts.

Suggested avgsessionevents.sql: -- Average events per session for all Tech Creator subdomains SELECT AVG(eventcount)::numeric(10,4) AS avgeventspersessiontechcreator FROM webevent_sessions WHERE host LIKE '%.techcreator.io';

-- Average events per session by specified hosts SELECT host, AVG(eventcount)::numeric(10,4) AS avgeventspersession FROM webeventsessions WHERE host IN ('zachwilson.techcreator.io', 'zachwilson.tech', 'lulu.techcreator.io') GROUP BY host ORDER BY host;

### 2) Makefile target not provided

Please add a Makefile target (sessionization_job) that starts your job in the course runtime. Example:

sessionizationjob: docker compose exec jobmanager \\ flink run -py /opt/src/job/flinksessionization_homework.py -d

If your repo uses a different path/layout, adjust accordingly and include brief run instructions in the README or HOMEWORK_ANSWERS.md.

### 3) JDBC sink for host summary needs a primary key (planner/upsert semantics)

Your host summary sink is an unbounded aggregation (GROUP BY host) and will emit updates as new sessions arrive. The JDBC connector requires a primary key to handle upserts. Without a PK, planning or runtime can fail.

Fix: declare a (not enforced) primary key on host in the Flink DDL and create a physical table with a real PRIMARY KEY in Postgres.

Flint DDL change (host summary): CREATE TABLE webeventsessionhostsummary ( host VARCHAR, sessioncount BIGINT, totalevents BIGINT, avgeventspersession DOUBLE, PRIMARY KEY (host) NOT ENFORCED ) WITH ( 'connector' = 'jdbc', 'url' = '', 'table-name' = 'webeventsessionhost_summary', 'username' = '', 'password' = '', 'driver' = 'org.postgresql.Driver' );

Postgres physical table: CREATE TABLE IF NOT EXISTS webeventsessionhostsummary ( host TEXT PRIMARY KEY, sessioncount BIGINT NOT NULL, totalevents BIGINT NOT NULL, avgeventsper_session DOUBLE PRECISION NOT NULL );

### 4) Physical table creation

Flink’s JDBC DDL registers a connector table, but it does not create the physical Postgres tables. Please include a small SQL DDL file that creates both target tables ahead of time:

-- sessions table (append-only) CREATE TABLE IF NOT EXISTS webeventsessions ( ip TEXT NOT NULL, host TEXT NOT NULL, sessionstart TIMESTAMP(3) NOT NULL, sessionend TIMESTAMP(3) NOT NULL, event_count BIGINT NOT NULL );

-- host summary (upsertable) CREATE TABLE IF NOT EXISTS webeventsessionhostsummary ( host TEXT PRIMARY KEY, sessioncount BIGINT NOT NULL, totalevents BIGINT NOT NULL, avgeventsper_session DOUBLE PRECISION NOT NULL );

## Correctness and robustness notes

### Event time parsing/time zone

Your TO_TIMESTAMP with a literal 'Z' parses the timestamp as local time, discarding the fact the source is UTC. This can shift timestamps if the JVM isn’t set to UTC.

Options to fix:

Explicitly pin the table local time zone to UTC at startup: tenv.getconfig().set("table.local-time-zone", "UTC")

Or parse to epoch and then to TIMESTAMPLTZ (works in Flink 1.16): eventtsms AS UNIXTIMESTAMP(eventtime, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''') * 1000, eventtimestamp AS TOTIMESTAMPLTZ(eventtsms, 3)

Either way, ensure your session window times truly reflect UTC input.

### Watermark tolerance

A 15-second watermark may be tight for out-of-order Kafka events. If you observe prematurely closed sessions, consider bumping this to 60–120s.

### Startup offsets

You use latest-offset, which is fine for a live pipeline, but for initial backfills and QA, consider earliest-offset during validation runs.

## Clarity of answers

You answered the per-host averages using the offline dataset and explained the limitations. Good.

The question “What is the average number of web events per session for a user on Tech Creator?” suggests an overall figure for the Tech Creator platform. Please add the “overall Tech Creator” average (e.g., host LIKE '%.techcreator.io') as a single number alongside the per-host comparison.

## Testing instructions to add

Prereqs:

Confirm the JDBC and Kafka connector JARs plus Postgres driver are on the classpath of your Flink cluster.

Provide a .env or documentation listing required env vars:

KAFKAURL, KAFKATOPIC, KAFKAGROUP, KAFKAWEBTRAFFICKEY, KAFKAWEBTRAFFIC_SECRET

POSTGRESURL, POSTGRESUSER, POSTGRES_PASSWORD

Steps:

Create Postgres tables (run the provided DDL SQL).

make sessionization_job (or the equivalent docker compose command).

Verify writes:

SELECT COUNT(*) FROM webeventsessions;

Run avgsessionevents.sql to produce the requested metrics.

## Minor code polish suggestions

Make watermark and checkpoint intervals configurable via env vars.

Consider adding restart strategy to the StreamExecutionEnvironment for resilience.

For the Kafka source, consider 'json.ignore-parse-errors' = 'true' if you expect imperfect data.

## Overall assessment

Strong Flink job and thoughtful engineering choices. You met the core sessionization requirement and wrote sessions to Postgres. The main gaps are deliverables (SQL script, Makefile target), host-summary sink upsert semantics (missing PK), and time zone parsing. Address those and this is an A-level submission.

If anything in my review environment assumptions doesn’t match yours, please provide:

Your Makefile and/or exact runtime command(s).

docker-compose.yml (if used), especially how connector JARs are provisioned.

The physical Postgres DDL you used (if any) and the database connection details format (e.g., POSTGRES_URL).

A short sample of the raw Kafka event_time strings to double-check the parser/time zone.

---

# Post-Grade Remediation Record

This section was added after grading. It is **not** part of the original grader response.

## Remediation summary

The post-grade hardening work was performed on the dedicated branch `remediation/week05-post-grade-hardening`, preserving the original graded commit `719b2db45c3498d1bd90adbbeed7a8d4b540b91d`.

| Grader finding | Remediation status | Evidence / implementation |
|---|---|---|
| Missing `avgsessionevents.sql` | Addressed | Added `sql/avgsessionevents.sql` and a portable grader-facing copy. It computes the overall `%.techcreator.io` average and compares all three requested hosts. |
| Missing Makefile target | Addressed | Added `sessionization_job`; also added `runtime-check`, `postgres-init`, and `session-metrics`. The grader-facing Makefile was adapted to work from the extracted flat submission package. |
| Host-summary JDBC sink lacked PK/upsert semantics | Addressed | Flink DDL now declares `PRIMARY KEY (host) NOT ENFORCED`; physical PostgreSQL summary table defines `host TEXT PRIMARY KEY`. |
| Physical PostgreSQL tables not provided | Addressed | Added `create_sessionization_tables.sql` for both `web_event_sessions` and `web_event_session_host_summary`. |
| UTC event-time interpretation | Addressed | Table local timezone is explicitly pinned with `table.local-time-zone = UTC`. |
| Watermark tolerance was fixed at 15 seconds | Hardened | `FLINK_WATERMARK_SECONDS` is configurable; default remains 15 seconds. |
| Checkpoint interval fixed in code | Hardened | `FLINK_CHECKPOINT_INTERVAL_MS` is configurable; default remains 10,000 ms. |
| Latest-offset only | Hardened | `KAFKA_STARTUP_MODE` supports both `latest-offset` and `earliest-offset`; live default remains `latest-offset`. |
| Overall Tech Creator metric missing | Addressed | Added explicit `host LIKE '%.techcreator.io'` metric query. |
| Required environment variables needed documentation | Addressed | `HOMEWORK_ANSWERS.md` documents Kafka/PostgreSQL runtime variables and optional tuning variables. |
| Restart strategy suggestion | Optional / not implemented in the evidence reviewed | Grader characterized this as a minor polish suggestion; no restart-strategy validation evidence was produced in the remediation log supplied for this archive. |
| `json.ignore-parse-errors` suggestion | Optional / not implemented in the evidence reviewed | Grader characterized this as a minor polish suggestion; no implementation evidence was produced in the remediation log supplied for this archive. |
| Connector JAR / Postgres driver classpath confirmation | Course-runtime dependent | The job was repeatedly validated in the course-compatible Flink 1.16.2 / Python 3.7.9 environment; this archive does not independently inventory every connector JAR. |

## PostgreSQL integration evidence

The new SQL/DDL deliverables were executed against an isolated PostgreSQL 15 validation container.

Validated behavior included:

- Both physical tables created successfully.
- Re-running the DDL was idempotent (`CREATE TABLE IF NOT EXISTS`).
- `web_event_session_host_summary` had exactly one primary key on `host`.
- The host-summary table accepted an insert followed by an `ON CONFLICT (host) DO UPDATE` operation without creating a duplicate row.
- The final upsert result was `session_count=3`, `total_events=9`, `avg_events_per_session=3` with exactly one summary row.

## Deterministic metric validation

A controlled four-session fixture was used solely to validate the required SQL calculations:

| Host | Session event counts | Expected average | Validated average |
|---|---:|---:|---:|
| `zachwilson.techcreator.io` | 2, 4 | 3.0000 | 3.0000 |
| `lulu.techcreator.io` | 6 | 6.0000 | 6.0000 |
| `zachwilson.tech` | 8 | 8.0000 | 8.0000 |
| Overall `%.techcreator.io` | 2, 4, 6 | 4.0000 | 4.0000 |

These deterministic fixture values are validation evidence only; they do not replace the historical/offline results included in the homework submission.

## Grader-facing remediation package

The hardened submission package contains eight files:

1. `flink_sessionization_homework.py`
2. `HOMEWORK_ANSWERS.md`
3. `Makefile`
4. `avgsessionevents.sql`
5. `create_sessionization_tables.sql`
6. `offline_sessionization_summary.csv`
7. `offline_sessionization_summary.json`
8. `SHA256SUMS.txt`

The package checksum manifest was regenerated after remediation and all seven payload files verified successfully.

## Current standing

- **Recorded grade:** B
- **Original graded commit preserved:** Yes
- **Post-grade remediation performed:** Yes
- **Revised grade:** Not established in the supplied evidence
- **Grader characterization after proposed fixes:** “Address those and this is an A-level submission.”
