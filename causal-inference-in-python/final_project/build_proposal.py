"""Build the four-page proposal PDF from its editable Markdown source."""

from __future__ import annotations

import html
import re
import argparse
from functools import partial
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "final_project_proposal.pdf"
INK = colors.HexColor("#192B3A")
TEAL = colors.HexColor("#167D8D")
GRAY = colors.HexColor("#52616B")
PALE = colors.HexColor("#EEF5F7")


def register_fonts() -> tuple[str, str, str, str]:
    system = Path("/System/Library/Fonts/Supplemental")
    files = {
        "Body": "Georgia.ttf",
        "BodyBold": "Georgia Bold.ttf",
        "Heading": "Arial.ttf",
        "HeadingBold": "Arial Bold.ttf",
    }
    if not all((system / file).exists() for file in files.values()):
        return "Times-Roman", "Times-Bold", "Helvetica", "Helvetica-Bold"
    for name, file in files.items():
        pdfmetrics.registerFont(TTFont(name, str(system / file)))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold")
    pdfmetrics.registerFontFamily("Heading", normal="Heading", bold="HeadingBold")
    return "Body", "BodyBold", "Heading", "HeadingBold"


BODY, BODY_BOLD, SANS, SANS_BOLD = register_fonts()
STYLES = {
    "title": ParagraphStyle(
        "title", fontName=SANS_BOLD, fontSize=23, leading=26,
        textColor=INK, spaceAfter=4,
    ),
    "subtitle": ParagraphStyle(
        "subtitle", fontName=SANS, fontSize=13, leading=17,
        textColor=TEAL, spaceAfter=10,
    ),
    "meta": ParagraphStyle(
        "meta", fontName=SANS, fontSize=8.6, leading=11,
        textColor=GRAY, spaceAfter=10,
    ),
    "section": ParagraphStyle(
        "section", fontName=SANS_BOLD, fontSize=12.1, leading=15,
        textColor=TEAL, spaceBefore=7, spaceAfter=6, keepWithNext=True,
    ),
    "body": ParagraphStyle(
        "body", fontName=BODY, fontSize=10.2, leading=14,
        textColor=INK, spaceAfter=6, alignment=TA_LEFT,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName=BODY, fontSize=10, leading=13.5,
        textColor=INK, leftIndent=10, firstLineIndent=-7, spaceAfter=4.5,
    ),
    "reference": ParagraphStyle(
        "reference", fontName=SANS, fontSize=8.5, leading=11.3,
        textColor=GRAY, spaceAfter=5,
    ),
    "code": ParagraphStyle(
        "code", fontName="Courier", fontSize=8.5, leading=10.8,
        textColor=INK, backColor=PALE, borderPadding=7,
        leftIndent=7, rightIndent=7, spaceBefore=3, spaceAfter=9,
    ),
}


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: f'<link href="{m.group(2)}" color="#167D8D">{m.group(1)}</link>',
        escaped,
    )
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    # Italics map to the regular face to keep the font setup portable.
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", escaped)
    return escaped


class CausalGraph(Flowable):
    """A compact native-vector working DAG, not an empirical graph estimate."""

    def __init__(self, dataset: str = "IHDP") -> None:
        super().__init__()
        self.width = 504
        self.height = 64
        self.dataset = dataset

    def draw(self) -> None:
        c = self.canv
        c.setFillColor(PALE)
        c.roundRect(0, 3, self.width, 57, 5, stroke=0, fill=1)
        c.setFont(SANS_BOLD, 8)
        c.setFillColor(GRAY)
        c.drawString(11, 47, "WORKING DAG")
        nodes = {"X": (205, 43), "T": (155, 17), "Y": (305, 17)}
        edges = [("X", "T"), ("X", "Y"), ("T", "Y")]
        labels = ["X: baseline covariates", "T: intervention", "Y: simulated outcome"]
        if self.dataset == "Twins":
            labels = ["X: baseline pair risk", "T: twin observed", "Y: recorded mortality"]
        elif self.dataset == "Lalonde":
            labels = ["X: baseline covariates", "T: training assignment", "Y: 1978 earnings"]
        elif self.dataset == "Criteo":
            nodes = {"X": (235, 43), "T": (135, 17), "E": (235, 17), "Y": (315, 17)}
            edges = [("T", "E"), ("E", "Y"), ("X", "Y")]
            labels = ["T: ad eligibility; E: exposure", "X: pre-assignment features", "Y: conversion"]

        def arrow(x1: float, y1: float, x2: float, y2: float) -> None:
            import math

            angle = math.atan2(y2 - y1, x2 - x1)
            start = (x1 + 11 * math.cos(angle), y1 + 11 * math.sin(angle))
            end = (x2 - 12 * math.cos(angle), y2 - 12 * math.sin(angle))
            c.setStrokeColor(TEAL)
            c.setLineWidth(1)
            c.line(*start, *end)
            path = c.beginPath()
            path.moveTo(*end)
            path.lineTo(end[0] - 5 * math.cos(angle - .45), end[1] - 5 * math.sin(angle - .45))
            path.lineTo(end[0] - 5 * math.cos(angle + .45), end[1] - 5 * math.sin(angle + .45))
            path.close()
            c.setFillColor(TEAL)
            c.drawPath(path, fill=1, stroke=0)

        for start, end in edges:
            arrow(*nodes[start], *nodes[end])
        if self.dataset == "Criteo":
            # X -> E runs vertically behind the two circles.
            arrow(*nodes["X"], *nodes["E"])
        for label, (x, y) in nodes.items():
            c.setFillColor(colors.white)
            c.circle(x, y, 10, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont(SANS_BOLD, 10)
            c.drawCentredString(x, y - 3, label)
        c.setFont(SANS, 7.6)
        c.setFillColor(GRAY)
        for y, label in zip([35, 24, 13], labels):
            c.drawString(350, y, label)


def page_furniture(canvas, doc, dataset="IHDP", date="November 3, 2026") -> None:
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(1.3)
    canvas.line(54, h - 35, w - 54, h - 35)
    canvas.setFont(SANS, 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(54, h - 26, "CAUSAL MODELS  /  FINAL PROJECT PROPOSAL")
    canvas.drawRightString(w - 54, h - 26, dataset.upper())
    canvas.setStrokeColor(colors.HexColor("#D6E0E5"))
    canvas.setLineWidth(.5)
    canvas.line(54, 39, w - 54, 39)
    canvas.setFont(SANS, 7.5)
    canvas.drawString(54, 26, f"Sovin Birla  |  {date}")
    canvas.drawRightString(w - 54, 26, f"{doc.page} / 4")
    canvas.restoreState()


def build(source_path=None, output_path=None, dataset="IHDP", date="November 3, 2026") -> None:
    source_path = Path(source_path) if source_path else ROOT / "proposal.md"
    output_path = Path(output_path) if output_path else OUTPUT
    source = source_path.read_text()
    story = []
    references = False
    blocks = re.split(r"\n\s*\n", source.strip())
    for block in blocks:
        block = block.strip()
        if block == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif block.startswith("```text\n"):
            code = block.removeprefix("```text\n").removesuffix("\n```")
            story.append(KeepTogether([Preformatted(code, STYLES["code"])]))
        elif block.startswith("Working DAG:"):
            story.append(CausalGraph(dataset))
            story.append(Spacer(1, 4))
        elif block.startswith("# "):
            story.append(Paragraph(inline(block[2:]), STYLES["title"]))
        elif block.startswith("## "):
            story.append(Paragraph(inline(block[3:]), STYLES["subtitle"]))
        elif block.startswith("### "):
            heading = block[4:]
            references = heading == "References"
            story.append(Paragraph(inline(heading), STYLES["section"]))
        elif block.startswith("**Final project proposal"):
            story.append(Paragraph(inline(block.replace("**", "")), STYLES["meta"]))
        elif block.startswith("- "):
            for line in block.splitlines():
                story.append(Paragraph("&#8226; " + inline(line[2:]), STYLES["bullet"]))
        else:
            style = STYLES["reference"] if references else STYLES["body"]
            story.append(Paragraph(inline(" ".join(block.splitlines())), style))

    title = " ".join(line.lstrip("# ") for line in source.splitlines() if line.startswith(("# ", "## ")))
    document = SimpleDocTemplate(
        str(output_path), pagesize=letter, leftMargin=54, rightMargin=54,
        topMargin=47, bottomMargin=51,
        title=title,
        author="Sovin Birla", subject="Final project proposal for Causal Models",
    )
    decorate = partial(page_furniture, dataset=dataset, date=date)
    document.build(story, onFirstPage=decorate, onLaterPages=decorate)
    reader = PdfReader(output_path)
    if len(reader.pages) != 4:
        raise RuntimeError(f"Expected four pages; found {len(reader.pages)}. Adjust layout before delivery.")
    print(f"Created {output_path.name}: {len(reader.pages)} pages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dataset", default="IHDP", choices=["IHDP", "Twins", "Lalonde", "Criteo"])
    parser.add_argument("--date", default="November 3, 2026")
    args = parser.parse_args()
    build(args.source, args.output, args.dataset, args.date)
