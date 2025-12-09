"""
Native Masa├╝st├╝ Uygulamas─▒ - PyQt5 ile Tam Native GUI
HTML kullanmadan, sadece PyQt5 widget'lar─▒ ile
"""
import sys
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QDialog, QFormLayout, QTextEdit, QComboBox, QMessageBox,
    QHeaderView, QStatusBar, QMenuBar, QMenu, QAction, QGroupBox,
    QGridLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QColor
from sql_init import get_db
from models.cari_hesap_model import CariHesapModel
from models.user_model import UserModel
import hashlib

class DatabaseWorker(QThread):
    """SQLite i┼ƒlemlerini ayr─▒ thread'de yapan worker"""
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, operation, data=None):
        super().__init__()
        self.operation = operation
        self.data = data
        
    def run(self):
        try:
            model = CariHesapModel()
            if self.operation == 'get_all':
                cari_list = model.get_all()
                self.data_loaded.emit(cari_list)
            elif self.operation == 'create':
                result = model.create(self.data)
                self.data_loaded.emit([result])
            elif self.operation == 'update':
                result = model.update(self.data['id'], self.data)
                self.data_loaded.emit([result])
            elif self.operation == 'delete':
                model.delete(self.data['id'])
                self.data_loaded.emit([])
        except Exception as e:
            self.error_occurred.emit(str(e))

class DashboardWidget(QWidget):
    """Ana dashboard ekran─▒"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Ba┼ƒl─▒k
        title = QLabel("MUBA - Cari Hesap Y├╢netim Sistemi")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # K─▒sayollar grubu
        shortcuts_group = QGroupBox("K─▒sayollar─▒m")
        shortcuts_layout = QGridLayout()
        shortcuts_group.setLayout(shortcuts_layout)
        
        # K─▒sayol butonlar─▒
        btn_satis = QPushButton("Sat─▒┼ƒ Faturalar─▒")
        btn_satis.setMinimumHeight(80)
        btn_satis.setStyleSheet("font-size: 14px; font-weight: bold;")
        btn_satis.clicked.connect(lambda: self.parent_window.show_fatura_list())
        
        btn_cari = QPushButton("Cari Hesap")
        btn_cari.setMinimumHeight(80)
        btn_cari.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #667eea; color: white;")
        btn_cari.clicked.connect(lambda: self.parent_window.show_cari_list())
        
        btn_malzeme = QPushButton("Malzemeler")
        btn_malzeme.setMinimumHeight(80)
        btn_malzeme.setStyleSheet("font-size: 14px; font-weight: bold;")
        btn_malzeme.clicked.connect(lambda: self.parent_window.show_malzeme_list())
        
        btn_fatura_gonder = QPushButton("Fatura G├╢nder")
        btn_fatura_gonder.setMinimumHeight(80)
        btn_fatura_gonder.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #ff6b6b; color: white;")
        btn_fatura_gonder.clicked.connect(lambda: self.parent_window.show_fatura_gonder())
        
        btn_ekstre = QPushButton("Cari Hesap\nEkstresi")
        btn_ekstre.setMinimumHeight(80)
        btn_ekstre.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #28a745; color: white;")
        btn_ekstre.clicked.connect(lambda: self.parent_window.show_cari_ekstre())
        
        btn_tahsilat = QPushButton("Tahsilat\nGiri┼ƒi")
        btn_tahsilat.setMinimumHeight(80)
        btn_tahsilat.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #ffc107; color: black;")
        btn_tahsilat.clicked.connect(lambda: self.parent_window.show_tahsilat_giris())
        
        btn_finansal = QPushButton("Finansal\nAnaliz")
        btn_finansal.setMinimumHeight(80)
        btn_finansal.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #17a2b8; color: white;")
        btn_finansal.clicked.connect(lambda: self.parent_window.show_finansal_analiz())
        
        btn_alim_faturasi = QPushButton("Al─▒m\nFaturas─▒")
        btn_alim_faturasi.setMinimumHeight(80)
        btn_alim_faturasi.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #6f42c1; color: white;")
        btn_alim_faturasi.clicked.connect(lambda: self.parent_window.show_purchase_invoice())
        
        btn_tahsilat_list = QPushButton("Tahsilat\nListesi")
        btn_tahsilat_list.setMinimumHeight(80)
        btn_tahsilat_list.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #17a2b8; color: white;")
        btn_tahsilat_list.clicked.connect(lambda: self.parent_window.show_tahsilat_list())
        
        btn_odemeler = QPushButton("├ûdemeler")
        btn_odemeler.setMinimumHeight(80)
        btn_odemeler.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #dc3545; color: white;")
        btn_odemeler.clicked.connect(lambda: self.parent_window.show_odemeler())
        
        btn_hesap_makinesi = QPushButton("Hesap\nMakinesi")
        btn_hesap_makinesi.setMinimumHeight(80)
        btn_hesap_makinesi.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #6c757d; color: white;")
        btn_hesap_makinesi.clicked.connect(lambda: self.parent_window.show_hesap_makinesi())
        
        btn_ai_model = QPushButton("≡ƒñû AI\n├ûdeme Tahmini")
        btn_ai_model.setMinimumHeight(80)
        btn_ai_model.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e91e63; color: white;")
        btn_ai_model.clicked.connect(lambda: self.parent_window.show_ai_payment_predictor())
        
        shortcuts_layout.addWidget(btn_satis, 0, 0)
        shortcuts_layout.addWidget(btn_cari, 0, 1)
        shortcuts_layout.addWidget(btn_malzeme, 0, 2)
        shortcuts_layout.addWidget(btn_fatura_gonder, 1, 0)
        shortcuts_layout.addWidget(btn_ekstre, 1, 1)
        shortcuts_layout.addWidget(btn_tahsilat, 1, 2)
        shortcuts_layout.addWidget(btn_finansal, 2, 0)
        shortcuts_layout.addWidget(btn_alim_faturasi, 2, 1)
        shortcuts_layout.addWidget(btn_tahsilat_list, 2, 2)
        shortcuts_layout.addWidget(btn_odemeler, 3, 0)
        shortcuts_layout.addWidget(btn_hesap_makinesi, 3, 1)
        shortcuts_layout.addWidget(btn_ai_model, 3, 2)
        
        layout.addWidget(shortcuts_group)
        layout.addStretch()
        
        self.setLayout(layout)

class CariHesapEkleDialog(QDialog):
    """Cari hesap ekleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Cari Hesap Ekle")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # ─░sim
        self.isim_input = QLineEdit()
        self.isim_input.setPlaceholderText("├ûrn: ABC ┼₧irketi")
        form_layout.addRow("─░sim / ┼₧irket Ad─▒ *:", self.isim_input)
        
        # Vergi No
        self.vergi_no_input = QLineEdit()
        self.vergi_no_input.setPlaceholderText("├ûrn: 1234567890")
        form_layout.addRow("Vergi Numaras─▒ *:", self.vergi_no_input)
        
        # Telefon
        self.telefon_input = QLineEdit()
        self.telefon_input.setPlaceholderText("├ûrn: +90 555 123 45 67")
        form_layout.addRow("Telefon *:", self.telefon_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("├ûrn: info@example.com")
        form_layout.addRow("E-Posta *:", self.email_input)
        
        # Adres
        self.adres_input = QTextEdit()
        self.adres_input.setMaximumHeight(80)
        self.adres_input.setPlaceholderText("Tam adres bilgisi")
        form_layout.addRow("Adres *:", self.adres_input)
        
        # ┼₧ehir
        self.sehir_combo = QComboBox()
        self.sehir_combo.addItem("┼₧ehir Se├ºiniz", "")
        sehirler = [
            "Adana", "Ad─▒yaman", "Afyonkarahisar", "A─ƒr─▒", "Amasya", "Ankara",
            "Antalya", "Artvin", "Ayd─▒n", "Bal─▒kesir", "Bilecik", "Bing├╢l",
            "Bitlis", "Bolu", "Burdur", "Bursa", "├çanakkale", "├çank─▒r─▒",
            "├çorum", "Denizli", "Diyarbak─▒r", "Edirne", "Elaz─▒─ƒ", "Erzincan",
            "Erzurum", "Eski┼ƒehir", "Gaziantep", "Giresun", "G├╝m├╝┼ƒhane",
            "Hakkari", "Hatay", "Isparta", "Mersin", "─░stanbul", "─░zmir",
            "Kars", "Kastamonu", "Kayseri", "K─▒rklareli", "K─▒r┼ƒehir", "Kocaeli",
            "Konya", "K├╝tahya", "Malatya", "Manisa", "Kahramanmara┼ƒ", "Mardin",
            "Mu─ƒla", "Mu┼ƒ", "Nev┼ƒehir", "Ni─ƒde", "Ordu", "Rize", "Sakarya",
            "Samsun", "Siirt", "Sinop", "Sivas", "Tekirda─ƒ", "Tokat",
            "Trabzon", "Tunceli", "┼₧anl─▒urfa", "U┼ƒak", "Van", "Yozgat",
            "Zonguldak", "Aksaray", "Bayburt", "Karaman", "K─▒r─▒kkale",
            "Batman", "┼₧─▒rnak", "Bart─▒n", "Ardahan", "I─ƒd─▒r", "Yalova",
            "Karab├╝k", "Kilis", "Osmaniye", "D├╝zce"
        ]
        for sehir in sehirler:
            self.sehir_combo.addItem(sehir, sehir)
        form_layout.addRow("┼₧ehir *:", self.sehir_combo)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_data(self):
        """Form verilerini d├╢nd├╝r"""
        return {
            'unvani': self.isim_input.text().strip(),
            'vergiNo': self.vergi_no_input.text().strip(),
            'telefon': self.telefon_input.text().strip(),
            'email': self.email_input.text().strip(),
            'adres': self.adres_input.toPlainText().strip(),
            'sehir': self.sehir_combo.currentData(),
            'iletisim': {
                'il': self.sehir_combo.currentData() or '',
                'ulke': 'T├£RK─░YE'
            },
            'statusu': 'Kullan─▒mda'
        }
        
    def validate(self):
        """Form validasyonu"""
        if not self.isim_input.text().strip():
            QMessageBox.warning(self, "Hata", "─░sim / ┼₧irket Ad─▒ zorunludur!")
            self.isim_input.setFocus()
            return False
        if not self.vergi_no_input.text().strip():
            QMessageBox.warning(self, "Hata", "Vergi Numaras─▒ zorunludur!")
            self.vergi_no_input.setFocus()
            return False
        if not self.telefon_input.text().strip():
            QMessageBox.warning(self, "Hata", "Telefon zorunludur!")
            self.telefon_input.setFocus()
            return False
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Hata", "E-Posta zorunludur!")
            self.email_input.setFocus()
            return False
        # Email format kontrol├╝
        if '@' not in email or '.' not in email.split('@')[1]:
            QMessageBox.warning(self, "Hata", "Ge├ºerli bir e-posta adresi giriniz!")
            self.email_input.setFocus()
            return False
        if not self.adres_input.toPlainText().strip():
            QMessageBox.warning(self, "Hata", "Adres zorunludur!")
            self.adres_input.setFocus()
            return False
        if not self.sehir_combo.currentData():
            QMessageBox.warning(self, "Hata", "┼₧ehir se├ºimi zorunludur!")
            self.sehir_combo.setFocus()
            return False
        return True

class CariHesapListWidget(QWidget):
    """Cari hesap listesi widget'─▒"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.cari_list = []
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # ├£st toolbar
        toolbar = QHBoxLayout()
        
        # Geri butonu
        btn_geri = QPushButton("ΓåÉ Geri")
        btn_geri.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 15px; font-weight: bold;")
        btn_geri.clicked.connect(lambda: self.parent_window.show_dashboard())
        toolbar.addWidget(btn_geri)
        
        title = QLabel("Cari Hesaplar")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        btn_yeni = QPushButton("Yeni Cari Hesap Ekle")
        btn_yeni.setStyleSheet("background-color: #667eea; color: white; padding: 8px 15px; font-weight: bold;")
        btn_yeni.clicked.connect(self.yeni_cari_ekle)
        toolbar.addWidget(btn_yeni)
        
        layout.addLayout(toolbar)
        
        # Arama ├ºubu─ƒu
        search_layout = QHBoxLayout()
        search_label = QLabel("Ara:")
        search_label.setStyleSheet("font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("┼₧irket ad─▒, vergi numaras─▒ veya ad ile ara...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Vergi Numaras─▒", "┼₧irket Ad─▒", "Telefon", "E-Posta", 
            "Bor├º Durumu", "Adres", "NOT1"
        ])
        
        # Tablo ayarlar─▒
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemDoubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_data(self):
        """Cari hesaplar─▒ y├╝kle"""
        self.worker = DatabaseWorker('get_all')
        self.worker.data_loaded.connect(self.on_data_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
        
    def on_data_loaded(self, data):
        """Veri y├╝klendi─ƒinde"""
        self.cari_list = data
        self.all_cari_data = data  # T├╝m veriyi sakla
        self.update_table(data)
    
    def update_table(self, data):
        """Tabloyu g├╝ncelle"""
        self.table.setRowCount(len(data))
        
        for row, cari in enumerate(data):
            # Vergi numaras─▒n─▒ maskelenmi┼ƒ g├╢ster
            vergi_no_hash = cari.get('vergiNoHash', '')
            if vergi_no_hash:
                vergi_no_display = vergi_no_hash[:6] + '****'
            else:
                vergi_no_display = str(cari.get('vergiNo', '-'))
            self.table.setItem(row, 0, QTableWidgetItem(vergi_no_display))
            
            self.table.setItem(row, 1, QTableWidgetItem(cari.get('unvani', '-')))
            self.table.setItem(row, 2, QTableWidgetItem(cari.get('telefon', '-')))
            self.table.setItem(row, 3, QTableWidgetItem(cari.get('email', '-')))
            
            # Bor├º durumu
            borc_durumu = self.calculate_borc_durumu(cari)
            borc_item = QTableWidgetItem(borc_durumu)
            # B (bor├º) varsa k─▒rm─▒z─▒, A (alacak) varsa ye┼ƒil
            if borc_durumu.startswith('B'):
                borc_item.setForeground(QColor(220, 53, 69))  # K─▒rm─▒z─▒
            elif borc_durumu.startswith('A'):
                borc_item.setForeground(QColor(40, 167, 69))  # Ye┼ƒil
            else:
                borc_item.setForeground(QColor(108, 117, 125))  # Gri
            self.table.setItem(row, 4, borc_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(cari.get('adres', '-')))
            
            not1 = ''
            if cari.get('notlar') and cari['notlar'].get('not1'):
                not1 = cari['notlar']['not1']
                if len(not1) > 50:
                    not1 = not1[:50] + '...'
            self.table.setItem(row, 6, QTableWidgetItem(not1 or '-'))
    
    def calculate_borc_durumu(self, cari):
        """Bor├º durumunu hesapla"""
        borc = cari.get('borc', 0)
        alacak = cari.get('alacak', 0)
        bakiye = borc - alacak
        
        if bakiye > 0:
            # M├╝┼ƒteriye borcumuz var ΓåÆ B
            return f"B ({bakiye:.2f} Γé║)"
        elif bakiye < 0:
            # M├╝┼ƒteriden alaca─ƒ─▒m─▒z var ΓåÆ A
            return f"A ({abs(bakiye):.2f} Γé║)"
        else:
            # Bakiye 0
            return "-"
    
    def on_search(self, text):
        """Arama yap"""
        if not text or not text.strip():
            self.update_table(self.all_cari_data)
            return
        
        query = text.lower().strip()
        filtered = []
        for cari in self.all_cari_data:
            unvani = cari.get('unvani', '').lower()
            vergi_no = str(cari.get('vergiNo', '')).lower()
            vergi_no_hash = cari.get('vergiNoHash', '').lower()
            ad = cari.get('ad', '').lower()
            
            if (query in unvani or
                query in vergi_no or
                query in vergi_no_hash[:6] or
                query in ad):
                filtered.append(cari)
        
        self.update_table(filtered)
            
    def on_error(self, error_msg):
        """Hata olu┼ƒtu─ƒunda"""
        QMessageBox.critical(self, "Hata", f"Veri y├╝klenirken hata olu┼ƒtu:\n{error_msg}")
        
    def yeni_cari_ekle(self):
        """Yeni cari hesap ekle"""
        dialog = CariHesapEkleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.validate():
                data = dialog.get_data()
                self.save_cari(data)
                
    def save_cari(self, data):
        """Cari hesab─▒ kaydet"""
        self.worker = DatabaseWorker('create', data)
        self.worker.data_loaded.connect(self.on_save_success)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
        
    def on_save_success(self, data):
        """Kay─▒t ba┼ƒar─▒l─▒"""
        QMessageBox.information(self, "Ba┼ƒar─▒l─▒", "Cari hesap ba┼ƒar─▒yla eklendi!")
        self.load_data()
        
    def show_context_menu(self, position):
        """Sa─ƒ t─▒k men├╝s├╝"""
        item = self.table.itemAt(position)
        if item:
            row = item.row()
            cari_id = self.cari_list[row]['id']
            
            menu = QMenu(self)
            not_action = menu.addAction("Not Ekle/D├╝zenle")
            delete_action = menu.addAction("Sil")
            
            action = menu.exec_(self.table.viewport().mapToGlobal(position))
            
            if action == not_action:
                self.edit_not(cari_id, row)
            elif action == delete_action:
                self.delete_cari(cari_id)
                
    def edit_not(self, cari_id, row):
        """Not d├╝zenle - Sadece admin"""
        # Admin kontrol├╝
        if not self.parent_window or not self.parent_window.current_user:
            QMessageBox.warning(self, "Uyar─▒", "Giri┼ƒ yapman─▒z gerekiyor!")
            return
        
        user_role = self.parent_window.current_user.get('role', 'user')
        if user_role != 'admin':
            QMessageBox.warning(self, "Yetkisiz Eri┼ƒim", "Bu i┼ƒlem i├ºin admin yetkisi gereklidir!")
            return
        
        cari = self.cari_list[row]
        notlar = cari.get('notlar', {})
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Not Ekle/D├╝zenle")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        not1_input = QTextEdit()
        not1_input.setPlainText(notlar.get('not1', ''))
        not1_input.setMaximumHeight(100)
        form_layout.addRow("NOT1:", not1_input)
        
        not2_input = QTextEdit()
        not2_input.setPlainText(notlar.get('not2', ''))
        not2_input.setMaximumHeight(100)
        form_layout.addRow("NOT2:", not2_input)
        
        not3_input = QTextEdit()
        not3_input.setPlainText(notlar.get('not3', ''))
        not3_input.setMaximumHeight(100)
        form_layout.addRow("NOT3:", not3_input)
        
        ozel_not_input = QTextEdit()
        ozel_not_input.setPlainText(notlar.get('ozelNot', ''))
        ozel_not_input.setMaximumHeight(150)
        form_layout.addRow("├ûzel Not:", ozel_not_input)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            cari['notlar'] = {
                'not1': not1_input.toPlainText(),
                'not2': not2_input.toPlainText(),
                'not3': not3_input.toPlainText(),
                'ozelNot': ozel_not_input.toPlainText()
            }
            self.update_cari(cari)
            
    def update_cari(self, data):
        """Cari hesab─▒ g├╝ncelle - Sadece admin"""
        # Admin kontrol├╝
        if not self.parent_window or not self.parent_window.current_user:
            QMessageBox.warning(self, "Uyar─▒", "Giri┼ƒ yapman─▒z gerekiyor!")
            return
        
        user_role = self.parent_window.current_user.get('role', 'user')
        if user_role != 'admin':
            QMessageBox.warning(self, "Yetkisiz Eri┼ƒim", "Bu i┼ƒlem i├ºin admin yetkisi gereklidir!")
            return
        
        self.worker = DatabaseWorker('update', data)
        self.worker.data_loaded.connect(self.on_update_success)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
        
    def on_update_success(self, data):
        """G├╝ncelleme ba┼ƒar─▒l─▒"""
        QMessageBox.information(self, "Ba┼ƒar─▒l─▒", "Notlar ba┼ƒar─▒yla kaydedildi!")
        self.load_data()
        
    def delete_cari(self, cari_id):
        """Cari hesab─▒ sil"""
        reply = QMessageBox.question(
            self, "Sil", "Bu cari hesab─▒ silmek istedi─ƒinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.worker = DatabaseWorker('delete', {'id': cari_id})
            self.worker.data_loaded.connect(self.on_delete_success)
            self.worker.error_occurred.connect(self.on_error)
            self.worker.start()
            
    def on_delete_success(self, data):
        """Silme ba┼ƒar─▒l─▒"""
        QMessageBox.information(self, "Ba┼ƒar─▒l─▒", "Cari hesap ba┼ƒar─▒yla silindi!")
        self.load_data()
    
    def on_double_click(self, item):
        """├çift t─▒klama - ┼₧irket detaylar─▒n─▒ g├╢ster"""
        row = item.row()
        if row < len(self.cari_list):
            cari = self.cari_list[row]
            self.show_cari_detail(cari)
    
    def show_cari_detail(self, cari):
        """Cari hesap detaylar─▒n─▒ g├╢ster"""
        from views.cari_hesap_detail_view import CariHesapDetailView
        from controllers.fatura_controller import FaturaController
        
        detail_view = CariHesapDetailView(cari, self)
        
        # Faturalar─▒ y├╝kle
        fatura_controller = FaturaController('get_by_cari_id', {'cari_id': cari['id']})
        fatura_controller.data_loaded.connect(lambda faturalar: detail_view.display_faturalar(faturalar))
        fatura_controller.error_occurred.connect(lambda err: detail_view.display_faturalar([]))
        fatura_controller.start()
        
        # Dialog'u g├╢ster
        detail_view.exec_()

class AddUserDialog(QDialog):
    """Yeni kullan─▒c─▒ ekleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Kullan─▒c─▒ Ekle")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        form.addRow("Ad Soyad:", self.name_input)
        
        self.email_input = QLineEdit()
        form.addRow("E-posta:", self.email_input)
        
        self.username_input = QLineEdit()
        form.addRow("Kullan─▒c─▒ Ad─▒:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form.addRow("┼₧ifre:", self.password_input)
        
        self.role_input = QComboBox()
        self.role_input.addItems(['user', 'staff', 'admin'])
        form.addRow("Rol:", self.role_input)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'name': self.name_input.text(),
            'email': self.email_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'role': self.role_input.currentText()
        }

class UserManagementDialog(QDialog):
    """Kullan─▒c─▒ y├╢netimi dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kullan─▒c─▒ Y├╢netimi")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        
        self.user_model = UserModel()
        
        layout = QVBoxLayout()
        
        # Ba┼ƒl─▒k
        title = QLabel("Kullan─▒c─▒ Y├╢netimi")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Toolbar
        toolbar = QHBoxLayout()
        btn_add = QPushButton("Yeni Kullan─▒c─▒ Ekle")
        btn_add.setStyleSheet("background-color: #28a745; color: white; padding: 8px 15px; font-weight: bold;")
        btn_add.clicked.connect(self.add_user)
        
        btn_sil = QPushButton("Se├ºili Kullan─▒c─▒lar─▒ Sil")
        btn_sil.setStyleSheet("background-color: #dc3545; color: white; padding: 8px 15px; font-weight: bold;")
        btn_sil.clicked.connect(self.delete_selected_users)
        
        btn_refresh = QPushButton("Yenile")
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px 15px; font-weight: bold;")
        btn_refresh.clicked.connect(self.load_users)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_sil)
        toolbar.addWidget(btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Tablo
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Ad", "E-posta", "Kullan─▒c─▒ Ad─▒", "Rol", "Durum"])
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.users_table.customContextMenuRequested.connect(self.show_user_context_menu)
        
        # Header ayarlar─▒
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.users_table)
        
        self.setLayout(layout)
        
        # Kullan─▒c─▒lar─▒ y├╝kle
        self.load_users()
    
    def load_users(self):
        """Kullan─▒c─▒lar─▒ y├╝kle"""
        try:
            users = self.user_model.get_all()
            self.users = users  # Kullan─▒c─▒lar─▒ sakla
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user.get('id', '-'))))
                self.users_table.setItem(row, 1, QTableWidgetItem(user.get('name', '-')))
                self.users_table.setItem(row, 2, QTableWidgetItem(user.get('email', '-')))
                self.users_table.setItem(row, 3, QTableWidgetItem(user.get('username', '-') or '-'))
                
                role_item = QTableWidgetItem(user.get('role', 'user'))
                if user.get('role') == 'admin':
                    role_item.setForeground(QColor(200, 0, 0))
                elif user.get('role') == 'staff':
                    role_item.setForeground(QColor(255, 165, 0))
                self.users_table.setItem(row, 4, role_item)
                
                status = "Aktif" if user.get('is_active', 1) else "Pasif"
                status_item = QTableWidgetItem(status)
                if not user.get('is_active', 1):
                    status_item.setForeground(QColor(128, 128, 128))
                self.users_table.setItem(row, 5, status_item)
            
            self.users_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kullan─▒c─▒lar y├╝klenirken hata olu┼ƒtu:\n{str(e)}")
    
    def add_user(self):
        """Yeni kullan─▒c─▒ ekle"""
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                if not data.get('name') or not data.get('email') or not data.get('password'):
                    QMessageBox.warning(self, "Uyar─▒", "Ad, e-posta ve ┼ƒifre alanlar─▒ zorunludur!")
                    return
                
                user = self.user_model.create(data)
                QMessageBox.information(self, "Ba┼ƒar─▒l─▒", f"Kullan─▒c─▒ ba┼ƒar─▒yla eklendi!\n\nAd: {user.get('name')}\nE-posta: {user.get('email')}")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kullan─▒c─▒ eklenirken hata olu┼ƒtu:\n{str(e)}")
    
    def show_user_context_menu(self, position):
        """Kullan─▒c─▒ tablosu i├ºin context menu"""
        item = self.users_table.itemAt(position)
        if item:
            row = item.row()
            if hasattr(self, 'users') and row < len(self.users):
                user = self.users[row]
                user_id = user.get('id')
                user_name = user.get('name', 'Kullan─▒c─▒')
                
                from PyQt5.QtWidgets import QMenu
                menu = QMenu(self)
                delete_action = menu.addAction("≡ƒùæ∩╕Å Bu Kullan─▒c─▒y─▒ Sil")
                action = menu.exec_(self.users_table.viewport().mapToGlobal(position))
                if action == delete_action:
                    self.delete_user(user_id, user_name)
    
    def delete_user(self, user_id, user_name):
        """Kullan─▒c─▒y─▒ sil"""
        reply = QMessageBox.question(
            self, 'Onay',
            f'"{user_name}" kullan─▒c─▒s─▒n─▒ silmek istedi─ƒinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.user_model.delete(user_id)
                QMessageBox.information(self, "Ba┼ƒar─▒l─▒", f'"{user_name}" kullan─▒c─▒s─▒ ba┼ƒar─▒yla silindi!')
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kullan─▒c─▒ silinirken hata olu┼ƒtu:\n{str(e)}")
    
    def delete_selected_users(self):
        """Se├ºili kullan─▒c─▒lar─▒ sil"""
        if not hasattr(self, 'users'):
            QMessageBox.warning(self, "Uyar─▒", "├ûnce kullan─▒c─▒lar─▒ y├╝kleyin!")
            return
        
        selected_rows = set()
        for item in self.users_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Uyar─▒", "L├╝tfen silmek istedi─ƒiniz kullan─▒c─▒lar─▒ se├ºin!")
            return
        
        user_ids = []
        user_names = []
        for row in selected_rows:
            if row < len(self.users):
                user = self.users[row]
                user_ids.append(user.get('id'))
                user_names.append(user.get('name', 'Kullan─▒c─▒'))
        
        if not user_ids:
            QMessageBox.warning(self, "Uyar─▒", "Silinecek kullan─▒c─▒ bulunamad─▒!")
            return
        
        reply = QMessageBox.question(
            self, 'Onay',
            f'{len(user_ids)} adet kullan─▒c─▒y─▒ silmek istedi─ƒinize emin misiniz?\n\n'
            f'Kullan─▒c─▒lar: {", ".join(user_names[:5])}{"..." if len(user_names) > 5 else ""}',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                deleted_count = 0
                for user_id in user_ids:
                    try:
                        self.user_model.delete(user_id)
                        deleted_count += 1
                    except Exception as e:
                        QMessageBox.warning(self, "Uyar─▒", f"Kullan─▒c─▒ silinirken hata: {str(e)}")
                
                QMessageBox.information(self, "Ba┼ƒar─▒l─▒", f"{deleted_count} adet kullan─▒c─▒ ba┼ƒar─▒yla silindi!")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kullan─▒c─▒lar silinirken hata olu┼ƒtu:\n{str(e)}")

class MainWindow(QMainWindow):
    """Ana pencere"""
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.init_ui()
        
        # Login kontrol├╝
        self.check_login()
        
    def check_login(self):
        """Login kontrol├╝"""
        from views.login_view import LoginView
        login_dialog = LoginView(self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.current_user = login_dialog.logged_in_user
            self.update_ui_for_user()
        else:
            # Login iptal edildiyse uygulamay─▒ kapat
            self.close()
    
    def update_ui_for_user(self):
        """Kullan─▒c─▒ya g├╢re UI'yi g├╝ncelle"""
        if self.current_user:
            user_name = self.current_user.get('name', 'Kullan─▒c─▒')
            user_role = self.current_user.get('role', 'user')
            self.status_bar.showMessage(f"Ho┼ƒ geldiniz, {user_name} ({user_role.upper()})")
            self.create_menu_bar()  # Men├╝y├╝ yeniden olu┼ƒtur (rol bazl─▒)
        
    def init_ui(self):
        self.setWindowTitle("MUBA - Cari Hesap Y├╢netim Sistemi")
        self.setGeometry(100, 100, 1400, 900)
        
        # Men├╝ ├ºubu─ƒu
        self.create_menu_bar()
        
        # Durum ├ºubu─ƒu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Haz─▒r")
        
        # Ana widget
        self.show_dashboard()
        
    def create_menu_bar(self):
        """Men├╝ ├ºubu─ƒunu olu┼ƒtur"""
        menubar = self.menuBar()
        menubar.clear()  # ├ûnceki men├╝leri temizle
        
        # Dosya men├╝s├╝
        file_menu = menubar.addMenu('Dosya')
        
        logout_action = QAction('├ç─▒k─▒┼ƒ Yap', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Uygulamadan ├ç─▒k', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Kullan─▒c─▒ men├╝s├╝ (Admin/Staff i├ºin)
        if self.current_user and self.current_user.get('role') in ['admin', 'staff']:
            user_menu = menubar.addMenu('Kullan─▒c─▒lar')
            user_list_action = QAction('Kullan─▒c─▒ Listesi', self)
            user_list_action.triggered.connect(self.show_user_list)
            user_menu.addAction(user_list_action)
            
            # Admin men├╝s├╝
            admin_menu = menubar.addMenu('Admin')
            admin_logs_action = QAction('≡ƒ¢í∩╕Å Admin Paneli', self)
            admin_logs_action.triggered.connect(self.show_admin_panel)
            admin_menu.addAction(admin_logs_action)
        
        # Ayarlar men├╝s├╝
        settings_menu = menubar.addMenu('Ayarlar')
        gmail_action = QAction('Gmail Ayarlar─▒', self)
        gmail_action.triggered.connect(self.show_gmail_settings)
        settings_menu.addAction(gmail_action)
        
        # Yard─▒m men├╝s├╝
        help_menu = menubar.addMenu('Yard─▒m')
        about_action = QAction('Hakk─▒nda', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def logout(self):
        """├ç─▒k─▒┼ƒ yap"""
        reply = QMessageBox.question(
            self, '├ç─▒k─▒┼ƒ', '├ç─▒k─▒┼ƒ yapmak istedi─ƒinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.check_login()
    
    def show_user_list(self):
        """Kullan─▒c─▒ listesini g├╢ster (Admin/Staff)"""
        dialog = UserManagementDialog(self)
        dialog.exec_()
        
    def show_dashboard(self):
        """Dashboard'u g├╢ster"""
        # Eski DashboardWidget yerine yeni DashboardView kullan
        try:
            from views.dashboard_view import DashboardView
            self.dashboard = DashboardView(self)
            self.dashboard.set_cari_button_callback(self.show_cari_list)
            self.dashboard.set_malzeme_button_callback(self.show_malzeme_list)
            self.dashboard.set_satis_button_callback(self.show_fatura_list)
            self.dashboard.set_ekstre_button_callback(self.show_cari_ekstre)
            self.dashboard.set_tahsilat_button_callback(self.show_tahsilat_giris)
            self.dashboard.set_hesap_makinesi_button_callback(self.show_hesap_makinesi)
            self.dashboard.set_finansal_button_callback(self.show_finansal_analiz)
            self.dashboard.set_alim_faturasi_button_callback(self.show_purchase_invoice)
            self.dashboard.set_tahsilat_list_button_callback(self.show_tahsilat_list)
            self.dashboard.set_fatura_gonder_button_callback(self.show_fatura_gonder)
            self.dashboard.set_ai_model_button_callback(self.show_ai_payment_predictor)
            self.dashboard.set_odemeler_button_callback(self.show_odemeler)
        except Exception as e:
            # Fallback: Eski DashboardWidget kullan
            print(f"DashboardView y├╝klenemedi, DashboardWidget kullan─▒l─▒yor: {e}")
            import traceback
            traceback.print_exc()
            self.dashboard = DashboardWidget(self)
        self.setCentralWidget(self.dashboard)
        self.status_bar.showMessage("Ana Sayfa")
        # KPI ve son hareketleri doldur (widget'─▒n haz─▒r olmas─▒n─▒ bekle)
        QTimer.singleShot(300, self._refresh_dashboard_metrics)
        QTimer.singleShot(300, self._refresh_recent_activity)
        
    def show_cari_list(self):
        """Cari hesap listesini g├╢ster"""
        self.cari_list = CariHesapListWidget(self)
        self.setCentralWidget(self.cari_list)
        self.status_bar.showMessage("Cari Hesaplar")
    
    def show_fatura_list(self):
        """Fatura listesini g├╢ster"""
        try:
            from views.fatura_list_view import FaturaListView
            from controllers.fatura_list_controller import FaturaListController
            
            self.fatura_list_view = FaturaListView(self)
            self.fatura_list_controller = FaturaListController(self.fatura_list_view, self)
            self.setCentralWidget(self.fatura_list_view)
            self.status_bar.showMessage("Sat─▒┼ƒ Faturalar─▒")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Fatura listesi a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_malzeme_list(self):
        """Malzeme listesini g├╢ster"""
        from views.malzeme_list_view import MalzemeListView
        from controllers.malzeme_list_controller import MalzemeListController
        
        self.malzeme_list_view = MalzemeListView(self)
        self.malzeme_list_controller = MalzemeListController(self.malzeme_list_view, self)
        self.setCentralWidget(self.malzeme_list_view)
        self.status_bar.showMessage("Malzemeler")
    
    def show_fatura_gonder(self):
        """Fatura g├╢nderme ekran─▒n─▒ g├╢ster"""
        from views.fatura_gonder_view import FaturaGonderView
        from controllers.fatura_gonder_controller import FaturaGonderController
        
        self.fatura_gonder_view = FaturaGonderView(self)
        self.fatura_gonder_controller = FaturaGonderController(self.fatura_gonder_view, self)
        self.setCentralWidget(self.fatura_gonder_view)
        self.status_bar.showMessage("Fatura G├╢nder - E-Posta ─░le G├╢nderim")
    
    def show_cari_ekstre(self):
        """Cari hesap ekstresini g├╢ster"""
        try:
            from views.cari_hesap_ekstre_view import CariHesapEkstreView
            from controllers.cari_hesap_ekstre_controller import CariHesapEkstreListController
            
            self.cari_ekstre_view = CariHesapEkstreView(self)
            self.cari_ekstre_controller = CariHesapEkstreListController(self.cari_ekstre_view, self)
            self.setCentralWidget(self.cari_ekstre_view)
            self.status_bar.showMessage("Cari Hesap Ekstresi")
        except Exception as e:
            error_msg = f"Ekstre a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", error_msg)
    
    def show_tahsilat_giris(self):
        """Tahsilat giri┼ƒ ekran─▒n─▒ g├╢ster"""
        try:
            from views.tahsilat_giris_view import TahsilatGirisView
            # Tkinter ekran─▒n─▒ PyQt5 penceresi i├ºinde a├º
            tahsilat_view = TahsilatGirisView(parent=self)
            tahsilat_view.run()
        except Exception as e:
            error_msg = f"Tahsilat ekran─▒ a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", error_msg)
    
    def show_tahsilat_list(self):
        """Tahsilat listesi ekran─▒n─▒ g├╢ster"""
        try:
            from views.tahsilat_list_view import TahsilatListView
            from controllers.tahsilat_list_controller import TahsilatListController
            
            tahsilat_view = TahsilatListView(self)
            self.tahsilat_list_controller = TahsilatListController(self)
            self.setCentralWidget(self.tahsilat_list_controller.view)
            self.status_bar.showMessage("Tahsilat Listesi")
        except Exception as e:
            error_msg = f"Tahsilat listesi a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", error_msg)
    
    def show_odemeler(self):
        """├ûdemeler ekran─▒n─▒ g├╢ster"""
        try:
            from views.odeme_list_view import OdemeListView
            from controllers.odeme_list_controller import OdemeListController
            
            odeme_view = OdemeListView(self)
            self.odeme_list_controller = OdemeListController(self)
            self.odeme_list_controller.set_view(odeme_view)
            self.setCentralWidget(odeme_view)
            self.status_bar.showMessage("├ûdemeler")
        except Exception as e:
            error_msg = f"├ûdemeler ekran─▒ a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", error_msg)
    
    def show_finansal_analiz(self):
        """Finansal analiz dashboard'unu g├╢ster"""
        try:
            # Zaten a├º─▒k bir process var m─▒ kontrol et
            if hasattr(self, '_finansal_analiz_process') and self._finansal_analiz_process:
                try:
                    # Process hala ├ºal─▒┼ƒ─▒yor mu kontrol et
                    if self._finansal_analiz_process.poll() is None:
                        # Process hala ├ºal─▒┼ƒ─▒yor, pencereyi ├╢ne getirmeye ├ºal─▒┼ƒ
                        # (Windows'ta pencereyi bulmak zor olabilir, bu y├╝zden yeni a├ºmay─▒ tercih edebiliriz)
                        return
                    else:
                        # Process kapanm─▒┼ƒ
                        self._finansal_analiz_process = None
                except:
                    self._finansal_analiz_process = None
            
            # Tkinter dashboard'u ayr─▒ bir Python s├╝recinde a├º (thread-safe de─ƒil, subprocess kullan)
            import subprocess
            import sys
            import os
            
            # Finansal analiz dashboard'unu ayr─▒ bir Python s├╝recinde ├ºal─▒┼ƒt─▒r
            script_path = os.path.join(os.path.dirname(__file__), 'views', 'finansal_analiz_dashboard.py')
            script_path = os.path.abspath(script_path)  # Mutlak yol kullan
            
            # Script path'inin var oldu─ƒunu kontrol et
            if not os.path.exists(script_path):
                error_msg = f"Finansal analiz dashboard dosyas─▒ bulunamad─▒:\n{script_path}\n\nMevcut dizin: {os.getcwd()}\n__file__ dizini: {os.path.dirname(__file__)}"
                print(f"ERROR: {error_msg}")
                QMessageBox.critical(self, "Hata", error_msg)
                return
            
            
            # Windows'ta normal ┼ƒekilde a├º (Tkinter penceresi g├╢r├╝nmeli)
            try:
                # Basit subprocess a├º - Tkinter kendi penceresini a├ºacak
                # cwd'yi views klas├╢r├╝n├╝n parent'─▒na ayarla (import'lar i├ºin)
                cwd = os.path.dirname(__file__)
                
                # Hata mesajlar─▒n─▒ g├╢rmek i├ºin log dosyas─▒ olu┼ƒtur
                log_file = os.path.join(cwd, 'finansal_analiz_log.txt')
                
                # UTF-8 encoding ile log dosyas─▒ a├º
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'  # Unicode encoding ayarla
                
                self._finansal_analiz_process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=cwd,
                    env=env,
                    stdout=open(log_file, 'w', encoding='utf-8'),
                    stderr=subprocess.STDOUT  # stderr'i stdout'a y├╢nlendir
                )
            except Exception as e:
                error_msg = f"Finansal analiz dashboard a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}\n\nDosya yolu: {script_path}"
                print(f"ERROR: {error_msg}")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Hata", error_msg)
                return
            
            # Process'in kapanmas─▒n─▒ izle (opsiyonel, arka planda ├ºal─▒┼ƒ─▒r)
            def cleanup_process():
                if hasattr(self, '_finansal_analiz_process') and self._finansal_analiz_process:
                    try:
                        self._finansal_analiz_process.wait(timeout=0.1)
                    except:
                        pass
            
            # Cleanup'─▒ arka planda ├ºal─▒┼ƒt─▒r (non-blocking)
            import threading
            cleanup_thread = threading.Thread(target=cleanup_process, daemon=True)
            cleanup_thread.start()
            
        except Exception as e:
            error_msg = f"Finansal analiz dashboard a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", error_msg)
    
    def show_purchase_invoice(self):
        """Al─▒┼ƒ Faturalar─▒ listesi ekran─▒n─▒ g├╢ster"""
        try:
            from views.purchase_invoice_list_view import PurchaseInvoiceListView
            from controllers.purchase_invoice_list_controller import PurchaseInvoiceListController
            
            self.purchase_invoice_list_view = PurchaseInvoiceListView(self)
            self.purchase_invoice_list_controller = PurchaseInvoiceListController(self.purchase_invoice_list_view, self)
            self.setCentralWidget(self.purchase_invoice_list_view)
            self.status_bar.showMessage("Al─▒┼ƒ Faturalar─▒")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Al─▒┼ƒ Faturalar─▒ ekran─▒ a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}")
            import traceback
            traceback.print_exc()
        
    def show_gmail_settings(self):
        """Gmail ayarlar─▒n─▒ g├╢ster"""
        from views.gmail_settings_dialog import GmailSettingsDialog
        from services.email_service import EmailService
        
        dialog = GmailSettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Ayarlar─▒ kaydet
            if dialog.save_to_env():
                # EmailService instance'─▒n─▒ s─▒f─▒rla (yeni ayarlar─▒ y├╝klemek i├ºin)
                EmailService._instance = None
                EmailService._server = None
                
                QMessageBox.information(
                    self, 
                    "Ba┼ƒar─▒l─▒", 
                    "Gmail ayarlar─▒ kal─▒c─▒ olarak kaydedildi!\n\n"
                    "Art─▒k mail g├╢nderirken onay istenmeyecek.\n"
                    f"G├╢nderen: {dialog.email_input.text().strip()}"
                )
            else:
                QMessageBox.warning(self, "Uyar─▒", "Gmail ayarlar─▒ kaydedilemedi!")
    
    def show_hesap_makinesi(self):
        """Hesap makinesi dialog'unu g├╢ster"""
        try:
            from views.hesap_makinesi_dialog import HesapMakinesiDialog
            dialog = HesapMakinesiDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hesap makinesi a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_admin_panel(self):
        """Admin panelini g├╢ster"""
        try:
            # Admin kontrol├╝
            if not self.current_user:
                QMessageBox.warning(self, "Uyar─▒", "Giri┼ƒ yapman─▒z gerekiyor!")
                return
            
            # Kullan─▒c─▒ rol├╝n├╝ kontrol et
            user_role = self.current_user.get('role', 'user')
            is_admin = user_role == 'admin' or self.current_user.get('is_admin', False)
            
            if not is_admin:
                QMessageBox.warning(self, "Yetkisiz Eri┼ƒim", "Bu sayfaya eri┼ƒim yetkiniz yok! Admin yetkisi gereklidir.")
                return
            
            from views.admin_panel_view import AdminPanelView
            self.admin_panel_view = AdminPanelView(self)
            self.setCentralWidget(self.admin_panel_view)
            self.status_bar.showMessage("Admin Paneli - Sistem Loglar─▒")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Admin paneli a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_ai_payment_predictor(self):
        """AI ├ûdeme Tahmini ekran─▒n─▒ g├╢ster"""
        try:
            from views.ai_payment_predictor_view import AIPaymentPredictorView
            from services.payment_predictor import PaymentPredictor
            from models.cari_hesap_model import CariHesapModel
            from models.tahsilat_model import TahsilatModel
            import pandas as pd
            
            self.ai_view = AIPaymentPredictorView(self)
            
            # Cari hesaplar─▒ y├╝kle
            cari_model = CariHesapModel()
            cari_list = cari_model.get_all()
            self.ai_view.load_cari_hesaplar(cari_list)
            
            # Tahmin callback'i
            def on_tahmin():
                cari_id = self.ai_view.get_selected_cari_id()
                if not cari_id:
                    self.ai_view.show_error("L├╝tfen bir m├╝┼ƒteri se├ºiniz!")
                    return
                
                try:
                    # Tahsilat verilerini al
                    tahsilat_model = TahsilatModel()
                    tahsilatlar = tahsilat_model.get_all()
                    
                    # Cari hesaba g├╢re filtrele
                    cari_tahsilatlar = [t for t in tahsilatlar if t.get('cari_id') == cari_id]
                    
                    if len(cari_tahsilatlar) < 2:
                        self.ai_view.show_error("Bu m├╝┼ƒteri i├ºin yeterli ├╢deme verisi yok! (En az 2 ├╢deme gerekli)")
                        return
                    
                    # DataFrame olu┼ƒtur
                    df_data = []
                    for tahsilat in cari_tahsilatlar:
                        df_data.append({
                            'MusteriID': cari_id,
                            'VadeTarihi': tahsilat.get('vadeTarihi', ''),
                            'OdemeTarihi': tahsilat.get('odemeTarihi', ''),
                            'Tutar': float(tahsilat.get('tutar', 0))
                        })
                    
                    df = pd.DataFrame(df_data)
                    
                    # Modeli y├╝kle veya e─ƒit
                    predictor = PaymentPredictor()
                    try:
                        predictor.load_model()
                    except FileNotFoundError:
                        # Model yoksa, t├╝m m├╝┼ƒterilerin verileriyle e─ƒit
                        self.ai_view.show_success("Model e─ƒitiliyor, l├╝tfen bekleyin...")
                        QApplication.processEvents()  # UI'yi g├╝ncelle
                        
                        # T├╝m tahsilat verilerini al
                        all_tahsilatlar = tahsilat_model.get_all()
                        if len(all_tahsilatlar) < 10:
                            self.ai_view.show_error("Model e─ƒitimi i├ºin yeterli veri yok! (En az 10 ├╢deme gerekli)")
                            return
                        
                        # T├╝m veriler i├ºin DataFrame olu┼ƒtur
                        all_df_data = []
                        for tahsilat in all_tahsilatlar:
                            all_df_data.append({
                                'MusteriID': tahsilat.get('cari_id', ''),
                                'VadeTarihi': tahsilat.get('vadeTarihi', ''),
                                'OdemeTarihi': tahsilat.get('odemeTarihi', ''),
                                'Tutar': float(tahsilat.get('tutar', 0))
                            })
                        
                        all_df = pd.DataFrame(all_df_data)
                        
                        # Modeli e─ƒit
                        try:
                            predictor.train(all_df, test_size=0.2, random_state=42)
                            self.ai_view.show_success("Model ba┼ƒar─▒yla e─ƒitildi!")
                        except Exception as e:
                            self.ai_view.show_error(f"Model e─ƒitimi ba┼ƒar─▒s─▒z:\n{str(e)}")
                            import traceback
                            traceback.print_exc()
                            return
                    
                    result = predictor.predict(cari_id, df)
                    
                    # Cari hesap bilgisini ekle
                    cari = next((c for c in cari_list if c.get('id') == cari_id), {})
                    result['musteri_adi'] = cari.get('unvani', cari_id)
                    
                    # Sonu├ºlar─▒ g├╢ster
                    self.ai_view.display_results([result])
                    self.ai_view.show_success("Tahmin ba┼ƒar─▒yla tamamland─▒!")
                    
                except FileNotFoundError:
                    self.ai_view.show_error("Model dosyas─▒ bulunamad─▒! ├ûnce modeli e─ƒitmeniz gerekiyor.")
                except Exception as e:
                    self.ai_view.show_error(f"Tahmin yap─▒l─▒rken hata olu┼ƒtu:\n{str(e)}")
                    import traceback
                    traceback.print_exc()
            
            self.ai_view.set_callbacks(on_tahmin=on_tahmin)
            self.setCentralWidget(self.ai_view)
            self.status_bar.showMessage("AI ├ûdeme Tahmini")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI ├ûdeme Tahmini ekran─▒ a├º─▒l─▒rken hata olu┼ƒtu:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _refresh_dashboard_metrics(self):
        """Ger├ºek verilerle KPI kartlar─▒n─▒ g├╝ncelle"""
        try:
            if not hasattr(self, "dashboard") or not self.dashboard:
                return
            
            # Dashboard widget'─▒n─▒n hala var olup olmad─▒─ƒ─▒n─▒ kontrol et
            try:
                # Widget'a eri┼ƒmeyi dene
                if not hasattr(self.dashboard, "update_kpi_data"):
                    return
            except RuntimeError:
                # Widget silinmi┼ƒ
                return
            
            metrics = self.get_dashboard_metrics()
            
            try:
                self.dashboard.update_kpi_data(
                    ciro=metrics.get("ciro", 0.0),
                    alacak=metrics.get("alacak", 0.0),
                    gider=metrics.get("gider", 0.0),
                    musteri_sayisi=metrics.get("musteri_sayisi", 0),
                )
            except RuntimeError:
                # Widget silinmi┼ƒ, sessizce ├º─▒k
                return
        except RuntimeError:
            # Widget silinmi┼ƒ, sessizce ├º─▒k
            return
        except Exception as e:
            print(f"KPI metrikleri y├╝klenemedi: {e}")
            import traceback
            traceback.print_exc()

    def _refresh_recent_activity(self):
        """Son hareketler tablosunu doldur"""
        try:
            if not hasattr(self, "dashboard") or not self.dashboard:
                # Dashboard hen├╝z haz─▒r de─ƒilse tekrar dene
                QTimer.singleShot(200, self._refresh_recent_activity)
                return
            
            # Dashboard widget'─▒n─▒n hala var olup olmad─▒─ƒ─▒n─▒ kontrol et
            try:
                # Widget'a eri┼ƒmeyi dene
                if not hasattr(self.dashboard, "update_recent_activity"):
                    QTimer.singleShot(200, self._refresh_recent_activity)
                    return
            except RuntimeError:
                # Widget silinmi┼ƒ
                return
            
            activities = self.get_recent_activity()
            try:
                self.dashboard.update_recent_activity(activities)
            except RuntimeError:
                # Widget silinmi┼ƒ, sessizce ├º─▒k
                return
        except RuntimeError:
            # Widget silinmi┼ƒ, sessizce ├º─▒k
            return
        except Exception as e:
            print(f"Son hareketler y├╝klenemedi: {e}")
            import traceback
            traceback.print_exc()

    def get_dashboard_metrics(self):
        """Ger├ºek de─ƒerleri modellerden hesapla"""
        from models.fatura_model import FaturaModel
        from models.tahsilat_model import TahsilatModel
        from models.purchase_invoice_model import PurchaseInvoiceModel
        from models.cari_hesap_model import CariHesapModel

        faturalar = FaturaModel().get_all()
        toplam_ciro = sum(float(f.get("netTutar", 0) or 0) for f in faturalar)

        tahsilatlar = TahsilatModel().get_all()
        toplam_tahsilat = sum(float(t.get("tutar", 0) or 0) for t in tahsilatlar)
        alacak = max(toplam_ciro - toplam_tahsilat, 0)

        alim_faturalari = PurchaseInvoiceModel().get_all()
        toplam_gider = sum(float(f.get("net_tutar", 0) or 0) for f in alim_faturalari)

        musteriler = CariHesapModel().get_all()
        musteri_sayisi = len(musteriler) if musteriler else 0

        return {
            "ciro": toplam_ciro,
            "alacak": alacak,
            "gider": toplam_gider,
            "musteri_sayisi": musteri_sayisi,
        }

    def get_recent_activity(self):
        """Sat─▒┼ƒ faturalar─▒ ve tahsilatlardan son 10 hareket - Sadece mevcut kullan─▒c─▒n─▒n i┼ƒlemleri"""
        try:
            from models.fatura_model import FaturaModel
            from models.tahsilat_model import TahsilatModel
            
            # Mevcut kullan─▒c─▒ ID'sini al
            current_user_id = None
            if hasattr(self, 'current_user') and self.current_user:
                current_user_id = self.current_user.get('id')
                # ID'yi string'e ├ºevir (veritaban─▒nda string olarak saklan─▒yor olabilir)
                if current_user_id:
                    current_user_id = str(current_user_id)
            
            faturalar = FaturaModel().get_all()
            tahsilatlar = TahsilatModel().get_all()

            activity = []
            for f in faturalar:
                # Sadece bu kullan─▒c─▒n─▒n olu┼ƒturdu─ƒu veya d├╝zenledi─ƒi faturalar─▒ g├╢ster
                # E─ƒer created_by bo┼ƒsa (eski kay─▒tlar), g├╢ster (geriye d├╢n├╝k uyumluluk)
                created_by = str(f.get("created_by", "") or "")
                last_modified_by = str(f.get("last_modified_by", "") or "")
                
                # E─ƒer kullan─▒c─▒ giri┼ƒ yapm─▒┼ƒsa filtreleme yap
                if current_user_id:
                    # E─ƒer created_by ve last_modified_by bo┼ƒsa, eski kay─▒t oldu─ƒu i├ºin g├╢ster
                    if not created_by and not last_modified_by:
                        # Eski kay─▒tlar─▒ g├╢ster (geriye d├╢n├╝k uyumluluk)
                        pass
                    elif created_by != current_user_id and last_modified_by != current_user_id:
                        # Yeni kay─▒tlar i├ºin sadece bu kullan─▒c─▒n─▒n i┼ƒlemlerini g├╢ster
                        continue
                # E─ƒer kullan─▒c─▒ giri┼ƒ yapmam─▒┼ƒsa t├╝m kay─▒tlar─▒ g├╢ster
                
                # Cari hesap bilgisini d├╝zg├╝n al
                cari_hesap = f.get("cariHesap", {})
                if isinstance(cari_hesap, str):
                    import json
                    try:
                        cari_hesap = json.loads(cari_hesap)
                    except:
                        cari_hesap = {}
                
                activity.append({
                    "tarih": f.get("tarih", ""),
                    "musteri": cari_hesap.get("unvani", "") if isinstance(cari_hesap, dict) else "",
                    "aciklama": f.get("faturaNo", ""),
                    "tutar": float(f.get("netTutar", 0) or f.get("toplam", 0) or 0),
                    "tip": "gelir",
                    "id": f.get("id", ""),
                    "entity_type": "fatura"
                })
            
            for t in tahsilatlar:
                # Sadece bu kullan─▒c─▒n─▒n olu┼ƒturdu─ƒu veya d├╝zenledi─ƒi tahsilatlar─▒ g├╢ster
                # E─ƒer created_by bo┼ƒsa (eski kay─▒tlar), g├╢ster (geriye d├╢n├╝k uyumluluk)
                created_by = str(t.get("created_by", "") or "")
                last_modified_by = str(t.get("last_modified_by", "") or "")
                
                # E─ƒer kullan─▒c─▒ giri┼ƒ yapm─▒┼ƒsa filtreleme yap
                if current_user_id:
                    # E─ƒer created_by ve last_modified_by bo┼ƒsa, eski kay─▒t oldu─ƒu i├ºin g├╢ster
                    if not created_by and not last_modified_by:
                        # Eski kay─▒tlar─▒ g├╢ster (geriye d├╢n├╝k uyumluluk)
                        pass
                    elif created_by != current_user_id and last_modified_by != current_user_id:
                        # Yeni kay─▒tlar i├ºin sadece bu kullan─▒c─▒n─▒n i┼ƒlemlerini g├╢ster
                        continue
                # E─ƒer kullan─▒c─▒ giri┼ƒ yapmam─▒┼ƒsa t├╝m kay─▒tlar─▒ g├╢ster
                
                activity.append({
                    "tarih": t.get("tarih", ""),
                    "musteri": t.get("cari_unvani", "") or t.get("cari", ""),
                    "aciklama": f"Tahsilat ({t.get('odeme_turu', '')})",
                    "tutar": float(t.get("tutar", 0) or 0),
                    "tip": "gider",
                    "id": t.get("id", ""),
                    "entity_type": "tahsilat"
                })
            
            # Tarihe g├╢re s─▒rala ve son 10'unu al
            activity = sorted(activity, key=lambda x: x.get("tarih", ""), reverse=True)[:10]
            return activity
        except Exception as e:
            print(f"Son hareket hesaplanamad─▒: {e}")
            import traceback
            traceback.print_exc()
            return []

    def show_about(self):
        """Hakk─▒nda"""
        QMessageBox.about(
            self,
            "Hakk─▒nda",
            "MUBA - Cari Hesap Y├╢netim Sistemi\n\n"
            "Python PyQt5 ve SQLite ile geli┼ƒtirilmi┼ƒtir.\n"
            "Versiyon: 1.0.0"
        )
        
    def closeEvent(self, event):
        """Kapatma"""
        reply = QMessageBox.question(
            self, '├ç─▒k─▒┼ƒ', 'Uygulamadan ├º─▒kmak istedi─ƒinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setApplicationName("MUBA")
    app.setOrganizationName("MUBA")
    app.setStyle('Fusion')
    
    # SQLite veritaban─▒n─▒ ba┼ƒlat
    try:
        from sql_init import get_db
        db = get_db()
        print("SQLite veritaban─▒ ba┼ƒar─▒yla ba┼ƒlat─▒ld─▒")
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"SQLite veritaban─▒ ba┼ƒlat─▒lamad─▒:\n{e}")
        sys.exit(1)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

