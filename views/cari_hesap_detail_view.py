"""
Cari Hesap Detail View - Şirket detay görünümü (MUBA teması)
Şirket bilgileri ve ilgili faturaların listesi
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QFormLayout, QPushButton, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CariHesapDetailView(QDialog):
    """Cari hesap detay görünümü - View katmanı"""

    def __init__(self, cari_data, parent=None):
        super().__init__(parent)
        self.cari_data = cari_data or {}
        self._init_colors()
        self.setWindowTitle(f"Şirket Detayları - {self.cari_data.get('unvani', 'Bilinmeyen')}")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.init_ui()

    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"

    def _tint(self, hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.color_bg};
            }}
            QGroupBox {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 4px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 6px;
                color: {self.color_primary_dark};
                font-weight: 700;
            }}
            QTableWidget {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                alternate-background-color: #f5f6fb;
            }}
            QHeaderView::section {{
                background: #f3f4ff;
                padding: 6px;
                border: 1px solid {self.color_border};
                font-weight: 600;
                color: {self.color_text};
                font-size: 12px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel(f"Şirket Bilgileri: {self.cari_data.get('unvani', '-')}")
        title.setFont(QFont("", 18, QFont.Bold))
        title.setStyleSheet(f"color: {self.color_primary_dark};")
        layout.addWidget(title)

        tabs = QTabWidget()

        # Bilgiler tab
        bilgiler_tab = QWidget()
        bilgiler_layout = QVBoxLayout()
        bilgi_group = QGroupBox("Şirket Bilgileri")
        bilgi_form = QFormLayout()

        bilgi_form.addRow("Şirket Adı:", QLabel(self.cari_data.get('unvani', '-')))
        bilgi_form.addRow("Vergi Numarası:", QLabel(self._mask_vergi_no()))
        bilgi_form.addRow("Telefon:", QLabel(self.cari_data.get('telefon', '-')))
        bilgi_form.addRow("E-Posta:", QLabel(self.cari_data.get('email', '-')))

        iletisim = self.cari_data.get('iletisim', {}) or {}
        if isinstance(iletisim, str):
            import json
            try:
                iletisim = json.loads(iletisim)
            except Exception:
                iletisim = {}

        bilgi_form.addRow("Şehir:", QLabel(iletisim.get('il', '-')))
        bilgi_form.addRow("Ülke:", QLabel(iletisim.get('ulke', 'Türkiye')))
        bilgi_form.addRow("Adres:", QLabel(self.cari_data.get('adres', '-')))
        bilgi_form.addRow("Durum:", QLabel(self.cari_data.get('statusu', '-')))

        bilgi_group.setLayout(bilgi_form)
        bilgiler_layout.addWidget(bilgi_group)
        bilgiler_layout.addStretch()
        bilgiler_tab.setLayout(bilgiler_layout)
        tabs.addTab(bilgiler_tab, "Bilgiler")

        # Faturalar tab
        faturalar_tab = QWidget()
        faturalar_layout = QVBoxLayout()

        self.fatura_table = QTableWidget()
        self.fatura_table.setColumnCount(5)
        self.fatura_table.setHorizontalHeaderLabels([
            "Fatura No", "Tarih", "Tür", "Toplam", "Durum"
        ])
        self.fatura_table.horizontalHeader().setStretchLastSection(True)
        self.fatura_table.setAlternatingRowColors(True)
        faturalar_layout.addWidget(self.fatura_table)

        faturalar_tab.setLayout(faturalar_layout)
        tabs.addTab(faturalar_tab, "Faturalar")

        # Alt toolbar
        toolbar = QHBoxLayout()
        self.btn_kapat = QPushButton("Kapat")
        self._style_btn(self.btn_kapat, self.color_primary_dark)
        self.btn_kapat.clicked.connect(self.close)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_kapat)

        layout.addWidget(tabs)
        layout.addLayout(toolbar)
        self.setLayout(layout)

        # Veri doldur
        self.load_faturalar(self.cari_data.get('faturalar', []))

    def _style_btn(self, btn, bg, fg="#ffffff"):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: none;
                padding: 9px 14px;
                font-weight: 700;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background: {self._tint(bg, 1.07)}; }}
            QPushButton:pressed {{ background: {self._tint(bg, 0.9)}; }}
        """)

    def _mask_vergi_no(self):
        vergi_no = self.cari_data.get('vergiNo', '-') or '-'
        if len(vergi_no) > 4:
            return f"{'*' * (len(vergi_no) - 4)}{vergi_no[-4:]}"
        return vergi_no

    def load_faturalar(self, faturalar):
        faturalar = faturalar or []
        self.fatura_table.setRowCount(len(faturalar))
        for i, f in enumerate(faturalar):
            self.fatura_table.setItem(i, 0, QTableWidgetItem(str(f.get('faturaNo', '-'))))
            self.fatura_table.setItem(i, 1, QTableWidgetItem(str(f.get('tarih', '-'))))
            self.fatura_table.setItem(i, 2, QTableWidgetItem(str(f.get('tur', '-'))))
            toplam = float(f.get('toplam', 0) or 0)
            self.fatura_table.setItem(i, 3, QTableWidgetItem(f"{toplam:.2f} TL"))
            self.fatura_table.setItem(i, 4, QTableWidgetItem(str(f.get('durum', '-'))))

    # Callback bağlayıcı (geri dönüş için)
    def set_close_callback(self, callback):
        self.btn_kapat.clicked.connect(callback)
