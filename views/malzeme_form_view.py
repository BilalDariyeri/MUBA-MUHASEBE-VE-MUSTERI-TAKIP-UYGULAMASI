"""
Malzeme Form View - MUBA teması
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QMessageBox, QDialogButtonBox, QDoubleSpinBox, QSpinBox, QFrame, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase


class MalzemeFormView(QDialog):
    """Malzeme form görünümü - View katmanı"""
    
    def __init__(self, parent=None, malzeme_data=None):
        super().__init__(parent)
        self.malzeme_data = malzeme_data
        self.is_edit_mode = malzeme_data is not None
        self.setWindowTitle("Yeni Malzeme Ekle" if not self.is_edit_mode else "Malzeme Düzenle")
        self.setModal(True)
        self.setMinimumWidth(760)
        self._load_brand_fonts()
        self._init_colors()
        self.init_ui()
        
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
        self.setStyleSheet(f"QDialog {{ background: {self.color_bg}; }}")
        
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(12)
        
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
            }}
            QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTextEdit {{
                border: 1px solid {self.color_border};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
                border: 1px solid {self.color_primary};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(14)
        
        header = QLabel("Malzeme Bilgileri" if not self.is_edit_mode else "Malzeme Düzenle")
        header.setFont(self._brand_font(size=16, bold=True))
        header.setStyleSheet(f"color: {self.color_text};")
        card_layout.addWidget(header)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.kod_input = QLineEdit()
        self.kod_input.setReadOnly(True)
        self.kod_input.setPlaceholderText("Malzeme adı girildiğinde otomatik oluşur")
        self.kod_input.setStyleSheet("background: #f5f6fb; color: #6b7280;")
        form_layout.addRow("Malzeme Kodu (Otomatik):", self.kod_input)
        
        self.ad_input = QLineEdit()
        self.ad_input.setPlaceholderText("Örn: silindir başı itici 30x300")
        if not self.is_edit_mode:
            self.ad_input.textChanged.connect(self.on_ad_changed)
        form_layout.addRow("Malzeme Adı (Uzun İsim) *:", self.ad_input)
        
        self.birim_combo = QComboBox()
        self.birim_combo.addItems(["Adet", "Kg", "Ton", "Litre", "Metre", "m²", "m³", "Paket", "Kutu"])
        form_layout.addRow("Birim *:", self.birim_combo)
        
        self.stok_input = QDoubleSpinBox()
        self.stok_input.setMinimum(-999999.99)
        self.stok_input.setMaximum(999999.99)
        self.stok_input.setValue(0)
        self.stok_input.setDecimals(2)
        form_layout.addRow("Stok Miktarı:", self.stok_input)
        
        self.birim_fiyat_input = QDoubleSpinBox()
        self.birim_fiyat_input.setMinimum(0)
        self.birim_fiyat_input.setMaximum(9999999.99)
        self.birim_fiyat_input.setValue(0)
        self.birim_fiyat_input.setDecimals(2)
        self.birim_fiyat_input.setPrefix("₺ ")
        form_layout.addRow("Birim Fiyat:", self.birim_fiyat_input)
        
        self.kdv_input = QSpinBox()
        self.kdv_input.setMinimum(0)
        self.kdv_input.setMaximum(100)
        self.kdv_input.setValue(18)
        self.kdv_input.setSuffix("%")
        form_layout.addRow("KDV Oranı:", self.kdv_input)
        
        self.kategori_input = QLineEdit()
        self.kategori_input.setPlaceholderText("Örn: İnşaat Malzemesi")
        form_layout.addRow("Kategori:", self.kategori_input)
        
        self.aciklama_input = QTextEdit()
        self.aciklama_input.setMaximumHeight(90)
        self.aciklama_input.setPlaceholderText("Malzeme açıklaması...")
        form_layout.addRow("Açıklama:", self.aciklama_input)
        
        self.durum_combo = QComboBox()
        self.durum_combo.addItems(["Aktif", "Pasif"])
        form_layout.addRow("Durum:", self.durum_combo)
        
        card_layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Kaydet")
        buttons.button(QDialogButtonBox.Cancel).setText("İptal")
        buttons.button(QDialogButtonBox.Save).setCursor(Qt.PointingHandCursor)
        buttons.button(QDialogButtonBox.Cancel).setCursor(Qt.PointingHandCursor)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet(f"""
            QPushButton {{
                min-height: 34px;
                border-radius: 6px;
                padding: 8px 14px;
            }}
            QPushButton[text='Kaydet'] {{
                background: {self.color_primary};
                color: #ffffff;
            }}
            QPushButton[text='Kaydet']:hover {{ background: #1d2b56; }}
            QPushButton[text='Kaydet']:pressed {{ background: #182347; }}
            QPushButton[text='İptal'] {{
                background: #6c757d;
                color: #ffffff;
            }}
            QPushButton[text='İptal']:hover {{ background: #5a6268; }}
        """)
        card_layout.addWidget(buttons)
        
        outer.addWidget(card)
        self.setLayout(outer)
        
    def load_data(self):
        """Düzenleme modunda veriyi yükle"""
        if not self.malzeme_data:
            return
        self.kod_input.setText(self.malzeme_data.get('kod', ''))
        self.ad_input.setText(self.malzeme_data.get('ad', ''))
        birim = self.malzeme_data.get('birim', 'Adet')
        index = self.birim_combo.findText(birim)
        if index >= 0:
            self.birim_combo.setCurrentIndex(index)
        self.stok_input.setValue(self.malzeme_data.get('stok', 0))
        self.birim_fiyat_input.setValue(self.malzeme_data.get('birimFiyat', 0))
        self.kdv_input.setValue(self.malzeme_data.get('kdvOrani', 18))
        self.kategori_input.setText(str(self.malzeme_data.get('kategori') or ''))
        self.aciklama_input.setPlainText(str(self.malzeme_data.get('aciklama') or ''))
        durum = self.malzeme_data.get('durum', 'Aktif')
        index = self.durum_combo.findText(durum)
        if index >= 0:
            self.durum_combo.setCurrentIndex(index)
        
    def get_data(self):
        """Form verilerini döndür"""
        kod = self.kod_input.text().strip().upper() if self.is_edit_mode else None
        ad_text = self.ad_input.text()
        kategori_text = self.kategori_input.text()
        aciklama_text = self.aciklama_input.toPlainText()
        return {
            'kod': kod,
            'ad': ad_text.strip() if ad_text else '',
            'birim': self.birim_combo.currentText(),
            'stok': self.stok_input.value(),
            'birimFiyat': self.birim_fiyat_input.value(),
            'kdvOrani': self.kdv_input.value(),
            'kategori': kategori_text.strip() if kategori_text else '',
            'aciklama': aciklama_text.strip() if aciklama_text else '',
            'durum': self.durum_combo.currentText()
        }
    
    def on_ad_changed(self, text):
        """Malzeme adı değiştiğinde otomatik kod oluştur"""
        if not self.is_edit_mode and text.strip():
            try:
                from models.malzeme_model import MalzemeModel
                model = MalzemeModel()
                kod = model._generate_kod_from_name(text)
                self.kod_input.setText(kod)
            except Exception:
                pass
    
    def validate(self):
        """Form validasyonu"""
        if not self.ad_input.text().strip():
            QMessageBox.warning(self, "Hata", "Malzeme Adı zorunludur!")
            self.ad_input.setFocus()
            return False
        if not self.birim_combo.currentText():
            QMessageBox.warning(self, "Hata", "Birim zorunludur!")
            self.birim_combo.setFocus()
            return False
        return True
