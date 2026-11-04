"""Build only the Chinese question PDF. This script does not export answers."""

from html import escape
from pathlib import Path
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Preformatted, Spacer,
    KeepTogether, PageBreak,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Homework_3_题干翻译.md"
OUTPUT = ROOT / "Homework_3_题干翻译.pdf"
pdfmetrics.registerFont(TTFont("CJK", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("CJK-Bold", r"C:\Windows\Fonts\msyhbd.ttc", subfontIndex=0))
pdfmetrics.registerFontFamily("CJK", normal="CJK", bold="CJK-Bold", italic="CJK", boldItalic="CJK-Bold")
INK = colors.HexColor("#20252c")
BLUE = colors.HexColor("#264c70")
STYLES = {
    "title": ParagraphStyle("title", fontName="CJK-Bold", fontSize=20, leading=29, textColor=INK, spaceAfter=14),
    "body": ParagraphStyle("body", fontName="CJK", fontSize=10.3, leading=17.2, textColor=INK, wordWrap="CJK", spaceAfter=9),
    "note": ParagraphStyle("note", fontName="CJK", fontSize=8.4, leading=13.5, textColor=colors.HexColor("#58616b"), wordWrap="CJK", spaceAfter=9),
    "heading": ParagraphStyle("heading", fontName="CJK-Bold", fontSize=13.8, leading=21, textColor=BLUE, spaceBefore=12, spaceAfter=8, keepWithNext=True),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=8.2, leading=11.6, textColor=INK, backColor=colors.HexColor("#f4f5f7"), borderPadding=9, spaceBefore=3, spaceAfter=12),
    "equation": ParagraphStyle("equation", fontName="CJK", fontSize=12, leading=23, alignment=TA_CENTER, textColor=INK, spaceBefore=3, spaceAfter=12),
}


def latex(text):
    text = re.sub(r"\\(?:mathrm|text)\{([^{}]*)\}", r"\1", text)
    text = text.replace(r"\min", "min").replace(r"\max", "max")
    text = text.replace(r"\ldots", "…").replace(r"\times", "×").replace(r"\leq", "≤").replace(r"\geq", "≥")
    text = text.replace(r"\ ", " ").replace(r"\,", " ")
    text = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", text)
    text = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"<super>\1</super>", text)
    text = re.sub(r"\^([A-Za-z0-9])", r"<super>\1</super>", text)
    return text


def inline(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    parts = re.split(r"(\$[^$]+\$|`[^`]+`)", text)
    result = []
    for part in parts:
        if part.startswith("$") and part.endswith("$"):
            result.append(latex(escape(part[1:-1])))
        elif part.startswith("`") and part.endswith("`"):
            result.append('<font name="Courier" size="9.1">' + escape(part[1:-1]) + "</font>")
        else:
            result.append(re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escape(part)))
    return "".join(result)


def footer(canvas, document):
    width, height = A4
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d9dfe5"))
    canvas.setLineWidth(0.5)
    canvas.line(45, height - 35, width - 45, height - 35)
    canvas.setFont("CJK", 8)
    canvas.setFillColor(colors.HexColor("#65717d"))
    canvas.drawString(45, height - 26, "计算机网络作业三 · 题干翻译")
    canvas.drawRightString(width - 45, 25, str(document.page))
    canvas.restoreState()


def build():
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story = []
    index = 0
    current = None
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), STYLES["title"]))
        elif line.startswith("## "):
            current = line[3:]
            if current in ("P3-3", "P3-6"):
                story.append(PageBreak())
            story.append(Paragraph(current, STYLES["heading"]))
        elif line.startswith("```"):
            index += 1
            code = []
            while index < len(lines) and not lines[index].startswith("```"):
                code.extend(textwrap.wrap(lines[index], width=102, expand_tabs=False,
                                          replace_whitespace=False, drop_whitespace=False,
                                          break_long_words=True, break_on_hyphens=False) or [""])
                index += 1
            story.append(Preformatted("\n".join(code), STYLES["code"]))
        elif line == "$$":
            index += 1
            equation = []
            while index < len(lines) and lines[index] != "$$":
                equation.append(lines[index])
                index += 1
            raw = "".join(equation)
            if raw != r"\max\left\{\frac{NF}{u_s},\frac{F}{d_{\min}}\right\}.":
                raise ValueError(f"Unrecognized question equation: {raw}")
            equation_text = "max { NF/u<sub>s</sub>, F/d<sub>min</sub> }。"
            story.append(Paragraph(equation_text, STYLES["equation"]))
        else:
            style = STYLES["note"] if current is None else STYLES["body"]
            story.append(Paragraph(inline(line), style))
        index += 1
    width, height = A4
    document = BaseDocTemplate(str(OUTPUT), pagesize=A4, title="计算机网络作业三：题干翻译", author="", leftMargin=45, rightMargin=45, topMargin=51, bottomMargin=44)
    document.addPageTemplates(PageTemplate(id="questions", frames=[Frame(45, 44, width - 90, height - 95, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer))
    document.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
