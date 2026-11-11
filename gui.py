"""
Modern Tkinter Graphical User Interface for PDF STEP Extractor.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List

from core import extract_step_from_pdf
from notifier import notify_success, notify_not_found, notify_error
import registry


class StepExtractorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF STEP Çıkarıcı")
        self.root.geometry("700x560")
        self.root.minsize(620, 480)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Configure styling
        self._setup_styles()
        self._create_widgets()
        self._update_registry_status()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Color palette
        self.bg_color = "#0f172a"        # slate-900
        self.card_bg = "#1e293b"         # slate-800
        self.card_border = "#334155"     # slate-700
        self.accent_blue = "#38bdf8"     # sky-400
        self.btn_blue = "#2563eb"        # blue-600
        self.btn_blue_hover = "#1d4ed8"  # blue-700
        self.text_main = "#f8fafc"       # slate-50
        self.text_muted = "#94a3b8"      # slate-400
        self.success_color = "#22c55e"   # green-500
        self.warning_color = "#f59e0b"   # amber-500

        self.root.configure(bg=self.bg_color)

        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_bg)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_main, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_main, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=self.card_bg, foreground=self.text_muted, font=("Segoe UI", 9))

        # Button styles
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.btn_blue,
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(14, 8)
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.btn_blue_hover), ("pressed", "#1e40af")]
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 9),
            background=self.card_border,
            foreground="#ffffff",
            borderwidth=0,
            padding=(10, 6)
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#475569")]
        )

        # Treeview styling
        style.configure(
            "Treeview",
            background="#1e293b",
            foreground="#f8fafc",
            fieldbackground="#1e293b",
            font=("Segoe UI", 9),
            rowheight=26,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#0f172a",
            foreground="#94a3b8",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=6
        )
        style.map("Treeview", background=[("selected", "#3b82f6")])

    def _create_widgets(self):
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 16))

        title_lbl = ttk.Label(
            header_frame,
            text="📦 PDF STEP Model Çıkarıcı",
            font=("Segoe UI", 16, "bold"),
            foreground=self.accent_blue
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ttk.Label(
            header_frame,
            text="Teknik resim PDF'lerindeki gömülü 3D CAD (.stp) modellerini saniyeler içinde çıkarır.",
            foreground=self.text_muted,
            font=("Segoe UI", 9)
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Card 1: Context Menu Status & Toggle
        reg_card = ttk.Frame(main_container, style="Card.TFrame", padding=14)
        reg_card.pack(fill=tk.X, pady=(0, 14))

        reg_header = ttk.Frame(reg_card, style="Card.TFrame")
        reg_header.pack(fill=tk.X)

        self.reg_status_lbl = ttk.Label(
            reg_header,
            text="Sağ Tık Menüsü Durumu Kontrol Ediliyor...",
            style="Card.TLabel",
            font=("Segoe UI", 10, "bold")
        )
        self.reg_status_lbl.pack(side=tk.LEFT)

        self.reg_btn = ttk.Button(
            reg_header,
            text="...",
            style="Secondary.TButton",
            command=self._toggle_registry
        )
        self.reg_btn.pack(side=tk.RIGHT)

        reg_desc = ttk.Label(
            reg_card,
            text="Kurulduğunda, Windows Gezgini'nde birden fazla dosya (PDF, Excel vb.) seçtiğinizde dahi sağ tıklayıp 'STEP Dosyasını Çıkar' diyebilirsiniz. Excel gibi dosyalar otomatik es geçilir, yalnızca PDF'lerin içindeki STEP modelleri çıkarılır.",
            style="Muted.TLabel",
            wraplength=640
        )
        reg_desc.pack(anchor="w", pady=(6, 0))

        # Card 2: Manual Select Action
        action_card = ttk.Frame(main_container, style="Card.TFrame", padding=14)
        action_card.pack(fill=tk.X, pady=(0, 14))

        action_inner = ttk.Frame(action_card, style="Card.TFrame")
        action_inner.pack(fill=tk.X)

        action_info = ttk.Frame(action_inner, style="Card.TFrame")
        action_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        action_title = ttk.Label(
            action_info,
            text="PDF Dosyası Seçerek Çıkar",
            style="Card.TLabel",
            font=("Segoe UI", 11, "bold")
        )
        action_title.pack(anchor="w")

        action_sub = ttk.Label(
            action_info,
            text="Bilgisayarınızdan bir veya birden fazla PDF dosyası seçin.",
            style="Muted.TLabel"
        )
        action_sub.pack(anchor="w", pady=(2, 0))

        select_btn = ttk.Button(
            action_inner,
            text="📂 PDF Dosyası Seç",
            style="Primary.TButton",
            command=self._select_and_extract
        )
        select_btn.pack(side=tk.RIGHT, padx=5)

        # Card 3: Extraction History Table
        hist_frame = ttk.Frame(main_container)
        hist_frame.pack(fill=tk.BOTH, expand=True)

        hist_header = ttk.Frame(hist_frame)
        hist_header.pack(fill=tk.X, pady=(0, 6))

        hist_title = ttk.Label(
            hist_header,
            text="İşlem Geçmişi / Çıkarılan Dosyalar",
            font=("Segoe UI", 10, "bold")
        )
        hist_title.pack(side=tk.LEFT)

        open_folder_btn = ttk.Button(
            hist_header,
            text="📁 Seçili Klasörü Aç",
            style="Secondary.TButton",
            command=self._open_selected_folder
        )
        open_folder_btn.pack(side=tk.RIGHT)

        # Table
        columns = ("pdf", "step", "size", "status")
        self.tree = ttk.Treeview(hist_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("pdf", text="PDF Dosyası")
        self.tree.heading("step", text="Çıkarılan STEP Dosyası")
        self.tree.heading("size", text="Boyut")
        self.tree.heading("status", text="Durum")

        self.tree.column("pdf", width=180, anchor="w")
        self.tree.column("step", width=200, anchor="w")
        self.tree.column("size", width=80, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        scroll = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda event: self._open_selected_folder())

        # Data store for row paths
        self.history_items = {}

    def _update_registry_status(self):
        installed = registry.is_installed()
        if installed:
            self.reg_status_lbl.configure(
                text="🟢 Sağ Tık Menüsü: AKTİF (Windows Explorer Entegre Edildi)",
                foreground=self.success_color
            )
            self.reg_btn.configure(text="Sağ Tık Menüsünden Kaldır")
        else:
            self.reg_status_lbl.configure(
                text="⚪ Sağ Tık Menüsü: YÜKLÜ DEĞİL",
                foreground=self.warning_color
            )
            self.reg_btn.configure(text="➕ Sağ Tık Menüsüne Ekle")

    def _toggle_registry(self):
        installed = registry.is_installed()
        if installed:
            ok, msg = registry.uninstall()
            if ok:
                messagebox.showinfo("Başarılı", "Sağ tık menü seçeneği kaldırıldı.")
            else:
                messagebox.showerror("Hata", msg)
        else:
            ok, msg = registry.install()
            if ok:
                messagebox.showinfo(
                    "Başarılı",
                    "Sağ tık menüsüne başarıyla eklendi!\n\nArtık ister tek bir PDF'e, ister PDF ve Excel gibi karışık dosyalara sağ tıklayıp 'STEP Dosyasını Çıkar' seçeneğini kullanabilirsiniz."
                )
            else:
                messagebox.showerror("Hata", msg)
        self._update_registry_status()

    def _select_and_extract(self):
        file_paths = filedialog.askopenfilenames(
            title="Dosyaları Seçin (PDF ve diğerleri)",
            filetypes=[("PDF ve Desteklenen Dosyalar", "*.pdf;*.PDF"), ("Tüm Dosyalar", "*.*")]
        )
        if not file_paths:
            return

        for p in file_paths:
            if p.lower().endswith(".pdf"):
                self.process_pdf(p)

    def process_pdf(self, pdf_path: str):
        res = extract_step_from_pdf(pdf_path)
        pdf_name = os.path.basename(pdf_path)
        target_dir = os.path.dirname(os.path.abspath(pdf_path))

        if res["success"] and res["extracted"]:
            notify_success(res["extracted"], pdf_path, target_dir)
            for item in res["extracted"]:
                size_kb = f"{item['size'] / 1024:.1f} KB"
                row_id = self.tree.insert(
                    "",
                    0,
                    values=(pdf_name, item["filename"], size_kb, "✅ Çıkarıldı")
                )
                self.history_items[row_id] = item["path"]
        else:
            notify_not_found(pdf_path)
            row_id = self.tree.insert(
                "",
                0,
                values=(pdf_name, "-", "-", "⚠️ STEP Yok")
            )
            self.history_items[row_id] = target_dir

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Bilgi", "Lütfen tablodan bir satır seçin.")
            return

        row_id = selected[0]
        path = self.history_items.get(row_id)
        if not path:
            return

        if os.path.isfile(path):
            subprocess.run(["explorer", f"/select,{os.path.abspath(path)}"])
        elif os.path.isdir(path):
            subprocess.run(["explorer", os.path.abspath(path)])


def start_gui():
    root = tk.Tk()
    app = StepExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    start_gui()
