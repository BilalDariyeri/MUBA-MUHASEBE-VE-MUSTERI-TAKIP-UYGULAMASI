"""
Fatura Form View - Fatura form görünümü
MVC View katmanı - Sadece UI işlemleri
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QMessageBox, QDialogButtonBox, QDoubleSpinBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QGroupBox,
    QLabel, QDateEdit, QTimeEdit, QRadioButton, QButtonGroup, QTabWidget,
    QWidget, QGridLayout
)
from PyQt5.QtCore import Qt, QDate, QTime, QDateTime
from PyQt5.QtGui import QFont, QKeyEvent
from datetime import datetime


class FaturaFormView(QDialog):
    """Fatura form görünümü - View katmanı"""
    
    def __init__(self, parent=None, fatura_data=None):
        super().__init__(parent)
        self.fatura_data = fatura_data
        self.is_edit_mode = fatura_data is not None
        self.setWindowTitle("Satış Faturası - Fatura Detayları")
        self.setModal(True)
        self._init_colors()
        
        # Tam ekran yap
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.showMaximized()
        
        self.cari_hesaplar = []
        self.selected_cari_id = None
        self.selected_cari_kodu = None  # Cari hesap kodu için ayrı değişken
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
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"
        
    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"""
            QDialog {{ background: {self.color_bg}; }}
            QGroupBox {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                color: {self.color_text};
                font-weight: 600;
            }}
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
                border: 1px solid {self.color_border};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {self.color_primary};
            }}
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
            QPushButton {{
                min-height: 32px;
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)
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
        # Enter tuşu ile yeni satır ekleme
        self.satirlar_table.keyPressEvent = self.on_table_key_press
        
        # Otomatik doldurma için flag (sonsuz döngüyü önlemek için)
        self.is_auto_filling = False
        
        # LOGO mantığı: Enter'a basıldığında arama yapılacak
        # Her karakter değişikliğinde değil, sadece Enter'da
    
    def init_header_section(self, main_layout):
        """Cari hesap ve fatura genel bilgilerinin olduğu üst kısım"""
        header_group = QGroupBox("Fatura ve Cari Bilgileri")
        header_layout = QGridLayout()
        
        # --- Sol Taraf (Cari Bilgileri) ---
        header_layout.addWidget(QLabel("Cari Kodu:"), 0, 0)
        self.txt_cari_kodu = QLineEdit()
        self.txt_cari_kodu.setPlaceholderText("120 00 ...")
        header_layout.addWidget(self.txt_cari_kodu, 0, 1)
        
        header_layout.addWidget(QLabel("Unvanı:"), 1, 0)
        unvan_layout = QHBoxLayout()
        self.txt_unvan = QLineEdit()
        self.txt_unvan.setPlaceholderText("Örnek Müşteri A.Ş.")
        self.txt_unvan.setReadOnly(True)
        self.txt_unvan.setStyleSheet("background-color: #e9ecef;")
        btn_unvan_sec = QPushButton("...")
        btn_unvan_sec.setMaximumWidth(30)
        btn_unvan_sec.clicked.connect(self.select_cari_hesap)
        unvan_layout.addWidget(self.txt_unvan)
        unvan_layout.addWidget(btn_unvan_sec)
        header_layout.addLayout(unvan_layout, 1, 1)
        
        header_layout.addWidget(QLabel("Ödeme Planı:"), 2, 0)
        self.cmb_odeme = QComboBox()
        self.cmb_odeme.addItems(["120 Gün", "Peşin", "30 Gün", "60 Gün"])
        header_layout.addWidget(self.cmb_odeme, 2, 1)
        
        # --- Sağ Taraf (Fatura Detayları) ---
        header_layout.addWidget(QLabel("Tarih:"), 0, 2)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        header_layout.addWidget(self.date_edit, 0, 3)
        
        header_layout.addWidget(QLabel("Fatura Tipi:"), 1, 2)
        self.cmb_tip = QComboBox()
        self.cmb_tip.addItems(["Satış Faturası", "İade Faturası", "Proforma", "e-Fatura", "e-Arşiv"])
        header_layout.addWidget(self.cmb_tip, 1, 3)
        
        header_layout.addWidget(QLabel("Ambar:"), 2, 2)
        self.cmb_ambar = QComboBox()
        self.cmb_ambar.addItems(["Merkez Depo", "Şube 1", "Şube 2", "000, Merkez"])
        header_layout.addWidget(self.cmb_ambar, 2, 3)
        
        header_group.setLayout(header_layout)
        main_layout.addWidget(header_group)
    
    def init_table_section(self, main_layout):
        """Orta kısımdaki ürün listesi tablosu"""
        self.satirlar_table = QTableWidget()
        
        # Sütun Başlıkları - Malzeme Kodu ve Malzeme İsmi eklendi
        columns = ["Malzeme Kodu", "Malzeme İsmi", "Miktar", "Birim", "Açıklama", "Birim Fiyat (TL)", "Döviz Fiyatı", "Döviz Türü", "KDV %", "Tutar", "Net Tutar"]
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
            self.add_row(["", "", "", "", "", "", "", "", "", "", ""])
    
    def add_row(self, data):
        """Tabloya yeni satır ekleme fonksiyonu"""
        row_position = self.satirlar_table.rowCount()
        self.satirlar_table.insertRow(row_position)
        
        for i, item in enumerate(data):
            if i == 3:  # Birim sütunu - ComboBox (yeni sıra: 3)
                birim_combo = QComboBox()
                birim_combo.addItems(["", "ADET", "Kg", "Ton", "Litre", "Metre", "m²", "m³"])
                self.satirlar_table.setCellWidget(row_position, i, birim_combo)
            elif i == 7:  # Döviz Türü sütunu - ComboBox (yeni sıra: 7)
                doviz_combo = QComboBox()
                doviz_combo.addItems(["", "TL", "USD", "EUR"])
                doviz_combo.currentTextChanged.connect(lambda text, row=row_position: self.on_doviz_changed(row, text))
                self.satirlar_table.setCellWidget(row_position, i, doviz_combo)
            else:
                self.satirlar_table.setItem(row_position, i, QTableWidgetItem(item))
        
    
    def init_footer_section(self, main_layout):
        """Alt kısımdaki döviz ve toplam bilgileri"""
        footer_widget = QWidget()
        footer_layout = QHBoxLayout()
        
        # Sol Alt: Para Birimi Seçimi
        currency_group = QGroupBox("Kullanılacak Para Birimi")
        currency_layout = QVBoxLayout()
        
        self.r1 = QRadioButton("Yerel Para Birimi (TL)")
        self.r1.setChecked(True)
        self.r2 = QRadioButton("İşlem Döviz")
        self.r3 = QRadioButton("EURO / USD")
        
        currency_layout.addWidget(self.r1)
        currency_layout.addWidget(self.r2)
        currency_layout.addWidget(self.r3)
        
        currency_group.setLayout(currency_layout)
        footer_layout.addWidget(currency_group)
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
        self.txt_genel_toplam.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.txt_genel_toplam.setAlignment(Qt.AlignRight)
        
        totals_layout.addRow("Toplam Masraf:", self.txt_ara_toplam)
        totals_layout.addRow("Toplam KDV:", self.txt_kdv_toplam)
        totals_layout.addRow("NET TUTAR:", self.txt_genel_toplam)
        
        totals_group.setLayout(totals_layout)
        footer_layout.addWidget(totals_group)
        
        # Butonlar (Kaydet / Kapat)
        action_layout = QVBoxLayout()
        
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn_save.clicked.connect(self.on_save)
        
        self.btn_close = QPushButton("Kapat")
        self.btn_close.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.btn_close.clicked.connect(self.reject)
        
        action_layout.addWidget(self.btn_save)
        action_layout.addWidget(self.btn_close)
        footer_layout.addLayout(action_layout)
        
        footer_widget.setLayout(footer_layout)
        main_layout.addWidget(footer_widget)
    
    def on_table_key_press(self, event):
        """Tablo tuş basımı event handler"""
        from PyQt5.QtCore import Qt
        current_row = self.satirlar_table.currentRow()
        current_col = self.satirlar_table.currentColumn()
        
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Enter tuşuna basıldığında
            # LOGO mantığı: Malzeme kodu veya ismi sütunundaysa arama yap
            if current_col == 0:  # Malzeme Kodu sütunu
                self.search_and_fill_malzeme_by_kod(current_row)
                # Sonraki sütuna geç
                self.satirlar_table.setCurrentCell(current_row, 1)
                return
            elif current_col == 1:  # Malzeme İsmi sütunu
                self.search_and_fill_malzeme_by_ad(current_row)
                # Sonraki sütuna geç
                self.satirlar_table.setCurrentCell(current_row, 2)
                return
            else:
                # Diğer sütunlarda normal Enter davranışı
                # Eğer son satırdaysak yeni satır ekle
                if current_row == self.satirlar_table.rowCount() - 1:
                    self.add_row(["", "", "", "", "", "", "", "", "", "", ""])
                    # Yeni satıra geç
                    self.satirlar_table.setCurrentCell(current_row + 1, 0)
                else:
                    # Bir sonraki satıra geç
                    self.satirlar_table.setCurrentCell(current_row + 1, current_col)
        else:
            # Diğer tuşlar için varsayılan davranış
            QTableWidget.keyPressEvent(self.satirlar_table, event)
    
    def on_cell_changed(self, row, col):
        """Hücre değiştiğinde"""
        # Otomatik doldurma sırasında tekrar tetiklenmesin
        if self.is_auto_filling:
            return
        
        # Malzeme ismi değiştiğinde otomatik kod oluştur
        if col == 1:  # Malzeme İsmi sütunu
            self.on_malzeme_ismi_changed(row)
        
        # LOGO mantığı: Sadece miktar, fiyat gibi hesaplanabilir alanlar değiştiğinde toplam hesapla
        # Malzeme kodu/isim değişikliklerinde Enter'a basılana kadar bekle
        if col not in [0, 1]:  # Malzeme kodu/isim hariç diğer sütunlar
            self.calculate_totals(row, col)
    
    def search_and_fill_malzeme_by_kod(self, row):
        """LOGO mantığı: Malzeme koduna göre arama yap ve doldur"""
        try:
            kod_item = self.satirlar_table.item(row, 0)
            if not kod_item:
                return
            
            kod = kod_item.text().strip().upper()
            if not kod or len(kod) < 1:
                return
            
            # Veritabanında tam eşleşme ara
            from models.malzeme_model import MalzemeModel
            malzeme_model = MalzemeModel()
            malzeme = malzeme_model.get_by_kod(kod)
            
            if malzeme:
                # Tam eşleşme bulundu, otomatik doldur
                self.fill_malzeme_data(row, malzeme, kod)
            else:
                # Tam eşleşme yok, dialog aç
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
            if not ad or len(ad) < 2:  # En az 2 karakter
                return
            
            # Eğer kod sütunu boşsa veya read-only değilse otomatik kod oluştur
            kod_item = self.satirlar_table.item(row, 0)
            if not kod_item or kod_item.text().strip() == '':
                from models.malzeme_model import MalzemeModel
                malzeme_model = MalzemeModel()
                kod = malzeme_model._generate_unique_kod(ad)
                
                # Kod oluştur ve read-only yap
                self.is_auto_filling = True
                self.satirlar_table.blockSignals(True)
                new_kod_item = QTableWidgetItem(str(kod))
                new_kod_item.setFlags(new_kod_item.flags() & ~Qt.ItemIsEditable)  # Read-only yap
                self.satirlar_table.setItem(row, 0, new_kod_item)
                self.satirlar_table.blockSignals(False)
                self.is_auto_filling = False
        except Exception as e:
            print(f"Otomatik kod oluşturma hatası: {e}")
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
    
    def search_and_fill_malzeme_by_ad(self, row):
        """LOGO mantığı: Malzeme ismine göre arama yap ve doldur - Otomatik kod oluştur"""
        try:
            ad_item = self.satirlar_table.item(row, 1)
            if not ad_item:
                return
            
            ad = ad_item.text().strip()
            if not ad or len(ad) < 1:
                return
            
            # Veritabanında ara
            from models.malzeme_model import MalzemeModel
            malzeme_model = MalzemeModel()
            results = malzeme_model.search(ad)
            
            # Tam eşleşme ara (büyük/küçük harf duyarsız)
            malzeme = None
            for result in results:
                if result.get('ad', '').strip().lower() == ad.lower():
                    malzeme = result
                    break
            
            if malzeme:
                # Tam eşleşme bulundu, otomatik doldur
                kod = malzeme.get('kod', '')
                self.fill_malzeme_data(row, malzeme, kod)
            elif len(results) == 1:
                # Tek sonuç varsa otomatik doldur
                malzeme = results[0]
                kod = malzeme.get('kod', '')
                self.fill_malzeme_data(row, malzeme, kod)
            elif len(results) > 1:
                # Birden fazla sonuç varsa dialog aç
                self.show_malzeme_search_dialog(row, ad, search_type='ad', results=results)
            else:
                # Sonuç yok - Otomatik kod oluştur ve doldur
                kod = malzeme_model._generate_unique_kod(ad)
                # Sadece kod ve ismi doldur, diğer bilgileri boş bırak
                self.fill_malzeme_data_auto_kod(row, ad, kod)
        except Exception as e:
            print(f"Malzeme ismi arama hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def show_malzeme_search_dialog(self, row, search_text, search_type='kod', results=None):
        """Malzeme arama dialog'unu göster (LOGO mantığı)"""
        try:
            from views.stok_select_dialog import StokSelectDialog
            
            dialog = StokSelectDialog(self)
            
            # Eğer önceden arama sonuçları varsa, dialog'a gönder
            if results:
                # Dialog'un search input'una yaz ve filtrele
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
            
            # Malzeme bilgilerini al
            malzeme_kodu = kod or malzeme.get('kod', '')
            malzeme_ad = malzeme.get('ad', '')
            birim = malzeme.get('birim', 'ADET')
            # Birim fiyatı farklı alanlardan kontrol et
            birim_fiyat = float(
                malzeme.get('birimFiyat', 0) or 
                malzeme.get('birim_fiyat', 0) or 
                malzeme.get('current_sell_price', 0) or 
                malzeme.get('satis_fiyati', 0) or 
                0
            )
            kdv_orani = float(malzeme.get('kdvOrani', 18) or malzeme.get('kdv_orani', 18) or 18)
            
            # 0. Malzeme Kodu - Otomatik oluşturulan kod (read-only değil, ama otomatik dolduruluyor)
            if malzeme_kodu:
                kod_item = QTableWidgetItem(str(malzeme_kodu))
                kod_item.setFlags(kod_item.flags() & ~Qt.ItemIsEditable)  # Read-only yap
                self.satirlar_table.setItem(row, 0, kod_item)
            
            # 1. Malzeme İsmi
            if malzeme_ad:
                self.satirlar_table.setItem(row, 1, QTableWidgetItem(str(malzeme_ad)))
            
            # 2. Miktar - BOŞ BIRAK (kullanıcı girecek)
            # Miktarı değiştirmiyoruz
            
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
            
            # 4. Açıklama - boş bırakılabilir
            
            # 5. Birim Fiyat (TL) - Her zaman göster (0 olsa bile)
            birim_fiyat_text = f"{birim_fiyat:.2f}".replace('.', ',')
            self.satirlar_table.setItem(row, 5, QTableWidgetItem(birim_fiyat_text))
            
            # 6. Döviz Fiyatı - Başlangıçta TL fiyatı ile aynı
            self.satirlar_table.setItem(row, 6, QTableWidgetItem(f"{birim_fiyat_text} ₺"))
            
            # 7. Döviz Türü - TL varsayılan
            doviz_combo = self.satirlar_table.cellWidget(row, 7)
            if doviz_combo:
                doviz_combo.setCurrentText("TL")
            
            # 8. KDV %
            self.satirlar_table.setItem(row, 8, QTableWidgetItem(str(int(kdv_orani))))
            
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
            
            # Toplamları hesapla (miktar varsa)
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
            
            # 0. Malzeme Kodu - Otomatik oluşturulan kod (read-only)
            kod_item = QTableWidgetItem(str(kod))
            kod_item.setFlags(kod_item.flags() & ~Qt.ItemIsEditable)  # Read-only yap
            self.satirlar_table.setItem(row, 0, kod_item)
            
            # 1. Malzeme İsmi zaten dolu (kullanıcı yazdı)
            # Diğer alanlar boş kalacak, kullanıcı dolduracak
            
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
            
        except Exception as e:
            print(f"Otomatik kod doldurma hatası: {e}")
            import traceback
            traceback.print_exc()
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
    
    def on_cell_double_clicked(self, row, col):
        """Hücre çift tıklandığında"""
        if col == 0 or col == 1:  # Malzeme Kodu veya İsmi sütunu
            self.select_stok(row)
    
    def on_doviz_changed(self, row, doviz_turu):
        """Döviz türü değiştiğinde fiyatı hesapla"""
        try:
            birim_fiyat_item = self.satirlar_table.item(row, 5)  # Birim Fiyat (TL) - yeni sıra: 5
            if not birim_fiyat_item:
                return
            
            birim_fiyat_text = birim_fiyat_item.text().replace(',', '.').replace(' TL', '').replace(' ₺', '').strip()
            if not birim_fiyat_text:
                return
            
            try:
                birim_fiyat_tl = float(birim_fiyat_text)
            except:
                return
            
            # Döviz kurları (basit örnek - gerçek uygulamada API'den alınmalı)
            kur_usd = 34.0  # 1 USD = 34 TL
            kur_eur = 37.0  # 1 EUR = 37 TL
            
            doviz_fiyat = 0
            if doviz_turu == "USD":
                doviz_fiyat = birim_fiyat_tl / kur_usd
            elif doviz_turu == "EUR":
                doviz_fiyat = birim_fiyat_tl / kur_eur
            elif doviz_turu == "TL":
                doviz_fiyat = birim_fiyat_tl
            
            # Döviz fiyatını göster (kısaltma ile)
            if doviz_fiyat > 0:
                if doviz_turu == "USD":
                    doviz_text = f"{doviz_fiyat:.2f} $"
                elif doviz_turu == "EUR":
                    doviz_text = f"{doviz_fiyat:.2f} €"
                else:
                    doviz_text = f"{doviz_fiyat:.2f} ₺"
                self.satirlar_table.setItem(row, 6, QTableWidgetItem(doviz_text))  # Döviz Fiyatı - yeni sıra: 6
        except Exception as e:
            print(f"Döviz fiyatı hesaplama hatası: {e}")
    
    def select_stok(self, row):
        """Stok seç"""
        try:
            from views.stok_select_dialog import StokSelectDialog
            from models.malzeme_model import MalzemeModel
            
            dialog = StokSelectDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                selected_stok = dialog.get_selected_stok()
                if selected_stok:
                    # Signal'i geçici olarak blokla (setItem çağrıları sırasında)
                    self.satirlar_table.blockSignals(True)
                    
                    # Tüm stok özelliklerini al
                    stok_ad = selected_stok.get('ad', '')
                    stok_kodu = selected_stok.get('kod', '')  # VERİTABANINDAKİ MEVCUT KODU KULLAN
                    birim = selected_stok.get('birim', 'ADET')
                    # Birim fiyatı farklı alanlardan kontrol et
                    birim_fiyat = float(
                        selected_stok.get('birimFiyat', 0) or 
                        selected_stok.get('birim_fiyat', 0) or 
                        selected_stok.get('current_sell_price', 0) or 
                        selected_stok.get('satis_fiyati', 0) or 
                        0
                    )
                    kdv_orani = float(selected_stok.get('kdvOrani', 18) or selected_stok.get('kdv_orani', 18) or 18)
                    
                    # Eğer kod yoksa (eski kayıtlar için) otomatik oluştur
                    if not stok_kodu:
                        malzeme_model = MalzemeModel()
                        stok_kodu = malzeme_model._generate_unique_kod(stok_ad)
                    
                    # Stok bilgilerini satıra doldur
                    # 0. Malzeme Kodu (veritabanındaki mevcut kod) - Read-only
                    kod_item = QTableWidgetItem(str(stok_kodu))
                    kod_item.setFlags(kod_item.flags() & ~Qt.ItemIsEditable)  # Read-only yap
                    self.satirlar_table.setItem(row, 0, kod_item)
                    
                    # 1. Malzeme İsmi
                    self.satirlar_table.setItem(row, 1, QTableWidgetItem(str(stok_ad)))
                    
                    # 2. Miktar - BOŞ BIRAK (kullanıcı girecek)
                    # Miktarı otomatik doldurma, kullanıcı kendisi girecek
                    
                    # 3. Birim - ComboBox'u güncelle
                    birim_combo = self.satirlar_table.cellWidget(row, 3)
                    if birim_combo:
                        # Birim değerini büyük harfe çevir (ADET, KG, vb.)
                        birim_upper = birim.upper() if birim else 'ADET'
                        index = birim_combo.findText(birim_upper)
                        if index >= 0:
                            birim_combo.setCurrentIndex(index)
                        else:
                            # Eğer birim listede yoksa, ekle ve seç
                            birim_combo.addItem(birim_upper)
                            birim_combo.setCurrentText(birim_upper)
                    
                    # 4. Açıklama (boş bırakılabilir)
                    # Açıklama sütunu boş kalabilir
                    
                    # 5. Birim Fiyat (TL) - Her zaman göster (0 olsa bile)
                    birim_fiyat_text = f"{birim_fiyat:.2f}".replace('.', ',')
                    self.satirlar_table.setItem(row, 5, QTableWidgetItem(birim_fiyat_text))
                    
                    # 6. Döviz Fiyatı - Başlangıçta TL fiyatı ile aynı (kısaltma ile)
                    self.satirlar_table.setItem(row, 6, QTableWidgetItem(f"{birim_fiyat_text} ₺"))
                    
                    # 8. KDV %
                    self.satirlar_table.setItem(row, 8, QTableWidgetItem(str(int(kdv_orani))))
                    
                    # 7. Döviz Türü - TL varsayılan
                    doviz_combo = self.satirlar_table.cellWidget(row, 7)
                    if doviz_combo:
                        doviz_combo.setCurrentText("TL")
                    
                    # 8. KDV %
                    self.satirlar_table.setItem(row, 8, QTableWidgetItem(str(int(kdv_orani))))
                    
                    # Signal bloğunu kaldır
                    self.satirlar_table.blockSignals(False)
                    
                    # Tutar ve Net Tutar otomatik hesaplanacak (miktar girildiğinde)
                    # Toplamları hesapla
                    self.calculate_totals(row, 0)
                    
        except Exception as e:
            print(f"select_stok hatası: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", f"Stok seçilirken hata oluştu:\n{e}")
            # Signal bloğunu kaldır (hata durumunda da)
            try:
                self.satirlar_table.blockSignals(False)
            except:
                pass
    
    def select_cari_hesap(self):
        """Cari hesap seç"""
        from views.cari_hesap_select_dialog import CariHesapSelectDialog
        
        dialog = CariHesapSelectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_cari = dialog.get_selected_cari()
            if selected_cari:
                # Tüm cari bilgilerini doldur
                cari_kodu = selected_cari.get('kodu', '')
                # Fatura numarasını koru, sadece cari kodunu sakla
                # txt_cari_kodu alanı fatura numarası için kullanılıyor, cari kodunu saklamıyoruz
                self.txt_unvan.setText(selected_cari.get('unvani', ''))
                self.selected_cari_id = selected_cari.get('id')
                self.selected_cari_kodu = cari_kodu  # Cari kodunu sakla (get_data'da kullanılacak)
                
                # Ödeme planını cari hesaptan al (varsa)
                odeme_plan = selected_cari.get('odemePlani', '')
                if odeme_plan:
                    index = self.cmb_odeme.findText(odeme_plan)
                    if index >= 0:
                        self.cmb_odeme.setCurrentIndex(index)
    
    def calculate_totals(self, row=None, col=None):
        """Toplamları hesapla"""
        try:
            # Otomatik doldurma sırasında tekrar tetiklenmesin
            if self.is_auto_filling:
                return
            
            # Signal'i geçici olarak blokla (sonsuz döngüyü önlemek için)
            self.satirlar_table.blockSignals(True)
            
            toplam = 0
            toplam_kdv = 0
            
            for r in range(self.satirlar_table.rowCount()):
                miktar_item = self.satirlar_table.item(r, 2)  # Miktar - yeni sıra: 2
                birim_fiyat_item = self.satirlar_table.item(r, 5)  # Birim Fiyat (TL) - yeni sıra: 5
                kdv_item = self.satirlar_table.item(r, 8)  # KDV % - yeni sıra: 8
                
                if miktar_item and birim_fiyat_item:
                    miktar_text = miktar_item.text().replace(',', '.').strip()
                    birim_fiyat_text = birim_fiyat_item.text().replace(',', '.').replace(' TL', '').replace(' ₺', '').strip()
                    
                    if miktar_text and birim_fiyat_text:
                        try:
                            miktar = float(miktar_text) if miktar_text else 0
                            birim_fiyat = float(birim_fiyat_text) if birim_fiyat_text else 0
                            tutar = miktar * birim_fiyat
                            
                            # KDV hesapla
                            kdv_orani = 0
                            if kdv_item and kdv_item.text():
                                try:
                                    kdv_orani = float(kdv_item.text().replace(',', '.').strip())
                                except:
                                    kdv_orani = 0
                            
                            kdv = tutar * (kdv_orani / 100)
                            # tutar = KDV hariç tutar (net tutar)
                            # kdv = KDV tutarı
                            # tutar_kdv_dahil = KDV dahil tutar
                            tutar_kdv_dahil = tutar + kdv
                            
                            # Tutar (KDV hariç) ve Net Tutar (KDV dahil) sütunlarını güncelle (yeni sıra: 9 ve 10)
                            self.satirlar_table.setItem(r, 9, QTableWidgetItem(f"{tutar:.2f} ₺".replace('.', ',')))
                            self.satirlar_table.setItem(r, 10, QTableWidgetItem(f"{tutar_kdv_dahil:.2f} ₺".replace('.', ',')))
                            
                            toplam += tutar  # KDV hariç toplam
                            toplam_kdv += kdv  # KDV tutarı
                        except Exception as e:
                            print(f"Hesaplama hatası (satır {r}): {e}")
                            pass
            
            # Signal bloğunu kaldır
            self.satirlar_table.blockSignals(False)
            
            # Toplamları güncelle
            self.txt_ara_toplam.setText(f"{toplam:.2f}".replace('.', ','))
            self.txt_kdv_toplam.setText(f"{toplam_kdv:.2f}".replace('.', ','))
            self.txt_genel_toplam.setText(f"{(toplam + toplam_kdv):.2f}".replace('.', ','))
        except Exception as e:
            print(f"calculate_totals genel hatası: {e}")
            import traceback
            traceback.print_exc()
            # Signal bloğunu kaldır (hata durumunda da)
            try:
                self.satirlar_table.blockSignals(False)
            except:
                pass
    
    def load_data(self):
        """Düzenleme modunda veriyi yükle"""
        if not self.fatura_data:
            return
        
        try:
            self.is_auto_filling = True
            self.satirlar_table.blockSignals(True)
            
            # Fatura numarası
            fatura_no = self.fatura_data.get('faturaNo', '')
            self.txt_cari_kodu.setText(fatura_no)
            
            # Tarih
            tarih = self.fatura_data.get('tarih', '')
            if tarih:
                try:
                    from datetime import datetime
                    tarih_obj = datetime.strptime(tarih, '%Y-%m-%d')
                    self.date_edit.setDate(QDate(tarih_obj.year, tarih_obj.month, tarih_obj.day))
                except:
                    pass
            
            # Fatura tipi
            fatura_tipi = self.fatura_data.get('faturaTipi', '')
            if fatura_tipi:
                index = self.cmb_tip.findText(fatura_tipi)
                if index >= 0:
                    self.cmb_tip.setCurrentIndex(index)
            
            # Cari hesap bilgileri
            cari_hesap = self.fatura_data.get('cariHesap', {})
            if isinstance(cari_hesap, dict):
                self.txt_unvan.setText(cari_hesap.get('unvani', ''))
                self.selected_cari_id = cari_hesap.get('id')
                self.selected_cari_kodu = cari_hesap.get('kodu', '')
            
            # Satırları yükle
            satirlar = self.fatura_data.get('satirlar', [])
            if satirlar and isinstance(satirlar, list):
                # Mevcut satırları temizle
                self.satirlar_table.setRowCount(0)
                
                # Her satırı yükle
                for satir in satirlar:
                    if not satir:
                        continue
                    
                    # Satır verilerini hazırla
                    malzeme_kodu = satir.get('stokKodu') or satir.get('malzemeKodu') or ''
                    malzeme_ismi = satir.get('malzemeIsmi') or satir.get('aciklama') or ''
                    miktar = satir.get('miktar', 0)
                    birim = satir.get('birim', '')
                    aciklama = satir.get('aciklama', '')
                    birim_fiyat = float(satir.get('birimFiyat', 0) or 0)
                    doviz_fiyat = float(satir.get('dovizFiyat', 0) or 0)
                    doviz_turu = satir.get('dovizTuru', 'TL')
                    kdv_orani = float(satir.get('kdvOrani', 0) or 0)
                    tutar = float(satir.get('tutar', 0) or 0)
                    net_tutar = float(satir.get('netTutar', 0) or 0)
                    
                    # Miktar formatı
                    if birim.upper() in ['ADET', 'ADT']:
                        miktar_text = str(int(miktar)) if miktar else ''
                    else:
                        miktar_text = f"{miktar:.2f}".replace('.', ',') if miktar else ''
                    
                    # Birim fiyat formatı
                    birim_fiyat_text = f"{birim_fiyat:.2f}".replace('.', ',') if birim_fiyat > 0 else ''
                    
                    # Döviz fiyat formatı
                    doviz_fiyat_text = ''
                    if doviz_fiyat > 0:
                        if doviz_turu == 'USD':
                            doviz_fiyat_text = f"{doviz_fiyat:.2f} $"
                        elif doviz_turu == 'EUR':
                            doviz_fiyat_text = f"{doviz_fiyat:.2f} €"
                        else:
                            doviz_fiyat_text = f"{doviz_fiyat:.2f} ₺"
                    
                    # Tutar formatı
                    tutar_text = f"{tutar:.2f} ₺".replace('.', ',') if tutar > 0 else ''
                    net_tutar_text = f"{net_tutar:.2f} ₺".replace('.', ',') if net_tutar > 0 else ''
                    
                    # Satır ekle
                    row_data = [
                        str(malzeme_kodu),      # 0: Malzeme Kodu
                        str(malzeme_ismi),      # 1: Malzeme İsmi
                        miktar_text,             # 2: Miktar
                        birim,                   # 3: Birim (ComboBox)
                        str(aciklama),           # 4: Açıklama
                        birim_fiyat_text,        # 5: Birim Fiyat
                        doviz_fiyat_text,        # 6: Döviz Fiyatı
                        doviz_turu,              # 7: Döviz Türü (ComboBox)
                        str(int(kdv_orani)),     # 8: KDV %
                        tutar_text,              # 9: Tutar
                        net_tutar_text           # 10: Net Tutar
                    ]
                    self.add_row(row_data)
                    
                    # Birim ComboBox'u güncelle
                    row = self.satirlar_table.rowCount() - 1
                    birim_combo = self.satirlar_table.cellWidget(row, 3)
                    if birim_combo and birim:
                        birim_upper = birim.upper()
                        index = birim_combo.findText(birim_upper)
                        if index >= 0:
                            birim_combo.setCurrentIndex(index)
                        else:
                            birim_combo.addItem(birim_upper)
                            birim_combo.setCurrentText(birim_upper)
                    
                    # Döviz Türü ComboBox'u güncelle
                    doviz_combo = self.satirlar_table.cellWidget(row, 7)
                    if doviz_combo and doviz_turu:
                        index = doviz_combo.findText(doviz_turu)
                        if index >= 0:
                            doviz_combo.setCurrentIndex(index)
            
            # Toplamları güncelle
            toplam = float(self.fatura_data.get('toplam', 0) or 0)
            toplam_kdv = float(self.fatura_data.get('toplamKDV', 0) or 0)
            net_tutar = float(self.fatura_data.get('netTutar', 0) or 0)
            
            self.txt_ara_toplam.setText(f"{toplam:.2f}".replace('.', ','))
            self.txt_kdv_toplam.setText(f"{toplam_kdv:.2f}".replace('.', ','))
            self.txt_genel_toplam.setText(f"{net_tutar:.2f}".replace('.', ','))
            
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
            
        except Exception as e:
            print(f"load_data hatası: {e}")
            import traceback
            traceback.print_exc()
            self.satirlar_table.blockSignals(False)
            self.is_auto_filling = False
        
    def get_data(self):
        """Form verilerini döndür"""
        # Fatura ID'yi ekle (güncelleme için)
        fatura_id = None
        if self.is_edit_mode and self.fatura_data:
            fatura_id = self.fatura_data.get('id')
        
        # Satırları topla
        satirlar = []
        for r in range(self.satirlar_table.rowCount()):
            try:
                malzeme_kodu = self.satirlar_table.item(r, 0).text() if self.satirlar_table.item(r, 0) else ""  # Malzeme Kodu
                malzeme_ismi = self.satirlar_table.item(r, 1).text() if self.satirlar_table.item(r, 1) else ""  # Malzeme İsmi
                miktar_text = self.satirlar_table.item(r, 2).text() if self.satirlar_table.item(r, 2) else ""  # Miktar
                birim_widget = self.satirlar_table.cellWidget(r, 3)  # Birim
                birim = birim_widget.currentText() if birim_widget else ""
                aciklama = self.satirlar_table.item(r, 4).text() if self.satirlar_table.item(r, 4) else ""  # Açıklama
                birim_fiyat_text = self.satirlar_table.item(r, 5).text() if self.satirlar_table.item(r, 5) else ""  # Birim Fiyat
                doviz_fiyat_text = self.satirlar_table.item(r, 6).text() if self.satirlar_table.item(r, 6) else ""  # Döviz Fiyatı
                doviz_widget = self.satirlar_table.cellWidget(r, 7)  # Döviz Türü
                doviz = doviz_widget.currentText() if doviz_widget else ""
                kdv_text = self.satirlar_table.item(r, 8).text() if self.satirlar_table.item(r, 8) else ""  # KDV %
                tutar_text = self.satirlar_table.item(r, 9).text() if self.satirlar_table.item(r, 9) else ""  # Tutar
                net_tutar_text = self.satirlar_table.item(r, 10).text() if self.satirlar_table.item(r, 10) else ""  # Net Tutar
                
                if malzeme_kodu or malzeme_ismi or miktar_text or aciklama:
                    # Güvenli float dönüşümleri
                    try:
                        miktar = float(miktar_text.replace(',', '.').strip() or "0")
                    except:
                        miktar = 0
                    
                    try:
                        birim_fiyat = float(birim_fiyat_text.replace(',', '.').replace(' TL', '').replace(' ₺', '').strip() or "0")
                    except:
                        birim_fiyat = 0
                    
                    try:
                        kdv_orani = float(kdv_text.replace(',', '.').strip() or "0")
                    except:
                        kdv_orani = 0
                    
                    try:
                        # Tutar ve Net Tutar'dan ₺ işaretini temizle
                        tutar = float(tutar_text.replace(',', '.').replace(' ₺', '').replace(' TL', '').strip() or "0")
                    except:
                        tutar = 0
                    
                    try:
                        # Net Tutar = Tutar + KDV
                        net_tutar_clean = net_tutar_text.replace(',', '.').replace(' ₺', '').replace(' TL', '').strip() or "0"
                        net_tutar = float(net_tutar_clean)
                    except:
                        # Eğer okunamazsa hesapla
                        net_tutar = tutar + (tutar * kdv_orani / 100)
                    
                    try:
                        # Döviz fiyatından kısaltmayı temizle ($, €, ₺)
                        doviz_fiyat_clean = doviz_fiyat_text.replace(',', '.').replace(' $', '').replace(' €', '').replace(' ₺', '').strip() or "0"
                        doviz_fiyat = float(doviz_fiyat_clean)
                    except:
                        doviz_fiyat = 0
                    
                    satirlar.append({
                        'stokKodu': malzeme_kodu,  # Malzeme kodu olarak kaydet
                        'malzemeKodu': malzeme_kodu,  # Yeni alan
                        'malzemeIsmi': malzeme_ismi,  # Yeni alan
                        'miktar': miktar,
                        'birim': birim,
                        'aciklama': aciklama,
                        'birimFiyat': birim_fiyat,
                        'dovizFiyat': doviz_fiyat,
                        'dovizTuru': doviz,
                        'kdvOrani': kdv_orani,
                        'tutar': tutar,
                        'netTutar': net_tutar
                    })
            except Exception as e:
                print(f"Satır {r} veri okuma hatası: {e}")
                continue
        
        # Toplamları güvenli şekilde oku
        # txt_ara_toplam = KDV hariç toplam (net tutar)
        # txt_kdv_toplam = KDV tutarı
        # txt_genel_toplam = KDV dahil toplam (net tutar + KDV)
        try:
            ara_toplam_text = self.txt_ara_toplam.text().replace(',', '.').strip() or "0"
            net_tutar_kdv_haric = float(ara_toplam_text)  # KDV hariç toplam
        except:
            net_tutar_kdv_haric = 0
        
        try:
            toplam_kdv_text = self.txt_kdv_toplam.text().replace(',', '.').strip() or "0"
            toplam_kdv = float(toplam_kdv_text)  # KDV tutarı
        except:
            toplam_kdv = 0
        
        try:
            genel_toplam_text = self.txt_genel_toplam.text().replace(',', '.').strip() or "0"
            toplam_kdv_dahil = float(genel_toplam_text)  # KDV dahil toplam
        except:
            toplam_kdv_dahil = net_tutar_kdv_haric + toplam_kdv  # Hesapla
        
        # Eğer genel toplam hesaplanmamışsa, hesapla
        if toplam_kdv_dahil == 0:
            toplam_kdv_dahil = net_tutar_kdv_haric + toplam_kdv
        
        # Veritabanı için uygun format
        toplam = toplam_kdv_dahil  # KDV dahil toplam
        net_tutar = net_tutar_kdv_haric  # KDV hariç toplam
        
        # Fatura numarası - eğer yoksa otomatik oluştur
        fatura_no_text = self.txt_cari_kodu.text().strip()
        # Eğer fatura numarası formatında değilse (ARV veya AAA ile başlamıyorsa), otomatik oluştur
        if not fatura_no_text or (not fatura_no_text.startswith('ARV') and not fatura_no_text.startswith('AAA')):
            fatura_no = self.generate_fatura_no()
        else:
            fatura_no = fatura_no_text
        
        # Cari hesap bilgileri
        selected_cari_id = getattr(self, 'selected_cari_id', '')
        selected_cari_kodu = getattr(self, 'selected_cari_kodu', '') or ''
        
        # Cari hesabın email bilgisini veritabanından çek
        cari_email = ''
        if selected_cari_id:
            try:
                from models.cari_hesap_model import CariHesapModel
                cari_model = CariHesapModel()
                cari_data = cari_model.get_by_id(selected_cari_id)
                if cari_data:
                    cari_email = cari_data.get('email', '')
                    # Eğer email yoksa iletisim içinde ara
                    if not cari_email:
                        iletisim = cari_data.get('iletisim', {})
                        if isinstance(iletisim, str):
                            import json
                            try:
                                iletisim = json.loads(iletisim)
                            except:
                                iletisim = {}
                        cari_email = iletisim.get('email', '') if isinstance(iletisim, dict) else ''
            except Exception as e:
                print(f"Cari hesap email çekme hatası: {e}")
        
        # Ödeme planını al
        odeme_plani = self.cmb_odeme.currentText() if hasattr(self, 'cmb_odeme') else '30 Gün'
        
        result = {
            'faturaNo': fatura_no,
            'tarih': self.date_edit.date().toString("yyyy-MM-dd"),
            'faturaTipi': self.cmb_tip.currentText(),
            'cariId': selected_cari_id,
            'odemePlani': odeme_plani,  # Ödeme planını fatura verisine ekle
            'cariHesap': {
                'id': selected_cari_id,
                'kodu': selected_cari_kodu,
                'unvani': self.txt_unvan.text().strip(),
                'email': cari_email,  # Email'i cariHesap içine ekle
                'odemePlani': odeme_plani  # Ödeme planını cariHesap içine de ekle
            },
            'satirlar': satirlar,
            'toplam': toplam_kdv_dahil,  # KDV dahil toplam
            'toplamKDV': toplam_kdv,  # KDV tutarı
            'netTutar': net_tutar_kdv_haric,  # KDV hariç toplam
            'durum': 'Açık'
        }
        
        # Güncelleme modunda fatura ID'yi ekle
        if self.is_edit_mode and self.fatura_data:
            result['id'] = self.fatura_data.get('id')
        
        return result
        
    def generate_fatura_no(self):
        """Fatura numarasını otomatik oluştur - Model'den al"""
        from models.fatura_model import FaturaModel
        try:
            model = FaturaModel()
            fatura_no = model._generate_fatura_no()
            self.txt_cari_kodu.setText(fatura_no)
            return fatura_no
        except Exception as e:
            # Hata durumunda basit numara oluştur
            from datetime import datetime
            import time
            year = datetime.now().year
            timestamp = int(time.time()) % 1000000
            fatura_no = f"ARV{year}{timestamp:06d}"
            self.txt_cari_kodu.setText(fatura_no)
            return fatura_no
    
    def validate(self):
        """Form validasyonu"""
        # Cari hesap seçimi kontrolü - selected_cari_id veya unvan alanı kontrol edilmeli
        selected_cari_id = getattr(self, 'selected_cari_id', None)
        unvan_text = self.txt_unvan.text().strip()
        
        if not selected_cari_id and not unvan_text:
            QMessageBox.warning(self, "Hata", "Cari hesap seçimi zorunludur!\nLütfen cari hesap seçin.")
            return False
        
        # Eğer unvan varsa ama ID yoksa, tekrar kontrol et
        if unvan_text and not selected_cari_id:
            QMessageBox.warning(self, "Hata", "Cari hesap seçimi tamamlanmamış!\nLütfen tekrar cari hesap seçin.")
            return False
        
        # Malzeme satırları kontrolü - En az bir satır olmalı ve miktar girilmiş olmalı
        satir_sayisi = self.satirlar_table.rowCount()
        if satir_sayisi == 0:
            QMessageBox.warning(self, "Hata", "Fatura için en az bir malzeme satırı eklenmelidir!")
            return False
        
        # Her satırda miktar kontrolü
        for r in range(satir_sayisi):
            # Malzeme kodu kontrolü
            malzeme_kodu_item = self.satirlar_table.item(r, 0)  # Malzeme Kodu
            malzeme_kodu = malzeme_kodu_item.text().strip() if malzeme_kodu_item else ""
            
            # Eğer malzeme kodu varsa, miktar zorunlu
            if malzeme_kodu:
                miktar_item = self.satirlar_table.item(r, 2)  # Miktar
                miktar_text = miktar_item.text().strip() if miktar_item else ""
                
                if not miktar_text:
                    QMessageBox.warning(
                        self, 
                        "Hata", 
                        f"{r + 1}. satırdaki malzeme için miktar girilmesi zorunludur!\n"
                        f"Malzeme: {malzeme_kodu}"
                    )
                    # Hatalı satıra odaklan
                    self.satirlar_table.setCurrentCell(r, 2)
                    return False
                
                # Miktar 0'dan büyük olmalı
                try:
                    miktar = float(miktar_text.replace(',', '.'))
                    if miktar <= 0:
                        QMessageBox.warning(
                            self,
                            "Hata",
                            f"{r + 1}. satırdaki malzeme için miktar 0'dan büyük olmalıdır!\n"
                            f"Malzeme: {malzeme_kodu}"
                        )
                        self.satirlar_table.setCurrentCell(r, 2)
                        return False
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Hata",
                        f"{r + 1}. satırdaki malzeme için geçerli bir miktar girilmelidir!\n"
                        f"Malzeme: {malzeme_kodu}"
                    )
                    self.satirlar_table.setCurrentCell(r, 2)
                    return False
        
        return True
    
    def on_save(self):
        """Kaydet butonuna tıklandığında"""
        if self.validate():
            self.accept()
