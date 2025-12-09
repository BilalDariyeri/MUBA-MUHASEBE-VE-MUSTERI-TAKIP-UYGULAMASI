"""
Veritabanı Yönetim Aracı
Veritabanını görüntüleme ve veri ekleme aracı
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QComboBox,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QMessageBox, QTabWidget,
    QGroupBox, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from sql_init import get_db
from models.user_model import UserModel
from models.cari_hesap_model import CariHesapModel
from models.malzeme_model import MalzemeModel
from models.fatura_model import FaturaModel
import uuid


class AddUserDialog(QDialog):
    """Kullanıcı ekleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Kullanıcı Ekle")
        self.setFixedSize(400, 350)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        form.addRow("Ad Soyad *:", self.name_input)
        
        self.email_input = QLineEdit()
        form.addRow("E-posta *:", self.email_input)
        
        self.username_input = QLineEdit()
        form.addRow("Kullanıcı Adı:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form.addRow("Şifre *:", self.password_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "staff", "admin"])
        form.addRow("Rol:", self.role_combo)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'name': self.name_input.text(),
            'email': self.email_input.text(),
            'username': self.username_input.text() or None,
            'password': self.password_input.text(),
            'role': self.role_combo.currentText()
        }


class AddCariDialog(QDialog):
    """Cari hesap ekleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Cari Hesap Ekle")
        self.setFixedSize(500, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        scroll = QWidget()
        scroll_layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.unvan_input = QLineEdit()
        form.addRow("Unvan *:", self.unvan_input)
        
        self.vergi_no_input = QLineEdit()
        form.addRow("Vergi No *:", self.vergi_no_input)
        
        self.telefon_input = QLineEdit()
        form.addRow("Telefon:", self.telefon_input)
        
        self.email_input = QLineEdit()
        form.addRow("E-posta:", self.email_input)
        
        self.adres_input = QTextEdit()
        self.adres_input.setMaximumHeight(80)
        form.addRow("Adres:", self.adres_input)
        
        self.sehir_input = QLineEdit()
        form.addRow("Şehir:", self.sehir_input)
        
        self.ad_input = QLineEdit()
        form.addRow("Ad:", self.ad_input)
        
        scroll_layout.addLayout(form)
        scroll.setLayout(scroll_layout)
        layout.addWidget(scroll)
        
        buttons = QHBoxLayout()
        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'unvani': self.unvan_input.text(),
            'vergiNo': self.vergi_no_input.text(),
            'telefon': self.telefon_input.text(),
            'email': self.email_input.text(),
            'adres': self.adres_input.toPlainText(),
            'sehir': self.sehir_input.text(),
            'ad': self.ad_input.text()
        }


class AddMalzemeDialog(QDialog):
    """Malzeme ekleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Malzeme Ekle")
        self.setFixedSize(450, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.kod_input = QLineEdit()
        self.kod_input.setReadOnly(True)  # Otomatik oluşturulacak, değiştirilemez
        self.kod_input.setStyleSheet("background-color: #f0f0f0;")
        form.addRow("Kod (Otomatik):", self.kod_input)
        
        self.ad_input = QLineEdit()
        self.ad_input.textChanged.connect(self.on_ad_changed)  # Ad değiştiğinde kodu güncelle
        form.addRow("Ad *:", self.ad_input)
        
        self.birim_combo = QComboBox()
        self.birim_combo.addItems(["ADET", "Kg", "Ton", "Litre", "Metre", "m²", "m³"])
        form.addRow("Birim *:", self.birim_combo)
        
        self.stok_input = QDoubleSpinBox()
        self.stok_input.setMaximum(999999999)
        form.addRow("Stok:", self.stok_input)
        
        self.birim_fiyat_input = QDoubleSpinBox()
        self.birim_fiyat_input.setMaximum(999999999)
        form.addRow("Birim Fiyat:", self.birim_fiyat_input)
        
        self.kdv_input = QSpinBox()
        self.kdv_input.setMaximum(100)
        self.kdv_input.setValue(18)
        form.addRow("KDV %:", self.kdv_input)
        
        self.aciklama_input = QTextEdit()
        self.aciklama_input.setMaximumHeight(80)
        form.addRow("Açıklama:", self.aciklama_input)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def on_ad_changed(self, text):
        """Ad değiştiğinde otomatik kod oluştur"""
        if text.strip():
            try:
                from models.malzeme_model import MalzemeModel
                model = MalzemeModel()
                # Önce base kod oluştur (benzersizlik kontrolü olmadan)
                kod = model._generate_kod_from_name(text)
                self.kod_input.setText(kod)
            except:
                pass
    
    def get_data(self):
        # Kod otomatik oluşturulacak, boş gönder
        return {
            'kod': None,  # None gönder ki otomatik oluşturulsun
            'ad': self.ad_input.text(),
            'birim': self.birim_combo.currentText(),
            'stok': self.stok_input.value(),
            'birimFiyat': self.birim_fiyat_input.value(),
            'kdvOrani': self.kdv_input.value(),
            'aciklama': self.aciklama_input.toPlainText()
        }


class DatabaseManager(QMainWindow):
    """Veritabanı yönetim penceresi"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("GO WINGS - Veritabanı Yönetim Aracı")
        self.setGeometry(100, 100, 1200, 700)
        
        central = QWidget()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Veritabanı Yönetim Aracı")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Users tab
        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "Kullanıcılar")
        
        # Cari Hesap tab
        cari_tab = self.create_cari_tab()
        tabs.addTab(cari_tab, "Cari Hesaplar")
        
        # Malzeme tab
        malzeme_tab = self.create_malzeme_tab()
        tabs.addTab(malzeme_tab, "Malzemeler")
        
        layout.addWidget(tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)
    
    def create_users_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        btn_add = QPushButton("Yeni Kullanıcı Ekle")
        btn_add.clicked.connect(self.add_user)
        btn_refresh = QPushButton("Yenile")
        btn_refresh.clicked.connect(self.load_users)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Ad Soyad", "E-posta", "Kullanıcı Adı", "Rol", "Durum"])
        layout.addWidget(self.users_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_cari_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        btn_add = QPushButton("Yeni Cari Hesap Ekle")
        btn_add.clicked.connect(self.add_cari)
        btn_refresh = QPushButton("Yenile")
        btn_refresh.clicked.connect(self.load_cari)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.cari_table = QTableWidget()
        self.cari_table.setColumnCount(5)
        self.cari_table.setHorizontalHeaderLabels(["ID", "Unvan", "Vergi No", "Telefon", "E-posta"])
        layout.addWidget(self.cari_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_malzeme_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        btn_add = QPushButton("Yeni Malzeme Ekle")
        btn_add.clicked.connect(self.add_malzeme)
        btn_refresh = QPushButton("Yenile")
        btn_refresh.clicked.connect(self.load_malzeme)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.malzeme_table = QTableWidget()
        self.malzeme_table.setColumnCount(6)
        self.malzeme_table.setHorizontalHeaderLabels(["ID", "Kod", "Ad", "Birim", "Stok", "Birim Fiyat"])
        layout.addWidget(self.malzeme_table)
        
        widget.setLayout(layout)
        return widget
    
    def load_data(self):
        self.load_users()
        self.load_cari()
        self.load_malzeme()
    
    def load_users(self):
        try:
            model = UserModel()
            users = model.get_all()
            
            self.users_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user.get('id', ''))))
                self.users_table.setItem(row, 1, QTableWidgetItem(str(user.get('name', ''))))
                self.users_table.setItem(row, 2, QTableWidgetItem(str(user.get('email', ''))))
                self.users_table.setItem(row, 3, QTableWidgetItem(str(user.get('username', '') or '-')))
                self.users_table.setItem(row, 4, QTableWidgetItem(str(user.get('role', 'user'))))
                status = "Aktif" if user.get('is_active', 1) else "Pasif"
                self.users_table.setItem(row, 5, QTableWidgetItem(status))
            
            self.users_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kullanıcılar yüklenirken hata:\n{str(e)}")
    
    def load_cari(self):
        try:
            model = CariHesapModel()
            cari_list = model.get_all()
            
            self.cari_table.setRowCount(len(cari_list))
            for row, cari in enumerate(cari_list):
                self.cari_table.setItem(row, 0, QTableWidgetItem(str(cari.get('id', ''))))
                self.cari_table.setItem(row, 1, QTableWidgetItem(str(cari.get('unvani', ''))))
                self.cari_table.setItem(row, 2, QTableWidgetItem(str(cari.get('vergiNo', ''))))
                self.cari_table.setItem(row, 3, QTableWidgetItem(str(cari.get('telefon', '') or '-')))
                self.cari_table.setItem(row, 4, QTableWidgetItem(str(cari.get('email', '') or '-')))
            
            self.cari_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Cari hesaplar yüklenirken hata:\n{str(e)}")
    
    def load_malzeme(self):
        try:
            model = MalzemeModel()
            malzeme_list = model.get_all()
            
            self.malzeme_table.setRowCount(len(malzeme_list))
            for row, malzeme in enumerate(malzeme_list):
                self.malzeme_table.setItem(row, 0, QTableWidgetItem(str(malzeme.get('id', ''))))
                self.malzeme_table.setItem(row, 1, QTableWidgetItem(str(malzeme.get('kod', ''))))
                self.malzeme_table.setItem(row, 2, QTableWidgetItem(str(malzeme.get('ad', ''))))
                self.malzeme_table.setItem(row, 3, QTableWidgetItem(str(malzeme.get('birim', ''))))
                self.malzeme_table.setItem(row, 4, QTableWidgetItem(str(malzeme.get('stok', 0))))
                self.malzeme_table.setItem(row, 5, QTableWidgetItem(f"{malzeme.get('birimFiyat', 0):.2f} ₺"))
            
            self.malzeme_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Malzemeler yüklenirken hata:\n{str(e)}")
    
    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                if not data.get('name') or not data.get('email') or not data.get('password'):
                    QMessageBox.warning(self, "Uyarı", "Lütfen tüm zorunlu alanları doldurun")
                    return
                
                model = UserModel()
                model.create(data)
                QMessageBox.information(self, "Başarılı", "Kullanıcı başarıyla eklendi!")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kullanıcı eklenirken hata:\n{str(e)}")
    
    def add_cari(self):
        dialog = AddCariDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                if not data.get('unvani') or not data.get('vergiNo'):
                    QMessageBox.warning(self, "Uyarı", "Unvan ve Vergi No zorunludur")
                    return
                
                model = CariHesapModel()
                model.create(data)
                QMessageBox.information(self, "Başarılı", "Cari hesap başarıyla eklendi!")
                self.load_cari()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Cari hesap eklenirken hata:\n{str(e)}")
    
    def add_malzeme(self):
        dialog = AddMalzemeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                if not data.get('ad') or not data.get('birim'):
                    QMessageBox.warning(self, "Uyarı", "Ad ve Birim zorunludur")
                    return
                
                model = MalzemeModel()
                model.create(data)
                QMessageBox.information(self, "Başarılı", "Malzeme başarıyla eklendi!")
                self.load_malzeme()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Malzeme eklenirken hata:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Veritabanını başlat
    try:
        from sql_init import get_db
        db = get_db()
        print("Veritabanı başarıyla başlatıldı")
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Veritabanı başlatılamadı:\n{e}")
        sys.exit(1)
    
    window = DatabaseManager()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

