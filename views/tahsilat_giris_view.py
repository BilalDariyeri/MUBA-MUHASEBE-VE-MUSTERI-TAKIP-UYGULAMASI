"""
Tahsilat Girisi Ekrani (tkinter) - MUBA temasi
Kompakt tasarim, kucuk fontlar
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json
import uuid
from sql_init import get_db


class TahsilatGirisView:
    """Tahsilat girisi ekrani"""

    def __init__(self, parent=None):
        self.parent = parent
        self.root = tk.Tk()
        self.root.title("MUBA - Tahsilat Girisi Ekrani")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        self.colors = self._init_colors()
        self.root.configure(bg=self.colors["light"])

        self.odeme_turu = tk.StringVar(value="Nakit")
        self.cari_dict = {}

        self.init_ui()

    def _init_colors(self):
        return {
            "primary": "#233568",
            "primary_dark": "#0f112b",
            "accent": "#f48c06",
            "success": "#16a34a",
            "danger": "#ef4444",
            "white": "#ffffff",
            "dark": "#1e2a4c",
            "light": "#e7e3ff",
            "border": "#d0d4f2",
            "muted": "#666a87",
        }

    def _tint(self, hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _style_button(self, btn, bg, fg="#ffffff"):
        btn.configure(
            bg=bg,
            fg=fg,
            activebackground=self._tint(bg, 1.05),
            activeforeground=fg,
            relief=tk.FLAT,
            padx=12,
            pady=7,
            font=("Arial", 11, "bold"),
            cursor="hand2",
        )

    def init_ui(self):
        # Ana container
        main_container = tk.Frame(self.root, bg=self.colors["light"])
        main_container.pack(fill=tk.BOTH, expand=True)

        # Ust baslik
        header = tk.Frame(main_container, bg=self.colors["primary"], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text="Tahsilat Girisi",
            bg=self.colors["primary"],
            fg="white",
            font=("Arial", 16, "bold"),
            pady=12,
        ).pack()

        # Icerik
        content_frame = tk.Frame(main_container, bg=self.colors["light"], padx=16, pady=16)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        # Sol kolon - temel bilgiler
        left_panel = tk.LabelFrame(
            content_frame,
            text="TEMEL BILGILER",
            bg="white",
            fg=self.colors["dark"],
            font=("Arial", 11, "bold"),
            padx=14,
            pady=14,
            relief=tk.SOLID,
            bd=1,
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        left_panel.columnconfigure(1, weight=1)

        tk.Label(left_panel, text="Cari Hesap:", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=8, padx=8
        )
        self.cari_combo = ttk.Combobox(left_panel, width=34, state="readonly", font=("Arial", 10))
        self.cari_combo["values"] = self.load_cari_hesaplar()
        self.cari_combo.bind("<<ComboboxSelected>>", self.on_cari_selected)
        self.cari_combo.grid(row=0, column=1, sticky="ew", pady=8, padx=8)

        tk.Label(left_panel, text="Islem Tarihi:", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=8, padx=8
        )
        self.tarih_entry = DateEntry(
            left_panel,
            width=30,
            background=self.colors["primary"],
            foreground="white",
            borderwidth=2,
            date_pattern="dd.mm.yyyy",
            locale="tr_TR",
            font=("Arial", 10, "bold"),
        )
        self.tarih_entry.grid(row=1, column=1, sticky="w", pady=8, padx=8)

        tk.Label(left_panel, text="Tutar (TL):", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=8, padx=8
        )
        self.tutar_entry = tk.Entry(
            left_panel,
            width=34,
            font=("Arial", 11, "bold"),
            bg="white",
            fg=self.colors["primary"],
            relief=tk.SOLID,
            bd=2,
        )
        self.tutar_entry.grid(row=2, column=1, sticky="ew", pady=8, padx=8)
        vcmd = (self.root.register(self.validate_number), "%P")
        self.tutar_entry.config(validate="key", validatecommand=vcmd)

        tk.Label(left_panel, text="Odeme Turu:", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky="w", pady=8, padx=8
        )
        radio_frame = tk.Frame(left_panel, bg="white")
        radio_frame.grid(row=3, column=1, sticky="w", pady=8, padx=8)
        for text, value in [("Nakit", "Nakit"), ("Cek", "Cek"), ("Senet", "Senet")]:
            tk.Radiobutton(
                radio_frame,
                text=text.upper(),
                variable=self.odeme_turu,
                value=value,
                bg="white",
                fg=self.colors["dark"],
                font=("Arial", 11, "bold"),
                cursor="hand2",
                command=self.on_odeme_turu_changed,
                activebackground="white",
                activeforeground=self.colors["primary"],
                padx=10,
                pady=4,
            ).pack(side=tk.LEFT, padx=6)

        # Sag kolon - detaylar
        right_panel = tk.LabelFrame(
            content_frame,
            text="DETAYLAR",
            bg="white",
            fg=self.colors["dark"],
            font=("Arial", 11, "bold"),
            padx=14,
            pady=14,
            relief=tk.SOLID,
            bd=1,
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 12))
        right_panel.columnconfigure(1, weight=1)

        tk.Label(right_panel, text="Kasa Secimi:", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=8, padx=8
        )
        self.kasa_combo = ttk.Combobox(right_panel, width=30, state="readonly", font=("Arial", 10))
        self.kasa_combo.grid(row=0, column=1, sticky="ew", pady=8, padx=8)

        tk.Label(right_panel, text="Aciklama:", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="nw", pady=8, padx=8
        )
        self.aciklama_entry = tk.Text(right_panel, height=3, font=("Arial", 10), bg="white", fg=self.colors["dark"])
        self.aciklama_entry.grid(row=1, column=1, sticky="ew", pady=8, padx=8)

        tk.Label(right_panel, text="Vade Tarihi:", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=8, padx=8
        )
        self.vade_entry = DateEntry(
            right_panel,
            width=28,
            background=self.colors["danger"],
            foreground="white",
            borderwidth=2,
            date_pattern="dd.mm.yyyy",
            locale="tr_TR",
            font=("Arial", 10, "bold"),
        )
        self.vade_entry.grid(row=2, column=1, sticky="w", pady=8, padx=8)

        tk.Label(
            right_panel, text="Belge Numarasi:", bg="white", fg=self.colors["dark"], font=("Arial", 10, "bold")
        ).grid(row=3, column=0, sticky="w", pady=8, padx=8)
        self.belge_no_entry = tk.Entry(right_panel, width=30, font=("Arial", 10), bg="white", fg=self.colors["dark"])
        self.belge_no_entry.grid(row=3, column=1, sticky="ew", pady=8, padx=8)

        self.vadesi_g_metin = tk.Label(
            right_panel, text="VADESI GECMIS BORCLAR", bg="white", fg=self.colors["danger"], font=("Arial", 11, "bold")
        )
        self.vadesi_g_metin.grid(row=4, column=0, columnspan=2, sticky="w", pady=(14, 6), padx=8)
        self.borclar_text = tk.Text(
            right_panel, height=5, bg="white", fg=self.colors["dark"], wrap=tk.WORD, font=("Arial", 10)
        )
        self.borclar_text.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 10))
        right_panel.rowconfigure(5, weight=1)

        # Alt butonlar
        button_frame = tk.Frame(main_container, bg=self.colors["light"], pady=12)
        button_frame.pack(fill=tk.X)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.btn_cancel = tk.Button(button_frame, text="Iptal", command=self.on_cancel)
        self._style_button(self.btn_cancel, self.colors["danger"])
        self.btn_cancel.grid(row=0, column=0, sticky="e", padx=10)

        self.btn_save = tk.Button(button_frame, text="Kaydet", command=self.on_save)
        self._style_button(self.btn_save, self.colors["success"])
        self.btn_save.grid(row=0, column=1, sticky="w", padx=10)

    # -------------------
    # Islevesel metotlar
    # -------------------
    def validate_number(self, value):
        if value == "" or value == ".":
            return True
        try:
            float(value.replace(",", "."))
            return True
        except ValueError:
            return False

    def load_cari_hesaplar(self):
        """DB'den cari hesap listesi cek (mock: bos)"""
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, unvani FROM cari_hesap")
            rows = cursor.fetchall()
            self.cari_dict = {r[1]: r[0] for r in rows}
            return list(self.cari_dict.keys())
        except Exception:
            return []

    def on_cari_selected(self, event=None):
        pass

    def on_odeme_turu_changed(self):
        pass

    def on_save(self):
        """Kaydet butonu"""
        if not self.cari_combo.get():
            messagebox.showwarning("Uyari", "Cari hesap seciniz.")
            return
        if not self.tutar_entry.get().strip():
            messagebox.showwarning("Uyari", "Tutar giriniz.")
            return
        try:
            tutar = float(self.tutar_entry.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Uyari", "Gecerli bir tutar giriniz.")
            return

        data = {
            "id": str(uuid.uuid4()),
            "cari": self.cari_combo.get(),
            "cari_id": self.cari_dict.get(self.cari_combo.get()),
            "tarih": self.tarih_entry.get_date().strftime("%Y-%m-%d"),
            "vade": self.vade_entry.get_date().strftime("%Y-%m-%d"),
            "tutar": tutar,
            "odeme_turu": self.odeme_turu.get(),
            "belge_no": self.belge_no_entry.get().strip(),
            "aciklama": self.aciklama_entry.get("1.0", tk.END).strip(),
        }
        messagebox.showinfo("Bilgi", f"Tahsilat kaydedildi:\n{json.dumps(data, indent=2, ensure_ascii=False)}")

    def on_cancel(self):
        if messagebox.askyesno("Onay", "Islemi iptal etmek istiyor musunuz?"):
            self.root.destroy()

    def run(self):
        """PyQt controller'dan cagildiginda tkinter dongusunu baslat"""
        self.root.mainloop()


if __name__ == "__main__":
    app = TahsilatGirisView()
    app.run()
