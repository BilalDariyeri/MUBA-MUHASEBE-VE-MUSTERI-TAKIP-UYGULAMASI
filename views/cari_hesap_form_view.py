"""
Cari Hesap Form View - Form görünümü (MUBA teması)
Yeni cari hesap ekleme/düzenleme formu
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class CariHesapFormView(QDialog):
    """Cari hesap form görünümü - View katmanı"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_colors()
        self.setWindowTitle("Yeni Cari Hesap Ekle")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.init_ui()

    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_accent = "#f48c06"
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"

    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.color_bg};
            }}
            QLineEdit, QTextEdit, QComboBox {{
                border: 1px solid {self.color_border};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 13px;
                background: #ffffff;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 1px solid {self.color_primary};
            }}
        """)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        # İsim
        self.isim_input = QLineEdit()
        self.isim_input.setPlaceholderText("Örn: ABC Şirketi")
        form_layout.addRow("İsim / Şirket Adı *:", self.isim_input)

        # Vergi No
        self.vergi_no_input = QLineEdit()
        self.vergi_no_input.setPlaceholderText("Örn: 1234567890")
        form_layout.addRow("Vergi Numarası *:", self.vergi_no_input)

        # Telefon
        self.telefon_input = QLineEdit()
        self.telefon_input.setPlaceholderText("Örn: +90 555 123 45 67")
        form_layout.addRow("Telefon *:", self.telefon_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Örn: info@example.com")
        form_layout.addRow("E-Posta *:", self.email_input)

        # Adres
        self.adres_input = QTextEdit()
        self.adres_input.setMaximumHeight(80)
        self.adres_input.setPlaceholderText("Tam adres bilgisi")
        form_layout.addRow("Adres *:", self.adres_input)

        # Şehir
        self.sehir_combo = QComboBox()
        self.sehir_combo.addItem("Şehir Seçiniz", "")
        sehirler = [
            "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara",
            "Antalya", "Artvin", "Aydın", "Balıkesir", "Bilecik", "Bingöl",
            "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı",
            "Çorum", "Denizli", "Diyarbakır", "Edirne", "Elazığ", "Erzincan",
            "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane",
            "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir",
            "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir", "Kocaeli",
            "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin",
            "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya",
            "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
            "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat",
            "Zonguldak", "Aksaray", "Bayburt", "Karaman", "Kırıkkale",
            "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova",
            "Karabük", "Kilis", "Osmaniye", "Düzce"
        ]
        for sehir in sehirler:
            self.sehir_combo.addItem(sehir, sehir)
        form_layout.addRow("Şehir *:", self.sehir_combo)

        layout.addLayout(form_layout)

        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText("Kaydet")
        buttons.button(QDialogButtonBox.Cancel).setText("İptal")
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate_and_accept(self):
        if not self.isim_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "İsim/Şirket adı zorunludur.")
            return
        if not self.vergi_no_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Vergi numarası zorunludur.")
            return
        if not self.telefon_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Telefon zorunludur.")
            return
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "E-posta zorunludur.")
            return
        self.accept()

    def get_data(self):
        return {
            'unvani': self.isim_input.text().strip(),
            'vergiNo': self.vergi_no_input.text().strip(),
            'telefon': self.telefon_input.text().strip(),
            'email': self.email_input.text().strip(),
            'adres': self.adres_input.toPlainText().strip(),
            'sehir': self.sehir_combo.currentData()
        }
