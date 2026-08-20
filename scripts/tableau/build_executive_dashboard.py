#!/usr/bin/env python3
"""
===============================================================================
DataExpert Boot Camp — Tableau Executive Dashboard Builder
===============================================================================

Author:
    Ceasar Jackson

Project:
    DataExpert Boot Camp — Data Visualization / Tableau Homework

Purpose:
    Safely generate a Tableau executive-dashboard candidate from the verified
    source workbook without modifying that source workbook in place.

Key safety guarantees:
    * Source workbook is read-only.
    * Source SHA-256 and Git branch are validated.
    * A timestamped checkpoint is created before candidate generation.
    * Candidate output receives a distinct filename.
    * KPI transformations occur only in candidate text.
    * Source worksheet names are validated before candidate-only renaming.
    * XML, dashboard zones, dimensions, and source immutability are validated.
    * No Git staging, commit, push, replacement, or publication is performed.

Important player-combat naming:
    Verified source:
        EXEC 0 — Player Combat Performance

    Generated candidate:
        EXEC 00 — Player Combat Performance

Usage:
    python3 scripts/tableau/build_executive_dashboard.py

Validation:
    python3 -m py_compile scripts/tableau/build_executive_dashboard.py
    python3 scripts/tableau/build_executive_dashboard.py
===============================================================================
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_SOURCE = Path(
    "data_visualization/tableau_homework/tableau/"
    "CeasarJackson_DataExpert_Tableau_Homework.twb"
)

EXPECTED_BRANCH = "improve/week07-post-grade-hardening"

EXPECTED_SOURCE_SHA256 = (
    "5d5b55c03dc4b8518ccf057e3e4e945778b846669089c5a1471586fdeab9b9f0"
)

DASHBOARD_NAME = "EXECUTIVE DASHBOARD — Halo Performance"

SOURCE_PLAYER_COMBAT_SHEET = "EXEC 0 — Player Combat Performance"
CANDIDATE_PLAYER_COMBAT_SHEET = "EXEC-00 — Player Combat Performance"

CHECKPOINT_DIR = Path(
    "data_visualization/tableau_homework/validation/checkpoints"
)
RESULTS_DIR = Path(
    "data_visualization/tableau_homework/validation/results"
)

EXPECTED_SHEETS = (
    "KPI 01 — Matches with Player Data",
    "KPI 02 — Unique Players",
    "KPI 03 — Total Kills",
    "KPI 04 — Overall K/D",
    "KPI 05 — Player Win Rate",
    "KPI 06 — Medals Awarded",
    SOURCE_PLAYER_COMBAT_SHEET,
    "EXP 01 — Medal Volume Over Time",
    "EXP 03 — Medal Classification Mix",
    "EXEC 06 — Team vs Individual Medal Activity",
    "EXEC 07 — Medal Activity by Difficulty",
    "EXEC 08 — Top 10 Medal Rankings",
)

EXPECTED_DASHBOARD_SHEETS = (
    "KPI 01 — Matches with Player Data",
    "KPI 02 — Unique Players",
    "KPI 03 — Total Kills",
    "KPI 04 — Overall K/D",
    "KPI 05 — Player Win Rate",
    "KPI 06 — Medals Awarded",
    CANDIDATE_PLAYER_COMBAT_SHEET,
    "EXP 01 — Medal Volume Over Time",
    "EXP 03 — Medal Classification Mix",
    "EXEC 06 — Team vs Individual Medal Activity",
    "EXEC 07 — Medal Activity by Difficulty",
    "EXEC 08 — Top 10 Medal Rankings",
)


# ---------------------------------------------------------------------------
# Terminal formatting
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"


def info(message: str) -> None:
    print(f"{CYAN}INFO:{RESET} {message}")


def success(message: str) -> None:
    print(f"{GREEN}PASS:{RESET} {message}")


def warn(message: str) -> None:
    print(f"{YELLOW}WARN:{RESET} {message}")


def fail(message: str) -> None:
    print(f"{RED}FAIL:{RESET} {message}", file=sys.stderr)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def current_git_branch() -> str | None:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def worksheet_pattern(name: str) -> str:
    """Return a regex matching a Tableau worksheet by exact name."""
    return (
        r"<worksheet\b[^>]*\bname=(?:'"
        + re.escape(name)
        + r"'|\""
        + re.escape(name)
        + r"\")"
    )


def worksheet_block_pattern(name: str) -> str:
    """Return a regex matching an entire Tableau worksheet block."""
    return (
        r"(<worksheet\b[^>]*name='"
        + re.escape(name)
        + r"'[^>]*>[\s\S]*?</worksheet>)"
    )


def zone_style(indent: str = "            ") -> str:
    return (
        f"{indent}<zone-style>\n"
        f"{indent}  <format attr='border-color' value='#000000' />\n"
        f"{indent}  <format attr='border-style' value='none' />\n"
        f"{indent}  <format attr='border-width' value='0' />\n"
        f"{indent}  <format attr='margin' value='4' />\n"
        f"{indent}</zone-style>"
    )


def worksheet_zone(
    zone_id: int,
    name: str,
    x: int,
    y: int,
    w: int,
    h: int,
) -> str:
    return (
        f"          <zone h='{h}' id='{zone_id}' "
        f"name='{name}' w='{w}' x='{x}' y='{y}'>\n"
        f"{zone_style('            ')}\n"
        f"          </zone>"
    )


# ---------------------------------------------------------------------------
# KPI candidate-only normalization
# ---------------------------------------------------------------------------


def normalize_kpi06(text: str) -> str:
    """Normalize KPI 06 to a single-measure KPI card."""

    worksheet_name = "KPI 06 — Medals Awarded"
    match = re.search(worksheet_block_pattern(worksheet_name), text)

    if not match:
        fail(f"Unable to locate worksheet for normalization: {worksheet_name}")

    original = match.group(1)
    updated = original

    updated, count_filter = re.subn(
        r"\s*<filter class='categorical' "
        r"column='\[federated\.0mvsqey1l1l9bz1ci24fn0qxcphu\]\.\[:Measure Names\]'>"
        r"[\s\S]*?</filter>",
        "",
        updated,
        count=1,
    )

    updated, count_slices = re.subn(
        r"\s*<slices>\s*"
        r"<column>\[federated\.0mvsqey1l1l9bz1ci24fn0qxcphu\]\.\[:Measure Names\]</column>\s*"
        r"</slices>",
        "",
        updated,
        count=1,
    )

    updated, count_text = re.subn(
        r"<text column='\[federated\.0mvsqey1l1l9bz1ci24fn0qxcphu\]\.\[Multiple Values\]' />",
        "<text column='[federated.0mvsqey1l1l9bz1ci24fn0qxcphu].[sum:total_medals_awarded:qk]' />",
        updated,
        count=1,
    )

    updated, count_rows = re.subn(
        r"<rows>\[federated\.0mvsqey1l1l9bz1ci24fn0qxcphu\]\.\[:Measure Names\]</rows>",
        "<rows />",
        updated,
        count=1,
    )

    checks = {
        "Measure Names filter": count_filter,
        "Measure Names slices": count_slices,
        "Multiple Values text encoding": count_text,
        "Measure Names rows shelf": count_rows,
    }

    failures = [name for name, count in checks.items() if count != 1]
    if failures:
        fail(
            "KPI 06 normalization did not match expected source structure: "
            + ", ".join(failures)
        )

    if "[Multiple Values]" in updated:
        fail("KPI 06 still references Multiple Values after normalization.")

    if "[:Measure Names]" in updated:
        fail("KPI 06 still references Measure Names after normalization.")

    expected_encoding = (
        "<text column="
        "'[federated.0mvsqey1l1l9bz1ci24fn0qxcphu]."
        "[sum:total_medals_awarded:qk]' />"
    )

    if expected_encoding not in updated:
        fail("KPI 06 direct medal text encoding was not created.")

    success("Normalized KPI 06 to a single-measure KPI card.")
    return text.replace(original, updated, 1)


def normalize_kpi_card_presentation(text: str) -> str:
    """Refine KPI-card presentation in generated candidates only."""

    kpi_names = (
        "KPI 01 — Matches with Player Data",
        "KPI 02 — Unique Players",
        "KPI 03 — Total Kills",
        "KPI 04 — Overall K/D",
        "KPI 05 — Player Win Rate",
        "KPI 06 — Medals Awarded",
    )

    for worksheet_name in kpi_names:
        match = re.search(worksheet_block_pattern(worksheet_name), text)

        if not match:
            fail(
                "Unable to locate KPI worksheet for presentation refinement: "
                + worksheet_name
            )

        original = match.group(1)
        updated = original

        target_font = (
            "24"
            if worksheet_name in (
                "KPI 01 — Matches with Player Data",
                "KPI 02 — Unique Players",
            )
            else "28"
        )

        updated = updated.replace(
            "fontsize='32'",
            f"fontsize='{target_font}'",
        )

        if worksheet_name == "KPI 02 — Unique Players":
            for stray_font in ("32", "28", "24"):
                updated = updated.replace(
                    "<run fontname='Benton Sans Book' "
                    f"fontsize='{stray_font}'>Æ </run>",
                    "",
                )

        if worksheet_name == "KPI 01 — Matches with Player Data":
            updated = updated.replace(
                "Matchers With Player Data",
                "Matches With Player Data",
            )

        if worksheet_name == "KPI 06 — Medals Awarded":
            updated = updated.replace(
                "Total Medal Awarded",
                "Total Medals Awarded",
            )

        text = text.replace(original, updated, 1)

    if "Matchers With Player Data" in text:
        fail("KPI 01 typo remains after presentation refinement.")

    kpi06_match = re.search(
        worksheet_block_pattern("KPI 06 — Medals Awarded"),
        text,
    )

    if not kpi06_match:
        fail("Unable to re-read KPI 06 after presentation refinement.")

    if "Total Medal Awarded" in kpi06_match.group(0):
        fail("KPI 06 label typo remains after presentation refinement.")

    success("Refined KPI card fonts and corrected KPI 01 / KPI 06 labels.")
    return text


def promote_kpi01_for_candidate(text: str) -> str:
    """
    Replace the stale KPI 01 worksheet with a completely fresh serialization
    cloned from the proven-good KPI 02 worksheet.

    This candidate-only production promotion preserves the successful KPI 01A
    experiment while restoring the final worksheet name.

    Production behavior:
        * clone KPI 02's known-good worksheet structure
        * substitute matches_with_player_data semantics
        * use the verified 20pt KPI value and 12pt descriptive label
        * generate a genuinely new worksheet UUID
        * replace the stale original KPI 01 worksheet
        * remove stale KPI 01 worksheet-window metadata

    The source workbook is never modified.
    """

    source_name = "KPI 02 — Unique Players"
    target_name = "KPI 01 — Matches with Player Data"

    source_match = re.search(
        worksheet_block_pattern(source_name),
        text,
    )

    target_match = re.search(
        worksheet_block_pattern(target_name),
        text,
    )

    if not source_match:
        fail("Unable to locate KPI 02 production template worksheet.")

    if not target_match:
        fail("Unable to locate stale KPI 01 worksheet for replacement.")

    fresh_ws = source_match.group(1)

    substitutions = (
        ("KPI 02 — Unique Players", target_name),
        ("[sum:unique_players:qk]", "[sum:matches_with_player_data:qk]"),
        ("[unique_players]", "[matches_with_player_data]"),
        ("Unique Players", "Matches With Player Data"),
    )

    for old_value, new_value in substitutions:
        if old_value not in fresh_ws:
            fail("Production KPI 01 template token missing: " + old_value)
        fresh_ws = fresh_ws.replace(old_value, new_value)

    # Preserve the exact presentation that visually succeeded as KPI 01A.
    fresh_ws, value_font_count = re.subn(
        r"<run fontsize='24'>(<!\[CDATA\[<"
        r"\[federated\.0mvsqey1l1l9bz1ci24fn0qxcphu\]"
        r"\.\[sum:matches_with_player_data:qk\]>"
        r"\]\]></run>)",
        r"<run fontsize='20'>\1",
        fresh_ws,
        count=1,
    )

    if value_font_count != 1:
        fail("Unable to apply production KPI 01 value font normalization.")

    old_label = (
        "<run fontname='Benton Sans Book' "
        "fontsize='14'>Matches With Player Data</run>"
    )
    new_label = (
        "<run fontname='Benton Sans Book' "
        "fontsize='12'>Matches With Player Data</run>"
    )

    if old_label not in fresh_ws:
        fail("Unable to locate production KPI 01 descriptive label.")

    fresh_ws = fresh_ws.replace(old_label, new_label, 1)

    # New worksheet identity: do not reuse the stale KPI 01 simple-id.
    fresh_ws, uuid_count = re.subn(
        r"<simple-id uuid='[^']+'",
        f"<simple-id uuid='{{{str(uuid.uuid4()).upper()}}}'",
        fresh_ws,
        count=1,
    )

    if uuid_count != 1:
        fail("Unable to generate fresh production KPI 01 worksheet UUID.")

    # Replace, rather than duplicate, the stale worksheet.
    text = text.replace(
        target_match.group(1),
        fresh_ws,
        1,
    )

    # The successful KPI 01A worksheet had no legacy worksheet-window state.
    # Remove KPI 01's old worksheet window so the production sheet has the
    # same clean identity characteristics.
    window_patterns = (
        r"\s*<window\b[^>]*class='worksheet'[^>]*name='"
        + re.escape(target_name)
        + r"'[^>]*>[\s\S]*?</window>",
        r"\s*<window\b[^>]*name='"
        + re.escape(target_name)
        + r"'[^>]*class='worksheet'[^>]*>[\s\S]*?</window>",
    )

    removed = 0

    for pattern in window_patterns:
        text, count = re.subn(
            pattern,
            "",
            text,
            count=1,
        )
        if count:
            removed = count
            break

    if removed != 1:
        fail("Expected exactly one stale KPI 01 worksheet window.")

    # Production invariants.
    production_matches = re.findall(
        worksheet_block_pattern(target_name),
        text,
    )

    if len(production_matches) != 1:
        fail(
            "Expected exactly one production KPI 01 worksheet; found "
            + str(len(production_matches))
        )

    production_ws = production_matches[0]

    required = (
        target_name,
        "[matches_with_player_data]",
        "[sum:matches_with_player_data:qk]",
        "Matches With Player Data",
        "fontsize='20'",
        "fontsize='12'",
        "mark-labels-show",
        "mark-labels-cull",
    )

    for token in required:
        if token not in production_ws:
            fail("Production KPI 01 missing required token: " + token)

    forbidden = (
        "unique_players",
        "Unique Players",
        "KPI 01A",
    )

    for token in forbidden:
        if token in production_ws:
            fail("Production KPI 01 contains unexpected token: " + token)

    success(
        "Promoted fresh KPI 01 implementation to production worksheet identity."
    )

    return text


def remove_bootstrap_dashboard2(candidate_text: str) -> str:
    """
    Remove Tableau's bootstrap Dashboard 2 from the generated candidate.

    Dashboard 2 is retained long enough for clone_dashboard_window() to harvest
    Tableau-generated dashboard-window syntax. It is removed only from the
    completed candidate so the fresh production KPI 01 has no legacy Dashboard 2
    ownership.
    """

    dashboard_patterns = (
        r"\s*<dashboard\b[^>]*name='Dashboard 2'[^>]*>"
        r"[\s\S]*?</dashboard>",
        r'\s*<dashboard\b[^>]*name="Dashboard 2"[^>]*>'
        r"[\s\S]*?</dashboard>",
    )

    dashboard_removed = 0

    for pattern in dashboard_patterns:
        candidate_text, count = re.subn(
            pattern,
            "",
            candidate_text,
            count=1,
        )
        if count:
            dashboard_removed = count
            break

    if dashboard_removed != 1:
        fail("Expected exactly one bootstrap Dashboard 2 definition.")

    window_patterns = (
        r"\s*<window\b[^>]*class='dashboard'[^>]*name='Dashboard 2'[^>]*>"
        r"[\s\S]*?</window>",
        r"\s*<window\b[^>]*name='Dashboard 2'[^>]*class='dashboard'[^>]*>"
        r"[\s\S]*?</window>",
        r'\s*<window\b[^>]*class="dashboard"[^>]*name="Dashboard 2"[^>]*>'
        r"[\s\S]*?</window>",
        r'\s*<window\b[^>]*name="Dashboard 2"[^>]*class="dashboard"[^>]*>'
        r"[\s\S]*?</window>",
    )

    window_removed = 0

    for pattern in window_patterns:
        candidate_text, count = re.subn(
            pattern,
            "",
            candidate_text,
            count=1,
        )
        if count:
            window_removed = count
            break

    if window_removed != 1:
        fail("Expected exactly one bootstrap Dashboard 2 window.")

    success("Removed bootstrap Dashboard 2 from generated candidate.")

    return candidate_text




# ---------------------------------------------------------------------------
# Candidate-only player-combat worksheet rename
# ---------------------------------------------------------------------------


def rename_exec00_for_candidate(text: str) -> str:
    """
    Rename the verified player-combat worksheet in candidate text only.

    Every exact source-name reference is renamed together so Tableau worksheet,
    window, thumbnail, dashboard-zone, and viewpoint metadata remain consistent.
    """

    source_name = SOURCE_PLAYER_COMBAT_SHEET
    candidate_name = CANDIDATE_PLAYER_COMBAT_SHEET

    if source_name == candidate_name:
        fail("Player-combat source and candidate names must differ.")

    source_pattern = worksheet_pattern(source_name)
    candidate_pattern = worksheet_pattern(candidate_name)

    if not re.search(source_pattern, text):
        fail(
            "Unable to locate source player-combat worksheet for candidate "
            f"rename: {source_name}"
        )

    if re.search(candidate_pattern, text):
        fail(
            "Candidate player-combat worksheet already exists before rename: "
            f"{candidate_name}"
        )

    reference_count = text.count(source_name)

    if reference_count < 1:
        fail("No exact player-combat worksheet-name references were found.")

    updated = text.replace(source_name, candidate_name)

    if source_name in updated:
        fail("Source player-combat name remains after candidate-only rename.")

    if not re.search(candidate_pattern, updated):
        fail("Candidate player-combat worksheet rename could not be verified.")

    success(
        "Renamed player-combat worksheet for candidate only: "
        f"{source_name} -> {candidate_name} "
        f"({reference_count} exact reference(s) updated)."
    )

    return updated


# ---------------------------------------------------------------------------
# Dashboard generation
# ---------------------------------------------------------------------------


def build_dashboard_xml() -> str:
    """Build one fixed-size, desktop-oriented executive dashboard."""

    zones: list[str] = []

    zones.append(
        """          <zone forceUpdate='true' h='7000' id='10' type-v2='text' w='98400' x='800' y='1000'>
            <formatted-text>
              <run bold='true' fontsize='20'>Halo Player &amp; Medal Performance</run>
              <run>Æ&#10;</run>
              <run fontsize='11'>Executive Analytics Dashboard</run>
            </formatted-text>
            <zone-style>
              <format attr='border-color' value='#000000' />
              <format attr='border-style' value='none' />
              <format attr='border-width' value='0' />
              <format attr='margin' value='4' />
            </zone-style>
          </zone>"""
    )

    kpis = [
        "KPI 01 — Matches with Player Data",
        "KPI 02 — Unique Players",
        "KPI 03 — Total Kills",
        "KPI 04 — Overall K/D",
        "KPI 05 — Player Win Rate",
        "KPI 06 — Medals Awarded",
    ]

    kpi_y = 8500
    kpi_h = 16500
    left = 800
    total_w = 98400
    gap = 400
    card_w = (total_w - gap * 5) // 6

    zone_id = 20

    for index, sheet in enumerate(kpis):
        x = left + index * (card_w + gap)
        zones.append(
            worksheet_zone(
                zone_id=zone_id,
                name=sheet,
                x=x,
                y=kpi_y,
                w=card_w,
                h=kpi_h,
            )
        )
        zone_id += 1

    zones.append(
        worksheet_zone(
            zone_id=30,
            name=CANDIDATE_PLAYER_COMBAT_SHEET,
            x=800,
            y=25500,
            w=48700,
            h=29500,
        )
    )

    zones.append(
        worksheet_zone(
            zone_id=31,
            name="EXP 01 — Medal Volume Over Time",
            x=50500,
            y=25500,
            w=48700,
            h=29500,
        )
    )

    zones.append(
        worksheet_zone(
            zone_id=40,
            name="EXP 03 — Medal Classification Mix",
            x=800,
            y=55500,
            w=35000,
            h=23500,
        )
    )

    zones.append(
        worksheet_zone(
            zone_id=41,
            name="EXEC 06 — Team vs Individual Medal Activity",
            x=36400,
            y=55500,
            w=28200,
            h=23500,
        )
    )

    zones.append(
        worksheet_zone(
            zone_id=42,
            name="EXEC 07 — Medal Activity by Difficulty",
            x=65200,
            y=55500,
            w=34000,
            h=23500,
        )
    )

    zones.append(
        worksheet_zone(
            zone_id=50,
            name="EXEC 08 — Top 10 Medal Rankings",
            x=800,
            y=79500,
            w=98400,
            h=19500,
        )
    )

    child_zones = "\n".join(zones)
    dashboard_uuid = str(uuid.uuid4()).upper()

    return f"""    <dashboard enable-sort-zone-taborder='true' name='{DASHBOARD_NAME}'>
      <style />
      <size maxheight='1000' maxwidth='1400' minheight='1000' minwidth='1400' sizing-mode='fixed' />
      <zones>
        <zone h='100000' id='4' type-v2='layout-basic' w='100000' x='0' y='0'>
{child_zones}
          <zone-style>
            <format attr='border-color' value='#000000' />
            <format attr='border-style' value='none' />
            <format attr='border-width' value='0' />
            <format attr='margin' value='8' />
          </zone-style>
        </zone>
      </zones>
      <simple-id uuid='{{{dashboard_uuid}}}' />
    </dashboard>"""


def clone_dashboard_window(text: str) -> str:
    """
    Clone Dashboard 2 window metadata while rebuilding dashboard viewpoints.
    """

    patterns = (
        r"(<window\b[^>]*class='dashboard'[^>]*name='Dashboard 2'[^>]*>[\s\S]*?</window>)",
        r'(<window\b[^>]*class="dashboard"[^>]*name="Dashboard 2"[^>]*>[\s\S]*?</window>)',
        r"(<window\b[^>]*name='Dashboard 2'[^>]*class='dashboard'[^>]*>[\s\S]*?</window>)",
    )

    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue

        window = match.group(1)

        window = window.replace(
            "name='Dashboard 2'",
            f"name='{DASHBOARD_NAME}'",
            1,
        )

        viewpoints = ["      <viewpoints>"]

        for sheet in EXPECTED_DASHBOARD_SHEETS:
            viewpoints.extend(
                [
                    f"        <viewpoint name='{sheet}'>",
                    "          <zoom type='entire-view' />",
                    "        </viewpoint>",
                ]
            )

        viewpoints.append("      </viewpoints>")
        viewpoints_xml = "\n".join(viewpoints)

        window, count = re.subn(
            r"      <viewpoints>[\s\S]*?</viewpoints>",
            viewpoints_xml,
            window,
            count=1,
        )

        if count != 1:
            fail("Unable to replace Dashboard 2 viewpoints metadata.")

        window = re.sub(
            r"<simple-id uuid='[^']+'",
            f"<simple-id uuid='{{{str(uuid.uuid4()).upper()}}}'",
            window,
            count=1,
        )

        return window

    fail("No Dashboard 2 <window> block was found.")


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a safe Tableau executive-dashboard candidate."
    )

    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source .twb workbook (default: {DEFAULT_SOURCE})",
    )

    parser.add_argument(
        "--allow-sha-mismatch",
        action="store_true",
        help=(
            "Allow generation when source SHA differs from the verified "
            "bootstrap checkpoint. Use only after reviewing the difference."
        ),
    )

    args = parser.parse_args()
    source = args.source.resolve()

    print("=" * 78)
    print(" TABLEAU EXECUTIVE DASHBOARD — SAFE AUTOMATION")
    print("=" * 78)

    if not source.is_file():
        fail(f"Source workbook does not exist: {source}")

    branch = current_git_branch()

    if branch:
        info(f"Git branch: {branch}")
        if branch != EXPECTED_BRANCH:
            fail(
                f"Expected branch '{EXPECTED_BRANCH}', but current branch is "
                f"'{branch}'."
            )
    else:
        warn("Unable to determine Git branch; continuing with file validation.")

    source_hash = sha256(source)
    info(f"Source SHA-256: {source_hash}")

    if source_hash != EXPECTED_SOURCE_SHA256:
        message = (
            "Source SHA does not match the verified Dashboard 2 bootstrap "
            f"state.\nExpected: {EXPECTED_SOURCE_SHA256}\n"
            f"Actual:   {source_hash}"
        )

        if not args.allow_sha_mismatch:
            fail(
                message
                + "\nRe-run with --allow-sha-mismatch only after confirming "
                "the workbook changes are intentional."
            )

        warn(message)

    text = source.read_text(encoding="utf-8")

    # Candidate-only KPI transformations.
    text = normalize_kpi06(text)
    text = normalize_kpi_card_presentation(text)
    text = promote_kpi01_for_candidate(text)

    # Validate verified SOURCE worksheet names before any source/candidate rename.
    missing = []

    for sheet in EXPECTED_SHEETS:
        if not re.search(worksheet_pattern(sheet), text):
            missing.append(sheet)

    if missing:
        fail(
            "Required source worksheets are missing:\n  - "
            + "\n  - ".join(missing)
        )

    success(f"All {len(EXPECTED_SHEETS)} required source worksheets exist.")

    # Candidate-only rename after source validation.
    text = rename_exec00_for_candidate(text)

    if re.search(
        r"<dashboard\b[^>]*\bname=(?:'"
        + re.escape(DASHBOARD_NAME)
        + r"'|\""
        + re.escape(DASHBOARD_NAME)
        + r"\")",
        text,
    ):
        fail(f"Dashboard already exists: {DASHBOARD_NAME}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint = (
        CHECKPOINT_DIR
        / f"{source.stem}_pre_dashboard_automation_{timestamp}.twb"
    )

    shutil.copy2(source, checkpoint)

    success(f"Checkpoint created: {checkpoint}")
    success(f"Checkpoint SHA-256: {sha256(checkpoint)}")

    candidate = (
        source.parent
        / f"{source.stem}_AUTOMATED_{timestamp}.twb"
    )

    dashboard_xml = build_dashboard_xml()

    if "</dashboards>" not in text:
        fail("Could not find </dashboards> insertion point.")

    candidate_text = text.replace(
        "  </dashboards>",
        dashboard_xml + "\n  </dashboards>",
        1,
    )

    dashboard_window = clone_dashboard_window(text)

    if dashboard_window:
        if "</windows>" not in candidate_text:
            fail("Dashboard window was generated but </windows> is missing.")

        candidate_text = candidate_text.replace(
            "  </windows>",
            dashboard_window + "\n  </windows>",
            1,
        )

        success("Cloned Dashboard 2 window metadata for candidate dashboard.")

    # Dashboard 2 was scaffolding only. Remove it after harvesting its
    # Tableau-generated window syntax so production KPI 01 has no legacy
    # bootstrap-dashboard ownership.
    candidate_text = remove_bootstrap_dashboard2(candidate_text)

    candidate.write_text(candidate_text, encoding="utf-8")

    # ------------------------------------------------------------------
    # Candidate validation
    # ------------------------------------------------------------------

    info("Validating candidate XML...")

    try:
        ElementTree.parse(candidate)
    except ElementTree.ParseError as exc:
        candidate.unlink(missing_ok=True)
        fail(f"Generated candidate is not valid XML: {exc}")

    success("Candidate is well-formed XML.")

    generated = candidate.read_text(encoding="utf-8")

    match = re.search(
        r"<dashboard\b[^>]*\bname='"
        + re.escape(DASHBOARD_NAME)
        + r"'[^>]*>[\s\S]*?</dashboard>",
        generated,
    )

    if not match:
        fail("Generated executive dashboard could not be re-read.")

    dashboard = match.group(0)

    for sheet in EXPECTED_DASHBOARD_SHEETS:
        if f"name='{sheet}'" not in dashboard:
            fail(f"Dashboard is missing worksheet zone: {sheet}")

    success(
        f"Dashboard contains all {len(EXPECTED_DASHBOARD_SHEETS)} "
        "expected worksheet zones."
    )

    size_match = re.search(
        r"<size[^>]+maxheight='1000'[^>]+maxwidth='1400'",
        dashboard,
    )

    if not size_match:
        fail("Dashboard does not retain expected 1400 × 1000 fixed size.")

    success("Dashboard dimensions validated at 1400 × 1000.")

    dashboard_names = re.findall(
        r"<dashboard\b[^>]*\bname=(?:'([^']+)'|\"([^\"]+)\")",
        generated,
    )

    flattened_names = [a or b for a, b in dashboard_names]

    if flattened_names.count(DASHBOARD_NAME) != 1:
        fail(
            "Expected exactly one generated executive dashboard, found "
            f"{flattened_names.count(DASHBOARD_NAME)}."
        )

    if SOURCE_PLAYER_COMBAT_SHEET in generated:
        fail(
            "Source player-combat worksheet name unexpectedly remains in "
            "generated candidate."
        )

    if CANDIDATE_PLAYER_COMBAT_SHEET not in generated:
        fail(
            "Candidate player-combat worksheet name is missing from "
            "generated candidate."
        )

    # Explicitly prove the source file remained unchanged.
    final_source_hash = sha256(source)

    if final_source_hash != source_hash:
        fail(
            "Source workbook changed during generation.\n"
            f"Before: {source_hash}\n"
            f"After:  {final_source_hash}"
        )

    candidate_hash = sha256(candidate)

    result_file = (
        RESULTS_DIR
        / f"tableau_dashboard_automation_{timestamp}.txt"
    )

    result_file.write_text(
        "\n".join(
            [
                "TABLEAU EXECUTIVE DASHBOARD AUTOMATION",
                f"Source: {source}",
                f"Source SHA256: {source_hash}",
                f"Checkpoint: {checkpoint}",
                f"Checkpoint SHA256: {sha256(checkpoint)}",
                f"Candidate: {candidate}",
                f"Candidate SHA256: {candidate_hash}",
                f"Dashboard: {DASHBOARD_NAME}",
                "Dashboard Size: 1400x1000",
                f"Worksheet Zones: {len(EXPECTED_DASHBOARD_SHEETS)}",
                f"Source Player Combat Sheet: {SOURCE_PLAYER_COMBAT_SHEET}",
                f"Candidate Player Combat Sheet: {CANDIDATE_PLAYER_COMBAT_SHEET}",
                "Source Modified: NO",
                "Status: PASS",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 78)
    print(" AUTOMATION COMPLETE")
    print("=" * 78)
    print(f"Source:      {source}")
    print(f"Checkpoint:  {checkpoint}")
    print(f"Candidate:   {candidate}")
    print(f"Result log:  {result_file}")
    print(f"SHA-256:     {candidate_hash}")
    print()
    print(f"{BOLD}{GREEN}PASS:{RESET} Source workbook was NOT modified.")
    print(
        f"{BOLD}{YELLOW}NEXT:{RESET} Open the candidate in Tableau for "
        "visual validation before promotion."
    )


if __name__ == "__main__":
    main()
