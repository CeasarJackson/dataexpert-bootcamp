# =============================================================================
# DataExpert Boot Camp — Week 5 Apache Flink Sessionization
# Makefile
# =============================================================================
#
# Author:
#   Ceasar Jackson
#
# Purpose:
#   Provide reproducible commands for running the Week 5 sessionization job
#   against the course Apache Flink runtime.
#
# Runtime assumptions:
#   - The course Docker Compose Flink cluster has already been started.
#   - The JobManager container is named "jobmanager", as defined by the
#     upstream course docker-compose.yml.
#   - Kafka/PostgreSQL credentials are provided through the course runtime
#     environment and are not stored in this Makefile.
#
# Usage:
#
#   make help
#   make runtime-check
#   make sessionization_job
#
# =============================================================================

SHELL := /bin/bash

JOBMANAGER_CONTAINER ?= jobmanager
POSTGRES_CONTAINER ?= eczachly-flink-postgres
POSTGRES_USER ?= postgres
POSTGRES_DB ?= postgres

LOCAL_JOB := flink_sessionization_homework.py
CONTAINER_JOB := /tmp/flink_sessionization_homework.py

FLINK_BIN := ./bin/flink
PY_FILES := /opt/src

.PHONY: help
help:
	@echo
	@echo "DataExpert Week 5 — Apache Flink Sessionization"
	@echo
	@echo "Targets:"
	@echo "  make runtime-check       Verify the course Flink JobManager is running"
	@echo "  make postgres-init       Create required PostgreSQL sink tables"
	@echo "  make sessionization_job  Submit the Week 5 sessionization job"
	@echo "  make session-metrics     Run the required homework metric queries"
	@echo


.PHONY: runtime-check
runtime-check:
	@docker inspect "$(JOBMANAGER_CONTAINER)" >/dev/null 2>&1 \
		|| { \
			echo "ERROR: Docker container '$(JOBMANAGER_CONTAINER)' does not exist."; \
			echo "Start the upstream course Flink runtime before submitting the job."; \
			exit 1; \
		}
	@docker inspect \
		--format '{{.State.Running}}' \
		"$(JOBMANAGER_CONTAINER)" \
		| grep -qx 'true' \
		|| { \
			echo "ERROR: Docker container '$(JOBMANAGER_CONTAINER)' is not running."; \
			exit 1; \
		}
	@echo "PASS: course Flink JobManager is running"


.PHONY: sessionization_job
sessionization_job: runtime-check
	@test -f "$(LOCAL_JOB)" \
		|| { \
			echo "ERROR: missing local job: $(LOCAL_JOB)"; \
			exit 1; \
		}
	@echo "Copying validated Week 5 job into the course JobManager..."
	docker cp \
		"$(LOCAL_JOB)" \
		"$(JOBMANAGER_CONTAINER):$(CONTAINER_JOB)"
	@echo "Submitting Week 5 Flink sessionization job..."
	docker exec \
		"$(JOBMANAGER_CONTAINER)" \
		"$(FLINK_BIN)" run \
		-py "$(CONTAINER_JOB)" \
		--pyFiles "$(PY_FILES)" \
		-d


.PHONY: postgres-init
postgres-init:
	@test -f "create_sessionization_tables.sql" \
		|| { \
			echo "ERROR: missing create_sessionization_tables.sql"; \
			exit 1; \
		}
	@docker inspect "$(POSTGRES_CONTAINER)" >/dev/null 2>&1 \
		|| { \
			echo "ERROR: PostgreSQL container '$(POSTGRES_CONTAINER)' does not exist."; \
			exit 1; \
		}
	@echo "Creating Week 5 PostgreSQL sink tables..."
	docker exec -i \
		"$(POSTGRES_CONTAINER)" \
		psql \
		-U "$(POSTGRES_USER)" \
		-d "$(POSTGRES_DB)" \
		-v ON_ERROR_STOP=1 \
		< create_sessionization_tables.sql


.PHONY: session-metrics
session-metrics:
	@test -f "avgsessionevents.sql" \
		|| { \
			echo "ERROR: missing avgsessionevents.sql"; \
			exit 1; \
		}
	@docker inspect "$(POSTGRES_CONTAINER)" >/dev/null 2>&1 \
		|| { \
			echo "ERROR: PostgreSQL container '$(POSTGRES_CONTAINER)' does not exist."; \
			exit 1; \
		}
	@echo "Running Week 5 required session metrics..."
	docker exec -i \
		"$(POSTGRES_CONTAINER)" \
		psql \
		-U "$(POSTGRES_USER)" \
		-d "$(POSTGRES_DB)" \
		-v ON_ERROR_STOP=1 \
		< avgsessionevents.sql
