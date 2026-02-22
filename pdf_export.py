from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from datetime import datetime
from pathlib import Path

def _wrap(c, text, x, y, w, leading=14):
    lines = []
    for para in (text or "").split("\n"):
        if not para.strip():
            lines.append("")
            continue
        lines += simpleSplit(para, c._fontname, c._fontsize, w)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
        if y < 20*mm:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = 280*mm
    return y

def export_readiness_map(pdf_path:str, family_name:str, notes:str, sections:list):
    # sections: list of (title, body)
    Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setTitle("Ownership Readiness Map")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, 285*mm, "Ownership Readiness Map (Draft)")
    c.setFont("Helvetica", 11)
    c.drawString(20*mm, 278*mm, f"Rodina: {family_name}")
    c.drawString(20*mm, 272*mm, f"Vygenerováno: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y = 262*mm
    c.setFont("Helvetica", 11)
    y = _wrap(c, "Interní facilitátorské poznámky:\n" + (notes or ""), 20*mm, y, 170*mm)
    y -= 8
    for title, body in sections:
        c.setFont("Helvetica-Bold", 13)
        y = _wrap(c, title, 20*mm, y, 170*mm, leading=16)
        c.setFont("Helvetica", 11)
        y = _wrap(c, body, 20*mm, y, 170*mm)
        y -= 10
    c.save()
