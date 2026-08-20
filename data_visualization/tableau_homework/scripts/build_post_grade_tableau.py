#!/usr/bin/env python3
"""
===============================================================================
DataExpert Boot Camp — Week 7 Post-Grade Tableau Builder
===============================================================================

Author:
    Ceasar Jackson

Project:
    DataExpert Boot Camp — Data Visualization / Tableau Homework

Purpose:
    Build a post-grade Tableau derivative from the verified Week 7 graded
    workbook while preserving the graded artifact byte-for-byte.

    This phase adds three purpose-built live CSV data sources:

        * map_performance
        * medal_distribution
        * medal_per_match

    Hyper extracts are intentionally NOT fabricated. Tableau Desktop will be
    allowed to create native extract metadata after the live data sources have
    been validated successfully.

Safety:
    * Requires the post-grade hardening branch.
    * Requires the exact verified graded workbook SHA-256.
    * Never modifies the graded source workbook.
    * Rebuilds the candidate deterministically from the graded source.
    * Validates all source CSV schemas before workbook generation.
    * Validates generated workbook XML.
    * Verifies the graded source remains immutable.

Usage:
    python3 \
      data_visualization/tableau_homework/scripts/build_post_grade_tableau.py
===============================================================================
"""

from __future__ import annotations

import csv
import hashlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

# Preserve Tableau's canonical user namespace prefix during XML
# serialization. Without registration, ElementTree emits ns0.
ET.register_namespace(
    "user",
    "http://www.tableausoftware.com/xml/user",
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BRANCH = "improve/week07-post-grade-hardening"

ROOT = Path("data_visualization/tableau_homework")

SOURCE = (
    ROOT
    / "tableau"
    / "CeasarJackson_DataExpert_Tableau_Homework_FINAL_20260818_221605.twb"
)

CANDIDATE = (
    ROOT
    / "tableau"
    / "CeasarJackson_DataExpert_Tableau_Homework_POST_GRADE.twb"
)

DATA_DIR = ROOT / "data" / "prepared" / "post_grade"

EXPECTED_SOURCE_SHA256 = (
    "49d7b7648933f26097298c0f9519716bc7dcec23ea829a0230f93e294d245fe8"
)


DATASOURCES = (
    {
        "caption": "post_grade_map_performance",
        "name": "federated.postgrade.map.performance",
        "connection_name": "textscan.postgrade.map.performance",
        "connection_caption": "Post-Grade Map Performance",
        "filename": "map_performance.csv",
        "hyper_filename": "map_performance.hyper",
        "fields": (
            ("map_id", "string", "dimension", "nominal"),
            ("map_name", "string", "dimension", "nominal"),
            ("match_count", "integer", "measure", "quantitative"),
            ("player_match_count", "integer", "measure", "quantitative"),
            ("distinct_players", "integer", "measure", "quantitative"),
            ("medal_count", "integer", "measure", "quantitative"),
            ("medals_per_match", "real", "measure", "quantitative"),
            (
                "medals_per_player_match",
                "real",
                "measure",
                "quantitative",
            ),
        ),
    },
    {
        "caption": "post_grade_medal_distribution",
        "name": "federated.postgrade.medal.distribution",
        "connection_name": "textscan.postgrade.medal.distribution",
        "connection_caption": "Post-Grade Medal Distribution",
        "filename": "medal_distribution.csv",
        "hyper_filename": "medal_distribution.hyper",
        "fields": (
            ("medal_rank", "integer", "dimension", "ordinal"),
            ("medal_id", "string", "dimension", "nominal"),
            ("medal_name", "string", "dimension", "nominal"),
            ("medal_count", "integer", "measure", "quantitative"),
            ("share_of_medals", "real", "measure", "quantitative"),
        ),
    },
    {
        "caption": "post_grade_medal_per_match",
        "name": "federated.postgrade.medal.per.match",
        "connection_name": "textscan.postgrade.medal.per.match",
        "connection_caption": "Post-Grade Medal Per Match",
        "filename": "medal_per_match.csv",
        "hyper_filename": "medal_per_match.hyper",
        "fields": (
            ("match_count", "integer", "measure", "quantitative"),
            (
                "player_match_count",
                "integer",
                "measure",
                "quantitative",
            ),
            (
                "matches_with_medal_rows",
                "integer",
                "measure",
                "quantitative",
            ),
            (
                "matches_without_medal_rows",
                "integer",
                "measure",
                "quantitative",
            ),
            ("medal_count", "integer", "measure", "quantitative"),
            ("medals_per_match", "real", "measure", "quantitative"),
            (
                "medals_per_player_match",
                "real",
                "measure",
                "quantitative",
            ),
        ),
    },
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def die(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def passed(message: str) -> None:
    print(f"PASS: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def pretty_caption(field: str) -> str:
    return field.replace("_", " ").title()


def remote_type(datatype: str) -> str:
    mapping = {
        "string": "129",
        "integer": "20",
        "real": "5",
    }

    try:
        return mapping[datatype]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported Tableau datatype: {datatype}"
        ) from exc


def aggregation(datatype: str) -> str:
    if datatype == "string":
        return "Count"

    return "Sum"


def validate_csv_schema(spec: dict[str, object]) -> None:
    filename = str(spec["filename"])
    path = DATA_DIR / filename

    if not path.is_file():
        die(f"required post-grade CSV missing: {path}")

    fields = spec["fields"]
    expected = [field[0] for field in fields]

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as stream:
        reader = csv.reader(stream)

        try:
            actual = next(reader)
        except StopIteration:
            die(f"CSV is empty: {path}")

    if actual != expected:
        die(
            f"CSV schema mismatch: {path}\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}"
        )

    passed(f"CSV schema: {filename}")


def csv_data_row_count(path: Path) -> int:
    """Return the number of data rows in a header-based CSV file."""

    if not path.is_file():
        raise FileNotFoundError(
            f"CSV source does not exist: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as stream:
        reader = csv.reader(stream)

        try:
            next(reader)
        except StopIteration as exc:
            raise ValueError(
                f"CSV source is empty: {path}"
            ) from exc

        return sum(1 for _row in reader)


def object_token(filename: str) -> str:
    stem = filename.removesuffix(".csv")
    digest = hashlib.sha256(
        filename.encode("utf-8")
    ).hexdigest()[:32].upper()

    return f"{stem}.csv_{digest}"


def add_text(parent: ET.Element, tag: str, value: str) -> ET.Element:
    node = ET.SubElement(parent, tag)
    node.text = value
    return node


def build_metadata_records(
    parent: ET.Element,
    filename: str,
    fields: tuple[tuple[str, str, str, str], ...],
    object_id: str,
) -> None:
    records = ET.SubElement(parent, "metadata-records")

    capability = ET.SubElement(
        records,
        "metadata-record",
        {"class": "capability"},
    )

    ET.SubElement(capability, "remote-name")
    add_text(capability, "remote-type", "0")
    add_text(capability, "parent-name", f"[{filename}]")
    ET.SubElement(capability, "remote-alias")
    add_text(capability, "aggregation", "Count")
    add_text(capability, "contains-null", "true")

    attributes = ET.SubElement(capability, "attributes")

    capability_attributes = (
        ("character-set", '"UTF-8"'),
        ("collation", '"en_US"'),
        ("field-delimiter", '","'),
        ("header-row", '"true"'),
        ("locale", '"en_US"'),
        ("single-char", '""'),
    )

    for name, value in capability_attributes:
        attribute = ET.SubElement(
            attributes,
            "attribute",
            {
                "datatype": "string",
                "name": name,
            },
        )
        attribute.text = value

    for ordinal, field in enumerate(fields):
        name, datatype, _role, _field_type = field

        record = ET.SubElement(
            records,
            "metadata-record",
            {"class": "column"},
        )

        add_text(record, "remote-name", name)
        add_text(record, "remote-type", remote_type(datatype))
        add_text(record, "local-name", f"[{name}]")
        add_text(record, "parent-name", f"[{filename}]")
        add_text(record, "remote-alias", name)
        add_text(record, "ordinal", str(ordinal))
        add_text(record, "local-type", datatype)
        add_text(record, "aggregation", aggregation(datatype))

        if datatype == "string":
            add_text(record, "scale", "1")
            add_text(record, "width", "1073741823")

        add_text(record, "contains-null", "true")

        if datatype == "string":
            ET.SubElement(
                record,
                "collation",
                {
                    "flag": "0",
                    "name": "LEN_RUS",
                },
            )

        add_text(record, "object-id", f"[{object_id}]")


def build_datasource(spec: dict[str, object]) -> ET.Element:
    caption = str(spec["caption"])
    datasource_name = str(spec["name"])
    connection_name = str(spec["connection_name"])
    connection_caption = str(spec["connection_caption"])
    filename = str(spec["filename"])
    fields = spec["fields"]

    object_id = object_token(filename)

    datasource = ET.Element(
        "datasource",
        {
            "caption": caption,
            "inline": "true",
            "name": datasource_name,
            "version": "18.1",
        },
    )

    connection = ET.SubElement(
        datasource,
        "connection",
        {"class": "federated"},
    )

    named_connections = ET.SubElement(
        connection,
        "named-connections",
    )

    named_connection = ET.SubElement(
        named_connections,
        "named-connection",
        {
            "caption": connection_caption,
            "name": connection_name,
        },
    )

    ET.SubElement(
        named_connection,
        "connection",
        {
            "class": "textscan",
            "directory": str(DATA_DIR.resolve()),
            "filename": filename,
            "password": "",
            "server": "",
        },
    )

    relation = ET.SubElement(
        connection,
        "relation",
        {
            "connection": connection_name,
            "name": filename,
            "table": f"[{filename.removesuffix('.csv')}#csv]",
            "type": "table",
        },
    )

    columns = ET.SubElement(
        relation,
        "columns",
        {
            "character-set": "UTF-8",
            "header": "yes",
            "locale": "en_US",
            "separator": ",",
        },
    )

    for ordinal, field in enumerate(fields):
        name, datatype, _role, _field_type = field

        ET.SubElement(
            columns,
            "column",
            {
                "datatype": datatype,
                "name": name,
                "ordinal": str(ordinal),
            },
        )

    build_metadata_records(
        connection,
        filename,
        fields,
        object_id,
    )

    ET.SubElement(
        datasource,
        "aliases",
        {"enabled": "yes"},
    )

    ET.SubElement(
        datasource,
        "column",
        {
            "caption": filename,
            "datatype": "table",
            "name": (
                "[__tableau_internal_object_id__]."
                f"[{object_id}]"
            ),
            "role": "measure",
            "type": "quantitative",
        },
    )

    for name, datatype, role, field_type in fields:
        ET.SubElement(
            datasource,
            "column",
            {
                "caption": pretty_caption(name),
                "datatype": datatype,
                "name": f"[{name}]",
                "role": role,
                "type": field_type,
            },
        )

    object_graph = ET.SubElement(
        datasource,
        "object-graph",
    )

    objects = ET.SubElement(object_graph, "objects")

    obj = ET.SubElement(
        objects,
        "object",
        {
            "caption": filename,
            "id": object_id,
        },
    )

    properties = ET.SubElement(
        obj,
        "properties",
        {"context": ""},
    )

    ET.SubElement(
        properties,
        "relation",
        {
            "connection": connection_name,
            "name": filename,
            "table": f"[{filename.removesuffix('.csv')}#csv]",
            "type": "table",
        },
    )

    return datasource




def hyper_update_time(hyper_path: Path) -> str:
    """Return Hyper mtime formatted like Tableau TWB update-time metadata."""

    modified = hyper_path.stat().st_mtime

    modified_utc = datetime.fromtimestamp(
        modified,
        tz=timezone.utc,
    )

    return modified_utc.strftime(
        "%m/%d/%Y %I:%M:%S %p"
    )


def add_post_grade_extract(
    datasource: ET.Element,
    hyper_path: Path,
    csv_path: Path,
) -> None:
    """Attach a local Hyper extract and Tableau refresh lineage."""

    hyper_path = hyper_path.resolve()
    csv_path = csv_path.resolve()

    if not hyper_path.is_file():
        raise FileNotFoundError(
            f"Hyper extract does not exist: {hyper_path}"
        )

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"CSV source does not exist: {csv_path}"
        )

    if datasource.find("./extract") is not None:
        raise ValueError(
            "Datasource already contains an extract; refusing duplicate"
        )

    object_graph = datasource.find("./object-graph")

    if object_graph is None:
        raise ValueError(
            "Datasource has no object-graph"
        )

    object_graph_index = list(datasource).index(
        object_graph
    )

    extract = ET.Element(
        "extract",
        {
            "count": "-1",
            "enabled": "true",
            "object-id": "",
            "units": "records",
            "user-specific": "false",
        },
    )

    # Tableau datasource XML uses an ordered content model.
    # The extract must precede later datasource metadata such as
    # object-graph; appending it after object-graph causes Tableau
    # Desktop to reject the workbook during XML validation.
    datasource.insert(
        object_graph_index,
        extract,
    )

    connection = ET.SubElement(
        extract,
        "connection",
        {
            "access_mode": "readonly",
            "authentication": "auth-none",
            "author-locale": "en_US",
            "class": "hyper",
            "dbname": str(hyper_path),
            "default-settings": "yes",
            "schema": "Extract",
            "sslmode": "",
            "tablename": "Extract",
            "update-time": hyper_update_time(hyper_path),
            "username": "tableau_internal_user",
        },
    )

    ET.SubElement(
        connection,
        "relation",
        {
            "name": "Extract",
            "table": "[Extract].[Extract]",
            "type": "table",
        },
    )

    # Tableau requires extract-level field metadata for generated fields to
    # remain fully resolvable after save/publish. The I20 experiment proved
    # that refresh lineage alone is not sufficient for PG02 field/sort
    # validity. Mirror the extract field metadata Tableau writes natively.
    filename = csv_path.name
    fields = None

    for spec in DATASOURCES:
        if str(spec["filename"]) == filename:
            fields = spec["fields"]
            break

    if fields is None:
        raise ValueError(
            f"No datasource field specification found for CSV: {filename}"
        )

    object_id = object_token(filename)

    extract_records = ET.SubElement(
        connection,
        "metadata-records",
    )

    for ordinal, field in enumerate(fields):
        name, datatype, _role, _field_type = field

        record = ET.SubElement(
            extract_records,
            "metadata-record",
            {"class": "column"},
        )

        add_text(record, "remote-name", name)
        add_text(record, "remote-type", remote_type(datatype))
        add_text(record, "local-name", f"[{name}]")
        add_text(record, "remote-alias", name)
        add_text(record, "local-type", datatype)
        add_text(record, "aggregation", aggregation(datatype))
        add_text(record, "parent-name", "[Extract]")
        add_text(record, "ordinal", str(ordinal))
        add_text(record, "family", filename)
        add_text(record, "approx-count", str(csv_data_row_count(csv_path)))
        add_text(record, "contains-null", "false")

        if datatype == "string":
            ET.SubElement(
                record,
                "collation",
                {
                    "flag": "0",
                    "name": "LEN_RUS",
                },
            )

        add_text(record, "object-id", f"[{object_id}]")

    refresh = ET.SubElement(
        connection,
        "refresh",
    )

    ET.SubElement(
        refresh,
        "refresh-event",
        {
            "add-from-file-path": csv_path.stem,
            "increment-value": "%null%",
            "refresh-type": "create",
            "rows-inserted": str(csv_data_row_count(csv_path)),
            "timestamp-start": (
                datetime.now(timezone.utc)
                .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            ),
        },
    )

    obj = object_graph.find("./objects/object")

    if obj is None:
        raise ValueError(
            "Datasource object-graph has no object"
        )

    existing_extract_context = obj.find(
        "./properties[@context='extract']"
    )

    if existing_extract_context is not None:
        raise ValueError(
            "Datasource already contains extract object-graph context"
        )

    properties = ET.SubElement(
        obj,
        "properties",
        {
            "context": "extract",
        },
    )

    ET.SubElement(
        properties,
        "relation",
        {
            "name": "Extract",
            "table": "[Extract].[Extract]",
            "type": "table",
        },
    )


def build_pg01_map_performance_worksheet() -> ET.Element:
    """Build the minimal PG 01 map-performance validation worksheet."""

    datasource_caption = "post_grade_map_performance"
    datasource_name = "federated.postgrade.map.performance"

    worksheet = ET.Element(
        "worksheet",
        {"name": "PG 01 — Map Performance"},
    )

    table = ET.SubElement(worksheet, "table")
    view = ET.SubElement(table, "view")

    view_datasources = ET.SubElement(view, "datasources")

    ET.SubElement(
        view_datasources,
        "datasource",
        {
            "caption": datasource_caption,
            "name": datasource_name,
        },
    )

    dependencies = ET.SubElement(
        view,
        "datasource-dependencies",
        {"datasource": datasource_name},
    )

    ET.SubElement(
        dependencies,
        "column",
        {
            "caption": "Map Name",
            "datatype": "string",
            "name": "[map_name]",
            "role": "dimension",
            "type": "nominal",
        },
    )

    ET.SubElement(
        dependencies,
        "column",
        {
            "caption": "Medals Per Match",
            "datatype": "real",
            "name": "[medals_per_match]",
            "role": "measure",
            "type": "quantitative",
        },
    )

    ET.SubElement(
        dependencies,
        "column-instance",
        {
            "column": "[map_name]",
            "derivation": "None",
            "name": "[none:map_name:nk]",
            "pivot": "key",
            "type": "nominal",
        },
    )

    ET.SubElement(
        dependencies,
        "column-instance",
        {
            "column": "[medals_per_match]",
            "derivation": "Sum",
            "name": "[sum:medals_per_match:qk]",
            "pivot": "key",
            "type": "quantitative",
        },
    )

    ET.SubElement(
        view,
        "aggregation",
        {"value": "true"},
    )

    ET.SubElement(table, "style")

    panes = ET.SubElement(table, "panes")

    pane = ET.SubElement(
        panes,
        "pane",
        {
            "selection-relaxation-option":
                "selection-relaxation-allow"
        },
    )

    pane_view = ET.SubElement(pane, "view")

    ET.SubElement(
        pane_view,
        "breakdown",
        {"value": "auto"},
    )

    ET.SubElement(
        pane,
        "mark",
        {"class": "Automatic"},
    )

    rows = ET.SubElement(table, "rows")
    rows.text = (
        f"[{datasource_name}]."
        "[none:map_name:nk]"
    )

    cols = ET.SubElement(table, "cols")
    cols.text = (
        f"[{datasource_name}]."
        "[sum:medals_per_match:qk]"
    )

    # Tableau worksheet content model requires a simple-id after <table>.
    # Use a fixed UUID so candidate generation remains deterministic.
    ET.SubElement(
        worksheet,
        "simple-id",
        {
            "uuid":
                "{8C4D42E1-5D92-4C69-9DB2-"
                "9B85B22E1A01}"
        },
    )

    return worksheet


def build_pg02_medal_distribution_worksheet() -> ET.Element:
    """Build the minimal PG 02 medal-distribution validation worksheet."""

    datasource_caption = "post_grade_medal_distribution"
    datasource_name = "federated.postgrade.medal.distribution"

    worksheet = ET.Element(
        "worksheet",
        {"name": "PG 02 — Medal Distribution"},
    )

    table = ET.SubElement(worksheet, "table")
    view = ET.SubElement(table, "view")

    view_datasources = ET.SubElement(view, "datasources")

    ET.SubElement(
        view_datasources,
        "datasource",
        {
            "caption": datasource_caption,
            "name": datasource_name,
        },
    )

    dependencies = ET.SubElement(
        view,
        "datasource-dependencies",
        {"datasource": datasource_name},
    )

    ET.SubElement(
        dependencies,
        "column",
        {
            "caption": "Medal Name",
            "datatype": "string",
            "name": "[medal_name]",
            "role": "dimension",
            "type": "nominal",
        },
    )

    ET.SubElement(
        dependencies,
        "column",
        {
            "caption": "Medal Count",
            "datatype": "integer",
            "name": "[medal_count]",
            "role": "measure",
            "type": "quantitative",
        },
    )

    ET.SubElement(
        dependencies,
        "column-instance",
        {
            "column": "[medal_name]",
            "derivation": "None",
            "name": "[none:medal_name:nk]",
            "pivot": "key",
            "type": "nominal",
        },
    )

    ET.SubElement(
        dependencies,
        "column-instance",
        {
            "column": "[medal_count]",
            "derivation": "Sum",
            "name": "[sum:medal_count:qk]",
            "pivot": "key",
            "type": "quantitative",
        },
    )

    # Reproduce the known-good Tableau Top-N contract used by EXEC 08.
    # Tableau groups medal rows by medal_name first, then keeps the ten
    # members with the largest SUM(medal_count).
    tableau_user_ns = "http://www.tableausoftware.com/xml/user"

    top_filter = ET.SubElement(
        view,
        "filter",
        {
            "class": "categorical",
            "column":
                f"[{datasource_name}]."
                "[none:medal_name:nk]",
        },
    )

    top_end = ET.SubElement(
        top_filter,
        "groupfilter",
        {
            "count": "10",
            "end": "top",
            "function": "end",
            "units": "records",
            f"{{{tableau_user_ns}}}ui-marker": "end",
            f"{{{tableau_user_ns}}}ui-top-by-field": "true",
        },
    )

    top_order = ET.SubElement(
        top_end,
        "groupfilter",
        {
            "direction": "DESC",
            "expression": "SUM([medal_count])",
            "function": "order",
            f"{{{tableau_user_ns}}}ui-marker": "order",
        },
    )

    ET.SubElement(
        top_order,
        "groupfilter",
        {
            "function": "level-members",
            "level": "[none:medal_name:nk]",
            f"{{{tableau_user_ns}}}ui-enumeration": "all",
            f"{{{tableau_user_ns}}}ui-marker": "enumerate",
        },
    )

    shelf_sorts = ET.SubElement(view, "shelf-sorts")

    ET.SubElement(
        shelf_sorts,
        "shelf-sort-v2",
        {
            "dimension-to-sort":
                f"[{datasource_name}]."
                "[none:medal_name:nk]",
            "direction": "DESC",
            "is-on-innermost-dimension": "true",
            "measure-to-sort-by":
                f"[{datasource_name}]."
                "[sum:medal_count:qk]",
            "shelf": "rows",
        },
    )

    slices = ET.SubElement(view, "slices")

    slice_column = ET.SubElement(slices, "column")
    slice_column.text = (
        f"[{datasource_name}]."
        "[none:medal_name:nk]"
    )

    ET.SubElement(
        view,
        "aggregation",
        {"value": "true"},
    )

    ET.SubElement(table, "style")

    panes = ET.SubElement(table, "panes")

    pane = ET.SubElement(
        panes,
        "pane",
        {
            "selection-relaxation-option":
                "selection-relaxation-allow"
        },
    )

    pane_view = ET.SubElement(pane, "view")

    ET.SubElement(
        pane_view,
        "breakdown",
        {"value": "auto"},
    )

    ET.SubElement(
        pane,
        "mark",
        {"class": "Automatic"},
    )

    rows = ET.SubElement(table, "rows")
    rows.text = (
        f"[{datasource_name}]."
        "[none:medal_name:nk]"
    )

    cols = ET.SubElement(table, "cols")
    cols.text = (
        f"[{datasource_name}]."
        "[sum:medal_count:qk]"
    )

    # Tableau worksheet content model requires a simple-id after <table>.
    # Use a fixed UUID so candidate generation remains deterministic.
    ET.SubElement(
        worksheet,
        "simple-id",
        {
            "uuid":
                "{54B8477E-A891-45D0-9A7C-"
                "79AF21E22B02}"
        },
    )

    return worksheet


def validate_candidate() -> None:
    tree = ET.parse(CANDIDATE)
    root = tree.getroot()

    datasources = root.find("datasources")

    if datasources is None:
        die("candidate has no <datasources> collection")

    for spec in DATASOURCES:
        caption = str(spec["caption"])

        matches = [
            node
            for node in datasources.findall("datasource")
            if node.get("caption") == caption
        ]

        if len(matches) != 1:
            die(
                f"expected exactly one datasource {caption}; "
                f"found {len(matches)}"
            )

        node = matches[0]

        hyper_filename = str(spec["hyper_filename"])

        expected_hyper_path = (
            ROOT
            / "tableau"
            / "extracts"
            / hyper_filename
        ).resolve()

        extract = node.find("./extract")

        if extract is None:
            die(
                f"post-grade datasource missing extract metadata: "
                f"{caption}"
            )

        hyper_connection = extract.find("./connection")

        if hyper_connection is None:
            die(
                f"post-grade datasource extract connection missing: "
                f"{caption}"
            )

        if hyper_connection.get("class") != "hyper":
            die(
                f"unexpected extract connection class: {caption}"
            )

        actual_dbname = hyper_connection.get("dbname")

        if actual_dbname is None:
            die(
                f"post-grade extract dbname missing: {caption}"
            )

        actual_hyper_path = Path(actual_dbname).resolve()

        if actual_hyper_path != expected_hyper_path:
            die(
                f"post-grade extract path mismatch: {caption}\\n"
                f"Expected: {expected_hyper_path}\\n"
                f"Actual:   {actual_hyper_path}"
            )

        if not actual_hyper_path.is_file():
            die(
                f"post-grade extract file missing: "
                f"{actual_hyper_path}"
            )

        relation = hyper_connection.find("./relation")

        if relation is None:
            die(
                f"post-grade extract relation missing: {caption}"
            )

        if relation.get("table") != "[Extract].[Extract]":
            die(
                f"unexpected extract relation table: {caption}"
            )

        if relation.get("type") != "table":
            die(
                f"unexpected extract relation type: {caption}"
            )

        extract_properties = node.find(
            "./object-graph/objects/object/"
            "properties[@context='extract']"
        )

        if extract_properties is None:
            die(
                f"extract object-graph context missing: {caption}"
            )

        extract_relation = extract_properties.find("./relation")

        if extract_relation is None:
            die(
                f"extract object-graph relation missing: {caption}"
            )

        if extract_relation.get("table") != "[Extract].[Extract]":
            die(
                f"unexpected extract object-graph table: {caption}"
            )

        textscan = node.find(
            "./connection/named-connections/"
            "named-connection/connection"
        )

        if textscan is None:
            die(f"textscan connection missing: {caption}")

        if textscan.get("class") != "textscan":
            die(f"unexpected connection class: {caption}")

    passed("three post-grade datasources validated")
    passed("three post-grade Hyper extract bindings validated")



def build_pg03_medals_per_match_worksheet() -> ET.Element:
    """Build PG 03 — Medals per Match as a single-value KPI."""

    datasource_name = "federated.postgrade.medal.per.match"

    worksheet = ET.Element(
        "worksheet",
        {
            "name": "PG 03 — Medals per Match",
        },
    )

    table = ET.SubElement(worksheet, "table")
    view = ET.SubElement(table, "view")

    datasources = ET.SubElement(view, "datasources")

    ET.SubElement(
        datasources,
        "datasource",
        {
            "caption": "post_grade_medal_per_match",
            "name": datasource_name,
        },
    )

    dependencies = ET.SubElement(
        view,
        "datasource-dependencies",
        {
            "datasource": datasource_name,
        },
    )

    ET.SubElement(
        dependencies,
        "column",
        {
            "caption": "Medals per Match",
            "datatype": "real",
            "default-format": "n#,##0.00;-#,##0.00",
            "name": "[medals_per_match]",
            "role": "measure",
            "type": "quantitative",
        },
    )

    ET.SubElement(
        dependencies,
        "column-instance",
        {
            "column": "[medals_per_match]",
            "derivation": "Sum",
            "name": "[sum:medals_per_match:qk]",
            "pivot": "key",
            "type": "quantitative",
        },
    )

    ET.SubElement(
        view,
        "aggregation",
        {
            "value": "true",
        },
    )

    ET.SubElement(table, "style")

    panes = ET.SubElement(table, "panes")

    pane = ET.SubElement(
        panes,
        "pane",
        {
            "selection-relaxation-option":
                "selection-relaxation-allow",
        },
    )

    pane_view = ET.SubElement(pane, "view")

    ET.SubElement(
        pane_view,
        "breakdown",
        {
            "value": "auto",
        },
    )

    ET.SubElement(
        pane,
        "mark",
        {
            "class": "Automatic",
        },
    )

    encodings = ET.SubElement(pane, "encodings")

    field_reference = (
        f"[{datasource_name}]."
        "[sum:medals_per_match:qk]"
    )

    ET.SubElement(
        encodings,
        "text",
        {
            "column": field_reference,
        },
    )

    customized_label = ET.SubElement(
        pane,
        "customized-label",
    )

    formatted_text = ET.SubElement(
        customized_label,
        "formatted-text",
    )

    value_run = ET.SubElement(
        formatted_text,
        "run",
        {
            "bold": "true",
            "fontsize": "28",
        },
    )
    value_run.text = f"<{field_reference}>"

    newline_run = ET.SubElement(
        formatted_text,
        "run",
    )
    newline_run.text = "Æ\n"

    caption_run = ET.SubElement(
        formatted_text,
        "run",
        {
            "fontsize": "14",
        },
    )
    caption_run.text = "Medals per Match"

    pane_style = ET.SubElement(pane, "style")

    style_rule = ET.SubElement(
        pane_style,
        "style-rule",
        {
            "element": "mark",
        },
    )

    ET.SubElement(
        style_rule,
        "format",
        {
            "attr": "mark-labels-show",
            "value": "true",
        },
    )

    ET.SubElement(
        style_rule,
        "format",
        {
            "attr": "mark-labels-cull",
            "value": "true",
        },
    )

    ET.SubElement(table, "rows")
    ET.SubElement(table, "cols")

    ET.SubElement(
        worksheet,
        "simple-id",
        {
            "uuid":
                "{AC7E313E-CEB4-45B0-9C3E-"
                "C94DCC1B7B03}",
        },
    )

    return worksheet


def integrate_pg03_into_executive_dashboard(
    root: ET.Element,
) -> None:
    """Replace executive KPI 06 with PG03 Medals per Match.

    This transformation intentionally changes only the worksheet reference
    used by zone 25 of the post-grade executive dashboard and the matching
    dashboard-window viewpoint.

    The existing KPI 06 worksheet remains in the workbook because other
    dashboards may continue to reference it.
    """

    dashboard_name = (
        "Halo Multiplayer Performance: Executive Overview"
    )
    old_sheet = "KPI 06 — Medals Awarded"
    new_sheet = "PG 03 — Medals per Match"

    dashboards = [
        dashboard
        for dashboard in root.findall("./dashboards/dashboard")
        if dashboard.get("name") == dashboard_name
    ]

    if len(dashboards) != 1:
        die(
            "PG04 expected exactly one executive dashboard; "
            f"found {len(dashboards)}"
        )

    dashboard = dashboards[0]

    zones = [
        zone
        for zone in dashboard.findall(".//zone")
        if zone.get("id") == "25"
    ]

    if len(zones) != 1:
        die(
            "PG04 expected exactly one dashboard zone 25; "
            f"found {len(zones)}"
        )

    zone = zones[0]

    expected_geometry = {
        "x": "82800",
        "y": "8500",
        "w": "16000",
        "h": "15000",
    }

    if zone.get("name") != old_sheet:
        die(
            "PG04 zone 25 source worksheet mismatch: "
            f"{zone.get('name')!r}"
        )

    actual_geometry = {
        key: zone.get(key)
        for key in expected_geometry
    }

    if actual_geometry != expected_geometry:
        die(
            "PG04 zone 25 geometry mismatch\n"
            f"Expected: {expected_geometry}\n"
            f"Actual:   {actual_geometry}"
        )

    target_worksheets = [
        worksheet
        for worksheet in root.findall("./worksheets/worksheet")
        if worksheet.get("name") == new_sheet
    ]

    if len(target_worksheets) != 1:
        die(
            "PG04 expected exactly one target PG03 worksheet; "
            f"found {len(target_worksheets)}"
        )

    windows = [
        window
        for window in root.findall("./windows/window")
        if (
            window.get("class") == "dashboard"
            and window.get("name") == dashboard_name
        )
    ]

    if len(windows) != 1:
        die(
            "PG04 expected exactly one executive dashboard window; "
            f"found {len(windows)}"
        )

    window = windows[0]

    old_viewpoints = [
        viewpoint
        for viewpoint in window.findall("./viewpoints/viewpoint")
        if viewpoint.get("name") == old_sheet
    ]

    new_viewpoints = [
        viewpoint
        for viewpoint in window.findall("./viewpoints/viewpoint")
        if viewpoint.get("name") == new_sheet
    ]

    if len(old_viewpoints) != 1:
        die(
            "PG04 expected exactly one KPI06 dashboard viewpoint; "
            f"found {len(old_viewpoints)}"
        )

    if new_viewpoints:
        die(
            "PG04 target PG03 viewpoint already exists in "
            "executive dashboard"
        )

    zone.set("name", new_sheet)
    old_viewpoints[0].set("name", new_sheet)

    final_geometry = {
        key: zone.get(key)
        for key in expected_geometry
    }

    if final_geometry != expected_geometry:
        die("PG04 unexpectedly changed zone 25 geometry")

    if zone.get("name") != new_sheet:
        die("PG04 failed to replace zone 25 worksheet")

    final_names = [
        viewpoint.get("name")
        for viewpoint in window.findall("./viewpoints/viewpoint")
    ]

    if old_sheet in final_names:
        die(
            "PG04 KPI06 remained in executive dashboard viewpoints"
        )

    if final_names.count(new_sheet) != 1:
        die(
            "PG04 expected PG03 exactly once in executive "
            "dashboard viewpoints"
        )

    passed(
        "PG04 executive dashboard: "
        "KPI06 -> PG03 Medals per Match"
    )

def main() -> None:
    print("=" * 78)
    print(" WEEK 7 — BUILD POST-GRADE TABLEAU CANDIDATE")
    print("=" * 78)

    print()
    print("===== SAFETY =====")

    branch = current_branch()

    if branch != BRANCH:
        die(
            f"expected branch {BRANCH}; found {branch}"
        )

    passed(f"branch: {branch}")

    if not SOURCE.is_file():
        die(f"graded source missing: {SOURCE}")

    source_sha = sha256(SOURCE)

    if source_sha != EXPECTED_SOURCE_SHA256:
        die(
            "graded source SHA mismatch\n"
            f"Expected: {EXPECTED_SOURCE_SHA256}\n"
            f"Actual:   {source_sha}"
        )

    passed(f"graded source SHA-256: {source_sha}")

    ET.parse(SOURCE)
    passed("graded source is valid XML")

    print()
    print("===== VALIDATE POST-GRADE DATA =====")

    for spec in DATASOURCES:
        validate_csv_schema(spec)

    print()
    print("===== REBUILD CANDIDATE =====")

    shutil.copy2(SOURCE, CANDIDATE)

    tree = ET.parse(CANDIDATE)
    root = tree.getroot()

    datasources = root.find("datasources")

    if datasources is None:
        die("graded workbook has no <datasources> collection")

    existing_captions = {
        node.get("caption")
        for node in datasources.findall("datasource")
    }

    for spec in DATASOURCES:
        caption = str(spec["caption"])

        if caption in existing_captions:
            die(
                f"post-grade datasource already exists in "
                f"graded source: {caption}"
            )

        datasource = build_datasource(spec)

        hyper_filename = str(spec["hyper_filename"])
        hyper_path = (
            ROOT
            / "tableau"
            / "extracts"
            / hyper_filename
        )

        csv_path = DATA_DIR / str(spec["filename"])

        add_post_grade_extract(
            datasource,
            hyper_path,
            csv_path,
        )

        datasources.append(datasource)

        passed(
            f"added datasource + extract: "
            f"{caption} -> {hyper_filename}"
        )

    worksheets = root.find("worksheets")

    if worksheets is None:
        die("graded workbook has no <worksheets> collection")

    pg01_name = "PG 01 — Map Performance"

    if any(
        worksheet.get("name") == pg01_name
        for worksheet in worksheets.findall("worksheet")
    ):
        die(f"worksheet already exists: {pg01_name}")

    worksheets.append(build_pg01_map_performance_worksheet())
    passed(f"added worksheet: {pg01_name}")

    pg02_name = "PG 02 — Medal Distribution"

    if any(
        worksheet.get("name") == pg02_name
        for worksheet in worksheets.findall("worksheet")
    ):
        die(f"worksheet already exists: {pg02_name}")

    worksheets.append(build_pg02_medal_distribution_worksheet())
    passed(f"added worksheet: {pg02_name}")

    pg03_name = "PG 03 — Medals per Match"

    if any(
        worksheet.get("name") == pg03_name
        for worksheet in worksheets.findall("worksheet")
    ):
        die(f"worksheet already exists: {pg03_name}")

    worksheets.append(build_pg03_medals_per_match_worksheet())
    passed(f"added worksheet: {pg03_name}")

    integrate_pg03_into_executive_dashboard(root)

    ET.indent(tree, space="  ")

    tree.write(
        CANDIDATE,
        encoding="utf-8",
        xml_declaration=True,
        short_empty_elements=True,
    )

    print()
    print("===== VALIDATE CANDIDATE =====")

    validate_candidate()

    candidate_sha = sha256(CANDIDATE)

    if candidate_sha == source_sha:
        die(
            "candidate SHA did not diverge after datasource "
            "transformation"
        )

    passed("candidate differs from graded source")

    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        die("graded source changed during candidate generation")

    passed("graded source remained immutable")

    print()
    print("===== RESULT =====")
    print(f"Source:    {SOURCE}")
    print(f"Candidate: {CANDIDATE}")
    print(f"SHA-256:   {candidate_sha}")

    print()
    print("=" * 78)
    print(" POST-GRADE DATASOURCE FOUNDATION COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()
