"""
Alış Faturası List View - Liste görünümü
MVC View katmanı - Sadece UI işlemleri
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class PurchaseInvoiceListView(QWidget):
    """Alış faturası listesi görünümü - View katmanı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.invoice_list = []
        self.filtered_list = []
        self._init_colors()
        self.init_ui()

    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_success = "#16a34a"
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
            QWidget#purchase_root {{
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
                left: 12px;
                padding: 0 6px;
                color: {self.color_text};
                font-weight: 700;
            }}
            QLineEdit {{
                border: 1px solid {self.color_border};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 13px;
                background: #ffffff;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.color_primary};
            }}
            QTableWidget {{
                background: #ffffff;
                alternate-background-color: #f5f6fb;
                border: none;
            }}
            QHeaderView::section {{
                background: #f3f4ff;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {self.color_border};
                color: {self.color_text};
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        self.setObjectName("purchase_root")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        def style_btn(btn, bg, fg="#ffffff"):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg};
                    color: {fg};
                    border: none;
                    padding: 8px 14px;
                    font-weight: 700;
                    border-radius: 4px;
                }}
                QPushButton:hover {{ background: {self._tint(bg, 1.07)}; }}
                QPushButton:pressed {{ background: {self._tint(bg, 0.9)}; }}
            """)
        
        # Üst toolbar
        toolbar = QHBoxLayout()
        
        # Geri butonu
        self.btn_geri = QPushButton("← Geri")
        style_btn(self.btn_geri, self.color_primary)
        toolbar.addWidget(self.btn_geri)
        
        title = QLabel("Alış Faturaları")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        # Export butonları
        self.btn_export_pdf = QPushButton("PDF")
        style_btn(self.btn_export_pdf, self.color_accent)
        toolbar.addWidget(self.btn_export_pdf)
        
        self.btn_export_excel = QPushButton("Excel")
        style_btn(self.btn_export_excel, self.color_success)
        toolbar.addWidget(self.btn_export_excel)
        
        self.btn_export_csv = QPushButton("CSV")
        style_btn(self.btn_export_csv, self.color_primary_dark)
        toolbar.addWidget(self.btn_export_csv)
        
        self.btn_yeni = QPushButton("Yeni Alış Faturası Ekle")
        style_btn(self.btn_yeni, self.color_primary)
        toolbar.addWidget(self.btn_yeni)
        
        layout.addLayout(toolbar)
        
        # Arama çubuğu
        search_layout = QHBoxLayout()
        search_label = QLabel("Ara:")
        search_label.setStyleSheet(f"font-weight: 700; color: {self.color_text};")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Fatura no, tedarikçi veya tarih ile ara...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Fatura No", "Tarih", "Tedarikçi",
            "Toplam", "KDV", "Net Tutar", "Durum"
        ])
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def display_data(self, invoice_list):
        """Veriyi tabloda göster"""
        if invoice_list is None:
            invoice_list = []
        self.invoice_list = invoice_list
        self.filtered_list = invoice_list
        self._update_table()
    
    def _update_table(self):
        """Tabloyu güncelle"""
        if not hasattr(self, 'filtered_list') or self.filtered_list is None:
            self.filtered_list = []
        
        self.table.setRowCount(len(self.filtered_list))
        
        for row, invoice in enumerate(self.filtered_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(invoice.get('fatura_no', '-'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(invoice.get('fatura_tarihi', '-'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(invoice.get('tedarikci_unvani', '-'))))
            
            toplam = float(invoice.get('toplam', 0) or 0)
            toplam_kdv = float(invoice.get('toplam_kdv', 0) or 0)
            net_tutar = float(invoice.get('net_tutar', 0) or 0)
            
            self.table.setItem(row, 3, QTableWidgetItem(f"{toplam:.2f} TL"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{toplam_kdv:.2f} TL"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{net_tutar:.2f} TL"))
            
            durum = invoice.get('durum', 'Açık')
            durum_item = QTableWidgetItem(str(durum))
            if durum == 'Kesildi':
                durum_item.setForeground(QColor(40, 167, 69))  # Yeşil
            elif durum == 'İptal':
                durum_item.setForeground(QColor(220, 53, 69))  # Kırmızı
            else:
                durum_item.setForeground(QColor(108, 117, 125))  # Gri
            self.table.setItem(row, 6, durum_item)
    
    def on_search_changed(self, text):
        """Arama metni değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(text)
    
    def get_selected_row(self):
        """Seçili satırı döndür"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_list):
            return self.filtered_list[current_row]
        return None
    
    def show_error(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        QMessageBox.information(self, "Başarılı", message)
    
    def set_callbacks(self, on_geri, on_yeni, on_context_menu=None, on_double_click=None, on_search=None, 
                      on_export_pdf=None, on_export_excel=None, on_export_csv=None):
        """Callback'leri ayarla"""
        self.btn_geri.clicked.connect(on_geri)
        self.btn_yeni.clicked.connect(on_yeni)
        if on_export_pdf:
            self.btn_export_pdf.clicked.connect(on_export_pdf)
        if on_export_excel:
            self.btn_export_excel.clicked.connect(on_export_excel)
        if on_export_csv:
            self.btn_export_csv.clicked.connect(on_export_csv)
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
        self.filtered_list = filtered_list
        self._update_table()

