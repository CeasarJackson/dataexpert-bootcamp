#!/usr/bin/env python3
"""
===============================================================================
DataExpert Boot Camp - Tableau Input Validator
===============================================================================
Author: Ceasar Jackson
Purpose: Validate compact prepared Tableau datasets and expected KPI values.
===============================================================================
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List

RESET="\033[0m"; GREEN="\033[32m"; RED="\033[31m"; CYAN="\033[36m"
def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if sys.stdout.isatty() else text

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def count_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as f:
        return max(sum(1 for _ in f)-1,0)

def read_single_row(path: Path) -> Dict[str,str]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=1:
        raise ValueError(f"{path} must contain exactly one data row; found {len(rows)}")
    return rows[0]

EXPECTED_FILES={
    "executive_kpis.csv":1,
    "executive_daily_performance.csv":269,
    "executive_player_performance.csv":69420,
    "exploratory_medal_summary.csv":136,
}
EXPECTED_KPIS={
    "matches_with_player_data":"19050",
    "unique_players":"69420",
    "total_kills":"1350442",
    "overall_kill_death_ratio":"0.9869",
    "player_appearance_win_rate":"0.4797",
    "total_medals_awarded":"1560446",
}

def main() -> int:
    p=argparse.ArgumentParser(description="Validate DataExpert Tableau homework inputs.")
    p.add_argument("--workspace", type=Path, required=True)
    args=p.parse_args()
    ws=args.workspace.resolve(); prepared=ws/"data"/"prepared"
    failures: List[str]=[]; report={"workspace":str(ws),"files":{},"kpis":{}}
    print(color("="*72,CYAN)); print(color("TABLEAU INPUT VALIDATION",CYAN)); print(color("="*72,CYAN))
    for fn, expected in EXPECTED_FILES.items():
        path=prepared/fn
        if not path.is_file():
            failures.append(f"missing required dataset: {path}"); print(color(f"FAIL: {path}",RED)); continue
        rows=count_rows(path); report["files"][fn]={"rows":rows,"sha256":sha256(path),"bytes":path.stat().st_size}
        if rows!=expected:
            msg=f"{fn}: expected {expected:,} rows; found {rows:,}"; failures.append(msg); print(color(f"FAIL: {msg}",RED))
        else: print(color(f"PASS: {fn} rows={rows:,}",GREEN))
    kp=prepared/"executive_kpis.csv"
    if kp.is_file():
        try:
            row=read_single_row(kp)
            for field, expected in EXPECTED_KPIS.items():
                actual=row.get(field); report["kpis"][field]=actual
                if actual!=expected:
                    msg=f"{field}: expected {expected}; found {actual}"; failures.append(msg); print(color(f"FAIL: {msg}",RED))
                else: print(color(f"PASS: {field}={actual}",GREEN))
        except Exception as exc:
            failures.append(str(exc)); print(color(f"FAIL: {exc}",RED))
    out=ws/"validation"/"results"/"tableau_input_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True); report["status"]="FAIL" if failures else "PASS"; report["failures"]=failures
    out.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(f"Report: {out}")
    if failures:
        print(color(f"FAIL: {len(failures)} validation issue(s)",RED)); return 1
    print(color("PASS: Tableau input validation complete",GREEN)); return 0

if __name__=="__main__":
    raise SystemExit(main())
