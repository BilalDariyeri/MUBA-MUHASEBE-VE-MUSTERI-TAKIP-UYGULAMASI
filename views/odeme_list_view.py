"""
Ödeme List View - MUBA teması
Sekmeli görünüm: Tedarikçi, Maaş, Kira, Diğer
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QGroupBox, QGridLayout, QFrame, QComboBox, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QPixmap


class OdemeListView(QWidget):
    """Ödeme listesi görünümü - View katmanı (Sekmeli)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.odeme_list = []
        self.filtered_list = []
        self.filtered_lists = {
            'TEDARIKCI': [],
            'MAAS': [],
            'KIRA': [],
            'DIGER': []
        }
        self.current_kategori = 'TEDARIKCI'
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
        self.color_danger = "#ef4444"
    
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
        
        title = QLabel("Ödemeler")
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
        
        self.btn_sync = QPushButton("Alım Faturalarını Senkronize Et")
        self._style_secondary_button(self.btn_sync, self.color_info)
        toolbar.addWidget(self.btn_sync)
        
        self.btn_yeni = QPushButton("Yeni Ödeme")
        self._style_primary_button(self.btn_yeni, self.color_accent, dark_text=True)
        toolbar.addWidget(self.btn_yeni)
        
        layout.addLayout(toolbar)
        
        # Özet İstatistikler
        stats_group = QGroupBox("Özet İstatistikler")
        stats_group.setStyleSheet(self._group_style())
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(12)
        stats_layout.setContentsMargins(12, 16, 12, 12)
        
        self.label_toplam_odeme = self._create_stat_card("Toplam Ödeme", "0 ₺", self.color_primary)
        self.label_tedarikci = self._create_stat_card("Tedarikçi", "0 ₺", self.color_info)
        self.label_maas = self._create_stat_card("Maaş", "0 ₺", self.color_success)
        self.label_kira = self._create_stat_card("Kira", "0 ₺", self.color_warning)
        self.label_diger = self._create_stat_card("Diğer", "0 ₺", self.color_muted)
        
        stats_layout.addWidget(self.label_toplam_odeme, 0, 0)
        stats_layout.addWidget(self.label_tedarikci, 0, 1)
        stats_layout.addWidget(self.label_maas, 0, 2)
        stats_layout.addWidget(self.label_kira, 0, 3)
        stats_layout.addWidget(self.label_diger, 0, 4)
        layout.addWidget(stats_group)
        
        # Sekmeler
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.color_border};
                border-radius: 8px;
                background: {self.color_card};
            }}
            QTabBar::tab {{
                background: {self.color_primary_soft};
                color: {self.color_text};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: {self.color_primary};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {self._adjust_color(self.color_primary_soft, 1.1)};
            }}
        """)
        
        # Her sekme için tablo widget'ı oluştur
        self.tables = {}
        self.filter_inputs = {}
        self.filter_combos = {}
        
        kategoriler = [
            ('TEDARIKCI', 'Tedarikçi Ödemeleri'),
            ('MAAS', 'Maaş Ödemeleri'),
            ('KIRA', 'Kira Ödemeleri'),
            ('DIGER', 'Diğer Ödemeler')
        ]
        
        for kategori, label in kategoriler:
            tab_widget = self._create_tab_content(kategori)
            self.tab_widget.addTab(tab_widget, label)
        
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def _create_tab_content(self, kategori):
        """Sekme içeriği oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Arama ve Filtreleme
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
        search_input = QLineEdit()
        search_input.setPlaceholderText("Tedarikçi, tarih, ödeme türü veya tutar ile ara...")
        search_input.setStyleSheet(f"""
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
        filter_combo = QComboBox()
        filter_combo.addItems(["Tümü", "Nakit", "Havale/EFT", "Çek", "Kredi Kartı"])
        filter_combo.setStyleSheet(f"""
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
        filter_layout.addWidget(search_input)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(filter_combo)
        layout.addWidget(filter_card)
        
        # Tablo
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
        
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Tarih", "Tedarikçi/Alıcı", "Tutar", "Ödeme Türü",
            "Kasa/Banka", "Belge No", "Açıklama", "Alım Faturası"
        ])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.setStyleSheet(f"""
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
        
        table_layout.addWidget(table)
        layout.addWidget(table_card)
        
        # Kaydet
        self.tables[kategori] = table
        self.filter_inputs[kategori] = search_input
        self.filter_combos[kategori] = filter_combo
        
        # Signal bağlantıları
        search_input.textChanged.connect(lambda text, k=kategori: self.on_search_changed(text, k))
        filter_combo.currentTextChanged.connect(lambda text, k=kategori: self.on_filter_changed(text, k))
        table.customContextMenuRequested.connect(lambda pos, k=kategori: self.on_context_menu(pos, k))
        
        return widget
    
    def on_tab_changed(self, index):
        """Sekme değiştiğinde"""
        kategoriler = ['TEDARIKCI', 'MAAS', 'KIRA', 'DIGER']
        if index < len(kategoriler):
            self.current_kategori = kategoriler[index]
            if hasattr(self, '_refresh_callback'):
                self._refresh_callback(self.current_kategori)
    
    def on_search_changed(self, text, kategori):
        """Arama metni değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(text, kategori)
    
    def on_filter_changed(self, text, kategori):
        """Filtre değiştiğinde"""
        if hasattr(self, '_filter_callback'):
            self._filter_callback(text, kategori)
    
    def on_context_menu(self, position, kategori):
        """Sağ tık menüsü"""
        if hasattr(self, '_context_menu_callback'):
            self._context_menu_callback(position, kategori)
    
    def display_data(self, odeme_list, kategori=None):
        """Veriyi tabloda göster"""
        if odeme_list is None:
            odeme_list = []
        
        self.odeme_list = odeme_list
        
        # Kategorilere göre ayır
        for kat in ['TEDARIKCI', 'MAAS', 'KIRA', 'DIGER']:
            self.filtered_lists[kat] = [o for o in odeme_list if o.get('kategori') == kat]
            self._update_table(self.filtered_lists[kat], kat)
        
        self._update_statistics(odeme_list)
    
    def _update_table(self, odeme_list, kategori):
        """Tabloyu güncelle"""
        if kategori not in self.tables:
            return
        
        table = self.tables[kategori]
        table.setRowCount(len(odeme_list))
        
        for row, odeme in enumerate(odeme_list):
            # Tarih
            tarih_item = QTableWidgetItem(str(odeme.get('tarih', '-')))
            tarih_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, tarih_item)
            
            # Tedarikçi/Alıcı
            tedarikci = odeme.get('tedarikci_unvani', '-')
            if not tedarikci or tedarikci == '-':
                # Kategoriye göre varsayılan isim
                if odeme.get('kategori') == 'MAAS':
                    tedarikci = odeme.get('aciklama', 'Maaş Ödemesi')
                elif odeme.get('kategori') == 'KIRA':
                    tedarikci = odeme.get('aciklama', 'Kira Ödemesi')
                else:
                    tedarikci = odeme.get('aciklama', '-')
            table.setItem(row, 1, QTableWidgetItem(str(tedarikci)))
            
            # Tutar
            tutar = float(odeme.get('tutar', 0) or 0)
            tutar_item = QTableWidgetItem(f"{tutar:,.2f} ₺")
            tutar_item.setForeground(QColor(self.color_danger))
            tutar_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            tutar_item.setFont(QFont("", -1, QFont.Bold))
            table.setItem(row, 2, tutar_item)
            
            # Ödeme Türü
            odeme_turu = odeme.get('odeme_turu', 'Nakit')
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
            table.setItem(row, 3, odeme_item)
            
            # Kasa/Banka
            kasa_banka = odeme.get('kasa', '') or odeme.get('banka', '-')
            table.setItem(row, 4, QTableWidgetItem(str(kasa_banka)))
            
            # Belge No
            belge_no = odeme.get('belge_no', '-')
            table.setItem(row, 5, QTableWidgetItem(str(belge_no)))
            
            # Açıklama
            aciklama = odeme.get('aciklama', '-')
            table.setItem(row, 6, QTableWidgetItem(str(aciklama)))
            
            # Alım Faturası
            alim_faturasi_no = odeme.get('alim_faturasi_no', '-')
            table.setItem(row, 7, QTableWidgetItem(str(alim_faturasi_no)))
    
    def _update_statistics(self, odeme_list):
        """İstatistikleri güncelle"""
        toplam = sum(float(o.get('tutar', 0) or 0) for o in odeme_list)
        tedarikci = sum(float(o.get('tutar', 0) or 0) for o in odeme_list if o.get('kategori') == 'TEDARIKCI')
        maas = sum(float(o.get('tutar', 0) or 0) for o in odeme_list if o.get('kategori') == 'MAAS')
        kira = sum(float(o.get('tutar', 0) or 0) for o in odeme_list if o.get('kategori') == 'KIRA')
        diger = sum(float(o.get('tutar', 0) or 0) for o in odeme_list if o.get('kategori') == 'DIGER')
        
        self.label_toplam_odeme.value_label.setText(f"{toplam:,.2f} ₺")
        self.label_tedarikci.value_label.setText(f"{tedarikci:,.2f} ₺")
        self.label_maas.value_label.setText(f"{maas:,.2f} ₺")
        self.label_kira.value_label.setText(f"{kira:,.2f} ₺")
        self.label_diger.value_label.setText(f"{diger:,.2f} ₺")
    
    def set_callbacks(self, on_geri=None, on_yeni=None, on_search=None, on_filter=None, 
                     on_context_menu=None, on_export_pdf=None, on_export_excel=None, on_refresh=None, on_sync=None):
        """Callback'leri ayarla"""
        if on_geri:
            self.btn_geri.clicked.connect(on_geri)
        if on_yeni:
            self.btn_yeni.clicked.connect(on_yeni)
        if on_export_pdf:
            self.btn_export_pdf.clicked.connect(on_export_pdf)
        if on_export_excel:
            self.btn_export_excel.clicked.connect(on_export_excel)
        if on_sync:
            self.btn_sync.clicked.connect(on_sync)
        self._search_callback = on_search
        self._filter_callback = on_filter
        self._context_menu_callback = on_context_menu
        self._refresh_callback = on_refresh
    
    def get_current_kategori(self):
        """Mevcut seçili kategoriyi döndür"""
        return self.current_kategori
    
    def get_selected_row(self, kategori=None):
        """Seçili satırı döndür"""
        kat = kategori or self.current_kategori
        if kat not in self.tables:
            return None
        table = self.tables[kat]
        current_row = table.currentRow()
        if current_row >= 0:
            # Filtered list'ten al
            if hasattr(self, 'filtered_lists') and kat in self.filtered_lists:
                if current_row < len(self.filtered_lists[kat]):
                    return self.filtered_lists[kat][current_row]
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
            self, 'Sil', 'Bu ödemeyi silmek istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
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
        value_label.setObjectName(f"value_{title.replace(' ', '_')}")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Value label'a referans ekle
        card.value_label = value_label
        
        return card
    
    @staticmethod
    def _adjust_color(hex_color, factor):
        """Rengi aydınlatmak/koyulaştırmak için yardımcı fonksiyon"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

