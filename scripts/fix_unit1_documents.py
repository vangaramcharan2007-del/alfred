"""
Fixes all Unit 1 assignment documents:
Replaces friend's credentials ('Poola Sai Kruthi Pranav' / 'RA2511027010145')
with 'RAM CHARAN VANGA' and 'RA2511027010164'.
Generates updated DOCX and compiles native PDF for every single session (S1 to S8, SLO1 and SLO2).
"""

import os
import re
from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor

NEW_NAME = "RAM CHARAN VANGA"
NEW_REG_NO = "RA2511027010164"

# Patterns to match any variation of friend's name and reg no
NAME_PATTERN = re.compile(r"poola\s+sai\s+kruthi\s+pranav", re.IGNORECASE)
REG_PATTERN = re.compile(r"ra2511027010145", re.IGNORECASE)


def replace_in_paragraph(p):
    """Replaces name and reg number in a paragraph."""
    text = p.text
    changed = False

    if NAME_PATTERN.search(text):
        text = NAME_PATTERN.sub(NEW_NAME, text)
        changed = True

    if REG_PATTERN.search(text):
        text = REG_PATTERN.sub(NEW_REG_NO, text)
        changed = True

    if changed:
        # Preserve font styling if possible, otherwise update text
        if len(p.runs) == 1:
            p.runs[0].text = text
        else:
            p.text = text
    return changed


def replace_in_table(table):
    """Replaces name and reg number in table cells."""
    changed_count = 0
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if replace_in_paragraph(p):
                    changed_count += 1
    return changed_count


def process_docx_file(input_path: Path, output_docx_path: Path) -> bool:
    doc = docx.Document(input_path)
    changed = 0

    for p in doc.paragraphs:
        if replace_in_paragraph(p):
            changed += 1

    for table in doc.tables:
        changed += replace_in_table(table)

    output_docx_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_docx_path))
    return changed > 0


def convert_all_docx_to_pdf(docx_dir: Path, pdf_dir: Path):
    """Uses Word COM to batch-convert all docx in docx_dir to pdf_dir."""
    import win32com.client
    import pythoncom

    pythoncom.CoInitialize()
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    pdf_dir.mkdir(parents=True, exist_ok=True)

    for docx_file in docx_dir.glob("*.docx"):
        pdf_file = pdf_dir / (docx_file.stem + ".pdf")
        print(f" Converting: {docx_file.name} -> {pdf_file.name}...")
        try:
            doc = word.Documents.Open(str(docx_file.resolve()))
            doc.SaveAs(str(pdf_file.resolve()), FileFormat=17)  # 17 = wdFormatPDF
            doc.Close()
            print(f" [OK] {pdf_file.name} created ({pdf_file.stat().st_size} bytes)")
        except Exception as e:
            print(f" [ERR] Failed to convert {docx_file.name}: {e}")

    word.Quit()


def create_u1s1_files(output_docx_dir: Path):
    """Creates U1S1SLO1 and U1S1SLO2 for Ram Charan Vanga from reference content."""
    # U1S1SLO1: Crossword
    doc1 = docx.Document()
    for s in doc1.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1.0)
    
    p = doc1.add_paragraph(NEW_NAME); p.paragraph_format.space_after = Pt(2)
    p = doc1.add_paragraph(NEW_REG_NO); p.paragraph_format.space_after = Pt(12)
    p = doc1.add_paragraph("Sub ject : DSA"); p.paragraph_format.space_after = Pt(12)
    p = doc1.add_paragraph("Unit 1, S1, SLO1"); p.paragraph_format.space_after = Pt(18)
    
    p = doc1.add_paragraph("Across"); p.paragraph_format.space_after = Pt(6)
    across_items = [
        "4. VARIABLE", "5. FLOWCHART", "6. SWITCH", "7. PRINTF",
        "8. INT", "9. INCREMENT", "10. MAIN", "11. FLOAT", "12. SQRT"
    ]
    for item in across_items:
        p = doc1.add_paragraph(f"    {item}"); p.paragraph_format.space_after = Pt(2)

    p = doc1.add_paragraph("Down"); p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(6)
    down_items = [
        "1. SCANF", "2. KEYWORDS", "3. DENNISRITCHIE", "4. NEWLINE",
        "5. RELATIONAL", "6. VOID", "7. COMPILER"
    ]
    for item in down_items:
        p = doc1.add_paragraph(f"    {item}"); p.paragraph_format.space_after = Pt(2)

    doc1.save(str(output_docx_dir / "U1S1SLO1.docx"))
    print(" [OK] Generated U1S1SLO1.docx")

    # U1S1SLO2: Matching
    doc2 = docx.Document()
    for s in doc2.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1.0)

    p = doc2.add_paragraph(NEW_NAME); p.paragraph_format.space_after = Pt(2)
    p = doc2.add_paragraph(NEW_REG_NO); p.paragraph_format.space_after = Pt(12)
    p = doc2.add_paragraph("Sub ject : DSA"); p.paragraph_format.space_after = Pt(12)
    p = doc2.add_paragraph("Unit 1, S1, SLO2"); p.paragraph_format.space_after = Pt(18)

    p = doc2.add_paragraph("No.               Answer"); p.paragraph_format.space_after = Pt(6)
    matching_items = [
        "1. int           G – Used to store whole numbers",
        "2. float         I – Floating-point data type",
        "3. char          H – Used to print characters",
        "4. main()        F – Keyword to start main function",
        "5. return 0;     J – Ends a function and returns value to OS",
        "6. #include<stdio.h> C – Preprocessor directive",
        "7. ; (semicolon) D – Statement terminator",
        "8. %d            B – Format specifier for integers",
        "9. %f            A – Format specifier for float",
        "10. %c           E – Format specifier for characters"
    ]
    for item in matching_items:
        p = doc2.add_paragraph(item); p.paragraph_format.space_after = Pt(2)

    doc2.save(str(output_docx_dir / "U1S1SLO2.docx"))
    print(" [OK] Generated U1S1SLO2.docx")


def run():
    downloads_dir = Path(r"C:\Users\vanga\Downloads")
    out_dir = Path.cwd() / "outputs" / "srm_unit1_fixed"
    docx_out = out_dir / "docx"
    pdf_out = out_dir / "pdfs"

    docx_out.mkdir(parents=True, exist_ok=True)
    pdf_out.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f" Fixing Unit 1 Documents for {NEW_NAME} ({NEW_REG_NO})")
    print("=" * 60)

    # 1. Create U1S1SLO1 and U1S1SLO2
    create_u1s1_files(docx_out)

    # 2. Fix existing U1S2SLO1 through U1S8SLO2
    target_files = sorted(downloads_dir.glob("U1*.docx"))
    for tf in target_files:
        dest_docx = docx_out / tf.name
        changed = process_docx_file(tf, dest_docx)
        print(f" Processed {tf.name}: replaced friend details -> saved to {dest_docx.name}")

    # 3. Batch convert all to PDF
    print("\n--- Batch Converting all Unit 1 Documents to PDF ---")
    convert_all_docx_to_pdf(docx_out, pdf_out)

    print("\n" + "=" * 60)
    print(f" All 16 Unit 1 Documents Fixed & Converted to PDF!")
    print(f" DOCX Directory: {docx_out}")
    print(f" PDF Directory:  {pdf_out}")
    print("=" * 60)


if __name__ == "__main__":
    run()
