# DataExpert Boot Camp — Week 5 Apache Flink Sessionization

## Overview

This workspace contains the Week 5 Apache Flink homework implementation,
validation evidence, reference materials, and grader-facing submission
artifacts.

The assignment requires a Flink job that:

1. Sessionizes incoming web events by IP address and host.
2. Uses a five-minute inactivity gap.
3. Calculates the average number of web events per session.
4. Compares results for:
   - `zachwilson.techcreator.io`
   - `zachwilson.tech`
   - `lulu.techcreator.io`

## Implementation

The validated implementation is located at:

- `scripts/flink_sessionization_homework.py`

The grader-facing copy is located at:

- `submission/flink_sessionization_homework.py`

The two Python files are intentionally identical.

The implementation uses the PyFlink Table API session-window interface
supported by the course runtime:

    Session.with_gap(lit(SESSION_GAP_MINUTES).minutes)
        .on(col("event_timestamp"))

The configured inactivity gap is:

    SESSION_GAP_MINUTES: int = 5

Sessions are grouped by:

    (ip, host)

Each completed session produces:

- `ip`
- `host`
- `session_start`
- `session_end`
- `event_count`

## Course Runtime Compatibility

The final solution was validated with:

- Apache Flink 1.16.2
- PyFlink 1.16.2
- Python 3.7.9

The Flink planner accepted the session-window implementation and produced
a plan containing:

    SessionGroupWindow('w, event_timestamp, 300000)

The value `300000` milliseconds represents the required five-minute
session inactivity gap.

The validated plan also contained:

    Exchange(distribution=[hash[ip, host]])

which confirms partitioning by the homework-required `ip + host` key.

## Coordinated Multi-Sink Execution

The implementation writes two outputs:

1. Completed session detail.
2. Host-level session statistics.

Both streaming INSERT statements are submitted using one Flink
`StatementSet`.

The validated implementation contains:

- one `create_statement_set()` call
- two `add_insert_sql()` calls
- one `statement_set.execute()` call
- one `table_result.wait()` call

This allows both sinks to participate in one coordinated streaming job.

## Historical Offline Validation

An additional offline validation was performed using the historical
`events.csv` file from the course materials.

That historical file does not contain an IP address column. Therefore,
`device_id` was used only as an offline session-identity surrogate.
The actual Flink homework implementation continues to group by `ip`
and `host` as required by the assignment.

Historical results were:

| Host | Sessions | Events | Average Events per Session |
| --- | ---: | ---: | ---: |
| `zachwilson.techcreator.io` | 2,521 | 4,339 | 1.721142 |
| `zachwilson.tech` | 1 | 2 | 2.000000 |
| `lulu.techcreator.io` | 1,503 | 2,652 | 1.764471 |

The `zachwilson.tech` result contains only one qualifying historical
session and therefore is not a robust comparative estimate.

Among the two hosts with substantial historical session counts,
`lulu.techcreator.io` had the higher average number of events per
session.

## Workspace Structure

The Week 5 workspace is organized as follows:

    week05_sessionization/
    ├── README.md
    ├── reference/
    ├── scripts/
    │   ├── flink_sessionization_homework.py
    │   └── validate_submission.sh
    ├── submission/
    │   ├── flink_sessionization_homework.py
    │   ├── HOMEWORK_ANSWERS.md
    │   ├── offline_sessionization_summary.csv
    │   ├── offline_sessionization_summary.json
    │   └── SHA256SUMS.txt
    └── validation/
        ├── logs/
        ├── recovery/
        └── results/

Local validation logs, recovery checkpoints, the full offline
sessionization output, and the generated ZIP package are intentionally
excluded from Git.

## Grader-Facing Submission

The committed `submission/` directory contains exactly five files:

1. `flink_sessionization_homework.py`
2. `HOMEWORK_ANSWERS.md`
3. `offline_sessionization_summary.csv`
4. `offline_sessionization_summary.json`
5. `SHA256SUMS.txt`

Verify submission integrity with:

    cd apache_flink/week05_sessionization/submission
    shasum -a 256 -c SHA256SUMS.txt

## Validation

The workspace includes:

- Python syntax validation.
- Flink 1.16.2 / Python 3.7.9 runtime validation.
- Session-window planner validation.
- StatementSet execution-model validation.
- Historical offline sessionization validation.
- Submission checksum validation.
- Secret-file and credential-literal checks.
- Git whitespace validation.

The Flink 1.16.2 planner successfully confirmed a five-minute session
window grouped by `ip` and `host`.

## Security

No live Kafka credentials, passwords, API keys, or credential environment
files are committed in this workspace.

Runtime credentials are supplied through environment variables.

The `reference/example.env` file is retained only as the upstream
non-secret configuration template.

## Author

Ceasar Jackson
