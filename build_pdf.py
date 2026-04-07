#!/usr/bin/env python3
"""
PWMP SEO Audit — PDF report generator.

Reads a JSON payload describing a client audit and produces a branded
PDF in PWMP colors (#07457C navy, #BC0300 red) using ReportLab.

Usage:
    python scripts/build_pdf.py --payload path/to/payload.json --out path/to/report.pdf
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Brand constants
# ---------------------------------------------------------------------------
PWMP_NAVY = colors.HexColor("#07457C")
PWMP_RED = colors.HexColor("#BC0300")
PWMP_LIGHT_GREY = colors.HexColor("#F2F4F7")
PWMP_DARK_GREY = colors.HexColor("#333333")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = PROJECT_ROOT / "templates" / "pdf" / "assets" / "pwmp-logo.png"
FOOTER_TEXT = "Prepared by Pressure Washing Marketing Pros  |  Confidential"

PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN = 0.75 * inch


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {}

    styles["CoverTitle"] = ParagraphStyle(
        "CoverTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=PWMP_NAVY,
        alignment=TA_CENTER,
        spaceBefore=24,
        spaceAfter=24,
    )
    styles["CoverSub"] = ParagraphStyle(
        "CoverSub",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        alignment=TA_CENTER,
        textColor=PWMP_DARK_GREY,
        spaceAfter=6,
    )
    styles["H1"] = ParagraphStyle(
        "H1",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PWMP_NAVY,
        spaceBefore=6,
        spaceAfter=14,
    )
    styles["H2"] = ParagraphStyle(
        "H2",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=PWMP_NAVY,
        spaceBefore=10,
        spaceAfter=6,
    )
    styles["Body"] = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=PWMP_DARK_GREY,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    styles["Bullet"] = ParagraphStyle(
        "Bullet",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=PWMP_DARK_GREY,
        leftIndent=14,
        bulletIndent=4,
    )
    styles["ConflictFlag"] = ParagraphStyle(
        "ConflictFlag",
        parent=base["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=15,
        textColor=colors.white,
    )
    return styles


# ---------------------------------------------------------------------------
# Page template with footer + page numbers
# ---------------------------------------------------------------------------
def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(PWMP_DARK_GREY)
    canvas.drawString(MARGIN, 0.4 * inch, FOOTER_TEXT)
    canvas.drawRightString(
        PAGE_WIDTH - MARGIN, 0.4 * inch, f"Page {doc.page}"
    )
    canvas.setStrokeColor(PWMP_NAVY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 0.55 * inch, PAGE_WIDTH - MARGIN, 0.55 * inch)
    canvas.restoreState()


def _draw_cover_footer(canvas, doc):
    # Cover page: no page number displayed, still draw small footer line.
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(PWMP_DARK_GREY)
    canvas.drawCentredString(PAGE_WIDTH / 2, 0.4 * inch, FOOTER_TEXT)
    canvas.restoreState()


def build_doc(out_path: Path) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        str(out_path),
        pagesize=LETTER,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=0.75 * inch,
        title="PWMP SEO & Local Visibility Audit",
        author="Pressure Washing Marketing Pros",
    )
    frame = Frame(
        MARGIN,
        0.75 * inch,
        PAGE_WIDTH - 2 * MARGIN,
        PAGE_HEIGHT - MARGIN - 0.75 * inch,
        id="body",
    )
    cover = PageTemplate(id="Cover", frames=frame, onPage=_draw_cover_footer)
    body = PageTemplate(id="Body", frames=frame, onPage=_draw_footer)
    doc.addPageTemplates([cover, body])
    return doc


# ---------------------------------------------------------------------------
# Flowable builders
# ---------------------------------------------------------------------------
def bullet_list(items: list[str], styles: dict[str, ParagraphStyle]) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(i, styles["Body"]), leftIndent=10) for i in items or []],
        bulletType="bullet",
        start="•",
        bulletColor=PWMP_NAVY,
        leftIndent=12,
    )


def conflict_callout(conflict: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    text = (
        f"⚠ <b>Data Conflict Noted:</b> The client indicated "
        f"<i>{conflict.get('typeform_value', '—')}</i> on their intake form, but "
        f"<i>{conflict.get('transcript_value', '—')}</i> was agreed upon during the "
        f"strategy call. This report uses the "
        f"{'strategy call' if conflict.get('resolution') == 'transcript' else 'intake form'}"
        f" as the source of truth for "
        f"<b>{conflict.get('field', 'this field')}</b>."
    )
    para = Paragraph(text, styles["ConflictFlag"])
    tbl = Table([[para]], colWidths=[PAGE_WIDTH - 2 * MARGIN - 0.2 * inch])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PWMP_RED),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 1, PWMP_RED),
            ]
        )
    )
    return tbl


def section_heading(num: int, title: str, styles) -> Paragraph:
    return Paragraph(f"{num}. {title}", styles["H1"])


def subheading(text: str, styles) -> Paragraph:
    return Paragraph(text, styles["H2"])


def body(text: str, styles) -> Paragraph:
    return Paragraph(text, styles["Body"])


def conflicts_for_section(section_name: str, conflicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [c for c in conflicts or [] if c.get("section") == section_name]


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------
def build_cover(payload: dict[str, Any], styles) -> list[Any]:
    story: list[Any] = []
    story.append(Spacer(1, 0.6 * inch))
    if LOGO_PATH.exists():
        try:
            img = Image(str(LOGO_PATH), width=2.8 * inch, height=1.1 * inch, kind="proportional")
            img.hAlign = "CENTER"
            story.append(img)
        except Exception:
            story.append(Paragraph("Pressure Washing Marketing Pros", styles["CoverTitle"]))
    else:
        story.append(Paragraph("Pressure Washing Marketing Pros", styles["CoverTitle"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("SEO &amp; LOCAL VISIBILITY<br/>AUDIT REPORT", styles["CoverTitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"<b>Client:</b> {payload.get('business_name', '—')}", styles["CoverSub"]))
    story.append(Paragraph(f"<b>Primary Market:</b> {payload.get('primary_market', '—')}", styles["CoverSub"]))
    story.append(Paragraph("<b>Prepared For:</b> Strategy &amp; Implementation Planning", styles["CoverSub"]))
    story.append(Paragraph("<b>Prepared By:</b> Pressure Washing Marketing Pros", styles["CoverSub"]))
    story.append(
        Paragraph(
            f"<b>Date:</b> {payload.get('date') or datetime.today().strftime('%B %d, %Y')}",
            styles["CoverSub"],
        )
    )
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())
    return story


def build_exec_summary(sections, conflicts, styles) -> list[Any]:
    story = [section_heading(1, "Executive Summary", styles)]
    for c in conflicts_for_section("Executive Summary", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    summary = sections.get("executive_summary", "—")
    story.append(body(summary, styles))
    story.append(PageBreak())
    return story


def build_gbp(sections, conflicts, styles) -> list[Any]:
    data = sections.get("gbp_review", {}) or {}
    story = [section_heading(2, "Google Business Profile (GBP) Review", styles)]
    for c in conflicts_for_section("Google Business Profile Review", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(subheading("Current Status", styles))
    story.append(bullet_list(data.get("current_status", []), styles))
    story.append(subheading("Identified Gaps", styles))
    story.append(bullet_list(data.get("identified_gaps", []), styles))
    story.append(subheading("Recommendations", styles))
    story.append(bullet_list(data.get("recommendations", []), styles))
    story.append(PageBreak())
    return story


def build_indexed_pages(sections, conflicts, styles) -> list[Any]:
    data = sections.get("indexed_pages", {}) or {}
    story = [section_heading(3, "Indexed Pages & Site Structure Review", styles)]
    for c in conflicts_for_section("Indexed Pages & Site Structure Review", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(subheading("Currently Indexed Pages", styles))
    story.append(bullet_list(data.get("pages", []), styles))
    story.append(subheading("Key Observations", styles))
    story.append(bullet_list(data.get("observations", []), styles))
    story.append(subheading("Impact", styles))
    story.append(body(data.get("impact", "—"), styles))
    story.append(PageBreak())
    return story


def build_keyword_strategy(sections, conflicts, styles) -> list[Any]:
    data = sections.get("keyword_strategy", {}) or {}
    story = [section_heading(4, "Keyword Strategy & Targeting Rationale", styles)]
    for c in conflicts_for_section("Keyword Strategy & Targeting Rationale", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(subheading("Recommended Primary Target", styles))
    story.append(body(data.get("recommended_primary_target", "—"), styles))
    story.append(subheading("Reasoning", styles))
    story.append(body(data.get("reasoning", "—"), styles))
    story.append(subheading("Strategic Outcome", styles))
    story.append(body(data.get("strategic_outcome", "—"), styles))
    story.append(PageBreak())
    return story


def build_backlink_technical(sections, conflicts, styles) -> list[Any]:
    data = sections.get("backlink_technical", {}) or {}
    story = [section_heading(5, "Backlink & Technical SEO Analysis", styles)]
    for c in conflicts_for_section("Backlink & Technical SEO Analysis", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(subheading("Backlink Profile", styles))
    story.append(
        body(
            f"<b>Total backlinks:</b> {data.get('total_backlinks', '—')}  &nbsp;•&nbsp;  "
            f"<b>Domain Rating:</b> {data.get('domain_rating', '—')}",
            styles,
        )
    )
    story.append(body(data.get("anchor_analysis", "—"), styles))
    story.append(subheading("Issues Identified", styles))
    story.append(bullet_list(data.get("issues", []), styles))
    story.append(subheading("Technical Observations", styles))
    story.append(bullet_list(data.get("technical_observations", []), styles))
    story.append(subheading("Recommendations", styles))
    story.append(bullet_list(data.get("recommendations", []), styles))
    story.append(PageBreak())
    return story


def build_rankings(sections, conflicts, styles) -> list[Any]:
    data = sections.get("rankings", {}) or {}
    story = [section_heading(6, "Current Rankings Assessment", styles)]
    for c in conflicts_for_section("Current Rankings Assessment", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    keywords = data.get("current_keywords", []) or []
    if keywords:
        table_data = [["Keyword", "Position"]]
        for kw in keywords:
            table_data.append([kw.get("keyword", "—"), str(kw.get("position", "—"))])
        tbl = Table(table_data, colWidths=[4.5 * inch, 1.5 * inch])
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), PWMP_NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.4, PWMP_NAVY),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PWMP_LIGHT_GREY]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(tbl)
        story.append(Spacer(1, 0.15 * inch))
    else:
        story.append(body("No ranking keywords found in Ahrefs data.", styles))
    story.append(subheading("Root Causes of Ranking Gaps", styles))
    story.append(bullet_list(data.get("root_causes", []), styles))
    story.append(PageBreak())
    return story


def build_competitors(sections, conflicts, styles) -> list[Any]:
    comps = sections.get("competitors", []) or []
    gaps = sections.get("market_gaps", []) or []
    story = [section_heading(7, "Competitor & Content Gap Analysis", styles)]
    for c in conflicts_for_section("Competitor & Content Gap Analysis", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(subheading("Top Competitors Identified", styles))
    if comps:
        table_data = [["Competitor", "Founded", "Reviews", "Notable Strengths"]]
        for c in comps:
            table_data.append(
                [
                    c.get("name", "—"),
                    str(c.get("founded", "—")),
                    c.get("reviews", "—"),
                    Paragraph(c.get("strengths", "—"), styles["Body"]),
                ]
            )
        tbl = Table(
            table_data,
            colWidths=[1.7 * inch, 0.8 * inch, 1.3 * inch, 3.2 * inch],
        )
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), PWMP_NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                    ("GRID", (0, 0), (-1, -1), 0.4, PWMP_NAVY),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PWMP_LIGHT_GREY]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(tbl)
        story.append(Spacer(1, 0.15 * inch))
    story.append(subheading("Critical Market Gaps Across Competitors", styles))
    story.append(bullet_list(gaps, styles))
    story.append(PageBreak())
    return story


def build_advantages(sections, conflicts, styles) -> list[Any]:
    advs = sections.get("competitive_advantages", []) or []
    story = [section_heading(8, "Competitive Advantages to Pursue", styles)]
    for c in conflicts_for_section("Competitive Advantages to Pursue", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(bullet_list(advs, styles))
    story.append(PageBreak())
    return story


def build_ads_insight(sections, conflicts, styles) -> list[Any]:
    text = sections.get("ads_insight", "—")
    story = [section_heading(9, "Google Ads Search Term Insight (Keyword Validation)", styles)]
    for c in conflicts_for_section("Google Ads Search Term Insight", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(body(text, styles))
    story.append(PageBreak())
    return story


def build_keyword_opportunities(sections, conflicts, styles) -> list[Any]:
    data = sections.get("keyword_opportunities", {}) or {}
    story = [section_heading(10, "High-Intent Keyword Opportunities", styles)]
    for c in conflicts_for_section("High-Intent Keyword Opportunities", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    groups = [
        ("A. Core Service + Location (Highest Priority)", data.get("core_service_location", [])),
        ("B. Surface-Specific Keywords (High Conversion)", data.get("surface_specific", [])),
        ("C. Cross-Service Keywords", data.get("cross_service", [])),
        ("D. \u201cNear Me\u201d & Mobile Searches", data.get("near_me", [])),
    ]
    for title, items in groups:
        story.append(subheading(title, styles))
        story.append(bullet_list(items, styles))
    story.append(PageBreak())
    return story


def build_money_pages(sections, conflicts, styles) -> list[Any]:
    data = sections.get("money_pages", {}) or {}
    story = [section_heading(11, "Core Money Pages to Build & Optimize", styles)]
    for c in conflicts_for_section("Core Money Pages to Build & Optimize", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    story.append(subheading("Homepage", styles))
    story.append(body(data.get("homepage", "—"), styles))
    story.append(subheading("Residential Services", styles))
    story.append(bullet_list(data.get("residential", []), styles))
    story.append(subheading("Commercial Services", styles))
    story.append(bullet_list(data.get("commercial", []), styles))
    story.append(
        body(
            "<i>Each page should include: process breakdown, before/after visuals, FAQs, "
            "internal links, and location relevance.</i>",
            styles,
        )
    )
    story.append(PageBreak())
    return story


def build_roadmap(sections, conflicts, styles) -> list[Any]:
    data = sections.get("roadmap", {}) or {}
    story = [section_heading(12, "Strategic Roadmap", styles)]
    for c in conflicts_for_section("Strategic Roadmap", conflicts):
        story.append(conflict_callout(c, styles))
        story.append(Spacer(1, 0.1 * inch))
    phases = [
        ("Phase 1: Foundation (0\u201360 Days)", data.get("phase_1", [])),
        ("Phase 2: Expansion (60\u2013120 Days)", data.get("phase_2", [])),
        ("Phase 3: Domination (120+ Days)", data.get("phase_3", [])),
    ]
    for title, items in phases:
        story.append(subheading(title, styles))
        story.append(bullet_list(items, styles))
    return story


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def build_story(payload: dict[str, Any], styles) -> list[Any]:
    sections = payload.get("sections", {}) or {}
    conflicts = payload.get("conflicts", []) or []
    story: list[Any] = []
    story.extend(build_cover(payload, styles))
    story.extend(build_exec_summary(sections, conflicts, styles))
    story.extend(build_gbp(sections, conflicts, styles))
    story.extend(build_indexed_pages(sections, conflicts, styles))
    story.extend(build_keyword_strategy(sections, conflicts, styles))
    story.extend(build_backlink_technical(sections, conflicts, styles))
    story.extend(build_rankings(sections, conflicts, styles))
    story.extend(build_competitors(sections, conflicts, styles))
    story.extend(build_advantages(sections, conflicts, styles))
    story.extend(build_ads_insight(sections, conflicts, styles))
    story.extend(build_keyword_opportunities(sections, conflicts, styles))
    story.extend(build_money_pages(sections, conflicts, styles))
    story.extend(build_roadmap(sections, conflicts, styles))
    return story


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate PWMP SEO audit PDF.")
    ap.add_argument("--payload", required=True, help="Path to JSON payload file.")
    ap.add_argument("--out", required=True, help="Output PDF path.")
    args = ap.parse_args()

    payload_path = Path(args.payload)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with payload_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not LOGO_PATH.exists():
        print(
            f"[build_pdf] WARNING: logo not found at {LOGO_PATH}. "
            "The cover will fall back to a text title. Drop the PWMP logo "
            "at that path for full branding.",
            file=sys.stderr,
        )

    styles = build_styles()
    doc = build_doc(out_path)
    story = build_story(payload, styles)
    doc.build(story)
    print(f"[build_pdf] Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
