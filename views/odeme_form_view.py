"""
Ödeme Form View - Yeni ödeme ekleme formu
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QComboBox,
    QTextEdit, QDateEdit, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QFontDatabase


class OdemeFormView(QDialog):
    """Ödeme ekleme/düzenleme formu"""
    
    def __init__(self, parent=None, odeme_data=None):
        super().__init__(parent)
        self.odeme_data = odeme_data
        self._load_brand_fonts()
        self._init_colors()
        self.init_ui()
        
        if odeme_data:
            self.load_data(odeme_data)
    
    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"
        self.color_success = "#10b981"
    
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
        self.setWindowTitle("Yeni Ödeme Ekle" if not self.odeme_data else "Ödeme Düzenle")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        self.setStyleSheet(f"background: {self.color_bg};")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel("Yeni Ödeme Ekle" if not self.odeme_data else "Ödeme Düzenle")
        title.setFont(self._brand_font(size=20, bold=True))
        title.setStyleSheet(f"color: {self.color_text}; padding: 10px;")
        layout.addWidget(title)
        
        # Kategori seçimi
        kategori_group = QGroupBox("Kategori")
        kategori_group.setStyleSheet(self._group_style())
        kategori_layout = QFormLayout(kategori_group)
        kategori_layout.setSpacing(10)
        
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems([
            "Tedarikçi Ödemesi",
            "Maaş Ödemesi",
            "Kira Ödemesi",
            "Diğer Ödeme"
        ])
        self.kategori_combo.currentIndexChanged.connect(self.on_kategori_changed)
        self.kategori_combo.setStyleSheet(self._combo_style())
        kategori_layout.addRow("Kategori:", self.kategori_combo)
        
        layout.addWidget(kategori_group)
        
        # Temel Bilgiler
        basic_group = QGroupBox("Temel Bilgiler")
        basic_group.setStyleSheet(self._group_style())
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)
        
        self.tarih_input = QDateEdit()
        self.tarih_input.setDate(QDate.currentDate())
        self.tarih_input.setCalendarPopup(True)
        self.tarih_input.setStyleSheet(self._input_style())
        basic_layout.addRow("Tarih:", self.tarih_input)
        
        self.tutar_input = QLineEdit()
        self.tutar_input.setPlaceholderText("0.00")
        self.tutar_input.setStyleSheet(self._input_style())
        basic_layout.addRow("Tutar (₺):", self.tutar_input)
        
        self.odeme_turu_combo = QComboBox()
        self.odeme_turu_combo.addItems(["Nakit", "Havale/EFT", "Çek", "Kredi Kartı"])
        self.odeme_turu_combo.setStyleSheet(self._combo_style())
        basic_layout.addRow("Ödeme Türü:", self.odeme_turu_combo)
        
        layout.addWidget(basic_group)
        
        # Tedarikçi/Alıcı Bilgileri (kategoriye göre görünür)
        self.tedarikci_group = QGroupBox("Tedarikçi Bilgileri")
        self.tedarikci_group.setStyleSheet(self._group_style())
        tedarikci_layout = QFormLayout(self.tedarikci_group)
        tedarikci_layout.setSpacing(10)
        
        self.tedarikci_combo = QComboBox()
        self.tedarikci_combo.setEditable(True)
        self.tedarikci_combo.setStyleSheet(self._combo_style())
        tedarikci_layout.addRow("Tedarikçi:", self.tedarikci_combo)
        
        self.alim_faturasi_combo = QComboBox()
        self.alim_faturasi_combo.setStyleSheet(self._combo_style())
        tedarikci_layout.addRow("Alım Faturası:", self.alim_faturasi_combo)
        
        layout.addWidget(self.tedarikci_group)
        
        # Maaş/Kira Bilgileri (kategoriye göre görünür)
        self.maas_kira_group = QGroupBox("Detay Bilgileri")
        self.maas_kira_group.setStyleSheet(self._group_style())
        maas_kira_layout = QFormLayout(self.maas_kira_group)
        maas_kira_layout.setSpacing(10)
        
        self.personel_kira_input = QLineEdit()
        self.personel_kira_input.setPlaceholderText("Personel adı veya kira açıklaması")
        self.personel_kira_input.setStyleSheet(self._input_style())
        maas_kira_layout.addRow("Açıklama:", self.personel_kira_input)
        
        layout.addWidget(self.maas_kira_group)
        
        # Diğer Bilgiler
        other_group = QGroupBox("Diğer Bilgiler")
        other_group.setStyleSheet(self._group_style())
        other_layout = QFormLayout(other_group)
        other_layout.setSpacing(10)
        
        self.kasa_combo = QComboBox()
        self.kasa_combo.addItems(["Kasa 1", "Kasa 2", "Ana Kasa"])
        self.kasa_combo.setEditable(True)
        self.kasa_combo.setStyleSheet(self._combo_style())
        other_layout.addRow("Kasa:", self.kasa_combo)
        
        self.banka_combo = QComboBox()
        self.banka_combo.addItems(["Ziraat Bankası", "İş Bankası", "Garanti Bankası"])
        self.banka_combo.setEditable(True)
        self.banka_combo.setStyleSheet(self._combo_style())
        other_layout.addRow("Banka:", self.banka_combo)
        
        self.belge_no_input = QLineEdit()
        self.belge_no_input.setPlaceholderText("Belge numarası")
        self.belge_no_input.setStyleSheet(self._input_style())
        other_layout.addRow("Belge No:", self.belge_no_input)
        
        self.vade_tarihi_input = QDateEdit()
        self.vade_tarihi_input.setCalendarPopup(True)
        self.vade_tarihi_input.setDate(QDate.currentDate())
        self.vade_tarihi_input.setStyleSheet(self._input_style())
        other_layout.addRow("Vade Tarihi:", self.vade_tarihi_input)
        
        self.aciklama_input = QTextEdit()
        self.aciklama_input.setMaximumHeight(80)
        self.aciklama_input.setPlaceholderText("Açıklama (opsiyonel)")
        self.aciklama_input.setStyleSheet(self._input_style())
        other_layout.addRow("Açıklama:", self.aciklama_input)
        
        layout.addWidget(other_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_iptal = QPushButton("İptal")
        self.btn_iptal.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_muted};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._adjust_color(self.color_muted, 1.1)};
            }}
        """)
        self.btn_iptal.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_iptal)
        
        self.btn_kaydet = QPushButton("Kaydet")
        self.btn_kaydet.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_accent};
                color: white;
                padding: 10px 30px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._adjust_color(self.color_accent, 1.1)};
            }}
        """)
        self.btn_kaydet.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_kaydet)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # İlk kategori değişikliğini tetikle
        self.on_kategori_changed(0)
        
        # Verileri yükle
        self.load_tedarikciler()
        self.load_alim_faturalari()
    
    def on_kategori_changed(self, index):
        """Kategori değiştiğinde"""
        kategori_map = {
            0: 'TEDARIKCI',
            1: 'MAAS',
            2: 'KIRA',
            3: 'DIGER'
        }
        kategori = kategori_map.get(index, 'DIGER')
        
        # Tedarikçi grubunu göster/gizle
        self.tedarikci_group.setVisible(kategori == 'TEDARIKCI')
        
        # Maaş/Kira grubunu göster/gizle
        self.maas_kira_group.setVisible(kategori in ['MAAS', 'KIRA', 'DIGER'])
        
        if kategori == 'MAAS':
            self.maas_kira_group.setTitle("Maaş Bilgileri")
            self.personel_kira_input.setPlaceholderText("Personel adı")
        elif kategori == 'KIRA':
            self.maas_kira_group.setTitle("Kira Bilgileri")
            self.personel_kira_input.setPlaceholderText("Kira açıklaması (adres, dönem vb.)")
        else:
            self.maas_kira_group.setTitle("Detay Bilgileri")
            self.personel_kira_input.setPlaceholderText("Açıklama")
    
    def load_tedarikciler(self):
        """Tedarikçileri yükle"""
        try:
            from models.cari_hesap_model import CariHesapModel
            cari_model = CariHesapModel()
            cari_list = cari_model.get_all()
            
            self.tedarikci_combo.clear()
            self.tedarikci_combo.addItem("", None)
            for cari in cari_list:
                unvan = cari.get('unvani', '')
                if unvan:
                    self.tedarikci_combo.addItem(unvan, cari.get('id'))
        except Exception as e:
            print(f"Tedarikçi yükleme hatası: {e}")
    
    def load_alim_faturalari(self):
        """Alım faturalarını yükle"""
        try:
            from models.purchase_invoice_model import PurchaseInvoiceModel
            invoice_model = PurchaseInvoiceModel()
            invoices = invoice_model.get_all()
            
            self.alim_faturasi_combo.clear()
            self.alim_faturasi_combo.addItem("Seçiniz...", None)
            for invoice in invoices:
                fatura_no = invoice.get('fatura_no', '')
                tedarikci = invoice.get('tedarikci_unvani', '')
                if fatura_no:
                    display_text = f"{fatura_no} - {tedarikci}" if tedarikci else fatura_no
                    self.alim_faturasi_combo.addItem(display_text, invoice.get('id'))
        except Exception as e:
            print(f"Alım faturası yükleme hatası: {e}")
    
    def load_data(self, odeme_data):
        """Mevcut ödeme verisini yükle"""
        kategori = odeme_data.get('kategori', 'DIGER')
        kategori_map = {
            'TEDARIKCI': 0,
            'MAAS': 1,
            'KIRA': 2,
            'DIGER': 3
        }
        self.kategori_combo.setCurrentIndex(kategori_map.get(kategori, 3))
        
        if odeme_data.get('tarih'):
            self.tarih_input.setDate(QDate.fromString(odeme_data['tarih'], "yyyy-MM-dd"))
        
        self.tutar_input.setText(str(odeme_data.get('tutar', '')))
        
        odeme_turu = odeme_data.get('odeme_turu', 'Nakit')
        index = self.odeme_turu_combo.findText(odeme_turu)
        if index >= 0:
            self.odeme_turu_combo.setCurrentIndex(index)
        
        if odeme_data.get('tedarikci_id'):
            index = self.tedarikci_combo.findData(odeme_data['tedarikci_id'])
            if index >= 0:
                self.tedarikci_combo.setCurrentIndex(index)
        
        if odeme_data.get('alim_faturasi_id'):
            index = self.alim_faturasi_combo.findData(odeme_data['alim_faturasi_id'])
            if index >= 0:
                self.alim_faturasi_combo.setCurrentIndex(index)
        
        self.personel_kira_input.setText(odeme_data.get('aciklama', ''))
        self.kasa_combo.setCurrentText(odeme_data.get('kasa', ''))
        self.banka_combo.setCurrentText(odeme_data.get('banka', ''))
        self.belge_no_input.setText(odeme_data.get('belge_no', ''))
        
        if odeme_data.get('vade_tarihi'):
            self.vade_tarihi_input.setDate(QDate.fromString(odeme_data['vade_tarihi'], "yyyy-MM-dd"))
        
        self.aciklama_input.setPlainText(odeme_data.get('aciklama', ''))
    
    def get_data(self):
        """Form verilerini al"""
        kategori_map = {
            0: 'TEDARIKCI',
            1: 'MAAS',
            2: 'KIRA',
            3: 'DIGER'
        }
        kategori = kategori_map.get(self.kategori_combo.currentIndex(), 'DIGER')
        
        data = {
            'kategori': kategori,
            'tarih': self.tarih_input.date().toString("yyyy-MM-dd"),
            'tutar': float(self.tutar_input.text() or 0),
            'odeme_turu': self.odeme_turu_combo.currentText(),
            'kasa': self.kasa_combo.currentText(),
            'banka': self.banka_combo.currentText(),
            'belge_no': self.belge_no_input.text(),
            'vade_tarihi': self.vade_tarihi_input.date().toString("yyyy-MM-dd"),
            'aciklama': self.aciklama_input.toPlainText()
        }
        
        if kategori == 'TEDARIKCI':
            tedarikci_id = self.tedarikci_combo.currentData()
            if tedarikci_id:
                data['tedarikci_id'] = tedarikci_id
            data['tedarikci_unvani'] = self.tedarikci_combo.currentText()
            
            alim_faturasi_id = self.alim_faturasi_combo.currentData()
            if alim_faturasi_id:
                data['alim_faturasi_id'] = alim_faturasi_id
        else:
            # Maaş/Kira/Diger için açıklama alanını kullan
            aciklama = self.personel_kira_input.text()
            if aciklama:
                data['aciklama'] = aciklama
        
        return data
    
    def validate(self):
        """Form validasyonu"""
        if not self.tutar_input.text() or float(self.tutar_input.text() or 0) <= 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir tutar girin!")
            return False
        
        kategori = self.kategori_combo.currentIndex()
        if kategori == 0:  # Tedarikçi
            if not self.tedarikci_combo.currentText():
                QMessageBox.warning(self, "Uyarı", "Lütfen bir tedarikçi seçin!")
                return False
        
        return True
    
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
    
    def _input_style(self):
        return f"""
            QLineEdit, QTextEdit, QDateEdit {{
                padding: 8px;
                border: 1px solid {self.color_border};
                border-radius: 6px;
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus {{
                border: 1px solid {self.color_primary};
            }}
        """
    
    def _combo_style(self):
        return f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {self.color_border};
                border-radius: 6px;
                font-size: 13px;
            }}
            QComboBox:focus {{
                border: 1px solid {self.color_primary};
            }}
        """
    
    @staticmethod
    def _adjust_color(hex_color, factor):
        """Rengi aydınlatmak/koyulaştırmak için yardımcı fonksiyon"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

