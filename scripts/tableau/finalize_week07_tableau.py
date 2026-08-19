#!/usr/bin/env python3
"""Finalize the DataExpert Week 7 Tableau workbook contract."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

BRANCH = "feature/week07-data-visualization-finalization"

SOURCE = Path(
    "data_visualization/tableau_homework/tableau/"
    "CeasarJackson_DataExpert_Tableau_Homework_AUTOMATED_20260818_204557.twb"
)

EXPECTED_SHA = "a0d7c8e08311a7b8bff492394e522a905f24b2ed473b6b4cc3f1576a607342ea"

RESULTS = Path(
    "data_visualization/tableau_homework/validation/results"
)

DAILY = "federated.1ul5i980sl8mhx17damkr106y1e5"
PLAYERS = "federated.1yyt3be0kzraxu14te5vx00wolrf"
MEDAL_SUMMARY = "federated.1vy04sp10qrx3o1erb2c11t1zcv0"
MEDALS = "federated.1mg9f830ivlerq1h7h3l01kcjv03"

EXEC_DASH = "Halo Multiplayer Performance: Executive Overview"
EXP_DASH = "Halo Player & Medal Explorer"


def die(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def simple_id() -> str:
    return f"{{{str(uuid.uuid4()).upper()}}}"


def worksheet(
    name: str,
    caption: str,
    ds: str,
    dependencies: str,
    rows: str,
    cols: str,
    extra_view: str = "",
    encodings: str = "",
) -> str:
    enc = ""
    if encodings:
        enc = f"""
            <encodings>
{encodings}
            </encodings>"""

    return f"""    <worksheet name='{name}'>
      <table>
        <view>
          <datasources>
            <datasource caption='{caption}' name='{ds}' />
          </datasources>
          <datasource-dependencies datasource='{ds}'>
{dependencies}
          </datasource-dependencies>
{extra_view}          <aggregation value='true' />
        </view>
        <style />
        <panes>
          <pane selection-relaxation-option='selection-relaxation-allow'>
            <view>
              <breakdown value='auto' />
            </view>
            <mark class='Automatic' />{enc}
          </pane>
        </panes>
        <rows>{rows}</rows>
        <cols>{cols}</cols>
      </table>
      <simple-id uuid='{simple_id()}' />
    </worksheet>"""


def zone(zone_id: int, name: str, x: int, y: int, w: int, h: int) -> str:
    return f"""          <zone h='{h}' id='{zone_id}' name='{name}' w='{w}' x='{x}' y='{y}'>
            <zone-style>
              <format attr='border-color' value='#000000' />
              <format attr='border-style' value='none' />
              <format attr='border-width' value='0' />
              <format attr='margin' value='4' />
            </zone-style>
          </zone>"""


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&apos;")
        .replace('"', "&quot;")
    )


def dashboard(name: str, title: str, sheets: list[str]) -> str:
    xml_name = xml_escape(name)
    xml_title = xml_escape(title)

    zones = [
        f"""          <zone forceUpdate='true' h='7000' id='10' type-v2='text' w='98400' x='800' y='1000'>
            <formatted-text>
              <run bold='true' fontsize='20'>{xml_title}</run>
            </formatted-text>
          </zone>"""
    ]

    if len(sheets) == 10:
        for i, sheet in enumerate(sheets[:6]):
            zones.append(zone(20 + i, sheet, 800 + i * 16400, 8500, 16000, 15000))

        zones.extend([
            zone(40, sheets[6], 800, 24500, 48700, 35500),
            zone(41, sheets[7], 50500, 24500, 48700, 35500),
            zone(42, sheets[8], 800, 61000, 48700, 37000),
            zone(43, sheets[9], 50500, 61000, 48700, 37000),
        ])
    else:
        zones.extend([
            zone(30, sheets[0], 800, 9000, 48700, 28000),
            zone(31, sheets[1], 50500, 9000, 48700, 28000),
            zone(32, sheets[2], 800, 38000, 32000, 28000),
            zone(33, sheets[3], 34000, 38000, 32000, 28000),
            zone(34, sheets[4], 67200, 38000, 32000, 28000),
            zone(35, sheets[5], 800, 67000, 98400, 31000),
        ])

    body = "\n".join(zones)

    return f"""    <dashboard enable-sort-zone-taborder='true' name='{xml_name}'>
      <style />
      <size maxheight='1000' maxwidth='1400' minheight='1000' minwidth='1400' sizing-mode='fixed' />
      <zones>
        <zone h='100000' id='4' type-v2='layout-basic' w='100000' x='0' y='0'>
{body}
        </zone>
      </zones>
      <simple-id uuid='{simple_id()}' />
    </dashboard>"""


def main() -> None:
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    if branch != BRANCH:
        die(f"expected branch {BRANCH}; found {branch}")

    if not SOURCE.is_file():
        die(f"candidate missing: {SOURCE}")

    source_sha = sha256(SOURCE)
    if source_sha != EXPECTED_SHA:
        die(f"candidate SHA mismatch: {source_sha}")

    text = SOURCE.read_text(encoding="utf-8")

    required_absent = [
        "EXEC 01 — Matches Over Time",
        "EXEC 02 — Combat Performance Trend",
        "EXEC 03 — Top Established Players",
        "EXEC 04 — Top Medal Distribution",
        "EXP 05 — Player Medal Leaderboard",
        "EXP 06 — Player / Medal Detail",
        EXEC_DASH,
        EXP_DASH,
    ]

    for name in required_absent:
        if f"name='{name}'" in text:
            die(f"target already exists: {name}")

    sheets = []

    sheets.append(worksheet(
        "EXEC 01 — Matches Over Time",
        "executive_daily_performance",
        DAILY,
        """            <column caption='Completion Date' datatype='date' name='[completion_date]' role='dimension' type='ordinal' />
            <column caption='Matches' datatype='integer' name='[matches]' role='measure' type='quantitative' />
            <column-instance column='[completion_date]' derivation='Week-Trunc' name='[twk:completion_date:qk]' pivot='key' type='quantitative' />
            <column-instance column='[matches]' derivation='Sum' name='[sum:matches:qk]' pivot='key' type='quantitative' />""",
        f"[{DAILY}].[sum:matches:qk]",
        f"[{DAILY}].[twk:completion_date:qk]",
    ))

    sheets.append(worksheet(
        "EXEC 02 — Combat Performance Trend",
        "executive_daily_performance",
        DAILY,
        """            <column caption='Completion Date' datatype='date' name='[completion_date]' role='dimension' type='ordinal' />
            <column caption='Kill Death Ratio' datatype='real' name='[kill_death_ratio]' role='measure' type='quantitative' />
            <column-instance column='[completion_date]' derivation='Week-Trunc' name='[twk:completion_date:qk]' pivot='key' type='quantitative' />
            <column-instance column='[kill_death_ratio]' derivation='Avg' name='[avg:kill_death_ratio:qk]' pivot='key' type='quantitative' />""",
        f"[{DAILY}].[avg:kill_death_ratio:qk]",
        f"[{DAILY}].[twk:completion_date:qk]",
    ))

    sheets.append(worksheet(
        "EXEC 03 — Top Established Players",
        "executive_player_performance",
        PLAYERS,
        """            <column caption='Player Gamertag' datatype='string' name='[player_gamertag]' role='dimension' type='nominal' />
            <column caption='Kills' datatype='integer' name='[kills]' role='measure' type='quantitative' />
            <column datatype='integer' name='[established_player_flag]' role='measure' type='quantitative' />
            <column-instance column='[player_gamertag]' derivation='None' name='[none:player_gamertag:nk]' pivot='key' type='nominal' />
            <column-instance column='[kills]' derivation='Sum' name='[sum:kills:qk]' pivot='key' type='quantitative' />
            <column-instance column='[established_player_flag]' derivation='None' name='[none:established_player_flag:qk]' pivot='key' type='quantitative' />""",
        f"[{PLAYERS}].[none:player_gamertag:nk]",
        f"[{PLAYERS}].[sum:kills:qk]",
        f"""          <filter class='quantitative' column='[{PLAYERS}].[none:established_player_flag:qk]' included-values='in-range'>
            <min>1</min><max>1</max>
          </filter>
""",
    ))

    sheets.append(worksheet(
        "EXEC 04 — Top Medal Distribution",
        "exploratory_medal_summary",
        MEDAL_SUMMARY,
        """            <column caption='Medal Name' datatype='string' name='[medal_name]' role='dimension' type='nominal' />
            <column caption='Medal Count' datatype='integer' name='[medal_count]' role='measure' type='quantitative' />
            <column-instance column='[medal_name]' derivation='None' name='[none:medal_name:nk]' pivot='key' type='nominal' />
            <column-instance column='[medal_count]' derivation='Sum' name='[sum:medal_count:qk]' pivot='key' type='quantitative' />""",
        f"[{MEDAL_SUMMARY}].[none:medal_name:nk]",
        f"[{MEDAL_SUMMARY}].[sum:medal_count:qk]",
    ))

    sheets.append(worksheet(
        "EXP 05 — Player Medal Leaderboard",
        "exploratory_daily_player_medals",
        MEDALS,
        """            <column caption='Player Gamertag' datatype='string' name='[player_gamertag]' role='dimension' type='nominal' />
            <column caption='Medal Count' datatype='integer' name='[medal_count]' role='measure' type='quantitative' />
            <column-instance column='[player_gamertag]' derivation='None' name='[none:player_gamertag:nk]' pivot='key' type='nominal' />
            <column-instance column='[medal_count]' derivation='Sum' name='[sum:medal_count:qk]' pivot='key' type='quantitative' />""",
        f"[{MEDALS}].[none:player_gamertag:nk]",
        f"[{MEDALS}].[sum:medal_count:qk]",
    ))

    sheets.append(worksheet(
        "EXP 06 — Player / Medal Detail",
        "exploratory_daily_player_medals",
        MEDALS,
        """            <column caption='Player Gamertag' datatype='string' name='[player_gamertag]' role='dimension' type='nominal' />
            <column caption='Medal Name' datatype='string' name='[medal_name]' role='dimension' type='nominal' />
            <column caption='Medal Count' datatype='integer' name='[medal_count]' role='measure' type='quantitative' />
            <column-instance column='[player_gamertag]' derivation='None' name='[none:player_gamertag:nk]' pivot='key' type='nominal' />
            <column-instance column='[medal_name]' derivation='None' name='[none:medal_name:nk]' pivot='key' type='nominal' />
            <column-instance column='[medal_count]' derivation='Sum' name='[sum:medal_count:qk]' pivot='key' type='quantitative' />""",
        f"[{MEDALS}].[none:player_gamertag:nk] / [{MEDALS}].[none:medal_name:nk]",
        f"[{MEDALS}].[sum:medal_count:qk]",
        encodings=f"              <text column='[{MEDALS}].[sum:medal_count:qk]' />",
    ))

    if "  </worksheets>" not in text:
        die("missing </worksheets>")

    text = text.replace(
        "  </worksheets>",
        "\n".join(sheets) + "\n  </worksheets>",
        1,
    )

    exec_sheets = [
        "KPI 01 — Matches with Player Data",
        "KPI 02 — Unique Players",
        "KPI 03 — Total Kills",
        "KPI 04 — Overall K/D",
        "KPI 05 — Player Win Rate",
        "KPI 06 — Medals Awarded",
        "EXEC 01 — Matches Over Time",
        "EXEC 02 — Combat Performance Trend",
        "EXEC 03 — Top Established Players",
        "EXEC 04 — Top Medal Distribution",
    ]

    exp_sheets = [
        "EXP 01 — Medal Volume Over Time",
        "EXP 02 — Medal Ranking",
        "EXP 03 — Medal Classification Mix",
        "EXP 04 — Medal Difficulty Mix",
        "EXP 05 — Player Medal Leaderboard",
        "EXP 06 — Player / Medal Detail",
    ]

    dashboards = (
        dashboard(EXEC_DASH, "Halo Multiplayer Performance — Executive Overview", exec_sheets)
        + "\n"
        + dashboard(EXP_DASH, "Halo Player &amp; Medal Explorer", exp_sheets)
    )

    if "  </dashboards>" not in text:
        die("missing </dashboards>")

    text = text.replace(
        "  </dashboards>",
        dashboards + "\n  </dashboards>",
        1,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = SOURCE.with_name(
        "CeasarJackson_DataExpert_Tableau_Homework_FINAL_"
        f"{timestamp}.twb"
    )

    output.write_text(text, encoding="utf-8")

    try:
        ET.parse(output)
    except ET.ParseError as exc:
        output.unlink(missing_ok=True)
        die(f"generated XML invalid: {exc}")

    if sha256(SOURCE) != source_sha:
        die("source candidate changed during finalization")

    RESULTS.mkdir(parents=True, exist_ok=True)

    report = RESULTS / f"week07_finalization_{timestamp}.txt"
    report.write_text(
        "\n".join([
            "WEEK 07 TABLEAU FINALIZATION",
            f"Source: {SOURCE}",
            f"Source SHA256: {source_sha}",
            f"Final: {output}",
            f"Final SHA256: {sha256(output)}",
            f"Executive Dashboard: {EXEC_DASH}",
            f"Exploratory Dashboard: {EXP_DASH}",
            "Source Modified: NO",
            "XML Status: PASS",
            "",
        ]),
        encoding="utf-8",
    )

    print("=" * 78)
    print(" WEEK 07 TABLEAU FINALIZATION COMPLETE")
    print("=" * 78)
    print(f"Final workbook: {output}")
    print(f"SHA-256:        {sha256(output)}")
    print(f"Report:         {report}")


if __name__ == "__main__":
    main()
