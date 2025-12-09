"""
Register View - Kayıt ekranı (MUBA teması)
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap
from models.user_model import UserModel


class RegisterView(QDialog):
    """Kayıt ekranı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_model = UserModel()
        self.email = ""
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
        """UI'yi başlat"""
        self.setWindowTitle("MUBA - Kayıt Ol")
        self.setFixedSize(460, 520)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog { background: #e7e3ff; }
            QLineEdit {
                border: 1px solid #d0d4f2;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                background: #ffffff;
            }
            QLineEdit:focus { border: 1px solid #233568; }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(30, 24, 30, 24)
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #d0d4f2;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(22, 22, 22, 22)
        
        # Logo + başlık
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
        
        title = QLabel("Yeni Kullanıcı Kaydı")
        title.setFont(self._brand_font(size=18, bold=True))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #233568;")
        header.addWidget(title)
        
        subtitle = QLabel("MUBA hesabınızı oluşturun ve devam edin.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(self._brand_font(size=11))
        subtitle.setStyleSheet("color: #666a87;")
        header.addWidget(subtitle)
        
        card_layout.addLayout(header)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Adınız Soyadınız")
        self.name_input.setMinimumHeight(36)
        form_layout.addRow("Ad Soyad *:", self.name_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@email.com")
        self.email_input.setMinimumHeight(36)
        form_layout.addRow("E-posta *:", self.email_input)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("kullaniciadi (opsiyonel)")
        self.username_input.setMinimumHeight(36)
        form_layout.addRow("Kullanıcı Adı:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("En az 6 karakter")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(36)
        form_layout.addRow("Şifre *:", self.password_input)
        
        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setPlaceholderText("Şifreyi tekrar giriniz")
        self.password_confirm_input.setEchoMode(QLineEdit.Password)
        self.password_confirm_input.setMinimumHeight(36)
        form_layout.addRow("Şifre Tekrar *:", self.password_confirm_input)
        
        card_layout.addLayout(form_layout)
        
        # Butonlar
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        
        self.register_btn = QPushButton("Kayıt Ol")
        self.register_btn.setMinimumHeight(42)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #233568;
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #1d2b56; }
            QPushButton:pressed { background-color: #182347; }
        """)
        self.register_btn.clicked.connect(self.on_register)
        buttons.addWidget(self.register_btn)
        
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.setMinimumHeight(42)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #5a6268; }
            QPushButton:pressed { background-color: #4e565c; }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)
        
        card_layout.addLayout(buttons)
        layout.addWidget(card)
        
        # Enter tuşu ile kayıt
        self.password_input.returnPressed.connect(self.on_register)
        self.password_confirm_input.returnPressed.connect(self.on_register)
        self.email_input.returnPressed.connect(lambda: self.password_input.setFocus())
        
        self.setLayout(layout)
    
    def on_register(self):
        """Kayıt işlemi"""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        password_confirm = self.password_confirm_input.text()
        
        # Validasyon
        if not name:
            QMessageBox.warning(self, "Hata", "Ad soyad gereklidir")
            self.name_input.setFocus()
            return
        
        if not email:
            QMessageBox.warning(self, "Hata", "E-posta adresi gereklidir")
            self.email_input.setFocus()
            return
        
        if '@' not in email or '.' not in email.split('@')[1]:
            QMessageBox.warning(self, "Hata", "Geçerli bir e-posta adresi giriniz")
            self.email_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Hata", "Şifre gereklidir")
            self.password_input.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Hata", "Şifre en az 6 karakter olmalıdır")
            self.password_input.setFocus()
            return
        
        if password != password_confirm:
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor")
            self.password_confirm_input.setFocus()
            return
        
        try:
            data = {
                'name': name,
                'email': email,
                'password': password
            }
            if username:
                data['username'] = username
            
            user = self.user_model.create(data)
            self.email = email
            QMessageBox.information(self, "Başarılı", "Kayıt başarılı! Giriş yapabilirsiniz.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Hata", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt hatası:\n{str(e)}")

