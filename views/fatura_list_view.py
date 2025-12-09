"""
Fatura List View - MUBA teması
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QMessageBox,
    QLineEdit, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QPixmap


class FaturaListView(QWidget):
    """Satış Faturaları listesi - View katmanı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.fatura_list = []
        self.filtered_list = []
        self._load_brand_fonts()
        self._init_colors()
        self.init_ui()
        
    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary_soft = "#dfe3ff"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"
        self.color_success = "#10b981"
        self.color_warning = "#f59e0b"
    
    def _load_brand_fonts(self):
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "fonts")
        if not os.path.isdir(fonts_dir):
            return
        for file in os.listdir(fonts_dir):
            if file.lower().endswith((".otf", ".ttf")):
                try:
                    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, file))
                except Exception:
                    pass
    
    def _brand_font(self, size=13, weight=QFont.Normal, bold=False):
        font = QFont("SF Pro Display", pointSize=size, weight=weight)
        font.setBold(bold)
        return font
        
    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"background: {self.color_bg};")
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Üst bar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.btn_geri = QPushButton("Geri")
        self.btn_geri.setMinimumHeight(36)
        self.btn_geri.setCursor(Qt.PointingHandCursor)
        self.btn_geri.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_primary_dark};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0c0e23; }}
        """)
        toolbar.addWidget(self.btn_geri)
        
        title = QLabel("Satış Faturaları")
        title.setFont(self._brand_font(size=18, bold=True))
        title.setStyleSheet(f"color: {self.color_text};")
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        self.btn_export_pdf = QPushButton("PDF")
        self._style_secondary_button(self.btn_export_pdf, "#e11d48")
        toolbar.addWidget(self.btn_export_pdf)
        
        self.btn_export_excel = QPushButton("Excel")
        self._style_secondary_button(self.btn_export_excel, "#059669")
        toolbar.addWidget(self.btn_export_excel)
        
        self.btn_export_csv = QPushButton("CSV")
        self._style_secondary_button(self.btn_export_csv, "#0ea5e9")
        toolbar.addWidget(self.btn_export_csv)
        
        self.btn_gonder = QPushButton("Fatura Gönder")
        self._style_primary_button(self.btn_gonder, self.color_accent, dark_text=True)
        toolbar.addWidget(self.btn_gonder)
        
        self.btn_yeni = QPushButton("Yeni Fatura")
        self._style_primary_button(self.btn_yeni, self.color_primary)
        toolbar.addWidget(self.btn_yeni)
        
        layout.addLayout(toolbar)
        
        # Arama alanı
        search_card = QFrame()
        search_card.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
            }}
            QLineEdit {{
                border: 1px solid {self.color_border};
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.color_primary};
            }}
        """)
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(12, 10, 12, 10)
        search_layout.setSpacing(8)
        search_label = QLabel("Ara:")
        search_label.setFont(self._brand_font(size=12, bold=True))
        search_label.setStyleSheet(f"color: {self.color_text};")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Fatura no, cari hesap veya tarih ile ara...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_card)
        
        # Tablo kartı
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
            }}
        """)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Fatura No", "Tarih", "Cari Kodu", "Ünvan", 
            "Toplam", "KDV", "Net Tutar", "Durum", "Düzenleyen"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: #ffffff;
                alternate-background-color: #f5f6fb;
                border: none;
            }}
            QHeaderView::section {{
                background: #f5f6fb;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {self.color_border};
                color: {self.color_muted};
                font-weight: 600;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QTableWidget::item:selected {{
                background: {self.color_primary_soft};
                color: {self.color_primary_dark};
            }}
        """)
        
        layout_table_actions = QHBoxLayout()
        layout_table_actions.setSpacing(8)
        layout_table_actions.addStretch()
        
        table_layout.addWidget(self.table)
        table_layout.addLayout(layout_table_actions)
        layout.addWidget(table_card)
        
        self.setLayout(layout)
    
    def _style_primary_button(self, btn, bg, dark_text=False):
        text_color = "#0f112b" if dark_text else "#ffffff"
        btn.setMinimumHeight(36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                font-weight: 700;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
            }}
            QPushButton:hover {{ background-color: {self._adjust_color(bg, 1.08)}; }}
            QPushButton:pressed {{ background-color: {self._adjust_color(bg, 0.9)}; }}
        """)
    
    def _style_secondary_button(self, btn, bg):
        btn.setMinimumHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background-color: {self._adjust_color(bg, 1.08)}; }}
            QPushButton:pressed {{ background-color: {self._adjust_color(bg, 0.9)}; }}
        """)
    
    def display_data(self, fatura_list):
        """Veriyi tabloda göster"""
        self.fatura_list = fatura_list or []
        self.filtered_list = self.fatura_list
        self._update_table()
    
    def _update_table(self):
        """Tabloyu güncelle"""
        if not hasattr(self, 'filtered_list') or self.filtered_list is None:
            self.filtered_list = []
        
        self.table.setRowCount(len(self.filtered_list))
        
        for row, fatura in enumerate(self.filtered_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(fatura.get('faturaNo', '-'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(fatura.get('tarih', '-'))))
            
            cari_hesap = fatura.get('cariHesap', {}) if isinstance(fatura.get('cariHesap'), dict) else {}
            self.table.setItem(row, 2, QTableWidgetItem(str(cari_hesap.get('kodu', '-'))))
            self.table.setItem(row, 3, QTableWidgetItem(str(cari_hesap.get('unvani', '-'))))
            
            toplam = float(fatura.get('toplam', 0) or 0)
            toplam_kdv = float(fatura.get('toplamKDV', 0) or 0)
            net_tutar = float(fatura.get('netTutar', 0) or 0)
            
            self.table.setItem(row, 4, QTableWidgetItem(f"{toplam:.2f} ₺"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{toplam_kdv:.2f} ₺"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{net_tutar:.2f} ₺"))
            
            durum = fatura.get('durum', 'Açık')
            durum_item = QTableWidgetItem(str(durum))
            if durum == 'Kesildi':
                durum_item.setForeground(QColor(40, 167, 69))
            else:
                durum_item.setForeground(QColor(255, 193, 7))
            self.table.setItem(row, 7, durum_item)
            
            duzenleyen = fatura.get('last_modified_by_name', '') or fatura.get('created_by_name', '-')
            self.table.setItem(row, 8, QTableWidgetItem(str(duzenleyen)))
    
    def on_search_changed(self, text):
        """Arama metni değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(text)
    
    def get_selected_row(self):
        """Seçili satırı döndür"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.fatura_list):
            return self.fatura_list[current_row]
        return None
    
    def show_error(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        QMessageBox.information(self, "Başarılı", message)
    
    def set_callbacks(self, on_geri, on_yeni, on_context_menu=None, on_double_click=None, on_search=None, 
                      on_export_pdf=None, on_export_excel=None, on_export_csv=None, on_gonder=None):
        """Callback'leri ayarla"""
        self.btn_geri.clicked.connect(on_geri)
        self.btn_yeni.clicked.connect(on_yeni)
        if on_export_pdf:
            self.btn_export_pdf.clicked.connect(on_export_pdf)
        if on_export_excel:
            self.btn_export_excel.clicked.connect(on_export_excel)
        if on_export_csv:
            self.btn_export_csv.clicked.connect(on_export_csv)
        if on_gonder:
            self.btn_gonder.clicked.connect(on_gonder)
        if on_context_menu:
            self.table.customContextMenuRequested.connect(on_context_menu)
        if on_double_click:
            def handle_double_click(item):
                row = item.row()
                if hasattr(self, 'filtered_list') and row >= 0 and row < len(self.filtered_list):
                    on_double_click(self.filtered_list[row])
                else:
                    on_double_click(None)
            self.table.itemDoubleClicked.connect(handle_double_click)
        if on_search:
            self._search_callback = on_search
    
    def filter_data(self, filtered_list):
        """Filtrelenmiş veriyi göster"""
        self.filtered_list = filtered_list or []
        self._update_table()
    
    @staticmethod
    def _adjust_color(hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
