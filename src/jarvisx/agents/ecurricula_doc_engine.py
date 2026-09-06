"""
ECURRICULA DOCUMENT & PDF ENGINE
Generates Word (.docx) and PDF files for SRM eCurricula assignments
matching the exact formatting reference of student Vanga Ram Charan (RA2511027010164).
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

DEFAULT_STUDENT_NAME = "VANGA RAM CHARAN"
DEFAULT_REG_NO = "RA2511027010164"
DEFAULT_SUBJECT = "Sub ject : DSA"


class ECurriculaDocEngine:
    """Generates standardized docx and pdf submissions for SRM eCurricula."""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        student_name: str = DEFAULT_STUDENT_NAME,
        reg_no: str = DEFAULT_REG_NO,
        subject: str = DEFAULT_SUBJECT
    ):
        self.student_name = student_name
        self.reg_no = reg_no
        self.subject = subject

        base_dir = Path(output_dir) if output_dir else Path.cwd() / "outputs" / "srm_unit2"
        self.docx_dir = base_dir / "docx"
        self.pdf_dir = base_dir / "pdfs"
        self.docx_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

    def create_assignment(
        self,
        unit: int = 2,
        session: int = 1,
        slo: int = 1,
        content_type: str = "crossword",
        data: Any = None,
        filename_prefix: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Creates both .docx and .pdf files.
        content_type options: 'crossword', 'matching', 'qa', 'raw'
        """
        doc = docx.Document()

        # Set 1 inch standard margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # Style standard body text
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        font.color.rgb = RGBColor(0, 0, 0)

        # 1. Add Student Header (matching reference layout)
        p_name = doc.add_paragraph(self.student_name)
        p_name.paragraph_format.space_before = Pt(0)
        p_name.paragraph_format.space_after = Pt(4)

        p_reg = doc.add_paragraph(self.reg_no)
        p_reg.paragraph_format.space_before = Pt(0)
        p_reg.paragraph_format.space_after = Pt(12)

        p_subj = doc.add_paragraph(self.subject)
        p_subj.paragraph_format.space_before = Pt(0)
        p_subj.paragraph_format.space_after = Pt(12)

        unit_str = f"Unit {unit}, S{session}, SLO{slo}"
        p_unit = doc.add_paragraph(unit_str)
        p_unit.paragraph_format.space_before = Pt(0)
        p_unit.paragraph_format.space_after = Pt(20)

        # 2. Render content based on content_type
        if content_type == "crossword":
            self._render_crossword(doc, data)
        elif content_type == "matching":
            self._render_matching(doc, data)
        elif content_type == "qa":
            self._render_qa(doc, data)
        else:
            self._render_raw(doc, data)

        # 3. Save DOCX
        tag = filename_prefix or f"U{unit}S{session}SLO{slo}"
        docx_filename = f"{tag}_{self.reg_no}.docx"
        pdf_filename = f"{tag}_{self.reg_no}.pdf"

        docx_path = str(self.docx_dir / docx_filename)
        pdf_path = str(self.pdf_dir / pdf_filename)

        doc.save(docx_path)

        # 4. Convert to PDF
        self._convert_to_pdf(docx_path, pdf_path, unit_str, content_type, data)

        return {
            "docx_path": docx_path,
            "pdf_path": pdf_path,
            "tag": tag,
            "student": self.student_name,
            "reg_no": self.reg_no,
            "header": unit_str
        }

    def _render_crossword(self, doc: docx.Document, data: Dict[str, List[str]]):
        """
        Renders Across and Down crossword answers.
        data format: {'across': ['4. VARIABLE', '5. FLOWCHART'], 'down': ['1. SCANF']}
        """
        data = data or {}
        across_list = data.get('across', [])
        down_list = data.get('down', [])

        if across_list:
            p_across = doc.add_paragraph("Across")
            p_across.paragraph_format.space_before = Pt(8)
            p_across.paragraph_format.space_after = Pt(8)

            for item in across_list:
                p = doc.add_paragraph(f"    {item}")
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(3)

        if down_list:
            p_down = doc.add_paragraph("Down")
            p_down.paragraph_format.space_before = Pt(14)
            p_down.paragraph_format.space_after = Pt(8)

            for item in down_list:
                p = doc.add_paragraph(f"    {item}")
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(3)

    def _render_matching(self, doc: docx.Document, data: List[Any]):
        """
        Renders matching pairs format:
        No.    Answer
        1. int G - Used to store whole numbers
        """
        p_title = doc.add_paragraph("No.               Answer")
        p_title.paragraph_format.space_before = Pt(8)
        p_title.paragraph_format.space_after = Pt(8)

        data = data or []
        for item in data:
            if isinstance(item, str):
                line = item
            elif isinstance(item, dict):
                line = f"{item.get('no', '')}. {item.get('left', '')}   {item.get('code', '')} \u2013 {item.get('text', '')}"
            else:
                line = str(item)
            p = doc.add_paragraph(line)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)

    def _render_qa(self, doc: docx.Document, data: List[Dict[str, str]]):
        """Renders Question and Answer format."""
        data = data or []
        for idx, item in enumerate(data, 1):
            q = item.get("question", "")
            a = item.get("answer", "")

            p_q = doc.add_paragraph()
            run_q = p_q.add_run(f"Q{idx}. {q}")
            run_q.bold = True
            p_q.paragraph_format.space_before = Pt(10)
            p_q.paragraph_format.space_after = Pt(4)

            p_a = doc.add_paragraph(a)
            p_a.paragraph_format.space_before = Pt(0)
            p_a.paragraph_format.space_after = Pt(10)

    def _render_raw(self, doc: docx.Document, data: Any):
        """Renders raw text lines."""
        if isinstance(data, list):
            for line in data:
                p = doc.add_paragraph(str(line))
                p.paragraph_format.space_after = Pt(3)
        elif isinstance(data, str):
            for line in data.splitlines():
                p = doc.add_paragraph(line)
                p.paragraph_format.space_after = Pt(3)

    def _convert_to_pdf(self, docx_path: str, pdf_path: str, unit_str: str, content_type: str, data: Any):
        """Converts DOCX to PDF using Word COM if available, or ReportLab fallback."""
        try:
            import win32com.client
            import pythoncom
            pythoncom.CoInitialize()
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            abs_docx = str(Path(docx_path).resolve())
            abs_pdf = str(Path(pdf_path).resolve())
            doc = word.Documents.Open(abs_docx)
            doc.SaveAs(abs_pdf, FileFormat=17)  # 17 = wdFormatPDF
            doc.Close()
            word.Quit()
            return
        except Exception:
            # Fallback to reportlab
            self._generate_pdf_reportlab(pdf_path, unit_str, content_type, data)

    def _generate_pdf_reportlab(self, pdf_path: str, unit_str: str, content_type: str, data: Any):
        """ReportLab fallback to ensure PDF is always generated accurately."""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        y = height - 72  # 1 inch margin
        c.setFont("Helvetica", 11)

        c.drawString(72, y, self.student_name); y -= 16
        c.drawString(72, y, self.reg_no); y -= 24
        c.drawString(72, y, self.subject); y -= 24
        c.drawString(72, y, unit_str); y -= 36

        if content_type == "crossword" and isinstance(data, dict):
            if data.get('across'):
                c.drawString(72, y, "Across"); y -= 18
                for line in data.get('across', []):
                    c.drawString(96, y, line); y -= 15
            if data.get('down'):
                y -= 10
                c.drawString(72, y, "Down"); y -= 18
                for line in data.get('down', []):
                    c.drawString(96, y, line); y -= 15

        elif content_type == "matching" and isinstance(data, list):
            c.drawString(72, y, "No.               Answer"); y -= 18
            for item in data:
                line = item if isinstance(item, str) else f"{item.get('no')}. {item.get('left')} {item.get('code')} \u2013 {item.get('text')}"
                c.drawString(72, y, line); y -= 16

        elif isinstance(data, list):
            for line in data:
                c.drawString(72, y, str(line)[:90]); y -= 16

        c.save()
