"""
Core STEP Extraction Engine for PDF files.
Extracts embedded 3D CAD STEP models (ISO-10303-21) from PDF files.
"""

import os
import re
import hashlib
from typing import List, Dict, Tuple, Optional
from pypdf import PdfReader


def sanitize_filename(filename: str, fallback_stem: str = "model") -> str:
    """Sanitize filename and ensure valid characters and proper extension."""
    if not filename:
        return f"{fallback_stem}.stp"

    # Remove invalid Windows filename characters: \ / : * ? " < > |
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename).strip()
    if not cleaned or cleaned.lower() in ("untitled object", "embeddedfile", "attachment", "embedded"):
        return f"{fallback_stem}.stp"

    # Ensure .stp or .step extension
    if not cleaned.lower().endswith((".stp", ".step", ".stpz", ".stepz")):
        cleaned += ".stp"

    return cleaned


def fix_turkish_encoding(text: str) -> str:
    """
    Fixes common Turkish character mis-mappings (mojibake) between CP1254 and Latin-1.
    For example, 0xDD is 'İ' in CP1254, but becomes 'Ý' or unicode escapes in Latin-1.
    """
    if not text:
        return text

    tr_latin1_map = {
        "\u00dd": "İ",
        "\u00fd": "ı",
        "\u00de": "Ş",
        "\u00fe": "ş",
        "\u00d0": "Ğ",
        "\u00f0": "ğ",
    }
    for bad, good in tr_latin1_map.items():
        text = text.replace(bad, good)

    return text


def is_step_content(data: bytes, filename: str = "") -> bool:
    """Check if byte payload is an ISO-10303-21 STEP file."""
    if not data:
        return False

    prefix = data.lstrip()[:1000]
    if prefix.startswith(b"ISO-10303-21") or b"HEADER;" in prefix and b"FILE_DESCRIPTION" in prefix:
        return True

    # Filename extension check with basic CAD verification
    if filename.lower().endswith((".stp", ".step", ".stpz", ".stepz")):
        return True

    return False


def _get_filename_from_filespec(fs: dict, default_name: str = "") -> str:
    """Extract and properly decode filename from a PDF Filespec dictionary."""
    uf = fs.get("/UF")
    f = fs.get("/F")

    # If UF has replacement character \ufffd and F is present, try decoding F with CP1254
    fname = ""
    if uf and "\ufffd" in str(uf) and f:
        try:
            fname = str(f).encode("latin1").decode("cp1254")
        except Exception:
            fname = str(uf)
    elif uf:
        fname = str(uf)
    elif f:
        try:
            fname = str(f).encode("latin1").decode("cp1254")
        except Exception:
            fname = str(f)
    else:
        fname = default_name

    return fix_turkish_encoding(fname)


def extract_step_from_pdf(pdf_path: str, output_dir: Optional[str] = None, overwrite: bool = True) -> Dict:
    """
    Extracts all STEP files found in the given PDF.
    
    Returns a dictionary:
    {
        'success': bool,
        'pdf_path': str,
        'extracted': list of dicts: [
            {'filename': '...', 'path': '...', 'size': 12345, 'status': 'extracted' | 'already_exists'}
        ],
        'message': str
    }
    """
    abs_pdf_path = os.path.abspath(pdf_path)
    if not os.path.exists(abs_pdf_path):
        return {
            "success": False,
            "pdf_path": abs_pdf_path,
            "extracted": [],
            "message": f"PDF dosyası bulunamadı: {abs_pdf_path}"
        }

    target_dir = os.path.abspath(output_dir) if output_dir else os.path.dirname(abs_pdf_path)
    os.makedirs(target_dir, exist_ok=True)
    pdf_stem = os.path.splitext(os.path.basename(abs_pdf_path))[0]

    try:
        reader = PdfReader(abs_pdf_path)
    except Exception as e:
        return {
            "success": False,
            "pdf_path": abs_pdf_path,
            "extracted": [],
            "message": f"PDF dosyası okunamadı (bozuk veya şifreli olabilir): {e}"
        }

    raw_candidates: List[Tuple[str, bytes]] = []

    # Method 1: EmbeddedFiles tree in /Root /Names
    try:
        root = reader.trailer.get("/Root", {})
        names = root.get("/Names", {})
        if names and "/EmbeddedFiles" in names:
            ef_node = names["/EmbeddedFiles"]

            def walk_ef_node(node):
                items = []
                if not node:
                    return items
                obj = node.get_object()
                if "/Names" in obj:
                    arr = obj["/Names"]
                    for i in range(0, len(arr), 2):
                        key = arr[i]
                        fs = arr[i + 1].get_object()
                        name = _get_filename_from_filespec(fs, str(key))
                        ef_dict = fs.get("/EF", {})
                        if ef_dict:
                            ef_dict_obj = ef_dict.get_object() if hasattr(ef_dict, "get_object") else ef_dict
                            stream_ref = ef_dict_obj.get("/UF") or ef_dict_obj.get("/F")
                            if stream_ref:
                                stream_obj = stream_ref.get_object()
                                data = stream_obj.get_data()
                                items.append((name, data))
                if "/Kids" in obj:
                    for kid in obj["/Kids"]:
                        items.extend(walk_ef_node(kid))
                return items

            raw_items = walk_ef_node(ef_node)
            raw_candidates.extend(raw_items)
    except Exception:
        pass

    # Method 2: Page Annotations (/FileAttachment)
    try:
        for page in reader.pages:
            if "/Annots" in page:
                for annot_ref in page["/Annots"]:
                    annot = annot_ref.get_object()
                    if annot.get("/Subtype") == "/FileAttachment":
                        fs_ref = annot.get("/FS")
                        if fs_ref:
                            fs = fs_ref.get_object()
                            name = _get_filename_from_filespec(fs, "attachment.stp")
                            ef_dict = fs.get("/EF", {})
                            if ef_dict:
                                ef_dict_obj = ef_dict.get_object() if hasattr(ef_dict, "get_object") else ef_dict
                                stream_ref = ef_dict_obj.get("/UF") or ef_dict_obj.get("/F")
                                if stream_ref:
                                    stream_obj = stream_ref.get_object()
                                    data = stream_obj.get_data()
                                    raw_candidates.append((name, data))
    except Exception:
        pass

    # Method 3: pypdf built-in attachments fallback
    if not raw_candidates:
        try:
            for att_name, data_list in reader.attachments.items():
                for data in data_list:
                    raw_candidates.append((att_name, data))
        except Exception:
            pass

    # Method 4: Scan indirect objects for ISO-10303 stream content if still empty
    if not raw_candidates:
        try:
            for obj_id in reader.xref:
                try:
                    obj = reader.get_object(obj_id)
                    if hasattr(obj, "get_data"):
                        data = obj.get_data()
                        if data and data.lstrip().startswith(b"ISO-10303-21"):
                            raw_candidates.append((f"{pdf_stem}.stp", data))
                except Exception:
                    continue
        except Exception:
            pass

    # Process, deduplicate and save candidates
    seen_hashes = set()
    extracted_files = []

    for name, data in raw_candidates:
        if not data:
            continue

        h = hashlib.md5(data).hexdigest()
        if h in seen_hashes:
            continue

        if not is_step_content(data, name):
            continue

        seen_hashes.add(h)

        final_filename = sanitize_filename(name, fallback_stem=pdf_stem)
        dest_path = os.path.join(target_dir, final_filename)

        # Collision handling if not overwriting
        if os.path.exists(dest_path) and not overwrite:
            base, ext = os.path.splitext(final_filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
                counter += 1
            final_filename = os.path.basename(dest_path)

        status = "overwritten" if os.path.exists(dest_path) else "created"
        with open(dest_path, "wb") as f_out:
            f_out.write(data)

        # Windows Mark-of-the-Web (Zone.Identifier) engellemesini otomatik kaldır
        try:
            zone_stream = dest_path + ":Zone.Identifier"
            if os.path.exists(zone_stream):
                os.remove(zone_stream)
        except Exception:
            pass

        extracted_files.append({
            "filename": final_filename,
            "path": dest_path,
            "size": len(data),
            "status": status
        })

    if extracted_files:
        count = len(extracted_files)
        file_names = ", ".join([f["filename"] for f in extracted_files])
        return {
            "success": True,
            "pdf_path": abs_pdf_path,
            "extracted": extracted_files,
            "message": f"{count} adet STEP dosyası çıkarıldı: {file_names}"
        }
    else:
        return {
            "success": False,
            "pdf_path": abs_pdf_path,
            "extracted": [],
            "message": "Bu PDF dosyasında ekli 3D CAD/STEP modeli bulunamadı."
        }
