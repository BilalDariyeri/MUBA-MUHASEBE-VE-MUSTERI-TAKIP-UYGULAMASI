"""
Malzeme List View - MUBA teması
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor
from services.kur_service import KurService


class MalzemeListView(QWidget):
    """Malzeme listesi görünümü - View katmanı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.malzeme_list = []
        self.filtered_list = []
        self.kur_service = KurService()
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
        self._style_primary_button(self.btn_geri, self.color_primary_dark)
        toolbar.addWidget(self.btn_geri)
        
        title = QLabel("Malzemeler")
        title.setFont(self._brand_font(size=18, bold=True))
        title.setStyleSheet(f"color: {self.color_text};")
        toolbar.addWidget(title)
        toolbar.addStretch()
        
        self.btn_yeni = QPushButton("Yeni Malzeme")
        self._style_primary_button(self.btn_yeni, self.color_accent, dark_text=True)
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
        self.search_input.setPlaceholderText("Malzeme kodu veya ad ile ara...")
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
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Kod", "Malzeme Adı", "Birim", "Stok", "Birim Fiyat (₺)", 
            "Geliş Fiyatı (₺)", "USD", "EUR", "KDV %", "Kategori", "Durum"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)
        
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
        
        table_layout.addWidget(self.table)
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
    
    def display_data(self, malzeme_list):
        """Veriyi tabloda göster"""
        self.malzeme_list = malzeme_list or []
        self.filtered_list = self.malzeme_list
        self._update_table()
    
    def _update_table(self):
        """Tabloyu güncelle"""
        self.table.setRowCount(len(self.filtered_list))
        
        for row, malzeme in enumerate(self.filtered_list):
            self.table.setItem(row, 0, QTableWidgetItem(malzeme.get('kod', '-')))
            self.table.setItem(row, 1, QTableWidgetItem(malzeme.get('ad', '-')))
            self.table.setItem(row, 2, QTableWidgetItem(malzeme.get('birim', '-')))
            
            stok = malzeme.get('stok', 0)
            birim = malzeme.get('birim', 'Adet')
            stok_text = f"{int(stok)}" if birim == 'Adet' else f"{stok:.2f}"
            stok_item = QTableWidgetItem(stok_text)
            if stok < 0:
                stok_item.setForeground(QColor(220, 53, 69))
            elif stok == 0:
                stok_item.setForeground(QColor(245, 158, 11))
            self.table.setItem(row, 3, stok_item)
            
            birim_fiyat = float(malzeme.get('birimFiyat', 0) or 0)
            self.table.setItem(row, 4, QTableWidgetItem(f"{birim_fiyat:.2f} ₺"))
            
            gelis_fiyati = float(malzeme.get('current_buy_price', 0) or malzeme.get('average_cost', 0) or 0)
            gelis_item = QTableWidgetItem(f"{gelis_fiyati:.2f} ₺")
            gelis_item.setForeground(QColor(220, 53, 69) if gelis_fiyati > 0 else QColor(108, 117, 125))
            self.table.setItem(row, 5, gelis_item)
            
            if birim_fiyat > 0:
                usd_amount = self.kur_service.try_to_usd(birim_fiyat)
                eur_amount = self.kur_service.try_to_eur(birim_fiyat)
                usd_item = QTableWidgetItem(f"${usd_amount:.2f}")
                usd_item.setForeground(QColor(40, 167, 69))
                eur_item = QTableWidgetItem(f"€{eur_amount:.2f}")
                eur_item.setForeground(QColor(14, 165, 233))
            else:
                usd_item = QTableWidgetItem("-")
                eur_item = QTableWidgetItem("-")
            self.table.setItem(row, 6, usd_item)
            self.table.setItem(row, 7, eur_item)
            
            kdv = malzeme.get('kdvOrani', 0)
            self.table.setItem(row, 8, QTableWidgetItem(f"%{kdv}"))
            self.table.setItem(row, 9, QTableWidgetItem(malzeme.get('kategori', '-')))
            
            durum = malzeme.get('durum', 'Aktif')
            durum_item = QTableWidgetItem(durum)
            durum_item.setForeground(QColor(40, 167, 69) if durum == 'Aktif' else QColor(108, 117, 125))
            self.table.setItem(row, 10, durum_item)
    
    def on_search_changed(self, text):
        """Arama metni değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(text)
    
    def get_selected_row(self):
        """Seçili satırı döndür"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.malzeme_list):
            return self.malzeme_list[current_row]
        return None
    
    def show_error(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        QMessageBox.information(self, "Başarılı", message)
    
    def show_delete_confirmation(self):
        """Silme onayı göster"""
        reply = QMessageBox.question(
            self, "Sil", "Bu malzemeyi silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def set_callbacks(self, on_geri, on_yeni, on_context_menu, on_double_click=None, on_search=None):
        """Callback'leri ayarla"""
        self.btn_geri.clicked.connect(on_geri)
        self.btn_yeni.clicked.connect(on_yeni)
        self.table.customContextMenuRequested.connect(on_context_menu)
        if on_double_click:
            self.table.itemDoubleClicked.connect(lambda item: on_double_click(self.filtered_list[item.row()] if item.row() < len(self.filtered_list) else None))
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
