"""
Cari Hesap Seçim Dialog - Cari hesap seçimi için
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CariHesapSelectDialog(QDialog):
    """Cari hesap seçim dialog'u"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cari Hesap Seç")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.selected_cari = None
        self.init_ui()
        self.load_cari_hesaplar()
        
    def init_ui(self):
        """UI'yi başlat"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Arama
        search_layout = QHBoxLayout()
        search_label = QLabel("Ara:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Kod, unvan veya vergi no ile ara...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Kod", "Unvan", "Vergi No", "Telefon"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_sec = QPushButton("Seç")
        btn_sec.setStyleSheet("background-color: #667eea; color: white; padding: 8px 20px; font-weight: bold;")
        btn_sec.clicked.connect(self.accept_selection)
        button_layout.addWidget(btn_sec)
        
        btn_iptal = QPushButton("İptal")
        btn_iptal.setStyleSheet("padding: 8px 20px;")
        btn_iptal.clicked.connect(self.reject)
        button_layout.addWidget(btn_iptal)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_cari_hesaplar(self):
        """Cari hesapları yükle"""
        from controllers.cari_hesap_controller import CariHesapController
        from PyQt5.QtCore import QEventLoop
        
        self.all_cari = []
        self.filtered_cari = []
        
        self.controller = CariHesapController('get_all')
        loop = QEventLoop()
        self.controller.data_loaded.connect(lambda data: self.on_data_loaded(data, loop))
        self.controller.error_occurred.connect(lambda err: self.on_error(err, loop))
        self.controller.start()
        
        # Thread bitene kadar bekle
        loop.exec_()
    
    def on_data_loaded(self, data, loop):
        """Veri yüklendiğinde"""
        self.all_cari = data
        self.filtered_cari = data
        self.update_table()
        loop.quit()
    
    def on_error(self, err, loop):
        """Hata oluştuğunda"""
        QMessageBox.critical(self, "Hata", f"Cari hesaplar yüklenirken hata:\n{err}")
        loop.quit()
    
    def update_table(self):
        """Tabloyu güncelle"""
        self.table.setRowCount(len(self.filtered_cari))
        
        for row, cari in enumerate(self.filtered_cari):
            self.table.setItem(row, 0, QTableWidgetItem(cari.get('kodu', '-')))
            self.table.setItem(row, 1, QTableWidgetItem(cari.get('unvani', '-')))
            
            # Vergi numarasını maskelenmiş göster
            vergi_no_hash = cari.get('vergiNoHash', '')
            if vergi_no_hash:
                vergi_no_display = vergi_no_hash[:6] + '****'
            else:
                vergi_no_display = str(cari.get('vergiNo', '-'))
            self.table.setItem(row, 2, QTableWidgetItem(vergi_no_display))
            
            self.table.setItem(row, 3, QTableWidgetItem(cari.get('telefon', '-')))
    
    def on_search(self, text):
        """Arama yap"""
        if not text or not text.strip():
            self.filtered_cari = self.all_cari
        else:
            query = text.lower().strip()
            self.filtered_cari = []
            for cari in self.all_cari:
                kod = str(cari.get('kodu', '')).lower()
                unvan = cari.get('unvani', '').lower()
                vergi_no = str(cari.get('vergiNo', '')).lower()
                
                if (query in kod or query in unvan or query in vergi_no):
                    self.filtered_cari.append(cari)
        self.update_table()
    
    def on_double_click(self, item):
        """Çift tıklama ile seç"""
        self.accept_selection()
    
    def accept_selection(self):
        """Seçimi onayla"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_cari):
            self.selected_cari = self.filtered_cari[current_row]
            self.accept()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari hesap seçin!")
    
    def get_selected_cari(self):
        """Seçili cari hesabı döndür"""
        return self.selected_cari

