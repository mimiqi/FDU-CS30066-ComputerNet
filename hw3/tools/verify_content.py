"""Check source-message fidelity, answer calculations, links, and PDF text."""

from fractions import Fraction
from pathlib import Path
import re
from urllib.parse import unquote

import pdfplumber
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
question_path = ROOT / "Homework_3_题干翻译.md"
answer_path = ROOT / "Homework_3_解答.md"
questions = question_path.read_text(encoding="utf-8")
answers = answer_path.read_text(encoding="utf-8")
blocks = re.findall(r"```text\n(.*?)\n```", questions, re.S)
with pdfplumber.open(ROOT / "Homework_3.pdf") as original:
    pages = [page.extract_text(x_tolerance=2, y_tolerance=3) for page in original.pages]
request = re.search(r"(GET /cs453/.*?<cr><lf><cr><lf>)", pages[0].replace("\n", ""), re.S).group(1)
response = pages[1].split("HTTP/1.1 200 OK", 1)[1].split("a. Was the server", 1)[0]
response = "HTTP/1.1 200 OK" + response.replace("\n", "").strip()
assert request == blocks[0].replace("\n", ""), "Request differs from original"
assert response == blocks[1].replace("\n", ""), "Response differs from original"
print("PASS: both HTTP messages match original text exactly after removing layout newlines")

expected_headings = [f"## P3-{i}" for i in range(1, 10)]
assert re.findall(r"^## P3-[1-9]$", questions, re.M) == expected_headings
assert re.findall(r"^## P3-[1-9]$", answers, re.M) == expected_headings
print("PASS: all nine question and answer headings")

with pdfplumber.open(ROOT / "Homework_3_题干翻译.pdf") as translated:
    assert len(translated.pages) == 3
    pdf_text = "".join(page.extract_text() for page in translated.pages)
    assert chr(92) not in pdf_text, "Unconverted LaTeX command in PDF"
    assert all(item in pdf_text for item in ("3874", "200812:39:45GMT", "P3-9"))
    for number, page in enumerate(translated.pages, 1):
        bad = [char for char in page.chars if char["x0"] < 44 or char["x1"] > page.width - 44
               or char["top"] < 14 or char["bottom"] > page.height - 17]
        assert not bad, f"Text outside printable margins: page {number}"
print("PASS: translated PDF has three pages, converted math, and no text beyond page margins")

rows = re.findall(r"^\| (10|100|1000) \| (300 Kbps|700 Kbps|2 Mbps) \| ([\d,.]+) \| ([\d,.]+) \|$", answers, re.M)
assert len(rows) == 9
upload_rates = {"300 Kbps": 300000, "700 Kbps": 700000, "2 Mbps": 2000000}
for n, upload, cs_text, p2p_text in rows:
    n, upload = int(n), upload_rates[upload]
    cs = max(Fraction(n * 20 * 10**9, 30 * 10**6), Fraction(20 * 10**9, 2 * 10**6))
    p2p = max(Fraction(20 * 10**9, 30 * 10**6), Fraction(20 * 10**9, 2 * 10**6),
              Fraction(n * 20 * 10**9, 30 * 10**6 + n * upload))
    assert abs(float(cs_text.replace(",", "")) - float(cs)) < 0.005
    assert abs(float(p2p_text.replace(",", "")) - float(p2p)) < 0.005
print("PASS: all 18 numerical distribution times, including rounding")

for path in (question_path, answer_path):
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if "://" not in target:
            assert (path.parent / unquote(target)).exists(), f"Broken local link: {target}"
assert (ROOT / "code" / "P3_9_实验记录.md").exists()
assert not (ROOT / "Homework_3_解答.pdf").exists(), "Answer PDF must await user approval"
print("PASS: local links and experiment record exist; answer PDF has not been created")
