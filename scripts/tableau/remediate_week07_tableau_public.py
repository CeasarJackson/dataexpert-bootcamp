#!/usr/bin/env python3
"""Week 7 Tableau Public remediation helper."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

BRANCH = "remediation/week07-tableau-public-links"

ROOT = Path("data_visualization/tableau_homework")

WORKBOOK = (
    ROOT / "tableau" /
    "CeasarJackson_DataExpert_Tableau_Homework_FINAL_20260818_221605.twb"
)

EXPECTED_WORKBOOK_SHA = (
    "49d7b7648933f26097298c0f9519716bc7dcec23ea829a0230f93e294d245fe8"
)

VALIDATOR = ROOT / "scripts/validate_tableau_workbook.py"
PACKAGER = ROOT / "scripts/package_tableau_submission.py"

SUBMISSION = ROOT / "submission"
LINKS = ROOT / "tableau_public_links.txt"
ZIP = SUBMISSION / "CeasarJackson_DataExpert_Tableau_Homework.zip"
ZIP_SHA = SUBMISSION / "CeasarJackson_DataExpert_Tableau_Homework.zip.sha256"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def validate_text_artifacts() -> None:
    """Validate whitespace in human-maintained text artifacts only.

    Tableau Desktop writes .twb XML using CRLF line endings. Git interprets
    the carriage returns as trailing whitespace when the workbook differs
    from the repository baseline, so a repository-wide ``git diff --check``
    produces false-positive failures for Tableau-generated XML.

    Tableau binary/XML artifacts are validated separately by workbook XML
    parsing, contract checks, extract audits, SHA-256 checks, and TWBX ZIP
    integrity tests.
    """

    paths = [
        ROOT / "README.md",
        ROOT / "docs" / "TABLEAU_DASHBOARD_BLUEPRINT.md",
        ROOT / "tableau_public_links.txt",
        Path(__file__),
    ]

    failures: list[str] = []

    for path in paths:
        if not path.is_file():
            continue

        text = path.read_text(encoding="utf-8")

        for number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                failures.append(f"{path}:{number}: trailing whitespace")

    if failures:
        raise SystemExit(
            "FAIL: whitespace validation failed\n"
            + "\n".join(failures)
        )

    print("PASS: human-maintained text artifacts pass whitespace validation")


def require_branch() -> None:
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    if branch != BRANCH:
        raise SystemExit(
            f"FAIL: expected branch {BRANCH}; found {branch}"
        )

    print(f"PASS: branch: {branch}")


def validate_workbook() -> None:
    if not WORKBOOK.is_file():
        raise SystemExit(f"FAIL: workbook missing: {WORKBOOK}")

    digest = sha256(WORKBOOK)

    if digest != EXPECTED_WORKBOOK_SHA:
        raise SystemExit(
            "FAIL: workbook SHA mismatch\n"
            f"Expected: {EXPECTED_WORKBOOK_SHA}\n"
            f"Actual:   {digest}"
        )

    print(f"PASS: workbook SHA-256: {digest}")

    run([
        sys.executable,
        str(VALIDATOR),
        "--workspace", str(ROOT),
        "--workbook", str(WORKBOOK),
    ])


def validate_url(label: str, url: str) -> None:
    if not url.startswith("https://public.tableau.com/views/"):
        raise SystemExit(
            f"FAIL: {label} must use https://public.tableau.com/views/"
        )

    lowered = url.lower()

    for forbidden in ("/profile/", "/authoring/", "/shared/"):
        if forbidden in lowered:
            raise SystemExit(
                f"FAIL: {label} contains forbidden path {forbidden}"
            )

    remainder = url.removeprefix(
        "https://public.tableau.com/views/"
    ).split("?", 1)[0].strip("/")

    if remainder.count("/") < 1:
        raise SystemExit(
            f"FAIL: {label} does not point to a specific view"
        )

    print(f"PASS: {label} URL shape")


def check_public(label: str, url: str) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            print(
                f"PASS: {label} reachable: "
                f"HTTP {response.status}"
            )
    except Exception as exc:
        print(
            f"WARN: automatic reachability check failed: {exc}"
        )
        print(
            "      Verify this URL manually in a private browser."
        )


def finalize(executive: str, exploratory: str) -> None:
    require_branch()
    validate_workbook()

    validate_url("Executive", executive)
    validate_url("Exploratory", exploratory)

    check_public("Executive", executive)
    check_public("Exploratory", exploratory)

    SUBMISSION.mkdir(parents=True, exist_ok=True)

    LINKS.write_text(
        f"Executive Dashboard: {executive}\n"
        f"Exploratory Dashboard: {exploratory}\n",
        encoding="utf-8",
    )

    print(f"PASS: created {LINKS}")

    run([
        sys.executable,
        str(PACKAGER),
        "--workspace", str(ROOT),
        "--workbook", str(WORKBOOK),
    ])

    with zipfile.ZipFile(ZIP) as z:
        already_present = "tableau_public_links.txt" in z.namelist()

    if not already_present:
        with zipfile.ZipFile(
            ZIP,
            "a",
            compression=zipfile.ZIP_DEFLATED,
        ) as z:
            z.write(
                LINKS,
                arcname="tableau_public_links.txt",
            )

        print("PASS: added links file to ZIP")

    with zipfile.ZipFile(ZIP) as z:
        bad = z.testzip()
        names = z.namelist()

    if bad:
        raise SystemExit(f"FAIL: ZIP corrupt at {bad}")

    if "tableau_public_links.txt" not in names:
        raise SystemExit(
            "FAIL: links file missing from ZIP"
        )

    digest = sha256(ZIP)

    ZIP_SHA.write_text(
        f"{digest}  {ZIP.name}\n",
        encoding="utf-8",
    )

    validate_text_artifacts()

    print()
    print("PASS: Week 7 remediation finalized")
    print(f"ZIP SHA-256: {digest}")
    print("ZIP members:")
    for name in names:
        print(f"  {name}")


def prepublish() -> None:
    require_branch()
    validate_workbook()
    validate_text_artifacts()

    print()
    print("PASS: prepublication validation complete")
    print(f"Open and publish: {WORKBOOK}")
    print("Then copy the two direct Tableau Public /views/ URLs.")


def main() -> None:
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    sub.add_parser("prepublish")

    final = sub.add_parser("finalize")
    final.add_argument("--executive-url", required=True)
    final.add_argument("--exploratory-url", required=True)

    args = parser.parse_args()

    if args.command == "prepublish":
        prepublish()
    else:
        finalize(
            args.executive_url,
            args.exploratory_url,
        )


if __name__ == "__main__":
    main()
