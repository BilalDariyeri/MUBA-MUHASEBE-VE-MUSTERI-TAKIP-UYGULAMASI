"""
Gmail Settings Dialog - Gmail hesap ayarları (MUBA teması)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QCheckBox, QGroupBox, QTextEdit
)
from PyQt5.QtCore import Qt


class GmailSettingsDialog(QDialog):
    """Gmail hesap ayarları dialog'u"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_colors()
        self.setWindowTitle("Gmail Hesap Ayarları")
        self.setFixedSize(500, 400)
        self.init_ui()
        self.load_settings()

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
                padding: 9px 14px;
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
            QLineEdit, QTextEdit {{
                border: 1px solid {self.color_border};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 13px;
                background: #ffffff;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {self.color_primary};
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
                left: 10px;
                padding: 0 6px;
                color: {self.color_primary};
                font-weight: 700;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Gmail Hesap Bağlantısı")
        title.setStyleSheet(f"color: {self.color_primary}; font-size: 18px; font-weight: 700;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info_group = QGroupBox("Bilgi")
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(80)
        info_text.setText(
            "Fatura gönderimi için Gmail hesabınızı bağlayın.\n"
            "Uygulama bazlı şifre kullanmanız önerilir."
        )
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        form_group = QGroupBox("Ayarlar")
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Gmail adresi")
        form_layout.addRow("E-posta:", self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Uygulama şifresi")
        form_layout.addRow("Şifre:", self.password_input)

        self.smtp_server_input = QLineEdit("smtp.gmail.com")
        form_layout.addRow("SMTP Sunucu:", self.smtp_server_input)

        self.smtp_port_input = QLineEdit("587")
        form_layout.addRow("SMTP Port:", self.smtp_port_input)

        self.ssl_checkbox = QCheckBox("SSL/TLS kullan")
        self.ssl_checkbox.setChecked(True)
        form_layout.addRow("", self.ssl_checkbox)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        btn_save = QPushButton("Kaydet")
        btn_cancel = QPushButton("İptal")
        self._style_btn(btn_save, self.color_accent, "#0f112b")
        self._style_btn(btn_cancel, self.color_muted)
        btn_save.clicked.connect(self.save_settings)
        btn_cancel.clicked.connect(self.reject)

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(btn_save)
        footer.addWidget(btn_cancel)

        layout.addLayout(footer)
        self.setLayout(layout)

    def save_settings(self):
        """Ayarları kaydet ve dialogu kapat"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        smtp_server = self.smtp_server_input.text().strip()
        smtp_port = self.smtp_port_input.text().strip()
        use_ssl = self.ssl_checkbox.isChecked()

        if not email or not password:
            QMessageBox.warning(self, "Uyarı", "E-posta ve şifre zorunludur.")
            return

        try:
            import os
            os.environ['GMAIL_EMAIL'] = email
            os.environ['GMAIL_PASSWORD'] = password
            os.environ['GMAIL_SMTP_SERVER'] = smtp_server
            os.environ['GMAIL_SMTP_PORT'] = smtp_port
            os.environ['GMAIL_USE_SSL'] = '1' if use_ssl else '0'
            QMessageBox.information(self, "Başarılı", "Gmail ayarları kaydedildi.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilirken hata oluştu:\n{str(e)}")

    def load_settings(self):
        """Önceden kaydedilmiş ortam değişkenlerini yükle"""
        import os
        self.email_input.setText(os.environ.get('GMAIL_EMAIL', ''))
        self.password_input.setText(os.environ.get('GMAIL_PASSWORD', ''))
        self.smtp_server_input.setText(os.environ.get('GMAIL_SMTP_SERVER', 'smtp.gmail.com'))
        self.smtp_port_input.setText(os.environ.get('GMAIL_SMTP_PORT', '587'))
        self.ssl_checkbox.setChecked(os.environ.get('GMAIL_USE_SSL', '1') == '1')
