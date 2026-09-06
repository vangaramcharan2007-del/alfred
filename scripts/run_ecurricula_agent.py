"""
SRM eCurricula Unit 2 Autonomous Agent Runner
Supports generating assignments (DOCX -> PDF), solving MCQs, and facilitating Google Drive link submissions.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from jarvisx.agents.ecurricula_doc_engine import ECurriculaDocEngine
from jarvisx.agents.ecurricula_solver import ECurriculaSolver
from jarvisx.automation.gdrive_uploader import GDriveHelper


def run_unit2_pipeline(
    unit: int = 2,
    session: int = 1,
    slo: int = 1,
    content_type: str = "crossword",
    data: dict = None,
    open_drive: bool = False
):
    print("=" * 60)
    print(" SRM eCurricula Unit 2 Agent Pipeline")
    print(" Student: VANGA RAM CHARAN (RA2511027010164)")
    print(f" Target: Unit {unit}, Session {session}, SLO {slo}")
    print("=" * 60)

    doc_engine = ECurriculaDocEngine()
    gdrive_helper = GDriveHelper()

    print("\n[1/3] Generating DOCX & compiling native PDF...")
    res = doc_engine.create_assignment(
        unit=unit,
        session=session,
        slo=slo,
        content_type=content_type,
        data=data
    )

    print(f" [+] DOCX Created: {res['docx_path']}")
    print(f" [+] PDF Created:  {res['pdf_path']}")

    if os.path.exists(res['pdf_path']):
        size = os.path.getsize(res['pdf_path'])
        print(f" [OK] PDF verified: {size} bytes")

    print("\n[2/3] Preparing Google Drive upload...")
    if open_drive:
        gdrive_helper.open_drive_in_browser()
        print(" [OK] Opened Google Drive in browser.")

    gdrive_helper.reveal_pdf_in_explorer(res['pdf_path'])
    print(" [OK] PDF selected in File Explorer for drag & drop.")

    print("\n[3/3] Submission Ready!")
    print(f" Tag: {res['tag']}")
    print(f" Header: {res['header']}")
    print("-" * 60)
    return res


if __name__ == "__main__":
    # Demo execution for U2 S1 SLO1
    demo_crossword = {
        "across": [
            "4. ARRAY",
            "5. LINKEDLIST",
            "7. POINTER",
            "8. TRAVERSAL"
        ],
        "down": [
            "1. STACK",
            "2. QUEUE",
            "3. NODE",
            "6. HEAD"
        ]
    }
    run_unit2_pipeline(unit=2, session=1, slo=1, content_type="crossword", data=demo_crossword, open_drive=False)
