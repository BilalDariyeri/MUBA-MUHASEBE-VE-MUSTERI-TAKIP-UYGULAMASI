"""
Login View - Giris ekrani (MUBA temasi)
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap
from models.user_model import UserModel


class LoginView(QDialog):
    """Giris ekrani"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_model = UserModel()
        self.logged_in_user = None
        self._load_brand_fonts()
        self.init_ui()

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

    def _brand_font(self, size=14, weight=QFont.Normal, bold=False):
        font = QFont("SF Pro Display", pointSize=size, weight=weight)
        font.setBold(bold)
        return font

    def init_ui(self):
        """UI'yi baslat"""
        self.setWindowTitle("MUBA - Giris")
        self.setFixedSize(440, 380)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #e7e3ff;
            }
            QLabel {
                border: none;
                background: transparent;
            }
            QLineEdit {
                border: 1px solid #d0d4f2;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                background: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #233568;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(30, 24, 30, 24)

        # Kart
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: none;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(22, 22, 22, 22)

        # Logo + baslik
        header = QVBoxLayout()
        header.setSpacing(6)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "muba-2.png")
        if not os.path.exists(logo_path):
            alt = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "muba-1.png")
            if os.path.exists(alt):
                logo_path = alt
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        header.addWidget(logo_label)

        title = QLabel("MUBA - Giris")
        title.setFont(self._brand_font(size=18, bold=True))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #233568;")
        header.addWidget(title)

        subtitle = QLabel("Mali isler / CRM erisimi icin giris yapin.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(self._brand_font(size=11))
        subtitle.setStyleSheet("color: #666a87;")
        header.addWidget(subtitle)

        card_layout.addLayout(header)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@email.com")
        self.email_input.setMinimumHeight(36)
        form_layout.addRow("E-posta:", self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("********")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(36)
        form_layout.addRow("Sifre:", self.password_input)

        card_layout.addLayout(form_layout)

        # Buton
        self.login_btn = QPushButton("Giris Yap")
        self.login_btn.setMinimumHeight(42)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #233568;
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #1d2b56;
            }}
            QPushButton:pressed {{
                background-color: #182347;
            }}
        """)
        self.login_btn.clicked.connect(self.on_login)
        card_layout.addWidget(self.login_btn)

        layout.addWidget(card)

        # Enter ile giris
        self.password_input.returnPressed.connect(self.on_login)
        self.email_input.returnPressed.connect(lambda: self.password_input.setFocus())

        self.setLayout(layout)

    def on_login(self):
        """Giris islemi"""
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email:
            QMessageBox.warning(self, "Hata", "E-posta adresi gereklidir")
            self.email_input.setFocus()
            return

        if '@' not in email or '.' not in email.split('@')[-1]:
            QMessageBox.warning(self, "Hata", "Gecerli bir e-posta adresi giriniz")
            self.email_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Hata", "Sifre gereklidir")
            self.password_input.setFocus()
            return

        try:
            user = self.user_model.authenticate(email, password)
            if user:
                self.logged_in_user = user
                QMessageBox.information(self, "Basarili", f"Hos geldiniz, {user['name']}!")
                self.accept()
            else:
                QMessageBox.warning(self, "Hata", "E-posta veya sifre hatali")
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Giris hatasi:\n{str(e)}")

    def on_register(self):
        """Kayit ekranini ac"""
        from views.register_view import RegisterView
        register_dialog = RegisterView(self)
        if register_dialog.exec_() == QDialog.Accepted:
            self.email_input.setText(register_dialog.email)
            self.password_input.setFocus()
