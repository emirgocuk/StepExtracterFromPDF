"""
Windows 10 Native Notification System for STEP Extractor.
"""

import os
import sys
import subprocess
from typing import List, Dict, Optional

try:
    from winotify import Notification, audio
    HAS_WINOTIFY = True
except ImportError:
    HAS_WINOTIFY = False


def _get_icon_path() -> str:
    """Get absolute path to app icon if it exists."""
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    icon_candidate = os.path.join(base_dir, "app_icon.ico")
    if os.path.exists(icon_candidate):
        return icon_candidate
    return ""


def notify_success(extracted_files: List[Dict], pdf_path: str, target_dir: str):
    """Notify user of successful STEP extraction."""
    if not extracted_files:
        return

    count = len(extracted_files)
    file_names = ", ".join([f["filename"] for f in extracted_files])
    first_file = extracted_files[0]["path"]

    title = f"✅ STEP Dosyası Çıkarıldı ({count} Adet)" if count > 1 else "✅ STEP Dosyası Çıkarıldı"
    msg = f"{file_names}\nKonum: {target_dir}"

    if HAS_WINOTIFY:
        try:
            toast = Notification(
                app_id="PDF STEP Çıkarıcı",
                title=title,
                msg=msg,
                duration="short",
                icon=_get_icon_path()
            )
            toast.set_audio(audio.Default, loop=False)
            toast.launch = target_dir
            toast.add_actions(label="📁 Klasörü Aç", launch=target_dir)
            toast.show()
            return
        except Exception:
            pass


def notify_not_found(pdf_path: str):
    """Notify user that no STEP file was found in the PDF."""
    pdf_name = os.path.basename(pdf_path)
    title = "⚠️ STEP Modeli Bulunamadı"
    msg = f"'{pdf_name}' içerisinde gömülü 3D STEP modeli tespit edilemedi."

    if HAS_WINOTIFY:
        try:
            toast = Notification(
                app_id="PDF STEP Çıkarıcı",
                title=title,
                msg=msg,
                duration="short",
                icon=_get_icon_path()
            )
            toast.set_audio(audio.Reminder, loop=False)
            toast.show()
            return
        except Exception:
            pass


def notify_error(pdf_path: str, error_msg: str):
    """Notify user of an error during extraction."""
    pdf_name = os.path.basename(pdf_path)
    title = "❌ Çıkarma Hatası"
    msg = f"'{pdf_name}' işlenirken hata oluştu:\n{error_msg}"

    if HAS_WINOTIFY:
        try:
            toast = Notification(
                app_id="PDF STEP Çıkarıcı",
                title=title,
                msg=msg,
                duration="short",
                icon=_get_icon_path()
            )
            toast.show()
            return
        except Exception:
            pass
