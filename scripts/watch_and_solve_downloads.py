"""
SRM eCurricula Autonomous Watcher & Solver
Watches C:\\Users\\vanga\\Downloads for downloaded worksheets (e.g. U2S1SLO1.docx),
instantly extracts questions, solves them with AI, and generates the final PDF submission.
"""

import os
import sys
import time
import re
from pathlib import Path
import docx
from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from jarvisx.agents.ecurricula_doc_engine import ECurriculaDocEngine
from jarvisx.agents.ecurricula_solver import ECurriculaSolver
from jarvisx.automation.gdrive_uploader import GDriveHelper

load_dotenv()


def parse_and_solve_worksheet(docx_path: str):
    print(f"\n[+] Processing worksheet: {docx_path}")
    doc = docx.Document(docx_path)
    text_content = []
    for p in doc.paragraphs:
        if p.text.strip():
            text_content.append(p.text.strip())

    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join([cell.text.strip().replace("\n", " ") for cell in row.cells])
            text_content.append(row_text)

    full_text = "\n".join(text_content)
    print(f"[*] Extracted {len(text_content)} lines from worksheet.")

    # Determine Unit, Session, SLO from filename (e.g. U2S1SLO1.docx)
    filename = Path(docx_path).name
    m = re.search(r"U(\d+)S(\d+)SLO(\d+)", filename, re.IGNORECASE)
    if m:
        unit = int(m.group(1))
        session = int(m.group(2))
        slo = int(m.group(3))
    else:
        unit, session, slo = 2, 1, 1

    solver = ECurriculaSolver()
    doc_engine = ECurriculaDocEngine()
    gdrive_helper = GDriveHelper()

    # Determine content type: Crossword, Matching, or Q&A
    is_crossword = "across" in full_text.lower() or "down" in full_text.lower()
    is_matching = "match" in full_text.lower() or "column" in full_text.lower()

    if is_crossword:
        print("[*] Detected Crossword Puzzle. Solving...")
        solved = solver.solve_crossword(full_text)
        content_type = "crossword"
        data = solved
    elif is_matching:
        print("[*] Detected Matching Pairs. Solving...")
        solved = solver.solve_matching(full_text)
        content_type = "matching"
        data = solved
    else:
        print("[*] Solving general DSA questions...")
        # Fallback to general solver
        lines = [line for line in text_content if len(line) > 3]
        content_type = "raw"
        data = lines

    print("[*] Generating formatted DOCX and compiling native PDF...")
    res = doc_engine.create_assignment(
        unit=unit,
        session=session,
        slo=slo,
        content_type=content_type,
        data=data
    )

    print(f" [OK] PDF Created: {res['pdf_path']}")
    gdrive_helper.reveal_pdf_in_explorer(res['pdf_path'])
    print(" [OK] Highlighted PDF in File Explorer for Google Drive upload.")
    return res


def watch_downloads_folder():
    downloads_dir = Path(r"C:\Users\vanga\Downloads")
    print("=" * 60)
    print(f" SRM eCurricula Autonomous Watcher Active")
    print(f" Watching directory: {downloads_dir}")
    print(" Click 'DOWNLOAD DOCX' in eCurricula to automatically generate solved PDF!")
    print("=" * 60)

    seen = set(os.listdir(downloads_dir))

    while True:
        try:
            time.sleep(2)
            current = set(os.listdir(downloads_dir))
            new_files = current - seen
            for fname in new_files:
                if fname.lower().endswith(".docx") and "slo" in fname.lower():
                    time.sleep(1)  # wait for download to finish writing
                    fpath = str(downloads_dir / fname)
                    parse_and_solve_worksheet(fpath)
            seen = current
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Watcher notice:", e)


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        parse_and_solve_worksheet(sys.argv[1])
    else:
        watch_downloads_folder()
