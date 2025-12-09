"""
Alım Faturası Giriş View - UI Katmanı
Satış faturası formatında profesyonel alım faturası ekranı
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QMessageBox, QDialogButtonBox, QDoubleSpinBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QGroupBox,
    QLabel, QDateEdit, QWidget, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QKeyEvent
from datetime import datetime


class PurchaseInvoiceView(QDialog):
    """Alım Faturası Giriş Ekranı - Satış faturası formatında"""
    
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.invoice_data = invoice_data
        self.is_edit_mode = invoice_data is not None
        self._init_colors()
        self.setWindowTitle("Alım Faturası - Fatura Detayları")
        self.setModal(True)
        
        # Tam ekran yap
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.showMaximized()
        
        self.malzemeler = []
        # Otomatik doldurma için flag
        self.is_auto_filling = False
        self.init_ui()
        
        # Fatura numarasını otomatik oluştur
        if not self.is_edit_mode:
            self.generate_fatura_no()
        
        # Otomatik 10 satır yükle
        self.load_default_rows()
        
        if self.is_edit_mode:
            self.load_data()

    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_success = "#16a34a"
        self.color_muted = "#666a87"
        self.color_danger = "#ef4444"
        self.color_primary_soft = "#dfe3ff"

    def _tint(self, hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _style_btn(self, btn, bg, dark_text=False):
        text_color = "#0f112b" if dark_text else "#ffffff"
        btn.setMinimumHeight(34)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                font-weight: 700;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{ background-color: {self._tint(bg, 1.08)}; }}
            QPushButton:pressed {{ background-color: {self._tint(bg, 0.9)}; }}
        """)
    
    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"""
            QDialog#purchase_invoice {{
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
                color: {self.color_primary_dark};
                font-weight: 700;
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {{
                border: 1px solid {self.color_border};
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                background: #ffffff;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
                border: 1px solid {self.color_primary};
            }}
            QTableWidget {{
                background: #ffffff;
                alternate-background-color: #f5f6fb;
                border: 1px solid {self.color_border};
            }}
            QHeaderView::section {{
                background: #f3f4ff;
                padding: 6px;
                border: 1px solid {self.color_border};
                font-weight: 600;
                color: {self.color_primary_dark};
            }}
        """)
        self.setObjectName("purchase_invoice")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 1. BÖLÜM: Üst Bilgi Alanı (Header)
        self.init_header_section(layout)
        
        # 2. BÖLÜM: Orta Tablo Alanı (Grid)
        self.init_table_section(layout)
        
        # 3. BÖLÜM: Alt Toplamlar (Footer)
        self.init_footer_section(layout)
        
        self.setLayout(layout)
        
        # Satır değişikliklerini dinle
        self.satirlar_table.cellChanged.connect(self.on_cell_changed)
        # Stok kodu sütununa çift tıklama ile stok seçimi
        self.satirlar_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        # Enter tuşu ile yeni satır ekleme - keyPressEvent override
        self.original_key_press = self.satirlar_table.keyPressEvent
        self.satirlar_table.keyPressEvent = self.on_table_key_press_wrapper
    
    def init_header_section(self, main_layout):
        """Tedarikçi ve fatura genel bilgilerinin olduğu üst kısım"""
        header_group = QGroupBox("Fatura ve Tedarikçi Bilgileri")
        header_layout = QGridLayout()
        
        # --- Sol Taraf (Tedarikçi Bilgileri) ---
        header_layout.addWidget(QLabel("Tedarikçi:"), 0, 0)
        self.txt_tedarikci = QLineEdit()
        self.txt_tedarikci.setPlaceholderText("Tedarikçi adı girin")
        header_layout.addWidget(self.txt_tedarikci, 0, 1)
        
        # --- Sağ Taraf (Fatura Detayları) ---
        header_layout.addWidget(QLabel("Fatura No:"), 0, 2)
        self.txt_fatura_no = QLineEdit()
        self.txt_fatura_no.setReadOnly(True)
        self.txt_fatura_no.setStyleSheet(f"background-color: {self.color_border};")
        header_layout.addWidget(self.txt_fatura_no, 0, 3)
        
        header_layout.addWidget(QLabel("Tarih:"), 1, 2)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        header_layout.addWidget(self.date_edit, 1, 3)
        
        header_group.setLayout(header_layout)
        main_layout.addWidget(header_group)
    
    def init_table_section(self, main_layout):
        """Orta kısımdaki ürün listesi tablosu"""
        self.satirlar_table = QTableWidget()
        
        # Sütun Başlıkları
        columns = ["Malzeme Kodu", "Malzeme İsmi", "Miktar", "Birim", "Birim Fiyat (TL)", "KDV %", "Net Tutar", "Tutar"]
        self.satirlar_table.setColumnCount(len(columns))
        self.satirlar_table.setHorizontalHeaderLabels(columns)
        
        # Tablo Görünüm Ayarları
        self.satirlar_table.verticalHeader().setVisible(False)
        self.satirlar_table.setAlternatingRowColors(True)
        header = self.satirlar_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        main_layout.addWidget(self.satirlar_table)
    
    def load_default_rows(self):
        """Otomatik 10 satır yükle"""
        for i in range(10):
            self.add_row(["", "", "", "", "", "", "", ""])
    
    def add_row(self, data):
        """Tabloya yeni satır ekleme fonksiyonu"""
        row_position = self.satirlar_table.rowCount()
        self.satirlar_table.insertRow(row_position)
        
        for i, item in enumerate(data):
            if i == 3:  # Birim sütunu - ComboBox
                birim_combo = QComboBox()
                birim_combo.addItems(["", "ADET", "Kg", "Ton", "Litre", "Metre", "m²", "m³"])
                self.satirlar_table.setCellWidget(row_position, i, birim_combo)
            else:
                self.satirlar_table.setItem(row_position, i, QTableWidgetItem(item))
    
    def init_footer_section(self, main_layout):
        """Alt kısımdaki toplam bilgileri"""
        footer_widget = QWidget()
        footer_layout = QHBoxLayout()
        
        footer_layout.addStretch()
        
        # Sağ Alt: Toplam Hesaplamalar
        totals_group = QGroupBox("Genel Toplamlar")
        totals_layout = QFormLayout()
        
        self.txt_ara_toplam = QLineEdit("0,00")
        self.txt_ara_toplam.setReadOnly(True)
        self.txt_ara_toplam.setAlignment(Qt.AlignRight)
        
        self.txt_kdv_toplam = QLineEdit("0,00")
        self.txt_kdv_toplam.setReadOnly(True)
        self.txt_kdv_toplam.setAlignment(Qt.AlignRight)
        
        self.txt_genel_toplam = QLineEdit("0,00")
        self.txt_genel_toplam.setReadOnly(True)
        self.txt_genel_toplam.setStyleSheet("font-weight: bold; font-size: 14px; color: #233568;")
        self.txt_genel_toplam.setAlignment(Qt.AlignRight)
        
        totals_layout.addRow("Toplam Masraf:", self.txt_ara_toplam)
        totals_layout.addRow("Toplam KDV:", self.txt_kdv_toplam)
        totals_layout.addRow("NET TUTAR:", self.txt_genel_toplam)
        
        totals_group.setLayout(totals_layout)
        footer_layout.addWidget(totals_group)
        
        # Butonlar (Kaydet / Kapat)
        action_layout = QVBoxLayout()
        
        self.btn_save = QPushButton("Kaydet")
        self._style_btn(self.btn_save, self.color_success)
        self.btn_save.clicked.connect(self.on_save)
        
        self.btn_close = QPushButton("Kapat")
        self._style_btn(self.btn_close, self.color_danger)
        self.btn_close.clicked.connect(self.reject)
        
        action_layout.addWidget(self.btn_save)
        action_layout.addWidget(self.btn_close)
        footer_layout.addLayout(action_layout)
        
        footer_widget.setLayout(footer_layout)
        main_layout.addWidget(footer_widget)
    
    def on_table_key_press_wrapper(self, event):
        """Tablo tuş basımı event handler wrapper"""
        current_row = self.satirlar_table.currentRow()
        current_col = self.satirlar_table.currentColumn()
        
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Enter tuşuna basıldığında
            if current_col == 0:  # Malzeme Kodu sütunu
                self.search_and_fill_malzeme_by_kod(current_row)
                self.satirlar_table.setCurrentCell(current_row, 1)
                return
            elif current_col == 1:  # Malzeme İsmi sütunu
                self.search_and_fill_malzeme_by_ad(current_row)
                self.satirlar_table.setCurrentCell(current_row, 2)
                return
            else:
                # Diğer sütunlarda normal Enter davranışı
                if current_row == self.satirlar_table.rowCount() - 1:
                    self.add_row(["", "", "", "", "", "", "", ""])
                    self.satirlar_table.setCurrentCell(current_row + 1, 0)
                else:
                    self.satirlar_table.setCurrentCell(current_row + 1, current_col)
        else:
            # Diğer tuşlar için orijinal davranış
            QTableWidget.keyPressEvent(self.satirlar_table, event)
    
    def on_cell_changed(self, row, col):
        """Hücre değiştiğinde"""
        if self.is_auto_filling:
            return
        
        if col == 1:  # Malzeme İsmi sütunu
            self.on_malzeme_ismi_changed(row)
        
        if col not in [0, 1]:  # Malzeme kodu/isim hariç diğer sütunlar
            self.calculate_totals(row, col)
    
    def search_and_fill_malzeme_by_kod(self, row):
        """Malzeme koduna göre arama yap ve doldur"""
        try:
            kod_item = self.satirlar_table.item(row, 0)
            if not kod_item:
                return
            
            kod = kod_item.text().strip().upper()
            if not kod or len(kod) < 1:
                return
            
            from models.malzeme_model import MalzemeModel
            malzeme_model = MalzemeModel()
            malzeme = malzeme_model.get_by_kod(kod)
            
            if malzeme:
                self.fill_malzeme_data(row, malzeme, kod)
            else:
                self.show_malzeme_search_dialog(row, kod, search_type='kod')
        except Exception as e:
            print(f"Malzeme kodu arama hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def on_malzeme_ismi_changed(self, row):
        """Malzeme ismi değiştiğinde otomatik kod oluştur"""
        try:
            ad_item = self.satirlar_table.item(row, 1)
            if not ad_item:
                return
            
            ad = ad_item.text().strip()
            if not ad or len(ad) < 2:
                return
            
            kod_item = self.satirlar_table.item(row, 0)
            if not kod_item or kod_item.text().strip() == '':
                from models.malzeme_model import MalzemeModel
                malzeme_model = MalzemeModel()
                kod = malzeme_model._generate_unique_kod(ad)
                
                self.is_auto_filling = True
                self.satirlar_table.blockSignals(True)
                new_kod_item = QTableWidgetItem(str(kod))
                new_kod_item.setFlags(new_kod_item.flags() & ~Qt.ItemIsEditable)
                self.satirlar_table.setItem(row, 0, new_kod_item)
                self.satirlar_table.blockSignals(False)
                self.is_auto_filling = False
        except Exception as e:
            print(f"Otomatik kod oluşturma hatası: {e}")
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
    
    def search_and_fill_malzeme_by_ad(self, row):
        """Malzeme ismine göre arama yap ve doldur"""
        try:
            ad_item = self.satirlar_table.item(row, 1)
            if not ad_item:
                return
            
            ad = ad_item.text().strip()
            if not ad or len(ad) < 1:
                return
            
            from models.malzeme_model import MalzemeModel
            malzeme_model = MalzemeModel()
            results = malzeme_model.search(ad)
            
            malzeme = None
            for result in results:
                if result.get('ad', '').strip().lower() == ad.lower():
                    malzeme = result
                    break
            
            if malzeme:
                kod = malzeme.get('kod', '')
                self.fill_malzeme_data(row, malzeme, kod)
            elif len(results) == 1:
                malzeme = results[0]
                kod = malzeme.get('kod', '')
                self.fill_malzeme_data(row, malzeme, kod)
            elif len(results) > 1:
                self.show_malzeme_search_dialog(row, ad, search_type='ad', results=results)
            else:
                kod = malzeme_model._generate_unique_kod(ad)
                self.fill_malzeme_data_auto_kod(row, ad, kod)
        except Exception as e:
            print(f"Malzeme ismi arama hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def show_malzeme_search_dialog(self, row, search_text, search_type='kod', results=None):
        """Malzeme arama dialog'unu göster"""
        try:
            from views.stok_select_dialog import StokSelectDialog
            
            dialog = StokSelectDialog(self)
            
            if results:
                dialog.search_input.setText(search_text)
                dialog.on_search(search_text)
            
            if dialog.exec_() == QDialog.Accepted:
                selected_stok = dialog.get_selected_stok()
                if selected_stok:
                    kod = selected_stok.get('kod', '')
                    self.fill_malzeme_data(row, selected_stok, kod)
        except Exception as e:
            print(f"Malzeme arama dialog hatası: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Hata", f"Malzeme seçilirken hata oluştu:\n{e}")
    
    def fill_malzeme_data(self, row, malzeme, kod=None):
        """Malzeme verilerini satıra doldur"""
        try:
            self.is_auto_filling = True
            self.satirlar_table.blockSignals(True)
            
            malzeme_kodu = kod or malzeme.get('kod', '')
            malzeme_ad = malzeme.get('ad', '')
            birim = malzeme.get('birim', 'ADET')
            birim_fiyat = float(malzeme.get('current_buy_price', 0) or malzeme.get('birimFiyat', 0) or 0)
            kdv_orani = float(malzeme.get('kdvOrani', 18) or 18)
            
            # 0. Malzeme Kodu
            if malzeme_kodu:
                kod_item = QTableWidgetItem(str(malzeme_kodu))
                kod_item.setFlags(kod_item.flags() & ~Qt.ItemIsEditable)
                self.satirlar_table.setItem(row, 0, kod_item)
            
            # 1. Malzeme İsmi
            if malzeme_ad:
                self.satirlar_table.setItem(row, 1, QTableWidgetItem(str(malzeme_ad)))
            
            # 3. Birim - ComboBox'u güncelle
            birim_combo = self.satirlar_table.cellWidget(row, 3)
            if birim_combo:
                birim_upper = birim.upper() if birim else 'ADET'
                index = birim_combo.findText(birim_upper)
                if index >= 0:
                    birim_combo.setCurrentIndex(index)
                else:
                    birim_combo.addItem(birim_upper)
                    birim_combo.setCurrentText(birim_upper)
            
            # 4. Birim Fiyat
            if birim_fiyat > 0:
                birim_fiyat_text = f"{birim_fiyat:.2f}".replace('.', ',')
                self.satirlar_table.setItem(row, 4, QTableWidgetItem(birim_fiyat_text))
            
            # 5. KDV %
            self.satirlar_table.setItem(row, 5, QTableWidgetItem(str(int(kdv_orani))))
            
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
            
            self.calculate_totals(row, 0)
            
        except Exception as e:
            print(f"Malzeme doldurma hatası: {e}")
            import traceback
            traceback.print_exc()
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
    
    def fill_malzeme_data_auto_kod(self, row, ad, kod):
        """Malzeme isminden otomatik kod oluşturulduğunda sadece kod ve ismi doldur"""
        try:
            self.is_auto_filling = True
            self.satirlar_table.blockSignals(True)
            
            kod_item = QTableWidgetItem(str(kod))
            kod_item.setFlags(kod_item.flags() & ~Qt.ItemIsEditable)
            self.satirlar_table.setItem(row, 0, kod_item)
            
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
            
        except Exception as e:
            print(f"Otomatik kod doldurma hatası: {e}")
            import traceback
            traceback.print_exc()
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
    
    def calculate_totals(self, row, col):
        """Satır toplamlarını hesapla"""
        try:
            if self.is_auto_filling:
                return
            
            # Miktar, Birim Fiyat, KDV al
            miktar_item = self.satirlar_table.item(row, 2)
            fiyat_item = self.satirlar_table.item(row, 4)
            kdv_item = self.satirlar_table.item(row, 5)
            
            miktar = self.parse_float(miktar_item.text() if miktar_item else "0")
            fiyat = self.parse_float(fiyat_item.text() if fiyat_item else "0")
            kdv = self.parse_float(kdv_item.text() if kdv_item else "18")
            
            if miktar > 0 and fiyat > 0:
                net_tutar = miktar * fiyat
                kdv_tutari = net_tutar * (kdv / 100)
                tutar = net_tutar + kdv_tutari
                
                self.is_auto_filling = True
                self.satirlar_table.blockSignals(True)
                
                self.satirlar_table.setItem(row, 6, QTableWidgetItem(f"{net_tutar:.2f}".replace('.', ',')))
                self.satirlar_table.setItem(row, 7, QTableWidgetItem(f"{tutar:.2f}".replace('.', ',')))
                
                self.satirlar_table.blockSignals(False)
                self.is_auto_filling = False
                
                self.update_footer_totals()
        except Exception as e:
            print(f"Toplam hesaplama hatası: {e}")
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
    
    def update_footer_totals(self):
        """Footer'daki toplamları güncelle"""
        try:
            net_toplam = 0
            kdv_toplam = 0
            
            for row in range(self.satirlar_table.rowCount()):
                net_item = self.satirlar_table.item(row, 6)
                tutar_item = self.satirlar_table.item(row, 7)
                
                if net_item and tutar_item:
                    net = self.parse_float(net_item.text())
                    tutar = self.parse_float(tutar_item.text())
                    net_toplam += net
                    kdv_toplam += (tutar - net)
            
            self.txt_ara_toplam.setText(f"{net_toplam:.2f}".replace('.', ','))
            self.txt_kdv_toplam.setText(f"{kdv_toplam:.2f}".replace('.', ','))
            self.txt_genel_toplam.setText(f"{net_toplam + kdv_toplam:.2f}".replace('.', ','))
        except Exception as e:
            print(f"Footer toplam güncelleme hatası: {e}")
    
    def parse_float(self, text):
        """Metni float'a çevir (virgül/nokta desteği)"""
        if not text:
            return 0.0
        try:
            return float(text.replace(',', '.'))
        except:
            return 0.0
    
    def on_cell_double_clicked(self, row, col):
        """Hücreye çift tıklandığında"""
        if col == 0 or col == 1:
            # Stok seçim dialog'unu aç
            self.show_malzeme_search_dialog(row, "")
    
    def generate_fatura_no(self):
        """Fatura numarasını otomatik oluştur"""
        from models.purchase_invoice_model import PurchaseInvoiceModel
        try:
            model = PurchaseInvoiceModel()
            fatura_no = model._generate_fatura_no()
            self.txt_fatura_no.setText(fatura_no)
            return fatura_no
        except Exception as e:
            from datetime import datetime
            year = datetime.now().year
            fatura_no = f"AL{year}0000001"
            self.txt_fatura_no.setText(fatura_no)
            return fatura_no
    
    def load_data(self):
        """Düzenleme modunda verileri yükle"""
        if not self.invoice_data:
            return
        # TODO: Düzenleme modu implementasyonu
        pass
    
    def get_data(self) -> dict:
        """Form verilerini al"""
        items = []
        
        for row in range(self.satirlar_table.rowCount()):
            kod_item = self.satirlar_table.item(row, 0)
            ad_item = self.satirlar_table.item(row, 1)
            miktar_item = self.satirlar_table.item(row, 2)
            birim_combo = self.satirlar_table.cellWidget(row, 3)
            fiyat_item = self.satirlar_table.item(row, 4)
            kdv_item = self.satirlar_table.item(row, 5)
            
            kod = kod_item.text().strip() if kod_item else ""
            ad = ad_item.text().strip() if ad_item else ""
            miktar = self.parse_float(miktar_item.text() if miktar_item else "0")
            birim = birim_combo.currentText() if birim_combo else ""
            fiyat = self.parse_float(fiyat_item.text() if fiyat_item else "0")
            kdv = self.parse_float(kdv_item.text() if kdv_item else "18")
            
            if kod and ad and miktar > 0 and fiyat > 0:
                # Malzeme ID'sini bul
                from models.malzeme_model import MalzemeModel
                malzeme_model = MalzemeModel()
                malzeme = malzeme_model.get_by_kod(kod)
                
                if malzeme:
                    net_tutar = miktar * fiyat
                    kdv_tutari = net_tutar * (kdv / 100)
                    tutar = net_tutar + kdv_tutari
                    
                    items.append({
                        'malzeme_id': malzeme['id'],
                        'malzeme_kodu': kod,
                        'malzeme_adi': ad,
                        'miktar': miktar,
                        'birim': birim,
                        'birim_fiyat': fiyat,
                        'kdv_orani': kdv,
                        'net_tutar': round(net_tutar, 2),
                        'tutar': round(tutar, 2)
                    })
        
        fatura_no = self.txt_fatura_no.text().strip()
        if not fatura_no:
            fatura_no = self.generate_fatura_no()
        
        return {
            'fatura_no': fatura_no,
            'fatura_tarihi': self.date_edit.date().toString("yyyy-MM-dd"),
            'tedarikci_unvani': self.txt_tedarikci.text().strip(),
            'items': items,
            'aciklama': ''
        }
    
    def on_save(self):
        """Kaydet butonuna tıklandığında"""
        if hasattr(self, 'on_save_callback') and self.on_save_callback:
            self.on_save_callback()
        else:
            # Eğer callback yoksa direkt kabul et
            self.accept()
    
    def set_callbacks(self, on_save=None):
        """Callback'leri ayarla"""
        self.on_save_callback = on_save
    
    def accept(self):
        """Dialog kabul edildiğinde"""
        super().accept()
    
    def on_temizle(self):
        """Formu temizle (Controller'dan çağrılır)"""
        # Tüm satırları temizle
        self.satirlar_table.setRowCount(0)
        # 10 satır yükle
        self.load_default_rows()
        # Tedarikçi alanını temizle
        self.txt_tedarikci.clear()
        # Tarihi bugüne ayarla
        self.date_edit.setDate(QDate.currentDate())
        # Fatura numarasını yeniden oluştur
        self.generate_fatura_no()
        # Toplamları sıfırla
        self.txt_ara_toplam.setText("0,00")
        self.txt_kdv_toplam.setText("0,00")
        self.txt_genel_toplam.setText("0,00")
