#!/usr/bin/env python3
"""
===============================================================================
DataExpert Boot Camp - Tableau Submission Packager
===============================================================================
Author: Ceasar Jackson
Purpose: Create a reproducible Tableau submission ZIP and SHA-256 checksum.
===============================================================================
"""
from __future__ import annotations
import argparse, hashlib, sys, zipfile
from pathlib import Path

RESET="\033[0m"; GREEN="\033[32m"; RED="\033[31m"; CYAN="\033[36m"
def color(text, code): return f"{code}{text}{RESET}" if sys.stdout.isatty() else text
def sha256(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def main()->int:
    p=argparse.ArgumentParser(description="Package Tableau homework submission.")
    p.add_argument("--workspace",type=Path,required=True); p.add_argument("--workbook",type=Path,required=True); p.add_argument("--output",type=Path)
    a=p.parse_args(); ws=a.workspace.resolve(); wb=a.workbook.resolve()
    if not wb.is_file(): print(color(f"FAIL: workbook missing: {wb}",RED)); return 1
    support=[ws/"README.md",ws/"docs"/"TABLEAU_DASHBOARD_BLUEPRINT.md",ws/"validation"/"results"/"tableau_dashboard_dataset_summary.json",ws/"validation"/"results"/"source_profile.txt"]
    missing=[p for p in support if not p.is_file()]
    if missing:
        [print(color(f"FAIL: missing support file: {p}",RED)) for p in missing]; return 1
    out=(a.output or (ws/"submission"/"CeasarJackson_DataExpert_Tableau_Homework.zip")).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists(): out.unlink()
    print(color("="*72,CYAN)); print(color("TABLEAU SUBMISSION PACKAGING",CYAN)); print(color("="*72,CYAN))
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for path in [wb]+support:
            z.write(path,arcname=path.name); print(color(f"ADD: {path.name}",GREEN))
    with zipfile.ZipFile(out) as z:
        bad=z.testzip()
        if bad: print(color(f"FAIL: corrupt member: {bad}",RED)); return 1
    digest=sha256(out); sha=out.with_suffix(out.suffix+".sha256"); sha.write_text(f"{digest}  {out.name}\n",encoding="utf-8")
    print(color(f"PASS: ZIP: {out}",GREEN)); print(color(f"PASS: SHA256: {digest}",GREEN)); return 0

if __name__=="__main__": raise SystemExit(main())
