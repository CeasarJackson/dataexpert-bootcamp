#!/usr/bin/env python3
"""
===============================================================================
DataExpert Boot Camp - Apache Flink Sessionization Homework
===============================================================================

Author:
    Ceasar Jackson

Purpose:
    Implement the Week 5 Apache Flink homework requirements:

    1. Sessionize incoming web events by IP address and host.
    2. Use a five-minute inactivity gap.
    3. Calculate the average number of web events per session.
    4. Compare results for:
         - zachwilson.techcreator.io
         - zachwilson.tech
         - lulu.techcreator.io

Design:
    This implementation uses Flink SQL/Table API session windows rather than
    fixed tumbling windows.

    A SESSION window is required because a session is defined by inactivity:
    when no new event arrives for the same grouping key for five minutes, the
    current session closes.

Important:
    This file intentionally contains no Kafka passwords, API keys, or other
    secrets. Runtime credentials are supplied through environment variables.

Usage:
    Submit inside the course Flink runtime, for example:

        ./bin/flink run \
            -py /opt/src/job/flink_sessionization_homework.py \
            --pyFiles /opt/src \
            -d

===============================================================================
"""

from __future__ import annotations

import os
import sys
from typing import Tuple

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment
from pyflink.table.expressions import col, lit
from pyflink.table.window import Session


SESSION_GAP_MINUTES: int = 5

TARGET_HOSTS: Tuple[str, ...] = (
    "zachwilson.techcreator.io",
    "zachwilson.tech",
    "lulu.techcreator.io",
)


def require_env(name: str) -> str:
    """
    Return a required environment variable.

    Raises:
        RuntimeError: If the variable is absent or blank.
    """
    value = os.environ.get(name, "").strip()

    if not value:
        raise RuntimeError(
            f"Required environment variable is missing or empty: {name}"
        )

    return value


def create_events_source_kafka(t_env: StreamTableEnvironment) -> str:
    """
    Register the Kafka source containing bootcamp web events.

    The source schema follows the upstream DataExpert Flink training material.
    Event time is converted to a Flink TIMESTAMP and assigned a watermark so
    event-time session windows can close correctly.
    """
    table_name = "events"

    kafka_key = require_env("KAFKA_WEB_TRAFFIC_KEY")
    kafka_secret = require_env("KAFKA_WEB_TRAFFIC_SECRET")
    kafka_url = require_env("KAFKA_URL")
    kafka_topic = require_env("KAFKA_TOPIC")
    kafka_group = require_env("KAFKA_GROUP")

    timestamp_pattern = "yyyy-MM-dd''T''HH:mm:ss.SSS''Z''"

    source_ddl = f"""
        CREATE TABLE {table_name} (
            url VARCHAR,
            referrer VARCHAR,
            user_agent VARCHAR,
            host VARCHAR,
            ip VARCHAR,
            headers VARCHAR,
            event_time VARCHAR,
            event_timestamp AS TO_TIMESTAMP(event_time, '{timestamp_pattern}'),
            WATERMARK FOR event_timestamp
                AS event_timestamp - INTERVAL '15' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = '{kafka_url}',
            'topic' = '{kafka_topic}',
            'properties.group.id' = '{kafka_group}',
            'properties.security.protocol' = 'SASL_SSL',
            'properties.sasl.mechanism' = 'PLAIN',
            'properties.sasl.jaas.config' =
                'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="{kafka_key}" password="{kafka_secret}";',
            'scan.startup.mode' = 'latest-offset',
            'properties.auto.offset.reset' = 'latest',
            'format' = 'json'
        )
    """

    t_env.execute_sql(source_ddl)

    return table_name


def create_session_sink_postgres(t_env: StreamTableEnvironment) -> str:
    """
    Register a PostgreSQL sink containing one row per completed session.
    """
    table_name = "web_event_sessions"

    postgres_url = require_env("POSTGRES_URL")
    postgres_user = os.environ.get("POSTGRES_USER", "postgres")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "postgres")

    sink_ddl = f"""
        CREATE TABLE {table_name} (
            ip VARCHAR,
            host VARCHAR,
            session_start TIMESTAMP(3),
            session_end TIMESTAMP(3),
            event_count BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = '{postgres_url}',
            'table-name' = '{table_name}',
            'username' = '{postgres_user}',
            'password' = '{postgres_password}',
            'driver' = 'org.postgresql.Driver'
        )
    """

    t_env.execute_sql(sink_ddl)

    return table_name


def create_host_summary_sink_postgres(
    t_env: StreamTableEnvironment,
) -> str:
    """
    Register a PostgreSQL sink containing host-level session statistics.
    """
    table_name = "web_event_session_host_summary"

    postgres_url = require_env("POSTGRES_URL")
    postgres_user = os.environ.get("POSTGRES_USER", "postgres")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "postgres")

    sink_ddl = f"""
        CREATE TABLE {table_name} (
            host VARCHAR,
            session_count BIGINT,
            total_events BIGINT,
            avg_events_per_session DOUBLE
        ) WITH (
            'connector' = 'jdbc',
            'url' = '{postgres_url}',
            'table-name' = '{table_name}',
            'username' = '{postgres_user}',
            'password' = '{postgres_password}',
            'driver' = 'org.postgresql.Driver'
        )
    """

    t_env.execute_sql(sink_ddl)

    return table_name


def build_session_view(
    t_env: StreamTableEnvironment,
    source_table: str,
) -> str:
    """
    Create a temporary view containing one row per IP/host session.

    Apache Flink 1.16.2 does not support SESSION as a SQL windowing TVF.
    The supported PyFlink 1.16 session-window API is therefore used here.

    Sessions are keyed by the homework-required pair:

        (ip, host)

    A session closes after five minutes of inactivity.
    """
    view_name = "sessionized_events"

    source = (
        t_env.from_path(source_table)
        .filter(
            col("ip").is_not_null
            & (col("ip").trim() != "")
            & col("host").is_not_null
            & (col("host").trim() != "")
        )
    )

    sessionized = (
        source
        .window(
            Session
            .with_gap(lit(SESSION_GAP_MINUTES).minutes)
            .on(col("event_timestamp"))
            .alias("w")
        )
        .group_by(
            col("ip"),
            col("host"),
            col("w"),
        )
        .select(
            col("ip"),
            col("host"),
            col("w").start.alias("session_start"),
            col("w").end.alias("session_end"),
            col("ip").count.alias("event_count"),
        )
    )

    t_env.create_temporary_view(
        view_name,
        sessionized,
    )

    return view_name

def add_sessions_insert(
    statement_set,
    session_view: str,
    session_sink: str,
) -> None:
    """
    Add the completed-session PostgreSQL insert to the shared StatementSet.

    Both homework sinks consume the same unbounded sessionized stream. Adding
    their INSERT statements to one StatementSet allows Flink to plan and
    submit them as a single coordinated streaming job rather than launching
    independent jobs from separate execute_sql() calls.
    """
    statement_set.add_insert_sql(
        f"""
            INSERT INTO {session_sink}
            SELECT
                ip,
                host,
                session_start,
                session_end,
                event_count
            FROM {session_view}
        """
    )


def add_host_summary_insert(
    statement_set,
    session_view: str,
    summary_sink: str,
) -> None:
    """
    Add host-level session statistics to the shared StatementSet.

    The aggregate is intentionally derived from the same sessionized temporary
    view used by the detailed session sink so both outputs share identical
    five-minute session semantics.
    """
    host_literals = ", ".join(f"'{host}'" for host in TARGET_HOSTS)

    statement_set.add_insert_sql(
        f"""
            INSERT INTO {summary_sink}
            SELECT
                host,
                COUNT(*) AS session_count,
                SUM(event_count) AS total_events,
                CAST(AVG(event_count) AS DOUBLE) AS avg_events_per_session
            FROM {session_view}
            WHERE host IN ({host_literals})
            GROUP BY host
        """
    )


def configure_environment() -> StreamTableEnvironment:
    """
    Create the Flink streaming execution and table environments.
    """
    env = StreamExecutionEnvironment.get_execution_environment()

    env.enable_checkpointing(10_000)
    env.set_parallelism(3)

    settings = (
        EnvironmentSettings.new_instance()
        .in_streaming_mode()
        .build()
    )

    return StreamTableEnvironment.create(
        env,
        environment_settings=settings,
    )


def run() -> None:
    """
    Configure and execute the Week 5 sessionization pipeline.
    """
    print("=" * 72)
    print("DataExpert Week 5 - Apache Flink Sessionization Homework")
    print("=" * 72)
    print(f"Session gap: {SESSION_GAP_MINUTES} minutes")
    print("Session key: ip + host")
    print("Target hosts:")

    for host in TARGET_HOSTS:
        print(f"  - {host}")

    t_env = configure_environment()

    source_table = create_events_source_kafka(t_env)
    session_sink = create_session_sink_postgres(t_env)
    summary_sink = create_host_summary_sink_postgres(t_env)

    session_view = build_session_view(
        t_env,
        source_table,
    )

    # Submit both unbounded sink statements as one coordinated Flink job.
    #
    # Calling execute_sql() separately for multiple streaming INSERT
    # statements can create independent long-running jobs. StatementSet is
    # the appropriate Table API mechanism when multiple sinks consume the
    # same streaming pipeline.
    statement_set = t_env.create_statement_set()

    print("Adding completed-session sink to StatementSet...")
    add_sessions_insert(
        statement_set,
        session_view,
        session_sink,
    )

    print("Adding host-summary sink to StatementSet...")
    add_host_summary_insert(
        statement_set,
        session_view,
        summary_sink,
    )

    print("Submitting coordinated multi-sink Flink job...")
    table_result = statement_set.execute()

    print(
        "PASS: coordinated Flink job submitted "
        f"(Job ID: {table_result.get_job_client().get_job_id()})"
    )

    # Streaming execution is intentionally blocking here so that a foreground
    # invocation remains attached to the submitted job and propagates runtime
    # failures to the caller.
    table_result.wait()


def main() -> int:
    """
    Program entry point with explicit failure reporting.
    """
    try:
        run()
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(
            f"ERROR: Flink sessionization job failed: {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
