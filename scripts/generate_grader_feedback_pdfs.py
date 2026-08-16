#!/usr/bin/env python3
"""
===============================================================================
DataExpert Bootcamp - Grader Feedback PDF Generator
===============================================================================

Author:
    Ceasar Jackson

Purpose:
    Generate a professional PDF reference for every canonical grader-feedback
    Markdown file in the DataExpert Bootcamp repository.

Canonical convention:
    <homework>/docs/CeasarJackson_<Homework>_Grader_Feedback.md
    <homework>/docs/CeasarJackson_<Homework>_Grader_Feedback.pdf

Design goals:
    - Keep Markdown as the searchable / Git-diffable source of truth.
    - Produce a matching archival PDF for visual/reference use.
    - Avoid installing PDF libraries into the active project environment.
    - Support batch generation across all homework directories.
    - Fail safely and report exactly which files succeeded or failed.

Recommended execution:
    uv run --with reportlab \
      scripts/generate_grader_feedback_pdfs.py \
      --root .

Examples:
    # Discover what would be generated
    uv run --with reportlab \
      scripts/generate_grader_feedback_pdfs.py \
      --root . --dry-run

    # Generate/update all canonical feedback PDFs
    uv run --with reportlab \
      scripts/generate_grader_feedback_pdfs.py \
      --root . --force

    # Generate one Markdown file
    uv run --with reportlab \
      scripts/generate_grader_feedback_pdfs.py \
      --single apache_flink/week05_sessionization/docs/CeasarJackson_Week5_DataExpert_Grader_Feedback.md \
      --force

    # Validate that matching PDFs exist and are non-empty
    uv run --with reportlab \
      scripts/generate_grader_feedback_pdfs.py \
      --root . --check

Notes:
    - The script intentionally targets files ending in "_Grader_Feedback.md".
    - Existing PDFs are preserved unless --force is supplied or the Markdown
      source is newer than the PDF.
    - Markdown is rendered with a conservative, readable archival layout.
===============================================================================
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        KeepTogether,
        ListFlowable,
        ListItem,
        PageBreak,
        Paragraph,
        Preformatted,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError as exc:
    print(
        "ERROR: reportlab is required.\n"
        "Recommended invocation:\n"
        "  uv run --with reportlab scripts/generate_grader_feedback_pdfs.py --root .",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


# ---------------------------------------------------------------------------
# Terminal output
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"


def _use_color() -> bool:
    return sys.stdout.isatty()


def paint(text: str, color: str) -> str:
    return f"{color}{text}{RESET}" if _use_color() else text


def info(message: str) -> None:
    print(paint(f"INFO: {message}", CYAN))


def ok(message: str) -> None:
    print(paint(f"PASS: {message}", GREEN))


def warn(message: str) -> None:
    print(paint(f"WARN: {message}", YELLOW))


def fail(message: str) -> None:
    print(paint(f"FAIL: {message}", RED), file=sys.stderr)


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD_TEXT = re.compile(r"\*\*([^*]+)\*\*")
ITALIC_TEXT = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
LINK_TEXT = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def inline_markup(text: str) -> str:
    """Convert a conservative Markdown inline subset to ReportLab XML."""
    escaped = html.escape(text, quote=False)

    # Links first so nested punctuation is preserved.
    escaped = LINK_TEXT.sub(
        lambda m: f'<link href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</link>',
        escaped,
    )
    escaped = INLINE_CODE.sub(r'<font name="Courier">\1</font>', escaped)
    escaped = BOLD_TEXT.sub(r"<b>\1</b>", escaped)
    escaped = ITALIC_TEXT.sub(r"<i>\1</i>", escaped)
    return escaped


def split_table_row(line: str) -> List[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells)


@dataclass
class ParsedBlock:
    kind: str
    payload: object
    level: int = 0


def parse_markdown(text: str) -> List[ParsedBlock]:
    lines = text.splitlines()
    blocks: List[ParsedBlock] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            blocks.append(ParsedBlock("rule", None))
            i += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            code_lines: List[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            blocks.append(ParsedBlock("code", ("\n".join(code_lines), language)))
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            blocks.append(
                ParsedBlock("heading", heading.group(2).strip(), len(heading.group(1)))
            )
            i += 1
            continue

        # Markdown table: header row followed by separator row.
        if "|" in line and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            rows = [split_table_row(line)]
            i += 2
            while i < len(lines):
                candidate = lines[i]
                if not candidate.strip() or "|" not in candidate:
                    break
                rows.append(split_table_row(candidate))
                i += 1
            blocks.append(ParsedBlock("table", rows))
            continue

        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].lstrip())
                i += 1
            blocks.append(ParsedBlock("quote", " ".join(quote_lines)))
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: List[str] = []
            while i < len(lines):
                m = re.match(r"^[-*]\s+(.*)$", lines[i].strip())
                if not m:
                    break
                items.append(m.group(1).strip())
                i += 1
            blocks.append(ParsedBlock("ulist", items))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines):
                m = re.match(r"^\d+\.\s+(.*)$", lines[i].strip())
                if not m:
                    break
                items.append(m.group(1).strip())
                i += 1
            blocks.append(ParsedBlock("olist", items))
            continue

        # Standard paragraph, joining wrapped Markdown lines.
        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt == "---"
                or nxt.startswith("#")
                or nxt.startswith("```")
                or nxt.startswith(">")
                or re.match(r"^[-*]\s+", nxt)
                or re.match(r"^\d+\.\s+", nxt)
                or ("|" in lines[i] and i + 1 < len(lines) and is_table_separator(lines[i + 1]))
            ):
                break
            paragraph_lines.append(nxt)
            i += 1

        blocks.append(ParsedBlock("paragraph", " ".join(paragraph_lines)))

    return blocks


# ---------------------------------------------------------------------------
# PDF rendering
# ---------------------------------------------------------------------------

def build_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ArchiveTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            spaceAfter=10,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArchiveH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            spaceBefore=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArchiveH3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            spaceBefore=9,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArchiveH4",
            parent=styles["Heading4"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArchiveBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArchiveQuote",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=13,
            leftIndent=18,
            borderWidth=0,
            spaceBefore=4,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArchiveCode",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            leftIndent=8,
            rightIndent=8,
            spaceBefore=5,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArchiveFooter",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            textColor=colors.HexColor("#666666"),
            alignment=TA_CENTER,
        )
    )
    return styles


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = LETTER

    canvas.setStrokeColor(colors.HexColor("#D0D0D0"))
    canvas.setLineWidth(0.5)
    canvas.line(0.65 * inch, 0.48 * inch, width - 0.65 * inch, 0.48 * inch)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(0.65 * inch, 0.30 * inch, "DataExpert Bootcamp - Grader Feedback Archive")
    canvas.drawRightString(
        width - 0.65 * inch,
        0.30 * inch,
        f"Page {canvas.getPageNumber()}",
    )
    canvas.restoreState()


def table_from_rows(rows: Sequence[Sequence[str]], styles) -> Table:
    if not rows:
        return Table([[""]])

    width_count = max(len(r) for r in rows)
    normalized = [list(r) + [""] * (width_count - len(r)) for r in rows]

    data = []
    for r_index, row in enumerate(normalized):
        data.append(
            [
                Paragraph(
                    inline_markup(cell),
                    styles["ArchiveBody"],
                )
                for cell in row
            ]
        )

    usable_width = 7.2 * inch
    col_widths = [usable_width / width_count] * width_count

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AAAAAA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def render_markdown_to_pdf(source: Path, target: Path) -> None:
    styles = build_styles()
    blocks = parse_markdown(source.read_text(encoding="utf-8"))

    doc = SimpleDocTemplate(
        str(target),
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=source.stem,
        author="Ceasar Jackson",
        subject="DataExpert Bootcamp grader feedback archive",
    )

    story = []

    for block in blocks:
        if block.kind == "heading":
            level = block.level
            style_name = {
                1: "ArchiveTitle",
                2: "ArchiveH2",
                3: "ArchiveH3",
            }.get(level, "ArchiveH4")
            story.append(Paragraph(inline_markup(str(block.payload)), styles[style_name]))
            continue

        if block.kind == "paragraph":
            story.append(
                Paragraph(inline_markup(str(block.payload)), styles["ArchiveBody"])
            )
            continue

        if block.kind == "quote":
            story.append(
                Paragraph(inline_markup(str(block.payload)), styles["ArchiveQuote"])
            )
            continue

        if block.kind == "code":
            code, _language = block.payload  # type: ignore[misc]
            story.append(
                Preformatted(
                    str(code),
                    styles["ArchiveCode"],
                    maxLineLength=110,
                )
            )
            continue

        if block.kind == "rule":
            story.append(Spacer(1, 4))
            rule = Table([[""]], colWidths=[7.2 * inch], rowHeights=[1])
            rule.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#B0B0B0")),
                    ]
                )
            )
            story.append(rule)
            story.append(Spacer(1, 8))
            continue

        if block.kind in {"ulist", "olist"}:
            items = [
                ListItem(
                    Paragraph(inline_markup(item), styles["ArchiveBody"]),
                    leftIndent=12,
                )
                for item in block.payload  # type: ignore[union-attr]
            ]
            story.append(
                ListFlowable(
                    items,
                    bulletType="1" if block.kind == "olist" else "bullet",
                    leftIndent=22,
                    bulletFontName="Helvetica",
                    bulletFontSize=8,
                    spaceAfter=6,
                )
            )
            continue

        if block.kind == "table":
            story.append(table_from_rows(block.payload, styles))  # type: ignore[arg-type]
            story.append(Spacer(1, 8))
            continue

    target.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


# ---------------------------------------------------------------------------
# Discovery / validation
# ---------------------------------------------------------------------------

def discover(root: Path) -> List[Path]:
    return sorted(
        p for p in root.rglob("*_Grader_Feedback.md")
        if ".git" not in p.parts
    )


def target_for(source: Path) -> Path:
    return source.with_suffix(".pdf")


def needs_generation(source: Path, target: Path, force: bool) -> bool:
    if force:
        return True
    if not target.exists():
        return True
    return source.stat().st_mtime > target.stat().st_mtime


def validate_pair(source: Path, target: Path) -> Tuple[bool, str]:
    if not source.is_file():
        return False, f"missing Markdown source: {source}"
    if not target.is_file():
        return False, f"missing PDF: {target}"
    if target.stat().st_size <= 0:
        return False, f"empty PDF: {target}"

    try:
        data = target.read_bytes()[:5]
    except OSError as exc:
        return False, f"unable to read PDF {target}: {exc}"

    if data != b"%PDF-":
        return False, f"invalid PDF signature: {target}"

    return True, "OK"


def relative_display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate matching PDFs for DataExpert grader-feedback Markdown files."
    )
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to scan recursively (default: current directory).",
    )
    source_group.add_argument(
        "--single",
        type=Path,
        help="Generate/check one explicit *_Grader_Feedback.md file.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate PDFs even when they appear current.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing PDFs.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate matching PDF existence/signature instead of generating.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.single:
        source = args.single.expanduser().resolve()
        root = Path.cwd().resolve()
        sources = [source]
    else:
        root = args.root.expanduser().resolve()
        sources = discover(root)

    print("=" * 79)
    print(" DATAEXPERT BOOTCAMP - GRADER FEEDBACK PDF GENERATOR")
    print("=" * 79)
    print(f"Root: {root}")
    print(f"Mode: {'CHECK' if args.check else 'DRY-RUN' if args.dry_run else 'GENERATE'}")
    print(f"Discovered Markdown files: {len(sources)}")
    print()

    if not sources:
        warn("No *_Grader_Feedback.md files found.")
        return 0

    failures = 0
    generated = 0
    skipped = 0

    for source in sources:
        target = target_for(source)
        source_display = relative_display(source, root)
        target_display = relative_display(target, root)

        if not source.is_file():
            fail(f"missing source: {source_display}")
            failures += 1
            continue

        if args.check:
            valid, reason = validate_pair(source, target)
            if valid:
                ok(f"{target_display}")
            else:
                fail(reason)
                failures += 1
            continue

        if not needs_generation(source, target, args.force):
            ok(f"current: {target_display}")
            skipped += 1
            continue

        if args.dry_run:
            info(f"would generate: {source_display} -> {target_display}")
            continue

        try:
            render_markdown_to_pdf(source, target)
        except Exception as exc:
            fail(f"{source_display}: {exc}")
            failures += 1
            continue

        valid, reason = validate_pair(source, target)
        if not valid:
            fail(reason)
            failures += 1
            continue

        ok(f"generated: {target_display} ({target.stat().st_size:,} bytes)")
        generated += 1

    print()
    print("=" * 79)
    print(
        f"Summary: generated={generated} skipped={skipped} "
        f"failures={failures} total={len(sources)}"
    )
    print("=" * 79)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
