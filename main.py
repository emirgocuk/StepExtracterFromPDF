"""
Main Entry Point for PDF STEP Extractor.
Supports both silent right-click context menu execution and standalone GUI mode.
"""

import sys
import os
from typing import List

from core import extract_step_from_pdf
from notifier import notify_success, notify_not_found, notify_error


def handle_cli_extraction(pdf_paths: List[str]):
    """Silent extraction mode when called from Windows Explorer context menu."""
    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            continue

        try:
            res = extract_step_from_pdf(pdf_path)
            target_dir = os.path.dirname(os.path.abspath(pdf_path))

            if res["success"] and res["extracted"]:
                notify_success(res["extracted"], pdf_path, target_dir)
            else:
                notify_not_found(pdf_path)
        except Exception as e:
            notify_error(pdf_path, str(e))


def main():
    # If file arguments are passed via Explorer right-click or drag-drop
    if len(sys.argv) > 1:
        file_args = sys.argv[1:]
        # Only process PDF files, silently skip non-PDF files (e.g. Excel, Word, etc.)
        valid_pdfs = [p for p in file_args if p.lower().endswith((".pdf",))]
        if valid_pdfs:
            handle_cli_extraction(valid_pdfs)
        # Always terminate silently when invoked via CLI/Context Menu
        sys.exit(0)

    # Otherwise launch interactive GUI (only when directly double-clicked)
    from gui import start_gui
    start_gui()


if __name__ == "__main__":
    main()
