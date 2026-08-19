#!/usr/bin/env python3
"""
===============================================================================
DataExpert Boot Camp - Tableau Workbook Validator
===============================================================================
Author: Ceasar Jackson
Purpose: Validate required Tableau worksheets, dashboards, and source refs.
===============================================================================
"""
from __future__ import annotations

import argparse, json, sys, zipfile
from pathlib import Path
from typing import List
from xml.etree import ElementTree as ET

RESET="\033[0m"; GREEN="\033[32m"; RED="\033[31m"; CYAN="\033[36m"
def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if sys.stdout.isatty() else text

REQUIRED_WORKSHEETS=[
"KPI 01 — Matches with Player Data","KPI 02 — Unique Players","KPI 03 — Total Kills","KPI 04 — Overall K/D","KPI 05 — Player Win Rate","KPI 06 — Medals Awarded",
"EXEC 01 — Matches Over Time","EXEC 02 — Combat Performance Trend","EXEC 03 — Top Established Players","EXEC 04 — Top Medal Distribution",
"EXP 01 — Medal Volume Over Time","EXP 02 — Medal Ranking","EXP 03 — Medal Classification Mix","EXP 04 — Medal Difficulty Mix","EXP 05 — Player Medal Leaderboard","EXP 06 — Player / Medal Detail"]
REQUIRED_DASHBOARDS=["Halo Multiplayer Performance: Executive Overview","Halo Player & Medal Explorer"]
SOURCE_TOKENS=["executive_kpis.csv","executive_daily_performance.csv","executive_player_performance.csv","exploratory_medal_summary.csv","exploratory_daily_player_medals.csv"]

def load_xml(path: Path):
    if path.suffix.lower()==".twb": return path.read_text(encoding="utf-8"), str(path)
    if path.suffix.lower()==".twbx":
        with zipfile.ZipFile(path) as z:
            names=[n for n in z.namelist() if n.lower().endswith(".twb")]
            if len(names)!=1: raise ValueError(f"TWBX must contain exactly one .twb; found {len(names)}")
            return z.read(names[0]).decode("utf-8"), f"{path}!/{names[0]}"
    raise ValueError("Workbook must be .twb or .twbx")

def names(root, parent_tag, child_tag):
    parent=root.find(parent_tag)
    if parent is None: return []
    return [x.attrib["name"] for x in parent.findall(child_tag) if x.attrib.get("name")]

def main() -> int:
    p=argparse.ArgumentParser(description="Validate Tableau workbook contract.")
    p.add_argument("--workbook", type=Path, required=True); p.add_argument("--workspace", type=Path, required=True)
    a=p.parse_args(); wb=a.workbook.resolve(); ws=a.workspace.resolve()
    if not wb.is_file(): print(color(f"FAIL: workbook missing: {wb}",RED)); return 1
    try: xml, origin=load_xml(wb); root=ET.fromstring(xml)
    except Exception as exc: print(color(f"FAIL: parse error: {exc}",RED)); return 1
    worksheets=names(root,"worksheets","worksheet"); dashboards=names(root,"dashboards","dashboard"); failures=[]
    print(color("="*72,CYAN)); print(color("TABLEAU WORKBOOK VALIDATION",CYAN)); print(color("="*72,CYAN)); print(f"Workbook XML: {origin}")
    for n in REQUIRED_WORKSHEETS:
        if n in worksheets: print(color(f"PASS: worksheet: {n}",GREEN))
        else: failures.append(f"missing worksheet: {n}"); print(color(f"FAIL: worksheet: {n}",RED))
    for n in REQUIRED_DASHBOARDS:
        if n in dashboards: print(color(f"PASS: dashboard: {n}",GREEN))
        else: failures.append(f"missing dashboard: {n}"); print(color(f"FAIL: dashboard: {n}",RED))
    for tok in SOURCE_TOKENS:
        if tok in xml: print(color(f"PASS: source reference: {tok}",GREEN))
        else: failures.append(f"missing source reference: {tok}"); print(color(f"FAIL: source reference: {tok}",RED))
    out=ws/"validation"/"results"/"tableau_workbook_validation.json"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"workbook":str(wb),"worksheets":worksheets,"dashboards":dashboards,"failures":failures,"status":"FAIL" if failures else "PASS"},indent=2)+"\n",encoding="utf-8")
    print(f"Report: {out}")
    if failures: print(color(f"FAIL: {len(failures)} workbook issue(s)",RED)); return 1
    print(color("PASS: Tableau workbook contract satisfied",GREEN)); return 0

if __name__=="__main__": raise SystemExit(main())
