"""
Cari Hesap List View - MUBA teması
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QMessageBox,
    QLineEdit, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QPixmap


class CariHesapListView(QWidget):
    """Cari hesap listesi görünümü - View katmanı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.cari_list = []
        self.filtered_list = []
        self._load_brand_fonts()
        self._init_colors()
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
        self.color_primary_soft = "#dfe3ff"
    
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
        
        title = QLabel("Cari Hesaplar")
        title.setFont(self._brand_font(size=18, bold=True))
        title.setStyleSheet(f"color: {self.color_text};")
        toolbar.addWidget(title)
        toolbar.addStretch()
        
        self.btn_yeni = QPushButton("Yeni Cari Hesap")
        self.btn_yeni.setMinimumHeight(36)
        self.btn_yeni.setCursor(Qt.PointingHandCursor)
        self.btn_yeni.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_accent};
                color: #0f112b;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #d87c05; }}
        """)
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
        self.search_input.setPlaceholderText("Şirket adı, vergi no veya ad ile ara...")
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Vergi Numarası", "Şirket Adı", "Telefon", "E-Posta", 
            "Borç/Alacak", "Adres", "NOT1"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.itemDoubleClicked.connect(self.on_double_click)
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
    
    def on_double_click(self, item):
        """Çift tıklama event handler"""
        row = item.row()
        if row < len(self.cari_list):
            if hasattr(self, '_double_click_callback'):
                self._double_click_callback(self.cari_list[row])
    
    def display_data(self, cari_list):
        """Veriyi tabloda göster"""
        self.cari_list = cari_list or []
        self.filtered_list = self.cari_list
        self._update_table()
    
    def _update_table(self):
        """Tabloyu güncelle"""
        self.table.setRowCount(len(self.filtered_list))
        
        for row, cari in enumerate(self.filtered_list):
            vergi_no_display = self._mask_vergi_no(cari.get('vergiNoHash', ''), cari.get('vergiNo', ''))
            self.table.setItem(row, 0, QTableWidgetItem(vergi_no_display))
            self.table.setItem(row, 1, QTableWidgetItem(cari.get('unvani', '-')))
            self.table.setItem(row, 2, QTableWidgetItem(cari.get('telefon', '-')))
            self.table.setItem(row, 3, QTableWidgetItem(cari.get('email', '-')))
            
            borc_durumu = self._calculate_borc_durumu(cari)
            borc_item = QTableWidgetItem(borc_durumu)
            if borc_durumu.startswith('B'):
                borc_item.setForeground(QColor(220, 53, 69))
            elif borc_durumu.startswith('A'):
                borc_item.setForeground(QColor(40, 167, 69))
            else:
                borc_item.setForeground(QColor(108, 117, 125))
            self.table.setItem(row, 4, borc_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(cari.get('adres', '-')))
            
            not1 = ''
            if cari.get('notlar') and cari['notlar'].get('not1'):
                not1 = cari['notlar']['not1']
                if len(not1) > 50:
                    not1 = not1[:50] + '...'
            self.table.setItem(row, 6, QTableWidgetItem(not1 or '-'))
    
    def _calculate_borc_durumu(self, cari):
        """Borç durumunu hesapla"""
        borc = cari.get('borc', 0)
        alacak = cari.get('alacak', 0)
        bakiye = borc - alacak
        
        if bakiye > 0:
            return f"B ({bakiye:.2f} ₺)"
        elif bakiye < 0:
            return f"A ({abs(bakiye):.2f} ₺)"
        else:
            return "-"
    
    def on_search_changed(self, text):
        """Arama metni değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(text)
    
    def _mask_vergi_no(self, vergi_no_hash: str, vergi_no_original: str) -> str:
        """Vergi numarasını maskelenmiş göster"""
        if vergi_no_hash:
            return vergi_no_hash[:6] + '****'
        elif vergi_no_original:
            return vergi_no_original
        return '-'
    
    def get_selected_row(self):
        """Seçili satırı döndür"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.cari_list):
            return self.cari_list[current_row]
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
            self, "Sil", "Bu cari hesabı silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def set_callbacks(self, on_geri, on_yeni, on_context_menu, on_double_click=None, on_search=None):
        """Callback'leri ayarla"""
        self.btn_geri.clicked.connect(on_geri)
        self.btn_yeni.clicked.connect(on_yeni)
        self.table.customContextMenuRequested.connect(on_context_menu)
        if on_double_click:
            self._double_click_callback = on_double_click
        if on_search:
            self._search_callback = on_search
    
    def filter_data(self, filtered_list):
        """Filtrelenmiş veriyi göster"""
        self.filtered_list = filtered_list or []
        self._update_table()
