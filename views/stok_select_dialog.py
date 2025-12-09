"""
Stok Seçim Dialog - Stok seçimi için (MUBA teması)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt


class StokSelectDialog(QDialog):
    """Stok seçim dialog'u"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stok Seç")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.selected_stok = None
        self._init_colors()
        self.init_ui()
        self.load_stoklar()

    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_accent = "#f48c06"
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"

    def _style_btn(self, btn, bg, fg="#ffffff"):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: none;
                padding: 8px 12px;
                font-weight: 700;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background: {self._tint(bg, 1.07)}; }}
            QPushButton:pressed {{ background: {self._tint(bg, 0.9)}; }}
        """)

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
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        search_layout = QHBoxLayout()
        search_label = QLabel("Ara:")
        search_label.setStyleSheet(f"font-weight: 700; color: {self.color_text};")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Kod, ad veya açıklama ile ara...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Kod", "Ad", "Birim", "Birim Fiyat", "Stok", "KDV %"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_double_click)

        layout.addWidget(self.table)

        footer = QHBoxLayout()
        footer.addStretch()
        
        self.btn_sec = QPushButton("Seç")
        self._style_btn(self.btn_sec, self.color_accent)
        self.btn_sec.clicked.connect(self.accept_selection)
        footer.addWidget(self.btn_sec)
        
        self.btn_kapat = QPushButton("Kapat")
        self._style_btn(self.btn_kapat, self.color_primary)
        self.btn_kapat.clicked.connect(self.reject)
        footer.addWidget(self.btn_kapat)
        layout.addLayout(footer)

        self.setLayout(layout)

    # Data loaders and handlers
    def load_stoklar(self, stok_list=None):
        """Stok listesini tabloya yükle"""
        try:
            if stok_list is None:
                # Veritabanından malzemeleri yükle
                from models.malzeme_model import MalzemeModel
                malzeme_model = MalzemeModel()
                stok_list = malzeme_model.get_all()
            
            self.all_stok = stok_list or []
            self.update_table(self.all_stok)
        except Exception as e:
            print(f"Stok yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Hata", f"Malzemeler yüklenirken hata oluştu:\n{str(e)}")
            self.all_stok = []
            self.update_table([])

    def update_table(self, stok_list):
        self.table.setRowCount(len(stok_list))
        for row, stok in enumerate(stok_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(stok.get('kod', '-'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(stok.get('ad', '-'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(stok.get('birim', '-'))))
            
            # Birim fiyatı farklı alanlardan kontrol et (öncelik sırasına göre)
            birim_fiyat = 0.0
            # Önce birimFiyat'ı kontrol et (None veya boş değilse)
            if 'birimFiyat' in stok and stok['birimFiyat'] is not None:
                try:
                    birim_fiyat = float(stok['birimFiyat'])
                except (ValueError, TypeError):
                    birim_fiyat = 0.0
            elif 'birim_fiyat' in stok and stok['birim_fiyat'] is not None:
                try:
                    birim_fiyat = float(stok['birim_fiyat'])
                except (ValueError, TypeError):
                    birim_fiyat = 0.0
            elif 'current_sell_price' in stok and stok['current_sell_price'] is not None:
                try:
                    birim_fiyat = float(stok['current_sell_price'])
                except (ValueError, TypeError):
                    birim_fiyat = 0.0
            
            # Fiyatı göster (0 olsa bile)
            birim_fiyat_text = f"{birim_fiyat:.2f} TL"
            self.table.setItem(row, 3, QTableWidgetItem(birim_fiyat_text))
            
            # Stok miktarı
            stok_miktar = stok.get('stok', stok.get('stok_miktar', 0))
            if stok_miktar is None or stok_miktar == '':
                stok_miktar = '-'
            else:
                try:
                    stok_miktar = f"{float(stok_miktar):.2f}"
                except:
                    stok_miktar = str(stok_miktar)
            self.table.setItem(row, 4, QTableWidgetItem(str(stok_miktar)))
            
            # KDV oranı
            kdv_orani = stok.get('kdvOrani', stok.get('kdv_orani', 0))
            if kdv_orani is None or kdv_orani == '':
                kdv_orani = '-'
            else:
                try:
                    kdv_orani = f"{int(float(kdv_orani))}"
                except:
                    kdv_orani = str(kdv_orani)
            self.table.setItem(row, 5, QTableWidgetItem(str(kdv_orani)))

    def on_search(self, text):
        """Arama filtresi"""
        text = text.lower()
        filtered = []
        for stok in getattr(self, 'all_stok', []):
            haystack = f"{stok.get('kod','')} {stok.get('ad','')} {stok.get('aciklama','')}".lower()
            if text in haystack:
                filtered.append(stok)
        self.update_table(filtered)

    def on_double_click(self, item):
        """Çift tıklama ile seçim"""
        row = item.row()
        try:
            # Filtrelenmiş listeden seç
            filtered_list = self._get_filtered_list()
            
            if row < len(filtered_list):
                self.selected_stok = filtered_list[row]
                self.accept()
            else:
                QMessageBox.warning(self, "Uyarı", "Geçersiz seçim!")
        except Exception as e:
            print(f"Stok seçim hatası: {e}")
            import traceback
            traceback.print_exc()
            self.selected_stok = None
    
    def _get_filtered_list(self):
        """Filtrelenmiş listeyi döndür"""
        filtered_list = []
        search_text = self.search_input.text().lower()
        if search_text:
            for stok in getattr(self, 'all_stok', []):
                haystack = f"{stok.get('kod','')} {stok.get('ad','')} {stok.get('aciklama','')}".lower()
                if search_text in haystack:
                    filtered_list.append(stok)
        else:
            filtered_list = getattr(self, 'all_stok', [])
        return filtered_list

    def accept_selection(self):
        """Seç butonuna basıldığında"""
        try:
            current_row = self.table.currentRow()
            if current_row >= 0:
                # Filtrelenmiş listeden seç
                filtered_list = self._get_filtered_list()
                
                if current_row < len(filtered_list):
                    self.selected_stok = filtered_list[current_row]
                    self.accept()
                else:
                    QMessageBox.warning(self, "Uyarı", "Lütfen bir malzeme seçiniz!")
            else:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir malzeme seçiniz!")
        except Exception as e:
            print(f"Seçim hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def get_selected_stok(self):
        return self.selected_stok
