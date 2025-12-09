"""
Tahsilat List View - MUBA teması
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QGroupBox, QGridLayout, QFrame, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QPixmap


class TahsilatListView(QWidget):
    """Tahsilat listesi görünümü - View katmanı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.tahsilat_list = []
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
        self.color_info = "#0ea5e9"
    
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
        
        title = QLabel("Tahsilatlar")
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
        
        self.btn_yeni = QPushButton("Yeni Tahsilat")
        self._style_primary_button(self.btn_yeni, self.color_accent, dark_text=True)
        toolbar.addWidget(self.btn_yeni)
        
        layout.addLayout(toolbar)
        
        # Özet İstatistikler
        stats_group = QGroupBox("Özet İstatistikler")
        stats_group.setStyleSheet(self._group_style())
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(12)
        stats_layout.setContentsMargins(12, 16, 12, 12)
        
        self.label_toplam_odeme = self._create_stat_card("Toplam Tahsilat", "0 ₺", self.color_primary)
        self.label_nakit = self._create_stat_card("Nakit", "0 ₺", self.color_success)
        self.label_havale = self._create_stat_card("Havale/EFT", "0 ₺", self.color_info)
        self.label_cek = self._create_stat_card("Çek", "0 ₺", self.color_warning)
        self.label_kayit_sayisi = self._create_stat_card("Kayıt Sayısı", "0", self.color_muted)
        
        stats_layout.addWidget(self.label_toplam_odeme, 0, 0)
        stats_layout.addWidget(self.label_nakit, 0, 1)
        stats_layout.addWidget(self.label_havale, 0, 2)
        stats_layout.addWidget(self.label_cek, 0, 3)
        stats_layout.addWidget(self.label_kayit_sayisi, 0, 4)
        layout.addWidget(stats_group)
        
        # Arama ve Filtreleme kartı
        filter_card = QFrame()
        filter_card.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(8)
        
        search_label = QLabel("Ara:")
        search_label.setFont(self._brand_font(size=12, bold=True))
        search_label.setStyleSheet(f"color: {self.color_text};")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari hesap, tarih, ödeme türü veya tutar ile ara...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {self.color_border};
                border-radius: 6px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.color_primary};
            }}
        """)
        
        filter_label = QLabel("Ödeme Türü:")
        filter_label.setFont(self._brand_font(size=12, bold=True))
        filter_label.setStyleSheet(f"color: {self.color_text};")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tümü", "Nakit", "Havale/EFT", "Çek", "Senet", "Kredi Kartı"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        self.filter_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {self.color_border};
                border-radius: 6px;
                font-size: 13px;
                min-width: 120px;
            }}
            QComboBox:focus {{
                border: 1px solid {self.color_primary};
            }}
        """)
        
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_input)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        layout.addWidget(filter_card)
        
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
            "Tarih", "Cari Hesap", "Tutar", "Ödeme Türü",
            "Kasa/Banka", "Belge No", "Açıklama", "Eski Borç", "Yeni Borç"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
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
    
    def _group_style(self):
        return f"""
            QGroupBox {{
                background-color: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                color: {self.color_text};
                font-weight: 600;
            }}
        """
    
    def _create_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        title_label = QLabel(title)
        title_label.setFont(self._brand_font(size=11, bold=True))
        title_label.setStyleSheet(f"color: {self.color_muted};")
        value_label = QLabel(value)
        value_label.setFont(self._brand_font(size=16, bold=True))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName(f"value_{title.replace(' ', '_').replace('/', '_')}")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card
    
    def display_data(self, tahsilat_list):
        """Veriyi tabloda göster"""
        if tahsilat_list is None:
            tahsilat_list = []
        self.tahsilat_list = tahsilat_list
        self.filtered_list = tahsilat_list
        self._update_table()
        self._update_statistics()
    
    def _update_table(self):
        """Tabloyu güncelle"""
        if not hasattr(self, 'filtered_list') or self.filtered_list is None:
            self.filtered_list = []
        
        self.table.setRowCount(len(self.filtered_list))
        
        for row, tahsilat in enumerate(self.filtered_list):
            tarih_item = QTableWidgetItem(str(tahsilat.get('tarih', '-')))
            tarih_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, tarih_item)
            
            self.table.setItem(row, 1, QTableWidgetItem(str(tahsilat.get('cari_unvani', '-'))))
            
            tutar = float(tahsilat.get('tutar', 0) or 0)
            tutar_item = QTableWidgetItem(f"{tutar:,.2f} ₺")
            tutar_item.setForeground(QColor(40, 167, 69))
            tutar_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            tutar_item.setFont(QFont("", -1, QFont.Bold))
            self.table.setItem(row, 2, tutar_item)
            
            odeme_turu = tahsilat.get('odeme_turu', 'Nakit')
            odeme_item = QTableWidgetItem(str(odeme_turu))
            odeme_item.setTextAlignment(Qt.AlignCenter)
            if odeme_turu == 'Nakit':
                odeme_item.setForeground(QColor(40, 167, 69))
            elif odeme_turu in ['Havale/EFT', 'Havale', 'EFT']:
                odeme_item.setForeground(QColor(14, 165, 233))
            elif odeme_turu == 'Çek':
                odeme_item.setForeground(QColor(245, 158, 11))
            elif odeme_turu == 'Kredi Kartı':
                odeme_item.setForeground(QColor(99, 102, 241))
            else:
                odeme_item.setForeground(QColor(108, 117, 125))
            self.table.setItem(row, 3, odeme_item)
            
            kasa_banka = tahsilat.get('kasa', '') or tahsilat.get('banka', '-')
            self.table.setItem(row, 4, QTableWidgetItem(str(kasa_banka)))
            
            belge_no = tahsilat.get('belge_no', '-')
            self.table.setItem(row, 5, QTableWidgetItem(str(belge_no)))
            
            aciklama = tahsilat.get('aciklama', '')
            self.table.setItem(row, 6, QTableWidgetItem(str(aciklama)))
            
            eski_borc = float(tahsilat.get('eski_borc', 0) or 0)
            eski_borc_item = QTableWidgetItem(f"{eski_borc:,.2f} ₺")
            eski_borc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if eski_borc > 0:
                eski_borc_item.setForeground(QColor(220, 53, 69))
            self.table.setItem(row, 7, eski_borc_item)
            
            yeni_borc = float(tahsilat.get('yeni_borc', 0) or 0)
            yeni_borc_item = QTableWidgetItem(f"{yeni_borc:,.2f} ₺")
            yeni_borc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if yeni_borc < eski_borc:
                yeni_borc_item.setForeground(QColor(40, 167, 69))
            elif yeni_borc > 0:
                yeni_borc_item.setForeground(QColor(245, 158, 11))
            self.table.setItem(row, 8, yeni_borc_item)
    
    def _update_statistics(self):
        """İstatistikleri güncelle"""
        data = self.filtered_list if hasattr(self, 'filtered_list') else []
        
        toplam = sum(float(t.get('tutar', 0) or 0) for t in data)
        nakit = sum(float(t.get('tutar', 0) or 0) for t in data if t.get('odeme_turu') == 'Nakit')
        havale = sum(float(t.get('tutar', 0) or 0) for t in data if t.get('odeme_turu') in ['Havale/EFT', 'Havale', 'EFT'])
        cek = sum(float(t.get('tutar', 0) or 0) for t in data if t.get('odeme_turu') == 'Çek')
        kayit_sayisi = len(data)
        
        self._update_stat_value(self.label_toplam_odeme, f"{toplam:,.2f} ₺")
        self._update_stat_value(self.label_nakit, f"{nakit:,.2f} ₺")
        self._update_stat_value(self.label_havale, f"{havale:,.2f} ₺")
        self._update_stat_value(self.label_cek, f"{cek:,.2f} ₺")
        self._update_stat_value(self.label_kayit_sayisi, str(kayit_sayisi))
    
    def _update_stat_value(self, card, value):
        for child in card.findChildren(QLabel):
            if child.objectName().startswith("value_"):
                child.setText(value)
                break
    
    def on_search_changed(self, text):
        """Arama metni değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(text, self.filter_combo.currentText())
    
    def on_filter_changed(self, filter_text):
        """Filtre değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(self.search_input.text(), filter_text)
    
    def get_selected_row(self):
        """Seçili satırı döndür"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_list):
            return self.filtered_list[current_row]
        return None
    
    def filter_data(self, filtered_list):
        """Filtrelenmiş veriyi göster"""
        self.filtered_list = filtered_list or []
        self._update_table()
        self._update_statistics()
    
    def set_callbacks(self, callbacks):
        """Callback'leri ayarla"""
        self._search_callback = callbacks.get('on_search')
        self.btn_geri.clicked.connect(callbacks.get('on_geri', lambda: None))
        self.btn_export_pdf.clicked.connect(callbacks.get('on_export_pdf', lambda: None))
        self.btn_export_excel.clicked.connect(callbacks.get('on_export_excel', lambda: None))
        self.btn_yeni.clicked.connect(callbacks.get('on_yeni', lambda: None))
        self.table.customContextMenuRequested.connect(callbacks.get('on_context_menu', lambda _: None))
    
    def show_error(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        QMessageBox.information(self, "Başarılı", message)
    
    def show_delete_confirmation(self):
        """Silme onayı iste"""
        reply = QMessageBox.question(
            self, "Silme Onayı",
            "Bu ödeme kaydını silmek istediğinize emin misiniz?\nBu işlem geri alınamaz.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    @staticmethod
    def _adjust_color(hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
